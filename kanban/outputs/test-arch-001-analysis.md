# Dashboard 策略系統架構分析（測試階段 1）

**任務 ID:** test-arch-001
**代理:** Charlie Analyst (模擬 Architect 角色)
**狀態:** completed
**時間戳:** 2026-02-21T19:36:00+08:00
**版本:** v1.0

---

## 執行摘要

本報告分析了 Dashboard 後端策略系統的架構，聚焦於雙市場確認策略（台灣 Market Score [120MA 斜率] + 美國 Market Score [20MA 斜率]）和三態倉位控制（全倉/半倉/空倉）的實現。

**主要發現：**

1. 系統採用清晰的策略接口設計（IStrategy），支持四種策略類型和三種執行模式
2. 現有架構已實現完整的信號生成、倉位計算和重新平衡邏輯
3. MarketThermometerService 為市場狀態判斷提供了標準化接口，可直接用於雙市場確認
4. 系統具有良好的可擴展性，支持策略組合（Composite）和信號合併（SignalMerger）
5. 存在輕微架構不一致：DualMomentumStrategy 引用了不存在的 `indicators.IndicatorCalculator`

---

## 1. 模塊架構分析

### 1.1 整體架構圖

```
┌─────────────────────────────────────────────────────────────────┐
│                      Dashboard 策略系統                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    核心層 (Core Layer)                 │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │  • IStrategy (抽象基類)                               │    │
│  │  • ICompositeStrategy (組合策略接口)                   │    │
│  │  • SignalMerger (信號合併引擎 - 8 種算法)             │    │
│  │  • 核心類型定義 (types.py)                             │    │
│  └────────────────────┬────────────────────────────────────┘    │
│                       │                                           │
│  ┌────────────────────▼────────────────────────────────────┐    │
│  │                  策略實現層 (Implementations)           │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │  SIGNAL_BASED:                                           │    │
│  │    • RSIStrategy, MACDStrategy, SuperTrendStrategy      │    │
│  │    • DualMomentumStrategy ⭐ (雙動量策略)               │    │
│  │    • ATRBreakoutStrategy, SqueezeStrategy              │    │
│  │                                                         │    │
│  │  PERIODIC_REBALANCE:                                    │    │
│  │    • MomentumStrategy (Top N 輪動)                      │    │
│  │                                                         │    │
│  │  CONDITIONAL_REBALANCE:                                 │    │
│  │    • SectorRotationStrategy                            │    │
│  │                                                         │    │
│  │  COMPOSITE:                                             │    │
│  │    • CompositeStrategy (組合多個子策略)                │    │
│  └────────────────────┬────────────────────────────────────┘    │
│                       │                                           │
│  ┌────────────────────▼────────────────────────────────────┐    │
│  │                  服務層 (Services)                       │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │  • MarketThermometerService ⭐ (市場溫度計)            │    │
│  │    - US: SPY 20MA 斜率                                  │    │
│  │    - TW: 0050.TW 120MA 斜率                             │    │
│  │    - 三種持倉模式 (safe/balanced/aggressive)            │    │
│  │    - 同步警報檢測 (黃金同步/死亡同步)                    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      數據層 (Data Layer)                        │
├─────────────────────────────────────────────────────────────────┤
│  • DuckDB 數據庫                                             │    │
│  • daily_prices 表 (價格數據)                                │    │
│  • market_scores 表 (市場分數)                               │    │
│  • market_thermometer 表 (溫度計歷史)                         │    │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 模塊職責劃分

| 層級 | 模塊 | 職責 |
|------|------|------|
| **核心層** | IStrategy | 定義策略統一接口，確保所有策略行為一致 |
| | ICompositeStrategy | 管理多個子策略，提供信號合併和對沖功能 |
| | SignalMerger | 提供 8 種信號合併算法（全票通過/多數決/加權等） |
| | types.py | 定義所有核心數據結構（枚舉、dataclass） |
| **實現層** | DualMomentumStrategy | 實現雙動量策略：相對動量排名 + 絕對動量過濾 |
| | CompositeStrategy | 組合多個子策略，應用信號合併算法 |
| **服務層** | MarketThermometerService | 基於 MA 斜率判斷市場狀態，提供倉位建議 |

---

## 2. 關鍵接口總結

### 2.1 IStrategy 接口

**用途：** 所有交易策略的抽象基類，確保策略行為一致性

**核心方法：**

| 方法 | 輸入參數 | 返回值 | 用途 |
|------|----------|--------|------|
| `generate_signals()` | `ExecutionContext`, `symbols?` | `SignalList` | 根據當前市場狀態生成交易信號（BUY/SELL/HOLD） |
| `should_rebalance()` | `ExecutionContext` | `bool` | 判斷投資組合是否需要重新平衡 |
| `calculate_target_weights()` | `ExecutionContext` | `Dict[Symbol, float]` | 計算目標倉位權重（總和為 1.0） |

**屬性：**

- `name: str` - 策略名稱
- `strategy_type: StrategyType` - 策略類型（SIGNAL_BASED/PERIODIC_REBALANCE/CONDITIONAL_REBALANCE/COMPOSITE）
- `execution_mode: ExecutionMode` - 執行時機（IMMEDIATE/NEXT_OPEN/NEXT_CLOSE）

**設計模式：** 策略模式（Strategy Pattern）+ 模板方法模式（Template Method Pattern）

---

### 2.2 ICompositeStrategy 接口

**用途：** 組合多個子策略的高級接口，支持信號合併和對沖配置

**擴展方法（繼承自 IStrategy）：**

| 方法 | 輸入參數 | 返回值 | 用途 |
|------|----------|--------|------|
| `add_sub_strategy()` | `IStrategy`, `weight` | `None` | 添加子策略並分配權重 |
| `remove_sub_strategy()` | `strategy_name` | `None` | 移除指定子策略 |
| `get_sub_strategies()` | - | `List[IStrategy]` | 獲取所有子策略列表 |
| `merge_signals()` | `signals_per_strategy` | `SignalList` | 合併多個子策略的信號 |
| `should_hedge()` | `ExecutionContext` | `bool` | 判斷是否需要啟動對沖 |
| `calculate_hedge_weights()` | `ExecutionContext`, `main_weights` | `Dict[Symbol, float]` | 計算包含對沖的目標權重 |

**信號合併算法：**
- `unanimous` - 全票通過
- `majority` - 多數決
- `weighted` - 權重加權
- `priority` - 優先級
- `any` - 任何信號
- `conservative` - 保守（優先 SELL）
- `aggressive` - 進取（優先 BUY）
- `momentum_weighted` - 動量加權

---

### 2.3 SignalAction 枚舉

**用途：** 定義所有可能的交易動作

| 枚舉值 | 用途 | 適用場景 |
|--------|------|----------|
| `BUY` | 開多頭倉位 | 信號觸發進場 |
| `SELL` | 平多頭倉位 | 信號觸發出場 |
| `HOLD` | 持續持有 | 維持現狀 |
| `REDUCE` | 減倉 | 部分止損/止盈 |
| `INCREASE` | 加倉 | 趨勢確認加倉 |
| `HEDGE_SHORT` | 開空頭對沖 | 風險管理 |
| `HEDGE_LONG` | 開多頭對沖 | 跨資產對沖 |
| `HEDGE_CLOSE` | 平對沖倉位 | 解除風險管理 |

---

### 2.4 ExecutionContext 類

**用途：** 策略執行時的上下文信息，提供投資組合和市場當前狀態

**屬性：**

| 屬性 | 類型 | 用途 |
|------|------|------|
| `portfolio_value` | `float` | 投資組合總價值（現金 + 持倉） |
| `available_cash` | `float` | 可用現金 |
| `current_positions` | `List[PositionState]` | 當前持倉列表 |
| `market_date` | `date` | 當前交易日期 |
| `market_status` | `str` | 市場狀態（OPEN/CLOSED/PRE_MARKET/AFTER_HOURS） |

**驗證規則：**
- `portfolio_value` 必須為正
- `available_cash` 不能為負，且不能超過 `portfolio_value`
- `market_status` 必須為有效值

---

### 2.5 MarketThermometerService 類

**用途：** 基於移動平均線斜率判斷市場狀態，提供標準化的倉位配置建議

**核心方法：**

| 方法 | 輸入參數 | 返回值 | 用途 |
|------|----------|--------|------|
| `get_thermometer()` | `market`, `target_date?` | `Dict` | 獲取市場溫度計狀態 |
| `calculate_ma_slope()` | `symbol`, `ma_period`, `target_date` | `(slope, ma_value, price)` | 計算 MA 斜率 |
| `get_position_recommendation()` | `state`, `ma_slope`, `market_score` | `Dict` | 計算三種持倉模式建議 |
| `detect_sync_alert()` | `market`, `target_date`, `lookback_days?` | `Dict or None` | 檢測黃金同步/死亡同步 |
| `get_thermometer_history()` | `market`, `days?` | `List[Dict]` | 獲取歷史溫度計數據 |

**市場配置：**

| 市場 | 代理指標 | MA 週期 | 應用場景 |
|------|----------|---------|----------|
| `US` | SPY | 20 | 美股短期趨勢判定 |
| `TW` | 0050.TW | 120 | 台股長期趨勢判定 |

**持倉模式：**

| 模式 | 範圍 | 邏輯 |
|------|------|------|
| `safe` | 30% ~ 100% | MA 上升 = 100%，下降 = 30% |
| `balanced` | 30% ~ 100% | 漸進調整（根據方向和 Score） |
| `aggressive` | 30% ~ 100% | Score ≥ 35 = 100%，否則 30% |

**輸出數據結構：**

```python
{
    'market': 'US' or 'TW',
    'date': 'YYYY-MM-DD',
    'state': 'prosperity' or 'recession',  # MA 斜率 > 0 為繁榮
    'ma_slope': float,  # 標準化斜率
    'ma_slope_pct': float,  # 百分比形式
    'ma_period': int,  # MA 週期
    'proxy_symbol': 'SPY' or '0050.TW',
    'current_price': float,
    'ma_value': float,
    'price_above_ma': bool,
    'market_score': int,  # 0-100
    'sync_alert': {  # 或 None
        'type': 'golden' or 'death',
        'message': '...',
        'confidence': 'high'
    },
    'position_modes': {
        'safe': {'allocation': int, 'reason': str, 'description': str},
        'balanced': {'allocation': int, 'reason': str, 'description': str},
        'aggressive': {'allocation': int, 'reason': str, 'description': str}
    }
}
```

---

## 3. 數據流分析

### 3.1 完整數據流程

```
┌─────────────┐
│ 市場數據源   │
│ (Price DB)  │
└──────┬──────┘
       │
       ▼
