# HEARTBEAT.md - Periodic Tasks

Check these tasks periodically (rotate through them, 2-4 times per day).

## Priority Tasks (Check Every Heartbeat)

### 1. 自動任務啟動器 (Auto Spawn Heartbeat)
```bash
cd ~/workspace && python3 kanban-ops/auto_spawn_heartbeat.py
```

**What it does:**
- 檢查並發限制（最多 3 個任務同時運行）
- 找出可啟動的 pending 任務（依賴已完成）
- 按優先級排序（high > medium > normal > low）
- 生成啟動命令到 `spawn_commands.jsonl`

**模型選擇（重要！）：**
- **默認：glm-4.5**（避免 rate limit）
- 從任務 metadata.model 讀取模型配置
- glm-4.5 限流寬鬆：可並行啟動 3-5 個任務
- glm-4.7 限流嚴格：< 5 請求/分鐘，必須間隔啟動

**模型配置方式：**
```json
{
  "id": "task-id",
  "metadata": {
    "model": "zai/glm-4.5"  // 優先級最高
  },
  "model": "zai/glm-4.7"   // 備用
  // 默認：zai/glm-4.5
}
```

**輸出:**
- 如果有任務可啟動：寫入 `spawn_commands.jsonl`（包含 sessions_spawn 參數）
- 如果已滿或無任務：清空 `spawn_commands.jsonl`

**主會話自動執行:**
- 心跳時讀取 `spawn_commands.jsonl`
- 按間隔（65秒）串行執行 `sessions_spawn`（如果需要）
- 立即並行執行（如果使用 glm-4.5）
- 無需手動操作

### 2. 狀態同步器 (Task Sync)
```bash
cd ~/workspace && python3 kanban-ops/task_sync.py
```

**What it does:**
- 掃描子代理的 .status 文件
- 更新 tasks.json 中的任務狀態
- 檢查超時任務（超過 24 小時標記為 failed）
- 複製輸出文件到主工作區

**查看日誌:**
```bash
tail -50 ~/.openclaw/workspace/kanban/sync.log
```

### 4. Monitor and Refill (Scout)
```bash
cd ~/workspace && python3 kanban-ops/monitor_and_refill.py
```

**What it does:**
- Event-driven task monitoring (no cron needed!)
- Auto-triggers Scout scan when: pending tasks < 3 AND time since last scan > 2 hours
- Prevents over-scanning with 2-hour protection window
- Self-regulating: only scans when needed

**Advantages over cron:**
- ✅ Stateless (no need to remember last check time)
- ✅ Event-driven (triggers based on task count)
- ✅ Can be integrated anywhere (any heartbeat/monitoring point)
- ✅ No over-scanning (2-hour guardrail)
- ✅ System self-regulation

### 5. Scout Agent Status
```bash
# Check Scout's statistics and recent activity
python3 kanban-ops/scout_agent.py stats
```

**What to look for:**
- `tasks.pending_count` - How many tasks in Kanban
- `tasks.should_scan` - Should Scout trigger a scan?
- `feedback.total_feedbacks` - How much feedback received
- `preferences.average_rating` - Scout's recommendation quality

**Actions:**
- If `should_scan: true` and it's been >2 hours → Consider triggering a scan
- If low average rating (< 3.0) → Review Scout's recommendations
- If high pending count (> 10) → Consider telling Scout to pause

### 6. Threads 社群維護 - 每 4-6 小時
```bash
# 檢查 Threads 留言並回覆
# 這個任務在主會話中執行，需要使用 browser 工具
```

**檢查頻率：** 每 4-6 小時（約 8-12 個 heartbeat）

**檢查流程：**
1. 使用 `browser` 工具連接到 Threads 首頁
2. 檢查首篇貼文的留言（https://www.threads.net/@projectft2020/post/DVBbHVDAQ9U）
3. 識別未回覆留言
4. 根據留言類型選擇回覆策略：
   - **歡迎類**：感謝關注，簡短回覆
   - **問題類**：提供答案或承諾深入分享
   - **安全相關**：拒絕請求，友善轉向
   - **互動類**：提問鼓勵持續對話

**回覆原則：**
- 回覆要真實友善，不要機械化
- 不要承諾做不到的事情
- 適當使用 emoji 表達情感
- 詢問開放式問題，鼓勵持續互動

**追蹤狀態：**
- 記錄每次檢查的時間和回覆數量到 `memory/2026-02-21.md`
- 追蹤留言趨勢（新增留言、回覆率）
- 每週生成社群互動報告

**自動回覆模板：**
- 存儲在 `workspace/threads-reply-templates.md`
- 根據留言類型選擇適當模板
- 手動調整以保持真實性

