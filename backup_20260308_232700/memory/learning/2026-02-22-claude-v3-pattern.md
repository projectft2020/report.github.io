# Claude Sonnet 4.5 開發 Market Score V3 的模式學習

**學習時間：** 2026-02-22 04:15 AM
**貢獻者：** Claude Sonnet 4.5 <noreply@anthropic.com>
**項目：** Matrix Dashboard - Market Score V3 策略

---

## 📊 Git 提交概覽

### 提交時間線

```
1275ecf - feat(weighting): add Linear Momentum weighting method
  ↓
0a5ba1a - feat(market-score-v3): add MS V3 strategy with tests
  ↓  
11d0c68 - feat(dual-market): add Dual Market Confirm strategy
  ↓
a0f6e22 - feat(strategy-symbol-match): add Strategy Symbol Match feature
  ↓
7fac5ff - refactor(prediction-momentum): restructure into module
  ↓
6a8b015 - chore(config): register new strategies and routes
```

### 總體變更統計

- **新增文件：** 15+ 個
- **新增代碼：** ~10,000+ 行
- **測試覆蓋：** 28 個測試用例（MS V3）
- **文檔完整度：** 100%（API 文檔 + 代碼注釋）

---

## 🎯 核心開發模式

### 1. 策略實現模式（Strategy Implementation）

#### 文件結構
```
backend/services/strategies/implementations/
├── market_score_v3_strategy.py       (466 lines)
└── test_market_score_v3_strategy.py  (551 lines)
```

#### 代碼組織

**1. 模塊級文檔字符串（Module Docstring）**
```python
"""
Market Score V3 Strategy

Four-confirmation position sizing strategy:
- 100% position: TW Score > 50 AND US Score > 50 AND 0050.TW > 120MA AND QQQ > 20MA
- 0% position: TW Score < 40 OR US Score < 40 OR 0050.TW < 120MA OR QQQ < 20MA
- 50% position: Otherwise (default)

Portfolio: 50% QQQ + 50% 0050.TW
"""
```

**2. 類級文檔字符串（Class Docstring）**
```python
class MarketScoreV3Strategy(IStrategy):
    """
    Market Score V3 Strategy with Four Confirmations.

    Entry Conditions (100% position):
        1. TW Market Score > 50
        2. US Market Score > 50
        3. 0050.TW price > 120MA
        4. QQQ price > 20MA

    Exit Conditions (0% position):
        1. TW Market Score < 40
        2. US Market Score < 40
        3. 0050.TW price < 120MA
        4. QQQ price < 20MA

    Otherwise: 50% position

    Portfolio: 50% QQQ + 50% 0050.TW
    """
```

**3. 類常量（Class Constants）**
```python
# Fixed portfolio weights
PORTFOLIO = {
    'QQQ': 0.5,
    '0050.TW': 0.5,
}
```

**4. 初始化方法（__init__）**
```python
def __init__(
    self,
    name: str = "Market Score V3",
    tw_etf: str = '0050.TW',
    us_etf: str = 'QQQ',
    tw_ma_period: int = 120,
    us_ma_period: int = 20,
    execution_mode: ExecutionMode = ExecutionMode.NEXT_OPEN,
):
    super().__init__(name, StrategyType.SIGNAL_BASED, execution_mode)
    
    # Validate
    if tw_ma_period <= 0 or us_ma_period <= 0:
        raise ValueError("MA periods must be positive")
    
    # Cache for data and scores
    self._conn = None
    self._price_cache: Dict[str, pd.DataFrame] = {}
    self._ma_cache: Dict[str, pd.Series] = {}
    self._score_cache: Dict[str, Optional[float]] = {}
    self._last_calculation_date: Optional[date] = None
    
    # Current position state (0.0, 0.5, or 1.0)
    self._current_position_size = 0.0
```