┌────────────────────────────────────────────────────────────┐
│ 1. 價格數據獲取                                            │
│    • DailyPrice → DuckDB (daily_prices 表)                │
└────────────────────────────────────────────────────────────┘
       │
       ├─────────────────────────────────────────┐
       ▼                                         ▼
┌─────────────────────┐          ┌─────────────────────────────┐
│ 2. MarketThermometerService │          │ 3. Strategy.generate_signals() │
│                             │          │                             │
│ get_thermometer('US')      │          │ • 從 DB 讀取歷史價格        │
│ ├─ calculate_ma_slope()    │          │ • 計算技術指標             │
│ │   ├─ 讀取 SPY 價格       │          │ • 判斷進場/出場條件         │
│ │   ├─ 計算 20MA           │          │ • 生成 StrategySignal       │
│ │   ├─ 計算斜率 (線性回歸)  │          │                             │
│ │   └─ 判斷 state          │          │                             │
│ ├─ _get_market_score()     │          │                             │
│ │   └─ 讀取 market_scores  │          │                             │
│ ├─ get_position_recommendation() │          │                             │
│ │   └─ 計算三種模式建議     │          │                             │
│ └─ detect_sync_alert()     │          │                             │
│     └─ 檢測同步警報         │          │                             │
└─────────┬───────────────────┘          └─────────┬───────────────────┘
          │                                      │
          │                                      ▼
          │                          ┌─────────────────────────────┐
          │                          │ 4. SignalList              │
          │                          │    • List[StrategySignal]   │
          │                          │    • 每個 Signal 包含：     │
          │                          │      - symbol, action       │
          │                          │      - strength, reason     │
          │                          │      - timestamp            │
          │                          └─────────┬───────────────────┘
          │                                    │
          ▼                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. 決策層：雙市場確認策略                                        │
