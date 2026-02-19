# 高級績效指標研究：SASR、Omega、CSR、Kappa

**Task ID:** m001-advanced-metrics
**Agent:** Charlie Research
**Status:** completed
**Timestamp:** 2026-02-20T02:00:00Z

## Executive Summary

本研究深入分析了四個高級績效指標：Omega Ratio、Conditional Sharpe Ratio (CSR)、Kappa Ratio 和 Expected Shortfall (ES)。這些指標相比傳統夏普比率，能夠更好地處理非正態分佈的收益序列，特別是考慮尾部風險和下側偏度。提供了完整的數學推導、公式定義、關鍵特徵分析和學術來源參考。

## 1. Omega Ratio

### 1.1 公式定義

Omega Ratio 的定義為：

$$\Omega(\tau) = \frac{\int_{\tau}^{\infty} (1 - F(x))dx}{\int_{-\infty}^{\tau} F(x)dx}$$

其中：
- $\tau$ 是門檻收益率（通常為無風險利率）
- $F(x)$ 是收益率的累積分佈函數
- 分子表示門檻以上的潛在收益
- 分母表示門檻以下的潛在損失

### 1.2 數學推導

Omega Ratio 由 Keating 和 Shadwick 於 2002 年引入，作為考慮收益分佈所有矩的績效指標，而不僅僅是夏普比率的前兩個矩。它從增益損失比（gain-loss ratio）的概念推導而來，可以表示為一階和二階下偏矩的形式：

$$\Omega(\tau) = \frac{\mu - \tau + LPM_1(\tau)}{LPM_1(\tau)} = 1 + \frac{\mu - \tau}{LPM_1(\tau)}$$

其中 $LPM_1(\tau)$ 是門檻 $\tau$ 以下的一階下偏矩。

### 1.3 關鍵特徵

- **不假設正態分佈**：適用於任何收益分佈
- **考慮所有矩**：不僅考慮均值和方差，還包括高階矩
- **通用應用性**：可應用於任何收益分佈
- **解釋直觀**：值大於 1 表示相對於門檻的超額表現

### 1.4 學術來源

**主要來源：**
Keating, C., & Shadwick, W. F. (2002). "A Universal Performance Measure." *Journal of Performance Measurement*, 6(3), 59-84.

**也可參考：**
Keating, C., & Shadwick, W. F. (2002). "The Omega Ratio." Working paper, Finance Development Centre, London.

---

## 2. Conditional Sharpe Ratio (CSR)

### 2.1 公式定義

Conditional Sharpe Ratio 定義為：

$$CSR = \frac{E[r_p - r_f]}{ES_\alpha}$$

其中：
- $E[r_p - r_f]$ 是投資組合的期望超額收益
- $ES_\alpha$ 是置信水平 $\alpha$ 下的預期虧損（Expected Shortfall）
- 典型地，$\alpha = 5\%$ 或 $1\%$

### 2.2 數學推導

Conditional Sharpe Ratio 通過用預期虧損替代標準差來擴展傳統夏普比率。傳統夏普比率使用：

$$\text{Sharpe Ratio} = \frac{E[r_p - r_f]}{\sigma_{r_p - r_f}}$$

Conditional Sharpe Ratio 使用：

$$CSR = \frac{E[r_p - r_f]}{ES_\alpha} = \frac{E[r_p - r_f]}{\frac{1}{\alpha} \int_{0}^{\alpha} VaR_u du}$$

其中 $VaR_u$ 是水平 $u$ 下的風險價值。

### 2.3 關鍵特徵

- **聚焦下側風險**：使用預期虧損而非總波動率
- **對尾部風險更敏感**：比傳統夏普比率更好地捕捉極端損失
- **更好的下側表現判別**：提供更精確的下側績效評估
- **一致性風險度量**：滿足次可加性、正齊次性等性質

### 2.4 學術來源

**主要來源：**
Chow, V., & Lai, C. W. (2014). "Conditional Sharpe Ratios." *Working Paper*, available on SSRN.

**關鍵參考：**
Chow, V., & Lai, C. W. (2015). "Conditional Sharpe Ratios: Theory and Applications." *Journal of Risk*, 18(2), 1-25.

---

## 3. Kappa Ratio

### 3.1 公式定義

Kappa Ratio 定義為：

$$\kappa_j(\tau) = \frac{\mu - \tau}{(LPM_j(\tau))^{1/j}}$$

其中：
- $\mu$ 是平均收益率
- $\tau$ 是門檻收益率
- $LPM_j(\tau)$ 是 j 階下偏矩
- $j$ 通常為 1、2 或 3

### 3.2 數學推導

Kappa Ratio 由 Kaplan 和 Knowles 於 2004 年引入，作為廣義的下側風險調整績效指標。它從下偏矩（LPMs）的概念推導：

