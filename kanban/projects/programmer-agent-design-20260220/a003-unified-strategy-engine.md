# A003 - Unified Strategy Engine Deep Analysis

**Task ID:** a003-unified-strategy-engine
**Agent:** Charlie Analyst
**Status:** completed
**Timestamp:** 2026-02-21T00:19:00+08:00

---

## Executive Summary

The unified strategy engine design presents a well-architected solution for consolidating legacy trading strategies into a single, maintainable system. The core innovation is the `IStrategy` interface combined with VectorBT for backtesting execution, enabling code unification, simplified maintenance, and enhanced functionality through strategy composition (SignalMerger). The design follows clean architecture principles with clear separation of concerns through dedicated components like SignalAdapter, ExecutionContextFactory, and UnifiedStrategyEngine.

Key findings: The architecture successfully decouples strategy logic from execution infrastructure, supports both individual and composite strategies, and maintains backward compatibility. The migration plan is phased and methodical, with comprehensive testing strategies. However, the design primarily focuses on VectorBT integration with minimal Backtrader references, suggesting a strategic shift away from Backtrader.

---

## 1. Architecture Overview

### 1.1 Design Goals

The unified strategy engine is built around four core objectives:

1. **Code Unification** - All strategies implement a single `IStrategy` interface
2. **Maintenance Simplification** - Single codebase eliminates duplication
3. **Feature Enhancement** - Supports `SignalMerger` for combining multiple strategies
4. **Backward Compatibility** - API interfaces remain unchanged

### 1.2 High-Level Architecture

```
API Layer (FastAPI)
    ↓
UnifiedStrategyEngine (NEW)
    ├─ Strategy Initialization (StrategyFactory)
    ├─ Historical Data Loading (VBTDataLoader)
    ├─ Daily Signal Generation (NEW LOGIC)
    ├─ VectorBT Backtesting Execution
    └─ Result Formatting
```

**Architecture Pattern:** The system follows a **Layered Architecture** with clear separation between:
- **Presentation Layer**: API endpoints (`/api/strategies/technical/run`)
- **Business Logic Layer**: UnifiedStrategyEngine, strategies
- **Data Access Layer**: VBTDataLoader
- **Infrastructure Layer**: VectorBT execution engine

### 1.3 Core Design Philosophy

1. **Interface-Based Design**: All strategies implement `IStrategy`, enabling polymorphism
2. **Factory Pattern**: `StrategyFactory` centralizes strategy instantiation
3. **Adapter Pattern**: `SignalAdapter` bridges IStrategy signals to VectorBT format
4. **Context Pattern**: `ExecutionContextFactory` provides strategy execution context
5. **Composition over Inheritance**: `CompositeStrategy` combines multiple strategies

---

## 2. Unified Interface Design

### 2.1 IStrategy Interface

The `IStrategy` interface is the cornerstone of the unified system. While the full interface definition is not shown in the document, the design reveals its key methods:

**Core Methods:**
```python
class IStrategy:
    def generate_signals(
        self,
        context: ExecutionContext,
        symbols: List[str]
    ) -> List[StrategySignal]:
        """Generate trading signals for given context and symbols"""
        pass

    @property
    def name(self) -> str:
        """Strategy identifier"""
        pass
```

**SignalAction Enum:**
```python
class SignalAction(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"  # No action
```

**StrategySignal Structure:**
```python
@dataclass
class StrategySignal:
    symbol: str
    action: SignalAction
    confidence: float  # Signal strength 0.0-1.0
```

### 2.2 ExecutionContext Design

The execution context provides strategy instances with all necessary runtime information:

```python
@dataclass
class ExecutionContext:
    portfolio_value: float
    available_cash: float
    current_positions: List[PositionState]
    market_date: date
    market_status: str  # 'OPEN', 'CLOSED', etc.
```

**PositionState Structure:**
```python
@dataclass
class PositionState:
    symbol: str
    quantity: int
    current_price: float
    # May include: entry_price, unrealized_pnl, etc.
```

