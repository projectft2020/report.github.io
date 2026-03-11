# Dashboard 樣式和工具分析

**Task ID:** a002e
**Agent:** Charlie Analyst
**Status:** completed
**Timestamp:** 2026-02-21T00:33:00+08:00

## Executive Summary

Dashboard 前端使用 React + Vite + Bootstrap 5 構建，採用 CSS Custom Properties 實現主題系統，搭配 React Bootstrap 組件庫。工具函數涵蓋認證、格式化、API 呼叫等核心功能，並提供自訂 Context 和 Hooks 進行狀態管理。整體架構清晰，適合快速開發和維護。

## Analysis

### 1. 樣式技術棧和配置

#### 1.1 主要依賴

```json
{
  "UI Framework": {
    "bootstrap": "^5.3.8",
    "react-bootstrap": "^2.10.10",
    "bootstrap-icons": "^1.13.1"
  },
  "React": {
    "react": "^19.2.0",
    "react-dom": "^19.2.0",
    "react-router-dom": "^7.11.0"
  },
  "State Management": {
    "zustand": "^5.0.9",
    "@tanstack/react-query": "^5.90.16"
  },
  "Visualization": {
    "chart.js": "^4.5.1",
    "echarts": "^6.0.0",
    "recharts": "^3.6.0",
    "three": "^0.182.0"
  },
  "Build Tools": {
    "vite": "^7.2.4",
    "@vitejs/plugin-react": "^5.1.1"
  }
}
```

#### 1.2 構建配置 (Vite)

**檔案位置:** `/Users/charlie/Dashboard/frontend/vite.config.js`

```javascript
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': '/src',
      '@services': '/src/services'
    }
  },
  server: {
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
});
```

**關鍵配置:**
- 路徑別名: `@` → `/src`, `@services` → `/src/services`
- 開發代理: `/api` → 後端 `http://localhost:8000` (或 Docker 環境)
- 熱模組替換 (HMR): Vite 預設啟用

### 2. 主題系統說明

#### 2.1 CSS Custom Properties (主題變數)

**檔案位置:** `/Users/charlie/Dashboard/frontend/src/index.css`

```css
:root {
  /* Premium Color Palette */
  --primary: #0d6efd;
  --primary-rgb: 13, 110, 253;
  --secondary: #6c757d;
  --accent: #646cff;

  --success: #10b981;
  --danger: #ef4444;
  --warning: #f59e0b;
  --info: #3b82f6;

  /* Neutrals */
  --bg-main: #f8fafc;
  --bg-card: #ffffff;
  --bg-sidebar: #ffffff;
  --text-main: #1e293b;
  --text-muted: #64748b;
  --border-color: #e2e8f0;

  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
  --shadow-premium: 0 20px 25px -5px rgba(0, 0, 0, 0.05);

  /* Borders & Radius */
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-pill: 9999px;

  /* Typography */
  --font-heading: 'Outfit', sans-serif;
  --font-body: 'Inter', sans-serif;
}
```

**主題特點:**
- 使用 CSS 變數定義顏色、陰影、圓角、字型
- 支援 Glassmorphism 效果 (`backdrop-filter: blur`)
- Premium 卡片設計帶有懸停動畫
- 全局過渡效果: `transition: background-color 0.2s ease`

#### 2.2 自訂 CSS 類別

```css
/* Glassmorphism */
.glass {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.18);
}

/* Premium Card with Hover */
.premium-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-premium);
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.premium-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 30px -10px rgba(0, 0, 0, 0.1);
}

/* Animations */
.animate-fade-in { animation: fadeIn 0.4s ease-out forwards; }
.animate-slide-up { animation: slideUp 0.5s ease-out forwards; }
```

#### 2.3 字型配置

```css
/* Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

/* 字型應用 */
body { font-family: var(--font-body); }
h1, h2, h3, h4, h5, h6 { font-family: var(--font-heading); }
```

#### 2.4 主題切換

**檔案位置:** `/Users/charlie/Dashboard/frontend/src/App.jsx`

