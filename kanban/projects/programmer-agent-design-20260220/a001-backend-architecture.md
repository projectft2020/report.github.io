# Dashboard 後端架構完整分析報告

**任務 ID:** a001
**整合任務:** 整合 a001a-a001h 所有分析結果
**生成時間:** 2026-02-21T00:05:00+08:00
**文檔版本:** 1.0
**狀態:** completed

---

## 文檔概述

本文檔整合了 Dashboard 系統後端架構的完整分析，涵蓋 API 路由層、服務層、策略系統、回測引擎、數據訪問層、工具腳本、中間件和認證、測試策略等所有核心模塊。此文檔將作為設計 programmer sub-agent 的核心參考資料，提供完整的後端知識基礎。

**整合的分析報告:**
- a001a: API 路由層分析
- a001b: 服務層分析（未完成，基於推斷）
- a001c: 策略系統分析
- a001d: 回測引擎分析
- a001e: 數據訪問層分析
- a001f: 工具和腳本分析
- a001g: 中間件和認證分析
- a001h: 測試策略分析

---

## 1. 模塊依賴圖

### 1.1 整體架構層級圖

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              PRESENTATION LAYER                                 │
│  ┌──────────────────────────────────────────────────────────────────────────┐  │
│  │                         FRONTEND (React)                                │  │
│  └──────────────────────────────┬───────────────────────────────────────────┘  │
└─────────────────────────────────┼───────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              API GATEWAY LAYER                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │  System     │  │  Auth       │  │  Rate Limit │  │  CORS            │ │
│  │  Middleware │  │  Middleware │  │  Middleware │  │  Middleware      │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘ │
└─────────┼──────────────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │                  │
          ▼                  ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              ROUTER LAYER                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │   Strategies  │  │   Analysis   │  │   Market     │  │   System         │ │
│  │   Router     │  │   Router     │  │   Router     │  │   Router         │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘ │
└─────────┼──────────────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │                  │
          ▼                  ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              SERVICE LAYER                                     │
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │                      Strategy System                                   │  │
│  │  ┌─────────────────────────────────────────────────────────────┐     │  │
│  │  │ StrategyRegistry (Centralized Strategy Management)         │     │  │
│  │  │ • register() / unregister() / get()                          │     │  │
│  │  │ • list_ids() / check_symbol_resonance()                       │     │  │
│  │  └──────────────┬──────────────────────────────────────────────┘     │  │
│  │  ┌──────────────┴──────────────────────────────────────────────┐     │  │
│  │  │ StrategyAggregator (Cross-Strategy Analysis)                │     │  │
│  │  │ • compare_strategies() / analyze_symbol()                   │     │  │
│  │  └─────────────────────────────────────────────────────────────┘     │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │                    Backtesting Engines                                │  │
│  │  ┌──────────────────────┐  ┌──────────────────────┐                 │  │
│  │  │  Backtrader Engine   │  │   VectorBT Engine    │                 │  │
│  │  │  • Event-driven      │  │  • Vectorized       │                 │  │
│  │  │  • Cerebro broker   │  │  • Parameter scan   │                 │  │
│  │  └──────────┬───────────┘  └──────────┬───────────┘                 │  │
│  └─────────────┼───────────────────────────┼─────────────────────────────┘  │
│                │                           │                                 │
│  ┌─────────────┼───────────────────────────┼─────────────────────────────┐  │
│  │  ┌─────────▼────────┐  ┌─────────────▼───────┐  ┌───────────────┐  │  │
│  │  │ Market Data      │  │ Performance         │  │ Risk Analysis │  │  │
│  │  │ Service          │  │ Service             │  │ Service       │  │  │
│  │  └──────────────────┘  └─────────────────────┘  └───────────────┘  │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            REPOSITORY LAYER                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │ Strategy     │  │ Backtest     │  │ Market       │  │ User / Session   │ │
│  │ Repository   │  │ Repository   │  │ Repository   │  │ Repository       │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘ │
└─────────┼──────────────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │                  │
          └──────────────────┼──────────────────┼──────────────────┘
                             │                  │
                             ▼                  ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            STORAGE LAYER                                     │
│  ┌──────────────────────────────────────────────────────────────────────────┐  │
│  │                     DATABASE LAYER                                     │  │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐          │  │
│  │  │   DuckDB       │  │  PostgreSQL    │  │    Redis       │          │  │
│  │  │  • Strategy    │  │  • User Data   │  │  • Cache      │          │  │
│  │  │    Configs    │  │  • Sessions    │  │  • Queue      │          │  │
│  │  │  • Backtest    │  │  • Tasks      │  │  • Sessions   │          │  │
│  │  │    Results    │  │  • Boards     │  │               │          │  │
│  │  └────────────────┘  └────────────────┘  └────────────────┘          │  │
│  └──────────────────────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────────────────┐  │
│  │                     FILE SYSTEM LAYER                                  │  │
│  │  • Reports (Markdown)                                               │  │
│  │  • Converted HTML                                                    │  │
│  │  • Logs & State Files                                                │  │
│  └──────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 模塊依賴關係

```
System (Auth, Config, Health)
    │
    ├─────────────────────┬─────────────────────┬─────────────────────┐
    │                     │                     │                     │
    ▼                     ▼                     ▼                     ▼
Strategies          Analysis            Market              System
Router              Router              Router              Router
    │                     │                     │                     │
    │                     │                     │                     │
    ▼                     ▼                     ▼                     ▼
StrategyRegistry    PerformanceService  MarketDataService   ConfigService
    │                     │                     │                     │
    │                     │                     │                     │
    ├─────────┬───────────┼───────────┬─────────┴─────────┬───────────┤
    │         │           │           │                 │           │
    ▼         ▼           ▼           ▼                 ▼           ▼
Backtrader  VectorBT   Metrics     MarketData       Auth        Session
Engine      Engine      Calculator  Provider         Manager     Manager
    │         │           │           │                 │           │
    └─────────┴───────────┼───────────┴─────────────────┴───────────┘
                          │
                          ▼
                    Repository Layer
                    (Strategy, Backtest,
                     Market, User, Session...)
                          │
                          ▼
                    Storage Layer
                    (DuckDB, PostgreSQL,
                     Redis, File System)
```

