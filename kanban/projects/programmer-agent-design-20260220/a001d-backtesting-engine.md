# Dashboard 回測引擎分析

**Task ID:** a001d
**Agent:** Charlie Analyst
**Status:** completed
**Timestamp:** 2026-02-20T23:38:00+08:00

## Executive Summary

本分析深入研究了 Dashboard 回測引擎的架構設計，涵蓋 Backtrader 和 VectorBT 雙引擎集成方案、完整的回測數據流路徑以及性能優化策略。分析表明，採用統一策略引擎架構可以靈活切換不同的回測後端，同時通過多層緩存和向量化運算顯著提升性能。關鍵建議是建立清晰的抽象層以支持策略可移植性，並實現異步處理機制來提升系統吞吐量。

---

## 架構概述

### 回測引擎架構圖

```
┌─────────────────────────────────────────────────────────────────┐
│                      Dashboard Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ API Gateway  │  │   Web UI     │  │ WebSocket    │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼─────────────────┼─────────────────┼──────────────────┘
          │                 │                 │
          ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Unified Strategy Engine                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Strategy Abstraction Layer                  │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │   │
│  │  │ Strategy    │  │ Signal      │  │ Risk        │     │   │
│  │  │ Interface   │  │ Generator   │  │ Manager     │     │   │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘     │   │
│  └─────────┼─────────────────┼─────────────────┼────────────┘   │
│            │                 │                 │                 │
│  ┌─────────┴─────────────────┴─────────────────┴─────────────┐   │
│  │              Execution Engine Interface                   │   │
│  └───────────────────────┬───────────────────────────────────┘   │
└──────────────────────────┼───────────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Backtrader     │ │   VectorBT      │ │  Future:        │
│  Engine         │ │   Engine        │ │  Custom Engine  │
└────────┬────────┘ └────────┬────────┘ └─────────────────┘
         │                   │
         ▼                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Data Access Layer                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ Market Data │  │ Cache Layer │  │ DB Adapter  │             │
│  │ Provider    │  │ (Redis)     │  │ (PostgreSQL)│             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
└─────────┼─────────────────┼─────────────────┼────────────────────┘
          │                 │                 │
          ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Storage Layer                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │            Time Series Database (TimescaleDB)          │    │
│  │  - OHLCV Data                                          │    │
│  │  - Indicator Values                                    │    │
│  │  - Backtest Results                                    │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Backtrader 集成方式

### 核心組件

#### 1. 策略適配器 (Strategy Adapter)

```python
# backend/backtesting/backtrader_adapter.py
class BacktraderStrategyAdapter(bt.Strategy):
    """
    適配器模式：將統一策略接口轉換為 Backtrader 策略
    
    職責：
    - 實現 bt.Strategy 接口
    - 接收統一策略定義並映射到 Backtrader 方法
    - 處理訂單管理和倉位追蹤
    """
    
    params = (
        ('strategy_config', None),  # 統一策略配置
        ('risk_params', None),      # 風控參數
    )
    
    def __init__(self):
        # 初始化策略組件
        self.signal_generator = SignalGenerator(self.p.strategy_config)
        self.risk_manager = RiskManager(self.p.risk_params)
        self.position_tracker = PositionTracker()
        
        # 指標初始化
        self._init_indicators()
    
    def _init_indicators(self):
        """根據策略配置初始化技術指標"""
        for ind_config in self.p.strategy_config.get('indicators', []):
            ind_type = ind_config['type']
            ind_params = ind_config.get('params', {})
            
            if ind_type == 'sma':
                setattr(self, ind_config['name'], 
                       bt.indicators.SMA(self.data, period=ind_params.get('period', 20)))
            elif ind_type == 'rsi':
                setattr(self, ind_config['name'],
                       bt.indicators.RSI(self.data, period=ind_params.get('period', 14)))
            # ... 更多指標
    
    def next(self):
        """每根 K 線執行"""
        # 生成交易信號
        signals = self.signal_generator.generate(self._get_current_context())
        
        # 應用風控
        filtered_signals = self.risk_manager.filter(signals, self.position_tracker)
        
        # 執行訂單
        self._execute_orders(filtered_signals)
    
    def _get_current_context(self):
        """構建當前市場上下文"""
        return {
            'datetime': self.data.datetime.datetime(0),
            'open': self.data.open[0],
            'high': self.data.high[0],
            'low': self.data.low[0],
            'close': self.data.close[0],
            'volume': self.data.volume[0],
            'indicators': {
                name: getattr(self, name)[0]
                for name in self.p.strategy_config.get('indicators', [])
            },
            'position': self.position_tracker.get_current_position(),
        }
```

#### 2. 數據饋送器 (Data Feed)

```python
# backend/backtesting/backtrader_datafeed.py
class DatabaseDataFeed(bt.DataBase):
    """
    從數據庫加載歷史數據並轉換為 Backtrader 格式
    
    優化策略：
    - 批量加載減少查詢次數
    - 使用生成器實現懶加載
    - 支持預讀取緩存
    """
    
    params = (
        ('db_session', None),
        ('symbol', None),
        ('start_date', None),
        ('end_date', None),
        ('timeframe', bt.TimeFrame.Days),
        ('preload', True),
        ('lookback', 100),  # 指標回看窗口
    )
    
    def start(self):
        """初始化數據流"""
        if self.p.preload:
            self._preload_data()
        else:
            self._setup_generator()
    
    def _preload_data(self):
        """預加載所有數據到內存"""
        query = """
            SELECT datetime, open, high, low, close, volume
            FROM market_data
            WHERE symbol = %s
              AND datetime >= %s
              AND datetime <= %s
            ORDER BY datetime ASC
        """
        
        results = self.p.db_session.execute(
            query,
            (self.p.symbol, self.p.start_date, self.p.end_date)
        ).fetchall()
        
        self._data = self._convert_to_arrays(results)
        self._load_data_into_cerebro()
    
    def _setup_generator(self):
        """設置生成器實現懶加載"""
        self._generator = self._data_generator()
        self._advance()
    
    def _data_generator(self):
        """數據生成器"""
        batch_size = 1000
        offset = 0
        
        while True:
            query = """
                SELECT datetime, open, high, low, close, volume
                FROM market_data
                WHERE symbol = %s
                  AND datetime >= %s
                  AND datetime <= %s
                ORDER BY datetime ASC
                LIMIT %s OFFSET %s
            """
            
            results = self.p.db_session.execute(
                query,
                (self.p.symbol, self.p.start_date, self.p.end_date,
                 batch_size, offset)
            ).fetchall()
            
            if not results:
                break
            
            for row in results:
                yield row
            
            offset += batch_size