```javascript
useEffect(() => {
  document.body.className = 'light-theme'; // 目前固定為 light-theme
}, []);
```

**備註:** 目前僅支援亮色主題，深色主題可透過擴展 CSS 變數實現。

### 3. 工具函數清單

#### 3.1 認證工具 (`/Users/charlie/Dashboard/frontend/src/utils/auth.js`)

**核心函數:**

| 函數名稱 | 描述 | 返回值 |
|---------|------|--------|
| `getUserRole()` | 取得當前使用者角色 | `'admin' \| 'vip' \| 'free'` |
| `getUserToken()` | 取得使用者 Token (雙系統) | `string \| null` |
| `getAuthMethod()` | 取得認證方法 | `'admin_token' \| 'bearer_token' \| null` |
| `authenticateUser(code)` | 使用存取碼認證 | `Promise<{success, role, message}>` |
| `validateToken()` | 驗證 Token 有效性 | `Promise<{valid, role}>` |
| `logout()` | 登出 | `Promise<void>` |
| `isAdmin()` | 檢查是否為管理員 | `boolean` |
| `isVIP()` | 檢查是否為 VIP 或管理員 | `boolean` |
| `isFreeUser()` | 檢查是否為免費用戶 | `boolean` |
| `shouldShowPaywall()` | 是否顯示付費牆 | `boolean` |
| `getUserDisplayName()` | 取得使用者顯示名稱 | `string` |
| `getAuthHeaders()` | 取得 API 請求的認證標頭 | `Object` |
| `isAuthenticated()` | 檢查是否已認證 | `boolean` |
| `getUserInfo()` | 取得使用者完整資訊 | `Object` |

**使用者角色常數:**

```javascript
export const USER_ROLES = {
  ADMIN: 'admin',
  VIP: 'vip',
  FREE: 'free'
};
```

#### 3.2 格式化工具 (`/Users/charlie/Dashboard/frontend/src/utils/formatters.js`)

| 函數名稱 | 描述 | 範例 |
|---------|------|------|
| `formatCurrency(value, fractionDigits)` | 格式化貨幣 (USD) | `1234.56` → `"$1,234.56"` |
| `formatDecimal(value, fractionDigits)` | 格式化小數與逗號 | `1234.567` → `"1,234.57"` |
| `formatPercent(value, fractionDigits)` | 格式化百分比 | `12.3456` → `"12.35%"` |
| `formatLargeNumber(value)` | 格式化大數字 (K, M, B, T) | `1,500,000` → `"1.50M"` |

#### 3.3 API 服務 (`/Users/charlie/Dashboard/frontend/src/services/api.js`)

**主要 API 服務模組:**

| 服務模組 | 端點範圍 | 主要功能 |
|---------|---------|---------|
| `StockApi` | `/stocks/*`, `/stock/*` | 股票資料、歷史、批量查詢 |
| `MarketApi` | `/market/*`, `/tw/*` | 市場數據、熱力圖、台股 |
| `SystemApi` | `/system/*` | 系統狀態、重新整理、回填 |
| `ScreenerApi` | `/market/screener/*`, `/sector/*` | 技術指標篩選、類股相似度 |
| `MomentumApi` | `/momentum/*` | 動量策略指數 |
| `AllocationApi` | `/strategy/*` | 資產配置策略 |
| `DualMomentumApi` | `/dual-momentum/*` | 雙動量回測 |
| `HistoryApi` | `/history/*` | 回測歷史管理 |
| `SignalPathApi` | `/signal-path` | 信號路徑分析 |
| `AnalysisApi` | `/analysis/*` | 策略分析儀表板 |

**Axios 攔截器:**

```javascript
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token');
  if (token) {
    config.headers['X-Admin-Token'] = token;
  }
  return config;
});
```

#### 3.4 Chart.js 配置 (`/Users/charlie/Dashboard/frontend/src/chartSetup.js`)

**全域註冊元件:**

```javascript
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  ArcElement,
  annotationPlugin  // chartjs-plugin-annotation
);
```

#### 3.5 i18n 配置 (`/Users/charlie/Dashboard/frontend/src/i18n.js`)

