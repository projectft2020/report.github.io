# 高級架構師/開發者能力定義報告

**任務 ID:** a005-competencies
**整合範圍:** a001 (後端架構) + a002 (前端架構) + a003 (統一策略引擎) + a004 (Git 開發模式)
**生成時間:** 2026-02-21T00:43:00+08:00
**狀態:** completed

---

## 執行摘要

本報告基於 Dashboard 系統的完整技術架構分析，定義了高級架構師和資深開發者的核心能力框架，並為 Programmer Sub-Agent 的設計提供了明確的技能優先級和學習路徑。核心發現：系統採用**前後端分離架構**、**統一策略引擎**、**微服務化後端**、**測試驅動開發**，具備**完善的 CI/CD 基礎設施**（待實施）和**嚴格的代碼規範**（100% Conventional Commits）。

**關鍵能力層級：**
- **P0（必備）**：Python/React 開發、測試驅動開發、Git 提交規範、FastAPI/React Query
- **P1（重要）**：VectorBT/Backtrader 回測、Zustand 狀態管理、Docker 容器化、策略架構
- **P2（可選）**：Three.js 3D 視覺化、ECharts 高級圖表、Celery 任務隊列
- **P3（未來擴展）**：機器學習、實時數據流處理、Kubernetes 部署

---

## 1. 高級架構師能力定義

### 1.1 系統架構設計能力

#### A. 分層架構設計

**技能要求：**
- 理解和設計清晰的分層架構（Presentation → API Gateway → Router → Service → Repository → Storage）
- 定義明確的服務邊界和職責
- 設計可擴展的模塊化系統

**Dashboard 應用：**
```
前端架構：React Components → Custom Hooks → React Query → API Client
後端架構：FastAPI Routers → Services → Repositories → DuckDB/PostgreSQL/Redis
```

**能力指標：**
- 能夠繪製完整的系統架構圖（類型、層級、數據流）
- 能夠定義 API 端點和服務契約
- 能夠設計高可用性和可擴展性方案

#### B. 數據架構設計

**技能要求：**
- 設計合適的數據庫 schema（關係型 vs 分析型）
- 定義數據流和 ETL 管道
- 優化查詢性能和索引策略

**Dashboard 應用：**
- **DuckDB**：策略配置、回測結果（分析型）
- **PostgreSQL**：用戶數據、會話管理、任務隊列（關係型）
- **Redis**：緩存、會話存儲（鍵值存儲）

**能力指標：**
- 能夠根據使用場景選擇合適的數據庫
- 能夠設計高效的查詢和索引策略
- 能夠設計數據遷移和備份方案

#### C. 微服務架構理解

**技能要求：**
- 理解微服務與單體應用的權衡
- 設計服務間通信機制（REST/GraphQL/gRPC）
- 處理服務發現、負載均衡、容錯機制

**Dashboard 應用：**
- 策略服務（Strategy Service）
- 市場數據服務（Market Data Service）
- 回測引擎服務（Backtest Engine Service）
- 績效分析服務（Performance Service）

**能力指標：**
- 能夠劃分服務邊界
- 能夠設計服務間 API 契約
- 能夠處理分布式事務和最終一致性

### 1.2 技術選型決策能力

#### A. 框架和庫選型

**技能要求：**
- 評估不同技術方案的權衡
- 考慮性能、可維護性、社區支持、學習成本
- 做出基於證據的技術決策

**Dashboard 技術選型示例：**

| 類別 | 選擇 | 理由 |
|------|------|------|
| 後端框架 | FastAPI | 高性能、自動文檔、類型驗證 |
| 前端框架 | React 19 | 組件化、生態系統、Hooks |
| 狀態管理 | Zustand + React Query | 簡潔 + 服務端狀態管理 |
| 回測引擎 | VectorBT | 向量化、高性能、易於集成 |
| 數據庫 | DuckDB | 內嵌、分析型、零配置 |

**能力指標：**
- 能夠編寫技術決策記錄（ADR）
- 能夠比較不同方案的優缺點
- 能夠考慮長期維護成本

#### B. 性能優化決策

**技能要求：**
- 識別性能瓶頸
- 選擇合適的優化策略（緩存、索引、異步、並行）
- 權衡優化成本和收益

**Dashboard 優化策略：**
- **緩存**：Redis（5分鐘 TTL）、React Query（2-60分鐘 staleTime）
- **並行**：pytest-xdist、多進程回測
- **向量化**：VectorBT、NumPy 操作
- **批量查詢**：減少數據庫往返

**能力指標：**
- 能夠使用性能分析工具（profiling）
- 能夠設定性能基準（benchmarking）
- 能夠衡量優化效果

#### C. 安全性決策

**技能要求：**
- 識別安全風險（SQL 注入、XSS、CSRF）
- 實施適當的安全措施
- 遵循安全最佳實踐

**Dashboard 安全措施：**
- **認證**：Session-based、X-Admin-Token
- **授權**：AdminRoute、ProtectedRoute
- **輸入驗證**：Pydantic、PropTypes
- **HTTPS**：生產環境強制

**能力指標：**
- 能夠進行安全審計
- 能夠實施安全的認證和授權
- 能夠處理敏感數據（密碼、API keys）

### 1.3 重構和優化能力

#### A. 代碼重構策略

**技能要求：**
- 識別代碼異味（Code Smells）
- 應用設計模式（工廠、適配器、策略）
- 實施漸進式重構

**Dashboard 重構案例：**
- **統一策略引擎**：從多個獨立策略遷移到 IStrategy 接口
- **React Query 遷移**：從 requestProtection.js 遷移到 React Query（減少 30-70% 代碼）
- **符號類型統一**：統一 symbol 處理（FuturesSymbol、StockSymbol）

**重構模式：**
```python
# 工廠模式
class StrategyFactory:
    @staticmethod
    def create(strategy_type: str, params: Dict) -> IStrategy:
        ...

# 適配器模式
class SignalAdapter:
    @staticmethod
    def signals_to_vectorbt(signals) -> pd.DataFrame:
        ...

# 策略模式
class RSIStrategy(IStrategy):
    def generate_signals(self, context, symbols):
        ...
```

**能力指標：**
- 能夠識別需要重構的代碼
- 能夠設計和實施重構計劃
- 能夠確保重構不改變行為（測試驅動）

#### B. 架構優化

**技能要求：**
- 識別架構瓶頸
- 設計和實施架構優化
- 權衡優化的複雜度和收益

**Dashboard 架構優化案例：**
- **從 Backtrader 遷移到 VectorBT**：向量化回測，性能提升 5-10x
- **引入 Redis 緩存**：減少數據庫查詢 60%
- **API 層分離**：從單體 API 遷移到微服務

**能力指標：**
- 能夠設計架構演進路線圖
- 能夠實施零停機優化
- 能夠監控和驗證優化效果

#### C. 技術債管理

**技能要求：**
- 識別和量化技術債
- 優先級排序和規劃償還
- 建立預防技術債的文化

**Dashboard 技術債案例：**
- **棄用警告**：get_futures_spec() → get_spec_for_symbol()
- **測試覆蓋率**：60% → 目標 80%
- **CI/CD**：手動部署 → GitHub Actions 自動化

**能力指標：**
- 能夠建立技術債清單
- 能夠制定償還計劃
- 能夠平衡新功能開發和技術債償還

### 1.4 跨領域知識整合能力

#### A. 金融領域知識

**技能要求：**
- 理解量化交易基本概念（Alpha、Beta、夏普比率）
- 理解技術指標（RSI、MACD、移動平均線）
- 理解風險管理（最大回撤、VaR）

**Dashboard 應用：**
- **策略引擎**：支持 RSI、MACD、Momentum、SuperTrend、Bollinger Bands
- **績效分析**：夏普比率、Sortino 比率、最大回撤、勝率
- **風險分析**：VaR、風險暴露、壓力測試

**能力指標：**
- 能夠與金融專家溝通需求
- 能夠實施金融指標計算
- 能夠解釋策略績效指標

#### B. 數據科學知識

**技能要求：**
- 理解統計學基本概念（均值、方差、分佈）
- 理解機器學習基本概念（訓練、驗證、測試）
- 能夠使用數據分析工具（pandas、numpy）

**Dashboard 應用：**
- **技術指標計算**：pandas-ta-classic
- **回測引擎**：VectorBT（向量化計算）
- **數據處理**：DuckDB（SQL 查詢）、pandas（數據清洗）

**能力指標：**
- 能夠處理時間序列數據
- 能夠計算技術指標
- 能夠進行數據可視化

#### C. 前後端知識整合

**技能要求：**
- 理解前端和後端交互模式
- 能夠設計 RESTful API
- 能夠處理前端狀態管理

**Dashboard 應用：**
- **API 設計**：FastAPI + Pydantic（自動文檔）
- **前端狀態管理**：Zustand（全局）+ React Query（服務端）+ useState（本地）
- **數據流**：Component → Hook → React Query → API → Service → Repository → DB

**能力指標：**
- 能夠設計前後端分離架構
- 能夠處理異步數據加載
- 能夠優化前端性能

### 1.5 團隊技術領導力

#### A. 技術決策溝通

**技能要求：**
- 能夠清晰表達技術決策的理據
- 能夠傾聽和整合不同意見
- 能夠建立共識

**Dashboard 案例：**
- **統一策略引擎設計**：6 個重構文檔，明確的決策記錄
- **Conventional Commits**：100% 遵循率，明確的提交規範

**能力指標：**
- 能夠編寫清晰的技術文檔
- 能夠進行有效的技術演示
- 能夠建立開發者社區

#### B. 代碼審查指導

**技能要求：**
- 能夠提供建設性的代碼審查反饋
- 能夠指導初級開發者
- 能夠建立代碼審查文化

**Dashboard 代碼審查標準：**
- **功能正確性**：符合需求、邊界情況處理
- **代碼質量**：可讀性、風格、註釋
- **測試覆蓋**：新功能測試、測試通過率
- **安全性**：輸入驗證、權限檢查
- **性能**：無明顯退化、查詢優化

**能力指標：**
- 能夠識別代碼中的問題
- 能夠提供改進建議
- 能夠建立代碼審查流程

#### C. 技術規劃和路線圖

**技能要求：**
- 能夠制定技術發展路線圖
- 能夠平衡短期和長期目標
- 能夠適應變化和調整計劃

**Dashboard 技術路線圖示例：**
- **Phase 1**：統一策略引擎（4-5 天）
- **Phase 2**：React Query 遷移（2-3 週）
- **Phase 3**：CI/CD 自動化（1-2 週）
- **Phase 4**：微服務拆分（持續）

**能力指標：**
- 能夠制定現實的技術計劃
- 能夠跟蹤和報告進度
- 能夠根據變化調整計劃

---