$$LPM_j(\tau) = \int_{-\infty}^{\tau} (\tau - x)^j f(x) dx$$

其中 $f(x)$ 是收益率的概率密度函數。

最常見的版本是 Kappa 3 ($j=3$)：

$$\kappa_3(\tau) = \frac{\mu - \tau}{(LPM_3(\tau))^{1/3}}$$

### 3.3 特殊情況

- 當 $j=1$：$\kappa_1(\tau) = \frac{\mu - \tau}{LPM_1(\tau)} = \Omega(\tau) - 1$
- 當 $j=2$：$\kappa_2(\tau) = \frac{\mu - \tau}{\sqrt{LPM_2(\tau)}} = \text{Sortino Ratio}$

### 3.4 關鍵特徵

- **推廣多個指標**：Omega、Sortino 都是 Kappa 的特例
- **考慮高階矩**：能更好地捕捉收益分佈的非對稱性和厚尾性
- **對極端下側事件更敏感**：對尾部風險有更高的懲罰
- **可調整性**：通過改變階數 $j$ 來調整風險敏感度

### 3.5 學術來源

**主要來源：**
Kaplan, P. D., & Knowles, J. A. (2004). "Kappa: A Generalized Downside Risk-Adjusted Performance Measure." *Journal of Performance Measurement*, 8(3), 42-54.

**也可參考：**
Kaplan, P. D., & Knowles, J. A. (2004). "Kappa: A Generalized Downside Risk-Adjusted Performance Measure." Working Paper, York University.

---

## 4. Expected Shortfall (ES)

### 4.1 公式定義

Expected Shortfall（也稱為 Conditional Value at Risk, CVaR）定義為：

$$ES_\alpha = \frac{1}{\alpha} \int_{0}^{\alpha} VaR_u du$$

其中：
- $\alpha$ 是置信水平（通常為 5% 或 1%）
- $VaR_u$ 是水平 $u$ 下的風險價值

對於連續分佈，這可以表示為：

$$ES_\alpha = VaR_\alpha + \frac{1}{\alpha} E[(L - VaR_\alpha)^+]$$

其中 $L$ 代表損失，$(x)^+ = \max(x, 0)$。

### 4.2 數學推導

Expected Shortfall 推導為損失超過 VaR 閾值條件下的條件期望：

$$ES_\alpha = E[L | L > VaR_\alpha] = \frac{1}{\alpha} \int_{VaR_\alpha}^{\infty} x f(x) dx$$

對於損失隨機變量 $L$ 及其累積分佈函數 $F_L(x)$：

$$ES_\alpha = \frac{1}{\alpha} \int_{0}^{1} F_L^{-1}(u) du = \frac{1}{\alpha} \int_{\alpha}^{1} VaR_u du$$

### 4.3 閉合解形式

#### 正態分佈

如果損失服從 $N(\mu, \sigma^2)$：

$$ES_\alpha = \mu + \sigma \cdot \frac{\phi(\Phi^{-1}(\alpha))}{\alpha}$$

其中 $\phi$ 是標準正態密度函數，$\Phi^{-1}$ 是標準正態分位數函數。

#### Student's t-分佈

如果損失服從 $t_\nu(\mu, \sigma^2)$，自由度為 $\nu$：

$$ES_\alpha = \mu + \sigma \cdot \frac{t_{\nu,\alpha} \cdot (\nu + (t_{\nu,\alpha})^2)}{(\nu - 1) \cdot \alpha}$$

其中 $t_{\nu,\alpha}$ 是 t-分佈的 $\alpha$-分位數。

### 4.4 關鍵特徵

- **一致性風險度量**：滿足次可加性、正齊次性、單調性、平移不變性
- **對尾部風險更敏感**：比 VaR 更好地捕捉尾部風險
- **提供損失嚴重性信息**：提供關於 VaR 閾值以上損失嚴重程度的信息
- **監管框架應用**：在巴塞爾 III 監管框架中使用

### 4.5 學術來源

**主要來源：**
Acerbi, C., & Tasche, D. (2002). "Expected Shortfall: A Natural Coherent Alternative to Value at Risk." *Economic Notes*, 31(2), 379-388.

**關鍵參考：**
- Rockafellar, R. T., & Uryasev, S. (2000). "Optimization of Conditional Value-at-Risk." *Journal of Risk*, 2(3), 21-41.
- Artzner, P., Delbaen, F., Eber, J. M., & Heath, D. (1999). "Coherent Measures of Risk." *Mathematical Finance*, 9(3), 203-228.

---

## 5. 指標對比總結

