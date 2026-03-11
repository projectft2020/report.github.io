# Git 開發模式整合報告

**任務 ID:** a004e
**分析者:** Charlie Analyst
**狀態:** completed
**時間戳:** 2026-02-21T00:35:00+08:00
**輸入文件:** a004a, a004b, a004c, a004d
**專案:** Dashboard (/Users/charlie/Dashboard)

---

## 執行摘要

本報告整合了 Dashboard 專案的 Git 提交歷史分析、重構計劃、分支策略與 CI/CD 分析，以及開發工具鏈分析，形成完整的 Git 開發模式文檔。專案採用 **Sprint 模式開發**、**100% Conventional Commits 規範**、**漸進式遷移重構策略**，具備**完善的測試基礎設施**（506 個測試，86% 通過率）和**Docker 化部署流程**，但缺少**正式的 GitHub Actions CI/CD 流水線**和**明確的分支策略文檔**。

**關鍵發現：**
- ✅ **提交規範嚴格：** 100% 遵循 Conventional Commits 規範，子類型使用率 12%，任務標記使用率 16%
- ✅ **重構策略成熟：** 6 個主要重構文檔，採用漸進式遷移、向後兼容、工廠模式、介面抽象
- ✅ **測試基礎完善：** pytest + vitest + cypress，多層次測試策略，整體覆蓋率 60%
- ✅ **工具鏈完整：** 容器化部署、自動化腳本、pre-commit hooks、完整的開發/測試/部署流程
- ⚠️ **CI/CD 缺失：** 無 GitHub Actions workflows，依賴手動部署腳本
- ⚠️ **分支策略未定義：** 無分支策略文檔、PR 模板、代碼審查流程文檔

---

## 1. Git 開發模式總結

### 1.1 提交模式和頻率

#### 提交類型分佈（最近 50 次提交）

| 類型 | 數量 | 比例 | 說明 |
|------|------|------|------|
| feat | 17 | 34.0% | 新功能開發，佔比最高 |
| fix | 12 | 24.0% | 錯誤修復，第二大類型 |
| refactor | 8 | 16.0% | 代碼重構 |
| docs | 5 | 10.0% | 文檔更新 |
| test | 3 | 6.0% | 測試相關 |
| debug | 2 | 4.0% | 調試記錄 |
| feat(subtype) | 3 | 6.0% | 帶子類型的新功能 |

**總計：** 50 次提交

#### 開發節奏特徵

**日期分佈：**
- **2026-02-05:** 14 次提交 - 高強度開發日
- **2026-02-06:** 34 次提交 - 超高強度開發日（近 24 小時連續開發）
- **2026-02-07:** 1 次提交 - 維護日
- **2026-02-19:** 1 次提交 - 維護日

**特點：**
- 集中式 Sprint 開發：96% 的提交集中在 2 天內
- 平均提交頻率：約 42 分鐘/次提交（高峰時段）
- 間歇性維護：非 Sprint 日期偶爾有維護提交

**時間段偏好：**
- 晚間開發 (18:00-24:00)：60%，主要開發時段
- 下午開發 (12:00-18:00)：28%，次要開發時段
- 深夜開發 (00:00-06:00)：10%，深夜調試/趕工
- 上午開發 (06:00-12:00)：2%，最少

#### 開發週期模式

**三階段 Sprint 模式：**

```
Phase 1: 基礎架構 (2/5) - 14 commits
  ├── 策略開發 (volatility filter, ATR Breakout)
  ├── SSoT 註冊表實現
  └── 測試套件構建

Phase 2: 系統完善 (2/6) - 34 commits
  ├── 架構重構 (REF-001 到 REF-005)
  ├── 代碼質量提升 (ARCH-001 到 ARCH-008)
  ├── 功能完善 (Market Score 2.0, UI 優化)
  └── 文檔更新

Phase 3: 維護階段 (2/7, 2/19) - 2 commits
  ├── 部署配置更新
  └── 新功能添加 (SKTASR 指標)
```

#### 開發質量指標

| 指標 | 數值 | 評估 |
|------|------|------|
| 重構率 | 16% (8/50) | ✅ 積極的代碼維護 |
| 測試覆蓋 | 6% (3/50) | ⚠️ 有待提升（建議 15-20%） |
| 文檔更新 | 10% (5/50) | ✅ 適中 |
| 調試比例 | 4% (2/50) | ✅ 代碼質量較好 |

### 1.2 Conventional Commits 規範說明

#### 規範遵循情況

**遵循率：** 100% ✅

所有提交都嚴格遵循 `type: description` 格式，格式一致性極高。

#### 提交類型定義

| 類型 | 用途 | 使用頻率 |
|------|------|----------|
| `feat` | 新功能開發 | 34% |
| `fix` | Bug 修復 | 24% |
| `refactor` | 代碼重構（不改變功能） | 16% |
| `docs` | 文檔更新 | 10% |
| `test` | 測試相關 | 6% |
| `debug` | 調試記錄 | 4% |

#### 子類型使用模式

**常用子類型：**
- `feat(performance)` - 性能相關功能
- `feat(models)` - 數據模型
- `feat(ssot)` - 單一數據源
- `feat(strategies)` - 策略相關
- `feat(ui)` - 用戶界面
- `refactor(code-quality)` - 代碼質量
- `fix(technical)` - 技術性修復

**子類型使用率：** 6/50 = 12%，顯示有系統性的模塊化開發

#### 任務標記使用

**任務標記類型：**
- `ARCH-001` 到 `ARCH-008` - 架構任務
- `Q4-#18` - 季度任務
- `REF-001` 到 `REF-005` - 重構任務

**標記使用率：** 8/50 = 16%，顯示有結構化的任務管理

### 1.3 提交信息格式和最佳實踐

#### 標準格式

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

#### 實際範例

**簡短描述（20-40字符）：**
```bash
feat: add momentum indicator
fix: correct API timeout
docs: update deployment docs
```

**中等長度（41-60字符）：**
```bash
feat(performance): implement database operations for daily scheduler
fix(system): remove duplicate API prefix from system routers
```

**帶子類型：**
```bash
feat(ssot): add 5 SSoT registries with comprehensive metadata
refactor(code-quality): clean debug code from production (ARCH-001)
fix(technical): handle pandas Series in volatility reduction
```

**帶任務標記：**
```bash
feat(tests): add contract tests for critical services (ARCH-005)
refactor: complete REF-001 through REF-005 plus pytest improvements
```

#### 提交信息長度分佈

| 長度範圍 | 數量 | 比例 | 特點 |
|----------|------|------|------|
| 短描述 (20-40字符) | 28 | 56% | 簡潔明瞭 |
| 中等長度 (41-60字符) | 15 | 30% | 信息完整 |
| 長描述 (61+字符) | 7 | 14% | 詳細說明 |

#### 最佳實踐建議

**提交前檢查清單：**
1. ✅ 遵循 Conventional Commits 格式
2. ✅ 使用正確的 type（feat/fix/refactor/docs/test）
3. ✅ 描述簡潔明確（50 字符以內主標題）
4. ✅ 相關功能使用子類型分類
5. ✅ 關聯任務標記（如 ARCH-001）
6. ✅ 單次提交範圍適中（不超過 300-500 行）

**提交信息撰寫原則：**
- 使用命令語氣（如 "add" 而非 "added" 或 "adds"）
- 首字母小寫
- 結尾不加句點
- 描述改變了什麼，而不是為什麼改變
- 避免使用 "fix bug" 這種模糊描述，說明修復了什麼 bug

**壞例子 vs 好例子：**

❌ 壞例子：
```bash
fix
update stuff
doing some refactoring
```

✅ 好例子：
```bash
fix: correct indentation errors in module loader
refactor: break down monolithic files into modular components
feat: add volatility-based position size reduction
```

---

## 2. Refactoring Plan 分析

### 2.1 所有重構計劃概覽

#### 重構文檔清單

