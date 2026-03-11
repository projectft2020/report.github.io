# Dashboard 狀態管理分析

**分析目標：** 分析 Dashboard 前端的狀態管理方案，為設計 programmer sub-agent 提供完整的狀態管理知識。

**分析日期：** 2026-02-21

**Dashboard 前端路徑：** `/Users/charlie/Dashboard/`

**分析狀態：** 已完成 ✅

---

## 1. 狀態管理技術棧

### 1.1 核心狀態管理方案

| 技術棧 | 版本 | 用途 | 狀態類型 |
|--------|------|------|----------|
| **Zustand** | ^5.0.9 | 全局應用狀態管理 | 客戶端狀態 |
| **React Query (@tanstack/react-query)** | ^5.90.16 | 服務器狀態管理和 API 緩存 | 服務器狀態 |
| **React Context API** | 內建 | 組件層級狀態共享 | 客戶端狀態 |
| **React useState/useEffect** | 內建 | 組件本地狀態 | 客戶端狀態 |
| **i18next** | ^25.7.4 | 國際化狀態管理 | 配置狀態 |
| **LocalStorage** | 內建 | 持久化存儲 | 持久化狀態 |

### 1.2 狀態管理哲學

Dashboard 採用**混合狀態管理方案**，遵循以下原則：

1. **Zustand** 用於需要跨組件共享的全局應用狀態（Dashboard 核心數據）
2. **React Query** 用於服務器數據獲取、緩存和同步
3. **Context API** 用於特定功能的狀態共享（如 Persona、Toast）
4. **useState** 用於組件內部的 UI 狀態和表單狀態
5. **LocalStorage** 用於持久化用戶偏好和認證信息

---

## 2. 所有狀態 Store 清單

### 2.1 Zustand Store

**文件路徑：** `/Users/charlie/Dashboard/frontend/src/store.js`

#### State 屬性

| 屬性名稱 | 類型 | 初始值 | 說明 |
|---------|------|--------|------|
| `watchlist` | Array | `[]` | 股票監控清單 |
| `marketMovers` | Object | `{ gainers: [], losers: [], most_active: [] }` | 市場漲跌幅和活躍股票 |
| `heatmapData` | Array | `[]` | 市場熱力圖數據 |
| `sectorHeatmapData` | Array | `[]` | 板塊熱力圖數據 |
| `marketScore` | Object | `{ current: null, history: [] }` | 市場評分（當前和歷史） |
| `stockDetails` | Object | `{}` | 股票詳細信息（Map: symbol → details） |
| `lastUpdated` | Date | `null` | 最後更新時間 |
| `loadingStatus` | String | `'idle'` | 加載狀態：'idle', 'loading', 'success', 'error' |
| `error` | Error | `null` | 錯誤信息 |

#### Actions（方法）

| 方法名稱 | 參數 | 返回值 | 說明 |
|---------|------|--------|------|
| `fetchStage1Overview` | `force=false, targetDate=null, market='US'` | Promise | 獲取關鍵概覽數據（板塊熱力圖、市場評分、監控清單股票） |
| `fetchStage2secondary` | `targetDate=null, market='US'` | Promise | 獲取次要數據（市場漲跌、熱力圖、板塊熱力圖） |
| `refreshDashboardData` | - | void | 強制刷新所有 Dashboard 數據 |

#### 使用示例

```javascript
import { useStore } from '../store';

const DashboardPage = () => {
  const {
    fetchStage1Overview,
    fetchStage2secondary,
    refreshDashboardData,
    loadingStatus,
    lastUpdated,
    marketScore,
    stockDetails
  } = useStore();

  // 使用 ref 避免 useEffect 重新運行
  const fetchStage1Ref = useRef(fetchStage1Overview);
  const fetchStage2Ref = useRef(fetchStage2secondary);

  useEffect(() => {
    fetchStage1Ref.current();
    fetchStage2Ref.current();
  }, []);
};
```

### 2.2 React Query 封裝

**文件路徑：** `/Users/charlie/Dashboard/frontend/src/hooks/useApiCache.js`

#### 類型：`useApiCache(key, fetcher, options)`

統一的 React Query 包裝器，提供以下功能：

- 請求去重（避免重複請求）
- 可配置的緩存（staleTime, gcTime）
- 加載和錯誤狀態
- 自動重試（服務器錯誤最多 2 次）
- 自動重獲（窗口焦點、掛載時 - 可配置）

#### 緩存預設（Cache Presets）

