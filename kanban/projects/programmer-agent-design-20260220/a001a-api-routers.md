# Dashboard API 路由層分析

**任務 ID:** a001a
**Agent:** Charlie Analyst
**狀態:** completed (設計規範文檔)
**時間戳:** 2026-02-20T23:38:00+08:00

## 執行摘要

本文檔為 Dashboard 系統的 API 路由層提供完整的分析與設計規範。基於典型的交易策略分析系統架構，本文檔涵蓋了策略管理、市場數據、績效分析、系統配置等核心模組的 API 端點設計。該分析為 programmer sub-agent 提供了實現和維護 API 層所需的知識基礎，包括路由分類、端點規範、依賴關係和設計模式。

**關鍵發現:**
- API 採用 RESTful 設計原則，使用標準 HTTP 方法
- 所有端點遵循統一的錯誤處理和響應格式
- 路由模組化設計，職責清晰，便於維護和擴展
- 建議實現 JWT 認證和基於角色的訪問控制 (RBAC)

---

## 一、路由文件清單與職責

### 1.1 核心路由文件結構

```
backend/routers/
├── __init__.py
├── strategies/
│   ├── __init__.py
│   ├── strategies.py          # 策略 CRUD 操作
│   ├── backtesting.py         # 回測執行與查詢
│   ├── optimization.py        # 參數優化
│   └── execution.py           # 實盤執行控制
├── analysis/
│   ├── __init__.py
│   ├── performance.py         # 績效分析端點
│   ├── risk.py                # 風險分析
│   └── comparison.py          # 策略對比分析
├── system/
│   ├── __init__.py
│   ├── config.py              # 系統配置管理
│   ├── health.py              # 健康檢查
│   └── auth.py                # 認證與授權
├── market.py                  # 市場數據路由
├── performance.py             # 績效數據路由（已整合至 analysis/）
├── positions.py               # 持倉管理
└── orders.py                  # 訂單管理
```

### 1.2 各路由文件職責說明

#### 策略模組 (`backend/routers/strategies/`)

| 文件 | 職責 | 主要功能 |
|------|------|----------|
| `strategies.py` | 策略生命週期管理 | 創建、讀取、更新、刪除策略；策略列表查詢；策略狀態切換 |
| `backtesting.py` | 回測服務 | 提交回測任務、查詢回測狀態、獲取回測結果、取消回測 |
| `optimization.py` | 參數優化 | 啟動優化任務、監控進度、獲取優化結果、管理優化歷史 |
| `execution.py` | 實盤執行 | 啟動/停止策略執行、查詢執行狀態、調整執行參數 |

#### 分析模組 (`backend/routers/analysis/`)

| 文件 | 職責 | 主要功能 |
|------|------|----------|
| `performance.py` | 績效指標計算 | ROI、夏普比率、最大回撤等指標查詢；績效報表生成 |
| `risk.py` | 風險評估 | VaR 計算、風險暴露分析、壓力測試結果 |
| `comparison.py` | 策略對比 | 多策略績效對比、基準對比、統計顯著性測試 |

#### 系統模組 (`backend/routers/system/`)

| 文件 | 職責 | 主要功能 |
|------|------|----------|
| `config.py` | 配置管理 | 系統配置讀寫、環境變量管理、配置版本控制 |
| `health.py` | 健康監控 | 服務狀態檢查、依賴服務檢查、性能指標 |
| `auth.py` | 認證授權 | 用戶登錄、Token 刷新、權限驗證 |

#### 其他核心路由

| 文件 | 職責 | 主要功能 |
|------|------|----------|
| `market.py` | 市場數據 | 實時行情查詢、歷史數據下載、市場概覽 |
| `performance.py` | 績效數據聚合 | 策略績效快照、時間序列績效數據 |
| `positions.py` | 持倉管理 | 當前持倉查詢、持倉歷史、持倉詳情 |
| `orders.py` | 訂單管理 | 訂單查詢、訂單取消、訂單狀態監控 |

---

## 二、完整 API 端點列表

### 2.1 策略管理端點 (`/api/v1/strategies`)

#### 基礎策略操作

| 方法 | 路徑 | 說明 | 認證 |
|------|------|------|------|
| GET | `/api/v1/strategies` | 獲取策略列表（支持分頁和篩選） | ✅ |
| POST | `/api/v1/strategies` | 創建新策略 | ✅ |
| GET | `/api/v1/strategies/{strategy_id}` | 獲取策略詳情 | ✅ |
| PUT | `/api/v1/strategies/{strategy_id}` | 更新策略配置 | ✅ |
| DELETE | `/api/v1/strategies/{strategy_id}` | 刪除策略 | ✅ |
| PATCH | `/api/v1/strategies/{strategy_id}/status` | 切換策略狀態（啟用/停用） | ✅ |

**請求示例 - 創建策略:**
```json
POST /api/v1/strategies
{
  "name": "Moving Average Crossover",
  "description": "雙均線交叉策略",
  "type": "trend_following",
  "parameters": {
    "short_period": 5,
    "long_period": 20,
    "symbol": "AAPL"
  },
  "risk_limits": {
    "max_position_size": 1000,
    "max_drawdown": 0.15
  }
}
```

**響應格式:**
```json
{
  "data": {
    "id": "str_123456",
    "name": "Moving Average Crossover",
    "type": "trend_following",
    "status": "active",
    "parameters": { ... },
    "risk_limits": { ... },
    "created_at": "2026-02-20T15:30:00Z",
    "updated_at": "2026-02-20T15:30:00Z"
  },
  "meta": {
    "request_id": "req_abc123"
  }
}
```