| # | 文檔 | 狀態 | 類別 | 主要內容 |
|---|------|------|------|----------|
| 1 | React Query 遷移計畫 | ✅ Adopted | Frontend | 遷移到 TanStack Query，減少代碼 30-70% |
| 2 | 符號類型統一 | ✅ Complete | Backend | 統一 symbol 類型處理，11 tests passing |
| 3 | 策略系統實作架構 | ✅ Ready | Backend | 統一策略系統，分類實現計劃 |
| 4 | 複合策略系統整合指南 | ✅ Ready | Backend | 複合和對沖策略整合，5 種回測模式 |
| 5 | 統一策略引擎設計 | ✅ Design | Backend | IStrategy + VectorBT 統一，4-5 天預估 |
| 6 | 期貨多策略組合回測系統 | ✅ Complete | New Feature | 期貨多策略回測，102 tests passing |

#### 重構範圍分類

**Frontend Refactoring:**
- React Query Migration Plan：從 requestProtection.js 遷移到 React Query

**Backend Architecture:**
- Symbol Type Unification：統一 symbol 類型處理
- Strategy System Implementation：統一策略系統架構
- Unified Strategy Engine Design：新舊策略系統統一
- Composite Strategy Integration Guide：複合策略整合

**New Feature Implementation:**
- Futures Multi-Strategy Backtest System：期貨多策略回測

### 2.2 重構策略和方法

#### 策略 1：漸進式遷移（Progressive Migration）

**應用範圍：** React Query、Strategy System、Unified Engine

**核心原則：**
1. 非破壞性變更 - 新舊代碼共存
2. 優先級驅動 - 核心/高流量組件優先遷移
3. 漸進式替換 - 不強制一次性遷移
4. 向後兼容 - 舊 API 暫時保留

**執行步驟：**
```mermaid
Phase 1: Core/Priority → Phase 2: Expansion → Phase 3: Completion
```

**實例：**
```python
# 新舊共存時期
def get_futures_spec(symbol: FuturesSymbol):
    # 舊函數，發出警告但仍然工作
    warnings.warn("Deprecated, use get_spec_for_symbol", DeprecationWarning)
    return _get_spec_impl(symbol)

def get_spec_for_symbol(symbol: Union[FuturesSymbol, str]):
    # 新函數，統一入口點
    return _get_spec_impl(symbol)
```

#### 策略 2：工廠模式（Factory Pattern）

**應用範圍：** Strategy System, Futures Backtest, Composite Integration

**實例：**
```python
class StrategyFactory:
    _strategies = {}

    @classmethod
    def register(cls, strategy_type: str, strategy_class: Type[IStrategy]):
        cls._strategies[strategy_type] = strategy_class

    @classmethod
    def create(cls, strategy_type: str, params: Dict) -> IStrategy:
        strategy_class = cls._strategies.get(strategy_type)
        if not strategy_class:
            raise ValueError(f"Unknown strategy type: {strategy_type}")
        return strategy_class(**params)

# 使用裝飾器自動註冊
@StrategyFactory.register("rsi")
class RSIStrategy(IStrategy):
    def __init__(self, period: int = 14, **kwargs):
        super().__init__(period=period, **kwargs)
        # ...
```

**優勢：**
- 開閉原則（Open-Closed Principle）：對擴展開放，對修改封閉
- 動態策略註冊：新策略無需修改引擎代碼
- 易於測試：可輕鬆替換策略實現

#### 策略 3：介面抽象（Interface Abstraction）

**應用範圍：** Strategy System, Unified Engine

**實例：**
```python
class IStrategy(ABC):
    @abstractmethod
    def generate_signals(self, context: StrategyContext) -> List[Signal]:
        pass

    @abstractmethod
    def calculate_target_weights(self, context: StrategyContext) -> Dict[str, float]:
        pass

    @abstractmethod
    def get_metadata(self) -> StrategyMetadata:
        pass
```

**優勢：**
- 所有策略類型一致的 API
- 可用 mock 實現進行測試
- 易於替換實現

#### 策略 4：適配器模式（Adapter Pattern）

**應用範圍：** Composite Integration, Unified Engine

**實例：**
```python
# SignalAdapter: IStrategy signals → VectorBT format
class SignalAdapter:
    @staticmethod
    def signals_to_vectorbt(ohlcv_index: pd.DatetimeIndex,
                           signals_by_date: Dict[date, List[Signal]]) -> pd.Series:
        """Convert IStrategy signals to VectorBT format"""
        entries = []
        for date, signals in signals_by_date.items():
            for signal in signals:
                if signal.action == "BUY":
                    entries.append((date, 1))
                elif signal.action == "SELL":
                    entries.append((date, -1))
        return pd.Series([v for d, v in entries],
                         index=pd.DatetimeIndex([d for d, v in entries]))

# FuturesResultAdapter: futures results → performance module format
class FuturesResultAdapter:
    def to_daily_metrics_input(self, futures_result: FuturesResult) -> Dict:
        """Convert futures results to performance module format"""
        return {
            "equity_curve": futures_result.equity_curve,
            "returns": futures_result.returns,
            "benchmark": futures_result.benchmark_returns
        }
```

**優勢：**
- 橋接不相容的介面
- 重用現有模組無需修改
- 清晰的關注點分離

#### 策略 5：混合架構（Mixed Architecture）

**應用範圍：** Futures Backtest, Composite Integration

**原則：** 專門化組件 + 共享模組

```
Specialized: Futures backtest engine (handles multipliers, margins)
    + Shared: Performance/Analytics modules (reused)
```

**實例：**
```python
# 專門化：期貨回測引擎
class FuturesBacktestEngine:
    def __init__(self):
        self.multiplier_lookup = MultiplierRegistry()
        self.margin_calculator = MarginCalculator()

    def run_backtest(self, strategies: List[IFuturesStrategy]):
        # 處理期貨特定邏輯（合約乘數、保證金）
        pass

# 共享：性能分析模組（重用）
class PerformanceAnalyzer:
    def analyze(self, equity_curve: pd.Series, **kwargs):
        # 通用性能分析，適用於所有回測結果
        pass
```

**優勢：**
- 正確處理領域特定邏輯
- 避免重複造輪子
- 保持系統一致性

### 2.3 重構最佳實踐

#### 最佳實踐 1：向後兼容（Backward Compatibility）

**模式：**
1. 創建新的並行實現
2. 標記舊實現為 deprecated 並發出警告
3. 漸進遷移使用
4. 在未來版本中移除棄用代碼（如 v2.0）

**實例：**
```python
def _deprecated(message: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            warnings.warn(message, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)
        return wrapper
    return decorator

@_deprecated("get_futures_spec is deprecated, use get_spec_for_symbol")
def get_futures_spec(symbol: FuturesSymbol):
    return _get_spec_impl(symbol)
```

**時間線：**
- 立即：舊函數仍然工作但發出警告
- v1.6（2 週）：開始替換調用點
- v2.0（1 個月）：移除棄用函數

#### 最佳實踐 2：測試驅動重構（Test-Driven Refactoring）

**方法：**
1. 先編寫全面的測試
2. 實施變更
3. 確保所有測試通過
4. 添加回歸測試

**覆蓋率範例：**
- Symbol Type Unification：11 個測試（Enum/string 輸入，棄用警告）
- Futures Backtest：102 個測試（4 個階段，101 通過）
- React Query：功能驗證測試

**測試金字塔：**
```
          ┌──────────────┐
          │   E2E Tests  │  關鍵流程，數量少
          ├──────────────┤
          │ Integration  │  API 層級，中等數量
          ├──────────────┤
          │  Unit Tests  │  核心邏輯，數量多
          └──────────────┘
```

#### 最佳實踐 3：配置驅動設計（Configuration-Driven Design）

**模式：** 外部化參數，允許運行時配置

**實例：**
```python
# React Query: Cache presets
CACHE_PRESETS = {
    "static": {"staleTime": 3600000, "gcTime": 86400000},  # 1h stale, 1d gc
    "dynamic": {"staleTime": 30000, "gcTime": 300000}      # 30s stale, 5m gc
}

# Futures Backtest: Capital management mode
CAPITAL_MANAGEMENT_MODES = {
    "constant": ConstantExposure,
    "floating": FloatingExposure
}

# SRS Scoring: Configurable 5-dimension weights
SRS_WEIGHTS = {
    "return": 0.30,
    "volatility": 0.20,
    "max_drawdown": 0.25,
    "sharpe_ratio": 0.15,
    "win_rate": 0.10
}
```

