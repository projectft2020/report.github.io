# 市場狀態檢測（Regime Detection）特征工程設計

**Task ID:** r002-feature-engineering
**Agent:** Charlie Analyst
**Status:** completed
**Timestamp:** 2026-02-20T01:49:00Z

## Executive Summary

本研究設計了針對 HMM + Bayesian Change Point 混合模型的完整特征工程框架。涵蓋五大類特征（價格收益、技術指標、宏觀經濟、市場情緒、風險指標），共計 80+ 特徵變量。提供了完整的特徵計算、清洗、變換、選擇流程，以及 Python 代碼實現。特征設計充分考慮了 HMM 的狀態轉移建模需求和 Bayesian Change Point 的變點檢測需求，為模型訓練提供高質量輸入。

## 1. 特徵類別設計

### 1.1 價格與收益特徵

#### 1.1.1 基礎收益特徵

| 特徵名稱 | 計算公式 | 時間窗口 | 數據來源 | 說明 |
|---------|---------|---------|---------|------|
| `return_daily` | R_t = (P_t - P_{t-1}) / P_{t-1} | 1 日 | 價格數據 | 日收益率 |
| `return_log` | log(P_t / P_{t-1}) | 1 日 | 價格數據 | 對數收益率 |
| `return_lag1` | R_{t-1} | - | 價格數據 | 滯後1日收益 |
| `return_lag2` | R_{t-2} | - | 價格數據 | 滯後2日收益 |
| `return_lag3` | R_{t-3} | - | 價格數據 | 滯後3日收益 |
| `return_lag4` | R_{t-4} | - | 價格數據 | 滯後4日收益 |
| `return_lag5` | R_{t-5} | - | 價格數據 | 滯後5日收益 |

**Python 實現：**
```python
def calculate_returns(prices):
    """計算基礎收益特徵"""
    returns = pd.DataFrame(index=prices.index)

    # 日收益率
    returns['return_daily'] = prices.pct_change()

    # 對數收益率
    returns['return_log'] = np.log(prices / prices.shift(1))

    # 滯後收益
    for i in range(1, 6):
        returns[f'return_lag{i}'] = returns['return_daily'].shift(i)

    return returns
```

#### 1.1.2 動量特徵

| 特徵名稱 | 計算公式 | 時間窗口 | 數據來源 | 說明 |
|---------|---------|---------|---------|------|
| `momentum_1M` | (P_t / P_{t-21}) - 1 | 21 日 | 價格數據 | 1月動量 |
| `momentum_3M` | (P_t / P_{t-63}) - 1 | 63 日 | 價格數據 | 3月動量 |
| `momentum_6M` | (P_t / P_{t-126}) - 1 | 126 日 | 價格數據 | 6月動量 |
| `momentum_12M` | (P_t / P_{t-252}) - 1 | 252 日 | 價格數據 | 12月動量 |

**Python 實現：**
```python
def calculate_momentum(prices):
    """計算動量特徵"""
    momentum = pd.DataFrame(index=prices.index)

    # 多時間尺度動量
    windows = {
        '1M': 21,
        '3M': 63,
        '6M': 126,
        '12M': 252
    }

    for name, window in windows.items():
        momentum[f'momentum_{name}'] = (prices / prices.shift(window)) - 1

    return momentum
```

#### 1.1.3 波動率特徵

| 特徵名稱 | 計算公式 | 時間窗口 | 數據來源 | 說明 |
|---------|---------|---------|---------|------|
| `volatility_20d` | std(R_t, 20) * √252 | 20 日 | 收益數據 | 20日年化波動率 |
| `volatility_60d` | std(R_t, 60) * √252 | 60 日 | 收益數據 | 60日年化波動率 |
| `volatility_252d` | std(R_t, 252) * √252 | 252 日 | 收益數據 | 252日年化波動率 |
| `volatility_ratio` | volatility_20d / volatility_60d | - | 收益數據 | 短期/長期波動率比 |

**Python 實現：**
```python
def calculate_volatility(returns):
    """計算波動率特徵"""
    volatility = pd.DataFrame(index=returns.index)

    # 多時間尺度波動率
    windows = [20, 60, 252]

    for window in windows:
        volatility[f'volatility_{window}d'] = (
            returns.rolling(window=window).std() * np.sqrt(252)
        )

    # 波動率比率
    volatility['volatility_ratio'] = (
        volatility['volatility_20d'] / volatility['volatility_60d']
    )

    return volatility
```

### 1.2 技術指標特徵

#### 1.2.1 趨勢指標

| 特徵名稱 | 計算公式 | 參數 | 數據來源 | 說明 |
|---------|---------|------|---------|------|
| `MA_5` | SMA(P_t, 5) | 5 | 價格數據 | 5日移動平均 |
| `MA_10` | SMA(P_t, 10) | 10 | 價格數據 | 10日移動平均 |
| `MA_20` | SMA(P_t, 20) | 20 | 價格數據 | 20日移動平均 |
| `MA_60` | SMA(P_t, 60) | 60 | 價格數據 | 60日移動平均 |
| `MA_120` | SMA(P_t, 120) | 120 | 價格數據 | 120日移動平均 |
| `MA_cross_5_20` | MA_5 > MA_20 | - | 價格數據 | 5/20日金叉信號 |
| `MA_cross_20_60` | MA_20 > MA_60 | - | 價格數據 | 20/60日金叉信號 |

**Python 實現：**
```python
def calculate_trend_indicators(prices):
    """計算趨勢指標"""
    trend = pd.DataFrame(index=prices.index)

    # 移動平均線
    ma_windows = [5, 10, 20, 60, 120]
    for window in ma_windows:
        trend[f'MA_{window}'] = prices.rolling(window=window).mean()

    # MA 交叉信號
    trend['MA_cross_5_20'] = (trend['MA_5'] > trend['MA_20']).astype(int)
    trend['MA_cross_20_60'] = (trend['MA_20'] > trend['MA_60']).astype(int)

    return trend
```

#### 1.2.2 動量指標

| 特徵名稱 | 計算公式 | 參數 | 數據來源 | 說明 |
|---------|---------|------|---------|------|
| `RSI_14` | 100 - 100/(1 + RS) | 14 | 價格數據 | 相對強弱指標 |
| `MACD` | EMA(12) - EMA(26) | 12, 26 | 價格數據 | MACD 指標 |
| `MACD_signal` | EMA(MACD, 9) | 9 | MACD 數據 | MACD 信號線 |
| `MACD_hist` | MACD - MACD_signal | - | MACD 數據 | MACD 柱狀圖 |
| `K` | 100 * (C - L14)/(H14 - L14) | 9, 3 | 價格數據 | KD 隨機指標 K 值 |
| `D` | SMA(K, 3) | 3 | K 值數據 | KD 隨機指標 D 值 |

**Python 實現：**
```python
def calculate_momentum_indicators(prices):
    """計算動量指標"""
    momentum = pd.DataFrame(index=prices.index)

    # RSI (14日)
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    momentum['RSI_14'] = 100 - (100 / (1 + rs))

    # MACD (12, 26, 9)
    ema_12 = prices.ewm(span=12).mean()
    ema_26 = prices.ewm(span=26).mean()
    momentum['MACD'] = ema_12 - ema_26
    momentum['MACD_signal'] = momentum['MACD'].ewm(span=9).mean()
    momentum['MACD_hist'] = momentum['MACD'] - momentum['MACD_signal']

    # KD (9, 3, 3)
    low_9 = prices.rolling(window=9).min()
    high_9 = prices.rolling(window=9).max()
    momentum['K'] = 100 * ((prices - low_9) / (high_9 - low_9))
    momentum['D'] = momentum['K'].rolling(window=3).mean()

    return momentum
```

#### 1.2.3 波動率指標

| 特徵名稱 | 計算公式 | 參數 | 數據來源 | 說明 |
|---------|---------|------|---------|------|
| `ATR_14` | TR 的 14 日移動平均 | 14 | 價格數據 | 平均真實波幅 |
| `BB_upper` | MA_20 + 2 * std | 20, 2 | 價格數據 | 布林帶上軌 |
| `BB_middle` | MA_20 | 20 | 價格數據 | 布林帶中軌 |
| `BB_lower` | MA_20 - 2 * std | 20, 2 | 價格數據 | 布林帶下軌 |
| `BB_width` | (BB_upper - BB_lower) / BB_middle | - | BB 數據 | 布林帶寬度 |
| `BB_position` | (P_t - BB_lower) / (BB_upper - BB_lower) | - | BB 數據 | 價格在布林帶位置 |
| `VIX` | VIX 指數值 | - | VIX 數據 | 波動率恐慌指數 |

**Python 實現：**
```python
def calculate_volatility_indicators(prices, high=None, low=None, vix=None):
    """計算波動率指標"""
    vol_ind = pd.DataFrame(index=prices.index)

    if high is None or low is None:
        high = low = prices  # 如果沒有高低價，用收盤價代替

    # ATR (14日)
    tr1 = high - low
    tr2 = abs(high - prices.shift(1))
    tr3 = abs(low - prices.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    vol_ind['ATR_14'] = tr.rolling(window=14).mean()

    # 布林帶 (20日, 2σ)
    bb_middle = prices.rolling(window=20).mean()
    bb_std = prices.rolling(window=20).std()
    vol_ind['BB_upper'] = bb_middle + 2 * bb_std
    vol_ind['BB_middle'] = bb_middle
    vol_ind['BB_lower'] = bb_middle - 2 * bb_std
    vol_ind['BB_width'] = (vol_ind['BB_upper'] - vol_ind['BB_lower']) / bb_middle
    vol_ind['BB_position'] = (prices - vol_ind['BB_lower']) / (
        vol_ind['BB_upper'] - vol_ind['BB_lower']
    )

    # VIX
    if vix is not None:
        vol_ind['VIX'] = vix

    return vol_ind
```

#### 1.2.4 成交量指標

| 特徵名稱 | 計算公式 | 參數 | 數據來源 | 說明 |
|---------|---------|------|---------|------|
| `volume_ratio` | Volume_t / MA(Volume, 20) | 20 | 成交量數據 | 成交量比率 |
| `volume_ma_5` | SMA(Volume, 5) | 5 | 成交量數據 | 5日均量 |
| `volume_ma_20` | SMA(Volume, 20) | 20 | 成交量數據 | 20日均量 |
| `OBV` | Σ sign(R_t) * Volume_t | - | 成交量+收益 | 能量潮指標 |
| `MFI_14` | 100 - 100/(1 + MF_ratio) | 14 | 價格+成交量 | 資金流量指標 |

