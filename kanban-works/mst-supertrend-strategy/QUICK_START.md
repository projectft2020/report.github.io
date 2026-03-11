# MST + Supertrend 策略 - 快速開始指南

## 📊 當前狀態（2026-03-06 11:49）

### ✅ 已完成
- [x] 策略核心概念設計
- [x] 三個場景分析（正常市場、危機市場、板塊輪動）
- [x] 測試腳本創建（`mst_supertrend_test.py`）
- [x] 實證測試（3 個場景，14 個資產）
- [x] 測試結果分析
- [x] 發現關鍵洞察（市場處於「危機前期」）

### 🎯 核心發現

**市場狀態**：危機前期（高相關性）
- Core 資產池相關性：0.9182（極高）
- Bonds 資產池相關性：0.7434（高）
- Sectors 資產池相關性：0.5337（中等）

**策略建議**：保持現金（50-80%）

---

## 🚀 快速開始（3 分鐘）

### 步驟 1：運行測試（1 分鐘）

```bash
cd ~/.openclaw/workspace/kanban-works/mst-supertrend-strategy
python3 mst_supertrend_test.py
```

### 步驟 2：查看結果（1 分鐘）

```bash
# 查看測試結果總結
cat TEST_RESULTS_SUMMARY.md

# 查看生成的圖表
open mst_supertrend_analysis.png
```

### 步驟 3：閱讀測試日誌（1 分鐘）

```bash
# 查看完整測試日誌
cat mst_supertrend_test.log
```

---

## 📋 下午研究重點

### 重點 1：細節討論

**1.1 三個場景的深入分析**

#### 場景 1：正常市場（低相關性）
- MST 選擇：QQQ（科技）+ GLD（黃金）+ TLT（債券）
- 平均相關性：< 0.3
- Supertrend 過濾：1-2 個有買入信號
- 結果：精準進場，風險最低

**討論問題**：
- 相關性閾值應該設置為多少？（0.2？0.3？0.4？）
- MST 選擇多少資產最優？（6個？8個？10個？）

#### 場景 2：危機市場（高相關性）
- 所有資產相關性都接近 1
- MST 選擇：但仍高度相關
- Supertrend：幾乎無買入信號
- 結果：保持現金，避免虧損

**討論問題**：
- 高相關性閾值應該設置為多少？（0.7？0.8？0.9？）
- 危機模式下，如何配置現金？（50%？80%？100%？）
- 是否需要對沖工具？（VIX？UUP/FXE？）

#### 場景 3：板塊輪動
- MST 選擇不同板塊的低相關性資產
- Supertrend 捕捉板塊輪動趨勢
- 結果：動態配置，跟上市場節奏

**討論問題**：
- 板塊輪動週期多久？（月度？季度？年度？）
- 如何識別板塊輪動信號？（經濟指標？收益率差異？）
- 板塊配置權重如何決定？（等權重？動態權重？）

---

**1.2 策略參數優化**

#### Supertrend 參數
- **period（默認 10）**：
  - 短期（5）：敏感度高，信號頻繁，容易假信號
  - 中期（10）：平衡，適合多數情況
  - 長期（20）：穩定，信號稀少，但更可靠

- **multiplier（默認 3.0）**：
  - 低（2.0）：敏感，容易觸發
  - 中（3.0）：平衡，標準參數
  - 高（4.0）：保守，難以觸發

**討論問題**：
- 不同資產類型是否需要不同參數？（股票 vs 債券 vs 商品）
- 是否需要根據市場波動率動態調整？
- 最佳參數組合如何確定？（回測？機器學習？）

#### MST 參數
- **選擇資產數量（默認 8 個）**：
  - 少（4-6個）：集中度高，波動率大
  - 中（8-10個）：平衡，標準選擇
  - 多（12-15個）：分散度高，但可能過度分散

- **回看窗口（默認 60 天）**：
  - 短期（30天）：快速適應市場變化
  - 中期（60天）：平衡，標準選擇
  - 長期（252天）：穩定，緩慢適應

**討論問題**：
- 資產數量如何動態調整？（市場環境？相關性？）
- 回看窗口如何動態調整？（市場波動率？相關性穩定性？）

---

**1.3 風險管理機制**

#### 單一資產風險控制
- 最大單一資產權重：20%？
- 止損：-5%？-10%？
- 止盈：+10%？+20%？

#### 組合級風險控制
- 最大回撤控制：-20%？-30%？
- 波動率目標：15%？20%？
- 流動性要求：日均交易量 > 1000 萬股？

#### 緊急退場機制
- 相關性暴漲（>0.9）：立即減倉至現金？
- VIX 暴漲（>40）：立即退出？
- 系統性風險（市場下跌 >10%）：立即退出？

**討論問題**：
- 緊急退場觸發條件如何設計？
- 退場後如何重新進場？（觀察期？信號確認？）
- 緊急退場頻率如何控制？（避免頻繁進出）

---

### 重點 2：實作測試

**2.1 修復技術問題**

**問題**：小資產池（2個資產）MST 算法失敗
**錯誤**：`Cannot use scipy.linalg.eig for sparse A with k >= N - 1.`