### 2.3 Interface Benefits

| Aspect | Traditional Approach | Unified Interface |
|--------|---------------------|-------------------|
| Code Duplication | Multiple strategy implementations | Single interface, multiple implementations |
| Testing | Test each strategy separately | Test interface once, verify implementations |
| Composition | Difficult to combine strategies | Easy via CompositeStrategy |
| Maintenance | Update each strategy individually | Update interface, all strategies benefit |

---

## 3. Key Components

### 3.1 SignalAdapter

**Purpose:** Convert IStrategy's `SignalAction` format to VectorBT's boolean DataFrame format.

**Key Characteristics:**
- Static utility class (no state)
- Converts date-grouped signals to DataFrame
- Handles BUY/SELL/HOLD mapping
- Maintains temporal alignment with OHLCV data

**Conversion Logic:**
```python
signals_by_date = {
    date(2024, 1, 1): [
        StrategySignal("AAPL", SignalAction.BUY, 0.8),
        StrategySignal("MSFT", SignalAction.SELL, 0.6)
    ]
}

↓ Convert to ↓

entries DataFrame:
Date        | AAPL | MSFT | GOOGL
------------|------|------|------
2024-01-01  | True | False| False

exits DataFrame:
Date        | AAPL | MSFT | GOOGL
------------|------|------|------
2024-01-01  | False| True | False
```

**Design Pattern:** Adapter Pattern - bridges between IStrategy signal domain and VectorBT execution domain.

### 3.2 ExecutionContextFactory

**Purpose:** Create ExecutionContext instances for daily signal generation.

**Key Characteristics:**
- Maintains portfolio state across iterations
- Tracks initial capital
- Simulates position changes
- Provides clean context for each strategy invocation

**State Management:**
```python
class ExecutionContextFactory:
    def __init__(self, initial_cash: float = 100000):
        self.initial_cash = initial_cash
        self.positions: Dict[str, PositionState] = {}  # Runtime state
```

**Design Pattern:** Factory Pattern + State Pattern - creates context objects while managing runtime state.

### 3.3 UnifiedStrategyEngine

**Purpose:** Core orchestrator integrating IStrategy with VectorBT.

**Responsibilities:**
1. Load historical data
2. Generate signals daily
3. Convert signals to VectorBT format
4. Execute VectorBT backtest
5. Format and return results

**Key Methods:**
```python
class UnifiedStrategyEngine:
    def backtest(
        self,
        symbols: List[str],
        start_date: date,
        end_date: date,
        universe: str
    ) -> Dict[str, Any]:
        # Main backtest orchestration

    def _generate_signals_daily(
        self,
        dates: pd.DatetimeIndex,
        symbols: List[str],
        start_date: date,
        end_date: date
    ) -> Dict[date, List[StrategySignal]]:
        # Core signal generation loop
```

**Design Pattern:** Facade Pattern - provides simplified interface to complex subsystem (strategy + VectorBT).

### 3.4 StrategyFactory

**Purpose:** Centralized strategy instantiation.

**Supported Strategy Types:**
- **Individual Strategies:** RSI, MACD, Momentum, SuperTrend
- **Composite Strategies:** SignalMerger combinations

**Merge Algorithms (for CompositeStrategy):**
```python
merge_algorithms = [
    'majority_vote',  # Buy if majority says buy
    'unanimous',      # Buy only if all say buy
    'weighted',       # Weight by confidence
    'any'             # Buy if any says buy
]
```

**Design Pattern:** Factory Pattern + Abstract Factory Pattern.

---

## 4. Backtrader Integration

### 4.1 Current Status

**Observation:** The design document does **not** include Backtrader integration details. The architecture explicitly focuses on VectorBT as the primary execution engine.

### 4.2 Implications

1. **Strategic Shift:** The system appears to be migrating away from Backtrader toward VectorBT
2. **Backward Compatibility:** No mention of maintaining Backtrader compatibility
3. **Legacy Code:** Existing Backtrader strategies will need migration