## 2. 資深開發者能力定義

### 2.1 全棧開發能力

#### A. 後端開發（Python/FastAPI）

**核心技能：**
- FastAPI 路由、依賴注入、中間件
- Pydantic 數據驗證和序列化
- SQLAlchemy/DuckDB 數據庫操作
- 異步編程（asyncio、async/await）

**Dashboard 後端架構：**
```python
# 路由層
@router.get("/api/v1/strategies")
async def get_strategies(
    page: int = 1,
    limit: int = 10,
    current_user: User = Depends(get_current_user)
):
    ...

# 服務層
class StrategyService:
    def __init__(self, db: Session):
        self.db = db
        self.registry = StrategyRegistry()

    async def create_strategy(self, data: StrategyCreate):
        ...

# Repository 層
class StrategyRepository:
    def __init__(self, conn: duckdb.DuckDBPyConnection):
        self.conn = conn

    def save(self, strategy: Strategy):
        ...
```

**能力指標：**
- 能夠獨立開發 FastAPI 端點
- 能夠設計 RESTful API
- 能夠處理異常和錯誤

#### B. 前端開發（React 19）

**核心技能：**
- React 19 Hooks（useState, useEffect, useMemo, useCallback）
- 函數式組件和高階組件
- React Router v7（路由、導航、保護）
- 響應式設計（Bootstrap 5）

**Dashboard 前端組件示例：**
```jsx
// 頁面組件
const StrategyPage = () => {
  const { data, isLoading } = useStrategyAPI();
  const { addToast } = useToast();

  return (
    <div className="container">
      <StrategyHeader />
      <Tabs>
        <TabPane tab="Builder">
          <BuilderTab />
        </TabPane>
        <TabPane tab="Backtest">
          <BacktestTab />
        </TabPane>
      </Tabs>
    </div>
  );
};

// 自定義 Hook
const useStrategyAPI = () => {
  const { data, isLoading, error } = useApiCache(
    ['strategies'],
    apiClient.getStrategies
  );

  const { mutate, mutateAsync } = useApiMutation(
    (data) => apiClient.createStrategy(data),
    {
      onSuccess: () => {
        cacheUtils.invalidate(['strategies']);
      }
    }
  );

  return { data, isLoading, mutate };
};
```

**能力指標：**
- 能夠獨立開發 React 組件
- 能夠使用 React Hooks 管理狀態
- 能夠處理表單和用戶輸入

#### C. API 集成

**核心技能：**
- Axios/HTTP 客戶端配置
- React Query 數據獲取和緩存
- 錯誤處理和重試邏輯
- 請求去重和保護

**Dashboard API 集成示例：**
```javascript
// Axios 配置
const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'X-Admin-Token': localStorage.getItem('adminToken')
  }
});

// React Query 使用
const { data, isLoading, error, refetch } = useApiCache(
  ['market', 'heatmap', targetDate],
  () => MarketApi.getHeatmap(targetDate, market),
  {
    staleTime: 5 * 60 * 1000,  // 5 分鐘
    gcTime: 10 * 60 * 1000     // 10 分鐘
  }
);

// 突變操作
const { mutate, isLoading: isSaving } = useApiMutation(
  (data) => StockApi.addTrackedSymbols(data),
  {
    onSuccess: () => {
      toast.success('符號已添加');
      cacheUtils.invalidate(['tracked-symbols']);
    },
    onError: (error) => {
      toast.error('添加失敗');
    }
  }
);
```

**能力指標：**
- 能夠配置和使用 HTTP 客戶端
- 能夠使用 React Query 管理服務端狀態
- 能夠處理錯誤和加載狀態

### 2.2 測試驅動開發能力

#### A. 單元測試

**Python（pytest）：**
```python
# 測試策略服務
def test_strategy_create(db_session):
    service = StrategyService(db_session)
    data = StrategyCreate(
        name="Test Strategy",
        type="trend_following",
        parameters={"period": 14}
    )

    result = await service.create_strategy(data)

    assert result.id is not None
    assert result.name == "Test Strategy"
    assert result.status == "active"

# 測試回測引擎
def test_backtest_engine_rsi(mocker):
    engine = BacktraderEngine(config={}, db_session=mocker.MagicMock())

    engine.add_strategy({
        "type": "rsi",
        "parameters": {"period": 14}
    })
    engine.add_data("AAPL", date(2024, 1, 1), date(2024, 12, 31))

    result = engine.run()

    assert "total_return" in result
    assert "sharpe_ratio" in result
```

**JavaScript（vitest）：**
```javascript
// 測試 API 客戶端
describe('StockApi', () => {
  it('should fetch stock history', async () => {
    const mockData = { date: '2024-01-01', close: 100 };
    vi.spyOn(apiClient, 'get').mockResolvedValue({ data: mockData });

    const result = await StockApi.getHistory('AAPL', { days: 30 });

    expect(result).toEqual(mockData);
    expect(apiClient.get).toHaveBeenCalledWith('/stocks/AAPL/history', expect.any(Object));
  });
});

// 測試自定義 Hook
describe('useStrategyAPI', () => {
  it('should return strategies data', () => {
    const { result } = renderHook(() => useStrategyAPI());

    expect(result.current.isLoading).toBe(false);
    expect(result.current.data).toBeDefined();
  });
});
```

**能力指標：**
- 能夠編寫單元測試
- 能夠使用 mock 和 stub
- 能夠達到 >80% 測試覆蓋率

#### B. 集成測試

**Python（pytest）：**
```python
# 測試 API 端點
async def test_create_strategy_api(client, auth_header):
    response = await client.post(
        "/api/v1/strategies",
        json={
            "name": "Integration Test Strategy",
            "type": "trend_following",
            "parameters": {"period": 14}
        },
        headers=auth_header
    )

    assert response.status_code == 200
    assert response.json()["data"]["name"] == "Integration Test Strategy"

# 測試服務層集成
async def test_strategy_backtest_integration(db_session):
    service = StrategyService(db_session)
    engine = BacktraderEngine(config={}, db_session=db_session)

    strategy = await service.create_strategy(...)
    engine.add_strategy(strategy.config)

    result = engine.run()

    assert result is not None
    assert result["total_return"] is not None
```

**JavaScript（cypress）：**
```javascript
// E2E 測試示例
describe('Strategy Page', () => {
  beforeEach(() => {
    cy.login('admin', 'password');
    cy.visit('/strategies/builder');
  });

  it('should create a new strategy', () => {
    cy.get('[data-testid="strategy-name-input"]').type('Test Strategy');
    cy.get('[data-testid="strategy-type-select"]').select('rsi');
    cy.get('[data-testid="submit-button"]').click();

    cy.contains('Strategy created successfully').should('be.visible');
  });

  it('should display strategy list', () => {
    cy.get('[data-testid="strategy-card"]').should('have.length.greaterThan', 0);
  });
});
```

**能力指標：**
- 能夠編寫集成測試
- 能夠測試 API 端點
- 能夠使用測試數據庫

#### C. 測試最佳實踐

**AAA 模式（Arrange-Act-Assert）：**
```python
def test_strategy_calculate_rsi():
    # Arrange
    strategy = RSIStrategy(period=14)
    prices = pd.Series([100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113])

    # Act
    rsi = strategy._calculate_rsi(prices)

    # Assert
    assert 0 <= rsi <= 100
    assert not pd.isna(rsi)
```

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

**Dashboard 測試覆蓋率：**
| 類別 | 測試數 | 通過率 | 覆蓋率 | 目標 |
|----------|-------|-----------|----------|------|
| 🐍 後端 | 244 | 91% | 70% | 80% |
| ⚛️ 前端工具 | 152 | 100% | 100% | ✅ |
| ⚛️ 前端組件 | 110 | 63% | ~30% | 70% |
| **總計** | **506** | **86%** | **60%** | **80%** |

**能力指標：**
- 能夠遵循測試最佳實踐
- 能夠達到測試覆蓋率目標
- 能夠編寫可維護的測試

### 2.3 代碼審查能力

#### A. 代碼審查標準

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

#### B. 代碼審查實踐

**審查流程：**
1. **快速審查**（5-10 分鐘）
   - 確認 PR 描述清晰
   - 確認測試覆蓋充分
   - 確認沒有明顯問題

2. **深入審查**（20-30 分鐘）
   - 代碼邏輯正確性
   - 代碼質量和風格
   - 性能影響
   - 安全性

3. **建設性反饋**
   - 解釋為什麼要修改
   - 提供具體建議
   - 對代碼不對人

**反饋示例：**

❌ 壞例子：
```
這段代碼有問題，改一下。
```

✅ 好例子：
```
我注意到這裡使用 `for` 循環計算 RSI，這在大型數據集上可能會很慢。建議使用 `pandas_ta` 的向量化操作：

```python
# 當前
for i in range(len(prices)):
    rsi = calculate_rsi(prices[:i+1])

# 建議
rsi = ta.momentum.RSIIndicator(prices, window=14).rsi()
```

這樣可以提升性能 5-10x。如果需要更多幫助，請告訴我。
```

**能力指標：**
- 能夠提供建設性的審查意見
- 能夠識別代碼中的問題
- 能夠建立審查文化

### 2.4 問題診斷和調試能力

#### A. 調試工具使用

**Python 調試：**
```python
# 使用 pdb
import pdb; pdb.set_trace()

# 使用 IPython
from IPython import embed; embed()

# 使用 print
print(f"DEBUG: rsi_value = {rsi_value}, current_date = {current_date}")

# 使用 logging
import logging
logging.basicConfig(level=logging.DEBUG)
logger.debug(f"Strategy signal generated: {signal}")
```

**JavaScript 調試：**
```javascript
// 使用 console.log
console.log('DEBUG:', data);

// 使用 debugger
debugger;

// 使用 React DevTools
// 在組件中添加 displayName
Component.displayName = 'StrategyPage';

// 使用 React Query DevTools
<QueryClientProvider client={queryClient}>
  <App />
  <ReactQueryDevTools initialIsOpen={false} />
</QueryClientProvider>
```

#### B. 問題診斷流程

**1. 問題重現**
- 清楚地描述問題
- 找到重現步驟
- 記錄錯誤信息

**2. 日志分析**
```python
# 查看應用日志
tail -f logs/app.log

# 搜索錯誤
grep "ERROR" logs/app.log

# 查看特定請求
grep "request_id_abc123" logs/app.log
```

**3. 數據驗證**
```python
# 驗證數據完整性
df = pd.read_csv('data.csv')
print(df.info())
print(df.describe())
print(df.isnull().sum())
```

**4. 代碼追蹤**
```python
# 使用 profiling
import cProfile
cProfile.run('strategy.generate_signals()')

# 使用 memory profiling
from memory_profiler import profile
@profile
def generate_signals():
    ...
```

