# 跨資產動能策略 - Backtrader 快速範例

**說明**：這個範例使用 Backtrader 框架快速驗證我們的策略概念。

---

## 安裝 Backtrader

```bash
pip install backtrader
```

---

## 基礎策略範例

### 策略 1：單資產動能（QQQ）

```python
import backtrader as bt
import yfinance as yf
import pandas as pd

class MomentumStrategy(bt.Strategy):
    params = (
        ('ma_fast', 10),
        ('ma_mid', 60),
        ('ma_slow', 200),
        ('position_size', 0.2),
    )

    def __init__(self):
        self.ma_fast = bt.indicators.SMA(self.data.close, period=self.params.ma_fast)
        self.ma_mid = bt.indicators.SMA(self.data.close, period=self.params.ma_mid)
        self.ma_slow = bt.indicators.SMA(self.data.close, period=self.params.ma_slow)

    def next(self):
        # 如果沒有倉位
        if not self.position:
            # 做多條件：快線 > 中線 > 慢線
            if self.ma_fast > self.ma_mid > self.ma_slow:
                size = int(self.broker.getcash() * self.params.position_size)
                self.buy(size=size)

        # 如果有倉位
        else:
            # 平倉條件：快線 < 中線 < 慢線
            if self.ma_fast < self.ma_mid < self.ma_slow:
                self.sell(size=self.position.size)


# 執行回測
def run_backtest(symbol='QQQ', start_date='2020-01-01', end_date='2024-01-01'):
    cerebro = bt.Cerebro()

    # 載入數據
    data = bt.feeds.YahooFinanceData(
        dataname=symbol,
        fromdate=pd.to_datetime(start_date),
        todate=pd.to_datetime(end_date)
    )
    cerebro.adddata(data)

    # 加入策略
    cerebro.addstrategy(MomentumStrategy)

    # 設定初始資本
    cerebro.broker.setcash(100000.0)

    # 設定交易成本
    cerebro.broker.setcommission(commission=0.001)  # 0.1% 手續費

    # 執行回測
    print('初始資本: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('最終資本: %.2f' % cerebro.broker.getvalue())

    # 繪製結果
    cerebro.plot()


if __name__ == '__main__':
    run_backtest()
```

---

## 策略 2：跨資產動能

```python
class MultiAssetMomentumStrategy(bt.Strategy):
    params = (
        ('ma_fast', 10),
        ('ma_mid', 60),
        ('ma_slow', 200),
        ('position_size', 0.1),
    )

    def __init__(self):
        self.assets = ['QQQ', 'GLD', 'UUP', 'TLT']
        self.prices = {}

        # 為每個資產創建價格線
        for asset in self.assets:
            self.prices[asset] = bt.indicators.SMA(self.data[asset].close, period=self.params.ma_slow)

    def next(self):
        # 統計做多資產數量
        long_positions = 0

        # 檢查每個資產
        for asset in self.assets:
            ma_fast = bt.indicators.SMA(self.data[asset].close, period=self.params.ma_fast)
            ma_mid = bt.indicators.SMA(self.data[asset].close, period=self.params.ma_mid)
            ma_slow = bt.indicators.SMA(self.data[asset].close, period=self.params.ma_slow)

            # 如果有倉位，檢查是否平倉
            if self.getposition(self.data[asset]).size > 0:
                if ma_fast < ma_mid < ma_slow:
                    self.close(self.data[asset])

            # 如果沒有倉位，檢查是否做多
            elif self.getposition(self.data[asset]).size == 0:
                if ma_fast > ma_mid > ma_slow:
                    size = int(self.broker.getcash() * self.params.position_size)
                    self.buy(data=self.data[asset], size=size)

                    long_positions += 1

        # 極端事件：如果多個資產同時跌破 MA200，降低整體曝險
        if long_positions > 0:
            broken_assets = []

            for asset in self.assets:
                if self.data[asset].close < self.prices[asset]:
                    broken_assets.append(asset)

            if len(broken_assets) >= 2:
                # 降低所有倉位 50%
                for asset in self.assets:
                    if self.getposition(self.data[asset]).size > 0:
                        self.close(self.data[asset])
```

---

## 策略 3：動態槓桿

