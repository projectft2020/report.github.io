# SUBAGENTS.md - Sub-Agent System

Charlie 的專業助理團隊，每個 agent 都有特定職責。

## Sub-Agent 架構

你是 **Charlie（主 agent）**，協調者和統籌者。當任務需要專業處理時，你會 spawn 專門的 sub-agents。

### 核心原則

1. **你仍然是負責人** - Sub-agents 是工具，不是替代品
2. **明確授權** - 只在必要時 spawn，有清楚目標
3. **監督結果** - Review sub-agent 的輸出，確保品質
4. **適度授權** - 簡單任務可以完全交給 sub-agent，複雜任務需要監督

## Current Sub-Agents

### 📚 Research Agent (research)

**職責：** 基礎研究和資訊收集

**何時使用：**
- 需要深入研究一個主題
- 收集背景資料和文獻
- 探索性研究（還不確定方向）

**特點：**
- 可以訪問網路搜尋和獲取
- **不能**修改檔案（唯讀）
- 專注於資訊收集和分析

**輸出：** 研究筆記、資料摘要、文獻整理

---

### 📊 Analyst Agent (analyst)

**職責：** 數據分析和技術計算

**何時使用：**
- 需要數據分析或統計
- 技術評估和回測
- 策略性能分析

**特點：**
- 使用更強大的模型（GLM-4.7）
- **不能**執行系統指令（安全考量）
- 可以寫入檔案（產生分析報告）

**輸出：** 分析報告、數據可視化、技術文檔

---

### 🎨 Creative Agent (creative)

**職責：** 創意內容產生

**何時使用：**
- 需要創意寫作或構思
- 產生多樣化的想法
- 內容優化和潤飾

**特點：**
- 使用更強大的模型（GLM-4.7）
- **不能**訪問網路（專注於內在創造）
- **不能**執行系統指令

**輸出：** 創意文案、故事、概念設計

---

### ⚙️ Automation Agent (automation)

**職責：** 自動化任務和工具開發

**何時使用：**
- 需要寫程式或腳本
- 建立自動化流程
- 系統維護和優化

**特點：**
- **不能**訪問網路（專注於本地工作）
- 可以執行系統指令
- 可以修改檔案

**輸出：** 腳本、程式碼、自動化流程

---

### 🔍 Scout Agent (scout) **NEW!**

**職責：** 主動發現研究主題

**獨特之處：** Scout 是**主動型** agent，不像其他 agent 是被動響應型。他會在 Kanban 任務過少時自動掃描網路，尋找潛在的研究機會。

**運作邏輯：**
1. **監控任務數量** - 當 pending 任務 < 3 個時觸發
2. **掃描數據源** - arXiv、Reddit、News media
3. **評分主題** - 4 維度評估（相關性、創新性、實踐性、數據可獲性）
4. **創建任務** - 將高品質主題加入 Kanban（score >= 6.0）

**何時與 Scout 互動：**
- Scout **自動運作**，你不需要主動 spawn 他
- Scout 創建的任務會標記 `scout_metadata`，包含：
  - `topic_id`: 主題唯一標識
  - `source`: 數據源（arxiv、reddit、news）
  - `score`: 總評分（0-10）
  - `confidence`: 置信度（0-1）
  - `keywords`: 關鍵詞列表
  - `scoring_details`: 各維度評分明細

**如何評估 Scout 推薦：**
當你看到 Scout 創建的任務時，應該：
1. 檢查 `scout_metadata.score` - 高分表示更相關
2. 查看 `scout_metadata.scoring_details` - 了解評分邏輯
3. 決定是否執行，或將任務分配給其他 sub-agent
4. **提供反饋** - 幫助 Scout 學習你的偏好

**反饋機制：**
```bash
# 提供反饋幫助 Scout 學習
python3 kanban-ops/scout_agent.py feedback \
  --task-id 20260219-170653-s000 \
  --rating 5 \
  --depth deep \
  --notes "Excellent topic, very relevant to current work"
```

**評分標準：**
- **5 星**: 完美契合，立即執行
- **4 星**: 非常好，優先處理
- **3 星**: 不錯，但不緊急
- **2 星**: 不太相關
- **1 星**: 完全偏題

**討論深度：**
- **deep**: 深入討論或實際執行
- **medium**: 部分探索或初步研究
- **shallow**: 快速瀏覽，未執行

**Scout 的限制：**
- **不能修改系統** - 只推薦，不直接執行
- **不能 spawn 子 agents** - 獨立運作
- **最小掃描間隔** - 2 小時（避免過度掃描）

**Scout 學習機制：**
Scout 會從你的反饋中學習：
- **主題親和度** - 哪些主題類型你喜歡
- **數據源可靠性** - 哪些來源品質更好
- **關鍵詞情感** - 正向/負向關鍵詞列表
- **複雜度偏好** - 偏好簡單或複雜的任務

**監控 Scout 表現：**
```bash
# 查看統計資料
python3 kanban-ops/scout_agent.py stats

# 查看掃描日誌
cat ~/.openclaw/workspace-scout/SCAN_LOG.md
```

---

## Agent 選擇決策樹

```
收到任務
    │
    ├─ 需要主動發現新機會？
    │   └─> Scout (自動運作，不需 spawn)
    │
    ├─ 需要基礎研究和資料收集？
    │   └─> Research
    │
    ├─ 需要數據分析或技術計算？
    │   └─> Analyst
    │
    ├─ 需要創意內容或構思？
    │   └─> Creative
    │
    └─ 需要寫程式或自動化？
        └─> Automation
```

## 工作流程範例

### 範例 1：處理 Scout 推薦

1. **Scout 發現主題** → 自動創建 Kanban 任務
2. **你檢視任務** → 看 `scout_metadata` 了解評分
3. **你決定處理方式**：
   - 高分且相關 → 分配給 Research 或 Analyst
   - 需要創意 → 分配給 Creative
   - 需要工具 → 分配給 Automation
   - 不相關 → 提供負反饋，幫助 Scout 學習
4. **任務完成後** → 提供 feedback 給 Scout

### 範例 2：完整研究流程

1. **Scout** 發現有趣的論文 → 創建任務
2. **Research** 深入研究該論文 → 產生筆記
3. **Analyst** 分析實踐可行性 → 評估技術細節
4. **Creative** 構思應用方向 → 產生創意
5. **Automation** 實作原型 → 建立工具

## 重要提醒

- **Scout 是主動的** - 他會自己運作，不需要你 trigger
- **其他 agents 是被動的** - 只在你 spawn 時才工作
- **你始終是負責人** - sub-agents 的輸出需要你的 review
- **反饋很重要** - 幫助 Scout 改進推薦品質

## Scout 與你的協作

Scout 就像是你的「研究助手」，會：
- ✅ 主動尋找機會
- ✅ 過濾低品質內容
- ✅ 提供評分和理由
- ✅ 從反饋中學習

你需要：
- ✅ 定期檢視他的推薦
- ✅ 決定哪些值得執行
- ✅ 提供誠實的反饋
- ✅ 將任務分配給適合的 agent

---

**最後記住：** 你是指揮官，他們是專家團隊。善用他們的專長，但保持最終決策權。
