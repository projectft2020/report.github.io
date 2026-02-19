# 跨資產動能 + 動態風險預算 + 極端情境壓力測試 - 完整研究計畫

**啟動日期：** 2026-02-17
**對標機構：** Man AHL、AQR Capital Management、Renaissance Technologies
**核心精神：** 制度化風險控制優先於報酬追逐；結構勝於預測；資本存活率高於短期勝率

---

## 📊 研究框架總覽

### 三大核心支柱

```
支柱 1：跨資產動能模型
├─ 基礎動能（MA 交叉）
├─ 同步極端事件偵測
└─ Regime 切換分析

支柱 2：動態風險預算
├─ 波動目標化（Volatility Targeting）
├─ Equal Risk Contribution（ERC）
└─ 槓桿控制規則

支柱 3：極端情境壓力測試
├─ 歷史危機模擬（2008、2020）
├─ 順序風險（Monte Carlo）
├─ 資本耗竭模型
└─ VaR / CVaR 分析
```

---

## 第一部分：制度設計（Institutional Architecture）

### ① 資產選擇邏輯

#### 結構低相關原則
我們選擇四個 ETF，它們在不同經濟週期中有不同的表現，實現結構分散：

| 資產 | 經濟因子 | 特點 | 低相關性 |
|------|---------|------|---------|
| **QQQ** | 成長、科技 | 納斯達克 100，高動量 | 與 GLD 負相關 |
| **GLD** | 通膨、避險 | 黃金，貨幣貶值對沖 | 與 QQQ 低相關 |
| **UUP** | 美元流動性 | 美元指數期貨 | 與其他資產低相關 |
| **TLT** | 利率風險 | 20 年期美債期貨 | 與股票負相關 |

#### 為什麼選 ETF 而非期貨？
1. ✅ **更容易取得**：ETF 任何券商都能買
2. ✅ **手續費更低**：期貨手續費高，ETF 低
3. ✅ **長期持有友好**：ETF 可以長期持有，不需要換月
4. ✅ **流動性更好**：ETF 市場深度更深

#### 最低資產配置（建議）
- **保守配置**：QQQ 50% + GLD 25% + UUP 25%
- **激進配置**：QQQ 60% + GLD 20% + UUP 20% + TLT 0%
- **對沖配置**：QQQ 40% + GLD 30% + UUP 20% + TLT 10%

---

### ② 風險框架（三層防護）

#### A 層：波動目標化（Volatility Targeting）

**核心思想**：不是追求最大收益，而是追求目標波動

**目標設定**：
```python
目標年化波動 = 10% - 15%
實際年化波動 = 近 60 日波動 * sqrt(252)
動態槓桿 = 目標波動 / 實際波動
```

**槓桿控制規則**：
```python
if 實際波動 > 15%:
    槓桿 = 0.7 倍  # 降低曝險
elif 實際波動 < 8%:
    槓桿 = 1.2 倍  # 增加持續性
else:
    槓桿 = 1.0 倍  # 正常水平
```

**為什麼這樣設？**
- ✅ **防止過度槓桿**：高波動時降低槓桿
- ✅ **增加抗跌性**：低波動時提高槓桿
- ✅ **符合 Kelly 公式**：波動率調整槓桿

---

#### B 層：Equal Risk Contribution（ERC）

**核心思想**：每個資產貢獻相同風險，而非相同資金

**完整 ERC（機構級）**：
```python
# 1. 計算協方差矩陣
cov_matrix = returns.cov()

# 2. 計算當前權重下的邊際風險貢獻
marginal_risk_contribution = (cov_matrix @ weights) * weights

# 3. 計算目標風險貢獻（總風險 / n 個資產）
target_risk_contribution = portfolio_variance / n

# 4. 調整權重（迭代優化）
# 重複 100 次
for _ in range(100):
    weights = weights * (marginal_risk_contribution / target_risk_contribution)
    weights = weights / weights.sum()  # 正規化
```

