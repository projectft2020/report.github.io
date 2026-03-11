# Dashboard API 客戶端分析

**分析目標：** 分析 Dashboard 前端的 API 調用和服務層，為設計 programmer sub-agent 提供完整的 API 集成知識。

**分析日期：** 2026-02-21

**Dashboard 路徑：** `/Users/charlie/Dashboard/`

**技術棧：**
- 前端框架：React 19.2.0
- HTTP 客戶端：Axios 1.13.2
- 數據獲取：@tanstack/react-query 5.90.16
- 構建工具：Vite 7.2.4
- 語言：JavaScript (非 TypeScript)

---

## 1. API 客戶端配置說明

### 1.1 Axios 實例配置

**位置：** `/Users/charlie/Dashboard/frontend/src/services/api.js`

```javascript
import axios from 'axios';

const API_BASE_URL = '/api';

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    paramsSerializer: {
        indexes: null // 使用 format: sma=20&sma=44 而不是 sma[0]=20&sma[1]=44
    }
});
```

**關鍵配置：**
- `baseURL`: 使用相對路徑 `/api`，自動適應當前主機（localhost 或遠程 IP）
- `paramsSerializer.indexes: null`: 關鍵配置，用於處理數組參數，避免方括號格式
- 支持自定義 `paramsSerializer` 以兼容 FastAPI 的參數處理

### 1.2 請求攔截器 - 認證處理

```javascript
apiClient.interceptors.request.use((config) => {
    const token = localStorage.getItem('admin_token');
    if (token) {
        config.headers['X-Admin-Token'] = token;
    }
    return config;
}, (error) => {
    return Promise.reject(error);
});
```

**認證策略：**
- 使用 `X-Admin-Token` header 傳遞管理員令牌
- Token 存儲在 `localStorage` 中
- 統一攔截器自動注入，無需手動添加

### 1.3 React Query 全局配置

**位置：** `/Users/charlie/Dashboard/frontend/src/main.jsx`

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

**環境差異：**

| 配置項 | 開發環境 | 生產環境 | 說明 |
|--------|---------|---------|------|
| `staleTime` | 0 | 2 分鐘 | 開發無快取（測試最新代碼） |
| `gcTime` | 0 | 5 分鐘 | 快取保留時間 |
| `refetchOnWindowFocus` | false | true | 視窗聚焦時自動刷新 |
| `retry` | 1 | 1 | 失敗重試次數 |

---

## 2. 所有 API 函數清單（按模塊分類）

### 2.1 StockApi - 股票數據服務

**位置：** `/Users/charlie/Dashboard/frontend/src/services/api.js`

| 函數名 | 方法 | 端點 | 描述 |
|--------|------|------|------|
| `getAllStocks()` | GET | `/stocks` | 獲取所有追蹤股票的基本概覽 |
| `getHistory(symbol, params)` | GET | `/stocks/{symbol}/history` | 獲取股票歷史數據及技術指標 |
| `getStockDetail(symbol, days)` | GET | `/stock/{symbol}` | 獲取單個股票詳細信息 |
| `getBatchStocks(symbols, days)` | POST | `/stocks/batch` | 批量獲取股票數據（優化版） |
| `addTrackedSymbols(symbols)` | POST | `/tracked_symbols` | 添加符號到追蹤列表 |
| `deleteTrackedSymbol(symbol)` | DELETE | `/tracked_symbols/{symbol}` | 刪除追蹤符號 |
| `getTrackedSymbols()` | GET | `/tracked_symbols` | 獲取追蹤符號列表 |
| `getQuarterlyMetric(symbol, metric)` | GET | `/stock/{symbol}/quarterly-metric` | 獲取季度財務指標 |
| `getQuarterlyFundamentals(symbol)` | GET | `/stock/{symbol}/quarterly-fundamentals` | 獲取季度基本面數據 |

**使用示例：**
```javascript
import { StockApi } from './services/api';

// 獲取股票歷史數據，帶技術指標
const data = await StockApi.getHistory('AAPL', {
    sma: [20, 60],
    macd: true,
    rsi: true,
    supertrend: true,
    extremes: true
});
```

### 2.2 MarketApi - 市場數據服務