**語言設定:**

```javascript
i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en },
      'zh-TW': { translation: zhTW }
    },
    fallbackLng: 'en',
    supportedLngs: ['en', 'zh-TW'],
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage']
    }
  });
```

**語言切換:**

```javascript
// 在 DashboardLayout.jsx 中
i18n.changeLanguage(i18n.language === 'en' ? 'zh-TW' : 'en');
```

### 4. 自訂 Hooks 清單

#### 4.1 資料協調 Hook (`/Users/charlie/Dashboard/frontend/src/hooks/useDataOrchestrator.js`)

```javascript
export const useDataOrchestrator = () => {
  // Stage 1 prefetch disabled - data loaded on-demand in pages
  // No auto-refresh - rely on HMR and manual refresh
  return { loadingStatus: 'idle', lastUpdated: null };
};
```

**功能:** 管理應用程式資料生命週期 (預取、階段、重新整理)
**備註:** 目前階段 1 和階段 2 的預取已停用，資料在各頁面按需載入。

#### 4.2 Persona 相關 Hooks (`/Users/charlie/Dashboard/frontend/src/contexts/PersonaContext.jsx`)

**PersonaContext 提供的 Hooks:**

| Hook 名稱 | 描述 |
|---------|------|
| `usePersona()` | 取得 Persona Context，提供完整 Persona 功能 |
| `usePersonaPreferences()` | 取得當前 Persona 的偏好設定 |
| `usePersonaFeature(featureName)` | 檢查特定功能是否應顯示 |
| `isPersonaFeatureEnabled()` | 檢查 Persona 功能是否啟用 (工具函數) |

**PersonaContext 提供的方法:**

```javascript
{
  // 狀態
  personas,              // 可用 Persona 清單
  currentPersona,       // 當前 Persona ID
  preferences,          // 當前偏好設定
  loading,              // 載入狀態
  error,                // 錯誤資訊
  showSelectionModal,   // 是否顯示選擇 Modal

  // 方法
  selectPersona(personaId),              // 選擇 Persona
  getRecommendation(userData),          // 取得推薦 Persona
  shouldShowFeature(featureName),       // 檢查功能是否顯示
  getDefaultMetrics(),                 // 取得預設指標
  getChartComplexity(),                 // 取得圖表複雜度
  getPreference(key, defaultValue),     // 取得偏好設定
  dismissSelectionModal(),              // 關閉選擇 Modal
  loadUserPersona(),                    // 重新載入使用者 Persona
  getUserId(),                          // 取得使用者 ID
  featureEnabled                        // 功能旗標
}
```

**預設 Persona:**

```javascript
{
  beginner: {
    id: 'beginner',
    name: '新手',
    ui_preferences: {
      show_advanced_options: false,
      show_explanations: true,
      default_view: 'guided',
      chart_complexity: 'simple',
      default_metrics: ['sharpe', 'total_return', 'mdd']
    }
  },
  intermediate: { ... },
  expert: { ... },
  conservative: { ... },
  aggressive: { ... }
}
```

#### 4.3 Toast Hook (`/Users/charlie/Dashboard/frontend/src/components/shared/Toast.jsx`)

```javascript
const { toast, success, error, warning, info } = useToast();

// 使用範例
toast.success('Saved successfully!');
toast.error('Failed to save');
toast.show('Custom message', 'info');
```

### 5. 類型定義和接口

**備註:** 本專案使用 JavaScript (非 TypeScript)，沒有明確的類型定義檔案。但透過 JSDoc 和文件註解提供類型提示。

#### 5.1 API 回應類型 (JSDoc 註解)

**StockApi.getHistory:**

```javascript
/**
 * Get stock history with optional indicators.
 * @param {string} symbol
 * @param {Object} params - { sma: [20, 60], macd: true, rsi: true, supertrend: true, extremes: true }
 */
getHistory: async (symbol, params = {}) => { ... }
```

#### 5.2 認證相關類型

**getUserRole() 返回值:** `'admin' | 'vip' | 'free'`

**authenticateUser() 返回值:**

