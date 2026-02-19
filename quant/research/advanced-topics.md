# 量化交易深化研究方向

**記錄日期：** 2026-02-17
**來源：** 用戶提供的專業研究方向
**核心思想：** 制度化風險管理與結構化 alpha 生產

---

## 🎯 五大深化研究方向

### 一、跨資產趨勢疊加（Trend Overlay Across Uncorrelated Assets）

#### 對標機構
- **Man AHL**：全球趨勢跟隨
- **Aspect Capital**：系統性趨勢與多策略

#### 為何重要

**核心洞察**：
- 趨勢策略 = 時間分散
- 跨資產 = 結構分散
- 低相關資產同步波動 = 風險溢酬重新定價窗口

**為什麼這重要**：
當 NQ（美股期貨）、GC（黃金）、DX（離岸人民幣）這類低相關商品同步波動時，趨勢強度與相關性結構會發生突變，這正是風險溢酬重新定價的機會。

#### 可深化方向

##### 1. 建立「跨資產同步破位」指標

**實作思路**：
```python
class CrossAssetTrendBreakdown:
    def __init__(self, assets):
        self.assets = assets  # 例如 ['NQ', 'GC', 'DX']

    def calculate_breakdown_indicator(self, window=60):
        """計算跨資產同步破位指標"""
        results = {}

        for asset in self.assets:
            # 獲取當前資產的價格
            current_price = self.get_price(asset)

            # 計算過去 20 日的移動平均線
            ma_20 = self.get_ma(asset, 20)

            # 獲取所有資產的移動平均線
            other_ma = [self.get_ma(a, 20) for a in self.assets if a != asset]

            # 檢查是否同時破位
            all_below_ma = all(other_price <= ma for other_price, ma in zip(other_ma, other_ma))

            # 計算破位後的收益率
            if current_price > ma_20 and all_below_ma:
                forward_return = self.calculate_forward_return(asset, window)
                results[asset] = {
                    'breakdown': True,
                    'forward_return': forward_return
                }
            else:
                results[asset] = {
                    'breakdown': False,
                    'forward_return': 0
                }

        return results
```

##### 2. 研究不同波動 regime 下趨勢半衰期

**實作思路**：
```python
class TrendHalfLifeAnalysis:
    def analyze_regime(self, asset, volatility regimes):
        """分析不同波動 regime 下的趨勢半衰期"""
        regime_results = {}

        for regime in volatility_regimes:
            # 過濾屬於當前 regime 的數據
            regime_data = self.get_regime_data(asset, regime)

            # 計算趨勢（12m 截斷）
            returns = regime_data.pct_change(252)  # 12個月

            # 計算相關係數
            corr = returns.rolling(252).corr(returns.shift(-1))

            # 計算趨勢持續時間（半衰期）
            half_life = self.calculate_half_life(corr)

            regime_results[regime] = {
                'average_half_life': half_life.mean(),
                'half_life_std': half_life.std()
            }

        return regime_results
```

##### 3. 分析兩個負相關資產同跌時的 forward return

**實作思路**：
```python
class NegativeCorrelationTrade:
    def analyze_buy_signal(self, asset1, asset2, lookback=252):
        """分析兩個負相關資產同跌時的 forward return"""
        # 獲取兩個資產的價格
        price1 = self.get_price(asset1)
        price2 = self.get_price(asset2)

        # 計算相關係數
        returns1 = price1.pct_change()
        returns2 = price2.pct_change()
        corr = returns1.rolling(lookback).corr(returns2)

        # 檢測負相關且同跌的情況
        buy_signals = []

        for i in range(lookback, len(price1)):
            # 過去 3 日的表現
            past_3d_returns1 = returns1.iloc[i-3:i].sum()
            past_3d_returns2 = returns2.iloc[i-3:i].sum()

            # 負相關且同跌
            if corr.iloc[i] < 0 and past_3d_returns1 < -0.03 and past_3d_returns2 < -0.03:
                # 計算 forward return
                forward_return = (price1.iloc[i] - price1.iloc[i-3]) / price1.iloc[i-3]
                buy_signals.append({
                    'date': price1.index[i],
                    'asset1': asset1,
                    'asset2': asset2,
                    'forward_return': forward_return,
                    'corr': corr.iloc[i]
                })

        return pd.DataFrame(buy_signals)
```

#### 實作計畫

**階段 1**（1 週）：
- [ ] 收集 3-5 個低相關資產數據（NQ、GC、DX 等）
- [ ] 實作移動平均線
- [ ] 實作相關係數計算
- [ ] 初步回測