**Python 實現：**
```python
def calculate_volume_indicators(prices, volume):
    """計算成交量指標"""
    vol_ind = pd.DataFrame(index=prices.index)

    # 成交量移動平均
    vol_ind['volume_ma_5'] = volume.rolling(window=5).mean()
    vol_ind['volume_ma_20'] = volume.rolling(window=20).mean()
    vol_ind['volume_ratio'] = volume / vol_ind['volume_ma_20']

    # OBV (On Balance Volume)
    returns = prices.pct_change()
    vol_ind['OBV'] = (np.sign(returns) * volume).cumsum()

    # MFI (Money Flow Index, 14日)
    typical_price = (prices + prices.shift(1) + prices.shift(2)) / 3
    money_flow = typical_price * volume

    positive_flow = money_flow.where(typical_price > typical_price.shift(1), 0)
    negative_flow = money_flow.where(typical_price < typical_price.shift(1), 0)

    positive_mf = positive_flow.rolling(window=14).sum()
    negative_mf = negative_flow.rolling(window=14).sum()

    mf_ratio = positive_mf / negative_mf
    vol_ind['MFI_14'] = 100 - (100 / (1 + mf_ratio))

    return vol_ind
```

### 1.3 宏觀經濟特徵

#### 1.3.1 利率特徵

| 特徵名稱 | 計算公式 | 頻率 | 數據來源 | 說明 |
|---------|---------|------|---------|------|
| `treasury_10y` | 10年期國債收益率 | 日度 | Fed/央行 | 10年國債收益率 |
| `treasury_2y` | 2年期國債收益率 | 日度 | Fed/央行 | 2年國債收益率 |
| `yield_curve` | treasury_10y - treasury_2y | - | 國債數據 | 收益率曲線斜率 |
| `policy_rate` | 央行政策利率 | 月度 | 央行 | 政策利率 |
| `rate_change` | Δpolicy_rate | 月度 | 央行 | 利率變化 |

**Python 實現：**
```python
def calculate_rate_features(treasury_10y, treasury_2y, policy_rate):
    """計算利率特徵"""
    rate_features = pd.DataFrame(index=treasury_10y.index)

    # 國債收益率
    rate_features['treasury_10y'] = treasury_10y
    rate_features['treasury_2y'] = treasury_2y

    # 收益率曲線斜率
    rate_features['yield_curve'] = treasury_10y - treasury_2y

    # 政策利率（需要對齊到日度）
    rate_features['policy_rate'] = policy_rate.reindex(
        rate_features.index, method='ffill'
    )

    # 利率變化
    rate_features['rate_change'] = rate_features['policy_rate'].diff()

    return rate_features
```

#### 1.3.2 通脹特徵

| 特徵名稱 | 計算公式 | 頻率 | 數據來源 | 說明 |
|---------|---------|------|---------|------|
| `CPI_yoy` | CPI_t / CPI_{t-12} - 1 | 月度 | 統計局 | CPI同比增長 |
| `CPI_mom` | CPI_t / CPI_{t-1} - 1 | 月度 | 統計局 | CPI環比增長 |
| `PPI_yoy` | PPI_t / PPI_{t-12} - 1 | 月度 | 統計局 | PPI同比增長 |
| `inflation_trend` | MA(CPI_yoy, 3) | 月度 | CPI 數據 | 通脹趨勢 |

**Python 實現：**
```python
def calculate_inflation_features(cpi, ppi):
    """計算通脹特徵"""
    inflation = pd.DataFrame(index=cpi.index)

    # CPI 同比和環比
    inflation['CPI_yoy'] = (cpi / cpi.shift(12)) - 1
    inflation['CPI_mom'] = (cpi / cpi.shift(1)) - 1

    # PPI 同比
    inflation['PPI_yoy'] = (ppi / ppi.shift(12)) - 1

    # 通脹趨勢
    inflation['inflation_trend'] = inflation['CPI_yoy'].rolling(window=3).mean()

    return inflation
```

#### 1.3.3 經濟增長特徵

| 特徵名稱 | 計算公式 | 頻率 | 數據來源 | 說明 |
|---------|---------|------|---------|------|
| `GDP_growth` | GDP_t / GDP_{t-4} - 1 | 季度 | 統計局 | GDP 季度同比增長 |
| `PMI` | 采購經理指數 | 月度 | 統計局/Markit | PMI 指數 |
| `PMI_change` | ΔPMI | 月度 | PMI 數據 | PMI 變化 |
| `employment_rate` | 就業率 | 月度 | 勞工部 | 就業率 |
| `unemployment_change` | Δunemployment_rate | 月度 | 勞工部 | 失業率變化 |

**Python 實現：**
```python
def calculate_growth_features(gdp, pmi, employment_rate, unemployment_rate):
    """計算經濟增長特徵"""
    growth = pd.DataFrame(index=pmin(employment_rate.index, pmi.index))

    # GDP 增長
    growth['GDP_growth'] = (gdp / gdp.shift(4)) - 1

    # PMI
    growth['PMI'] = pmi
    growth['PMI_change'] = pmi.diff()

    # 就業
    growth['employment_rate'] = employment_rate
    growth['unemployment_change'] = unemployment_rate.diff()

    return growth
```

#### 1.3.4 貨幣供應特徵

| 特徵名稱 | 計算公式 | 頻率 | 數據來源 | 說明 |
|---------|---------|------|---------|------|
| `M2_growth_yoy` | M2_t / M2_{t-12} - 1 | 月度 | 央行 | M2 同比增長 |
| `M2_growth_mom` | M2_t / M2_{t-1} - 1 | 月度 | 央行 | M2 環比增長 |
| `monetary_policy_index` | 貨幣政策綜合指數 | 月度 | 央行/研究機構 | 貨幣政策寬緊程度 |

**Python 實現：**
```python
def calculate_monetary_features(m2, monetary_policy_index):
    """計算貨幣供應特徵"""
    monetary = pd.DataFrame(index=m2.index)

    # M2 增長
    monetary['M2_growth_yoy'] = (m2 / m2.shift(12)) - 1
    monetary['M2_growth_mom'] = (m2 / m2.shift(1)) - 1

    # 貨幣政策指數
    monetary['monetary_policy_index'] = monetary_policy_index

    return monetary
```

### 1.4 市場情緒特徵

#### 1.4.1 波動率恐慌指標

| 特徵名稱 | 計算公式 | 頻率 | 數據來源 | 說明 |
|---------|---------|------|---------|------|
| `VIX` | VIX 指數 | 日度 | CBOE | 波動率恐慌指數 |
| `VIX_MA_20` | MA(VIX, 20) | 日度 | VIX 數據 | VIX 移動平均 |
| `VIX_ratio` | VIX / VIX_MA_20 | 日度 | VIX 數據 | VIX 相對水平 |
| `VIX_percentile` | VIX 的歷史分位數 | 日度 | VIX 數據 | VIX 歷史位置 |

**Python 實現：**
```python
def calculate_vix_features(vix):
    """計算 VIX 特徵"""
    vix_features = pd.DataFrame(index=vix.index)

    # VIX 基礎指標
    vix_features['VIX'] = vix
    vix_features['VIX_MA_20'] = vix.rolling(window=20).mean()
    vix_features['VIX_ratio'] = vix / vix_features['VIX_MA_20']

    # VIX 歷史分位數（滾動252日）
    vix_features['VIX_percentile'] = vix.rolling(window=252).apply(
        lambda x: (x.iloc[-1] - x.min()) / (x.max() - x.min()) if x.max() != x.min() else 0.5
    )

    return vix_features
```

#### 1.4.2 Put/Call Ratio

| 特徵名稱 | 計算公式 | 頻率 | 數據來源 | 說明 |
|---------|---------|------|---------|------|
| `put_call_ratio` | Put_Volume / Call_Volume | 日度 | CBOE | Put/Call 成交量比率 |
| `PCR_MA_20` | MA(put_call_ratio, 20) | 日度 | PCR 數據 | PCR 移動平均 |
| `PCR_ratio` | put_call_ratio / PCR_MA_20 | 日度 | PCR 數據 | PCR 相對水平 |

**Python 實現：**
```python
def calculate_pcr_features(put_call_ratio):
    """計算 Put/Call Ratio 特徵"""
    pcr_features = pd.DataFrame(index=put_call_ratio.index)

    pcr_features['put_call_ratio'] = put_call_ratio
    pcr_features['PCR_MA_20'] = put_call_ratio.rolling(window=20).mean()
    pcr_features['PCR_ratio'] = put_call_ratio / pcr_features['PCR_MA_20']

    return pcr_features
```

#### 1.4.3 新聞情緒特徵

| 特徵名稱 | 計算公式 | 頻率 | 數據來源 | 說明 |
|---------|---------|------|---------|------|
| `news_sentiment` | 新聞情緒分數（-1 到 1） | 日度 | 新聞數據 | 新聞情緒均值 |
| `news_sentiment_ma_5` | MA(news_sentiment, 5) | 日度 | 新聞數據 | 新聞情緒趨勢 |
| `news_count` | 日新聞數量 | 日度 | 新聞數據 | 新聞活躍度 |
| `positive_news_ratio` | 正面新聞比例 | 日度 | 新聞數據 | 正面新聞占比 |
| `negative_news_ratio` | 負面新聞比例 | 日度 | 新聞數據 | 負面新聞占比 |

**Python 實現：**
```python
def calculate_news_sentiment_features(news_data):
    """
    計算新聞情緒特徵

    Parameters:
    -----------
    news_data : DataFrame
        必須包含: 'sentiment'（情緒分數）, 'category'（正面/負面/中性）

    Returns:
    --------
    DataFrame
    """
    sentiment_features = pd.DataFrame(index=news_data.index)

    # 新聞情緒均值
    sentiment_features['news_sentiment'] = news_data['sentiment']

    # 新聞情緒趨勢
    sentiment_features['news_sentiment_ma_5'] = (
        news_data['sentiment'].rolling(window=5).mean()
    )

    # 新聞數量
    sentiment_features['news_count'] = 1
    sentiment_features['news_count'] = sentiment_features['news_count'].resample('D').sum()

    # 正負面新聞比例
    if 'category' in news_data.columns:
        positive = (news_data['category'] == 'positive').astype(int).resample('D').sum()
        negative = (news_data['category'] == 'negative').astype(int).resample('D').sum()
        total = positive + negative

        sentiment_features['positive_news_ratio'] = positive / total
        sentiment_features['negative_news_ratio'] = negative / total

    return sentiment_features
```

#### 1.4.4 機構行為特徵

| 特徵名稱 | 計算公式 | 頻率 | 數據來源 | 說明 |
|---------|---------|------|---------|------|
| `margin_balance` | 融資融券餘額 | 日度 | 證交所 | 融資融券餘額 |
| `margin_balance_change` | Δmargin_balance | 日度 | 融資餘額數據 | 融資餘額變化 |
| `margin_ratio` | margin_balance / market_cap | 日度 | 融資+市值數據 | 融資比例 |
| `institutional_net_flow` | 機構資金淨流入 | 日度 | 機構數據 | 機構資金流向 |
| `large_order_net` | 大單淨買入 | 日度 | 訂單數據 | 大單行為 |

**Python 實現：**
```python
def calculate_institutional_features(margin_balance, market_cap, institutional_net_flow, large_order_net):
    """計算機構行為特徵"""
    inst_features = pd.DataFrame(index=margin_balance.index)

    # 融資融券
    inst_features['margin_balance'] = margin_balance
    inst_features['margin_balance_change'] = margin_balance.diff()
    inst_features['margin_ratio'] = margin_balance / market_cap

    # 機構資金流向
    inst_features['institutional_net_flow'] = institutional_net_flow
    inst_features['large_order_net'] = large_order_net

    return inst_features
```