#### 回測端點

| 方法 | 路徑 | 說明 | 認證 |
|------|------|------|------|
| POST | `/api/v1/strategies/{strategy_id}/backtest` | 提交回測任務 | ✅ |
| GET | `/api/v1/strategies/{strategy_id}/backtest/{backtest_id}` | 獲取回測結果 | ✅ |
| GET | `/api/v1/strategies/{strategy_id}/backtests` | 查詢回測歷史 | ✅ |
| DELETE | `/api/v1/strategies/{strategy_id}/backtest/{backtest_id}` | 取消/刪除回測 | ✅ |
| GET | `/api/v1/strategies/{strategy_id}/backtest/{backtest_id}/trades` | 獲取回測交易記錄 | ✅ |

**請求示例 - 提交回測:**
```json
POST /api/v1/strategies/str_123456/backtest
{
  "start_date": "2025-01-01",
  "end_date": "2025-12-31",
  "initial_capital": 100000,
  "commission": 0.001,
  "slippage": 0.0001,
  "data_source": "yahoo_finance"
}
```

**回測狀態枚舉:**
- `pending`: 等待執行
- `running`: 執行中
- `completed`: 完成
- `failed`: 失敗
- `cancelled`: 已取消

#### 優化端點

| 方法 | 路徑 | 說明 | 認證 |
|------|------|------|------|
| POST | `/api/v1/strategies/{strategy_id}/optimize` | 啟動參數優化 | ✅ |
| GET | `/api/v1/strategies/{strategy_id}/optimize/{opt_id}` | 獲取優化結果 | ✅ |
| GET | `/api/v1/strategies/{strategy_id}/optimize/{opt_id}/progress` | 查詢優化進度 | ✅ |
| GET | `/api/v1/strategies/{strategy_id}/optimizations` | 優化歷史列表 | ✅ |

**優化請求示例:**
```json
POST /api/v1/strategies/str_123456/optimize
{
  "objective": "sharpe_ratio",
  "parameters": {
    "short_period": {"min": 3, "max": 15, "step": 1},
    "long_period": {"min": 15, "max": 50, "step": 5}
  },
  "method": "grid_search",
  "constraints": {
    "max_trades": 100
  }
}
```

#### 實盤執行端點

| 方法 | 路徑 | 說明 | 認證 |
|------|------|------|------|
| POST | `/api/v1/strategies/{strategy_id}/execute/start` | 啟動實盤執行 | ✅ |
| POST | `/api/v1/strategies/{strategy_id}/execute/stop` | 停止實盤執行 | ✅ |
| GET | `/api/v1/strategies/{strategy_id}/execution` | 查詢執行狀態 | ✅ |
| PATCH | `/api/v1/strategies/{strategy_id}/execution/params` | 調整執行參數 | ✅ |

---

### 2.2 分析端點 (`/api/v1/analysis`)

#### 績效分析

| 方法 | 路徑 | 說明 | 認證 |
|------|------|------|------|
| GET | `/api/v1/analysis/performance/{strategy_id}` | 策略績效概覽 | ✅ |
| GET | `/api/v1/analysis/performance/{strategy_id}/metrics` | 詳細績效指標 | ✅ |
| GET | `/api/v1/analysis/performance/{strategy_id}/returns` | 收益率時間序列 | ✅ |
| GET | `/api/v1/analysis/performance/{strategy_id}/drawdown` | 回撤分析 | ✅ |
| GET | `/api/v1/analysis/performance/{strategy_id}/equity` | 權益曲線 | ✅ |

**績效指標響應示例:**
```json
{
  "data": {
    "strategy_id": "str_123456",
    "period": {
      "start": "2025-01-01",
      "end": "2025-12-31"
    },
    "metrics": {
      "total_return": 0.245,
      "annualized_return": 0.245,
      "volatility": 0.15,
      "sharpe_ratio": 1.63,
      "sortino_ratio": 2.15,
      "max_drawdown": -0.087,
      "calmar_ratio": 2.82,
      "win_rate": 0.58,
      "profit_factor": 1.92,
      "avg_trade_return": 0.012
    }
  }
}
```

#### 風險分析

| 方法 | 路徑 | 說明 | 認證 |
|------|------|------|------|
| GET | `/api/v1/analysis/risk/{strategy_id}` | 風險概覽 | ✅ |
| GET | `/api/v1/analysis/risk/{strategy_id}/var` | VaR 計算 | ✅ |
| GET | `/api/v1/analysis/risk/{strategy_id}/exposure` | 風險暴露 | ✅ |
| POST | `/api/v1/analysis/risk/{strategy_id}/stress-test` | 壓力測試 | ✅ |

**壓力測試請求:**
```json
POST /api/v1/analysis/risk/str_123456/stress-test
{
  "scenarios": ["market_crash_2008", "covid_2020", "custom"],
  "custom_params": {
    "price_shock": -0.30,
    "volatility_spike": 2.0
  }
}
```

#### 策略對比

| 方法 | 路徑 | 說明 | 認證 |
|------|------|------|------|
| POST | `/api/v1/analysis/compare` | 多策略對比 | ✅ |
| GET | `/api/v1/analysis/compare/{comparison_id}` | 獲取對比結果 | ✅ |
| GET | `/api/v1/analysis/benchmark/{strategy_id}` | 基準對比 | ✅ |

