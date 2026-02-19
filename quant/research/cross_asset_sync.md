# 跨資產同步極端事件研究

**啟動日期：** 2026-02-17
**優先順序：** 1️⃣
**對標機構：** Man AHL、Aspect Capital
**核心思想：** 時間分散 + 結構分散 = 完美風險分散

---

## 🎯 研究目標

### 核心洞察

**趨勢策略本質上是「時間分散」**
**跨資產則是「結構分散」**

當 NQ（美股期貨）、GC（黃金）、DX（離岸人民幣）這類低相關商品同步波動時，趨勢強度與相關性結構會發生突變，這正是風險溢酬重新定價的窗口。

### 為什麼這重要

這與目前正在測試「兩個低相關商品同跌做多」的概念高度重合，可以進一步制度化。

---

## 📊 數據需求

### 需要收集的資產

#### 1. NQ - 美股期貨（納斯達克 100）
- **代碼**：NQ (Nasdaq-100 Future)
- **交易所**：CME
- **週期**：日線
- **特點**：科技股為主，高動量

#### 2. GC - 黃金
- **代碼**：GC (Gold Future)
- **交易所**：CME
- **週期**：日線
- **特點**：避險資產，低相關

#### 3. DX - 離岸人民幣
- **代碼**：DX (Dollar Index - Offshore)
- **交易所**：ICE
- **週期**：日線
- **特點**：貨幣資產，對比貨幣

#### 4. 補充資產（可選）
- **ES** - S&P 500 期貨
- **CL** - 原油期貨
- **GC** - 白銀期貨
- **ZB** - 10 年期國債期貨

---

## 🔍 研究問題

### 1. 跨資產同步破位指標
- **問題**：如何定義「同步破位」？
- **方法**：當多個低相關資產同時突破關鍵均線時
- **指標**：破位後的 forward return

### 2. 波動 regime 下趨勢半衰期
- **問題**：在不同波動環境下，趨勢持續時間如何？
- **方法**：按波動率分組（低、中、高）
- **分析**：每個 regime 的平均趨勢半衰期

### 3. 負相關資產同跌時的 forward return
- **問題**：兩個負相關資產同跌時，未來收益如何？
- **方法**：檢測負相關且同跌，計算 forward return
- **意義**：尋找風險溢價機會

---

## 🛠️ 實作計畫

### 階段 1：數據收集（本週）
- [ ] 收集 NQ、GC、DX 日線數據
- [ ] 數據清洗與處理
- [ ] 計算相關係數矩陣
- [ ] 可視化資產相關性

### 階段 2：基礎分析（下週）
- [ ] 實作移動平均線指標
- [ ] 實作同步破位檢測
- [ ] 分析波動 regime
- [ ] 初步回測

### 階段 3：進階研究（2 週後）
- [ ] 實作負相關交易策略
- [ ] 優化參數
- [ ] 實盤測試
- [ ] 風險管理

---

## 💻 代碼架構

### 主程式
```python
# quant/research/cross_asset_sync/main.py

from cross_asset_analyzer import CrossAssetAnalyzer

def main():
    # 初始化分析器
    analyzer = CrossAssetAnalyzer(
        assets=['NQ', 'GC', 'DX'],
        windows=[20, 50, 200]
    )

    # 加載數據
    analyzer.load_data()

    # 分析相關性
    analyzer.analyze_correlations()

    # 分析同步破位
    breakdowns = analyzer.analyze_breakdowns()

    # 分析負相關交易
    trade_signals = analyzer.analyze_negative_correlation()

    # 回測
    backtest_results = analyzer.backtest_signals()

    # 儲存結果
    analyzer.save_results(backtest_results)

if __name__ == '__main__':
    main()
```

### 模組結構
```
quant/research/cross_asset_sync/
├── main.py                      # 主程式
├── cross_asset_analyzer.py      # 分析器核心
├── data_loader.py               # 數據載入
├── correlation_analysis.py      # 相關性分析
├── breakdown_detector.py        # 同步破位檢測
├── regime_analysis.py           # 波動 regime 分析
├── trade_signal_generator.py    # 交易信號生成
├── backtest_engine.py           # 回測引擎
├── risk_manager.py              # 風險管理
└── visualization.py             # 可視化
```

---

## 📈 基礎指標定義