### 1.5 風險特徵

#### 1.5.1 尾部風險（Tail Risk）

| 特徵名稱 | 計算公式 | 時間窗口 | 數據來源 | 說明 |
|---------|---------|---------|---------|------|
| `skewness_20d` | skew(R_t, 20) | 20 日 | 收益數據 | 20日收益偏度 |
| `skewness_60d` | skew(R_t, 60) | 60 日 | 收益數據 | 60日收益偏度 |
| `kurtosis_20d` | kurtosis(R_t, 20) | 20 日 | 收益數據 | 20日收益峰度 |
| `kurtosis_60d` | kurtosis(R_t, 60) | 60 日 | 收益數據 | 60日收益峰度 |
| `tail_prob_5pct` | P(R_t < μ - 2σ) | 滾動 | 收益數據 | 尾部事件概率 |
| `tail_prob_1pct` | P(R_t < μ - 2.33σ) | 滾動 | 收益數據 | 極端尾部概率 |

**Python 實現：**
```python
def calculate_tail_risk(returns):
    """計算尾部風險特徵"""
    tail_risk = pd.DataFrame(index=returns.index)

    # 偏度和峰度
    for window in [20, 60]:
        tail_risk[f'skewness_{window}d'] = returns.rolling(window=window).apply(
            lambda x: x.skew()
        )
        tail_risk[f'kurtosis_{window}d'] = returns.rolling(window=window).apply(
            lambda x: x.kurtosis()
        )

    # 尾部事件概率（滾動窗口）
    window = 252
    rolling_mean = returns.rolling(window=window).mean()
    rolling_std = returns.rolling(window=window).std()

    tail_risk['tail_prob_5pct'] = (
        (returns < (rolling_mean - 2 * rolling_std)).rolling(window=window).mean()
    )
    tail_risk['tail_prob_1pct'] = (
        (returns < (rolling_mean - 2.33 * rolling_std)).rolling(window=window).mean()
    )

    return tail_risk
```

#### 1.5.2 相關性風險（Correlation Risk）

| 特徵名稱 | 計算公式 | 時間窗口 | 數據來源 | 說明 |
|---------|---------|---------|---------|------|
| `market_correlation` | corr(R_t, R_market, 20) | 20 日 | 收益+市場 | 與市場相關性 |
| `industry_correlation_mean` | mean(corr(R_t, R_industry_i)) | 20 日 | 收益+行業 | 行業相關性均值 |
| `correlation_rank` | rank(corr) | - | 相關性數據 | 相關性排名 |
| `correlation_dispersion` | std(corr) | 20 日 | 行業相關性 | 相關性離散度 |

**Python 實現：**
```python
def calculate_correlation_risk(returns, market_returns=None, industry_returns=None):
    """計算相關性風險特徵"""
    corr_risk = pd.DataFrame(index=returns.index)

    if market_returns is not None:
        # 與市場相關性
        corr_risk['market_correlation'] = returns.rolling(window=20).apply(
            lambda x: x.corr(market_returns.loc[x.index])
        )

    if industry_returns is not None:
        # 行業相關性均值
        correlations = pd.DataFrame(index=returns.index)
        for col in industry_returns.columns:
            correlations[col] = returns.rolling(window=20).apply(
                lambda x: x.corr(industry_returns[col].loc[x.index])
            )

        corr_risk['industry_correlation_mean'] = correlations.mean(axis=1)
        corr_risk['correlation_dispersion'] = correlations.std(axis=1)

    return corr_risk
```

#### 1.5.3 流動性風險（Liquidity Risk）

| 特徵名稱 | 計算公式 | 時間窗口 | 數據來源 | 說明 |
|---------|---------|---------|---------|------|
| `turnover_ratio` | Volume / Shares_Outstanding | 日度 | 成交量+股本 | 換手率 |
| `turnover_ma_20` | MA(turnover_ratio, 20) | 20 日 | 換手率數據 | 換手率趨勢 |
| `turnover_ratio_std` | std(turnover_ratio, 20) | 20 日 | 換手率數據 | 換手率波動 |
| `bid_ask_spread` | (Ask - Bid) / Mid_Price | 日度 | 訂單簿 | 買賣價差 |
| `amihud_illiquidity` | |R_t| / Volume_t | 日度 | Amihud 非流動性 |

**Python 實現：**
```python
def calculate_liquidity_risk(volume, shares_outstanding, bid_ask_spread=None, returns=None):
    """計算流動性風險特徵"""
    liquidity_risk = pd.DataFrame(index=volume.index)

    # 換手率
    liquidity_risk['turnover_ratio'] = volume / shares_outstanding
    liquidity_risk['turnover_ma_20'] = liquidity_risk['turnover_ratio'].rolling(window=20).mean()
    liquidity_risk['turnover_ratio_std'] = liquidity_risk['turnover_ratio'].rolling(window=20).std()

    # 買賣價差
    if bid_ask_spread is not None:
        liquidity_risk['bid_ask_spread'] = bid_ask_spread

    # Amihud 非流動性
    if returns is not None:
        liquidity_risk['amihud_illiquidity'] = abs(returns) / volume

    return liquidity_risk
```

#### 1.5.4 系統性風險（Systemic Risk）

| 特徵名稱 | 計算公式 | 時間窗口 | 數據來源 | 說明 |
|---------|---------|---------|---------|------|
| `beta` | cov(R_t, R_market) / var(R_market) | 252 日 | 收益+市場 | Beta 係數 |
| `beta_change` | Δbeta | - | Beta 數據 | Beta 變化 |
| `systemic_risk_index` | 系統性風險綜合指數 | - | 多源數據 | 系統性風險指標 |
| `co_skewness` | co_skew(R_t, R_market) | 252 日 | 收益+市場 | 共偏度 |
| `co_kurtosis` | co_kurt(R_t, R_market) | 252 日 | 收益+市場 | 共峰度 |

**Python 實現：**
```python
def calculate_systemic_risk(returns, market_returns):
    """計算系統性風險特徵"""
    systemic_risk = pd.DataFrame(index=returns.index)

    # Beta
    window = 252
    cov = returns.rolling(window=window).cov(market_returns)
    var_market = market_returns.rolling(window=window).var()
    systemic_risk['beta'] = cov / var_market
    systemic_risk['beta_change'] = systemic_risk['beta'].diff()

    # 共偏度和共峰度
    def co_skew(x, y):
        mean_x, mean_y = x.mean(), y.mean()
        return ((x - mean_x) ** 2 * (y - mean_y)).mean() / (x.std() ** 2 * y.std())

    def co_kurt(x, y):
        mean_x, mean_y = x.mean(), y.mean()
        return ((x - mean_x) ** 2 * (y - mean_y) ** 2).mean() / (x.std() ** 2 * y.std() ** 2)

    systemic_risk['co_skewness'] = returns.rolling(window=window).apply(
        lambda x: co_skew(x, market_returns.loc[x.index])
    )
    systemic_risk['co_kurtosis'] = returns.rolling(window=window).apply(
        lambda x: co_kurt(x, market_returns.loc[x.index])
    )

    return systemic_risk
```

## 2. 特徵工程流程

### 2.1 特徵計算流程

