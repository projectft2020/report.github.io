# Dashboard 頁面結構分析

**分析目標：** 分析 Dashboard 前端的頁面結構，為設計 programmer sub-agent 提供完整的頁面知識基礎。

**Dashboard 前端路徑：** `/Users/charlie/Dashboard/`

**分析日期：** 2026-02-21

**技術棧：**
- Frontend: React 19.2.0 + Vite
- 路由: React Router v7
- UI Framework: Bootstrap 5 + Custom CSS modules
- 狀態管理: Zustand + React Context
- API: Axios + TanStack Query (React Query)
- 圖表: Chart.js, ECharts, Recharts, Three.js
- 國際化: i18next

---

## 一、頁面文件清單（按功能分類）

### 1.1 主要導航頁面

| 頁面名稱 | 路由 | 檔案路徑 | 功能描述 |
|---------|------|---------|---------|
| **Market Scanner** | `/` | `/pages/market-scanner/index.jsx` | 市場掃描儀首頁，顯示高共鳴度股票和策略信號 |
| **Signal Dashboard** | `/signals` | `/pages/SignalDashboardPage/index.jsx` | 信號儀表板，決策漏斗入口點 |
| **Strategy Showcase** | `/strategy-showcase` | `/pages/StrategyShowcasePage/` | 公開策略展示頁（免費用戶） |

### 1.2 策略相關頁面

| 頁面名稱 | 路由 | 檔案路徑 | 功能描述 |
|---------|------|---------|---------|
| **Unified Strategy Page** | `/strategies/:tab` | `/pages/StrategyPage/index.jsx` | 統一策略中心（Builder、Backtest、History） |
| **Strategy Studio** | `/strategy-studio` → `/strategies/builder` | `/pages/StrategyStudioPage/` | 策略工作室（舊版，重定向到新頁面） |
| **Strategy Comparison** | `/strategy-comparison` | `/pages/StrategyComparisonPage/` | 策略比較實驗室 |
| **Allocation Strategies** | `/allocation` | `/pages/AllocationPage/index.jsx` | 配置策略頁面（統合 6040/All-Weather/Golden Butterfly） |
| **Momentum Strategies** | `/momentum` | `/pages/MomentumPage/index.jsx` | 動量策略頁面（US/TW 統一） |
| **Technical Strategy Lab** | `/strategies/technical-lab` | `/pages/TechnicalStrategyPage/` | 技術指標回測實驗室 |
| **F-Index Strategy** | `/strategies/f-index` | `/pages/FIndexStrategyPage/` | F-Index 策略（每週） |
| **Dual Momentum** | `/dual-momentum` | `/pages/DualMomentumPage/index.jsx` | 雙重動量策略 |
| **Backtest History** | `/backtest-history` | `/pages/BacktestHistoryPage/` | 回測歷史記錄 |
| **Laboratory** | `/laboratory` | `/pages/LaboratoryPage/index.jsx` | 實驗室頁面 |

### 1.3 市場分析頁面

| 頁面名稱 | 路由 | 檔案路徑 | 功能描述 |
|---------|------|---------|---------|
| **Market Heatmap** | `/market-heatmap` | `/pages/MarketHeatmapPage/` | 市場熱力圖 |
| **Market Indices** | `/market-indices` | `/pages/MarketIndicesPage/` | 市場指數 |
| **Market Breadth** | `/market-breadth` | `/pages/MarketBreadthPage/` | 市場廣度 |
| **Sector Flow** | `/sector-rotation` | `/pages/SectorFlowPage/` | 板塊流動 |
| **RRG** | `/rrg` | `/pages/RRGPage/` | 動態相對強度圖（Relative Rotation Graph） |

### 1.4 篩選器頁面

| 頁面名稱 | 路由 | 檔案路徑 | 功能描述 |
|---------|------|---------|---------|
| **MACD Screener** | `/screener/macd` | `/pages/MacdScreenerPage/` | MACD 篩選器 |
| **RSI Screener** | `/screener/rsi` | `/pages/RsiScreenerPage/` | RSI 篩選器 |
| **SuperTrend Screener** | `/screener/supertrend` | `/pages/SuperTrendScreenerPage/` | SuperTrend 篩選器 |
| **Extremes Screener** | `/screener/extremes` | `/pages/ExtremesScreenerPage/` | 極值篩選器 |
| **F-Index Screener** | `/screener/f-index` | `/pages/FIndexScreenerPage/` | F-Index 篩選器 |

### 1.5 期貨與預測頁面

| 頁面名稱 | 路由 | 檔案路徑 | 功能描述 |
|---------|------|---------|---------|
| **Futures Composite** | `/futures` | `/pages/FuturesCompPage/` | 期貨複合分析 |
| **Futures Backtest** | `/futures-backtest` | `/pages/FuturesBacktestPage/index.jsx` | 期貨多策略回測系統 |
| **Prediction Momentum** | `/prediction-momentum` | `/pages/PredictionMomentumPage/index.jsx` | 預測動量 |
| **Prediction Momentum (Type 2)** | `/prediction-momentum-type2` | `/pages/PredictionMomentumType2Page/index.jsx` | 預測動量（梯次型） |
| **Prediction Momentum (Hedged)** | `/prediction-momentum-hedged` | `/pages/PredictionMomentumHedgedPage/index.jsx` | 預測動量（對沖型） |
| **Prediction Momentum (Futures)** | `/prediction-momentum-futures` | `/pages/PredictionMomentumFuturesPage/index.jsx` | 預測動量（期貨） |

