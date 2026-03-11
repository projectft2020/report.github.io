# Market Score V3 完整技術規格文檔

**版本：** v1.0
**日期：** 2026-02-22
**狀態：** 完整技術規格
**作者：** Charlie

---

## 📋 目錄

1. [功能概述](#1-功能概述)
2. [API 規格](#2-api-規格)
3. [資料結構](#3-資料結構)
4. [業務邏輯](#4-業務邏輯)
5. [前端規格](#5-前端規格)
6. [測試需求](#6-測試需求)
7. [非功能性需求](#7-非功能性需求)

---

## 1. 功能概述

### 1.1 目標

Market Score V3 是一個四確認機制的部位大小策略，結合台灣和美國市場的多項指標，動態調整投資組合的倉位。

### 1.2 核心功能

1. **四確認機制（'all' 方法論）**
   - 台灣市場分數 > 50
   - 美國市場分數 > 50
   - 台灣 ETF (0050.TW) 價格 > 120 日均線
   - 美國 ETF (QQQ) 價格 > 20 日均線

2. **多方法論投票系統**
   - 支援單一方法論選擇
   - 支援多方法論投票組合
   - 每個方法論投票 0% 或 100%
   - 最終倉位 = (投票數 / 總數) × 100%

3. **漸進式部位控制**
   - 0%: 空倉
   - 25%: 1/4 倉位
   - 50%: 半倉
   - 75%: 3/4 倉位
   - 100%: 全倉

### 1.3 非目標

**不包含的功能：**
- ❌ 實時交易執行（僅回測和信號生成）
- ❌ 滑點和交易成本模擬
- ❌ 複雜的投資組合優化
- ❌ 自動再平衡調度
- ❌ 風險管理模組（止損、止盈）

### 1.4 投資組合

**預設投資組合：**
```python
PORTFOLIO = {
    'QQQ': 0.5,      # 美國納斯達克 100 ETF
    '0050.TW': 0.5   # 台灣 50 ETF
}
```

**部位大小到實際權重的映射：**

| 總倉位 | QQQ 權重 | 0050.TW 權重 | 現金權重 |
|-------|---------|------------|---------|
| 100% | 0.5 | 0.5 | 0.0 |
| 75% | 0.375 | 0.375 | 0.25 |
| 50% | 0.25 | 0.25 | 0.5 |
| 25% | 0.125 | 0.125 | 0.75 |
| 0% | 0.0 | 0.0 | 1.0 |

---

## 2. API 規格

### 2.1 端點總覽

| 端點 | 方法 | 描述 | 認證 |
|-----|------|------|------|
| `/api/market-score-v3/backtest` | POST | 執行回測 | No |
| `/api/market-score-v3/current-signals` | GET | 獲取當前信號 | No |

---

### 2.2 POST /api/market-score-v3/backtest

#### 2.2.1 請求參數

**查詢參數（Query Parameters）：**

| 參數 | 類型 | 必填 | 預設值 | 範圍/限制 | 描述 |
|-----|------|------|-------|----------|------|
| `start_date` | string | ✅ | - | YYYY-MM-DD | 回測開始日期 |
| `end_date` | string | ✅ | - | YYYY-MM-DD | 回測結束日期 |
| `initial_capital` | float | ❌ | 100000 | > 0 | 初始資金 |
| `tw_weight` | float | ❌ | 0.5 | [0, 1] | 台灣 ETF 權重（僅雙市模式） |
| `us_weight` | float | ❌ | 0.5 | [0, 1] | 美國 ETF 權重（僅雙市模式） |
| `tw_etf` | string | ❌ | "0050.TW" | - | 台灣 ETF 代碼 |
| `us_etf` | string | ❌ | "QQQ" | - | 美國 ETF 代碼 |
| `single_mode` | bool | ❌ | false | - | 單一商品模式（僅使用 us_etf） |
| `methodology` | string | ❌ | "all" | - | 策略方法論（單一或多個，逗號分隔） |

**methodology 參數詳解：**

**單一方法論選項：**
- `"all"`: 四確認機制（漸進式部位）
- `"tw_score"`: 台灣市場分數 > 50
- `"us_score"`: 美國市場分數 > 50
- `"tw_ma"`: 0050.TW 價格 > 120MA
- `"us_ma"`: QQQ 價格 > 20MA
- `"tw_score_ma"`: 台灣市場分數 > 台灣市場分數 120MA
- `"us_score_ma"`: 美國市場分數 > 美國市場分數 20MA

**多方法論選項（逗號分隔）：**
- `"tw_ma,us_ma"`: 2 個方法論，各投票 50%
- `"tw_ma,us_ma,tw_score"`: 3 個方法論，各投票 33.3%
- `"tw_ma,us_ma,tw_score,us_score"`: 4 個方法論，各投票 25%

#### 2.2.2 請求範例

**範例 1: 基本回測（預設四確認）**
```bash
curl -X POST "http://localhost:8000/api/market-score-v3/backtest?start_date=2023-01-01&end_date=2024-01-01"
```

**範例 2: 單一方法論 - 僅使用台灣 MA**
```bash
curl -X POST "http://localhost:8000/api/market-score-v3/backtest?start_date=2023-01-01&end_date=2024-01-01&methodology=tw_ma"
```

**範例 3: 雙市模式，自定義權重**
```bash
curl -X POST "http://localhost:8000/api/market-score-v3/backtest?start_date=2023-01-01&end_date=2024-01-01&tw_weight=0.6&us_weight=0.4&methodology=tw_ma,us_ma"
```

**範例 4: 單一商品模式（僅交易 QQQ）**
```bash
curl -X POST "http://localhost:8000/api/market-score-v3/backtest?start_date=2023-01-01&end_date=2024-01-01&single_mode=true&us_etf=QQQ"
```

**範例 5: 多方法論投票（4 個方法）**
```bash
curl -X POST "http://localhost:8000/api/market-score-v3/backtest?start_date=2023-01-01&end_date=2024-01-01&methodology=tw_ma,us_ma,tw_score,us_score"
```

#### 2.2.3 回應格式

**成功回應（200 OK）：**

```json
{
  "summary": {
    "initial_capital": 100000.0,
    "final_equity": 148637.23,
    "total_return": 0.4864,
    "total_return_pct": 48.64,
    "sharpe_ratio": 2.37,
    "max_drawdown": -0.0766,
    "max_drawdown_pct": -7.66,
    "num_trades": 190,
    "start_date": "2023-01-01",
    "end_date": "2024-12-31",
    "trading_days": 463
  },
  "position_stats": {
    "pct_100_days": 265,
    "pct_75_days": 96,
    "pct_50_days": 69,
    "pct_25_days": 27,
    "pct_0_days": 6
  },
  "equity_curve": [
    {
      "date": "2023-01-01",
      "value": 100000.0
    },
    {
      "date": "2023-01-02",
      "value": 100523.45
    },
    {
      "date": "2023-01-03",
      "value": 99876.23
    }
  ],
  "benchmark_curve": [
    {
      "date": "2023-01-01",
      "value": 100000.0
    },
    {
      "date": "2023-01-02",
      "value": 100234.56
    }
  ],
  "return_series": [
    {
      "date": "2023-01-02",
      "value": 100523.45
    },
    {
      "date": "2023-01-03",
      "value": 99876.23
    }
  ],
  "drawdown_curve": [
    {
      "date": "2023-01-02",
      "drawdown": 0.0
    },
    {
      "date": "2023-01-03",
      "drawdown": -0.0065
    }
  ],
  "positions": [
    {
      "date": "2023-01-01",
      "position_size": 0.75,
      "0050.TW_shares": 187,
      "QQQ_shares": 62
    },
    {
      "date": "2023-01-02",
      "position_size": 1.0,
      "0050.TW_shares": 250,
      "QQQ_shares": 83
    }
  ],
  "trades": [
    {
      "date": "2023-01-02",
      "symbol": "QQQ",
      "action": "BUY",
      "shares": 21,
      "price": 315.23,
      "value": 6619.83,
      "reason": "75% → 100%: 4/4 confirmations [TW Score, US Score, 0050.TW>MA, QQQ>MA]"
    },
    {
      "date": "2023-01-15",
      "symbol": "0050.TW",
      "action": "SELL",
      "shares": 63,
      "price": 125.45,
      "value": 7903.35,
      "reason": "100% → 75%: 3/4 confirmations [TW Score, US Score, QQQ>MA -1]"
    }
  ],
  "returns_by_period": {
    "monthly": [
      {
        "date": "2023-01",
        "return": 0.0234
      },
      {
        "date": "2023-02",
        "return": -0.0156
      }
    ],
    "yearly": [
      {
        "year": 2023,
        "return": 0.2856
      },
      {
        "year": 2024,
        "return": 0.2008
      }
    ]
  }
}
```

**欄位說明：**

**summary (摘要)**
| 欄位 | 類型 | 描述 |
|-----|------|------|
| `initial_capital` | float | 初始資金 |
| `final_equity` | float | 最終資產 |
| `total_return` | float | 總收益率（小數） |
| `total_return_pct` | float | 總收益率（百分比） |
| `sharpe_ratio` | float | 夏普比率（年化） |
| `max_drawdown` | float | 最大回撤（小數） |
| `max_drawdown_pct` | float | 最大回撤（百分比） |
| `num_trades` | int | 總交易次數 |
| `start_date` | string | 開始日期 |
| `end_date` | string | 結束日期 |
| `trading_days` | int | 交易天數 |

**position_stats (部位統計)**
| 欄位 | 類型 | 描述 |
|-----|------|------|
| `pct_100_days` | int | 100% 倉位天數 |
| `pct_75_days` | int | 75% 倉位天數 |
| `pct_50_days` | int | 50% 倉位天數 |
| `pct_25_days` | int | 25% 倉位天數 |
| `pct_0_days` | int | 0% 倉位天數 |

**trades (交易記錄)**
| 欄位 | 類型 | 描述 |
|-----|------|------|
| `date` | string | 交易日期 |
| `symbol` | string | 交易標的 |
| `action` | string | 交易方向 (BUY/SELL) |
| `shares` | int | 交易股數 |
| `price` | float | 交易價格 |
| `value` | float | 交易金額 |
| `reason` | string | 交易原因 |

#### 2.2.4 錯誤回應

**錯誤代碼表：**

| HTTP 狀態碼 | 錯誤代碼 | 描述 | 解決方案 |
|-----------|---------|------|---------|
| 400 | INVALID_DATE_FORMAT | 日期格式錯誤 | 使用 YYYY-MM-DD 格式 |
| 400 | INVALID_DATE_RANGE | 結束日期小於開始日期 | 調整日期範圍 |
| 400 | INVALID_WEIGHT | 權重超出 [0, 1] 範圍 | 調整權重為 0-1 之間 |
| 400 | INVALID_METHODOLOGY | 無效的方法論 | 使用支援的方法論名稱 |
| 400 | INVALID_CAPITAL | 初始資金必須 > 0 | 設置正確的初始資金 |
| 500 | INTERNAL_ERROR | 伺服器內部錯誤 | 聯繫系統管理員 |

**錯誤回應範例：**

**範例 1: 無效日期格式**
```json
{
  "error": {
    "code": "INVALID_DATE_FORMAT",
    "message": "Invalid date format: '2023/01/01'. Expected format: YYYY-MM-DD",
    "details": {
      "field": "start_date",
      "provided": "2023/01/01",
      "expected": "YYYY-MM-DD"
    }
  }
}
```

**範例 2: 無效權重**
```json
{
  "error": {
    "code": "INVALID_WEIGHT",
    "message": "Weight must be between 0 and 1",
    "details": {
      "field": "tw_weight",
      "provided": 1.5,
      "expected": "[0, 1]"
    }
  }
}
```

**範例 3: 無效方法論**
```json
{
  "error": {
    "code": "INVALID_METHODOLOGY",
    "message": "Invalid methodology: 'invalid_method'",
    "details": {
      "provided": "invalid_method",
      "valid_options": [
        "all",
        "tw_score",
        "us_score",
        "tw_ma",
        "us_ma",
        "tw_score_ma",
        "us_score_ma"
      ]
    }
  }
}
```

**範例 4: 伺服器內部錯誤**
```json
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An internal server error occurred",
    "details": {
      "timestamp": "2026-02-22T04:15:23Z",
      "request_id": "req_abc123"
    }
  }
}
```

#### 2.2.5 前端錯誤處理行為

```typescript
// 錯誤處理示例
const handleBacktestError = (error: any) => {
  const errorCode = error.response?.data?.error?.code;

  switch (errorCode) {
    case 'INVALID_DATE_FORMAT':
      // UI: 顯示日期格式錯誤提示
      setErrorMessage('日期格式錯誤，請使用 YYYY-MM-DD 格式');
      break;

    case 'INVALID_DATE_RANGE':
      // UI: 顯示日期範圍錯誤提示
      setErrorMessage('結束日期必須大於開始日期');
      break;

    case 'INVALID_WEIGHT':
      // UI: 顯示權重錯誤提示
      setErrorMessage('權重必須在 0 到 1 之間');
      break;

    case 'INVALID_METHODOLOGY':
      // UI: 顯示方法論錯誤提示
      setErrorMessage('無效的方法論，請選擇有效的選項');
      break;

    case 'INVALID_CAPITAL':
      // UI: 顯示資金錯誤提示
      setErrorMessage('初始資金必須大於 0');
      break;

    case 'INTERNAL_ERROR':
    default:
      // UI: 顯示通用錯誤提示
      setErrorMessage('伺服器錯誤，請稍後再試');
      break;
  }

  // 記錄錯誤到日誌
  console.error('Backtest error:', error);
};
```

---

### 2.3 GET /api/market-score-v3/current-signals

#### 2.3.1 請求參數

**查詢參數（無）**

#### 2.3.2 請求範例

```bash
curl -X GET "http://localhost:8000/api/market-score-v3/current-signals"
```

#### 2.3.3 回應格式

**成功回應（200 OK）：**

```json
{
  "date": "2026-02-21",
  "tw_score": 98.0,
  "us_score": 25.0,
  "tw_above_ma": true,
  "us_above_ma": false,
  "position_size": 0.5,
  "position_pct": 50.0,
  "portfolio_weights": {
    "QQQ": 0.25,
    "0050.TW": 0.25,
    "CASH": 0.5
  },
  "confirmations": {
    "tw_score": true,
    "us_score": false,
    "tw_ma": true,
    "us_ma": false
  },
  "confirmation_count": 2,
  "max_confirmations": 4,
  "trade_reason": "50% position: 2/4 confirmations [TW Score, 0050.TW>MA]"
}
```

**欄位說明：**

| 欄位 | 類型 | 描述 |
|-----|------|------|
| `date` | string | 日期 |
| `tw_score` | float | 台灣市場分數 |
| `us_score` | float | 美國市場分數 |
| `tw_above_ma` | bool | 0050.TW 是否高於 120MA |
| `us_above_ma` | bool | QQQ 是否高於 20MA |
| `position_size` | float | 總倉位大小（0.0 - 1.0） |
| `position_pct` | float | 總倉位百分比（0 - 100） |
| `portfolio_weights` | object | 投資組合權重 |
| `portfolio_weights.QQQ` | float | QQQ 權重 |
| `portfolio_weights['0050.TW']` | float | 0050.TW 權重 |
| `portfolio_weights.CASH` | float | 現金權重 |
| `confirmations` | object | 各確認信號狀態 |
| `confirmations.tw_score` | bool | 台灣市場分數確認 |
| `confirmations.us_score` | bool | 美國市場分數確認 |
| `confirmations.tw_ma` | bool | 台灣 MA 確認 |
| `confirmations.us_ma` | bool | 美國 MA 確認 |
| `confirmation_count` | int | 當前確認數量 |
| `max_confirmations` | int | 最大確認數量 |
| `trade_reason` | string | 交易原因說明 |

#### 2.3.4 錯誤回應

**錯誤代碼表：**

| HTTP 狀態碼 | 錯誤代碼 | 描述 |
|-----------|---------|------|
| 500 | DATA_UNAVAILABLE | 數據不可用（可能是數據庫連接失敗） |
| 500 | CALCULATION_ERROR | 計算錯誤 |

**錯誤回應範例：**

**範例 1: 數據不可用**
```json
{
  "error": {
    "code": "DATA_UNAVAILABLE",
    "message": "Unable to fetch market data",
    "details": {
      "timestamp": "2026-02-22T04:15:23Z"
    }
  }
}
```

#### 2.3.5 前端錯誤處理行為

```typescript
const handleSignalsError = (error: any) => {
  const errorCode = error.response?.data?.error?.code;

  if (errorCode === 'DATA_UNAVAILABLE') {
    // UI: 顯示數據加載失敗提示
    setErrorMessage('無法獲取市場數據，請稍後再試');
  } else if (errorCode === 'CALCULATION_ERROR') {
    // UI: 顯示計算錯誤提示
    setErrorMessage('信號計算錯誤，請聯繫系統管理員');
  } else {
    // UI: 顯示通用錯誤提示
    setErrorMessage('伺服器錯誤，請稍後再試');
  }

  console.error('Signals error:', error);
};
```

---

## 3. 資料結構

### 3.1 TypeScript 類型定義

```typescript
// 請求參數
interface BacktestRequest {
  start_date: string;
  end_date: string;
  initial_capital?: number;
  tw_weight?: number;
  us_weight?: number;
  tw_etf?: string;
  us_etf?: string;
  single_mode?: boolean;
  methodology?: string;
}

// 回應摘要
interface BacktestSummary {
  initial_capital: number;
  final_equity: number;
  total_return: number;
  total_return_pct: number;
  sharpe_ratio: number;
  max_drawdown: number;
  max_drawdown_pct: number;
  num_trades: number;
  start_date: string;
  end_date: string;
  trading_days: number;
}

// 部位統計
interface PositionStats {
  pct_100_days: number;
  pct_75_days: number;
  pct_50_days: number;
  pct_25_days: number;
  pct_0_days: number;
}

// 權益曲線點
interface EquityPoint {
  date: string;
  value: number;
}

// 交易記錄
interface Trade {
  date: string;
  symbol: string;
  action: 'BUY' | 'SELL';
  shares: number;
  price: number;
  value: number;
  reason: string;
}

// 週期回報
interface PeriodReturn {
  date: string;
  year?: number;
  return: number;
}

// 週期回報集合
interface ReturnsByPeriod {
  monthly: PeriodReturn[];
  yearly: PeriodReturn[];
}

// 完整回測回應
interface BacktestResponse {
  summary: BacktestSummary;
  position_stats: PositionStats;
  equity_curve: EquityPoint[];
  benchmark_curve: EquityPoint[];
  return_series: EquityPoint[];
  drawdown_curve: EquityPoint[];
  positions: EquityPoint[];
  trades: Trade[];
  returns_by_period: ReturnsByPeriod;
}

// 當前信號回應
interface CurrentSignalsResponse {
  date: string;
  tw_score: number;
  us_score: number;
  tw_above_ma: boolean;
  us_above_ma: boolean;
  position_size: number;
  position_pct: number;
  portfolio_weights: {
    QQQ: number;
    '0050.TW': number;
    CASH: number;
  };
  confirmations: {
    tw_score: boolean;
    us_score: boolean;
    tw_ma: boolean;
    us_ma: boolean;
  };
  confirmation_count: number;
  max_confirmations: number;
  trade_reason: string;
}

// 錯誤回應
interface ErrorResponse {
  error: {
    code: string;
    message: string;
    details?: any;
  };
}
```

### 3.2 Python 類型定義

```python
from typing import Dict, List, Optional, TypedDict, Union
from datetime import date
from enum import Enum

class ErrorCode(str, Enum):
    INVALID_DATE_FORMAT = "INVALID_DATE_FORMAT"
    INVALID_DATE_RANGE = "INVALID_DATE_RANGE"
    INVALID_WEIGHT = "INVALID_WEIGHT"
    INVALID_METHODOLOGY = "INVALID_METHODOLOGY"
    INVALID_CAPITAL = "INVALID_CAPITAL"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    DATA_UNAVAILABLE = "DATA_UNAVAILABLE"
    CALCULATION_ERROR = "CALCULATION_ERROR"

class TradeAction(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

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

class PositionStats(TypedDict):
    pct_100_days: int
    pct_75_days: int
    pct_50_days: int
    pct_25_days: int
    pct_0_days: int

class EquityPoint(TypedDict):
    date: str
    value: float

class Trade(TypedDict):
    date: str
    symbol: str
    action: str
    shares: int
    price: float
    value: float
    reason: str

class PeriodReturn(TypedDict):
    date: str
    year: Optional[int]
    return: float

class ReturnsByPeriod(TypedDict):
    monthly: List[PeriodReturn]
    yearly: List[PeriodReturn]

class BacktestResponse(TypedDict):
    summary: BacktestSummary
    position_stats: PositionStats
    equity_curve: List[EquityPoint]
    benchmark_curve: List[EquityPoint]
    return_series: List[EquityPoint]
    drawdown_curve: List[EquityPoint]
    positions: List[EquityPoint]
    trades: List[Trade]
    returns_by_period: ReturnsByPeriod

class CurrentSignalsResponse(TypedDict):
    date: str
    tw_score: float
    us_score: float
    tw_above_ma: bool
    us_above_ma: bool
    position_size: float
    position_pct: float
    portfolio_weights: Dict[str, float]
    confirmations: Dict[str, bool]
    confirmation_count: int
    max_confirmations: int
    trade_reason: str
```

---

## 4. 業務邏輯

### 4.1 四確認機制（'all' 方法論）

#### 4.1.1 確認條件

| 確認 | 條件 | 說明 |
|-----|------|------|
| 1 | TW Score > 50 | 台灣市場分數 > 50 |
| 2 | US Score > 50 | 美國市場分數 > 50 |
| 3 | 0050.TW > 120MA | 台灣 50 ETF 價格 > 120 日均線 |
| 4 | QQQ > 20MA | 美國納斯達克 100 ETF 價格 > 20 日均線 |

#### 4.1.2 倉位映射

```
確認數量 → 總倉位 → QQQ 權重 → 0050.TW 權重 → 現金權重
    0    →   0%   →   0.0    →     0.0      →    1.0
    1    →   25%  →   0.125  →     0.125    →    0.75
    2    →   50%  →   0.25   →     0.25     →    0.5
    3    →   75%  →   0.375  →     0.375    →    0.25
    4    →   100% →   0.5    →     0.5      →    0.0
```

#### 4.1.3 偽代碼

```
FUNCTION calculate_position_all_methodology(
    tw_score: float,
    us_score: float,
    tw_above_ma: bool,
    us_above_ma: bool
) -> (float, str):

    # 計算確認數量
    confirmations = 0
    IF tw_score > 50 THEN
        confirmations += 1
    END IF

    IF us_score > 50 THEN
        confirmations += 1
    END IF

    IF tw_above_ma THEN
        confirmations += 1
    END IF

    IF us_above_ma THEN
        confirmations += 1
    END IF

    # 映射到倉位
    SWITCH confirmations
        CASE 0:
            position_size = 0.0
            reason = "0% position: 0/4 confirmations"
        CASE 1:
            position_size = 0.25
            reason = "25% position: 1/4 confirmations"
        CASE 2:
            position_size = 0.5
            reason = "50% position: 2/4 confirmations"
        CASE 3:
            position_size = 0.75
            reason = "75% position: 3/4 confirmations"
        CASE 4:
            position_size = 1.0
            reason = "100% position: 4/4 confirmations"
    END SWITCH

    RETURN (position_size, reason)
```

### 4.2 多方法論投票系統

#### 4.2.1 單一方法論

**邏輯：**
```
position_size = 0.0 OR 1.0

IF condition TRUE THEN
    position_size = 1.0
    reason = "100% position: <methodology> ✓ Entry"
ELSE
    position_size = 0.0
    reason = "0% position: <methodology> ✗ Exit"
END IF
```

**方法論條件：**

| 方法論 | 條件 |
|-------|------|
| `tw_score` | TW Score > 50 |
| `us_score` | US Score > 50 |
| `tw_ma` | 0050.TW 價格 > 120MA |
| `us_ma` | QQQ 價格 > 20MA |
| `tw_score_ma` | TW Score > TW Score 120MA |
| `us_score_ma` | US Score > US Score 20MA |

#### 4.2.2 多方法論投票

**邏輯：**
```
total_methods = len(methodologies)
yes_votes = 0
active_methods = []

FOR EACH methodology IN methodologies:
    condition = evaluate_condition(methodology)
    IF condition TRUE THEN
        yes_votes += 1
        active_methods.append(methodology)
    END IF
END FOR

position_size = yes_votes / total_methods
position_pct = position_size * 100

reason = "{pct}% position: {votes}/{total} votes [{methods}]"
```

**範例 1: 2 個方法論（`tw_ma,us_ma`）**
```
total_methods = 2
yes_votes = 0

# tw_ma 檢查
IF 0050.TW > 120MA THEN
    yes_votes = 1
    active_methods = ["tw_ma"]
END IF

# us_ma 檢查
IF QQQ > 20MA THEN
    yes_votes = 2
    active_methods = ["tw_ma", "us_ma"]
END IF

# 結果
position_size = 2/2 = 1.0 (100%)
reason = "100% position: 2/2 votes [0050.TW>MA, QQQ>MA]"
```

**範例 2: 3 個方法論（`tw_ma,us_ma,tw_score`）**
```
total_methods = 3
yes_votes = 0

# tw_ma 檢查
IF 0050.TW > 120MA THEN
    yes_votes = 1
END IF

# us_ma 檢查
IF QQQ > 20MA THEN
    yes_votes = 2
END IF

# tw_score 檢查
IF TW Score > 50 THEN
    yes_votes = 3
END IF

# 結果
position_size = 3/3 = 1.0 (100%)
reason = "100% position: 3/3 votes [0050.TW>MA, QQQ>MA, TW Score]"
```

**範例 3: 3 個方法論（2 個 YES）**
```
total_methods = 3
yes_votes = 2

# 結果
position_size = 2/3 = 0.667 (66.7%)
reason = "67% position: 2/3 votes [0050.TW>MA, QQQ>MA, TW Score -1]"
```

### 4.3 市場分數計算

**公式：**
```
Market Score = MA Slope Score (max 50) + RSI Score (max 50)

MA Slope Score:
    slope = linear_regression(ma_series[-120:-1])
    normalized_slope = normalize(slope, -0.5, 0.5)
    ma_slope_score = normalized_slope * 50

RSI Score:
    rsi = calculate_rsi(prices[-120:-1], 14)
    normalized_rsi = normalize(rsi, 30, 70)
    rsi_score = normalized_rsi * 50

Market Score = ma_slope_score + rsi_score
```

**範圍：** 0 - 100

### 4.4 均線計算

**台灣 120MA：**
```
tw_120ma = average(prices_0050[-120:])
```

**美國 20MA：**
```
us_20ma = average(prices_qqq[-20:])
```

### 4.5 投資組合權重計算

```python
def calculate_portfolio_weights(
    position_size: float,
    tw_weight: float = 0.5,
    us_weight: float = 0.5,
    single_mode: bool = False
) -> Dict[str, float]:
    """
    計算投資組合權重

    Args:
        position_size: 總倉位大小 (0.0 - 1.0)
        tw_weight: 台灣 ETF 權重 (僅雙市模式)
        us_weight: 美國 ETF 權重 (僅雙市模式)
        single_mode: 單一商品模式

    Returns:
        投資組合權重字典 {'QQQ': float, '0050.TW': float, 'CASH': float}
    """
    if single_mode:
        # 單一商品模式：100% 資金在 us_etf
        qqq_weight = position_size * 1.0
        tw_weight_val = 0.0
    else:
        # 雙市模式：根據 tw_weight 和 us_weight 分配
        qqq_weight = position_size * us_weight
        tw_weight_val = position_size * tw_weight

    cash_weight = 1.0 - qqq_weight - tw_weight_val

    return {
        'QQQ': qqq_weight,
        '0050.TW': tw_weight_val,
        'CASH': cash_weight
    }
```

---

## 5. 前端規格

### 5.1 元件結構

```
MarketScoreV3Page/
├── index.jsx                 # 主頁面組件
├── components/
│   ├── BacktestForm.jsx      # 回測表單
│   ├── ResultsDisplay.jsx    # 回測結果顯示
│   ├── EquityChart.jsx       # 權益曲線圖表
│   ├── DrawdownChart.jsx     # 回撤曲線圖表
│   ├── PositionStats.jsx     # 部位統計
│   ├── TradeTable.jsx        # 交易記錄表
│   └── CurrentSignals.jsx    # 當前信號顯示
├── hooks/
│   ├── useBacktest.js        # 回測 Hook
│   ├── useCurrentSignals.js  # 當前信號 Hook
│   └── useChart.js          # 圖表 Hook
├── utils/
│   ├── api.js               # API 調用工具
│   └── formatters.js        # 格式化工具
└── constants.js             # 常量定義
```

### 5.2 狀態管理

#### 5.2.1 主頁面狀態

```typescript
interface MarketScoreV3PageState {
  // 表單狀態
  formData: {
    startDate: string;
    endDate: string;
    initialCapital: number;
    twWeight: number;
    usWeight: number;
    twEtf: string;
    usEtf: string;
    singleMode: boolean;
    methodology: string;
  };

  // 回測狀態
  backtestState: {
    loading: boolean;
    error: string | null;
    data: BacktestResponse | null;
  };

  // 當前信號狀態
  signalsState: {
    loading: boolean;
    error: string | null;
    data: CurrentSignalsResponse | null;
  };

  // UI 狀態
  uiState: {
    showAdvanced: boolean;
    selectedTab: 'results' | 'trades' | 'analysis';
  };
}
```

#### 5.2.2 狀態初始化

```typescript
const initialState: MarketScoreV3PageState = {
  formData: {
    startDate: '2023-01-01',
    endDate: '2024-12-31',
    initialCapital: 100000,
    twWeight: 0.5,
    usWeight: 0.5,
    twEtf: '0050.TW',
    usEtf: 'QQQ',
    singleMode: false,
    methodology: 'all'
  },
  backtestState: {
    loading: false,
    error: null,
    data: null
  },
  signalsState: {
    loading: false,
    error: null,
    data: null
  },
  uiState: {
    showAdvanced: false,
    selectedTab: 'results'
  }
};
```

### 5.3 交互流程

#### 5.3.1 頁面加載流程

```
[頁面掛載]
    ↓
[加載當前信號]
    ├─ [成功] → 顯示當前信號
    └─ [失敗] → 顯示錯誤提示
    ↓
[用戶可開始回測]
```

#### 5.3.2 回測執行流程

```
[用戶填寫表單]
    ↓
[驗證表單]
    ├─ [無效] → 顯示驗證錯誤
    └─ [有效] → 繼續
    ↓
[點擊執行回測]
    ↓
[設置 loading = true]
    ↓
[調用 API]
    ├─ [成功] →
    │   ├─ [顯示結果]
    │   ├─ [繪製圖表]
    │   └─ [設置 loading = false]
    └─ [失敗] →
        ├─ [顯示錯誤]
        └─ [設置 loading = false]
```

#### 5.3.3 方法論選擇交互

```
[用戶選擇方法論]
    ├─ [單一方法論]
    │   └─ 顯示該方法論的說明
    └─ [多方法論]
        ├─ 顯示已選方法論列表
        ├─ 允許添加/移除方法論
        └─ 顯示預期投票權重
```

### 5.4 組件詳細規格

#### 5.4.1 BacktestForm.jsx

**Props:**
```typescript
interface BacktestFormProps {
  formData: FormData;
  onChange: (formData: FormData) => void;
  onSubmit: () => void;
  loading: boolean;
}
```

**輸入欄位：**
| 欄位 | 類型 | 驗證 | 預設值 |
|-----|------|------|-------|
| 開始日期 | date | 必填 | 2023-01-01 |
| 結束日期 | date | 必填，>= 開始日期 | 2024-12-31 |
| 初始資金 | number | 必填，> 0 | 100000 |
| 台灣權重 | number | [0, 1] | 0.5 |
| 美國權重 | number | [0, 1] | 0.5 |
| 台灣 ETF | string | 必填 | 0050.TW |
| 美國 ETF | string | 必填 | QQQ |
| 單一模式 | boolean | - | false |
| 方法論 | string | 必填 | all |

#### 5.4.2 ResultsDisplay.jsx

**Props:**
```typescript
interface ResultsDisplayProps {
  data: BacktestResponse | null;
  loading: boolean;
}
```

**顯示內容：**
- 績效摘要（總回報、夏普比率、最大回撤等）
- 部位統計（各倉位天數）
- 權益曲線圖表
- 回撤曲線圖表
- 交易記錄表
- 週期回報分析

#### 5.4.3 CurrentSignals.jsx

**Props:**
```typescript
interface CurrentSignalsProps {
  data: CurrentSignalsResponse | null;
  loading: boolean;
}
```

**顯示內容：**
- 當前日期
- 市場分數（台灣/美國）
- MA 狀態（台灣/美國）
- 當前倉位
- 投資組合權重
- 確認信號狀態
- 交易原因

### 5.5 錯誤處理

#### 5.5.1 表單驗證錯誤

```typescript
const validateForm = (formData: FormData): FormErrors => {
  const errors: FormErrors = {};

  if (!formData.startDate) {
    errors.startDate = '開始日期為必填';
  }

  if (!formData.endDate) {
    errors.endDate = '結束日期為必填';
  } else if (formData.startDate && formData.endDate < formData.startDate) {
    errors.endDate = '結束日期必須大於開始日期';
  }

  if (formData.initialCapital <= 0) {
    errors.initialCapital = '初始資金必須大於 0';
  }

  if (formData.twWeight < 0 || formData.twWeight > 1) {
    errors.twWeight = '權重必須在 0 到 1 之間';
  }

  if (formData.usWeight < 0 || formData.usWeight > 1) {
    errors.usWeight = '權重必須在 0 到 1 之間';
  }

  return errors;
};
```

#### 5.5.2 API 錯誤處理

見 [2.2.5 前端錯誤處理行為](#225-前端錯誤處理行為) 和 [2.3.5 前端錯誤處理行為](#235-前端錯誤處理行為)

#### 5.5.3 用戶提示

| 錯誤類型 | UI 行為 |
|---------|---------|
| 表單驗證錯誤 | 顯示欄位下方的紅色錯誤文字 |
| API 錯誤 | 顯示頂部 alert 橫幅 |
| 網絡錯誤 | 顯示 "網絡連接錯誤，請檢查網絡設置" |
| 加載中 | 顯示 loading spinner |

---

## 6. 測試需求

### 6.1 單元測試

#### 6.1.1 策略邏輯測試

**測試案例：**

```python
import pytest
from services.strategies.implementations.market_score_v3_strategy import MarketScoreV3Strategy

class TestMarketScoreV3Strategy:
    """Market Score V3 策略單元測試"""

    def test_four_confirmations_all_true(self):
        """測試：4 個確認全部為 True → 100% 倉位"""
        strategy = MarketScoreV3Strategy()
        position_size, reason = strategy._calculate_position_all_methodology(
            tw_score=65,
            us_score=58,
            tw_above_ma=True,
            us_above_ma=True
        )
        assert position_size == 1.0
        assert "100%" in reason
        assert "4/4" in reason

    def test_four_confirmations_3_true(self):
        """測試：3 個確認為 True → 75% 倉位"""
        strategy = MarketScoreV3Strategy()
        position_size, reason = strategy._calculate_position_all_methodology(
            tw_score=65,
            us_score=45,  # < 50
            tw_above_ma=True,
            us_above_ma=True
        )
        assert position_size == 0.75
        assert "75%" in reason
        assert "3/4" in reason

    def test_four_confirmations_2_true(self):
        """測試：2 個確認為 True → 50% 倉位"""
        strategy = MarketScoreV3Strategy()
        position_size, reason = strategy._calculate_position_all_methodology(
            tw_score=65,
            us_score=45,
            tw_above_ma=True,
            us_above_ma=False
        )
        assert position_size == 0.5
        assert "50%" in reason
        assert "2/4" in reason

    def test_four_confirmations_1_true(self):
        """測試：1 個確認為 True → 25% 倉位"""
        strategy = MarketScoreV3Strategy()
        position_size, reason = strategy._calculate_position_all_methodology(
            tw_score=45,
            us_score=45,
            tw_above_ma=True,
            us_above_ma=False
        )
        assert position_size == 0.25
        assert "25%" in reason
        assert "1/4" in reason

    def test_four_confirmations_0_true(self):
        """測試：0 個確認為 True → 0% 倉位"""
        strategy = MarketScoreV3Strategy()
        position_size, reason = strategy._calculate_position_all_methodology(
            tw_score=45,
            us_score=45,
            tw_above_ma=False,
            us_above_ma=False
        )
        assert position_size == 0.0
        assert "0%" in reason
        assert "0/4" in reason

    def test_multiple_methodologies_voting_2_methods(self):
        """測試：2 個方法論投票（都通過）"""
        strategy = MarketScoreV3Strategy()
        methodologies = ["tw_ma", "us_ma"]
        position_size = strategy._calculate_position_by_voting(
            methodologies=methodologies,
            tw_above_ma=True,
            us_above_ma=True,
            tw_score=50,
            us_score=50
        )
        assert position_size == 1.0  # 2/2 = 100%

    def test_multiple_methodologies_voting_3_methods(self):
        """測試：3 個方法論投票（2 個通過）"""
        strategy = MarketScoreV3Strategy()
        methodologies = ["tw_ma", "us_ma", "tw_score"]
        position_size = strategy._calculate_position_by_voting(
            methodologies=methodologies,
            tw_above_ma=True,
            us_above_ma=True,
            tw_score=45,  # 不通過
            us_score=50
        )
        assert position_size == pytest.approx(0.667, rel=0.01)  # 2/3 ≈ 66.7%

    def test_portfolio_weights_single_mode(self):
        """測試：單一商品模式權重計算"""
        strategy = MarketScoreV3Strategy()
        weights = strategy._calculate_portfolio_weights(
            position_size=1.0,
            single_mode=True
        )
        assert weights['QQQ'] == 1.0
        assert weights['0050.TW'] == 0.0
        assert weights['CASH'] == 0.0

    def test_portfolio_weights_dual_mode(self):
        """測試：雙市模式權重計算"""
        strategy = MarketScoreV3Strategy()
        weights = strategy._calculate_portfolio_weights(
            position_size=0.5,
            tw_weight=0.6,
            us_weight=0.4,
            single_mode=False
        )
        assert weights['QQQ'] == pytest.approx(0.2, rel=0.01)  # 0.5 * 0.4
        assert weights['0050.TW'] == pytest.approx(0.3, rel=0.01)  # 0.5 * 0.6
        assert weights['CASH'] == pytest.approx(0.5, rel=0.01)  # 1.0 - 0.2 - 0.3

    def test_market_score_calculation(self):
        """測試：市場分數計算"""
        strategy = MarketScoreV3Strategy()
        score = strategy._calculate_market_score(
            symbol='0050.TW',
            period=120,
            market_date=date(2024, 1, 1)
        )
        assert 0 <= score <= 100  # 分數範圍檢查
```

**測試覆蓋目標：**
- ✅ 線路覆蓋率：> 90%
- ✅ 分支覆蓋率：> 85%
- ✅ 函數覆蓋率：100%

#### 6.1.2 API 端點測試

**測試案例：**

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestMarketScoreV3API:
    """Market Score V3 API 端點測試"""

    def test_backtest_success(self):
        """測試：成功回測"""
        response = client.post(
            "/api/market-score-v3/backtest",
            params={
                "start_date": "2023-01-01",
                "end_date": "2024-01-01"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "equity_curve" in data
        assert "trades" in data

    def test_backtest_invalid_date_format(self):
        """測試：無效日期格式"""
        response = client.post(
            "/api/market-score-v3/backtest",
            params={
                "start_date": "2023/01/01",  # 錯誤格式
                "end_date": "2024-01-01"
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "INVALID_DATE_FORMAT"

    def test_backtest_invalid_date_range(self):
        """測試：無效日期範圍"""
        response = client.post(
            "/api/market-score-v3/backtest",
            params={
                "start_date": "2024-01-01",
                "end_date": "2023-01-01"  # 結束日期 < 開始日期
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "INVALID_DATE_RANGE"

    def test_backtest_invalid_weight(self):
        """測試：無效權重"""
        response = client.post(
            "/api/market-score-v3/backtest",
            params={
                "start_date": "2023-01-01",
                "end_date": "2024-01-01",
                "tw_weight": 1.5  # > 1
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "INVALID_WEIGHT"

    def test_backtest_invalid_methodology(self):
        """測試：無效方法論"""
        response = client.post(
            "/api/market-score-v3/backtest",
            params={
                "start_date": "2023-01-01",
                "end_date": "2024-01-01",
                "methodology": "invalid_method"
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert data["error"]["code"] == "INVALID_METHODOLOGY"

    def test_current_signals_success(self):
        """測試：成功獲取當前信號"""
        response = client.get("/api/market-score-v3/current-signals")
        assert response.status_code == 200
        data = response.json()
        assert "tw_score" in data
        assert "us_score" in data
        assert "position_size" in data
```

**測試覆蓋目標：**
- ✅ 端點覆蓋率：100%
- ✅ 錯誤碼覆蓋率：100%

### 6.2 整合測試

**測試案例：**

```python
class TestMarketScoreV3Integration:
    """Market Score V3 整合測試"""

    def test_full_backtest_workflow(self):
        """測試：完整回測工作流"""
        # 1. 執行回測
        response = client.post(
            "/api/market-score-v3/backtest",
            params={
                "start_date": "2023-01-01",
                "end_date": "2024-01-01",
                "methodology": "all"
            }
        )

        # 2. 驗證回應
        assert response.status_code == 200
        data = response.json()

        # 3. 驗證數據完整性
        assert len(data["equity_curve"]) > 0
        assert len(data["trades"]) > 0
        assert data["summary"]["trading_days"] > 0

        # 4. 驗證邏輯正確性
        assert data["summary"]["final_equity"] > 0
        assert -1 <= data["summary"]["max_drawdown"] <= 0
        assert data["summary"]["total_return_pct"] >= -100

    def test_backtest_with_custom_weights(self):
        """測試：自定義權重回測"""
        response = client.post(
            "/api/market-score-v3/backtest",
            params={
                "start_date": "2023-01-01",
                "end_date": "2024-01-01",
                "tw_weight": 0.7,
                "us_weight": 0.3,
                "methodology": "all"
            }
        )
        assert response.status_code == 200
        data = response.json()

        # 驗證權重影響
        # （具體驗證邏輯需要根據實際實現調整）
```

### 6.3 E2E 測試

**測試案例（Playwright/Cypress）：**

```javascript
// Playwright E2E 測試
import { test, expect } from '@playwright/test';

test.describe('Market Score V3 Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173/market-score-v3');
  });

  test('displays current signals on page load', async ({ page }) => {
    // 驗證當前信號顯示
    await expect(page.locator('[data-testid="tw-score"]')).toBeVisible();
    await expect(page.locator('[data-testid="us-score"]')).toBeVisible();
    await expect(page.locator('[data-testid="position-size"]')).toBeVisible();
  });

  test('executes backtest successfully', async ({ page }) => {
    // 填寫表單
    await page.fill('[data-testid="start-date"]', '2023-01-01');
    await page.fill('[data-testid="end-date"]', '2024-01-01');
    await page.fill('[data-testid="initial-capital"]', '100000');

    // 點擊執行按鈕
    await page.click('[data-testid="submit-backtest"]');

    // 等待結果
    await page.waitForSelector('[data-testid="backtest-results"]', { timeout: 30000 });

    // 驗證結果
    await expect(page.locator('[data-testid="total-return"]')).toBeVisible();
    await expect(page.locator('[data-testid="sharpe-ratio"]')).toBeVisible();
    await expect(page.locator('[data-testid="equity-chart"]')).toBeVisible();
  });

  test('displays validation error for invalid date range', async ({ page }) => {
    // 填寫無效日期範圍
    await page.fill('[data-testid="start-date"]', '2024-01-01');
    await page.fill('[data-testid="end-date"]', '2023-01-01');

    // 點擊執行按鈕
    await page.click('[data-testid="submit-backtest"]');

    // 驗證錯誤提示
    await expect(page.locator('[data-testid="date-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="date-error"]')).toContainText(
      '結束日期必須大於開始日期'
    );
  });

  test('handles API error gracefully', async ({ page }) => {
    // 模擬 API 錯誤（需要修改測試環境）
    await page.route('**/api/market-score-v3/backtest', route => {
      route.fulfill({
        status: 500,
        body: JSON.stringify({
          error: {
            code: 'INTERNAL_ERROR',
            message: 'An internal server error occurred'
          }
        })
      });
    });

    // 執行回測
    await page.fill('[data-testid="start-date"]', '2023-01-01');
    await page.fill('[data-testid="end-date"]', '2024-01-01');
    await page.click('[data-testid="submit-backtest"]');

    // 驗證錯誤提示
    await expect(page.locator('[data-testid="api-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="api-error"]')).toContainText(
      '伺服器錯誤'
    );
  });
});
```

**測試覆蓋目標：**
- ✅ 關鍵用戶流程：100%
- ✅ 錯誤處理流程：100%
- ✅ 跨瀏覽器兼容性：Chrome, Firefox, Safari

### 6.4 性能測試

**測試案例：**

```python
class TestMarketScoreV3Performance:
    """Market Score V3 性能測試"""

    def test_backtest_performance_large_dataset(self):
        """測試：大型數據集回測性能"""
        import time

        start_time = time.time()

        response = client.post(
            "/api/market-score-v3/backtest",
            params={
                "start_date": "2010-01-01",
                "end_date": "2024-12-31",  # 15 年數據
                "methodology": "all"
            }
        )

        end_time = time.time()
        duration = end_time - start_time

        # 驗證性能
        assert response.status_code == 200
        assert duration < 10.0  # 15 年數據應在 10 秒內完成

    def test_concurrent_backtests(self):
        """測試：並發回測"""
        import concurrent.futures
        import time

        def run_backtest():
            start_time = time.time()
            response = client.post(
                "/api/market-score-v3/backtest",
                params={
                    "start_date": "2023-01-01",
                    "end_date": "2024-01-01",
                    "methodology": "all"
                }
            )
            end_time = time.time()
            return response.status_code, end_time - start_time

        # 執行 5 個並發回測
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(run_backtest) for _ in range(5)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]

        # 驗證所有請求成功
        for status_code, duration in results:
            assert status_code == 200
            assert duration < 5.0
```

**性能目標：**
- ✅ 回測 1 年數據：< 2 秒
- ✅ 回測 10 年數據：< 5 秒
- ✅ 並發 5 個回測：< 10 秒
- ✅ API 響應時間（p95）：< 3 秒

---

## 7. 非功能性需求

### 7.1 性能需求

| 指標 | 目標 | 測量方法 |
|-----|------|---------|
| API 響應時間（p50） | < 1 秒 | 端到端測試 |
| API 響應時間（p95） | < 3 秒 | 端到端測試 |
| API 響應時間（p99） | < 5 秒 | 端到端測試 |
| 回測 1 年數據 | < 2 秒 | 性能測試 |
| 回測 10 年數據 | < 5 秒 | 性能測試 |
| 並發處理能力 | 10 個並發請求 | 負載測試 |

### 7.2 兼容性需求

**瀏覽器兼容性：**
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

**瀏覽器功能支持：**
- ✅ ES6+
- ✅ CSS Grid
- ✅ CSS Flexbox
- ✅ Fetch API
- ✅ Web Workers（可選）

**API 版本兼容性：**
- ✅ REST API v1
- ✅ OpenAPI 3.0

### 7.3 可維護性需求

**代碼質量：**
- ✅ Python PEP 8 標準
- ✅ TypeScript ESLint + Prettier
- ✅ 測試覆蓋率 > 80%
- ✅ 文檔覆蓋率 > 90%

**代碼結構：**
- ✅ 模組化設計
- ✅ 清晰的職責分離
- ✅ 易於擴展
- ✅ 易於測試

**文檔要求：**
- ✅ API 文檔（OpenAPI/Swagger）
- ✅ 代碼註釋
- ✅ 架構文檔
- ✅ 部署文檔

### 7.4 安全性需求

**輸入驗證：**
- ✅ 所有輸入參數驗證
- ✅ SQL 注入防護
- ✅ XSS 防護
- ✅ CSRF 防護

**數據保護：**
- ✅ 敏感數據加密
- ✅ HTTPS 通信
- ✅ 認證和授權（如需要）

**錯誤處理：**
- ✅ 不暴露敏感信息
- ✅ 詳細的日誌記錄
- ✅ 錯誤監控和警報

### 7.5 可擴展性需求

**水平擴展：**
- ✅ 無狀態 API 設計
- ✅ 支負載均衡
- ✅ 支多實例部署

**垂直擴展：**
- ✅ 內存使用優化
- ✅ CPU 使用優化
- ✅ 緩存策略

**功能擴展：**
- ✅ 易於添加新方法論
- ✅ 易於添加新指標
- ✅ 易於添加新市場

---

## 8. 版本歷史

| 版本 | 日期 | 變更內容 | 作者 |
|-----|------|---------|------|
| v1.0 | 2026-02-22 | 初始版本，完整技術規格 | Charlie |

---

## 9. 參考文檔

- [OpenAPI 規範](https://swagger.io/specification/)
- [FastAPI 文檔](https://fastapi.tiangolo.com/)
- [React 文檔](https://react.dev/)
- [TypeScript 文檔](https://www.typescriptlang.org/)
- [Playwright 文檔](https://playwright.dev/)

---

**文檔結束**
