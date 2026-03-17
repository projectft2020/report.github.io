# MEMORY.md - Long-Term Memory (Main Index)

> **Quick Reference:** This file is your long-term memory. It's kept minimal for fast access.
> **For Details:** Check `memory/topics/*.md` for categorized knowledge.
> **For History:** Check `memory/YYYY-MM-DD.md` for daily logs.

---

## 📋 Quick Navigation

### Core Knowledge (memory/topics/)
- **[Business Model](memory/topics/商業模式.md)** - 商業模式設計、價值主張、目標受眾
- **[Memory System](memory/topics/記憶系統.md)** - 三層架構、QMD 整合、GPU OOM 解決方案
- **[System Optimization](memory/topics/系統優化.md)** - 背壓機制、容量規劃、三層超時機制
- **[Research Reports](memory/topics/研究報告.md)** - 研究品質標準、11 部分模板、實證驗證
- **[Quantitative Research](memory/topics/量化研究.md)** - 量化交易策略、市場範圍、研究方法
- **[Risk Management](memory/topics/risk-management.md)** - 風險指標、厚尾分佈、非傳統止損
- **[System Architecture](memory/topics/system-architecture.md)** - Kanban、監控、自動化
- **[Scout System](memory/topics/scout-system.md)** - 數據源、偏好學習、掃描器
- **[Sub-Agents](memory/topics/sub-agents.md)** - Research、Analyst、Creative、Automation、Architect
- **[Monitoring](memory/topics/monitoring.md)** - Prometheus、Grafana、Dashboard
- **[Kanban](memory/topics/kanban.md)** - 任務管理、狀態同步、並發執行
- **[User Preferences](memory/topics/user-preferences.md)** - 研究偏好、報告標準、實務需求
- **[Research Standards](memory/topics/research-standards.md)** - 研究品質、文檔模板、驗證流程

### Daily Logs (memory/YYYY-MM-DD.md)
- **[Today](memory/2026-02-23.md)** - Scout Phase 2 實施完成
- **[Yesterday](memory/2026-02-22.md)** - 市場分數 V3、開發模式
- **[Previous Days](memory/)** - Browse by date for full context


## 🎯 User Profile & Preferences

### Identity
- **Name:** David
- **Preferred Language:** Traditional Chinese (Taiwan usage)
- **Preferred Report Type:** 深入量化研究（完整數學推導 + 實證驗證）
- **Practical Tool Requirement:** 簡化到 3 分鐘操作，單一指標決策（DHRI 範例）
- **Core Value:** Seriousness, consistency, genuine utility

### Research Preferences ⭐⭐⭐⭐
- **喜歡的深度：** ⭐⭐⭐⭐ 極高（數學推導 + 實證驗證）
- **研究品質標準：** m001 範例（Omega/CSR/Kappa/SKTASR 研究報告）
- **報告模板：** 11 個部分（執行摘要、理論基礎、公式、特徵、實證、代碼、建議）
- **複雜度偏好：** [2, 3]（中等到高等）
- **子代理選擇：** Research (0.35), Analyst (0.40), Creative (0.15), Automation (0.10)

### Scout Preferences
- **高權重主題（affinity_score: 0.9）：**
  - performance_metrics
  - risk_adjusted_metrics
  - fat_tail_analysis
  - skewness_kurtosis
  - quantitative_research

- **正面關鍵詞：**
  - mathematical derivation, empirical testing, rolling window, statistical significance, diebold-mariano, hypothesis testing, fat-tailed, power law, tail index, coherent risk measure, utility function, maximum likelihood, monte carlo, backtesting

- **數據源可靠性：**
  - arxiv: 0.95, reddit_r_quant: 0.8, bloomberg: 0.75, threads: 0.7


## 🚀 Recent Major Achievements

### 2026-03-05: 系統優化 Phase 1 完成
- ✅ P0 優化：Spawning 超時保護、API 錯誤追蹤
- ✅ P1 優化：背壓機制、失敗任務清理、Scout 自動觸發
- ✅ P2 優化：任務優先級系統、持久 datetime 錯誤修復
- ✅ 卡住任務從 6 個降至 0 個（100% 改善）
- ✅ 回滾時間從 120 分鐘降至 45 分鐘（62.5% 改善）
- ✅ 系統健康度：1.00（完全健康）
- ✅ 完成研究：19 篇（機器學習、量化、市場微結構）
- **核心洞察：** 背壓機制是必需品，容量規劃不在 100% 運作，系統成熟度需要精細控制
- **文檔：** memory/topics/system-architecture.md（已更新優化成果）