```

#### 3. 回測引擎 (Backtesting Engine)

```python
# backend/backtesting/backtrader_engine.py
class BacktraderEngine:
    """
    Backtrader 回測引擎封裝
    
    職責：
    - 配置 Cerebro 實例
    - 管理數據源和策略
    - 執行回測並收集結果
    - 結果序列化和存儲
    """
    
    def __init__(self, config: dict, db_session: Session):
        self.config = config
        self.db_session = db_session
        self.cerebro = bt.Cerebro()
        self._setup_cerebro()
    
    def _setup_cerebro(self):
        """配置 Cerebro 實例"""
        # 設置初始資金
        self.cerebro.broker.setcash(self.config.get('initial_capital', 100000))
        
        # 設置交易手續費
        self.cerebro.broker.setcommission(
            commission=self.config.get('commission', 0.001),
            leverage=self.config.get('leverage', 1.0)
        )
        
        # 添加分析器
        self._add_analyzers()
        
        # 設置滑點
        self.cerebro.broker.set_slippage_perc(
            perc=self.config.get('slippage', 0.0001)
        )
    
    def _add_analyzers(self):
        """添加回測分析器"""
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, 
                                 _name='sharpe',
                                 timeframe=bt.TimeFrame.Days)
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, 
                                 _name='drawdown')
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, 
                                 _name='trades')
        self.cerebro.addanalyzer(bt.analyzers.Returns, 
                                 _name='returns')
        self.cerebro.addanalyzer(bt.analyzers.TimeReturn, 
                                 _name='timereturn')
    
    def add_strategy(self, strategy_config: dict, risk_params: dict = None):
        """添加策略"""
        self.cerebro.addstrategy(
            BacktraderStrategyAdapter,
            strategy_config=strategy_config,
            risk_params=risk_params or {}
        )
    
    def add_data(self, symbol: str, start_date: datetime, 
                 end_date: datetime):
        """添加數據源"""
        data = DatabaseDataFeed(
            db_session=self.db_session,
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            preload=True  # 預加載提升性能
        )
        self.cerebro.adddata(data)
    
    def run(self) -> dict:
        """執行回測"""
        results = self.cerebro.run()
        
        # 提取結果
        backtest_result = self._extract_results(results[0])
        
        # 保存到數據庫
        self._save_results(backtest_result)
        
        return backtest_result
    
    def _extract_results(self, strategy) -> dict:
        """提取回測結果"""
        analyzers = strategy.analyzers
        
        return {
            'final_value': self.cerebro.broker.getvalue(),
            'initial_capital': self.config.get('initial_capital'),
            'return': (self.cerebro.broker.getvalue() / 
                      self.config.get('initial_capital', 1) - 1),
            'sharpe_ratio': analyzers.sharpe.get_analysis().get('sharperatio'),
            'max_drawdown': analyzers.drawdown.get_analysis().get('max', {}).get('drawdown'),
            'total_trades': analyzers.trades.get_analysis().get('total', {}).get('total'),
            'win_rate': self._calculate_win_rate(analyzers.trades.get_analysis()),
            'daily_returns': analyzers.timereturn.get_analysis(),
            'cagr': self._calculate_cagr(analyzers.returns.get_analysis()),
        }
```

### 性能優化要點

1. **數據預加載**：使用 `preload=True` 避免重複查詢
2. **批量查詢**：分批次從數據庫加載數據
3. **指標預計算**：將頻繁使用的指標緩存
4. **並行回測**：支持多進程並行執行
5. **內存優化**：使用 NumPy 數組而非列表存儲數據

---

## VectorBT 集成方式

### 核心組件

#### 1. 向量化策略執行器

```python
# backend/backtesting/vectorbt_executor.py
class VectorBTExecutor:
    """
    VectorBT 向量化回測執行器
    
    優勢：
    - 全向量化運算，極快速度
    - 支持批量策略回測
    - 自動處理數據對齊
    - 內置豐富的分析工具
    
    適用場景：
    - 參數掃描和優化
    - 大規模歷史回測
    - 指標計算密集型任務
    """
    
    def __init__(self, config: dict, db_session: Session):
        self.config = config
        self.db_session = db_session
        self._load_data()
    
    def _load_data(self):
        """
        加載歷史數據為 DataFrame
        
        優化：
        - 使用 read_sql 直接加載到 DataFrame
        - 設置 datetime 索引加速查詢
        - 使用適當的數據類型減少內存
        """
        query = """
            SELECT symbol, datetime, open, high, low, close, volume
            FROM market_data
            WHERE symbol = ANY(%s)
              AND datetime >= %s
              AND datetime <= %s
            ORDER BY symbol, datetime
        """
        
        df = pd.read_sql(
            query,
            con=self.db_session.bind,
            params=(
                self.config['symbols'],
                self.config['start_date'],
                self.config['end_date']
            )
        )
        
        # 轉換為 VectorBT 格式
        self.data = self._pivot_to_vbt_format(df)
    
    def _pivot_to_vbt_format(self, df: pd.DataFrame) -> vbt.Data:
        """
        將數據轉換為 VectorBT 格式
        
        格式：
        - MultiIndex columns: (symbol, field)
        - DatetimeIndex
        """
        df_pivoted = df.pivot_table(
            index='datetime',
            columns='symbol',
            values=['open', 'high', 'low', 'close', 'volume'],
            aggfunc='first'
        )
        
        # 合併多級列
        df_pivoted.columns = df_pivoted.columns.swaplevel(0, 1)
        df_pivoted = df_pivoted.sort_index(axis=1)
        
        return vbt.Data.from_data(df_pivoted)
    
    def run_backtest(self, strategy_func: Callable, **params) -> dict:
        """
        執行向量化回測
        
        Args:
            strategy_func: 接收數據返回交易信號的函數
            params: 策略參數，支持參數網格
        """
        # 生成信號
        signals = strategy_func(self.data, **params)
        
        # 執行回測
        portfolio = vbt.Portfolio.from_signals(
            close=self.data['close'],
            entries=signals['entry'],
            exits=signals['exit'],
            **self._get_portfolio_config()
        )
        
        # 計算指標
        metrics = self._calculate_metrics(portfolio)
        
        return {
            'portfolio': portfolio,
            'metrics': metrics,
            'signals': signals,
        }
    
    def run_param_scan(self, strategy_func: Callable, 
                      param_grid: dict) -> pd.DataFrame:
        """
        參數掃描
        
        利用 VectorBT 的向量化能力，同時測試多組參數
        
        Returns:
            包含所有參數組合及其指標的 DataFrame
        """
        # 構建參數網格
        from itertools import product
        
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        all_params = list(product(*param_values))
        
        results = []
        
        for param_combo in all_params:
            params = dict(zip(param_names, param_combo))
            
            try:
                result = self.run_backtest(strategy_func, **params)
                
                row = params.copy()
                row.update(result['metrics'])
                results.append(row)
                
            except Exception as e:
                # 記錄失敗的參數組合
                row = params.copy()
                row['error'] = str(e)
                results.append(row)
        
        return pd.DataFrame(results)
    
    def _get_portfolio_config(self) -> dict:
        """獲取投資組合配置"""
        return {
            'init_cash': self.config.get('initial_capital', 100000),
            'fees': self.config.get('commission', 0.001),
            'slippage': self.config.get('slippage', 0.0001),
            'freq': self.config.get('frequency', '1D'),
        }
    
    def _calculate_metrics(self, portfolio: vbt.Portfolio) -> dict:
        """計算回測指標"""
        return {
            'total_return': portfolio.total_return(),
            'sharpe_ratio': portfolio.sharpe_ratio(),
            'sortino_ratio': portfolio.sortino_ratio(),
            'max_drawdown': portfolio.max_drawdown(),
            'win_rate': portfolio.trades.win_rate(),
            'avg_return': portfolio.returns.mean(),
            'volatility': portfolio.returns.std(),
            'calmar_ratio': portfolio.calmar_ratio(),
            'total_trades': len(portfolio.trades.records_readable),
        }