**5. 私有輔助方法（Private Helper Methods）**
```python
def _get_db_conn(self):
    """Get database connection."""
    ...

def _load_prices(self, symbol: str, start_date: date, end_date: date) -> pd.DataFrame:
    """Load price data for symbol."""
    ...

def _calculate_ma(self, symbol: str, ma_period: int, market_date: date) -> Optional[float]:
    """Calculate MA value for symbol."""
    ...
```

**6. 公共方法（Public Methods - IStrategy Interface）**
```python
def generate_signal(self, context: ExecutionContext) -> SignalList:
    """Generate trading signals."""
    ...

def execute_trade(self, signal: StrategySignal, context: ExecutionContext) -> bool:
    """Execute trade."""
    ...

def get_position_state(self, context: ExecutionContext) -> PositionState:
    """Get current position state."""
    ...
```

---

### 2. 測試模式（Test Pattern）

#### 測試文件結構
```python
"""
Tests for Market Score V3 Strategy
"""

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import Mock, patch
import pandas as pd
import numpy as np

from database import get_db
from routers.market_score_v3 import (
    _calculate_position_by_methodology,
    _get_trade_reason,
    _calculate_benchmark
)
```

#### 測試組織結構

**1. Test Fixtures（測試夾具）**
```python
@pytest.fixture
def mock_strategy():
    """Create a mock MarketScoreV3Strategy"""
    strategy = Mock()
    
    # Mock market score calculations
    strategy.tw_etf = "0050.TW"
    strategy.us_etf = "QQQ"
    strategy.tw_ma_period = 120
    strategy.us_ma_period = 20
    
    def mock_calculate_market_score(symbol, period, date):
        scores = {
            ("0050.TW", 120): {"2023-01-01": 65, "2023-01-02": 66},
            ("QQQ", 20): {"2023-01-01": 58, "2023-01-02": 59}
        }
        return scores.get((symbol, period), {}).get(str(date))
    
    strategy._calculate_market_score = mock_calculate_market_score
    
    return strategy
```

**2. 測試類組織（Test Class Organization）**
```python
class TestSingleMethodology:
    """Tests for single methodology selection"""
    
    def test_all_methodology_4_confirmations(self, mock_strategy):
        """Test 'all' methodology with 4 confirmations"""
        ...
    
    def test_tw_score_methodology(self, mock_strategy):
        """Test TW Score > 50 methodology"""
        ...

class TestMultipleMethodologies:
    """Tests for multiple methodology voting"""
    
    def test_2_methods_voting(self, mock_strategy):
        """Test 2 methods voting (50% each)"""
        ...
    
    def test_3_methods_voting(self, mock_strategy):
        """Test 3 methods voting (33.3% each)"""
        ...
```

**3. 測試覆蓋類型（Test Coverage Types）**

| 類型 | 測試內容 | 示例 |
|------|---------|------|
| **單一方法論** | 單個確認條件的邏輯 | `test_tw_score_methodology` |
| **多方法論投票** | 多個確認條件的投票機制 | `test_2_methods_voting` |
| **交易原因生成** | 交易理由的字串格式化 | `test_trade_reason_single_method` |
| **API 端點集成** | 路由端點的端到端測試 | `test_backtest_api_integration` |
| **基準計算** | Buy & Hold 基準的計算 | `test_benchmark_calculation` |
| **邊界情況** | 極端值和錯誤處理 | `test_edge_case_none_score` |
| **性能測試** | 大數據量的性能表現 | `test_large_backtest_performance` |

---

### 3. API 端點模式（API Endpoint Pattern）

#### 路由文件結構
```
backend/routers/market_score_v3.py
├── Module Docstring (NumPy-style API 文檔)
├── Imports
├── Router Definition
├── Endpoint Functions
└── Helper Functions
```

#### 模塊級文檔（NumPy-style API 文檔）

**特點：**
- 放在文件頂部（導入之前）
- 使用 NumPy 風格的文檔格式
- 包含完整的 API 文檔（參數、返回值、示例）