**簡化 ERC（個人級）**：
```python
# 每個資產的波動率
volatilities = returns.rolling(60).std() * np.sqrt(252)

# 初始權重 = 1 / 波動率
weights = 1 / volatilities

# 正規化
weights = weights / weights.sum()
```

**兩者的關係**：
- ✅ **簡化 ERC 足夠好**：效果與完整 ERC 接近
- ✅ **計算簡單**：不需要協方差矩陣
- ✅ **容易調整**：每月重新計算

---

#### C 層：極端情境壓力測試

**核心思想**：不是避免虧損，而是避免資本死亡

**模擬情境**：

**1. 歷史危機模擬**：
- 2008 金融危机：標準化到 -50% 最大回撤
- 2020 疫情崩盤：標準化到 -30% 最大回撤

**2. 順序風險（Order Risk）**：
```python
# 隨機打亂報酬順序 10,000 次
simulations = 10000

for _ in range(simulations):
    # 隨機打亂報酬順序
    shuffled_returns = returns.sample(frac=1).values

    # 計算資本變化
    capital = initial_capital
    for ret in shuffled_returns:
        capital = capital * (1 + ret)

    # 計算最大回撤
    drawdown = calculate_max_drawdown(capital)
    drawdowns.append(drawdown)

# 計算資本死亡概率
death_prob = np.mean([dd < -0.8 for dd in drawdowns])
```

**3. 資本耗竭模型**：
```python
# 最大連續虧損期
max_consecutive_loss = 0
current_loss = 0

for ret in returns:
    if ret < 0:
        current_loss += 1
        max_consecutive_loss = max(max_consecutive_loss, current_loss)
    else:
        current_loss = 0

# 95% VaR
var_95 = np.percentile(returns, 5)

# 期望最大回撤
expected_max_drawdown = np.mean(drawdowns)
```

---

## 第二部分：Alpha 結構（Signal Generation）

### ③ 基礎動能模型

**核心思想**：僅使用簡單但穩定的指標

**指標**：
- ✅ 10 MA（快線）
- ✅ 60 MA（中線）
- ✅ 200 MA（慢線）

**月度 Rebalance 規則**：

| 條件 | 行為 | 槓桿 |
|------|------|------|
| 所有資產 > 200 MA | 做多 | 1.0 倍 |
| QQQ > 200MA, GLD < 200MA | QQQ 做多，GLD 觀望 | 1.0 倍 |
| QQQ > 60MA > 200MA | 做多（最高回報） | 1.2 倍 |
| 10MA < 60MA < 200MA | 空倉/降低風險 | 0.7 倍 |
| 所有資產 < 200MA | 全面降風險 | 0.5 倍 |

**簡化策略（更實用）**：
1. **只選擇 1 個做多**（回報率最高的）
2. **做多時**：槓桿 = 目標波動 / 實際波動（上限 1.2 倍）
3. **空倉時**：槓桿 = 0.7 倍（等待機會）

---

### ④ 跨資產同步極端訊號

**核心思想**：兩個低相關資產同時下跌 2σ 時是極端事件

**定義 2σ 下跌**：
```python
# 獲取過去 60 日的回報
past_returns = returns.tail(60)

# 計算均值和標準差
mu = past_returns.mean()
sigma = past_returns.std()

# 當前回報 < mu - 2*sigma
if current_return < mu - 2*sigma:
    return True  # 2σ 下跌
```

**測試項目**：

**1. Forward Return 測試**：
```python
# 找到同步 2σ 下跌的點
extreme_events = []

for i in range(60, len(returns)):
    # 檢查是否兩資產同跌 2σ
    if qqq_2sigma[i] and gld_2sigma[i]:
        # 計算 forward return
        forward_5d = (prices[i+5] - prices[i]) / prices[i]
        forward_10d = (prices[i+10] - prices[i]) / prices[i]
        forward_20d = (prices[i+20] - prices[i]) / prices[i]

        extreme_events.append({
            'date': dates[i],
            'forward_5d': forward_5d,
            'forward_10d': forward_10d,
            'forward_20d': forward_20d
        })

# 計算條件勝率
win_rate = np.mean([ret > 0 for ret in [e['forward_20d'] for e in extreme_events]])
```