```

#### 2. 通用策略庫

```python
# backend/backtesting/vectorbt_strategies.py
class VectorBTStrategies:
    """
    VectorBT 通用策略實現
    
    特點：
    - 純 NumPy/NumExpr 實現，高度優化
    - 支持批量操作
    - 易於組合和擴展
    """
    
    @staticmethod
    def sma_crossover(data: vbt.Data, 
                     fast_period: int = 10, 
                     slow_period: int = 30) -> dict:
        """
        SMA 交叉策略
        
        Returns:
            dict 包含 entry 和 exit 信號
        """
        close = data['close']
        
        # 計算 SMA（向量化）
        fast_sma = vbt.MA.run(close, window=fast_period).ma
        slow_sma = vbt.MA.run(close, window=slow_period).ma
        
        # 生成信號（交叉）
        entries = fast_sma.vbt.crossed_above(slow_sma)
        exits = fast_sma.vbt.crossed_below(slow_sma)
        
        return {
            'entry': entries,
            'exit': exits,
            'indicators': {
                'fast_sma': fast_sma,
                'slow_sma': slow_sma,
            }
        }
    
    @staticmethod
    def rsi_strategy(data: vbt.Data,
                     period: int = 14,
                     oversold: int = 30,
                     overbought: int = 70) -> dict:
        """
        RSI 策略
        
        Returns:
            dict 包含信號和指標
        """
        close = data['close']
        
        # 計算 RSI
        rsi = vbt.RSI.run(close, window=period).rsi
        
        # 生成信號
        entries = rsi.vbt.crossed_below(oversold)   # 超賣區買入
        exits = rsi.vbt.crossed_above(overbought)   # 超買區賣出
        
        return {
            'entry': entries,
            'exit': exits,
            'indicators': {
                'rsi': rsi,
            }
        }
    
    @staticmethod
    def bollinger_bands(data: vbt.Data,
                       period: int = 20,
                       std_dev: float = 2.0) -> dict:
        """
        布林帶策略
        
        Returns:
            dict 包含信號和指標
        """
        close = data['close']
        
        # 計算布林帶
        bb = vbt.BBANDS.run(close, window=period, std=std_dev)
        
        # 生成信號
        entries = close.vbt.crossed_below(bb.lower)  # 觸及下軌買入
        exits = close.vbt.crossed_above(bb.upper)      # 觸及上軌賣出
        
        return {
            'entry': entries,
            'exit': exits,
            'indicators': {
                'upper': bb.upper,
                'middle': bb.middle,
                'lower': bb.lower,
            }
        }
    
    @staticmethod
    def multi_factor_strategy(data: vbt.Data,
                             factors: dict) -> dict:
        """
        多因子組合策略
        
        Args:
            factors: 因子配置
                {
                    'sma': {'fast': 10, 'slow': 30},
                    'rsi': {'period': 14, 'oversold': 30},
                    ...
                }
        
        Returns:
            dict 包含組合信號
        """
        signals = []
        
        # 計算各因子信號
        if 'sma' in factors:
            sma_signals = VectorBTStrategies.sma_crossover(
                data, **factors['sma']
            )
            signals.append(sma_signals['entry'])
        
        if 'rsi' in factors:
            rsi_signals = VectorBTStrategies.rsi_strategy(
                data, **factors['rsi']
            )
            signals.append(rsi_signals['entry'])
        
        # 組合信號（邏輯與）
        if signals:
            combined_entry = np.all(signals, axis=0)
            combined_exit = np.any([sma_signals['exit'], rsi_signals['exit']], axis=0)
        else:
            combined_entry = pd.Series(False, index=data.index)
            combined_exit = pd.Series(False, index=data.index)
        
        return {
            'entry': combined_entry,
            'exit': combined_exit,
        }
```

### 性能優化要點

1. **向量化運算**：利用 NumPy/NumExpr 實現批量計算
2. **參數網格掃描**：一次測試數千個參數組合
3. **內存優化**：使用適當的 dtypes (float32 vs float64)
4. **並行計算**：支持多進程參數優化
5. **惰性計算**：按需計算指標，避免不必要的計算

---

## 回測數據流

### 完整數據流圖

```
┌──────────────────────────────────────────────────────────────────┐
│                      1. 數據收集層                                │
└──────────────────────────────────────────────────────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        ▼                         ▼                         ▼
┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
│   Market API      │   │   WebSocket Feed   │   │   File Import     │
│   (Binance, etc.) │   │   (Real-time)      │   │   (CSV, Excel)    │
└─────────┬─────────┘   └─────────┬─────────┘   └─────────┬─────────┘
          │                       │                       │
          └───────────────────────┴───────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                   2. 數據驗證與清洗                               │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  • 時間戳對齊                                                │ │
│  │  • 缺失值處理 (向前填充/插值)                               │ │
│  │  • 異常值檢測 (3σ規則)                                      │ │
│  │  • 數據完整性校驗                                            │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                   3. 數據存儲層                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │               TimescaleDB (PostgreSQL)                     │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  Table: market_data                                   │  │ │
│  │  │    - symbol VARCHAR(20)                               │  │ │
│  │  │    - datetime TIMESTAMPTZ                             │  │ │
│  │  │    - open, high, low, close DECIMAL                   │  │ │
│  │  │    - volume BIGINT                                    │  │ │
│  │  │    - PRIMARY KEY (symbol, datetime)                  │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                   4. 緩存層                                       │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Redis Cache                                               │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  Key Pattern: data:{symbol}:{timeframe}:{date}       │  │ │
│  │  │  TTL: 7 days                                         │  │ │
│  │  │  Format: Protobuf (壓縮)                             │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│   Backtrader Engine      │     │    VectorBT Engine      │
│   Data Feed Loader       │     │    DataFrame Loader     │
└───────────┬─────────────┘     └───────────┬─────────────┘
            │                               │
            ▼                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                   5. 策略執行層                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Signal Generation → Order Management → Position Tracking   │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                   6. 結果計算層                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  • PnL 計算 (逐筆/逐日)                                    │ │
