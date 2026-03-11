# 交易分析系統開發需求

## 目標
基於 410 筆 Supertrend 實際交易數據，開發分析工具驗證第一性原理：
1. 假突破檢測（盤整期的 whipsaw）
2. 趨勢持久度（持倉時間 vs 報酬率）
3. 市場狀態影響（ADX、ATR、波動率）
4. 期望值建模（E[收益] = Σ P(狀態) × E[狀態收益]）

---

## 模塊 1: 交易數據解析器

### 輸入
```python
# 交易歷史數據（CSV 格式）
trade_data = [
    {
        "股票代碼": "2356.TW",
        "進場日期": "2026-01-22",
        "出場日期": "2026-02-03",
        "類型": "long",
        "進場價": 48.65,
        "出場價": 44.65,
        "數量": 57.124,
        "報酬率": -0.09  # 百分比
    },
    # ... 410 筆
]
```

### 輸出
```python
class Trade:
    stock_code: str
    entry_date: datetime
    exit_date: datetime
    entry_price: float
    exit_price: float
    quantity: float
    return_pct: float
    holding_days: int
    market_state: Optional[MarketState]  # 後續填充
```

### 功能
1. 解析 CSV（處理缺失值、格式轉換）
2. 計算持倉天數
3. 計算實際報酬率（驗證數據一致性）
4. 基礎統計（總交易、勝率、平均報酬）

---

## 模塊 2: 市場狀態回溯引擎

### 目標
為每筆交易獲取期間的歷史價格數據，計算市場狀態指標

### 輸入
```python
trade: Trade  # 從模塊 1 生成
lookback_days: int = 30  # 進場前 N 天的數據
```

### 流程
```python
def get_market_state(trade: Trade, lookback_days: int = 30) -> MarketState:
    """
    步驟：
    1. 從 API 獲取歷史價格數據（yfinance 或 Dashboard API）
       - 範圍：entry_date - lookback_days 到 exit_date
       - 數據：OHLCV（開高低收量）

    2. 計算技術指標
       - ADX（14 期）：趨勢強度
       - ATR（14 期）：波動率
       - Supertrend（與交易相同參數）：驗證交易點

    3. 識別市場狀態
       - ADX < 20: 無趨勢（盤整）
       - 20 ≤ ADX < 50: 中等趨勢
       - ADX ≥ 50: 強趨勢

       - 進場時 Supertrend 方向 vs 實際價格走勢
         * 一致 → 可能真趨勢
         * 翻轉 → 可能假突破

    4. 計算期間統計
       - 最大回撤（Max Drawdown）
       - 最大盈利（Max Profit）
       - 波動率（Standard Deviation）
    """
```

### 輸出
```python
class MarketState:
    adx_at_entry: float          # 進場時的 ADX
    atr_at_entry: float          # 進場時的 ATR
    trend_strength: str          # "無趨勢", "中等", "強"
    volatility_level: str       # "低", "中", "高"

    # 假突破檢測
    supertrend_flips: int       # 交易期間 ST 翻轉次數
    is_fake_breakout: bool      # 是否為假突破
    fake_breakout_score: float  # 0-1 分數

    # 期間統計
    max_profit: float           # 期間最大盈利（%）
    max_drawdown: float         # 期間最大回撤（%）
    price_volatility: float     # 價格波動率

    # 趨勢一致性
    is_trend_aligned: bool      # ST 方向與價格走勢是否一致
    trend_alignment_score: float  # 0-1 分數
```

### API 來源選項
1. **優先：Dashboard API**
   ```python
   # 如果 Dashboard 有歷史價格 API
   GET /api/market/history?symbol={symbol}&start={start_date}&end={end_date}
   ```

2. **備用：yfinance**
   ```python
   import yfinance as yf
   ticker = yf.Ticker(symbol.replace(".TW", ".TW"))
   data = ticker.history(start=start_date, end=end_date, interval="1d")
   ```

3. **緩存機制**
   ```python
   # 避免重複請求同一支股票的相同日期範圍
   cache_key = f"{symbol}:{start_date}:{end_date}"
   if cache_key in price_cache:
       return price_cache[cache_key]
   ```

---

## 模塊 3: 假突破檢測器

### 目標
識別哪些交易可能是假突破（盤整期的 whipsaw）