### 1.6 台灣市場頁面

| 頁面名稱 | 路由 | 檔案路徑 | 功能描述 |
|---------|------|---------|---------|
| **Taiwan Market** | `/taiwan-market` | `/pages/TaiwanMarketPage/` | 台灣市場脈搏 |
| **TW Stock Detail** | `/tw-stock/:symbol` | `/pages/TaiwanStockDetailPage/` | 台灣個股詳情 |

### 1.7 市場評分頁面

| 頁面名稱 | 路由 | 檔案路徑 | 功能描述 |
|---------|------|---------|---------|
| **Market Score** | `/market-score` | `/pages/MarketScorePage/` | 市場評分詳情 |
| **Market Score Monitor** | `/market-score-monitor` | `/pages/MarketScoreMonitorPage/` | 市場評分監控 |

### 1.8 分析與評估頁面

| 頁面名稱 | 路由 | 檔案路徑 | 功能描述 |
|---------|------|---------|---------|
| **Stock Detail** | `/stock/:symbol` | `/pages/StockDetailPage/` | 個股分析頁面 |
| **Stock History Pulse** | `/stock-pulse/:symbol` | `/pages/StockHistoryPulsePage/` | 個股歷史脈衝（免費用戶轉化） |
| **Portfolio Mixer** | `/portfolio-mixer` | `/pages/PortfolioMixerPage/index.jsx` | 投資組合混音器 |
| **Rebalance Sensitivity** | `/rebalance-sensitivity` | `/pages/RebalanceSensitivityPage/` | 再平衡敏感度分析 |
| **Performance Attribution** | `/performance-attribution` | `/pages/PerformanceAttributionPage/` | 績效歸因分析 |

### 1.9 AI 與宏觀頁面

| 頁面名稱 | 路由 | 檔案路徑 | 功能描述 |
|---------|------|---------|---------|
| **AI Model Calculation** | `/ai-model-calculation` | `/pages/AIModelCalculationPage/index.jsx` | AI 模型計算 |
| **Macro Dashboard** | `/macro` | `/pages/MacroDashboardPage/index.jsx` | 宏觀儀表板 |

### 1.10 系統與管理頁面

| 頁面名稱 | 路由 | 檔案路徑 | 功能描述 |
|---------|------|---------|---------|
| **System Operations** | `/system-operations` | `/pages/SystemOperationsPage/index.jsx` | 系統操作 |
| **Admin Analytics** | `/admin/analytics` | `/pages/AdminAnalyticsPage/index.jsx` | 管理員分析儀表板 |
| **Dashboard Analytics (Old)** | `/dashboard-analytics` | `/pages/DashboardPage.jsx` | 舊版主頁（管理員） |

### 1.11 驗證與測試頁面

| 頁面名稱 | 路由 | 檔案路徑 | 功能描述 |
|---------|------|---------|---------|
| **Shadow Trading** | `/shadow-trading` | `/pages/ShadowTradingPage/` | 影子交易分析（P0-1 驗證） |
| **Scenario Analysis** | `/scenario-analysis` | `/pages/ScenarioAnalysisPage/` | 情境分析（P2-6） |
| **Strategy Analysis Dashboard** | `/analysis/strategies/:runId` | `/pages/StrategyAnalysisDashboard/index.jsx` | 策略分析儀表板 |

### 1.12 開發與測試頁面

| 頁面名稱 | 路由 | 檔案路徑 | 功能描述 |
|---------|------|---------|---------|
| **UI Test Page** | `/ui-test` | `/pages/UITestPage/` | 共用元件展示（Task #13） |

---

## 二、頁面路由結構圖

