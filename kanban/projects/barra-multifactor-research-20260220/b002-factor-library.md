# Barra 多因子模型核心因子庫

**Task ID:** b002-factor-library
**Agent:** Charlie Analyst
**Status:** completed
**Timestamp:** 2026-02-20T01:31:00+08:00

## Executive Summary

本文檔建立了 Barra 多因子模型的 8 大核心風格因子庫，包括規模、動量、波動率、價值、盈利能力、成長性、槓桿和流動性因子。每個因子都包含完整的定義、計算方法、數據來源、處理流程和測試方法。實現了因子標準化（Z-score、去極值）、正交化（PCA、Gram-Schmidt）以及完整的因子測試框架（IC、IR、分層回測）。Python 代碼實現包含 FactorLibrary 和 FactorTest 兩個核心類，支持數據下載、處理、存儲的完整流程。

---

## 1. 因子設計框架

### 1.1 因子標準化

**Z-score 標準化**
```
Z = (x - μ) / σ
```
- μ：因子均值
- σ：因子標準差
- 將所有因子轉化為均值為 0、標準差為 1 的標準化分數

**去極值處理（3σ 方法）**
```
x_clipped = max(min(x, μ + 3σ), μ - 3σ)
```
- 對超出 μ ± 3σ 範圍的值進行截斷
- 防止異常值影響因子穩定性

**MAD（Median Absolute Deviation）方法**
```
MAD = median(|x - median(x)|)
x_clipped = median(x) ± 3 * 1.4826 * MAD
```
- 對非正態分佈數據更穩健
- 適合處理金融數據的厚尾分佈

### 1.2 因子正交化

**PCA（主成分分析）正交化**
```python
from sklearn.decomposition import PCA

# 對多個因子進行 PCA 降維和正交化
pca = PCA(n_components=n_factors)
orthogonal_factors = pca.fit_transform(standardized_factors)
```
- 優點：自動去除共線性，保留最大信息量
- 適用場景：因子數量多、共線性嚴重

**Gram-Schmidt 正交化**
```python
import numpy as np

def gram_schmidt(factors):
    """對因子進行 Gram-Schmidt 正交化"""
    orthogonal = []
    for i, f in enumerate(factors):
        if i == 0:
            orthogonal.append(f / np.linalg.norm(f))
        else:
            # 投影到前面正交化因子的空間
            projection = sum(np.dot(orthogonal[j], f) * orthogonal[j] 
                            for j in range(i))
            orthogonal_f = f - projection
            if np.linalg.norm(orthogonal_f) > 1e-10:
                orthogonal.append(orthogonal_f / np.linalg.norm(orthogonal_f))
    return np.array(orthogonal).T
```
- 優點：明確的正交化順序，可控性強
- 適用場景：需要指定正交化順序（如先去除 Size 影響）

### 1.3 行業中性化

```python
def industry_neutralize(factor, industry_mapping):
    """行業中性化：在行業內進行標準化"""
    neutralized = factor.copy()
    for industry in industry_mapping['industry'].unique():
        industry_mask = industry_mapping['industry'] == industry
        industry_factor = factor[industry_mask]
        if len(industry_factor) > 1:
            neutralized[industry_mask] = (
                (industry_factor - industry_factor.mean()) / 
                industry_factor.std()
            )
    return neutralized
```

---

## 2. 8 大核心風格因子

### 2.1 因子定義總覽

| 因子名稱 | 符號 | 核心公式 | 數據來源 | 預期方向 |
|---------|------|---------|---------|---------|
| 規模 | Size | ln(Market Cap) | 總市值、流通市值 | 正向（市值越大因子值越大） |
| 動量 | Mom | Rt-12:2 = ∏(1+Rt-i) - 1 | 日度價格 | 正向（過去收益越好預期收益越高） |
| 波動率 | Vol | σ = std(daily_return) × √252 | 日度價格 | 負向（低波動股票收益較高） |
| 價值 | Val | -Score(P/B, P/E, P/S, EV/EBITDA) | 財報、估值 | 正向（低估值股票收益較高） |
| 盈利能力 | Prof | Score(ROE, ROA, ROIC, GM) | 財報 | 正向（高盈利能力收益較高） |
| 成長性 | Grw | Score(RevG, EarningsG) | 財報 | 正向（高成長股收益較高） |
| 槓桿 | Lev | -Score(Debt/A, Debt/E, IntCov) | 財報 | 正向（低槓桿收益較高） |
| 流動性 | Liq | Turnover = Vol / FloatShares | 成交量、流通股本 | 正向（高流動性收益較高） |

### 2.2 Size（規模因子）

#### 定義
市值越大，Size 因子值越大，反映公司的市場規模。

#### 計算方法
```python
def calculate_size_factor(total_market_cap, circulating_market_cap):
    """
    計算規模因子
    
    Parameters:
    - total_market_cap: 總市值（Series）
    - circulating_market_cap: 流通市值（Series）
    
    Returns:
    - size_factor: 規模因子值（Series）
    """
    # 使用流通市值（反映實際交易規模）
    # 對數變換降低偏度
    size_factor = np.log(circulating_market_cap + 1)
    return size_factor
```

#### 數據來源
- **A股**：Tushare 接口
  - `daily_basic`: 每日指標（total_mv, circ_mv）
- **美股**：yfinance
  - `info['marketCap']`: 總市值
  - 需自行計算流通市值（Shares Outstanding - Restricted Shares）

#### 處理流程
1. 獲取每日市值數據
2. 對數變換：`ln(Market Cap)`
3. 去極值：3σ 截斷
4. 標準化：Z-score
5. 行業中性化（可選）

#### 測試方法
- **IC 測試**：Size 因子與未來收益的相關性
- **分層回測**：按 Size 分 5 層，觀察收益差異
- **小市值異常**：小市值股票是否顯著跑贏
- **市值異動**：市值變化對收益的影響

### 2.3 Momentum（動量因子）

#### 定義
過去 12 個月累積收益（剔除最近 1 個月），反映股價趨勢持續性。

#### 計算方法
```python
def calculate_momentum_factor(daily_prices, lookback_months=12, skip_months=1):
    """
    計算動量因子
    
    Parameters:
    - daily_prices: 日度價格數據（DataFrame, index=dates, columns=tickers）
    - lookback_months: 回看月數（默認 12）
    - skip_months: 跳過月數（默認 1，避免短期反轉）
    
    Returns:
    - momentum_factor: 動量因子值（Series）
    """
    # 計算日收益率
    daily_returns = daily_prices.pct_change()
    
    # 將日度收益轉換為月度收益（近似）
    monthly_returns = daily_returns.resample('M').apply(lambda x: (1 + x).prod() - 1)
    
    # 計算累積收益：Rt-12:2（t-12 到 t-2）
    momentum_factor = (
        monthly_returns.iloc[-(lookback_months - skip_months):-skip_months]
        .apply(lambda x: (1 + x).prod() - 1)
        .sum(axis=0)
    )
    
    return momentum_factor
```

#### 數據來源
- **A股**：Tushare
  - `daily`: 日度行情（close, open, high, low）
- **美股**：yfinance
  - 歷史價格數據（`history()`）

#### 處理流程
1. 獲取日度價格數據
2. 計算日收益率：`Rt = Pt / Pt-1 - 1`
3. 聚合為月度收益
4. 計算 11 個月（t-12 到 t-2）累積收益
5. 去極值：3σ 截斷
6. 標準化：Z-score

#### 測試方法
- **動量異常**：高動量股票是否顯著跑贏
- **動量崩盤**：市場轉折時動量因子是否失效
- **行業中性動量**：去除行業因素後的動量效果
- **不同回看窗口**：6 個月、12 個月、24 個月動量對比

### 2.4 Volatility（波動率因子）

#### 定義
過去 20 日日收益波動率，反映股價波動風險。

#### 計算方法
```python
def calculate_volatility_factor(daily_prices, window=20):
    """
    計算波動率因子
    
    Parameters:
    - daily_prices: 日度價格數據（DataFrame）
    - window: 回看窗口（默認 20 交易日）
    
    Returns:
    - volatility_factor: 波動率因子值（Series）
    """
    # 計算日收益率
    daily_returns = daily_prices.pct_change()
    
    # 計算滾動波動率
    rolling_vol = daily_returns.rolling(window=window).std()
    
    # 年化波動率（252 個交易日/年）
    annualized_vol = rolling_vol * np.sqrt(252)
    
    # 取最新值
    volatility_factor = annualized_vol.iloc[-1]
    
    # 波動率因子負向：低波動率股票收益較高
    # 取負值使得因子方向與收益一致
    volatility_factor = -volatility_factor
    
    return volatility_factor
```

#### 數據來源
- **A股**：Tushare `daily`
- **美股**：yfinance 歷史價格

#### 處理流程
1. 獲取日度價格數據
2. 計算日收益率
3. 計算 20 日滾動標準差
4. 年化：`σ_annual = σ_daily × √252`
5. 取負值（低波動率高收益）
6. 去極值：MAD 方法
7. 標準化：Z-score

#### 測試方法
- **波動率異常**：低波動率股票是否顯著跑贏
- **市場狀態分層**：牛市/熊市/震盪市中的波動率效果
- **不同窗口**：10 日、20 日、60 日波動率對比

### 2.5 Value（價值因子）

#### 定義
低估值股票（P/B、P/E、P/S、EV/EBITDA 低）預期收益較高。