### 判斷標準
```python
def detect_fake_breakout(trade: Trade, market_state: MarketState) -> bool:
    """
    假突破的 3 個條件（滿足任意 2 個即判斷為假突破）：

    1. 趨勢弱
       - market_state.adx_at_entry < 25

    2. 持倉時間短且虧損
       - trade.holding_days <= 14
       - trade.return_pct < 0

    3. Supertrend 頻繁翻轉
       - market_state.supertrend_flips >= 2

    4. 波動率低
       - market_state.atr_at_entry / trade.entry_price < 0.02
    """

    conditions = []

    # 條件 1：趨勢弱
    if market_state.adx_at_entry < 25:
        conditions.append("趨勢弱（ADX < 25）")

    # 條件 2：短持倉且虧損
    if trade.holding_days <= 14 and trade.return_pct < 0:
        conditions.append("短持倉且虧損（≤14天）")

    # 條件 3：ST 頻繁翻轉
    if market_state.supertrend_flips >= 2:
        conditions.append("ST 頻繁翻轉（≥2次）")

    # 條件 4：低波動率
    volatility_ratio = market_state.atr_at_entry / trade.entry_price
    if volatility_ratio < 0.02:
        conditions.append("低波動率（ATR/Price < 2%）")

    # 滿足至少 2 個條件
    is_fake = len(conditions) >= 2

    return is_fake, conditions
```

### 輸出
```python
class FakeBreakoutAnalysis:
    is_fake_breakout: bool
    confidence_score: float  # 0-1，基於滿足條件數量
    reasons: List[str]       # 觸發的條件
    alternative_decision: str  # "應該進場", "應該等待", "不確定"
```

---

## 模塊 4: 趨勢持久度分析器

### 目標
分析持倉時間與報酬率的關係，驗證趨勢慣性假設

### 分析邏輯
```python
def analyze_trend_persistence(trades: List[Trade]) -> TrendPersistenceReport:
    """
    1. 按持倉時間分組
       - 短期：< 14 天
       - 中期：14-30 天
       - 長期：> 30 天

    2. 計算每組統計
       - 平均報酬率
       - 勝率
       - 盈虧比
       - 標準差

    3. 統計檢驗
       - t 檢驗：長期 vs 短期的報酬率差異
       - 卡方檢驗：勝率差異
    """

    # 分組
    short_trades = [t for t in trades if t.holding_days < 14]
    medium_trades = [t for t in trades if 14 <= t.holding_days <= 30]
    long_trades = [t for t in trades if t.holding_days > 30]

    # 計算統計
    short_stats = calculate_stats(short_trades)
    medium_stats = calculate_stats(medium_trades)
    long_stats = calculate_stats(long_trades)

    # 統計檢驗
    from scipy import stats
    t_stat, p_value = stats.ttest_ind(
        [t.return_pct for t in long_trades],
        [t.return_pct for t in short_trades]
    )

    is_significant = p_value < 0.05  # 顯著性水平 5%

    return TrendPersistenceReport(
        short_stats=short_stats,
        medium_stats=medium_stats,
        long_stats=long_stats,
        t_test_p_value=p_value,
        is_long_term_significantly_better=is_significant
    )
```

### 輸出
```python
class TrendPersistenceReport:
    short_stats: TradeGroupStats    # 短期組統計
    medium_stats: TradeGroupStats    # 中期組統計
    long_stats: TradeGroupStats     # 長期組統計

    # 統計檢驗
    t_test_p_value: float            # t 檢驗 p 值
    is_long_term_significantly_better: bool

    # 結論
    recommendation: str              # "優先長持倉", "無明顯差異", "優先短持倉"
    confidence_level: float         # 0-1
```

---

## 模塊 5: 期望值建模器

### 目標
建立基於市場狀態的期望收益模型

### 模型結構
```python
class ExpectedReturnModel:
    """
    E[收益] = Σ P(狀態_i) × E[狀態_i收益]

    狀態定義：
    - 弱趨勢（ADX < 25）
    - 中等趨勢（25 ≤ ADX < 50）
    - 強趨勢（ADX ≥ 50）

    對於每個狀態：
    - P(狀態)：歷史該狀態的交易比例
    - E[狀態收益]：該狀態下交易的平均報酬率
    """

    def fit(self, trades: List[Trade]):
        """用歷史數據訓練模型"""
        self.state_returns = {}
        self.state_probabilities = {}

        for state in ["weak", "medium", "strong"]:
            state_trades = [t for t in trades if t.market_state.trend_strength == state]

            # P(狀態)
            self.state_probabilities[state] = len(state_trades) / len(trades)

            # E[狀態收益]
            self.state_returns[state] = np.mean([t.return_pct for t in state_trades])

    def predict(self, market_state: MarketState) -> float:
        """預測當前市場狀態下的期望收益"""
        state = market_state.trend_strength
        expected_return = self.state_returns[state]

        # 應用置信區間
        if state == "weak":
            # 弱趨勢時，期望收益不穩定
            return expected_return * 0.5
        elif state == "strong":
            # 強趨勢時，期望收益較可靠
            return expected_return * 1.0
        else:
            return expected_return * 0.8

    def calculate_overall_expectation(self) -> float:
        """計算整體期望收益"""
        expected_value = sum(
            self.state_probabilities[state] * self.state_returns[state]
            for state in self.state_probabilities
        )
        return expected_value
```