**階段 2**（2 週）：
- [ ] 建立「同步破位」指標
- [ ] 分析波動 regime
- [ ] 分析負相關交易

**階段 3**（2 週）：
- [ ] 優化參數
- [ ] 實盤測試
- [ ] 風險管理

---

### 二、純因子風險分解（Factor Decomposition & Risk Budgeting）

#### 對標機構
- **AQR Capital Management**

#### 為何重要

**核心洞察**：
- AQR 核心不在選股，而在風險來源的拆解
- 真正的 alpha 來自風險預算配置，而非單一訊號
- Alpha = β + α + 風險調整

**為什麼這重要**：
許多策略失敗不是因為缺乏 alpha，而是因為風險配置不當。正確的風險預算能顯著提升策略表現。

#### 可深化方向

##### 1. 將 QQQ + GLD + USDU 拆解為三個因子

**實作思路**：
```python
class FactorDecomposition:
    def decompose_portfolio(self, portfolio_prices):
        """將投組拆解為三個因子"""
        results = {}

        # QQQ - 成長因子
        results['growth'] = portfolio_prices['QQQ'].pct_change()

        # GLD - 通膨對沖因子
        results['inflation_hedge'] = portfolio_prices['GLD'].pct_change()

        # USDU - 美元流動性因子
        results['liquidity'] = portfolio_prices['USDU'].pct_change()

        return results

    def extract_factor_betas(self, factor_returns, market_returns):
        """提取因子 beta"""
        # OLS 回歸
        beta = {}

        for factor_name, factor_ret in factor_returns.items():
            X = sm.add_constant(market_returns)
            y = factor_ret
            model = sm.OLS(y, X).fit()
            beta[factor_name] = model.params['QQQ']  # 假設 QQQ 是市場指標

        return beta
```

##### 2. 應用 Equal Risk Contribution（ERC）於月度波動

**實作思路**：
```python
class ERCPortfolio:
    def calculate_erc_weights(self, asset_returns, target_volatility=0.15):
        """計算等風險分配權重"""
        # 計算每個資產的波動率
        volatilities = asset_returns.rolling(252).std()

        # 初始權重（等權）
        weights = np.ones(len(asset_returns.columns)) / len(asset_returns.columns)

        # 迭代優化找到等風險權重
        for _ in range(100):
            # 計算當前投組波動率
            portfolio_vol = np.sqrt(weights @ volatilities.T @ weights)

            # 計算邊際風險貢獻
            marginal_risk_contribution = volatilities * weights

            # 計算目標波動率
            target_mc = portfolio_vol / len(weights)

            # 更新權重
            weights = weights * (marginal_risk_contribution / target_mc)

            # 正規化權重
            weights = weights / weights.sum()

        return weights
```

##### 3. 建立動態槓桿 = 目標波動 / 實際波動

**實作思路**：
```python
class VolatilityTargeting:
    def __init__(self, target_volatility=0.15):
        self.target_volatility = target_volatility

    def calculate_dynamic_leverage(self, asset_returns, window=252):
        """計算動態槓桿"""
        # 計算實際波動率
        realized_vol = asset_returns.rolling(window).std()

        # 計算動態槓桿
        leverage = self.target_volatility / realized_vol

        # 限制槓桿範圍（避免過度槓桿）
        leverage = np.clip(leverage, 0.5, 3.0)

        return leverage

    def apply_leverage(self, portfolio_prices, leverage):
        """應用槓桿到投組"""
        returns = portfolio_prices.pct_change()

        # 調整後的回報 = 槓桿 * 實際回報
        leveraged_returns = returns * leverage

        # 調整後的價格 = 原價格 * 槓桿
        leveraged_prices = portfolio_prices * leverage

        return leveraged_returns, leveraged_prices
```

#### 實作計畫

**階段 1**（1 週）：
- [ ] 收集 QQQ、GLD、USDU 數據
- [ ] 實作因子分解
- [ ] 實作 ERC 算法

**階段 2**（2 週）：
- [ ] 實作動態槓桿
- [ ] 回測驗證
- [ ] 與等權對比

**階段 3**（1 週）：
- [ ] 優化參數
- [ ] 實盤測試
- [ ] 風險分析

---

### 三、Alpha 工廠思維（Mass Signal Generation）

#### 對標機構
- **WorldQuant**

#### 為何重要