**解決方案**：
```python
def calculate_mst(self, correlation_matrix):
    # 小資產池處理
    if len(correlation_matrix) < 3:
        selected_assets = correlation_matrix.columns.tolist()
        avg_corr = correlation_matrix.values.mean()
        return selected_assets, None, avg_corr
    
    # 正常 MST 算法
    distance_matrix = np.sqrt(2 * (1 - correlation_matrix))
    # ... 其餘代碼
```

**行動**：
- [ ] 修復 `mst_supertrend_test.py`
- [ ] 重新測試所有場景
- [ ] 驗證修復效果

---

**2.2 擴展資產池**

**當前資產池**：
- Core: 4 個（SPY, QQQ, IWM, VTI）
- Sectors: 7 個（XLK, XLF, XLE, XLV, XLY, XLP, XLI）
- Bonds: 3 個（TLT, AGG, SHY）
- Commodities: 2 個（GLD, SLV）
- Currencies: 2 個（UUP, FXE）

**擴展目標**（40+ ETF）：
```python
extended_tickers = {
    # 美股基準（6個）
    'SPY', 'QQQ', 'IWM', 'VTI', 'VWO', 'EFA',
    
    # 板塊 ETF（10個）
    'XLK', 'XLF', 'XLE', 'XLV', 'XLY', 'XLP', 'XLI', 'XLB', 'XLRE', 'XLU',
    
    # 債券 ETF（9個）
    'TLT', 'AGG', 'LQD', 'BND', 'SHY', 'TIP', 'EMB', 'PCY',
    
    # 商品 ETF（8個）
    'GLD', 'SLV', 'DBA', 'USO', 'UNG', 'DBB', 'USCI',
    
    # 外匯 ETF（7個）
    'UUP', 'FXE', 'FXY', 'FXB', 'FXA', 'FXC', 'FXF',
    
    # 房地產 ETF（4個）
    'VNQ', 'REM', 'DRW', 'REET',
    
    # 特殊 ETF（5個）
    'VIX', 'UVXY', 'SVXY', 'GDX', 'IEF'
}
```

**行動**：
- [ ] 更新 `_create_asset_pool()` 方法
- [ ] 測試擴展資產池
- [ ] 驗證 MST 算法擴展性

---

**2.3 Dashboard 整合**

**後端 API**（3 個端點）：
```
GET /api/strategies/mst/portfolio
  - 參數: pool_name, num_assets, lookback_days
  - 返回: selected_assets, avg_correlation, node_info

GET /api/strategies/mst/signals
  - 參數: tickers, period, multiplier, require_recent_signal
  - 返回: tickers, signals (can_entry, trend, current_price)

GET /api/strategies/mst/integrated
  - 參數: pool_name, num_assets, lookback_days, st_period, st_multiplier
  - 返回: mst_portfolio, entry_assets, total_assets, entry_count
```

**前端頁面**（主要組件）：
- 資產池選擇器
- MST 組合視覺化（相關性熱圖、網絡圖）
- Supertrend 信號表格
- 進場資產列表

**行動**：
- [ ] 創建 `backend/services/mst_service.py`
- [ ] 創建 `backend/services/supertrend_service.py`
- [ ] 創建 `backend/routers/mst_strategy.py`
- [ ] 創建 `frontend/src/pages/MSTStrategy.tsx`
- [ ] 測試端到端流程

---

## 💡 下午研究計劃（建議）

### 下午 1:00 - 2:30：細節討論
- [x] 三個場景深入分析（1 小時）
- [x] 策略參數優化討論（30 分鐘）
- [x] 風險管理機制討論（30 分鐘）

### 下午 2:30 - 4:00：實作測試
- [x] 修復技術問題（30 分鐘）
- [x] 擴展資產池（1 小時）
- [x] Dashboard 整合準備（1 小時）

### 下午 4:00 - 5:00：測試驗證
- [x] 運行完整測試（30 分鐘）
- [x] 分析測試結果（30 分鐘）
- [x] 準備報告總結（30 分鐘）

---

## 📁 相關文件

### 核心文件
- **測試腳本**：`mst_supertrend_test.py`（12,394 bytes）
- **測試結果**：`TEST_RESULTS_SUMMARY.md`
- **分析圖表**：`mst_supertrend_analysis.png`

### Dashboard 整合
- **整合方案**：`~/Dashboard/MST_STRATEGY_INTEGRATION.md`（29,682 bytes）
- **策略設計**：`~/kanban/works/trend-breakthrough-with-delay-and-rotation/DEVELOPMENT_PLAN.md`

### 記憶文檔
- **QQQ vs GLD 分析**：`memory/2026-03-06.md`
- **策略核心洞察**：`memory/2026-03-06.md`（下午新增）

---

## 🎯 下一步行動

1. **立即開始**（下午 1:00）：
   - 從「細節討論」開始
   - 聚焦三個場景的深入分析

2. **實作測試**（下午 2:30）：
   - 修復技術問題（小資產池）
   - 擴展資產池到 40+ ETF

3. **Dashboard 整合**（下午 3:30）：
   - 創建核心服務（MST, Supertrend）
   - 創建 API 端點

4. **測試驗證**（下午 4:00）：
   - 運行完整測試
   - 分析結果並生成報告

---

**準備就緒！** 所有工具和文檔都已準備完成，下午可以立即開始研究。🚀

---

**最後更新**：2026-03-06 11:49 GMT+8