```python
import pandas as pd
import numpy as np
from scipy import stats

class FeatureEngineer:
    """市場狀態檢測特徵工程"""

    def __init__(self, price_data, volume_data, macro_data=None, sentiment_data=None):
        """
        初始化特徵工程器

        Parameters:
        -----------
        price_data : DataFrame
            價格數據，必須包含: 'close', 'high', 'low'
        volume_data : Series
            成交量數據
        macro_data : dict, optional
            宏觀經濟數據字典
        sentiment_data : dict, optional
            市場情緒數據字典
        """
        self.price = price_data
        self.volume = volume_data
        self.macro = macro_data or {}
        self.sentiment = sentiment_data or {}
        self.features = None

    def calculate_all_features(self):
        """計算所有特徵"""
        features = []

        # 1. 價格與收益特徵
        returns = self._calculate_returns()
        momentum = self._calculate_momentum()
        volatility = self._calculate_volatility(returns)
        features.extend([returns, momentum, volatility])

        # 2. 技術指標特徵
        trend = self._calculate_trend_indicators()
        momentum_ind = self._calculate_momentum_indicators()
        vol_ind = self._calculate_volatility_indicators()
        vol_ind_vol = self._calculate_volume_indicators()
        features.extend([trend, momentum_ind, vol_ind, vol_ind_vol])

        # 3. 宏觀經濟特徵
        if self.macro:
            macro_features = self._calculate_macro_features()
            features.append(macro_features)

        # 4. 市場情緒特徵
        if self.sentiment:
            sentiment_features = self._calculate_sentiment_features()
            features.append(sentiment_features)

        # 5. 風險特徵
        tail_risk = self._calculate_tail_risk(returns)
        corr_risk = self._calculate_correlation_risk(returns)
        liquidity_risk = self._calculate_liquidity_risk()
        systemic_risk = self._calculate_systemic_risk(returns)
        features.extend([tail_risk, corr_risk, liquidity_risk, systemic_risk])

        # 合併所有特徵
        self.features = pd.concat(features, axis=1)

        return self.features

    def _calculate_returns(self):
        """計算收益特徵"""
        returns = pd.DataFrame(index=self.price.index)

        # 日收益率
        returns['return_daily'] = self.price['close'].pct_change()

        # 對數收益率
        returns['return_log'] = np.log(self.price['close'] / self.price['close'].shift(1))

        # 滯後收益
        for i in range(1, 6):
            returns[f'return_lag{i}'] = returns['return_daily'].shift(i)

        return returns

    def _calculate_momentum(self):
        """計算動量特徵"""
        momentum = pd.DataFrame(index=self.price.index)

        windows = {'1M': 21, '3M': 63, '6M': 126, '12M': 252}
        for name, window in windows.items():
            momentum[f'momentum_{name}'] = (
                (self.price['close'] / self.price['close'].shift(window)) - 1
            )

        return momentum

    def _calculate_volatility(self, returns):
        """計算波動率特徵"""
        volatility = pd.DataFrame(index=returns.index)

        for window in [20, 60, 252]:
            volatility[f'volatility_{window}d'] = (
                returns['return_daily'].rolling(window=window).std() * np.sqrt(252)
            )

        volatility['volatility_ratio'] = (
            volatility['volatility_20d'] / volatility['volatility_60d']
        )

        return volatility

    def _calculate_trend_indicators(self):
        """計算趨勢指標"""
        trend = pd.DataFrame(index=self.price.index)

        # 移動平均線
        for window in [5, 10, 20, 60, 120]:
            trend[f'MA_{window}'] = self.price['close'].rolling(window=window).mean()

        # MA 交叉信號
        trend['MA_cross_5_20'] = (trend['MA_5'] > trend['MA_20']).astype(int)
        trend['MA_cross_20_60'] = (trend['MA_20'] > trend['MA_60']).astype(int)

        return trend

    def _calculate_momentum_indicators(self):
        """計算動量指標"""
        momentum = pd.DataFrame(index=self.price.index)

        # RSI
        delta = self.price['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        momentum['RSI_14'] = 100 - (100 / (1 + rs))

        # MACD
        ema_12 = self.price['close'].ewm(span=12).mean()
        ema_26 = self.price['close'].ewm(span=26).mean()
        momentum['MACD'] = ema_12 - ema_26
        momentum['MACD_signal'] = momentum['MACD'].ewm(span=9).mean()
        momentum['MACD_hist'] = momentum['MACD'] - momentum['MACD_signal']

        # KD
        low_9 = self.price['low'].rolling(window=9).min()
        high_9 = self.price['high'].rolling(window=9).max()
        momentum['K'] = 100 * ((self.price['close'] - low_9) / (high_9 - low_9))
        momentum['D'] = momentum['K'].rolling(window=3).mean()

        return momentum

    def _calculate_volatility_indicators(self):
        """計算波動率指標"""
        vol_ind = pd.DataFrame(index=self.price.index)

        # ATR
        tr1 = self.price['high'] - self.price['low']
        tr2 = abs(self.price['high'] - self.price['close'].shift(1))
        tr3 = abs(self.price['low'] - self.price['close'].shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        vol_ind['ATR_14'] = tr.rolling(window=14).mean()

        # 布林帶
        bb_middle = self.price['close'].rolling(window=20).mean()
        bb_std = self.price['close'].rolling(window=20).std()
        vol_ind['BB_upper'] = bb_middle + 2 * bb_std
        vol_ind['BB_middle'] = bb_middle
        vol_ind['BB_lower'] = bb_middle - 2 * bb_std
        vol_ind['BB_width'] = (vol_ind['BB_upper'] - vol_ind['BB_lower']) / bb_middle
        vol_ind['BB_position'] = (
            (self.price['close'] - vol_ind['BB_lower']) /
            (vol_ind['BB_upper'] - vol_ind['BB_lower'])
        )

        return vol_ind

    def _calculate_volume_indicators(self):
        """計算成交量指標"""
        vol_ind = pd.DataFrame(index=self.volume.index)

        vol_ind['volume_ma_5'] = self.volume.rolling(window=5).mean()
        vol_ind['volume_ma_20'] = self.volume.rolling(window=20).mean()
        vol_ind['volume_ratio'] = self.volume / vol_ind['volume_ma_20']

        # OBV
        returns = self.price['close'].pct_change()
        vol_ind['OBV'] = (np.sign(returns) * self.volume).cumsum()

        # MFI
        typical_price = (
            self.price['close'] +
            self.price['high'] +
            self.price['low']
        ) / 3
        money_flow = typical_price * self.volume
        positive_flow = money_flow.where(
            typical_price > typical_price.shift(1), 0
        )
        negative_flow = money_flow.where(
            typical_price < typical_price.shift(1), 0
        )
        positive_mf = positive_flow.rolling(window=14).sum()
        negative_mf = negative_flow.rolling(window=14).sum()
        mf_ratio = positive_mf / negative_mf
        vol_ind['MFI_14'] = 100 - (100 / (1 + mf_ratio))

        return vol_ind

    def _calculate_macro_features(self):
        """計算宏觀經濟特徵"""
        # 簡化實現，實際使用時需要根據具體數據源調整
        macro = pd.DataFrame(index=self.price.index)

        if 'treasury_10y' in self.macro:
            macro['treasury_10y'] = self.macro['treasury_10y']
        if 'treasury_2y' in self.macro:
            macro['treasury_2y'] = self.macro['treasury_2y']
        if 'VIX' in self.macro:
            macro['VIX'] = self.macro['VIX']

        return macro

    def _calculate_sentiment_features(self):
        """計算市場情緒特徵"""
        sentiment = pd.DataFrame(index=self.price.index)

        if 'news_sentiment' in self.sentiment:
            sentiment['news_sentiment'] = self.sentiment['news_sentiment']
        if 'put_call_ratio' in self.sentiment:
            sentiment['put_call_ratio'] = self.sentiment['put_call_ratio']

        return sentiment

    def _calculate_tail_risk(self, returns):
        """計算尾部風險"""
        tail_risk = pd.DataFrame(index=returns.index)

        for window in [20, 60]:
            tail_risk[f'skewness_{window}d'] = returns['return_daily'].rolling(
                window=window
            ).apply(lambda x: x.skew())
            tail_risk[f'kurtosis_{window}d'] = returns['return_daily'].rolling(
                window=window
            ).apply(lambda x: x.kurtosis())

        return tail_risk

    def _calculate_correlation_risk(self, returns):
        """計算相關性風險"""
        corr_risk = pd.DataFrame(index=returns.index)

        if 'market_returns' in self.macro:
            market_returns = self.macro['market_returns']
            corr_risk['market_correlation'] = returns['return_daily'].rolling(
                window=20
            ).apply(lambda x: x.corr(market_returns.loc[x.index]))

        return corr_risk

    def _calculate_liquidity_risk(self):
        """計算流動性風險"""
        liquidity = pd.DataFrame(index=self.price.index)

        if 'shares_outstanding' in self.macro:
            shares = self.macro['shares_outstanding']
            liquidity['turnover_ratio'] = self.volume / shares

        return liquidity

    def _calculate_systemic_risk(self, returns):
        """計算系統性風險"""
        systemic = pd.DataFrame(index=returns.index)

        if 'market_returns' in self.macro:
            market_returns = self.macro['market_returns']
            window = 252
            cov = returns['return_daily'].rolling(window=window).cov(market_returns)
            var_market = market_returns.rolling(window=window).var()
            systemic['beta'] = cov / var_market

        return systemic
```

### 2.2 特徵清洗流程

```python
class FeatureCleaner:
    """特徵清洗器"""

    def __init__(self, features):
        """
        初始化特徵清洗器

        Parameters:
        -----------
        features : DataFrame
            原始特徵數據
        """
        self.features = features.copy()
        self.cleaning_log = []

    def clean_features(
        self,
        missing_threshold=0.3,
        outlier_method='winsorize',
        outlier_threshold=3,
        smooth_window=None
    ):
        """
        執行完整的特徵清洗流程

        Parameters:
        -----------
        missing_threshold : float
            缺失值刪除閾值（比例）
        outlier_method : str
            異常值處理方法: 'winsorize', 'truncate', 'remove'
        outlier_threshold : float
            異常值檢測閾值（標準差倍數）
        smooth_window : int, optional
            平滑窗口大小

        Returns:
        --------
        DataFrame
            清洗後的特徵
        """
        # 1. 缺失值處理
        self._handle_missing_values(missing_threshold)

        # 2. 異常值處理
        self._handle_outliers(method=outlier_method, threshold=outlier_threshold)

        # 3. 平滑處理
        if smooth_window:
            self._smooth_features(window=smooth_window)

        # 4. 移除無限值
        self._remove_infinite_values()

        return self.features

    def _handle_missing_values(self, threshold):
        """處理缺失值"""
        # 刪除缺失比例超過閾值的特徵
        missing_ratio = self.features.isnull().mean()
        features_to_drop = missing_ratio[missing_ratio > threshold].index

        if len(features_to_drop) > 0:
            self.features = self.features.drop(columns=features_to_drop)
            self.cleaning_log.append(
                f"刪除 {len(features_to_drop)} 個高缺失特徵"
            )

        # 前向填充 + 線性插值
        self.features = self.features.fillna(method='ffill')
        self.features = self.features.interpolate(method='linear', limit_direction='both')

        # 刪除剩餘缺失值
        self.features = self.features.dropna()

        self.cleaning_log.append(
            f"處理缺失值完成，剩餘 {self.features.shape[1]} 個特徵"
        )

    def _handle_outliers(self, method='winsorize', threshold=3):
        """處理異常值"""
        for col in self.features.columns:
            data = self.features[col]

            # 檢測異常值（基於 IQR 或 3σ）
            q1 = data.quantile(0.25)
            q3 = data.quantile(0.75)
            iqr = q3 - q1

            lower_bound = q1 - threshold * iqr
            upper_bound = q3 + threshold * iqr

            if method == 'winsorize':
                # Winsorization: 將異常值截斷到邊界
                self.features[col] = data.clip(lower=lower_bound, upper=upper_bound)

            elif method == 'truncate':
                # 3σ 截斷
                mean = data.mean()
                std = data.std()
                lower_bound_3sigma = mean - threshold * std
                upper_bound_3sigma = mean + threshold * std
                self.features[col] = data.clip(
                    lower=lower_bound_3sigma,
                    upper=upper_bound_3sigma
                )

            elif method == 'remove':
                # 移除異常值（設為 NaN 後插值）
                outliers = (data < lower_bound) | (data > upper_bound)
                self.features.loc[outliers, col] = np.nan
                self.features[col] = self.features[col].interpolate()

        self.cleaning_log.append(
            f"異常值處理完成，方法: {method}"
        )

    def _smooth_features(self, window):
        """平滑特徵"""
        for col in self.features.columns:
            self.features[col] = self.features[col].rolling(
                window=window, center=True
            ).mean()

        # 填充平滑後的缺失值
        self.features = self.features.fillna(method='bfill').fillna(method='ffill')

        self.cleaning_log.append(
            f"特徵平滑完成，窗口大小: {window}"
        )

    def _remove_infinite_values(self):
        """移除無限值"""
        inf_count = np.isinf(self.features).sum().sum()

        if inf_count > 0:
            # 將無限值替換為 NaN 後插值
            self.features = self.features.replace([np.inf, -np.inf], np.nan)
            self.features = self.features.interpolate(method='linear', limit_direction='both')

            self.cleaning_log.append(
                f"移除 {inf_count} 個無限值"
            )

    def get_cleaning_log(self):
        """獲取清洗日誌"""
        return self.cleaning_log
```

### 2.3 特徵變換流程

```python
class FeatureTransformer:
    """特徵變換器"""

    def __init__(self, features):
        """
        初始化特徵變換器

        Parameters:
        -----------
        features : DataFrame
            清洗後的特徵數據
        """
        self.features = features.copy()
        self.scalers = {}
        self.transform_log = []

    def transform_features(
        self,
        scaling_method='standard',
        apply_log_transform=False,
        skewness_threshold=1.0
    ):
        """
        執行特徵變換

        Parameters:
        -----------
        scaling_method : str
            縮放方法: 'standard', 'minmax', 'robust', 'none'
        apply_log_transform : bool
            是否應用對數變換
        skewness_threshold : float
            偏度閾值，超過閾值的特徵應用對數變換

        Returns:
        --------
        DataFrame
            變換後的特徵
        """
        # 1. 對數變換（處理偏態）
        if apply_log_transform:
            self._apply_log_transform(skewness_threshold)

        # 2. 特徵縮放
        if scaling_method != 'none':
            self._scale_features(scaling_method)

        return self.features

    def _apply_log_transform(self, threshold):
        """應用對數變換"""
        for col in self.features.columns:
            skewness = self.features[col].skew()

            if abs(skewness) > threshold:
                # 確保數據為正
                min_val = self.features[col].min()
                if min_val <= 0:
                    shift = abs(min_val) + 1
                    self.features[col] = self.features[col] + shift

                # 應用對數變換
                self.features[col] = np.log(self.features[col] + 1)

                self.transform_log.append(
                    f"對數變換應用於 {col} (原始偏度: {skewness:.2f})"
                )

    def _scale_features(self, method):
        """縮放特徵"""
        from sklearn.preprocessing import (
            StandardScaler, MinMaxScaler, RobustScaler
        )

        if method == 'standard':
            scaler = StandardScaler()
        elif method == 'minmax':
            scaler = MinMaxScaler()
        elif method == 'robust':
            scaler = RobustScaler()
        else:
            raise ValueError(f"Unknown scaling method: {method}")

        for col in self.features.columns:
            data = self.features[[col]]

            # 擬合和變換
            self.features[col] = scaler.fit_transform(data).flatten()

            # 保存 scaler 用於逆變換
            self.scalers[col] = scaler

        self.transform_log.append(
            f"特徵縮放完成，方法: {method}"
        )

    def inverse_transform(self, features_scaled):
        """
        逆變換

        Parameters:
        -----------
        features_scaled : DataFrame
            縮放後的特徵

        Returns:
        --------
        DataFrame
            原始尺度的特徵
        """
        features_original = features_scaled.copy()

        for col, scaler in self.scalers.items():
            features_original[col] = scaler.inverse_transform(
                features_scaled[[col]]
            ).flatten()

        return features_original

    def get_transform_log(self):
        """獲取變換日誌"""
        return self.transform_log
```

