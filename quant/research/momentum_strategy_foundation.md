# 基礎動能策略 - 第一週研究報告

**研究日期：** 2026-02-17  
**週期：** 第 1-2 週（基礎動能 + 回測）  
**狀態：** 理論研究完成，準備實作  

---

## 🎯 策略概述

### 核心理念
建立一個跨資產動能策略，利用不同資產類別的動能效應來生成 alpha。策略將通過多空組合來降低市場風險，並透過動態權重調整來優化風險回報比。

### 選定資產
根據跨資產動能策略的完整計畫，我們選擇以下四個核心資產：

| 資產 | 代碼 | 資產類別 | 市場代表性 | 動能特性 |
|------|------|----------|------------|----------|
| 納斯達克100 | QQQ | 股票ETF | 美國科技股 | 高波動性，成長導向 |
| 黃金ETF | GLD | 商品ETF | 避險資產 | 通膨對沖，低相關性 |
| 美元指數ETF | UUP | 貨幣ETF | 美元強弱 | 匯率波動，全球影響 |
| 長期公債ETF | TLT | 債券ETF | 利率敏感 | 收益穩定，避險功能 |

---

## 📊 動能計算方法

### 1. 時間框架選擇

#### 短期動能（1-3 個月）
- **計算期間**：21 個交易日（1 個月）
- **特點**：反應快速，適合捕捉短期趨勢
- **風險**：噪音較多，可能產生假信號

#### 中期動能（3-6 個月）
- **計算期間**：63 個交易日（3 個月）
- **特點**：平衡性較好，減少噪音
- **風險**：反應速度中等

#### 長期動能（6-12 個月）
- **計算期間**：126 個交易日（6 個月）
- **特點**：趨勢明確，噪音最少
- **風險**：反應緩慢，錯過早期機會

### 2. 動能得分計算

#### 標準化動能得分
```
動能得分 = (當前價格 - n 日前價格) / n 日前價格
```

#### 排名動能得分
```
排名動能 = RANK(動能得分) / 資產總數
```

#### 加權動能得分
```
加權動能 = 0.4 × 短期動能 + 0.3 × 中期動能 + 0.3 × 長期動能
```

### 3. 動能信號生成

#### 多空信號定義
- **多頭信號**：動能得分 > 0.5
- **空頭信號**：動能得分 < -0.5
- **中性信號**：-0.5 ≤ 動能得分 ≤ 0.5

#### 信號強度分級
| 等級 | 動能得分範圍 | 信號強度 | 權重建議 |
|------|--------------|----------|----------|
| 強多 | > 0.8 | 非常強 | 1.5x |
| 多 | 0.5 - 0.8 | 強 | 1.2x |
| 中性 | -0.5 - 0.5 | 中性 | 1.0x |
| 空 | -0.8 - -0.5 | 弱 | 0.8x |
| 強空 | < -0.8 | 非常弱 | 0.5x |

---

## ⚖️ 權重分配策略

### 1. 等權重基準（Baseline）
```
初始權重 = [0.25, 0.25, 0.25, 0.25]
```

### 2. 動能調整權重
```
調整後權重 = 基礎權重 × (1 + 動能得分 × 調整係數)
```

### 3. 風險平價權重（Risk Parity）
```
風險權重 = 1 / 資產波動率
標準化權重 = 風險權重 / SUM(風險權重)
```

### 4. 動態權重計算步驟

#### 步驟 1：計算基礎動能
```python
def calculate_momentum(price_series, lookback_days):
    return (price_series.iloc[-1] - price_series.iloc[-lookback_days]) / price_series.iloc[-lookback_days]
```

#### 步驟 2：計算組合權重
```python
def calculate_dynamic_weights(momentum_scores, base_weights, adjustment_factor=0.3):
    adjusted_weights = base_weights * (1 + momentum_scores * adjustment_factor)
    return adjusted_weights / adjusted_weights.sum()
```

#### 步驟 3：風險控制
```python
def risk_control(weights, max_single_weight=0.4, min_single_weight=0.1):
    weights = np.clip(weights, min_single_weight, max_single_weight)
    return weights / weights.sum()
```