```python
class VolatilityTargetedStrategy(bt.Strategy):
    params = (
        ('target_vol', 0.15),
        ('min_leverage', 0.7),
        ('max_leverage', 1.2),
        ('lookback', 60),
    )

    def __init__(self):
        self.returns = bt.indicators.ROC(self.data.close, period=1)
        self.volatility = bt.indicators.ATR(period=self.params.lookback) / self.data.close * 100
        self.rolling_vol = self.volatility.rolling(window=self.params.lookback)

    def next(self):
        # 計算當前波動率
        current_vol = self.rolling_vol[-1]

        # 計算動態槓桿
        leverage = self.params.target_vol / current_vol

        # 限制槓桿範圍
        leverage = max(self.params.min_leverage, min(self.params.max_leverage, leverage))

        # 調整倉位大小
        position_size = self.params.position_size * leverage

        # 如果沒有倉位
        if not self.position:
            # 做多條件
            if self.data.close > self.data.close > self.data.close > self.data.close:  # 示例條件
                size = int(self.broker.getcash() * position_size)
                self.buy(size=size)

        # 如果有倉位
        else:
            # 平倉條件
            if self.data.close < self.data.close < self.data.close < self.data.close:
                self.sell(size=self.position.size)

        # 記錄槓桿
        self.log(f'Leverage: {leverage:.2f}')
```

---

## 策略 4：ERC（等風險分配）

```python
class ERCPortfolioStrategy(bt.Strategy):
    params = (
        ('lookback', 60),
    )

    def __init__(self):
        self.returns = {}
        self.volatilities = {}
        self.weights = {}

        # 為每個資產計算回報率
        for asset in ['QQQ', 'GLD', 'UUP', 'TLT']:
            self.returns[asset] = bt.indicators.ROC(self.data[asset].close, period=1)
            self.volatilities[asset] = self.returns[asset].rolling(window=self.params.lookback).std()

    def next(self):
        # 計算權重（簡化版：1 / 波動率）
        total_inverse_vol = 0

        for asset in self.returns:
            asset_vol = self.volatilities[asset][-1]
            if asset_vol > 0:
                self.weights[asset] = 1 / asset_vol
                total_inverse_vol += self.weights[asset]
            else:
                self.weights[asset] = 0

        # 正規化權重
        for asset in self.weights:
            self.weights[asset] /= total_inverse_vol

        # 執行調整
        for asset in self.returns:
            target_size = int(self.broker.getcash() * self.weights[asset])
            current_size = self.getposition(self.data[asset]).size

            # 如果目標大小與當前不同，調整
            if abs(target_size - current_size) > 10:
                if target_size > current_size:
                    self.buy(data=self.data[asset], size=target_size - current_size)
                else:
                    self.sell(data=self.data[asset], size=current_size - target_size)

        # 記錄權重
        self.log(f'Weights: QQQ={self.weights["QQQ"]:.2f}, GLD={self.weights["GLD"]:.2f}, UUP={self.weights["UUP"]:.2f}, TLT={self.weights["TLT"]:.2f}')
```

---

## 壓力測試範例

### 2008 危機模擬

```python
def run_stress_test():
    cerebro = bt.Cerebro()

    # 載入 QQQ 數據
    data = bt.feeds.YahooFinanceData(
        dataname='QQQ',
        fromdate=pd.to_datetime('2000-01-01'),
        todate=pd.to_datetime('2010-01-01')
    )
    cerebro.adddata(data)

    # 加入策略
    cerebro.addstrategy(MomentumStrategy)

    # 設定初始資本
    cerebro.broker.setcash(100000.0)

    # 執行回測
    print('2008 危機回測開始')
    cerebro.run()
    print('最終資本: %.2f' % cerebro.broker.getvalue())

    # 繪製結果
    cerebro.plot()
```

---

## 使用 yfinance 載入多個資產

```python
class MultiAssetLoader(bt.feeds.PandasData):
    params = (
        ('datetime', None),
        ('open', 'Open'),
        ('high', 'High'),
        ('low', 'Low'),
        ('close', 'Close'),
        ('volume', 'Volume'),
    )

def load_multi_asset():
    # 載入所有資產
    symbols = ['QQQ', 'GLD', 'UUP', 'TLT']
    dataframes = {}

    for symbol in symbols:
        # 從 Yahoo Finance 載入
        df = yf.download(symbol, start='2020-01-01', end='2024-01-01', progress=False)
        df.columns = df.columns.str.lower()  # 統一列名為小寫
        dataframes[symbol] = df

    # 合併數據
    merged_data = pd.DataFrame()

    for symbol in symbols:
        merged_data = pd.concat([merged_data, dataframes[symbol]], axis=1)

    # 創建 Backtrader 數據
    class MultiAssetData(bt.feeds.PandasData):
        params = {
            ('datetime', None),
            ('open', 'open'),
            ('high', 'high'),
            ('low', 'low'),
            ('close', 'close'),
            ('volume', 'volume'),
        }

    data = MultiAssetData(dataname=merged_data)

    return data, merged_data


# 使用範例
data, df = load_multi_asset()
cerebro.adddata(data)

# 加入策略
cerebro.addstrategy(MultiAssetMomentumStrategy)

# 執行回測
cerebro.broker.setcash(100000.0)
cerebro.broker.setcommission(commission=0.001)
cerebro.run()
cerebro.plot()
```

