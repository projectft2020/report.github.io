# Market Score V3 策略 - Dashboard 實現規格

**項目:** Dashboard Strategy V3 Implementation  
**日期:** 2026-02-22  
**參考實現:** `/Users/charlie/.openclaw/workspace/market_score_dual_confirm_strategy.py`  
**回測結果:** `/Users/charlie/.openclaw/workspace/market_score_dual_confirm_strategy_results.csv`

---

## 1. 策略概述

### 1.1 核心理念

**Market Score V3** 是一個基於雙市場（TW/US）確認的三態倉位策略，通過結合台灣市場和美國市場的 Market Score 來決定倉位，降低錯誤訊號並提高風險調整後收益。

### 1.2 策略特性

| 特性 | 說明 |
|------|------|
| **雙重確認** | TW 和 US Market Score 必須同時達到條件才執行 |
| **三態倉位** | 0%（空倉）、50%（半倉）、100%（滿倉） |
| **漸進式加倉** | 根據 Market Score 強度調整倉位 |
| **動態止損** | 市場轉弱時自動降倉位 |
| **多市場適配** | 支持 TW/US 兩市場個別評分 |

---

## 2. 技術需求

### 2.1 架構要求

**必須遵循 Dashboard 現有架構：**

```
backend/services/strategies/
├── interface.py              # IStrategy 接口（必須實現）
└── implementations/
    └── dual_market_confirm_strategy.py  # 本策略實現位置
```

### 2.2 核心接口實現

**IStrategy 接口必須實現的方法：**

```python
class IStrategy(ABC):
    @abstractmethod
    def get_name(self) -> str: ...
    
    @abstractmethod
    def get_description(self) -> str: ...
    
    @abstractmethod
    def get_params_schema(self) -> dict: ...
    
    @abstractmethod
    def get_params_default(self) -> dict: ...
    
    @abstractmethod
    def validate_params(self, params: dict) -> bool: ...
    
    @abstractmethod
    def backtest(self, 
                 data: pd.DataFrame, 
                 params: dict,
                 start_date: str = None,
                 end_date: str = None) -> BacktestResult: ...
```

### 2.3 可復用服務

**現有服務（必須使用，避免重複造輪子）：**

| 服務名稱 | 位置 | 用途 |
|---------|------|------|
| `MarketThermometerService` | `services/market_thermometer/` | 獲取 TW/US 市場 MA 斜率和 Market Score |
| `IndicatorCalculator` | `services/indicators/` | 統一的技術指標計算（RSI, MACD 等） |
| `VBTDataLoader` | `services/data/` | 統一的價格數據加載 |
| `StrategyParamsRegistry` | `services/strategies/` | 策略參數管理和驗證 |

---

## 3. 實現細節

### 3.1 Market Score 計算

**Market Score 定義（0-100 分）：**

```python
def calculate_market_score(ma_slope: float, rsi: float) -> int:
    """
    根據 MA 斜率和 RSI 計算 Market Score
    
    Args:
        ma_slope: MA 斜率（正數代表上升趨勢）
        rsi: RSI 指標（0-100）
    
    Returns:
        int: Market Score (0-100)
    """
    # MA 斜率貢獻：斜率每增加 0.1，貢獻 10 分（最高 50 分）
    slope_score = min(50, max(0, ma_slope * 100))
    
    # RSI 貢獻：RSI 在 30-70 之間給分
    if 30 <= rsi <= 70:
        rsi_score = 50  # 中性區域
    elif rsi < 30:
        rsi_score = rsi * 0.5  # 超賣，給分較低
    else:  # rsi > 70
        rsi_score = 50 - (rsi - 70) * 1.25  # 超買，扣分
    
    return int(slope_score + rsi_score)
```

### 3.2 V3 策略核心邏輯

**策略理念：雙市場四重確認**

v3 策略要求 TW 和 US 兩個市場的 Market Score 和趨勢指標同時達到條件，嚴格控制倉位。