**優勢：**
- 易於實驗和 A/B 測試
- 環境特定配置
- 參數調優無需重啟

#### 最佳實踐 4：清晰的文檔（Clear Documentation）

**每個重構計劃包括：**
1. **決策記錄（Decision Records）** - 決定了什麼和為什麼
2. **替代方案分析（Alternative Analysis）** - 考慮的選項和權衡
3. **實施步驟（Implementation Steps）** - 分階段方法
4. **代碼範例（Code Examples）** - Before/After 比較
5. **測試策略（Testing Strategy）** - 如何驗證
6. **風險評估（Risk Assessment）** - 潛在問題和緩解措施

#### 最佳實踐 5：API 版本化策略（API Versioning Strategy）

**模式：** 新端點使用統一路由，舊端點保留

```
New: /api/backtest/unified (auto-selects best mode)
Old: /api/backtest/run (legacy, forwards internally)
```

**優勢：**
- 現有客戶端零破壞性變更
- 漸進採用新功能
- 未來棄用路徑清晰

### 2.4 重構工作流程總結

#### 標準重構生命週期

```
┌─────────────────────────────────────────────────────────────┐
│  1. 發現與分析 (Discovery & Analysis)                        │
│  - 識別問題（如高維護成本）                                 │
│  - 探索替代方案                                             │
│  - 用權衡記錄決策                                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  2. 設計與規劃 (Design & Planning)                          │
│  - 定義階段（P0, P1, P2）                                   │
│  - 指定依賴關係（DAG）                                      │
│  - 預估工作量和時間線                                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  3. 基礎建設 (Phase 1: Foundation)                          │
│  - 構建核心組件                                             │
│  - 編寫全面的測試                                           │
│  - 建立向後兼容層                                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  4. 漸進遷移 (Phase 2+: Incremental Migration)              │
│  - 遷移高優先級組件                                         │
│  - 驗證結果（比較測試）                                     │
│  - 標記舊代碼為 deprecated                                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  5. 驗證與清理 (Validation & Cleanup)                       │
│  - 回歸測試                                                 │
│  - 性能驗證                                                 │
│  - 文檔更新                                                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  6. 完成與棄用 (Completion & Deprecation)                   │
│  - 移除棄用代碼（按計劃）                                   │
│  - 最終報告                                                 │
└─────────────────────────────────────────────────────────────┘
```

#### 常見模式

**優先級定義：**
- P0：核心功能，阻塞性問題
- P1：重要功能，增強分析
- P2：擴展功能

**依賴管理：**
- 強依賴：Phase 2 要求 Phase 1 完成
- 弱依賴：Phase 5 可與 Phase 1-2 並行運行

**驗證標準：**
- 功能正確性（如 RSI 計算與 TradingView 誤差 < 1%）
- 性能基準（如 1000 點 < 100ms）
- 測試覆蓋率（> 80% 單元測試）

---

## 3. 分支策略和工作流程

### 3.1 分支結構和命名規範

#### 當前狀態

**未發現的配置文件：**
- ❌ `.github/PULL_REQUEST_TEMPLATE.md`
- ❌ `.github/workflows/*.yml`
- ❌ `CONTRIBUTING.md`
- ❌ `WORKFLOW.md`
- ❌ `CODE_REVIEW.md`

**推斷的分支策略：**

| 分支類型 | 推斷命名 | 用途 | 說明 |
|---------|---------|------|------|
| 主分支 | `main` | 生產代碼 | DEPLOYMENT.md 中提到推送到 main |
| 開發分支 | `develop`（可能） | 開發整合 | 未明確確認 |
| 功能分支 | `feature/*` | 新功能開發 | 無證據支持 |
| 修補分支 | `hotfix/*` | 緊急修復 | 無證據支持 |
| 發布分支 | `release/*` | 版本發布準備 | 無證據支持 |

#### 推薦的分支策略（Git Flow）

```
main (生產)
  ↑
  develop (開發整合)
  ↑
  ├── feature/* (功能分支)
  ├── hotfix/* (緊急修復)
  ├── release/* (發布準備)
  └── bugfix/* (一般修復)
```

#### 分支命名規範

**格式：** `<type>/<short-description>`

**類型定義：**
- `feature/*` - 新功能開發
- `fix/*` - Bug 修復
- `hotfix/*` - 緊急生產修復
- `refactor/*` - 代碼重構
- `docs/*` - 文檔更新
- `test/*` - 測試相關
- `release/*` - 版本發布準備

**命名範例：**
```bash
feature/add-momentum-indicator
fix/data-fetching-timeout
hotfix/production-deployment
refactor/restructure-database-layer
docs/update-readme
test/add-contract-tests
release/v1.0.0
```

#### 分支保護規則（建議）

**對於 `main` 分支：**
- ✅ 要求 PR 檢查通過
- ✅ 要求狀態檢查通過（CI workflow）
- ✅ 要求代碼審查（至少 1 名審查者批准）
- ✅ 要求分支是最新的（合併前更新）
- ✅ 限制誰可以推送（僅維護者）
- ✅ 要求線性歷史（禁止合併提交）

**對於 `develop` 分支：**
- ✅ 要求 PR 檢查通過
- ✅ 要求狀態檢查通過（CI workflow）
- ✅ 要求代碼審查（至少 1 名審查者批准）
- ❌ 不限制誰可以推送（開發者可推送）

### 3.2 Pull Request 流程

#### 推薦的 PR 模板

```markdown
## Pull Request 模板

### 描述
簡短描述此 PR 的目的和範圍。

### 變更類型
- [ ] 新功能 (feat)
- [ ] Bug 修復 (fix)
- [ ] 性能優化 (performance)
- [ ] 重構 (refactor)
- [ ] 文檔更新 (docs)
- [ ] 測試相關 (test)
- [ ] 調試記錄 (debug)

### 相關 Issue
關聯 Issue: #<issue_number>

### 變更摘要
- [ ] 前端變更
- [ ] 後端變更
- [ ] 資料庫變更
- [ ] Docker 配置變更

### 測試檢查清單
- [ ] 前端已編譯 (`cd frontend && npm run build`)
- [ ] 後端測試通過 (`cd backend && pytest -m "not slow"`)
- [ ] 前端測試通過 (`cd frontend && npm test -- --run`)
- [ ] E2E 測試通過（如適用）
- [ ] 測試覆蓋率未下降
- [ ] 代碼 lint 通過（`npm run lint`, `ruff check`）

### 部署檢查清單
- [ ] Docker 鏡像可構建
- [ ] 本地 Docker 測試通過
- [ ] 環境變數已更新（如需要）

### 截圖 / 演示
（如適用，添加 UI 變更的截圖）

### 審查者
@reviewer1 @reviewer2
```

#### PR 創建指南

**1. 保持 PR 小而專注：**
- 每個 PR 一個功能
- 不超過 300-500 行變更
- 清晰的標題和描述

**2. 完善的描述：**
- 為什麼需要這個變更？
- 做了什麼變更？
- 如何測試？
- 相關的 Issue 或文檔

**3. 自審：**
- 在創建 PR 之前，自我審查代碼
- 確保測試通過
- 確保構建成功

### 3.3 代碼審查流程

#### 推薦的審查標準

**功能正確性：**
- [ ] 功能符合需求
- [ ] 邊界情況已處理
- [ ] 錯誤處理完善

**代碼質量：**
- [ ] 代碼可讀性好
- [ ] 遵循項目風格
- [ ] 無重複代碼
- [ ] 適當的註釋

**測試覆蓋：**
- [ ] 新功能有測試覆蓋
- [ ] 測試通過率 100%
- [ ] 覆蓋率未下降