**結構：**
```python
"""
Market Score V3 Strategy API Endpoints

================================================================================
API Endpoint: POST /api/market-score-v3/backtest
================================================================================

Description:
    Run backtest for Market Score V3 strategy with flexible methodology selection.

    Supports both single methodology and multiple methodologies (voting system).

Query Parameters:
    ---------------
    start_date : str [required]
        Start date in YYYY-MM-DD format

    end_date : str [required]
        End date in YYYY-MM-DD format

    initial_capital : float [optional, default=100000]
        Initial capital for backtesting

    tw_weight : float [optional, default=0.5]
        Taiwan ETF weight (0-1). Only used in dual mode.

    us_weight : float [optional, default=0.5]
        US ETF weight (0-1). Only used in dual mode.

    tw_etf : str [optional, default="0050.TW"]
        Taiwan ETF symbol for trading

    us_etf : str [optional, default="QQQ"]
        US ETF symbol for trading

    single_mode : bool [optional, default=False]
        If True, trade only us_etf (single commodity mode)
        If False, trade both tw_etf and us_etf (dual mode)

    methodology : str [optional, default="all"]
        Strategy methodology(ies). Can be single or comma-separated list.

        Single Methodology Options:
        - "all": ALL (4 Confirmations) - Progressive position (0%, 25%, 50%, 75%, 100%)
        - "tw_score": TW Market Score > 50
        - "us_score": US Market Score > 50
        - "tw_ma": 0050.TW Price > 120MA
        - "us_ma": QQQ Price > 20MA
        - "tw_score_ma": TW Score > TW Score's 120MA
        - "us_score_ma": US Score > US Score's 20MA

        Multiple Methodologies (comma-separated):
        - "tw_ma,us_ma": 2 methods, each votes 50%
        - "tw_ma,us_ma,tw_score": 3 methods, each votes 33.3%
        - "tw_ma,us_ma,tw_score,us_score": 4 methods, each votes 25%

        When multiple methodologies are specified:
        - Each method votes YES (1) or NO (0) for position
        - Final position = (YES votes / Total votes) × 100%
        - Example: 2 methods, both YES → 100%, 1 of 2 YES → 50%

Response Format:
    -------------
    {
        "summary": {...},
        "position_stats": {...},
        "equity_curve": [...],
        "benchmark_curve": [...],
        "return_series": [...],
        "drawdown_curve": [...],
        "positions": [...],
        "trades": [...],
        "returns_by_period": {...}
    }

Example Requests:
    ---------------
    # 1. Basic backtest (default: ALL 4 confirmations)
    POST /api/market-score-v3/backtest?start_date=2023-01-01&end_date=2024-01-01

    # 2. Single methodology - TW MA only
    POST /api/market-score-v3/backtest?start_date=2023-01-01&end_date=2024-01-01&methodology=tw_ma

    # 3. Multiple methodologies - 2 methods voting
    POST /api/market-score-v3/backtest?start_date=2023-01-01&end_date=2024-01-01&methodology=tw_ma,us_ma
...
"""
```

#### 端點函數結構

```python
@router.post("/backtest")
async def run_backtest(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    initial_capital: float = Query(100000, description="Initial capital"),
    tw_weight: float = Query(0.5, description="Taiwan ETF weight (0-1)"),
    us_weight: float = Query(0.5, description="US ETF weight (0-1)"),
    tw_etf: str = Query("0050.TW", description="Taiwan ETF symbol"),
    us_etf: str = Query("QQQ", description="US ETF symbol"),
    single_mode: bool = Query(False, description="Single commodity mode"),
    methodology: str = Query("all", description="Strategy methodology"),
    conn: duckdb.DuckDBPyConnection = Depends(get_db)
):
    """
    Run backtest for Market Score V3 strategy.

    This endpoint supports both single and multiple methodology selection:
    - Single: Use one strategy methodology
    - Multiple: Combine methodologies through voting (each method votes 0% or 100%)
    
    [參數說明...]
    
    Returns:
    --------
    dict
        Backtest results containing:
        - summary: Performance metrics
        - position_stats: Days spent at each position level
        - equity_curve: Daily portfolio values
        - benchmark_curve: Daily benchmark values
        - return_series: Daily NAV data for monthly returns calculation
        - drawdown_curve: Daily drawdown percentages
        - positions: Daily position details
        - trades: List of all trades with reasons
        - returns_by_period: Monthly and yearly returns
    """
    # 實現...
```