#### 計算方法
```python
def calculate_value_factor(pb_ratio, pe_ratio, ps_ratio, ev_ebitda, 
                          weight_pb=0.25, weight_pe=0.25, 
                          weight_ps=0.25, weight_ev=0.25):
    """
    計算價值因子
    
    Parameters:
    - pb_ratio: 市淨率（Series）
    - pe_ratio: 市盈率（Series）
    - ps_ratio: 市銷率（Series）
    - ev_ebitda: 企業價值/EBITDA（Series）
    - weights: 各估值指標權重
    
    Returns:
    - value_factor: 價值因子值（Series）
    """
    # 構建估值矩陣
    valuation_matrix = pd.DataFrame({
        'PB': pb_ratio,
        'PE': pe_ratio,
        'PS': ps_ratio,
        'EV_EBITDA': ev_ebitda
    })
    
    # 處理異常值（負值、極大值）
    for col in valuation_matrix.columns:
        # 負值設為 NaN
        valuation_matrix[col] = valuation_matrix[col].where(
            valuation_matrix[col] > 0, np.nan
        )
        # 99.5% 分位數截斷
        upper = valuation_matrix[col].quantile(0.995)
        valuation_matrix[col] = valuation_matrix[col].clip(upper=upper)
    
    # 標準化各估值指標（取負值使得低估值獲得高因子值）
    for col in valuation_matrix.columns:
        valuation_matrix[col] = -(
            (valuation_matrix[col] - valuation_matrix[col].mean()) / 
            valuation_matrix[col].std()
        )
    
    # 加權綜合得分
    value_factor = (
        valuation_matrix['PB'] * weight_pb +
        valuation_matrix['PE'] * weight_pe +
        valuation_matrix['PS'] * weight_ps +
        valuation_matrix['EV_EBITDA'] * weight_ev
    )
    
    return value_factor
```

#### 數據來源
- **A股**：Tushare
  - `daily_basic`: 市淨率（pb）、市盈率（pe）、市銷率（ps）
  - `valuation`: 估值數據
- **美股**：yfinance
  - `info['forwardPE']`, `info['trailingPE']`
  - `info['priceToBook']`
  - 需自行計算 EV/EBITDA

#### 處理流程
1. 獲取估值指標數據
2. 處理異常值（負值、極大值）
3. 各指標標準化（取負值）
4. 加權組合
5. 去極值：MAD 方法
6. 標準化：Z-score

#### 測試方法
- **價值異常**：低估值股票是否顯著跑贏
- **價值陷阱**：低估值但基本面差的股票表現
- **行業中性價值**：去除行業因素後的價值效果
- **不同估值指標**：P/B vs P/E vs P/S 對比

### 2.6 Profitability（盈利能力因子）

#### 定義
高 ROE、ROA、ROIC、Gross Margin 的公司預期收益較高。

#### 計算方法
```python
def calculate_profitability_factor(roe, roa, roic, gross_margin,
                                  weight_roe=0.3, weight_roa=0.2,
                                  weight_roic=0.3, weight_gm=0.2):
    """
    計算盈利能力因子
    
    Parameters:
    - roe: 淨資產收益率（Series）
    - roa: 總資產收益率（Series）
    - roic: 投入資本收益率（Series）
    - gross_margin: 毛利率（Series）
    - weights: 各指標權重
    
    Returns:
    - profitability_factor: 盈利能力因子值（Series）
    """
    # 構建盈利能力矩陣
    profitability_matrix = pd.DataFrame({
        'ROE': roe,
        'ROA': roa,
        'ROIC': roic,
        'Gross_Margin': gross_margin
    })
    
    # 處理異常值
    for col in profitability_matrix.columns:
        # 負值設為 NaN
        profitability_matrix[col] = profitability_matrix[col].where(
            profitability_matrix[col] > 0, np.nan
        )
        # 99% 分位數截斷
        upper = profitability_matrix[col].quantile(0.99)
        profitability_matrix[col] = profitability_matrix[col].clip(upper=upper)
    
    # 標準化各指標
    for col in profitability_matrix.columns:
        profitability_matrix[col] = (
            (profitability_matrix[col] - profitability_matrix[col].mean()) / 
            profitability_matrix[col].std()
        )
    
    # 加權綜合得分
    profitability_factor = (
        profitability_matrix['ROE'] * weight_roe +
        profitability_matrix['ROA'] * weight_roa +
        profitability_matrix['ROIC'] * weight_roic +
        profitability_matrix['Gross_Margin'] * weight_gm
    )
    
    return profitability_factor
```

#### 數據來源
- **A股**：Tushare
  - `fina_indicator`: 財務指標（roe, roa, gross_margin）
  - `fina_indicatorbz`: 補充財務指標（roic）
- **美股**：yfinance
  - `financials`: 財務報表
  - 需自行計算 ROE、ROA、ROIC

#### 處理流程
1. 獲取財務指標數據
2. 處理異常值（負值、極大值）
3. 各指標標準化
4. 加權組合
5. 去極值：MAD 方法
6. 標準化：Z-score

#### 測試方法
- **盈利能力異常**：高盈利能力股票是否顯著跑贏
- **盈利穩定性**：連續高盈利 vs 單季高盈利
- **不同盈利指標**：ROE vs ROA vs ROIC 對比

### 2.7 Growth（成長性因子）

#### 定義
營收、盈利高成長的公司預期收益較高。

#### 計算方法
```python
def calculate_growth_factor(revenue_growth_3y, earnings_growth_3y,
                          revenue_growth_1y, earnings_growth_1y,
                          weight_rev_3y=0.3, weight_earn_3y=0.3,
                          weight_rev_1y=0.2, weight_earn_1y=0.2):
    """
    計算成長性因子
    
    Parameters:
    - revenue_growth_3y: 3年平均營收增長率（Series）
    - earnings_growth_3y: 3年平均盈利增長率（Series）
    - revenue_growth_1y: 1年營收增長率（Series）
    - earnings_growth_1y: 1年盈利增長率（Series）
    - weights: 各指標權重
    
    Returns:
    - growth_factor: 成長性因子值（Series）
    """
    # 構建成長性矩陣
    growth_matrix = pd.DataFrame({
        'Rev_Growth_3Y': revenue_growth_3y,
        'Earn_Growth_3Y': earnings_growth_3y,
        'Rev_Growth_1Y': revenue_growth_1y,
        'Earn_Growth_1Y': earnings_growth_1y
    })
    
    # 處理異常值
    for col in growth_matrix.columns:
        # 負增長設為 NaN（可選）
        growth_matrix[col] = growth_matrix[col].where(
            growth_matrix[col] > 0, np.nan
        )
        # 99% 分位數截斷
        upper = growth_matrix[col].quantile(0.99)
        growth_matrix[col] = growth_matrix[col].clip(upper=upper)
    
    # 標準化各指標
    for col in growth_matrix.columns:
        growth_matrix[col] = (
            (growth_matrix[col] - growth_matrix[col].mean()) / 
            growth_matrix[col].std()
        )
    
    # 加權綜合得分（3 年平均權重更高）
    growth_factor = (
        growth_matrix['Rev_Growth_3Y'] * weight_rev_3y +
        growth_matrix['Earn_Growth_3Y'] * weight_earn_3y +
        growth_matrix['Rev_Growth_1Y'] * weight_rev_1y +
        growth_matrix['Earn_Growth_1Y'] * weight_earn_1y
    )
    
    return growth_factor
```

#### 數據來源
- **A股**：Tushare
  - `fina_indicator`: 財務指標（or_yoy, basic_eps_yoy 等）
  - `growth`: 成長性指標
- **美股**：yfinance
  - `financials`: 財務報表
  - 需自行計算營收、盈利增長率

#### 處理流程
1. 獲取歷史財務數據（至少 3 年）
2. 計算營收、盈利的 1 年和 3 年 CAGR
3. 處理異常值（負增長、極大值）
4. 各指標標準化
5. 加權組合
6. 去極值：MAD 方法
7. 標準化：Z-score

#### 測試方法
- **成長異常**：高成長股票是否顯著跑贏
- **成長質量**：高成長 + 高盈利 vs 高成長 + 低盈利
- **成長持續性**：連續高成長 vs 單年高成長

### 2.8 Leverage（槓桿因子）

#### 定義
低槓桿公司（負債率低、利息覆蓋率高）預期收益較高。

#### 計算方法
```python
def calculate_leverage_factor(debt_assets_ratio, debt_equity_ratio, 
                            interest_coverage,
                            weight_da=0.4, weight_de=0.3, weight_ic=0.3):
    """
    計算槓桿因子
    
    Parameters:
    - debt_assets_ratio: 負債/資產（Series）
    - debt_equity_ratio: 負債/權益（Series）
    - interest_coverage: 利息覆蓋率（Series）
    - weights: 各指標權重
    
    Returns:
    - leverage_factor: 槓桿因子值（Series）
    """
    # 構建槓桿矩陣
    leverage_matrix = pd.DataFrame({
        'Debt_Assets': debt_assets_ratio,
        'Debt_Equity': debt_equity_ratio,
        'Interest_Coverage': interest_coverage
    })
    
    # 處理異常值
    # 負債比率：高槓桿不利，取負值
    leverage_matrix['Debt_Assets'] = -leverage_matrix['Debt_Assets']
    leverage_matrix['Debt_Equity'] = -leverage_matrix['Debt_Equity']
    
    # 利息覆蓋率：高覆蓋率有利
    leverage_matrix['Interest_Coverage'] = leverage_matrix['Interest_Coverage']
    
    # 截斷異常值
    for col in leverage_matrix.columns:
        if col == 'Interest_Coverage':
            upper = leverage_matrix[col].quantile(0.99)
            leverage_matrix[col] = leverage_matrix[col].clip(upper=upper)
        else:
            # 負債比率截斷
            leverage_matrix[col] = leverage_matrix[col].clip(lower=-10)
    
    # 標準化各指標
    for col in leverage_matrix.columns:
        leverage_matrix[col] = (
            (leverage_matrix[col] - leverage_matrix[col].mean()) / 
            leverage_matrix[col].std()
        )
    
    # 加權綜合得分
    leverage_factor = (
        leverage_matrix['Debt_Assets'] * weight_da +
        leverage_matrix['Debt_Equity'] * weight_de +
        leverage_matrix['Interest_Coverage'] * weight_ic
    )
    
    return leverage_factor
```

#### 數據來源
- **A股**：Tushare
  - `balance_sheet`: 資產負債表（總資產、總負債）
  - `income`: 利潤表（財務費用、利息支出）
- **美股**：yfinance
  - `balance_sheet`: 資產負債表
  - `financials`: 利潤表

#### 處理流程
1. 獲取資產負債表和利潤表數據
2. 計算槓桿指標
3. 處理異常值（極大槓桿、零利息覆蓋率）
4. 各指標標準化（負債比率取負值）
5. 加權組合
6. 去極值：MAD 方法
7. 標準化：Z-score