#### 3.2.1 倉位決策邏輯（核心）

```python
def calculate_position(row):
    """
    根據雙市場同時確認策略計算倉位
    
    輸入參數（row DataFrame）：
        - tw_market_score: 台灣 Market Score (0-100)
        - us_market_score: 美國 Market Score (0-100)
        - tw0050_above_120ma: 台股是否在 120MA 之上
        - qqq_above_20ma: 美股是否在 20MA 之上
    
    輸出：
        - position_size: 0.0 (空倉), 0.5 (半倉), 1.0 (全倉)
    """
    # 提取變量
    tw_ms = row['tw_market_score']
    us_ms = row['us_market_score']
    tw0050_above = row['tw0050_above_120ma']
    qqq_above = row['qqq_above_20ma']
    
    # === 情況 1: Market Score 數據缺失 ===
    if pd.isna(tw_ms) or pd.isna(us_ms):
        # 只使用趨勢指標
        if tw0050_above and qqq_above:
            return 1.0  # 雙重趨勢向上 → 全倉
        elif (tw0050_above == False) and (qqq_above == False):
            return 0.0  # 雙重趨勢向下 → 空倉
        else:
            return 0.5  # 趨勢分歧 → 半倉
    
    # === 情況 2: Market Score 可用，完整四重確認 ===
    # 進場條件（全倉 100%）：四個條件必須同時滿足
    if (tw_ms > 50 and us_ms > 50 and          # 兩市場 Market Score 都 > 50
        tw0050_above and qqq_above):             # 兩市場趨勢都向上
        return 1.0
    
    # 出場條件（空倉 0%）：四個條件必須同時滿足
    if (tw_ms < 40 and us_ms < 40 and             # 兩市場 Market Score 都 < 40
        (tw0050_above == False) and (qqq_above == False)):  # 兩市場趨勢都向下
        return 0.0
    
    # 其他情況 → 半倉 50%
    return 0.5
```

#### 3.2.2 策略參數（門檻值）

```python
# Market Score 門檻
LONG_THRESHOLD = 50    # > 50 為多頭
SHORT_THRESHOLD = 40   # < 40 為空頭
NEUTRAL_MIN = 40       # 中性區間下限
NEUTRAL_MAX = 50       # 中性區間上限

# 趨勢指標
TW_MA_PERIOD = 120     # 台股 120 日均線
US_MA_PERIOD = 20      # 美股 20 日均線
```

#### 3.2.3 決策流程圖

```
開始
  │
  ├─> Market Score 可用？
  │   ├─ NO ─> 使用趨勢指標
  │   │          ├─ 兩趨勢都向上 → 全倉 100%
  │   │          ├─ 兩趨勢都向下 → 空倉 0%
  │   │          └─ 趨勢分歧 → 半倉 50%
  │   │
  │   └─ YES ─> 四重確認檢查
  │              ├─ TW_MS > 50 AND US_MS > 50
  │              │   AND TW_0050 > 120MA
  │              │   AND QQQ > 20MA
  │              │   └─→ 全倉 100%
  │              │
  │              ├─ TW_MS < 40 AND US_MS < 40
  │              │   AND TW_0050 < 120MA
  │              │   AND QQQ < 20MA
  │              │   └─→ 空倉 0%
  │              │
  │              └─ 其他情況 → 半倉 50%
  │
結束
```

#### 3.2.4 投資組合結構

**資產配置：**

```python
# 50% QQQ + 50% 0050.TW
portfolio_daily_return = qqq_daily_return * 0.5 + tw0050_daily_return * 0.5

# 投資組合價值計算
portfolio_value[t] = portfolio_value[t-1] * (1 + portfolio_daily_return[t] * position_size[t])
```

**注意：**
- 倉位控制應用於整個投資組合，而非單個資產
- 每日根據當日倉位計算收益
- 避免頻繁交易，只在倉位變化時調整

#### 3.2.5 數據需求

**必需數據：**