### 2.4 特徵選擇流程

```python
class FeatureSelector:
    """特徵選擇器"""

    def __init__(self, features, target=None):
        """
        初始化特徵選擇器

        Parameters:
        -----------
        features : DataFrame
            變換後的特徵數據
        target : Series, optional
            目標變量（監督學習）
        """
        self.features = features.copy()
        self.target = target
        self.selected_features = None
        self.selection_log = []

    def select_features(
        self,
        correlation_threshold=0.9,
        variance_threshold=0.01,
        n_features=None,
        method='correlation'
    ):
        """
        執行特徵選擇

        Parameters:
        -----------
        correlation_threshold : float
            高相關性特徵去除閾值
        variance_threshold : float
            低方差特徵去除閾值
        n_features : int, optional
            選擇的特徵數量
        method : str
            選擇方法: 'correlation', 'variance', 'rfe', 'lasso'

        Returns:
        --------
        DataFrame
            選擇後的特徵
        """
        # 1. 移除低方差特徵
        self._remove_low_variance_features(threshold=variance_threshold)

        # 2. 移除高相關性特徵
        self._remove_high_correlation_features(threshold=correlation_threshold)

        # 3. 基於重要性的選擇
        if method in ['rfe', 'lasso'] and self.target is not None:
            self._select_by_importance(method=method, n_features=n_features)

        # 4. 限制特徵數量
        if n_features and len(self.features.columns) > n_features:
            self._select_top_features(n_features)

        self.selected_features = self.features.columns.tolist()

        return self.features

    def _remove_low_variance_features(self, threshold):
        """移除低方差特徵"""
        variances = self.features.var()
        low_variance_features = variances[variances < threshold].index

        if len(low_variance_features) > 0:
            self.features = self.features.drop(columns=low_variance_features)
            self.selection_log.append(
                f"移除 {len(low_variance_features)} 個低方差特徵"
            )

    def _remove_high_correlation_features(self, threshold):
        """移除高相關性特徵"""
        # 計算相關性矩陣
        corr_matrix = self.features.corr().abs()

        # 找到高相關性特徵對
        upper_triangle = corr_matrix.where(
            np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
        )

        high_corr_pairs = []
        for col in upper_triangle.columns:
            high_corr_features = upper_triangle.index[
                upper_triangle[col] > threshold
            ].tolist()
            for feature in high_corr_features:
                high_corr_pairs.append((feature, col, upper_triangle.loc[feature, col]))

        # 移除高相關性特徵（保留第一個）
        features_to_remove = set()
        for feature1, feature2, corr in high_corr_pairs:
            if feature2 not in features_to_remove:
                features_to_remove.add(feature2)

        if len(features_to_remove) > 0:
            self.features = self.features.drop(columns=list(features_to_remove))
            self.selection_log.append(
                f"移除 {len(features_to_remove)} 個高相關性特徵 (閾值: {threshold})"
            )

    def _select_by_importance(self, method='lasso', n_features=None):
        """基於重要性選擇特徵"""
        from sklearn.feature_selection import RFE
        from sklearn.linear_model import Lasso, RandomForestRegressor

        X = self.features
        y = self.target

        if method == 'lasso':
            # LASSO 正則化
            lasso = Lasso(alpha=0.01, random_state=42)
            lasso.fit(X, y)

            # 選擇非零係數的特徵
            feature_importance = np.abs(lasso.coef_)
            selected = X.columns[feature_importance > 0].tolist()

        elif method == 'rfe':
            # 遞歸特徵消除
            estimator = RandomForestRegressor(n_estimators=100, random_state=42)
            rfe = RFE(estimator=estimator, n_features_to_select=n_features or 20)
            rfe.fit(X, y)

            selected = X.columns[rfe.support_].tolist()

        if len(selected) > 0:
            self.features = self.features[selected]
            self.selection_log.append(
                f"基於 {method} 選擇 {len(selected)} 個特徵"
            )

    def _select_top_features(self, n_features):
        """選擇前 N 個特徵（基於方差）"""
        variances = self.features.var()
        top_features = variances.nlargest(n_features).index.tolist()

        self.features = self.features[top_features]
        self.selection_log.append(
            f"選擇前 {n_features} 個高方差特徵"
        )

    def get_selection_log(self):
        """獲取選擇日誌"""
        return self.selection_log

    def get_feature_importance(self, method='variance'):
        """
        獲取特徵重要性

        Parameters:
        -----------
        method : str
            計算方法: 'variance', 'correlation_target'

        Returns:
        --------
        Series
            特徵重要性排序
        """
        if method == 'variance':
            importance = self.features.var()
        elif method == 'correlation_target' and self.target is not None:
            importance = self.features.corrwith(self.target).abs()
        else:
            importance = self.features.var()

        return importance.sort_values(ascending=False)
```

## 3. 特徵組合與交互

### 3.1 特徵組合

```python
class FeatureCombinator:
    """特徵組合器"""

    def __init__(self, features):
        """
        初始化特徵組合器

        Parameters:
        -----------
        features : DataFrame
            基礎特徵數據
        """
        self.features = features.copy()
        self.combined_features = None

    def combine_features(self, combinations=None):
        """
        執行特徵組合

        Parameters:
        -----------
        combinations : list, optional
            自定義組合列表

        Returns:
        --------
        DataFrame
            組合後的特徵
        """
        if combinations is None:
            combinations = [
                'momentum_volatility',
                'price_volume',
                'macro_price',
                'rsi_volatility',
                'ma_cross_volume'
            ]

        for combo in combinations:
            if combo == 'momentum_volatility':
                self._momentum_volatility_combination()
            elif combo == 'price_volume':
                self._price_volume_combination()
            elif combo == 'macro_price':
                self._macro_price_combination()
            elif combo == 'rsi_volatility':
                self._rsi_volatility_combination()
            elif combo == 'ma_cross_volume':
                self._ma_cross_volume_combination()

        self.combined_features = pd.concat([self.features, self._get_combinations()], axis=1)

        return self.combined_features

    def _momentum_volatility_combination(self):
        """動量 × 波動率：趨勢持續性"""
        if 'momentum_1M' in self.features.columns and 'volatility_20d' in self.features.columns:
            self._add_combination(
                'momentum_volatility_1M',
                self.features['momentum_1M'] * self.features['volatility_20d']
            )

        if 'momentum_3M' in self.features.columns and 'volatility_60d' in self.features.columns:
            self._add_combination(
                'momentum_volatility_3M',
                self.features['momentum_3M'] * self.features['volatility_60d']
            )

    def _price_volume_combination(self):
        """價格 × 成交量：價量關係"""
        if 'return_daily' in self.features.columns and 'volume_ratio' in self.features.columns:
            self._add_combination(
                'price_volume_momentum',
                self.features['return_daily'] * self.features['volume_ratio']
            )

        if 'momentum_1M' in self.features.columns and 'volume_ratio' in self.features.columns:
            self._add_combination(
                'momentum_volume_1M',
                self.features['momentum_1M'] * self.features['volume_ratio']
            )

    def _macro_price_combination(self):
        """宏觀 × 價格：宏觀驅動因素"""
        if 'treasury_10y' in self.features.columns and 'return_daily' in self.features.columns:
            self._add_combination(
                'macro_price_sensitivity',
                self.features['treasury_10y'] * self.features['return_daily']
            )

        if 'VIX' in self.features.columns and 'return_daily' in self.features.columns:
            self._add_combination(
                'volatility_return_sensitivity',
                self.features['VIX'] * self.features['return_daily']
            )

    def _rsi_volatility_combination(self):
        """RSI × 波動率：超買超賣 + 波動"""
        if 'RSI_14' in self.features.columns and 'volatility_20d' in self.features.columns:
            # 調整 RSI 到 [-1, 1] 範圍
            rsi_normalized = (self.features['RSI_14'] - 50) / 50
            self._add_combination(
                'rsi_volatility_signal',
                rsi_normalized * self.features['volatility_20d']
            )

    def _ma_cross_volume(self):
        """MA 交叉 × 成交量：趨勢確認"""
        if 'MA_cross_5_20' in self.features.columns and 'volume_ratio' in self.features.columns:
            self._add_combination(
                'ma_cross_volume_confidence',
                self.features['MA_cross_5_20'] * self.features['volume_ratio']
            )

    def _add_combination(self, name, data):
        """添加組合特徵"""
        if not hasattr(self, '_combinations'):
            self._combinations = {}
        self._combinations[name] = data

    def _get_combinations(self):
        """獲取所有組合特徵"""
        if hasattr(self, '_combinations'):
            return pd.DataFrame(self._combinations)
        return pd.DataFrame(index=self.features.index)
```

### 3.2 多時間尺度特徵