```
/ (根目錄)
├── /                           → MarketScanner (市場掃描儀)
│   └── 無參數，顯示市場總覽
│
├── /ui-test                    → UITestPage (UI 測試，管理員專用)
│
├── /dashboard-analytics        → DashboardPage (舊版主頁，管理員專用)
│
├── /strategy-showcase          → StrategyShowcasePage (公開策略展示)
│   └── ?strategy={slug}        → 顯示特定策略詳情
│
├── /performance-attribution    → PerformanceAttributionPage (績效歸因)
│
├── /stock-pulse/:symbol        → StockHistoryPulsePage (個股脈衝，免費轉化)
│
├── /signals                    → SignalDashboardPage (信號儀表板，管理員專用)
│
├── /alerts                     → 重定向至 /system-operations
│
├── /strategy-comparison        → StrategyComparisonPage (策略實驗室，管理員專用)
│
├── /strategy-studio            → 重定向至 /strategies/builder
│
├── /strategies                 → 重定向至 /strategies/builder
│
├── /strategies/:tab            → StrategyPage (統一策略頁面)
│   ├── /strategies/builder     → Builder Tab (策略構建器)
│   ├── /strategies/backtest    → Backtest Tab (回測)
│   └── /strategies/history     → History Tab (歷史)
│
├── /admin/analytics            → AdminAnalyticsPage (管理員分析)
│
├── /market-heatmap             → MarketHeatmapPage (市場熱力圖)
│
├── /taiwan-market              → TaiwanMarketPage (台灣市場)
│
├── /tw-stock/:symbol           → TaiwanStockDetailPage (台股詳情)
│
├── /allocation                 → AllocationPage (配置策略)
│   ├── /strategy/6040          → 重定向至 /allocation
│   ├── /strategy/all-weather   → 重定向至 /allocation
│   └── /strategy/golden-butterfly → 重定向至 /allocation
│
├── /momentum                   → MomentumPage (動量策略)
│   ├── /momentum-index         → 重定向至 /momentum?market=US&type=classic
│   ├── /tw-momentum-index      → 重定向至 /momentum?market=TW&type=classic
│   ├── /v2/momentum            → 重定向至 /momentum
│   └── /strategy/momentum_tw   → 重定向至 /momentum?market=TW&type=classic
│
├── /strategies/technical-lab   → TechnicalStrategyPage (技術策略實驗室)
│   └── /strategies/technical   → 重定向至 /strategies/technical-lab
│
├── /futures                    → FuturesCompPage (期貨複合分析)
│
├── /futures-backtest           → FuturesBacktestPage (期貨回測)
│
├── /prediction-momentum        → PredictionMomentumPage (預測動量)
│
├── /prediction-momentum-type2  → PredictionMomentumType2Page (預測動量 Type 2)
│
├── /prediction-momentum-hedged  → PredictionMomentumHedgedPage (預測動量對沖)
│
├── /prediction-momentum-futures → PredictionMomentumFuturesPage (預測動量期貨)
│
├── /ai-model-calculation       → AIModelCalculationPage (AI 模型計算)
│
├── /strategies/f-index         → FIndexStrategyPage (F-Index 策略)
│
├── /dual-momentum              → DualMomentumPage (雙重動量)
│
├── /backtest-history           → BacktestHistoryPage (回測歷史)
│
├── /laboratory                 → LaboratoryPage (實驗室)
│
├── /macro                      → MacroDashboardPage (宏觀儀表板)
│
├── /system-operations          → SystemOperationsPage (系統操作)
│
├── /market-indices             → MarketIndicesPage (市場指數)
│
├── /market-breadth             → MarketBreadthPage (市場廣度)
│
├── /screener/macd              → MacdScreenerPage (MACD 篩選器)
│
├── /screener/rsi               → RsiScreenerPage (RSI 篩選器)
│
├── /screener/supertrend        → SuperTrendScreenerPage (SuperTrend 篩選器)
│
├── /screener/extremes          → ExtremesScreenerPage (極值篩選器)
│
├── /screener/f-index           → FIndexScreenerPage (F-Index 篩選器)
│
├── /sector-rotation            → SectorFlowPage (板塊流動)
│
├── /rrg                        → RRGPage (相對強度圖)
│
├── /shadow-trading             → ShadowTradingPage (影子交易分析)
│
├── /scenario-analysis          → ScenarioAnalysisPage (情境分析)
│
├── /analysis/strategies/:runId  → StrategyAnalysisDashboard (策略分析儀表板)
│
├── /stock/:symbol              → StockDetailPage (個股詳情)
│
├── /market-score               → MarketScorePage (市場評分)
│
├── /market-score-monitor       → MarketScoreMonitorPage (市場評分監控)
│
├── /portfolio-mixer            → PortfolioMixerPage (投資組合混音器)
│
└── /rebalance-sensitivity      → RebalanceSensitivityPage (再平衡敏感度)
```

---

## 三、導航流程說明

### 3.1 導航架構

Dashboard 使用 **側邊導航欄（Sidebar）** + **頂部標題欄（Header）** 的經典佈局：

```
┌─────────────────────────────────────────────────────────────┐
│  [側邊欄]  │  [頂部標題欄 - Page Title | 截圖 | 收合 | 語言]    │
├────────────┼──────────────────────────────────────────────────┤
│            │                                                  │
│  [導航選項] │                                                  │
│  - Overview │                                                  │
│  - Decision │              [主內容區域]                          │
│    Funnel   │              (Page Content)                       │
│  - Showcase │                                                  │
│  - Data     │                                                  │
│    Maintain │                                                  │
│  - Old      │                                                  │
│    Version  │                                                  │
│            │                                                  │
└────────────┴──────────────────────────────────────────────────┘
```

### 3.2 側邊欄分組結構

側邊欄導航分為 5 個主要群組：

#### **群組 1: Overview（總覽）**
- **Market Scanner** (`/`) - 市場掃描儀
  - 顯示市場溫度
  - 高共鳴度股票列表
  - 策略信號網格

#### **群組 2: Decision Funnel（決策漏斗）** [管理員專用]
- **Signal Dashboard** (`/signals`) - 信號儀表板
  - 決策漏斗入口點
  - 多策略信號匯總
- **Strategy Lab** (`/strategy-comparison`) - 策略比較實驗室
  - 策略績效對比
  - 策略選擇工具

#### **群組 3: Showcase（展示）**
- **動態策略連結**
  - 從 API 載入已發布策略
  - 按市場（US/TW）分組
  - 每個策略連結至 `/strategy-showcase?strategy={slug}`

#### **群組 4: Data Maintain（資料維護）** [管理員專用]
- **Strategy Studio** (`/strategies/builder`) - 策略工作室
  - 策略構建與編輯
  - 參數配置
- **Strategy Lab (Tech)** (`/strategies/technical-lab`) - 技術策略實驗室
  - 技術指標回測
- **Momentum** (`/momentum`) - 動量策略
  - US/TW 市場動量
- **System Ops** (`/system-operations`) - 系統操作
  - 告警與通知
  - 系統設定
- **Platform Analytics** (`/admin/analytics`) - 平台分析
  - 使用者行為分析
  - 系統績效監控