### 2026-03-04: Scout Reports 項目設計完成
- ✅ 完整技術設計文檔（106 KB，共 5 個文檔）
- ✅ Agent-ready 設計（API 包裝器、類型提示、全面文檔）
- ✅ 獨立項目架構（不與 Dashboard 合併）
- ✅ 完整 API 規範（報告、反饋、搜索、分析、偏好）
- ✅ 前後端技術棧規範（FastAPI + React 19）
- ✅ 開發者指南和項目總結
- **項目位置：** `~/.openclaw/workspace/ScoutReports/`
- **實施時間：** 9-13 天（完整實施）
- **核心特性：** Markdown 報告展示、全文搜索、反饋收集、偏好學習、分析儀表板

### 2026-02-23: Scout Phase 2 完成
- ✅ 實現 10 個爬文類型數據源掃描器（Threads, Quantocracy, QuantConnect, Nuclear Phynance, QuantNet, SSRN, NBER, Hedge Fund Reports, TradingView, Quant StackExchange）
- ✅ 通用網頁掃描器框架，易於擴展
- ✅ 所有掃描器 100% 測試通過
- ✅ 集成到完整掃描流程
- **系統狀態：** 12 個數據源（2 個 API + 10 個爬文），每天預計掃描 100+ 主題

### 2026-02-22: 市場分數 V3 開發
- ✅ 完整的 3-tier 文檔（模組級 → 類級 → 方法級）
- ✅ 全面類型提示和回歸驗證
- ✅ 智能緩存機制（_price_cache, _ma_cache, _score_cache）
- ✅ 優雅錯誤處理（try-except + logger.error + return safe defaults）
- ✅ 新的開發模式範例（MarketScore V3 pattern）

### 2026-03-06: 知識圖譜更新 + 研究任務完成 + OpenClaw 升級評估 Phase 1-2
- ✅ 完成知識圖譜更新（knowledge-matrix-2026-03-06.md）
- ✅ 記憶維護完成（MEMORY.md、SOUL.md、topics/ 更新）
- ✅ 完成 3 個研究任務（GOPO、Transformer 理論、LSVI-UCB++）
- ✅ OpenClaw 升級評估 Phase 1-2 完成（風險評估、Breaking Checks、Sub-Agent 影響）
- ✅ 系統優化 Phase 1 實證成果記錄（背壓機制、三層超時、數據優先診斷）
- **知識圖譜：** knowledge-matrix-2026-03-06.md（18.7 KB）
- **研究任務：** GOPO（希爾伯特空間優化）、Transformer（逼近能力）、LSVI-UCB++（間隙依賴邊界）
- **核心洞察：** 不應盲目追蹤最新版本，需要評估必要性，相容準備策略最佳

### 2026-03-02: 知識矩陣與 Web 4.0 經濟計畫整合
- ✅ 完成知識圖譜矩陣世界（短中長期記憶 + QMD 向量知識）
- ✅ 提取 5 大維度關鍵因子（倉位管理、預測技術、風險控制、執行優化、市場洞察）
- ✅ 完成 4 項重要研究（Kelly 1956、Kernel R²、GNN 預測、Kelly+VIX Hybrid）
- ✅ 核心學習：部位規模是戰略選擇、AI 深刻改變市場結構、簡單驗證 > 複雜未驗證
- **核心發現：** 倉位管理從「操作細節」升級為「戰略選擇」，根本性改變策略表現
- **文檔：** knowledge-matrix-2026-03-02.md

### 2026-02-28: Supertrend 策略深度分析
- ✅ 分析 462 筆 Supertrend 實際交易數據
- ✅ 驗證第一性原理：假突破檢測、趨勢持久度、市場狀態影響
- ✅ 對比不同策略的績效
- ✅ 驗證用戶提供的策略對比數據的真實性（發現嚴重問題）
- **核心發現：** 第 7 天虧損幅度是關鍵預測因子，第 11 天確認趨勢

### 2026-02-27: 經濟系統啟動
- ✅ 受控自主經濟實驗啟動（90,000 TWD 可用本金）
- ✅ 策略研究第一輪回測（RSI、Supertrend、MACD）
- ✅ 學習策略分類與評估標準（趨勢跟踪、均值回歸、動量策略）
- ✅ 單一資產 vs 組合級別洞察
- ✅ 倉位管理問題討論