---

## 🎯 交易執行規則

### 1. 再平衡頻率

#### 每週再平衡（Weekly）
- **頻率**：每週一開盤
- **優點**：跟隨趨勢，反應較快
- **缺點**：交易成本較高

#### 雙週再平衡（Bi-weekly）
- **頻率**：每兩週一再開盤
- **優點**：平衡交易成本和反應速度
- **缺點**：可能錯過短期機會

#### 月度再平衡（Monthly）
- **頻率**：每月第一個週一
- **優點**：交易成本最低
- **缺點**：反應較慢

### 2. 交易成本考慮

#### 假設交易成本
| 成本類型 | 比率 | 影響 |
|----------|------|------|
| 佣金 | 0.1% | 每次交易 |
| 滑點 | 0.2% | 大額交易 |
| 稅費 | 0.0% | 假設免稅帳戶 |
| 總成本 | 0.3% | 每次交易 |

#### 成本優化策略
- **最小交易量**：避免頻繁的小額交易
- **批量執行**：集中在一個時間點執行所有交易
- **流動性考慮**：選擇流動性好的時段交易

### 3. 執行演算法

#### 基礎執行邏輯
```python
def execute_rebalance(current_weights, target_weights, prices):
    # 計算需要買賣的份數
    current_value = calculate_portfolio_value(current_weights, prices)
    target_shares = (target_weights * current_value) / prices
    
    # 生成交易訂單
    orders = []
    for asset in assets:
        diff = target_shares[asset] - current_shares[asset]
        if abs(diff) > MIN_TRADE_UNITS:
            orders.append({
                'asset': asset,
                'action': 'BUY' if diff > 0 else 'SELL',
                'quantity': abs(diff)
            })
    
    return orders
```

---

## 📈 回測框架設計

### 1. 回測期間

#### 主要回測期間
- **開始日期**：2010-01-01
- **結束日期**：2025-12-31
- **總期間**：16 年
- **樣本外**：最近 2 年

#### 市場環境覆蓋
- **牛市**：2010-2015, 2019-2021
- **熊市**：2015-2016, 2018, 2022
- **震盪市**：2016-2018, 2021-2022
- **COVID-19**：2020
- **通膨危機**：2022-2023

### 2. 績效評估指標

#### 核心指標
| 指標 | 計算方式 | 目標值 |
|------|----------|--------|
| 年化報酬率 | CAGR | > 8% |
| 年化波動率 | 標準差 | < 15% |
| 夏普比率 | (報酬率 - 無風險利率) / 波動率 | > 0.5 |
| 最大回撤 | Max Drawdown | < -25% |
| 勝率 | 正報酬月數 / 總月數 | > 60% |

#### 風險指標
| 指標 | 計算方式 | 目標值 |
|------|----------|--------|
| VaR (95%) | 分位數 | < -3% |
| CVaR | 超過 VaR 的平均損失 | < -5% |
| Calmar 比率 | 年化報酬率 / 最大回撤 | > 0.3 |
| Sortino 比率 | (報酬率 - 無風險利率) / 下行波動率 | > 0.8 |

### 3. 基準比較

#### 基準組合
1. **買入持有**：等權重持有四個資產
2. **60/40 組合**：60% QQQ + 40% TLT
3. **S&P 500**：單一市場基準
4. **無風險利率**：3 個月期國庫券

#### 超額報酬分析
```python
def calculate_excess_returns(strategy_returns, benchmark_returns):
    # 計算策略相對基準的超額報酬
    excess_returns = strategy_returns - benchmark_returns
    
    # 計算追蹤誤差
    tracking_error = excess_returns.std() * np.sqrt(252)
    
    # 計算信息比率
    information_ratio = excess_returns.mean() / tracking_error
    
    return {
        'excess_returns': excess_returns,
        'tracking_error': tracking_error,
        'information_ratio': information_ratio
    }
```

---

## 🛠️ 實作技術棧

