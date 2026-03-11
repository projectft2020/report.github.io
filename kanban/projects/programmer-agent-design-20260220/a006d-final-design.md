# Programmer Sub-Agent 最終設計規劃

**文檔 ID:** a006d-final
**版本:** 1.0
**狀態:** Final
**創建日期:** 2026-02-21
**最後更新:** 2026-02-21
**適用對象:** Programmer Sub-Agent 實施團隊
**基於文件:**
- a005-competencies.md (高級架構師能力定義)
- a006a-5.md (統一知識庫)
- a006c-1.md (實施路徑框架)
- a006c-2.md (評估指標和方法)
- a006c-3.md (代碼和文檔)
- a006-design-plan.md (設計規劃)

---

## 目錄

1. [概述和目標](#1-概述和目標)
2. [核心設計原則](#2-核心設計原則)
3. [能力模型和技能矩陣](#3-能力模型和技能矩陣)
4. [統一知識庫](#4-統一知識庫)
5. [實施路徑框架](#5-實施路徑框架)
6. [評估指標和方法](#6-評估指標和方法)
7. [實踐項目清單](#7-實踐項目清單)
8. [風險管理和後備方案](#8-風險管理和後備方案)
9. [時間線和里程碑](#9-時間線和里程碑)
10. [結論和建議](#10-結論和建議)

---

## 1. 概述和目標

### 1.1 項目背景

Programmer Sub-Agent 是專為 Dashboard 量化交易系統設計的智能編程助手。本設計規劃基於系統的完整技術架構分析，提供一套**完整的能力建設、知識整合和實施指南**，確保 Sub-Agent 能夠從初級開發者逐步成長為高級架構師。

Dashboard 系統採用**前後端分離架構**、**統一策略引擎**、**微服務化後端**、**測試驅動開發**，具備**完善的 CI/CD 基礎設施**和**嚴格的代碼規範**。

### 1.2 核心目標

| 目標類別 | 具體目標 | 成功指標 | 優先級 |
|---------|---------|---------|--------|
| **能力建設** | 建立從初級到架構師的完整能力模型 | 4 階段路徑覆蓋率 100% | P0 |
| **知識整合** | 統一後端、前端、策略引擎、Git 開發模式知識庫 | 知識庫覆蓋率 ≥ 95% | P0 |
| **質量保證** | 建立測試驅動開發和代碼審查文化 | 測試覆蓋率 ≥ 80%，審查通過率 ≥ 90% | P0 |
| **持續改進** | 建立評估機制和反饋循環 | 每季度評估一次，改進措施執行率 ≥ 80% | P1 |
| **風險管理** | 識別和緩解實施風險 | 風險緩解覆蓋率 100% | P1 |

### 1.3 技術棧概覽

```
┌─────────────────────────────────────────────────────────────────┐
│                        前端層 (Frontend)                        │
│  React 19 + Vite + Zustand + React Query + Bootstrap 5        │
├─────────────────────────────────────────────────────────────────┤
│                        API 網關層 (API Gateway)                   │
│  FastAPI Middleware (Auth, CORS, Rate Limit)                   │
├─────────────────────────────────────────────────────────────────┤
│                        後端服務層 (Backend Services)             │
│  策略服務 | 市場數據服務 | 分析服務 | 執行服務                  │
├─────────────────────────────────────────────────────────────────┤
│                        策略引擎層 (Strategy Engine)              │
│  IStrategy 接口 | VectorBT | Backtrader | Signal Adapter      │
├─────────────────────────────────────────────────────────────────┤
│                        數據存儲層 (Storage)                      │
│  PostgreSQL | DuckDB | Redis | File System                    │
├─────────────────────────────────────────────────────────────────┤
│                        開發工具層 (DevTools)                    │
│  Git | GitHub Actions | Docker | pytest | Vitest               │
└─────────────────────────────────────────────────────────────────┘
```

### 1.4 預期成果

| 類別 | 具體成果 | 驗證方式 |
|------|---------|---------|
| **文檔成果** | 完整的設計規劃文檔 | 專業評審通過 |
| **能力成果** | 清晰的能力模型和技能矩陣 | 4 階段路徑完整 |
| **實施成果** | 可執行的實施路徑 | 實踐項目驗證 |
| **質量成果** | 測試驅動開發文化和代碼審查機制 | 覆蓋率和審查率達標 |
| **風險成果** | 完整的風險識別和後備方案 | 風險評估報告 |

---

## 2. 核心設計原則

本設計基於以下核心原則，指導整個實施過程：

| 原則 | 說明 | 應用場景 |
|------|------|---------|
| **漸進式複雜度** | 從簡單的 CRUD 開始，逐步增加到複雜的策略架構 | 所有 4 個階段 |
| **測試驅動** | 每個階段都強調 TDD，確保代碼質量 | 代碼實踐 |
| **實踐優先** | 通過實際項目和代碼示例學習，而非理論堆砌 | 所有任務 |
| **知識整合** | 前後端、策略引擎、數據庫知識逐步融合 | 知識庫設計 |
| **反饋循環** | 每個階段都有明確的驗證標準和評估機制 | 評估體系 |
| **可量化** | 所有指標應該可測量、可驗證 | 評估方法 |
| **可執行** | 所有任務都有明確的交付物和驗證標準 | 實施路徑 |

---

## 3. 能力模型和技能矩陣

### 3.1 四階段能力模型

```
階段 1: 初級開發者 (0-3 個月)
   ├─ P0: 基礎生存技能
   └─ 目標: 獨立完成簡單的前後端功能

階段 2: 中級開發者 (3-6 個月)
   ├─ P0+P1: 核心開發技能
   └─ 目標: 掌握回測引擎和策略引擎

階段 3: 高級開發者 (6-12 個月)
   ├─ P0+P1+P2: 進階技能
   └─ 目標: 掌握複合策略和性能優化

階段 4: 高級架構師 (12+ 個月)
   ├─ P0-P3: 全部技能
   └─ 目標: 微服務架構和技術領導力
```

### 3.2 能力維度框架

```
┌─────────────────────────────────────────────────────────────┐
│                  程序員能力評估框架                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  技術能力 (40%)                                              │
│  ├─ 代碼質量 (測試覆蓋率、複雜度、重複率)                      │
│  ├─ 架構設計 (API 設計、數據模型、微服務)                      │
│  ├─ 技術棧掌握 (Python/FastAPI, React, 回測引擎)              │
│  └─ 問題解決能力 (調試、優化、故障排除)                        │
│                                                             │
│  實踐能力 (30%)                                              │
│  ├─ TDD 執行度 (測試先於實現、測試策略)                        │
│  ├─ 代碼審查參與度 (審查頻率、回應時間、質量)                  │
│  ├─ 文檔完整性 (Docstring、API 文檔、README)                  │
│  └─ Git 規範遵循度 (Conventional Commits、分支管理)           │
│                                                             │
│  領域知識 (20%)                                              │
│  ├─ 量化交易知識 (技術指標、回測概念、市場數據)                 │
│  ├─ 策略引擎理解 (IStrategy 接口、信號處理、策略工廠)           │
│  ├─ 金融指標掌握 (Sharpe Ratio, Max Drawdown 等)             │
│  └─ 數據分析能力 (pandas、NumPy、統計計算)                    │
│                                                             │
│  領導力 (10%) - 僅高級/架構師階段                             │
│  ├─ 技術指導 (代碼審查、知識分享、導師制度)                     │
│  ├─ 技術決策 (ADR、技術選型、技術債管理)                       │
│  └─ 團隊影響力 (規範制定、團隊建設、技術文化)                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 技能優先級層級

```
┌─────────────────────────────────────────────────────┐
│ P0 (必備) - 基礎生存技能                             │
│ Python/FastAPI, React 19, 測試驅動開發, Git 提交規範 │
├─────────────────────────────────────────────────────┤
│ P1 (重要) - 核心開發技能                             │
│ VectorBT/Backtrader, Zustand, React Query, 策略引擎  │
├─────────────────────────────────────────────────────┤
│ P2 (可選) - 進階技能                                 │
│ Three.js, Celery, 高級圖表, 性能優化                 │
├─────────────────────────────────────────────────────┤
│ P3 (未來擴展) - 專家技能                             │
│ 機器學習, 實時數據流, Kubernetes, 架構設計           │
└─────────────────────────────────────────────────────┘
```

### 3.4 評分標準

| 等級 | 分數範圍 | 描述 |
|------|---------|------|
| **優秀 (A)** | 90-100 | 超越預期，可作為參考標準 |
| **良好 (B)** | 80-89 | 達到預期，有改進空間 |
| **合格 (C)** | 70-79 | 基本達標，需要改進 |
| **待改進 (D)** | 60-69 | 未達標，必須改進 |
| **不合格 (F)** | 0-59 | 嚴重不達標，需重新培訓 |

### 3.5 晉升門檻

| 階段 | 最低分數 | 必備條件 |
|------|---------|---------|
| 階段 1 → 階段 2 | 75 分 | 所有 P0 指標達到 C 以上 |
| 階段 2 → 階段 3 | 80 分 | 所有 P0+P1 指標達到 B 以上 |
| 階段 3 → 階段 4 | 85 分 | 所有 P0-P2 指標達到 B 以上，領導力達到 C 以上 |
| 架構師維持 | 85 分 | 所有指標達到 B 以上 |

---

## 4. 統一知識庫

### 4.1 知識庫架構

統一知識庫整合 Dashboard 專案的完整技術知識，為 Programmer Sub-Agent 提供開發所需的：

```
統一知識庫 (KB-UNIFIED-001)
├── 後端架構知識
│   ├── API 端點設計
│   ├── 服務層架構
│   ├── 數據結構和模型
│   ├── 錯誤處理機制
│   └── 緩存策略
├── 前端架構知識
│   ├── React 組件層級
│   ├── 共享組件庫
│   ├── 狀態管理 (Zustand + React Query)
│   ├── UI 模式
│   └── API 集成
├── 策略引擎知識
│   ├── IStrategy 接口
│   ├── 策略模板 (RSI, MACD, Confluence, Composite)
│   ├── VectorBT 集成
│   ├── 策略工廠
│   └── 核心算法 (向量化 RSI/MACD)
└── Git 開發模式
    ├── 分支策略 (Git Flow)
    ├── Conventional Commits
    ├── Code Review 流程
    └── CI/CD 集成
```

### 4.2 快速開始指南（5 分鐘上手）

#### 4.2.1 環境準備（2 分鐘）

```bash
# 1. 克隆專案
git clone <repo-url>
cd Dashboard

# 2. 設置 Python 環境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r backend/requirements.txt

# 3. 設置 Node 環境
cd frontend
npm install

# 4. 啟動開發服務器
# 終端 1: 後端
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 終端 2: 前端
cd frontend
npm run dev
```

#### 4.2.2 創建第一個策略（1 分鐘）

```python
# backend/strategies/my_strategy.py
from .base import IStrategy, Signal, SignalAction, ExecutionContext
from datetime import date
from typing import List

class MyFirstStrategy(IStrategy):
    """簡單的趨勢跟隨策略"""
    name = "my_first_strategy"

    def __init__(self, short_period: int = 5, long_period: int = 20):
        self.short_period = short_period
        self.long_period = long_period

    def generate_signals(
        self,
        context: ExecutionContext,
        symbols: List[str]
    ) -> List[Signal]:
        """生成交易信號"""
        signals = []

        for symbol in symbols:
            # 獲取移動平均線數據
            short_ma = self._get_ma(symbol, context.market_date, self.short_period)
            long_ma = self._get_ma(symbol, context.market_date, self.long_period)

            # 簡單的交叉策略
            if short_ma > long_ma:
                signals.append(Signal(
                    symbol=symbol,
                    action=SignalAction.BUY,
                    confidence=0.8
                ))

        return signals

    def _get_ma(self, symbol: str, date: date, period: int) -> float:
        """獲取移動平均線值"""
        # 實現略
        pass
```

#### 4.2.3 提交代碼（1 分鐘）

```bash
# 1. 創建功能分支
git checkout develop
git pull origin develop
git checkout -b feature/my-first-strategy

# 2. 提交代碼（遵循 Conventional Commits）
git add .
git commit -m "feat: add my first strategy implementation"

# 3. 推送到遠端
git push -u origin feature/my-first-strategy
```

### 4.3 核心設計原則

| 原則 | 說明 |
|------|------|
| **分層架構** | 前端 → API → 服務 → 倉庫 → 存儲，清晰的關注點分離 |
| **接口驅動** | 策略引擎基於 `IStrategy` 接口，實現策略邏輯與執行分離 |
| **狀態分類** | 全局狀態(Zustand) + 服務端狀態(React Query) + 本地狀態(useState) |
| **API 版本化** | RESTful 設計，統一的請求/響應格式 |
| **測試金字塔** | 單元測試 → 集成測試 → E2E 測試 |
| **Git Flow** | feature/fix/hotfix 分支 + Conventional Commits + CI/CD |

### 4.4 後端架構核心知識

#### 4.4.1 API 端點設計

**策略管理端點:**

| 方法 | 路徑 | 描述 | 認證 |
|------|------|------|------|
| GET | `/api/v1/strategies` | 列出策略 | ✅ |
| POST | `/api/v1/strategies` | 創建策略 | ✅ |
| GET | `/api/v1/strategies/{strategy_id}` | 獲取策略詳情 | ✅ |
| PUT | `/api/v1/strategies/{strategy_id}` | 更新策略配置 | ✅ |
| DELETE | `/api/v1/strategies/{strategy_id}` | 刪除策略 | ✅ |

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
    "request_id": "req_abc123",
    "timestamp": "2026-02-20T23:38:00Z"
  }
}
```

#### 4.4.2 核心服務

**StrategyRegistry** - 策略註冊表
```python
class StrategyRegistry:
    def register(self, strategy_id: str, strategy: IStrategy):
        """註冊策略"""

    def unregister(self, strategy_id: str):
        """註銷策略"""

    def get(self, strategy_id: str) -> Optional[IStrategy]:
        """獲取策略實例"""

    def list_ids(self) -> List[str]:
        """列出所有策略 ID"""
```

**TechnicalStrategyService** - 技術指標工廠
```python
class TechnicalStrategyService:
    def generate_strategy(self, strategy_type: str, universe: str, params: dict):
        """根據策略類型生成策略結果"""

    def calc_metrics(self, backtest_result: dict) -> dict:
        """計算回測指標"""

# 支持的策略類型
SUPPORTED_TYPES = [
    'RSI', 'MACD', 'Supertrend', 'Bollinger Bands',
    'Momentum', 'Dual Momentum', 'Sector Rotation',
    'Extremes', 'RSI Trend'
]
```

#### 4.4.3 數據結構

**Strategy 模型:**
```python
@dataclass
class Strategy:
    id: str  # 策略 ID (e.g., "str_123456")
    name: str
    description: str
    type: str  # 策略類型 (trend_following, mean_reversion, etc.)
    status: str  # active, inactive, archived
    parameters: Dict  # 策略參數
    risk_limits: Dict  # 風險限制
    created_at: datetime
    updated_at: datetime
```

**PerformanceMetrics 模型:**
```python
@dataclass
class PerformanceMetrics:
    total_return: float
    cagr: float  # 複合年化增長率
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    volatility: float
    calmar_ratio: float
    win_rate: float
    profit_factor: float
    avg_win: float
    avg_loss: float
    total_trades: int
```

#### 4.4.4 錯誤處理

**統一錯誤碼:**

| 錯誤碼 | HTTP 狀態 | 描述 |
|--------|-----------|------|
| `VALIDATION_ERROR` | 422 | 請求參數驗證失敗 |
| `STRATEGY_NOT_FOUND` | 404 | 策略不存在 |
| `STRATEGY_NAME_EXISTS` | 409 | 策略名稱已存在 |
| `BACKTEST_NOT_FOUND` | 404 | 回測任務不存在 |
| `INVALID_DATE_RANGE` | 422 | 無效日期範圍 |
| `INSUFFICIENT_DATA` | 400 | 數據不足 |
| `UNAUTHORIZED` | 401 | 未授權訪問 |
| `FORBIDDEN` | 403 | 無權限訪問 |
| `INTERNAL_ERROR` | 500 | 內部服務器錯誤 |

### 4.5 前端架構核心知識

#### 4.5.1 React 組件層級

```
App (根組件)
├── ErrorBoundary (錯誤邊界)
├── QueryClientProvider (React Query)
├── PersonaProvider (Persona 上下文)
├── ToastProvider (Toast 通知)
├── Router (BrowserRouter)
└── DashboardLayout (主佈局組件)
    ├── Sidebar (側邊欄)
    ├── Header (頂部欄)
    └── Main Content (主內容區)
        └── Routes → Page Components (40+ 頁面)
```

#### 4.5.2 共享組件庫

| 組件名稱 | 用途 | 複用度 |
|---------|------|--------|
| **ErrorBoundary** | 錯誤邊界，捕獲 React 錯誤 | ⭐⭐⭐⭐⭐ |
| **ToastProvider** | Toast 通知系統 | ⭐⭐⭐⭐⭐ |
| **Skeleton** | 骨架屏加載狀態 | ⭐⭐⭐⭐⭐ |
| **EmptyState** | 空狀態顯示組件 | ⭐⭐⭐⭐ |
| **EmptyStatePresets** | 預設空狀態模板 | ⭐⭐⭐⭐ |

#### 4.5.3 狀態管理分類

| 狀態類型 | 推薦方案 | 理由 |
|---------|----------|------|
| **全局應用狀態** | Zustand | 跨多個組件共享，如 Dashboard 核心數據 |
| **服務器狀態** | React Query | 需要從 API 獲取，需要緩存和同步 |
| **功能特定狀態** | Context | 特定功能的狀態共享，如 Persona、Toast |
| **表單/UI 狀態** | useState | 組件內部狀態，不需要共享 |
| **持久化狀態** | LocalStorage | 需要跨會話保存，如用戶偏好、認證信息 |

**Zustand Store 示例:**
```javascript
const useStore = create((set) => ({
  watchlist: [],
  marketMovers: {
    gainers: [],
    losers: [],
    most_active: []
  },
  heatmapData: [],
  marketScore: {
    current: null,
    history: []
  },
  stockDetails: {},
  lastUpdated: null,
  loadingStatus: 'idle',
  error: null,

  fetchStage1Overview: async (force, targetDate, market) => {
    // 獲取關鍵概覽數據
  },

  fetchStage2secondary: async (targetDate, market) => {
    // 獲取次要數據
  },

  refreshDashboardData: () => {
    // 強制刷新所有數據
  }
}));
```

**React Query 配置:**
```javascript
const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            refetchOnWindowFocus: CONFIG.refetchOnWindowFocus,
            retry: 1,
            staleTime: CONFIG.staleTime,
            gcTime: CONFIG.cacheTime,
            refetchOnMount: CONFIG.refetchOnMount,
        },
    },
});
```

#### 4.5.4 UI 模式

**加載狀態模式:**
```javascript
const { data, error, isLoading } = useApiCache(key, fetcher);

// 1. 加載狀態
if (isLoading && !data) {
  return <Skeleton.PageLoader text="Loading..." />;
}

// 2. 錯誤狀態
if (error) {
  return (
    <EmptyStatePresets.LoadError
      message={`Failed: ${error.message}`}
      action={<button onClick={refetch}>Retry</button>}
    />
  );
}

// 3. 空狀態
if (!data || data.length === 0) {
  return <EmptyStatePresets.NoData />;
}

// 4. 主內容
return <div>{/* 頁面內容 */}</div>;
```

#### 4.5.5 API 集成鏈路

```
組件層 (Component Layer)
    React Component (Page / UI)
        ↓
自定義 Hook 層 (Custom Hooks)
    useMomentum, useAllocation, useStrategyAPI
        ↓
React Query 層 (TanStack Query)
    useApiCache / useApiMutation
    (緩存檢查、去重、重試)
        ↓
請求保護層 (Request Protection)
    protectedFetch (去重、超時、重試)
        ↓
Axios 實例層 (HTTP Client)
    apiClient (統一配置、攔截器)
        ↓
網絡層 (Network)
    HTTP Request (GET / POST / PUT / DELETE)
        ↓
後端層 (Backend)
    FastAPI (Python)
        ↓
響應層 (Response)
    JSON Response / Error
```

### 4.6 策略引擎核心知識

#### 4.6.1 IStrategy 接口契約

```python
class SignalAction(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

@dataclass
class Signal:
    symbol: str
    action: SignalAction
    confidence: float  # 0.0 to 1.0
    reason: str = ""

    def __post_init__(self):
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("Confidence must be 0.0-1.0")

@dataclass
class ExecutionContext:
    portfolio_value: float
    available_cash: float
    current_positions: List['PositionState']
    market_date: date
    market_status: str  # 'OPEN', 'CLOSED', etc.

class IStrategy:
    @property
    def name(self) -> str:
        """策略標識符"""
        raise NotImplementedError

    def generate_signals(
        self,
        context: ExecutionContext,
        symbols: List[str]
    ) -> List[Signal]:
        """
        核心方法：生成交易信號

        約束：
        - 返回信號列表（每個標的最多一個）
        - 只返回 BUY/SELL（HOLD 通過不返回表示）
        - 信心分數 0.0-1.0
        - 對相同輸入必須確定性
        - 交易前檢查 market_status
        - 尊重持倉狀態和現金約束
        """
        raise NotImplementedError
```

#### 4.6.2 策略模板

**模板 1: RSI 均值回歸策略**
```python
class RSIStrategy(IStrategy):
    """使用 RSI 指標的均值回歸策略"""

    name = "rsi_mean_reversion"

    def __init__(
        self,
        period: int = 14,
        buy_threshold: int = 30,
        sell_threshold: int = 70,
        min_trade_size: float = 1000.0
    ):
        if not (0 < buy_threshold < sell_threshold < 100):
            raise ValueError("Invalid threshold values")
        self.period = period
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold
        self.min_trade_size = min_trade_size
        self.rsi_cache = {}

    def generate_signals(
        self,
        context: ExecutionContext,
        symbols: List[str]
    ) -> List[Signal]:
        signals = []

        for symbol in symbols:
            # 檢查市場狀態
            if context.market_status != 'CLOSED':
                continue

            # 檢查是否已持有
            existing_position = next(
                (p for p in context.current_positions if p.symbol == symbol),
                None
            )

            # 獲取 RSI 值
            rsi = self._get_rsi(symbol, context.market_date)

            # 生成買入信號（僅當未持有時）
            if rsi < self.buy_threshold and not existing_position:
                signals.append(Signal(
                    symbol=symbol,
                    action=SignalAction.BUY,
                    confidence=self._calculate_confidence(rsi, self.buy_threshold)
                ))

            # 生成賣出信號（僅當持有时）
            elif rsi > self.sell_threshold and existing_position:
                signals.append(Signal(
                    symbol=symbol,
                    action=SignalAction.SELL,
                    confidence=self._calculate_confidence(rsi, self.sell_threshold)
                ))

        return signals
```

**模板 2: MACD 趨勢跟隨策略**
```python
class MACDStrategy(IStrategy):
    """使用 MACD 交叉的趨勢跟隨策略"""

    name = "macd_trend_following"

    def __init__(
        self,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9,
        min_trade_size: float = 1000.0
    ):
        self.fast = fast
        self.slow = slow
        self.signal = signal
        self.min_trade_size = min_trade_size
        self.indicator_cache = {}

    def generate_signals(
        self,
        context: ExecutionContext,
        symbols: List[str]
    ) -> List[Signal]:
        signals = []

        for symbol in symbols:
            # 檢查市場狀態
            if context.market_status != 'CLOSED':
                continue

            # 獲取當前和前一日的 MACD 值
            macd, signal_line = self._get_macd(symbol, context.market_date)
            prev_macd, prev_signal = self._get_macd_previous(symbol, context.market_date)

            # 檢查現有持倉
            existing_position = next(
                (p for p in context.current_positions if p.symbol == symbol),
                None
            )

            # MACD 向上交叉信號線（看漲）
            if (macd > signal_line and prev_macd <= prev_signal) and not existing_position:
                signals.append(Signal(
                    symbol=symbol,
                    action=SignalAction.BUY,
                    confidence=min(1.0, abs(macd - signal_line) / abs(signal_line))
                ))

            # MACD 向下交叉信號線（看跌）
            elif (macd < signal_line and prev_macd >= prev_signal) and existing_position:
                signals.append(Signal(
                    symbol=symbol,
                    action=SignalAction.SELL,
                    confidence=min(1.0, abs(macd - signal_line) / abs(signal_line))
                ))

        return signals
```

**模板 3: 組合策略**
```python
class CompositeStrategy(IStrategy):
    """使用可配置合併算法組合多個策略"""

    name = "composite_strategy"

    MERGE_ALGORITHMS = [
        'majority_vote',  # 多數決
        'unanimous',      # 一致同意
        'weighted',       # 加權
        'any'             # 任一
    ]

    def __init__(
        self,
        strategies: List[IStrategy],
        merge_algorithm: str = 'majority_vote'
    ):
        if merge_algorithm not in self.MERGE_ALGORITHMS:
            raise ValueError(f"Invalid merge algorithm: {merge_algorithm}")
        self.strategies = strategies
        self.merge_algorithm = merge_algorithm

    def generate_signals(
        self,
        context: ExecutionContext,
        symbols: List[str]
    ) -> List[Signal]:
        # 收集所有策略的信號
        all_signals_by_symbol = {symbol: [] for symbol in symbols}

        for strategy in self.strategies:
            strategy_signals = strategy.generate_signals(context, symbols)
            for signal in strategy_signals:
                all_signals_by_symbol[signal.symbol].append(signal)

        # 合併每個標的的信號
        merged_signals = []
        for symbol, signals in all_signals_by_symbol.items():
            if not signals:
                continue

            merged_signal = self._merge_signals(symbol, signals)
            if merged_signal:
                merged_signals.append(merged_signal)

        return merged_signals
```

#### 4.6.3 VectorBT 集成

**信號適配器:**
```python
class SignalAdapter:
    """將 IStrategy 信號轉換為 VectorBT 格式"""

    @staticmethod
    def signals_to_vectorbt(
        ohlcv_index: pd.MultiIndex,
        signals_by_date: Dict[date, List[Signal]]
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        將策略信號轉換為 VectorBT 進入/退出 DataFrame

        參數：
            ohlcv_index: 來自 VBTDataLoader 的 MultiIndex
            signals_by_date: 映射日期到 List[Signal] 的字典

        返回：
            entries: DataFrame[symbol] = bool (True = 買入信號)
            exits: DataFrame[symbol] = bool (True = 賣出信號)
        """
        # 從索引中提取所有標的
        symbols = ohlcv_index.get_level_values('symbol').unique()

        # 創建空 DataFrame
        entries = pd.DataFrame(False, index=ohlcv_index.get_level_values('date').unique(), columns=symbols)
        exits = pd.DataFrame(False, index=ohlcv_index.get_level_values('date').unique(), columns=symbols)

        # 填充信號
        for signal_date, signals in signals_by_date.items():
            if signal_date not in entries.index:
                continue

            for signal in signals:
                if signal.symbol not in symbols:
                    continue

                if signal.action == SignalAction.BUY:
                    entries.loc[signal_date, signal.symbol] = True
                elif signal.action == SignalAction.SELL:
                    exits.loc[signal_date, signal.symbol] = True

        return entries, exits
```

#### 4.6.4 策略工廠

```python
from typing import Dict, Any

class StrategyFactory:
    """集中化策略實例化"""

    @staticmethod
    def create(strategy_type: str, params: Dict[str, Any] = None) -> IStrategy:
        """
        通過類型創建策略實例

        參數：
            strategy_type: 策略標識符
            params: 策略參數

        返回：
            IStrategy 實例
        """
        params = params or {}

        # 個體策略
        if strategy_type == 'rsi':
            return RSIStrategy(
                period=params.get('period', 14),
                buy_threshold=params.get('buy_threshold', 30),
                sell_threshold=params.get('sell_threshold', 70),
                min_trade_size=params.get('min_trade_size', 1000.0)
            )

        elif strategy_type == 'macd':
            return MACDStrategy(
                fast=params.get('fast', 12),
                slow=params.get('slow', 26),
                signal=params.get('signal', 9),
                min_trade_size=params.get('min_trade_size', 1000.0)
            )

        # 組合策略
        elif strategy_type == 'composite':
            strategies = []
            for strat_type in params.get('strategies', []):
                strategies.append(StrategyFactory.create(strat_type['type'], strat_type.get('params', {})))

            return CompositeStrategy(
                strategies=strategies,
                merge_algorithm=params.get('merge_algorithm', 'majority_vote')
            )

        else:
            raise ValueError(f"Unknown strategy type: {strategy_type}")
```

#### 4.6.5 核心算法

**向量化 RSI 計算:**
```python
import numpy as np
import pandas as pd

class VectorizedRSI:
    """性能優化的向量化 RSI 計算"""

    def calculate(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """
        使用向量化操作計算 RSI

        參數：
            prices: 價格序列
            period: RSI 週期

        返回：
            RSI 值
        """
        # 計算價格變化
        delta = prices.diff()

        # 分離漲跌幅
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)

        # 計算平均漲跌幅（指數加權）
        avg_gains = gains.ewm(span=period, adjust=False).mean()
        avg_losses = losses.ewm(span=period, adjust=False).mean()

        # 計算 RSI
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))

        return rsi
```

**向量化 MACD 計算:**
```python
class VectorizedMACD:
    """向量化 MACD 計算"""

    def calculate(
        self,
        prices: pd.Series,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> tuple[pd.Series, pd.Series]:
        """
        使用向量化操作計算 MACD

        返回：
            (macd_line, signal_line)
        """
        # 計算 EMA
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()

        # MACD 線
        macd_line = ema_fast - ema_slow

        # 信號線（MACD 的 EMA）
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()

        return macd_line, signal_line
```

### 4.7 Git 開發模式

#### 4.7.1 分支策略（Git Flow）

```
main (生產代碼)
  ↑
  develop (開發整合)
  ↑
  ├── feature/* (功能分支)
  ├── hotfix/* (緊急修復)
  ├── release/* (發布準備)
  ├── fix/* (一般修復)
  └── refactor/* (代碼重構)
```

#### 4.7.2 Conventional Commits 規範

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type 類型:**
- `feat`: 新功能
- `fix`: Bug 修復
- `docs`: 文檔更新
- `style`: 代碼格式（不影響代碼運行）
- `refactor`: 重構（不是新功能也不是修復）
- `test`: 添加測試
- `chore`: 構建過程或輔助工具的變動

**示例:**
```bash
git commit -m "feat(strategies): add RSI mean reversion strategy"
git commit -m "fix(api): handle empty items list gracefully"
git commit -m "refactor(items): extract validation logic to separate function"
git commit -m "docs(readme): update installation instructions"
git commit -m "test(items): add comprehensive tests for items API"
git commit -m "style(items): format code with black and ruff"
```

#### 4.7.3 PR 流程

```markdown
## PR 模板

### 描述
簡要描述這個 PR 的目的和實現的功能。

### 變更類型
- [ ] Bug 修復
- [ ] 新功能
- [ ] 代碼重構
- [ ] 文檔更新
- [ ] 其他

### 測試
- [ ] 已添加單元測試
- [ ] 已添加集成測試
- [ ] 已通過所有測試

### 檢查清單
- [ ] 代碼遵循項目規範
- [ ] 已通過 linter 檢查
- [ ] 已更新相關文檔
- [ ] 已通過代碼審查
```

---

## 5. 實施路徑框架

### 5.1 實施路徑概述

本實施路徑基於 **漸進式能力建設** 原則，包含 4 個清晰的階段：

```
階段 1: 初級開發者 (0-3 個月)
   ├─ P0: 基礎生存技能
   ├─ 核心學習目標: 掌握全棧基礎、建立 TDD 習慣
   ├─ 預估時間: 8-9 週
   └─ 晉升門檻: 總分 ≥ 75 分

階段 2: 中級開發者 (3-6 個月)
   ├─ P0+P1: 核心開發技能
   ├─ 核心學習目標: 掌握回測引擎、策略引擎、狀態管理
   ├─ 預估時間: 10-11 週
   └─ 晉升門檻: 總分 ≥ 80 分

階段 3: 高級開發者 (6-12 個月)
   ├─ P0+P1+P2: 進階技能
   ├─ 核心學習目標: 掌握複合策略、性能優化、架構思維
   ├─ 預估時間: 12-16 週
   └─ 晉升門檻: 總分 ≥ 85 分

階段 4: 高級架構師 (12+ 個月)
   ├─ P0-P3: 全部技能
   ├─ 核心學習目標: 微服務架構、DevOps、跨領域整合
   ├─ 預估時間: 持續進階
   └─ 維持標準: 總分 ≥ 85 分
```

### 5.2 階段 1: 初級開發者 (0-3 個月)

#### 5.2.1 核心學習目標

1. **掌握全棧基礎技能**: 能夠獨立完成簡單的前後端功能
2. **建立測試驅動開發習慣**: TDD 成為開發的默認模式
3. **理解系統架構**: 掌握分層架構和 API 設計基本概念
4. **熟悉開發工作流**: Git 提交規範、代碼審查流程

#### 5.2.2 必備技能矩陣

**後端開發 (P0):**

| 技能 | 內容 | 掌握程度 | 驗證方式 |
|------|------|---------|---------|
| **Python 基礎** | 數據類型、函數、類、異步編程 | ⭐⭐⭐⭐⭐ | 代碼審查 |
| **FastAPI 基礎** | 路由、依賴注入、請求/響應模型 | ⭐⭐⭐⭐⭐ | 單元測試 |
| **Pydantic 驗證** | 數據模型、驗證規則、錯誤處理 | ⭐⭐⭐⭐⭐ | 測試覆蓋率 |
| **DuckDB 基礎** | 連接、查詢、CRUD 操作 | ⭐⭐⭐⭐ | 集成測試 |
| **錯誤處理** | 自定義異常、全局異常處理器 | ⭐⭐⭐⭐ | 代碼審查 |

**前端開發 (P0):**

| 技能 | 內容 | 掌握程度 | 驗證方式 |
|------|------|---------|---------|
| **React 19 基礎** | 函數組件、Hooks (useState, useEffect) | ⭐⭐⭐⭐⭐ | 組件測試 |
| **Bootstrap 5** | 響應式佈局、組件使用 | ⭐⭐⭐⭐ | UI 審查 |
| **Axios** | HTTP 客戶端配置、GET/POST/PUT/DELETE | ⭐⭐⭐⭐⭐ | 測試 Mock |
| **狀態管理基礎** | useState, useContext | ⭐⭐⭐⭐ | 單元測試 |
| **表單處理** | 受控組件、表單驗證 | ⭐⭐⭐⭐ | E2E 測試 |

**測試驅動開發 (P0):**

| 技能 | 內容 | 掌握程度 | 驗證方式 |
|------|------|---------|---------|
| **pytest 基礎** | 測試編寫、fixture、mock | ⭐⭐⭐⭐⭐ | 測試覆蓋率 |
| **vitest 基礎** | 單元測試、組件測試 | ⭐⭐⭐⭐ | 測試覆蓋率 |
| **TDD 流程** | Red-Green-Refactor | ⭐⭐⭐⭐⭐ | 代碼審查 |
| **AAA 模式** | Arrange-Act-Assert | ⭐⭐⭐⭐⭐ | 測試審查 |
| **測試覆蓋率** | pytest-cov, vitest coverage | ⭐⭐⭐ | CI/CD 報告 |

#### 5.2.3 實踐任務清單

**任務 1.1: 創建完整的 CRUD API**

**目標**: 實現完整的 CRUD API

**交付物**:
- `backend/routers/items.py` (150 行)
- `backend/tests/test_items.py` (100 行)
- 測試覆蓋率 ≥ 80%

**驗證標準**:
- [ ] 實現 GET/POST/PUT/DELETE 端點
- [ ] 使用 Pydantic 模型驗證
- [ ] 使用 DuckDB 存儲數據
- [ ] 統一錯誤處理
- [ ] 測試覆蓋率 ≥ 80%

**任務 1.2: 實現技術指標計算**

**目標**: 掌握 pandas 數據處理和技術指標計算

**交付物**:
- `backend/indicators/simple_rsi.py` (80 行)
- `backend/indicators/simple_macd.py` (80 行)
- `backend/tests/test_indicators.py` (120 行)
- 測試覆蓋率 ≥ 90%

**驗證標準**:
- [ ] 使用 pandas 進行向量化計算
- [ ] 實現 RSI 和 MACD 類
- [ ] 編寫單元測試
- [ ] 測試覆蓋率 ≥ 90%

**任務 1.3: 創建前端頁面**

**目標**: 創建項目管理的前端頁面

**交付物**:
- `frontend/src/pages/ItemsPage/index.jsx` (200 行)
- `frontend/src/pages/ItemsPage/__tests__/ItemsPage.test.jsx` (150 行)
- 組件測試覆蓋率 ≥ 70%

**驗證標準**:
- [ ] 使用 React 19 Hooks
- [ ] 使用 Bootstrap 5 佈局
- [ ] 整合後端 API
- [ ] 實現表單驗證
- [ ] 組件測試覆蓋率 ≥ 70%

#### 5.2.4 預估學習時間

| 任務類別 | 預估時間 | 優先級 |
|---------|---------|--------|
| Python/FastAPI 基礎 | 2 週 | P0 |
| React 19 基礎 | 2 週 | P0 |
| 測試驅動開發 | 1 週 | P0 |
| DuckDB 基礎 | 3 天 | P0 |
| Git 規範 | 2 天 | P0 |
| 實踐項目 (任務 1.1-1.3) | 4 週 | P0 |
| **總計** | **8-9 週** | |

#### 5.2.5 驗證標準

**代碼質量驗證**:
- [ ] 所有 API 端點有完整的單元測試（覆蓋率 ≥ 80%）
- [ ] 所有前端組件有組件測試
- [ ] 所有提交遵循 Conventional Commits 規範（100%）
- [ ] 代碼通過 linter 檢查（ruff, eslint）
- [ ] 代碼通過格式化工具（black, prettier）

**功能驗證**:
- [ ] 能夠獨立完成完整的 CRUD API 實現
- [ ] 能夠實現簡單的技術指標計算
- [ ] 前後端能夠正確交互
- [ ] 能夠處理常見錯誤情況

**知識驗證**:
- [ ] 能夠解釋分層架構的概念
- [ ] 能夠解釋 TDD 的 Red-Green-Refactor 流程
- [ ] 能夠解釋 RESTful API 的設計原則
- [ ] 能夠閱讀和理解現有代碼

**晉升門檻**: 總分 ≥ 75 分，且所有 P0 指標達到 C 以上

### 5.3 階段 2: 中級開發者 (3-6 個月)

#### 5.3.1 核心學習目標

1. **掌握回測引擎使用**: 能夠使用 VectorBT 和 Backtrader 進行策略回測
2. **理解策略引擎架構**: 掌握 IStrategy 接口和策略模式
3. **熟練狀態管理**: 精通 Zustand 和 React Query
4. **建立代碼審查能力**: 能夠審查他人代碼並提供建設性反饋

#### 5.3.2 必備技能矩陣

**回測引擎 (P1):**

| 技能 | 內容 | 掌握程度 | 驗證方式 |
|------|------|---------|---------|
| **VectorBT 基礎** | 數據加載、信號生成、組合創建 | ⭐⭐⭐⭐⭐ | 回測結果驗證 |
| **Backtrader 基礎** | Cerebro、策略類、數據 feed | ⭐⭐⭐⭐ | 回測對比 |
| **績效指標計算** | Sharpe Ratio、Max Drawdown、Win Rate | ⭐⭐⭐⭐ | 指標驗證 |
| **參數優化** | 網格搜索、並行回測 | ⭐⭐⭐ | 優化結果 |

**策略引擎 (P1):**

| 技能 | 內容 | 掌握程度 | 驗證方式 |
|------|------|---------|---------|
| **IStrategy 接口** | generate_signals 實現 | ⭐⭐⭐⭐⭐ | 接口契約測試 |
| **策略模式** | 工廠模式、適配器模式、組合策略 | ⭐⭐⭐⭐ | 設計審查 |
| **信號處理** | 信號生成、合併、過濾 | ⭐⭐⭐⭐ | 信號測試 |
| **策略工廠** | 策略註冊、實例化 | ⭐⭐⭐⭐ | 工廠測試 |

**狀態管理 (P1):**

| 技能 | 內容 | 掌握程度 | 驗證方式 |
|------|------|---------|---------|
| **Zustand** | Store 定義、actions、selectors | ⭐⭐⭐⭐⭐ | Store 測試 |
| **React Query** | useApiCache、useApiMutation、cache 管理 | ⭐⭐⭐⭐⭐ | 緩存測試 |
| **狀態分類原則** | 全局狀態、服務端狀態、本地狀態 | ⭐⭐⭐⭐ | 代碼審查 |
| **快取策略** | staleTime、gcTime、invalidate | ⭐⭐⭐⭐ | 性能測試 |

#### 5.3.3 實踐任務清單

**任務 2.1: 實現完整的 RSI 策略**

**目標**: 掌握 IStrategy 接口和 VectorBT 回測

**交付物**:
- `backend/strategies/rsi_strategy.py` (150 行)
- `backend/backtest/vectorbt_executor.py` (200 行)
- `backend/tests/test_rsi_strategy.py` (120 行)
- 測試覆蓋率 ≥ 85%

**驗證標準**:
- [ ] 實現 RSIStrategy 類
- [ ] 使用 VectorBT 執行回測
- [ ] 計算績效指標
- [ ] 測試覆蓋率 ≥ 85%

**任務 2.2: 實現策略工廠**

**目標**: 掌握工廠模式和策略註冊機制

**交付物**:
- `backend/strategies/factory.py` (80 行)
- `backend/tests/test_strategy_factory.py` (60 行)
- 測試覆蓋率 ≥ 90%

**驗證標準**:
- [ ] 實現 StrategyFactory 類
- [ ] 註冊內置策略
- [ ] 支持動態策略註冊
- [ ] 測試覆蓋率 ≥ 90%

**任務 2.3: 實現 React Query 緩存管理**

**目標**: 掌握 React Query 的緩存和狀態管理

**交付物**:
- `frontend/src/hooks/useApiCache.js` (150 行)
- `frontend/src/hooks/__tests__/useApiCache.test.js` (100 行)
- 測試覆蓋率 ≥ 80%

**驗證標準**:
- [ ] 實現 useApiCache hook
- [ ] 實現 useApiMutation hook
- [ ] 實現快取預設
- [ ] 測試覆蓋率 ≥ 80%

**任務 2.4: 實現 Zustand Store**

**目標**: 掌握 Zustand 全局狀態管理

**交付物**:
- `frontend/src/store/dashboardStore.js` (120 行)
- `frontend/src/store/__tests__/dashboardStore.test.js` (80 行)
- 測試覆蓋率 ≥ 85%

**驗證標準**:
- [ ] 創建 Dashboard store
- [ ] 實現 actions 和 selectors
- [ ] 整合 React Query
- [ ] 測試覆蓋率 ≥ 85%

#### 5.3.4 預估學習時間

| 任務類別 | 預估時間 | 優先級 |
|---------|---------|--------|
| VectorBT 學習 | 1 週 | P1 |
| Backtrader 學習 | 1 週 | P1 |
| 策略引擎架構 | 1 週 | P1 |
| Zustand 精通 | 3 天 | P1 |
| React Query 精通 | 3 天 | P1 |
| 集成測試 | 3 天 | P1 |
| 實踐項目 (任務 2.1-2.4) | 5 週 | P1 |
| **總計** | **10-11 週** | |

#### 5.3.5 驗證標準

**代碼質量驗證**:
- [ ] 策略實現遵循 IStrategy 接口契約
- [ ] 回測代碼有完整的單元測試和集成測試
- [ ] 測試覆蓋率 ≥ 85%
- [ ] 所有提交遵循 Conventional Commits
- [ ] 代碼審查通過（至少 1 次他人審查）

**功能驗證**:
- [ ] 能夠使用 VectorBT 執行策略回測
- [ ] 能夠正確實現並使用策略工廠
- [ ] 能夠使用 React Query 管理服務端狀態
- [ ] 能夠使用 Zustand 管理全局狀態
- [ ] 能夠編寫集成測試

**知識驗證**:
- [ ] 能夠解釋策略模式的工作原理
- [ ] 能夠解釋向量化計算的性能優勢
- [ ] 能夠解釋 React Query 的緩存策略
- [ ] 能夠審查他人代碼並提供建設性反饋
- [ ] 能夠設計測試策略

**晉升門檻**: 總分 ≥ 80 分，且所有 P0+P1 指標達到 B 以上

### 5.4 階段 3: 高級開發者 (6-12 個月)

#### 5.4.1 核心學習目標

1. **掌握複合策略設計**: 能夠設計和實現組合策略和信號合併算法
2. **精通性能優化**: 能夠識別和解決性能瓶頸
3. **建立架構思維**: 能夠進行技術選型和架構設計決策
4. **具備技術指導能力**: 能夠指導初級和中級開發者

#### 5.4.2 必備技能矩陣

**複合策略 (P2):**

| 技能 | 內容 | 掌握程度 | 驗證方式 |
|------|------|---------|---------|
| **組合策略** | CompositeStrategy、多策略組合 | ⭐⭐⭐⭐⭐ | 回測驗證 |
| **信號合併算法** | 多數決、一緻同意、加權投票 | ⭐⭐⭐⭐ | 算法測試 |
| **策略共識機制** | 信號共振、多指標匯合 | ⭐⭐⭐ | 共識測試 |
| **策略優化** | 參數掃描、網格搜索 | ⭐⭐⭐ | 優化結果 |

**性能優化 (P2):**

| 技能 | 內容 | 掌握程度 | 驗證方式 |
|------|------|---------|---------|
| **向量化優化** | NumPy、pandas 向量化操作 | ⭐⭐⭐⭐⭐ | 性能基準測試 |
| **並行處理** | multiprocessing、asyncio | ⭐⭐⭐⭐ | 並行效率 |
| **查詢優化** | SQL 優化、索引優化 | ⭐⭐⭐⭐ | 查詢性能 |
| **緩存策略** | 多級緩存、緩存失效 | ⭐⭐⭐⭐ | 緩存命中率 |

**架構設計 (P2):**

| 技能 | 內容 | 掌握程度 | 驗證方式 |
|------|------|---------|---------|
| **微服務架構** | 服務拆分、API 網關 | ⭐⭐⭐⭐ | 架構審查 |
| **API 版本化** | 向後兼容、遷移策略 | ⭐⭐⭐⭐ | API 設計審查 |
| **數據架構設計** | Schema 設計、ETL 流程 | ⭐⭐⭐⭐ | 數據建模 |
| **技術選型** | ADR、權衡分析 | ⭐⭐⭐⭐ | ADR 文檔 |
| **E2E 測試策略** | 測試金字塔、測試覆蓋 | ⭐⭐⭐⭐ | 測試計劃 |

#### 5.4.3 實踐任務清單

**任務 3.1: 實現複合策略和信號合併**

**目標**: 掌握複合策略設計和信號合併算法

**交付物**:
- `backend/strategies/composite_strategy.py` (250 行)
- `backend/strategies/signal_merger.py` (200 行)
- `backend/tests/test_composite_strategy.py` (180 行)
- 測試覆蓋率 ≥ 90%

**驗證標準**:
- [ ] 實現 CompositeStrategy 類
- [ ] 實現 5 種信號合併算法
- [ ] 支持動態配置合併算法
- [ ] 測試覆蓋率 ≥ 90%

**任務 3.2: 性能優化和並行處理**

**目標**: 掌握性能優化和並行處理技術

**交付物**:
- `backend/optimization/vectorized_indicators.py` (180 行)
- `backend/optimization/parallel_backtest.py` (150 行)
- `backend/optimization/cache_manager.py` (120 行)
- 性能提升 ≥ 50%

**驗證標準**:
- [ ] 向量化指標計算
- [ ] 並行化回測執行
- [ ] 實現多級緩存
- [ ] 性能提升 ≥ 50%

**任務 3.3: Three.js 3D 可視化**

**目標**: 掌握 Three.js 3D 可視化

**交付物**:
- `frontend/src/components/ThreeDChart.jsx` (200 行)
- `frontend/src/components/__tests__/ThreeDChart.test.jsx` (80 行)
- 測試覆蓋率 ≥ 80%

**驗證標準**:
- [ ] 使用 Three.js 創建 3D 圖表
- [ ] 實現交互式 3D 可視化
- [ ] 優化渲染性能
- [ ] 測試覆蓋率 ≥ 80%

**任務 3.4: 架構決策記錄 (ADR)**

**目標**: 掌握架構決策記錄的編寫

**交付物**:
- `docs/adr/001-choose-vectorbt.md`
- `docs/adr/002-api-versioning.md`
- `docs/adr/003-cache-strategy.md`

**驗證標準**:
- [ ] 寫 3 個 ADR
- [ ] 包含技術選型的權衡分析
- [ ] 獲得團隊審查
- [ ] 遵循 ADR 模板

#### 5.4.4 預估學習時間

| 任務類別 | 預估時間 | 優先級 |
|---------|---------|--------|
| 複合策略設計 | 2 週 | P2 |
| 信號合併算法 | 1 週 | P2 |
| 性能優化 | 2 週 | P2 |
| Three.js 學習 | 1 週 | P2 |
| 架構設計 | 1 週 | P2 |
| 技術選型 | 1 週 | P2 |
| 實踐項目 (任務 3.1-3.4) | 8 週 | P2 |
| **總計** | **16-18 週** | |

#### 5.4.5 驗證標準

**代碼質量驗證**:
- [ ] 複合策略實現完整且可擴展
- [ ] 信號合併算法實現正確且高效
- [ ] 性能優化效果明顯（≥ 50%）
- [ ] 測試覆蓋率 ≥ 90%
- [ ] 所有提交遵循 Conventional Commits

**功能驗證**:
- [ ] 能夠組合多個策略
- [ ] 能夠使用多種信號合併算法
- [ ] 性能顯著提升
- [ ] 3D 可視化流暢
- [ ] 架構決策記錄完整

**知識驗證**:
- [ ] 能夠解釋複合策略的設計模式
- [ ] 能夠解釋性能優化的方法
- [ ] 能夠進行技術選型和權衡分析
- [ ] 能夠指導初級和中級開發者
- [ ] 能夠進行架構審查

**晉升門檻**: 總分 ≥ 85 分，且所有 P0-P2 指標達到 B 以上，領導力達到 C 以上

### 5.5 階段 4: 高級架構師 (12+ 個月)

#### 5.5.1 核心學習目標

1. **掌握微服務架構**: 能夠設計和實現微服務系統
2. **精通 DevOps**: 能夠設置 CI/CD 和容器化部署
3. **跨領域整合**: 能夠整合機器學習、實時數據流等技術
4. **技術領導力**: 能夠制定技術路線圖和培養團隊

#### 5.5.2 必備技能矩陣

**微服務技術 (P3):**

| 技能 | 內容 | 掌握程度 | 驗證方式 |
|------|------|---------|---------|
| **微服務架構** | 服務拆分、API 網關、服務發現 | ⭐⭐⭐⭐⭐ | 架構實現審查 |
| **gRPC** | Protobuf、gRPC 服務 | ⭐⭐⭐⭐⭐ | gRPC 服務實現 |
| **API 網關** | 路由、認證、限流 | ⭐⭐⭐⭐⭐ | 網關實現審查 |
| **服務發現** | Consul、etcd | ⭐⭐⭐⭐ | 服務發現集成 |
| **分布式事務** | Saga、TCC | ⭐⭐⭐ | 事務處理實現 |

**DevOps (P3):**

| 技能 | 內容 | 掌握程度 | 驗證方式 |
|------|------|---------|---------|
| **Docker** | 容器化、Docker Compose | ⭐⭐⭐⭐⭐ | 容器化所有服務 |
| **Kubernetes** | Pod、Deployment、Service | ⭐⭐⭐⭐⭐ | 部署到 K8s |
| **CI/CD** | GitHub Actions、Jenkins | ⭐⭐⭐⭐⭐ | 設置自動部署 |
| **監控** | Prometheus、Grafana | ⭐⭐⭐⭐ | 實現監控 |
| **日誌** | ELK、Loki | ⭐⭐⭐ | 集中日誌 |

**機器學習 (P3):**

| 技能 | 內容 | 掌握程度 | 驗證方式 |
|------|------|---------|---------|
| **模型訓練** | scikit-learn、XGBoost | ⭐⭐⭐⭐⭐ | 訓練 3 個模型 |
| **模型部署** | Flask、FastAPI、MLflow | ⭐⭐⭐⭐⭐ | 部署模型 |
| **特徵工程** | 數據預處理、特徵選擇 | ⭐⭐⭐⭐ | 設計特徵 |
| **模型評估** | 交叉驗證、超參調優 | ⭐⭐⭐⭐ | 優化模型 |

**技術領導力 (P3):**

| 技能 | 內容 | 掌握程度 | 驗證方式 |
|------|------|---------|---------|
| **技術路線圖** | 規劃、優先級、里程碑 | ⭐⭐⭐⭐⭐ | 制定路線圖 |
| **人才培養** | 導師計劃、技能評估 | ⭐⭐⭐⭐⭐ | 培養 3 人 |
| **技術規範** | 編碼規範、架構規範 | ⭐⭐⭐⭐⭐ | 制定規範 |
| **技術演進** | 技術債管理、重構計劃 | ⭐⭐⭐⭐⭐ | 管理技術債 |

#### 5.5.3 實踐任務清單

**任務 4.1: 微服務架構實現**

**目標**: 設計和實現完整的微服務架構

**交付物**:
```
microservices/
├── api-gateway/ (API 網關服務)
├── strategy-service/ (策略服務)
├── market-data-service/ (市場數據服務)
├── backtest-service/ (回測服務)
├── execution-service/ (執行服務)
└── docker-compose.yml
```

**驗證標準**:
- [ ] 設計服務邊界
- [ ] 實現 API 網關
- [ ] 集成服務發現
- [ ] 實現分布式事務
- [ ] 測試覆蓋率 ≥ 90%

**任務 4.2: Kubernetes 部署和監控**

**目標**: 設置 Kubernetes 集群和監控系統

**交付物**:
```
k8s/
├── api-gateway/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── ingress.yaml
├── strategy-service/
│   ├── deployment.yaml
│   └── service.yaml
├── monitoring/
│   ├── prometheus/
│   ├── grafana/
│   └── alertmanager/
└── charts/
```

**驗證標準**:
- [ ] 編寫 Kubernetes manifests
- [ ] 設置 Helm charts
- [ ] 集成 Prometheus 和 Grafana
- [ ] 設置告警系統
- [ ] 實現自動部署

**任務 4.3: 機器學習模型集成**

**目標**: 訓練和部署機器學習模型

**交付物**:
```
ml/
├── models/
│   ├── price_prediction.py
│   ├── sentiment_analysis.py
│   └── anomaly_detection.py
├── training/
│   └── train_models.py
├── deployment/
│   └── model_api.py
└── monitoring/
    └── model_monitoring.py
```

**驗證標準**:
- [ ] 訓練 3 個不同的 ML 模型
- [ ] 實現特徵工程
- [ ] 部署模型為 API 服務
- [ ] 實現模型監控
- [ ] 測試覆蓋率 ≥ 85%

**任務 4.4: 技術路線圖制定**

**目標**: 制定完整的技術路線圖

**交付物**:
```
docs/
├── roadmap/
│   ├── current_state.md
│   ├── technical_debt.md
│   ├── goals/
│   │   ├── short_term.md
│   │   └── long_term.md
│   ├── milestones.md
│   └── resource_plan.md
```

**驗證標準**:
- [ ] 分析當前技術現狀
- [ ] 識別技術債
- [ ] 制定短期和長期目標
- [ ] 規劃資源和時間
- [ ] 獲得團隊批准

#### 5.5.4 預估學習時間

| 任務類別 | 預估時間 | 優先級 |
|---------|---------|--------|
| 微服務架構 | 4 週 | P3 |
| Kubernetes | 4 週 | P3 |
| 機器學習 | 4 週 | P3 |
| 實時數據流 | 4 週 | P3 |
| 技術領導力 | 持續 | P3 |
| 實踐項目 (任務 4.1-4.4) | 16 週 | P3 |
| **總計** | **32-36 週** | |

#### 5.5.5 驗證標準

**架構質量驗證**:
- [ ] 微服務架構設計合理
- [ ] 服務邊界清晰
- [ ] API 網關功能完整
- [ ] 分布式事務處理正確
- [ ] 測試覆蓋率 ≥ 90%

**DevOps 驗證**:
- [ ] 所有服務容器化
- [ ] Kubernetes 部署成功
- [ ] CI/CD 流程自動化
- [ ] 監控和告警系統運作
- [ ] 自動部署正常

**機器學習驗證**:
- [ ] 模型訓練完成
- [ ] 模型部署成功
- [ ] 模型監控運作
- [ ] 性能指標達標
- [ ] 測試覆蓋率 ≥ 85%

**領導力驗證**:
- [ ] 技術路線圖完整
- [ ] 團隊培養計劃執行
- [ ] 技術規範制定
- [ ] 技術債管理有效
- [ ] 團隊成長明顯

**維持標準**: 總分 ≥ 85 分，且所有指標達到 B 以上

---

## 6. 評估指標和方法

### 6.1 評估體系概述

本評估體系基於 **科學量化** 和 **持續改進** 原則：

| 原則 | 說明 |
|------|------|
| **可量化性** | 所有指標應該可測量、可驗證 |
| **多維度** | 從技術、實踐、領域、領導力四個維度評估 |
| **漸進性** | 評估標準隨階段逐步提高 |
| **客觀性** | 通過自動化工具和同行審查減少主觀偏差 |
| **行動導向** | 評估結果應該直接導向具體改進行動 |

### 6.2 評估維度框架

```
技術能力 (40%)                                              │
├─ 代碼質量 (15%)                                          │
│  ├─ 測試覆蓋率 (5%)                                      │
│  ├─ Linter 通過率 (3%)                                   │
│  ├─ 代碼複雜度 (3%)                                      │
│  ├─ 代碼重複率 (2%)                                      │
│  └─ 類型註解覆蓋 (2%)                                    │
├─ 架構設計 (10-15%)                                       │
│  ├─ API 設計質量 (3-4%)                                   │
│  ├─ 狀態管理設計 (3%)                                    │
│  ├─ 策略模式應用 (2%)                                    │
│  ├─ 工廠模式應用 (2%)                                    │
│  └─ 微服務架構理解 (3-4%)                                 │
└─ 技術棧掌握 (10-15%)                                      │
   ├─ VectorBT/Backtrader (3%)                             │
   ├─ React 19 (4%)                                       │
   ├─ Zustand/React Query (4%)                             │
   └─ 策略引擎 (3%)                                        │

實踐能力 (30%)                                              │
├─ TDD 執行度 (8-10%)                                       │
│  ├─ 測試先於實現比例 (3-4%)                               │
│  ├─ 集成測試覆蓋 (3%)                                     │
│  └─ E2E 測試覆蓋 (3%)                                     │
├─ 代碼審查能力 (10-12%)                                     │
│  ├─ 審查參與頻率 (3%)                                     │
│  ├─ 審查回應時間 (2%)                                     │
│  ├─ 審查質量評分 (3-4%)                                   │
│  └─ 建設性反饋 (2%)                                       │
├─ 文檔完整性 (5-7%)                                        │
│  ├─ Docstring 覆蓋率 (3-4%)                               │
│  ├─ API 文檔質量 (2%)                                     │
│  └─ README 質量 (1-2%)                                    │
└─ Git 規範遵循度 (4-5%)                                    │
   ├─ Conventional Commits (2-3%)                          │
   ├─ PR 描述質量 (2%)                                      │
   └─ 提交粒度 (1%)                                         │

領域知識 (20%)                                              │
├─ 回測引擎掌握 (8-10%)                                      │
│  ├─ VectorBT 熟練度 (3-4%)                                │
│  ├─ Backtrader 熟練度 (3%)                               │
│  ├─ 績效指標理解 (2%)                                    │
│  └─ 參數優化理解 (1%)                                     │
├─ 策略引擎深入 (6-8%)                                       │
│  ├─ 策略工廠設計 (3%)                                     │
│  ├─ 信號合併理解 (2%)                                     │
│  └─ 策略參數管理 (1%)                                     │
└─ 技術指標掌握 (4-6%)                                       │
   ├─ 技術指標實現 (2-3%)                                   │
   └─ 指標優化 (2%)                                         │

領導力 (10%) - 僅高級/架構師階段                            │
├─ 技術指導 (6%)                                           │
│  ├─ 指導初級開發者 (2%)                                   │
│  ├─ 代碼審查指導 (2%)                                     │
│  └─ 知識傳遞 (2%)                                         │
└─ 技術決策 (4%)                                           │
   ├─ ADR 質量 (2%)                                         │
   └─ 技術選型影響 (2%)                                     │
```

### 6.3 階段 1 評估指標

#### 6.3.1 技術能力指標 (40%)

**代碼質量 (15%):**

| 指標 | 測量方法 | 權重 | 目標值 | 評分標準 |
|------|---------|------|--------|---------|
| **測試覆蓋率** | `pytest-cov` / `vitest coverage` | 5% | ≥80% | 80%=70分, 85%=80分, 90%=90分, 95+=100分 |
| **Linter 通過率** | `ruff check` / `eslint` | 3% | 100% | 100%=100分, 90%=60分, <90%=0分 |
| **代碼複雜度** | `radon` / `complexity report` | 3% | ≤10 | ≤10=100分, 15=80分, 20=60分, >20=0分 |
| **代碼重複率** | `duplication detector` | 2% | <5% | <3%=100分, 3-5%=80分, 5-10%=60分, >10%=0分 |
| **類型註解覆蓋** | `mypy` 檢查 | 2% | ≥90% | 90%=70分, 95%=80分, 100%=100分 |

**架構設計理解 (10%):**

| 指標 | 測量方法 | 權重 | 目標值 | 評分標準 |
|------|---------|------|--------|---------|
| **分層架構理解** | 代碼審查 + 問答 | 3% | 正確理解分層 | 完全理解=100分, 基本理解=70分, 不理解=0分 |
| **RESTful API 設計** | API 設計審查 | 3% | 符合 REST 原則 | 完全符合=100分, 基本符合=70分, 不符合=0分 |
| **數據模型設計** | Schema 設計審查 | 2% | 合理規範 | 合理=100分, 可改進=70分, 不合理=0分 |
| **錯誤處理** | 代碼審查 | 2% | 全面正確 | 全面=100分, 基本=70分, 不足=0分 |

**技術棧掌握 (15%):**

| 技能類別 | 具體技能 | 權重 | 測量方法 | 目標值 | 評分標準 |
|---------|---------|------|---------|--------|---------|
| **Python** | 基礎語法、異步編程 | 3% | 代碼審查 + 測試 | 熟練 | 熟練=100分, 基本=70分, 生疏=0分 |
| **FastAPI** | 路由、依賴注入、驗證 | 4% | API 實現審查 | 熟練 | 同上 |
| **React 19** | Hooks、組件、狀態 | 4% | 組件實現審查 | 熟練 | 同上 |
| **DuckDB** | 查詢、CRUD 操作 | 2% | 數據操作審查 | 熟練 | 同上 |
| **Git** | Conventional Commits | 2% | 提交歷史檢查 | 100% 遵循 | 100%=100分, 80%=70分, <80%=0分 |

#### 6.3.2 實踐能力指標 (30%)

**TDD 執行度 (10%):**

| 指標 | 測量方法 | 權重 | 目標值 | 評分標準 |
|------|---------|------|--------|---------|
| **測試先於實現比例** | Git 提交歷史分析 | 4% | ≥80% | 80%=70分, 90%=90分, 100%=100分 |
| **測試數量與功能匹配** | 測試/功能比 | 3% | ≥3:1 | 3:1=70分, 5:1=90分, 10:1=100分 |
| **AAA 模式遵循度** | 代碼審查 | 3% | 100% | 100%=100分, 80%=70分, <80%=0分 |

**代碼審查參與度 (5%):**

| 指標 | 測量方法 | 權重 | 目標值 | 評分標準 |
|------|---------|------|--------|---------|
| **PR 創建頻率** | PR 數量 / 月 | 2% | ≥4 PR/月 | 4=70分, 6=90分, 8+=100分 |
| **PR 審查回應時間** | 平均回應時間 | 2% | <24小時 | <24h=100分, 24-48h=70分, >48h=0分 |
| **審查質量評分** | 審查反饋質量 | 1% | ≥3/5 | 3=60分, 4=80分, 5=100分 |

**文檔完整性 (10%):**

| 指標 | 測量方法 | 權重 | 目標值 | 評分標準 |
|------|---------|------|--------|---------|
| **Docstring 覆蓋率** | `pydocstyle` 檢查 | 4% | ≥90% | 90%=70分, 95%=80分, 100%=100分 |
| **API 文檔完整性** | Swagger/OpenAPI 檢查 | 3% | 100% | 100%=100分, 80%=70分, <80%=0分 |
| **README 質量** | 人工審查 | 2% | 完整清晰 | 完整=100分, 基本=70分, 不完整=0分 |
| **註釋質量** | 代碼審查 | 1% | 合理必要 | 合理=100分, 過多/過少=50分, 不當=0分 |

**Git 規範遵循度 (5%):**

| 指標 | 測量方法 | 權重 | 目標值 | 評分標準 |
|------|---------|------|--------|---------|
| **Conventional Commits** | Commit 檢查 | 3% | 100% | 100%=100分, 90%=70分, <90%=0分 |
| **分支命名規範** | 分支名檢查 | 1% | 100% | 100%=100分, 否則=0分 |
| **提交粒度** | 人工審查 | 1% | 合理 | 合理=100分, 否則=0分 |

#### 6.3.3 領域知識指標 (20%)

**量化交易基礎 (8%):**

| 指標 | 測量方法 | 權重 | 目標值 | 評分標準 |
|------|---------|------|--------|---------|
| **技術指標理解** | 問答 + 實現 | 3% | 理解至少 3 個 | 3個=70分, 5個=90分, 10+=100分 |
| **回測概念理解** | 問答 | 2% | 理解基本概念 | 完全理解=100分, 基本=70分, 不理解=0分 |
| **市場數據結構** | 代碼審查 | 2% | 正確使用 | 正確=100分, 基本=70分, 錯誤=0分 |
| **交易信號概念** | 問答 | 1% | 理解買賣信號 | 理解=100分, 否則=0分 |

**策略引擎理解 (6%):**

| 指標 | 測量方法 | 權重 | 目標值 | 評分標準 |
|------|---------|------|--------|---------|
| **IStrategy 接口理解** | 問答 + 代碼審查 | 3% | 理解接口契約 | 完全理解=100分, 基本=70分, 不理解=0分 |
| **信號生成邏輯** | 代碼審查 | 2% | 正確實現 | 正確=100分, 基本=70分, 錯誤=0分 |
| **執行上下文理解** | 問答 | 1% | 理解各欄位 | 理解=100分, 否則=0分 |

**數據分析能力 (6%):**

| 指標 | 測量方法 | 權重 | 目標值 | 評分標準 |
|------|---------|------|--------|---------|
| **pandas 操作** | 代碼審查 | 3% | 熟練 | 熟練=100分, 基本=70分, 生疏=0分 |
| **數據清洗** | 代碼審查 | 2% | 正確處理 | 正確=100分, 基本=70分, 錯誤=0分 |
| **統計計算** | 代碼審查 | 1% | 正確計算 | 正確=100分, 否則=0分 |

#### 6.3.4 階段 1 總評分表

| 維度 | 權重 | 得分 | 加權得分 |
|------|------|------|---------|
| 技術能力 | 40% | ___ / 100 | ___ / 40 |
| 實踐能力 | 30% | ___ / 100 | ___ / 30 |
| 領域知識 | 20% | ___ / 100 | ___ / 20 |
| 領導力 | 0% | N/A | 0 / 0 |
| **總分** | **100%** | | **___ / 90** |

**晉升門檻**: 總分 ≥ 75 分，且所有 P0 指標達到 C 以上

### 6.4 階段 2-4 評估指標概覽

由於篇幅限制，這裡提供階段 2-4 的關鍵變化：

**階段 2 中級開發者:**
- 測試覆蓋率目標: ≥85%
- 代碼複雜度目標: ≤8
- 代碼重複率目標: <3%
- 類型註解目標: ≥95%
- 新增領導力指標: 10% (代碼審查領導力 + 知識分享)
- 晉升門檻: 總分 ≥ 80 分，所有 P0+P1 指標達到 B 以上

**階段 3 高級開發者:**
- 測試覆蓋率目標: ≥90%
- 代碼複雜度目標: ≤5
- 代碼重複率目標: <2%
- 類型註解目標: ≥98%
- 領導力指標提升: 技術指導 (6%) + 技術決策 (4%)
- 晉升門檻: 總分 ≥ 85 分，所有 P0-P2 指標達到 B 以上，領導力達到 C 以上

**階段 4 高級架構師:**
- 測試覆蓋率目標: ≥95%
- 代碼複雜度目標: ≤3
- 代碼重複率目標: <1%
- 新增安全審查指標
- 領導力指標提升: 技術領導 (6%) + 技術決策 (4%)
- 維持標準: 總分 ≥ 85 分，所有指標達到 B 以上

### 6.5 評估方法和工具

#### 6.5.1 自評工具

**自評腳本示例:**
```python
# scripts/self_assessment.py
import subprocess
import json
from pathlib import Path

class SelfAssessment:
    """自評工具"""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)

    def measure_test_coverage(self) -> float:
        """測量測試覆蓋率"""
        result = subprocess.run(
            ['pytest', '--cov=backend', '--cov-report=json'],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )

        # 解析 coverage.json
        coverage_file = self.repo_path / 'coverage.json'
        if coverage_file.exists():
            with open(coverage_file) as f:
                data = json.load(f)
            return data['totals']['percent_covered']
        return 0.0

    def measure_code_complexity(self) -> float:
        """測量代碼複雜度"""
        result = subprocess.run(
            ['radon', 'cc', 'backend/', '-a', '-j'],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            data = json.loads(result.stdout)
            # 計算平均複雜度
            total_complexity = 0
            count = 0
            for module in data.values():
                for klass in module.values():
                    for method in klass.values():
                        total_complexity += method['complexity']
                        count += 1

            if count > 0:
                return total_complexity / count
        return 0.0

    def analyze_tdd_compliance(self) -> float:
        """分析 TDD 合規性"""
        # 實現略
        pass

    def generate_report(self) -> Dict:
        """生成自評報告"""
        report = {
            'test_coverage': self.measure_test_coverage(),
            'code_complexity': self.measure_code_complexity(),
            'tdd_compliance': self.analyze_tdd_compliance()
        }

        return report
```

#### 6.5.2 代碼審查檢查清單

**通用代碼審查清單:**

```markdown
# 代碼審查檢查清單

## 代碼質量

- [ ] 測試覆蓋率是否足夠？（目標: 階段 1 ≥80%, 階段 2 ≥85%, 階段 3 ≥90%, 階段 4 ≥95%）
- [ ] 代碼複雜度是否合理？（目標: 階段 1 ≤10, 階段 2 ≤8, 階段 3 ≤5, 階段 4 ≤3）
- [ ] 是否有代碼重複？
- [ ] 是否有明顯的 bug？
- [ ] 是否有潛在的安全漏洞？
- [ ] 錯誤處理是否完善？
- [ ] 類型註解是否完整？

## 架構和設計

- [ ] 設計是否符合分層架構原則？
- [ ] API 設計是否符合 RESTful 原則？
- [ ] 數據模型設計是否合理？
- [ ] 是否有循環依賴？
- [ ] 模塊職責是否清晰？

## 測試

- [ ] 測試是否遵循 TDD 原則？
- [ ] 測試是否獨立且可重複？
- [ ] 測試是否覆蓋邊界情況？
- [ ] 是否有集成測試？
- [ ] 測試命名是否清晰？

## 文檔

- [ ] Docstring 是否完整？
- [ ] API 文檔是否更新？
- [ ] README 是否需要更新？
- [ ] 是否有適當的註釋？

## Git 和工作流

- [ ] Commit message 是否符合 Conventional Commits？
- [ ] PR 描述是否清晰完整？
- [ ] 是否拆分合理的 PR？

## 性能

- [ ] 是否有性能問題？
- [ ] 是否有必要的性能測試？
- [ ] 數據庫查詢是否優化？

## 安全

- [ ] 是否有 SQL 注入風險？
- [ ] 是否有 XSS 風險？
- [ ] 敏感信息是否硬編碼？
```

### 6.6 評估時間表和頻率

| 評估類型 | 頻率 | 責任人 | 目的 |
|---------|------|--------|------|
| **自評** | 每月 | 個人 | 自我反思和改進 |
| **代碼審查** | 每次 PR | 審查者 | 即時反饋 |
| **同行評估** | 每季度 | 團隊 | 360 度視角 |
| **項目評估** | 每項目完成後 | 項目負責人 | 項目質量評估 |
| **階段評估** | 每階段結束 | 導師 + 自評 | 晉升評估 |
| **年度評估** | 每年 | HR + 導師 | 總體發展評估 |

---

## 7. 實踐項目清單

### 7.1 實踐項目總覽

本節提供完整的實踐項目清單，分為 4 個階段，每個階段包含多個具體項目：

| 階段 | 項目數量 | 總預估時間 | 核心技能覆蓋 |
|------|---------|-----------|-------------|
| 階段 1 | 3 個項目 | 8-9 週 | P0 基礎技能 |
| 階段 2 | 4 個項目 | 10-11 週 | P0+P1 核心技能 |
| 階段 3 | 4 個項目 | 16-18 週 | P0+P1+P2 進階技能 |
| 階段 4 | 4 個項目 | 32-36 週 | P0-P3 全部技能 |

### 7.2 階段 1 實踐項目

#### 項目 1.1: CRUD API 開發

**目標**: 實現完整的項目管理系統 API

**技能覆蓋**: FastAPI、Pydantic、DuckDB、錯誤處理、pytest

**交付物**:
- `backend/routers/items.py` (150 行)
- `backend/tests/test_items.py` (100 行)
- 測試覆蓋率 ≥ 80%

**驗收標準**:
- [ ] 實現 GET/POST/PUT/DELETE 端點
- [ ] 使用 Pydantic 模型驗證
- [ ] 使用 DuckDB 存儲數據
- [ ] 統一錯誤處理
- [ ] 測試覆蓋率 ≥ 80%

#### 項目 1.2: 技術指標計算

**目標**: 實現 RSI 和 MACD 技術指標

**技能覆蓋**: pandas、NumPy、向量化計算、pytest

**交付物**:
- `backend/indicators/simple_rsi.py` (80 行)
- `backend/indicators/simple_macd.py` (80 行)
- `backend/tests/test_indicators.py` (120 行)
- 測試覆蓋率 ≥ 90%

**驗收標準**:
- [ ] 使用 pandas 進行向量化計算
- [ ] 實現 RSI 和 MACD 類
- [ ] 編寫單元測試
- [ ] 測試覆蓋率 ≥ 90%

#### 項目 1.3: 前端項目管理頁面

**目標**: 創建項目管理的前端頁面

**技能覆蓋**: React 19、Bootstrap 5、Axios、useState、表單處理

**交付物**:
- `frontend/src/pages/ItemsPage/index.jsx` (200 行)
- `frontend/src/pages/ItemsPage/__tests__/ItemsPage.test.jsx` (150 行)
- 組件測試覆蓋率 ≥ 70%

**驗收標準**:
- [ ] 使用 React 19 Hooks
- [ ] 使用 Bootstrap 5 佈局
- [ ] 整合後端 API
- [ ] 實現表單驗證
- [ ] 組件測試覆蓋率 ≥ 70%

### 7.3 階段 2 實踐項目

#### 項目 2.1: RSI 策略實現

**目標**: 掌握 IStrategy 接口和 VectorBT 回測

**技能覆蓋**: IStrategy 接口、VectorBT、回測執行、績效指標

**交付物**:
- `backend/strategies/rsi_strategy.py` (150 行)
- `backend/backtest/vectorbt_executor.py` (200 行)
- `backend/tests/test_rsi_strategy.py` (120 行)
- 測試覆蓋率 ≥ 85%

**驗收標準**:
- [ ] 實現 RSIStrategy 類
- [ ] 使用 VectorBT 執行回測
- [ ] 計算績效指標
- [ ] 測試覆蓋率 ≥ 85%

#### 項目 2.2: 策略工廠實現

**目標**: 掌握工廠模式和策略註冊機制

**技能覆蓋**: 工廠模式、策略註冊、動態實例化

**交付物**:
- `backend/strategies/factory.py` (80 行)
- `backend/tests/test_strategy_factory.py` (60 行)
- 測試覆蓋率 ≥ 90%

**驗收標準**:
- [ ] 實現 StrategyFactory 類
- [ ] 註冊內置策略
- [ ] 支持動態策略註冊
- [ ] 測試覆蓋率 ≥ 90%

#### 項目 2.3: React Query 緩存管理

**目標**: 掌握 React Query 的緩存和狀態管理

**技能覆蓋**: React Query、useApiCache、useApiMutation、快取策略

**交付物**:
- `frontend/src/hooks/useApiCache.js` (150 行)
- `frontend/src/hooks/__tests__/useApiCache.test.js` (100 行)
- 測試覆蓋率 ≥ 80%

**驗收標準**:
- [ ] 實現 useApiCache hook
- [ ] 實現 useApiMutation hook
- [ ] 實現快取預設
- [ ] 測試覆蓋率 ≥ 80%

#### 項目 2.4: Zustand 實現

**目標**: 掌握 Zustand 全局狀態管理

**技能覆蓋**: Zustand、Store、actions、selectors

**交付物**:
- `frontend/src/store/dashboardStore.js` (120 行)
- `frontend/src/store/__tests__/dashboardStore.test.js` (80 行)
- 測試覆蓋率 ≥ 85%

**驗收標準**:
- [ ] 創建 Dashboard store
- [ ] 實現 actions 和 selectors
- [ ] 整合 React Query
- [ ] 測試覆蓋率 ≥ 85%

### 7.4 階段 3 實踐項目

#### 項目 3.1: 複合策略實現

**目標**: 掌握組合策略和信號合併算法

**技能覆蓋**: CompositeStrategy、信號合併、並行計算

**交付物**:
- `backend/strategies/composite_strategy.py` (250 行)
- `backend/strategies/signal_merger.py` (200 行)
- `backend/tests/test_composite_strategy.py` (180 行)
- 測試覆蓋率 ≥ 90%

**驗收標準**:
- [ ] 實現 CompositeStrategy 類
- [ ] 實現 5 種信號合併算法
- [ ] 支持動態配置合併算法
- [ ] 測試覆蓋率 ≥ 90%

#### 項目 3.2: 性能優化

**目標**: 識別和解決性能瓶頸

**技能覆蓋**: 向量化、並行處理、多級緩存

**交付物**:
- `backend/optimization/vectorized_indicators.py` (180 行)
- `backend/optimization/parallel_backtest.py` (150 行)
- `backend/optimization/cache_manager.py` (120 行)
- 性能提升 ≥ 50%

**驗收標準**:
- [ ] 向量化指標計算
- [ ] 並行化回測執行
- [ ] 實現多級緩存
- [ ] 性能提升 ≥ 50%

#### 項目 3.3: Three.js 可視化

**目標**: 掌握 Three.js 3D 可視化

**技能覆蓋**: Three.js、3D 圖表、渲染優化

**交付物**:
- `frontend/src/components/ThreeDChart.jsx` (200 行)
- `frontend/src/components/__tests__/ThreeDChart.test.jsx` (80 行)
- 測試覆蓋率 ≥ 80%

**驗收標準**:
- [ ] 使用 Three.js 創建 3D 圖表
- [ ] 實現交互式 3D 可視化
- [ ] 優化渲染性能
- [ ] 測試覆蓋率 ≥ 80%

#### 項目 3.4: ADR 文檔

**目標**: 掌握架構決策記錄的編寫

**技能覆蓋**: ADR、技術選型、權衡分析

**交付物**:
- `docs/adr/001-choose-vectorbt.md`
- `docs/adr/002-api-versioning.md`
- `docs/adr/003-cache-strategy.md`

**驗收標準**:
- [ ] 寫 3 個 ADR
- [ ] 包含技術選型的權衡分析
- [ ] 獲得團隊審查
- [ ] 遵循 ADR 模板

### 7.5 階段 4 實踐項目

#### 項目 4.1: 微服務架構

**目標**: 設計和實現完整的微服務架構

**技能覆蓋**: 微服務、API 網關、服務發現、分布式事務

**交付物**:
```
microservices/
├── api-gateway/
├── strategy-service/
├── market-data-service/
├── backtest-service/
├── execution-service/
└── docker-compose.yml
```

**驗收標準**:
- [ ] 設計服務邊界
- [ ] 實現 API 網關
- [ ] 集成服務發現
- [ ] 實現分布式事務
- [ ] 測試覆蓋率 ≥ 90%

#### 項目 4.2: Kubernetes 部署

**目標**: 設置 Kubernetes 集群和監控系統

**技能覆蓋**: Kubernetes、Helm、Prometheus、Grafana

**交付物**:
```
k8s/
├── api-gateway/
├── strategy-service/
├── monitoring/
│   ├── prometheus/
│   ├── grafana/
│   └── alertmanager/
└── charts/
```

**驗收標準**:
- [ ] 編寫 Kubernetes manifests
- [ ] 設置 Helm charts
- [ ] 集成 Prometheus 和 Grafana
- [ ] 設置告警系統
- [ ] 實現自動部署

#### 項目 4.3: 機器學習集成

**目標**: 訓練和部署機器學習模型

**技能覆蓋**: scikit-learn、模型訓練、模型部署、模型監控

**交付物**:
```
ml/
├── models/
│   ├── price_prediction.py
│   ├── sentiment_analysis.py
│   └── anomaly_detection.py
├── training/
│   └── train_models.py
├── deployment/
│   └── model_api.py
└── monitoring/
    └── model_monitoring.py
```

**驗收標準**:
- [ ] 訓練 3 個不同的 ML 模型
- [ ] 實現特徵工程
- [ ] 部署模型為 API 服務
- [ ] 實現模型監控
- [ ] 測試覆蓋率 ≥ 85%

#### 項目 4.4: 技術路線圖

**目標**: 制定完整的技術路線圖

**技能覆蓋**: 技術規劃、資源管理、里程碑設置

**交付物**:
```
docs/
├── roadmap/
│   ├── current_state.md
│   ├── technical_debt.md
│   ├── goals/
│   ├── milestones.md
│   └── resource_plan.md
```

**驗收標準**:
- [ ] 分析當前技術現狀
- [ ] 識別技術債
- [ ] 制定短期和長期目標
- [ ] 規劃資源和時間
- [ ] 獲得團隊批准

---

## 8. 風險管理和後備方案

### 8.1 風險識別

| 風險類別 | 風險描述 | 影響程度 | 發生概率 | 風險等級 |
|---------|---------|---------|---------|---------|
| **學習曲線風險** | 新技術學習時間超出預期 | 高 | 中 | 高 |
| **質量風險** | 代碼質量不達標，影響系統穩定性 | 高 | 中 | 高 |
| **進度風險** | 項目進度延遲，影響晉升時間 | 中 | 高 | 高 |
| **資源風險** | 導師資源不足，影響學習效果 | 高 | 中 | 高 |
| **技術風險** | 技術選型錯誤，需要重新學習 | 高 | 低 | 中 |
| **文化風險** | 團隊不支持 TDD 和代碼審查文化 | 中 | 中 | 中 |

### 8.2 風險緩解措施

#### 8.2.1 學習曲線風險

**緩解措施:**
1. **漸進式學習**: 從簡單到複雜，分階段學習
2. **多種學習資源**: 官方文檔、在線課程、實踐項目
3. **導師指導**: 安排經驗豐富的開發者作為導師
4. **學習小組**: 組織學習小組，互相幫助

**後備方案:**
- 如果某個技術學習困難，調整時間表，增加學習時間
- 提供額外的培訓資源和支持

#### 8.2.2 質量風險

**緩解措施:**
1. **TDD 強制執行**: 測試先於實現，確保代碼質量
2. **代碼審查**: 所有代碼必須通過審查才能合併
3. **自動化檢查**: CI/CD 自動運行測試、linter、格式化工具
4. **質量門檻**: 設置最低質量標準，達標才能晉升

**後備方案:**
- 如果代碼質量不達標，延長當前階段，直到達標
- 提供額外的代碼審查和指導

#### 8.2.3 進度風險

**緩解措施:**
1. **明確的里程碑**: 設置清晰的里程碑和交付物
2. **定期評估**: 每週評估進度，及時調整計劃
3. **優先級管理**: 優先完成高優先級任務
4. **靈活調整**: 根據實際情況調整時間表

**後備方案:**
- 如果進度嚴重延遲，調整晉升門檻或時間表
- 提供額外的資源和支持

#### 8.2.4 資源風險

**緩解措施:**
1. **導師計劃**: 建立正式的導師計劃
2. **知識分享**: 定期組織技術分享會
3. **文檔完善**: 維護完善的技術文檔和知識庫
4. **團隊協作**: 建立積極的團隊協作文化

**後備方案:**
- 如果導師資源不足，尋找外部導師或培訓
- 如果團隊文化不支持，從小範圍開始推動 TDD 和代碼審查

### 8.3 監控和報告機制

| 監控指標 | 監控頻率 | 報告對象 | 閾值 |
|---------|---------|---------|------|
| 測試覆蓋率 | 每週 | 個人、導師 | <目標值 - 5% |
| 代碼複雜度 | 每週 | 個人、導師 | >目標值 + 2 |
| PR 審查時間 | 即時 | 審查者 | >48小時 |
| 學習進度 | 每週 | 導師 | 落後 >1週 |
| 質量評分 | 每月 | 個人、導師 | <C 等級 |

### 8.4 應急計劃

**場景 1: 技術學習嚴重困難**

症狀: 連續 2 週無法完成預期的學習任務

行動:
1. 暫停當前技術學習
2. 評估困難原因
3. 調整學習策略或更換學習資源
4. 增加導師指導時間
5. 考虑延長學習時間或調整技能優先級

**場景 2: 代碼質量長期不達標**

症狀: 連續 3 個月測試覆蓋率或代碼複雜度不達標

行動:
1. 停止新功能開發
2. 集中進行代碼重構和質量提升
3. 提供額外的代碼審查和指導
4. 可能需要重新培訓或調整角色定位

**場景 3: 導師資源不足**

症狀: 無法及時提供導師指導

行動:
1. 尋找替代導師資源
2. 建立學習小組，互相幫助
3. 利用在線社區和論壇
4. 考慮外部培訓或諮詢

---

## 9. 時間線和里程碑

### 9.1 整體時間線

```
2026-02-21: 設計規劃完成

階段 1: 初級開發者 (8-9 週)
  2026-02-22 ~ 2026-04-22
  ├─ 週 1-2: 環境設置 & Python/FastAPI 基礎
  ├─ 週 3-4: React 19 基礎
  ├─ 週 5: DuckDB & 數據操作
  ├─ 週 6: React Hooks & 表單
  ├─ 週 7: 錯誤處理 & 認證
  ├─ 週 8-9: TDD 實踐 & 項目整合
  └─ 里程碑: 總分 ≥ 75 分

階段 2: 中級開發者 (10-11 週)
  2026-04-23 ~ 2026-07-10
  ├─ 週 1-2: VectorBT 基礎
  ├─ 週 3-4: Backtrader 基礎
  ├─ 週 5-6: 策略引擎
  ├─ 週 7-8: Zustand Store
  ├─ 週 9-10: React Query
  ├─ 週 11: 集成測試
  └─ 里程碑: 總分 ≥ 80 分

階段 3: 高級開發者 (16-18 週)
  2026-07-11 ~ 2026-11-10
  ├─ 週 1-3: 複合策略
  ├─ 週 4-6: 信號合併算法
  ├─ 週 7-9: 性能優化
  ├─ 週 10-12: 架構設計
  ├─ 週 13-15: 技術選型
  ├─ 週 16-18: 領導力
  └─ 里程碑: 總分 ≥ 85 分

階段 4: 高級架構師 (32-36 週)
  2026-11-11 ~ 2027-07-25
  ├─ 週 1-4: 微服務架構
  ├─ 週 5-8: gRPC 和服務發現
  ├─ 週 9-12: Kubernetes
  ├─ 週 13-16: 機器學習
  ├─ 週 17-20: 實時數據流
  ├─ 週 21-24: 技術領導力
  ├─ 週 25-28: 技術路線圖
  ├─ 週 29-32: 人才培養
  ├─ 週 33-36: 持續改進
  └─ 維持標準: 總分 ≥ 85 分
```

### 9.2 關鍵里程碑

| 里程碑 | 日期 | 驗收標準 | 成功指標 |
|--------|------|---------|---------|
| **M1: 階段 1 完成** | 2026-04-22 | 總分 ≥ 75 分 | 所有 P0 指標達到 C 以上 |
| **M2: 階段 2 完成** | 2026-07-10 | 總分 ≥ 80 分 | 所有 P0+P1 指標達到 B 以上 |
| **M3: 階段 3 完成** | 2026-11-10 | 總分 ≥ 85 分 | 所有 P0-P2 指標達到 B 以上 |
| **M4: 階段 4 完成** | 2027-07-25 | 總分 ≥ 85 分 | 所有指標達到 B 以上 |
| **M5: 架構師認證** | 2027-08-01 | 通過架構師評估 | 維持標準 ≥ 6 個月 |

### 9.3 每月檢查點

| 月份 | 檢查項目 | 責任人 | 預期結果 |
|------|---------|--------|---------|
| 2026-03 | 階段 1 進度評估 | 導師 | 完成進度 ≥ 60% |
| 2026-04 | 階段 1 最終評估 | 導師 + 個人 | 達到晉升門檻 |
| 2026-05 | 階段 2 進度評估 | 導師 | 完成進度 ≥ 40% |
| 2026-06 | 階段 2 中期評估 | 導師 | 完成進度 ≥ 80% |
| 2026-07 | 階段 2 最終評估 | 導師 + 個人 | 達到晉升門檻 |
| 2026-08 | 階段 3 進度評估 | 導師 | 完成進度 ≥ 30% |
| 2026-09 | 階段 3 中期評估 | 導師 | 完成進度 ≥ 60% |
| 2026-10 | 階段 3 後期評估 | 導師 | 完成進度 ≥ 90% |
| 2026-11 | 階段 3 最終評估 | 導師 + 個人 | 達到晉升門檻 |
| 2026-12 | 階段 4 進度評估 | 導師 | 完成進度 ≥ 25% |
| 2027-01 | 階段 4 中期評估 | 導師 | 完成進度 ≥ 50% |
| 2027-02 | 階段 4 後期評估 | 導師 | 完成進度 ≥ 75% |
| 2027-03 | 階段 4 最終評估 | 導師 + 個人 | 達到維持標準 |

---

## 10. 結論和建議

### 10.1 總結

本設計規劃整合了 Programmer Sub-Agent 的完整能力建設、知識整合和實施指南，提供了一條從初級開發者到高級架構師的清晰路徑。文檔包含：

1. **完整的能力模型**: 4 階段能力建設路徑，清晰的技能矩陣
2. **統一的知識庫**: 整合後端、前端、策略引擎、Git 開發模式知識
3. **詳細的實施路徑**: 每個階段都有具體的學習目標、技能要求、實踐任務
4. **科學的評估體系**: 多維度評估，可量化的指標，明確的晉升門檻
5. **豐富的實踐項目**: 15 個實踐項目，覆蓋所有核心技能
6. **完善風險管理**: 識別風險，制定緩解措施和後備方案

### 10.2 核心優勢

| 優勢 | 說明 |
|------|------|
| **漸進式複雜度** | 從簡單到複雜，每個階段都有明確的目標和驗收標準 |
| **測試驅動** | 強調 TDD，確保代碼質量從一開始就得到保障 |
| **實踐優先** | 通過實際項目學習，而非純理論 |
| **知識整合** | 前後端、策略引擎、Git 開發模式知識完全整合 |
| **反饋循環** | 每個階段都有明確的驗證標準和評估機制 |
| **可量化** | 所有指標都可測量、可驗證 |
| **可執行** | 所有任務都有明確的交付物和驗證標準 |

### 10.3 實施建議

#### 10.3.1 立即行動項

1. **建立實施團隊**
   - 指定專案負責人
   - 選拔導師團隊
   - 定義角色和職責

2. **設置基礎設施**
   - 搭建開發環境
   - 配置 CI/CD
   - 建立代碼審查流程

3. **啟動階段 1**
   - 開始環境設置和基礎學習
   - 建立學習小組
   - 設置監控和報告機制

#### 10.3.2 中期行動項（1-3 個月）

1. **完善知識庫**
   - 補充更多代碼示例
   - 添加更多 FAQ
   - 建立知識分享機制

2. **優化評估體系**
   - 自動化更多評估流程
   - 完善同行評估機制
   - 建立改進計劃模板

3. **擴展實踐項目**
   - 根據實際情況調整項目
   - 添加更多真實場景項目
   - 建立項目庫

#### 10.3.3 長期行動項（6-12 個月）

1. **持續改進**
   - 收集反饋，持續優化
   - 更新技術棧和知識庫
   - 改進評估指標和方法

2. **擴展應用**
   - 推廣到其他團隊
   - 建立最佳實踐庫
   - 建立社區和知識分享平台

3. **長期跟蹤**
   - 跟蹤畢業生的職業發展
   - 收集成功案例和經驗
   - 持續改進培訓計劃

### 10.4 成功因素

| 成功因素 | 說明 | 重要性 |
|---------|------|--------|
| **管理支持** | 高層管理的大力支持是成功的關鍵 | ⭐⭐⭐⭐⭐ |
| **導師質量** | 導師的經驗和指導能力直接影響學習效果 | ⭐⭐⭐⭐⭐ |
| **學習動力** | 學習者的主動性和學習動力 | ⭐⭐⭐⭐⭐ |
| **資源投入** | 充足的時間、資源和人力投入 | ⭐⭐⭐⭐ |
| **文化支持** | 支持 TDD 和代碼審查的團隊文化 | ⭐⭐⭐⭐ |
| **持續改進** | 根據反饋持續改進培訓計劃 | ⭐⭐⭐⭐ |
| **評估機制** | 公平、透明、科學的評估機制 | ⭐⭐⭐ |

### 10.5 未來展望

本設計規劃為 Programmer Sub-Agent 提供了完整的成長路徑，未來可以進一步擴展：

1. **更多技術棧**: 添加更多前沿技術棧，如 Web3、區塊鏈等
2. **更多領域**: 擴展到其他領域，如金融科技、醫療科技等
3. **AI 輔助**: 探索 AI 輔助編程和學習
4. **全球化**: 支持多語言和全球化推廣
5. **社區建設**: 建立開發者社區，促進知識分享和協作

---

## 附錄

### A. 參考文獻

1. Dashboard 專案技術文檔
2. FastAPI 官方文檔
3. React 19 官方文檔
4. VectorBT 官方文檔
5. Backtrader 官方文檔
6. Zustand 官方文檔
7. React Query 官方文檔
8. Clean Code (Robert C. Martin)
9. Test-Driven Development (Kent Beck)
10. Design Patterns (Erich Gamma et al.)

### B. 術語表

| 術語 | 定義 |
|------|------|
| **IStrategy** | 策略接口，定義策略生成信號的契約 |
| **VectorBT** | Python 庫，用於向量化回測 |
| **Backtrader** | Python 庫，用於策略回測 |
| **Zustand** | React 狀態管理庫 |
| **React Query** | React 服務端狀態管理庫 |
| **TDD** | 測試驅動開發 |
| **AAA** | Arrange-Act-Assert 測試模式 |
| **ADR** | 架構決策記錄 |
| **Conventional Commits** | Git 提交信息規範 |
| **Git Flow** | Git 分支管理策略 |

### C. 聯繫方式

如有問題或建議，請聯繫：
- 專案負責人: [待定]
- 技術負責人: [待定]
- 電子郵件: [待定]

---

**文檔版本歷史:**

| 版本 | 日期 | 作者 | 變更說明 |
|------|------|------|---------|
| 1.0 | 2026-02-21 | Programmer Sub-Agent 設計團隊 | 初始版本，整合所有設計文檔 |

---

**文檔狀態:** Final

**審批狀態:** 待審批

**最後審閱:** 2026-02-21