#### **群組 5: Old Version（舊版）** [管理員專用，預設折疊]
包含所有舊版頁面，按類別分組：
- 市場分析類（Heatmap, Indices, Breadth, Sector, RRG）
- 策略類（Allocation, Futures, Prediction, AI Model, F-Index）
- 台股類（Taiwan Market, Market Score）
- 實驗室類（Portfolio Mixer, Rebalance Sensitivity, Dual Momentum, Backtest History）
- 驗證類（Shadow Trading, Scenario Analysis）

### 3.3 導航交互模式

#### 3.3.1 頁面切換
- 使用 React Router `NavLink` 進行路由導航
- 主動路由自動高亮（`active` class）
- 路由變更時自動關閉移動端側邊欄

#### 3.3.2 側邊欄折疊/展開
- **桌面模式**：
  - 點擊收合圖標切換窄版/寬版
  - 窄版只顯示圖標，隱藏文字
- **移動/平板模式**：
  - 點擊漢堡選單顯示覆蓋式側邊欄
  - 點擊遮罩層或關閉按鈕收起側邊欄

#### 3.3.3 群組折疊
- 每個群組可獨立折疊/展開
- 使用狀態管理各群組開關（`groupsOpen`）
- 預設：Overview, Decision Funnel, Showcase, Maintain 展開；Old Version 折疊

#### 3.3.4 動態導航
- Showcase 群組的策略連結動態載入
- 從 `/api/resonance/strategies` API 獲取已發布策略
- 過濾條件：`catalog_enabled = true`
- 按市場分組（US/TW）並按名稱排序

### 3.4 路由跳轉模式

#### 3.4.1 卡片點擊跳轉（Market Scanner）
```javascript
handleCardClick(cardType, payload) {
  if (cardType === 'resonance') {
    // 高共鳴度卡片 → 個股脈衝頁面
    navigate(`/stock-pulse/${symbol}`);
  } else if (cardType === 'signal') {
    // 信號卡片 → 策略展示頁面
    navigate(`/strategy-showcase?strategy=${strategyType}`);
  }
}
```

#### 3.4.2 查看全部跳轉
```javascript
// 查看特定類型策略的所有信號
navigate(`/strategy-showcase?strategy=${strategyType}`);
```

#### 3.4.3 頁面重定向模式
多處使用重定向以簡化路由或保持向後兼容：

| 舊路由 | 新路由 | 原因 |
|--------|--------|------|
| `/strategy/6040` | `/allocation` | 統一配置頁面 |
| `/momentum-index` | `/momentum?market=US&type=classic` | 統一動量頁面，參數化 |
| `/strategy-studio` | `/strategies/builder` | 整合到統一策略頁 |
| `/alerts` | `/system-operations` | 功能整合 |

### 3.5 權限控制

#### 3.5.1 AdminRoute（管理員專用路由）
```javascript
<AdminRoute isEnabled={pageConfig.xxx} configLoaded={configLoaded}>
  <ProtectedPage />
</AdminRoute>
```
- 檢查條件：`isEnabled` (頁面配置) + `isAdmin()` (使用者角色)
- 不符合條件：重定向至 `/`

#### 3.5.2 ProtectedRoute（保護路由）
```javascript
<ProtectedRoute isEnabled={pageConfig.xxx} configLoaded={configLoaded}>
  <Page />
</ProtectedRoute>
```
- 只檢查 `isEnabled`
- 不檢查使用者角色（適合一般用戶可訪問但需配置開啟的頁面）

#### 3.5.3 權限檢查工具
- `isAdmin()` - 檢查是否為管理員
- `getUserRole()` - 獲取使用者角色

### 3.6 頁面配置動態載入

```javascript
useEffect(() => {
  const fetchConfig = async () => {
    const response = await apiClient.get('/config');
    if (response.data && response.data.page_visibility) {
      setPageConfig(prev => ({ ...prev, ...response.data.page_visibility }));
    }
  };
  fetchConfig();
}, []);
```

- 從後端 API 動態載入頁面可見性配置
- 配置項目：
  - `dashboard`, `momentum_index`, `market_indices`, `market_heatmap`, `market_breadth`
  - `screener_macd`, `screener_rsi`, `screener_supertrend`, `screener_extremes`, `screener_f_index`
  - 等等...

---

## 四、關鍵頁面的功能和交互

### 4.1 MarketScanner（市場掃描儀）

**位置：** `/`（首頁）

**核心功能：**
1. **市場溫度顯示**
   - 顯示當前市場狀態（US/TW）
   - 溫度指示器（熱/溫/冷）

2. **高共鳴度股票區塊**
   - 顯示近期高共鳴度個股
   - 每張卡片可點擊跳轉至 `/stock-pulse/{symbol}`
   - 顯示策略數量

3. **策略信號網格**
   - 按策略類型分組顯示信號
   - 每個策略顯示：
     - 勝率（WR）
     - 期望報酬（EV 6M）
   - "View All" 按鈕跳轉至策略展示頁

4. **市場切換**
   - US Market ↔ TW Market
   - 信號模式切換（entry/exit）

5. **本地存儲**
   - 記住使用者選擇的市場和信號模式
   - 下次訪問自動恢復

**組件結構：**
```
MarketScanner
├── ScannerHeader (標題 + 市場/信號模式切換器)
├── MarketTemperatureSection (市場溫度)
├── SummaryStats (統計總覽)
├── HighResonanceSection (高共鳴度股票卡片網格)
└── StrategyGridSection (策略信號網格)
```