### 移動平均線
```python
def calculate_ma(prices, period):
    """計算移動平均線"""
    return prices.rolling(period).mean()
```

### 相關係數
```python
def calculate_correlation(returns1, returns2, window=60):
    """計算滾動相關係數"""
    return returns1.rolling(window).corr(returns2)
```

### 同步破位
```python
def detect_breakdown(prices, ma_window=20, lookback=5):
    """檢測同步破位"""
    ma = prices.rolling(ma_window).mean()

    for i in range(lookback, len(prices)):
        # 當前價格低於移動平均
        if prices.iloc[i] < ma.iloc[i]:
            # 檢查過去 lookback 天是否都在 MA 下方
            all_below = all(prices.iloc[i-lookback:i] <= ma.iloc[i-lookback:i])
            if all_below:
                return True

    return False
```

### Forward Return
```python
def calculate_forward_return(prices, days=20):
    """計算 forward return"""
    forward_return = prices.shift(-days) / prices - 1
    return forward_return
```

---

## 📊 關鍵結果指標

### 1. 同步破位成功率
- **指標**：破位後 20 日回報 > 0 的比例
- **目標**：> 55%

### 2. 波動 regime 趨勢半衰期
- **指標**：不同 regime 下的平均趨勢持續時間
- **目標**：明顯差異（> 20%）

### 3. 負相關交易收益
- **指標**：兩個負相關資產同跌時的平均回報
- **目標**：正收益，IR > 0.5

### 4. Sharpe Ratio
- **指標**：策略調整後夏普比率
- **目標**：> 1.0

### 5. 最大回撤
- **指標**：策略的最大回撤
- **目標**：< 15%

---

## 🔬 實驗設計

### 實驗 1：不同窗口期的同步破位

**假設**：窗口期影響同步破位檢測效果

**變數**：
- ma_window: [10, 20, 50, 100]
- lookback: [3, 5, 10, 20]

**測試**：
- 計算不同參數下的成功率
- 找出最佳參數組合

### 實驗 2：不同資產組合

**假設**：資產選擇影響同步效果

**變數**：
- 資產組合: [NQ+GC], [NQ+DX], [GC+DX], [NQ+GC+DX], [ES+GC+DX]

**測試**：
- 比較不同組合的相關性
- 計算不同組合的同步破位成功率

### 實驗 3：時間週期效應

**假設**：不同時間週期表現不同

**變數**：
- 週期: [日線, 週線, 月線]
- 分析窗口: [3 個月, 6 個月, 12 個月]

**測試**：
- 比較不同週期的效果
- 選擇最佳週期

---

## ⚠️ 風險控制

### 實驗限制
- ⚠️ 歷史數據可能不完全
- ⚠️ 模擬回測可能高估實盤表現
- ⚠️ 流動性風險未考慮

### 實盤檢查清單
- [ ] 流動性檢查（每個資產的日均成交量）
- [ ] 交易成本模擬（滑點、手續費）
- [ ] 風險限制（最大倉位、止損）
- [ ] 持續監控（實盤 vs 回測差異）

---

## 📝 待辦事項

### 立即開始
- [ ] 收集數據（NQ、GC、DX）
- [ ] 建立 Python 環境
- [ ] 實作基礎分析器

### 本週目標
- [ ] 完成數據收集
- [ ] 實作同步破位檢測
- [ ] 初步回測

### 下週目標
- [ ] 實作波動 regime 分析
- [ ] 實作負相關交易
- [ ] 優化參數

### 本月目標
- [ ] 完成 3 個實驗
- [ ] 記錄所有發現
- [ ] 準備實盤測試

---

## 📚 參考資源

### 資料來源
- [Yahoo Finance](https://finance.yahoo.com/)
- [CME Group](https://www.cmegroup.com/)
- [ICE](https://www.theice.com/)

### 相關論文
- [Asset Allocation Across Uncorrelated Assets](https://...)
- [Trend Following in Multi-Asset Markets](https://...)
- [Risk Parity in Portfolio Management](https://...)

### 相關帳號
- [@voltima_quant](https://www.threads.net/@voltima_quant) - 全職自營量化團隊
- [Man AHL](https://www.manahm.com/) - 全球趨勢跟隨
- [Aspect Capital](https://www.aspect.co.uk/) - 系統性趨勢策略

---

**記錄完成日期：** 2026-02-17
**下次更新：** 數據收集完成後