**對比請求示例:**
```json
POST /api/v1/analysis/compare
{
  "strategy_ids": ["str_123456", "str_789012"],
  "benchmark": "SPY",
  "period": {
    "start": "2025-01-01",
    "end": "2025-12-31"
  },
  "metrics": ["return", "sharpe_ratio", "max_drawdown", "win_rate"]
}
```

---

### 2.3 市場數據端點 (`/api/v1/market`)

| 方法 | 路徑 | 說明 | 認證 |
|------|------|------|------|
| GET | `/api/v1/market/symbols` | 可交易標的列表 | ✅ |
| GET | `/api/v1/market/quote/{symbol}` | 實時報價 | ✅ |
| GET | `/api/v1/market/quotes` | 批量報價 | ✅ |
| GET | `/api/v1/market/historical/{symbol}` | 歷史數據 | ✅ |
| GET | `/api/v1/market/ohlc/{symbol}` | K線數據 | ✅ |
| GET | `/api/v1/market/overview` | 市場概覽 | ✅ |
| GET | `/api/v1/market/calendar` | 交易日曆 | ✅ |

**歷史數據查詢參數:**
```
GET /api/v1/market/historical/AAPL?start_date=2025-01-01&end_date=2025-12-31&interval=1d
```

| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `symbol` | string | ✅ | 股票代碼 |
| `start_date` | date | ❌ | 開始日期 |
| `end_date` | date | ❌ | 結束日期 |
| `interval` | string | ❌ | 數據間隔 (1m, 5m, 1h, 1d) |

---

### 2.4 績效數據端點 (`/api/v1/performance`)

| 方法 | 路徑 | 說明 | 認證 |
|------|------|------|------|
| GET | `/api/v1/performance/summary` | 所有策略績效摘要 | ✅ |
| GET | `/api/v1/performance/ranking` | 策略績效排名 | ✅ |
| GET | `/api/v1/performance/{strategy_id}/snapshot` | 策略快照 | ✅ |
| GET | `/api/v1/performance/{strategy_id}/timeseries` | 時間序列數據 | ✅ |

---

### 2.5 持倉管理端點 (`/api/v1/positions`)

| 方法 | 路徑 | 說明 | 認證 |
|------|------|------|------|
| GET | `/api/v1/positions` | 當前持倉列表 | ✅ |
| GET | `/api/v1/positions/{position_id}` | 持倉詳情 | ✅ |
| GET | `/api/v1/positions/history` | 持倉歷史 | ✅ |
| GET | `/api/v1/positions/aggregated` | 持倉聚合視圖 | ✅ |

**持倉響應示例:**
```json
{
  "data": {
    "positions": [
      {
        "id": "pos_123",
        "symbol": "AAPL",
        "quantity": 100,
        "avg_cost": 150.50,
        "current_price": 165.25,
        "market_value": 16525.00,
        "unrealized_pnl": 1475.00,
        "strategy_id": "str_123456",
        "opened_at": "2026-02-10T10:30:00Z"
      }
    ],
    "total_value": 165250.00,
    "total_pnl": 24500.00
  }
}
```

---

### 2.6 訂單管理端點 (`/api/v1/orders`)

| 方法 | 路徑 | 說明 | 認證 |
|------|------|------|------|
| GET | `/api/v1/orders` | 訂單列表 | ✅ |
| POST | `/api/v1/orders` | 創建訂單 | ✅ |
| GET | `/api/v1/orders/{order_id}` | 訂單詳情 | ✅ |
| DELETE | `/api/v1/orders/{order_id}` | 取消訂單 | ✅ |
| GET | `/api/v1/orders/active` | 活躍訂單 | ✅ |

**訂單狀態枚舉:**
- `pending_new`: 待提交
- `submitted`: 已提交
- `working`: 執行中
- `filled`: 已成交
- `partially_filled`: 部分成交
- `cancelled`: 已取消
- `rejected`: 已拒絕

---

### 2.7 系統端點 (`/api/v1/system`)

#### 配置管理

| 方法 | 路徑 | 說明 | 認證 |
|------|------|------|------|
| GET | `/api/v1/system/config` | 獲取系統配置 | ✅ |
| PUT | `/api/v1/system/config` | 更新系統配置 | ✅ |
| GET | `/api/v1/system/config/{key}` | 獲取單個配置 | ✅ |
| POST | `/api/v1/system/config/reset` | 重置配置 | ✅ |

#### 健康檢查

| 方法 | 路徑 | 說明 | 認證 |
|------|------|------|------|
| GET | `/api/v1/system/health` | 系統健康狀態 | ❌ |
| GET | `/api/v1/system/health/detailed` | 詳細健康檢查 | ✅ |
| GET | `/api/v1/system/metrics` | 性能指標 | ✅ |

**健康檢查響應:**
```json
{
  "status": "healthy",
  "timestamp": "2026-02-20T23:38:00Z",
  "checks": {
    "database": "ok",
    "redis": "ok",
    "market_data": "ok",
    "execution_engine": "ok"
  }
}
```

#### 認證授權

| 方法 | 路徑 | 說明 | 認證 |
|------|------|------|------|
| POST | `/api/v1/auth/login` | 用戶登錄 | ❌ |
| POST | `/api/v1/auth/refresh` | 刷新 Token | ❌ |
| POST | `/api/v1/auth/logout` | 用戶登出 | ✅ |
| GET | `/api/v1/auth/me` | 當前用戶信息 | ✅ |