---

### 4. 註冊模式（Registration Pattern）

#### Factory 註冊（backend/services/strategies/factory.py）

**1. 導入策略類**
```python
from .implementations.market_score_v3_strategy import MarketScoreV3Strategy
```

**2. 註冊到類型映射**
```python
class StrategyFactory:
    # Strategy type registry (lowercase name -> class)
    _registry: Dict[str, Type[IStrategy]] = {
        ...
        "market_score_v3": MarketScoreV3Strategy,
        "market_score_v3_strategy": MarketScoreV3Strategy,
    }
```

**3. 添加默認參數**
```python
_default_params: Dict[str, Dict[str, Any]] = {
    ...
    "market_score_v3": {
        "tw_etf": "0050.TW",
        "us_etf": "QQQ",
        "tw_ma_period": 120,
        "us_ma_period": 20,
    },
}
```

#### Router 註冊（backend/main.py）

**1. 導入路由**
```python
from routers import market_score_v3 as market_score_v3_router
```

**2. 註冊到 FastAPI 應用**
```python
app.include_router(market_score_v3_router.router)  # Market Score V3
```

#### Frontend 註冊

**1. 導入頁面組件（frontend/src/App.jsx）**
```javascript
const MarketScoreV3Page = React.lazy(() => import('./pages/MarketScoreV3Page.jsx'));
```

**2. 添加路由**
```javascript
<Route 
  path="/market-score-v3" 
  element={
    <AdminRoute isEnabled={pageConfig.market_score_v3} configLoaded={configLoaded}>
      <MarketScoreV3Page />
    </AdminRoute>
  } 
/>
```

**3. 添加導航菜單（frontend/src/components/DashboardLayout.jsx）**
```javascript
{/* 4. AI Strategy */}
<SidebarGroup
    title="AI Strategy"
    icon="bi-robot"
    isOpen={groupsOpen.ai_strategy}
    onToggle={() => toggleGroup('ai_strategy')}
    isSidebarCollapsed={isSidebarCollapsed}
>
    {isAdminUser && (
        <li className={styles['nav-item']}>
            <NavLink to="/market-score-v3">
                <i className="bi bi-graph-up-arrow me-2"></i> 
                <span>Market Score V3</span>
            </NavLink>
        </li>
    )}
</SidebarGroup>
```

---

## 🎨 代碼風格和最佳實踐

### 1. 文檔字符串（Docstrings）

**三層級文檔：**
- **模塊級：** 功能概述、API 文檔（NumPy-style）
- **類級：** 策略邏輯、進出場條件、投資組合
- **方法級：** 參數、返回值、異常、示例

**示例：**
```python
def _load_prices(self, symbol: str, start_date: date, end_date: date) -> pd.DataFrame:
    """
    Load price data for symbol.
    
    Args:
        symbol: Stock symbol (e.g., "QQQ", "0050.TW")
        start_date: Start date for price data
        end_date: End date for price data
    
    Returns:
        DataFrame with 'trade_date' and 'close' columns
    
    Raises:
        ValueError: If symbol is invalid
    """
    ...
```

### 2. 類型提示（Type Hints）

**全面使用類型提示：**
```python
from typing import Dict, List, Optional, Tuple, Any

def _calculate_position_by_methodology(
    strategy: Mock,
    market_date: date,
    methodologies: List[str]
) -> float:
    ...
```

### 3. 錯誤處理（Error Handling）

**優雅的錯誤處理：**
```python
try:
    conn = self._get_db_conn()
    df = conn.execute(query, [symbol, start_date, end_date]).fetchdf()
    
    if df.empty:
        logger.warning(f"No price data for {symbol}")
        return pd.DataFrame()
    
    return df
    
except Exception as e:
    logger.error(f"Error loading prices for {symbol}: {e}")
    return pd.DataFrame()
```

