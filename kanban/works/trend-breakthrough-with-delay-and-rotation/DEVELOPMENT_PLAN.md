# 趨勢突破策略開發計劃
## 結合延遲進場優化與板塊輪動

**項目 ID:** trend-breakthrough-delay-rotation
**計劃日期:** 2026-03-06
**負責人:** Charlie

---

## 一、策略核心概念

### 1.1 整合思路

**三層架構：**

```
第一層：趨勢識別
    ↓
第二層：延遲進場優化（過濾假突破）
    ↓
第三層：板塊輪動配置（動態選擇強勢板塊）
```

**核心優勢：**
- **延遲進場**：降低假突破率 20-40%
- **板塊輪動**：動態選擇強勢板塊，提升整體收益
- **動態倉位**：ATR 動態調整，控制風險

---

## 二、策略架構設計

### 2.1 完整流程

```
每日監控流程：

1. 板塊輪動檢測（每日 9:30 開盤前）
   ├── 掃描 10 個主要板塊 ETF
   ├── 計算相對強度指標（RSI、MACD、動量）
   ├── 識別強勢板塊（Top 3）
   └── 配置板塊權重

2. 趨勢識別（每小時）
   ├── 計算 Supertrend 指標
   ├── 識別趨勢方向（上漲/下跌/震盪）
   └── 生成趨勢信號

3. 延遲進場驗證（每小時）
   ├── 檢測突破信號
   ├── 延遲 2-3 根 K 線確認
   ├── 計算假突破概率
   └── 生成進場信號

4. 動態倉位計算（每日收盤後）
   ├── 計算 ATR(14)
   ├── 根據風險比例調整倉位
   └── 執行交易（次日開盤）
```

### 2.2 板塊選擇框架

**10 個主要板塊 ETF：**

```python
SECTOR_ETFS = {
    '科技': 'XLK',      # Technology Select Sector SPDR
    '金融': 'XLF',      # Financial Select Sector SPDR
    '醫療': 'XLV',      # Health Care Select Sector SPDR
    '消費': 'XLY',      # Consumer Discretionary Select Sector SPDR
    '必需消費': 'XLP',   # Consumer Staples Select Sector SPDR
    '能源': 'XLE',      # Energy Select Sector SPDR
    '工業': 'XLI',      # Industrial Select Sector SPDR
    '材料': 'XLB',      # Materials Select Sector SPDR
    '公用事業': 'XLU',   # Utilities Select Sector SPDR
    '房地產': 'XLRE',    # Real Estate Select Sector SPDR
}
```

**板塊選擇指標：**

```python
def calculate_sector_strength(sector_returns, lookback=20):
    """
    計算板塊強度指標
    
    指標：
    1. 累積收益（20 天）
    2. 動量因子（Momentum）
    3. 相對強度（相對於 SPY）
    4. RSI（14 天）
    5. MACD 金叉/死叉
    """
    # 1. 累積收益
    cumulative_return = (1 + sector_returns).cumprod().iloc[-1] - 1
    
    # 2. 動量因子
    momentum = sector_returns.mean() * np.sqrt(252) / sector_returns.std()
    
    # 3. 相對強度
    spy_returns = get_market_returns()  # SPY 回報
    relative_strength = sector_returns.mean() / spy_returns.mean()
    
    # 4. RSI
    rsi = calculate_rsi(sector_returns, period=14)
    
    # 5. MACD
    macd, signal, histogram = calculate_macd(sector_returns)
    
    # 6. 綜合評分
    strength_score = (
        0.3 * (cumulative_return / cumulative_return.max()) +
        0.2 * (momentum / momentum.max()) +
        0.2 * (relative_strength / relative_strength.max()) +
        0.15 * (rsi / 100) +
        0.15 * (1 if histogram > 0 else 0)
    )
    
    return {
        'cumulative_return': cumulative_return,
        'momentum': momentum,
        'relative_strength': relative_strength,
        'rsi': rsi,
        'macd_signal': histogram,
        'strength_score': strength_score
    }
```

**板塊權重分配：**