| 數據項 | 來源 | 用途 |
|-------|------|------|
| QQQ 價格 | VBTDataLoader | 美股 ETF 價格 |
| 0050.TW 價格 | VBTDataLoader | 台股 ETF 價格 |
| TW Market Score | MarketThermometerService | 台灣市場狀態 |
| US Market Score | MarketThermometerService | 美國市場狀態 |
| TW 120MA | IndicatorCalculator | 台股趨勢判斷 |
| US 20MA | IndicatorCalculator | 美股趨勢判斷 |

**時間範圍：**
- 回測期：2019-01-01 至 2024-12-31
- 確保有足夠的歷史數據計算 MA

### 3.3 參數設計

**V3 策略參數（簡化設計）：**

v3 策略的參數相對固定，核心邏輯是雙市場四重確認。以下是可調整的參數：

```python
{
    "tw_market": {
        "type": "object",
        "properties": {
            "etf_ticker": {
                "type": "string",
                "default": "0050.TW",
                "description": "台灣市場 ETF 代碼（用於交易）"
            },
            "ma_period": {
                "type": "integer",
                "default": 120,
                "minimum": 20,
                "maximum": 250,
                "description": "移動平均線週期（趨勢判斷）"
            }
        }
    },
    "us_market": {
        "type": "object",
        "properties": {
            "etf_ticker": {
                "type": "string",
                "default": "QQQ",
                "description": "美國市場 ETF 代碼（用於交易）"
            },
            "ma_period": {
                "type": "integer",
                "default": 20,
                "minimum": 10,
                "maximum": 50,
                "description": "移動平均線週期（趨勢判斷）"
            }
        }
    },
    "market_score_thresholds": {
        "type": "object",
        "properties": {
            "long_threshold": {
                "type": "integer",
                "default": 50,
                "minimum": 40,
                "maximum": 70,
                "description": "Market Score 多頭門檻（> 此值為多頭）"
            },
            "short_threshold": {
                "type": "integer",
                "default": 40,
                "minimum": 20,
                "maximum": 50,
                "description": "Market Score 空頭門檻（< 此值為空頭）"
            }
        }
    },
    "portfolio_weights": {
        "type": "object",
        "properties": {
            "tw_weight": {
                "type": "number",
                "default": 0.5,
                "minimum": 0,
                "maximum": 1,
                "description": "台灣 ETF 權重（建議 0.5）"
            },
            "us_weight": {
                "type": "number",
                "default": 0.5,
                "minimum": 0,
                "maximum": 1,
                "description": "美國 ETF 權重（建議 0.5）"
            }
        }
    }
}
```

**默認參數：**

```python
DEFAULT_PARAMS = {
    "tw_market": {
        "etf_ticker": "0050.TW",
        "ma_period": 120
    },
    "us_market": {
        "etf_ticker": "QQQ",
        "ma_period": 20
    },
    "market_score_thresholds": {
        "long_threshold": 50,
        "short_threshold": 40
    },
    "portfolio_weights": {
        "tw_weight": 0.5,
        "us_weight": 0.5
    }
}
```

**參數說明：**

| 參數 | 默認值 | 可調範圍 | 說明 |
|------|-------|---------|------|
| TW ETF 代碼 | 0050.TW | 任何台股 ETF | 實際交易目標 |
| TW MA 週期 | 120 | 20-250 | 趨勢判斷週期 |
| US ETF 代碼 | QQQ | 任何美股 ETF | 實際交易目標 |
| US MA 週期 | 20 | 10-50 | 趨勢判斷週期 |
| 多頭門檻 | 50 | 40-70 | Market Score > 50 為多頭 |
| 空頭門檻 | 40 | 20-50 | Market Score < 40 為空頭 |
| TW 權重 | 0.5 | 0-1 | 台灣 ETF 資產配置 |
| US 權重 | 0.5 | 0-1 | 美國 ETF 資產配置 |

