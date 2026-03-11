# Dashboard 開發標準模板

**版本:** v1.0
**基於:** Market Score V3 開發模式
**最後更新:** 2026-02-22

---

## 📋 目錄

1. [開發流程標準](#開發流程標準)
2. [代碼組織結構](#代碼組織結構)
3. [代碼撰寫規範](#代碼撰寫規範)
4. [測試撰寫規範](#測試撰寫規範)
5. [API 端點規範](#api-端點規範)
6. [前端組件規範](#前端組件規範)
7. [系統註冊規範](#系統註冊規範)
8. [質量檢查清單](#質量檢查清單)

---

## 開發流程標準

### 完整開發流程

```
階段 1: 策略實現
├── 創建策略類（[strategy_name]_strategy.py）
│   ├── 繼承 IStrategy
│   ├── 實現核心方法
│   ├── 添加文檔字符串（三層級）
│   └── 類型提示和錯誤處理
├── 編寫測試（test_[strategy_name].py）
│   ├── Test fixtures
│   ├── 各個方法論測試
│   ├── 邊界情況測試
│   └── API 集成測試
└── 創建示例腳本（tools/*.py）

階段 2: API 開發
├── 創建路由文件（[router_name].py）
│   ├── NumPy-style API 文檔
│   ├── 端點函數
│   └── 輔助函數
└── 註冊到 main.py

階段 3: 前端開發
├── 創建頁面組件（[FeatureName]Page.jsx）
├── 註冊路由
└── 添加導航菜單

階段 4: 系統註冊
├── Factory 註冊（_registry + _default_params）
└── 提交代碼
```

### 每個階段的交付物

| 階段 | 交付物 | 數量 |
|-----|--------|------|
| 階段 1 | 策略實現文件 | 1 |
| 階段 1 | 測試文件 | 1+ |
| 階段 1 | 示例腳本 | 0+ |
| 階段 2 | API 路由文件 | 1 |
| 階段 3 | 前端頁面組件 | 1+ |
| 階段 4 | Factory 註冊 | 1 |

---

## 代碼組織結構

### Backend 結構

```
backend/
├── services/
│   ├── strategies/
│   │   ├── core/
│   │   │   └── interface.py                    # IStrategy 接口
│   │   ├── implementations/
│   │   │   └── [strategy_name]_strategy.py       # 策略實現
│   │   ├── indicators/
│   │   │   └── indicator_calculator.py         # 指標計算器
│   │   ├── signal_strategies/
│   │   │   └── [strategy_name].py                # 信號策略
│   │   ├── params/
│   │   │   └── [param_name].py                  # 參數定義
│   │   └── __init__.py                          # Factory 註冊
│   └── market_thermometer_service.py            # 市場溫度計服務
├── routers/
│   └── strategies/
│       └── [router_name].py                     # API 路由
└── tests/
    ├── services/
    │   └── strategies/
    │       └── test_[strategy_name].py          # 策略測試
    └── routers/
        └── strategies/
            └── test_[router_name].py            # API 測試
```

### Frontend 結構

```
frontend/
├── src/
│   ├── pages/
│   │   └── [FeatureName]Page.jsx                # 頁面組件
│   ├── components/
│   │   └── [ComponentName].jsx                  # 子組件
│   ├── hooks/
│   │   └── use[FeatureName].js                 # 自定義 Hook
│   └── utils/
│       └── [utilName].js                       # 工具函數
├── App.jsx                                     # 路由註冊
└── components/
    └── DashboardLayout.jsx                     # 導航菜單
```

---

## 代碼撰寫規範

### 三層級文檔字符串

#### 層級 1: 模塊級文檔（NumPy-style API 文檔）

```python
"""
================================================================================
[Strategy Name] Strategy API Endpoints
================================================================================

API Endpoint: POST /api/[route-name]/backtest

Description:
    [策略描述，1-2 句話]

Query Parameters:
    ---------------
    start_date : str [required]
        Start date in YYYY-MM-DD format

    end_date : str [required]
        End date in YYYY-MM-DD format

    param1 : float [optional, default=X.X]
        Parameter 1 description

    param2 : int [optional, default=N]
        Parameter 2 description

Response Format:
    {
        "summary": {
            "initial_capital": float,
            "final_equity": float,
            "total_return": float,
            "total_return_pct": float,
            "sharpe_ratio": float,
            "max_drawdown": float,
            "max_drawdown_pct": float,
            "num_trades": int,
            "start_date": str,
            "end_date": str,
            "trading_days": int
        },
        "equity_curve": [...],
        "trades": [...]
    }

Example Requests:
    ---------------
    POST /api/[route-name]/backtest?start_date=2023-01-01&end_date=2024-01-01
    POST /api/[route-name]/backtest?param1=1.5&param2=10

Error Codes:
    -----------
    INVALID_DATE_FORMAT - 日期格式錯誤
    INVALID_DATE_RANGE - 日期範圍錯誤
    INVALID_PARAM1 - 參數 1 無效

================================================================================
"""
```

#### 層級 2: 類級文檔（策略邏輯）

```python
class NewStrategy(IStrategy):
    """
    [Strategy Name] - [策略簡短描述]

    實現方式：
    - [實現細節 1]
    - [實現細節 2]

    核心邏輯：
    - [核心邏輯 1]
    - [核心邏輯 2]

    驗收標準：
    - [標準 1]
    - [標準 2]

    性能要求：
    - [性能要求]
    """
```

#### 層級 3: 方法級文檔（參數/返回值）

```python
def calculate_position(
    self,
    param1: float,
    param2: int,
    context: ExecutionContext
) -> Tuple[float, str]:
    """
    計算倉位大小

    Args:
        param1: 參數 1 說明
        param2: 參數 2 說明
        context: 執行上下文

    Returns:
        (position_size, reason): 倉位大小 (0.0-1.0) 和原因說明

    Raises:
        ValueError: 如果參數無效
    """
```

### 類型提示規範

#### 函數類型提示

```python
from typing import Dict, List, Optional, Tuple, Union
from datetime import date

def calculate_position(
    param1: float,
    param2: Optional[int] = None,
    context: ExecutionContext = None
) -> Tuple[float, str]:
    """計算倉位大小"""
    pass

def get_signals(
    symbols: List[str],
    dates: List[date]
) -> Dict[str, List[float]]:
    """獲取信號"""
    pass

def process_data(
    data: Union[pd.DataFrame, List[Dict]]
) -> Optional[pd.DataFrame]:
    """處理數據"""
    pass
```

#### Dataclass 類型提示

```python
from dataclasses import dataclass
from typing import TypedDict

@dataclass
class StrategyParams:
    """策略參數"""
    param1: float
    param2: int
    param3: Optional[str] = None

class BacktestSummary(TypedDict):
    initial_capital: float
    final_equity: float
    total_return: float
    total_return_pct: float
    sharpe_ratio: float
    max_drawdown: float
    max_drawdown_pct: float
    num_trades: int
    start_date: str
    end_date: str
    trading_days: int
```

### 錯誤處理規範

#### 優雅錯誤處理

```python
import logging

logger = logging.getLogger(__name__)

def load_data(symbol: str, start_date: date, end_date: date) -> pd.DataFrame:
    """
    載入數據

    Args:
        symbol: 股票代碼
        start_date: 開始日期
        end_date: 結束日期

    Returns:
        數據 DataFrame，如果失敗返回空 DataFrame
    """
    try:
        data = self._loader.load(symbol, start_date, end_date)
        return data
    except FileNotFoundError as e:
        logger.error(f"Data not found for {symbol}: {e}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Failed to load data for {symbol}: {e}")
        return pd.DataFrame()

def calculate_score(symbol: str) -> float:
    """
    計算分數

    Args:
        symbol: 股票代碼

    Returns:
        分數 (0-100)，如果失敗返回 0.0
    """
    try:
        data = load_data(symbol)
        if data.empty:
            return 0.0

        # 計算邏輯...
        return score
    except Exception as e:
        logger.warning(f"Failed to calculate score for {symbol}: {e}")
        return 0.0
```

#### 驗證和異常拋出

```python
def validate_params(param1: float, param2: int) -> None:
    """
    驗證參數

    Args:
        param1: 參數 1
        param2: 參數 2

    Raises:
        ValueError: 如果參數無效
    """
    if param1 < 0:
        raise ValueError(f"param1 must be >= 0, got {param1}")

    if param2 <= 0:
        raise ValueError(f"param2 must be > 0, got {param2}")

def calculate_with_validation(param1: float, param2: int) -> float:
    """帶驗證的計算"""
    try:
        validate_params(param1, param2)
        # 計算邏輯...
        return result
    except ValueError as e:
        logger.error(f"Parameter validation failed: {e}")
        raise
```

### 智能緩存機制

```python
from typing import Dict, Tuple
from datetime import date, timedelta

class CachedStrategy:
    """帶緩存的策略"""

    def __init__(self):
        # 緩存字典
        self._price_cache: Dict[Tuple[str, date, date], pd.DataFrame] = {}
        self._ma_cache: Dict[Tuple[str, int, date], float] = {}
        self._score_cache: Dict[Tuple[str, date], float] = {}

    def load_prices(
        self,
        symbol: str,
        start_date: date,
        end_date: date
    ) -> pd.DataFrame:
        """載入價格（帶緩存）"""
        cache_key = (symbol, start_date, end_date)

        if cache_key in self._price_cache:
            return self._price_cache[cache_key]

        try:
            prices = self._loader.load(symbol, start_date, end_date)
            self._price_cache[cache_key] = prices
            return prices
        except Exception as e:
            logger.error(f"Failed to load prices for {symbol}: {e}")
            return pd.DataFrame()

    def calculate_ma(
        self,
        symbol: str,
        period: int,
        market_date: date
    ) -> float:
        """計算移動平均線（帶緩存）"""
        cache_key = (symbol, period, market_date)

        if cache_key in self._ma_cache:
            return self._ma_cache[cache_key]

        prices = self.load_prices(
            symbol,
            market_date - timedelta(days=period * 2),
            market_date
        )

        if prices.empty:
            ma_value = 0.0
        else:
            ma_value = prices['close'].tail(period).mean()

        self._ma_cache[cache_key] = ma_value
        return ma_value

    def clear_cache(self) -> None:
        """清除所有緩存"""
        self._price_cache.clear()
        self._ma_cache.clear()
        self._score_cache.clear()
        logger.debug("Cache cleared")
```

### 日誌記錄規範

```python
import logging

logger = logging.getLogger(__name__)

class LoggedStrategy:
    """帶日誌的策略"""

    def backtest(self, start_date: str, end_date: str) -> BacktestResponse:
        """執行回測"""
        logger.info(f"Starting backtest: {start_date} to {end_date}")

        try:
            # 回測邏輯...
            logger.info(f"Backtest completed: {len(equity_curve)} days")
            logger.debug(f"Final equity: {final_equity:.2f}")
            return result

        except Exception as e:
            logger.error(f"Backtest failed: {e}")
            raise

    def generate_signals(self, data: pd.DataFrame) -> List[Signal]:
        """生成信號"""
        logger.debug(f"Generating signals for {len(data)} data points")

        signals = []

        for i, row in data.iterrows():
            # 記錄關鍵決策
            if row['condition1']:
                logger.debug(f"{row['date']}: Condition 1 met ✓")
            else:
                logger.debug(f"{row['date']}: Condition 1 not met ✗")

            # 信號生成邏輯...
            signal = self._generate_signal(row)
            signals.append(signal)

        logger.info(f"Generated {len(signals)} signals")
        return signals
```

---

## 測試撰寫規範

### 測試文件結構

```python
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date, timedelta
import pandas as pd

from backend.services.strategies.implementations.new_strategy import NewStrategy
from backend.services.strategies.core.interface import ExecutionContext

# ===== Fixtures =====

@pytest.fixture
def strategy():
    """創建策略實例"""
    return NewStrategy(name="Test Strategy")

@pytest.fixture
def mock_context():
    """創建模擬上下文"""
    context = Mock(spec=ExecutionContext)
    context.current_time = datetime.now()
    context.portfolio_value = 100000.0
    context.cash = 100000.0
    context.positions = {}
    return context

@pytest.fixture
def mock_prices():
    """創建模擬價格數據"""
    dates = pd.date_range(start='2023-01-01', periods=250, freq='D')
    prices = pd.DataFrame({
        'open': range(100, 350),
        'high': range(101, 351),
        'low': range(99, 349),
        'close': range(100, 350),
        'volume': range(1000000, 1250000, 1000)
    }, index=dates)
    return prices

# ===== 測試類 =====

class TestNewStrategy:
    """新策略測試"""

    def test_init(self, strategy):
        """測試初始化"""
        assert strategy.name == "Test Strategy"
        # 更多斷言...

    def test_calculate_position(self, strategy):
        """測試倉位計算"""
        position_size, reason = strategy.calculate_position(
            param1=1.0,
            param2=10
        )
        assert 0.0 <= position_size <= 1.0
        assert isinstance(reason, str)

    def test_edge_case_empty_data(self, strategy):
        """測試邊界情況：空數據"""
        result = strategy.process_data(pd.DataFrame())
        assert result == 0.0

    def test_error_handling(self, strategy):
        """測試錯誤處理"""
        with patch.object(strategy, '_load_data', side_effect=Exception("Test error")):
            result = strategy.calculate_score("INVALID")
            # 應該返回默認值而不是拋出異常
            assert result == 0.0

class TestNewStrategyAPI:
    """新策略 API 測試"""

    @pytest.fixture
    def client(self):
        """創建測試客戶端"""
        from fastapi.testclient import TestClient
        from main import app
        return TestClient(app)

    def test_backtest_success(self, client):
        """測試：成功回測"""
        response = client.post(
            "/api/new-strategy/backtest",
            params={
                "start_date": "2023-01-01",
                "end_date": "2024-01-01"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data

    def test_backtest_invalid_date_format(self, client):
        """測試：無效日期格式"""
        response = client.post(
            "/api/new-strategy/backtest",
            params={
                "start_date": "2023/01/01",  # 錯誤格式
                "end_date": "2024-01-01"
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "INVALID_DATE_FORMAT"

    def test_backtest_invalid_param(self, client):
        """測試：無效參數"""
        response = client.post(
            "/api/new-strategy/backtest",
            params={
                "start_date": "2023-01-01",
                "end_date": "2024-01-01",
                "param1": -1.0  # 無效值
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "INVALID_PARAM1"
```

### 測試覆蓋率要求

| 測試類型 | 覆蓋率要求 |
|---------|----------|
| 行覆蓋率 | > 85% |
| 分支覆蓋率 | > 80% |
| 函數覆蓋率 | 100% |

---

## API 端點規範

### API 路由文件模板

```python
"""
================================================================================
[Feature Name] API Endpoints
================================================================================

API Endpoint: POST /api/[route-name]/endpoint

Description:
    [端點描述，1-2 句話]

Query Parameters:
    ---------------
    param1 : type [required/optional, default=value]
        參數描述

    param2 : type [required/optional, default=value]
        參數描述

Response Format:
    {
        "field1": type,
        "field2": type
    }

Example Requests:
    ---------------
    POST /api/[route-name]/endpoint?param1=value1&param2=value2

Error Codes:
    -----------
    INVALID_PARAM - 參數無效
================================================================================
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
import logging

from backend.services.strategies.implementations.new_strategy import NewStrategy

logger = logging.getLogger(__name__)

router = APIRouter()

# ===== 端點函數 =====

@router.post("/endpoint")
async def endpoint_function(
    param1: float = Query(..., description="Parameter 1"),
    param2: Optional[int] = Query(None, description="Parameter 2")
):
    """
    端點描述

    Args:
        param1: 參數 1
        param2: 參數 2（可選）

    Returns:
        回應數據

    Raises:
        HTTPException: 如果參數無效
    """
    try:
        # 驗證參數
        if param1 < 0:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "code": "INVALID_PARAM1",
                        "message": "Parameter 1 must be >= 0",
                        "details": {
                            "field": "param1",
                            "provided": param1,
                            "expected": ">= 0"
                        }
                    }
                }
            )

        # 處理邏輯...
        result = process_data(param1, param2)

        logger.info(f"Endpoint executed successfully")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Endpoint failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An internal server error occurred"
                }
            }
        )

# ===== 輔助函數 =====

def process_data(param1: float, param2: Optional[int]) -> dict:
    """處理數據"""
    # 處理邏輯...
    return {"result": "success"}
```

---

## 前端組件規範

### 頁面組件模板

```jsx
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

// 自定義 Hooks
import { useBacktest } from '../hooks/useBacktest';

// 子組件
import { BacktestForm } from '../components/BacktestForm';
import { ResultsDisplay } from '../components/ResultsDisplay';

/**
 * [Feature Name] Page
 *
 * 功能描述：
 * - 功能 1
 * - 功能 2
 *
 * 狀態管理：
 * - formData: 表單數據
 * - backtestState: 回測狀態
 * - uiState: UI 狀態
 */
const FeaturePage = () => {
  // ===== 狀態 =====
  const [formData, setFormData] = useState({
    startDate: '2023-01-01',
    endDate: '2024-12-31',
    param1: 1.0,
    param2: 10,
  });

  const [backtestState, setBacktestState] = useState({
    loading: false,
    error: null,
    data: null,
  });

  const [uiState, setUiState] = useState({
    showAdvanced: false,
    selectedTab: 'results',
  });

  // ===== Hooks =====
  const { executeBacktest, loading, error, data } = useBacktest();

  // ===== 處理函數 =====
  const handleFormChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleBacktestSubmit = async () => {
    try {
      setBacktestState(prev => ({ ...prev, loading: true, error: null }));

      await executeBacktest(formData);

      setBacktestState(prev => ({
        ...prev,
        loading: false,
        data: data,
      }));
    } catch (err) {
      setBacktestState(prev => ({
        ...prev,
        loading: false,
        error: err.message,
      }));
    }
  };

  // ===== 渲染 =====
  return (
    <div className="feature-page">
      <h1>[Feature Name]</h1>

      <BacktestForm
        formData={formData}
        onChange={handleFormChange}
        onSubmit={handleBacktestSubmit}
        loading={backtestState.loading}
      />

      {backtestState.error && (
        <div className="error-message">
          {backtestState.error}
        </div>
      )}

      {backtestState.data && (
        <ResultsDisplay data={backtestState.data} />
      )}
    </div>
  );
};

export default FeaturePage;
```

---

## 系統註冊規範

### Factory 註冊

```python
# backend/services/strategies/__init__.py

# 1. 導入策略類
from .implementations.new_strategy import NewStrategy

# 2. 註冊到 registry
_registry: Dict[str, Type[IStrategy]] = {
    "new_strategy": NewStrategy,
}

# 3. 定義默認參數
_default_params: Dict[str, Dict[str, Any]] = {
    "new_strategy": {
        "param1": 1.0,
        "param2": 10,
        "param3": "default_value",
    },
}
```

### Router 註冊

```python
# main.py

from routers import new_feature as new_feature_router

app.include_router(
    new_feature_router.router,
    prefix="/api/new-feature",
    tags=["New Feature"]
)
```

### Frontend 註冊

```jsx
// App.jsx

const FeaturePage = React.lazy(() => import('./pages/FeaturePage.jsx'));

<Route
  path="/new-feature"
  element={
    <AdminRoute>
      <FeaturePage />
    </AdminRoute>
  />
/>
```

```jsx
// DashboardLayout.jsx

<NavLink to="/new-feature">
  <i className="bi bi-[icon-name]"></i>
  <span>Feature Name</span>
</NavLink>
```

---

## 質量檢查清單

### 代碼質量

- [ ] 所有公共函數都有類型提示
- [ ] 所有公共函數都有 docstring（三層級）
- [ ] 錯誤處理完整
- [ ] 日誌記錄適當
- [ ] 遵循 PEP 8 編碼規範

### 測試質量

- [ ] 測試覆蓋率 > 80%
- [ ] 所有关鍵路徑測試
- [ ] 邊界條件測試
- [ ] 錯誤處理測試
- [ ] Mock 使用正確

### API 質量

- [ ] NumPy-style API 文檔完整
- [ ] 請求/回應範例完整
- [ ] 錯誤代碼定義完整
- [ ] 參數驗證完整
- [ ] API 測試完成

### Frontend 質量

- [ ] 組件結構清晰
- [ ] State 定義完整
- [ ] 錯誤處理完整
- [ ] 加載狀態處理
- [ ] 用戶提示清晰

---

**版本:** v1.0
**基於:** Market Score V3 開發模式
**最後更新:** 2026-02-22