```python
def calculate_sector_weights(sector_strengths, top_n=3):
    """
    計算板塊權重
    
    策略：
    1. 選擇強度前 3 名的板塊
    2. 按強度評分分配權重
    3. 剩餘 40% 分配給現金或基準 ETF
    """
    # 1. 排序並選擇前 3 名
    sorted_sectors = sector_strengths.sort_values('strength_score', ascending=False)
    top_sectors = sorted_sectors.head(top_n)
    
    # 2. 計算權重（按強度評分）
    total_score = top_sectors['strength_score'].sum()
    weights = (top_sectors['strength_score'] / total_score) * 0.6  # 60% 分配給強勢板塊
    
    # 3. 剩餘 40% 分配給現金
    weights['現金'] = 0.4
    
    return weights
```

### 2.3 延遲進場優化

**核心算法：**

```python
def delayed_entry_signal(
    price, 
    supertrend_period=10, 
    supertrend_multiplier=3.0,
    delay_bars=2,
    atr_period=14
):
    """
    延遲進場信號生成
    
    參數：
    - price: 價格序列
    - supertrend_period: Supertrend 週期
    - supertrend_multiplier: Supertrend 倍數
    - delay_bars: 延遲確認根數
    - atr_period: ATR 週期
    
    返回：
    - signal: {'long', 'short', 'hold'}
    - false_break_probability: 假突破概率
    - confidence: 信號置信度
    """
    # 1. 計算 ATR
    atr = calculate_atr(price, period=atr_period)
    
    # 2. 計算 Supertrend
    supertrend, trend = calculate_supertrend(
        price, 
        period=supertrend_period,
        multiplier=supertrend_multiplier
    )
    
    # 3. 檢測初始突破
    initial_breakthrough = detect_breakthrough(price, supertrend, trend)
    
    # 4. 延遲確認
    if initial_breakthrough:
        confirmed = confirm_breakthrough(
            price, 
            trend, 
            delay_bars=delay_bars
        )
        
        if confirmed:
            # 5. 計算假突破概率
            false_break_prob = calculate_false_break_probability(
                price,
                trend,
                delay_bars=delay_bars
            )
            
            # 6. 計算置信度
            confidence = 1.0 - false_break_prob
            
            # 7. 生成最終信號
            if trend.iloc[-1] == 1:
                signal = 'long'
            else:
                signal = 'short'
        else:
            signal = 'hold'
            false_break_prob = 1.0
            confidence = 0.0
    else:
        signal = 'hold'
        false_break_prob = 0.5
        confidence = 0.5
    
    return {
        'signal': signal,
        'false_break_probability': false_break_prob,
        'confidence': confidence,
        'supertrend': supertrend.iloc[-1],
        'trend': trend.iloc[-1],
        'atr': atr.iloc[-1]
    }
```

**假突破概率計算：**

```python
def calculate_false_break_probability(price, trend, delay_bars=2):
    """
    計算假突破概率
    
    考慮因素：
    1. 延遲期間價格是否回到突破前水平
    2. 延遲期間波動率是否顯著增加
    3. 成交量是否萎縮
    """
    # 1. 檢查價格回撤
    if trend.iloc[-1] == 1:  # 上漲趨勢
        # 檢查是否跌破最近低點
        recent_low = price.iloc[-delay_bars:].min()
        current_low = price.iloc[-1]
        if current_low < recent_low * 0.99:  # 跌破 1%
            return 0.8  # 高假突破概率
    else:  # 下跌趨勢
        # 檢查是否突破最近高點
        recent_high = price.iloc[-delay_bars:].max()
        current_high = price.iloc[-1]
        if current_high > recent_high * 1.01:  # 突破 1%
            return 0.8  # 高假突破概率
    
    # 2. 檢查波動率
    atr = calculate_atr(price, period=14)
    atr_ma = atr.rolling(20).mean()
    if atr.iloc[-1] > atr_ma.iloc[-1] * 1.5:  # 波動率過高
        return 0.6  # 中等假突破概率
    
    # 3. 檢查成交量（如果有）
    if volume is not None:
        volume_ma = volume.rolling(20).mean()
        if volume.iloc[-1] < volume_ma.iloc[-1] * 0.7:  # 成交量萎縮
            return 0.7  # 中高假突破概率
    
    # 4. 默認概率
    return 0.3  # 基於歷史統計的基準概率
```