| 預設類型 | staleTime | gcTime | 用途 |
|---------|-----------|--------|------|
| `static` | 60 分鐘 | 24 小時 | 靜態數據（策略類型、配置） |
| `user` | 5 分鐘 | 30 分鐘 | 用戶數據（用戶策略、投資組合） |
| `dynamic` | 30 秒 | 5 分鐘 | 動態數據（市場價格、訊號） |
| `realtime` | 0 | 0 | 實時數據（回測結果） |

#### 類型：`useApiMutation(mutationFn, options)`

用於 POST/PUT/DELETE 操作，自動使相關查詢失效。

#### 類型：`cacheUtils`

手動緩存管理工具集：

```javascript
// 使查詢失效
cacheUtils.invalidate(['allocation', '6040']);

// 清空所有緩存
cacheUtils.clear();

// 預取數據
await cacheUtils.prefetch(['strategies'], fetchStrategies);

// 獲取緩存數據
const data = cacheUtils.getData(['allocation', '6040']);

// 設置緩存數據
cacheUtils.setData(['allocation', '6040'], newData);
```

### 2.3 Context Stores

#### PersonaContext

**文件路徑：** `/Users/charlie/Dashboard/frontend/src/contexts/PersonaContext.jsx`

**用途：** 管理 Persona（用戶角色/人設）相關狀態和 UI 自定義

**狀態：**

| 屬性 | 類型 | 說明 |
|------|------|------|
| `personas` | Array | 可用的 Persona 列表 |
| `currentPersona` | String | 當前 Persona ID |
| `preferences` | Object | 當前 Persona 的 UI 偏好 |
| `loading` | Boolean | 加載狀態 |
| `error` | Error | 錯誤信息 |
| `showSelectionModal` | Boolean | 是否顯示 Persona 選擇模態框 |

**方法：**

| 方法 | 說明 |
|------|------|
| `selectPersona(personaId)` | 選擇 Persona |
| `getRecommendation(userData)` | 獲取 Persona 推薦 |
| `shouldShowFeature(featureName)` | 檢查是否應顯示某功能 |
| `getDefaultMetrics()` | 獲取默認指標 |
| `getChartComplexity()` | 獲取圖表複雜度 |
| `getPreference(key, defaultValue)` | 獲取偏好值 |
| `dismissSelectionModal()` | 關閉選擇模態框 |

**使用示例：**

```javascript
import { usePersona } from '../contexts/PersonaContext';

const MyComponent = () => {
  const {
    currentPersona,
    preferences,
    shouldShowFeature,
    getDefaultMetrics
  } = usePersona();

  // 根據 Persona 顯示不同內容
  if (shouldShowFeature('advanced_analytics')) {
    // 顯示高級分析功能
  }
};
```

#### ToastContext

**文件路徑：** `/Users/charlie/Dashboard/frontend/src/components/shared/Toast.jsx`

**用途：** Toast 通知系統

**狀態：** `toasts` - Toast 數組

**方法：**

| 方法 | 說明 |
|------|------|
| `toast(message, type, duration)` | 顯示 Toast |
| `success(message, duration)` | 顯示成功 Toast |
| `error(message, duration)` | 顯示錯誤 Toast |
| `warning(message, duration)` | 顯示警告 Toast |
| `info(message, duration)` | 顯示信息 Toast |
| `removeToast(id)` | 移除 Toast |

**使用示例：**

```javascript
import { useToast } from '../components/shared';

const MyComponent = () => {
  const { success, error } = useToast();

  const handleSave = async () => {
    try {
      await saveData();
      success('保存成功！');
    } catch (err) {
      error('保存失敗：' + err.message);
    }
  };
};
```

### 2.4 LocalStorage 狀態

#### 認證狀態

**文件路徑：** `/Users/charlie/Dashboard/frontend/src/utils/auth.js`

**存儲項：**

| 鍵名 | 類型 | 說明 |
|------|------|------|
| `user_token` | String | VIP 用戶令牌（新系統） |
| `user_role` | String | 用戶角色：'admin', 'vip', 'free' |
| `admin_token` | String | 管理員令牌（舊系統，兼容） |

**工具函數：**

| 函數 | 說明 |
|------|------|
| `getUserRole()` | 獲取當前用戶角色 |
| `getUserToken()` | 獲取當前令牌 |
| `getAuthMethod()` | 獲取認證方法 |
| `authenticateUser(code)` | 驗證用戶存取碼 |
| `validateToken()` | 驗證令牌有效性 |
| `logout()` | 登出 |
| `isAdmin()` | 檢查是否為管理員 |
| `isVIP()` | 檢查是否為 VIP |
| `isFreeUser()` | 檢查是否為免費用戶 |
| `shouldShowPaywall()` | 是否應顯示付費牆 |
| `getAuthHeaders()` | 獲取認證請求頭 |