### 4.3 Potential Backtrader Integration (If Needed)

If Backtrader integration is required, it would follow the same pattern:

```python
class BacktraderEngine:
    """Alternative execution engine using Backtrader"""

    def __init__(self, strategy: IStrategy):
        self.strategy = strategy

    def backtest(self, data: pd.DataFrame) -> bt.Cerebro:
        """Execute using Backtrader"""
        cerebro = bt.Cerebro()
        # Convert IStrategy to Backtrader Strategy class
        bt_strategy = self._convert_to_backtrader_strategy()
        cerebro.addstrategy(bt_strategy)
        return cerebro.run()
```

**Recommendation:** If Backtrader support is needed, implement as an alternative engine following the same IStrategy interface.

---

## 5. VectorBT Integration

### 5.1 Integration Architecture

VectorBT serves as the **execution engine** in the unified architecture:

```
IStrategy.generate_signals()
    ↓
SignalAdapter.signals_to_vectorbt()
    ↓
vbt.Portfolio.from_signals()
    ↓
pf.stats() → Results
```

### 5.2 Key Integration Points

**1. Data Loading:**
```python
class VBTDataLoader:
    def load_ohlcv(
        self,
        symbols: List[str],
        start_date: date,
        end_date: date
    ) -> pd.DataFrame:
        """Load OHLCV data in VectorBT format"""
        # Returns MultiIndex DataFrame: (symbol, date)
        pass

    def load_prices(
        self,
        symbols: List[str],
        start_date: date,
        end_date: date
    ) -> pd.DataFrame:
        """Load price data for portfolio creation"""
        pass
```

**2. Signal Conversion:**
```python
entries, exits = SignalAdapter.signals_to_vectorbt(
    ohlcv_index,
    signals_by_date
)

# entries: DataFrame[symbol] = bool (True = buy signal)
# exits: DataFrame[symbol] = bool (True = sell signal)
```

**3. Portfolio Creation:**
```python
pf = vbt.Portfolio.from_signals(
    data,              # Price data
    entries=entries,    # Boolean entry signals
    exits=exits,        # Boolean exit signals
    init_cash=initial_cash,
    freq='1D',
    fees=0.001,         # Optional: transaction costs
    slippage=0.0001     # Optional: slippage
)
```

**4. Metrics Extraction:**
```python
stats = pf.stats()

metrics = {
    'total_return': stats['total_return'],
    'sharpe_ratio': stats['sharpe_ratio'],
    'max_drawdown': stats['max_drawdown'],
    'win_rate': stats['win_rate'],
    'num_trades': stats['num_trades'],
    'equity_curve': pf.value().tolist()
}
```

### 5.3 VectorBT Advantages in This Architecture

| Feature | Benefit |
|---------|---------|
| Vectorized Operations | Fast computation across multiple symbols |
| Signal-Based Interface | Natural fit for IStrategy signal output |
| Portfolio Class | Built-in position management |
| Extensive Metrics | Comprehensive performance analytics |
| Pandas Integration | Seamless data handling |

---

## 6. Strategy Execution Flow

### 6.1 Complete Execution Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│ 1. API Request                                             │
│    POST /api/strategies/technical/run                      │
│    { strategy_type: "rsi", universe: "tw_strategy" }      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Strategy Factory                                         │
│    strategy = StrategyFactory.create("rsi", params)        │
│    → Instantiates RSIStrategy with parameters              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Data Loading                                             │
│    ohlcv = VBTDataLoader.load_ohlcv(symbols, start, end)   │
│    → Loads historical price data                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. Daily Signal Generation (Loop)                          │
│                                                            │
│    For each date in date_range:                            │
│      a. Calculate portfolio value                          │
│      b. Create ExecutionContext                            │
│      c. strategy.generate_signals(context, symbols)        │
│      d. Store signals for date                             │
│      e. Update position state (simulated)                  │
│                                                            │
│    → Output: Dict[date, List[StrategySignal]]              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. Signal Conversion                                        │
│    entries, exits = SignalAdapter.signals_to_vectorbt(...) │
│    → Converts to Boolean DataFrames                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. VectorBT Execution                                        │
│    pf = vbt.Portfolio.from_signals(                         │
│        data, entries, exits, init_cash                      │
│    )                                                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 7. Results Formatting                                       │
│    return {                                                 │
│        'equity_curve': pf.value().tolist(),                │
│        'returns': stats['total_return'],                   │
│        'sharpe_ratio': stats['sharpe_ratio'],              │
│        'max_drawdown': stats['max_drawdown'],               │
│        ...                                                  │
│    }                                                        │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Signal Generation Loop Detail