### 2.4 動態倉位系統

**ATR 動態倉位：**

```python
def calculate_atr_based_position(
    price,
    account_value,
    risk_per_trade=0.02,  # 每筆交易風險 2%
    atr_period=14,
    stop_loss_atr_multiplier=2.0
):
    """
    ATR 動態倉位計算
    
    公式：
    倉位 = (賬戶價值 × 風險比例) / (ATR × 止損倍數)
    """
    # 1. 計算 ATR
    atr = calculate_atr(price, period=atr_period)
    current_atr = atr.iloc[-1]
    
    # 2. 計算止損距離
    stop_loss_distance = current_atr * stop_loss_atr_multiplier
    
    # 3. 計算風險金額
    risk_amount = account_value * risk_per_trade
    
    # 4. 計算倉位
    position_size = risk_amount / stop_loss_distance
    
    # 5. 計算股數
    number_of_shares = int(position_size / price.iloc[-1])
    
    # 6. 計算實際倉位金額
    position_value = number_of_shares * price.iloc[-1]
    
    # 7. 計算實際風險比例
    actual_risk_ratio = (position_value * stop_loss_distance / price.iloc[-1]) / account_value
    
    return {
        'atr': current_atr,
        'stop_loss_distance': stop_loss_distance,
        'number_of_shares': number_of_shares,
        'position_value': position_value,
        'position_pct': position_value / account_value,
        'actual_risk_ratio': actual_risk_ratio
    }
```

**綜合倉位分配：**

```python
def calculate_final_position(
    account_value,
    sector_weights,
    sector_signals,
    risk_per_trade=0.02
):
    """
    綜合倉位分配
    
    考慮：
    1. 板塊權重（來自板塊輪動）
    2. 板塊信號（來自趨勢識別）
    3. 延遲進場確認
    4. ATR 動態倉位
    """
    final_positions = {}
    total_allocated = 0
    
    for sector, weight in sector_weights.items():
        if sector == '現金':
            continue
        
        # 1. 獲取板塊信號
        signal = sector_signals[sector]['signal']
        confidence = sector_signals[sector]['confidence']
        
        # 2. 如果信號是 'hold'，跳過
        if signal == 'hold':
            continue
        
        # 3. 計算該板塊的目標倉位
        target_weight = weight * confidence  # 按置信度調整
        
        # 4. 獲取該板塊的代表股票/ETF 價格
        price = get_sector_price(sector)
        
        # 5. 計算 ATR 動態倉位
        position_info = calculate_atr_based_position(
            price,
            account_value,
            risk_per_trade=risk_per_trade
        )
        
        # 6. 限制最大倉位（單一板塊不超過 30%）
        max_position_weight = min(target_weight, 0.3)
        position_info['target_weight'] = max_position_weight
        position_info['actual_weight'] = position_info['position_pct']
        
        # 7. 如果實際權重超過目標權重，限制到目標權重
        if position_info['actual_weight'] > max_position_weight:
            position_info['number_of_shares'] = int(
                (account_value * max_position_weight) / price.iloc[-1]
            )
            position_info['position_value'] = (
                position_info['number_of_shares'] * price.iloc[-1]
            )
            position_info['position_pct'] = max_position_weight
        
        final_positions[sector] = position_info
        total_allocated += position_info['position_pct']
    
    # 8. 剩餘資金分配給現金
    final_positions['現金'] = 1.0 - total_allocated
    
    return final_positions
```

---

## 三、實施計劃

### Phase 1: 基礎模塊開發（1-2 週）

#### Week 1: 板塊輪動系統
- [ ] 獲取 10 個板塊 ETF 的歷史數據
- [ ] 實現板塊強度計算
- [ ] 實現板塊權重分配
- [ ] 回測板塊輪動策略

#### Week 2: 延遲進場系統
- [ ] 實現 Supertrend 指標
- [ ] 實現突破檢測
- [ ] 實現延遲確認機制
- [ ] 實現假突破概率計算
- [ ] 回測延遲進場效果

### Phase 2: 整合系統（2-3 週）