**注意：**
- `long_threshold` 必須 > `short_threshold`
- `tw_weight` + `us_weight` 應該 = 1.0（否則會有現金閒置）
- Market Score 從 `MarketThermometerService` 獲取，不需要自己計算
- 參數驗證應檢查以上約束

### 3.4 數據流程

```
1. 加載價格數據
   └─> VBTDataLoader.load_data(['0050.TW', 'QQQ'])
       └─> 返回包含 close, volume 的 DataFrame

2. 計算趨勢指標（MA）
   └─> IndicatorCalculator.add_indicators(df, ma_periods=[120, 20])
       ├─> tw0050_above_120ma: tw0050_close > SMA(120)
       └─> qqq_above_20ma: qqq_close > SMA(20)

3. 獲取 Market Score（從服務）
   └─> MarketThermometerService.get_score_history(market='TW')
       └─> MarketThermometerService.get_score_history(market='US')
       ├─> 返回 total_score (0-100)
       └─> 合併到主 DataFrame

4. 倉位決策（四重確認）
   └─> calculate_position(row)
       ├─> 檢查 Market Score 是否可用
       ├─> 應用四重確認邏輯
       └─> 返回 position_size (0.0, 0.5, 1.0)

5. 計算投資組合收益
   └─> portfolio_return = tw0050_return * 0.5 + qqq_return * 0.5

6. 回測執行（逐日）
   └─> 遍歷每一天，應用倉位並計算價值

7. 返回結果
   └─> BacktestResult
       ├─> total_return (總收益率)
       ├─> sharpe_ratio (夏普比率)
       ├─> max_drawdown (最大回撤)
       ├─> win_rate (勝率)
       └─> position_stats (倉位統計)
```

### 3.5 核心代碼結構

```python
class DualMarketConfirmStrategy(IStrategy):
    
    def __init__(self, config=None):
        self.config = config or {}
        self.tw_ma_period = self.config.get('tw_market', {}).get('ma_period', 120)
        self.us_ma_period = self.config.get('us_market', {}).get('ma_period', 20)
        self.long_threshold = self.config.get('market_score_thresholds', {}).get('long_threshold', 50)
        self.short_threshold = self.config.get('market_score_thresholds', {}).get('short_threshold', 40)
        self.tw_weight = self.config.get('portfolio_weights', {}).get('tw_weight', 0.5)
        self.us_weight = self.config.get('portfolio_weights', {}).get('us_weight', 0.5)
    
    def get_name(self) -> str:
        return "dual_market_confirm_v3"
    
    def get_description(self) -> str:
        return "Market Score V3: Dual-market confirmation with 4-factor validation (TW/US Market Score + Trend)"
    
    def backtest(self, data: pd.DataFrame, params: dict, start_date: str = None, end_date: str = None):
        # 1. 載入價格數據
        tw_df = VBTDataLoader.load_data(params['tw_market']['etf_ticker'], 'TW')
        us_df = VBTDataLoader.load_data(params['us_market']['etf_ticker'], 'US')
        
        # 2. 計算趨勢指標
        tw_df['sma'] = IndicatorCalculator.sma(tw_df['close'], self.tw_ma_period)
        tw_df['above_ma'] = tw_df['close'] > tw_df['sma']
        
        us_df['sma'] = IndicatorCalculator.sma(us_df['close'], self.us_ma_period)
        us_df['above_ma'] = us_df['close'] > us_df['sma']
        
        # 3. 獲取 Market Score
        tw_ms = MarketThermometerService.get_score_history('TW', start_date, end_date)
        us_ms = MarketThermometerService.get_score_history('US', start_date, end_date)
        
        # 4. 合併數據
        df = pd.merge(tw_df[['close', 'above_ma']], us_df[['close', 'above_ma']], 
                      left_index=True, right_index=True, suffixes=('_tw', '_us'))
        df = df.merge(tw_ms[['total_score']], left_index=True, right_index=True, how='left')
        df = df.merge(us_ms[['total_score']], left_index=True, right_index=True, how='left')
        df = df.rename(columns={'total_score_x': 'tw_market_score', 'total_score_y': 'us_market_score'})
        
        # 5. 計算倉位
        df['position_size'] = df.apply(self._calculate_position, axis=1)
        
        # 6. 計算投資組合收益
        df['tw_return'] = df['close_tw'].pct_change()
        df['us_return'] = df['close_us'].pct_change()
        df['portfolio_return'] = df['tw_return'] * self.tw_weight + df['us_return'] * self.us_weight
        
        # 7. 回測執行
        df['portfolio_value'] = self._run_backtest(df)
        
        # 8. 計算績效指標
        return self._calculate_metrics(df)
    
    def _calculate_position(self, row: pd.Series) -> float:
        """四重確認倉位決策"""
        tw_ms = row['tw_market_score']
        us_ms = row['us_market_score']
        tw_above = row['above_ma_tw']
        us_above = row['above_ma_us']
        
        # Market Score 缺失 → 只用趨勢
        if pd.isna(tw_ms) or pd.isna(us_ms):
            if tw_above and us_above:
                return 1.0
            elif not tw_above and not us_above:
                return 0.0
            else:
                return 0.5
        
        # 四重確認
        if (tw_ms > self.long_threshold and us_ms > self.long_threshold and 
            tw_above and us_above):
            return 1.0
        elif (tw_ms < self.short_threshold and us_ms < self.short_threshold and 
              not tw_above and not us_above):
            return 0.0
        else:
            return 0.5
    
    def _run_backtest(self, df: pd.DataFrame) -> pd.Series:
        """執行回測"""
        initial_value = 100000
        portfolio_value = [initial_value]
        
        for i in range(1, len(df)):
            prev_value = portfolio_value[-1]
            daily_return = df['portfolio_return'].iloc[i]
            position = df['position_size'].iloc[i]
            new_value = prev_value * (1 + daily_return * position)
            portfolio_value.append(new_value)
        
        return pd.Series(portfolio_value, index=df.index)
    
    def _calculate_metrics(self, df: pd.DataFrame) -> BacktestResult:
        """計算績效指標"""
        # ... 計算總收益率、夏普比率、最大回撤等
        pass
```