**能力指標：**
- 能夠使用調試工具
- 能夠系統化地診斷問題
- 能夠找到根本原因

### 2.5 文檔編寫能力

#### A. 代碼文檔

**Python 文檔字符串（docstrings）：**
```python
def generate_signals(
    self,
    context: ExecutionContext,
    symbols: List[str]
) -> List[StrategySignal]:
    """
    Generate trading signals for given context and symbols.

    Args:
        context: Execution context containing portfolio state and market information
        symbols: List of symbols to generate signals for

    Returns:
        List of StrategySignal objects with BUY/SELL actions

    Raises:
        ValueError: If context is invalid or symbols list is empty

    Examples:
        >>> strategy = RSIStrategy(period=14)
        >>> context = ExecutionContext(...)
        >>> signals = strategy.generate_signals(context, ['AAPL'])
        >>> print(signals[0].action)
        BUY
    """
    ...
```

**JavaScript/JSDoc：**
```javascript
/**
 * Fetches stock history data for a given symbol.
 *
 * @param {string} symbol - Stock symbol (e.g., 'AAPL')
 * @param {Object} params - Query parameters
 * @param {number} params.days - Number of days of history to fetch
 * @returns {Promise<Object>} Promise resolving to stock history data
 * @throws {Error} If symbol is not provided
 *
 * @example
 * const history = await getHistory('AAPL', { days: 30 });
 * console.log(history.data);
 */
export const getHistory = async (symbol, params = {}) => {
  ...
};
```

#### B. API 文檔

**Swagger/OpenAPI（FastAPI 自動生成）：**
```python
from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

app = FastAPI(
    title="Dashboard API",
    description="Quantitative Trading Dashboard API",
    version="1.0.0"
)

class StrategyCreate(BaseModel):
    """Request model for creating a strategy."""
    name: str = Field(..., description="Strategy name")
    type: str = Field(..., description="Strategy type")
    parameters: dict = Field(default={}, description="Strategy parameters")

@app.post(
    "/api/v1/strategies",
    response_model=StrategyResponse,
    summary="Create a new strategy",
    description="Creates a new trading strategy with the given configuration",
    tags=["Strategies"]
)
async def create_strategy(
    strategy: StrategyCreate,
    current_user: User = Depends(get_current_user)
):
    ...
```

#### C. 架構文檔

**架構圖和數據流：**
```markdown
## Backend Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Strategies  │  │   Analysis   │  │   Market     │     │
│  │   Router     │  │   Router     │  │   Router     │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
└─────────┼──────────────────┼──────────────────┼───────────┘
          │                  │                  │
          ▼                  ▼                  ▼
  ┌───────────────────────────────────────────────────────┐  │
  │                    Service Layer                       │  │
  │  StrategyRegistry  │  PerformanceService  │ MarketData  │  │
  └───────────────────────────────────────────────────────┘  │
                        │                                      │
                        ▼                                      │
  ┌───────────────────────────────────────────────────────┐  │
  │                   Repository Layer                      │  │
  │  StrategyRepo  │  BacktestRepo  │  MarketRepo         │  │
  └───────────────────────────────────────────────────────┘  │
                        │                                      │
                        ▼                                      │
  ┌───────────────────────────────────────────────────────┐  │
  │                    Storage Layer                       │  │
  │  DuckDB  │  PostgreSQL  │  Redis                       │  │
  └───────────────────────────────────────────────────────┘  │
```
```

**能力指標：**
- 能夠編寫清晰的代碼文檔
- 能夠維護 API 文檔
- 能夠創建架構文檔

---

## 3. Dashboard 項目特定能力

### 3.1 量化交易系統開發知識

#### A. 技術指標實現

**支持的技術指標：**
- **RSI (Relative Strength Index)**：相對強弱指數
- **MACD (Moving Average Convergence Divergence)**：指數平滑異同移動平均線
- **SuperTrend**：超級趨勢指標
- **Bollinger Bands**：布林帶
- **Momentum**：動量指標
- **Dual Momentum**：雙重動量
- **Sector Rotation**：板塊輪動
- **Extremes**：極值指標

**實現示例：**
```python
class RSIStrategy(IStrategy):
    def __init__(self, period: int = 14, buy_threshold: float = 30, sell_threshold: float = 70):
        self.period = period
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold

    def generate_signals(self, context: ExecutionContext, symbols: List[str]) -> List[StrategySignal]:
        signals = []

        for symbol in symbols:
            # 獲取 RSI 值
            rsi = self._get_rsi(symbol, context.market_date)

            # 生成信號
            if rsi < self.buy_threshold:
                signals.append(StrategySignal(
                    symbol=symbol,
                    action=SignalAction.BUY,
                    confidence=(self.buy_threshold - rsi) / self.buy_threshold
                ))
            elif rsi > self.sell_threshold:
                signals.append(StrategySignal(
                    symbol=symbol,
                    action=SignalAction.SELL,
                    confidence=(rsi - self.sell_threshold) / (100 - self.sell_threshold)
                ))

        return signals

    def _get_rsi(self, symbol: str, date: datetime.date) -> float:
        # 使用 pandas-ta 計算 RSI
        prices = self.data_loader.get_prices(symbol, date - timedelta(days=self.period * 2), date)
        rsi = ta.momentum.RSIIndicator(prices['close'], window=self.period).rsi()
        return rsi.iloc[-1]
```

#### B. 策略類型和模式

**策略類型：**
- **Trend Following（趨勢跟蹤）**：移動平均線、MACD、Momentum
- **Mean Reversion（均值回歸）**：RSI、Bollinger Bands
- **Momentum（動量）**：Dual Momentum、Relative Strength
- **Volatility（波動率）**：ATR、Volatility Breakout
- **Composite（複合）**：多策略組合、對沖策略

**策略模式：**
```python
# 趨勢跟蹤模式
class TrendFollowingStrategy(IStrategy):
    """跟隨市場趨勢，在趨勢確認時進場，在趨勢反轉時出場。"""

# 均值回歸模式
class MeanReversionStrategy(IStrategy):
    """在價格偏離均值時反向交易。"""

# 動量模式
class MomentumStrategy(IStrategy):
    """買入表現好的資產，賣出表現差的資產。"""
```

#### C. 回測框架使用

**Backtrader 使用：**
```python
import backtrader as bt

class BacktraderRSIStrategy(bt.Strategy):
    params = (('period', 14), ('buy_threshold', 30), ('sell_threshold', 70))

    def __init__(self):
        self.rsi = bt.indicators.RSI(self.data.close, period=self.params.period)

    def next(self):
        if not self.position:
            if self.rsi < self.params.buy_threshold:
                self.buy()
        else:
            if self.rsi > self.params.sell_threshold:
                self.sell()

# 運行回測
cerebro = bt.Cerebro()
cerebro.addstrategy(BacktraderRSIStrategy)
cerebro.adddata(data)
results = cerebro.run()
```

**VectorBT 使用：**
```python
import vectorbt as vbt

# 加載數據
data = vbt.YFData.download('AAPL', start='2024-01-01', end='2024-12-31').get()

# 計算 RSI
rsi = vbt.RSI.run(data['Close'], window=14)

# 生成信號
entries = rsi.rsi_below(30, crossed=True)
exits = rsi.rsi_above(70, crossed=True)

# 創建組合
pf = vbt.Portfolio.from_signals(
    data['Close'],
    entries=entries,
    exits=exits,
    init_cash=100000,
    fees=0.001
)

# 獲取結果
stats = pf.stats()
print(stats['total_return'], stats['sharpe_ratio'])
```

**能力指標：**
- 能夠實現技術指標
- 能夠設計策略邏輯
- 能夠使用回測框架

### 3.2 策略引擎架構理解

#### A. 統一策略接口（IStrategy）

**接口定義：**
```python
class IStrategy(ABC):
    @abstractmethod
    def generate_signals(
        self,
        context: ExecutionContext,
        symbols: List[str]
    ) -> List[StrategySignal]:
        """
        Generate trading signals for given context and symbols.

        Args:
            context: Execution context with portfolio state and market info
            symbols: List of symbols to analyze

        Returns:
            List of signals (BUY/SELL actions with confidence)
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Strategy identifier."""
        pass
```

**信號定義：**
```python
@dataclass
class StrategySignal:
    symbol: str
    action: SignalAction  # BUY | SELL | HOLD
    confidence: float      # 0.0 to 1.0