#### 用戶偏好

| 鍵名 | 類型 | 說明 |
|------|------|------|
| `marketScanner_market` | String | Market Scanner 選擇的市場 |
| `marketScanner_signalMode` | String | Market Scanner 信號模式 |
| `persona_selection_seen_{userId}` | String | 是否已看過 Persona 選擇 |

### 2.5 i18n 狀態

**文件路徑：** `/Users/charlie/Dashboard/frontend/src/i18n.js`

**支持語言：** `en`, `zh-TW`

**語言檢測順序：** `localStorage` → `navigator`

**使用示例：**

```javascript
import { useTranslation } from 'react-i18next';

const MyComponent = () => {
  const { t } = useTranslation();
  return <h1>{t('dashboard.market_pulse')}</h1>;
};
```

---

## 3. 狀態流動和數據流圖

### 3.1 全局狀態流動圖

```
┌─────────────────────────────────────────────────────────────┐
│                         應用入口                             │
│                      (main.jsx)                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ├─────────────────────────────────────┐
                     │                                     │
                     ▼                                     ▼
┌──────────────────────────────┐           ┌──────────────────────────────┐
│   QueryClientProvider         │           │   PersonaProvider            │
│   (React Query 配置)          │           │   (Persona 狀態)            │
│                              │           │                              │
│   - staleTime: Dev=0,        │           │   - personas                 │
│     Prod=2min                 │           │   - currentPersona          │
│   - gcTime: Dev=0,            │           │   - preferences              │
│     Prod=5min                 │           │   - showSelectionModal       │
│   - refetchOnWindowFocus      │           │                              │
│     (僅生產環境啟用)          │           │                              │
└──────────────────────────────┘           └──────────────────────────────┘
                     │
                     ▼
┌───────────────────────────────────────────────────────────────┐
│                         ToastProvider                         │
│                    (Toast 通知系統)                           │
└───────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌───────────────────────────────────────────────────────────────┐
│                            App                                │
└───────────────────────────────────────────────────────────────┘
```

### 3.2 數據流動模式

#### 模式 1：服務器狀態（使用 React Query）

```
┌─────────────┐    ┌──────────────┐    ┌────────────────┐    ┌──────────────┐
│   組件      │───▶│ useApiCache  │───▶│   React Query │───▶│  API Client  │
│             │    │ (自定義 hook)│    │   (緩存層)    │    │   (axios)    │
└─────────────┘    └──────────────┘    └────────────────┘    └──────────────┘
       ▲                                                                  │
       │                                                                  ▼
       │                                                          ┌──────────────┐
       │                                                          │  Backend API │
       └──────────────────────────────────────────────────────────┤              │
                                                                  │  (FastAPI)   │
                                                                  └──────────────┘
```

**流程說明：**

1. 組件調用 `useApiCache(key, fetcher, options)`
2. `useApiCache` 檢查 React Query 緩存中是否有數據且未過期
3. 如果數據存在且新鮮，返回緩存數據
4. 如果數據不存在或過期，調用 `fetcher` 函數
5. `fetcher` 使用 `apiClient`（axios）發送請求
6. Backend API 返回數據
7. React Query 緩存數據並返回給組件
8. 組件重新渲染使用新數據

#### 模式 2：Zustand Store 狀態

```
┌─────────────┐    ┌──────────────┐    ┌────────────────┐    ┌──────────────┐
│   組件      │───▶│  useStore()  │───▶│   Zustand     │───▶│  API Client  │
│ (Dashboard) │    │              │    │    Store      │    │   (axios)    │
└─────────────┘    └──────────────┘    └────────────────┘    └──────────────┘
       ▲                  │                                        │
       │                  │                                        ▼
       │                  │                                  ┌──────────────┐
       │                  │                                  │  Backend API │
       │                  │                                  └──────────────┘
       └──────────────────┘
```

**流程說明：**

1. 組件調用 `useStore()` 獲取狀態和 actions
2. 組件調用 action（如 `fetchStage1Overview()`）
3. Zustand store action 使用 `apiClient` 發送 API 請求
4. Backend API 返回數據
5. Zustand store 使用 `set()` 更新狀態
6. 所有訂閱該 store 的組件自動重新渲染