The **daily signal generation** is the core innovation:

```python
for date in dates:
    # 1. Calculate portfolio state
    portfolio_value = cash + sum(
        pos.quantity * pos.current_price
        for pos in positions.values()
    )

    # 2. Create execution context
    context = ExecutionContextFactory.create_context(
        date=date,
        current_positions=positions,
        current_cash=cash,
        portfolio_value=portfolio_value
    )

    # 3. Generate signals (NEW LOGIC)
    signals = strategy.generate_signals(context, symbols)

    # 4. Store and update state
    if signals:
        signals_by_date[date] = signals
        # Update positions for next iteration
        for signal in signals:
            if signal.action == SignalAction.BUY:
                positions[signal.symbol] = create_position(...)
            elif signal.action == SignalAction.SELL:
                cash += positions[signal.symbol].value
                del positions[signal.symbol]
```

### 6.3 Composite Strategy Execution

When using `CompositeStrategy` with `SignalMerger`:

```
For each date:
    ├─ RSI.generate_signals() → [Signal(AAPL, BUY, 0.7)]
    ├─ MACD.generate_signals() → [Signal(AAPL, SELL, 0.6)]
    └─ SignalMerger.merge([rsi_signals, macd_signals])
        → [Signal(AAPL, HOLD, 0.65)]  # Majority vote
```

**Merge Algorithm Behavior:**
- **majority_vote:** Buy if 50%+ say buy
- **unanimous:** Buy only if all say buy
- **weighted:** Weighted average of confidence
- **any:** Buy if any says buy

---

## 7. Performance Optimization Strategies

### 7.1 Identified Performance Bottlenecks

| Bottleneck | Impact | Location |
|------------|--------|----------|
| Daily iteration loop | 🟠 Medium | `_generate_signals_daily()` |
| Repeated indicator calculations | 🟠 Medium | Strategy implementations |
| Database queries per date | 🔴 High | Data loading |
| Position state updates | 🟡 Low | Simulated trading |

### 7.2 Optimization Strategies

**Strategy 1: Vectorized Indicator Calculation**
```python
# Instead of: Calculate indicators per date
for date in dates:
    rsi = calculate_rsi(symbol, date)

# Use: Pre-calculate all indicators
def generate_signals(self, context, symbols):
    # Pre-computed indicators available
    rsi_values = self.indicator_cache[symbol]['rsi']
    current_rsi = rsi_values[context.market_date]
```

**Strategy 2: Batch Data Loading**
```python
class VBTDataLoader:
    def __init__(self):
        self.data_cache = {}  # Symbol → DataFrame

    def load_ohlcv_batch(self, symbols, start, end):
        # Load all symbols in one query
        query = """
        SELECT symbol, date, open, high, low, close, volume
        FROM prices
        WHERE symbol IN (?, ?, ...) AND date BETWEEN ? AND ?
        """
        return self.execute(query)
```

**Strategy 3: Indicator Caching**
```python
class IndicatorCache:
    def __init__(self):
        self.cache = {}  # (symbol, indicator) → Series

    def get_or_compute(self, symbol, indicator_fn):
        key = (symbol, indicator_fn.__name__)
        if key not in self.cache:
            self.cache[key] = indicator_fn(symbol)
        return self.cache[key]
```