│  │  • 風險指標 (Sharpe, Sortino, DD)                          │ │
│  │  • 交易統計 (勝率, 盈虧比)                                 │ │
│  │  • 繪圖數據生成                                            │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                   7. 結果存儲層                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Table: backtest_results                                   │ │
│  │    - id UUID                                              │ │
│  │    - strategy_id UUID                                      │ │
│  │    - params JSONB                                          │ │
│  │    - start_date, end_date DATE                             │ │
│  │    - total_return DECIMAL                                  │ │
│  │    - sharpe_ratio DECIMAL                                  │ │
│  │    - max_drawdown DECIMAL                                  │ │
│  │    - total_trades INT                                      │ │
│  │    - win_rate DECIMAL                                      │ │
│  │    - created_at TIMESTAMPTZ                                │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Table: trade_records                                      │ │
│  │    - id UUID                                              │ │
│  │    - backtest_id UUID (FK)                                │ │
│  │    - entry_date, exit_date DATE                            │ │
│  │    - entry_price, exit_price DECIMAL                       │ │
│  │    - quantity DECIMAL                                      │ │
│  │    - pnl DECIMAL                                           │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                   8. API 輸出層                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  REST API / GraphQL                                       │ │
│  │  • 獲取回測結果摘要                                        │ │
│  │  • 獲取詳細交易記錄                                        │ │
│  │  • 下載報告 (PDF/CSV)                                      │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

### 數據流詳細說明

#### 階段 1-2: 數據收集與清洗

```python
# backend/data/ingestion/market_data_processor.py
class MarketDataProcessor:
    """
    市場數據處理器
    
    職責：
    - 從多源獲取數據
    - 數據清洗和驗證
    - 統一格式轉換
    """
    
    def process_kline(self, raw_data: dict) -> pd.DataFrame:
        """
        處理 K 線數據
        
        清洗步驟：
        1. 時間戳轉換 (ms -> datetime)
        2. 列名標準化
        3. 缺失值處理
        4. 異常值檢測
        """
        df = pd.DataFrame(raw_data)
        
        # 時間戳轉換
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        # 重命名列
        df = df.rename(columns={
            'o': 'open', 'h': 'high', 'l': 'low', 'c': 'close', 'v': 'volume'
        })
        
        # 數據驗證
        self._validate_ohlc(df)
        
        # 異常值處理
        df = self._handle_outliers(df)
        
        return df[['datetime', 'open', 'high', 'low', 'close', 'volume']]
    
    def _validate_ohlc(self, df: pd.DataFrame):
        """驗證 OHLC 數據有效性"""
        # 檢查 high >= low
        invalid = df[df['high'] < df['low']]
        if not invalid.empty:
            raise ValueError(f"Invalid OHLC data: {len(invalid)} records")
        
        # 檢查 close 在 [low, high] 範圍內
        out_of_range = df[(df['close'] > df['high']) | (df['close'] < df['low'])]
        if not out_of_range.empty:
            raise ValueError(f"Close price out of range: {len(out_of_range)} records")
    
    def _handle_outliers(self, df: pd.DataFrame, std_threshold: float = 3.0):
        """處理異常值（3σ規則）"""
        for col in ['open', 'high', 'low', 'close']:
            mean = df[col].mean()
            std = df[col].std()
            
            lower_bound = mean - std_threshold * std
            upper_bound = mean + std_threshold * std
            
            # 標記異常值
            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
            
            # 使用前一個有效值填充
            df[col] = df[col].mask(outliers[col].index).ffill()
        
        return df
```

#### 階段 3-4: 存儲與緩存

```python
# backend/data/storage/market_data_store.py
class MarketDataStore:
    """
    市場數據存儲
    
    策略：
    - L1: Redis Cache (熱數據，7天)
    - L2: TimescaleDB (持久化)
    """
    
    def __init__(self, db_session: Session, redis_client: redis.Redis):
        self.db_session = db_session
        self.redis = redis_client
    
    def save_data(self, df: pd.DataFrame):
        """保存數據（寫時緩存）"""
        # 保存到數據庫
        self._save_to_db(df)
        
        # 異步更新緩存
        self._update_cache_async(df)
    
    def get_data(self, symbol: str, start_date: datetime, 
                 end_date: datetime) -> pd.DataFrame:
        """
        獲取數據（讀時緩存）
        
        查詢策略：
        1. 先查 Redis
        2. 緩存未命中則查數據庫
        3. 數據庫查詢結果寫入緩存
        """
        # 構建緩存鍵
        cache_key = f"data:{symbol}:{start_date}:{end_date}"
        
        # 嘗試從緩存獲取
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            return cached_data
        
        # 從數據庫查詢
        df = self._query_from_db(symbol, start_date, end_date)
        
        # 寫入緩存
        self._save_to_cache(cache_key, df)
        
        return df
    
    def _get_from_cache(self, key: str) -> Optional[pd.DataFrame]:
        """從 Redis 獲取數據"""
        try:
            data = self.redis.get(key)
            if data is None:
                return None
            
            # 反序列化 (Protocol Buffers)
            return self._deserialize(data)
        except Exception as e:
            logger.warning(f"Cache read failed: {e}")
            return None
    
    def _save_to_cache(self, key: str, df: pd.DataFrame, ttl: int = 604800):
        """保存到 Redis (TTL: 7天)"""
        try:
            # 序列化 (Protocol Buffers)
            serialized = self._serialize(df)
            
            self.redis.setex(key, ttl, serialized)
        except Exception as e:
            logger.warning(f"Cache write failed: {e}")
```

#### 階段 5-6: 策略執行與結果計算

