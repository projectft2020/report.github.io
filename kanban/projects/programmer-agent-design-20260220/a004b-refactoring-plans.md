# Refactoring Plans Analysis

**Task ID:** a004b
**Agent:** Charlie Analyst
**Status:** completed
**Timestamp:** 2026-02-21T00:19:00+08:00
**Source:** /Users/charlie/Dashboard/docs/architecture/

---

## Executive Summary

Analysis of Dashboard refactoring plans reveals a comprehensive architectural evolution strategy focused on modernizing the frontend state management, unifying strategy systems, and implementing multi-strategy backtesting capabilities. Six major refactoring documents were identified, spanning frontend optimization, backend architecture unification, and futures trading system implementation. Key themes include progressive migration, backward compatibility, and modular design patterns.

---

## 1. Document Inventory

### 1.1 Complete List of Refactoring Plans

| # | Document | Path | Status | Date |
|---|----------|------|--------|------|
| 1 | React Query 遷移計畫 | `current/react-query-migration-plan.md` | ✅ Adopted | 2026-01-31 |
| 2 | 符號類型統一 - 實施報告 | `current/symbol-type-unification.md` | ✅ Complete | 2026-01-31 |
| 3 | 策略系統實作架構 | `current/strategy-system-implementation.md` | ✅ Ready | 2026-01-31 |
| 4 | 複合策略系統整合指南 | `COMPOSITE_INTEGRATION_GUIDE.md` | ✅ Ready | 2026-01-30 |
| 5 | 統一策略引擎設計 | `unified-strategy-engine-design.md` | ✅ Design | 2026-01-30 |
| 6 | 期貨多策略組合回測系統 | `futures_multi_strategy_backtest_design.md` | ✅ Complete | 2026-01-30 |

### 1.2 Document Categories

**Frontend Refactoring:**
- React Query Migration Plan

**Backend Architecture:**
- Symbol Type Unification
- Strategy System Implementation
- Unified Strategy Engine Design
- Composite Strategy Integration Guide

**New Feature Implementation:**
- Futures Multi-Strategy Backtest System

---

## 2. Scope and Objectives

### 2.1 React Query 遷移計畫

**Scope:**
- Migrate frontend API data fetching from custom `requestProtection.js` to React Query (TanStack Query v5.90.16)
- Progressive migration across all frontend pages

**Objectives:**
1. Reduce codebase by 30-70% (20-60 lines per page average)
2. Lower maintenance costs (5 bug fixes in 2 weeks for requestProtection.js)
3. Implement built-in caching and request deduplication
4. Minimal bundle impact (only 13KB, 2.4% increase)

**Target Pages:**
- Phase 1 (Priority P0): StrategyShowcasePage, MomentumPage, AllocationPage, FuturesBacktestPage
- Phase 2 (Priority P1): MarketScanner, SignalDashboardPage, StrategyPage, PredictionMomentumPage
- Phase 3 (Priority P2): Remaining 30+ pages (as needed)

### 2.2 符號類型統一

**Scope:**
- Unify symbol type handling in futures backtest system
- Consolidate `get_futures_spec`, `get_futures_spec_by_str`, and `get_spec_for_symbol`

**Objectives:**
1. Single entry point: `get_spec_for_symbol`
2. Support both FuturesSymbol enum and string inputs
3. Deprecate duplicate functions with warnings
4. Maintain backward compatibility
5. Add `is_futures` property for type identification

**Status:** ✅ Complete - 11 tests passing, all existing tests pass

### 2.3 策略系統實作架構

**Scope:**
- Unified strategy system architecture
- Strategy classification and implementation status tracking
- Priority-driven implementation plan

**Objectives:**
1. Implement technical indicator calculation module (RSI, MACD, SuperTrend, Momentum)
2. Migrate signal strategies from mock to real indicator calculations
3. Implement initial return distribution analysis
4. Build SRS (Strategy Rating System) with 5-dimensional scoring
5. Implement advanced Bootstrap analysis with Numba acceleration

