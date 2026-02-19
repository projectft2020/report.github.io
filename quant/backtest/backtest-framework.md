# 回測框架建置

**分類日期：** 2026-02-17
**目標：** 建立可重複使用、可擴展的回測框架

---

## 架構設計

### 模組結構

```
backtest-framework/
├── core/
│   ├── engine.py           # 回測引擎
│   ├── strategy.py         # 策略基類
│   ├── portfolio.py        # 投組管理
│   └── risk_manager.py     # 風險管理
├── factors/
│   ├── loader.py           # 因子載入
│   ├── calculator.py       # 因子計算
│   └── validator.py        # 因子驗證
├── backtests/
│   ├── basic_backtest.py   # 基礎回測範例
│   └── multi_factor.py     # 多因子回測範例
├── evaluation/
│   ├── metrics.py          # 績效指標
│   ├── stats.py            # 統計檢驗
│   └── visualization.py    # 視覺化
└── data/
    ├── loader.py           # 資料載入
    ├── preprocessing.py    # 資料預處理
    └── sources/            # 資料來源
```

---

## 核心模組

### 1. 回測引擎 (Engine)

**功能**：
- 時間序列遍歷
- 交易執行
- 仓位管理
- 績效計算

**關鍵方法**：
```python
class BacktestEngine:
    def __init__(self, data, initial_capital):
        self.data = data
        self.initial_capital = initial_capital
        self.positions = {}
        self.equity_curve = []

    def run(self, strategy):
        """執行回測"""
        for date in self.data.dates:
            self._process_day(date, strategy)

    def _process_day(self, date, strategy):
        """處理每一天"""
        # 1. 檢查是否開盤
        if not self.data.is_trading_day(date):
            return

        # 2. 策略決策
        signals = strategy.get_signals(date)

        # 3. 執行交易
        self._execute_trades(date, signals)

        # 4. 更新倉位
        self._update_positions(date)

        # 5. 記錄績效
        self._record_performance(date)

    def _execute_trades(self, date, signals):
        """執行交易"""
        # 實作交易執行邏輯
        pass

    def get_equity_curve(self):
        """獲取權益曲線"""
        return pd.Series(self.equity_curve)
```

### 2. 策略基類 (Strategy)

**功能**：
- 提供統一的策略接口
- 狀態管理
- 風險限制

**關鍵方法**：
```python
class Strategy:
    def __init__(self, engine):
        self.engine = engine
        self.name = "Base Strategy"

    def get_signals(self, date):
        """獲取信號（平倉/開倉）"""
        raise NotImplementedError

    def get_position_size(self, date, signal):
        """獲取倉位大小"""
        return 0.1  # 預設 10% 資金

    def on_position_change(self, date, position):
        """倉位變化時的回調"""
        pass
```

### 3. 投組管理 (Portfolio)

**功能**：
- 資金分配
- 風險管理
- 倉位監控

**關鍵方法**：
```python
class Portfolio:
    def __init__(self, initial_capital, risk_per_trade=0.1):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions = {}
        self.risk_per_trade = risk_per_trade
        self.max_drawdown = 0

    def allocate(self, signals):
        """資金分配"""
        pass

    def check_risk(self):
        """檢查風險"""
        pass
```

### 4. 績效評估 (Evaluation)

**功能**：
- Returns 計算
- 風險指標
- 統計檢驗

**關鍵指標**：
```python
class Metrics:
    @staticmethod
    def calculate_returns(equity_curve):
        """計算收益率"""
        return equity_curve.pct_change()

    @staticmethod
    def calculate_volatility(returns, period=252):
        """計算波動率"""
        return returns.rolling(period).std() * np.sqrt(period)

    @staticmethod
    def calculate_sharpe(returns, risk_free_rate=0.02):
        """計算 Sharpe Ratio"""
        excess_returns = returns - risk_free_rate / 252
        return excess_returns.mean() / excess_returns.std() * np.sqrt(252)

    @staticmethod
    def calculate_max_drawdown(equity_curve):
        """計算最大回撤"""
        cummax = equity_curve.expanding().max()
        drawdown = (equity_curve - cummax) / cummax
        return drawdown.min()
```

---

## 多因子回測範例

### 因子組合策略