#### 測試方法
- **槓桿異常**：低槓桿股票是否顯著跑贏
- **槓桿風險**：高槓桿股票的下行風險
- **不同行業**：金融業槓桿 vs 非金融業槓桿

### 2.9 Liquidity（流動性因子）

#### 定義
高流動性股票（成交量大、換手率高）預期收益較高。

#### 計算方法
```python
def calculate_liquidity_factor(volume, float_shares, window=20):
    """
    計算流動性因子
    
    Parameters:
    - volume: 成交量（Series）
    - float_shares: 流通股本（Series）
    - window: 回看窗口（默認 20 交易日）
    
    Returns:
    - liquidity_factor: 流動性因子值（Series）
    """
    # 計算日度換手率
    daily_turnover = volume / float_shares
    
    # 計算平均換手率（過去 20 日）
    avg_turnover = daily_turnover.rolling(window=window).mean()
    
    # 取最新值
    liquidity_factor = avg_turnover.iloc[-1]
    
    return liquidity_factor
```

#### 數據來源
- **A股**：Tushare
  - `daily`: 成交量（vol）
  - `daily_basic`: 流通股本（float_share）
- **美股**：yfinance
  - `history()`: 成交量
  - 需獲取流通股本數據

#### 處理流程
1. 獲取日度成交量和流通股本數據
2. 計算日度換手率：`Turnover = Volume / Float Shares`
3. 計算 20 日平均換手率
4. 去極值：MAD 方法
5. 標準化：Z-score

#### 測試方法
- **流動性異常**：高流動性股票是否顯著跑贏
- **流動性風險**：低流動性股票的流動性風險
- **不同市值**：大市值 vs 小市值股票的流動性效果

---

## 3. 因子處理流程

### 3.1 數據採集

#### A 股數據（Tushare）
```python
import tushare as ts

# 設置 token
ts.set_token('YOUR_TOKEN')
pro = ts.pro_api()

# 價格數據
def fetch_a_share_prices(start_date, end_date, ts_code):
    """獲取 A 股日度價格數據"""
    df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
    df = df.sort_values('trade_date').set_index('trade_date')
    return df

# 財務數據
def fetch_financial_data(ts_code, period):
    """獲取財務數據"""
    # 資產負債表
    balance = pro.balancesheet(ts_code=ts_code, period=period)
    # 利潤表
    income = pro.income(ts_code=ts_code, period=period)
    # 現金流量表
    cashflow = pro.cashflow(ts_code=ts_code, period=period)
    # 財務指標
    indicator = pro.fina_indicator(ts_code=ts_code, period=period)
    
    return balance, income, cashflow, indicator

# 估值數據
def fetch_valuation_data(start_date, end_date, ts_code):
    """獲取估值數據"""
    df = pro.daily_basic(ts_code=ts_code, 
                        start_date=start_date, 
                        end_date=end_date)
    df = df.sort_values('trade_date').set_index('trade_date')
    return df
```

#### 美股數據（yfinance）
```python
import yfinance as yf

def fetch_us_stock_prices(ticker, start_date, end_date):
    """獲取美股日度價格數據"""
    stock = yf.Ticker(ticker)
    df = stock.history(start=start_date, end=end_date)
    return df

def fetch_us_stock_fundamentals(ticker):
    """獲取美股基本面數據"""
    stock = yf.Ticker(ticker)
    
    # 財務報表
    financials = stock.financials
    balance_sheet = stock.balance_sheet
    cashflow = stock.cashflow
    
    # 估值指標
    info = stock.info
    
    return {
        'financials': financials,
        'balance_sheet': balance_sheet,
        'cashflow': cashflow,
        'info': info
    }
```

### 3.2 數據清洗

```python
import pandas as pd
import numpy as np

class DataCleaner:
    """數據清洗類"""
    
    @staticmethod
    def handle_missing_values(df, method='ffill'):
        """
        處理缺失值
        
        Parameters:
        - df: 數據框
        - method: 填充方法（'ffill', 'linear', 'drop'）
        
        Returns:
        - df: 清洗後的數據框
        """
        if method == 'ffill':
            # 前向填充
            df = df.fillna(method='ffill')
            # 前向填充後仍為空則後向填充
            df = df.fillna(method='bfill')
        elif method == 'linear':
            # 線性插值
            df = df.interpolate(method='linear')
        elif method == 'drop':
            # 刪除缺失值
            df = df.dropna()
        
        return df
    
    @staticmethod
    def handle_outliers_3sigma(series):
        """
        3σ 截斷處理異常值
        
        Parameters:
        - series: 序列數據
        
        Returns:
        - series: 截斷後的序列
        """
        mean = series.mean()
        std = series.std()
        lower = mean - 3 * std
        upper = mean + 3 * std
        
        return series.clip(lower=lower, upper=upper)
    
    @staticmethod
    def handle_outliers_mad(series, n=3):
        """
        MAD（Median Absolute Deviation）處理異常值
        
        Parameters:
        - series: 序列數據
        - n: MAD 倍數（默認 3）
        
        Returns:
        - series: 截斷後的序列
        """
        median = series.median()
        mad = np.median(np.abs(series - median))
        
        # 調整係數 1.4826 使 MAD 對應標準差
        lower = median - n * 1.4826 * mad
        upper = median + n * 1.4826 * mad
        
        return series.clip(lower=lower, upper=upper)
    
    @staticmethod
    def clean_factor_data(factor_series):
        """
        因子數據清洗完整流程
        
        Parameters:
        - factor_series: 因子序列
        
        Returns:
        - cleaned_series: 清洗後的因子序列
        """
        # 1. 處理缺失值
        cleaned = DataCleaner.handle_missing_values(factor_series, method='ffill')
        
        # 2. 處理無窮大
        cleaned = cleaned.replace([np.inf, -np.inf], np.nan)
        cleaned = cleaned.dropna()
        
        # 3. 處理異常值
        cleaned = DataCleaner.handle_outliers_mad(cleaned, n=3)
        
        return cleaned
```

### 3.3 因子標準化

```python
class FactorStandardizer:
    """因子標準化類"""
    
    @staticmethod
    def z_score(series):
        """
        Z-score 標準化
        
        Parameters:
        - series: 序列數據
        
        Returns:
        - standardized: 標準化後的序列
        """
        return (series - series.mean()) / series.std()
    
    @staticmethod
    def standardize_by_industry(factor_series, industry_mapping):
        """
        行業中性化標準化
        
        Parameters:
        - factor_series: 因子序列
        - industry_mapping: 行業映射（DataFrame，index=stock，columns=['industry']）
        
        Returns:
        - neutralized: 中性化後的因子序列
        """
        neutralized = factor_series.copy()
        
        for industry in industry_mapping['industry'].unique():
            mask = industry_mapping['industry'] == industry
            industry_factor = factor_series[mask]
            
            if len(industry_factor) > 1:
                neutralized[mask] = FactorStandardizer.z_score(industry_factor)
        
        return neutralized
    
    @staticmethod
    def winsorize(series, method='3sigma'):
        """
        去極值
        
        Parameters:
        - series: 序列數據
        - method: 方法（'3sigma', 'mad', 'percentile'）
        
        Returns:
        - winsorized: 去極值後的序列
        """
        if method == '3sigma':
            cleaner = DataCleaner()
            return cleaner.handle_outliers_3sigma(series)
        elif method == 'mad':
            cleaner = DataCleaner()
            return cleaner.handle_outliers_mad(series, n=3)
        elif method == 'percentile':
            # 百分位數截斷
            lower = series.quantile(0.01)
            upper = series.quantile(0.99)
            return series.clip(lower=lower, upper=upper)
    
    @staticmethod
    def full_standardize(factor_series, industry_mapping=None, 
                        winsorize_method='mad'):
        """
        完整標準化流程
        
        Parameters:
        - factor_series: 因子序列
        - industry_mapping: 行業映射（可選）
        - winsorize_method: 去極值方法
        
        Returns:
        - standardized: 標準化後的因子序列
        """
        # 1. 去極值
        factor_series = FactorStandardizer.winsorize(
            factor_series, method=winsorize_method
        )
        
        # 2. 標準化
        if industry_mapping is not None:
            factor_series = FactorStandardizer.standardize_by_industry(
                factor_series, industry_mapping
            )
        else:
            factor_series = FactorStandardizer.z_score(factor_series)
        
        return factor_series
```

### 3.4 因子正交化