```javascript
Promise<{
  success: boolean,
  role: 'admin' | 'vip' | 'free',
  message: string
}>
```

#### 5.3 Context 類型 (PersonaContext)

**preferences 物件結構:**

```javascript
{
  show_advanced_options: boolean,
  show_explanations: boolean,
  default_view: 'guided' | 'standard' | 'compact',
  chart_complexity: 'simple' | 'standard' | 'detailed',
  default_metrics: string[],
  color_scheme: 'default' | 'safe' | 'growth',
  highlight_risk: boolean,
  highlight_returns: boolean
}
```

### 6. 構建配置說明

#### 6.1 Vite 配置 (`/Users/charlie/Dashboard/frontend/vite.config.js`)

```javascript
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': '/src',
      '@services': '/src/services'
    }
  },
  server: {
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
});
```

**關鍵設定:**
- **路徑別名:** 簡化 import 路徑
- **開發代理:** 繞過 CORS，代理 API 請求到後端

#### 6.2 ESLint 配置 (`/Users/charlie/Dashboard/frontend/eslint.config.js`)

**規則分層:**

| 層級 | 範圍 | 特別規則 |
|-----|------|---------|
| Base | `**/*.{js,jsx}` | 無 console 警告、必須使用 const |
| React Hooks | `**/*.{js,jsx}` | 鉤子規則檢查 |
| React Refresh | `**/*.{js,jsx}` | 只匯出組件常數 |
| Hooks 嚴格模式 | `src/hooks/**/*.{js,jsx}` | 禁止模組級變數、嚴格檢查依賴 |
| Components | `src/components/**/*.{js,jsx}` | 警告不穩定依賴 |

**關鍵規則:**

```javascript
// 無 console (除 warn/error/debug)
'no-console': ['warn', { allow: ['warn', 'error', 'debug'] }]

// React Hooks 嚴格模式
'react-hooks/rules-of-hooks': 'error',
'react-hooks/exhaustive-deps': 'error', // Hooks 目錄內更嚴格

// Hooks 目錄特別規則
'consistent-return': 'warn',
'no-implicit-globals': 'error',
'no-param-reassign': 'error',
```

#### 6.3 Vitest 配置 (`/Users/charlie/Dashboard/frontend/vitest.config.js`)

```javascript
export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'happy-dom',
    setupFiles: './tests/setup.js',
    exclude: ['**/e2e/**', '**/node_modules/**'],
    pool: 'forks',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'json', 'lcov'],
      lines: 50,
      functions: 50,
      branches: 50,
      statements: 50
    }
  }
});
```

**測試設定:**
- **環境:** happy-dom (輕量級 DOM 模擬)
- **覆蓋率目標:** 50% (所有指標)
- **排除:** E2E 測試 (由 Cypress 執行)
- **超時:** 30 秒 (適合 userEvent 互動)

#### 6.4 環境配置 (`/Users/charlie/Dashboard/frontend/src/config.js`)

```javascript
export const CONFIG = {
  enableAutoRefresh: false,
  autoRefreshInterval: 0,
  enableStatusPolling: false,
  statusPollInterval: 0,
  staleTime: IS_DEV ? 0 : 2 * 60 * 1000,     // Dev: 0s, Prod: 2min
  cacheTime: IS_DEV ? 0 : 5 * 60 * 1000,     // Dev: 0s, Prod: 5min
  refetchOnWindowFocus: !IS_DEV,
  refetchOnMount: false,
  enableDebugLogging: IS_DEV
};
```

**環境檢測:**

```javascript
export const IS_DEV =
  import.meta.env.VITE_NODE_ENV === 'development' ||
  import.meta.env.VITE_MODE === 'development' ||
  import.meta.env.DEV;
```

### 7. 前端工具最佳實踐

#### 7.1 專案結構