**Strategy 4: Parallel Signal Generation**
```python
from concurrent.futures import ThreadPoolExecutor

def _generate_signals_daily_parallel(self, dates, symbols):
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(
                self._generate_signals_for_date,
                date,
                symbols
            )
            for date in dates
        ]
        results = [f.result() for f in futures]
    return {k: v for d in results for k, v in d.items()}
```

**Strategy 5: Lazy Evaluation for Indicators**
```python
# Only calculate indicators when needed
@lru_cache(maxsize=100)
def get_rsi(self, symbol, period=14):
    """Cached RSI calculation"""
    return ta.momentum.RSIIndicator(
        self.price_data[symbol]['close'],
        window=period
    ).rsi()
```

### 7.3 Performance Metrics Monitoring

```python
class PerformanceMonitor:
    def __init__(self):
        self.metrics = {
            'data_load_time': [],
            'signal_gen_time': [],
            'vbt_execution_time': []
        }

    def measure(self, metric_name):
        """Decorator for timing functions"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                start = time.time()
                result = func(*args, **kwargs)
                elapsed = time.time() - start
                self.metrics[metric_name].append(elapsed)
                return result
            return wrapper
        return decorator

    def report(self):
        """Generate performance report"""
        return {
            name: {
                'mean': np.mean(times),
                'median': np.median(times),
                'max': max(times)
            }
            for name, times in self.metrics.items()
        }
```

### 7.4 Expected Performance Improvements

| Optimization | Expected Gain | Priority |
|--------------|---------------|----------|
| Vectorized indicators | 5-10x faster | 🔴 High |
| Batch data loading | 3-5x faster | 🔴 High |
| Indicator caching | 2-3x faster | 🟠 Medium |
| Parallel signal gen | 2-4x faster (multi-core) | 🟡 Low |
| Lazy evaluation | 1.5-2x faster | 🟡 Low |

---

## 8. Programmer Sub-Agent Knowledge Base

### 8.1 Core Concepts for Programmer Sub-Agent

When designing a programmer sub-agent to work with the unified strategy engine, it must understand:

#### A. Strategy Interface Contract

```python
# Every strategy must implement this interface
class IStrategy:
    name: str  # Unique identifier

    def generate_signals(
        self,
        context: ExecutionContext,
        symbols: List[str]
    ) -> List[StrategySignal]:
        """
        Core method: Generate trading signals

        Constraints:
        - Return list of signals, one per symbol
        - Only BUY/SELL actions (HOLD implied by absence)
        - Confidence score 0.0-1.0
        - Must be deterministic for same input
        """
        pass
```

#### B. Signal Semantics

| Signal Action | Meaning | Usage |
|---------------|---------|-------|
| BUY | Open long position | Entry signal |
| SELL | Close position | Exit signal |
| HOLD | No action | Implicit (not returned) |

**Signal Generation Rules:**
1. **One signal per symbol**: Don't return multiple signals for same symbol
2. **Confidence matters**: Use for ranking/filtering later
3. **Market awareness**: Check `context.market_status` before trading
4. **Position awareness**: Use `context.current_positions` to avoid double-entry

#### C. Context Interpretation

```python
# Always check portfolio state before generating signals
def generate_signals(self, context, symbols):
    signals = []

    for symbol in symbols:
        # Check if already holding
        existing_position = next(
            (p for p in context.current_positions if p.symbol == symbol),
            None
        )

        # Don't buy if already holding
        if existing_position:
            continue

        # Check cash availability
        if context.available_cash < self.min_trade_size:
            continue

        # Generate signal based on indicators
        if self.should_buy(symbol, context.market_date):
            signals.append(StrategySignal(
                symbol=symbol,
                action=SignalAction.BUY,
                confidence=0.8
            ))

    return signals
```

#### D. Data Access Patterns