│                                                                  │
│  if US.state == 'prosperity' and TW.state == 'prosperity':      │
│      allocation = 100%  # 全倉                                   │
│  elif US.state == 'recession' and TW.state == 'recession':      │
│      allocation = 30%   # 空倉                                    │
│  else:                                                          │
│      allocation = 65%   # 半倉                                   │
│                                                                  │
│  應用 MarketThermometer 的 position_modes:                       │
│  • safe模式：基於 MA 斜率的二元判斷                              │
│  • balanced模式：結合 MA 方向和 Score 的漸進調整                 │
│  • aggressive模式：Score 達標即滿倉                              │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. 倉位計算                                                      │
│    • calculate_target_weights(context)                          │
│    • 根據 allocation 調整現有倉位                               │
│    • 生成目標權重字典 Dict[Symbol, float]                        │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. 執行層                                                        │
│    • 根據 ExecutionMode 決定執行時機                            │
│    • 執行買賣訂單                                              │
│    • 更新持倉狀態                                              │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 8. 持久化                                                        │
│    • 保存倉位記錄到 DB                                          │
│    • 保存交易歷史                                              │
│    • 保存溫度計數據 (market_thermometer 表)                     │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 關鍵數據轉換點

| 階段 | 輸入 | 輸出 | 轉換邏輯 |
|------|------|------|----------|
| **價格 → MA 斜率** | `daily_prices` | `ma_slope` | 線性回歸最近 5 日 MA 值 |
| **MA 斜率 → 狀態** | `ma_slope` | `state` | `slope > 0 → 'prosperity'` |
| **狀態 + Score → 倉位** | `state`, `market_score` | `allocation` | 三種模式不同邏輯 |
| **信號 → 權重** | `SignalList` | `Dict[Symbol, float]` | 等權重 / 加權分配 |
| **權重 → 訂單** | `Dict[Symbol, float]` | `Orders` | 根據當前倉位計算買賣量 |