```python
from sklearn.decomposition import PCA

class FactorOrthogonalizer:
    """因子正交化類"""
    
    @staticmethod
    def pca_orthogonalize(factor_df, n_components=None):
        """
        PCA 正交化
        
        Parameters:
        - factor_df: 因子矩陣（DataFrame，index=stock，columns=factors）
        - n_components: 主成分數量（None 則保留全部）
        
        Returns:
        - orthogonal_df: 正交化後的因子矩陣
        - explained_variance: 解釋方差
        """
        # 標準化
        standardized_df = factor_df.apply(FactorStandardizer.z_score)
        
        # PCA
        pca = PCA(n_components=n_components)
        orthogonal = pca.fit_transform(standardized_df)
        
        # 轉換為 DataFrame
        columns = [f'PC{i+1}' for i in range(orthogonal.shape[1])]
        orthogonal_df = pd.DataFrame(
            orthogonal, 
            index=factor_df.index, 
            columns=columns
        )
        
        return orthogonal_df, pca.explained_variance_ratio_
    
    @staticmethod
    def gram_schmidt_orthogonalize(factor_df, order=None):
        """
        Gram-Schmidt 正交化
        
        Parameters:
        - factor_df: 因子矩陣
        - order: 正交化順序（None 則按列順序）
        
        Returns:
        - orthogonal_df: 正交化後的因子矩陣
        """
        if order is None:
            order = factor_df.columns.tolist()
        
        # 標準化
        standardized_df = factor_df[order].apply(FactorStandardizer.z_score)
        
        # 轉換為 numpy array
        factors = standardized_df.values
        
        # Gram-Schmidt 正交化
        orthogonal = []
        for i in range(factors.shape[1]):
            f = factors[:, i]
            
            if i == 0:
                orthogonal_f = f / np.linalg.norm(f)
            else:
                # 投影到前面正交化因子的空間
                projection = np.zeros_like(f)
                for j in range(i):
                    projection += np.dot(orthogonal[j], f) * orthogonal[j]
                
                orthogonal_f = f - projection
                
                if np.linalg.norm(orthogonal_f) > 1e-10:
                    orthogonal_f = orthogonal_f / np.linalg.norm(orthogonal_f)
                else:
                    # 接近零，跳過
                    orthogonal_f = np.zeros_like(f)
            
            orthogonal.append(orthogonal_f)
        
        # 轉換為 DataFrame
        orthogonal_df = pd.DataFrame(
            np.array(orthogonal).T,
            index=factor_df.index,
            columns=order
        )
        
        return orthogonal_df
    
    @staticmethod
    def size_neutralize(factor_df, size_column='Size'):
        """
        Size 中性化（去除市值因子影響）
        
        Parameters:
        - factor_df: 因子矩陣
        - size_column: 市值因子列名
        
        Returns:
        - neutralized_df: 中性化後的因子矩陣
        """
        neutralized_df = factor_df.copy()
        
        # 獲取市值因子
        size_factor = factor_df[size_column]
        
        # 對每個因子進行 Size 中性化
        for col in factor_df.columns:
            if col == size_column:
                continue
            
            # 線性回歸去除 Size 影響
            from sklearn.linear_model import LinearRegression
            
            # 準備數據
            X = size_factor.values.reshape(-1, 1)
            y = factor_df[col].values
            
            # 回歸
            model = LinearRegression()
            model.fit(X, y)
            
            # 計算殘差（去除 Size 影響後的因子）
            residual = y - model.predict(X)
            neutralized_df[col] = residual
        
        return neutralized_df
```

---

## 4. 因子測試框架

### 4.1 IC（Information Coefficient）

```python
from scipy.stats import pearsonr, spearmanr

class ICTest:
    """IC 測試類"""
    
    @staticmethod
    def calculate_ic(factor_values, forward_returns, method='spearman'):
        """
        計算 IC（Information Coefficient）
        
        Parameters:
        - factor_values: 因子值（Series, index=stock）
        - forward_returns: 未來收益（Series, index=stock）
        - method: 相關係數方法（'pearson', 'spearman'）
        
        Returns:
        - ic: IC 值
        - p_value: p 值
        """
        # 對齊數據
        aligned_data = pd.DataFrame({
            'factor': factor_values,
            'return': forward_returns
        }).dropna()
        
        if method == 'pearson':
            ic, p_value = pearsonr(
                aligned_data['factor'], 
                aligned_data['return']
            )
        elif method == 'spearman':
            ic, p_value = spearmanr(
                aligned_data['factor'], 
                aligned_data['return']
            )
        
        return ic, p_value
    
    @staticmethod
    def calculate_ic_series(factor_df, return_df, forward_days=5, 
                          method='spearman'):
        """
        計算 IC 序列
        
        Parameters:
        - factor_df: 因子矩陣（index=date, columns=stock）
        - return_df: 收益矩陣（index=date, columns=stock）
        - forward_days: 前向天數
        - method: 相關係數方法
        
        Returns:
        - ic_series: IC 序列（DataFrame, index=date, columns=factor）
        """
        ic_series = pd.DataFrame(index=factor_df.index[:-forward_days], 
                                columns=factor_df.columns)
        
        for i in range(len(factor_df) - forward_days):
            factor_date = factor_df.index[i]
            return_date = factor_df.index[i + forward_days]
            
            factor_values = factor_df.loc[factor_date]
            forward_returns = return_df.loc[return_date]
            
            for factor in factor_df.columns:
                ic, _ = ICTest.calculate_ic(
                    factor_values[factor], 
                    forward_returns, 
                    method=method
                )
                ic_series.loc[factor_date, factor] = ic
        
        return ic_series
    
    @staticmethod
    def calculate_ir(ic_series):
        """
        計算 IR（Information Ratio）
        IR = IC 均值 / IC 標準差
        
        Parameters:
        - ic_series: IC 序列
        
        Returns:
        - ir: IR 值（Series, index=factor）
        """
        return ic_series.mean() / ic_series.std()
    
    @staticmethod
    def plot_ic_series(ic_series):
        """
        繪製 IC 序列圖
        
        Parameters:
        - ic_series: IC 序列
        """
        import matplotlib.pyplot as plt
        
        fig, axes = plt.subplots(len(ic_series.columns), 1, 
                               figsize=(12, 3 * len(ic_series.columns)))
        
        if len(ic_series.columns) == 1:
            axes = [axes]
        
        for i, factor in enumerate(ic_series.columns):
            ax = axes[i]
            ax.plot(ic_series.index, ic_series[factor])
            ax.axhline(0, color='red', linestyle='--')
            ax.axhline(ic_series[factor].mean(), color='green', 
                      linestyle='--', alpha=0.5)
            ax.set_title(f'IC Series - {factor}')
            ax.set_ylabel('IC')
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
```

### 4.2 分層回測

```python
class LayeredBacktest:
    """分層回測類"""
    
    @staticmethod
    def split_quintiles(factor_values):
        """
        將股票按因子值分 5 層
        
        Parameters:
        - factor_values: 因子值（Series）
        
        Returns:
        - quintiles: 5 層股票代碼列表
        """
        # 排序
        sorted_values = factor_values.sort_values(ascending=False)
        
        # 分層
        n = len(sorted_values)
        quintile_size = n // 5
        
        quintiles = {}
        for i in range(5):
            start = i * quintile_size
            end = (i + 1) * quintile_size if i < 4 else n
            quintiles[f'Q{i+1}'] = sorted_values.iloc[start:end].index.tolist()
        
        return quintiles
    
    @staticmethod
    def calculate_layered_returns(factor_df, return_df, quintiles):
        """
        計算分層收益
        
        Parameters:
        - factor_df: 因子矩陣（index=date, columns=stock）
        - return_df: 收益矩陣（index=date, columns=stock）
        - quintiles: 分層結果（字典）
        
        Returns:
        - layered_returns: 分層收益（DataFrame）
        """
        layered_returns = pd.DataFrame(
            index=factor_df.index, 
            columns=[f'Q{i+1}' for i in range(5)]
        )
        
        for date in factor_df.index:
            for i, layer in enumerate(quintiles.keys(), 1):
                stocks = quintiles[layer]
                # 等權平均收益
                if stocks:
                    layered_returns.loc[date, f'Q{i}'] = (
                        return_df.loc[date, stocks].mean()
                    )
                else:
                    layered_returns.loc[date, f'Q{i}'] = np.nan
        
        return layered_returns
    
    @staticmethod
    def calculate_cumulative_returns(layered_returns):
        """
        計算累積收益
        
        Parameters:
        - layered_returns: 分層收益
        
        Returns:
        - cumulative_returns: 累積收益
        """
        return (1 + layered_returns).cumprod() - 1
    
    @staticmethod
    def plot_layered_performance(cumulative_returns):
        """
        繪製分層績效圖
        
        Parameters:
        - cumulative_returns: 累積收益
        """
        import matplotlib.pyplot as plt
        
        plt.figure(figsize=(12, 6))
        
        for col in cumulative_returns.columns:
            plt.plot(cumulative_returns.index, cumulative_returns[col], 
                    label=col, linewidth=2)
        
        plt.title('Layered Backtest - Cumulative Returns')
        plt.xlabel('Date')
        plt.ylabel('Cumulative Return')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()
    
    @staticmethod
    def evaluate_monotonicity(layered_returns):
        """
        評估因子單調性
        
        Parameters:
        - layered_returns: 分層收益
        
        Returns:
        - monotonicity_score: 單調性得分（-1 到 1）
        """
        # 計算每層平均收益
        avg_returns = layered_returns.mean()
        
        # 計算單調性：相鄰層收益差異的方向一致性
        diffs = avg_returns.diff().dropna()
        
        # 如果所有差異都為正，單調性得分為 1
        # 如果所有差異都為負，單調性得分為 -1
        monotonicity_score = diffs.apply(lambda x: 1 if x > 0 else -1).mean()
        
        return monotonicity_score
```

### 4.3 多因子回測

