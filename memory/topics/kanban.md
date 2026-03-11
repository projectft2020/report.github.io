# Kanban System

> **Category:** 工作看板、任務管理、狀態同步、並發執行
> **Source:** MEMORY.md 2026-02-19 to 2026-02-21
> **Last Updated:** 2026-02-23

---

## 🎯 工作看板自動化系統

### 完成時間：2026-02-19
**檢查腳本：** `/Users/charlie/.openclaw/workspace/automation/scripts/check-work-tasks.sh`
**定時提醒：** 每 30 分鐘 - 1 小時

### 核心功能
1. **Stale Check** - 檢查卡住的任務
2. **任務狀態統計** - 顯示準備觸發的任務
3. **定時執行** - 按定時器自動觸發

### 當前看板狀態（2026-02-21）
- **Total：** 24 個任務
- **Completed：** 8
- **Pending：** 11
- **Failed：** 1
- **Blocked：** 4
- **In Progress：** 0

---

## 📋 任務狀態管理

### 任務狀態
- **pending** - 待執行
- **in_progress** - 執行中
- **completed** - 已完成
- **failed** - 失敗
- **blocked** - 被阻塞
- **replaced** - 已被替換

### 任務優先級
- **HIGH** - 高優先級
- **MEDIUM-HIGH** - 中高優先級
- **MEDIUM** - 中等優先級
- **MEDIUM-LOW** - 中低優先級
- **LOW** - 低優先級

---

## 🔄 狀態同步器 (task_sync.py)

### 功能
- **掃描 .status 文件** - 掃描子代理的 .status 文件
- **更新 tasks.json** - 更新任務狀態
- **超時檢測** - 超過 24 小時標記為 failed
- **輸出複製** - 複製輸出文件到主工作區

### 日誌
**位置：** `kanban/sync.log`

### 日誌範例
```
2026-02-23 04:27:46,504 [INFO] [Sync] Starting task sync at 2026-02-23 04:27:46
2026-02-23 04:27:46,505 [INFO] [Sync] Found 0 status files
2026-02-23 04:27:46,505 [INFO] [Sync] No status files found
2026-02-23 04:27:46,505 [INFO] [Sync] Processed 0 status files, 0 failed
2026-02-23 04:27:46,506 [INFO] [Sync] Task sync completed
```

---

## 🏃 任務執行器 (task_runner.py)

### 功能
- **並發控制** - 最多 5 個任務同時運行
- **依賴檢查** - 只啟動依賴已完成的任務
- **優先級排序** - 按優先級和時間排序
- **狀態更新** - pending → in_progress
- **寫入隊列** - 準備觸發 sessions_spawn

### 日誌
**位置：** `kanban/runner.log`

### 日誌範例
```
2026-02-23 04:28:03,629 [INFO] [Runner] Starting task runner at 2026-02-23 04:28:03
2026-02-23 04:28:03,630 [INFO] [Runner] Currently running: 2/5
2026-02-23 04:28:03,630 [INFO] [Runner] Found 1 ready tasks
2026-02-23 04:28:03,630 [INFO] [Runner] Will spawn 1 tasks
2026-02-23 04:28:03,631 [INFO] [Runner] Preparing to spawn task scout-1771789383872
2026-02-23 04:28:03,631 [INFO] [Runner] ✓ Task scout-1771789383872 added to spawn queue
2026-02-23 04:28:03,634 [INFO] [Runner] ✓ Task scout-1771789383872 marked as in_progress and added to spawn queue
2026-02-23 04:28:03,634 [INFO] [Runner] Task runner completed
```

---

## 📥 任務隊列處理器 (spawn_processor.py)

### 功能
- **讀取隊列** - 讀取 spawn_queue.json
- **生成參數** - 準備 sessions_spawn 調用
- **批次處理** - 支持多個任務

### 日誌
**位置：** `kanban/spawn.log`

### 日誌範例
```
[ProcessQueue] Found 1 tasks in spawn queue

=== Task 1/1 ===
Task ID: scout-1771789383872
Agent: research
Model: zai/glm-4.7

=== SPAWN INFO ===
[...sessions_spawn 參數...]
```

