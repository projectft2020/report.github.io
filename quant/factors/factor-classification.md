# 因子分類與研究

**分類日期：** 2026-02-17
**目標：** 收集、整理、研究量化交易中常用的因子

---

## 因子分類

### 1. 價值因子 (Value Factors)
- **定義**：股價相對於基本面的低估
- **常見指標**：
  - P/E, P/B, P/C, P/S
  - EV/EBITDA
  - Dividend Yield

### 2. 成長因子 (Growth Factors)
- **定義**：公司成長潛力
- **常見指標**：
  - EPS Growth, Revenue Growth
  - ROE Growth, ROA Growth

### 3. 動能因子 (Momentum Factors)
- **定義**：過去收益的延續性
- **常見指標**：
  - 12個月截斷動能 (12m CUMRET)
  - 5個月截斷動能 (5m CUMRET)
  - 殺頭動能 (Head-and-Shoulders Momentum)

### 4. 品質因子 (Quality Factors)
- **定義**：公司經營品質
- **常見指標**：
  - ROE, ROA, ROIC
  - Debt-to-Equity, Debt-to-EBITDA
  - Gross Margin, Net Margin
  - Accruals (會計操縱)

### 5. 波動率因子 (Volatility Factors)
- **定義**：價格波動性
- **常見指標**：
  - Historical Volatility
  - Implied Volatility (IV)
  - Downside Risk

### 6. 量能因子 (Volume Factors)
- **定義**：交易活躍度
- **常見指標**：
  - Volume
  - Amplitude
  - Turnover Rate

### 7. 規模因子 (Size Factors)
- **定義**：市值大小
- **常見指標**：
  - Market Cap
  - Equity Value

### 8. 創新因子 (Innovation Factors)
- **定義**：公司創新能力
- **常見指標**：
  - R&D Spending
  - Patents
  - Innovation Index

---

## 推薦研究的因子

### 基礎因子組合
1. **Value + Momentum**：最經典的組合
2. **Quality + Value**：經營好且被低估
3. **Momentum + Quality**：強勢且經營好的公司

### 進階因子組合
1. **Multi-factor**：5-10 個因子混合
2. **動態組合**：根據市場環境調整權重
3. **風險調整組合**：基於 VaR、CVaR 調整

---

## 資料來源

### 免費資料庫
- [Kenneth French Data Library](http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html)
- [Yahoo Finance](https://finance.yahoo.com/)
- [FRED](https://fred.stlouisfed.org/)

### 專業資料庫
- [AQR Data Library](https://www.aqr.com/)
- [Compustat](https://www.compustat.com/)
- [CRSP](https://www.crsp.com/)

---

## 實證分析框架

### 回測步驟
1. **因子計算**：計算所有股票的因子值
2. **分組**：將股票分為 5 絮或 10 絘
3. **組合構建**：
   - 等權組合
   - 加權組合（按因子值）
   - 顯著性選擇
4. **績效評估**：
   - Returns
   - Volatility
   - Sharpe Ratio
   - Maximum Drawdown
   - Tail Risk

### 統計檢驗
1. **IC (Information Coefficient)**：因子預測能力
2. **IR (Information Ratio)**：因子相對風險調整後的收益
3. **t-test**：顯著性檢驗
4. **Fama-MacBeth 回歸**：因子 alpha

---

## 待研究項目

- [ ] 收集因子定義和計算方法
- [ ] 實作因子計算模組
- [ ] 建置回測框架
- [ ] 進行因子有效性驗證
- [ ] 實作多因子組合策略
- [ ] 分析組合表現