class SignalAction(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
```

**執行上下文：**
```python
@dataclass
class ExecutionContext:
    portfolio_value: float
    available_cash: float
    current_positions: List[PositionState]
    market_date: date
    market_status: str  # 'OPEN', 'CLOSED', etc.

@dataclass
class PositionState:
    symbol: str
    quantity: int
    current_price: float
    entry_price: float
    unrealized_pnl: float
```

#### B. 策略工廠模式

**策略工廠：**
```python
class StrategyFactory:
    _strategies = {}

    @classmethod
    def register(cls, strategy_type: str, strategy_class: Type[IStrategy]):
        """Register a strategy class."""
        cls._strategies[strategy_type] = strategy_class

    @classmethod
    def create(cls, strategy_type: str, params: Dict) -> IStrategy:
        """Create a strategy instance."""
        strategy_class = cls._strategies.get(strategy_type)
        if not strategy_class:
            raise ValueError(f"Unknown strategy type: {strategy_type}")
        return strategy_class(**params)

# 註冊策略
@StrategyFactory.register("rsi")
class RSIStrategy(IStrategy):
    ...

@StrategyFactory.register("macd")
class MACDStrategy(IStrategy):
    ...

# 使用工廠
strategy = StrategyFactory.create("rsi", {"period": 14, "buy_threshold": 30})
```

#### C. 複合策略和信號合併

**複合策略：**
```python
class CompositeStrategy(IStrategy):
    def __init__(self, strategies: List[IStrategy], merge_algorithm: str = "majority_vote"):
        self.strategies = strategies
        self.merge_algorithm = merge_algorithm

    def generate_signals(self, context: ExecutionContext, symbols: List[str]) -> List[StrategySignal]:
        # 收集所有策略的信號
        all_signals = []
        for strategy in self.strategies:
            signals = strategy.generate_signals(context, symbols)
            all_signals.append(signals)

        # 合併信號
        return self._merge_signals(all_signals)

    def _merge_signals(self, all_signals: List[List[StrategySignal]]) -> List[StrategySignal]:
        """Merge signals from multiple strategies."""
        if self.merge_algorithm == "majority_vote":
            return self._majority_vote_merge(all_signals)
        elif self.merge_algorithm == "unanimous":
            return self._unanimous_merge(all_signals)
        elif self.merge_algorithm == "weighted":
            return self._weighted_merge(all_signals)
        else:
            return self._any_merge(all_signals)
```

**信號合併算法：**
```python
class SignalMerger:
    @staticmethod
    def majority_vote_merge(all_signals: List[List[StrategySignal]]) -> List[StrategySignal]:
        """Buy if majority says buy."""
        # 按符號分組
        symbol_signals = defaultdict(list)
        for signals in all_signals:
            for signal in signals:
                symbol_signals[signal.symbol].append(signal)

        # 多數投票
        merged = []
        for symbol, signals in symbol_signals.items():
            buy_votes = sum(1 for s in signals if s.action == SignalAction.BUY)
            sell_votes = sum(1 for s in signals if s.action == SignalAction.SELL)

            if buy_votes > len(signals) / 2:
                merged.append(StrategySignal(
                    symbol=symbol,
                    action=SignalAction.BUY,
                    confidence=buy_votes / len(signals)
                ))
            elif sell_votes > len(signals) / 2:
                merged.append(StrategySignal(
                    symbol=symbol,
                    action=SignalAction.SELL,
                    confidence=sell_votes / len(signals)
                ))

        return merged
```

**能力指標：**
- 能夠實現 IStrategy 接口
- 能夠使用 StrategyFactory
- 能夠創建複合策略

### 3.3 Backtrader/VectorBT 使用能力

#### A. Backtrader 回測

**完整回測流程：**
```python
class BacktraderEngine:
    def __init__(self, config: dict, db_session: Session):
        self.config = config
        self.db = db_session
        self.cerebro = bt.Cerebro()

    def add_strategy(self, strategy_config: dict, risk_params: dict = None):
        """Add a strategy to cerebro."""
        strategy_class = self._get_strategy_class(strategy_config['type'])
        self.cerebro.addstrategy(
            strategy_class,
            **strategy_config.get('parameters', {}),
            **(risk_params or {})
        )

    def add_data(self, symbol: str, start_date: datetime.date, end_date: datetime.date):
        """Add data feed."""
        data = self._load_data(symbol, start_date, end_date)
        self.cerebro.adddata(bt.feeds.PandasData(data))

    def run(self) -> dict:
        """Execute backtest."""
        self.cerebro.broker.setcash(self.config.get('initial_capital', 100000))
        self.cerebro.broker.setcommission(commission=self.config.get('commission', 0.001))

        strategies = self.cerebro.run()
        strategy = strategies[0]

        return {
            'total_return': strategy.analyzers.total_return.get_analysis(),
            'sharpe_ratio': strategy.analyzers.sharpe.get_analysis()['sharperatio'],
            'max_drawdown': strategy.analyzers.drawdown.get_analysis()['max']['drawdown'],
            'trades': strategy._trades
        }
```

**優化策略：**
- 數據預加載（preload=True）
- 批量查詢減少數據庫訪問
- 支持並行回測（多進程）
- 內存優化（NumPy 數組）

#### B. VectorBT 回測

**完整回測流程：**
```python
class VectorBTExecutor:
    def __init__(self, data_loader: DataLoader):
        self.data_loader = data_loader

    def run_backtest(
        self,
        strategy_func: Callable,
        symbols: List[str],
        start_date: date,
        end_date: date,
        **params
    ) -> dict:
        """Execute vectorized backtest."""

        # 1. 加載數據
        ohlcv = self.data_loader.load_ohlcv(symbols, start_date, end_date)
        prices = ohlcv['close']

        # 2. 生成信號
        entries, exits = strategy_func(prices, **params)

        # 3. 創建組合
        pf = vbt.Portfolio.from_signals(
            prices,
            entries=entries,
            exits=exits,
            init_cash=params.get('initial_cash', 100000),
            fees=params.get('commission', 0.001),
            slippage=params.get('slippage', 0.0001)
        )

        # 4. 計算指標
        stats = pf.stats()

        return {
            'total_return': stats['total_return'],
            'sharpe_ratio': stats['sharpe_ratio'],
            'max_drawdown': stats['max_drawdown'],
            'win_rate': stats['win_rate'],
            'num_trades': stats['num_trades'],
            'equity_curve': pf.value().tolist()
        }

    def run_param_scan(
        self,
        strategy_func: Callable,
        param_grid: dict,
        **params
    ) -> pd.DataFrame:
        """Parameter scan with VectorBT."""
        # 創建參數組合
        keys, values = zip(*param_grid.items())
        combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]

        results = []
        for combo in combinations:
            result = self.run_backtest(strategy_func, **{**params, **combo})
            result.update(combo)
            results.append(result)

        return pd.DataFrame(results)
```

**優勢：**
- 全向量化運算，極快速度
- 支持批量策略回測
- 自動處理數據對齊
- 內置豐富的分析工具

**能力指標：**
- 能夠使用 Backtrader 進行回測
- 能夠使用 VectorBT 進行回測
- 能夠比較兩種回測引擎的結果

### 3.4 React 19 + Zustand + React Query 精通

#### A. React 19 Hooks

**常用 Hooks：**
```javascript
// useState - 本地狀態
const [market, setMarket] = useState('US');

// useEffect - 副作用
useEffect(() => {
  const fetchConfig = async () => {
    const response = await apiClient.get('/config');
    setPageConfig(response.data);
  };
  fetchConfig();
}, []);

// useMemo - 記憶化計算
const sortedStrategies = useMemo(() => {
  return strategies.sort((a, b) => b.sharpeRatio - a.sharpeRatio);
}, [strategies]);

// useCallback - 記憶化函數
const handleStrategyClick = useCallback((strategyId) => {
  navigate(`/strategies/builder?instance_id=${strategyId}`);
}, [navigate]);

// useRef - 引用
const fetchStage1Ref = useRef(fetchStage1Overview);

// useContext - 上下文
const { currentPersona, selectPersona } = useContext(PersonaContext);

// useReducer - 複雜狀態
const [formState, dispatch] = useReducer(formReducer, initialState);
```

#### B. Zustand 全局狀態管理

**Store 定義：**
```javascript
import create from 'zustand';

const useStore = create((set, get) => ({
  // State
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
  loadingStatus: 'idle',
  error: null,

  // Actions
  fetchStage1Overview: async (force, targetDate, market) => {
    set({ loadingStatus: 'loading' });
    try {
      const [movers, heatmap, score] = await Promise.all([
        MarketApi.getMovers(),
        MarketApi.getHeatmap(targetDate, market),
        MarketApi.getMarketScore()
      ]);

      set({
        marketMovers: movers,
        heatmapData: heatmap,
        marketScore: score,
        loadingStatus: 'success'
      });
    } catch (error) {
      set({ error, loadingStatus: 'error' });
    }
  },

  addWatchlistItem: (symbol) => {
    const watchlist = get().watchlist;
    if (!watchlist.includes(symbol)) {
      set({ watchlist: [...watchlist, symbol] });
    }
  },

  removeWatchlistItem: (symbol) => {
    const watchlist = get().watchlist;
    set({ watchlist: watchlist.filter(s => s !== symbol) });
  }
}));

export default useStore;
```

**使用 Store：**
```javascript
const DashboardPage = () => {
  const {
    watchlist,
    marketMovers,
    heatmapData,
    marketScore,
    loadingStatus,
    fetchStage1Overview,
    addWatchlistItem,
    removeWatchlistItem
  } = useStore();

  // 使用 ref 避免 useEffect 重新運行
  const fetchStage1Ref = useRef(fetchStage1Overview);

  useEffect(() => {
    fetchStage1Ref.current(false, null, 'US');
  }, []);

  return (
    <div className="dashboard">
      <MarketHeatmap data={heatmapData} />
      <MarketScoreCard score={marketScore.current} />
      <Watchlist
        symbols={watchlist}
        onAdd={addWatchlistItem}
        onRemove={removeWatchlistItem}
      />
    </div>
  );
};
```

#### C. React Query 服務端狀態管理

**Query Client 配置：**
```javascript
import { QueryClient } from '@tanstack/react-query';

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

**Cache Presets：**
```javascript
const cachePresets = {
  static: {
    staleTime: 60 * 60 * 1000,      // 1 小時
    gcTime: 24 * 60 * 60 * 1000,   // 24 小時
  },  // 靜態數據（策略類型、配置）
  user: {
    staleTime: 5 * 60 * 1000,      // 5 分鐘
    gcTime: 30 * 60 * 1000,        // 30 分鐘
  },  // 用戶數據（用戶策略、投資組合）
  dynamic: {
    staleTime: 30 * 1000,         // 30 秒
    gcTime: 5 * 60 * 1000,        // 5 分鐘
  },  // 動態數據（市場價格、訊號）
  realtime: {
    staleTime: 0,
    gcTime: 0,
  },  // 實時數據（回測結果）
};
```

**useApiCache Hook：**
```javascript
const useApiCache = (queryKey, fetcher, options = {}) => {
  const { data, isLoading, error, refetch, isFetching } = useQuery({
    queryKey,
    queryFn: fetcher,
    ...options
  });

  return { data, isLoading, error, refetch, isFetching };
};

// 使用示例
const { data, isLoading, error, refetch } = useApiCache(
  ['market', 'heatmap', targetDate],
  () => MarketApi.getHeatmap(targetDate, market),
  {
    staleTime: 5 * 60 * 1000,  // 5 分鐘
    gcTime: 10 * 60 * 1000     // 10 分鐘
  }
);
```

**useApiMutation Hook：**
```javascript
const useApiMutation = (mutationFn, options = {}) => {
  const queryClient = useQueryClient();

  const { mutate, mutateAsync, isLoading, error } = useMutation({
    mutationFn,
    onSuccess: (data, variables, context) => {
      // 使相關查詢失效
      if (options.invalidateKeys) {
        options.invalidateKeys.forEach(key => {
          queryClient.invalidateQueries(key);
        });
      }
      // 調用成功回調
      if (options.onSuccess) {
        options.onSuccess(data, variables, context);
      }
    },
    onError: options.onError
  });

  return { mutate, mutateAsync, isLoading, error };
};

// 使用示例
const { mutate, isLoading } = useApiMutation(
  (data) => apiClient.post('/strategies', data),
  {
    invalidateKeys: [['strategies']],
    onSuccess: () => {
      toast.success('策略已創建');
    },
    onError: (error) => {
      toast.error('創建失敗');
    }
  }
);
```

**手動緩存管理（cacheUtils）：**
```javascript
import { queryClient } from '../main';

const cacheUtils = {
  invalidate: (key) => {
    queryClient.invalidateQueries(key);
  },

  clear: () => {
    queryClient.clear();
  },

  prefetch: async (key, fetcher) => {
    await queryClient.prefetchQuery(key, fetcher);
  },

  getData: (key) => {
    return queryClient.getQueryData(key);
  },

  setData: (key, data) => {
    queryClient.setQueryData(key, data);
  }
};

// 使用示例
cacheUtils.invalidate(['strategies']);
cacheUtils.prefetch(['market', 'heatmap'], () => MarketApi.getHeatmap());
const data = cacheUtils.getData(['market', 'heatmap']);
cacheUtils.setData(['market', 'heatmap'], newData);
```