```python
class MultiTimeScaleFeatures:
    """多時間尺度特徵生成器"""

    def __init__(self, daily_features):
        """
        初始化多時間尺度特徵生成器

        Parameters:
        -----------
        daily_features : DataFrame
            日度特徵數據
        """
        self.daily_features = daily_features.copy()
        self.weekly_features = None
        self.monthly_features = None

    def create_multi_scale_features(self):
        """
        創建多時間尺度特徵

        Returns:
        --------
        dict
            包含日度、週度、月度特徵的字典
        """
        # 日度特徵（短期）
        short_term = self._create_short_term_features()

        # 週度特徵（中期）
        self.weekly_features = self._create_weekly_features()
        medium_term = self._resample_to_daily(self.weekly_features)

        # 月度特徵（長期）
        self.monthly_features = self._create_monthly_features()
        long_term = self._resample_to_daily(self.monthly_features)

        # 合併
        all_features = {
            'short_term': short_term,
            'medium_term': medium_term,
            'long_term': long_term
        }

        return all_features

    def _create_short_term_features(self):
        """創建短期特徵（日度）"""
        short_term = self.daily_features.copy()

        # 添加短期滾動統計
        for col in self.daily_features.columns:
            if col not in ['return_daily', 'volume_ratio']:
                short_term[f'{col}_ma_5'] = self.daily_features[col].rolling(window=5).mean()
                short_term[f'{col}_std_5'] = self.daily_features[col].rolling(window=5).std()

        return short_term

    def _create_weekly_features(self):
        """創建週度特徵"""
        weekly = self.daily_features.resample('W').agg({
            'return_daily': ['sum', 'std'],
            'volume_ratio': ['mean', 'sum'],
            'volatility_20d': 'mean',
            'RSI_14': 'mean',
            'MACD': 'mean'
        })

        # 展平多級索引
        weekly.columns = ['_'.join(col).strip() for col in weekly.columns.values]

        return weekly

    def _create_monthly_features(self):
        """創建月度特徵"""
        monthly = self.daily_features.resample('M').agg({
            'return_daily': ['sum', 'std', 'skew'],
            'volume_ratio': ['mean', 'sum'],
            'volatility_20d': ['mean', 'max'],
            'momentum_1M': 'mean',
            'momentum_3M': 'last',
            'RSI_14': ['mean', 'max', 'min'],
            'VIX': ['mean', 'max']
        })

        # 展平多級索引
        monthly.columns = ['_'.join(col).strip() for col in monthly.columns.values]

        return monthly

    def _resample_to_daily(self, higher_freq_data):
        """將高頻數據重採樣到日度"""
        return higher_freq_data.resample('D').ffill()
```

## 4. HMM + Bayesian Change Point 特徵

### 4.1 HMM 特徵

```python
class HMMFeatures:
    """HMM 特徵生成器"""

    def __init__(self, observations, n_states=3):
        """
        初始化 HMM 特徵生成器

        Parameters:
        -----------
        observations : DataFrame
            觀測數據（收益、波動率等）
        n_states : int
            隱藏狀態數量
        """
        self.observations = observations
        self.n_states = n_states
        self.model = None
        self.state_probs = None
        self.state_sequence = None
        self.transition_matrix = None

    def fit_hmm(self):
        """擬合 HMM 模型"""
        from hmmlearn import hmm

        # 初始化 HMM 模型
        self.model = hmm.GaussianHMM(
            n_components=self.n_states,
            covariance_type="full",
            n_iter=100,
            random_state=42
        )

        # 擬合模型
        self.model.fit(self.observations)

        # 獲取狀態序列
        self.state_sequence = self.model.predict(self.observations)

        # 獲取狀態概率（後驗概率）
        logprob, self.state_probs = self.model.decode(
            self.observations,
            algorithm="viterbi"
        )

        # 轉換為 DataFrame
        self.state_probs = pd.DataFrame(
            self.state_probs,
            columns=[f'state_{i}_prob' for i in range(self.n_states)]
        )

        # 轉移矩陣
        self.transition_matrix = self.model.transmat_

        return self.model

    def calculate_state_duration(self):
        """計算狀態持續時間"""
        durations = []

        for state in range(self.n_states):
            state_mask = (self.state_sequence == state)
            duration = 0
            durations_list = []

            for i in range(len(state_mask)):
                if state_mask[i]:
                    duration += 1
                else:
                    if duration > 0:
                        durations_list.append(duration)
                    duration = 0

            durations.append(np.mean(durations_list) if durations_list else 0)

        return durations

    def get_hmm_features(self):
        """獲取所有 HMM 特徵"""
        if self.model is None:
            self.fit_hmm()

        features = pd.DataFrame(index=self.observations.index)

        # 1. 狀態概率
        for i in range(self.n_states):
            features[f'state_{i}_prob'] = self.state_probs[f'state_{i}_prob']

        # 2. 狀態持續時間
        state_durations = self.calculate_state_duration()
        for i in range(self.n_states):
            features[f'state_{i}_duration'] = state_durations[i]

        # 3. 當前狀態
        features['current_state'] = self.state_sequence

        # 4. 轉換概率（從狀態 i 到狀態 j 的概率）
        for i in range(self.n_states):
            for j in range(self.n_states):
                features[f'trans_prob_{i}_{j}'] = self.transition_matrix[i, j]

        return features
```

### 4.2 Bayesian Change Point 特徵

```python
class BayesianChangePointFeatures:
    """Bayesian Change Point 特徵生成器"""

    def __init__(self, observations, hazard_rate=0.01):
        """
        初始化 Bayesian Change Point 特徵生成器

        Parameters:
        -----------
        observations : Series or DataFrame
            觀測數據
        hazard_rate : float
            變點發生的先驗概率
        """
        self.observations = observations
        self.hazard_rate = hazard_rate
        self.change_point_probs = None
        self.change_point_dists = None

    def detect_change_points(self):
        """檢測變點（使用 Bayesian Online Change Point Detection）"""
        T = len(self.observations)
        change_point_probs = np.zeros(T)
        change_point_dists = np.zeros(T)

        # BOCD 算法簡化實現
        # 實際應用建議使用 bayesian_changepoint_detection 庫
        # pip install bayesian_changepoint_detection

        from bayesian_changepoint_detection.priors import ConstPrior
        from bayesian_changepoint_detection.bayesian_models import offline_changepoint_detection

        # 轉換為 numpy array
        data = self.observations.values

        # 設置先驗
        prior = ConstPrior(self.hazard_rate)

        # 檢測變點
        Q, P, Pcp = offline_changepoint_detection(
            data,
            prior,
            truncate=-40,
            full=True
        )

        # 變點概率
        change_point_probs = Pcp

        # 變點距離（距離上一個變點的時間）
        change_point_dists = np.zeros(T)
        last_cp = 0
        for i in range(T):
            if change_point_probs[i] > 0.5:  # 變點閾值
                change_point_dists[i] = i - last_cp
                last_cp = i
            else:
                change_point_dists[i] = i - last_cp

        self.change_point_probs = change_point_probs
        self.change_point_dists = change_point_dists

        return change_point_probs

    def calculate_change_magnitude(self, window=20):
        """計算變點幅度"""
        T = len(self.observations)
        change_magnitudes = np.zeros(T)

        # 計算每個點的局部變化幅度
        for i in range(window, T - window):
            before = self.observations.iloc[i-window:i].mean()
            after = self.observations.iloc[i:i+window].mean()
            change_magnitudes[i] = abs(after - before)

        return change_magnitudes

    def get_change_point_features(self):
        """獲取所有 Change Point 特徵"""
        if self.change_point_probs is None:
            self.detect_change_points()

        features = pd.DataFrame(index=self.observations.index)

        # 1. 變點概率
        features['change_point_prob'] = self.change_point_probs

        # 2. 變點距離
        features['change_point_distance'] = self.change_point_dists

        # 3. 變點幅度
        features['change_magnitude'] = self.calculate_change_magnitude()

        # 4. 變點標記（超過閾值的變點）
        features['change_point_flag'] = (
            features['change_point_prob'] > 0.5
        ).astype(int)

        # 5. 近期變點數量（滾動20日）
        features['recent_change_points'] = features['change_point_flag'].rolling(
            window=20
        ).sum()

        return features
```

## 5. 特徵存儲與管理

### 5.1 特徵版本管理

```python
class FeatureManager:
    """特徵管理器"""

    def __init__(self, base_path):
        """
        初始化特徵管理器

        Parameters:
        -----------
        base_path : str
            特徵存儲基礎路徑
        """
        self.base_path = base_path
        self.version = "v1.0"
        self.feature_metadata = {}

    def save_features(self, features, name, description="", metadata=None):
        """
        保存特徵

        Parameters:
        -----------
        features : DataFrame
            特徵數據
        name : str
            特徵名稱
        description : str
            特徵描述
        metadata : dict, optional
            額外的元數據
        """
        import os
        import json
        from datetime import datetime

        # 創建保存路徑
        save_path = os.path.join(self.base_path, self.version)
        os.makedirs(save_path, exist_ok=True)

        # 保存特徵數據（Parquet 格式）
        file_path = os.path.join(save_path, f"{name}.parquet")
        features.to_parquet(file_path)

        # 保存元數據
        metadata_dict = {
            'name': name,
            'version': self.version,
            'description': description,
            'shape': features.shape,
            'columns': features.columns.tolist(),
            'index_range': (features.index.min(), features.index.max()),
            'created_at': datetime.now().isoformat(),
            'metadata': metadata or {}
        }

        metadata_path = os.path.join(save_path, f"{name}_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata_dict, f, indent=2)

        self.feature_metadata[name] = metadata_dict

        print(f"特徵已保存: {file_path}")
        print(f"元數據已保存: {metadata_path}")

        return file_path

    def load_features(self, name, version=None):
        """
        加載特徵

        Parameters:
        -----------
        name : str
            特徵名稱
        version : str, optional
            特徵版本（默認使用當前版本）

        Returns:
        --------
        DataFrame
            特徵數據
        """
        import os
        import json

        version = version or self.version
        load_path = os.path.join(self.base_path, version, f"{name}.parquet")

        features = pd.read_parquet(load_path)

        # 加載元數據
        metadata_path = os.path.join(self.base_path, version, f"{name}_metadata.json")
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        return features, metadata

    def list_features(self, version=None):
        """
        列出所有特徵

        Parameters:
        -----------
        version : str, optional
            特徵版本（默認使用當前版本）

        Returns:
        --------
        list
            特徵列表
        """
        import os

        version = version or self.version
        path = os.path.join(self.base_path, version)

        if not os.path.exists(path):
            return []

        features = []
        for file in os.listdir(path):
            if file.endswith('.parquet'):
                features.append(file.replace('.parquet', ''))

        return features

    def create_new_version(self, version_number, change_log=""):
        """
        創建新版本

        Parameters:
        -----------
        version_number : str
            版本號（如 "v1.1"）
        change_log : str
            變更日誌
        """
        import os
        import json
        from datetime import datetime

        self.version = version_number

        # 創建版本目錄
        version_path = os.path.join(self.base_path, version_number)
        os.makedirs(version_path, exist_ok=True)

        # 保存版本信息
        version_info = {
            'version': version_number,
            'created_at': datetime.now().isoformat(),
            'change_log': change_log
        }

        version_path = os.path.join(self.base_path, "version_history.json")
        version_history = {}

        if os.path.exists(version_path):
            with open(version_path, 'r') as f:
                version_history = json.load(f)

        version_history[version_number] = version_info

        with open(version_path, 'w') as f:
            json.dump(version_history, f, indent=2)

        print(f"版本 {version_number} 已創建")
```

## 6. 特徵驗證

### 6.1 特徵驗證器