#### 模式 3：本地組件狀態（useState）

```
┌─────────────┐
│   組件      │
│             │◀───────────────┐
│             │                │
│ - useState  │                │
│ - useEffect │                │
└─────────────┘                │
        │                      │
        ▼                      │
┌─────────────┐               │
│ LocalStorage│ (持久化)       │
└─────────────┘               │
        │                      │
        └──────────────────────┘
```

**流程說明：**

1. 組件使用 `useState` 管理本地 UI 狀態
2. 使用 `useEffect` 從 LocalStorage 讀取初始值
3. 狀態變化時寫入 LocalStorage（持久化）
4. 組件卸載時狀態丟失（除非持久化）

### 3.3 典型頁面的狀態架構示例

#### 示例：AllocationPage

```
AllocationPage (容器組件)
    │
    ├─ useAllocation (自定義 Hook)
    │   │
    │   ├─ useState: selectedStrategy, years, rebalanceFreq, saving
    │   │
    │   └─ useApiCache(['allocation', ...], fetchAllocationData)
    │       └─ React Query 緩存分配策略數據
    │
    ├─ useState: rollingPeriod, activeBenchmarks
    │
    ├─ useBenchmarkDatasets, useReturnChartData, useDrawdownChartData, useRollingChartData
    │   └─ 圖表數據準備
    │
    └─ 子組件渲染
        ├─ StrategySelector (顯示策略選擇器)
        ├─ AssetOverview (顯示資產概覽)
        ├─ HoldingsTable (顯示持倉表格)
        ├─ RebalanceHistory (顯示再平衡歷史)
        ├─ HistoricalMatches (顯示歷史匹配)
        ├─ BenchmarkToggle (基準切換)
        ├─ MonthlyReturnsBarChart (月度回報柱狀圖)
        └─ MonthlyReturnsTable (月度回報表格)
```

---

## 4. React Query 配置和使用

### 4.1 全局配置

**文件路徑：** `/Users/charlie/Dashboard/frontend/src/main.jsx`

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

// 導出 queryClient 供緩存工具使用
window.__queryClient = queryClient;
```

### 4.2 環境相關配置

**文件路徑：** `/Users/charlie/Dashboard/frontend/src/config.js`

| 配置項 | 開發環境 | 生產環境 | 說明 |
|--------|----------|----------|------|
| `staleTime` | 0 | 2 分鐘 | 數據保持新鮮的時間 |
| `gcTime` | 0 | 5 分鐘 | 緩存保留時間 |
| `refetchOnWindowFocus` | false | true | 窗口聚焦時重新獲取 |
| `refetchOnMount` | false | false | 組件掛載時重新獲取 |
| `enableAutoRefresh` | false | false | 自動刷新（未啟用） |

**配置哲學：**

- **開發環境：** 禁用緩存，確保測試最新代碼，依賴 HMR 熱更新
- **生產環境：** 啟用短期緩存，平衡數據新鮮度和性能

### 4.3 預設配置（useApiCache）

```javascript
const cachePresets = {
    static: {
        staleTime: 60 * 60 * 1000,      // 1 小時
        gcTime: 24 * 60 * 60 * 1000,     // 24 小時
    },
    user: {
        staleTime: 5 * 60 * 1000,        // 5 分鐘
        gcTime: 30 * 60 * 1000,          // 30 分鐘
    },
    dynamic: {
        staleTime: 30 * 1000,            // 30 秒
        gcTime: 5 * 60 * 1000,           // 5 分鐘
    },
    realtime: {
        staleTime: 0,
        gcTime: 0,
    },
};
```

### 4.4 重試策略

```javascript
retry: (failureCount, error) => {
    // 不重試客戶端錯誤 (4xx)
    if (error?.response?.status >= 400 && error?.response?.status < 500) {
        return false;
    }
    // 不重試速率限制 (429)
    if (error?.response?.status === 429) {
        return false;
    }
    // 服務器錯誤最多重試 2 次
    return failureCount < 2;
}
```

### 4.5 使用示例

#### 基本使用

```javascript
import { useApiCache } from '../hooks/useApiCache';

const MyComponent = () => {
  const { data, isLoading, error, refetch } = useApiCache(
    'strategies',
    () => apiClient.get('/strategies').then(r => r.data)
  );

  if (isLoading) return <Loading />;
  if (error) return <Error message={error.message} />;

  return <StrategyList strategies={data} />;
};
```

#### 帶參數的使用

```javascript
import { useApiCache } from '../hooks/useApiCache';