```python
# Access price data through strategy's data cache
class MyStrategy(IStrategy):
    def __init__(self, data_loader):
        self.data = data_loader
        self.indicator_cache = {}

    def get_rsi(self, symbol, date):
        """Get RSI for symbol at date"""
        # Load data for symbol
        df = self.data.load_prices([symbol], start_date, end_date)

        # Calculate if not cached
        if symbol not in self.indicator_cache:
            self.indicator_cache[symbol] = ta.momentum.RSIIndicator(
                df['close'],
                window=14
            ).rsi()

        # Return value at date
        return self.indicator_cache[symbol].loc[date]
```

### 8.2 Common Strategy Patterns

#### Pattern 1: Mean Reversion (RSI)

```python
class RSIStrategy(IStrategy):
    def __init__(self, period=14, buy_threshold=30, sell_threshold=70):
        self.period = period
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold
        self.rsi_cache = {}

    def generate_signals(self, context, symbols):
        signals = []

        for symbol in symbols:
            # Get RSI value
            rsi = self._get_rsi(symbol, context.market_date)

            # Generate signals
            if rsi < self.buy_threshold:
                signals.append(StrategySignal(
                    symbol=symbol,
                    action=SignalAction.BUY,
                    confidence=(self.buy_threshold - rsi) / self.buy_threshold
                ))
            elif rsi > self.sell_threshold:
                signals.append(StrategySignal(
                    symbol=symbol,
                    action=SignalAction.SELL,
                    confidence=(rsi - self.sell_threshold) / (100 - self.sell_threshold)
                ))

        return signals
```

#### Pattern 2: Trend Following (MACD)

```python
class MACDStrategy(IStrategy):
    def __init__(self, fast=12, slow=26, signal=9):
        self.fast = fast
        self.slow = slow
        self.signal = signal
        self.indicator_cache = {}

    def generate_signals(self, context, symbols):
        signals = []

        for symbol in symbols:
            macd, signal_line = self._get_macd(symbol, context.market_date)

            # MACD crossover: MACD crosses above signal
            if macd > signal_line and self._previous_macd_below_signal(symbol, context.market_date):
                signals.append(StrategySignal(
                    symbol=symbol,
                    action=SignalAction.BUY,
                    confidence=min(1.0, abs(macd - signal_line) / signal_line)
                ))
            elif macd < signal_line and self._previous_macd_above_signal(symbol, context.market_date):
                signals.append(StrategySignal(
                    symbol=symbol,
                    action=SignalAction.SELL,
                    confidence=min(1.0, abs(macd - signal_line) / signal_line)
                ))

        return signals
```

#### Pattern 3: Multi-Indicator Confluence

```python
class ConfluenceStrategy(IStrategy):
    def generate_signals(self, context, symbols):
        signals = []

        for symbol in symbols:
            # Get multiple indicators
            rsi = self.rsi_strategy._get_rsi(symbol, context.market_date)
            macd, _ = self.macd_strategy._get_macd(symbol, context.market_date)
            sma_diff = self._get_sma_diff(symbol, context.market_date)

            # Confluence: All indicators agree
            buy_signals = 0
            if rsi < 30:
                buy_signals += 1
            if macd > 0:
                buy_signals += 1
            if sma_diff > 0:
                buy_signals += 1

            # Require at least 2/3 agreement
            if buy_signals >= 2:
                signals.append(StrategySignal(
                    symbol=symbol,
                    action=SignalAction.BUY,
                    confidence=buy_signals / 3.0
                ))

        return signals
```

### 8.3 Testing Strategies for Programmer Sub-Agent

#### Unit Testing Template

```python
def test_strategy_signals():
    """Test strategy generates correct signals"""

    # Setup
    strategy = RSIStrategy(period=14)
    context = ExecutionContext(
        portfolio_value=100000,
        available_cash=50000,
        current_positions=[],
        market_date=date(2024, 1, 15),
        market_status='CLOSED'
    )
    symbols = ['AAPL', 'MSFT']

    # Execute
    signals = strategy.generate_signals(context, symbols)

    # Assert
    assert isinstance(signals, list)
    assert all(isinstance(s, StrategySignal) for s in signals)
    assert all(s.symbol in symbols for s in signals)
```