**2. Regime 分類**：
```python
def classify_regime(current_volatility):
    if current_volatility > 15%:
        return 'high_volatility'
    elif current_volatility > 8%:
        return 'medium_volatility'
    else:
        return 'low_volatility'
```

**3. 極端事件策略**：
```python
# 當 QQQ 跌破 200MA 且 GLD 同跌
if qqq_broken_200ma and gld_falling:
    # 降低整體曝險 50%
    reduce_position_size(0.5)
```

---

## 第三部分：資本存活模型（Capital Survival Model）

### ⑤ 資本耗竭臨界點

**定義**：資本死亡 = 資本低於可承受的底線

**臨界值設定**：
```python
# 可承受的最大回撤
max_acceptable_drawdown = 30%

# 資本死亡定義
capital_death = portfolio_value < initial_capital * (1 - max_acceptable_drawdown)
```

**建立模型**：
```python
# 最大連續虧損期
max_consecutive_loss = 0
current_consecutive_loss = 0

for ret in returns:
    if ret < 0:
        current_consecutive_loss += 1
        max_consecutive_loss = max(max_consecutive_loss, current_consecutive_loss)
    else:
        current_consecutive_loss = 0

# 95% VaR
var_95 = np.percentile(returns, 5)

# CVaR（尾部期望虧損）
cvar_95 = np.mean(returns[returns <= var_95])

# 期望最大回撤（10000 次模擬）
simulations = 10000
drawdowns = []

for _ in range(simulations):
    simulated_returns = returns.sample(frac=1).values
    capital = initial_capital

    for ret in simulated_returns:
        capital = capital * (1 + ret)

    drawdown = (initial_capital - capital) / initial_capital
    drawdowns.append(drawdown)

expected_max_drawdown = np.mean(drawdowns)
death_prob = np.mean([dd < max_acceptable_drawdown for dd in drawdowns])
```

---

### ⑥ 順序風險模擬（Monte Carlo）

**核心思想**：隨機打亂報酬順序，測試資本的生存概率

**方法**：
```python
simulations = 10000
capital_survival_prob = 0

for _ in range(simulations):
    # 隨機打亂報酬順序
    shuffled_returns = returns.sample(frac=1).values

    # 計算資本變化
    capital = initial_capital
    for ret in shuffled_returns:
        capital = capital * (1 + ret)

    # 檢查是否存活
    if capital > initial_capital * 0.7:  # 存活條件
        capital_survival_prob += 1

capital_survival_prob /= simulations
```

**退休提領情境測試**：
```python
# 模擬每年提領 4%
annual_withdrawal_rate = 0.04

for _ in range(simulations):
    capital = initial_capital
    shuffled_returns = returns.sample(frac=1).values

    for ret in shuffled_returns:
        # 扣除提領
        capital = capital * (1 + ret - annual_withdrawal_rate)
        capital = max(capital, 0)  # 不允許負資本

    # 計算生存年數
    years_survived = 0
    for _ in range(100):
        if capital > 0:
            capital = capital * (1 + annual_withdrawal_rate)
            years_survived += 1
        else:
            break

    survival_years.append(years_survived)
```