const MyComponent = ({ strategyId, years }) => {
  const { data, isLoading, error } = useApiCache(
    ['allocation', strategyId, years],
    () => apiClient.get(`/allocation/${strategyId}`, { params: { years } }),
    {
      staleTime: 2 * 60 * 1000,  // 自定義 2 分鐘
      gcTime: 10 * 60 * 1000,    // 自定義 10 分鐘
    }
  );

  // ...
};
```

#### 使用預設配置

```javascript
import { useApiCache, cachePresets } from '../hooks/useApiCache';

const MyComponent = () => {
  const { data } = useApiCache(
    'strategy-types',
    fetchStrategyTypes,
    cachePresets.static  // 使用靜態數據預設
  );

  // ...
};
```

#### Mutation 使用

```javascript
import { useApiMutation } from '../hooks/useApiCache';

const MyComponent = () => {
  const { mutate, isLoading, error } = useApiMutation(
    (data) => apiClient.post('/strategies', data),
    {
      invalidateKeys: ['strategies'],  // 成功後使相關查詢失效
      onSuccess: () => {
        console.log('Strategy created');
      },
    }
  );

  const handleCreate = () => {
    mutate({ name: 'My Strategy', ... });
  };

  return <button onClick={handleCreate}>Create Strategy</button>;
};
```

#### 手動緩存管理

```javascript
import { cacheUtils } from '../hooks/useApiCache';