---

## 完整回測範例（整合所有組件）

```python
import backtrader as bt
import yfinance as yf
import pandas as pd

class CompleteStrategy(bt.Strategy):
    params = (
        ('ma_fast', 10),
        ('ma_mid', 60),
        ('ma_slow', 200),
        ('position_size', 0.1),
        ('target_vol', 0.15),
        ('lookback', 60),
    )

    def __init__(self):
        # 動能指標
        self.ma_fast = bt.indicators.SMA(self.data.close, period=self.params.ma_fast)
        self.ma_mid = bt.indicators.SMA(self.data.close, period=self.params.ma_mid)
        self.ma_slow = bt.indicators.SMA(self.data.close, period=self.params.ma_slow)

        # 波動率指標
        self.returns = bt.indicators.ROC(self.data.close, period=1)
        self.volatility = self.returns.rolling(window=self.params.lookback).std()

        # 極端事件指標
        self.ema200 = bt.indicators.EMA(self.data.close, period=200)

    def next(self):
        # 1. 檢查極端事件
        if self.data.close < self.ema200:
            # 降低整體曝險 50%
            if self.position:
                self.sell(size=self.position.size * 0.5)

        # 2. 計算動態槓桿
        current_vol = self.volatility[-1]
        leverage = self.params.target_vol / current_vol
        leverage = max(0.7, min(1.2, leverage))

        # 3. 決策
        if not self.position:
            # 做多條件
            if self.ma_fast > self.ma_mid > self.ma_slow:
                size = int(self.broker.getcash() * self.params.position_size * leverage)
                self.buy(size=size)
        else:
            # 平倉條件
            if self.ma_fast < self.ma_mid < self.ma_slow:
                self.sell(size=self.position.size)

    def log(self, txt):
        dt = self.datas[0].datetime.date(0)
        print(f'{dt}, {txt}')


def run_backtest(symbol='QQQ'):
    cerebro = bt.Cerebro()

    # 載入數據
    data = bt.feeds.YahooFinanceData(
        dataname=symbol,
        fromdate=pd.to_datetime('2020-01-01'),
        todate=pd.to_datetime('2024-01-01')
    )
    cerebro.adddata(data)

    # 加入策略
    cerebro.addstrategy(CompleteStrategy)

    # 設定參數
    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.001)

    # 執行回測
    print(f'初始資本: ${cerebro.broker.getvalue():,.2f}')
    cerebro.run()
    print(f'最終資本: ${cerebro.broker.getvalue():,.2f}')

    # 繪製結果
    cerebro.plot()


if __name__ == '__main__':
    run_backtest('QQQ')
```

---

## 執行步驟

1. **安裝 Backtrader**
```bash
pip install backtrader
```

2. **安裝 yfinance**
```bash
pip install yfinance pandas
```

3. **執行回測**
```bash
python backtrader_example.py
```

4. **查看結果**
- 瀏覽器會自動打開，顯示回測圖表
- Console 會顯示初始資本和最終資本

---

## 常用指標

```python
# 移動平均線
SMA = bt.indicators.SMA(close, period=10)

# 指標交叉
cross_over = bt.indicators.CrossOver(fast, slow)

# ROC（變化率）
roc = bt.indicators.ROC(close, period=1)

# ATR（真實波動範圍）
atr = bt.indicators.ATR(period=14)

# 波動率
volatility = returns.rolling(60).std()

# 相關係數
correlation = returns.rolling(60).corr(other_returns)
```

---

## 常用設置

```python
# 初始資本
cerebro.broker.setcash(100000.0)

# 交易成本
cerebro.broker.setcommission(commission=0.001)  # 0.1%

# 滑點
cerebro.broker.set_slippage_perc(percents=0.001)  # 0.1% 滑點

# 日期範圍
fromdate = pd.to_datetime('2020-01-01')
todate = pd.to_datetime('2024-01-01')

# 交易手續費
cerebro.broker.setcheckmargin(0.5)  # 50% 保證金
```

---

## 總結

**Backtrader 的優勢**：
- ✅ 簡單易用
- ✅ 學習成本低
- ✅ 足夠驗證策略
- ✅ 豐富的指標和策略模板

**我們的實作路徑**：
1. 使用 Backtrader 快速驗證基礎策略
2. 逐步加入 ERC、動態槓桿等進階功能
3. 進行壓力測試
4. 最終生成完整報告

**下一步**：
- 安裝 Backtrader
- 執行第一個回測範例
- 驗證策略概念