---

## 4. 可重用組件清單

### 4.1 核心架構組件（完全可重用）

| 組件 | 路徑 | 可重用性 | 適用場景 |
|------|------|----------|----------|
| **IStrategy 接口** | `strategies/core/interface.py` | ⭐⭐⭐ | 所有策略基類 |
| **ICompositeStrategy 接口** | `strategies/core/interface.py` | ⭐⭐⭐ | 多策略組合 |
| **SignalMerger** | `strategies/core/signal_merger.py` | ⭐⭐⭐ | 信號合併（8 種算法） |
| **核心類型定義** | `strategies/core/types.py` | ⭐⭐⭐ | 所有數據結構 |

### 4.2 服務層組件（可直接重用）

| 組件 | 路徑 | 可重用性 | 適用場景 |
|------|------|----------|----------|
| **MarketThermometerService** | `services/market_thermometer_service.py` | ⭐⭐⭐ | 雙市場確認策略核心 |
| | | | • MA 斜率計算 |
| | | | • 狀態判定（繁榮/衰退）|
| | | | • 倉位建議（3 種模式）|
| | | | • 同步警報檢測 |

### 4.3 策略實現參考（部分可重用）

| 組件 | 路徑 | 可重用性 | 可重用部分 |
|------|------|----------|------------|
| **DualMomentumStrategy** | `strategies/implementations/dual_momentum_strategy.py` | ⭐⭐ | • 策略接口實現模式 |
| | | | • 倉位權重計算邏輯 |
| | | | • 動量計算方法 |
| **CompositeStrategy** | `strategies/implementations/composite_strategy.py` | ⭐⭐⭐ | • 子策略管理 |
| | | | • 對沖配置集成 |

### 4.4 數據層組件（基礎設施）

| 組件 | 表名 | 可重用性 | 用途 |
|------|------|----------|------|
| **價格數據表** | `daily_prices` | ⭐⭐⭐ | 存儲每日價格 |
| **市場分數表** | `market_scores` | ⭐⭐⭐ | 存儲 Market Score |
| **溫度計表** | `market_thermometer` | ⭐⭐⭐ | 存儲歷史溫度計數據 |

### 4.5 雙市場確認策略所需新增組件

| 組件類型 | 組件名稱 | 用途 | 優先級 |
|----------|----------|------|--------|
| **策略實現** | `DualMarketConfirmStrategy` | 結合 US + TW 溫度計判斷，生成三態倉位信號 | 高 |
| **配置類** | `DualMarketConfig` | 配置兩個市場的權重、閾值等參數 | 高 |
| **工廠類** | `StrategyFactory` | 創建策略實例（可選） | 中 |