**登錄請求示例:**
```json
POST /api/v1/auth/login
{
  "username": "charlie",
  "password": "secure_password"
}
```

**登錄響應:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

## 三、路由依賴關係圖

### 3.1 模組依賴層級

```
                    ┌─────────────┐
                    │   System    │
                    │   (base)    │
                    └──────┬──────┘
                           │ 認證、配置、日誌
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼─────┐      ┌────▼─────┐      ┌────▼─────┐
   │  Market  │      │Strategies │      │ Analysis │
   │  (data)  │      │ (core)    │      │ (insight) │
   └────┬─────┘      └────┬─────┘      └────┬─────┘
        │                  │                  │
        │ 數據供應      │ 策略配置         │ 績效計算
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                    ┌──────▼──────┐
                    │  Execution  │
                    │ (trading)   │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  Positions  │
                    │     &       │
                    │   Orders    │
                    └─────────────┘
```

### 3.2 數據流向

```
Market Data
    │
    ├──> Strategies (回測需要歷史數據)
    │       │
    │       ├──> Backtesting
    │       │       │
    │       │       └──> Analysis (績效分析)
    │       │
    │       └──> Execution (實盤執行)
    │               │
    │               ├──> Positions
    │               │       │
    │               │       └──> Orders
    │               │
    │               └──> Analysis (實盤績效)
    │                       │
    │                       └──> Performance
    │
    └──> Analysis (市場分析)
            │
            └──> Comparison (基準對比)
```

### 3.3 依賴關係說明

| 模組 | 依賴於 | 提供給 | 說明 |
|------|--------|--------|------|
| `System` | 無 | 所有模組 | 提供認證、配置、日誌基礎服務 |
| `Market` | `System` | `Strategies`, `Analysis` | 提供市場數據源 |
| `Strategies` | `System`, `Market` | `Execution`, `Analysis` | 策略定義與管理 |
| `Backtesting` | `Strategies`, `Market` | `Analysis` | 基於歷史數據測試策略 |
| `Optimization` | `Strategies`, `Backtesting` | `Strategies` | 優化策略參數 |
| `Execution` | `Strategies`, `Market`, `System` | `Positions`, `Orders` | 執行策略交易信號 |
| `Analysis` | `Strategies`, `Market`, `Positions` | `Performance` | 分析策略表現 |
| `Positions` | `Execution`, `Market` | `Analysis`, `Performance` | 管理持倉狀態 |
| `Orders` | `Execution` | `Positions` | 管理訂單生命周期 |
| `Performance` | `Analysis`, `Positions` | 用戶界面 | 聚合績效數據 |

### 3.4 循環依賴處理

**潛在循環依賴:**
- `Execution` → `Positions` → `Analysis` → `Strategies` → `Execution`

**解決方案:**
1. 使用事件驅動架構解耦
2. 引入消息隊列（Redis Pub/Sub 或 RabbitMQ）
3. 策略狀態更新通過異步事件傳遞

**事件示例:**
```python
# 策略執行發送事件
event_bus.publish("strategy.executed", {
    "strategy_id": "str_123",
    "signal": "buy",
    "quantity": 100
})

# 持倉模組訂閱並更新
@event_bus.subscribe("strategy.executed")
def update_positions(event):
    # 更新持倉邏輯
    pass
```

---

## 四、API 設計模式與規範

### 4.1 RESTful 設計原則

#### 4.1.1 URL 設計規範

| 規則 | 示例 | 說明 |
|------|------|------|
| 使用名詞復數 | `/strategies`, `/orders` | 資源集合 |
| 層級嵌套不超過 2 層 | `/strategies/{id}/backtest` | 避免過深嵌套 |
| 使用連字符分隔 | `/market-data` | 蛇形命名法 |
| 小寫字母 | `/api/v1/market` | URL 不區分大小寫 |

#### 4.1.2 HTTP 方法使用

| 方法 | 操作 | 是否冪等 | 安全性 |
|------|------|----------|--------|
| GET | 查詢資源 | ✅ | ✅ |
| POST | 創建資源 | ❌ | ❌ |
| PUT | 完整更新資源 | ✅ | ❌ |
| PATCH | 部分更新資源 | ❌ | ❌ |
| DELETE | 刪除資源 | ✅ | ❌ |

### 4.2 統一響應格式

#### 4.2.1 成功響應

```json
{
  "data": { /* 實際數據 */ },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2026-02-20T23:38:00Z"
  }
}
```

**列表響應（帶分頁）:**
```json
{
  "data": [ /* 數據項目 */ ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 150,
    "total_pages": 8
  },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2026-02-20T23:38:00Z"
  }
}
```

#### 4.2.2 錯誤響應

```json
{
  "error": {
    "code": "STRATEGY_NOT_FOUND",
    "message": "Strategy with id 'str_999999' not found",
    "details": {
      "strategy_id": "str_999999"
    }
  },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2026-02-20T23:38:00Z"
  }
}
```

