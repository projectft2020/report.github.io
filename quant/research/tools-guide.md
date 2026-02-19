# 量化研究工具使用指南

**建立日期：** 2026-02-19
**目的：** 建立標準化工具使用流程，避免重複錯誤

---

## 目錄
1. [環境準備](#環境準備)
2. [數據收集](#數據收集)
3. [策略開發](#策略開發)
4. [回測執行](#回測執行)
5. [結果分析](#結果分析)
6. [常見問題](#常見問題)

---

## 環境準備

### 基礎工具安裝

```bash
# Python 基礎環境
python3 --version  # 建議 3.9+
pip install --upgrade pip

# 資料處理
pip install pandas numpy

# 回測框架
pip install vectorbt backtrader zipline

# 技術指標
pip install TA-Lib  # 需要先安裝依賴

# 分析工具
pip install scikit-learn statsmodels

# 可視化
pip install matplotlib seaborn plotly dash

# 風險管理
pip install pyfolio quantstats riskfolio-lib

# 數據源
pip install yfinance alpha_vantage polygon-api-client
```

### 工作目錄結構

```
~/quant-research/
├── data/                    # 數據目錄
│   ├── tickers.csv          # 股票清單
│   └── [ticker]_historical.csv
├── strategies/              # 策略代碼
│   └── [strategy-name].py
├── backtests/               # 回測結果
│   └── [strategy-name]-[timestamp]/
├── notebooks/               # Jupyter notebooks
│   └── [analysis-notebook].ipynb
└── reports/                 # 報告文檔
    └── [report-name].md
```

---

## 數據收集

### yfinance 基礎使用

```python
import yfinance as yf

# 下載單一股票
ticker = "QQQ"
data = yf.download(ticker, start="2010-01-01", end="2025-01-01")

# 下載多隻股票
tickers = ["QQQ", "GLD", "UUP", "TLT"]
data = yf.download(tickers, start="2010-01-01", end="2025-01-01", group_by="ticker")

# 下載特定欄位
data = yf.download(ticker, start="2010-01-01", end="2025-01-01",
                  progress=False)

# 檢查數據
print(data.info())
print(data.head())
print(data.tail())

# 保存數據
data.to_csv(f"{ticker}_historical.csv")
```

### Alpha Vantage 基礎使用

```python
import requests

# 替換為你的 API Key
API_KEY = "YOUR_ALPHA_VANTAGE_API_KEY"

def get_alpha_vantage_data(ticker, function="TIME_SERIES_DAILY"):
    url = f"https://www.alphavantage.co/query?function={function}&symbol={ticker}&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()
    return data
```

---

## 策略開發

### VectorBT 策略工廠

```python
import vectorbt as vbt

# 創建簡單 MA crossover 策略
def ma_cross_strategy(close, fast_period=10, slow_period=60):
    # 計算移動平均
    fast_ma = close.rolling(window=fast_period).mean()
    slow_ma = close.rolling(window=slow_period).mean()

    # 生成信號
    signals = vbt.signals.entry_exit(
        fast_ma > slow_ma,  # 入場信號
        fast_ma < slow_ma  # 出場信號
    )

    return signals

# 執行回測
close_prices = close['Close']
signals = ma_cross_strategy(close_prices)

portfolio = vbt.Portfolio.from_signals(
    close_prices,
    entries=signals.entries,
    exits=signals.exits,
    init_cash=10000,
    freq='1d'
)

# 顯示結果
print(portfolio.stats())
```

### Backtrader 基礎使用

```python
import backtrader as bt

class MAStrategy(bt.Strategy):
    def __init__(self):
        self.fast_ma = bt.indicators.SMA(self.data.close, period=10)
        self.slow_ma = bt.indicators.SMA(self.data.close, period=60)

    def next(self):
        if len(self) > 1:
            if self.fast_ma[0] > self.slow_ma[0] and self.fast_ma[-1] <= self.slow_ma[-1]:
                self.buy()
            elif self.fast_ma[0] < self.slow_ma[0] and self.fast_ma[-1] >= self.slow_ma[-1]:
                self.sell()

# 執行回測
cerebro = bt.Cerebro()
cerebro.addstrategy(MAStrategy)
data = bt.feeds.PandasData(dataname=close_df)
cerebro.adddata(data)
cerebro.run()
```

---

## 回測執行

### 標準回測流程

1. **準備數據**
   ```python
   data = load_data("QQQ", "2010-01-01", "2025-01-01")
   ```

2. **定義策略**
   ```python
   signals = ma_cross_strategy(data['Close'])
   ```

3. **執行回測**
   ```python
   portfolio = vbt.Portfolio.from_signals(
       data['Close'],
       entries=signals.entries,
       exits=signals.exits,
       init_cash=10000,
       freq='1d'
   )
   ```

4. **保存結果**
   ```python
   results = portfolio.stats()
   results.to_csv("backtest_results.csv")
   ```

5. **可視化**
   ```python
   portfolio.plot()
   plt.savefig("backtest_chart.png")
   ```

---

## 結果分析

### 核心指標

```python
# 收益指標
total_return = portfolio.total_return
annualized_return = portfolio.total_return / years
sharpe_ratio = portfolio.sharpe_ratio

# 風險指標
volatility = portfolio.volatility
max_drawdown = portfolio.max_drawdown
value_at_risk = portfolio.value_at_risk

# 交易指標
num_trades = len(portfolio.trades)
avg_trades_per_year = num_trades / years
```

### 使用 pyfolio 分析

```python
import pyfolio as pf

# 生成詳細報告
pf.create_full_tear_sheet(
    portfolio.returns,
    benchmark_returns=benchmark_returns
)
```

### 使用 QuantStats 分析

```python
import quantstats as qs

# 生成報告
qs.reports.full(portfolio.returns, benchmark=benchmark_returns)

# 保存報告
qs.reports.html(portfolio.returns, benchmark=benchmark_returns,
                output="backtest_report.html")
```

---

## 常見問題

### Q1: 數據延遲問題

**問題**：yfinance 數據延遲 15 分鐘

**解決方案**：
```python
# 使用 Alpha Vantage 或 Polygon.io 獲取實時數據
# 或接受延遲（對回測通常無影響）
```

### Q2: 交易成本忽略

**問題**：回測結果過於樂觀

**解決方案**：
```python
# 設置交易成本
portfolio = vbt.Portfolio.from_signals(
    close_prices,
    entries=signals.entries,
    exits=signals.exits,
    commission=0.001,  # 0.1% 交易成本
    freq='1d'
)
```

### Q3: 過度擬合

**問題**：回測效果好但實盤表現差

**解決方案**：
```python
# 使用樣本外測試
train_size = int(len(data) * 0.7)
train_data = data[:train_size]
test_data = data[train_size:]

# 在訓練數據上優化參數
# 在測試數據上驗證
```

### Q4: 數據缺失處理

**問題**：數據中有 NaN 值

**解決方案**：
```python
# 刪除缺失值
data.dropna(inplace=True)

# 前向填充
data.fillna(method='ffill', inplace=True)

# 後向填充
data.fillna(method='bfill', inplace=True)

# 插值
data.interpolate(inplace=True)
```

---

## 最佳實踐

### 1. 數據驗證
- 檢查數據完整性
- 驗證日期範圍
- 確認數據格式

### 2. 參數範圍
- 設定合理的參數範圍
- 避免過度擬合
- 使用交叉驗證

### 3. 成本考慮
- 設置合理的交易成本
- 考慮滑點
- 考慮流動性限制

### 4. 風險管理
- 設定最大回撤限制
- 設定倉位管理
- 設定止損止盈

### 5. 報告透明
- 記錄所有參數
- 記錄所有假設
- 保存完整數據

---

## 相關資源

### 文檔
- [VectorBT 官方文檔](https://vectorbt.dev/)
- [Backtrader 文檔](http://www.backtrader.com/)
- [pyfolio 文檔](https://github.com/quantopian/pyfolio)

### 教程
- [QuantConnect 教程](https://www.quantconnect.com/learn)
- [Investopedia 量化交易](https://www.investopedia.com/quantitative-trading-4698601)

### 社區
- [Quant Connect 社區](https://www.quantconnect.com/forum)
- [Reddit r/algotrading](https://www.reddit.com/r/algotrading)

---

**最後更新：** 2026-02-19
**維護者：** Charlie