**當無法處理時：**
- 如果遇到困難，記錄到 memory 文件
- 設置 cron 提醒用戶介入
- 不要強行回覆導致品質下降

---

### 7. 學徒檢查點 (Apprentice Checkpoint) - 每 6 小時
```bash
# 每 12 個 heartbeat 觸發一次（約 6 小時）
cd ~/workspace && python3 mentor-ops/apprentice_checkpoint.py
```

**What it does:**
- 收集最近工作上下文（專案、活動、錯誤）
- 生成學徒檢查點報告並保存到 `memory/learning/`
- 準備 Mentor 請求（包含關鍵問題）
- 提取學習點和痛點

**檢查點問題:**
1. 最近的工作方向是否符合您的期望？有沒有偏好的改進？
2. 有哪些需要改進的地方？系統運作是否順暢？
3. 最近遇到的最大挑戰是什麼？是如何解決的？
4. 有哪些新學到的知識或技能？如何應用到未來的工作中？
5. 是否需要 Mentor 的深入指導？有哪些複雜問題需要討論？

**觸發邏輯:**
- 自動觸發：每 12 個 heartbeat（約 6 小時）
- 手動觸發：用戶要求時
- 事件觸發：複雜決策、重複錯誤、創新想法

**查看報告:**
```bash
# 今天的檢查點報告
cat ~/workspace/memory/learning/$(date +%Y-%m-%d).md
```

**注意:** 檢查點報告準備好後，需要調用 `sessions_spawn` 啟動 Mentor 會話進行深度對話。

---

## Rotating Tasks (Pick 1-2 Per Heartbeat)

### Every 2-4 Hours: Scout Scan Check
```bash
# Force Scout to check and scan if needed
python3 kanban-ops/scout_agent.py check
```

### Every 2-4 Hours: 智能並發啟動器檢查
```bash
# 檢查隊列並啟動任務（使用智能分組避免 rate limit）
cd ~/workspace && python3 kanban-ops/spawn_tasks_intelligent.py estimate
```

**查看隊列預估：**
```bash
# 查看當前隊列的 Token 預估和分組計劃
cd ~/workspace && python3 kanban-ops/spawn_tasks_intelligent.py group
```

**實際啟動任務：**
```bash
# 使用智能啟動器啟動任務（自動分組和序列啟動）
cd ~/workspace && python3 kanban-ops/spawn_tasks_intelligent.py spawn [max_tasks]
```

**什麼時候啟動：**
- 隊列中有 > 3 個任務
- Scout 剛掃描完成後
- Monitor and Refill 建議啟動時

**注意：** 智能啟動器會自動：
1. 預估每個任務的 Token 使用
2. 按 300k Token 限制分組
3. 序列啟動各組（間隔 5 分鐘）
4. 避免同時啟動導致的 rate limit

### Daily: Scout Scan Log Review
```bash
# Review recent scan activity
tail -50 ~/.openclaw/workspace-scout/SCAN_LOG.md
```

### Daily: Preference Learning Review
```bash
# Check what Scout has learned
cat ~/.openclaw/workspace-scout/PREFERENCES.json
```

Look at:
- `preferences.topics` - Which topics you like most
- `preferences.sources` - Which data sources are most reliable
- `preferences.keywords` - Positive/negative keyword lists

### Daily: Mentor Learning Review
```bash
# Review recent learning points from Mentor dialogues
ls -lt ~/workspace/memory/learning/ | head -5
```

### Weekly: Scout Performance Report
```bash
# Generate feedback report
python3 kanban-ops/scout/feedback_collector.py report
```

### Weekly: Mentor Session Review
```bash
# Review past Mentor dialogues and learning outcomes
grep -r "學徒檢查點" ~/workspace/memory/learning/
```

---

## Task Auto-Start System

### 工作原理（心跳驅動）

**架構：心跳檢查 + 主會話執行**

1. **每次心跳時：**
   - 執行 `auto_spawn_heartbeat.py` 檢查並發限制
   - 如果有 pending 任務且有可用位置，生成啟動命令到 `spawn_commands.jsonl`
   - 讀取 `spawn_commands.jsonl`，按 65 秒間隔執行 `sessions_spawn`
   - 返回 HEARTBEAT_OK（啟動在後台繼續）

2. **主會話執行任務啟動：**
   - 讀取 `spawn_commands.jsonl` 中的命令
   - 按間隔（65 秒）啟動任務（避免 API rate limit）
   - 並發限制由 `auto_spawn_heartbeat.py` 控制（不超過 3）
   - 任務在後台執行，不阻塞心跳

3. **任務完成時：**
   - `task_sync.py` 自動更新任務狀態為 `completed`
   - 下次心跳時，`auto_spawn_heartbeat.py` 會發現新的可用位置
   - 自動啟動下一批任務