**動態槓桿測試**：
```python
# 在極端前期崩盤下是否加速死亡？

# 模擬「前期崩盤 + 後期好轉」
for _ in range(simulations):
    # 前 30% 交易是崩盤
    shuffled_returns = returns.sample(frac=1).values
    bad_returns = shuffled_returns[:int(len(shuffled_returns)*0.3)]
    good_returns = shuffled_returns[int(len(shuffled_returns)*0.3):]

    capital = initial_capital

    # 前 30% 崩盤
    for ret in bad_returns:
        capital = capital * (1 + ret)

    # 後 70% 好轉（但槓桿高）
    for ret in good_returns:
        capital = capital * (1 + ret * 1.5)  # 槓桿 1.5 倍

    drawdown = (initial_capital - capital) / initial_capital
    drawdowns.append(drawdown)
```

---

## 第四部分：可執行實作（Implementation）

### 🔹 工具
- ✅ Python 3.8+
- ✅ yfinance（數據載入）
- ✅ numpy、pandas、matplotlib（計算和可視化）
- ✅ TradingView + Pine Script（監控和執行）

### 簡化版本架構

#### 1️⃣ 資產配置
```python
assets = ['QQQ', 'GLD', 'UUP', 'TLT']
```

#### 2️⃣ 風險管理簡化
```python
def calculate_weights(returns):
    # 計算近 60 日波動率
    vol = returns.rolling(60).std() * np.sqrt(252)

    # 計算權重
    weights = 1 / vol
    weights = weights / weights.sum()

    return weights
```

#### 3️⃣ 槓桿控制
```python
def calculate_leverage(portfolio_volatility):
    if portfolio_volatility > 0.15:
        return 0.7
    elif portfolio_volatility < 0.08:
        return 1.2
    else:
        return 1.0
```

#### 4️⃣ 極端事件策略
```python
def check_extreme_event(qqq_prices, gld_prices):
    # QQQ 跌破 200MA
    qqq_200ma = qqq_prices.rolling(200).mean()
    qqq_broken = qqq_prices < qqq_200ma

    # GLD 同跌
    gld_falling = gld_prices.pct_change().rolling(5).sum() < -0.03

    # 兩者同時發生
    if qqq_broken & gld_falling:
        return True
    else:
        return False
```

---

## 第五部分：12 週研究藍圖

### 第 1-2 週：建立基礎動能 + 回測
**目標**：完成基礎動能策略並回測

**任務**：
- [ ] 收集 QQQ + GLD + UUP + TLT 數據（yfinance）
- [ ] 計算 10 / 60 / 200 MA
- [ ] 實作基礎動能策略
  - [ ] 做多/空倉規則
  - [ ] 月度 rebalance
- [ ] 基礎回測
  - [ ] 初始資本 $100,000
  - [ ] 交易成本 0.1%
  - [ ] 滑點 0.05%

**預期輸出**：
- [ ] 策略回測報告
- [ ] Sharpe Ratio > 1.0
- [ ] 最大回撤 < 20%

---

### 第 3-4 週：加入波動目標化
**目標**：實作動態槓桿

**任務**：
- [ ] 計算近 60 日波動率
- [ ] 實作動態槓桿
  - [ ] 波動 > 15% → 0.7 倍
  - [ ] 波動 < 8% → 1.2 倍
  - [ ] 波動 8-15% → 1.0 倍
- [ ] 槓桿優化
  - [ ] 測試不同目標波動（10%、12%、15%）
  - [ ] 測試不同槓桿範圍（0.5-1.5）

**預期輸出**：
- [ ] 動態槓桿回測報告
- [ ] 與固定槓桿對比
- [ ] 找出最佳參數

---

### 第 5-6 週：加入 ERC
**目標**：實作等風險分配

**任務**：
- [ ] 實作簡化 ERC
  - [ ] 權重 = 1 / 波動率
  - [ ] 每月調整一次
- [ ] 與等權對比
  - [ ] ERC 的 Sharpe Ratio
  - [ ] ERC 的最大回撤
  - [ ] ERC 的波動率
- [ ] 最佳化參數
  - [ ] 窗口期（30、60、90、120）
  - [ ] 調整頻率（日線、週線、月線）