---

## 5. 技術債務識別

### 5.1 設計不一致

| 問題 | 位置 | 影響 | 嚴重程度 | 建議解決方案 |
|------|------|------|----------|-------------|
| **缺少 IndicatorCalculator** | `DualMomentumStrategy` 第 191 行 | 引用不存在的模塊，會導致運行時錯誤 | 🔴 高 | 實現 `indicators.py` 或重構為直接查詢數據庫 |
| **硬編碼數據庫連接** | `DualMomentumStrategy` 第 193-197 行 | 策略類直接導入 `database.db_conn`，違反依賴注入原則 | 🟡 中 | 通過 `ExecutionContext` 或構造函數注入連接 |

### 5.2 潛在架構問題

| 問題 | 描述 | 影響 | 嚴重程度 | 建議解決方案 |
|------|------|------|----------|-------------|
| **策略依賴外部數據庫** | 策略直接操作 DuckDB，與數據層耦合 | 難以單元測試，數據訪問邏輯分散 | 🟡 中 | 引入 Repository 模式，封裝數據訪問 |
| **缺少數據驗證層** | 價格數據沒有完整性檢查 | 可能因缺失數據導致計算錯誤 | 🟡 中 | 在價格查詢層添加數據驗證和異常處理 |
| **配置管理分散** | 策略參數硬編碼在構造函數中 | 難以動態調整策略參數 | 🟢 低 | 引入配置文件或配置管理服務 |

### 5.3 雙市場確認策略特定考慮

| 問題 | 描述 | 影響 | 嚴重程度 | 建議解決方案 |
|------|------|------|----------|-------------|
| **市場數據異步** | 台股和美股交易時間不同，數據更新頻率不一致 | 可能導致判斷基於過時數據 | 🟡 中 | 統一數據刷新時間，或添加時間戳驗證 |
| **權重配置靈活性** | 兩個市場的權重固定（均等），不適應不同市場條件 | 無法根據市場相對強度調整 | 🟢 低 | 支持可配置的市場權重參數 |
| **倉位狀態轉換** | 三態（全倉/半倉/空倉）直接切換，無緩衝 | 可能導致頻繁調倉，增加交易成本 | 🟡 中 | 添加滯後機制或過渡區間 |

### 5.4 文檔和測試

| 問題 | 描述 | 影響 | 嚴重程度 | 建議解決方案 |
|------|------|------|----------|-------------|
| **缺少單元測試** | 焖法針對策略邏輯的測試用例 | 重構風險高，難以驗證正確性 | 🟡 中 | 添加 pytest 測試用例 |
| **API 文檔不完整** | 部分方法缺少示例和返回值說明 | 開發者理解成本高 | 🟢 低 | 完善 docstring，添加使用示例 |

---

## 6. 雙市場確認策略架構建議

### 6.1 推薦架構設計