### 2026-02-26: AAPL 過度反應動量策略完成
- ✅ AAPL 過度反應動量策略研究完成（10分鐘頻率表現最佳）
- ✅ 網路環境改變（搬家）
- ✅ Kanban 操作清理

### 2026-02-21: Quantitative Research 多市場分析
- ✅ 完成台灣、美國、期指、商品期貨的技術、情感、風險分析
- ✅ 並發執行策略：5 個任務同時運行，100% 成功率
- ✅ 完成率：47% (8/17 tasks)

### 2026-02-20: 研究品質標準建立
- ✅ m001 範例（高級績效指標研究）
- ✅ 11 個部分的標準模板
- ✅ 實證驗證流程（滾動窗口、回歸分析、DM 檢驗）


## 核心工作方法（2026-03-09 新增）

### 「先檢查後做事」SOP

設計任何系統前的標準流程：

1. **檢查 TECH_INVENTORY.md**
   - 查看現有系統/工具/技能
   - 確認是否有適合的現有系統

2. **檢查 MEMORY.md**
   - 查看長期記憶中的相關信息
   - 確認是否已有相關決策或教訓

3. **檢查 memory/topics/system-architecture.md**
   - 查看系統架構
   - 確認是否符合現有架構

4. **檢查 skills/**
   - 查看現有技能
   - 確認是否有相關 SOP

5. **使用 memory_search 查詢相關技術**
   - 搜索關鍵技術詞
   - 確認是否已有相關實現

6. **評估功能匹配度**
   - 計算功能匹配百分比
   - 根據匹配度決策

7. **決策：**
   - ≥ 80%：使用現有系統
   - 50-79%：評估擴展現有系統
   - < 50%：設計新系統

### 三層防禦機制

**預防層：設計前檢查**
- 檢查 TECH_INVENTORY.md
- 檢查 MEMORY.md
- 檢查 memory/topics/
- 檢查 skills/
- 使用 memory_search

**檢測層：設計中審查**
- 技術棧檢查清單（TECH_STACK_CHECKLIST.md）
- 設計審查流程
- 代碼審查

**恢復層：設計後驗證**
- 實施後審計（POST_IMPLEMENTATION_AUDIT.md）
- 每月健康檢查
- 每季度技術債務評估

### 適配器模式整合

**應用場景：** 整合現有系統而不重複造輪子

**核心優勢：**
- 利用現有系統
- 統一介面
- 解耦設計
- 易於測試

**實現方式：**
```
統一 API (MemoryCore)
    ↓
適配器層 (QMD Adapter + Obsidian Adapter + Session Adapter)
    ↓
現有系統 (QMD CLI + Obsidian Files + 記憶體)
```

---

## 核心洞察（2026-03-09 新增）

### Mentor 的洞見

**「問題不是『如何整合』，而是『為什麼會忽略現有系統』。」**

這個洞見改變了我的思考方式：
- 問題不是技術問題，而是流程問題
- 可見性決定了行為（不知道有 QMD，就會建議用 ChromaDB）
- SOP 比代碼更重要（代碼可以重寫，流程決定了長期方向）

### 關鍵學習

1. **技術問題往往是流程問題**
   - 我建議用 ChromaDB 不是因為技術錯誤
   - 而是因為沒有檢查現有系統的 SOP

2. **可見性決定了行為**
   - 如果不知道有 QMD，就會建議用 ChromaDB
   - 技術棧庫存提升了可見性

3. **SOP 比代碼更重要**
   - 代碼可以重寫
   - 但流程決定了長期方向

---

## 可複用模式（2026-03-09 新增）

### 適配器模式整合

**應用場景：** 整合現有系統而不重複造輪子

**核心優勢：**
- 利用現有系統
- 統一介面
- 解耦設計
- 易於測試

**實現方式：**
```
統一 API (MemoryCore)
    ↓
適配器層 (QMD Adapter + Obsidian Adapter + Session Adapter)
    ↓
現有系統 (QMD CLI + Obsidian Files + 記憶體)
```

### 三層防禦機制

**應用場景：** 預防、檢測、恢復任何問題

**核心優勢：**
- 多層防護
- 系統化改進
- 持續優化

**實現方式：**
1. **預防：** 設計前檢查（SOP）
2. **檢測：** 設計中審查
3. **恢復：** 設計後驗證

---

## 效率提升指標（2026-03-09 新增）

### 記憶系統效率

**每日節省：** 91 分鐘（1.5 小時）
- 研究 2 筆：8 分鐘 (80%)
- 決策 3 個：6 分鐘 (67%)
- 錯誤 1 個：3 分鐘 (75%)
- 搜索 5 次：45 分鐘 (90%)
- 分析連結 1 次：29 分鐘 (97%)

**每月節省：** 45.5 小時
**每年節省：** 22.75 天

### 技術棧庫存

**系統數量：** 56 個
**檢查時間：** < 5 分鐘
**避免重複造輪子率：** 預計 80%+

### SOP 效率

**檢查步驟：** 6 個標準化步驟
**決策規則：** 3 個客觀規則
**審計頻率：** 每月 + 每季度

---

## 📊 System Status

### Active Projects
1. **Quantitative Research:** 47% (8/17 tasks)
2. **Programmer Agent Design:** 82% (45/55 tasks)

### Monitoring System
- **Prometheus:** ✅ Running (PID 96040)
- **Grafana:** ✅ Running (PID 97069)
- **Kanban Metrics Exporter:** ✅ Running (PID 96598)
- **Dashboard:** 8 panels (OpenClaw System Dashboard)

### Sub-Agent Reliability
| Agent | Success Rate | Status |
|--------|-------------|--------|
| Research | 100% | ✅ Reliable |
| Analyst | 100% | ✅ Reliable |
| Creative | - | - |
| Automation | 0% | ❌ Avoid for complex tasks |
| Architect | - | - |

### Scout System
- **數據源總數：** 12 個（2 API + 10 爬文）
- **掃描頻率：** 每 2-4 小時（由 Monitor and Refill 觸發）
- **預估主題數：** 100+ 主題/天
- **用戶反饋：** 開始需要提供反饋幫助改進


## 🎯 Key Decisions & Insights

### 系統優化核心原則（2026-03-05）
- **背壓機制是必需品：** 可複用模式（監測 → 計算健康度 → 動態調整）
- **容量規劃：** 不在 100% 容量運作，80% 是安全線，50% 是舒適線
- **系統成熟度：** 卡住任務增加不是失敗，而是需要更精細控制的信號
- **三層超時機制：** 30 秒（啟動警報）→ 30 分鐘（spawning 警報）→ 45 分鐘（自動回滾）→ 90 分鐘（執行超時）
- **數據優先診斷：** 先數據，後假設（本次缺失 API 錯誤日誌）
- **自動化整合：** 優先級規則引擎整合到心跳流程，避免手動執行

### 規格性原則：修補 vs 重構
- **修補：** 只修 bug，問題會重複，技術債累積
- **重構：** 重新設計，一次性解決根本問題
- **學習：** SOP 模式（問題分析 → 方案選擇 → 架構設計 → 完整實施 → 端到端驗證）

### 記憶體系統：三層架構
1. **MEMORY.md**（主索引）- 快速導航，核心知識
2. **INDEX.md**（主題索引）- 按主題分類，交叉引用
3. **memory/YYYY-MM-DD.md**（每日記錄）- 完整的原始記錄

### 並發執行策略
- ✅ 一次啟動 5 個任務（充分利用並發能力）
- ✅ 使用 Research 代理進行網絡搜索（100% 可靠）
- ✅ 使用 Analyst 代理進行分析（100% 可靠）
- ❌ 避免使用 Automation 代理（0% 可靠）

### 任務診斷與恢復
- **原則：** 檢查輸出文件存在且完整，再決定是否失敗
- **發現：** 很多 "terminated" 任務實際已完成（文件 > 20KB）
- **解決：** 更正狀態，自動恢復卡住任務

### 策略分類與評估標準（2026-02-27 20:45）
- **核心洞察：** 不同類型的策略評估方式完全不同！不能一概而論
- **趨勢跟踪（Supertrend, MACD）：** 總收益率 > 最大回撤 > 夏普比率 > 盈虧比；勝率30-50%正常
- **均值回歸（RSI, Bollinger）：** 勝率 > 交易頻率 > 回歸速度 > 殘差穩定性；勝率70-90%正常
- **動量策略：** 動量持續性 > 換手率 > 信息比率；勝率55-65%正常
- **應用：** 重新評估 RSI、Supertrend、MACD 策略

### 單一資產 vs 組合級別（2026-02-27 20:52）
- **核心問題：** 只操作 2330.TW 是不合理的！如果都沒行情就被固定成本壓垮了
- **單一資產風險：** 固定成本佔比巨大，缺乏多樣化
- **組合級別優勢：** 固定成本分攤到多個交易，分散風險
- **推薦：** 組合級別回測（50 隻股票）

### 數據驗證重要性（2026-02-28）
- **核心原則：** 數據驗證是研究的生命線
- **驗證檢查清單：** 邏輯一致性、概率分析、數據洩漏、計算方式一致性
- **關鍵教訓：** 勝率 100% 不可能，數據洩漏是回測的大敵

### 量化研究核心原則（2026-03-02）
- **簡單驗證 > 複雜未驗證：** 1/N 等權重、開盤區間突破等簡單策略表現優於複雜優化
- **樣本外測試至關重要：** 避免過度優化、考慮交易成本、驗證參數穩定性
- **AI 深刻改變市場：** AI 交易者能自主學習合謀、市場效率會被參與者影響、因子投資仍然有效
- **部位規模是戰略選擇：** 波動率目標法提供穩定性、波動率均等法平衡風險回報、金字塔加碼法追求高回報但風險巨大

### Kelly 準則發展（2026-03-02）
- **1956 原始論文：** 最優資金管理的數學基礎，連接信息論與投資
- **Kelly + VIX Hybrid (2025)：** 混合方法在增長與風險控制間取得最佳平衡
- **關鍵洞察：** log wealth 優化、避免賭徒破產、最大增長率等於信息傳輸率

### 睡覺模式任務系統（2026-03-16）
- **核心原則：** 利用空檔時間推進「重要但不緊急」的事務
- **執行矩陣：**
  - 緊急（卡住任務、錯誤）→ 主動執行
  - 重要（商業模式討論）→ 被動執行（你提醒）
  - 重要但不緊急（商業模式推進、知識整理）→ 睡覺時做
- **觸發條件：** 時間 23:00-08:00 + 距離上次用戶消息 > 2 小時 + 系統健康度 ≥ 0.5
- **任務類別：**
  - 商業模式推進（競爭對手研究、產品設計）
  - 知識整理（記憶維護、知識圖譜更新）
  - 技能優化（代碼重構、文檔更新）
  - 技術探索（新技術評估、原型開發）
- **執行頻率：** 每次睡覺時間執行 1-2 個任務
- **第二天早上匯報：** 簡要匯報昨晚完成的任務和進度
- **核心優勢：** 不打擾你、持續推進、利用空檔時間


## 🔧 Quick Commands & Paths

### Scout Agent
```bash
# 掃描所有數據源
cd ~/.openclaw/workspace-scout && python3 scout_agent.py scan

# 只掃描爬文數據源
python3 scout_agent.py web-only

# 查看統計
python3 scout_agent.py stats
```

### Kanban System
# 執行任務
cd ~/workspace && python3 kanban-ops/task_runner.py

# 處理任務隊列
python3 kanban-ops/process_spawn_queue.py

# 同步任務狀態
python3 kanban-ops/task_sync.py

# 自動補充檢查
python3 kanban-ops/monitor_and_refill.py

### Research Projects
# GitHub Pages 轉換腳本
cd ~/workspace && python3 publish-new-reports.py

# Git 提交和推送
cd ~/workspace/report && git add . && git commit -m "Auto publish" && git push


## 📝 Memory Maintenance

### How to Update This File
1. **每日記錄：** 更新 `memory/YYYY-MM-DD.md`
2. **主題分類：** 重要知識提取到 `memory/topics/*.md`
3. **更新索引：** 更新此文件的「最近成就」和「系統狀態」
4. **保持精簡：** 此文件應 < 100 行，細節移到子文件

### Search Memory
# 使用 memory_search 工具
memory_search "market score v3"

# 手動瀏覽
ls -la memory/topics/


## 📅 Update Log
### 2026-03-17 (Today)
- ✅ 記憶維護執行
- ✅ 知識提取：0 個學習點
- ✅ 模式識別：2 個核心模式
- ✅ 決策記錄：1 個關鍵決策
- ✅ 記憶系統重構完成（方案 D 改進版）
  - 移除 kanban-workspace collection（563 files → 0）
  - 清理空 collections（27 個）
  - 建立 topics/ 目錄結構（5 個主題文件）
  - 重建 QMD collections（memory-daily + memory-topics）
  - GPU OOM 問題解決（102 files vs 657 files）

### 2026-03-16 (Today)
- ✅ 記憶維護執行
- ✅ 知識提取：0 個學習點
- ✅ 模式識別：2 個核心模式
- ✅ 決策記錄：1 個關鍵決策

### 2026-03-12 (Today)
- ✅ 記憶維護執行
- ✅ 知識提取：0 個學習點
- ✅ 模式識別：13 個核心模式
- ✅ 決策記錄：0 個關鍵決策

### 2026-03-06 (Today)
- ✅ 記憶維護執行
- ✅ 知識提取：0 個學習點
- ✅ 模式識別：8 個核心模式
- ✅ 決策記錄：3 個關鍵決策


### 2026-03-05 (Today)
- ✅ P0+P1+P2 系統優化全部完成（卡住任務 ⬇️ 100%）
- ✅ 完成研究：19 篇（機器學習、量化、市場微結構）
- ✅ 背壓機制整合（健康度動態調整 0.67-1.00）
- ✅ 優先級系統自動化（每次心跳執行）
- ✅ 持久 datetime 錯誤修復
- ✅ 系統健康度：1.00（完全健康）
- 📁 更新 memory/topics/system-architecture.md（添加優化成果）

### 2026-02-23
- ✅ Scout Phase 2.1-W + 2.2-W 完成
- ✅ 記憶體系統重組（main-sub 層級結構）
- 📁 創建 memory/topics/ 目錄
- 📁 將 MEMORY.md 內容分類到子文件

### 2026-02-22
- ✅ 市場分數 V3 開發完成
- ✅ 研究報告完成：雙市場確認策略

### 2026-02-21
- ✅ 多市場量化分析開始（47% 進度）
- ✅ 記憶索引 INDEX.md 創建（7.9 KB）
- ✅ 三層記憶架構建立


**Last Updated:** 2026-03-09 02:14 AM
**Version:** v3.3
**Size:** ~180 lines
**Updates:** 添加核心工作方法、核心洞察、可複用模式、效率提升指標

## 已有系統和工具（2026-03-09 01:17 AM）

### QMD 向量資料庫

**基本信息：**
- 路徑：knowledge/qmd/
- CLI 工具：qmd
- 支援：官方
- 狀態：已整合

**功能：**
- 語義向量搜索（qmd vsearch）
- 向量索引和存儲
- 元數據管理
- 多 collection 支援

**使用方式：**
```bash
# 搜索
qmd vsearch "搜索內容" -n 10

# 添加文件
qmd add file.md -c collection_name

# 更新元數據
qmd update file_id --metadata '{"key": "value"}'
```

**整合狀態：**
- qmd_integration.py（整合腳本）
- knowledge/qmd/（向量存儲）
- 已經有大量記憶資料

### Obsidian 整合

**基本信息：**
- 狀態：已整合
- 文件：
  - obsidian_wrapper.py（14,028 bytes）
  - obsidian_memory.py（7,078 bytes）
  - obsidian_integration.py（7,072 bytes）
  - memory_system.py（6,631 bytes）
  - memory_system_maintain.py（9,424 bytes）

**功能：**
- 文件操作（create, read, append, delete）
- 搜索（search, search_context）
- 連結分析（get_orphans, get_deadends, get_unresolved, get_backlinks）
- 標籤管理（get_tags）
- 每日筆記（daily_append）
- Vault 管理（vault_info, list_vaults）

**使用方式：**
```python
from obsidian_wrapper import ObsidianWrapper

obsidian = ObsidianWrapper(vault_path="~/Documents/Obsidian")

# 創建筆記
obsidian.create_note("note.md", "# 標題\n內容")

# 搜索
results = obsidian.search("搜索關鍵詞")

# 獲取孤立筆記
orphans = obsidian.get_orphans()
```

### Kanban 系統

**基本信息：**
- 文件：tasks.json
- 腳本：kanban-ops/（多個腳本）
- 狀態：已整合

**功能：**
- 任務管理
- 並發控制
- 自動啟動
- 狀態同步

### Dashboard

**基本信息：**
- 路徑：Dashboard/（符號鏈接）
- 框架：FastAPI + React
- 狀態：已整合

**功能：**
- 策略回測
- 數據可視化
- 系統監控

---

**最後更新：** 2026-03-09 01:17 AM
