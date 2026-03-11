# Risk Management

> **Category:** 風險指標、厚尾分佈、非傳統止損策略
> **Source:** MEMORY.md 2026-02-19 to 2026-02-20
> **Last Updated:** 2026-02-23

---

## 🎯 核心概念

### 厚尾分佈 (Fat-Tailed Distribution)
**來源：** Nassim Taleb 黑天鵝理論
**問題：**
- 傳統風險度量（VaR、CVaR、標準差）失效
- 在厚尾市場下，極端事件發生頻率高於常態分佈假設
- 止損點處產生質量集中（point mass）

**Nassim Taleb 觀點：**
- 止損將收益分佈轉換為截斷過程
- 左尾被「截斷」，但集中在一個點（非消失）
- 厚尾分佈下，止損的轉換尤其危險
- 需要明確的基於障礙的建模

---

### 非傳統止損策略
**傳統問題：** 固定百分比止損（如 5%）
**轉換風險：** 在厚尾市場下不可恢復
**替代方案：**
1. **動態調整部位曝險**（如 100% → 50%）
2. **期權對沖**（有明確定價）
3. **組合比例調整**（QQQ+IAU 從 50/50 調整至 75/25）

**實務工具範例：** DHRI (Daily Hedge Ratio Indicator)
- 簡化成 3 種計算方法
- 30 秒查詢
- 3 分鐘執行
- 輸出：DHRI (0-100) → 避險比例 (0-50%)

---

## 📏 風險指標研究

### 高級績效指標
**m001 研究完成：** 2026-02-20
**研究的指標：**
1. **Omega Ratio** - Keating & Shadwick 2002
2. **Conditional Sharpe Ratio** - Chow & Lai 2014
3. **Kappa Ratio** - Kaplan & Knowles 2004
4. **Expected Shortfall** - Acerbi & Tasche 2002
5. **SKTASR** - 新風險調整收益指標

**特徵：**
- 完整的數學推導
- 學術來源明確
- 特徵分析深入（優點、缺點、應用場景）
- 特殊情況（閉合解、極限情況）

---

### 收益分佈作為策略評估指標
**研究主題：** s001 (risk-management-20260219)
**研究內容：**
- 收益分佈形態（偏度、峰度、肥尾指數）
- 對勝率、Sharpe Ratio、穩定性、健康度的影響
- 建立基於分佈的綜合評估框架

**應用價值：**
- 識別異常收益模式
- 評估策略在不同市場狀態下的表現
- 優化投資組合配置

---

### 肥尾市場下傳統風險指標失效研究
**研究主題：** s002 (risk-management-20260219)
**失效指標：**
- VaR (Value at Risk)
- CVaR (Conditional Value at Risk)
- 標準差

**替代方法：**
- Hill Estimator（尾指數估計）
- MLE（最大似然估計）
- Pareto 分佈建模
- 功率法則（Power Law）

---

## 🛠 實務工具

### DHRI (Daily Hedge Ratio Indicator)
**創建時間：** 2026-02-20
**位置：** `/Users/charlie/.openclaw/workspace/DHRI-daily-hedge-ratio.md`

**三種計算方法：**
1. **ultra_simple** - 僅需 VIX（推薦）
2. **simple** - VIX + 波動率
3. **precise** - 加入趨勢和市場狀態

**輸出：** DHRI (0-100) → 避險比例 (0-50%)
**代碼：** DailyHedgeRatioIndicator 類（可直接使用）

**用戶需求：**
- ✅ 深入理論（數學推導 + 學術來源）
- ✅ 實務簡化（複雜理論 → 可執行工具）
- ✅ 需求：3 分鐘每日操作流程
- ✅ 需求：單一指標決策（0-100）
- ✅ 需求：快速查詢表（30 秒）

---

## 📊 指標對比

### 傳統夏普比率 vs 新型指標

| 指標 | 特點 | 優點 | 缺點 |
|--------|------|------|------|
| **Sharpe Ratio** | 簡單計算 | 無考慮尾風險 | 假設正態分佈 |
| **Omega Ratio** | 考慮尾部分佈 | 對比分佈敏感 | 計算複雜 |
| **Conditional Sharpe** | 基於目標基準 | 考慮目標收益 | 需要定義基準 |
| **Kappa Ratio** | 考慮下跌風險 | 下行保護 | 計算不穩定 |
| **Expected Shortfall** | 風險量度明確 | 尾風險保護 | 需要假設分佈 |

---

## 🎯 實施建議

### 研究報告標準（基於 m001 範例）
1. Executive Summary（執行摘要）
2. 公式定義（完整數學表達式）
3. 數學推導（從基本概念到最終公式）
4. 特徵分析（優點、缺點、應用場景）
5. 特殊情況（閉合解、極限情況）
6. 學術來源（主要論文 + 參考文獻）
7. 指標對比表（多個指標一覽）
8. 實施建議（指標選擇、計算流程、應用場景）
9. 與傳統方法對比
10. 結論與參考文獻

### 深入研究 vs 實務工具
**研究報告：**
- 深入理解理論
- 學術參考
- 實證驗證
- 完整 Python 代碼
- 推送到 GitHub Pages（供深度學習）

**實務工具：**
- 快速執行（3 分鐘）
- 單一指標決策
- 保存到 workspace/（供日常使用）
- 避免複雜操作

---

## 📚 參考文獻

### 核心論文
- **Keating & Shadwick (2002)** - Omega Ratio
- **Chow & Lai (2014)** - Conditional Sharpe Ratio
- **Kaplan & Knowles (2004)** - Kappa Ratio
- **Acerbi & Tasche (2002)** - Expected Shortfall
- **Nassim Taleb** - The Black Swan, Antifragile

### 關鍵概念
- **Black Swan Theory** - 極端事件的重要性
- **Fat-Tailed Distribution** - 厚尾分佈的建模
- **Barrier-Based Modeling** - 基於障礙的風險建模
- **Point Mass** - 風險集中點的概念

---

**下一步重點：**
- 完成風險管理 4 個研究任務
- 探索新的風險度量方法
- 實施實務風險工具