**核心洞察**：
- WorldQuant 核心不是單一模型，而是數千個弱 alpha 的聚合
- 關鍵在於：訊號彼此低相關，且成本可控
- 不是追求強 single alpha，而是建立選擇機制

**為什麼這重要**：
單一訊號容易失效，但許多弱訊號的聚合可以形成穩定的策略。這是世界 quant 的核心優勢。

#### 可深化方向

##### 1. 建立 mini alpha library（20 個簡單指標）

**實作思路**：
```python
class MiniAlphaLibrary:
    def __init__(self):
        self.alphas = {
            'MA_Cross': self.ma_cross,
            'RSI': self.rsi,
            'MACD': self.macd,
            'BB_Width': self.bb_width,
            'VolRatio': self.vol_ratio,
            # ... 20 個指標
        }

    def ma_cross(self, prices, fast=10, slow=20):
        """移動平均線交叉"""
        ma_fast = prices.rolling(fast).mean()
        ma_slow = prices.rolling(slow).mean()

        # 金叉做多，死叉做空
        signal = (ma_fast > ma_slow) - (ma_fast <= ma_slow)
        return signal

    def rsi(self, prices, period=14):
        """RSI 指標"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return (rsi - 50) / 50  # 正規化到 -1 到 1

    # ... 其他 18 個指標

    def generate_all_alphas(self, prices):
        """生成所有 alpha"""
        results = {}

        for name, alpha_func in self.alphas.items():
            results[name] = alpha_func(prices)

        return pd.DataFrame(results)

    def calculate_ic(self, alpha_signals, future_returns, window=60):
        """計算信息係數（IC）"""
        ics = []

        for i in range(window, len(alpha_signals)):
            current_alpha = alpha_signals.iloc[i-window:i]
            current_returns = future_returns.iloc[i-window:i]

            # 計算相關係數
            ic = current_alpha.corr(current_returns)
            ics.append(ic)

        return pd.Series(ics)

    def calculate_ir(self, alpha_signals, future_returns, window=60):
        """計算信息比率（IR）"""
        ics = self.calculate_ic(alpha_signals, future_returns, window)

        # 計算平均 IC
        mean_ic = ics.mean()

        # 計算 IC 的標準差
        ic_std = ics.std()

        # 計算 IR = 平均 IC / IC 標準差
        ir = mean_ic / ic_std if ic_std > 0 else 0

        return ir
```

##### 2. 透過 rolling IC + IR 篩選

**實作思路**：
```python
class AlphaFilter:
    def filter_by_performance(self, alpha_library, asset_returns, 
                             min_ic=0.01, min_ir=0.5):
        """篩選表現好的 alpha"""
        selected_alphas = {}

        for alpha_name, alpha_signal in alpha_library.items():
            # 計算過去 60 天的 IC
            ics = alpha_signal.rolling(60).corr(asset_returns)

            # 計算 IR
            mean_ic = ics.mean()
            ic_std = ics.std()
            ir = mean_ic / ic_std if ic_std > 0 else 0

            # 篩選
            if mean_ic >= min_ic and ir >= min_ir:
                selected_alphas[alpha_name] = {
                    'ic': mean_ic,
                    'ir': ir,
                    'alpha_signal': alpha_signal
                }

        return selected_alphas

    def monitor_alpha_decay(self, alpha_library, asset_returns, window=252):
        """監控 alpha 衰退速度"""
        decay_info = {}

        for alpha_name, alpha_signal in alpha_library.items():
            # 計算過去 252 天的 IC 序列
            ics = alpha_signal.rolling(252).corr(asset_returns)

            # 計算 IC 衰退速度（斜率）
            ic_series = ics.dropna()
            if len(ic_series) > 10:
                slope = np.polyfit(
                    np.arange(len(ic_series)), 
                    ic_series.values, 
                    1
                )[0]

                decay_info[alpha_name] = {
                    'current_ic': ic_series.iloc[-1],
                    'ic_slope': slope,
                    'is_decaying': slope < 0
                }
            else:
                decay_info[alpha_name] = {
                    'current_ic': 0,
                    'ic_slope': 0,
                    'is_decaying': False
                }

        return decay_info
```

#### 實作計畫

**階段 1**（1 週）：
- [ ] 實作 20 個簡單指標
- [ ] 建立 alpha library
- [ ] 實作 IC/IR 計算

**階段 2**（2 週）：
- [ ] Alpha 篩選機制
- [ ] Alpha 衰退監控
- [ ] Alpha 聚合策略