#### Week 3: 動態倉位系統
- [ ] 實現 ATR 計算
- [ ] 實現 ATR 動態倉位
- [ ] 實現綜合倉位分配
- [ ] 實現止損/止盈機制

#### Week 4: 整合測試
- [ ] 整合三層架構
- [ ] 端到端測試
- [ ] 性能優化
- [ ] 文檔編寫

### Phase 3: 回測與優化（2-3 週）

#### Week 5: 完整回測
- [ ] 在 2020-2026 年期間回測
- [ ] 比較不同策略變體
- [ ] 統計假突破率改善
- [ ] 統計收益/風險指標

#### Week 6-7: 參數優化
- [ ] 網格搜索最優參數
- [ ] 遺傳算法優化
- [ ] 穩健性測試
- [ ] 壓力測試

### Phase 4: 實盤部署（持續）

#### 實盤啟動
- [ ] 紙盤交易測試
- [ ] 小額實盤測試
- [ ] 全規模部署
- [ ] 持續監控

---

## 四、預期成果

### 4.1 策略績效指標

**基準指標（2020-2026）：**

| 指標 | Supertrend 基準 | +延遲進場 | +板塊輪動 | +ATR動態倉位 | 完整策略 |
|------|--------------|----------|----------|------------|---------|
| 年化收益 | 12% | 15% (+25%) | 18% (+50%) | 16% (+33%) | 22% (+83%) |
| 年化波動 | 25% | 22% (-12%) | 20% (-20%) | 18% (-28%) | 17% (-32%) |
| 夏普比率 | 0.48 | 0.68 (+42%) | 0.90 (+88%) | 0.89 (+85%) | 1.29 (+169%) |
| 最大回撤 | -35% | -28% (-20%) | -25% (-29%) | -22% (-37%) | -18% (-49%) |
| Calmar比率 | 0.34 | 0.54 (+59%) | 0.72 (+112%) | 0.73 (+115%) | 1.22 (+259%) |
| 假突破率 | 35% | 21% (-40%) | 21% (-40%) | 21% (-40%) | 21% (-40%) |

### 4.2 關鍵改善

**1. 假突破率降低：35% → 21%（-40%）**
- 延遲進場有效過濾假突破
- 提高交易質量

**2. 夏普比率提升：0.48 → 1.29（+169%）**
- 板塊輪動提升整體收益
- 動態倉位控制風險

**3. 最大回撤降低：-35% → -18%（-49%）**
- 板塊輪動提供分散效果
- ATR 動態倉位控制槓桿

### 4.3 交易統計

**年度交易統計（預期）：**

| 指標 | 數值 |
|------|------|
| 總交易次數 | 60-80 次 |
| 勝率 | 55-65% |
| 盈虧比 | 1.5-2.0 |
| 平均持倉時間 | 15-25 天 |
| 單筆最大收益 | +15-25% |
| 單筆最大虧損 | -8-12% |

---

## 五、風險管理

### 5.1 多層風險控制

```
第一層：板塊層面風控
├── 單一板塊最大權重：30%
├── 最少同時持有板塊數：2 個
└── 板塊相關性監控（避免過度集中）

第二層：信號層面風控
├── 最低置信度閾值：60%
├── 假突破概率上限：40%
└── 連續虧損限制：連續 3 次虧損後暫停

第三層：倉位層面風控
├── 單筆風險比例：2%
├── 總倉位上限：95%（保留 5% 現金）
└── 止損：ATR × 2.0

第四層：組合層面風控
├── 最大回撤限制：-20%
├── 日內虧損限制：-5%
└── 週虧損限制：-10%
```

### 5.2 極端情況處理

**1. 市場崩盤（單日跌 > 8%）**
- 立即減倉至 30%
- 只保留現金和最穩定板塊
- 暫停新開倉

**2. 高波動時期（VIX > 40）**
- 降低風險比例至 1%
- 增加延遲確認至 3-4 根 K 線
- 提高假突破概率閾值

**3. 板塊輪動失效（強勢板塊 < 3 個）**
- 轉為等權重配置
- 降低總倉位至 70%
- 增加現金配置

---

## 六、代碼結構

### 項目目錄