```python
# backend/backtesting/result_analyzer.py
class BacktestResultAnalyzer:
    """
    回測結果分析器
    
    職責：
    - 從引擎原始結果計算指標
    - 生成可視化數據
    - 生成報告
    """
    
    def analyze(self, engine_result: dict) -> dict:
        """
        分析回測結果
        
        計算指標：
        1. 收益指標
        2. 風險指標
        3. 交易統計
        4. 繪圖數據
        """
        metrics = {}
        
        # 收益指標
        metrics.update(self._calculate_returns(engine_result))
        
        # 風險指標
        metrics.update(self._calculate_risk(engine_result))
        
        # 交易統計
        metrics.update(self._calculate_trade_stats(engine_result))
        
        # 繪圖數據
        metrics['plot_data'] = self._generate_plot_data(engine_result)
        
        return metrics
    
    def _calculate_returns(self, result: dict) -> dict:
        """計算收益指標"""
        daily_returns = result['daily_returns']
        
        return {
            'total_return': sum(daily_returns.values()),
            'cagr': self._calculate_cagr(daily_returns),
            'monthly_returns': self._group_returns(daily_returns, 'M'),
            'annual_returns': self._group_returns(daily_returns, 'Y'),
        }
    
    def _calculate_risk(self, result: dict) -> dict:
        """計算風險指標"""
        daily_returns = list(result['daily_returns'].values())
        
        return {
            'volatility': np.std(daily_returns) * np.sqrt(252),
            'var_95': np.percentile(daily_returns, 5),
            'cvar_95': np.mean([r for r in daily_returns if r <= np.percentile(daily_returns, 5)]),
        }
    
    def _generate_plot_data(self, result: dict) -> dict:
        """
        生成繪圖數據
        
        Returns:
            {
                'equity_curve': [(datetime, value), ...],
                'drawdown': [(datetime, value), ...],
                'trades': [{'entry': datetime, 'exit': datetime, ...}, ...]
            }
        """
        return {
            'equity_curve': result['equity_curve'],
            'drawdown': result['drawdown_series'],
            'trades': result['trade_records'],
        }
```

---

## 性能優化策略總結

### 數據層優化

#### 1. 多級緩存架構

```python
# 性能提升：數據加載速度提升 10-100x

class CacheManager:
    """
    多級緩存管理器
    
    L1: Redis (熱數據，< 7 天)
    L2: PostgreSQL TimescaleDB (溫數據，< 1 年)
    L3: S3/本地文件 (冷數據，存檔)
    """
    
    def get_data(self, symbol: str, start: datetime, end: datetime):
        # L1: Redis
        data = self.redis.get(symbol, start, end)
        if data:
            return data
        
        # L2: PostgreSQL
        data = self.pg.get_data(symbol, start, end)
        if data:
            # 回填 L1
            self.redis.set(symbol, start, end, data)
            return data
        
        # L3: S3
        data = self.s3.get_data(symbol, start, end)
        if data:
            # 回填 L1, L2
            self.redis.set(symbol, start, end, data)
            self.pg.insert_data(symbol, data)
            return data
        
        raise DataNotFoundError()
```

#### 2. 數據庫優化

```sql
-- TimescaleDB 分區和壓縮

-- 1. 創建超級表
SELECT create_hypertable('market_data', 'datetime', 
                         chunk_time_interval => INTERVAL '1 day');

-- 2. 壓縮舊數據 (節省 80-90% 存儲)
SELECT add_compression_policy('market_data', 
                             INTERVAL '30 days');

-- 3. 連續聚合 (預計算常用指標)
CREATE MATERIALIZED VIEW daily_ohlc
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 day', datetime) AS day,
    symbol,
    first(open, datetime) AS open,
    max(high) AS high,
    min(low) AS low,
    last(close, datetime) AS close,
    sum(volume) AS volume
FROM market_data
GROUP BY day, symbol;

-- 4. 查詢索引優化
CREATE INDEX idx_market_data_symbol_datetime 
ON market_data (symbol, datetime DESC);
```

### 回測層優化

#### 3. 並行回測

```python
# 性能提升：多參數組合回測速度提升 4-8x (取決於 CPU 核心數)

from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp

class ParallelBacktester:
    """
    並行回測引擎
    
    策略：
    - 獨立回測任務分配到不同進程
    - 結果收集和合併
    - 支持任務優先級和資源限制
    """
    
    def run_batch(self, tasks: List[dict], max_workers: int = None) -> List[dict]:
        """
        批量執行回測
        
        Args:
            tasks: 回測任務列表
            max_workers: 最大並發數，默認為 CPU 核心數
        """
        max_workers = max_workers or mp.cpu_count()
        
        results = []
        
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任務
            future_to_task = {
                executor.submit(self._run_single_backtest, task): task
                for task in tasks
            }
            
            # 收集結果
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Task failed: {task}, Error: {e}")
                    results.append({
                        'task': task,
                        'error': str(e),
                        'status': 'failed'
                    })
        
        return results
    
    @staticmethod
    def _run_single_backtest(task: dict) -> dict:
        """執行單個回測 (進程隔離)"""
        # 初始化引擎
        engine = BacktraderEngine(task['config'], task['db_session'])
        
        # 添加數據和策略
        engine.add_data(**task['data_config'])
        engine.add_strategy(**task['strategy_config'])
        
        # 執行
        return engine.run()
```

#### 4. 向量化優化

```python
# 性能提升：單策略回測速度提升 5-20x

import numba as nb

@nb.jit(nopython=True, parallel=True)
def calculate_sma_cross(prices: np.ndarray, fast: int, slow: int) -> np.ndarray:
    """
    使用 Numba 加速的 SMA 交叉計算
    
    性能提升：相比純 Python 快 10-50x
    """
    n = len(prices)
    signals = np.zeros(n, dtype=np.int8)
    
    for i in range(max(fast, slow), n):
        fast_sma = np.mean(prices[i-fast+1:i+1])
        slow_sma = np.mean(prices[i-slow+1:i+1])
        
        if fast_sma > slow_sma and signals[i-1] <= 0:
            signals[i] = 1  # 買入信號
        elif fast_sma < slow_sma and signals[i-1] >= 0:
            signals[i] = -1  # 賣出信號
    
    return signals

class VectorizedStrategy:
    """
    向量化策略執行器
    
    特點：
    - 避免循環，使用 NumPy/NumExpr
    - 關鍵路徑使用 Numba JIT
    - 批量處理多個標的
    """
    
    def run(self, prices: pd.DataFrame) -> pd.DataFrame:
        """
        執行向量化策略
        
        處理多標的，一次性計算所有信號
        """
        signals = {}
        
        for symbol in prices.columns:
            price_array = prices[symbol].values
            signals[symbol] = calculate_sma_cross(
                price_array, 
                fast=10, 
                slow=30
            )
        
        return pd.DataFrame(signals, index=prices.index)
```

#### 5. 增量回測