```python
class MultiFactorStrategy(Strategy):
    def __init__(self, engine, factors, weights=None):
        super().__init__(engine)
        self.factors = factors
        self.weights = weights if weights else [1.0] * len(factors)

    def get_signals(self, date):
        """根據因子計算信號"""
        # 1. 獲取所有股票
        stocks = self.engine.data.get_stocks(date)

        # 2. 計算因子值
        factor_values = {}
        for factor in self.factors:
            factor_values[factor] = factor.calculate(date)

        # 3. 計算綜合因子值
        composite = sum(
            factor_values[f] * w
            for f, w in zip(self.factors, self.weights)
        )

        # 4. 選擇前 N% 的股票
        top_n = int(len(stocks) * 0.2)
        selected = composite.nlargest(top_n)

        # 5. 返回信號
        return {
            'buy': selected.index.tolist(),
            'sell': [s for s in stocks if s not in selected]
        }
```

---

## ✅ 已完成功能（2026-02-19）

### 階段 1：基礎框架 - 完成 ✅
- [x] 建置回測引擎
- [x] 實作策略基類
- [x] 建立基本績效指標
- [x] 數據收集完成（QQQ+GLD+UUP+TLT, 2010-2025）
- [x] 基礎動能策略實作（10/60/200 MA）
- [x] 回測執行完成

### 階段 2：進階功能 - 進行中 🚀
- [ ] 因子載入器
- [ ] 因子計算引擎
- [ ] 交易成本模擬
- [ ] 滑點模擬
- [ ] 風險限制
- [ ] 波動目標化
- [ ] ERC（等風險組合）

### 階段 3：高級功能 - 待開始
- [ ] 多因子策略
- [ ] 統計顯著性測試
- [ ] Monte Carlo 模擬
- [ ] 壓力測試
- [ ] 實盤接口

---

## 📊 已完成回測

### 基礎動能策略（10/60/200 MA）
- **數據**：QQQ, GLD, UUP, TLT (2010-2025)
- **參數**：10MA > 60MA > 200MA 觸發信號
- **結果**：生成詳細儀表板與分析報告
- **輸出路徑**：/Users/charlie/.openclaw/workspace/quant/research/

---

## 📚 已有文檔

### 量化研究文檔
- [cross_asset_complete_plan.md](./cross_asset_complete_plan.md) - 跨資產動能策略完整計畫
- [matrix_system_integration.md](./matrix_system_integration.md) - Matrix 系統整合指南
- [momentum_strategy_foundation.md](./momentum_strategy_foundation.md) - 動能策略基礎
- [research_topics.md](./research_topics.md) - 研究主題列表
- [advanced-topics.md](./advanced-topics.md) - 進階主題
- [tools-guide.md](./tools-guide.md) - 工具使用指南

### 回測相關
- [backtest-framework.md](./backtest-framework.md) - 回測框架（本文件）
- [data_collection_preparation.md](./data_collection_preparation.md) - 數據收集準備

### 工作與日誌
- [todo.md](./todo.md) - 待辦事項（12 週計畫）
- 2026-02-19.md - 今日工作日誌
- [../../MEMORY.md](./../../MEMORY.md) - 長期記憶

---

## 🎯 下一步行動

### 高優先級
1. **進階回測** - 加入波動目標化
2. **策略優化** - 參數調整與測試
3. **交易成本** - 考慮實際交易成本

### 中優先級
4. **ERC 整合** - 等風險組合
5. **因子分析** - 深入研究動能因子
6. **數據擴展** - 更多資產類別

### 低優先級
7. **實盤準備** - 實盤交易準備
8. **報告生成** - 自動化報告
9. **Dashboard 整合** - 整合到 Matrix Dashboard

---

## 參考資源

### Python 函式庫
- [VectorBT](https://vectorbt.dev/) - 向量化回測 ✅
- [Backtrader](https://www.backtrader.com/) - 回測框架
- [Zipline](https://www.zipline.io/) - 金融回測
- [QuantLib](https://www.quantlib.org/) - 金融函式庫

### 資料來源
- [Yahoo Finance API](https://finance.yahoo.com/) - yfinance ✅
- [Alpha Vantage](https://www.alphavantage.co/) - 數據源
- [Polygon.io](https://polygon.io/) - 實時數據

### 論文資源
- [Spatio-Temporal Momentum (2023)](https://arxiv.org/abs/2302.10175) - 時間序列+截面動能統一
- [James, H. S., & Markowitz, H. M. (2019)](https://www.nber.org/papers/w27307) - 現代投資組合理論
- [Asness, C., Moskowitz, T., Pedersen, L., & Frazzini, M. (2013)](https://www.ssrn.com/abstract=2194002) - 趨勢與均值回歸

---

**最後更新：** 2026-02-19
**維護者：** Charlie
**進度：** 12 週計畫 - 第 1-2 週完成 ✅