| 函數名 | 方法 | 端點 | 描述 |
|--------|------|------|------|
| `getMovers()` | GET | `/market/movers` | 獲取市場漲跌幅榜 |
| `getHeatmap(targetDate, market)` | GET | `/market/heatmap` | 獲取市場熱力圖 |
| `getSectorHeatmap(targetDate, market)` | GET | `/market/sector-heatmap` | 獲取板塊熱力圖 |
| `getMarketScore()` | GET | `/market/score` | 獲取市場評分 |
| `getTwDashboard()` | GET | `/tw/dashboard` | 獲取台灣市場儀表板 |
| `getTwPulse()` | GET | `/tw/pulse` | 獲取台灣市場脈動 |
| `getTwHeatmap(mode)` | GET | `/market/heatmap` | 獲取台灣市場熱力圖 |
| `getTwSectorHeatmap()` | GET | `/tw/heatmap/sector` | 獲取台灣板塊熱力圖 |
| `getTwStockDetail(symbol, days)` | GET | `/stocks/{symbol}` | 獲取台灣股票詳情 |
| `getTwStockHistory(symbol, days)` | GET | `/stocks/{symbol}/history` | 獲取台灣股票歷史 |

### 2.3 SystemApi - 系統操作服務

| 函數名 | 方法 | 端點 | 描述 |
|--------|------|------|------|
| `refreshSymbol(symbol, full)` | POST | `/system/refresh` | 刷新單個股票數據 |
| `refreshAll(full)` | POST | `/system/refresh-all` | 刷新所有股票數據 |
| `getStatus()` | GET | `/system/status` | 獲取系統狀態 |
| `backfillStrategies(years, batch_size)` | POST | `/system/backfill-strategies` | 回填策略數據 |
| `yfinanceTwFast(years)` | POST | `/system/yfinance-tw-fast` | 快速獲取台灣數據 |
| `yfinanceTwRetryFailed(years)` | POST | `/system/yfinance-tw-retry-failed` | 重試失敗的台灣數據 |
| `backfillSymbol(symbol, years, market)` | POST | `/system/backfill-symbol` | 回填單個符號歷史 |

### 2.4 ScreenerApi - 篩選器服務

| 函數名 | 方法 | 端點 | 描述 |
|--------|------|------|------|
| `getSuperTrend(params)` | GET | `/market/screener/supertrend` | SuperTrend 篩選 |
| `getMacd(params)` | GET | `/market/screener/macd` | MACD 篩選 |
| `getExtremes(params)` | GET | `/market/screener/extremes` | 極值篩選 |
| `getRsi(params)` | GET | `/market/screener/rsi` | RSI 篩選 |
| `getFIndex(params)` | GET | `/market/screener/f-index` | F-Index 篩選 |
| `getSectorSimilarity(targetDate, market)` | GET | `/sector/similarity` | 板塊相似性分析 |

### 2.5 MomentumApi - 動量策略服務

| 函數名 | 方法 | 端點 | 描述 |
|--------|------|------|------|
| `getIndex(years, config)` | GET | `/momentum/index` | 美國動量指數 |
| `getType2Index(years, config)` | GET | `/momentum/type2` | 動量指數 Type 2 |
| `getTwIndex(years, config)` | GET | `/momentum/tw-index` | 台灣動量指數 |
| `getTwIndexType2(years, config)` | GET | `/momentum/tw-index-type2` | 台灣動量指數 Type 2 |

### 2.6 AllocationApi - 資產配置服務

| 函數名 | 方法 | 端點 | 描述 |
|--------|------|------|------|
| `get6040Strategy(years)` | GET | `/strategy/6040` | 60/40 策略回測 |
| `getAllWeatherStrategy(years)` | GET | `/strategy/all-weather` | All-Weather 策略 |
| `getGoldenButterflyStrategy(years)` | GET | `/strategy/golden-butterfly` | Golden Butterfly 策略 |
| `getStrategySummary()` | GET | `/strategy/summary` | 策略摘要 |

### 2.7 DualMomentumApi - 雙動量服務

| 函數名 | 方法 | 端點 | 描述 |
|--------|------|------|------|
| `runBacktest(config)` | POST | `/dual-momentum/backtest` | 運行雙動量回測 |
| `getDefaultConfig()` | GET | `/dual-momentum/default-config` | 獲取默認配置 |

### 2.8 HistoryApi - 回測歷史服務