```
┌─────────────────────────────────────────────────────────────────┐
│              DualMarketConfirmStrategy (新建)                   │
├─────────────────────────────────────────────────────────────────┤
│  職責：協調兩個市場的溫度計，生成三態倉位信號                    │
│                                                                 │
│  依賴：                                                         │
│    • MarketThermometerService (x2: US + TW)                    │
│    • DualMarketConfig (配置: 權重、閾值等)                      │
│                                                                 │
│  核心方法：                                                     │
│    • generate_signals():                                      │
│        1. 獲取 US 溫度計狀態                                     │
│        2. 獲取 TW 溫度計狀態                                     │
│        3. 應用雙市場確認邏輯                                     │
│        4. 生成 SELL/BUY/HOLD 信號                               │
│                                                                 │
│    • calculate_target_weights():                              │
│        1. 應用倉位模式 (safe/balanced/aggressive)               │
│        2. 返回目標權重                                           │
│                                                                 │
│    • should_rebalance():                                      │
│        檢查任一市場狀態是否變化                                 │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                雙市場確認邏輯                                    │
│                                                                 │
│  ┌─────────┬──────────┬─────────┐                              │
│  │ US 狀態 │ TW 狀態  │ 最終倉位 │                              │
│  ├─────────┼──────────┼─────────┤                              │
│  │ 繁榮   │ 繁榮    │ 全倉   │                              │
│  │ 繁榮   │ 衰退    │ 半倉   │                              │
│  │ 衰退   │ 繁榮    │ 半倉   │                              │
│  │ 衰退   │ 衰退    │ 空倉   │                              │
│  └─────────┴──────────┴─────────┘                              │
│                                                                 │
│  然後應用 MarketThermometer 的三種持倉模式細化：                 │
│  • safe: 基於 MA 斜率的二元調整                                 │
│  • balanced: 結合 MA 方向和 Score 的漸進調整                    │
│  • aggressive: Score 達標即滿倉                                │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 實現優先級

| 優先級 | 任務 | 工作量 | 說明 |
|--------|------|--------|------|
| **P0** | 修復 IndicatorCalculator 缺失 | 2h | 重構 DualMomentumStrategy 的數據訪問邏輯 |
| **P0** | 實現 DualMarketConfirmStrategy | 4h | 核心策略邏輯 |
| **P1** | 創建 DualMarketConfig 配置類 | 1h | 參數配置管理 |
| **P1** | 添加單元測試 | 3h | 測試核心邏輯 |
| **P2** | 引入 Repository 模式 | 4h | 解耦數據訪問層 |
| **P2** | 完善 API 文檔 | 2h | 添加使用示例 |

### 6.3 配置建議

```python
# 雙市場確認策略配置示例
dual_market_config = {
    'markets': {
        'US': {
            'weight': 0.5,           # 市場權重
            'proxy_symbol': 'SPY',    # 代理指標
            'ma_period': 20,          # MA 週期
        },
        'TW': {
            'weight': 0.5,
            'proxy_symbol': '0050.TW',
            'ma_period': 120,
        }
    },
    'position_mode': 'balanced',     # safe / balanced / aggressive
    'allocation_levels': {
        'full': 1.0,                 # 全倉比例
        'half': 0.65,                # 半倉比例
        'empty': 0.3                 # 空倉比例
    },
    'transition_buffer': 0.05,      # 轉換緩衝區（可選）
}
```

---

## 7. 總結與建議

### 7.1 架構優勢

1. **清晰的接口設計** - IStrategy 接口定義完善，所有策略行為一致
2. **良好的擴展性** - 支持多種策略類型和執行模式
3. **成熟的服務層** - MarketThermometerService 提供標準化市場狀態判斷
4. **靈活的組合能力** - CompositeStrategy 支持多策略組合和信號合併
5. **類型安全** - 使用 Enum 和 dataclass 確保數據一致性

### 7.2 需要改進的地方

1. **修復 IndicatorCalculator 缺失問題** - 這是阻礙現有策略運行的關鍵問題
2. **解耦數據訪問層** - 策略不應直接依賴數據庫連接
3. **完善測試覆蓋** - 特別是對於核心策略邏輯
4. **統一配置管理** - 避免參數硬編碼

### 7.3 雙市場確認策略實現路徑

**推薦實現路徑：**

```
Phase 1 (修復基礎): 
  • 修復 DualMomentumStrategy 的數據訪問問題
  • 驗證 MarketThermometerService 功能正常

Phase 2 (實現核心):
  • 創建 DualMarketConfirmStrategy
  • 實現雙市場確認邏輯
  • 集成三種持倉模式

Phase 3 (優化改進):
  • 添加單元測試
  • 重構數據訪問層 (Repository 模式)
  • 完善配置管理

Phase 4 (增強功能):
  • 添加滯後機制減少頻繁調倉
  • 支持可配置的市場權重
  • 添加回測和監控功能
```

### 7.4 信心度與局限性

- **信心度:** 高 - 分析基於完整的源代碼和清晰的接口定義
- **數據質量:** 高 - 所有關鍵文件已讀取和分析
- **假設:** 假設 MarketThermometerService 的數據庫連接正常，且 market_scores 表有數據
- **局限性:** 未分析其他策略實現（RSI、MACD 等），未評估回測框架

---

## 8. 元數據

- **分析框架:** 架構分析 + 數據流分析 + 技術債務評估
- **關注領域:** 雙市場確認策略、三態倉位控制
- **建議創意:** 可將此架構應用於多市場/多資產類別的組合策略
- **相關文檔:** 參考 IStrategy 接口定義和 MarketThermometerService 實現