**Strategy Types:**
- SignalBased: RSI, MACD, SuperTrend, FIndex
- Momentum: SP500Momentum, GeneralMomentum
- DualMomentum: DualMomentum
- Allocation: FixedWeight (60/40), AllWeather, GoldenButterfly
- Composite: PortfolioMixer

### 2.4 複合策略系統整合指南

**Scope:**
- Integration of composite and hedged strategy systems
- Unified backtest router supporting multiple modes
- Backward compatible architecture

**Objectives:**
1. Create StrategyOrchestrator for unified strategy execution
2. Implement 5 backtest modes: Legacy Single, VectorBT Single, Composite, Hedged, Unified
3. Build HedgedBacktestAdapter with hedge signal integration
4. Support 4 hedge types: Index Futures, Inverse ETF, Sector ETF, Cross Asset
5. Maintain full backward compatibility with existing `/api/backtest/run`

**Signal Merge Rules:**
- unanimous, majority, weighted, priority, conservative, aggressive (6 algorithms)

### 2.5 統一策略引擎設計

**Scope:**
- Unify new and old strategy systems using IStrategy + VectorBT
- SignalAdapter for converting IStrategy signals to VectorBT format
- ExecutionContextFactory for context creation

**Objectives:**
1. Code unification - all strategies use IStrategy interface
2. Simplified maintenance - single codebase
3. Enhanced functionality - SignalMerger for composite strategies
4. Backward compatible API

**Migration Phases:**
- Phase 1: Preparation (SignalAdapter, ExecutionContextFactory, UnifiedStrategyEngine)
- Phase 2: Single strategy migration (RSI, MACD, Momentum, SuperTrend)
- Phase 3: Composite strategy migration
- Phase 4: Cleanup and optimization

**Estimated Effort:** 4-5 days

### 2.6 期貨多策略組合回測系統

**Scope:**
- Multi-strategy portfolio backtest system for futures
- Support for constant and floating exposure modes
- Integration with existing performance/analytics modules

**Objectives:**
1. Implement 3 core strategies: ES_MACD, GC_MACD, ES_BuyHold
2. Build futures backtest engine with daily signal generation
3. Support contract sizing based on multiplier and exposure mode
4. Comprehensive performance analysis (equity curve, metrics, correlation)
5. API and frontend implementation

**Status:** ✅ Complete - All 4 phases delivered, 102 tests passing

**Capital Management:**
- Constant Exposure: Fixed investment regardless of P&L
- Floating Exposure: Investment scales with portfolio value

---

## 3. Refactoring Strategies and Methods

### 3.1 Progressive Migration Strategy

**Pattern:** Used across multiple refactoring plans

```mermaid
Phase 1: Core/Priority → Phase 2: Expansion → Phase 3: Completion
```

**Key Principles:**
1. **Non-breaking changes** - New and old code coexist during migration
2. **Priority-driven** - Core/high-traffic components migrated first
3. **Gradual replacement** - No forced one-time migration
4. **Backward compatibility** - Old APIs temporarily retained

**Examples:**
- React Query: New pages use `useApiCache`, old pages keep `requestProtection.js`
- Strategy System: Mock functions kept as fallback during real indicator implementation
- Symbol Types: Deprecated functions issue warnings but still work

### 3.2 Factory Pattern for Extensibility

**Used in:** Strategy System, Futures Backtest, Composite Integration

```python
# Strategy Factory Example
class StrategyFactory:
    @classmethod
    def create(cls, strategy_type: str, params: Dict) -> IStrategy:
        # Factory creates strategy instance dynamically
        # New strategies only need registration, no engine modification
```

**Benefits:**
- Open-Closed Principle - open for extension, closed for modification
- Dynamic strategy registration via decorators
- Easy to add new strategies without touching core engine code

### 3.3 Interface Abstraction

**Used in:** Strategy System, Unified Engine