**階段 3**（2 週）：
- [ ] 優化選擇策略
- [ ] 實盤測試
- [ ] 成本分析

---

### 四、極端市場下的資產耗竭風險（Tail Risk & Capital Decay）

#### 對標機構
- **Renaissance Technologies**
- **D. E. Shaw & Co.**

#### 為何重要

**核心洞察**：
- 真正頂級基金的秘密不在高報酬，而在避免爆倉
- Alpha 不是最終目標，保留資本是首要目標
- 這與退休提領模型完全相容

**為什麼這重要**：
策略失敗通常不是因為缺乏 alpha，而是因為極端情況下的爆倉。頂級基金在這方面有著深厚的研究。

#### 可深化方向

##### 1. 模擬「前五年 -50%」順序風險

**實作思路**：
```python
class SequenceRiskAnalysis:
    def simulate_sequence_risk(self, returns, initial_capital=1000000,
                              target_level=500000, years=5):
        """模擬順序風險（前五年 -50%）"""
        simulated_capitals = []

        for i in range(10000):  # 模擬 10000 種情況
            capital = initial_capital
            sequence_failed = False

            for year in range(years):
                # 隨機選擇一年的回報（從數據中重複採樣）
                year_return = returns.sample().values[0]

                # 計算下一年
                capital = capital * (1 + year_return)

                # 檢查是否跌破目標
                if capital <= target_level:
                    sequence_failed = True
                    break

            simulated_capitals.append(capital)

        # 計算成功率
        success_rate = sum(1 for cap in simulated_capitals if cap > target_level) / len(simulated_capitals)

        # 計算期望值
        expected_final = np.mean(simulated_capitals)

        return {
            'success_rate': success_rate,
            'expected_final': expected_final,
            'simulated_capitals': simulated_capitals
        }
```

##### 2. 建立資產耗竭臨界值模型

**實作思路**：
```python
class CapitalDepletionModel:
    def calculate_depletion_threshold(self, asset_prices, initial_capital,
                                     withdrawal_rate=0.04):
        """計算資產耗竭臨界值"""
        depletion_thresholds = []

        # 模擬不同市場情況
        for scenario in ['bull', 'bear', 'volatile']:
            if scenario == 'bull':
                scenario_returns = self.get_bull_market_returns()
            elif scenario == 'bear':
                scenario_returns = self.get_bear_market_returns()
            else:
                scenario_returns = self.get_volatility_market_returns()

            capital = initial_capital
            years_until_depletion = 0

            while capital > 0 and years_until_depletion < 50:
                capital = capital * (1 + scenario_returns.iloc[years_until_depletion] - withdrawal_rate)
                years_until_depletion += 1

            depletion_thresholds.append({
                'scenario': scenario,
                'years_until_depletion': years_until_depletion,
                'final_capital': capital
            })

        return pd.DataFrame(depletion_thresholds)

    def set_critical_capital(self, initial_capital, safety_factor=1.5):
        """設定臨界資本"""
        # 臨界資本 = 初始資本 * 安全係數
        critical_capital = initial_capital / safety_factor

        return critical_capital
```

##### 3. 設計「反脆弱再平衡」機制

**實作思路**：
```python
class AntifragileRebalancing:
    def __init__(self, critical_capital):
        self.critical_capital = critical_capital
        self.initial_capital = initial_capital

    def rebalance_on_capital_decline(self, current_capital, asset_allocation):
        """當資本下降時再平衡"""
        if current_capital < self.critical_capital:
            # 計算需要多少來回到初始水平
            recovery_needed = self.initial_capital - current_capital

            # 調整資產配置
            new_allocation = self._adjust_allocation(asset_allocation, recovery_needed)

            # 執行再平衡交易
            trades = self._execute_rebalance(asset_allocation, new_allocation)

            return {
                'action': 'rebalance',
                'current_capital': current_capital,
                'critical_capital': self.critical_capital,
                'recovery_needed': recovery_needed,
                'new_allocation': new_allocation,
                'trades': trades
            }
        else:
            return {
                'action': 'no_action',
                'current_capital': current_capital
            }

    def _adjust_allocation(self, allocation, recovery_needed):
        """調整資產配置"""
        # 根據回復需求調整
        target_allocation = allocation.copy()

        # 降低風險資產比例
        target_allocation['equities'] *= 0.7
        target_allocation['bonds'] *= 1.2

        # 正規化
        total = sum(target_allocation.values())
        target_allocation = {k: v/total for k, v in target_allocation.items()}

        return target_allocation

    def _execute_rebalance(self, old_allocation, new_allocation):
        """執行再平衡交易"""
        trades = []

        for asset in old_allocation:
            if asset in new_allocation:
                change = new_allocation[asset] - old_allocation[asset]

                if abs(change) > 0.01:  # 閾值
                    trades.append({
                        'asset': asset,
                        'change': change,
                        'action': 'buy' if change > 0 else 'sell'
                    })

        return trades
```