**狀態管理：**
- `loading`: 加載狀態
- `error`: 錯誤信息
- `summary`: API 回傳的數據
- `selectedMarket`: 當前選擇市場（'US' | 'TW'）
- `signalMode`: 信號模式（'entry' | 'exit'）

**數據來源：**
```javascript
GET /api/resonance/home?market={market}&target_date={today}&lookback_years=0.5&signal_mode={signalMode}
```

**交互流程：**
```
1. 頁面載入
   ↓
2. 從 localStorage 讀取上一次的市場和信號模式
   ↓
3. 調用 API 獲取數據
   ↓
4. 顯示市場溫度區塊（始終顯示）
   ↓
5. 顯示統計總覽（如有數據）
   ↓
6. 顯示高共鳴度股票（如有數據）
   ↓
7. 顯示策略信號網格（如有數據）
   ↓
8. 點擊卡片 → 跳轉至對應詳情頁
```

---

### 4.2 StrategyPage（統一策略頁面）

**位置：** `/strategies/:tab`

**標籤頁結構：**

#### **Tab 1: Builder（策略構建器）**
- 功能：
  - 創建新策略
  - 編輯現有策略
  - 配置策略參數
  - 保存/刪除策略
- 組件：`BuilderTab`

#### **Tab 2: Backtest（回測）**
- 功能：
  - 選擇策略進行回測
  - 設置回測參數
  - 查看回測結果
- 組件：`BacktestTab`

#### **Tab 3: History（歷史）**
- 功能：
  - 查看回測歷史記錄
  - 過濾與排序
- 組件：`HistoryTab`

**URL 參數處理：**
```javascript
// 載入特定策略進行編輯
?instance_id={instanceId} → 自動載入該策略至 Builder Tab
```

**狀態管理：**
- `activeTab`: 當前標籤（'builder' | 'backtest' | 'history'）
- `editStrategy`: 編輯中的策略對象
- `refreshKey`: 刷新鍵（觸發子組件重新載入）

**API Hook：**
- `useStrategyAPI()` - 封裝策略相關 API 調用

**交互流程：**
```
1. 載入頁面
   ↓
2. 檢查 URL 中的 instance_id
   ↓
3. 有 instance_id → 載入策略 → 顯示 Builder Tab
   ↓
4. 無 instance_id → 顯示當前 Tab
   ↓
5. 切換 Tab → 更新 URL
   ↓
6. 保存/刪除 → 刷新列表
```

---

### 4.3 MomentumPage（動量策略頁面）

**位置：** `/momentum`

**核心功能：**
1. **市場切換**
   - US Market (S&P 500)
   - TW Market (Top 50, Mid 51-100)

2. **預設配置**
   - Classic（經典模式）
   - Defensive（防禦模式）
   - Aggressive（進攻模式）

3. **回測數據顯示**
   - 總報酬率
   - 年化報酬率（CAGR）
   - 最大回撤（MDD）
   - 夏普比率
   - 勝率

4. **持倉表格**
   - 當前持倉列表
   - 可排序
   - 點擊跳轉至個股詳情

5. **板塊配置**
   - 板塊曝露度分析
   - 板塊績效

6. **績效圖表**
   - 策略 vs 基準指數對比
   - 可選擇多個基準指數

7. **月度報酬表**
   - 按月顯示報酬

8. **再平衡歷史**
   - 再平衡記錄
   - 交易日誌（可展開）

**組件結構：**
```
MomentumPage
├── StrategyConfigCard (策略配置卡)
├── MetricCard (多個指標卡片)
├── HoldingsTable (持倉表格)
├── SectorExposure (板塊配置)
├── PerformanceChart (績效圖表)
├── MonthlyReturnsTable (月度報酬表)
└── RebalanceHistory (再平衡歷史)
```

**自定義 Hook：**
- `useMomentum()` - 管理動量策略的所有狀態和邏輯

**狀態管理：**
- `market`: 市場（'US' | 'TW'）
- `universe`: 股票池（'sp500' | 'tw_1_50' | 'tw_51_100'）
- `presetType`: 預設類型
- `years`: 回測年數
- `config`: 策略配置
- `activeConfig`: 活動配置
- `data`: API 回傳數據
- `loading`: 加載狀態
- `error`: 錯誤信息
- `sortConfig`: 排序配置
- `showTradeLog`: 顯示交易日誌
- `availableBenchmarks`: 可用基準指數
- `activeBenchmarks`: 活動基準指數

**圖表輔助函數：**
- `useBenchmarkDatasets()` - 處理基準指數數據集
- `useReturnChartData()` - 準備回報率圖表數據

**常量：**
- `PRESETS` - 預設配置定義

---

### 4.4 DashboardLayout（佈局組件）

**核心功能：**

#### 4.4.1 響應式側邊欄
- **桌面模式**：固定顯示，可折疊
- **移動/平板模式**：覆蓋式顯示，點擊遮罩關閉

#### 4.4.2 群組導航
- 5 個主要群組
- 每個群組可獨立折疊
- 動態載入 Showcase 策略連結

#### 4.4.3 頁面標題
- 根據當前路由動態顯示頁面標題
- 函數：`getPageTitle(path)`

#### 4.4.4 截圖功能
- 使用 `html2canvas` 截取全頁面
- 截圖時隱藏側邊欄
- 支援滾動內容完整截取
- 自動下載 PNG 文件