### 1. 數據獲取
```python
# 使用 yfinance 獲取數據
import yfinance as yf

def get_price_data(tickers, start_date, end_date):
    data = yf.download(tickers, start=start_date, end=end_date)['Adj Close']
    return data
```

### 2. 策略核心
```python
class MomentumStrategy:
    def __init__(self, tickers, lookback_periods):
        self.tickers = tickers
        self.lookback_periods = lookback_periods
        self.weights = None
        
    def calculate_momentum(self, prices):
        momentum_scores = {}
        for period in self.lookback_periods:
            momentum = (prices.iloc[-1] / prices.iloc[-period] - 1)
            momentum_scores[period] = momentum
        return momentum_scores
    
    def generate_signals(self, momentum_scores):
        # 綜合動能得分
        combined_score = np.mean(list(momentum_scores.values()))
        
        # 生成信號
        if combined_score > 0.1:
            return 'BUY'
        elif combined_score < -0.1:
            return 'SELL'
        else:
            return 'HOLD'
```

### 3. 回測引擎
```python
class BacktestEngine:
    def __init__(self, strategy, initial_capital=100000):
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.portfolio_value = []
        self.positions = {}
        
    def run_backtest(self, prices):
        for date, price_row in prices.iterrows():
            # 計算當天動能
            momentum_scores = self.strategy.calculate_momentum(
                prices[:date]
            )
            
            # 生成信號
            signal = self.strategy.generate_signals(momentum_scores)
            
            # 執行交易
            self.execute_trade(signal, price_row, date)
            
            # 更新組合價值
            self.update_portfolio_value(price_row, date)
        
        return self.get_results()
```

---

## 📊 預期結果

### 1. 績效預期

#### 樂觀情景
- **年化報酬率**：10-12%
- **年化波動率**：12-15%
- **夏普比率**：0.6-0.8
- **最大回撤**：-15% to -20%

#### 基準情景
- **年化報酬率**：8-10%
- **年化波動率**：14-18%
- **夏普比率**：0.4-0.6
- **最大回撤**：-20% to -25%

#### 悲觀情景
- **年化報酬率**：5-8%
- **年化波動率**：16-20%
- **夏普比率**：0.2-0.4
- **最大回撤**：-25% to -30%

### 2. 風險特徵

#### 相關性分析
- **與傳統資產相關性**：低至中等
- **跨資產分散效果**：良好
- **市場中性程度**：部分中性

#### 極端情境分析
- **2008 類似危機**：預期回撤 -25% to -35%
- **2020 COVID 危機**：預期回撤 -20% to -30%
- **2022 通膨危機**：預期回撤 -15% to -25%

---

## 🎯 下一步行動

### 第 1-2 週任務清單

#### ✅ 本週完成（理論研究）
- [x] 基礎動能策略理論框架
- [x] 資產選擇與特性分析
- [x] 動能計算方法設計
- [x] 權重分配策略制定
- [x] 回測框架規劃

#### ⏳ 下週開始（實作階段）
- [ ] Matrix 系統整合
- [ ] 數據收集與清洗
- [ ] 基礎動能策略程式碼實作
- [ ] 第一次回測執行
- [ ] 結果分析與優化

### 優先級排序

1. **高優先級**：Matrix 系統整合
2. **中優先級**：數據收集
3. **中優先級**：策略實作
4. **低優先級**：回測執行

---

## 📝 備註與注意事項

### 技術限制
1. **數據品質**：確保數據的完整性和準確性
2. **滑點成本**：實際交易可能面臨更高的滑點
3. **流動性風險**：大額交易可能影響市場價格
4. **模型風險**：歷史表現不能保證未來結果

### 市場風險
1. **黑天鵝事件**：無法預測的極端事件
2. **制度變化**：交易規則或稅制改變
3. **相關性突變**：危機時期相關性可能急劇變化
4. **流動性乾涸**：市場流動性可能突然消失

---

**報告完成日期：** 2026-02-17  
**下次更新：** 第 2 週結束時（2026-03-03）  
**負責人：** Charlie (AI Assistant)  
**審核：** David (Researcher)