**安全性：**
- [ ] 無硬編碼密碼/API keys
- [ ] 適當的權限檢查
- [ ] 輸入驗證完善

**性能：**
- [ ] 無明顯性能退化
- [ ] 數據庫查詢優化
- [ ] 前端渲染優化

**文檔：**
- [ ] README 已更新（如需要）
- [ ] API 文檔已更新
- [ ] 註釋清晰

#### 審查者角色建議

| 角色 | 職責 | 建議人員 |
|------|------|---------|
| 技術審查者 | 代碼質量、架構 | 資深開發者 |
| 功能審查者 | 功能正確性、需求 | 產品經理/需求方 |
| 測試審查者 | 測試覆蓋、測試質量 | QA 工程師 |
| 安全審查者 | 安全漏洞、權限 | 安全專家（如需要） |

#### 審查流程

**1. 快速審查：**
- 確認 PR 描述清晰
- 確認測試覆蓋充分
- 確認沒有明顯問題

**2. 深入審查：**
- 代碼邏輯正確性
- 代碼質量和風格
- 性能影響
- 安全性

**3. 建設性反饋：**
- 解釋為什麼要修改
- 提供具體建議
- 對代碼不對人

#### 合併策略

**Squash and Merge（推薦）：**
- 清理提交歷史
- 每個 PR 一個提交
- 適合功能分支

**Rebase and Merge：**
- 保持線性歷史
- 適於小團隊
- 需要更嚴格的分支管理

**Merge Commit：**
- 保留完整歷史
- 適於大團隊
- 歷史可能較亂

---

## 4. CI/CD 流程說明

### 4.1 CI/CD Workflow 配置

#### 當前狀態

**❌ GitHub Actions Workflows 不存在**

`.github/workflows/` 目錄不存在，這是一個重大的 CI/CD 缺失。項目依賴手動執行測試和部署。

#### 推薦的 GitHub Actions Workflows