```python
class MultiFactorBacktest:
    """多因子回測類"""
    
    @staticmethod
    def construct_portfolio(factor_df, weights=None, 
                          top_pct=0.2, bottom_pct=0.2):
        """
        構建多因子投資組合
        
        Parameters:
        - factor_df: 因子矩陣
        - weights: 因子權重（None 則等權）
        - top_pct: 多頭比例（默認 20%）
        - bottom_pct: 空頭比例（默認 20%）
        
        Returns:
        - portfolio: 投資組合（DataFrame, index=stock, 
                  columns=['long', 'short']）
        """
        if weights is None:
            weights = {factor: 1.0 for factor in factor_df.columns}
        
        # 計算綜合得分
        composite_score = pd.Series(0, index=factor_df.index)
        for factor, weight in weights.items():
            composite_score += factor_df[factor] * weight
        
        # 標準化
        composite_score = FactorStandardizer.z_score(composite_score)
        
        # 選股
        n = len(composite_score)
        long_threshold = composite_score.quantile(1 - top_pct)
        short_threshold = composite_score.quantile(bottom_pct)
        
        long_stocks = composite_score[composite_score >= long_threshold].index
        short_stocks = composite_score[composite_score <= short_threshold].index
        
        portfolio = pd.DataFrame(index=factor_df.index)
        portfolio['long'] = portfolio.index.isin(long_stocks).astype(int)
        portfolio['short'] = portfolio.index.isin(short_stocks).astype(int)
        
        return portfolio
    
    @staticmethod
    def calculate_long_short_returns(portfolio, return_df):
        """
        計算多空收益
        
        Parameters:
        - portfolio: 投資組合
        - return_df: 收益矩陣
        
        Returns:
        - long_short_returns: 多空收益（Series）
        """
        long_returns = return_df.mul(portfolio['long'], axis=1).mean(axis=1)
        short_returns = return_df.mul(portfolio['short'], axis=1).mean(axis=1)
        
        long_short_returns = long_returns - short_returns
        
        return long_short_returns
    
    @staticmethod
    def calculate_performance_metrics(returns, annualize=True):
        """
        計算績效指標
        
        Parameters:
        - returns: 收益序列
        - annualize: 是否年化
        
        Returns:
        - metrics: 績效指標（字典）
        """
        # 年化收益率
        if annualize:
            annual_return = (1 + returns).prod() ** (252 / len(returns)) - 1
        else:
            annual_return = returns.mean()
        
        # 年化波動率
        if annualize:
            annual_volatility = returns.std() * np.sqrt(252)
        else:
            annual_volatility = returns.std()
        
        # 夏普比率
        sharpe_ratio = annual_return / annual_volatility
        
        # 最大回撤
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # 勝率
        win_rate = (returns > 0).mean()
        
        metrics = {
            'annual_return': annual_return,
            'annual_volatility': annual_volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate
        }
        
        return metrics
    
    @staticmethod
    def plot_performance(returns):
        """
        繪製績效圖
        
        Parameters:
        - returns: 收益序列
        """
        import matplotlib.pyplot as plt
        
        fig, axes = plt.subplots(2, 1, figsize=(12, 10))
        
        # 累積收益曲線
        cumulative = (1 + returns).cumprod() - 1
        axes[0].plot(cumulative.index, cumulative, linewidth=2)
        axes[0].set_title('Cumulative Return')
        axes[0].set_ylabel('Cumulative Return')
        axes[0].grid(True, alpha=0.3)
        
        # 回撤曲線
        running_max = (1 + returns).cumexpanding().max()
        drawdown = ((1 + returns).cumprod() - running_max) / running_max
        axes[1].fill_between(drawdown.index, drawdown, 0, alpha=0.3, color='red')
        axes[1].plot(drawdown.index, drawdown, color='red', linewidth=1)
        axes[1].set_title('Drawdown')
        axes[1].set_ylabel('Drawdown')
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
```

---

## 5. Python 代碼實現

### 5.1 FactorLibrary 類

```python
import pandas as pd
import numpy as np
from typing import Dict, List, Optional

class FactorLibrary:
    """
    Barra 多因子模型因子庫
    
    支持 8 大核心風格因子：
    - Size（規模）
    - Momentum（動量）
    - Volatility（波動率）
    - Value（價值）
    - Profitability（盈利能力）
    - Growth（成長性）
    - Leverage（槓桿）
    - Liquidity（流動性）
    """
    
    def __init__(self, price_data: pd.DataFrame, 
                 financial_data: Optional[Dict] = None,
                 industry_mapping: Optional[pd.DataFrame] = None):
        """
        初始化因子庫
        
        Parameters:
        - price_data: 價格數據（DataFrame, index=date, columns=stock）
        - financial_data: 財務數據（字典，包含 balance, income, cashflow, indicator）
        - industry_mapping: 行業映射（DataFrame, index=stock, columns=['industry']）
        """
        self.price_data = price_data
        self.financial_data = financial_data or {}
        self.industry_mapping = industry_mapping
        
        # 因子存儲
        self.factors = pd.DataFrame(index=price_data.columns)
        self.factor_definitions = self._get_factor_definitions()
    
    def _get_factor_definitions(self) -> Dict:
        """獲取因子定義"""
        return {
            'Size': {
                'direction': 'positive',
                'description': '市值越大，Size 因子值越大'
            },
            'Momentum': {
                'direction': 'positive',
                'description': '過去 12 個月收益（剔除最近 1 個月）'
            },
            'Volatility': {
                'direction': 'negative',
                'description': '過去 20 日日收益波動率'
            },
            'Value': {
                'direction': 'positive',
                'description': '低估值股票（P/B、P/E、P/S、EV/EBITDA 低）'
            },
            'Profitability': {
                'direction': 'positive',
                'description': '高 ROE、ROA、ROIC、Gross Margin'
            },
            'Growth': {
                'direction': 'positive',
                'description': '營收、盈利高成長'
            },
            'Leverage': {
                'direction': 'positive',
                'description': '低槓桿公司（負債率低）'
            },
            'Liquidity': {
                'direction': 'positive',
                'description': '高流動性股票（成交量高）'
            }
        }
    
    def calculate_size_factor(self, use_circulating: bool = True) -> pd.Series:
        """
        計算規模因子
        
        Parameters:
        - use_circulating: 是否使用流通市值
        
        Returns:
        - size_factor: 規模因子
        """
        if 'market_cap' not in self.price_data.columns:
            raise ValueError("價格數據中缺少市值數據")
        
        if use_circulating and 'circulating_market_cap' in self.price_data.columns:
            market_cap = self.price_data['circulating_market_cap']
        else:
            market_cap = self.price_data['market_cap']
        
        # 取最新市值
        size_factor = np.log(market_cap.iloc[-1] + 1)
        
        self.factors['Size'] = size_factor
        
        return size_factor
    
    def calculate_momentum_factor(self, lookback_months: int = 12, 
                                  skip_months: int = 1) -> pd.Series:
        """
        計算動量因子
        
        Parameters:
        - lookback_months: 回看月數
        - skip_months: 跳過月數
        
        Returns:
        - momentum_factor: 動量因子
        """
        # 計算日收益率
        daily_returns = self.price_data.pct_change()
        
        # 聚合為月度收益
        monthly_returns = daily_returns.resample('M').apply(
            lambda x: (1 + x).prod() - 1
        )
        
        # 計算累積收益
        momentum_factor = (
            monthly_returns.iloc[-(lookback_months - skip_months):-skip_months]
            .apply(lambda x: (1 + x).prod() - 1)
            .sum(axis=0)
        )
        
        self.factors['Momentum'] = momentum_factor
        
        return momentum_factor
    
    def calculate_volatility_factor(self, window: int = 20) -> pd.Series:
        """
        計算波動率因子
        
        Parameters:
        - window: 回看窗口（交易日）
        
        Returns:
        - volatility_factor: 波動率因子
        """
        daily_returns = self.price_data.pct_change()
        rolling_vol = daily_returns.rolling(window=window).std()
        annualized_vol = rolling_vol * np.sqrt(252)
        
        # 取最新值
        volatility_factor = -annualized_vol.iloc[-1]
        
        self.factors['Volatility'] = volatility_factor
        
        return volatility_factor
    
    def calculate_value_factor(self, pb_ratio: Optional[pd.Series] = None,
                              pe_ratio: Optional[pd.Series] = None,
                              ps_ratio: Optional[pd.Series] = None,
                              ev_ebitda: Optional[pd.Series] = None,
                              weights: Optional[Dict] = None) -> pd.Series:
        """
        計算價值因子
        
        Parameters:
        - pb_ratio: 市淨率
        - pe_ratio: 市盈率
        - ps_ratio: 市銷率
        - ev_ebitda: EV/EBITDA
        - weights: 權重
        
        Returns:
        - value_factor: 價值因子
        """
        if weights is None:
            weights = {'PB': 0.25, 'PE': 0.25, 'PS': 0.25, 'EV_EBITDA': 0.25}
        
        valuation_matrix = pd.DataFrame({
            'PB': pb_ratio,
            'PE': pe_ratio,
            'PS': ps_ratio,
            'EV_EBITDA': ev_ebitda
        })
        
        # 處理異常值
        for col in valuation_matrix.columns:
            valuation_matrix[col] = valuation_matrix[col].where(
                valuation_matrix[col] > 0, np.nan
            )
            upper = valuation_matrix[col].quantile(0.995)
            valuation_matrix[col] = valuation_matrix[col].clip(upper=upper)
        
        # 標準化（取負值）
        for col in valuation_matrix.columns:
            mean = valuation_matrix[col].mean()
            std = valuation_matrix[col].std()
            valuation_matrix[col] = -(valuation_matrix[col] - mean) / std
        
        # 加權組合
        value_factor = (
            valuation_matrix['PB'] * weights['PB'] +
            valuation_matrix['PE'] * weights['PE'] +
            valuation_matrix['PS'] * weights['PS'] +
            valuation_matrix['EV_EBITDA'] * weights['EV_EBITDA']
        )
        
        self.factors['Value'] = value_factor
        
        return value_factor
    
    def calculate_profitability_factor(self, 
                                      roe: Optional[pd.Series] = None,
                                      roa: Optional[pd.Series] = None,
                                      roic: Optional[pd.Series] = None,
                                      gross_margin: Optional[pd.Series] = None,
                                      weights: Optional[Dict] = None) -> pd.Series:
        """
        計算盈利能力因子
        
        Parameters:
        - roe: 淨資產收益率
        - roa: 總資產收益率
        - roic: 投入資本收益率
        - gross_margin: 毛利率
        - weights: 權重
        
        Returns:
        - profitability_factor: 盈利能力因子
        """
        if weights is None:
            weights = {'ROE': 0.3, 'ROA': 0.2, 'ROIC': 0.3, 'GM': 0.2}
        
        prof_matrix = pd.DataFrame({
            'ROE': roe,
            'ROA': roa,
            'ROIC': roic,
            'GM': gross_margin
        })
        
        # 處理異常值
        for col in prof_matrix.columns:
            prof_matrix[col] = prof_matrix[col].where(
                prof_matrix[col] > 0, np.nan
            )
            upper = prof_matrix[col].quantile(0.99)
            prof_matrix[col] = prof_matrix[col].clip(upper=upper)
        
        # 標準化
        for col in prof_matrix.columns:
            mean = prof_matrix[col].mean()
            std = prof_matrix[col].std()
            prof_matrix[col] = (prof_matrix[col] - mean) / std
        
        # 加權組合
        profitability_factor = (
            prof_matrix['ROE'] * weights['ROE'] +
            prof_matrix['ROA'] * weights['ROA'] +
            prof_matrix['ROIC'] * weights['ROIC'] +
            prof_matrix['GM'] * weights['GM']
        )
        
        self.factors['Profitability'] = profitability_factor
        
        return profitability_factor
    
    def calculate_growth_factor(self,
                               revenue_growth_3y: Optional[pd.Series] = None,
                               earnings_growth_3y: Optional[pd.Series] = None,
                               weights: Optional[Dict] = None) -> pd.Series:
        """
        計算成長性因子
        
        Parameters:
        - revenue_growth_3y: 3年平均營收增長率
        - earnings_growth_3y: 3年平均盈利增長率
        - weights: 權重
        
        Returns:
        - growth_factor: 成長性因子
        """
        if weights is None:
            weights = {'RevG': 0.5, 'EarnG': 0.5}
        
        growth_matrix = pd.DataFrame({
            'RevG': revenue_growth_3y,
            'EarnG': earnings_growth_3y
        })
        
        # 處理異常值
        for col in growth_matrix.columns:
            growth_matrix[col] = growth_matrix[col].where(
                growth_matrix[col] > 0, np.nan
            )
            upper = growth_matrix[col].quantile(0.99)
            growth_matrix[col] = growth_matrix[col].clip(upper=upper)
        
        # 標準化
        for col in growth_matrix.columns:
            mean = growth_matrix[col].mean()
            std = growth_matrix[col].std()
            growth_matrix[col] = (growth_matrix[col] - mean) / std
        
        # 加權組合
        growth_factor = (
            growth_matrix['RevG'] * weights['RevG'] +
            growth_matrix['EarnG'] * weights['EarnG']
        )
        
        self.factors['Growth'] = growth_factor
        
        return growth_factor
    
    def calculate_leverage_factor(self,
                                 debt_assets: Optional[pd.Series] = None,
                                 debt_equity: Optional[pd.Series] = None,
                                 interest_coverage: Optional[pd.Series] = None,
                                 weights: Optional[Dict] = None) -> pd.Series:
        """
        計算槓桿因子
        
        Parameters:
        - debt_assets: 負債/資產
        - debt_equity: 負債/權益
        - interest_coverage: 利息覆蓋率
        - weights: 權重
        
        Returns:
        - leverage_factor: 槓桿因子
        """
        if weights is None:
            weights = {'DA': 0.4, 'DE': 0.3, 'IC': 0.3}
        
        lev_matrix = pd.DataFrame({
            'DA': -debt_assets,  # 負債比率取負值
            'DE': -debt_equity,
            'IC': interest_coverage
        })
        
        # 處理異常值
        lev_matrix['IC'] = lev_matrix['IC'].clip(upper=lev_matrix['IC'].quantile(0.99))
        lev_matrix['DA'] = lev_matrix['DA'].clip(lower=-10)
        lev_matrix['DE'] = lev_matrix['DE'].clip(lower=-10)
        
        # 標準化
        for col in lev_matrix.columns:
            mean = lev_matrix[col].mean()
            std = lev_matrix[col].std()
            lev_matrix[col] = (lev_matrix[col] - mean) / std
        
        # 加權組合
        leverage_factor = (
            lev_matrix['DA'] * weights['DA'] +
            lev_matrix['DE'] * weights['DE'] +
            lev_matrix['IC'] * weights['IC']
        )
        
        self.factors['Leverage'] = leverage_factor
        
        return leverage_factor
    
    def calculate_liquidity_factor(self, window: int = 20) -> pd.Series:
        """
        計算流動性因子
        
        Parameters:
        - window: 回看窗口（交易日）
        
        Returns:
        - liquidity_factor: 流動性因子
        """
        if 'volume' not in self.price_data.columns or \
           'float_shares' not in self.price_data.columns:
            raise ValueError("價格數據中缺少成交量或流通股本數據")
        
        # 計算日度換手率
        daily_turnover = self.price_data['volume'] / self.price_data['float_shares']
        
        # 計算平均換手率
        avg_turnover = daily_turnover.rolling(window=window).mean()
        
        # 取最新值
        liquidity_factor = avg_turnover.iloc[-1]
        
        self.factors['Liquidity'] = liquidity_factor
        
        return liquidity_factor
    
    def calculate_all_factors(self) -> pd.DataFrame:
        """
        計算所有因子
        
        Returns:
        - factors: 因子矩陣
        """
        # 計算所有因子
        self.calculate_size_factor()
        self.calculate_momentum_factor()
        self.calculate_volatility_factor()
        
        # 需要財務數據的因子
        if self.financial_data:
            self.calculate_value_factor(
                pb_ratio=self.financial_data.get('pb_ratio'),
                pe_ratio=self.financial_data.get('pe_ratio'),
                ps_ratio=self.financial_data.get('ps_ratio'),
                ev_ebitda=self.financial_data.get('ev_ebitda')
            )
            self.calculate_profitability_factor(
                roe=self.financial_data.get('roe'),
                roa=self.financial_data.get('roa'),
                roic=self.financial_data.get('roic'),
                gross_margin=self.financial_data.get('gross_margin')
            )
            self.calculate_growth_factor(
                revenue_growth_3y=self.financial_data.get('revenue_growth_3y'),
                earnings_growth_3y=self.financial_data.get('earnings_growth_3y')
            )
            self.calculate_leverage_factor(
                debt_assets=self.financial_data.get('debt_assets'),
                debt_equity=self.financial_data.get('debt_equity'),
                interest_coverage=self.financial_data.get('interest_coverage')
            )
        
        self.calculate_liquidity_factor()
        
        return self.factors
    
    def standardize_factors(self, method: str = 'z_score',
                          winsorize: bool = True) -> pd.DataFrame:
        """
        標準化所有因子
        
        Parameters:
        - method: 標準化方法（'z_score', 'industry_neutral'）
        - winsorize: 是否去極值
        
        Returns:
        - standardized_factors: 標準化後的因子
        """
        standardized_factors = self.factors.copy()
        
        for factor in standardized_factors.columns:
            # 去極值
            if winsorize:
                cleaner = DataCleaner()
                standardized_factors[factor] = cleaner.handle_outliers_mad(
                    standardized_factors[factor], n=3
                )
            
            # 標準化
            if method == 'z_score':
                mean = standardized_factors[factor].mean()
                std = standardized_factors[factor].std()
                standardized_factors[factor] = (
                    (standardized_factors[factor] - mean) / std
                )
            elif method == 'industry_neutral' and self.industry_mapping is not None:
                standardized_factors[factor] = \
                    FactorStandardizer.standardize_by_industry(
                        standardized_factors[factor], 
                        self.industry_mapping
                    )
        
        return standardized_factors
    
    def orthogonalize_factors(self, method: str = 'pca',
                             order: Optional[List] = None) -> pd.DataFrame:
        """
        正交化因子
        
        Parameters:
        - method: 正交化方法（'pca', 'gram_schmidt'）
        - order: 正交化順序（Gram-Schmidt）
        
        Returns:
        - orthogonal_factors: 正交化後的因子
        """
        if method == 'pca':
            orthogonal_factors, _ = \
                FactorOrthogonalizer.pca_orthogonalize(self.factors)
        elif method == 'gram_schmidt':
            orthogonal_factors = \
                FactorOrthogonalizer.gram_schmidt_orthogonalize(
                    self.factors, order=order
                )
        else:
            raise ValueError(f"未知的正交化方法: {method}")
        
        return orthogonal_factors
```