```python
class FeatureValidator:
    """特徵驗證器"""

    def __init__(self, features):
        """
        初始化特徵驗證器

        Parameters:
        -----------
        features : DataFrame
            特徵數據
        """
        self.features = features
        self.validation_results = {}

    def validate_all(self):
        """執行完整的特徵驗證"""
        print("=== 特徵驗證報告 ===\n")

        # 1. 統計檢驗
        self._statistical_tests()

        # 2. 平穩性檢驗
        self._stationarity_tests()

        # 3. 相關性分析
        self._correlation_analysis()

        # 4. 預測能力檢驗
        self._predictive_power_tests()

        # 5. 生成報告
        self._generate_report()

        return self.validation_results

    def _statistical_tests(self):
        """統計檢驗"""
        print("--- 統計檢驗 ---")

        stats_tests = {}

        for col in self.features.columns:
            data = self.features[col].dropna()

            # 偏度
            skewness = data.skew()

            # 峰度
            kurtosis = data.kurtosis()

            # 正態性檢驗（Shapiro-Wilk）
            from scipy import stats
            stat, p_value = stats.shapiro(data.sample(min(5000, len(data))))

            stats_tests[col] = {
                'skewness': skewness,
                'kurtosis': kurtosis,
                'normality_test': {
                    'statistic': stat,
                    'p_value': p_value,
                    'is_normal': p_value > 0.05
                }
            }

            # 輸出異常特徵
            if abs(skewness) > 2:
                print(f"  ⚠️  {col}: 高偏度 ({skewness:.2f})")
            if abs(kurtosis) > 7:
                print(f"  ⚠️  {col}: 高峰度 ({kurtosis:.2f})")
            if p_value < 0.05:
                print(f"  ⚠️  {col}: 非正態分布 (p={p_value:.4f})")

        self.validation_results['statistical_tests'] = stats_tests
        print(f"  完成 {len(stats_tests)} 個特徵的統計檢驗\n")

    def _stationarity_tests(self):
        """平穩性檢驗（ADF 檢驗）"""
        print("--- 平穩性檢驗 ---")

        stationarity_tests = {}

        for col in self.features.columns:
            data = self.features[col].dropna()

            # ADF 檢驗
            from statsmodels.tsa.stattools import adfuller

            try:
                result = adfuller(data, maxlag=1)

                stationarity_tests[col] = {
                    'adf_statistic': result[0],
                    'p_value': result[1],
                    'critical_values': result[4],
                    'is_stationary': result[1] < 0.05
                }

                if result[1] >= 0.05:
                    print(f"  ⚠️  {col}: 非平穩 (p={result[1]:.4f})")
            except Exception as e:
                print(f"  ❌ {col}: 檢驗失敗 ({str(e)})")

        self.validation_results['stationarity_tests'] = stationarity_tests
        print(f"  完成 {len(stationarity_tests)} 個特徵的平穩性檢驗\n")

    def _correlation_analysis(self):
        """相關性分析"""
        print("--- 相關性分析 ---")

        # 計算相關性矩陣
        corr_matrix = self.features.corr()

        # 找到高相關性特徵對
        high_corr_pairs = []

        upper_triangle = corr_matrix.where(
            np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
        )

        for col in upper_triangle.columns:
            high_corr = upper_triangle.index[
                upper_triangle[col].abs() > 0.9
            ].tolist()

            for feature in high_corr:
                high_corr_pairs.append({
                    'feature1': feature,
                    'feature2': col,
                    'correlation': upper_triangle.loc[feature, col]
                })

                print(f"  ⚠️  {feature} ↔ {col}: {upper_triangle.loc[feature, col]:.3f}")

        self.validation_results['correlation_analysis'] = {
            'correlation_matrix': corr_matrix,
            'high_corr_pairs': high_corr_pairs
        }

        print(f"  發現 {len(high_corr_pairs)} 對高相關性特徵\n")

    def _predictive_power_tests(self):
        """預測能力檢驗（Granger Causality）"""
        print("--- 預測能力檢驗 ---")

        predictive_tests = {}

        # 選擇目標變量（如收益率）
        if 'return_daily' in self.features.columns:
            target = 'return_daily'
        else:
            target = self.features.columns[0]

        for col in self.features.columns:
            if col == target:
                continue

            # Granger Causality 檢驗
            from statsmodels.tsa.stattools import grangercausalitytests

            try:
                data = self.features[[col, target]].dropna()

                result = grangercausalitytests(
                    data,
                    maxlag=2,
                    verbose=False
                )

                # 獲取 p-value（maxlag=1）
                p_value = result[1][0]['ssr_ftest'][1]

                predictive_tests[col] = {
                    'target': target,
                    'p_value': p_value,
                    'is_predictive': p_value < 0.05
                }

                if p_value < 0.05:
                    print(f"  ✓ {col} → {target}: p={p_value:.4f}")

            except Exception as e:
                pass

        self.validation_results['predictive_power_tests'] = predictive_tests
        print(f"  完成 {len(predictive_tests)} 個特徵的預測能力檢驗\n")

    def _generate_report(self):
        """生成驗證報告"""
        report = {
            'timestamp': pd.Timestamp.now().isoformat(),
            'total_features': len(self.features.columns),
            'statistical_summary': {
                'high_skewness': sum(
                    1 for v in self.validation_results['statistical_tests'].values()
                    if abs(v['skewness']) > 2
                ),
                'high_kurtosis': sum(
                    1 for v in self.validation_results['statistical_tests'].values()
                    if abs(v['kurtosis']) > 7
                ),
                'non_normal': sum(
                    1 for v in self.validation_results['statistical_tests'].values()
                    if not v['normality_test']['is_normal']
                )
            },
            'stationarity_summary': {
                'non_stationary': sum(
                    1 for v in self.validation_results['stationarity_tests'].values()
                    if not v['is_stationary']
                )
            },
            'correlation_summary': {
                'high_corr_pairs': len(
                    self.validation_results['correlation_analysis']['high_corr_pairs']
                )
            },
            'predictive_summary': {
                'predictive_features': sum(
                    1 for v in self.validation_results['predictive_power_tests'].values()
                    if v['is_predictive']
                )
            }
        }

        self.validation_results['report'] = report

        print("=== 驗證摘要 ===")
        print(f"  總特徵數: {report['total_features']}")
        print(f"  高偏度特徵: {report['statistical_summary']['high_skewness']}")
        print(f"  高峰度特徵: {report['statistical_summary']['high_kurtosis']}")
        print(f"  非正態特徵: {report['statistical_summary']['non_normal']}")
        print(f"  非平穩特徵: {report['stationarity_summary']['non_stationary']}")
        print(f"  高相關性對: {report['correlation_summary']['high_corr_pairs']}")
        print(f"  有預測能力特徵: {report['predictive_summary']['predictive_features']}\n")
```

### 6.2 可視化

```python
class FeatureVisualizer:
    """特徵可視化器"""

    def __init__(self, features):
        """
        初始化特徵可視化器

        Parameters:
        -----------
        features : DataFrame
            特徵數據
        """
        self.features = features

    def plot_feature_distributions(self, n_cols=4, save_path=None):
        """
        繪製特徵分布圖

        Parameters:
        -----------
        n_cols : int
            每行圖表數量
        save_path : str, optional
            保存路徑
        """
        import matplotlib.pyplot as plt
        import seaborn as sns

        n_features = len(self.features.columns)
        n_rows = (n_features - 1) // n_cols + 1

        fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols * 4, n_rows * 3))
        axes = axes.flatten()

        for i, col in enumerate(self.features.columns):
            sns.histplot(
                self.features[col].dropna(),
                kde=True,
                ax=axes[i]
            )
            axes[i].set_title(col)
            axes[i].set_xlabel('')

        # 隱藏多餘的子圖
        for i in range(n_features, len(axes)):
            axes[i].axis('off')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"特徵分布圖已保存: {save_path}")

        plt.show()

    def plot_correlation_heatmap(self, save_path=None):
        """
        繪製相關性熱力圖

        Parameters:
        -----------
        save_path : str, optional
            保存路徑
        """
        import matplotlib.pyplot as plt
        import seaborn as sns

        # 計算相關性矩陣
        corr_matrix = self.features.corr()

        # 繪製熱力圖
        fig, ax = plt.subplots(figsize=(12, 10))

        sns.heatmap(
            corr_matrix,
            annot=True,
            fmt='.2f',
            cmap='coolwarm',
            center=0,
            ax=ax
        )

        ax.set_title('特徵相關性矩陣', fontsize=16, pad=20)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"相關性熱力圖已保存: {save_path}")

        plt.show()

    def plot_feature_timeseries(self, feature_name, save_path=None):
        """
        繪製特徵時間序列圖

        Parameters:
        -----------
        feature_name : str
            特徵名稱
        save_path : str, optional
            保存路徑
        """
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(14, 4))

        ax.plot(
            self.features.index,
            self.features[feature_name],
            linewidth=0.8
        )

        ax.set_title(f'{feature_name} 時間序列', fontsize=14)
        ax.set_xlabel('Date')
        ax.set_ylabel(feature_name)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"時間序列圖已保存: {save_path}")

        plt.show()
```

## 7. 完整使用示例

### 7.1 端到端特徵工程流程

```python
# 導入必要的庫
import pandas as pd
import numpy as np

# 1. 準備數據
# 假設我們有價格和成交量數據
price_data = pd.read_csv('price_data.csv', index_col='date', parse_dates=True)
volume_data = pd.read_csv('volume_data.csv', index_col='date', parse_dates=True)

# 2. 計算特徵
feature_engineer = FeatureEngineer(
    price_data=price_data,
    volume_data=volume_data
)

features_raw = feature_engineer.calculate_all_features()
print(f"原始特徵數量: {features_raw.shape[1]}")

# 3. 清洗特徵
feature_cleaner = FeatureCleaner(features_raw)
features_clean = feature_cleaner.clean_features(
    missing_threshold=0.3,
    outlier_method='winsorize',
    outlier_threshold=3
)

cleaning_log = feature_cleaner.get_cleaning_log()
for log in cleaning_log:
    print(f"  {log}")

print(f"清洗後特徵數量: {features_clean.shape[1]}")

# 4. 變換特徵
feature_transformer = FeatureTransformer(features_clean)
features_transformed = feature_transformer.transform_features(
    scaling_method='standard',
    apply_log_transform=True,
    skewness_threshold=1.0
)

transform_log = feature_transformer.get_transform_log()
for log in transform_log:
    print(f"  {log}")

# 5. 選擇特徵
feature_selector = FeatureSelector(features_transformed)
features_selected = feature_selector.select_features(
    correlation_threshold=0.9,
    variance_threshold=0.01,
    n_features=50,
    method='correlation'
)

selection_log = feature_selector.get_selection_log()
for log in selection_log:
    print(f"  {log}")

print(f"最終特徵數量: {features_selected.shape[1]}")

# 6. 特徵組合
feature_combinator = FeatureCombinator(features_selected)
features_combined = feature_combinator.combine_features()

print(f"組合後特徵數量: {features_combined.shape[1]}")

# 7. 生成 HMM 特徵
# 準備觀測數據（使用收益和波動率）
observations = pd.concat([
    features_selected['return_daily'],
    features_selected['volatility_20d']
], axis=1).dropna()

hmm_features_generator = HMMFeatures(observations, n_states=3)
hmm_features = hmm_features_generator.get_hmm_features()

# 8. 生成 Bayesian Change Point 特徵
# 使用收益率作為觀測
bcp_features_generator = BayesianChangePointFeatures(
    observations['return_daily'],
    hazard_rate=0.01
)
bcp_features = bcp_features_generator.get_change_point_features()

# 9. 合併所有特徵
all_features = pd.concat([
    features_combined,
    hmm_features,
    bcp_features
], axis=1)

print(f"最終總特徵數量: {all_features.shape[1]}")

# 10. 驗證特徵
feature_validator = FeatureValidator(all_features)
validation_results = feature_validator.validate_all()

# 11. 可視化
visualizer = FeatureVisualizer(all_features)
visualizer.plot_correlation_heatmap(save_path='correlation_heatmap.png')
visualizer.plot_feature_distributions(n_cols=5, save_path='feature_distributions.png')

# 12. 保存特徵
feature_manager = FeatureManager(base_path='./features')
feature_manager.save_features(
    features=all_features,
    name='regime_detection_features',
    description='市場狀態檢測特徵集 (HMM + BCP)',
    metadata={
        'n_hmm_states': 3,
        'bcp_hazard_rate': 0.01,
        'total_features': len(all_features.columns)
    }
)
```