```python
# 性能提升：增量更新速度提升 100x+

class IncrementalBacktester:
    """
    增量回測引擎
    
    應用場景：
    - 新數據到達時快速更新結果
    - 減少重複計算
    
    策略：
    - 緩存中間狀態
    - 只計算新增數據
    - 合併結果
    """
    
    def run_incremental(self, previous_result: dict, 
                       new_data: pd.DataFrame) -> dict:
        """
        增量回測
        
        Args:
            previous_result: 上次回測結果（包含快照）
            new_data: 新增數據
        
        Returns:
            合併後的完整結果
        """
        # 1. 從快照恢復狀態
        state = self._restore_state(previous_result['snapshot'])
        
        # 2. 只在新數據上運行回測
        incremental_result = self._run_on_new_data(state, new_data)
        
        # 3. 合併結果
        merged_result = self._merge_results(
            previous_result, 
            incremental_result
        )
        
        return merged_result
    
    def _restore_state(self, snapshot: dict) -> object:
        """恢復策略和引擎狀態"""
        # 從快照恢復倉位、指標值等
        pass
    
    def _run_on_new_data(self, state: object, 
                        new_data: pd.DataFrame) -> dict:
        """在新數據上運行回測"""
        # 只處理新數據
        pass
    
    def _merge_results(self, old: dict, new: dict) -> dict:
        """合併舊結果和新結果"""
        # 拼接交易記錄
        # 重新計算累計指標
        pass
```

### 資源優化

#### 6. 內存優化

```python
# 內存使用：減少 50-80%

import pyarrow as pa
import pyarrow.parquet as pq

class MemoryOptimizedDataLoader:
    """
    內存優化數據加載器
    
    策略：
    - 使用適當的 dtypes (float32 vs float64)
    - 使用 Parquet 格式（列式壓縮）
    - 按需加載（分塊讀取）
    """
    
    def load_data(self, path: str, 
                  columns: List[str] = None,
                  dtype_optimization: bool = True) -> pd.DataFrame:
        """
        加載數據並優化內存使用
        
        優化：
        1. 選擇必要的列
        2. 使用適當的數據類型
        3. 分塊讀取大文件
        """
        # 使用 Parquet（壓縮率高）
        table = pq.read_table(path, columns=columns)
        
        if dtype_optimization:
            # 優化數據類型
            table = self._optimize_dtypes(table)
        
        return table.to_pandas()
    
    def _optimize_dtypes(self, table: pa.Table) -> pa.Table:
        """優化數據類型"""
        optimized_fields = []
        
        for field in table.schema:
            if pa.types.is_float64(field.type):
                # 使用 float32 節省內存（精度對大多數場景足夠）
                optimized_fields.append(
                    pa.field(field.name, pa.float32())
                )
            elif pa.types.is_int64(field.type):
                # 根據數值範圍選擇更小的整型
                min_val, max_val = table.column(field.name).to_pandas().minmax()
                if min_val >= 0 and max_val < 256:
                    optimized_fields.append(
                        pa.field(field.name, pa.uint8())
                    )
                elif min_val >= 0 and max_val < 65536:
                    optimized_fields.append(
                        pa.field(field.name, pa.uint16())
                    )
                else:
                    optimized_fields.append(field)
            else:
                optimized_fields.append(field)
        
        return table.cast(pa.schema(optimized_fields))
```

#### 7. 數據壓縮

```python
# 存儲空間：減少 70-90%

import gzip
import pickle

class CompressedStorage:
    """
    壓縮存儲
    
    應用場景：
    - 回測結果存檔
    - 快照存儲
    - 報告緩存
    """
    
    def save(self, data: dict, path: str):
        """
        壓縮保存數據
        
        格式：gzip + pickle
        """
        # 序列化
        serialized = pickle.dumps(data)
        
        # 壓縮
        compressed = gzip.compress(serialized)
        
        # 保存
        with open(path, 'wb') as f:
            f.write(compressed)
        
        logger.info(f"Saved {len(serialized)} bytes, compressed to {len(compressed)} bytes "
                   f"({(1-len(compressed)/len(serialized))*100:.1f}% reduction)")
    
    def load(self, path: str) -> dict:
        """
        加載壓縮數據
        """
        with open(path, 'rb') as f:
            compressed = f.read()
        
        # 解壓
        serialized = gzip.decompress(compressed)
        
        # 反序列化
        return pickle.loads(serialized)
```

### 性能監控

#### 8. 性能分析工具

```python
# 性能可視化和瓶頸識別

import cProfile
import pstats
from io import StringIO

class PerformanceProfiler:
    """
    性能分析器
    
    功能：
    - 識別性能瓶頸
    - 追蹤資源使用
    - 生成報告
    """
    
    def profile_backtest(self, backtest_func: Callable, 
                        **kwargs) -> dict:
        """
        分析回測性能
        
        Returns:
            {
                'result': 回測結果,
                'profiling': 性能分析報告,
                'timing': 時間統計
            }
        """
        # 啟動性能分析
        profiler = cProfile.Profile()
        profiler.enable()
        
        # 執行回測
        import time
        start_time = time.time()
        result = backtest_func(**kwargs)
        elapsed = time.time() - start_time
        
        # 停止性能分析
        profiler.disable()
        
        # 生成報告
        stats = pstats.Stats(profiler)
        
        # 格式化輸出
        output = StringIO()
        stats.stream = output
        stats.sort_stats('cumulative')
        stats.print_stats(20)  # 前 20 個最耗時的函數
        
        return {
            'result': result,
            'profiling': output.getvalue(),
            'timing': {
                'total_time': elapsed,
                'total_time_human': f"{elapsed:.2f}s",
            }
        }
```

### 性能優化總結表

| 優化策略             | 性能提升    | 實施複雜度 | 優先級 |
|---------------------|------------|-----------|--------|
| Redis 緩存           | 10-100x    | 低        | 高     |
| 向量化運算           | 5-20x      | 中        | 高     |
| 並行回測             | 4-8x       | 中        | 高     |
| Numba JIT            | 10-50x     | 低        | 中     |
| TimescaleDB 壓縮     | 5x (存儲)   | 低        | 中     |
| 增量回測             | 100x+      | 高        | 低     |
| 內存優化             | 50-80%     | 低        | 中     |
| 數據壓縮             | 70-90%     | 低        | 低     |

---

## 關鍵接口和類別定義

### 統一策略引擎接口