**4.1.1 CI Workflow: `.github/workflows/ci.yml`**

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '24'

      - name: Install backend lint tools
        run: |
          pip install ruff black isort mypy

      - name: Install frontend dependencies
        run: |
          cd frontend && npm ci

      - name: Backend lint
        run: |
          ruff check backend/
          black --check backend/
          isort --check-only backend/
          mypy backend/

      - name: Frontend lint
        run: |
          cd frontend
          npm run lint
          npm run type-check

  test-backend:
    name: Backend Tests
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt

      - name: Run smoke tests
        run: |
          cd backend
          python -m pytest -m "smoke or fast" -v

      - name: Run unit tests
        run: |
          cd backend
          python -m pytest -m "unit and not slow" -v

      - name: Run full tests
        if: github.event_name == 'push' && (github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop')
        run: |
          cd backend
          python -m pytest -v --cov=. --cov-report=xml --cov-report=term

      - name: Upload coverage to Codecov
        if: github.event_name == 'push'
        uses: codecov/codecov-action@v4
        with:
          file: ./backend/coverage.xml
          flags: backend

  test-frontend:
    name: Frontend Tests
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '24'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      - name: Run unit tests
        run: |
          cd frontend
          npm run test -- --run

      - name: Run coverage
        if: github.event_name == 'push' && (github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop')
        run: |
          cd frontend
          npm run test:coverage

      - name: Upload coverage to Codecov
        if: github.event_name == 'push'
        uses: codecov/codecov-action@v4
        with:
          file: ./frontend/coverage/coverage-final.json
          flags: frontend

  test-e2e:
    name: E2E Tests
    runs-on: ubuntu-latest
    needs: [test-backend, test-frontend]
    if: github.event_name == 'push' && (github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop')
    steps:
      - uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '24'

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      - name: Run E2E tests
        run: |
          cd frontend
          npm run test:e2e

      - name: Upload E2E screenshots
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: cypress-screenshots
          path: frontend/cypress/screenshots

  build:
    name: Build
    runs-on: ubuntu-latest
    needs: [test-backend, test-frontend]
    steps:
      - uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '24'

      - name: Build frontend
        run: |
          cd frontend
          npm ci
          npm run build

      - name: Upload frontend build
        uses: actions/upload-artifact@v4
        with:
          name: frontend-dist
          path: frontend/dist
```

**4.1.2 CD Workflow: `.github/workflows/cd.yml`**

```yaml
name: CD

on:
  push:
    branches: [ main ]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deployment environment'
        required: true
        default: 'production'
        type: choice
        options:
          - production
          - staging

jobs:
  deploy:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: build
    environment:
      name: production
      url: http://172.235.215.225
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build Docker image
        run: |
          docker buildx build \
            --platform linux/amd64 \
            -t dashboard-app:${{ github.sha }} \
            -t dashboard-app:latest \
            -f Dockerfile \
            .

      - name: Export Docker image
        run: |
          docker save dashboard-app:latest | gzip > dashboard-app.tar.gz

      - name: Setup SSH
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.LINODE_SSH_KEY }}" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa
          ssh-keyscan -H ${{ secrets.LINODE_HOST }} >> ~/.ssh/known_hosts

      - name: Transfer Docker image to production
        run: |
          scp -o StrictHostKeyChecking=no \
            dashboard-app.tar.gz \
            root@${{ secrets.LINODE_HOST }}:/tmp/

      - name: Deploy on production server
        run: |
          ssh -o StrictHostKeyChecking=no root@${{ secrets.LINODE_HOST }} << 'ENDSSH'
            set -e
            echo "[Production] Stopping current container..."
            docker stop dashboard_app 2>/dev/null || true
            docker rm dashboard_app 2>/dev/null || true

            echo "[Production] Loading new Docker image..."
            docker load < /tmp/dashboard-app.tar.gz

            echo "[Production] Starting new container..."
            docker run -d \
              --name dashboard_app \
              --network dashboard_network \
              -v dashboard_data:/app/backend/market_data_db \
              -v app_logs:/app/backend/logs \
              -e ENV=production \
              -e PYTHONUNBUFFERED=1 \
              -e SKIP_AUTO_IMPORT=true \
              --restart unless-stopped \
              --health-cmd 'curl -f http://localhost:8000/health || exit 1' \
              --health-interval 30s \
              --health-timeout 10s \
              --health-retries 3 \
              --health-start-period 40s \
              dashboard-app:latest

            echo "[Production] Waiting for container to be healthy..."
            sleep 15
          ENDSSH

      - name: Health check
        run: |
          sleep 5
          curl -f http://${{ secrets.LINODE_HOST }}/health || exit 1

      - name: Notify deployment success
        if: success()
        run: |
          echo "Deployment successful!"
```

### 4.2 構建和部署步驟

#### 當前部署流程（手動）

**前置檢查清單（README.md）：**
```bash
# 在執行 git push 同步到伺服器之前，務必確保前端已經編譯為最新版本

# 1. 編譯前端
cd frontend && npm run build

# 2. 更新後端靜態檔案
# 將 frontend/dist 內容複製到 backend/static

# 3. 提交並啟動
# 執行 git push 後，確保遠端伺服器重啟以載入最新變更
```

#### 推薦的自動化部署流程

**使用 `scripts/deploy.sh` 腳本：**
```bash
./scripts/deploy.sh production
```

**腳本功能：**
1. 構建 Docker 鏡像（linux/amd64 平台）
2. 導出並壓縮鏡像
3. 通過 SSH 傳輸到生產服務器
4. 可選：傳輸資料庫
5. 在生產服務器上部署新版本
6. 驗證健康狀態

**部署配置：**
- 生產服務器：`root@172.235.215.225`
- 鏡像名稱：`dashboard-app:latest`
- 平台：`linux/amd64`

#### Docker 部署配置

**生產環境：`docker-compose.yml`**
```yaml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - dashboard_data:/app/backend/market_data_db
    environment:
      - ENV=production
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

**開發環境：`docker-compose.dev.yml`**
```yaml
services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.dev
      target: development
    ports:
      - "8001:8000"
    volumes:
      - ./backend:/app/backend
      - ./tracked_symbols.json:/app/tracked_symbols.json
    environment:
      - ENV=development
      - PYTHONUNBUFFERED=1
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    ports:
      - "5173:5173"
    volumes:
      - ./frontend/src:/app/src
      - ./frontend/public:/app/public
    environment:
      - NODE_ENV=development
      - VITE_API_URL=http://backend:8000
    command: npm run dev -- --host 0.0.0.0
```

### 4.3 CI/CD 最佳實踐

#### 最佳實踐 1：分層測試策略

**測試分類：**
```yaml
# pytest markers
- smoke: 快速冒煙測試，關鍵路徑
- fast: 快速單元測試（<1s each）
- unit: 單元測試
- integration: 集成測試
- slow: 慢速測試（需要外部資源或計算密集）
```

**CI 執行策略：**
```yaml
# PR: 只運行快速測試
pytest -m "smoke or fast or unit"

# develop: 運行所有測試（除 slow）
pytest -m "not slow"

# main: 運行完整測試套件
pytest -v --cov=. --cov-report=xml
```

#### 最佳實踐 2：並行測試執行

**pytest-xdist 配置：**
```ini
[pytest]
addopts = -n auto  # 自動使用所有 CPU 核心
```

**CI 並行配置：**
```yaml
strategy:
  matrix:
    python-version: ['3.11']
    node-version: ['24']
```

#### 最佳實踐 3：覆蓋率門檻

**推薦覆蓋率目標：**
- 後端：> 80%
- 前端 utils：> 90%
- 前端 components：> 70%

**當前狀態（TEST_BADGES.md）：**
| 類別 | 測試數 | 通過率 | 覆蓋率 | 目標 |
|----------|-------|-----------|----------|------|
| 🐍 後端 | 244 | 91% | 70% | 80% |
| ⚛️ 前端工具 | 152 | 100% | 100% | ✅ |
| ⚛️ 前端組件 | 110 | 63% | ~30% | 70% |
| **總計** | **506** | **86%** | **60%** | 80% |

#### 最佳實踐 4：健康檢查和自動重啟

**Docker 健康檢查：**
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

**自動重啟策略：**
```yaml
restart: unless-stopped  # 生產環境
restart: on-failure      # 開發環境（可選）
```

#### 最佳實踐 5：環境變量管理

**GitHub Secrets：**
```yaml
# CI/CD workflow
env:
  LINODE_HOST: ${{ secrets.LINODE_HOST }}
  LINODE_SSH_KEY: ${{ secrets.LINODE_SSH_KEY }}
```

**.env.example：**
```bash
ENV=development
ALLOW_EXTERNAL_API=False
ENABLE_BACKGROUND_WORKER=False
DATABASE_URL=duckdb:///backend/market_data_db/data.duckdb
```

---

## 5. 開發工具鏈清單

### 5.1 開發依賴（後端）

#### 核心框架與運行時

| 依賴 | 版本 | 用途 |
|------|------|------|
| `fastapi` | >=0.128.0 | Web 框架 |
| `uvicorn[standard]` | >=0.40.0 | ASGI 服務器 |
| `watchfiles` | >=0.21.0 | 熱重載支持 |
| `gunicorn` | latest | 生產環境 WSGI 服務器 |

#### 數據處理與分析

| 依賴 | 版本 | 用途 |
|------|------|------|
| `duckdb` | ==1.1.0 | 內嵌式分析型數據庫 |
| `pandas` | ==2.3.3 | 數據處理庫 |
| `numpy` | >=2.0.0 | 數值計算庫 |
| `scipy` | >=1.13.0 | 科學計算庫 |
| `yfinance` | >=0.2.51 | Yahoo Finance API |
| `pandas-ta-classic` | ==0.3.54 | 技術分析庫 |
| `backtrader` | latest | 回測框架 |
| `vectorbt` | ==0.28.2 | 向量化回測庫 |

#### 任務調度與處理

| 依賴 | 版本 | 用途 |
|------|------|------|
| `APScheduler` | latest | 任務調度器 |

#### 工具與庫

| 依賴 | 版本 | 用途 |
|------|------|------|
| `pydantic` | latest | 數據驗證 |
| `requests` | latest | HTTP 客戶端 |
| `httpx` | latest | 異步 HTTP 客戶端 |
| `python-multipart` | latest | 文件上傳支持 |
| `tqdm` | latest | 進度條 |

#### 測試依賴

| 依賴 | 版本 | 用途 |
|------|------|------|
| `pytest` | latest | 測試框架 |
| `pytest-xdist` | latest | 並行測試 |
| `pytest-timeout` | latest | 超時測試 |
| `pytest-cov` | latest | 覆蓋率測試 |

### 5.2 開發依賴（前端）

#### 核心框架與庫

| 依賴 | 版本 | 用途 |
|------|------|------|
| `react` | ^19.2.0 | React 框架 |
| `react-dom` | ^19.2.0 | DOM 渲染 |
| `react-router-dom` | ^7.11.0 | 路由管理 |
| `zustand` | ^5.0.9 | 狀態管理 |
| `@tanstack/react-query` | ^5.90.16 | 數據獲取與緩存 |

#### UI 組件與樣式

| 依賴 | 版本 | 用途 |
|------|------|------|
| `bootstrap` | ^5.3.8 | CSS 框架 |
| `react-bootstrap` | ^2.10.10 | React Bootstrap 組件 |
| `bootstrap-icons` | ^1.13.1 | 圖標庫 |
| `lucide-react` | ^0.562.0 | React 圖標 |

#### 圖表與可視化

| 依賴 | 版本 | 用途 |
|------|------|------|
| `chart.js` | ^4.5.1 | 圖表庫 |
| `react-chartjs-2` | ^5.3.1 | React Chart.js 封裝 |
| `echarts` | ^6.0.0 | ECharts 圖表 |
| `echarts-for-react` | ^3.0.5 | React ECharts 封裝 |
| `recharts` | ^3.6.0 | React 圖表庫 |
| `chartjs-adapter-date-fns` | ^3.0.0 | 時間適配器 |
| `chartjs-plugin-annotation` | ^3.1.0 | 註解插件 |
| `chartjs-plugin-zoom` | ^2.2.0 | 縮放插件 |

#### 3D 與高級可視化

| 依賴 | 版本 | 用途 |
|------|------|------|
| `three` | ^0.182.0 | 3D 庫 |
| `@react-three/fiber` | ^9.5.0 | React Three.js |
| `@react-three/drei` | ^10.7.7 | Three.js 實用工具 |

#### 工具與實用程序

| 依賴 | 版本 | 用途 |
|------|------|------|
| `axios` | ^1.13.2 | HTTP 客戶端 |
| `date-fns` | ^4.1.0 | 日期處理 |
| `luxon` | ^3.7.2 | 時間處理 |
| `html2canvas` | ^1.4.1 | HTML 轉圖片 |
| `d3-hierarchy` | ^3.1.2 | D3 層次結構 |
| `i18next` | ^25.7.4 | 國際化 |
| `react-i18next` | ^16.5.3 | React 國際化 |

### 5.3 自動化工具

#### 構建工具

| 工具 | 用途 | 配置 |
|------|------|------|
| `vite` | ^7.2.4 | 前端構建工具 | `vite.config.js` |
| `@vitejs/plugin-react` | ^5.1.1 | React 插件 | Vite 配置 |
| `docker` | latest | 容器化部署 | `Dockerfile`, `docker-compose.yml` |

#### 測試工具

| 工具 | 用途 | 配置 |
|------|------|------|
| `pytest` | latest | 後端測試框架 | `pytest.ini` |
| `pytest-xdist` | latest | 並行測試 | `pytest.ini` (-n auto) |
| `pytest-timeout` | latest | 超時測試 | `pytest.ini` (10s) |
| `pytest-cov` | latest | 覆蓋率測試 | `pytest.ini` |
| `vitest` | ^4.0.18 | 前端測試框架 | `vitest.config.js` |
| `@vitest/coverage-v8` | ^4.0.18 | 覆蓋率工具 | `vitest.config.js` |
| `cypress` | ^15.9.0 | E2E 測試 | `cypress.config.js` |
| `@testing-library/react` | ^16.3.1 | React 測試庫 | 測試配置 |
| `happy-dom` | ^20.0.11 | DOM 模擬 | vitest 配置 |

#### 代碼質量工具

| 工具 | 用途 | 配置 |
|------|------|------|
| `ruff` | latest | Python linter | `ruff.toml` |
| `black` | latest | Python formatter | `black.toml` |
| `isort` | latest | Python import sorter | `isort.cfg` |
| `mypy` | latest | Python type checker | `mypy.ini` |
| `eslint` | ^9.39.1 | JavaScript linter | `eslint.config.js` |
| `eslint-plugin-react-hooks` | ^7.0.1 | React Hooks 插件 | ESLint 配置 |
| `pre-commit` | latest | Git hooks | `.pre-commit-config.yaml` |

#### Makefile 自動化目標

```makefile
# 測試
test           - 運行所有測試（排除慢速）
test-smoke     - 運行冒煙測試
test-unit      - 運行單元測試
test-full      - 運行完整測試套件
test-new       - 運行最近修改文件的測試
test-coverage  - 運行覆蓋率測試
```

#### NPM Scripts

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "test": "vitest",
    "test:watch": "vitest --watch",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage",
    "test:e2e": "cypress run",
    "test:e2e:open": "cypress open",
    "test:e2e:mobile": "cypress run --viewport 375x667",
    "test:e2e:tablet": "cypress run --viewport 768x1024",
    "test:e2e:desktop": "cypress run --viewport 1920x1080",
    "lint": "eslint .",
    "type-check": "tsc --noEmit"
  }
}
```

### 5.4 工具鏈配置

#### Docker 配置

**多階段構建（生產）：**
```dockerfile
# Stage 1: Build React Frontend
FROM node:24-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --production=false
COPY frontend/ .
RUN npm run build