### 1.3 關鍵路徑和循環依賴

#### 關鍵路徑
1. **策略回測路徑:** Strategies Router → StrategyRegistry → Backtrader/VectorBT Engine → Backtest Repository → DuckDB
2. **市場數據路徑:** Market Router → MarketDataService → MarketData Provider → Market Repository → PostgreSQL/Redis
3. **用戶認證路徑:** System Router → Auth Middleware → Session Manager → Session Repository → PostgreSQL/Redis
4. **績效分析路徑:** Analysis Router → PerformanceService → Metrics Calculator → Backtest Repository → DuckDB

#### 潛在循環依賴
```
Strategy → Backtest → Analysis → Strategy
         ↓                    ↓
      Execution           Results
         ↑                    ↑
         └────────────────────┘
```

**解決方案:**
- 使用事件驅動架構解耦（Redis Pub/Sub）
- 引入消息隊列（Celery）
- 策略狀態更新通過異步事件傳遞

---

## 2. 完整的 API 端點清單

### 2.1 策略管理端點 (`/api/v1/strategies`)

#### 2.1.1 基礎策略操作

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

#### 2.1.2 回測端點

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

#### 2.1.3 優化端點

| 方法 | 路徑 | 說明 | 認證 |
|------|------|------|------|
| POST | `/api/v1/strategies/{strategy_id}/optimize` | 啟動參數優化 | ✅ |
| GET | `/api/v1/strategies/{strategy_id}/optimize/{opt_id}` | 獲取優化結果 | ✅ |
| GET | `/api/v1/strategies/{strategy_id}/optimize/{opt_id}/progress` | 查詢優化進度 | ✅ |
| GET | `/api/v1/strategies/{strategy_id}/optimizations` | 優化歷史列表 | ✅ |

#### 2.1.4 實盤執行端點

| 方法 | 路徑 | 說明 | 認證 |
|------|------|------|------|
| POST | `/api/v1/strategies/{strategy_id}/execute/start` | 啟動實盤執行 | ✅ |
| POST | `/api/v1/strategies/{strategy_id}/execute/stop` | 停止實盤執行 | ✅ |
| GET | `/api/v1/strategies/{strategy_id}/execution` | 查詢執行狀態 | ✅ |
| PATCH | `/api/v1/strategies/{strategy_id}/execution/params` | 調整執行參數 | ✅ |

### 2.2 分析端點 (`/api/v1/analysis`)

#### 2.2.1 績效分析

| 方法 | 路徑 | 說明 | 認證 |
|------|------|------|------|
| GET | `/api/v1/analysis/performance/{strategy_id}` | 策略績效概覽 | ✅ |
| GET | `/api/v1/analysis/performance/{strategy_id}/metrics` | 詳細績效指標 | ✅ |
| GET | `/api/v1/analysis/performance/{strategy_id}/returns` | 收益率時間序列 | ✅ |
| GET | `/api/v1/analysis/performance/{strategy_id}/drawdown` | 回撤分析 | ✅ |
| GET | `/api/v1/analysis/performance/{strategy_id}/equity` | 權益曲線 | ✅ |

#### 2.2.2 風險分析

| 方法 | 路徑 | 說明 | 認證 |
|------|------|------|------|
| GET | `/api/v1/analysis/risk/{strategy_id}` | 風險概覽 | ✅ |
| GET | `/api/v1/analysis/risk/{strategy_id}/var` | VaR 計算 | ✅ |
| GET | `/api/v1/analysis/risk/{strategy_id}/exposure` | 風險暴露 | ✅ |
| POST | `/api/v1/analysis/risk/{strategy_id}/stress-test` | 壓力測試 | ✅ |

#### 2.2.3 策略對比

| 方法 | 路徑 | 說明 | 認證 |
|------|------|------|------|
| POST | `/api/v1/analysis/compare` | 多策略對比 | ✅ |
| GET | `/api/v1/analysis/compare/{comparison_id}` | 獲取對比結果 | ✅ |
| GET | `/api/v1/analysis/benchmark/{strategy_id}` | 基準對比 | ✅ |

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

### 2.4 系統端點 (`/api/v1/system`)

#### 2.4.1 配置管理

| 方法 | 路徑 | 說明 | 認證 |
|------|------|------|------|
| GET | `/api/v1/system/config` | 獲取系統配置 | ✅ |
| PUT | `/api/v1/system/config` | 更新系統配置 | ✅ |
| GET | `/api/v1/system/config/{key}` | 獲取單個配置 | ✅ |
| POST | `/api/v1/system/config/reset` | 重置配置 | ✅ |

#### 2.4.2 健康檢查

| 方法 | 路徑 | 說明 | 認證 |
|------|------|------|------|
| GET | `/api/v1/system/health` | 系統健康狀態 | ❌ |
| GET | `/api/v1/system/health/detailed` | 詳細健康檢查 | ✅ |
| GET | `/api/v1/system/metrics` | 性能指標 | ✅ |

#### 2.4.3 認證授權

| 方法 | 路徑 | 說明 | 認證 |
|------|------|------|------|
| POST | `/api/v1/auth/login` | 用戶登錄 | ❌ |
| POST | `/api/v1/auth/refresh` | 刷新 Token | ❌ |
| POST | `/api/v1/auth/logout` | 用戶登出 | ✅ |
| GET | `/api/v1/auth/me` | 當前用戶信息 | ✅ |

---

## 3. 關鍵服務類別清單

### 3.1 策略系統服務

#### 3.1.1 StrategyRegistry
**職責:** 全局策略註冊表，管理所有可用策略

**關鍵方法:**
```python
class StrategyRegistry:
    def register(self, strategy_id: str, strategy: Strategy):
        """註冊策略"""
        
    def unregister(self, strategy_id: str):
        """註銷策略"""
        
    def get(self, strategy_id: str) -> Optional[Strategy]:
        """獲取策略實例"""
        
    def list_ids(self) -> List[str]:
        """列出所有策略 ID"""
```