```python
# IStrategy Interface
class IStrategy(ABC):
    @abstractmethod
    def generate_signals(self, context: StrategyContext) -> List[Signal]:
        pass

    @abstractmethod
    def calculate_target_weights(self, context: StrategyContext) -> Dict[str, float]:
        pass
```

**Benefits:**
- Consistent API across all strategy types
- Testable with mock implementations
- Easy to swap implementations

### 3.4 Adapter Pattern for Integration

**Used in:** Composite Integration, Unified Engine

```python
# SignalAdapter
class SignalAdapter:
    @staticmethod
    def signals_to_vectorbt(ohlcv_index, signals_by_date):
        # Convert IStrategy signals to VectorBT format
```

```python
# FuturesResultAdapter
class FuturesResultAdapter:
    def to_daily_metrics_input(self, futures_result):
        # Convert futures results to performance module format
```

**Benefits:**
- Bridging incompatible interfaces
- Reusing existing modules without modification
- Clean separation of concerns

### 3.5 Mixed Architecture for Specialization

**Used in:** Futures Backtest, Composite Integration

**Principle:** Specialized components + shared modules

```
Specialized: Futures backtest engine (handles multipliers, margins)
    + Shared: Performance/Analytics modules (reused)
```

**Benefits:**
- Handles domain-specific logic properly
- Avoids reinventing the wheel
- Maintains consistency across systems

---

## 4. Refactoring Best Practices

### 4.1 Backward Compatibility

**Pattern:**
1. Create new parallel implementation
2. Mark old implementation as deprecated with warnings
3. Gradually migrate usage
4. Remove deprecated code in future version (e.g., v2.0)

**Example - Symbol Type Unification:**
```python
@_deprecated("get_futures_spec is deprecated, use get_spec_for_symbol")
def get_futures_spec(symbol: FuturesSymbol):
    # Warning issued but still works
```

**Timeline:**
- Immediately: Old functions work with warnings
- v1.6 (2 weeks): Start replacing call sites
- v2.0 (1 month): Remove deprecated functions

### 4.2 Test-Driven Refactoring

**Approach:**
1. Write comprehensive tests first
2. Implement changes
3. Ensure all tests pass
4. Add regression tests

**Coverage Examples:**
- Symbol Type Unification: 11 tests (Enum/string inputs, deprecation warnings)
- Futures Backtest: 102 tests (4 phases, 101 passing)
- React Query: Functional verification tests

**Test Pyramid:**
```
          ┌──────────────┐
          │   E2E Tests  │  Few critical flows
          ├──────────────┤
          │ Integration  │  Medium, API-level
          ├──────────────┤
          │  Unit Tests  │  Many, core logic
          └──────────────┘
```

### 4.3 Deprecation Warnings