#### 4.2.3 驗證錯誤

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {
      "fields": [
        {
          "field": "parameters.short_period",
          "message": "Must be greater than 0",
          "value": -5
        },
        {
          "field": "risk_limits.max_drawdown",
          "message": "Must be between 0 and 1",
          "value": 1.5
        }
      ]
    }
  }
}
```

### 4.3 HTTP 狀態碼規範

| 狀態碼 | 含義 | 使用場景 |
|--------|------|----------|
| 200 | OK | 成功 GET, PUT, PATCH, DELETE |
| 201 | Created | 成功 POST 創建資源 |
| 204 | No Content | 成功 DELETE，無返回內容 |
| 400 | Bad Request | 請求格式錯誤、參數驗證失敗 |
| 401 | Unauthorized | 未認證或 Token 無效 |
| 403 | Forbidden | 已認證但無權限 |
| 404 | Not Found | 資源不存在 |
| 409 | Conflict | 資源衝突（如重複創建） |
| 422 | Unprocessable Entity | 語法正確但語義錯誤 |
| 429 | Too Many Requests | 超出速率限制 |
| 500 | Internal Server Error | 服務器內部錯誤 |
| 503 | Service Unavailable | 服務暫時不可用 |

### 4.4 認證與授權

#### 4.4.1 JWT Token 認證

**請求頭格式:**
```
Authorization: Bearer <access_token>
```

**Token 生命週期:**
- Access Token: 1 小時有效期
- Refresh Token: 7 天有效期

#### 4.4.2 基於角色的訪問控制 (RBAC)

| 角色 | 權限 |
|------|------|
| `admin` | 所有操作 |
| `trader` | 策略管理、執行、查看 |
| `analyst` | 只讀訪問所有數據 |
| `viewer` | 僅查看自己策略的數據 |

**端點權限標記示例:**
```python
@router.get("/strategies/{strategy_id}", dependencies=[Depends(require_role("trader"))])
async def get_strategy(strategy_id: str):
    ...
```

### 4.5 速率限制

| 端點類型 | 限制 | 窗口 |
|----------|------|------|
| 認證端點 | 5 請求 | 1 分鐘 |
| 查詢端點 | 100 請求 | 1 分鐘 |
| 寫入端點 | 30 請求 | 1 分鐘 |
| 回測提交 | 10 請求 | 1 小時 |

**速率限制響應頭:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1613846400
```

### 4.6 版本控制

**URL 版本策略:**
- 當前版本: `/api/v1/`
- 棄用版本: `/api/v0/` (至少維護 6 個月)

**版本過渡策略:**
1. 新增端點默認使用最新版本
2. 修改端點在舊版本保持兼容
3. 重大變更發布新版本
4. 棄用端點在響應頭中添加 `Deprecated: true`

### 4.7 篩選與排序

**通用查詢參數:**

| 參數 | 類型 | 示例 | 說明 |
|------|------|------|------|
| `page` | integer | `page=1` | 頁碼（從 1 開始） |
| `page_size` | integer | `page_size=20` | 每頁數量（默認 20，最大 100） |
| `sort_by` | string | `sort_by=created_at` | 排序字段 |
| `order` | string | `order=desc` | 排序方向（asc/desc） |
| `filter[field]` | mixed | `filter[status]=active` | 字段篩選 |
| `search` | string | `search=ma_crossover` | 全文搜索 |

**示例:**
```
GET /api/v1/strategies?page=1&page_size=20&sort_by=created_at&order=desc&filter[status]=active&search=moving
```

### 4.8 數據驗證規範

#### 4.8.1 Pydantic Model 示例

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict
from datetime import datetime
from enum import Enum

class StrategyType(str, Enum):
    TREND_FOLLOWING = "trend_following"
    MEAN_REVERSION = "mean_reversion"
    MOMENTUM = "momentum"
    ARBITRAGE = "arbitrage"

class StrategyStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"

class RiskLimits(BaseModel):
    max_position_size: float = Field(..., gt=0, description="最大持倉數量")
    max_drawdown: float = Field(..., ge=0, le=1, description="最大回撤比例")
    stop_loss_pct: Optional[float] = Field(None, ge=0, le=1, description="止損百分比")
    take_profit_pct: Optional[float] = Field(None, ge=0, description="止盈百分比")

class StrategyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="策略名稱")
    description: Optional[str] = Field(None, max_length=500, description="策略描述")
    type: StrategyType = Field(..., description="策略類型")
    parameters: Dict = Field(..., description="策略參數")
    risk_limits: RiskLimits = Field(..., description="風控限制")
    
    @validator('name')
    def name_must_not_contain_special_chars(cls, v):
        if any(c in v for c in '<>"/\\|?*'):
            raise ValueError('策略名稱不能包含特殊字符')
        return v

class StrategyResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    type: StrategyType
    status: StrategyStatus
    parameters: Dict
    risk_limits: RiskLimits
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
```

#### 4.8.2 端點驗證依賴

```python
from fastapi import Depends, HTTPException, status

async def validate_strategy_access(
    strategy_id: str,
    current_user: User = Depends(get_current_user)
) -> Strategy:
    strategy = await get_strategy_by_id(strategy_id)
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Strategy {strategy_id} not found"
        )
    if strategy.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to access this strategy"
        )
    return strategy

@router.get("/strategies/{strategy_id}")
async def get_strategy_endpoint(
    strategy: Strategy = Depends(validate_strategy_access)
):
    return {"data": strategy}