**協作方式:**
- 被所有策略相關服務依賴
- 與 StrategyRepository 交互加載策略配置
- 與 StrategyAggregator 協作進行跨策略分析

#### 3.1.2 StrategyAggregator
**職責:** 跨策略分析和聚合操作

**關鍵方法:**
```python
class StrategyAggregator:
    def check_symbol_resonance(self, symbol: str, strategy_types: List[str]):
        """檢查符號在多個策略中的共振情況"""
        
    def compare_strategies(self, strategy_ids: List[str]):
        """比較多個策略的績效"""
```

**協作方式:**
- 依賴 StrategyRegistry 獲取策略實例
- 為 Analysis Router 提供跨策略分析能力

#### 3.1.3 TechnicalStrategyService
**職責:** 技術指標策略工廠，生成不同類型的策略

**關鍵方法:**
```python
class TechnicalStrategyService:
    def generate_strategy(self, strategy_type: str, universe: str, params: dict):
        """根據策略類型生成策略結果"""
        
    def calc_metrics(self, backtest_result: dict) -> dict:
        """計算回測指標"""
```

**支持的策略類型:**
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Supertrend
- Bollinger Bands
- Momentum
- Dual Momentum
- Sector Rotation
- Extremes
- RSI Trend

### 3.2 回測引擎服務

#### 3.2.1 BacktraderEngine
**職責:** Backtrader 回測引擎封裝

**關鍵方法:**
```python
class BacktraderEngine:
    def __init__(self, config: dict, db_session: Session):
        """初始化引擎"""
        
    def add_strategy(self, strategy_config: dict, risk_params: dict = None):
        """添加策略"""
        
    def add_data(self, symbol: str, start_date: datetime, end_date: datetime):
        """添加數據源"""
        
    def run(self) -> dict:
        """執行回測"""
```

**優化策略:**
- 數據預加載（preload=True）
- 批量查詢減少數據庫訪問
- 支持並行回測（多進程）
- 內存優化（NumPy 數組）

#### 3.2.2 VectorBTExecutor
**職責:** VectorBT 向量化回測執行器

**關鍵方法:**
```python
class VectorBTExecutor:
    def run_backtest(self, strategy_func: Callable, **params) -> dict:
        """執行向量化回測"""
        
    def run_param_scan(self, strategy_func: Callable, param_grid: dict) -> pd.DataFrame:
        """參數掃描"""
```

**優勢:**
- 全向量化運算，極快速度
- 支持批量策略回測
- 自動處理數據對齊
- 內置豐富的分析工具

### 3.3 數據訪問服務

#### 3.3.1 MarketDataService
**職責:** 提供市場數據訪問接口

**關鍵方法:**
```python
class MarketDataService:
    def get_quote(self, symbol: str) -> dict:
        """獲取實時報價"""
        
    def get_historical(self, symbol: str, start_date: date, end_date: date) -> pd.DataFrame:
        """獲取歷史數據"""
        
    def get_ohlc(self, symbol: str, interval: str) -> pd.DataFrame:
        """獲取 K 線數據"""
```

**數據源優先級:**
1. 本地數據庫（最快）
2. Redis 緩存（次快）
3. 外部 API（Yahoo Finance, Alpha Vantage）
4. 數據服務商（Bloomberg, Wind）

#### 3.3.2 Repository Services
**職責:** 封裝數據庫訪問邏輯

**核心 Repository 列表:**
1. **StrategyRepository** - 策略配置管理
2. **BacktestRepository** - 回測結果管理
3. **MarketRepository** - 市場數據管理
4. **UserRepository** - 用戶數據管理
5. **SessionRepository** - 會話管理
6. **TaskRepository** - 任務管理
7. **BoardRepository** - Kanban 板管理
8. **ColumnRepository** - 列管理
9. **LabelRepository** - 標籤管理
10. **CommentRepository** - 評論管理

### 3.4 緩存服務

#### 3.4.1 StrategyCache
**職責:** 帶 TTL 的線程安全緩存

**緩存類型:**
| 緩存名稱 | TTL | 最大大小 | 用途 |
|---------|-----|----------|------|
| `template_cache` | 10 分鐘 | 100 | 策略模板配置 |
| `market_cache` | 15 分鐘 | 50 | 市場配置 |
| `universe_cache` | 10 分鐘 | 50 | 股票宇宙配置 |
| `showcase_cache` | 2 小時 | 200 | 展示數據 |
| `resonance_cache` | 5 分鐘 | 500 | 共振分析結果 |

**關鍵方法:**
```python
class StrategyCache:
    def get(self, key: str) -> Optional[Any]:
        """獲取緩存數據（檢查過期）"""
        
    def set(self, key: str, value: Any, ttl: Optional[timedelta] = None):
        """設置緩存數據（強制最大大小）"""
        
    def clear(self):
        """清除所有緩存"""
```

### 3.5 通知服務

#### 3.5.1 NotificationManager
**職責:** 管理系統通知發送

**支持的通知渠道:**
- Telegram
- Email
- Slack
- WebSocket（實時推送）

**關鍵方法:**
```python
class NotificationManager:
    async def send_notification(self, recipient: str, message: str, channel: str = 'telegram'):
        """發送通知"""
        
    async def send_bulk_notification(self, recipients: List[str], message: str):
        """批量發送通知"""
```

---

## 4. 完整的數據流圖

### 4.1 前端請求到數據庫響應的完整數據流

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         1. 前端請求發起                                      │
└─────────────────────────────────────────────────────────────────────────────────┘

  User Action → React Component
                    │
                    ├──────────────────────────────────────────┐
                    │                                          │
                    ▼                                          ▼
          ┌─────────────────┐                        ┌─────────────────┐
          │ 認證請求        │                        │ 數據請求        │
          │ (Login)         │                        │ (Fetch Data)    │
          └────────┬────────┘                        └────────┬────────┘
                   │                                          │
                   ▼                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         2. API Gateway                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Auth        │  │  Rate Limit  │  │  CORS        │  │  Validation  │  │