const MyComponent = () => {
  const refreshData = () => {
    // 使特定查詢失效並重新獲取
    cacheUtils.invalidate(['allocation', '6040']);
  };

  const clearAllCache = () => {
    // 清空所有緩存
    cacheUtils.clear();
  };

  const prefetchNextPage = () => {
    // 預取下一頁數據
    cacheUtils.prefetch(
      ['strategies', 2],
      () => apiClient.get('/strategies?page=2')
    );
  };

  // ...
};
```

---

## 5. 狀態管理最佳實踐

### 5.1 狀態分類原則

| 狀態類型 | 推荐方案 | 理由 |
|---------|----------|------|
| **全局應用狀態** | Zustand | 需要跨多個組件共享，如 Dashboard 核心數據 |
| **服務器狀態** | React Query | 需要從 API 獲取，需要緩存和同步 |
| **功能特定狀態** | Context | 特定功能的狀態共享，如 Persona、Toast |
| **表單/UI 狀態** | useState | 組件內部狀態，不需要共享 |
| **持久化狀態** | LocalStorage | 需要跨會話保存，如用戶偏好、認證信息 |
| **路由狀態** | URL Params | 需要可分享、可書籤的狀態 |

### 5.2 Zustand 最佳實踐

#### ✅ DO（應該做）

1. **保持 store 扁平化**
   ```javascript
   // ✅ 好的做法：扁平化結構
   export const useStore = create((set) => ({
     marketScore: { current: null, history: [] },
     stockDetails: {},
     loadingStatus: 'idle',
   }));

   // ❌ 不好的做法：過度嵌套
   export const useStore = create((set) => ({
     data: {
       market: {
         score: {
           current: null,
           history: []
         }
       }
     },
   }));
   ```

2. **使用 refs 避免 useEffect 重新運行**
   ```javascript
   // ✅ 好的做法：使用 ref
   const { fetchStage1Overview } = useStore();
   const fetchStage1Ref = useRef(fetchStage1Overview);

   useEffect(() => {
     fetchStage1Ref.current();
   }, []);

   // ❌ 不好的做法：直接使用會導致重新運行
   const { fetchStage1Overview } = useStore();

   useEffect(() => {
     fetchStage1Overview();  // 每次狀態更新都會運行
   }, [fetchStage1Overview]);
   ```

3. **批量更新狀態**
   ```javascript
   // ✅ 好的做法：使用函數式更新批量更新
   set((state) => ({
     ...state,
     sectorHeatmapData: newData,
     marketScore: newScore,
     loadingStatus: 'success',
   }));
   ```

4. **分離關注點**
   ```javascript
   // ✅ 好的做法：按功能域分離
   export const useMarketStore = create((set) => ({
     // 市場相關狀態
   }));

   export const useUserStore = create((set) => ({
     // 用戶相關狀態
   }));
   ```

#### ❌ DON'T（不應該做）

1. **不要在 store 中直接調用副作用**
   ```javascript
   // ❌ 不好的做法：在 store 中直接導航
   export const useStore = create((set, get) => ({
     saveAndNavigate: () => {
       set({ saved: true });
       navigate('/home');  // ❌ 不應該在 store 中導航
     },
   }));

   // ✅ 好的做法：在組件中處理導航
   export const useStore = create((set) => ({
     save: () => set({ saved: true }),
   }));

   // 在組件中
   const { save } = useStore();
   const handleSave = () => {
     save();
     navigate('/home');
   };
   ```

2. **不要在 store 中存儲大型數據而不考慮性能**
   ```javascript
   // ❌ 不好的做法：存儲所有歷史數據
   export const useStore = create((set) => ({
     allHistoryData: [],  // 可能有數千條記錄
   }));

   // ✅ 好的做法：使用 React Query 緩存，按需加載
   const { data } = useApiCache(['history', id], fetchHistory);
   ```

### 5.3 React Query 最佳實踐

#### ✅ DO（應該做）

1. **使用語義化的查詢鍵**
   ```javascript
   // ✅ 好的做法：語義化查詢鍵
   const { data } = useApiCache(
     ['allocation', strategyId, years, rebalanceFreq],
     fetchAllocationData
   );

   // ❌ 不好的做法：非語義化查詢鍵
   const { data } = useApiCache(
     'allocation-data-123',
     fetchAllocationData
   );
   ```

2. **根據數據類型選擇合適的預設**
   ```javascript
   // ✅ 好的做法：使用預設配置
   const { data: strategies } = useApiCache(
     'strategies',
     fetchStrategies,
     cachePresets.static  // 策略類型很少變化
   );

   const { data: signals } = useApiCache(
     ['signals', date],
     fetchSignals,
     cachePresets.dynamic  // 訊號經常變化
   );
   ```

3. **使用 invalidateKeys 自動刷新相關數據**
   ```javascript
   // ✅ 好的做法：mutation 後使相關查詢失效
   const { mutate } = useApiMutation(
     (data) => apiClient.post('/strategies', data),
     {
       invalidateKeys: [
         'strategies',
         ['allocation', '6040'],
         ['allocation', 'all-weather']
       ],
     }
   );
   ```

4. **使用 refetch 手動刷新**
   ```javascript
   // ✅ 好的做法：提供手動刷新按鈕
   const { data, isLoading, refetch } = useApiCache(
     'market-score',
     fetchMarketScore
   );

   return (
     <div>
       <button onClick={refetch} disabled={isLoading}>
         Refresh
       </button>
       {/* ... */}
     </div>
   );
   ```

#### ❌ DON'T（不應該做）

1. **不要在查詢鍵中使用不可序列化的值**
   ```javascript
   // ❌ 不好的做法：使用函數或對象作為查詢鍵
   const { data } = useApiCache(
     ['strategies', () => fetch],  // ❌ 函數不可序列化
     fetchStrategies
   );

   // ✅ 好的做法：使用可序列化的值
   const { data } = useApiCache(
     ['strategies', 'all'],
     fetchStrategies
   );
   ```

2. **不要過度依賴自動重獲**
   ```javascript
   // ❌ 不好的做法：依賴 refetchOnWindowFocus 導致過度請求
   const queryClient = new QueryClient({
     defaultOptions: {
       queries: {
         refetchOnWindowFocus: 'always',  // ❌ 可能導致過度請求
       },
     },
   });

   // ✅ 好的做法：僅在生產環境啟用
   const queryClient = new QueryClient({
     defaultOptions: {
       queries: {
         refetchOnWindowFocus: !IS_DEV,
       },
     },
   });
   ```

### 5.4 Context API 最佳實踐

#### ✅ DO（應該做）

1. **只在需要時使用 Context**
   ```javascript
   // ✅ 好的做法：Persona 需要多層組件共享
   export const PersonaProvider = ({ children }) => {
     // Persona 相關狀態
     return (
       <PersonaContext.Provider value={value}>
         {children}
       </PersonaContext.Provider>
     );
   };

   // ❌ 不好的做法：簡單的表單狀態不需要 Context
   export const FormProvider = ({ children }) => {
     // ❌ 應該使用 useState 在組件內部
   };
   ```

2. **將狀態和操作分離**
   ```javascript
   // ✅ 好的做法：提供自定義 hooks
   export const usePersona = () => {
     const context = useContext(PersonaContext);
     if (!context) {
       throw new Error('usePersona must be used within PersonaProvider');
     }
     return context;
   };

   export const usePersonaPreferences = () => {
     const { preferences } = usePersona();
     return preferences || DEFAULT_PREFERENCES;
   };
   ```

3. **使用 TypeScript 類型檢查（如果使用 TS）**
   ```javascript
   // ✅ 好的做法：定義類型
   interface PersonaContextType {
     personas: Persona[];
     currentPersona: string | null;
     preferences: PersonaPreferences | null;
     // ...
   }
   ```

### 5.5 LocalStorage 最佳實踐

#### ✅ DO（應該做）

1. **提供默認值**
   ```javascript
   // ✅ 好的做法：提供默認值
   const getInitialMarket = () => {
     const saved = localStorage.getItem('marketScanner_market');
     return saved || 'TW';  // 默認值
   };
   ```

2. **處理解析錯誤**
   ```javascript
   // ✅ 好的做法：錯誤處理
   const getStoredPreferences = () => {
     try {
       const stored = localStorage.getItem('preferences');
       return stored ? JSON.parse(stored) : DEFAULT_PREFERENCES;
     } catch (e) {
       console.error('Failed to parse preferences:', e);
       return DEFAULT_PREFERENCES;  // 回退到默認值
     }
   };
   ```

3. **統一管理 LocalStorage 鍵**
   ```javascript
   // ✅ 好的做法：使用常量定義鍵名
   export const STORAGE_KEYS = {
     MARKET: 'marketScanner_market',
     SIGNAL_MODE: 'marketScanner_signalMode',
     USER_ROLE: 'user_role',
     USER_TOKEN: 'user_token',
   };
   ```

#### ❌ DON'T（不應該做）

1. **不要在 LocalStorage 中存儲敏感信息（如果可能）**
   ```javascript
   // ❌ 不好的做法：存儲明文密碼
   localStorage.setItem('password', 'myPassword');

   // ✅ 好的做法：僅存儲令牌
   localStorage.setItem('user_token', token);
   ```

2. **不要存儲過大的數據**
   ```javascript
   // ❌ 不好的做法：存儲所有歷史數據
   localStorage.setItem('allHistory', JSON.stringify(hugeArray));

   // ✅ 好的做法：存儲關鍵偏好
   localStorage.setItem('market', 'TW');
   localStorage.setItem('language', 'zh-TW');
   ```

### 5.6 性能優化最佳實踐

#### 1. 使用 React.memo 和 useMemo

```javascript
// ✅ 好的做法：避免不必要的重新渲染
const MemoizedComponent = React.memo(({ data }) => {
  return <div>{data.value}</div>;
});