---

## 4. 驗收標準

### 4.1 功能驗收

- [ ] **接口實現完整** - 所有 IStrategy 方法正確實現
- [ ] **參數驗證** - 參數 schema 和默認值正確
- [ ] **錯誤處理** - 缺失數據、無效參數有適當錯誤提示
- [ ] **日誌記錄** - 關鍵操作有日誌輸出

### 4.2 性能驗收（與參考實現對比）

**回測期間：** 2017-01-01 至 2024-12-31  
**基準指數：** Buy & Hold (^TWII)

| 指標 | 參考 v3 目標 | 允許誤差 |
|------|-------------|---------|
| **總收益率** | ≥ +200% | ±5% |
| **夏普比率** | ≥ 3.5 | ±0.3 |
| **最大回撤** | ≤ -10% | ±2% |
| **跑贏年份** | ≥ 7/8 (87.5%) | - |
| **平均倉位** | 60%-70% | ±5% |

**對比組：**
- v2 策略（單市場 MA 趨勢）
- Buy & Hold（持續持有）

### 4.3 代碼品質

- [ ] **代碼風格** - 遵循 PEP 8
- [ ] **類型提示** - 使用 Type Hints
- [ ] **文檔字符串** - 所有公共方法有 docstring
- [ ] **單元測試** - 核心邏輯有測試覆蓋
- [ ] **示例用法** - 提供使用示例

---

## 5. 實現步驟

### 階段 1：基礎架構（1-2 小時）
```python
# 1.1 創建策略文件
touch backend/services/strategies/implementations/dual_market_confirm_strategy.py

# 1.2 實現 IStrategy 接口框架
class DualMarketConfirmStrategy(IStrategy):
    def get_name(self) -> str:
        return "dual_market_confirm_v3"
    
    def get_description(self) -> str:
        return "Market Score V3: Dual-market confirmation with 3-state position"
    
    # ... 其他方法框架
```