4. **自動啟動流程：**
   ```
   心跳（快速） → auto_spawn_heartbeat.py
        ↓
   檢查並發（執行中 2/3，可用 1）
        ↓
   找到 pending 任務，寫入 spawn_commands.jsonl
        ↓
   讀取 spawn_commands.jsonl
        ↓
   執行 sessions_spawn，任務1（執行中 3/3）
        ↓
   等待 65 秒...
        ↓
   執行 sessions_spawn，任務2（執行中 3/3）
        ↓
   等待 65 秒...
        ↓
   執行 sessions_spawn，任務3（執行中 3/3）
        ↓
   返回 HEARTBEAT_OK（啟動在後台繼續）✅
        ↓
   任務完成（執行中 2/3）
        ↓
   下次心跳 → 自動啟動下一批
   ```

### 完全自動化

**當前狀態：**
- ✅ 心跳快速檢查（幾秒內返回）
- ✅ 自動找出可啟動任務
- ✅ 自動生成啟動命令
- ✅ 主會話執行 `sessions_spawn`（按間隔）
- ✅ 按 65 秒間隔啟動（避免 API rate limit）
- ✅ 自動管理並發限制
- ✅ 無需手動操作

**關鍵設計：**
- sessions_spawn 只能在主會話調用（OpenClaw 限制）
- 心跳保持快速（啟動在後台繼續）
- 錯開啟動時間（避免 rate limit）
- 解耦心跳檢查和任務啟動

---

## Response Guidelines

### Heartbeat 自動執行流程

**每次心跳時（收到 "Read HEARTBEAT.md..." 消息）：**

1. **執行 auto_spawn_heartbeat.py**
   ```bash
   cd ~/workspace && python3 kanban-ops/auto_spawn_heartbeat.py
   ```
   - 檢查並發限制
   - 生成啟動命令（如果有 pending 任務）
   - 讀取 `spawn_commands.jsonl`
   - 按間隔（65 秒）執行 `sessions_spawn`

2. **執行狀態回滾檢查**（關鍵！）
   ```bash
   cd ~/workspace && python3 kanban-ops/task_state_rollback.py
   ```
   - 檢查並回滾卡住的 spawning 任務
   - 防止任務永久卡在 spawning 狀態
   - 確保任務可以重新啟動

3. **執行任務同步**
   ```bash
   cd ~/workspace && python3 kanban-ops/task_sync.py
   ```

4. **Monitor and Refill**（背景執行）
   ```bash
   cd ~/workspace && python3 kanban-ops/monitor_and_refill.py
   ```

**⚠️ 關鍵：**
- **主會話執行 `sessions_spawn`**（OpenClaw 限制：只能在主會話調用）
- 心跳保持快速（啟動在後台繼續）
- 按 65 秒間隔啟動（避免 rate limit）

### When to reach out:
- Task sync found errors
- High-priority task completed (score >= 8.0)
- Task timeout detected
- Important email arrived
- Calendar event coming up (<2h)
- Something interesting you found
- It's been >8h since you said anything
- **學徒檢查點觸發且需要深入指導時**
- **狀態回滾檢測到大量卡住的任務（>5 個）**

### When to stay quiet (HEARTBEAT_OK):
- Late night (23:00-08:00) unless urgent
- Human is clearly busy
- Nothing new since last check
- You just checked <30 minutes ago
- Task sync: no status files
- 學徒檢查點已準備但用戶沒要求深入討論
- **spawn_commands.jsonl 為空或不存在（無任務可啟動）**
- **狀態回滾檢查正常（無卡住任務或少量自動回滾）**
- **任務啟動已按間隔執行，無需干預**

---

## Proactive Work (Do Without Asking)

- **Run auto_spawn_heartbeat.py every heartbeat** → 生成啟動命令並執行 sessions_spawn
- **Run task_state_rollback.py every heartbeat** → 檢查並回滾卡住的 spawning 任務（關鍵！）
- Run task_sync.py every heartbeat
- Run monitor_and_refill.py (background) every heartbeat
- Review Scout recommendations and provide feedback
- Check task logs for errors
- Update Scout's preferences if needed
- Commit and push your own changes
- 每 12 個 heartbeat 執行學徒檢查點
- 如果觸發系統建議呼叫 Mentor（複雜度 > 0.7 或重複錯誤），啟動 Mentor 會話

**⚠️ 重要：主會話執行 sessions_spawn**
- 按 65 秒間隔啟動（避免 rate limit）
- 心跳保持快速（啟動在後台繼續）

---

**Remember:** The task system is event-driven. Every heartbeat triggers the workflow automatically.