│  │  Middleware  │  │  Middleware  │  │  Middleware  │  │  Middleware  │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
└─────────┼──────────────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │                  │
          ▼                  ▼                  ▼                  ▼
    ┌─────────┐        ┌─────────┐        ┌─────────┐        ┌─────────┐
    │ Check   │        │ Limit   │        │ Allow   │        │ Validate│
    │ Token   │        │ Check   │        │ Origin │        │ Schema  │
    └────┬────┘        └────┬────┘        └────┬────┘        └────┬────┘
         │                  │                  │                  │
         └──────────────────┼──────────────────┼──────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         3. Router Layer                                      │
│  ┌──────────────────────────────────────────────────────────────────────────┐  │
│  │                          Router Matching                                │  │
│  └──────────────────────────────────────────────────────────────────────────┘  │
│                                 │                                            │
│                ┌────────────────┴────────────────┐                           │
│                │                                 │                           │
│                ▼                                 ▼                           │
│  ┌───────────────────┐              ┌───────────────────┐                   │
│  │ Strategies Router │              │ System Router      │                   │
│  └─────────┬─────────┘              └─────────┬─────────┘                   │
└────────────┼──────────────────────────────────┼─────────────────────────────────┘
             │                                  │
             ▼                                  ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         4. Service Layer                                     │
│                                                                                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐  │
│  │                      Business Logic Execution                           │  │
│  │                                                                        │  │
│  │  [Auth] → SessionManager → authenticate() → create_session()              │  │
│  │                                                                        │  │
│  │  [Data] → StrategyRegistry → get() → Strategy → generate()               │  │
│  │           ↓                                                              │  │
│  │           MarketDataService → get_historical() → MarketRepository           │  │
│  └──────────────────────────────────────────────────────────────────────────┘  │
│                                 │                                            │
│                                 ▼                                            │
└─────────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         5. Repository Layer                                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐  │
│  │                       Database Operations                               │  │
│  │                                                                        │  │
│  │  [Session] → SessionRepository → findByToken() → UPDATE sessions          │  │
│  │  [Data]    → MarketRepository → findBySymbolAndDate() → SELECT ...         │  │
│  └──────────────────────────────────────────────────────────────────────────┘  │
│                                 │                                            │
│                                 ▼                                            │
└─────────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         6. Storage Layer                                      │
│  ┌──────────────────────────────────────────────────────────────────────────┐  │
│  │                      Database Queries                                    │  │
│  │                                                                        │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │  │
│  │  │  PostgreSQL │  │  DuckDB     │  │   Redis     │                  │  │
│  │  │             │  │             │  │             │                  │  │
│  │  │  SELECT /   │  │  SELECT /   │  │  GET / SET  │                  │  │
│  │  │  INSERT     │  │  INSERT     │  │             │                  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘                  │  │
│  │                                                                        │  │
│  │  ┌──────────────────────────────────────────────────────────────┐         │  │
│  │  │                    Query Optimization                  │         │  │
│  │  │  • Index Usage                                            │         │  │
│  │  │  • Connection Pooling                                     │         │  │
│  │  │  • Query Result Caching                                  │         │  │
│  │  └──────────────────────────────────────────────────────────────┘         │  │
│  └──────────────────────────────────────────────────────────────────────────┘  │
│                                 │                                            │
│                                 ▼                                            │
└─────────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         7. Response Assembly                                   │
│  ┌──────────────────────────────────────────────────────────────────────────┐  │
│  │                      Format Response                                   │  │
│  │                                                                        │  │
│  │  {                                                                     │  │
│  │    "data": { ... },                                                   │  │
│  │    "meta": {                                                           │  │
│  │      "request_id": "req_abc123",                                       │  │
│  │      "timestamp": "2026-02-20T23:38:00Z"                               │  │
│  │    }                                                                  │  │
│  │  }                                                                     │  │
│  └──────────────────────────────────────────────────────────────────────────┘  │
│                                 │                                            │
│                                 ▼                                            │
└─────────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         8. Frontend Update                                     │
└─────────────────────────────────────────────────────────────────────────────────┘

  API Response → React Component → State Update → UI Render
```

### 4.2 策略執行的數據流

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    STRATEGY EXECUTION DATA FLOW                                │
└─────────────────────────────────────────────────────────────────────────────────┘

  [1] STRATEGY CREATION                    [2] STRATEGY REGISTRATION
  ─────────────────────                    ───────────────────────
  
  ┌──────────────┐                        ┌──────────────┐
  │ POST /strategies│ ───────────────────▶ │ Strategy     │
  │ {            │                        │ Registry     │
  │  name: "...", │   ┌─────────────────▶ │ .register()  │
  │  type: "...", │   │                └──────────────┘
  │  params: {}  │   │                         │
  │ }            │   │                         ▼
  └──────────────┘   │              ┌──────────────┐
                     │              │ Strategy     │
                     │              │ Repository  │
                     │              │ .save()     │
                     │              └──────┬───────┘
                     │                     │
                     └─────────────────────┘

  [3] BACKTEST SUBMISSION                 [4] DATA LOADING
  ─────────────────────                  ────────────────
  
  ┌──────────────┐                        ┌──────────────┐
  │ POST /backtest│ ───────────────────▶ │ Market Data  │
  │ {            │                        │ Service      │
  │  strategy_id │   ┌─────────────────▶ │ .get_       │
  │  symbols: [] │   │                │ historical() │
  │  dates: {}   │   │                └──────┬───────┘
  │ }            │   │                       │
  └──────────────┘   │                       ▼
                     │              ┌──────────────┐
                     │              │ Market       │
                     │              │ Repository   │
                     │              │ .query()     │
                     │              └──────┬───────┘
                     │                     │
                     └─────────────────────┘
                                        │
                                        ▼
  [5] ENGINE SELECTION                   [6] BACKTEST EXECUTION
  ─────────────────────                  ────────────────
  
  ┌──────────────┐                        ┌──────────────┐
  │ Engine       │ ───────────────────▶ │ Backtrader   │
  │ Selector     │   ┌─────────────────▶ │ / VectorBT   │
  │              │   │                │ Executor     │
  └──────────────┘   │                └──────┬───────┘
                     │                       │
                     │                       ▼
                     │              ┌──────────────┐
                     │              │ Signal       │
                     │              │ Generation   │
                     │              │ → Order      │
                     │              │   Execution  │
                     │              └──────┬───────┘
                     │                     │
                     └─────────────────────┘
                                        │
                                        ▼
  [7] RESULT CALCULATION                 [8] RESULT STORAGE
  ─────────────────────                  ────────────────
  
  ┌──────────────┐                        ┌──────────────┐
  │ Metrics      │ ───────────────────▶ │ Backtest     │
  │ Calculator   │   ┌─────────────────▶ │ Repository   │
  │              │   │                │ .save()      │
  └──────────────┘   │                └──────┬───────┘
                     │                       │
                     │                       ▼
                     │              ┌──────────────┐
                     │              │ DuckDB /     │
                     │              │ PostgreSQL   │
                     │              │ INSERT ...   │
                     │              └──────────────┘
                     │
                     └─────────────────────┘

  [9] CACHE UPDATE                      [10] RESPONSE
  ─────────────────                      ────────────
  
  ┌──────────────┐                        ┌──────────────┐
  │ Strategy     │ ───────────────────▶ │ API Response │
  │ Cache        │   ┌─────────────────▶ │ {            │
  │ .set()       │   │                │  data: {}    │
  │              │   │                │  meta: {}    │
  └──────────────┘   │                │ }            │
                     │                └──────────────┘
                     │                       │
                     │                       ▼
                     │              ┌──────────────┐
                     │              │ Frontend     │
                     │              │ State Update │
                     │              └──────────────┘
                     │
                     └─────────────────────┘
```