**能力指標：**
- 能夠使用 React 19 Hooks
- 能夠使用 Zustand 管理全局狀態
- 能夠使用 React Query 管理服務端狀態
- 能夠實現複雜的狀態邏輯

### 3.5 FastAPI + DuckDB 數據處理能力

#### A. FastAPI 路由和依賴注入

**路由定義：**
```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/strategies", tags=["Strategies"])

class StrategyCreate(BaseModel):
    name: str
    type: str
    parameters: dict = {}

class StrategyResponse(BaseModel):
    id: str
    name: str
    type: str
    status: str
    created_at: datetime

@router.post("/", response_model=StrategyResponse)
async def create_strategy(
    strategy: StrategyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new strategy."""
    service = StrategyService(db)
    result = await service.create_strategy(strategy)

    return result

@router.get("/", response_model=List[StrategyResponse])
async def list_strategies(
    page: int = 1,
    limit: int = 10,
    current_user: User = Depends(get_current_user)
):
    """List all strategies."""
    ...
```

**依賴注入：**
```python
# 數據庫依賴
def get_db():
    conn = duckdb.connect('data.duckdb')
    try:
        yield conn
    finally:
        conn.close()

# 用戶認證依賴
def get_current_user(token: str = Depends(get_token_from_header)):
    user = auth_service.validate_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

# 使用依賴
@router.get("/protected")
async def protected_route(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return {"user": current_user.username}
```

#### B. DuckDB 數據庫操作

**Repository 模式：**
```python
class StrategyRepository:
    def __init__(self, conn: duckdb.DuckDBPyConnection):
        self.conn = conn

    def save(self, strategy: Strategy) -> str:
        """Save strategy to database."""
        strategy_id = str(uuid.uuid4())
        self.conn.execute("""
            INSERT INTO strategies (id, name, type, parameters, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (strategy_id, strategy.name, strategy.type,
              json.dumps(strategy.parameters), strategy.status,
              datetime.now()))
        return strategy_id

    def get_by_id(self, strategy_id: str) -> Optional[Strategy]:
        """Get strategy by ID."""
        result = self.conn.execute("""
            SELECT id, name, type, parameters, status, created_at
            FROM strategies
            WHERE id = ?
        """, (strategy_id,)).fetchone()

        if not result:
            return None

        return Strategy(
            id=result[0],
            name=result[1],
            type=result[2],
            parameters=json.loads(result[3]),
            status=result[4],
            created_at=result[5]
        )

    def list(self, page: int = 1, limit: int = 10) -> List[Strategy]:
        """List strategies with pagination."""
        offset = (page - 1) * limit
        results = self.conn.execute("""
            SELECT id, name, type, parameters, status, created_at
            FROM strategies
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (limit, offset)).fetchall()

        return [
            Strategy(
                id=r[0], name=r[1], type=r[2],
                parameters=json.loads(r[3]), status=r[4],
                created_at=r[5]
            )
            for r in results
        ]
```

**查詢優化：**
```python
# 使用索引（如果支持）
self.conn.execute("CREATE INDEX IF NOT EXISTS idx_strategies_type ON strategies(type)")

# 批量插入
def batch_save(self, strategies: List[Strategy]) -> List[str]:
    data = [
        (str(uuid.uuid4()), s.name, s.type, json.dumps(s.parameters),
         s.status, datetime.now())
        for s in strategies
    ]
    self.conn.executemany("""
        INSERT INTO strategies (id, name, type, parameters, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, data)
    return [d[0] for d in data]

# 使用 CTE（Common Table Expression）
def get_strategies_with_stats(self):
    results = self.conn.execute("""
        WITH strategy_stats AS (
            SELECT
                s.id,
                s.name,
                s.type,
                COUNT(b.id) as backtest_count,
                AVG(b.total_return) as avg_return,
                MAX(b.sharpe_ratio) as max_sharpe
            FROM strategies s
            LEFT JOIN backtests b ON s.id = b.strategy_id
            GROUP BY s.id, s.name, s.type
        )
        SELECT * FROM strategy_stats
        ORDER BY max_sharpe DESC
    """).fetchall()
    return results
```

#### C. 數據處理和轉換

**pandas + DuckDB 整合：**
```python
import pandas as pd
import duckdb

# 使用 DuckDB 查詢轉換為 pandas DataFrame
def get_market_data_as_dataframe(self, symbols: List[str], start_date: date, end_date: date):
    query = """
        SELECT symbol, date, open, high, low, close, volume
        FROM market_data
        WHERE symbol IN (?)
        AND date BETWEEN ? AND ?
        ORDER BY symbol, date
    """
    df = self.conn.execute(query, [symbols, start_date, end_date]).df()
    return df

# 使用 pandas 進行數據處理
def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
    # 計算移動平均線
    df['ma_20'] = df.groupby('symbol')['close'].transform(
        lambda x: x.rolling(window=20).mean()
    )
    df['ma_50'] = df.groupby('symbol')['close'].transform(
        lambda x: x.rolling(window=50).mean()
    )

    # 計算 RSI
    import pandas_ta as ta
    df['rsi'] = df.groupby('symbol')['close'].transform(
        lambda x: ta.momentum.RSIIndicator(x, window=14).rsi()
    )

    return df

# 使用 DuckDB 進行聚合查詢
def get_portfolio_performance(self, portfolio_id: str):
    query = """
        SELECT
            date,
            SUM(value) as total_value,
            SUM(cost) as total_cost,
            (SUM(value) - SUM(cost)) / SUM(cost) * 100 as return_pct
        FROM portfolio_positions
        WHERE portfolio_id = ?
        GROUP BY date
        ORDER BY date
    """
    return self.conn.execute(query, [portfolio_id]).df()
```

**能力指標：**
- 能夠使用 FastAPI 創建 API 端點
- 能夠使用依賴注入
- 能夠使用 DuckDB 進行數據庫操作
- 能夠整合 pandas 和 DuckDB

### 3.6 Git 流程和 CI/CD 實踐

#### A. Conventional Commits 規範

**提交格式：**
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**提交類型：**
- `feat` - 新功能
- `fix` - Bug 修復
- `refactor` - 代碼重構
- `docs` - 文檔更新
- `test` - 測試相關
- `debug` - 調試記錄

**提交範例：**
```bash
# 簡短描述
feat: add momentum indicator
fix: correct API timeout
docs: update deployment docs

# 中等長度
feat(performance): implement database operations for daily scheduler
fix(system): remove duplicate API prefix from system routers

# 帶子類型
feat(ssot): add 5 SSoT registries with comprehensive metadata
refactor(code-quality): clean debug code from production (ARCH-001)

# 帶任務標記
feat(tests): add contract tests for critical services (ARCH-005)
refactor: complete REF-001 through REF-005 plus pytest improvements
```

**最佳實踐：**
1. ✅ 遵循 Conventional Commits 格式
2. ✅ 使用正確的 type
3. ✅ 描述簡潔明確（50 字符以內主標題）
4. ✅ 相關功能使用子類型分類
5. ✅ 關聯任務標記（如 ARCH-001）
6. ✅ 單次提交範圍適中（不超過 300-500 行）

#### B. 分支策略

**Git Flow 分支模型：**
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

**分支命名規範：**
```bash
feature/add-momentum-indicator
fix/data-fetching-timeout
hotfix/production-deployment
refactor/restructure-database-layer
docs/update-readme
test/add-contract-tests
release/v1.0.0
```

**分支保護規則（main 分支）：**
- ✅ 要求 PR 檢查通過
- ✅ 要求狀態檢查通過（CI workflow）
- ✅ 要求代碼審查（至少 1 名審查者批准）
- ✅ 要求分支是最新的（合併前更新）
- ✅ 限制誰可以推送（僅維護者）
- ✅ 要求線性歷史（禁止合併提交）

#### C. CI/CD 流程

**CI Workflow（.github/workflows/ci.yml）：**
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

      - name: Backend lint
        run: |
          ruff check backend/
          black --check backend/
          isort --check-only backend/

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

      - name: Install dependencies
        run: pip install -r backend/requirements.txt

      - name: Run tests
        run: |
          cd backend
          pytest -m "not slow" -v --cov=. --cov-report=xml

      - name: Upload coverage
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

      - name: Install dependencies
        run: cd frontend && npm ci

      - name: Run tests
        run: |
          cd frontend
          npm run test -- --run
          npm run test:coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./frontend/coverage/coverage-final.json
          flags: frontend
```

**CD Workflow（.github/workflows/cd.yml）：**
```yaml
name: CD

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  deploy:
    name: Deploy to Production
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4

      - name: Build Docker image
        run: |
          docker buildx build \
            --platform linux/amd64 \
            -t dashboard-app:${{ github.sha }} \
            -t dashboard-app:latest \
            .

      - name: Export Docker image
        run: |
          docker save dashboard-app:latest | gzip > dashboard-app.tar.gz

      - name: Transfer to server
        run: |
          scp dashboard-app.tar.gz root@${{ secrets.LINODE_HOST }}:/tmp/

      - name: Deploy
        run: |
          ssh root@${{ secrets.LINODE_HOST }} << 'ENDSSH'
            docker stop dashboard_app 2>/dev/null || true
            docker rm dashboard_app 2>/dev/null || true
            docker load < /tmp/dashboard-app.tar.gz
            docker run -d --name dashboard_app \
              -v dashboard_data:/app/backend/market_data_db \
              -e ENV=production \
              --restart unless-stopped \
              dashboard-app:latest
          ENDSSH