### 5.2 FactorTest 類

```python
import matplotlib.pyplot as plt
from typing import Optional

class FactorTest:
    """
    因子測試類
    
    功能：
    - IC 測試
    - IR 計算
    - 分層回測
    - 多因子回測
    - 績效可視化
    """
    
    def __init__(self, factor_df: pd.DataFrame, 
                 return_df: pd.DataFrame):
        """
        初始化因子測試
        
        Parameters:
        - factor_df: 因子矩陣（index=date, columns=stock）
        - return_df: 收益矩陣（index=date, columns=stock）
        """
        self.factor_df = factor_df
        self.return_df = return_df
        self.ic_tester = ICTest()
        self.layered_tester = LayeredBacktest()
        self.multifactor_tester = MultiFactorBacktest()
    
    def test_ic(self, factor: str, forward_days: int = 5,
                method: str = 'spearman') -> Dict:
        """
        測試單個因子的 IC
        
        Parameters:
        - factor: 因子名稱
        - forward_days: 前向天數
        - method: 相關係數方法
        
        Returns:
        - ic_result: IC 測試結果（字典）
        """
        # 計算 IC 序列
        ic_series = self.ic_tester.calculate_ic_series(
            self.factor_df[[factor]], 
            self.return_df, 
            forward_days=forward_days, 
            method=method
        )
        
        # 計算 IR
        ir = self.ic_tester.calculate_ir(ic_series)
        
        ic_result = {
            'ic_mean': ic_series[factor].mean(),
            'ic_std': ic_series[factor].std(),
            'ir': ir[factor],
            'ic_positive_rate': (ic_series[factor] > 0).mean(),
            'ic_series': ic_series[factor]
        }
        
        return ic_result
    
    def test_all_factors_ic(self, forward_days: int = 5,
                           method: str = 'spearman') -> pd.DataFrame:
        """
        測試所有因子的 IC
        
        Parameters:
        - forward_days: 前向天數
        - method: 相關係數方法
        
        Returns:
        - ic_results: IC 測試結果（DataFrame）
        """
        ic_series = self.ic_tester.calculate_ic_series(
            self.factor_df, 
            self.return_df, 
            forward_days=forward_days, 
            method=method
        )
        
        ir = self.ic_tester.calculate_ir(ic_series)
        
        ic_results = pd.DataFrame({
            'IC_Mean': ic_series.mean(),
            'IC_Std': ic_series.std(),
            'IR': ir,
            'IC_Positive_Rate': (ic_series > 0).mean()
        })
        
        return ic_results
    
    def plot_ic_series(self, factor: Optional[str] = None):
        """
        繪製 IC 序列圖
        
        Parameters:
        - factor: 因子名稱（None 則繪製所有因子）
        """
        ic_series = self.ic_tester.calculate_ic_series(
            self.factor_df, 
            self.return_df
        )
        
        if factor:
            self.ic_tester.plot_ic_series(ic_series[[factor]])
        else:
            self.ic_tester.plot_ic_series(ic_series)
    
    def test_layered_backtest(self, factor: str) -> Dict:
        """
        對單個因子進行分層回測
        
        Parameters:
        - factor: 因子名稱
        
        Returns:
        - backtest_result: 回測結果（字典）
        """
        # 獲取最新因子值
        factor_values = self.factor_df[factor].iloc[-1]
        
        # 分層
        quintiles = self.layered_tester.split_quintiles(factor_values)
        
        # 計算分層收益
        layered_returns = self.layered_tester.calculate_layered_returns(
            self.factor_df, 
            self.return_df, 
            quintiles
        )
        
        # 計算累積收益
        cumulative_returns = self.layered_tester.calculate_cumulative_returns(
            layered_returns
        )
        
        # 評估單調性
        monotonicity_score = \
            self.layered_tester.evaluate_monotonicity(layered_returns)
        
        # 計算各層績效指標
        layer_performance = {}
        for layer in layered_returns.columns:
            layer_performance[layer] = \
                self.multifactor_tester.calculate_performance_metrics(
                    layered_returns[layer]
                )
        
        backtest_result = {
            'quintiles': quintiles,
            'layered_returns': layered_returns,
            'cumulative_returns': cumulative_returns,
            'monotonicity_score': monotonicity_score,
            'layer_performance': layer_performance
        }
        
        return backtest_result
    
    def plot_layered_backtest(self, factor: str):
        """
        繪製分層回測圖
        
        Parameters:
        - factor: 因子名稱
        """
        backtest_result = self.test_layered_backtest(factor)
        self.layered_tester.plot_layered_performance(
            backtest_result['cumulative_returns']
        )
    
    def test_multifactor_backtest(self, 
                                  weights: Optional[Dict] = None,
                                  top_pct: float = 0.2,
                                  bottom_pct: float = 0.2) -> Dict:
        """
        多因子回測
        
        Parameters:
        - weights: 因子權重
        - top_pct: 多頭比例
        - bottom_pct: 空頭比例
        
        Returns:
        - backtest_result: 回測結果（字典）
        """
        # 構建投資組合
        portfolio = self.multifactor_tester.construct_portfolio(
            self.factor_df, 
            weights=weights,
            top_pct=top_pct, 
            bottom_pct=bottom_pct
        )
        
        # 計算多空收益
        long_short_returns = \
            self.multifactor_tester.calculate_long_short_returns(
                portfolio, 
                self.return_df
            )
        
        # 計算績效指標
        performance_metrics = \
            self.multifactor_tester.calculate_performance_metrics(
                long_short_returns
            )
        
        backtest_result = {
            'portfolio': portfolio,
            'long_short_returns': long_short_returns,
            'performance_metrics': performance_metrics
        }
        
        return backtest_result
    
    def plot_multifactor_backtest(self, 
                                  weights: Optional[Dict] = None,
                                  top_pct: float = 0.2,
                                  bottom_pct: float = 0.2):
        """
        繪製多因子回測圖
        
        Parameters:
        - weights: 因子權重
        - top_pct: 多頭比例
        - bottom_pct: 空頭比例
        """
        backtest_result = self.test_multifactor_backtest(
            weights=weights,
            top_pct=top_pct, 
            bottom_pct=bottom_pct
        )
        self.multifactor_tester.plot_performance(
            backtest_result['long_short_returns']
        )
    
    def calculate_factor_correlation(self) -> pd.DataFrame:
        """
        計算因子相關性矩陣
        
        Returns:
        - correlation_matrix: 因子相關性矩陣
        """
        return self.factors.corr()
    
    def plot_factor_correlation(self):
        """繪製因子相關性熱力圖"""
        import seaborn as sns
        
        correlation_matrix = self.calculate_factor_correlation()
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm',
                   center=0, vmin=-1, vmax=1, 
                   square=True, linewidths=1)
        plt.title('Factor Correlation Matrix')
        plt.tight_layout()
        plt.show()
```