### 4.3 回測執行的數據流

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      BACKTEST EXECUTION DATA FLOW                                │
└─────────────────────────────────────────────────────────────────────────────────┘

  [1] REQUEST                    [2] VALIDATE                [3] LOAD CONFIG
  ──────────                    ──────────                ──────────────
  
  ┌──────────────┐              ┌──────────────┐           ┌──────────────┐
  │ POST /run    │ ──────────▶ │ Check        │ ────────▶ │ StrategyConfig│
  │ {            │              │ strategy_id  │           │ Service.get() │
  │  strategy_id │              │ exists?      │           │              │
  │  symbols: [] │              │              │           │ params = {...}│
  │  start_date  │              │              │           │ market = 'US'│
  │  end_date    │              │              │           │ template =...│
  │ }            │              │              │           └──────┬───────┘
  └──────────────┘              └──────────────┘                  │
                                                                  ▼
  [4] NORMALIZE TEMPLATE           [5] BUILD SERVICE           [6] EXECUTE
  ────────────────────────         ──────────────               ──────────
  
  ┌──────────────┐                ┌──────────────┐            ┌──────────────┐
  │ template_name │                │ Technical   │            │ generate_    │
  │ "rsi_tw"     │ ─────────────▶ │ Strategy    │ ─────────▶ │ strategy()   │
  │        ↓     │                │ Service     │            │              │
  │ "rsi"        │                │              │            │ raw_result = │
  └──────────────┘                └──────────────┘            │ {            │
                                                                  │  stats: {}  │
                                                                  │  return_    │
                                                                  │  series: [] │
                                                                  │  trades: [] │
                                                                  │ }           │
                                                                  └──────┬───────┘
                                                                         │
  [7] TRANSFORM RESULT            [8] GENERATE RUN_ID          [9] SAVE TO DB
  ─────────────────────            ─────────────────            ────────────
  
  ┌──────────────┐                ┌──────────────┐            ┌──────────────┐
  │ metrics = {  │                │ run_id =     │            │ INSERT INTO  │
  │  total_return│                │ uuid.uuid4() │ ─────────▶ │ backtest_    │
  │  cagr: 0.15  │ ─────────────▶ │ created_at = │            │ runs (       │
  │  sharpe: 1.2 │                │ now()        │            │   run_id,    │
  │  mdd: -0.08  │                │ completed_at │            │   strategy_id│
  │ }            │                │ = now()      │            │   metrics,   │
  └──────┬───────┘                └──────────────┘            │   equity_    │
         │                                                    │   curve,     │
         ▼                                                    │   ...        │
  ┌──────────────┐                                              └──────────────┘
  │ response = { │
  │  run_id: "...│
  │  metrics: {} │
  │  final_value│
  │  equity_curve│
  │ }            │
  └──────┬───────┘
         │
         ▼
  [10] RETURN RESPONSE
       ─────────────────
       JSON response to frontend
```

---

## 5. 完整的技術棧清單

### 5.1 後端框架和庫

#### 5.1.1 核心框架
| 技術 | 版本 | 用途 |
|------|------|------|
| **FastAPI** | 0.100+ | Web 框架，提供高性能 API |
| **Pydantic** | v2 | 數據驗證和序列化 |
| **SQLAlchemy** | 2.0+ | ORM 框架，數據庫抽象層 |
| **Alembic** | 1.10+ | 數據庫遷移工具 |

#### 5.1.2 回測引擎
| 技術 | 版本 | 用途 |
|------|------|------|
| **Backtrader** | 1.9.78+ | 事件驅動回測引擎 |
| **VectorBT** | 0.25+ | 向量化回測引擎 |
| **NumPy** | 1.24+ | 數值計算基礎庫 |
| **Pandas** | 2.0+ | 數據處理和分析 |

#### 5.1.3 數據處理
| 技術 | 版本 | 用途 |
|------|------|------|
| **DuckDB** | 0.9+ | 內嵌分析型數據庫 |
| **psycopg2** | 2.9+ | PostgreSQL 適配器 |
| **redis-py** | 4.5+ | Redis 客戶端 |
| **celery** | 5.2+ | 分布式任務隊列 |

#### 5.1.4 工具庫
| 技術 | 版本 | 用途 |
|------|------|------|
| **python-jose** | 3.3+ | JWT 生成和驗證 |
| **passlib** | 1.7+ | 密碼哈希（bcrypt） |
| **python-multipart** | 0.0.5+ | 文件上傳支持 |
| **uvicorn** | 0.23+ | ASGI 服務器 |
| **gunicorn** | 21.2+ | WSGI 服務器（生產環境）|

### 5.2 數據庫和存儲

#### 5.2.1 關係型數據庫
| 數據庫 | 版本 | 用途 |
|--------|------|------|
| **PostgreSQL** | 15+ | 用戶數據、會話、任務 |
| **DuckDB** | 0.9+ | 策略配置、回測結果、市場數據 |

#### 5.2.2 緩存和消息隊列
| 技術 | 版本 | 用途 |
|--------|------|------|
| **Redis** | 7+ | 緩存、會話存儲、消息隊列 |
| **Celery** | 5.2+ | 異步任務執行（broker: Redis）|

#### 5.2.3 文件存儲
| 類型 | 用途 |
|------|------|
| **本地文件系統** | 報告（Markdown）、轉換後 HTML、日誌 |
| **Git Repository** | 版本控制、發布管理 |

### 5.3 測試框架

| 技術 | 版本 | 用途 |
|------|------|------|
| **pytest** | 7.4+ | 單元測試框架 |
| **pytest-asyncio** | 0.21+ | 異步測試支持 |
| **httpx** | 0.24+ | HTTP 客戶端測試 |
| **unittest** | Python 內建 | 單元測試基礎框架 |
| **自訂測試框架** | - | SystemTester, EnhancedReportConverter |

### 5.4 開發工具

#### 5.4.1 代碼質量
| 工具 | 用途 |
|------|------|
| **black** | 代碼格式化 |
| **flake8** | 代碼風格檢查 |
| **mypy** | 類型檢查 |
| **pylint** | 代碼質量分析 |

#### 5.4.2 CI/CD
| 工具 | 用途 |
|------|------|
| **GitHub Actions** | 持續集成/持續部署 |
| **Docker** | 容器化部署 |
| **Docker Compose** | 本地開發環境 |

#### 5.4.3 監控和日誌
| 工具 | 用途 |
|------|------|
| **Prometheus** | 指標收集和監控 |
| **Grafana** | 可視化儀表板 |
| **ELK Stack** | 日誌收集和分析 |
| **OpenTelemetry** | 分散式追蹤 |

---

## 6. 架構原則和最佳實踐

### 6.1 代碼組織原則

#### 6.1.1 模塊化設計
```
backend/
├── routers/              # 路由層（API 端點）
│   ├── strategies/
│   │   ├── __init__.py
│   │   ├── backtest.py
│   │   ├── monte_carlo.py
│   │   ├── comparison.py
│   │   └── ...
│   ├── analysis/
│   ├── system/
│   ├── market.py
│   └── ...
├── services/             # 服務層（業務邏輯）
│   ├── strategies/
│   │   ├── strategy_registry.py
│   │   ├── technical_strategy.py
│   │   └── ...
│   ├── market_data_service.py
│   ├── performance_service.py
│   └── ...
├── repositories/         # 數據訪問層
│   ├── strategy_repository.py
│   ├── backtest_repository.py
│   └── ...
├── models/              # 數據模型
├── schemas/             # Pydantic 模型（請求/響應）
├── core/                # 核心配置和工具
│   ├── config.py
│   ├── security.py
│   ├── cache.py
│   └── exceptions.py
├── workers/             # 後台任務（Celery）
│   ├── backtest_worker.py
│   └── optimization_worker.py
└── main.py              # 應用入口
```

#### 6.1.2 關注點分離
- **Router 層:** 只處理 HTTP 請求/響應，不包含業務邏輯
- **Service 層:** 處理業務邏輯，協調多個 Repository
- **Repository 層:** 只負責數據庫操作
- **Model 層:** 定義數據結構

#### 6.1.3 依賴注入
```python
# 使用 FastAPI 的依賴注入
from fastapi import Depends

def get_current_user(token: str = Depends(oauth2_scheme)):
    """獲取當前用戶"""
    return decode_token(token)

@router.get("/strategies")
async def get_strategies(
    user: User = Depends(get_current_user),
    service: StrategyService = Depends()
):
    """獲取用戶的策略列表"""
    return service.get_user_strategies(user.id)
```

### 6.2 API 設計規範

#### 6.2.1 RESTful 原則
| 原則 | 實現 |
|------|------|
| 使用名詞復數 | `/strategies`, `/orders` |
| 資源導航 | `/strategies/{id}/backtest` |
| HTTP 方法語義 | GET（查詢）、POST（創建）、PUT（更新）、DELETE（刪除）|
| 狀態碼語義 | 200（成功）、201（創建）、400（錯誤）、404（未找到）|

#### 6.2.2 統一響應格式
```json
// 成功響應
{
  "data": { /* 實際數據 */ },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2026-02-20T23:38:00Z"
  }
}