```
frontend/
├── src/
│   ├── components/          # React 組件
│   │   ├── shared/        # 共享 UI 組件
│   │   │   ├── Skeleton.jsx
│   │   │   ├── ErrorBoundary.jsx
│   │   │   └── Toast.jsx
│   │   └── DashboardLayout.jsx
│   ├── contexts/          # React Context
│   │   └── PersonaContext.jsx
│   ├── hooks/             # 自訂 Hooks
│   │   └── useDataOrchestrator.js
│   ├── pages/             # 頁面組件
│   ├── services/          # API 服務
│   │   └── api.js
│   ├── utils/             # 工具函數
│   │   ├── auth.js
│   │   └── formatters.js
│   ├── locales/           # i18n 語言檔
│   ├── App.jsx
│   ├── main.jsx
│   ├── index.css
│   ├── chartSetup.js
│   ├── i18n.js
│   └── config.js
├── tests/                 # 單元測試
├── cypress/               # E2E 測試
├── vite.config.js
├── vitest.config.js
├── eslint.config.js
└── package.json
```

#### 7.2 代碼規範

**命名慣例:**
- 組件: PascalCase (`DashboardLayout`)
- Hooks: camelCase 前綴 `use` (`useDataOrchestrator`)
- 工具函數: camelCase (`formatCurrency`)
- 常數: UPPER_SNAKE_CASE (`USER_ROLES`)
- CSS 類別: kebab-case (`premium-card`)

**Import 順序:**

```javascript
// 1. React
import React, { useState } from 'react';

// 2. 第三方庫
import axios from 'axios';
import { useTranslation } from 'react-i18next';

// 3. 內部服務/工具
import apiClient from './services/api';
import { isAdmin } from './utils/auth';

// 4. 組件
import Component from './components/Component';

// 5. 樣式
import './styles.css';
```

#### 7.3 組件設計模式

**1. Error Boundary 包裝:**

```javascript
<ErrorBoundary>
  <YourComponent />
</ErrorBoundary>
```

**2. Skeleton Loading:**

```javascript
{loading ? (
  <Skeleton.Table rows={5} columns={4} />
) : (
  <Table data={data} />
)}
```

**3. Toast 通知:**

```javascript
const { toast } = useToast();
try {
  await apiCall();
  toast.success('Success!');
} catch (error) {
  toast.error('Failed');
}
```

**4. Lazy Loading:**

```javascript
const MarketScanner = React.lazy(() => import('./pages/market-scanner'));

<Suspense fallback={<LoadingFallback />}>
  <Routes>
    <Route path="/" element={<MarketScanner />} />
  </Routes>
</Suspense>
```

#### 7.4 狀態管理策略

**1. React Query (TanStack Query):**

```javascript
// 使用 React Query 進行資料取得
const { data, error, isLoading } = useQuery({
  queryKey: ['stocks'],
  queryFn: () => apiClient.get('/stocks')
});
```

**2. Context API:**

```javascript
// 使用 Context 管理全局狀態
const { currentPersona, preferences } = usePersona();
```

**3. Zustand (全域狀態):**

```javascript
// Zustand 用於跨元件狀態共享
import useStore from './store';
```

#### 7.5 API 呼叫最佳實踐

**1. 統一使用 apiClient:**

```javascript
import apiClient from './services/api';
const response = await apiClient.get('/stocks');
```

**2. 認證自動處理:**

```javascript
// Axios 攔截器自動加入 X-Admin-Token
// 無需手動設定標頭
```

**3. 錯誤處理:**

```javascript
try {
  const response = await apiClient.get('/endpoint');
  return response.data;
} catch (error) {
  console.error('API Error:', error);
  // 顯示錯誤訊息
  toast.error('Failed to fetch data');
}
```

#### 7.6 樣式最佳實踐

**1. 使用 CSS 變數:**

```css
/* 好 */
background: var(--bg-main);
color: var(--text-main);

/* 避免 (硬編碼) */
background: #f8fafc;
```

**2. 響應式設計:**

```css
/* 使用 Bootstrap 響應式類別 */
<div className="row">
  <div className="col-md-3 col-6">
    {/* 內容 */}
  </div>
</div>
```

**3. 自訂動畫:**

```css
/* 使用預定義動畫類別 */
<div className="animate-fade-in">Content</div>
<div className="animate-slide-up">Content</div>
```