#### Integration Testing Template

```python
def test_strategy_with_vectorbt():
    """Test strategy integrates with VectorBT"""

    # Setup
    strategy = RSIStrategy()
    engine = UnifiedStrategyEngine(
        strategy=strategy,
        data_loader=MockDataLoader(),
        context_factory=ExecutionContextFactory()
    )

    # Execute
    result = engine.backtest(
        symbols=['AAPL'],
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
        universe='test'
    )

    # Assert
    assert 'sharpe_ratio' in result
    assert 'max_drawdown' in result
    assert 'equity_curve' in result
```

### 8.4 Common Pitfalls & Best Practices

#### Pitfalls to Avoid

1. **❌ Not checking position state:**
```python
# Bad: Always buy
if rsi < 30:
    signals.append(Buy(symbol, 0.8))

# Good: Check if already holding
if rsi < 30 and not existing_position:
    signals.append(Buy(symbol, 0.8))
```

2. **❌ Ignoring cash constraints:**
```python
# Bad: Always buy regardless of cash
signals.append(Buy(symbol, 0.8))

# Good: Check cash availability
if context.available_cash >= min_trade_size:
    signals.append(Buy(symbol, 0.8))
```

3. **❌ Non-deterministic behavior:**
```python
# Bad: Uses random
if random.random() > 0.5:
    signals.append(Buy(symbol, 0.8))

# Good: Deterministic logic
if rsi < 30:
    signals.append(Buy(symbol, 0.8))
```

4. **❌ Inefficient indicator calculation:**
```python
# Bad: Recalculate every time
def generate_signals(self, context, symbols):
    for symbol in symbols:
        rsi = calculate_rsi(symbol, context.market_date)  # Slow!

# Good: Pre-calculate and cache
def __init__(self):
    self.rsi_cache = {}

def generate_signals(self, context, symbols):
    for symbol in symbols:
        rsi = self.rsi_cache[symbol].loc[context.market_date]
```

#### Best Practices

1. **✅ Use descriptive strategy names:**
```python
class RSIMeanReversionStrategy(IStrategy):
    name = "rsi_mean_reversion"  # Clear identifier
```

2. **✅ Validate inputs:**
```python
def __init__(self, period=14, buy_threshold=30, sell_threshold=70):
    if not (0 < buy_threshold < sell_threshold < 100):
        raise ValueError("Invalid thresholds")
    # ...
```

3. **✅ Document confidence scoring:**
```python
def _calculate_confidence(self, rsi, threshold):
    """
    Calculate confidence based on how far RSI is from threshold.

    Returns: 0.0 to 1.0
    """
    return min(1.0, abs(rsi - threshold) / threshold)
```

4. **✅ Use dataclasses for signals:**
```python
@dataclass
class StrategySignal:
    symbol: str
    action: SignalAction
    confidence: float

    def __post_init__(self):
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("Confidence must be 0.0-1.0")
```

### 8.5 Migration Guidelines

When migrating existing strategies to the unified interface:

**Step 1: Identify Dependencies**
```python
# Old strategy might use:
- Backtrader Cerebro
- Direct database access
- Global state
- Custom event loops

# Need to replace with:
- IStrategy interface
- VBTDataLoader
- ExecutionContext
- Signal generation
```

**Step 2: Extract Signal Logic**
```python
# Old: Embedded in backtrader next() method
def next(self):
    if self.rsi < 30:
        self.buy()

# New: Extract to generate_signals()
def generate_signals(self, context, symbols):
    signals = []
    for symbol in symbols:
        if self._get_rsi(symbol) < 30:
            signals.append(StrategySignal(symbol, BUY, 0.8))
    return signals
```