// 錯誤響應
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

#### 6.2.3 分頁和篩選
```python
# 通用查詢參數
class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    sort_by: Optional[str] = None
    order: str = Field("desc", regex="^(asc|desc)$")

class FilterParams(BaseModel):
    status: Optional[str] = None
    type: Optional[str] = None
    search: Optional[str] = None
```

### 6.3 錯誤處理策略

#### 6.3.1 統一異常類
```python
from fastapi import HTTPException, status

class StrategyNotFound(HTTPException):
    def __init__(self, strategy_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Strategy {strategy_id} not found",
            headers={"X-Error-Code": "STRATEGY_NOT_FOUND"}
        )

class ValidationFailed(HTTPException):
    def __init__(self, errors: List[dict]):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "errors": errors
            }
        )
```

#### 6.3.2 全局異常處理器
```python
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.headers.get("X-Error-Code", "HTTP_ERROR"),
                "message": exc.detail,
            },
            "meta": {
                "request_id": request.state.request_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )
```

### 6.4 日誌和監控策略

#### 6.4.1 結構化日誌
```python
import logging
import json

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        
    def log(self, level: str, message: str, **kwargs):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            "context": kwargs
        }
        self.logger.info(json.dumps(log_entry))

# 使用
logger = StructuredLogger(__name__)
logger.log("INFO", "Strategy created", strategy_id="str_123", user_id="user_456")
```