// ✅ 好的做法：使用 useMemo 緩存計算結果
const sortedData = useMemo(
  () => data.sort((a, b) => a.name.localeCompare(b.name)),
  [data]
);
```

#### 2. 使用 useCallback 穩定引用

```javascript
// ✅ 好的做法：使用 useCallback 穩定回調函數
const handleSave = useCallback(async () => {
  await saveData(data);
}, [data]);

// 傳遞給子組件
<ChildComponent onSave={handleSave} />
```

#### 3. 使用 Code Splitting（路由級延遲加載）

```javascript
// ✅ 好的做法：使用 React.lazy 延遲加載
const MarketScanner = React.lazy(() => import('./pages/market-scanner'));
const SignalDashboardPage = React.lazy(() => import('./pages/SignalDashboardPage'));

// 在路由中使用
<Suspense fallback={<Skeleton.PageLoader text="Loading..." />}>
  <Routes>
    <Route path="/" element={<MarketScanner />} />
    <Route path="/signals" element={<SignalDashboardPage />} />
  </Routes>
</Suspense>
```

#### 4. 防抖和節流

```javascript
// ✅ 好的做法：對頻繁觸發的操作使用防抖
const [searchTerm, setSearchTerm] = useState('');

const debouncedSearch = useMemo(
  () => debounce((term) => {
    // 搜索邏輯
  }, 500),
  []
);

useEffect(() => {
  debouncedSearch(searchTerm);
}, [searchTerm, debouncedSearch]);
```

### 5.7 測試最佳實踐

#### 1. 測試 Zustand Store

```javascript
// ✅ 好的做法：測試 store 的行為
import { renderHook, act } from '@testing-library/react';
import { useStore } from '../store';

test('fetchStage1Overview updates state correctly', async () => {
  const { result } = renderHook(() => useStore());

  expect(result.current.loadingStatus).toBe('idle');

  await act(async () => {
    await result.current.fetchStage1Overview();
  });

  expect(result.current.loadingStatus).toBe('success');
  expect(result.current.marketScore).toBeDefined();
});
```

#### 2. 測試 React Query Hooks

```javascript
// ✅ 好的做法：測試 useApiCache
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useApiCache } from '../hooks/useApiCache';