```

**能力指標：**
- 能夠遵循 Conventional Commits 規範
- 能夠使用 Git Flow 分支策略
- 能夠配置 CI/CD 流程
- 能夠使用 Docker 部署

---

## 4. 能力矩陣（Competency Matrix）

### 4.1 按技能類別分類

| 技能類別 | 技能項目 | 熟練度等級 | 優先級 | 重要性 |
|----------|----------|------------|--------|--------|
| **架構** | 分層架構設計 | P3 | 低 | 中 |
| | 數據架構設計 | P2 | 中 | 高 |
| | 微服務架構理解 | P3 | 低 | 中 |
| | 技術選型決策 | P2 | 中 | 高 |
| | 性能優化決策 | P1 | 高 | 高 |
| | 安全性決策 | P1 | 高 | 高 |
| | 重構和優化 | P1 | 高 | 高 |
| | 技術債管理 | P2 | 中 | 高 |
| | 跨領域知識整合 | P2 | 中 | 高 |
| | 團隊技術領導力 | P3 | 低 | 中 |
| **開發** | Python/FastAPI 開發 | P0 | 必備 | 高 |
| | React 19 開發 | P0 | 必備 | 高 |
| | API 集成 | P0 | 必備 | 高 |
| | 全棧開發能力 | P0 | 必備 | 高 |
| | 量化交易系統開發 | P1 | 高 | 高 |
| | 策略引擎架構理解 | P1 | 高 | 高 |
| | Backtrader 使用 | P1 | 高 | 高 |
| | VectorBT 使用 | P0 | 必備 | 高 |
| | React Hooks 精通 | P0 | 必備 | 高 |
| | Zustand 狀態管理 | P0 | 必備 | 高 |
| | React Query 精通 | P0 | 必備 | 高 |
| | FastAPI + DuckDB | P0 | 必備 | 高 |
| **測試** | 單元測試（pytest） | P0 | 必備 | 高 |
| | 單元測試（vitest） | P0 | 必備 | 高 |
| | 集成測試 | P1 | 高 | 高 |
| | E2E 測試（cypress） | P2 | 中 | 中 |
| | 測試驅動開發（TDD） | P1 | 高 | 高 |
| | 測試覆蓋率管理 | P1 | 高 | 高 |
| **工具** | Git/Conventional Commits | P0 | 必備 | 高 |
| | Docker 容器化 | P1 | 高 | 高 |
| | CI/CD 配置 | P2 | 中 | 高 |
| | 代碼審查（ruff, eslint） | P0 | 必備 | 高 |
| | 調試工具使用 | P0 | 必備 | 高 |
| | 性能分析工具 | P2 | 中 | 高 |
| **流程** | 代碼審查流程 | P1 | 高 | 高 |
| | 問題診斷和調試 | P0 | 必備 | 高 |
| | 文檔編寫能力 | P1 | 高 | 高 |
| | 技術決策記錄 | P2 | 中 | 中 |
| | 團隊協作溝通 | P2 | 中 | 中 |

### 4.2 熟練度等級定義

| 等級 | 描述 | 要求 |
|------|------|------|
| **P0（必備）** | 必須擁有的核心能力 | 能夠獨立完成任務，無需幫助 |
| **P1（重要）** | 應該擁有的重要能力 | 能夠在指導下完成任務 |
| **P2（可選）** | 可以擁有的加成能力 | 具備基本了解，能夠學習 |
| **P3（未來擴展）** | 期望擁有的專家級能力 | 需要長期培養和經驗積累 |

### 4.3 優先級評估

| 優先級 | 比例 | 說明 |
|--------|------|------|
| **P0（必備）** | 20% | 立即掌握，用於核心開發任務 |
| **P1（重要）** | 35% | 短期掌握，用於重要功能開發 |
| **P2（可選）** | 30% | 中期掌握，用於提升效率 |
| **P3（未來擴展）** | 15% | 長期培養，用於專家級發展 |

---

## 5. Programmer Sub-Agent 核心能力

### 5.1 必備能力（P0 - 必須擁有）

#### A. 開發技能

| 技能 | 描述 | 驗證方法 |
|------|------|----------|
| **Python/FastAPI** | 能夠創建 API 端點、使用依賴注入、編寫 Pydantic 模型 | 創建一個完整的 CRUD API 端點 |
| **React 19** | 能夠創建函數式組件、使用 Hooks、處理表單 | 創建一個完整的頁面組件 |
| **API 集成** | 能夠使用 Axios、React Query 管理服務端狀態 | 實現一個完整的數據加載和緩存流程 |
| **Zustand** | 能夠創建全局 store、管理跨組件狀態 | 實現一個全局狀態管理模塊 |
| **React Query** | 能夠使用 useQuery、useMutation、管理緩存 | 實現一個完整的 API 集成模塊 |
| **DuckDB** | 能夠執行 SQL 查詢、使用 pandas 整合 | 實現一個完整的 Repository 模塊 |

#### B. 測試技能

| 技能 | 描述 | 驗證方法 |
|------|------|----------|
| **pytest** | 能夠編寫單元測試、使用 fixture、mock 對象 | 編寫覆蓋率 >80% 的單元測試 |
| **vitest** | 能夠編寫前端單元測試、使用 happy-dom | 編寫覆蓋率 >70% 的組件測試 |
| **TDD** | 能夠遵循紅-綠-重構循環 | 使用 TDD 開發一個功能 |
| **測試覆蓋率** | 能夠達到項目測試覆蓋率目標 | 達到 >80% 測試覆蓋率 |

#### C. 工具技能

| 技能 | 描述 | 驗證方法 |
|------|------|----------|
| **Git/Conventional Commits** | 能夠遵循提交規範、創建分支、處理合併 | 提交 10 個符合規範的 commit |
| **代碼審查工具** | 能夠使用 ruff、black、eslint、pre-commit | 通過所有代碼質量檢查 |
| **調試工具** | 能夠使用 pdb、console.log、React DevTools | 調試並修復一個 bug |

### 5.2 重要能力（P1 - 應該擁有）

#### A. 量化交易技能

| 技能 | 描述 | 驗證方法 |
|------|------|----------|
| **VectorBT** | 能夠使用 VectorBT 進行向量化回測 | 實現一個完整的回測流程 |
| **技術指標實現** | 能夠實現 RSI、MACD、移動平均線等指標 | 實現一個技術指標並驗證結果 |
| **策略引擎架構** | 能夠理解並使用 IStrategy 接口 | 實現一個符合 IStrategy 接口的策略 |
| **策略工廠模式** | 能夠使用 StrategyFactory 創建策略 | 註冊並使用一個自定義策略 |

#### B. 高級開發技能

| 技能 | 描述 | 驗證方法 |
|------|------|----------|
| **重構和優化** | 能夠識別代碼異味、應用設計模式 | 重構一個模塊並提升代碼質量 |
| **性能優化** | 能夠識別性能瓶頸、實施優化策略 | 優化一個慢查詢或慢函數 |
| **集成測試** | 能夠編寫 API 端點測試、服務層測試 | 編寫覆蓋關鍵路徑的集成測試 |
| **E2E 測試** | 能夠使用 Cypress 編寫端到端測試 | 編寫一個完整的用戶流程測試 |

#### C. 流程技能

| 技能 | 描述 | 驗證方法 |
|------|------|----------|
| **代碼審查** | 能夠提供建設性的審查意識 | 審查 5 個 PR 並提供反饋 |
| **問題診斷** | 能夠系統化地診斷和調試問題 | 調試並修復 3 個生產問題 |
| **文檔編寫** | 能夠編寫清晰的代碼文檔和 API 文檔 | 編寫一份完整的模塊文檔 |

### 5.3 可選能力（P2 - 可以擁有）

#### A. 高級工具

| 技能 | 描述 | 驗證方法 |
|------|------|----------|
| **Docker** | 能夠編寫 Dockerfile、使用 docker-compose | 構建並運行一個 Docker 容器 |
| **CI/CD** | 能夠配置 GitHub Actions workflows | 配置一個完整的 CI/CD 流程 |
| **性能分析** | 能夠使用 profiler、benchmark 工具 | 分析並優化一個性能瓶頸 |

#### B. 高級前端

| 技能 | 描述 | 驗證方法 |
|------|------|----------|
| **Three.js** | 能夠創建 3D 可視化 | 實現一個簡單的 3D 圖表 |
| **ECharts 高級圖表** | 能夠使用 ECharts 創建複雜圖表 | 實現一個交互式熱力圖 |
| **React Query DevTools** | 能夠使用 DevTools 調試狀態 | 調試一個複雜的狀態問題 |

### 5.4 未來擴展（P3 - 期望擁有）

#### A. 架構能力

| 技能 | 描述 | 驗證方法 |
|------|------|----------|
| **系統架構設計** | 能夠設計完整的系統架構 | 設計一個新系統的架構 |
| **技術選型決策** | 能夠進行技術選型並記錄決策 | 編寫一份技術選型文檔 |
| **團隊技術領導力** | 能夠帶領團隊技術發展 | 指導 2-3 名初級開發者 |

#### B. 專業技能

| 技能 | 描述 | 驗證方法 |
|------|------|----------|
| **機器學習** | 能夠使用 scikit-learn、TensorFlow | 實現一個簡單的 ML 模型 |
| **實時數據流** | 能夠使用 Kafka、WebSocket | 實現一個實時數據推送功能 |
| **Kubernetes** | 能夠在 K8s 上部署應用 | 部署一個微服務到 K8s |

---

## 6. 知識模塊優先級

### 6.1 後端架構知識優先級

| 模塊 | 優先級 | 學習時間 | 關鍵知識點 |
|------|--------|----------|------------|
| **FastAPI 基礎** | P0 | 2-3 天 | 路由、依賴注入、Pydantic、異步編程 |
| **DuckDB 基礎** | P0 | 1-2 天 | SQL 查詢、數據庫操作、pandas 整合 |
| **Repository 模式** | P0 | 1 天 | 數據訪問層抽象、CRUD 操作 |
| **服務層設計** | P1 | 2 天 | 業務邏輯封裝、服務間協作 |
| **VectorBT 回測** | P0 | 3-4 天 | 向量化操作、信號生成、組合創建 |
| **Backtrader 回測** | P1 | 2-3 天 | 策略類、Cerebro、數據饋送 |
| **策略引擎架構** | P1 | 3-4 天 | IStrategy 接口、StrategyFactory、SignalAdapter |
| **認證授權** | P1 | 2 天 | JWT、Session、依賴注入 |
| **中間件** | P2 | 1 天 | 認證、CORS、Rate Limiting |
| **性能優化** | P2 | 2-3 天 | 緩存、索引、並行處理 |

### 6.2 前端架構知識優先級

| 模塊 | 優先級 | 學習時間 | 關鍵知識點 |
|------|--------|----------|------------|
| **React 19 Hooks** | P0 | 2-3 天 | useState, useEffect, useMemo, useCallback |
| **React Router v7** | P0 | 1 天 | 路由配置、導航、保護路由 |
| **Zustand** | P0 | 1-2 天 | Store 定義、Actions、Selectors |
| **React Query** | P0 | 3-4 天 | useQuery, useMutation, 緩存管理 |
| **Axios** | P0 | 1 天 | 實例配置、攔截器、錯誤處理 |
| **Bootstrap 5** | P0 | 1-2 天 | 組件、Grid、響應式設計 |
| **React Bootstrap** | P0 | 1 天 | React 組件封裝 |
| **Chart.js** | P1 | 2 天 | 圖表配置、數據綁定、交互 |
| **ECharts** | P2 | 2-3 天 | 高級圖表、主題、插件 |
| **Three.js** | P3 | 4-5 天 | 3D 場景、材質、渲染 |
| **React Testing Library** | P0 | 2 天 | render、screen、fireEvent |
| **Cypress** | P2 | 2-3 天 | E2E 測試、頁面對象、選擇器 |

### 6.3 策略引擎知識優先級

| 模塊 | 優先級 | 學習時間 | 關鍵知識點 |
|------|--------|----------|------------|
| **IStrategy 接口** | P0 | 1 天 | generate_signals、ExecutionContext、StrategySignal |
| **SignalAction 枚舉** | P0 | 0.5 天 | BUY、SELL、HOLD |
| **StrategyFactory** | P0 | 1 天 | 策略註冊、策略創建 |
| **SignalAdapter** | P0 | 1-2 天 | 信號轉換、DataFrame 轉換 |
| **ExecutionContextFactory** | P1 | 1 天 | 上下文創建、狀態管理 |
| **UnifiedStrategyEngine** | P1 | 2-3 天 | 回測流程、數據加載、結果格式化 |
| **CompositeStrategy** | P2 | 2-3 天 | 信號合併、多策略組合 |
| **SignalMerger** | P2 | 2 天 | 合併算法、投票機制 |
| **技術指標實現** | P1 | 3-4 天 | RSI、MACD、移動平均線、pandas-ta |
| **策略模式** | P1 | 2-3 天 | 趨勢跟蹤、均值回歸、動量 |

### 6.4 開發流程知識優先級

| 模塊 | 優先級 | 學習時間 | 關鍵知識點 |
|------|--------|----------|------------|
| **Conventional Commits** | P0 | 0.5 天 | 提交格式、提交類型、子類型 |
| **Git Flow** | P1 | 1 天 | 分支策略、分支命名、合併流程 |
| **代碼審查** | P1 | 1-2 天 | 審查標準、反饋技巧、PR 模板 |
| **單元測試** | P0 | 2-3 天 | pytest、vitest、AAA 模式 |
| **集成測試** | P1 | 2 天 | API 測試、服務層測試 |
| **E2E 測試** | P2 | 2-3 天 | Cypress、頁面对象、測試數據 |
| **Docker** | P2 | 2-3 天 | Dockerfile、docker-compose、鏡像構建 |
| **CI/CD** | P2 | 2-3 天 | GitHub Actions、workflow 配置 |
| **代碼質量工具** | P0 | 1 天 | ruff、black、eslint、pre-commit |
| **調試工具** | P0 | 1 天 | pdb、console.log、React DevTools |

### 6.5 最佳實踐優先級

| 模塊 | 優先級 | 學習時間 | 關鍵知識點 |
|------|--------|----------|------------|
| **SOLID 原則** | P1 | 1 天 | 單一職責、開閉原則、里氏替換、接口隔離、依賴倒置 |
| **設計模式** | P1 | 2-3 天 | 工廠、適配器、策略、單例、觀察者 |
| **代碼異味** | P1 | 1 天 | 重複代碼、過長函數、上帝類、特性依戀 |
| **重構策略** | P1 | 2 天 | 提取方法、提取類、重命名參數、引入參數對象 |
| **TDD** | P1 | 2-3 天 | 紅-綠-重構循環、測試金字塔 |
| **文檔編寫** | P1 | 1-2 天 | docstrings、JSDoc、API 文檔、架構文檔 |
| **安全最佳實踐** | P1 | 1 天 | 輸入驗證、輸出編碼、認證授權、HTTPS |
| **性能最佳實踐** | P2 | 2-3 天 | 緩存、索引、異步、並行 |

---

## 7. 學習路徑建議

### 7.1 新手入門路徑（1-2 個月）

**目標：** 掌握 P0 必備能力，能夠完成簡單的開發任務

**第一週：開發環境設置**
- [ ] 設置 Python 開發環境（Python 3.11、pip、venv）
- [ ] 設置 Node.js 開發環境（Node 24、npm、vite）
- [ ] 安裝和配置 Docker
- [ ] 克隆 Dashboard 項目並啟動本地環境
- [ ] 學習 Git 基礎操作（clone、add、commit、push）

**第二週：後端基礎**
- [ ] 學習 FastAPI 基礎（路由、依賴注入、Pydantic）
- [ ] 學習 DuckDB 基礎（SQL 查詢、數據庫操作）
- [ ] 實現一個簡單的 CRUD API 端點
- [ ] 編寫第一個 pytest 單元測試
- [ ] 學習 Conventional Commits 規範

**第三週：前端基礎**
- [ ] 學習 React 19 基礎（JSX、組件、Props）
- [ ] 學習 React Hooks（useState、useEffect）
- [ ] 學習 React Router v7
- [ ] 學習 Bootstrap 5
- [ ] 創建一個簡單的頁面組件

**第四週：API 集成**
- [ ] 學習 Axios
- [ ] 學習 React Query（useQuery、useMutation）
- [ ] 實現一個完整的數據加載和緩存流程
- [ ] 學習 Zustand
- [ ] 實現一個全局狀態管理模塊

**第五週：測試和調試**
- [ ] 深入學習 pytest（fixture、mock、parametrize）
- [ ] 深入學習 vitest（組件測試、happy-dom）
- [ ] 學習調試工具（pdb、console.log、React DevTools）
- [ ] 實現 TDD 流程
- [ ] 達到 >80% 測試覆蓋率

**第六週：整合實戰**
- [ ] 選擇一個小的功能開發任務
- [ ] 設計實現方案
- [ ] 使用 TDD 開發功能
- [ ] 編寫文檔
- [ ] 提交 PR 並參與代碼審查

**第七週：代碼質量**
- [ ] 學習 ruff、black、eslint
- [ ] 配置 pre-commit hooks
- [ ] 學習代碼審查標準
- [ ] 審查 2-3 個 PR
- [ ] 修復審查反饋的問題

**第八週：項目實戰**
- [ ] 完成一個完整的功能模塊
- [ ] 包括後端 API、前端 UI、測試、文檔
- [ ] 通過所有代碼質量檢查
- [ ] 合併到主分支
- [ ] 總結和反思

**關鍵里程碑：**
- ✅ 能夠獨立開發簡單的 API 端點
- ✅ 能夠獨立開發簡單的頁面組件
- ✅ 能夠編寫 >80% 覆蓋率的測試
- ✅ 能夠遵循 Conventional Commits 規範
- ✅ 能夠通過所有代碼質量檢查

### 7.2 進階提升路徑（2-3 個月）

**目標：** 掌握 P1 重要能力，能夠完成複雜的開發任務

**第一階段：量化交易基礎（2週）**
- [ ] 學習量化交易基本概念（Alpha、Beta、夏普比率）
- [ ] 學習技術指標（RSI、MACD、移動平均線）
- [ ] 學習 VectorBT 基礎（向量化操作、信號生成）
- [ ] 實現一個簡單的技術指標
- [ ] 使用 VectorBT 進行回測

**第二階段：策略引擎架構（3週）**
- [ ] 深入學習 IStrategy 接口
- [ ] 學習 StrategyFactory 模式
- [ ] 學習 SignalAdapter 轉換
- [ ] 實現一個符合 IStrategy 接口的策略
- [ ] 註冊並使用自定義策略
- [ ] 實現複合策略和信號合併

**第三階段：Backtrader 回測（2週）**
- [ ] 學習 Backtrader 基礎（策略類、Cerebro）
- [ ] 學習數據饋送（Data Feeds）
- [ ] 實現一個 Backtrader 策略
- [ ] 對比 Backtrader 和 VectorBT 的結果
- [ ] 優化回測性能

**第四階段：高級開發技能（3週）**
- [ ] 學習重構策略（識別代碼異味、應用設計模式）
- [ ] 學習性能優化（識別瓶頸、實施優化）
- [ ] 學習集成測試（API 測試、服務層測試）
- [ ] 學習 E2E 測試（Cypress）
- [ ] 重構一個現有模塊
- [ ] 優化一個性能瓶頸

**第五階段：開發流程（2週）**
- [ ] 深入學習 Git Flow 分支策略
- [ ] 學習代碼審查技巧
- [ ] 學習問題診斷方法
- [ ] 學習文檔編寫最佳實踐
- [ ] 參與 5-10 個代碼審查
- [ ] 調試並修復 3 個生產問題

**第六階段：Docker 和 CI/CD（2週）**
- [ ] 深入學習 Docker（Dockerfile、docker-compose）
- [ ] 構建並運行 Dashboard 的 Docker 容器
- [ ] 學習 GitHub Actions 基礎
- [ ] 配置 CI workflow（lint、test、build）
- [ ] 配置 CD workflow（deploy）
- [ ] 實現自動化部署流程

**第七階段：高級前端（2週）**
- [ ] 深入學習 React Query（緩存策略、優化）
- [ ] 學習 Chart.js 高級功能
- [ ] 學習 ECharts 基礎
- [ ] 實現一個交互式圖表組件
- [ ] 學習 React Query DevTools

**第八階段：項目實戰（2週）**
- [ ] 選擇一個複雜的功能開發任務
- [ ] 設計完整的實現方案
- [ ] 使用 TDD 開發功能
- [ ] 包括後端、前端、測試、文檔、部署
- [ ] 通過所有代碼質量檢查
- [ ] 合併到主分支
- [ ] 進行代碼審查

**關鍵里程碑：**
- ✅ 能夠實現符合 IStrategy 接口的策略
- ✅ 能夠使用 VectorBT 和 Backtrader 進行回測
- ✅ 能夠重構和優化代碼
- ✅ 能夠編寫集成測試和 E2E 測試
- ✅ 能夠配置 CI/CD 流程
- ✅ 能夠參與代碼審查並提供建設性反饋

### 7.3 專家級路徑（3-6 個月）

**目標：** 掌握 P2/P3 擴展能力，能夠進行架構設計和技術領導

**第一階段：系統架構設計（1個月）**
- [ ] 深入學習分層架構設計
- [ ] 學習微服務架構
- [ ] 學習數據架構設計
- [ ] 設計一個完整的系統架構
- [ ] 編寫架構設計文檔

**第二階段：技術選型決策（2週）**
- [ ] 學習技術選型方法
- [ ] 編寫技術決策記錄（ADR）
- [ ] 進行技術選型評估
- [ ] 記錄決策過程和理由
- [ ] 進行技術分享

**第三階段：高級性能優化（3週）**
- [ ] 深入學習性能分析工具
- [ ] 學習數據庫優化（索引、查詢優化）
- [ ] 學習緩存策略（Redis、React Query）
- [ ] 學習並行處理（multiprocessing、asyncio）
- [ ] 優化一個性能瓶頸
- [ ] 設定性能基準並監控

**第四階段：機器學習基礎（1個月）**
- [ ] 學習 scikit-learn 基礎
- [ ] 學習數據預處理
- [ ] 實現一個簡單的 ML 模型
- [ ] 將 ML 模型集成到 Dashboard
- [ ] 實現模型預測 API

**第五階段：實時數據流（2週）**
- [ ] 學習 WebSocket 基礎
- [ ] 實現一個實時數據推送功能
- [ ] 學習 Kafka 基礎（可選）
- [ ] 實現一個事件驅動的架構

**第六階段：Kubernetes（1個月）**
- [ ] 學習 Kubernetes 基礎
- [ ] 學習 Docker 鏡像優化
- [ ] 部署 Dashboard 到 Kubernetes
- [ ] 實現滾動更新和回滾
- [ ] 配置監控和日誌

**第七階段：團隊技術領導力（持續）**
- [ ] 指導 2-3 名初級開發者
- [ ] 進行技術分享和培訓
- [ ] 參與技術規劃和路線圖制定
- [ ] 建立開發者社區和文化
- [ ] 參與開源項目

**第八階段：專業發展（持續）**
- [ ] 學習領域知識（金融、數據科學）
- [ ] 參加技術會議和社群活動
- [ ] 閱讀技術博客和論文
- [ ] 寫技術博客和文章
- [ ] 參與技術討論和評論

**關鍵里程碑：**
- ✅ 能夠設計完整的系統架構
- ✅ 能夠進行技術選型並記錄決策
- ✅ 能夠優化性能瓶頸
- ✅ 能夠實現 ML 模型並集成
- ✅ 能夠部署到 Kubernetes
- ✅ 能夠指導初級開發者
- ✅ 能夠進行技術分享

---

## 8. 評估標準

### 8.1 能力評估指標

#### A. 開發能力評估

| 指標 | 描述 | 評估方法 | 目標值 |
|------|------|----------|--------|
| **API 端點開發** | 能夠獨立開發 API 端點 | 代碼審查、功能測試 | 100% 獨立完成 |
| **組件開發** | 能夠獨立開發 React 組件 | 代碼審查、UI 測試 | 100% 獨立完成 |
| **API 集成** | 能夠集成後端 API | E2E 測試、用戶測試 | 100% 功能正常 |
| **策略實現** | 能夠實現符合 IStrategy 接口的策略 | 單元測試、回測驗證 | 100% 通過 |
| **回測執行** | 能夠使用 VectorBT/Backtrader 執行回測 | 性能測試、結果驗證 | 100% 成功 |

#### B. 測試能力評估

| 指標 | 描述 | 評估方法 | 目標值 |
|------|------|----------|--------|
| **單元測試覆蓋率** | 單元測試覆蓋的代碼比例 | pytest-cov、vitest coverage | >80% |
| **測試通過率** | 測試通過的數量/總數 | pytest、vitest | 100% |
| **集成測試覆蓋** | 關鍵路徑的集成測試覆蓋 | 手動檢查 | >90% |
| **E2E 測試覆蓋** | 關鍵用戶流程的 E2E 測試覆蓋 | 手動檢查 | >80% |
| **測試質量** | 測試的可讀性和可維護性 | 代碼審查 | 優良 |

#### C. 代碼質量評估

| 指標 | 描述 | 評估方法 | 目標值 |
|------|------|----------|--------|
| **代碼規範遵循** | 遵循項目代碼風格 | ruff、black、eslint | 100% 通過 |
| **代碼審查通過率** | PR 一次性通過的比例 | GitHub Actions | >80% |
| **技術債積累** | 新增技術債的數量 | 代碼審查 | 最小化 |
| **Bug 密度** | 代碼中的 bug 數量/千行代碼 | Bug 追蹤系統 | <1 |
| **代碼重複率** | 重複代碼的比例 | SonarQube、手動檢查 | <3% |

#### D. 流程遵循評估

| 指標 | 描述 | 評估方法 | 目標值 |
|------|------|----------|--------|
| **Conventional Commits** | 提交信息規範遵循 | Git 歷史分析 | 100% |
| **PR 描述質量** | PR 描述的完整性和清晰度 | 代碼審查 | 優良 |
| **文檔完整性** | 代碼和 API 文檔的完整性 | 手動檢查 | >90% |
| **代碼審查參與** | 參與代碼審查的頻率和質量 | GitHub 記錄 | >5 PR/週 |
| **CI/CD 通過率** | CI/CD 流程通過的比例 | GitHub Actions | >95% |

### 8.2 測試/驗證方法

#### A. 實戰任務測試

**新手級任務：**
1. 創建一個簡單的 CRUD API 端點（GET、POST、PUT、DELETE）
2. 創建一個簡單的頁面組件（顯示列表、分頁、搜索）
3. 實現一個完整的 API 集成（數據加載、緩存、錯誤處理）
4. 編寫 >80% 覆蓋率的測試
5. 提交 10 個符合 Conventional Commits 規範的 commit

**進階級任務：**
1. 實現一個符合 IStrategy 接口的策略（RSI、MACD 等）
2. 使用 VectorBT 進行回測並驗證結果
3. 實現複合策略和信號合併
4. 重構一個現有模塊並提升代碼質量
5. 編寫集成測試和 E2E 測試
6. 參與 5-10 個代碼審查並提供建設性反饋
7. 配置 CI/CD 流程並實現自動化部署

**專家級任務：**
1. 設計一個完整的系統架構（包括數據架構）
2. 進行技術選型並編寫技術決策記錄
3. 優化一個性能瓶頸並提升 5-10x 性能
4. 實現一個 ML 模型並集成到 Dashboard
5. 實現一個實時數據推送功能
6. 部署 Dashboard 到 Kubernetes
7. 指導 2-3 名初級開發者

#### B. 筆試/面試測試

**技術知識筆試：**
- Python/FastAPI 基礎知識
- React 19 Hooks 基礎知識
- 量化交易基本概念
- 技術指標計算
- Git/Conventional Commits 規範
- 測試驅動開發（TDD）概念
- 設計模式和架構原則

**編程實戰測試：**
- 在 1 小時內實現一個簡單的 API 端點
- 在 1 小時內實現一個簡單的 React 組件
- 在 2 小時內實現一個完整的策略
- 在 2 小時內重構一個模塊

**系統設計測試：**
- 設計一個量化交易系統的架構
- 設計一個高性能 API 系統的架構
- 設計一個實時數據處理系統的架構

### 8.3 改進建議

#### A. 個人改進計劃

**短期改進（1-2 個月）：**
1. **提升測試覆蓋率**
   - 設定測試覆蓋率目標（後端 >80%，前端 >70%）
   - 使用 TDD 開發新功能
   - 定期審查測試覆蓋率報告

2. **改善代碼質量**
   - 學習並使用代碼質量工具（ruff、black、eslint）
   - 參與代碼審查並接受反饋
   - 閱讀優秀代碼並學習最佳實踐

3. **提升開發效率**
   - 學習快捷鍵和 IDE 插件
   - 學習自動化工具（pre-commit、CI/CD）
   - 學調試技巧

**中期改進（2-3 個月）：**
1. **深入量化交易知識**
   - 學習技術指標和策略模式
   - 學習回測框架（VectorBT、Backtrader）
   - 實現並測試多個策略

2. **提升架構能力**
   - 學習設計模式和架構原則
   - 學習微服務架構
   - 參與架構設計和技術選型

3. **提升溝通和協作能力**
   - 學習代碼審查技巧
   - 學習技術文檔編寫
   - 學習技術分享和演示

**長期改進（3-6 個月）：**
1. **專業發展**
   - 學習領域知識（金融、數據科學）
   - 參加技術會議和社群活動
   - 閱讀技術博客和論文

2. **技術領導力**
   - 指導初級開發者
   - 進行技術分享和培訓
   - 參與技術規劃和路線圖制定

3. **開源貢獻**
   - 參與開源項目
   - 貢獻到 Dashboard 項目
   - 建立個人技術品牌

#### B. 團隊改進計劃

**短期改進：**
1. **建立測試文化**
   - 設定測試覆蓋率目標
   - 強制執行測試要求
   - 獎勵高測試覆蓋率

2. **建立代碼審查文化**
   - 制定代碼審查標準
   - 強制執行代碼審查
   - 獎勵優質審查

3. **建立文檔文化**
   - 制定文檔編寫標準
   - 強制執行文檔要求
   - 獎勵優質文檔

**中期改進：**
1. **建立技術分享機制**
   - 定期技術分享會
   - 技術博客內部發布
   - 技術培訓和培養

2. **建立技術債管理機制**
   - 定期技術債審查
   - 制定技術債償還計劃
   - 監控技術債趨勢

3. **建立性能優化機制**
   - 定期性能評估
   - 制定性能優化計劃
   - 監控性能指標

**長期改進：**
1. **建立創新機制**
   - 鼓勵新想法和創新
   - 提供創新資源和支持
   - 獎勵創新成果

2. **建立人才培養機制**
   - 制定職業發展路徑
   - 提供培訓和指導
   - 建立晉升機制

3. **建立開放文化**
   - 鼓勵開源貢獻
   - 鼓勵技術分享
   - 鼓勵社群參與

---

## 9. 元數據

### 9.1 文檔信息

| 屬性 | 值 |
|------|-----|
| **文檔版本** | 1.0 |
| **生成時間** | 2026-02-21T00:43:00+08:00 |
| **作者** | Charlie Analyst (Sub-Agent) |
| **任務 ID** | a005-competencies |
| **狀態** | completed |

### 9.2 相關文檔

| 文檔 | 路徑 |
|------|------|
| **後端架構整合報告** | `/Users/charlie/.openclaw/workspace/kanban/projects/programmer-agent-design-20260220/a001-backend-architecture.md` |
| **前端架構整合報告** | `/Users/charlie/.openclaw/workspace/kanban/projects/programmer-agent-design-20260220/a002-frontend-architecture.md` |
| **統一策略引擎分析** | `/Users/charlie/.openclaw/workspace/kanban/projects/programmer-agent-design-20260220/a003-unified-strategy-engine.md` |
| **Git 開發模式報告** | `/Users/charlie/.openclaw/workspace/kanban/projects/programmer-agent-design-20260220/a004-git-development-pattern.md` |

### 9.3 下一步行動

此報告將作為 **a006（Programmer Sub-Agent 設計規劃）** 的直接輸入，用於：

1. **定義 Sub-Agent 核心能力**：基於 P0/P1 能力定義
2. **設計知識庫結構**：基於知識模塊優先級
3. **規劃學習路徑**：基於新手/進階/專家級路徑
4. **設計評估機制**：基於評估標準
5. **定義技能樹**：基於能力矩陣

### 9.4 反饋和改進

如有任何反饋或改進建議，請聯繫：
- **分析者**：Charlie Analyst (Sub-Agent)
- **請求者**：Charlie (Main Orchestrator)
- **項目**：Dashboard (/Users/charlie/Dashboard)

---

**文檔結束**