#### 6.4.2 關鍵指標
```python
from prometheus_client import Counter, Histogram

# 請求計數
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# 請求延遲
request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

# 回測計數
backtest_count = Counter(
    'backtests_total',
    'Total backtests executed',
    ['strategy_type', 'status']
)
```

### 6.5 安全最佳實踐

#### 6.5.1 認證安全
| 實踐 | 實現 |
|------|------|
| 密碼哈希 | 使用 bcrypt，salt rounds = 12 |
| JWT 簽名 | 使用 RS256 或 HS256 |
| Token 過期 | Access Token 1 小時，Refresh Token 7 天 |
| 速率限制 | 登錄 5 次/分鐘，API 100 次/分鐘 |

#### 6.5.2 輸入驗證
```python
from pydantic import BaseModel, Field, validator

class StrategyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: StrategyType
    parameters: Dict
    
    @validator('name')
    def name_must_not_contain_special_chars(cls, v):
        if any(c in v for c in '<>"/\\|?*'):
            raise ValueError('名稱不能包含特殊字符')
        return v
```

#### 6.5.3 SQL 注入防護
- 使用 SQLAlchemy ORM（參數化查詢）
- 避免 SQL 字符串拼接
- 使用 Alembic 管理數據庫遷移

### 6.6 測試最佳實踐

#### 6.6.1 測試金字塔
```
        /\
       /E2E\           少量
      /──────\
     / 集成 \          中量
    /────────\
   /  單元  \         大量
  /──────────\
```

#### 6.6.2 測試覆蓋率
- **目標覆蓋率:** 80% 以上
- **關鍵路徑覆蓋率:** 100%
- **異常處理覆蓋率:** 100%

#### 6.6.3 測試隔離
- 每個測試獨立運行
- 使用測試數據庫（不污染生產數據）
- Mock 外部依賴（如 API 調用）

---

## 7. 潛在改進點

### 7.1 技術債務

| 項目 | 描述 | 優先級 |
|------|------|--------|
| **服務層實現不完整** | a001b 分析無法完成，服務層缺少具體實現 | 高 |
| **緩存策略不一致** | 多種緩存實現，缺少統一接口 | 中 |
| **錯誤處理不統一** | 部分端點使用不同錯誤格式 | 中 |
| **缺少 API 版本控制** | 所有端點在 `/api/v1/`，缺少版本遷移策略 | 低 |

### 7.2 架構瓶頸

| 瓶頸 | 描述 | 影響 | 建議 |
|------|------|------|------|
| **同步回測** | Backtrader 回測同步執行，阻塞 API 響應 | 高 | 使用 Celery 異步任務 |
| **數據庫連接池** | PostgreSQL 連接池可能不夠大 | 中 | 增加連接池大小或使用連接池監控 |
| **緩存命中率** | 某些緩存 TTL 過短，命中率低 | 低 | 優化緩存策略，增加 TTL |
| **單點故障** | Redis 單節點，如果宕機影響系統 | 高 | 使用 Redis Sentinel 或 Cluster |

### 7.3 建議改進方向

#### 7.3.1 短期改進（1-2 週）
1. **完成服務層分析**
   - 定位並訪問 `backend/services/` 目錄
   - 補充服務層架構分析
   - 更新此文檔

2. **統一錯誤處理**
   - 創建統一的異常類庫
   - 實現全局異常處理器
   - 更新所有端點使用統一格式

3. **增加 API 文檔**
   - 完善 OpenAPI/Swagger 文檔
   - 添加更多示例和說明
   - 自動生成客戶端 SDK

#### 7.3.2 中期改進（1-2 個月）
1. **異步回測系統**
   ```python
   # 使用 Celery 實現異步回測
   @celery_app.task(bind=True)
   def run_backtest_task(self, strategy_id: str, config: dict):
       """異步回測任務"""
       try:
           # 執行回測
           result = execute_backtest(strategy_id, config)
           # 保存結果
           save_backtest_result(result)
           return result
       except Exception as e:
           # 錯誤處理
           handle_backtest_error(self.request.id, e)
           raise
   ```

2. **緩存層重構**
   - 實現統一的緩存接口
   - 支持多級緩存（L1: Redis, L2: 本地）
   - 自動緩存失效機制

3. **監控和告警系統**
   - 集成 Prometheus 指標
   - 設置 Grafana 儀表板
   - 配置告警規則（如回測失敗、API 響應時間過長）

#### 7.3.3 長期改進（3-6 個月）
1. **微服務架構遷移**
   - 將策略系統獨立為微服務
   - 將回測引擎獨立為微服務
   - 使用 API Gateway 統一入口

2. **實時流處理**
   - 使用 Kafka 或 RabbitMQ 處理實時市場數據
   - 實現流式回測
   - 支援實時策略調整

3. **機器學習集成**
   - 使用 ML 模型優化策略參數
   - 實現自適應策略
   - 異常檢測和風險預警

---

## 8. Programmer Sub-Agent 的後端知識基礎

### 8.1 關鍵後端能力要求

#### 8.1.1 核心技術能力
| 能力 | 要求 | 優先級 |
|------|------|--------|
| **Python/FastAPI 開發** | 熟練使用 FastAPI 構建 RESTful API | 高 |
| **設計模式應用** | 理解並應用策略模式、工廠模式、適配器模式等 | 高 |
| **數據庫優化** | 熟悉 PostgreSQL、DuckDB 的查詢優化 | 高 |
| **異步編程** | 掌握 Python async/await 和 Celery 任務隊列 | 高 |
| **測驅動開發** | 能夠編寫單元測試、集成測試、E2E 測試 | 中 |

#### 8.1.2 領域知識
| 領域 | 要求 | 優先級 |
|------|------|--------|
| **交易策略理解** | 理解常見技術指標策略（RSI, MACD, 均線交叉等）| 高 |
| **回測原理** | 理解回測執行流程、滑點、手續費等概念 | 高 |
| **績效指標** | 理解夏普比率、最大回撤、CAGR 等指標計算 | 高 |
| **數據結構** | 理解時間序列數據（OHLCV）的特點 | 中 |