```python
# backend/strategy_engine/interfaces.py

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class EngineType(Enum):
    """回測引擎類型"""
    BACKTRADER = "backtrader"
    VECTORBT = "vectorbt"
    CUSTOM = "custom"


@dataclass
class MarketContext:
    """
    市場上下文
    
    包含當前市場狀態信息，用於策略決策
    """
    datetime: datetime
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    indicators: Dict[str, float]
    position: Optional[float] = None
    balance: Optional[float] = None


@dataclass
class Signal:
    """
    交易信號
    
    direction: 1 (買入), -1 (賣出), 0 (持有)
    strength: 0-1 信號強度
    """
    direction: int
    strength: float
    timestamp: datetime
    symbol: str
    reason: Optional[str] = None


@dataclass
class BacktestConfig:
    """
    回測配置
    """
    engine_type: EngineType
    symbol: str
    start_date: datetime
    end_date: datetime
    initial_capital: float = 100000
    commission: float = 0.001
    slippage: float = 0.0001
    leverage: float = 1.0
    timeframe: str = "1D"


@dataclass
class BacktestResult:
    """
    回測結果
    """
    config: BacktestConfig
    total_return: float
    sharpe_ratio: Optional[float]
    max_drawdown: float
    total_trades: int
    win_rate: float
    equity_curve: List[tuple]
    trade_records: List[dict]
    daily_returns: Dict[datetime, float]
    metrics: Dict[str, float]


class IStrategy(ABC):
    """
    策略接口
    
    統一策略接口，支持多種回測引擎
    """
    
    @abstractmethod
    def initialize(self, config: Dict):
        """
        初始化策略
        
        Args:
            config: 策略配置參數
        """
        pass
    
    @abstractmethod
    def generate_signals(self, context: MarketContext) -> Optional[Signal]:
        """
        生成交易信號
        
        Args:
            context: 市場上下文
        
        Returns:
            Signal or None
        """
        pass
    
    @abstractmethod
    def on_bar(self, context: MarketContext):
        """
        每根 K 線回調
        
        Args:
            context: 市場上下文
        """
        pass
    
    @abstractmethod
    def on_order(self, order: dict):
        """
        訂單狀態回調
        
        Args:
            order: 訂單信息
        """
        pass


class IBacktestEngine(ABC):
    """
    回測引擎接口
    
    支持不同回測後端的統一接口
    """
    
    @abstractmethod
    def add_strategy(self, strategy: IStrategy):
        """添加策略"""
        pass
    
    @abstractmethod
    def add_data(self, symbol: str, start_date: datetime, 
                 end_date: datetime):
        """添加數據"""
        pass
    
    @abstractmethod
    def run(self) -> BacktestResult:
        """執行回測"""
        pass
    
    @abstractmethod
    def get_results(self) -> BacktestResult:
        """獲取結果"""
        pass


class IDataSource(ABC):
    """
    數據源接口
    
    支持多種數據源
    """
    
    @abstractmethod
    def get_ohlcv(self, symbol: str, start: datetime, 
                  end: datetime) -> pd.DataFrame:
        """
        獲取 OHLCV 數據
        
        Args:
            symbol: 交易對
            start: 開始時間
            end: 結束時間
        
        Returns:
            DataFrame with columns: datetime, open, high, low, close, volume
        """
        pass
    
    @abstractmethod
    def get_latest(self, symbol: str) -> Dict:
        """
        獲取最新數據
        
        Args:
            symbol: 交易對
        
        Returns:
            最新 OHLCV 數據
        """
        pass


class IRiskManager(ABC):
    """
    風控管理器接口
    """
    
    @abstractmethod
    def check_entry(self, signal: Signal, context: MarketContext) -> bool:
        """檢查入場風控"""
        pass
    
    @abstractmethod
    def check_exit(self, position: float, context: MarketContext) -> bool:
        """檢查出場風控"""
        pass
    
    @abstractmethod
    def calculate_position_size(self, signal: Signal, 
                               context: MarketContext) -> float:
        """計算倉位大小"""
        pass
```

### Backtrader 實現

```python
# backend/backtesting/backtrader_impl.py

class BacktraderEngineImpl(IBacktestEngine):
    """
    Backtrader 引擎實現
    """
    
    def __init__(self, config: BacktestConfig, db_session: Session):
        self.config = config
        self.db_session = db_session
        self._setup_cerebro()
    
    def _setup_cerebro(self):
        """設置 Cerebro 實例"""
        import backtrader as bt
        
        self.cerebro = bt.Cerebro()
        
        # 配置 broker
        self.cerebro.broker.setcash(self.config.initial_capital)
        self.cerebro.broker.setcommission(commission=self.config.commission)
        self.cerebro.broker.set_slippage_perc(perc=self.config.slippage)
        
        # 添加分析器
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    
    def add_strategy(self, strategy: IStrategy):
        """添加策略"""
        import backtrader as bt
        
        class StrategyWrapper(bt.Strategy):
            def __init__(self, inner_strategy):
                self.inner = inner_strategy
                self.inner.initialize({
                    'cerebro': self,
                })
            
            def next(self):
                context = self._build_context()
                signal = self.inner.generate_signals(context)
                
                if signal:
                    self._execute_signal(signal)
            
            def _build_context(self) -> MarketContext:
                return MarketContext(
                    datetime=self.data.datetime.datetime(0),
                    symbol=self.data._name,
                    open=self.data.open[0],
                    high=self.data.high[0],
                    low=self.data.low[0],
                    close=self.data.close[0],
                    volume=self.data.volume[0],
                    indicators={},
                )
            
            def _execute_signal(self, signal: Signal):
                size = self.broker.getcash() * signal.strength / self.data.close[0]
                
                if signal.direction == 1:
                    self.buy(size=size)
                elif signal.direction == -1:
                    self.sell(size=size)
        
        self.cerebro.addstrategy(StrategyWrapper, strategy)
    
    def add_data(self, symbol: str, start_date: datetime, 
                 end_date: datetime):
        """添加數據"""
        import backtrader as bt
        
        data = DatabaseDataFeed(
            db_session=self.db_session,
            symbol=symbol,
            start_date=start_date,
            end_date=end_date
        )
        
        self.cerebro.adddata(data)
    
    def run(self) -> BacktestResult:
        """執行回測"""
        results = self.cerebro.run()
        return self._build_result(results[0])
    
    def _build_result(self, strategy) -> BacktestResult:
        """構建結果"""
        return BacktestResult(
            config=self.config,
            total_return=(self.cerebro.broker.getvalue() / 
                         self.config.initial_capital - 1),
            sharpe_ratio=strategy.analyzers.sharpe.get_analysis().get('sharperatio'),
            max_drawdown=strategy.analyzers.drawdown.get_analysis()
                          .get('max', {}).get('drawdown'),
            total_trades=strategy.analyzers.trades.get_analysis()
                          .get('total', {}).get('total'),
            win_rate=0.0,  # 計算
            equity_curve=[],
            trade_records=[],
            daily_returns={},
            metrics={},
        )
```

### VectorBT 實現