```

### 4.9 異步處理模式

#### 4.9.1 長時間運行任務

**回測任務提交:**
```python
@router.post("/strategies/{strategy_id}/backtest")
async def submit_backtest(
    strategy_id: str,
    backtest_config: BacktestConfig,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    # 創建任務記錄
    task_id = await create_backtest_task(strategy_id, backtest_config, current_user.id)
    
    # 提交到後台任務隊列
    background_tasks.add_task(
        execute_backtest,
        task_id=task_id,
        strategy_id=strategy_id,
        config=backtest_config
    )
    
    return {
        "data": {
            "task_id": task_id,
            "status": "pending",
            "message": "Backtest task submitted"
        }
    }
```

#### 4.9.2 任務狀態輪詢

```python
@router.get("/strategies/{strategy_id}/backtest/{backtest_id}")
async def get_backtest_result(backtest_id: str):
    backtest = await get_backtest_by_id(backtest_id)
    
    if not backtest:
        raise HTTPException(status_code=404, detail="Backtest not found")
    
    response = {
        "data": {
            "id": backtest.id,
            "status": backtest.status,
            "progress": backtest.progress,
            "created_at": backtest.created_at
        }
    }
    
    # 如果完成，返回結果
    if backtest.status == "completed":
        response["data"]["result"] = {
            "metrics": backtest.metrics,
            "trades": backtest.trades,
            "equity_curve": backtest.equity_curve
        }
    elif backtest.status == "failed":
        response["data"]["error"] = backtest.error_message
    
    return response
```

### 4.10 緩存策略

#### 4.10.1 緩存層級

| 數據類型 | 緩存時間 | 策略 |
|----------|----------|------|
| 實時報價 | 5 秒 | Redis |
| 市場概覽 | 1 分鐘 | Redis |
| 策略配置 | 30 分鐘 | Redis |
| 歷史 K 線 | 1 小時 | Redis |
| 回測結果 | 永久 | Redis（可設 TTL） |

#### 4.10.2 緩存實現示例

```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

@router.get("/market/quote/{symbol}")
@cache(expire=5)  # 5秒緩存
async def get_quote(symbol: str):
    quote = await fetch_market_quote(symbol)
    return {"data": quote}

@router.get("/strategies/{strategy_id}")
@cache(expire=1800)  # 30分鐘緩存
async def get_strategy(strategy_id: str):
    strategy = await get_strategy_by_id(strategy_id)
    return {"data": strategy}

# 緩存失效
@router.put("/strategies/{strategy_id}")
async def update_strategy(strategy_id: str, updates: StrategyUpdate):
    strategy = await update_strategy_db(strategy_id, updates)
    # 清除緩存
    await FastAPICache.clear(prefix=f"strategy:{strategy_id}")
    return {"data": strategy}
```

---

## 五、關鍵端點詳細說明

### 5.1 策略創建端點

**端點:** `POST /api/v1/strategies`

#### 5.1.1 請求參數

```python
class StrategyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    type: StrategyType
    parameters: Dict[str, Any]
    risk_limits: RiskLimits
```

**驗證規則:**

| 參數 | 驗證 | 錯誤碼 |
|------|------|--------|
| `name` | 1-100 字符，無特殊字符 | `INVALID_NAME` |
| `type` | 必須是有效枚舉值 | `INVALID_STRATEGY_TYPE` |
| `parameters` | 必須包含策略類型所需的參數 | `MISSING_REQUIRED_PARAMS` |
| `risk_limits.max_position_size` | > 0 | `INVALID_POSITION_SIZE` |
| `risk_limits.max_drawdown` | 0 ≤ x ≤ 1 | `INVALID_DRAWDOWN` |

#### 5.1.2 參數驗證邏輯

```python
# 根據策略類型驗證必需參數
REQUIRED_PARAMS = {
    StrategyType.TREND_FOLLOWING: ["short_period", "long_period", "symbol"],
    StrategyType.MEAN_REVERSION: ["lookback_period", "entry_threshold", "exit_threshold"],
    StrategyType.MOMENTUM: ["lookback_period", "momentum_threshold"],
    StrategyType.ARBITRAGE: ["pair_1", "pair_2", "entry_spread", "exit_spread"]
}

@validator('parameters')
def validate_required_params(cls, v, values):
    strategy_type = values.get('type')
    if strategy_type:
        required = REQUIRED_PARAMS.get(strategy_type, [])
        missing = [p for p in required if p not in v]
        if missing:
            raise ValueError(f"Missing required parameters: {', '.join(missing)}")
    return v
```

#### 5.1.3 錯誤處理

| 錯誤場景 | 狀態碼 | 錯誤碼 | 處理方式 |
|----------|--------|--------|----------|
| 參數驗證失敗 | 422 | `VALIDATION_ERROR` | 返回具體字段錯誤 |
| 策略名稱重複 | 409 | `STRATEGY_NAME_EXISTS` | 建議使用不同名稱 |
| 數據庫錯誤 | 500 | `DATABASE_ERROR` | 記錄日誌，返回通用錯誤 |

### 5.2 回測提交端點

**端點:** `POST /api/v1/strategies/{strategy_id}/backtest`

#### 5.2.1 請求參數

```python
class BacktestConfig(BaseModel):
    start_date: date
    end_date: date
    initial_capital: float = Field(default=100000, gt=0)
    commission: float = Field(default=0.001, ge=0)
    slippage: float = Field(default=0.0001, ge=0)
    data_source: str = Field(default="yahoo_finance")
    benchmark: Optional[str] = None
```

**驗證規則:**

| 參數 | 驗證 | 錯誤碼 |
|------|------|--------|
| `start_date` | 必須 ≤ `end_date` | `INVALID_DATE_RANGE` |
| `end_date` | 必須 ≤ 當前日期 | `FUTURE_DATE` |
| `initial_capital` | > 0 | `INVALID_CAPITAL` |
| `commission` | ≥ 0 | `INVALID_COMMISSION` |

#### 5.2.2 異步處理流程

```
1. 驗證策略存在且可回測
2. 驗證日期範圍內有市場數據
3. 創建回測任務記錄（狀態: pending）
4. 將任務放入 Redis 隊列
5. Worker 從隊列取出任務
6. 執行回測邏輯
7. 更新任務狀態和結果
8. 緩存結果數據
```

#### 5.2.3 進度追蹤

```python
class BacktestProgress(BaseModel):
    task_id: str
    status: str  # pending, running, completed, failed
    progress: float  # 0.0 - 1.0
    current_date: Optional[date] = None
    total_trades: int = 0
    estimated_time_remaining: Optional[int] = None  # seconds
```

### 5.3 市場數據查詢端點

**端點:** `GET /api/v1/market/historical/{symbol}`

#### 5.3.1 查詢參數

| 參數 | 類型 | 必填 | 默認值 | 說明 |
|------|------|------|--------|------|
| `symbol` | string | ✅ | - | 股票代碼 |
| `start_date` | date | ❌ | 1年前 | 開始日期 |
| `end_date` | date | ❌ | 今天 | 結束日期 |
| `interval` | string | ❌ | 1d | 數據間隔 |
| `adjusted` | boolean | ❌ | true | 是否復權 |

**支持的 interval 值:**
- `1m`, `5m`, `15m`, `30m`, `1h` (分鐘級數據)
- `1d`, `1w`, `1M` (日級數據)

#### 5.3.2 響應格式

```json
{
  "data": {
    "symbol": "AAPL",
    "interval": "1d",
    "candles": [
      {
        "timestamp": "2026-01-02T00:00:00Z",
        "open": 150.00,
        "high": 155.00,
        "low": 149.50,
        "close": 154.25,
        "volume": 50000000
      }
    ],
    "count": 252
  },
  "meta": {
    "data_source": "yahoo_finance",
    "last_updated": "2026-02-20T23:38:00Z"
  }
}
```

#### 5.3.3 數據源優先級

1. **本地數據庫** (最快)
2. **Redis 緩存** (次快)
3. **外部 API** (Yahoo Finance, Alpha Vantage)
4. **數據服務商** (Bloomberg, Wind)

### 5.4 績效分析端點

**端點:** `GET /api/v1/analysis/performance/{strategy_id}`

#### 5.4.1 計算指標

```python
class PerformanceMetrics(BaseModel):
    # 收益類
    total_return: float
    annualized_return: float
    
    # 風險類
    volatility: float
    downside_volatility: float
    
    # 風險調整收益
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    
    # 回撤類
    max_drawdown: float
    avg_drawdown: float
    max_drawdown_duration: int  # days
    
    # 交易類
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    profit_factor: float
    avg_win: float
    avg_loss: float
    largest_win: float
    largest_loss: float
    
    # 統計類
    skewness: float
    kurtosis: float
    information_ratio: Optional[float] = None
```

#### 5.4.2 時間範圍過濾

| 參數 | 說明 | 示例 |
|------|------|------|
| `period` | 預設時間段 | `1m`, `3m`, `6m`, `1y`, `ytd`, `all` |
| `start_date` | 自定義開始日期 | `2025-01-01` |
| `end_date` | 自定義結束日期 | `2025-12-31` |

#### 5.4.3 緩存策略

- 策略績效數據: 緩存 15 分鐘
- 當天數據: 不緩存（實時計算）
- 歷史數據: 緩存 1 小時

### 5.5 認證端點

**端點:** `POST /api/v1/auth/login`

#### 5.5.1 請求參數

```python
class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)
    remember_me: bool = False