### 輸出
```python
class ExpectationReport:
    overall_expected_return: float     # 整體期望收益（%）
    state_expectations: Dict[str, float]  # 各狀態期望收益
    state_probabilities: Dict[str, float]  # 各狀態概率

    # 交易建議
    recommended_min_holding_days: int   # 建議最小持倉天數
    recommended_filter_threshold: float # 建議過濾門檻（ADX）
```

---

## 模塊 6: 視覺化儀表板

### 前端組件需求

#### 1. 交易分布圖
```typescript
// 持倉時間 vs 報酬率 散點圖
interface TradeScatterChartProps {
  trades: Trade[]
  x: 'holding_days'      // X 軸
  y: 'return_pct'        // Y 軸
  color: 'is_fake_breakout'  // 顏色分組
}

// 輸出：散點圖，顯示趨勢和假突破標記
```

#### 2. 市場狀態分布圖
```typescript
// 餅圖：假突破 vs 真趨勢
interface FakeBreakoutPieChartProps {
  trades: Trade[]
  breakdownBy: 'market_state' | 'holding_days'
}

// 輸出：餅圖，顯示假突破比例
```

#### 3. 報酬率分布直方圖
```typescript
interface ReturnDistributionHistogramProps {
  trades: Trade[]
  bins: number = 20  // 分桶數量
  groupBy?: 'holding_days' | 'market_state'  // 可選分組
}

// 輸出：直方圖，顯示報酬率分布
```

#### 4. 時間序列圖
```typescript
// 累積收益曲線
interface CumulativeReturnChartProps {
  trades: Trade[]
  filter?: (trade: Trade) => boolean  // 可選過濾器
}

// 輸出：累積收益曲線，可對比不同策略
```

---

## 技術棧建議

### 後端
- **Python**（數據分析優勢）
- **Pandas**（數據處理）
- **NumPy**（數值計算）
- **SciPy**（統計檢驗）
- **yfinance** 或 **Dashboard API**（數據來源）

### 前端
- **React + TypeScript**（Dashboard 現有技術棧）
- **Recharts** 或 **Chart.js**（圖表庫）
- **Ant Design**（UI 組件）

### 集成到 Dashboard
```python
# 新增 API 路由
@router.post("/analysis/trade-stats")
async def analyze_trades(
    trade_data: List[Trade],
    lookback_days: int = 30
) -> AnalysisReport:
    """
    1. 解析交易數據
    2. 回溯市場狀態
    3. 檢測假突破
    4. 分析趨勢持久度
    5. 建立期望值模型
    """
    return full_analysis_pipeline(trade_data, lookback_days)
```

---

## 開發優先級

### P0（必須）
1. ✅ 模塊 1: 交易數據解析器
2. ✅ 模塊 2: 市場狀態回溯引擎
3. ✅ 模塊 3: 假突破檢測器

### P1（重要）
4. 模塊 4: 趨勢持久度分析器
5. 模塊 5: 期望值建模器

### P2（優化）
6. 模塊 6: 視覺化儀表板
7. 性能優化（數據緩存、並行計算）

---

## 驗收標準

### 功能測試
- [ ] 能正確解析 410 筆交易數據
- [ ] 能獲取每筆交易期間的歷史價格數據
- [ ] 能計算 ADX、ATR、Supertrend 等指標
- [ ] 能正確識別假突破（至少 70% 準確率）
- [ ] 能生成趨勢持久度報告

### 性能測試
- [ ] 分析 410 筆交易 < 30 秒
- [ ] API 響應時間 < 5 秒
- [ ] 前端圖表渲染 < 2 秒

### 數據驗證
- [ ] 報酬率計算與數據一致
- [ ] 持倉天數計算正確
- [ ] ADX、ATR 計算與第三方工具一致

---

## 後續優化方向

### 1. 實時監控
- 運行中的交易實時計算市場狀態
- 預警潛在假突破

### 2. 機器學習
- 用歷史數據訓練分類模型（假突破 vs 真趨勢）
- 特徵工程：ADX、ATR、持倉時間、報酬率

### 3. 策略優化
- 基於分析結果調整 Supertrend 參數
- 測試不同的過濾條件（ADX 閾值、持倉時間）

---

**文檔版本**: v1.0
**創建日期**: 2026-02-28
**優先級**: P0
**預估工期**: 3-5 天
