# 策略研究計劃 - 量化交易（低頻）

## 研究方向

**核心：量化交易（低頻）**
- 永續性最高
- 成本可控（0.5% per trade）
- 可擴展

**輔助：技術服務（API）**
- 訂閱收入
- 被動特性

---

## 第一階段：策略篩選（第 1-2 週）

### Dashboard 策略模板

**可選策略：**
1. **BOLLINGER Strategy** (bollinger)
   - 布林帶策略
   - 適合波動市場

2. **MACD策略** (macd)
   - 移動平均收斂發散指標
   - 趨勢跟蹤

3. **動量策略** (momentum)
   - 基於價格動量選股
   - 適合強勢市場

4. **RSI策略** (rsi)
   - 相對強弱指標
   - 超買超賣

5. **RSI_TW Strategy** (rsi)
   - RSI 台股專用

6. **SUPERTREND Strategy** (supertrend)
   - 超級趨勢策略
   - 趨勢跟蹤

### 初步篩選標準

**低頻交易適用：**
- ✅ MACD（每日信號）
- ✅ Supertrend（趨勢跟蹤）
- ✅ RSI（超買超賣）

**不太適合低頻：**
- ❌ Momentum（需要頻繁調整）
- ⚠️ Bollinger（需要密切監控）

### 第一輪回測策略

**優先順序：**
1. **Supertrend** - 趨勢跟蹤，低頻友好
2. **MACD** - 經典趨勢策略
3. **RSI** - 反轉策略

**回測參數：**
- 市場：TW（台股）
- 時間範圍：2023-2026（3 年）
- 初始資金：100,000 TWD
- 倉位：100%（全倉）
- 手續費：0.1425%（台股標準）

**評估指標：**
- 總收益率
- 年化收益率
- 最大回撤
- 夏普比率
- 勝率
- 盈虧比

---

## 第二階段：回測執行

### 回測腳本

```bash
cd ~/Dashboard

# Supertrend 回測
curl -s -X POST "http://localhost:8000/api/strategies/backtest" \
  -H "X-Admin-Token: admin995" \
  -H "Content-Type: application/json" \
  -d '{
    "template": "supertrend",
    "params": {
      "length": 10,
      "multiplier": 3.0
    },
    "market": "TW",
    "symbol": "2330.TW",
    "start_date": "2023-01-01",
    "end_date": "2026-02-27",
    "initial_capital": 100000
  }'

# MACD 回測
curl -s -X POST "http://localhost:8000/api/strategies/backtest" \
  -H "X-Admin-Token: admin995" \
  -H "Content-Type: application/json" \
  -d '{
    "template": "macd",
    "params": {
      "fast_period": 12,
      "slow_period": 26,
      "signal_period": 9
    },
    "market": "TW",
    "symbol": "2330.TW",
    "start_date": "2023-01-01",
    "end_date": "2026-02-27",
    "initial_capital": 100000
  }'

# RSI 回測
curl -s -X POST "http://localhost:8000/api/strategies/backtest" \
  -H "X-Admin-Token: admin995" \
  -H "Content-Type: application/json" \
  -d '{
    "template": "rsi",
    "params": {
      "rsi_period": 14,
      "rsi_threshold": 70
    },
    "market": "TW",
    "symbol": "2330.TW",
    "start_date": "2023-01-01",
    "end_date": "2026-02-27",
    "initial_capital": 100000
  }'
```

---

## 第三階段：策略優化

### 參數優化

對於表現最好的策略，進行參數優化：

**Supertrend:**
- length: [5, 10, 15, 20]
- multiplier: [2.0, 2.5, 3.0, 3.5, 4.0]

**MACD:**
- fast_period: [8, 10, 12, 14]
- slow_period: [20, 24, 26, 30]
- signal_period: [7, 9, 11]

**RSI:**
- rsi_period: [7, 10, 14, 21]
- rsi_threshold: [65, 70, 75, 80]

### 多資產組合

考慮將策略應用到多個資產：
- 台灣 50 成分股
- ETF（0050.TW, 0056.TW）
- 美股（TSLA, NVDA, AAPL）

---

## 第四階段：紙面交易

### 模擬交易（第 3-4 週）

**執行流程：**
1. 每日檢查策略信號
2. 記錄建議的買入/賣出
3. 不實際下單
4. 記錄模擬收益

**記錄格式：**
```json
{
  "date": "2026-02-28",
  "strategy": "supertrend",
  "signal": "buy|sell|hold",
  "symbol": "2330.TW",
  "price": 500.0,
  "quantity": 200,
  "simulated_return": 0.0
}
```

---

## 風控規則

### 交易頻率
- 低頻交易：每週 1-2 次進場/出場
- 避免過度交易

### 倉位管理
- 初始階段：100% 單一資產（簡化）
- 進階階段：分散到 3-5 個資產

### 止損規則
- 單次虧損 > 10%：暫停交易
- 連續 3 次虧損：重新評估策略

### 止盈規則
- 達到目標收益：部分止盈
- 避免貪婪

---

## 記錄與追蹤

### 每日記錄

在 `economy/strategy_logs/` 目錄記錄：
- 策略信號
- 交易決策
- 市場觀察

### 每週報告

生成報告包含：
- 策略表現
- 回測結果
- 紙面交易結果
- 下週計劃

---

**創建日期：** 2026-02-27
**創建者：** Charlie
**狀態：** 初始規劃