### 階段 2：參數系統（30 分鐘）
```python
# 2.1 實現 get_params_schema()
# 2.2 實現 get_params_default()
# 2.3 實現 validate_params()
```

### 階段 3：數據整合（1 小時）
```python
# 3.1 集成 VBTDataLoader（載入 QQQ 和 0050.TW）
# 3.2 集成 IndicatorCalculator（計算 MA 趨勢）
# 3.3 集成 MarketThermometerService（獲取 Market Score）
# 3.4 合併所有數據到統一 DataFrame
```

### 階段 4：倉位決策（1 小時）
```python
# 4.1 實現 _calculate_position()（四重確認邏輯）
# 4.2 處理 Market Score 缺失情況
# 4.3 測試邊界情況（全倉、空倉、半倉）
```

### 階段 5：回測集成（1-2 小時）
```python
# 5.1 實現 backtest() 方法
# 5.2 集成 VBTDataLoader
# 5.3 返回 BacktestResult
```

### 階段 6：測試驗證（1 小時）
```python
# 6.1 單元測試
# 6.2 回測驗證（對比參考實現）
# 6.3 性能基準測試
```

### 階段 7：文檔和示例（30 分鐘）
```python
# 7.1 添加使用示例
# 7.2 更新策略文檔
# 7.3 API 文檔（如需要）
```

**預計總時間：** 5-7 小時

---

## 6. 測試案例

### 6.1 單元測試

```python
import pytest
import pandas as pd
import numpy as np

def test_position_decision_full_position():
    """測試四重確認 → 全倉"""
    strategy = DualMarketConfirmStrategy()
    
    # 情況 1: Market Score 和趨勢都確認多頭
    row = pd.Series({
        'tw_market_score': 60,
        'us_market_score': 70,
        'above_ma_tw': True,
        'above_ma_us': True
    })
    assert strategy._calculate_position(row) == 1.0
    
    # 情況 2: 剛好超過門檻
    row = pd.Series({
        'tw_market_score': 51,
        'us_market_score': 51,
        'above_ma_tw': True,
        'above_ma_us': True
    })
    assert strategy._calculate_position(row) == 1.0

def test_position_decision_empty_position():
    """測試四重確認 → 空倉"""
    strategy = DualMarketConfirmStrategy()
    
    # 情況 1: Market Score 和趨勢都確認空頭
    row = pd.Series({
        'tw_market_score': 35,
        'us_market_score': 30,
        'above_ma_tw': False,
        'above_ma_us': False
    })
    assert strategy._calculate_position(row) == 0.0
    
    # 情況 2: 剛好低於門檻
    row = pd.Series({
        'tw_market_score': 39,
        'us_market_score': 39,
        'above_ma_tw': False,
        'above_ma_us': False
    })
    assert strategy._calculate_position(row) == 0.0

def test_position_decision_half_position():
    """測試其他情況 → 半倉"""
    strategy = DualMarketConfirmStrategy()
    
    # 情況 1: Market Score 和趨勢分歧
    row = pd.Series({
        'tw_market_score': 60,
        'us_market_score': 30,
        'above_ma_tw': True,
        'above_ma_us': False
    })
    assert strategy._calculate_position(row) == 0.5
    
    # 情況 2: Market Score 在中性區間
    row = pd.Series({
        'tw_market_score': 45,
        'us_market_score': 45,
        'above_ma_tw': True,
        'above_ma_us': True
    })
    assert strategy._calculate_position(row) == 0.5

def test_position_decision_missing_market_score():
    """測試 Market Score 缺失 → 使用趨勢指標"""
    strategy = DualMarketConfirmStrategy()
    
    # 情況 1: 雙趨勢向上 → 全倉
    row = pd.Series({
        'tw_market_score': np.nan,
        'us_market_score': np.nan,
        'above_ma_tw': True,
        'above_ma_us': True
    })
    assert strategy._calculate_position(row) == 1.0
    
    # 情況 2: 雙趨勢向下 → 空倉
    row = pd.Series({
        'tw_market_score': np.nan,
        'us_market_score': np.nan,
        'above_ma_tw': False,
        'above_ma_us': False
    })
    assert strategy._calculate_position(row) == 0.0
    
    # 情況 3: 趨勢分歧 → 半倉
    row = pd.Series({
        'tw_market_score': np.nan,
        'us_market_score': np.nan,
        'above_ma_tw': True,
        'above_ma_us': False
    })
    assert strategy._calculate_position(row) == 0.5

def test_portfolio_weights():
    """測試投資組合權重"""
    strategy = DualMarketConfirmStrategy()
    
    # 默認權重
    assert strategy.tw_weight == 0.5
    assert strategy.us_weight == 0.5
    assert strategy.tw_weight + strategy.us_weight == 1.0
    
    # 自定義權重
    custom_config = {
        'portfolio_weights': {
            'tw_weight': 0.7,
            'us_weight': 0.3
        }
    }
    strategy_custom = DualMarketConfirmStrategy(custom_config)
    assert strategy_custom.tw_weight == 0.7
    assert strategy_custom.us_weight == 0.3
    assert strategy_custom.tw_weight + strategy_custom.us_weight == 1.0

def test_backtest_execution():
    """測試回測執行流程"""
    # 這個測試需要完整的數據和服務模擬
    # 可以使用 pytest fixtures 來模擬 VBTDataLoader 和 MarketThermometerService
    pass
```