#### 8.1.3 安全知識
| 能力 | 要求 | 優先級 |
|------|------|--------|
| **認證授權** | 理解 JWT、OAuth 2.0、RBAC 等機制 | 高 |
| **輸入驗證** | 能夠實現嚴格的輸入驗證和清理 | 高 |
| **SQL 注入防護** | 理解並實施防護措施 | 高 |
| **XSS/CSRF 防護** | 理解 Web 安全漏洞及防護 | 中 |

### 8.2 後端模塊優先級

#### 8.2.1 第一優先級（核心基礎）
1. **數據訪問層（Repository）**
   - 理由：所有模塊的基礎
   - 估計時間：3-5 天
   - 交付物：完整的 Repository 接口和實現

2. **API 路由層（Router）**
   - 理由：與前端直接交互
   - 估計時間：5-7 天
   - 交付物：所有 API 端點實現

3. **認證授權（Middleware）**
   - 理由：安全基礎
   - 估計時間：3-5 天
   - 交付物：JWT 認證、RBAC 實現

#### 8.2.2 第二優先級（業務邏輯）
4. **策略系統（Strategy System）**
   - 理由：核心功能
   - 估計時間：7-10 天
   - 交付物：策略註冊、策略執行、緩存

5. **回測引擎（Backtesting Engine）**
   - 理由：核心功能
   - 估計時間：10-14 天
   - 交付物：Backtrader 和 VectorBT 集成

6. **市場數據服務（Market Data Service）**
   - 理由：策略執行的依賴
   - 估計時間：5-7 天
   - 交付物：數據獲取、緩存、優化

#### 8.2.3 第三優先級（增強功能）
7. **績效分析服務（Performance Service）**
   - 理由：增強功能
   - 估計時間：5-7 天
   - 交付物：指標計算、可視化數據生成

8. **通知服務（Notification Service）**
   - 理由：用戶體驗增強
   - 估計時間：3-5 天
   - 交付物：Telegram/Email/Slack 通知

9. **監控和日誌（Monitoring & Logging）**
   - 理由：運維支持
   - 估計時間：5-7 天
   - 交付物：Prometheus 指標、Grafana 儀表板

### 8.3 後端開發工作流程

#### 8.3.1 需求分析階段
1. **理解需求**
   - 閱讀需求文檔
   - 與產品經理確認細節
   - 識別技術挑戰

2. **設計 API**
   - 定義 API 端點
   - 設計請求/響應格式
   - 編寫 OpenAPI 文檔

3. **設計數據模型**
   - 定義數據庫表結構
   - 設計實體關係
   - 編寫遷移腳本

#### 8.3.2 開發階段
4. **實現 Repository 層**
   - 創建數據訪問類
   - 編寫單元測試
   - 驗證查詢性能

5. **實現 Service 層**
   - 創建業務邏輯類
   - 實現核心算法
   - 編寫集成測試

6. **實現 Router 層**
   - 創建 API 端點
   - 集成中間件
   - 編寫 API 測試

#### 8.3.3 測試階段
7. **單元測試**
   - 測試每個函數和類
   - 目標覆蓋率 > 80%
   - Mock 外部依賴

8. **集成測試**
   - 測試組件間交互
   - 使用測試數據庫
   - 驗證數據流

9. **E2E 測試**
   - 測試完整用戶流程
   - 模擬真實環境
   - 驗證端到端行為

#### 8.3.4 部署階段
10. **代碼審查**
    - Pull Request 審查
    - 檢查代碼質量
    - 驗證功能完整性

11. **CI/CD 流程**
    - 自動化測試執行
    - 構建和打包
    - 部署到測試環境

12. **生環境部署**
    - 藍綠部署或滾動更新
    - 監控部署健康狀態
    - 準備回滾方案

#### 8.3.5 維護階段
13. **監控和告警**
    - 監控關鍵指標
    - 設置告警規則
    - 響應告警事件

14. **日誌分析**
    - 分析錯誤日誌
    - 識別性能瓶頸
    - 優化系統性能

15. **持續改進**
    - 收集用戶反饋
    - 規劃新功能
    - 優化現有功能

---

## 9. 總結

本文檔整合了 Dashboard 系統後端架構的完整分析，涵蓋了從 API 路由層、服務層、策略系統、回測引擎、數據訪問層、工具腳本、中間件和認證、測試策略等所有核心模塊。

### 9.1 關鍵發現

1. **架構成熟度:** 系統採用了分層架構，模塊化程度高，職責清晰。

2. **技術選型合理:** FastAPI + SQLAlchemy + DuckDB/PostgreSQL 的組合提供了良好的性能和靈活性。

3. **設計模式豐富:** 策略模式、工廠模式、適配器模式、聚合器模式等設計模式的應用，提高了系統的可擴展性。

4. **測試覆蓋全面:** 從單元測試到 E2E 測試，測試框架完善，測試質量高。

5. **工具鏈完整:** 自動化工具腳本涵蓋了從監控、轉換到 Git 操作和發布的完整流程。

### 9.2 待改進項目

1. **服務層分析不完整:** a001b 分析無法完成，需要補充服務層架構分析。

2. **異步處理待完善:** 回測執行目前為同步方式，建議改為異步處理。

3. **緩存策略待優化:** 多種緩存實現，缺少統一接口。

4. **監控系統待建立:** 缺少完整的監控和告警系統。

### 9.3 Programmer Sub-Agent 應用建議

此文檔為設計和實現 programmer sub-agent 提供了完整的後端知識基礎：

1. **理解整體架構:** 從 API 層到存儲層的完整架構圖
2. **掌握關鍵技術:** Python/FastAPI、SQLAlchemy、回測引擎等
3. **遵循最佳實踐:** 代碼組織、API 設計、錯誤處理、安全等
4. **按優先級開發:** 核心基礎 → 標業務邏輯 → 增強功能
5. **遵循開發流程:** 需求分析 → 開發 → 測試 → 部署 → 維護

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
- [Backtrader 文檔](https://www.backtrader.com/)
- [VectorBT 文檔](https://vectorbt.dev/)

---

**文檔版本:** 1.0
**最後更新:** 2026-02-21
**維護者:** Charlie Analyst
**下一階段:** 基於此文檔設計 programmer sub-agent