**4. Glassmorphism 效果:**

```css
/* 使用 .glass 類別 */
<div className="glass card">
  {/* 內容 */}
</div>
```

#### 7.7 國際化 (i18n)

**1. 使用翻譯鉤子:**

```javascript
const { t } = useTranslation();
<h1>{t('header.pro_terminal')}</h1>
```

**2. 語言檔位置:**

```
src/locales/
├── en.json         # 英文
└── zh-TW.json      # 繁體中文
```

#### 7.8 測試策略

**1. 單元測試 (Vitest + happy-dom):**

```javascript
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';

describe('Component', () => {
  it('renders correctly', () => {
    render(<Component />);
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });
});
```

**2. E2E 測試 (Cypress):**

```javascript
// cypress/e2e/example.cy.js
cy.visit('/');
cy.contains('Market Scanner').should('be.visible');
```

#### 7.9 開發工作流程

**1. 開發模式 (HMR):**

```bash
cd /Users/charlie/Dashboard
npm run dev
```

- 前端: Vite HMR 自動重新整理
- 後端: `uvicorn --reload` 自動重啟

**2. 建構生產版本:**

```bash
npm run build
```

**3. 測試:**

```bash
npm run test              # 單元測試
npm run test:watch        # 監聽模式
npm run test:coverage     # 覆蓋率報告
npm run test:e2e          # E2E 測試
```

**4. Lint:**

```bash
npm run lint
```

#### 7.10 常見反模式避免

**❌ 避免直接修改 Props:**

```javascript
// 錯誤
function Component({ data }) {
  data.name = 'New Name';  // 直接修改
}

// 正確
function Component({ data }) {
  const [name, setName] = useState(data.name);
}
```

**❌ 避免在 Hooks 中使用模組級變數:**

```javascript
// 錯誤 (共享狀態 bug)
let sharedState = null;

function useMyHook() {
  if (!sharedState) {
    sharedState = expensiveOperation();
  }
  return sharedState;
}

// 正確
function useMyHook() {
  const [state, setState] = useState(null);
  useEffect(() => {
    const result = expensiveOperation();
    setState(result);
  }, []);
  return state;
}
```

**❌ 避免硬編碼 CSS:**

```javascript
// 錯誤
<div style={{ backgroundColor: '#f8fafc' }}>

// 正確
<div style={{ backgroundColor: 'var(--bg-main)' }}>
// 或
<div className="premium-card">
```

**❌ 避免在 useEffect 中直接使用 async 函數:**

```javascript
// 錯誤
useEffect(async () => {
  await fetchData();
}, []);

// 正確
useEffect(() => {
  const fetchData = async () => {
    await apiCall();
  };
  fetchData();
}, []);
```

## Recommendations

1. **✅ 樣式系統:** 已完整實作 CSS 變數主題，建議擴展支援深色主題

2. **⚠️ 類型定義:** 目前使用 JavaScript，建議考慮逐步引入 TypeScript 或加強 JSDoc 註解

3. **✅ 工具函數:** 認證和格式化工具完整，API 服務模組化良好

4. **✅ 自訂 Hooks:** useDataOrchestrator 和 Persona 設計合理

5. **⚠️ 測試覆蓋率:** Vitest 設定目標 50%，建議提高至 70-80%

6. **✅ ESLint 規則:** Hooks 目錄嚴格模式設定完善

7. **✅ 構建配置:** Vite 和 Vitest 設定清晰，支援 HMR

## Confidence & Limitations

- **Confidence:** high
- **Data quality:** Excellent (直接讀取原始碼檔案)
- **Assumptions:** 無重大假設，所有結論基於實際程式碼
- **Limitations:**
  - 未深入分析各頁面的實作細節
  - 未檢查測試檔案的覆蓋率實際數值
  - 未分析效能優化細節

## Metadata

- **Analysis framework:** 前端架構分析 (樣式系統、工具函數、Hooks、構建配置)
- **Suggestions:** 本分析可用於設計 programmer sub-agent 的前端工具指引