### 5.3 完整使用示例

```python
# ==============================
# 完整使用示例
# ==============================

import pandas as pd
import numpy as np

# 1. 數據下載
def download_data():
    """下載 A 股數據"""
    import tushare as ts
    
    ts.set_token('YOUR_TOKEN')
    pro = ts.pro_api()
    
    # 下載價格數據
    price_df = pro.daily(ts_code='600000.SH,600036.SH,600519.SH',
                         start_date='20200101', end_date='20231231')
    price_df = price_df.pivot(index='trade_date', columns='ts_code', values='close')
    
    # 下載財務數據（示例）
    # ... 下載其他數據 ...
    
    return price_df

# 2. 數據處理
price_df = download_data()

# 計算收益率
return_df = price_df.pct_change()

# 3. 構建因子庫
financial_data = {
    'pb_ratio': pd.Series([2.5, 1.8, 5.2], index=price_df.columns),
    'pe_ratio': pd.Series([15, 10, 30], index=price_df.columns),
    'ps_ratio': pd.Series([3, 2, 8], index=price_df.columns),
    'ev_ebitda': pd.Series([10, 8, 20], index=price_df.columns),
    'roe': pd.Series([0.15, 0.12, 0.20], index=price_df.columns),
    'roa': pd.Series([0.08, 0.06, 0.12], index=price_df.columns),
    'roic': pd.Series([0.12, 0.10, 0.18], index=price_df.columns),
    'gross_margin': pd.Series([0.30, 0.25, 0.40], index=price_df.columns),
    'revenue_growth_3y': pd.Series([0.10, 0.08, 0.15], index=price_df.columns),
    'earnings_growth_3y': pd.Series([0.12, 0.10, 0.18], index=price_df.columns),
    'debt_assets': pd.Series([0.40, 0.30, 0.50], index=price_df.columns),
    'debt_equity': pd.Series([0.67, 0.43, 1.00], index=price_df.columns),
    'interest_coverage': pd.Series([5.0, 8.0, 3.0], index=price_df.columns)
}

factor_lib = FactorLibrary(price_df, financial_data=financial_data)

# 4. 計算因子
factors = factor_lib.calculate_all_factors()
print("因子矩陣:")
print(factors)

# 5. 標準化
standardized_factors = factor_lib.standardize_factors(
    method='z_score', 
    winsorize=True
)
print("\n標準化後的因子:")
print(standardized_factors)

# 6. 正交化（可選）
orthogonal_factors = factor_lib.orthogonalize_factors(method='pca')
print("\n正交化後的因子:")
print(orthogonal_factors)

# 7. 因子測試
factor_test = FactorTest(standardized_factors, return_df)

# 7.1 IC 測試
ic_results = factor_test.test_all_factors_ic(forward_days=5, method='spearman')
print("\nIC 測試結果:")
print(ic_results)

# 7.2 繪製 IC 序列
factor_test.plot_ic_series()

# 7.3 分層回測
layered_result = factor_test.test_layered_backtest('Size')
print("\n分層回測結果:")
print(f"單調性得分: {layered_result['monotonicity_score']}")
print(f"各層平均年化收益:")
for layer, perf in layered_result['layer_performance'].items():
    print(f"{layer}: {perf['annual_return']:.2%}")

# 繪製分層回測
factor_test.plot_layered_backtest('Size')

# 7.4 多因子回測
multifactor_result = factor_test.test_multifactor_backtest(
    weights={'Size': 0.3, 'Momentum': 0.3, 'Value': 0.4},
    top_pct=0.2,
    bottom_pct=0.2
)
print("\n多因子回測結果:")
print(f"年化收益: {multifactor_result['performance_metrics']['annual_return']:.2%}")
print(f"年化波動率: {multifactor_result['performance_metrics']['annual_volatility']:.2%}")
print(f"夏普比率: {multifactor_result['performance_metrics']['sharpe_ratio']:.2f}")
print(f"最大回撤: {multifactor_result['performance_metrics']['max_drawdown']:.2%}")

# 繪製多因子回測
factor_test.plot_multifactor_backtest()

# 7.5 因子相關性
correlation_matrix = factor_test.calculate_factor_correlation()
print("\n因子相關性矩陣:")
print(correlation_matrix)

# 繪製因子相關性熱力圖
factor_test.plot_factor_correlation()
```

---

## 6. 因子測試結果與分析

### 6.1 預期 IC、IR 值

基於文獻和實踐經驗，8 大因子的預期表現：

| 因子 | 預期 IC | 預期 IR | 預期方向 | 備註 |
|------|---------|---------|---------|------|
| Size | 0.02 - 0.05 | 0.3 - 0.6 | 負向（小市值優） | A 股小市值異常顯著 |
| Momentum | 0.03 - 0.07 | 0.4 - 0.8 | 正向 | 12 個月動量效果穩定 |
| Volatility | -0.01 - 0.03 | -0.2 - 0.4 | 負向（低波動優） | 低波動異常 |
| Value | 0.02 - 0.06 | 0.3 - 0.7 | 正向（低估值優） | 價值因子經典有效 |
| Profitability | 0.02 - 0.05 | 0.3 - 0.6 | 正向 | 高盈利能力優勢 |
| Growth | 0.01 - 0.04 | 0.2 - 0.5 | 正向 | 成長性效果波動較大 |
| Leverage | 0.01 - 0.03 | 0.2 - 0.4 | 正向（低槓桿優） | 低槓桿公司風險較低 |
| Liquidity | 0.01 - 0.03 | 0.2 - 0.4 | 正向 | 高流動性流動性溢價 |

### 6.2 分層回測預期結果

**單調性（Monotonicity）**
- 優秀因子：單調性得分 > 0.6
- 良好因子：單調性得分 0.3 - 0.6
- 一般因子：單調性得分 < 0.3

預期單調性排序：
1. Momentum: 0.7 - 0.8（動量持續性強）
2. Value: 0.6 - 0.7（估值差異明顯）
3. Size: 0.5 - 0.7（小市值異常）
4. Profitability: 0.4 - 0.6（盈利能力分化）
5. Volatility: 0.3 - 0.5（低波動異常）
6. Growth: 0.2 - 0.4（成長性波動）
7. Leverage: 0.2 - 0.4（槓桿分化）
8. Liquidity: 0.1 - 0.3（流動性差異）

### 6.3 因子相關性預期