#### 實作計畫

**階段 1**（1 週）：
- [ ] 實作順序風險模擬
- [ ] 計算耗竭臨界值
- [ ] 設定臨界資本

**階段 2**（2 週）：
- [ ] 實作反脆弱再平衡
- [ ] 回測風險管理效果
- [ ] 與固定再平衡對比

**階段 3**（1 週）：
- [ ] 優化參數
- [ ] 實盤測試
- [ ] 風險分析

---

### 五、流動性與市場結構（Microstructure Edge）

#### 對標機構
- **Citadel**

#### 為何重要

**核心洞察**：
- 高頻不必複製，但市場結構理解必須吸收
- 這能避免回測勝利、實盤崩解的情況

**為什麼這重要**：
許多策略在回測中表現很好，但實盤時因為流動性問題、交易成本等原因表現很差。理解市場結構能避免這個問題。

#### 可深化方向

##### 1. 研究期貨換月對策略影響

**實作思路**：
```python
class FuturesRollEffect:
    def analyze_roll_effect(self, futures_data, contract_roll_dates):
        """分析期貨換月效應"""
        results = {}

        for i in range(len(contract_roll_dates) - 1):
            current_contract = contract_roll_dates[i]
            next_contract = contract_roll_dates[i+1]

            # 獲取換月前的表現
            performance_before = self.calculate_performance(
                futures_data[current_contract],
                days=20
            )

            # 獲取換月後的表現
            performance_after = self.calculate_performance(
                futures_data[next_contract],
                days=20
            )

            # 計算換月效應
            roll_effect = performance_after - performance_before

            results[current_contract] = {
                'performance_before': performance_before,
                'performance_after': performance_after,
                'roll_effect': roll_effect
            }

        return pd.DataFrame(results).T

    def adjust_for_roll_effect(self, strategy_returns, roll_effects):
        """調整策略回報以反映換月效應"""
        adjusted_returns = []

        for i in range(len(strategy_returns)):
            # 獲取對應的換月效應
            roll_effect = roll_effects.iloc[i]

            # 調整回報
            adjusted_return = strategy_returns.iloc[i] - roll_effect
            adjusted_returns.append(adjusted_return)

        return pd.Series(adjusted_returns)
```

##### 2. 觀察量縮與趨勢轉折關係

**實作思路**：
```python
class VolumeTrendAnalysis:
    def analyze_volume_trend_reversal(self, prices, volumes):
        """分析量縮與趨勢轉折關係"""
        analysis = []

        for i in range(30, len(prices)):
            # 過去 20 日的量能
            past_20d_volume = volumes.iloc[i-30:i].mean()

            # 當前量能
            current_volume = volumes.iloc[i]

            # 計算量能比率
            volume_ratio = current_volume / past_20d_volume

            # 計算價格變動
            price_change = (prices.iloc[i] - prices.iloc[i-5]) / prices.iloc[i-5]

            # 趨勢方向
            trend_direction = 'up' if prices.iloc[i] > prices.iloc[i-10] else 'down'

            # 判斷量縮與趨勢轉折
            is_volatile_shrinkage = volume_ratio < 0.7
            is_trend_reversal = (trend_direction == 'up' and price_change < 0) or \
                              (trend_direction == 'down' and price_change > 0)

            analysis.append({
                'date': prices.index[i],
                'volume_ratio': volume_ratio,
                'price_change': price_change,
                'trend_direction': trend_direction,
                'is_volatile_shrinkage': is_volatile_shrinkage,
                'is_trend_reversal': is_trend_reversal,
                'significance': is_volatile_shrinkage and is_trend_reversal
            })

        return pd.DataFrame(analysis)

    def detect_volume_breakout(self, prices, volumes, threshold=0.5):
        """檢測量能突破"""
        volume_breakouts = []

        for i in range(10, len(prices)):
            # 計算 20 日均量
            avg_volume = volumes.iloc[i-10:i].mean()

            # 當前量能
            current_volume = volumes.iloc[i]

            # 檢測量能突破
            if current_volume > avg_volume * (1 + threshold):
                # 判斷價格方向
                price_change = (prices.iloc[i] - prices.iloc[i-5]) / prices.iloc[i-5]

                volume_breakouts.append({
                    'date': prices.index[i],
                    'current_volume': current_volume,
                    'avg_volume': avg_volume,
                    'breakout_ratio': current_volume / avg_volume,
                    'price_change': price_change,
                    'direction': 'up' if price_change > 0 else 'down'
                })

        return pd.DataFrame(volume_breakouts)
```