### 6.2 回測驗證

```python
# 測試數據（使用 v3 策略參數）
params = {
    "tw_market": {
        "etf_ticker": "0050.TW",
        "ma_period": 120
    },
    "us_market": {
        "etf_ticker": "QQQ",
        "ma_period": 20
    },
    "market_score_thresholds": {
        "long_threshold": 50,
        "short_threshold": 40
    },
    "portfolio_weights": {
        "tw_weight": 0.5,
        "us_weight": 0.5
    }
}

# 執行回測（使用 VBTDataLoader）
data = VBTDataLoader.load_data(['0050.TW', 'QQQ'], 
                                  markets=['TW', 'US'],
                                  start_date='2019-01-01',
                                  end_date='2024-12-31')

result = strategy.backtest(data, params, start_date='2019-01-01', end_date='2024-12-31')

# 驗證結果（基於 v3 參考實現的預期）
assert result.total_return >= 2.0  # ≥ 200%
assert result.sharpe_ratio >= 3.5
assert result.max_drawdown <= -0.10  # ≤ -10%
assert result.position_stats['avg_position'] >= 0.6  # 平均倉位 ≥ 60%
```

### 6.3 邊界測試

```python
def test_threshold_boundaries():
    """測試門檻邊界情況"""
    strategy = DualMarketConfirmStrategy()
    
    # 門檻邊界：long_threshold
    row = pd.Series({
        'tw_market_score': 50.0,  # 剛好等於門檻
        'us_market_score': 60.0,
        'above_ma_tw': True,
        'above_ma_us': True
    })
    # 50.0 不 > 50，應該是半倉
    assert strategy._calculate_position(row) == 0.5
    
    row['tw_market_score'] = 50.1  # 稍微超過
    # 50.1 > 50，應該是全倉
    assert strategy._calculate_position(row) == 1.0
    
    # 門檻邊界：short_threshold
    row = pd.Series({
        'tw_market_score': 40.0,  # 剛好等於門檻
        'us_market_score': 30.0,
        'above_ma_tw': False,
        'above_ma_us': False
    })
    # 40.0 不 < 40，應該是半倉
    assert strategy._calculate_position(row) == 0.5
    
    row['tw_market_score'] = 39.9  # 稍微低於
    # 39.9 < 40，應該是空倉
    assert strategy._calculate_position(row) == 0.0
```