**預期輸出**：
- [ ] ERC 回測報告
- [ ] ERC vs 等權對比
- [ ] 最佳 ERC 參數

---

### 第 7-8 週：同步極端事件測試
**目標**：實作同步極端訊號

**任務**：
- [ ] 實作 2σ 下跌檢測
- [ ] 測試 forward return
  - [ ] 5 日、10 日、20 日回報
  - [ ] 條件勝率
- [ ] Regime 分類
  - [ ] 高波動 / 中波動 / 低波動
  - [ ] 不同 regime 的表現
- [ ] 極端事件策略
  - [ ] QQQ 跌破 200MA 且 GLD 同跌
  - [ ] 降低曝險 50%

**預期輸出**：
- [ ] 同步極端事件報告
- [ ] Forward return 分析
- [ ] 極端事件策略回測

---

### 第 9-10 週：Monte Carlo 模擬
**目標**：測試資本存活概率

**任務**：
- [ ] 實作順序風險模擬
  - [ ] 隨機打亂報酬順序 10,000 次
  - [ ] 計算資本耗盡概率
- [ ] 退休提領情境測試
  - [ ] 每年提領 3%、4%、5%
  - [ ] 100 年生存概率
- [ ] 動態槓桿測試
  - [ ] 極端前期崩盤測試
  - [ ] 是否加速死亡？

**預期輸出**：
- [ ] 資本存活概率報告
- [ ] 退休提領生存概率
- [ ] 槓桿影響分析

---

### 第 11-12 週：壓力測試 + 交易成本修正
**目標**：完善策略

**任務**：
- [ ] 歷史危機模擬
  - [ ] 2008 金融危机
  - [ ] 2020 疫情崩盤
  - [ ] 2000 互聯網泡沫
- [ ] 加入交易成本
  - [ ] 手續費 0.1%
  - [ ] 滑點 0.05%
  - [ ] 每月調整成本
- [ ] 最終優化
  - [ ] 整合所有組件
  - [ ] 最終回測
  - [ ] 實盤準備

**預期輸出**：
- [ ] 壓力測試報告
- [ ] 交易成本修正後的回測
- [ ] 最終策略優化

---

## 第六部分：進階升級方向

### 若研究成熟，可延伸：
1. **Regime Switching（馬可夫轉換）**
   - 高波動 / 中波動 / 低波動 regime
   - regime 切換概率
   - regime-based 選擇

2. **Drawdown-based Leverage Control**
   - 根據最大回撤調整槓桿
   - 動態止損
   - 風險平價調整

3. **CDS 或 VIX 作為恐慌因子**
   - VIX 高 = 恐慌，降低槓桿
   - CDS spread = 債務風險
   - 恐慌因子調整風險配置

4. **期貨版本設計**
   - 將 ETF 策略改為期貨
   - 考慮期貨換月
   - 期貨槓桿優化

5. **AI 增強**
   - 機器學習預測 regime
   - 深度學習優化槓桿
   - 情緒分析

---

## 💡 核心原則

### 預測無法穫定複製
- ❌ 不追求單一強訊號
- ✅ 追求穩定的結構

### 結構可以穩定複製
- ✅ 波動率目標化
- ✅ 風險預算
- ✅ 多資產分散

### 槓桿必須服從波動
- ✅ 波動高 → 降低槓桿
- ✅ 波動低 → 提高槓桿

### 資本存活率高於短期報酬
- ✅ 避免爆倉
- ✅ 長期複利
- ✅ 風險調整後報酬

---

## 🎯 成功指標

### 必須達到的目標
1. **Sharpe Ratio > 1.0**
   - 風險調整後報酬良好

2. **最大回撤 < 20%**
   - 資本存活率高

3. **年化回報 > 10%**
   - 超越市場表現

4. **順序風險測試通過**
   - 資本死亡概率 < 10%

5. **壓力測試通過**
   - 2008、2020 危機存活