#### 4.4.5 語言切換
- 英文 ↔ 繁體中文
- 使用 `i18next` 管理翻譯

#### 4.4.6 管理員登錄
- 點擊盾牌圖標觸發登入模態框
- 使用 `onOpenLogin` 回調

#### 4.4.7 Persona 切換器
- 僅在 `personaEnabled` 時顯示
- 右上角顯示

**子組件：**
- `SidebarGroup` - 側邊欄群組
- `SplashScreen` - 開屏動畫
- `PersonaSwitcher` - Persona 切換器

**狀態管理：**
```javascript
const [isSidebarOpen, setIsSidebarOpen] = useState(false);
const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
const [isCapturing, setIsCapturing] = useState(false);
const [publishedStrategies, setPublishedStrategies] = useState({});
const [strategiesLoading, setStrategiesLoading] = useState(true);
const [groupsOpen, setGroupsOpen] = useState({
  overview: true,
  decision_funnel: true,
  showcase: true,
  maintenance: true,
  old_version: false,
});
```

---

## 五、頁面設計模式

### 5.1 頁面架構模式

#### 5.1.1 主容器模式（Main Container Pattern）
```
DashboardLayout (容器)
├── Sidebar (側邊導航)
└── MainWrapper (主內容區)
    ├── Header (頂部標題欄)
    └── Main Content (頁面內容)
        └── {children}
```

**特點：**
- 所有頁面都包裹在 `DashboardLayout` 中
- 統一的側邊欄和標題欄
- 只需實現 `{children}` 部分的頁面邏輯

#### 5.1.2 標籤頁模式（Tabs Pattern）
```
StrategyPage
├── Tabs
│   ├── Builder Tab
│   ├── Backtest Tab
│   └── History Tab
└── {activeTabContent}
```

**特點：**
- 適合相關功能集中在同一頁面
- 狀態在各標籤間共享
- URL 反映當前標籤狀態

---

### 5.2 數據獲取模式

#### 5.2.1 自定義 Hook 模式
```javascript
// 頁面組件
const Page = () => {
  const { data, loading, error, refetch } = useCustomHook();
  // ... UI 邏輯
};

// 自定義 Hook
const useCustomHook = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    // ... 數據獲取邏輯
  };

  return { data, loading, error, refetch: fetchData };
};
```

**示例：**
- `useMomentum()` - 動量策略頁面
- `useStrategyAPI()` - 策略 API

#### 5.2.2 TanStack Query 模式
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

**特點：**
- 自動緩存管理
- 自動重試
- 背景刷新
- 視窗聚焦刷新（可配置）

---

### 5.3 加載狀態模式

#### 5.3.1 Skeleton Loading（骨架屏）
```javascript
<Skeleton.PageLoader text="Loading..." />
<Skeleton.Card />
<Skeleton.Table rows={5} />
<Skeleton.Text lines={3} />
```

**組件位置：** `/components/shared/Skeleton.jsx`

#### 5.3.2 Loading Spinner
```javascript
{loading && !data && (
  <div className="spinner-border text-primary" role="status"></div>
)}
```

#### 5.3.3 Empty States（空狀態）
```javascript
<EmptyStatePresets.LoadError />
<EmptyStatePresets.NoSignals />
<EmptyStatePresets.NoData />
```

---

### 5.4 錯誤處理模式

#### 5.4.1 Error Boundary
```javascript
<ErrorBoundary>
  <ToastProvider>
    <Router>
      {/* 應用內容 */}
    </Router>
  </ToastProvider>
</ErrorBoundary>
```

#### 5.4.2 頁面級別錯誤
```javascript
if (error) {
  return (
    <div className="alert alert-danger">
      <h5>Error Loading Strategy</h5>
      <p>{error}</p>
      <button onClick={() => window.location.reload()}>
        Retry
      </button>
    </div>
  );
}
```

---

### 5.5 狀態管理模式

#### 5.5.1 Local State（本地狀態）
```javascript
const [state, setState] = useState(initialValue);
```

**使用場景：**
- UI 狀態（展開/折疊、切換器等）
- 臨時表單數據
- 頁面級別的加載/錯誤狀態

#### 5.5.2 Zustand Store（全局狀態）
```javascript
const { fetchStage1Overview, marketScore, stockDetails } = useStore();
```

**使用場景：**
- 跨頁面共享的數據
- 複雜的狀態邏輯
- 需要持久化的狀態

#### 5.5.3 Context API（上下文）
```javascript
const { featureEnabled: personaEnabled } = usePersona();
```

**使用場景：**
- 主題切換
- 語言設置
- 使用者角色
- 功能開關

---

### 5.6 組件復用模式

#### 5.6.1 共享組件庫（Shared Components）
**位置：** `/components/shared/`

**主要組件：**
- `Skeleton.jsx` - 骨架屏加載
- `EmptyState.jsx` - 空狀態
- `ErrorBoundary.jsx` - 錯誤邊界
- `ToastProvider.jsx` - 消息提示
- `Modal.jsx` - 模態框
- `Card.jsx` - 卡片容器
- `Button.jsx` - 按鈕

#### 5.6.2 業務組件
**位置：** `/components/`

**主要組件：**
- `DashboardLayout.jsx` - 佈局容器
- `MetricCard.jsx` - 指標卡片
- `Sparkline.jsx` - 迷你圖表
- `MarketScoreMeter.jsx` - 市場評分儀表
- `SectorHeatmap.jsx` - 板塊熱力圖