| 函數名 | 方法 | 端點 | 描述 |
|--------|------|------|------|
| `list(strategyType, market, limit)` | GET | `/history` | 獲取回測歷史列表 |
| `getById(id)` | GET | `/history/{id}` | 獲取單條回測記錄 |
| `save(data)` | POST | `/history` | 保存回測結果 |
| `delete(id)` | DELETE | `/history/{id}` | 刪除回測記錄 |
| `compare(ids)` | POST | `/history/compare` | 比較多個回測結果 |

### 2.9 AnalysisApi - 分析儀表板服務

| 函數名 | 方法 | 端點 | 描述 |
|--------|------|------|------|
| `getRegimePerformance(runId, params)` | GET | `/analysis/regime-performance/{runId}` | 市場週期績效分析 |
| `getCrossValidation(runId)` | GET | `/analysis/cross-validation/{runId}` | 交叉驗證結果 |
| `getSignalQuality(runId)` | GET | `/analysis/signal-quality/{runId}` | 信號質量分析 |
| `getMonteCarlo(runId)` | GET | `/analysis/monte-carlo/{runId}` | 蒙特卡羅模擬 |
| `getPerformanceAttribution(runId)` | GET | `/analysis/attribution/{runId}` | 績效歸因分析 |
| `getScenarioAnalysis(runId, params)` | GET | `/analysis/scenario/{runId}` | 情境分析 |
| `getShadowTrading(runId, params)` | GET | `/analysis/shadow-trading/{runId}` | 影子交易分析 |
| `getTornadoAnalysis(runId, params)` | GET | `/analysis/tornado/{runId}` | 龍捲風圖分析 |

### 2.10 策略系統 API (useStrategyAPI)

**位置：** `/Users/charlie/Dashboard/frontend/src/pages/StrategyPage/hooks/useStrategyAPI.js`

**基礎端點：** `/api/strategies`

#### Templates（策略模板）
| 函數名 | 端點 | 描述 |
|--------|------|------|
| `getTemplates()` | `/templates` | 獲取所有模板 |
| `getTemplate(templateId)` | `/templates/{id}` | 獲取單個模板 |
| `getTemplateMarkets(templateId)` | `/templates/{id}/markets` | 獲取模板支持的市场 |

#### Markets（市場）
| 函數名 | 端點 | 描述 |
|--------|------|------|
| `getMarkets()` | `/markets` | 獲取所有市场 |
| `getMarket(marketId)` | `/markets/{id}` | 獲取單個市场 |

#### Universes（股票池）
| 函數名 | 端點 | 描述 |
|--------|------|------|
| `getUniverses(marketId)` | `/universes` | 獲取股票池列表 |
| `getUniverse(universeId)` | `/universes/{id}` | 獲取單個股票池 |

#### Strategy Instances（策略實例）
| 函數名 | 端點 | 描述 |
|--------|------|------|
| `getInstances(filters)` | `/instances` | 獲取策略實例列表 |
| `getInstance(instanceId)` | `/crud/strategies` | 獲取單個策略實例 |
| `createInstance(data)` | `/instances` | 創建策略實例 |
| `updateInstance(instanceId, updates)` | `/crud/strategies/{id}` | 更新策略實例 |
| `deleteInstance(instanceId)` | `/crud/strategies/{id}` | 刪除策略實例 |
| `duplicateInstance(instanceId, newName)` | - | 複製策略實例 |

#### Backtest（回測）
| 函數名 | 端點 | 描述 |
|--------|------|------|
| `runBacktest(request)` | `/backtest/run` | 運行自定義回測 |
| `runSavedBacktest(strategyId)` | `/backtest/run-saved` | 運行已保存策略回測 |

#### History（歷史）
| 函數名 | 端點 | 描述 |
|--------|------|------|
| `getHistory(filters)` | `/history` | 獲取回測歷史 |
| `getHistoryRecord(recordId)` | `/history/{id}` | 獲取單條記錄 |
| `deleteHistoryRecord(recordId)` | `/history/{id}` | 刪除記錄 |

#### Resonance（共振信號）
| 函數名 | 端點 | 描述 |
|--------|------|------|
| `getResonanceStrategies()` | `/resonance/strategies` | 獲取共振策略列表 |
| `getResonanceSymbol(symbol, ...)` | `/resonance/symbol/{symbol}` | 獲取單個符號共振 |
| `discoverResonanceSymbols(options)` | `/resonance/discover` | 發現高共振符號 |
| `getDailySummary(options)` | `/resonance/summary` | 獲取每日摘要 |
| `runManualScan(market, date)` | `/resonance/scan` | 手動運行掃描 |