### 4. 緩存機制（Caching）

**智能緩存：**
```python
# Cache for data and scores
self._conn = None
self._price_cache: Dict[str, pd.DataFrame] = {}
self._ma_cache: Dict[str, pd.Series] = {}
self._score_cache: Dict[str, Optional[float]] = {}
self._last_calculation_date: Optional[date] = None
```

### 5. 日誌記錄（Logging）

**分級日誌：**
```python
logger.info(f"Backtest completed: {len(equity_curve)} days")
logger.warning(f"Insufficient data for {symbol}")
logger.error(f"Error loading prices for {symbol}: {e}")
```

---

## 📋 開發流程總結

### 階段 1：策略實現

1. **創建策略類**
   - 繼承 `IStrategy`
   - 實現核心方法
   - 添加文檔字符串
   - 類型提示和錯誤處理

2. **編寫測試**
   - 創建 test fixtures
   - 測試各個方法論
   - 測試邊界情況
   - 測試 API 集成

3. **創建示例腳本**
   - `tools/backtest_dual_market_strategy.py`
   - `tools/run_dual_market_strategy.py`
   - `tools/simple_backtest_dual_market.py`

### 階段 2：API 開發

1. **創建路由文件**
   - NumPy-style API 文檔
   - 端點函數
   - 輔助函數

2. **註冊到 main.py**
   - 導入路由
   - `app.include_router()`

### 階段 3：前端開發

1. **創建頁面組件**
   - `frontend/src/pages/MarketScoreV3Page.jsx`

2. **註冊路由**
   - `App.jsx` 添加 Route

3. **添加導航**
   - `DashboardLayout.jsx` 添加菜單項

### 階段 4：系統註冊

1. **Factory 註冊**
   - 導入策略類
   - 添加到 `_registry`
   - 添加到 `_default_params`

2. **提交代碼**
   - 結構清晰的提交消息
   - "Co-Authored-By: Claude Sonnet 4.5"

---

## 🎯 關鍵收穫

### 1. 文檔驅動開發
- API 文檔先於實現
- NumPy-style 文檔格式
- 示例即文檔

### 2. 測試驅動開發
- 28 個測試用例
- Mock 和 fixture 使用
- 邊界情況覆蓋

### 3. 模塊化設計
- 策略實現 → 測試 → API → 前端 → 註冊
- 每層獨立可測
- 清晰的職責分離

### 4. 類型安全和錯誤處理
- 全面類型提示
- 優雅的錯誤處理
- 分級日誌記錄

### 5. 緩存和性能優化
- 智能緩存機制
- 減少數據庫查詢
- 性能測試覆蓋

---

## 🔑 實用模式清單

### 策略實現模式
- [x] 三層級文檔字符串（模塊/類/方法）
- [x] 類常量定義（PORTFOLIO）
- [x] 私有輔助方法（_load_prices, _calculate_ma）
- [x] 緩存機制（_price_cache, _ma_cache）
- [x] 類型提示（Type Hints）
- [x] 錯誤處理和日誌記錄

### 測試模式
- [x] Test Fixtures（mock_strategy）
- [x] 測試類組織（TestSingleMethodology）
- [x] 多種測試類型（單一/多方法論/集成/性能）
- [x] Mock 和 Patch 使用
- [x] 邊界情況測試

### API 端點模式
- [x] NumPy-style API 文檔（模塊頂部）
- [x] Query 參數驗證和描述
- [x] FastAPI Depends 依賴注入
- [x] 詳細的返回值格式文檔
- [x] 示例請求和響應

### 註冊模式
- [x] Factory 註冊（_registry + _default_params）
- [x] Router 註冊（main.py）
- [x] Frontend 註冊（App.jsx + DashboardLayout.jsx）
- [x] 路由守護（AdminRoute）

---

**下一步：** 應用此模式開發新的策略或功能