---

### 5.7 路由保護模式

#### 5.7.1 AdminRoute（管理員路由）
```javascript
const AdminRoute = ({ isEnabled, configLoaded, children }) => {
  if (!configLoaded) return null;
  const hasAdminAccess = isAdmin();
  if (!isEnabled || !hasAdminAccess) {
    return <Navigate to="/" replace />;
  }
  return children;
};
```

**使用場景：**
- 管理員專用頁面
- 需要特定功能開關的頁面

#### 5.7.2 ProtectedRoute（保護路由）
```javascript
const ProtectedRoute = ({ isEnabled, configLoaded, children }) => {
  if (!configLoaded) return null;
  return isEnabled ? children : <Navigate to="/" replace />;
};
```

**使用場景：**
- 需要功能開關但不需要權限的頁面

---

### 5.8 代碼分割模式

#### 5.8.1 Lazy Loading（懶加載）
```javascript
const MarketScanner = React.lazy(() => import('./pages/market-scanner'));
const MomentumPage = React.lazy(() => import('./pages/MomentumPage/index.jsx'));
// ... 其他頁面
```

**特點：**
- 按需加載，減少初始包大小
- 使用 `Suspense` 包裹懶加載組件
- 統一的加載回退 UI

#### 5.8.2 Loading Fallback
```javascript
<Suspense fallback={<LoadingFallback />}>
  <Routes>
    {/* 懶加載的路由 */}
  </Routes>
</Suspense>
```

---

### 5.9 圖表組件模式

#### 5.9.1 Chart.js
```javascript
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS, CategoryScale, LinearScale,
  PointElement, LineElement, Title, Tooltip, Legend,
  Filler, ArcElement
} from 'chart.js';

ChartJS.register(...);
```

#### 5.9.2 ECharts
```javascript
import ReactECharts from 'echarts-for-react';
```

#### 5.9.3 Recharts
```javascript
import { LineChart, BarChart, PieChart } from 'recharts';
```

**選擇標準：**
- **Chart.js**: 簡單到中等複雜度圖表
- **ECharts**: 高度可定製、互動性強的圖表
- **Recharts**: React 原生、簡單配置

---

### 5.10 樣式模式

#### 5.10.1 Bootstrap + 自定義 CSS
```javascript
import 'bootstrap/dist/css/bootstrap.min.css';
import './DashboardLayout.module.css';
```

#### 5.10.2 CSS Modules
```javascript
import styles from './DashboardLayout.module.css';

<div className={styles['app-container']}>
  <aside className={styles['dashboard-sidebar']}>
```

#### 5.10.3 工具類（Utility Classes）
```javascript
className="d-flex justify-content-between align-items-center mb-4"
className="container-fluid p-4 animate-fade-in"
```

---

### 5.11 本地存儲模式

#### 5.11.1 localStorage
```javascript
// 讀取
const saved = localStorage.getItem('marketScanner_market');

// 保存
localStorage.setItem('marketScanner_market', market);
```

**使用場景：**
- 用戶偏好設置
- 頁面狀態持久化
- 臨時緩存

---

### 5.12 國際化模式

#### 5.12.1 i18next 配置
```javascript
import { useTranslation } from 'react-i18next';

const { t, i18n } = useTranslation();

// 翻譯
<h4>{t('header.pro_terminal')}</h4>

// 切換語言
i18n.changeLanguage('zh-TW');
```

**支持語言：**
- 英文（en）
- 繁體中文（zh-TW）

---

## 六、頁面開發指南（Programmer Sub-Agent）

### 6.1 創建新頁面

#### 6.1.1 基本頁面結構
```javascript
import React, { useState, useEffect } from 'react';

const NewPage = () => {
  // 1. 狀態定義
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 2. 數據獲取
  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/endpoint');
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // 3. 加載狀態
  if (loading && !data) {
    return <Skeleton.PageLoader text="Loading..." />;
  }

  // 4. 錯誤狀態
  if (error) {
    return (
      <EmptyStatePresets.LoadError
        message={`Error: ${error}`}
        action={<button onClick={fetchData}>Retry</button>}
      />
    );
  }

  // 5. 主內容
  return (
    <div className="container-fluid p-4 animate-fade-in">
      {/* 頁面內容 */}
    </div>
  );
};

export default NewPage;
```

#### 6.1.2 添加路由

**步驟 1：在 App.jsx 中引入頁面**
```javascript
const NewPage = React.lazy(() => import('./pages/NewPage/index.jsx'));
```

**步驟 2：添加路由定義**
```javascript
<Route path="/new-page" element={
  <AdminRoute isEnabled={true} configLoaded={configLoaded}>
    <NewPage />
  </AdminRoute>
} />
```

**步驟 3：在 DashboardLayout 中添加導航**
```javascript
<SidebarGroup title="Category" icon="bi-icon" isOpen={true}>
  <li className={styles['nav-item']}>
    <NavLink to="/new-page" className={({ isActive }) => `${styles['nav-link']} ${isActive ? styles['active'] : ''}`}>
      <i className="bi bi-icon me-2"></i> <span>New Page</span>
    </NavLink>
  </li>
</SidebarGroup>
```

**步驟 4：添加頁面標題**
```javascript
const getPageTitle = (path) => {
  if (path === '/new-page') return 'New Page Title';
  // ...
};
```

---

### 6.2 頁面組件劃分原則