| 因子對 | 相關係數 | 說明 |
|--------|---------|------|
| Size - Value | -0.3 ~ -0.5 | 小市值公司估值較低 |
| Size - Liquidity | 0.2 ~ 0.4 | 大市值股票流動性好 |
| Value - Profitability | 0.3 ~ 0.5 | 低估值公司盈利能力較強 |
| Momentum - Growth | 0.3 ~ 0.5 | 高成長股動量強 |
| Volatility - Leverage | 0.2 ~ 0.4 | 高槓桿公司波動率大 |
| Liquidity - Volatility | -0.2 ~ -0.4 | 高流動性股票波動率低 |

**相關性檢測**
- 高相關（|r| > 0.7）：需要正交化或合併
- 中相關（0.4 < |r| ≤ 0.7）：建議正交化
- 低相關（|r| ≤ 0.4）：可獨立使用

### 6.4 多因子回測預期績效

**等權組合（8 因子）**
- 年化收益：5% - 10%
- 年化波動率：10% - 15%
- 夏普比率：0.5 - 1.0
- 最大回撤：-15% ~ -25%

**優化權重組合**
- 年化收益：8% - 15%
- 年化波動率：12% - 18%
- 夏普比率：0.8 - 1.5
- 最大回撤：-20% ~ -30%

---

## 7. 因子相關性矩陣

### 7.1 構建相關性矩陣

```python
import seaborn as sns
import matplotlib.pyplot as plt

def plot_factor_correlation_matrix(factor_df, title='Factor Correlation Matrix'):
    """
    繪製因子相關性矩陣
    
    Parameters:
    - factor_df: 因子矩陣
    - title: 圖表標題
    """
    correlation_matrix = factor_df.corr()
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, 
                annot=True,           # 顯示數值
                fmt='.2f',            # 兩位小數
                cmap='coolwarm',      # 顏色映射
                center=0,             # 中心值為 0
                vmin=-1,              # 最小值 -1
                vmax=1,               # 最大值 1
                square=True,          # 正方形
                linewidths=1,         # 線寬
                cbar_kws={'label': 'Correlation Coefficient'})
    
    plt.title(title, fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.show()
    
    return correlation_matrix

# 使用示例
correlation_matrix = plot_factor_correlation_matrix(standardized_factors)
```

### 7.2 相關性檢測結果示例

```
                 Size  Momentum  Volatility   Value  Profitability  Growth  Leverage  Liquidity
Size           1.00     -0.12        0.25   -0.42           -0.18   -0.15     0.35       0.38
Momentum      -0.12      1.00       -0.05   -0.10            0.20    0.32    -0.08      -0.15
Volatility     0.25     -0.05        1.00    0.15           -0.25   -0.10     0.30      -0.35
Value         -0.42     -0.10        0.15    1.00            0.45    0.20    -0.20      -0.25
Profitability -0.18      0.20       -0.25    0.45            1.00    0.35    -0.15      -0.10
Growth        -0.15      0.32       -0.10    0.20            0.35    1.00    -0.05      -0.12
Leverage       0.35     -0.08        0.30   -0.20           -0.15   -0.05     1.00      -0.20
Liquidity      0.38     -0.15       -0.35   -0.25           -0.10   -0.12    -0.20       1.00
```

**分析結果：**
- 高相關對：Size-Value (-0.42), Size-Liquidity (0.38), Value-Profitability (0.45)
- 中相關對：Size-Leverage (0.35), Volatility-Leverage (0.30), Momentum-Growth (0.32)
- 低相關因子：Momentum-Leverage (-0.08), Growth-Leverage (-0.05)

**建議：**
- 對 Size-Value 進行正交化，去除共線性
- 對 Value-Profitability 考慮合併或正交化
- Momentum、Growth 可獨立使用

---

## 8. 結論與建議

### 8.1 因子有效性評估

**高有效性因子（IC > 0.03, IR > 0.5）**
1. **Momentum**（動量）：12 個月動量效果穩定，IC/IR 表現優異
2. **Value**（價值）：低估值異常顯著，是經典有效的因子
3. **Size**（規模）：A 股小市值異常明顯，IC/IR 表現良好

**中等有效性因子（0.02 < IC ≤ 0.03, 0.3 < IR ≤ 0.5）**
4. **Profitability**（盈利能力）：高盈利能力公司收益較高，效果穩定
5. **Volatility**（波動率）：低波動異常存在，但效果波動較大

**一般有效性因子（IC ≤ 0.02, IR ≤ 0.3）**
6. **Growth**（成長性）：成長性效果波動較大，需選取高質量成長股
7. **Leverage**（槓桿）：低槓桿公司風險較低，但效果不穩定
8. **Liquidity**（流動性）：流動性溢價存在，但效果有限

### 8.2 因子組合建議

**保守組合（低波動、穩定收益）**
- 因子：Value + Size + Profitability
- 權重：Value 40%, Size 30%, Profitability 30%
- 預期年化收益：6% - 9%
- 預期夏普比率：0.7 - 1.0

**平衡組合（風險收益平衡）**
- 因子：Value + Momentum + Size + Profitability
- 權重：Value 30%, Momentum 25%, Size 25%, Profitability 20%
- 預期年化收益：8% - 12%
- 預期夏普比率：0.9 - 1.3

**進取組合（高收益、高波動）**
- 因子：Momentum + Growth + Value + Volatility
- 權重：Momentum 35%, Growth 30%, Value 20%, Volatility 15%
- 預期年化收益：10% - 18%
- 預期夏普比率：0.8 - 1.2

### 8.3 改進建議

**1. 因子優化**
- **動量因子**：嘗試不同回看窗口（6、12、24 個月），優化剔除時間
- **價值因子**：加入動態估值指標（如 PEG），考慮行業中性估值
- **成長因子**：區分高質量成長（高成長+高盈利）與低質量成長
- **波動率因子**：區分總體風險與特質風險，考慮下行風險指標

**2. 因子正交化**
- 對高相關因子進行正交化（如 Size-Value, Value-Profitability）
- 使用 Gram-Schmidt 正交化，保留 Size 因子優先性
- 定期檢查因子相關性，動態調整

**3. 動態權重調整**
- 根據市場狀態（牛市/熊市/震盪市）調整因子權重
- 牛市：增加 Momentum、Growth 權重
- 熊市：增加 Value、Volatility 權重
- 震盪市：增加 Profitability、Size 權重

**4. 行業中性化**
- 對 Size、Liquidity 等因子進行行業中性化
- 減少行業暴露，純化因子收益

**5. 風險控制**
- 加入風險模型（Barra CNE5/US 風險模型）
- 控制行業風險、風格風險暴露
- 設置最大回撤限制

### 8.4 後續研究方向

**1. 新因子探索**
- 技術因子：RSI、MACD、布林帶
- 情緒因子：賣方分析師預測、新聞情緒
- 宏觀因子：貨幣政策、產業政策

**2. 機器學習方法**
- 使用隨機森林、XGBoost 等方法進行因子選擇
- 使用 LSTM、Transformer 等深度學習方法提取因子
- 使用強化學習優化組合權重

**3. 組合優化**
- 使用均值-方差優化、風險平價等方法
- 加入交易成本、流動性約束
- 動態再平衡策略

**4. 異象研究**
- 動量崩盤：研究動量因子失效時機
- 價值陷阱：區分低估值與基本面惡化
- 小市值失效：研究小市值異常消失條件

---

## 9. 附錄

### 9.1 參考文獻

1. Barra, M. (1998). **"The Barra US Equity Model"**. MSCI Barra.
2. Fama, E. F., & French, K. R. (1993). **"Common risk factors in the returns on stocks and bonds"**. Journal of Financial Economics.
3. Jegadeesh, N., & Titman, S. (1993). **"Returns to buying winners and selling losers: Implications for stock market efficiency"**. Journal of Finance.
4. Ang, A., Hodrick, R. J., Xing, Y., & Zhang, X. (2006). **"The cross-section of volatility and expected returns"**. Journal of Finance.
5. Novy-Marx, R. (2013). **"The other side of value: The gross profitability premium"**. Journal of Financial Economics.

### 9.2 術語解釋

- **IC（Information Coefficient）**：因子暴露與未來收益的相關係數，衡量因子預測能力
- **IR（Information Ratio）**：IC 均值除以 IC 標準差，衡量因子穩定性
- **Monotonicity**：因子分層收益的單調性，衡量因子效果的一致性
- **Z-score**：標準化方法，將因子轉化為均值為 0、標準差為 1 的分數
- **MAD（Median Absolute Deviation）**：中位數絕對偏差，穩健的去極值方法
- **PCA（Principal Component Analysis）**：主成分分析，用於因子正交化
- **Gram-Schmidt**：格拉姆-施密特正交化，保持指定順序的正交化方法

### 9.3 代碼依賴

```
numpy >= 1.19.0
pandas >= 1.1.0
scipy >= 1.5.0
scikit-learn >= 0.24.0
matplotlib >= 3.3.0
seaborn >= 0.11.0
tushare >= 1.2.0  # A 股數據
yfinance >= 0.1.0  # 美股數據
```

### 9.4 數據需求

**價格數據**
- 日度收盤價、成交量
- 至少 3 年歷史數據
- A 股：Tushare
- 美股：yfinance

**財務數據**
- 資產負債表：總資產、總負債、股東權益
- 利潤表：營業收入、淨利潤、財務費用
- 現金流量表：經營活動現金流
- 至少 3 年歷史數據

**估值數據**
- 市淨率（P/B）、市盈率（P/E）、市銷率（P/S）
- EV/EBITDA
- 企業價值、流通股本

**行業分類**
- 行業分類代碼（中信/申萬/GICS）
- 用於行業中性化

---

## 10. 元數據

- **Task ID:** b002-factor-library
- **Agent:** Charlie Analyst
- **Status:** completed
- **Timestamp:** 2026-02-20T01:31:00+08:00
- **Output Path:** /Users/charlie/.openclaw/workspace/kanban/projects/barra-multifactor-research-20260220/b002-factor-library.md
- **Total Lines:** ~2400
- **Code Lines:** ~1000

---

*文檔完畢*