# Stage 2: Python Backend
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y curl
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./backend/
COPY --from=frontend-build /app/frontend/dist ./backend/static
COPY tracked_symbols.json .
WORKDIR /app/backend
CMD ["gunicorn", "-w", "1", "-k", "uvicorn.workers.UvicornWorker",
     "main:app", "--bind", "0.0.0.0:8000", "--timeout", "120"]
```

#### Vite 配置（開發）

```javascript
// vite.config.js
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true
      }
    },
    host: '0.0.0.0',
    port: 5173
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@services': path.resolve(__dirname, './src/services')
    }
  }
})
```

#### Pytest 配置

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
addopts =
    -v
    --tb=line
    --strict-markers
    -n auto
    --timeout=10
    --timeout-method=thread
    -m "not slow"
    -rN

markers =
    smoke: Quick smoke tests
    fast: Fast unit tests (<1s each)
    slow: marks tests as slow
    integration: marks tests as integration
    unit: marks tests as unit tests
```

#### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-merge-conflict
      - id: debug-statements
      - id: check-todos
```

---

## 6. 開發流程最佳實踐

### 6.1 完整的開發工作流程

#### 開發流程圖

```
┌─────────────────────────────────────────────────────────────┐
│  1. 開始新任務 / 需求確認                                    │
│  - 創建或關聯 Issue                                         │
│  - 明確需求和驗收標準                                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  2. 創建功能分支                                            │
│  git checkout develop                                       │
│  git pull origin develop                                   │
│  git checkout -b feature/feature-name                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  3. 開發實現                                                │
│  - 編寫代碼                                                 │
│  - 遵循代碼風格（ruff, black, eslint）                     │
│  - 使用 Conventional Commits 格式提交                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  4. 測試                                                    │
│  - 單元測試（pytest, vitest）                               │
│  - 集成測試                                                 │
│  - E2E 測試（cypress）                                     │
│  - 覆蓋率檢查                                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  5. 代碼審查準備                                            │
│  - 自我審查                                                 │
│  - 編譯前端（npm run build）                                │
│  - 更新文檔                                                 │
│  - 提交並推送                                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  6. 創建 Pull Request                                      │
│  - 使用 PR 模板                                             │
│  - 關聯 Issue                                              │
│  - 清晰描述變更                                             │
│  - 添加截圖/演示（如適用）                                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  7. CI 自動檢查                                            │
│  - Lint 檢查                                               │
│  - 測試運行                                                 │
│  - 構建驗證                                                 │
│  - 覆蓋率報告                                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  8. 代碼審查                                                │
│  - 審查者審查代碼                                           │
│  - 討論和改進                                               │
│  - 修復問題                                                 │
│  - 審查通過                                                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  9. 合併到 develop                                          │
│  - Squash and Merge（推薦）                                 │
│  - 更新 develop 分支                                        │
│  - 刪除功能分支                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  10. 集成測試（develop 分支）                              │
│  - CI 自動運行完整測試套件                                  │
│  - 手動測試關鍵流程                                         │
│  - 驗證功能完整性                                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  11. 發布準備（release/* 分支）                            │
│  git checkout develop                                       │
│  git pull origin develop                                   │
│  git checkout -b release/v1.0.0                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  12. 發布到 main                                            │
│  - 創建 PR: release/v1.0.0 → main                          │
│  - CI/CD 自動部署到生產                                     │
│  - 健康檢查驗證                                             │
│  - 合併回 develop                                          │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 代碼質量保證

#### 質量保證層次

```
         ┌─────────────────┐
         │  代碼審查       │  Peer review, 架構評估
         ├─────────────────┤
         │  CI/CD          │  自動化測試, 構建, 部署
         ├─────────────────┤
         │  測試覆蓋       │  單元, 集成, E2E
         ├─────────────────┤
         │  代碼檢查       │  Lint, 格式化, 類型檢查
         ├─────────────────┤
         │  開發規範       │  命名, 結構, 文檔
         └─────────────────┘
```

#### 代碼風格規範

**Python 後端：**
```python
# 使用 ruff + black + isort
# ruff check backend/
# black backend/
# isort backend/

# 風格規則：
# - 最大行長度: 100 字符
# - 引號: 單引號優先
# - 縮進: 4 空格
# - 導入順序: stdlib, third-party, local
```

**JavaScript/TypeScript 前端：**
```javascript
// 使用 eslint + prettier
// npm run lint
// npm run type-check

// 風格規則：
// - 最大行長度: 100 字符
// - 引號: 單引號優先
// - 縮進: 2 空格
// - 結尾分號: 必需
```

#### 測試覆蓋率目標

| 層級 | 目標覆蓋率 | 當前覆蓋率 | 差距 |
|------|-----------|-----------|------|
| 後端單元測試 | > 80% | 70% | -10% |
| 前端 utils | > 90% | 100% | ✅ |
| 前端 components | > 70% | ~30% | -40% |
| 集成測試 | > 70% | 未統計 | - |
| E2E 測試 | 關鍵流程 | 部分覆蓋 | - |

#### 代碼審查清單

**功能正確性：**
- [ ] 功能符合需求
- [ ] 邊界情況已處理
- [ ] 錯誤處理完善

**代碼質量：**
- [ ] 代碼可讀性好
- [ ] 遵循項目風格
- [ ] 無重複代碼
- [ ] 適當的註釋

**測試覆蓋：**
- [ ] 新功能有測試覆蓋
- [ ] 測試通過率 100%
- [ ] 覆蓋率未下降

**安全性：**
- [ ] 無硬編碼密碼/API keys
- [ ] 適當的權限檢查
- [ ] 輸入驗證完善

**性能：**
- [ ] 無明顯性能退化
- [ ] 數據庫查詢優化
- [ ] 前端渲染優化

### 6.3 協作和審查流程

#### 協作原則

**1. 小而頻繁的 PR：**
- 每個 PR 一個功能
- 不超過 300-500 行變更
- 頻繁合併避免大型合併衝突

**2. 清晰的溝通：**
- PR 標題和描述清楚
- 說明變更原因
- 提供測試方法
- 適時使用截圖/錄屏

**3. 建設性反饋：**
- 對代碼不對人
- 解釋為什麼要修改
- 提供具體建議
- 承認好的做法

**4. 快速響應：**
- 審查者及時響應（24 小時內）
- 提交者快速修復問題
- 避免阻塞他人工作

#### 審查流程

**1. 快速審查（< 30 分鐘）：**
- 確認 PR 描述清晰
- 確認測試覆蓋充分
- 確認沒有明顯問題

**2. 深入審查（< 2 小時）：**
- 代碼邏輯正確性
- 代碼質量和風格
- 性能影響
- 安全性

**3. 修復和重新審查：**
- 提交者修復問題
- 審查者驗證修復
- 可能多輪迭代

#### 角色和職責

| 角色 | 職責 | 活躍度 |
|------|------|--------|
| 開發者 | 編寫代碼、測試、創建 PR | 每天 |
| 審查者 | 審查代碼、提供反饋 | 每天 |
| 維護者 | 合併 PR、管理發布 | 定期 |
| QA | 測試驗證、回歸測試 | 發布前 |

#### 溝通渠道

**PR 討論：**
- 使用 GitHub PR 評論
- 提及相關人員（@username）
- 關聯相關 Issue

**即時溝通：**
- 關鍵問題使用即時通訊工具
- 非緊急問題使用異步溝通

**文檔更新：**
- 變更後更新相關文檔
- 在 PR 中說明文檔更新

---

## 7. Programmer Sub-Agent 的開發流程知識基礎

### 7.1 關鍵開發能力要求

#### 必備能力（Priority P0）

**1. Git 和版本控制：**
```yaml
能力: 熟練使用 Git
證據: Dashboard 100% Conventional Commits 規範
要求:
  - 熟悉分支策略（Git Flow）
  - 遵循 Conventional Commits 格式
  - 正確處理合併衝突
  - 理解 rebase vs merge
```

**2. 測試驅動開發：**
```yaml
能力: TDD 和測試編寫
證據: 506 個測試，86% 通過率
要求:
  - 單元測試編寫（pytest, vitest）
  - 測試覆蓋率管理
  - Mock 和 fixture 使用
  - 測試金字塔原則
```

**3. 代碼質量意識：**
```yaml
能力: 代碼質量保證
證據: 重構率 16%，調試率 4%
要求:
  - 代碼審查參與
  - Lint 和格式化工具使用
  - 重構能力（漸進式遷移）
  - 技術債務管理
```

**4. CI/CD 理解：**
```yaml
能力: CI/CD 流程理解
證據: Docker 化部署，健康檢查
要求:
  - 理解 CI/CD pipeline
  - 編寫 workflow 配置
  - 環境變量管理
  - 部署自動化
```

#### 進階能力（Priority P1）

**1. 架構設計：**
```yaml
能力: 軟件架構理解
證據: 6 個重構計劃，多種設計模式
要求:
  - 設計模式應用（工廠、適配器、介面抽象）
  - 模組化設計
  - API 設計
  - 數據庫設計
```

**2. 性能優化：**
```yaml
能力: 性能優化
證據: feat(performance) 提交，並行測試
要求:
  - 數據庫查詢優化
  - 前端渲染優化
  - 緩存策略
  - 並發和異步處理
```

**3. 容器化和部署：**
```yaml
能力: Docker 和部署
證據: 多階段 Dockerfile，docker-compose
要求:
  - Dockerfile 編寫
  - Docker Compose 配置
  - 容器編排
  - 健康檢查和監控
```

#### 可選能力（Priority P2）

**1. DevOps：**
```yaml
能力: DevOps 實踐
證據: 部署腳本，自動化工具
要求:
  - 監控和日誌
  - 備份和恢復
  - 基礎設施即代碼
  - 安全加固
```

**2. 文檔和知識管理：**
```yaml
能力: 技術文檔
證據: docs 提交佔 10%
要求:
  - API 文檔編寫
  - 架構文檔
  - README 維護
  - 決策記錄（ADR）
```

### 7.2 開發工具優先級

#### 工具優先級矩陣

| 工具類別 | 工具 | 優先級 | 熟練度要求 |
|---------|------|--------|-----------|
| 版本控制 | Git | P0 | 熟練 |
| 後端測試 | pytest | P0 | 熟練 |
| 前端測試 | vitest | P0 | 熟練 |
| 代碼檢查 | ruff/black | P0 | 熟練 |
| 代碼檢查 | eslint | P0 | 熟練 |
| 後端框架 | FastAPI | P0 | 熟練 |
| 前端框架 | React | P0 | 熟練 |
| E2E 測試 | cypress | P1 | 中等 |
| 容器化 | Docker | P1 | 中等 |
| 數據處理 | pandas | P1 | 中等 |
| 圖表庫 | Chart.js/ECharts | P1 | 中等 |
| 數據庫 | DuckDB | P2 | 基礎 |
| 狀態管理 | Zustand | P2 | 基礎 |
| 數據獲取 | React Query | P2 | 基礎 |

#### 工具學習路徑

**階段 1：基礎工具（P0）**
```yaml
目標: 能獨立開發和測試
工具:
  - Git: 分支、提交、合併
  - pytest/vitest: 單元測試編寫
  - ruff/eslint: 代碼檢查和格式化
  - FastAPI: REST API 開發
  - React: 組件開發
預計時間: 2-3 週
```

**階段 2：進階工具（P1）**
```yaml
目標: 能進行集成和部署
工具:
  - cypress: E2E 測試
  - Docker: 容器化開發
  - pandas: 數據處理
  - Chart.js/ECharts: 數據可視化
預計時間: 2-3 週
```

**階段 3：專業工具（P2）**
```yaml
目標: 能處理複雜場景
工具:
  - DuckDB: 內嵌式數據庫
  - Zustand: 狀態管理
  - React Query: 數據獲取和緩存
預計時間: 1-2 週
```

### 7.3 開發工作流程建議

#### Programmer Sub-Agent 工作流

**1. 任務接收和規劃：**
```yaml
步驟:
  - 接收任務描述和需求
  - 分析相關 Issue 和文檔
  - 識別依賴和風險
  - 制定實施計劃
輸出:
  - 任務拆解
  - 實施步驟
  - 預估時間
```

**2. 開發環境準備：**
```yaml
步驟:
  - 創建功能分支
  - 拉取最新代碼
  - 設置環境變量
  - 啟動開發服務器
驗證:
  - 服務正常啟動
  - 測試通過
  - 無編譯錯誤
```

**3. 代碼實現：**
```yaml
原則:
  - 遵循項目代碼風格
  - 小步快跑，頻繁提交
  - 使用 Conventional Commits 格式
  - 適時重構
檢查:
  - 代碼 lint 通過
  - 測試通過
  - 類型檢查通過
```

**4. 測試和驗證：**
```yaml
測試層次:
  - 單元測試：覆蓋核心邏輯
  - 集成測試：驗證模組交互
  - E2E 測試：驗證關鍵流程
覆蓋率目標:
  - 新代碼：> 80%
  - 修改代碼：不下降
```

**5. 代碼審查準備：**
```yaml
準備:
  - 自我審查代碼
  - 更新相關文檔
  - 編寫 PR 描述
  - 添加測試證據
模板:
  - 變更類型
  - 相關 Issue
  - 測試檢查清單
  - 部署檢查清單
```

**6. 持續改進：**
```yaml
學習:
  - 從審查反饋學習
  - 分析失敗的測試
  - 研究最佳實踐
  - 總結經驗教訓
改進:
  - 更新知識庫
  - 分享最佳實踐
  - 改進工具鏈
  - 優化工作流
```

#### 常見工作場景

**場景 1：添加新功能**
```yaml
流程:
  1. 理解需求和設計
  2. 創建功能分支
  3. TDD 開發（紅-綠-重構）
  4. 編寫單元測試
  5. 實現功能代碼
  6. 編寫集成測試
  7. 代碼審查
  8. 合併到 develop
關鍵點:
  - 測試先行
  - 小步快跑
  - 頻繁提交
```

**場景 2：修復 Bug**
```yaml
流程:
  1. 複現和定位問題
  2. 創建 bugfix 分支
  3. 編寫失敗測試
  4. 修復問題
  5. 驗證測試通過
  6. 代碼審查
  7. 合併到 develop
關鍵點:
  - 先寫失敗測試
  - 最小修復
  - 根因分析
```

**場景 3：重構代碼**
```yaml
流程:
  1. 識別重構範圍
  2. 創建 refactor 分支
  3. 編寫測試保護（如果沒有）
  4. 漸進式重構
  5. 驗證測試通過
  6. 代碼審查
  7. 合併到 develop
關鍵點:
  - 小步重構
  - 保持測試通過
  - 向後兼容
```

**場景 4：緊急修復（hotfix）**
```yaml
流程:
  1. 從 main 創建 hotfix 分支
  2. 快速修復
  3. 最小測試
  4. 代碼審查（快速）
  5. 合併到 main 和 develop
  6. 立即部署
關鍵點:
  - 快速響應
  - 最小變更
  - 後續補充測試
```

---

## 8. 行動計劃和建議

### 8.1 立即行動（高優先級）

| # | 行動 | 優先級 | 預計時間 | 說明 |
|---|------|--------|----------|------|
| 1 | 創建 GitHub Actions CI workflow | High | 2-3 小時 | `.github/workflows/ci.yml`，包含 lint、測試、構建 |
| 2 | 創建 GitHub Actions CD workflow | High | 2-3 小時 | `.github/workflows/cd.yml`，自動化部署 |
| 3 | 創建 PR 模板 | High | 1 小時 | `.github/PULL_REQUEST_TEMPLATE.md` |
| 4 | 設置分支保護規則 | High | 30 分鐘 | GitHub 設置，main 分支保護、審查要求 |
| 5 | 創建分支策略文檔 | High | 2 小時 | `WORKFLOW.md`，Git Flow、分支命名、合併流程 |
| 6 | 創建代碼審查文檔 | High | 2 小時 | `CODE_REVIEW.md`，審查標準、流程、角色 |

### 8.2 短期行動（1-2 週）

| # | 行動 | 優先級 | 預計時間 | 說明 |
|---|------|--------|----------|------|
| 7 | 創建 CONTRIBUTING.md | Medium | 2 小時 | 開發流程、提交規範、代碼風格 |
| 8 | 設置 Codecov 或 Coveralls | Medium | 1 小時 | 集成到 CI workflow，覆蓋率報告 |
| 9 | 優化測試覆蓋率 | Medium | 持續 | 前端組件覆蓋率 30% → 70% |
| 10 | 繼續 React Query 遷移 | Medium | 2-3 週 | Phase 1 核心頁面 |
| 11 | 實施 Indicator Calculator | Medium | 2-3 天 | 所有 signal strategies 的基礎 |

### 8.3 中期行動（1 個月）

| # | 行動 | 優先級 | 預計時間 | 說明 |
|---|------|--------|----------|------|
| 12 | 實施自動化通知 | Low | 2 小時 | Slack/Discord 集成，PR 通知、部署狀態 |
| 13 | 設置預生產環境 | Low | 4-6 小時 | staging 服務器、staging workflow |
| 14 | 移除棄用代碼 | Low | 1-2 週 | 重構完成後清理 |
| 15 | 標準化統一策略引擎 | Low | 4-5 天 | 遷移所有策略到新系統 |

### 8.4 風險評估

| 風險 | 可能性 | 影響 | 緩解措施 | 狀態 |
|------|--------|------|---------|------|
| 手動部署錯誤 | High | High | ✅ 實施自動化 CD | 行動項 2 |
| 測試未在合併前運行 | High | Medium | ✅ 強制 CI 檢查通過 | 行動項 1, 4 |
| 代碼審查不完整 | Medium | High | ✅ 實施分支保護和審查要求 | 行動項 4, 6 |
| 前端未編譯就推送 | Medium | Medium | ✅ CI workflow 中包含構建步驟 | 行動項 1 |
| 測試覆蓋率下降 | Medium | Medium | ✅ 實施覆蓋率門檻和報告 | 行動項 8 |
| 部署到生產導致停機 | Low | High | ✅ 健康檢查、滾動更新、快速回滾 | 行動項 2 |

---

## 9. 信賴度與限制

### 信賴度：**High**

**原因：**
- ✅ 完整閱讀了所有 4 個輸入文檔
- ✅ 文檔之間相互驗證，一致性高
- ✅ Git 提交歷史、重構計劃、CI/CD 配置、工具鏈配置都有詳細記錄
- ✅ 數據來源明確，可追溯

### 數據質量

| 來源 | 質量 | 說明 |
|------|------|------|
| Git 提交歷史 | Excellent | 50 次提交，100% Conventional Commits |
| 重構計劃 | Excellent | 6 個完整文檔，詳細的決策記錄 |
| CI/CD 配置 | Good | Docker 配置完整，測試基礎完善，缺 GitHub Actions |
| 工具鏈配置 | Excellent | 完整的依賴清單和配置文件 |
| 分支策略 | Fair | 無文檔支持，主要推斷 |

### 假設

1. 項目使用 Git 進行版本控制（已確認）
2. 主要分支名稱為 `main`（推斷，基於 DEPLOYMENT.md）
3. 項目託管在 GitHub（推斷，因為參考文檔提到 GitHub Actions）
4. 開發者遵循基本的 Git 工作流（推斷）
5. PR 需要審查才能合併（推斷，建議）

### 限制

1. ❌ 無法執行 `git branch -a` 查看實際分支結構
2. ❌ 無法查看 GitHub 設置（分支保護、規則等）
3. ❌ 無法查看歷史提交和 PR 記錄
4. ❌ 無 GitHub Actions workflows（目錄不存在）
5. ❌ 無 PR 模板和審查文檔
6. ❌ 無法與團隊成員確認當前工作流程

### 建議的後續調查

1. 執行 `git branch -a` 查看實際分支結構
2. 查看 GitHub 設置頁面確認分支保護和規則
3. 查看過去的 PR 記錄了解實際流程
4. 與團隊成員確認當前工作流程和偏好
5. 監控 CI/CD 實施後的效果和改進

---

## 10. 元數據

**分析框架：** Git 開發模式整合分析

**輸入文檔：**
1. a004a-git-log.md - Git 提交歷史分析
2. a004b-refactoring-plans.md - Refactoring Plans 分析
3. a004c-branching-cicd.md - 分支策略和 CI/CD 分析
4. a004d-dev-toolchain.md - 開發工具鏈分析

**關鍵指標：**
- 提交規範遵循率：100%
- 提交類型分佈：feat 34%, fix 24%, refactor 16%
- 測試總數：506（86% 通過率）
- 整體覆蓋率：60%（後端 70%，前端 50%）
- 重構計劃：6 個主要文檔
- 開發模式：Sprint 模式（高強度 2-3 天）

**關鍵主題：**
1. Conventional Commits 100% 規範
2. Sprint 模式開發（高強度集中開發）
3. 漸進式遷移重構策略
4. 向後兼容原則
5. 工廠模式、適配器模式、介面抽象
6. 測試驅動開發（TDD）
7. Docker 化部署
8. 缺少 GitHub Actions CI/CD
9. 缺少明確的分支策略文檔
10. 完整的開發工具鏈

**後續使用建議：**
- 本報告將成為 a005（Programmer Sub-Agent 設計）和 a006（知識庫構建）的核心參考文檔
- 建議定期更新（每 3-6 個月）以反映開發流程的演進
- 可作為新成員入職培訓的參考文檔
- 可用作制定開發規範和最佳實踐的基礎

---

**報告生成時間：** 2026-02-21T00:35:00+08:00
**分析工具：** Charlie Analyst
**專案路徑：** /Users/charlie/Dashboard
**輸出路徑：** /Users/charlie/.openclaw/workspace/kanban/projects/programmer-agent-design-20260220/a004-git-development-pattern.md

---

*本報告整合了 4 個分析文檔的結果，形成完整的 Git 開發模式報告，為 Programmer Sub-Agent 的設計和知識庫構建提供核心參考。*