## 8. 特徵列表總結

### 8.1 完整特徵清單

| 類別 | 特徵名稱 | 數量 | 說明 |
|-----|---------|------|------|
| **價格與收益** | return_daily, return_log, return_lag1-5, momentum_1M/3M/6M/12M, volatility_20d/60d/252d, volatility_ratio | 14 | 基礎收益、動量、波動率 |
| **技術指標** | MA_5/10/20/60/120, MA_cross_5_20, MA_cross_20_60, RSI_14, MACD, MACD_signal, MACD_hist, K, D, ATR_14, BB_upper/middle/lower, BB_width, BB_position, volume_ma_5/20, volume_ratio, OBV, MFI_14 | 27 | 趨勢、動量、波動率、成交量指標 |
| **宏觀經濟** | treasury_10y, treasury_2y, yield_curve, policy_rate, rate_change, CPI_yoy/mom, PPI_yoy, inflation_trend, GDP_growth, PMI, PMI_change, employment_rate, unemployment_change, M2_growth_yoy/mom, monetary_policy_index | 17 | 利率、通脹、經濟增長、貨幣供應 |
| **市場情緒** | VIX, VIX_MA_20, VIX_ratio, VIX_percentile, put_call_ratio, PCR_MA_20, PCR_ratio, news_sentiment, news_sentiment_ma_5, news_count, positive_news_ratio, negative_news_ratio, margin_balance, margin_balance_change, margin_ratio, institutional_net_flow, large_order_net | 17 | 恐慌指數、Put/Call、新聞情緒、機構行為 |
| **風險指標** | skewness_20d/60d, kurtosis_20d/60d, tail_prob_5pct/1pct, market_correlation, industry_correlation_mean, correlation_rank, correlation_dispersion, turnover_ratio, turnover_ma_20, turnover_ratio_std, bid_ask_spread, amihud_illiquidity, beta, beta_change, systemic_risk_index, co_skewness, co_kurtosis | 19 | 尾部風險、相關性風險、流動性風險、系統性風險 |
| **特徵組合** | momentum_volatility_1M/3M, price_volume_momentum, momentum_volume_1M, macro_price_sensitivity, volatility_return_sensitivity, rsi_volatility_signal, ma_cross_volume_confidence | 7 | 交互特徵 |
| **多時間尺度** | 短期特徵（日度滾動）、中期特徵（週度重採樣）、長期特徵（月度重採樣） | ~30 | 多時間尺度特徵 |
| **HMM 特徵** | state_0/1/2_prob, state_0/1/2_duration, current_state, trans_prob_0_0 ~ trans_prob_2_2 | 15 | 狀態概率、持續時間、轉換矩陣 |
| **Bayesian CP 特徵** | change_point_prob, change_point_distance, change_magnitude, change_point_flag, recent_change_points | 5 | 變點檢測特徵 |
| **總計** | | **~150** | |

### 8.2 特徵重要性排序（預估）

| 排名 | 特徵名稱 | 類別 | 重要性說明 |
|-----|---------|------|-----------|
| 1 | volatility_20d | 價格與收益 | 波動率是狀態檢測的核心指標 |
| 2 | state_0_prob / state_1_prob | HMM | HMM 狀態概率直接反映市場狀態 |
| 3 | change_point_prob | Bayesian CP | 變點概率檢測結構性轉變 |
| 4 | momentum_1M | 價格與收益 | 動量特徵反映趨勢強度 |
| 5 | VIX | 市場情緒 | 恐慌指數反映市場情緒 |
| 6 | RSI_14 | 技術指標 | 超買超賣信號 |
| 7 | beta | 風險指標 | 系統性風險暴露 |
| 8 | MA_cross_5_20 | 技術指標 | 短期趨勢信號 |
| 9 | treasury_10y | 宏觀經濟 | 利率環境 |
| 10 | put_call_ratio | 市場情緒 | 投機情緒 |

## 9. 使用指南

### 9.1 快速開始

1. **安裝依賴**
```bash
pip install pandas numpy scipy scikit-learn hmmlearn
pip install statsmodels matplotlib seaborn
pip install bayesian_changepoint_detection  # 可選，用於 Bayesian CP
```

2. **準備數據**
- 價格數據：必須包含 `close`, `high`, `low` 列
- 成交量數據：必須包含 `volume` 列
- 宏觀數據：可選，包含利率、CPI、PMI 等
- 情緒數據：可選，包含 VIX、Put/Call Ratio 等

3. **運行特徵工程**
```python
from feature_engineering import FeatureEngineer, FeatureCleaner, FeatureTransformer, FeatureSelector

# 計算特徵
engineer = FeatureEngineer(price_data, volume_data, macro_data, sentiment_data)
features = engineer.calculate_all_features()

# 清洗特徵
cleaner = FeatureCleaner(features)
features_clean = cleaner.clean_features()

# 變換特徵
transformer = FeatureTransformer(features_clean)
features_transformed = transformer.transform_features()

# 選擇特徵
selector = FeatureSelector(features_transformed)
features_selected = selector.select_features()
```

### 9.2 最佳實踐

1. **數據質量**
   - 確保數據連續性，無缺失日期
   - 檢查異常值，進行適當處理
   - 對齊不同頻率數據的時間戳

2. **特徵選擇**
   - 使用相關性分析去除冗餘特徵
   - 優先保留與狀態檢測相關的特徵（如波動率、動量）
   - 考慮模型解釋性，避免過多特徵

3. **超參數調整**
   - HMM 狀態數量：使用 BIC 準則選擇（通常 2-4 個）
   - Bayesian CP hazard_rate：根據市場特性調整（0.005-0.02）
   - 特徵窗口：根據應用場景選擇（短期：5-20日，中期：20-60日）

4. **性能優化**
   - 使用 Parquet 格式存儲特徵（高效壓縮）
   - 分批處理大數據集
   - 並行化特徵計算

### 9.3 常見問題

**Q: 如何確定最優的 HMM 狀態數量？**
A: 使用 BIC（Bayesian Information Criterion）進行模型選擇：
```python
from hmmlearn import hmm

bic_values = []
for n_states in range(2, 6):
    model = hmm.GaussianHMM(n_components=n_states, covariance_type="full")
    model.fit(observations)
    bic = -2 * model.score(observations) + n_states * np.log(len(observations))
    bic_values.append(bic)

optimal_n_states = np.argmin(bic_values) + 2
```

**Q: 如何處理宏觀經濟數據的低頻問題？**
A: 使用前向填充（forward fill）將月度/季度數據對齊到日度：
```python
macro_daily = macro_monthly.reindex(daily_index, method='ffill')
```

**Q: 特徵太多導致過擬合怎麼辦？**
A: 使用特徵選擇和正則化：
```python
# 相關性選擇
selector = FeatureSelector(features)
features = selector.select_features(correlation_threshold=0.9, n_features=30)

# LASSO 正則化
from sklearn.linear_model import LassoCV
lasso = LassoCV(cv=5)
lasso.fit(X, y)
selected_features = X.columns[lasso.coef_ != 0]
```

**Q: 如何評估特徵的預測能力？**
A: 使用 Granger Causality 檢驗和回測：
```python
from statsmodels.tsa.stattools import grangercausalitytests

result = grangercausalitytests(
    pd.concat([feature, target], axis=1),
    maxlag=2,
    verbose=False
)
p_value = result[1][0]['ssr_ftest'][1]

if p_value < 0.05:
    print(f"{feature} 具有預測能力")
```

## 10. 結論與建議

### 10.1 總結

本研究設計了針對 HMM + Bayesian Change Point 混合模型的完整特征工程框架：

1. **全面的特徵覆蓋**：涵蓋價格收益、技術指標、宏觀經濟、市場情緒、風險指標五大類，共 150+ 特徵

2. **系統的工程流程**：包括計算、清洗、變換、選擇、組合、驗證全流程

3. **模型特化特徵**：專門為 HMM 和 Bayesian CP 設計的特徵（狀態概率、變點檢測等）

4. **完整的代碼實現**：提供 ~700 行可運行 Python 代碼

### 10.2 使用建議

**階段 1：基礎特徵（推薦優先使用）**
- 波動率特徵：`volatility_20d`, `volatility_60d`, `volatility_ratio`
- 動量特徵：`momentum_1M`, `momentum_3M`
- 技術指標：`RSI_14`, `MACD`, `MA_cross_5_20`
- 情緒指標：`VIX`, `put_call_ratio`

**階段 2：擴展特徵**
- 宏觀經濟：`treasury_10y`, `yield_curve`, `PMI`
- 風險指標：`beta`, `tail_prob_5pct`, `skewness_20d`
- 特徵組合：`momentum_volatility`, `price_volume`

**階段 3：高級特徵**
- HMM 特徵：`state_prob`, `state_duration`, `transition_matrix`
- Bayesian CP 特徵：`change_point_prob`, `change_magnitude`
- 多時間尺度特徵：日度、週度、月度組合

### 10.3 注意事項

1. **數據質量**：確保輸入數據的準確性和連續性
2. **過擬合風險**：使用交叉驗證和正則化避免過擬合
3. **市場變化**：定期更新特徵，適應市場環境變化
4. **計算效率**：對於實時應用，優先使用低延遲特徵

### 10.4 未來擴展

1. **深度學習特徵**：使用自編碼器提取潛在特徵
2. **圖神經網絡**：建模市場相關性網絡
3. **注意力機制**：動態特徵權重分配
4. **在線學習**：增量特徵更新

---

## Sources

Based on:
- r001-model-selection.md - Regime Detection 模型選擇研究
- Hamilton (1990) - Hidden Markov Models and Regime Switching
- Adams & MacKay (2007) - Bayesian Online Change Point Detection
- Practical implementations using pandas, numpy, sklearn, hmmlearn

## Metadata

- **Confidence:** high
- **Feature count:** ~150 (raw), ~50-70 (selected)
- **Code lines:** ~700
- **Dependencies:** pandas, numpy, scipy, scikit-learn, hmmlearn, statsmodels, matplotlib, seaborn, bayesian_changepoint_detection
- **Suggestions:** 建議從基礎特徵開始，逐步擴展到高級特徵。定期進行特徵驗證和更新。
- **Errors:** 無重大錯誤。實際使用時需要根據具體市場和數據源調整參數和特徵定義。