#### Showcase（展示）
| 函數名 | 端點 | 描述 |
|--------|------|------|
| `getShowcaseConfigs()` | `/showcase/configs` | 獲取展示配置 |
| `getShowcaseData(strategyType, ...)` | `/showcase/{type}` | 獲取展示數據 |
| `clearShowcaseCache()` | `/showcase/cache` | 清除展示快取 |

#### Comparison（比較）
| 函數名 | 端點 | 描述 |
|--------|------|------|
| `getComparison(options)` | `/comparison` | 獲取策略比較 |

#### Cache（快取管理）
| 函數名 | 端點 | 描述 |
|--------|------|------|
| `getCacheStats()` | `/cache/stats` | 獲取快取統計 |
| `clearCache()` | `/cache` | 清除快取 |

### 2.11 其他直接 fetch 調用

**動量頁面：**
- `GET /api/momentum/{market}?years=...&top_n=...&weighting_method=...`
- `GET /api/allocation/{strategy}?years=...&rebalance_freq=...`

**信號儀表板：**
- `GET /api/resonance/home?market=...&target_date=...&signal_mode=...`
- `GET /api/resonance/strategies`
- `GET /api/resonance/summary?market=...&target_date=...`

**期貨回測：**
- `POST /api/futures-backtest/run`

---

## 3. 錯誤處理和重試策略

### 3.1 請求保護機制

**位置：** `/Users/charlie/Dashboard/frontend/src/utils/requestProtection.js`

**核心功能：**
- 請求去重（防止重複請求）
- 請求超時處理（默認 30 秒）
- 指數退避重試（最多 3 次）
- AbortController 支持（可取消）
- 處理 React Strict Mode 雙重調用

**配置：**
```javascript
const CONFIG = {
  debounceMs: 300,           // 去重時間窗口
  maxConcurrent: 1,          // 最大併發請求數
  maxRetries: 3,             // 最大重試次數
  baseRetryDelay: 1000,      // 基礎重試延遲（ms）
  requestTimeout: 30000,     // 請求超時（ms）
};
```

**重試策略：**
- 僅對服務器錯誤（5xx）重試
- 不重試客戶端錯誤（4xx），包括 429（速率限制）
- 指數退避：`baseRetryDelay * 2^attempt`

**使用示例：**
```javascript
import { protectedFetch } from '../utils/requestProtection';

const response = await protectedFetch('/api/strategies/templates', {
  method: 'GET',
  headers: { 'Content-Type': 'application/json' }
});
```

### 3.2 React Query 重試配置

**位置：** `/Users/charlie/Dashboard/frontend/src/hooks/useApiCache.js`

```javascript
retry: (failureCount, error) => {
    // 不重試客戶端錯誤（4xx）
    if (error?.response?.status >= 400 && error?.response?.status < 500) {
        return false;
    }
    // 不重試速率限制（429）
    if (error?.response?.status === 429) {
        return false;
    }
    // 重試服務器錯誤最多 2 次
    return failureCount < 2;
}
```

### 3.3 React ErrorBoundary

**位置：** `/Users/charlie/Dashboard/frontend/src/components/shared/ErrorBoundary.jsx`

**功能：**
- 捕獲組件樹中的 JavaScript 錯誤
- 顯示友好錯誤 UI
- 開發模式下顯示詳細錯誤信息
- 支持自定義 fallback UI
- 提供重試和返回首頁按鈕

**使用示例：**
```jsx
<ErrorBoundary>
  <YourComponent />
</ErrorBoundary>
```

### 3.4 統一錯誤處理模式

**在組件中處理錯誤：**
```javascript
const { data, error, isLoading } = useApiCache(
    ['momentum', market, years],
    fetchMomentumData
);

if (isLoading) return <LoadingSpinner />;
if (error) return <ErrorMessage message={error.message} />;
```

**在異步操作中處理錯誤：**
```javascript
try {
    const response = await api.post('/api/backtest/run', config);
    setResults(response.data);
} catch (err) {
    const errorMsg = err.response?.data?.detail || err.message || 'Failed to run backtest';
    setError(errorMsg);
}
```

---

## 4. API 類型定義和接口

**注意：** 項目使用 JavaScript 而非 TypeScript，類型通過 JSDoc 註釋和 API 響應結構定義。