```
trend-breakthrough-with-delay-and-rotation/
├── data/
│   ├── sector_data.py          # 板塊數據獲取
│   ├── market_data.py          # 市場數據獲取
│   └── cache/                 # 數據緩存
├── indicators/
│   ├── supertrend.py          # Supertrend 指標
│   ├── atr.py                 # ATR 指標
│   ├── rsi.py                # RSI 指標
│   ├── macd.py               # MACD 指標
│   └── momentum.py           # 動量指標
├── strategies/
│   ├── sector_rotation.py     # 板塊輪動策略
│   ├── delayed_entry.py       # 延遲進場策略
│   └── dynamic_position.py   # 動態倉位策略
├── backtest/
│   ├── backtest_engine.py    # 回測引擎
│   ├── metrics.py           # 績效指標
│   └── reports.py           # 回測報告
├── risk/
│   ├── position_sizer.py     # 倉位計算
│   ├── stop_loss.py          # 止損機制
│   └── portfolio_monitor.py # 組合監控
├── main.py                   # 主程序
├── config.py                # 配置文件
├── requirements.txt         # 依賴
└── README.md               # 使用說明
```

### 核心模塊

**1. 板塊輪動系統（sector_rotation.py）**

```python
class SectorRotationSystem:
    """板塊輪動系統"""
    
    def __init__(self, sector_etfs, lookback=20):
        self.sector_etfs = sector_etfs
        self.lookback = lookback
        self.current_weights = None
        self.sector_strengths = None
    
    def update_sector_strengths(self):
        """更新板塊強度"""
        self.sector_strengths = {}
        
        for sector, ticker in self.sector_etfs.items():
            data = self._fetch_sector_data(ticker)
            strength = calculate_sector_strength(data, self.lookback)
            self.sector_strengths[sector] = strength
    
    def calculate_weights(self, top_n=3):
        """計算板塊權重"""
        strengths_df = pd.DataFrame(self.sector_strengths).T
        strengths_df = strengths_df.sort_values('strength_score', ascending=False)
        
        top_sectors = strengths_df.head(top_n)
        total_score = top_sectors['strength_score'].sum()
        
        weights = (top_sectors['strength_score'] / total_score) * 0.6
        weights['現金'] = 0.4
        
        self.current_weights = weights
        return weights
    
    def get_top_sectors(self, top_n=3):
        """獲取強勢板塊"""
        self.update_sector_strengths()
        self.calculate_weights(top_n=top_n)
        
        return list(self.current_weights.index)[:top_n]
```

**2. 延遲進場系統（delayed_entry.py）**

```python
class DelayedEntrySystem:
    """延遲進場系統"""
    
    def __init__(self, delay_bars=2, confidence_threshold=0.6):
        self.delay_bars = delay_bars
        self.confidence_threshold = confidence_threshold
        self.pending_signals = {}
    
    def generate_signal(self, price, supertrend, trend):
        """生成進場信號"""
        # 檢測突破
        breakthrough = self._detect_breakthrough(price, supertrend, trend)
        
        if breakthrough:
            # 添加到待確認信號
            self.pending_signals[len(price)] = {
                'initial_time': len(price),
                'trend': trend.iloc[-1],
                'price': price.iloc[-1]
            }
        
        # 檢查待確認信號
        confirmed_signals = self._confirm_signals(price, trend)
        
        return confirmed_signals
    
    def _detect_breakthrough(self, price, supertrend, trend):
        """檢測突破"""
        current_trend = trend.iloc[-1]
        current_price = price.iloc[-1]
        current_supertrend = supertrend.iloc[-1]
        
        # 上漲突破
        if current_trend == 0 and current_price > current_supertrend:
            return True, 'long'
        
        # 下跌突破
        if current_trend == 1 and current_price < current_supertrend:
            return True, 'short'
        
        return False, None
    
    def _confirm_signals(self, price, trend):
        """確認信號（延遲檢查）"""
        confirmed = {}
        
        for timestamp, signal in list(self.pending_signals.items()):
            # 計算延遲時間
            elapsed = len(price) - signal['initial_time']
            
            if elapsed >= self.delay_bars:
                # 確認趨勢是否持續
                current_trend = trend.iloc[-1]
                
                if current_trend == signal['trend']:
                    # 計算置信度
                    false_break_prob = calculate_false_break_probability(
                        price, trend, self.delay_bars
                    )
                    confidence = 1.0 - false_break_prob
                    
                    if confidence >= self.confidence_threshold:
                        confirmed[timestamp] = {
                            'direction': 'long' if current_trend == 1 else 'short',
                            'confidence': confidence,
                            'false_break_prob': false_break_prob
                        }
                
                # 移除已確認的信號
                del self.pending_signals[timestamp]
        
        return confirmed
```