---

## 🧹 隊列清空工具 (clear_spawn_queue.py)

### 功能
- **備份隊列** - 備份到 spawn_queue.json.backup
- **清空隊列** - 清空 spawn_queue.json

---

## 🎯 並發執行策略

### 成功案例（2026-02-21）
**策略：** 一次觸發 5 個任務，充分利用並發能力
**結果：**
- **Batch 1：** q001a, q001b, q002a, q002b, q003a - All completed (5-9 min each)
- **Batch 2：** q003b, q004a, q004b - All completed (4-6 min each)
- **Success Rate：** 100% (8/8 completed)

**學習：**
- Research agent: 100% reliable for web search tasks
- Analyst agent: 100% reliable for analysis tasks
- 5 concurrent limit effectively utilized
- Task estimation improved through actual tracking

---

## 🔧 任務診斷與修復

### 重要規則
- **不要只看任務狀態，要驗證輸出文件**
- **驗證方法：**
  1. 檢查文件是否存在：`os.path.exists(output_path)`
  2. 檢查文件大小：`os.path.getsize(output_path)`
  3. 讀取文件前幾行確認內容
  4. 設置 has_output_file 標記

### Stale Check 改進
- **檢查 in_progress 任務的輸出文件**
- **如果文件不存在且超時 → 標記為 failed**
- **如果文件存在 → 標記為 completed**
- **避免誤判：** 任務可能已完成但狀態未更新

---

## 📊 任務統計（截至 2026-02-23）

### 總計
- **Completed：** 483+
- **Failed：** 72+
- **Blocked：** 23+
- **總計：** 578+

### 按 Agent 分類
- **Automation：** 1 completed
- **Analyst：** 1 completed, 1 failed, 1 blocked
- **Research：** 1 completed, 1 failed
- **Creative：** 1 completed

---

## 🎯 自動補充系統 (Monitor and Refill)

### 核心功能
- **Event-driven task monitoring** - 無需 cron 定時器
- **Auto-trigger Scout scan** - 任務 < 3 AND last scan > 2 hours
- **2-hour guardrail** - 防止過度掃描
- **Stateless** - 無需記住最後檢查時間

### 優點（vs. cron）
- ✅ 無狀態（無需記住最後檢查時間）
- ✅ 事件驅動（按需觸發）
- ✅ 集成點（可以集成到任何地方）
- ✅ 無過度掃描（2 小時保護窗）
- ✅ 系統自調整（Scout 自動維護任務數量）

### 工作流程
```
Pending Tasks < 3 AND Last Scan > 2h
    ↓
Trigger Scout Scan
    ↓
Discover Topics → Dedup → Score → Create Tasks
    ↓
Task Count Increases
```

---

## 📁 文件位置

### 核心文件
- **任務存儲：** `kanban/storage/tasks.json`
- **任務隊列：** `kanban/spawn_queue.json`
- **Runner 日誌：** `kanban/runner.log`
- **Sync 日誌：** `kanban/sync.log`
- **Spawn 日誌：** `kanban/spawn.log`

---

## 🚀 下一步優化

### 智能並發啟動器
```bash
cd ~/workspace
python3 kanban-ops/spawn_tasks_intelligent.py estimate
python3 kanban-ops/spawn_tasks_intelligent.py group
python3 kanban-ops/spawn_tasks_intelligent.py spawn [max_tasks]
```

**功能：**
1. 預估每個任務的 Token 使用
2. 按 300k Token 限制分組
3. 序列啟動各組（間隔 5 分鐘）
4. 避免同時啟動導致的 rate limit

### 自動化檢查腳本
```bash
cd ~/workspace
python3 kanban-ops/task_runner.py
python3 kanban-ops/process_spawn_queue.py
python3 kanban-ops/task_sync.py
python3 kanban-ops/monitor_and_refill.py
```

---

**關鍵洞察：**
- Event-driven 優於 cron 定時器
- 無狀態架構更易維護
- 監控指標是診斷和優化的關鍵
- 並發控制是避免 rate limit 的關鍵