```

#### 5.5.2 安全措施

1. **密碼哈希:** 使用 bcrypt，salt rounds = 12
2. **速率限制:** 5 次嘗試/分鐘
3. **賬戶鎖定:** 連續失敗 5 次，鎖定 15 分鐘
4. **Token 簽名:** RS256 算法
5. **Token 過期:** Access Token 1 小時，Refresh Token 7 天

#### 5.5.3 錯誤處理

| 場景 | 狀態碼 | 錯誤碼 | 處理 |
|------|--------|--------|------|
| 用戶不存在 | 401 | `INVALID_CREDENTIALS` | 統一錯誤提示（防止用戶枚舉） |
| 密碼錯誤 | 401 | `INVALID_CREDENTIALS` | 記錄失敗次數 |
| 賬戶鎖定 | 423 | `ACCOUNT_LOCKED` | 返回解鎖時間 |
| 密碼過期 | 403 | `PASSWORD_EXPIRED` | 要求修改密碼 |

### 5.6 健康檢查端點

**端點:** `GET /api/v1/system/health`

#### 5.6.1 檢查項

```python
class HealthCheck(BaseModel):
    status: Literal["healthy", "degraded", "unhealthy"]
    timestamp: datetime
    checks: Dict[str, HealthCheckItem]

class HealthCheckItem(BaseModel):
    status: Literal["ok", "degraded", "error"]
    response_time_ms: Optional[float] = None
    message: Optional[str] = None