### 4.1 JSDoc 註釋示例

**股票 API：**
```javascript
/**
 * Get stock history with optional indicators.
 * @param {string} symbol - Stock symbol (e.g., 'AAPL')
 * @param {Object} params - Query parameters
 * @param {Array<number>} params.sma - SMA periods (e.g., [20, 60])
 * @param {boolean} params.macd - Include MACD indicator
 * @param {boolean} params.rsi - Include RSI indicator
 * @param {boolean} params.supertrend - Include SuperTrend indicator
 * @param {boolean} params.extremes - Include Extremes indicator
 * @returns {Promise<Object>} Stock history data with indicators
 */
getHistory: async (symbol, params = {}) => {
    const response = await apiClient.get(`/stocks/${symbol}/history`, { params });
    return response.data;
}
```

### 4.2 常見數據結構

**股票數據響應：**
```javascript
{
    symbol: "AAPL",
    dates: ["2024-01-01", "2024-01-02", ...],
    close: [150.0, 152.3, ...],
    volume: [5000000, 5500000, ...],
    // Indicators (optional)
    sma_20: [148.5, 149.2, ...],
    rsi: [55.3, 57.2, ...],
    macd: { signal: [...], macd: [...], histogram: [...] }
}
```

**回測結果響應：**
```javascript
{
    run_id: "uuid",
    strategy_id: "strategy-123",
    status: "completed",
    metrics: {
        total_return: 0.25,
        cagr: 0.08,
        mdd: -0.15,
        sharpe: 1.2,
        win_rate: 0.65,
        volatility: 0.12
    },
    equity_curve: [...],
    return_series: [...],
    trades: [...]
}
```

**共振信號響應：**
```javascript
{
    resonance_symbols: [
        {
            symbol: "AAPL",
            resonance_count: 4,
            strategies: ["rsi", "macd", "supertrend", "momentum"],
            last_signal: "buy"
        }
    ],
    by_strategy: {
        "rsi": { symbols: [...], signal: "buy" }
    }
}
```

### 4.3 配置常量

**位置：** `/Users/charlie/Dashboard/frontend/src/config.js`

```javascript
export const CONFIG = {
    enableAutoRefresh: false,
    autoRefreshInterval: 0,
    enableStatusPolling: false,
    statusPollInterval: 0,
    staleTime: IS_DEV ? 0 : 2 * 60 * 1000,
    cacheTime: IS_DEV ? 0 : 5 * 60 * 1000,
    refetchOnWindowFocus: !IS_DEV,
    refetchOnMount: false,
    enableDebugLogging: IS_DEV,
};
```

---

## 5. React Query Hooks 使用模式

### 5.1 useApiCache - 統一查詢 Hook

**位置：** `/Users/charlie/Dashboard/frontend/src/hooks/useApiCache.js`

**基本使用：**
```javascript
import { useApiCache } from '../hooks/useApiCache';

const { data, isLoading, error, refetch } = useApiCache(
    'strategies',
    () => api.getStrategies()
);
```

**帶參數的查詢：**
```javascript
const { data } = useApiCache(
    ['strategy', id],
    () => api.getStrategy(id),
    { staleTime: 10 * 60 * 1000 }
);
```

**返回值：**
- `data`: API 響應數據
- `isLoading`: 加載狀態
- `error`: 錯誤對象
- `refetch`: 手動刷新函數
- `isFetching`: 請求進行中（包含後台刷新）

### 5.2 useApiMutation - 統一變異 Hook

**位置：** `/Users/charlie/Dashboard/frontend/src/hooks/useApiCache.js`

**基本使用：**
```javascript
import { useApiMutation } from '../hooks/useApiCache';

const { mutate, mutateAsync, isLoading, error } = useApiMutation(
    (data) => api.createStrategy(data),
    {
        invalidateKeys: ['strategies'],
        onSuccess: () => console.log('Strategy created'),
    }
);

// 使用
mutate(strategyData);
// 或
await mutateAsync(strategyData);
```

**特性：**
- 自動使相關查詢失效（invalidateKeys）
- 支持成功/失敗回調
- 支持 `mutate`（不返回 Promise）和 `mutateAsync`（返回 Promise）

### 5.3 快取預設