---

## 7. 風險與注意事項

### 7.1 潛在風險

| 風險 | 說明 | 緩解措施 |
|------|------|---------|
| **數據缺失** | Market Score 可能在早期歷史數據中缺失 | 使用趨勢指標作為備選 |
| **四重確認過於嚴格** | 雙市場同時達標機率低，可能長期半倉 | 記錄倉位統計，監控半倉時間 |
| **市場分歧** | TW 和 US 長期走勢分歧時策略失效 | 添加分歧警告，記錄分歧天數 |
| **參數過擬合** | 門檻值（50/40）可能過度優化 | 提供默認值，允許用戶調整 |
| **ETF 流動性** | 0050.TW 和 QQQ 的流動性差異 | 確保數據覆蓋交易時間 |
| **匯率風險** | TW/US ETF 匯率波動影響收益 | 回測使用歷史匯率數據 |
| **交易成本** | 頻繁調整倉位產生交易成本 | 添加交易成本參數（可選） |

### 7.2 最佳實踐

1. **使用現有服務** - 不要重新實現 MarketThermometerService
2. **參數默認值** - 基於回測優化結果設置合理的默認值
3. **錯誤處理** - 提供清晰的錯誤信息和建議
4. **日誌記錄** - 記錄關鍵決策點，便於調試
5. **性能優化** - 使用向量化操作，避免循環
6. **數據驗證** - 檢查 Market Score 和價格數據的完整性
7. **倉位監控** - 記錄倉位變化次數和持續時間

### 7.3 V3 策略特有注意事項

**四重確認的嚴格性：**
- 要求 TW 和 US 的 Market Score **同時** > 50
- 要求 TW 和 US 的趨勢 **同時** 向上
- 這可能導致策略在某些時段長期處於半倉狀態

**Market Score 缺失處理：**
- 早期歷史數據（2019 之前）可能沒有 Market Score
- 必須正確處理 `NaN` 值，退回到趨勢指標
- 在日誌中記錄退回情況

**投資組合權重：**
- 默認 50/50 平衡配置
- 如用戶調整權重，應驗證 `tw_weight + us_weight = 1.0`
- 否則會有現金閒置，影響收益

---

## 8. 參考資料

### 8.1 參考實現

- **v3 策略腳本:** `/Users/charlie/.openclaw/workspace/market_score_dual_confirm_strategy.py`
- **回測結果:** `/Users/charlie/.openclaw/workspace/market_score_dual_confirm_strategy_results.csv`
- **Dashboard 策略示例:** `backend/services/strategies/implementations/dual_momentum_strategy.py`

### 8.2 架構文檔

- **IStrategy 接口:** `backend/services/strategies/interface.py`
- **MarketThermometerService:** `backend/services/market_thermometer/service.py`
- **回測框架:** `backend/services/backtesting/`

### 8.3 策略知識

- **雙動量策略:** Gary Antonacci 的雙動量理論
- **Market Thermometer:** 結合趨勢和超買超賣的市場狀態指標
- **風險平價:** 根據市場強度動態調整倉位

---

## 9. 交付清單

### 9.1 代碼文件

- [ ] `backend/services/strategies/implementations/dual_market_confirm_strategy.py`
- [ ] `tests/test_dual_market_confirm_strategy.py`（可選）

### 9.2 文檔

- [ ] 策略使用示例
- [ ] API 文檔（如集成到 Dashboard）
- [ ] 回測報告

### 9.3 驗證

- [ ] 單元測試通過
- [ ] 回測結果符合預期
- [ ] 性能基準測試通過

---

**文檔版本:** v1.1  
**最後更新:** 2026-02-22 01:35  
**狀態:** 準備開發 🚀

**變更記錄：**
- v1.1 (2026-02-22): 補充完整的 V3 策略四重確認邏輯
- v1.0 (2026-02-22): 初始版本