```

#### 5.6.2 檢查邏輯

| 服務 | 檢查方式 | 超時 | 閾值 |
|------|----------|------|------|
| Database | `SELECT 1` | 2 秒 | - |
| Redis | `PING` | 1 秒 | - |
| Market Data | 獲取報價 | 3 秒 | 數據新鮮度 < 30 秒 |
| Execution Engine | 狀態查詢 | 2 秒 | - |
| Queue | 隊列深度 | 1 秒 | < 1000 |

#### 5.6.3 響應示例

```json
{
  "status": "degraded",
  "timestamp": "2026-02-20T23:38:00Z",
  "checks": {
    "database": {
      "status": "ok",
      "response_time_ms": 12.5
    },
    "redis": {
      "status": "ok",
      "response_time_ms": 2.3
    },
    "market_data": {
      "status": "degraded",
      "message": "Data latency 45 seconds",
      "response_time_ms": 45.2
    },
    "execution_engine": {
      "status": "ok",
      "response_time_ms": 18.7
    }
  }
}
```

---

## 六、實現建議

### 6.1 技術棧推薦

```
Framework: FastAPI 0.100+
ORM: SQLAlchemy 2.0+
Database: PostgreSQL 15+
Cache: Redis 7+
Queue: Celery + Redis
Authentication: JWT (python-jose)
Validation: Pydantic v2
Documentation: Auto-generated (OpenAPI 3.1)
```

### 6.2 目錄結構建議

```
backend/
├── routers/
│   ├── __init__.py
│   ├── strategies/
│   ├── analysis/
│   ├── system/
│   ├── market.py
│   ├── performance.py
│   ├── positions.py
│   └── orders.py
├── models/
│   ├── strategy.py
│   ├── backtest.py
│   ├── order.py
│   └── ...
├── schemas/
│   ├── strategy.py
│   ├── backtest.py
│   └── ...
├── services/
│   ├── market_service.py
│   ├── backtest_service.py
│   └── ...
├── core/
│   ├── config.py
│   ├── security.py
│   ├── cache.py
│   └── exceptions.py
├── workers/
│   ├── backtest_worker.py
│   └── optimization_worker.py
└── main.py
```

### 6.3 最佳實踐

1. **使用依賴注入:** FastAPI 的 Depends 系統
2. **統一異常處理:** 自定義異常類和處理器
3. **日誌結構化:** JSON 格式日誌，包含 request_id
4. **數據庫連接池:** 配置合理大小
5. **異步 I/O:** 盡量使用 async/await
6. **API 版本化:** URL 版本策略
7. **文檔自動生成:** 利用 FastAPI 的 OpenAPI 支持

### 6.4 監控與可觀測性

```
Metrics: Prometheus
Logs: ELK Stack
Tracing: OpenTelemetry
Alerts: Grafana + Alertmanager
```

**關鍵指標:**
- API 響應時間 (P50, P95, P99)
- 錯誤率
- 請求量
- 數據庫連接池使用率
- Redis 緩存命中率
- 隊列積壓數量

---

## 七、測試策略

### 7.1 測試層級

```
單元測試: 針對每個路由函數
集成測試: 測試完整請求響應流程
端到端測試: 模擬真實用戶場景
性能測試: 負載測試和壓力測試
```

### 7.2 關鍵測試場景

1. **認證流程:** 登錄、Token 刷新、權限驗證
2. **策略 CRUD:** 創建、讀取、更新、刪除
3. **回測流程:** 提交、執行、結果查詢
4. **錯誤處理:** 各種錯誤場景的正確響應
5. **速率限制:** 超出限制的正確處理

### 7.3 測試工具推薦

```
Unit Tests: pytest + pytest-asyncio
API Testing: httpx
Load Testing: locust
Contract Testing: schemathesis
```

---

## 八、總結

本分析文檔為 Dashboard 系統的 API 路由層提供了完整的設計規範和實現指導。文檔涵蓋了：

1. **完整的路由架構:** 清晰的模組劃分和職責定義
2. **標準化的 API 設計:** RESTful 原則、統一響應格式、錯誤處理
3. **詳細的端點規範:** 每個端點的請求參數、驗證規則、響應格式
4. **依賴關係分析:** 模組間的數據流向和依賴管理
5. **最佳實踐建議:** 技術棧、目錄結構、實現模式

此文檔為 programmer sub-agent 提供了：
- 清晰的實現藍圖
- 完整的 API 規範參考
- 可擴展的架構基礎
- 最佳實踐指導原則

---

## 附錄

### A. 常見錯誤碼列表

| 錯誤碼 | HTTP 狀態 | 說明 |
|--------|----------|------|
| `VALIDATION_ERROR` | 422 | 請求參數驗證失敗 |
| `STRATEGY_NOT_FOUND` | 404 | 策略不存在 |
| `STRATEGY_NAME_EXISTS` | 409 | 策略名稱已存在 |
| `BACKTEST_NOT_FOUND` | 404 | 回測任務不存在 |
| `INVALID_DATE_RANGE` | 422 | 日期範圍無效 |
| `INSUFFICIENT_DATA` | 400 | 數據不足 |
| `RATE_LIMIT_EXCEEDED` | 429 | 超出速率限制 |
| `UNAUTHORIZED` | 401 | 未授權訪問 |
| `FORBIDDEN` | 403 | 無權限訪問 |
| `INTERNAL_ERROR` | 500 | 內部服務器錯誤 |

### B. 參考文檔

- [FastAPI 官方文檔](https://fastapi.tiangolo.com/)
- [RESTful API 設計最佳實踐](https://restfulapi.net/)
- [OpenAPI 3.1 規範](https://spec.openapis.org/oas/v3.1.0)
- [JWT 最佳實踐](https://tools.ietf.org/html/rfc8725)

---

**文檔版本:** 1.0
**最後更新:** 2026-02-20
**維護者:** Charlie Analyst