**Implementation:**
```python
def _deprecated(message: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            warnings.warn(message, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

**Benefits:**
- Smooth transition period
- Developer awareness without breaking builds
- Clear migration path

### 4.4 Configuration-Driven Design

**Pattern:** Externalize parameters, allow runtime configuration

**Examples:**
- React Query: Cache presets (static: 1h, dynamic: 30s)
- Futures Backtest: Capital management mode (constant/floating)
- SRS Scoring: Configurable 5-dimension weights

**Benefits:**
- Easy experimentation
- A/B testing
- Environment-specific configurations

### 4.5 Clear Documentation

**Each refactoring plan includes:**
1. **Decision records** - What was decided and why
2. **Alternative analysis** - Options considered with trade-offs
3. **Implementation steps** - Phased approach
4. **Code examples** - Before/after comparisons
5. **Testing strategy** - How to verify
6. **Risk assessment** - Potential issues and mitigation

### 4.6 API Versioning Strategy

**Pattern:** New endpoints with unified router, keep old endpoints

```
New: /api/backtest/unified (auto-selects best mode)
Old: /api/backtest/run (legacy, forwards internally)
```

**Benefits:**
- Zero-breaking change for existing clients
- Gradual adoption of new features
- Future deprecation path clear

---

## 5. Refactoring Workflow Summary

### 5.1 Standard Refactoring Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│  1. Discovery & Analysis                                     │
│  - Identify problem (e.g., high maintenance cost)          │
│  - Explore alternatives                                     │
│  - Document decision with trade-offs                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Design & Planning                                        │
│  - Define phases (P0, P1, P2)                                │
│  - Specify dependencies (DAG)                               │
│  - Estimate effort and timeline                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Foundation (Phase 1)                                     │
│  - Build core components                                    │
│  - Write comprehensive tests                                │
│  - Establish backward compatibility layer                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Incremental Migration (Phase 2+)                         │
│  - Migrate high-priority components                          │
│  - Verify results (comparison testing)                      │
│  - Mark old code as deprecated                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  5. Validation & Cleanup                                     │
│  - Regression testing                                       │
│  - Performance verification                                  │
│  - Documentation updates                                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  6. Completion & Deprecation                                 │
│  - Remove deprecated code (scheduled)                       │
│  - Final report                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Common Patterns Across Plans

**Priority Definition:**
- P0: Core functionality, blocking issues
- P1: Important features, enhanced analysis
- P2: Extension features

**Dependency Management:**
- Strong dependency: Phase 2 requires Phase 1
- Weak dependency: Phase 5 can run in parallel with Phase 1-2

**Verification Standards:**
- Functional correctness (e.g., RSI calculation < 1% error vs TradingView)
- Performance benchmarks (e.g., 1000 points < 100ms)
- Test coverage (> 80% unit tests)

### 5.3 Risk Mitigation

**Common Risks:**
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-------------|
| Bugs from refactoring | Medium | High | Comprehensive testing, keep old code |
| Learning curve | Medium | Medium | Documentation + examples + code reviews |
| Performance regression | Low | Medium | Monitoring + performance tests |
| Missing edge cases | Medium | Medium | High test coverage + CI/CD enforcement |

### 5.4 Success Metrics

**Short-term (1 month):**
- Core components migrated
- No functional regression bugs
- Code reduction > 20%

**Medium-term (3 months):**
- Major components migrated
- API requests reduced > 30% (caching effect)
- Old code maintenance = 0

**Long-term (6 months):**
- Most components using new architecture
- Deprecation of legacy systems possible

---

## 6. Cross-Document Insights

### 6.1 Architectural Consistency

**Common Design Patterns:**
1. **Factory Pattern** - Strategy creation, Futures strategies
2. **Interface Abstraction** - IStrategy, IFuturesStrategy
3. **Adapter Pattern** - SignalAdapter, HedgedBacktestAdapter
4. **Progressive Migration** - React Query, Strategy System, Unified Engine

**Philosophy:**
- Backward compatibility is paramount
- New and old systems coexist during transition
- Clear deprecation path with warnings
- Comprehensive testing before removal

### 6.2 Technology Stack Decisions

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Frontend State | React Query (TanStack Query) | Built-in caching, deduplication, reduces boilerplate |
| Backtest Engine | VectorBT | Optimized indicators, concise API |
| Acceleration | Numba | 10-20x speedup for Bootstrap |
| API Layer | FastAPI | Async support, automatic validation |
| Database | DuckDB | Embedded, fast analytics, vector operations |

### 6.3 Modular Design Principles

**Separation of Concerns:**
- Core layer: IStrategy, VectorBT, ShadowTradingEngine, Analysis
- Indicator layer: IndicatorCalculator (RSI, MACD, SuperTrend)
- Strategy layer: RSIStrategy, MACDStrategy, SuperTrendStrategy
- Analysis layer: ReturnDistribution, SRS, Bootstrap
- Presentation layer: Frontend components, API endpoints, Dashboard

**Dependency Flow:**
```
Foundation → Indicators → Strategies → Analysis → Presentation
```

---

## 7. Recommendations

### 7.1 Immediate Actions

1. **Continue React Query Migration** - Phase 1 core pages (2-3 weeks)
2. **Implement Indicator Calculator** - Foundation for all signal strategies (2-3 days)
3. **Migrate Signal Strategies** - Phase 2 with real indicators (3-4 days)

### 7.2 Medium-term Priorities

1. **Implement Return Distribution** - Phase 3 initial analysis (2-3 days)
2. **Build SRS Scoring System** - Phase 4 5-dimensional evaluation (3-4 days)
3. **Develop Bootstrap Analysis** - Phase 5 advanced analytics with Numba (2-3 days)

### 7.3 Long-term Planning

1. **Remove deprecated code** - After migration complete (v2.0 timeline)
2. **Standardize on unified backtest engine** - Phase out Backtrader where appropriate
3. **Extend futures system** - Add more strategies (RSI_LongOnly, Breakout, etc.)

### 7.4 Process Improvements

1. **Establish refactoring standards** - Based on patterns in these documents
2. **Create refactoring templates** - For common patterns (progressive migration, factory pattern)
3. **Document decision process** - Keep trade-off analysis for all major decisions
4. **Automate regression testing** - CI/CD enforcement for test coverage

---

## 8. Confidence & Limitations

### 8.1 Confidence Level: **High**

**Reasons:**
- Documents are comprehensive and well-structured
- Clear decision records with trade-off analysis
- Concrete implementation details with code examples
- Test strategies and success metrics defined
- Status markers showing implementation progress

### 8.2 Data Quality: **Excellent**

**Assessment:**
- 6 complete refactoring plans analyzed
- All documents include clear objectives, scope, and methodology
- Technical details are specific and actionable
- Testing and verification standards are explicit
- Timeline and effort estimates are provided

### 8.3 Assumptions Made

1. **ARCH-001 to ARCH-008 format**: Task mentioned these specific document codes, but found actual documents with different naming conventions
2. **Phase documents**: Task mentioned phase1, phase2, phase3 documents, but these appear to be integrated within comprehensive architecture documents rather than separate files
3. **Archive directory**: Checked archive folder but it appears the architecture documents in `/current/` are the active ones, with historical phase information embedded within them

### 8.4 Limitations

1. **Cannot execute shell commands**: Tool limitations prevented using `find` or `ls` to discover additional files
2. **Archive access**: Could not fully explore `/Users/charlie/Dashboard/docs/architecture/archive/` directory
3. **File system exploration**: Limited to reading specific known file paths
4. **Missing context**: No access to task-001 through task-015 mentioned in docs structure

### 8.5 What This Analysis Cannot Address

- Historical context for refactoring decisions (why certain alternatives were chosen)
- Implementation progress beyond documented status
- Team feedback or lessons learned during implementation
- Integration with external systems or dependencies
- Business justification or ROI analysis

---

## 9. Metadata

**Analysis Framework:** Refactoring Pattern Analysis + Architecture Review

**Key Themes Identified:**
1. Progressive migration (all documents)
2. Backward compatibility (all documents)
3. Factory pattern (Strategy, Futures systems)
4. Interface abstraction (IStrategy, IFuturesStrategy)
5. Adapter pattern (SignalAdapter, FuturesResultAdapter)
6. Test-driven approach (comprehensive test coverage)
7. Documentation-driven design (decision records, trade-offs)

**Success Factors:**
- Clear phasing with priorities (P0, P1, P2)
- Concrete acceptance criteria
- Risk mitigation strategies
- Success metrics at multiple time horizons
- Code examples for clarity

**Suggestions for Creative Work:**
- Create refactoring playbook based on these patterns
- Develop automated refactoring detection tools
- Build visual migration progress dashboards
- Create training materials for team onboarding
- Establish refactoring decision template

---

**End of Analysis**

*Generated by Charlie Analyst*
*Input: 6 architecture documents from Dashboard project*
*Date: 2026-02-21*