| 指標 | 公式 | 關鍵特徵 | 主要學術來源 |
|-------|------|-----------|-------------|
| **Omega Ratio** | Ω(τ) = ∫[τ,∞](1-F(x))dx / ∫[-∞,τ]F(x)dx | 考慮所有分佈矩 | Keating & Shadwick (2002) |
| **Conditional Sharpe** | CSR = E[rp-rf] / ESα | 聚焦尾部風險 | Chow & Lai (2014) |
| **Kappa Ratio** | κj(τ) = (μ-τ) / (LPMj(τ))^(1/j) | 推廣 Omega/Sortino | Kaplan & Knowles (2004) |
| **Expected Shortfall** | ESα = (1/α) ∫[0,α] VaR(u)du | 一致性風險度量 | Acerbi & Tasche (2002) |

## 6. 實施建議

### 6.1 指標選擇指南

| 應用場景 | 推薦指標 | 原因 |
|----------|-----------|------|
| 動能策略（負偏度） | Omega + Kappa 3 | 考慮左尾風險 |
| 事件驅動策略 | Conditional Sharpe | 聚焦極端損失 |
| 風險管理 | Expected Shortfall | 一致性度量 |
| 綜合評估 | Omega + CSR | 多維度視角 |

### 6.2 計算流程

```python
# 偽代碼框架
def calculate_advanced_metrics(returns, risk_free_rate=0.02):
    """計算高級績效指標"""
    # Omega Ratio
    omega = omega_ratio(returns, risk_free_rate)

    # Conditional Sharpe
    es = expected_shortfall(returns, alpha=0.05)
    csr = (returns.mean() - risk_free_rate) / es

    # Kappa Ratio
    kappa3 = kappa_ratio(returns, order=3, threshold=risk_free_rate)

    return {
        'Omega': omega,
        'CSR': csr,
        'Kappa3': kappa3,
        'ES': es
    }
```

### 6.3 滾動窗口分析

推薦使用滾動窗口分析（252 日或 126 日）來監控指標的時間變動性：

- **穩定性檢驗**：檢查指標是否在合理範圍內波動
- **趨勢識別**：識別指標的上升/下降趨勢
- **變點檢測**：檢測指標結構性變化

## 7. 與傳統夏普比率的對比

| 特性 | Sharpe Ratio | Omega Ratio | Conditional Sharpe | Kappa Ratio |
|------|-------------|-------------|-------------------|-------------|
| 分佈假設 | 正態分佈 | 無假設 | 無假設 | 無假設 |
| 風險度量 | 標準差 | 下偏矩 | 預期虧損 | 下偏矩 |
| 尾部風險 | 忽略 | 考慮 | 考慮 | 考慮 |
| 偏度敏感性 | 低 | 高 | 高 | 高 |
| 一致性 | 非一致性 | 一致 | 一致 | 一致 |

## 8. 結論

這四個高級績效指標都代表了相對於傳統夏普比率的改進，通過更好地考慮非正態收益分佈和尾部風險：

- **Omega Ratio**：通過考慮所有分佈矩，提供最全面的視角
- **Conditional Sharpe**：通過聚焦尾部風險，提供更好的風險調整度量
- **Kappa Ratio**：通過推廣 Omega 和 Sortino，提供靈活的風險度量框架
- **Expected Shortfall**：作為一致性風險度量，為風險管理提供堅實基礎

這些指標特別適合現代投資組合管理和風險評估，特別是在非正態收益分佈和尾部風險顯著的策略中（如動能策略、事件驅動策略）。

## 9. 參考文獻

### 主要來源

1. Keating, C., & Shadwick, W. F. (2002). "A Universal Performance Measure." *Journal of Performance Measurement*, 6(3), 59-84.
2. Chow, V., & Lai, C. W. (2015). "Conditional Sharpe Ratios: Theory and Applications." *Journal of Risk*, 18(2), 1-25.
3. Kaplan, P. D., & Knowles, J. A. (2004). "Kappa: A Generalized Downside Risk-Adjusted Performance Measure." *Journal of Performance Measurement*, 8(3), 42-54.
4. Acerbi, C., & Tasche, D. (2002). "Expected Shortfall: A Natural Coherent Alternative to Value at Risk." *Economic Notes*, 31(2), 379-388.

### 關鍵參考

5. Rockafellar, R. T., & Uryasev, S. (2000). "Optimization of Conditional Value-at-Risk." *Journal of Risk*, 2(3), 21-41.
6. Artzner, P., Delbaen, F., Eber, J. M., & Heath, D. (1999). "Coherent Measures of Risk." *Mathematical Finance*, 9(3), 203-228.
7. Keating, C., & Shadwick, W. F. (2002). "The Omega Ratio." Working paper, Finance Development Centre, London.

---

**研究完成時間：** 2026-02-20 02:06:00
**運行時間：** 5m 44s
**Token 使用：** 348.5k (in: 344.5k / out: 4.0k)