```javascript
export const cachePresets = {
    static: {
        staleTime: 60 * 60 * 1000,   // 1 小時
        gcTime: 24 * 60 * 60 * 1000, // 24 小時
    },
    user: {
        staleTime: 5 * 60 * 1000,   // 5 分鐘
        gcTime: 30 * 60 * 1000,     // 30 分鐘
    },
    dynamic: {
        staleTime: 30 * 1000,       // 30 秒
        gcTime: 5 * 60 * 1000,      // 5 分鐘
    },
    realtime: {
        staleTime: 0,
        gcTime: 0,
    },
};
```

### 5.4 快取工具函數

```javascript
import { cacheUtils } from '../hooks/useApiCache';

// 使查詢失效
cacheUtils.invalidate('strategies');

// 清除所有快取
cacheUtils.clear();

// 預取數據
await cacheUtils.prefetch('strategies', () => api.getStrategies());

// 獲取快取數據
const data = cacheUtils.getData('strategies');

// 設置快取數據
cacheUtils.setData('strategies', newData);
```

### 5.5 頁面級別使用模式

**MomentumPage:**
```javascript
const fetchMomentumData = useCallback(async () => {
    const params = new URLSearchParams({
        years,
        top_n: config.top_n,
        weighting_method: config.weighting_method,
        // ...
    });
    const response = await fetch(`/api/momentum/${market.toLowerCase()}?${params}`);
    return response.json();
}, [market, config, years]);

const { data, isLoading, error, refetch } = useApiCache(
    ['momentum', market, years, JSON.stringify(config)],
    fetchMomentumData,
    momentumCacheConfig
);
```

**AllocationPage:**
```javascript
const fetchAllocationData = useCallback(async () => {
    const response = await fetch(
        `/api/allocation/${selectedStrategy}?years=${years}&rebalance_freq=${rebalanceFreq}`
    );
    return response.json();
}, [selectedStrategy, years, rebalanceFreq]);

const { data, isLoading, error, refetch } = useApiCache(
    ['allocation', selectedStrategy, years, rebalanceFreq],
    fetchAllocationData,
    allocationCacheConfig
);
```

### 5.6 全局 QueryClient 訪問

**在 main.jsx 中暴露：**
```javascript
if (typeof window !== 'undefined') {
    window.__queryClient = queryClient;
}
```

**在任何地方使用：**
```javascript
const queryClient = window.__queryClient;
queryClient.invalidateQueries({ queryKey: ['strategies'] });
```

---

## 6. API 集成最佳實踐

### 6.1 統一使用 React Query

**✅ 推薦做法：**
```javascript
import { useApiCache } from '../hooks/useApiCache';

const { data, isLoading, error } = useApiCache(
    'endpoint',
    fetchFunction,
    { staleTime: 2 * 60 * 1000 }
);
```

**❌ 不推薦：**
```javascript
// 直接使用 fetch/axios（缺少快取、重試、去重）
useEffect(() => {
    fetch('/api/data').then(res => res.json()).then(setData);
}, []);
```

### 6.2 使用 protectedFetch 防止重複請求

**適用場景：**
- React Strict Mode 環境
- 頻繁觸發的用戶操作
- 可能並發發起相同請求的情況

**使用示例：**
```javascript
import { protectedFetch } from '../utils/requestProtection';

const data = await protectedFetch('/api/endpoint', {
    method: 'POST',
    body: JSON.stringify(payload)
});
```

### 6.3 統一錯誤處理

**在組件層面：**
```javascript
const { data, error, isLoading } = useApiCache(key, fetcher);

if (isLoading) return <LoadingSpinner />;
if (error) return <ErrorAlert message={error.message} />;
if (!data) return <EmptyState />;
```

**在 API 層面：**
```javascript
try {
    const response = await api.post('/api/backtest/run', config);
    return response.data;
} catch (err) {
    // 提取詳細錯誤信息
    const errorMsg = err.response?.data?.detail || err.message || 'Operation failed';
    throw new Error(errorMsg);
}
```

### 6.4 合理設置快取策略

**靜態數據（策略配置、市場列表）：**
```javascript
useApiCache('markets', fetchMarkets, cachePresets.static);
```

**用戶數據（用戶策略、投資組合）：**
```javascript
useApiCache(['user-strategies', userId], fetchUserStrategies, cachePresets.user);
```

**動態數據（市場價格、信號）：**
```javascript
useApiCache('market-prices', fetchMarketPrices, cachePresets.dynamic);
```