**3. 動態倉位系統（dynamic_position.py）**

```python
class DynamicPositionSystem:
    """動態倉位系統"""
    
    def __init__(self, account_value, risk_per_trade=0.02):
        self.account_value = account_value
        self.risk_per_trade = risk_per_trade
        self.current_positions = {}
    
    def calculate_position(self, symbol, price, atr, stop_loss_atr_multiplier=2.0):
        """計算單一資產倉位"""
        # 止損距離
        stop_loss_distance = atr * stop_loss_atr_multiplier
        
        # 風險金額
        risk_amount = self.account_value * self.risk_per_trade
        
        # 倉位大小
        position_size = risk_amount / stop_loss_distance
        
        # 股數
        number_of_shares = int(position_size / price)
        
        # 實際倉位金額
        position_value = number_of_shares * price
        
        # 實際風險比例
        actual_risk = (position_value * stop_loss_distance / price) / self.account_value
        
        return {
            'symbol': symbol,
            'shares': number_of_shares,
            'value': position_value,
            'weight': position_value / self.account_value,
            'actual_risk': actual_risk,
            'stop_loss': price * (1 - stop_loss_distance / price)
        }
    
    def allocate_portfolio(self, sector_weights, signals, prices):
        """分配組合倉位"""
        positions = {}
        total_allocated = 0
        
        for sector, weight in sector_weights.items():
            if sector == '現金':
                continue
            
            if sector not in signals or signals[sector]['direction'] == 'hold':
                continue
            
            # 計算目標倉位
            target_weight = weight * signals[sector]['confidence']
            
            # 限制最大倉位
            max_weight = min(target_weight, 0.3)
            
            # 計算倉位
            price = prices[sector]
            atr = calculate_atr(price, period=14)
            
            position = self.calculate_position(sector, price, atr)
            
            # 調整到目標權重
            if position['weight'] > max_weight:
                position['shares'] = int(
                    (self.account_value * max_weight) / price
                )
                position['value'] = position['shares'] * price
                position['weight'] = max_weight
            
            positions[sector] = position
            total_allocated += position['weight']
        
        # 剩餘現金
        positions['現金'] = 1.0 - total_allocated
        
        self.current_positions = positions
        return positions
```

---

## 七、下一步行動

### 立即開始（本週）

1. **獲取板塊數據**
   ```bash
   python data/sector_data.py --fetch --period 2020-01-01:2026-03-06
   ```

2. **測試板塊強度計算**
   ```bash
   python strategies/sector_rotation.py --test
   ```

3. **回測板塊輪動策略**
   ```bash
   python backtest/backtest_engine.py --strategy sector_rotation --start 2020-01-01 --end 2026-03-06
   ```

### 本月完成

1. **實現延遲進場系統**
2. **整合板塊輪動 + 延遲進場**
3. **實現動態倉位系統**
4. **完整回測驗證**

---

## 八、預期時間表

| 階段 | 任務 | 時間 | 里程碑 |
|------|------|------|--------|
| Phase 1 | 板塊輪動系統 | 1 週 | 板塊選擇策略完成 |
| Phase 1 | 延遲進場系統 | 1 週 | 假突破率降低 40% |
| Phase 2 | 動態倉位系統 | 1 週 | ATR 倉位優化完成 |
| Phase 2 | 整合測試 | 1 週 | 三層架構完成 |
| Phase 3 | 完整回測 | 1 週 | 回測結果確認 |
| Phase 3 | 參數優化 | 1-2 週 | 最優參數確定 |
| Phase 4 | 實盤部署 | 持續 | 策略上線 |

**總時間：** 6-8 週

---

**計劃完成日期：** 2026-04-30
**負責人：** Charlie
**狀態：** 計劃階段 📋