##### 3. 分析交易成本對 IR 的侵蝕速度

**實作思路**：
```python
class TransactionCostAnalysis:
    def calculate_impact_on_ir(self, returns, transaction_cost=0.0001, 
                              frequency=20):
        """計算交易成本對 IR 的侵蝕"""
        costs = []

        for i in range(frequency, len(returns)):
            # 計算過去頻率天的回報
            past_returns = returns.iloc[i-frequency:i]

            # 計算平均回報
            avg_return = past_returns.mean()

            # 計算交易成本
            cost = transaction_cost * frequency

            # 實際回報
            actual_return = avg_return - cost

            # 計算標準差（調整後）
            std = past_returns.std()

            # 計算調整後的 IR
            adjusted_ir = (actual_return / std) * np.sqrt(frequency)

            costs.append({
                'day': returns.index[i],
                'avg_return': avg_return,
                'transaction_cost': cost,
                'actual_return': actual_return,
                'std': std,
                'adjusted_ir': adjusted_ir
            })

        return pd.DataFrame(costs)

    def optimize_frequency(self, returns, min_ir=0.5):
        """優化交易頻率以最大化 IR"""
        frequencies = [5, 10, 20, 40, 60, 120]
        results = []

        for freq in frequencies:
            ir = self.calculate_impact_on_ir(returns, frequency=freq)
            best_ir = ir['adjusted_ir'].max()

            results.append({
                'frequency': freq,
                'max_ir': best_ir,
                'recommended': best_ir >= min_ir
            })

        return pd.DataFrame(results)
```

#### 實作計畫

**階段 1**（1 週）：
- [ ] 收集期貨換月數據
- [ ] 實作量縮分析
- [ ] 實作交易成本計算

**階段 2**（2 週）：
- [ ] 分析換月效應
- [ ] 分析量縮與趨勢關係
- [ ] 計算成本對 IR 的影響

**階段 3**（1 週）：
- [ ] 優化交易策略
- [ ] 實盤測試
- [ ] 成本優化

---

## 🎯 建議優先順序

依既有研究基礎：

```
1️⃣ 跨資產同步極端事件
   ↓
2️⃣ 動態風險預算與波動槓桿
   ↓
3️⃣ 順序風險與資本耗竭模型
   ↓
4️⃣ Alpha library 結構化
   ↓
5️⃣ 微結構優化
```

---

## 💡 核心思想

### 頂級量化基金的秘密

**不是神秘公式，而是**：
- ✅ 制度化風險管理
- ✅ 結構化 alpha 生產
- ✅ 資本配置邏輯
- ✅ 避免爆倉比追求高報酬更重要

**真正的差異來自**：
- 風險預算配置（而非單一訊號）
- 結構化 alpha 聚合（而非單一強模型）
- 極端風險管理（而非短期報酬最大化）

---

## 📊 與既有研究的關聯

### 1. 與 ERC 研究的關聯
- ERC = 等風險分配
- 跨資產同步 = 風險分散
- 兩者結合 = 完美的風險配置

### 2. 與動態槓桿的關聯
- 波動率目標 = 動態槓桿
- 關聯：控制波動率 = 控制風險

### 3. 與 Multi-factor 的關聯
- Alpha library = 多因子聚合
- IC/IR 篩選 = 因子選擇

### 4. 與回測的關聯
- 微結構分析 = 改善回測準確性
- 順序風險 = 考慮極端情況

---

## 🚀 下一步行動

### 本週
- [ ] 確認優先順序（可能調整）
- [ ] 開始第一個主題的研究
- [ ] 建立對應的資料結構
- [ ] 實作基礎代碼

### 下週
- [ ] 完成 3 個主題的初步實作
- [ ] 開始回測
- [ ] 記錄發現與問題

### 本月
- [ ] 完成 5 個主題的基礎框架
- [ ] 進行比較分析
- [ ] 優化參數

---

**記錄完成日期：** 2026-02-17
**下次更新：** 有新發現或調整時