**實時數據（回測結果）：**
```javascript
useApiCache(['backtest', runId], fetchBacktestResult, cachePresets.realtime);
```

### 6.5 使用 Query Keys 進行精確控制

**多參數查詢：**
```javascript
// 使用數組作為 key，參數變化時自動重新獲取
useApiCache(
    ['momentum', market, years, JSON.stringify(config)],
    fetchMomentumData
);
```

**使相關查詢失效：**
```javascript
// 使所有動量查詢失效
cacheUtils.invalidate(['momentum']);

// 使特定市場的動量查詢失效
cacheUtils.invalidate(['momentum', 'US']);
```

### 6.6 使用 Mutation 處理 POST/PUT/DELETE

```javascript
const createStrategy = useApiMutation(
    (data) => api.createStrategy(data),
    {
        invalidateKeys: ['strategies'],
        onSuccess: (data) => {
            console.log('Strategy created:', data);
            // 導航到新策略頁面
            navigate(`/strategies/builder?instance_id=${data.instance_id}`);
        },
        onError: (error) => {
            console.error('Failed to create strategy:', error);
            alert(`Failed: ${error.message}`);
        }
    }
);

createStrategy.mutate(strategyData);
```

### 6.7 環境感知配置

```javascript
import { IS_DEV } from '../config';

const cacheConfig = IS_DEV ? {} : {
    staleTime: 2 * 60 * 1000,  // 開發無快取
    gcTime: 10 * 60 * 1000,
};

const { data } = useApiCache(key, fetcher, cacheConfig);
```

### 6.8 組件拆分與 API 獲取

**保持 API 邏輯在自定義 Hooks 中：**
```javascript
// hooks/useMomentum.js
export const useMomentum = () => {
    const [market, setMarket] = useState('US');
    const [config, setConfig] = useState(defaultConfig);

    const { data, isLoading, error } = useApiCache(
        ['momentum', market, JSON.stringify(config)],
        fetchMomentumData
    );

    return { market, setMarket, config, setConfig, data, isLoading, error };
};
```

**組件只關心 UI：**
```javascript
const MomentumPage = () => {
    const { market, config, data, isLoading } = useMomentum();
    // 只渲染 UI
};
```

### 6.9 使用 localStorage 持久化偏好

```javascript
// 讀取保存的偏好
const getInitialMarket = () => {
    return localStorage.getItem('marketScanner_market') || 'US';
};

// 保存變更
const handleMarketChange = (market) => {
    setSelectedMarket(market);
    localStorage.setItem('marketScanner_market', market);
};
```

### 6.10 統一的認證處理

**使用 utils/auth.js：**
```javascript
import { getAuthHeaders, isAdmin, isVIP } from '../utils/auth';

// 獲取認證 headers
const headers = getAuthHeaders();

// 檢查權限
if (!isAdmin()) {
    return <Navigate to="/" replace />;
}

// 自動處理（通過 axios 攔截器）
// 無需手動添加 token
```

### 6.11 防止記憶體洩漏

**清理 useEffect：**
```javascript
useEffect(() => {
    const fetchData = async () => {
        // ...
    };
    fetchData();

    // 如果設置了輪詢，需要清理
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
}, [dependencies]);
```

### 6.12 使用 Suspense 和 ErrorBoundary

```javascript
<Suspense fallback={<LoadingSpinner />}>
    <ErrorBoundary>
        <YourComponent />
    </ErrorBoundary>
</Suspense>
```

### 6.13 日誌和調試

**開發環境啟用日誌：**
```javascript
import { IS_DEV } from '../config';

if (IS_DEV && options.enableDebugLogging) {
    console.debug('[useApiCache] Query:', { queryKey, options });
}
```

### 6.14 避免無限循環

**使用 useCallback 和依賴數組：**
```javascript
const fetchData = useCallback(async () => {
    const response = await fetch(`/api/data?param=${value}`);
    return response.json();
}, [value]); // 正確的依賴

useEffect(() => {
    fetchData();
}, [fetchData]); // fetchData 變化時重新執行
```

### 6.15 使用 debounce 和 throttle

```javascript
import { debounce, throttle } from '../utils/requestProtection';

// 防抖：防止頻繁觸發
const debouncedSearch = debounce((query) => {
    // 發起搜索請求
}, 300);

// 節流：限制調用頻率
const throttledRefresh = throttle(() => {
    // 刷新數據
}, 1000);
```