**Step 3: Register with StrategyFactory**
```python
class StrategyFactory:
    @staticmethod
    def create(strategy_type: str, params: Dict):
        # Add your strategy here
        if strategy_type == "my_strategy":
            return MyStrategy(
                param1=params.get('param1', default_value)
            )
```

**Step 4: Test and Verify**
```python
# Run comparison tests
old_result = run_old_strategy(...)
new_result = run_unified_strategy(...)

# Verify results match (within tolerance)
assert abs(old_result['sharpe'] - new_result['sharpe']) < 0.01
```

---

## 9. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| New/old result inconsistency | Medium | High | Comprehensive comparison testing |
| Performance degradation | Low | Medium | Vectorized optimizations, caching |
| API compatibility issues | Low | Medium | Maintain interface contracts |
| Missing edge cases | Medium | Medium | Extensive unit/integration tests |
| Complex strategy migration | High | High | Phased migration, code reviews |
| Position state simulation errors | Medium | High | Validate state transitions |

---

## 10. Recommendations

### 10.1 For Programmer Sub-Agent Design

1. **Priority 1 - Core Interface Mastery**
   - Ensure sub-agent understands `IStrategy` contract
   - Teach signal generation patterns
   - Emphasize context interpretation

2. **Priority 2 - Testing Discipline**
   - Require unit tests for all new strategies
   - Enforce integration tests before deployment
   - Automate regression testing

3. **Priority 3 - Performance Awareness**
   - Teach vectorized calculation techniques
   - Emphasize indicator caching
   - Profile before optimizing

4. **Priority 4 - Migration Safety**
   - Always test before migrating
   - Keep old code until verified
   - Document breaking changes

### 10.2 For System Implementation

1. **Start with Phase 1** (2-3 days)
   - Implement SignalAdapter, ExecutionContextFactory
   - Create UnifiedStrategyEngine foundation
   - Write comprehensive unit tests

2. **Migrate One Strategy at a Time** (3-4 days)
   - Start with simplest (RSI)
   - Verify results match old system
   - Then move to next (MACD, Momentum, SuperTrend)

3. **Add Composite Strategy Support** (1-2 days)
   - Implement CompositeStrategy
   - Add SignalMerger with multiple algorithms
   - Test strategy combinations

4. **Performance Optimization** (1-2 days)
   - Profile bottlenecks
   - Implement vectorization
   - Add caching layer

**Total Estimated Time:** 7-11 days

---

## 11. Confidence & Limitations

### Confidence Level: **High**

**Rationale:**
- Design is well-documented with clear architecture
- Design patterns are standard and proven
- Migration path is methodical and phased
- Testing strategy is comprehensive

### Limitations

1. **Incomplete Interface Definition**: Full IStrategy interface not shown in document
2. **No Backtrader Details**: Design focuses on VectorBT; Backtrader migration unclear
3. **Missing Implementation Details**: Some components described conceptually
4. **No Performance Benchmarks**: Expected improvements not quantified

### Assumptions Made

1. VectorBT is the preferred execution engine (not Backtrader)
2. Position state simulation is simplified (not full order book)
3. Database access is through DuckDB (based on conn parameter)
4. API remains backward compatible during migration

---

## 12. Metadata

**Analysis Framework:** Architecture Analysis + Design Pattern Identification

**Suggestions for Creative Work:**

1. **Strategy Development**: Use this analysis to guide programmer sub-agent in creating new strategies
2. **Performance Optimization**: Implement the vectorization and caching strategies
3. **Testing Automation**: Create automated comparison tests for migration validation
4. **Documentation**: Expand this into a full developer guide

**Related Artifacts:**
- Source Document: `/Users/charlie/Dashboard/docs/architecture/unified-strategy-engine-design.md`
- Output Path: `/Users/charlie/.openclaw/workspace/kanban/projects/programmer-agent-design-20260220/a003-unified-strategy-engine.md`

---

*Analysis complete. This document provides a comprehensive foundation for understanding the unified strategy engine architecture and serves as a knowledge base for designing the programmer sub-agent.*