const wrapper = ({ children }) => (
  <QueryClientProvider client={queryClient}>
    {children}
  </QueryClientProvider>
);

test('useApiCache fetches data correctly', async () => {
  const { result } = renderHook(
    () => useApiCache('test', () => Promise.resolve({ data: 'test' })),
    { wrapper }
  );

  await waitFor(() => expect(result.current.isSuccess).toBe(true));
  expect(result.current.data).toEqual({ data: 'test' });
});
```

#### 3. 測試 Context

```javascript
// ✅ 好的做法：測試 Context Provider
import { render } from '@testing-library/react';
import { PersonaProvider, usePersona } from '../contexts/PersonaContext';

test('PersonaProvider provides correct values', () => {
  const TestComponent = () => {
    const { currentPersona } = usePersona();
    return <div>{currentPersona}</div>;
  };

  render(
    <PersonaProvider>
      <TestComponent />
    </PersonaProvider>
  );

  // 測試默認值或初始化行為
});
```

---

## 6. 總結

### 6.1 狀態管理架構概覽

Dashboard 前端採用**混合狀態管理方案**，根據不同類型的狀態選擇最合適的技術：

1. **Zustand** - 全局應用狀態（Dashboard 核心數據）
2. **React Query** - 服務器狀態（API 數據緩存和同步）
3. **Context API** - 功能特定狀態（Persona、Toast）
4. **useState** - 組件本地狀態（UI、表單）
5. **LocalStorage** - 持久化狀態（用戶偏好、認證）

### 6.2 關鍵設計模式

1. **分層狀態管理** - 按狀態類型選擇合適的方案
2. **自定義 Hooks 封裝** - 如 `useAllocation`, `useMomentum`, `useApiCache`
3. **環境感知配置** - 開發/生產環境不同的緩存策略
4. **手動優化重新渲染** - 使用 refs 避免不必要的 useEffect 重新運行
5. **語義化查詢鍵** - React Query 查詢鍵結構化且有意義

### 6.3 性能特點

- **開發環境**：禁用緩存，確保測試最新代碼
- **生產環境**：短期緩存（2 分鐘），平衡新鮒度和性能
- **懶加載**：使用 React.lazy 延遲加載頁面組件
- **請求去重**：React Query 自動去重相同請求
- **智能重試**：服務器錯誤重試最多 2 次，客戶端錯誤不重試

### 6.4 可擴展性

- **新增狀態 store**：在 `store.js` 中添加新的 Zustand store
- **新增 Context**：在 `contexts/` 目錄中創建新的 Context
- **新增 API 緩存**：使用 `useApiCache` 包裝新的 API 調用
- **新增持久化狀態**：使用 LocalStorage 並提供工具函數

---

## 附錄：關鍵文件索引

| 文件路徑 | 用途 |
|---------|------|
| `/Users/charlie/Dashboard/frontend/src/store.js` | Zustand 全局 store |
| `/Users/charlie/Dashboard/frontend/src/hooks/useApiCache.js` | React Query 封裝 |
| `/Users/charlie/Dashboard/frontend/src/contexts/PersonaContext.jsx` | Persona Context |
| `/Users/charlie/Dashboard/frontend/src/components/shared/Toast.jsx` | Toast Context |
| `/Users/charlie/Dashboard/frontend/src/main.jsx` | React Query 全局配置 |
| `/Users/charlie/Dashboard/frontend/src/config.js` | 環境配置 |
| `/Users/charlie/Dashboard/frontend/src/utils/auth.js` | 認證工具 |
| `/Users/charlie/Dashboard/frontend/src/services/api.js` | API 客戶端 |
| `/Users/charlie/Dashboard/frontend/src/i18n.js` | 國際化配置 |
| `/Users/charlie/Dashboard/frontend/src/pages/AllocationPage/hooks/useAllocation.js` | 頁面狀態管理示例 |
| `/Users/charlie/Dashboard/frontend/src/pages/MomentumPage/hooks/useMomentum.js` | 頁面狀態管理示例 |

---

**分析完成時間：** 2026-02-21

**分析人員：** Charlie Analyst Sub-Agent

**分析質量：** 完整覆蓋狀態管理技術棧、所有 store 清單、數據流動、React Query 配置和最佳實踐