### 優先目標
1. ⭐⭐⭐⭐⭐ **資本存活**：避免爆倉
2. ⭐⭐⭐⭐⭐ **風險調整報酬**：Sharpe > 1
3. ⭐⭐⭐⭐ **穩定性**：低夏普 ratio 的波動
4. ⭐⭐⭐⭐ **結構性**：多資產分散

### 次要目標
1. 高頻 Alpha
2. 複雜的機器學習
3. 尖端的算法交易

---

## 📊 實作檢查清單

### 環境設定
- [ ] 安裝 Python 3.8+
- [ ] 安裝 yfinance
- [ ] 安裝 numpy、pandas、matplotlib
- [ ] 安裝 scikit-learn（機器學習）
- [ ] 設定工作目錄

### 數據準備
- [ ] 下載 QQQ 歷史數據
- [ ] 下載 GLD 歷史數據
- [ ] 下載 UUP 歷史數據
- [ ] 下載 TLT 歷史數據
- [ ] 數據驗證與清洗

### 策略開發
- [ ] 實作 MA 計算
- [ ] 實作基礎動能策略
- [ ] 實作動態槓桿
- [ ] 實作 ERC
- [ ] 實作極端事件檢測

### 回測
- [ ] 基礎回測
- [ ] 交易成本測試
- [ ] 滑點測試
- [ ] 不同參數優化

### 風險分析
- [ ] VaR 計算
- [ ] CVaR 計算
- [ ] 順序風險模擬
- [ ] Monte Carlo 模擬

### 壓力測試
- [ ] 2008 危機模擬
- [ ] 2020 危機模擬
- [ ] 2000 危機模擬

### 實盤準備
- [ ] 實作監控系統
- [ ] 設定警示條件
- [ ] 實作調整機制
- [ ] 記錄與日誌

---

## 🔍 待解決問題

### 短期（本週）
1. [ ] 選擇最適合的資產組合
2. [ ] 確定最佳參數（窗口期、槓桿範圍）
3. [ ] 建立數據載入模組

### 中期（下個月）
1. [ ] 完成基礎動能策略
2. [ ] 實作動態槓桿
3. [ ] 完成 ERC
4. [ ] 第一次回測

### 長期（3 個月）
1. [ ] 完成全部 12 週研究
2. [ ] 通過壓力測試
3. [ ] 實盤準備完成
4. [ ] 實盤執行

---

## 📚 參考資源

### 論文
- [AQR Factor Research Papers](https://www.aqr.com/Insights/Research)
- [Man AHL Research](https://www.manahm.com/Insights)
- [Renaissance Technologies Research](https://www.rentec.com/)

### 書籍
- [《Quantitative Portfolio Management》](https://www.aqr.com/) - AQR
- [《Volatility Trading》](https://www.wiley.com/) - Euan Sinclair
- [《Algorithmic Trading》](https://www.cengage.com/) - Ernest P. Chan

### 網站
- [yfinance Documentation](https://pypi.org/project/yfinance/)
- [Pine Script Documentation](https://www.tradingview.com/pine-script-reference/)
- [AQR Blog](https://www.aqr.com/Insights/Blog)

---

**記錄完成日期：** 2026-02-17
**下次更新：** 每週進度更新
**預計完成：** 2026-05-17（12 週）

---

## 🎓 研究理念

**市場不獎勵**：
- ❌ 預測準確度
- ❌ 單一強訊號
- ❌ 高頻 Alpha

**市場獎勵**：
- ✅ 資本存活時間
- ✅ 風險調整後報酬
- ✅ 長期穩定表現
- ✅ 結構性優勢

**真正優勢來自**：
1. **風險預算**（而非單一訊號）
2. **結構分散**（而非預測準確度）
3. **槓桿紀律**（服從波動率）
4. **資本存活**（而非短期報酬）

---

**Charlie** 🦄
2026-02-17