#### 6.2.1 單一職責
- 每個組件只負責一個功能
- 避免組件過大

#### 6.2.2 可復用性
- 提取共同邏輯到共享組件
- 使用 props 進行配置

#### 6.2.3 組件大小建議
```javascript
// 主頁面組件：300-500 行
const Page = () => { /* ... */ };

// 子組件：100-200 行
const Section = () => { /* ... */ };

// UI 組件：50-100 行
const Card = () => { /* ... */ };
```

---

### 6.3 API 調用模式

#### 6.3.1 使用 apiClient
```javascript
import apiClient from './services/api';

const response = await apiClient.get('/endpoint');
const data = response.data;
```

#### 6.3.2 使用原生 fetch
```javascript
const response = await fetch('/api/endpoint');
if (response.ok) {
  const data = await response.json();
}
```

---

### 6.4 圖表集成指南

#### 6.4.1 Chart.js 示例
```javascript
import { Line } from 'react-chartjs-2';

<Line
  data={chartData}
  options={{
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      tooltip: { mode: 'index', intersect: false }
    }
  }}
/>
```

#### 6.4.2 ECharts 示例
```javascript
import ReactECharts from 'echarts-for-react';

<ReactECharts
  option={option}
  style={{ height: 400 }}
/>
```

---

### 6.5 測試建議

#### 6.5.1 單元測試
```javascript
import { render, screen } from '@testing-library/react';
import NewPage from './NewPage';

test('renders loading state', () => {
  render(<NewPage />);
  expect(screen.getByText('Loading...')).toBeInTheDocument();
});
```

#### 6.5.2 E2E 測試
```javascript
describe('New Page', () => {
  it('displays data correctly', () => {
    cy.visit('/new-page');
    cy.get('[data-testid="data-display"]').should('be.visible');
  });
});
```

---

## 七、總結

### 7.1 Dashboard 頁面特點

1. **模組化設計** - 頁面按功能分組，職責清晰
2. **響應式佈局** - 支援桌面、平板、移動端
3. **代碼分割** - 懶加載優化性能
4. **權限控制** - 多層級路由保護
5. **狀態管理** - 結合 useState, Zustand, Context
6. **錯誤處理** - Error Boundary + 頁面級別錯誤處理
7. **加載優化** - Skeleton + Empty States
8. **國際化** - 支援多語言
9. **組件復用** - 共享組件庫 + 業務組件
10. **圖表豐富** - Chart.js, ECharts, Recharts

### 7.2 Programmer Sub-Agent 開發要點

1. **遵循現有模式** - 參考現有頁面結構和代碼風格
2. **使用共享組件** - 優先使用 `/components/shared` 中的組件
3. **錯誤處理** - 始終處理 loading 和 error 狀態
4. **路由保護** - 根據需求選擇 AdminRoute 或 ProtectedRoute
5. **本地存儲** - 合理使用 localStorage 保存用戶偏好
6. **API 調用** - 使用 apiClient 以獲得統一錯誤處理和攔截器
7. **樣式規範** - Bootstrap 類名 + CSS Modules
8. **代碼分割** - 使用 React.lazy 進行頁面懶加載
9. **測試覆蓋** - 編寫單元測試和 E2E 測試
10. **文檔更新** - 更新路由、導航和頁面標題映射

### 7.3 常見陷阱

1. **忘記路由保護** - 導致未授權訪問
2. **硬編碼數據** - 未從 API 或 props 獲取
3. **忽略錯誤狀態** - 用戶體驗差
4. **過大組件** - 難以維護和測試
5. **缺少本地存儲** - 用戶偏好丟失
6. **未處理懶加載** - 首屏加載慢
7. **缺少國際化** - 只支援一種語言

---

## 附錄：關鍵文件路徑

### 頁面目錄
```
/Users/charlie/Dashboard/frontend/src/pages/
├── market-scanner/           ← 市場掃描儀
├── StrategyPage/             ← 統一策略頁面
├── MomentumPage/             ← 動量策略
├── AllocationPage/           ← 配置策略
├── StockDetailPage.jsx       ← 個股詳情
├── DashboardPage.jsx          ← 舊版主頁
├── TaiwanMarketPage/          ← 台灣市場
├── ... (其他頁面)
```

### 組件目錄
```
/Users/charlie/Dashboard/frontend/src/components/
├── DashboardLayout.jsx       ← 主佈局
├── shared/                   ← 共享組件庫
│   ├── Skeleton.jsx          ← 骨架屏
│   ├── EmptyState.jsx        ← 空狀態
│   ├── ErrorBoundary.jsx     ← 錯誤邊界
│   └── ... (其他共享組件)
├── MetricCard.jsx            ← 指標卡片
├── Sparkline.jsx             ← 迷你圖表
└── ... (其他業務組件)
```

### 核心配置文件
```
/Users/charlie/Dashboard/frontend/src/
├── App.jsx                   ← 路由配置
├── main.jsx                  ← 應用入口
├── config.jsx                ← 全局配置
├── store.jsx                 ← Zustand store
└── i18n.js                  ← 國際化配置
```

---

**分析完成**

本文件為 Dashboard 前端頁面結構的完整分析，涵蓋：
- 50+ 頁面清單（按功能分類）
- 完整路由結構圖
- 詳細導航流程說明
- 關鍵頁面功能和交互分析
- 12 種頁面設計模式
- Programmer Sub-Agent 開發指南

可作為開發新頁面或修改現有頁面的參考文檔。