```python
# backend/backtesting/vectorbt_impl.py

class VectorBTEngineImpl(IBacktestEngine):
    """
    VectorBT 引擎實現
    """
    
    def __init__(self, config: BacktestConfig, db_session: Session):
        self.config = config
        self.db_session = db_session
        self.data = None
        self.strategy = None
    
    def add_data(self, symbol: str, start_date: datetime, 
                 end_date: datetime):
        """添加數據"""
        import vectorbt as vbt
        
        query = """
            SELECT datetime, open, high, low, close, volume
            FROM market_data
            WHERE symbol = %s AND datetime >= %s AND datetime <= %s
            ORDER BY datetime
        """
        
        df = pd.read_sql(
            query,
            con=self.db_session.bind,
            params=(symbol, start_date, end_date)
        )
        
        df.set_index('datetime', inplace=True)
        
        self.data = vbt.Data.from_data(df)
    
    def add_strategy(self, strategy: IStrategy):
        """添加策略"""
        self.strategy = strategy
    
    def run(self) -> BacktestResult:
        """執行回測"""
        import vectorbt as vbt
        
        # 生成信號
        signals = self._generate_signals()
        
        # 構建投資組合
        portfolio = vbt.Portfolio.from_signals(
            close=self.data['close'],
            entries=signals['entry'],
            exits=signals['exit'],
            init_cash=self.config.initial_capital,
            fees=self.config.commission,
            slippage=self.config.slippage,
        )
        
        return self._build_result(portfolio)
    
    def _generate_signals(self) -> dict:
        """生成信號"""
        signals = {'entry': [], 'exit': []}
        
        for i, row in self.data['close'].iterrows():
            context = MarketContext(
                datetime=i,
                symbol=self.config.symbol,
                close=row.values[0],
                high=row.values[0],  # VectorBT 通常使用 close
                low=row.values[0],
                open=row.values[0],
                volume=self.data['volume'].loc[i].values[0] if 'volume' in self.data else 0,
                indicators={},
            )
            
            signal = self.strategy.generate_signals(context)
            
            if signal:
                if signal.direction == 1:
                    signals['entry'].append((i, self.config.symbol))
                elif signal.direction == -1:
                    signals['exit'].append((i, self.config.symbol))
        
        return signals
    
    def _build_result(self, portfolio) -> BacktestResult:
        """構建結果"""
        return BacktestResult(
            config=self.config,
            total_return=portfolio.total_return(),
            sharpe_ratio=portfolio.sharpe_ratio(),
            max_drawdown=portfolio.max_drawdown(),
            total_trades=len(portfolio.trades.records_readable),
            win_rate=portfolio.trades.win_rate(),
            equity_curve=portfolio.value().to_list(),
            trade_records=portfolio.trades.records_readable.to_dict('records'),
            daily_returns=portfolio.returns().to_dict(),
            metrics={
                'sortino_ratio': portfolio.sortino_ratio(),
                'calmar_ratio': portfolio.calmar_ratio(),
                'volatility': portfolio.returns().std(),
            },
        )
```

### 數據庫適配器

```python
# backend/data/storage/db_adapter.py

class DatabaseAdapter(IDataSource):
    """
    數據庫數據源適配器
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_ohlcv(self, symbol: str, start: datetime, 
                  end: datetime) -> pd.DataFrame:
        """獲取 OHLCV 數據"""
        query = """
            SELECT datetime, open, high, low, close, volume
            FROM market_data
            WHERE symbol = %s
              AND datetime >= %s
              AND datetime <= %s
            ORDER BY datetime ASC
        """
        
        df = pd.read_sql(
            query,
            con=self.session.bind,
            params=(symbol, start, end)
        )
        
        df.set_index('datetime', inplace=True)
        return df
    
    def get_latest(self, symbol: str) -> Dict:
        """獲取最新數據"""
        query = """
            SELECT datetime, open, high, low, close, volume
            FROM market_data
            WHERE symbol = %s
            ORDER BY datetime DESC
            LIMIT 1
        """
        
        result = self.session.execute(query, (symbol,)).fetchone()
        
        if not result:
            raise ValueError(f"No data found for {symbol}")
        
        return {
            'datetime': result[0],
            'open': result[1],
            'high': result[2],
            'low': result[3],
            'close': result[4],
            'volume': result[5],
        }
    
    def save_backtest_result(self, result: BacktestResult):
        """保存回測結果"""
        import uuid
        
        result_id = str(uuid.uuid4())
        
        # 保存結果摘要
        self.session.execute(
            """
            INSERT INTO backtest_results 
            (id, strategy_id, params, start_date, end_date, 
             total_return, sharpe_ratio, max_drawdown, 
             total_trades, win_rate, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                result_id,
                None,  # strategy_id
                '{}',  # params JSON
                result.config.start_date,
                result.config.end_date,
                result.total_return,
                result.sharpe_ratio,
                result.max_drawdown,
                result.total_trades,
                result.win_rate,
                datetime.now(),
            )
        )
        
        # 保存交易記錄
        for trade in result.trade_records:
            self.session.execute(
                """
                INSERT INTO trade_records 
                (id, backtest_id, entry_date, exit_date, 
                 entry_price, exit_price, quantity, pnl)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    str(uuid.uuid4()),
                    result_id,
                    trade.get('entry_date'),
                    trade.get('exit_date'),
                    trade.get('entry_price'),
                    trade.get('exit_price'),
                    trade.get('size', 0),
                    trade.get('pnl', 0),
                )
            )
        
        self.session.commit()
```

---

## 總結與建議

### 架構優勢

1. **統一接口設計**：通過抽象層支持多種回測引擎，易於擴展
2. **雙引擎並行**：Backtrader 和 VectorBT 互補，覆蓋不同場景
3. **完整數據流**：從數據收集到結果存儲的端到端流程
4. **多層優化**：緩存、並行、向量化等多個維度的性能優化

### 關鍵設計決策

1. **Backtrader**：適合複雜策略、事件驅動、精確的訂單管理
2. **VectorBT**：適合參數優化、批量回測、指標計算
3. **緩存策略**：Redis L1 + PostgreSQL L2，平衡速度和持久化
4. **並行處理**：進程級並行避免 GIL 限制

### Programmer Sub-Agent 設計啟示

1. **模塊化設計**：每個組件有清晰的職責和接口
2. **可測試性**：依賴注入，易於單元測試
3. **可擴展性**：通過接口擴展，不改變核心代碼
4. **性能優先**：多種優化手段，根據場景選擇

### 待改進方向

1. **實時回測**：支持流數據實時回測
2. **雲原生**：支持分布式回測，彈性擴展
3. **可視化**：增強回測結果可視化
4. **策略庫**：預置更多常用策略

---

## Metadata

- **分析框架:** 架構分析 + 技術評估
- **建議用途:** Programmer Sub-Agent 設計參考
- **關鍵依賴:** Backtrader, VectorBT, PostgreSQL, Redis
- **估計複雜度:** 高（需要多個專業領域知識）