---

## 7. 架構總結

### 7.1 分層架構

```
┌─────────────────────────────────────┐
│         React Components           │  (UI 層)
├─────────────────────────────────────┤
│      Custom Hooks (useXXX)        │  (狀態管理層)
├─────────────────────────────────────┤
│   useApiCache / useApiMutation    │  (數據獲取層)
├─────────────────────────────────────┤
│     React Query (TanStack)        │  (快取和狀態)
├─────────────────────────────────────┤
│   protectedFetch (請求保護)        │  (網絡層)
├─────────────────────────────────────┤
│      Axios Instance               │  (HTTP 客戶端)
├─────────────────────────────────────┤
│           Backend API              │  (FastAPI 後端)
└─────────────────────────────────────┘
```

### 7.2 數據流

```
用戶操作 → UI 組件 → Hook → useApiCache
                                ↓
                        React Query 檢查快取
                                ↓
                    (miss) → protectedFetch → Axios → Backend API
                                ↓
                        React Query 快取數據
                                ↓
                        組件重新渲染
```

### 7.3 關鍵設計模式

1. **統一 API 客戶端：** 所有 HTTP 請求通過 Axios 實例
2. **統一認證：** 攔截器自動注入 token
3. **統一錯誤處理：** React Query + ErrorBoundary
4. **統一快取策略：** React Query + 環境配置
5. **請求保護：** 去重、超時、重試
6. **Hooks 抽象：** 封裝業務邏輯，組件只關注 UI
7. **Query Keys 管理：** 精確控制快取失效
8. **環境感知：** 開發/生產不同的配置

---

## 8. 為 Programmer Sub-Agent 的建議

### 8.1 遵循現有模式

當創建新功能時：
1. 在 `services/api.js` 中添加 API 函數（如果需要）
2. 創建自定義 Hook（如 `useFeatureName`）
3. 在 Hook 中使用 `useApiCache` 或 `useApiMutation`
4. 在組件中使用 Hook，不直接調用 API

### 8.2 使用組件庫

```javascript
import { Skeleton, EmptyState, EmptyStatePresets } from '../../components/shared';

// Loading 狀態
<Skeleton.PageLoader text="Loading..." />

// 空狀態
<EmptyStatePresets.NoData />

// 錯誤狀態
<EmptyStatePresets.LoadError message={error.message} />
```

### 8.3 使用現有常量和工具

```javascript
import { IS_DEV, CONFIG } from '../config';
import { cachePresets } from '../hooks/useApiCache';
import { getAuthHeaders, isAdmin } from '../utils/auth';
import { protectedFetch } from '../utils/requestProtection';
```

### 8.4 錯誤處理模板

```javascript
try {
    const response = await api.someMethod(params);
    return response.data;
} catch (err) {
    const errorMsg = err.response?.data?.detail || err.message || 'Operation failed';
    console.error('Error details:', err);
    throw new Error(errorMsg);
}
```

### 8.5 命名約定

- API 函數：`getSomething`, `createSomething`, `updateSomething`, `deleteSomething`
- Hooks：`useFeatureName`（駝峰命名）
- 文件命名：`FeaturePage/index.jsx`, `hooks/useFeature.js`
- Query Keys：`['feature', id]` 或 `['feature', param1, param2]`

---

## 9. 參考文檔和資源

### 9.1 關鍵文件路徑

- API 客戶端：`/Users/charlie/Dashboard/frontend/src/services/api.js`
- React Query 配置：`/Users/charlie/Dashboard/frontend/src/hooks/useApiCache.js`
- 請求保護：`/Users/charlie/Dashboard/frontend/src/utils/requestProtection.js`
- 認證工具：`/Users/charlie/Dashboard/frontend/src/utils/auth.js`
- 配置文件：`/Users/charlie/Dashboard/frontend/src/config.js`
- ErrorBoundary：`/Users/charlie/Dashboard/frontend/src/components/shared/ErrorBoundary.jsx`
- 入口文件：`/Users/charlie/Dashboard/frontend/src/main.jsx`

### 9.2 外部文檔

- React Query 文檔：https://tanstack.com/query/latest
- Axios 文檔：https://axios-http.com/
- React Router：https://reactrouter.com/

---

**分析完成**

**生成者：** Charlie Analyst Sub-agent

**最後更新：** 2026-02-21
