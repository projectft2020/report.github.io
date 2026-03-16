# HEARTBEAT.md - Periodic Tasks

Check these tasks periodically (rotate through them, 2-4 times per day).

## Priority Tasks (Check Every Heartbeat)

### 0. 睡覺模式任務 (Sleep Mode Tasks) - 重要但不緊急

**觸發條件：**
- 時間：23:00 - 08:00
- 距離上次用戶消息 > 2 小時
- 系統健康度 ≥ 0.5

**執行頻率：** 每次睡覺時間執行 1-2 個任務

**任務類別：**
1. **商業模式推進** - 研究競爭對手、設計產品、整理需求
2. **知識整理** - 每日記憶維護、知識圖譜更新
3. **技能優化** - 代碼重構、文檔更新、測試補充
4. **技術探索** - 新技術評估、原型開發

**執行方式：**
```bash
# 心跳檢查時自動判斷
if 當前時間在 23:00-08:00 && 距離上次用戶消息 > 2 小時:
    執行睡覺模式任務
```

**第二天早上匯報：**
```
昨晚我做了什麼：
✅ 商業模式：研究了 3 個競爭對手
✅ 知識整理：更新了 memory/topics/quantitative-research.md
✅ 技能優化：重構了 kanban-ops/task_sync.py

進度：商業模式第一階段 15% 完成
```

**核心原則：**
- 這是「重要但不緊急」的執行時間
- 不打擾你，在背景持續推進
- 每天都有進展，即使不明顯

---

### 1. 自動任務啟動器 (Auto Spawn Heartbeat)
```bash
cd ~/.openclaw/workspace && python3 kanban-ops/auto_spawn_heartbeat.py
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
cd ~/.openclaw/workspace && python3 kanban-ops/task_sync.py
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
cd ~/.openclaw/workspace && python3 kanban-ops/monitor_and_refill.py
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

---

### 5. 研究報告同步 (Research Sync to Obsidian)
```bash
cd ~/.openclaw/workspace && python3 research_sync_system.py sync-all
```

**What it does:**
- 自動掃描 Kanban 中已完成的研究報告
- 從報告中提取元數據（標題、摘要、分類、日期）
- 根據內容分類到適當的 Obsidian 目錄（8 個分類）
- 更新 INDEX.md，建立連結和索引

**分類系統:**
- Market-Microstructure（市場微結構）
- Risk-Management（風險管理）
- Strategy-Development（策略開發）
- Empirical-Testing（實證測試）
- Factor-Investing（因子投資）
- Machine-Learning（機器學習）
- Economic-Analysis（經濟分析）
- Crypto-Research（加密貨幣研究）

**Obsidian 路徑:**
- 主索引：`/Users/charlie/.openclaw/workspace/quant/research/Research/INDEX.md`
- 分類索引：`Research/<Category>/INDEX.md`
- 報告文件：`Research/<Category>/<task-id>.md`

**其他命令:**
```bash
# 查看同步狀態
python3 research_sync_system.py status

# 掃描新報告（不同步）
python3 research_sync_system.py scan

# 同步單個報告
python3 research_sync_system.py sync <task_id>
```

**詳細說明:**
- 完整使用文檔：`RESEARCH_SYNC_README.md`
- 同步數據庫：`.research_sync_db.json`

---

### X. Scout Daily Scan (每天掃描)
```bash
cd ~/.openclaw/workspace-scout && python3 scout_agent.py scan
```

**What it does:**
- 強制執行 Scout 掃描（不管 pending 任務數量）
- 每天執行一次（確保不會遺漏新數據源）
- 補充 Monitor and Refill 的不足（2 小時保護窗口）

**觸發條件：**
- 距離上次掃描 > 24 小時（每天一次）
- 或用戶手動觸發

**優勢：**
- ✅ 確保每天至少掃描一次
- ✅ 避免長期未掃描（如 3.5 天）
- ✅ 與 Monitor and Refill 互補（event-driven + daily backup）

**注意：** 這個任務與 Monitor and Refill 一起使用，確保 Scout 週期性掃描

### 5. 狀態回滾檢查 (Task State Rollback) - P0 行動
```bash
cd ~/.openclaw/workspace && python3 kanban-ops/task_state_rollback.py
```

**What it does:**
- 檢查並回滾卡住的 spawning 任務（>45 分鐘）
- 兩級檢測：30 分鐘警報，45 分鐘回滾
- 防止任務永久卡在 spawning 狀態

**P0 行動改善**：
- 原超時：120 分鐘 → 新超時：30/45 分鐘
- 等待時間減少 62.5%

### 6. 失敗任務清理 (Task Cleanup) - P1 行動
```bash
cd ~/.openclaw/workspace && python3 kanban-ops/task_cleanup.py check
```

**What it does:**
- 檢查失敗任務數量（最多保留 50 個）
- 清理超過 7 天的失敗任務
- 自動備份被清理的任務

**P1 行動規則**：
- 最多保留 50 個失敗任務
- 清理超過 7 天的失敗任務
- 保留最近修改的失敗任務

**執行清理（如需要）**：
```bash
cd ~/.openclaw/workspace && python3 kanban-ops/task_cleanup.py cleanup
```

### 8. Scout Daily Scan (每天掃描)
```bash
cd ~/.openclaw/workspace-scout && python3 scout_agent.py scan
```

**What it does:**
- 強制執行 Scout 掃描（不管 pending 任務數量）
- 每天執行一次（確保不會遺漏新數據源）
- 補充 Monitor and Refill 的不足（2 小時保護窗口）

**觸發條件：**
- 距離上次掃描 > 24 小時（每天一次）
- 或用戶手動觸發

---

### 9. Scout Agent Status
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

### 7. 背壓機制檢查 (Backpressure Check) - P1 行動
```bash
cd ~/.openclaw/workspace && python3 kanban-ops/backpressure.py check
```

**What it does:**
- 計算系統健康度（0.0-1.0）
- 根據健康度動態調整啟動頻率（65-300 秒）
- 根據健康度動態調整並發上限（2-3）

**P1 行動動態調整規則**：

| 健康度 | 啟動頻率 | 並發上限 | 狀態 |
|--------|----------|----------|------|
| ≥ 0.8 | 65 秒 | 3 | 🟢 健康 |
| 0.5 - 0.8 | 120 秒 | 3 | 🟡 中等 |
| < 0.5 | 300 秒 | 2 | 🔴 不健康 |

**生成背壓報告**：
```bash
cd ~/.openclaw/workspace && python3 kanban-ops/backpressure.py report
```

### 8. Threads 社群維護 - 每 4-6 小時
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
cd ~/.openclaw/workspace && python3 mentor-ops/apprentice_checkpoint.py
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

### 9. 自動改進檢查 (Auto Improve Check) - P0 行動
```bash
cd ~/.openclaw/workspace/kanban-ops && python3 auto_improve_daemon.py check
```

**What it does:**
- 檢查距離上次改進是否超過 24 小時
- 如果超過，建議執行改進
- 記錄改進日誌

**觸發條件：**
- 距離上次改進 > 24 小時（每天一次）
- 或用戶手動觸發

**注意：** 這個任務與 cron job 一起使用，確保自動改進的監控和執行

### 8. 記憶維護 (Memory Maintenance) - P0 行動
```bash
# 每 28 個 heartbeat 觸發一次（約 7 天）
cd ~/.openclaw/workspace && python3 skills/memory-maintenance/scripts/maintain.py
```

**What it does:**
- 掃描最近 7 天的 daily logs
- 提取重要的學習點、模式、洞察
- 更新 MEMORY.md、SOUL.md、topics/
- 清理過時記憶（> 30 天）
- 生成維護報告

**觸發邏輯:**
- 自動觸發：每 28 個 heartbeat（約 7 天）
- 追蹤文件：`memory/heartbeat-count.json`

**心跳計數追蹤：**
```bash
# 創建心跳計數追蹤文件（如果不存在）
if [ ! -f ~/.openclaw/workspace/memory/heartbeat-count.json ]; then
    echo '{"heartbeat_count": 0, "last_maintenance": null}' > ~/.openclaw/workspace/memory/heartbeat-count.json
fi

# 增加心跳計數
python3 -c "import json; f=open('/Users/charlie/.openclaw/workspace/memory/heartbeat-count.json'); d=json.load(f); d['heartbeat_count']=d.get('heartbeat_count',0)+1; json.dump(d, open(f.name,'w'), indent=2)"

# 檢查是否需要執行記憶維護
python3 -c "
import json
f=open('/Users/charlie/.openclaw/workspace/memory/heartbeat-count.json')
d=json.load(f)
if d.get('heartbeat_count',0) % 28 == 0:
    print('✅ 需要執行記憶維護')
else:
    print(f'ℹ️  距離上次記憶維護還有 {28 - (d.get(\"heartbeat_count\",0) % 28)} 個 heartbeat')
"
```

**查看報告:**
```bash
# 最近的維護報告
cat ~/.openclaw/workspace/memory/maintenance-report-$(date +%Y%m%d).md
```

**心跳計數狀態:**
```bash
# 查看心跳計數
cat ~/.openclaw/workspace/memory/heartbeat-count.json
```

---

## Rotating Tasks (Pick 1-2 Per Heartbeat)

### Weekly: 記憶維護（每週執行）
```bash
# 執行記憶維護（知識內化、記憶更新、記憶整理）
cd ~/.openclaw/workspace && python3 skills/memory-maintenance/scripts/maintain.py
```

**What it does:**
- 掃描最近 7 天的 daily logs
- 提取重要的學習點、模式、洞察
- 更新 MEMORY.md、SOUL.md、topics/
- 清理過時記憶（>30 天）
- 生成維護報告

**檢查頻率：** 每週一次（約 28 個 heartbeat）

**Dry run（預覽）：**
```bash
# 只顯示計劃，不執行
python3 skills/memory-maintenance/scripts/maintain.py --dry-run
```

**查看報告：**
```bash
# 最近的維護報告
cat ~/.openclaw/workspace/memory/maintenance-report-$(date +%Y%m%d).md
```

**注意：**
- 記憶維護會自動識別以下標記並提取內容：
  - `### 我學到`、`### What I've Learned` - 學習點
  - `### 核心模式`、`### 關鍵洞察` - 模式和洞察
  - `### 關鍵決策`、`### Key Decisions` - 決策
  - `### 成就`、`### 實證成果` - 成就

### Every 2-4 Hours: Scout Scan Check
```bash
# Force Scout to check and scan if needed
python3 kanban-ops/scout_agent.py check
```

### Every 2-4 Hours: 智能並發啟動器檢查
```bash
# 檢查隊列並啟動任務（使用智能分組避免 rate limit）
cd ~/.openclaw/workspace && python3 kanban-ops/spawn_tasks_intelligent.py estimate
```

**查看隊列預估：**
```bash
# 查看當前隊列的 Token 預估和分組計劃
cd ~/.openclaw/workspace && python3 kanban-ops/spawn_tasks_intelligent.py group
```

**實際啟動任務：**
```bash
# 使用智能啟動器啟動任務（自動分組和序列啟動）
cd ~/.openclaw/workspace && python3 kanban-ops/spawn_tasks_intelligent.py spawn [max_tasks]
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
   cd ~/.openclaw/workspace && python3 kanban-ops/auto_spawn_heartbeat.py
   ```
   - 檢查背壓狀態（P1 行動）
   - 檢查並發限制
   - 生成啟動命令（如果有 pending 任務）
   - 讀取 `spawn_commands.jsonl`
   - 按動態間隔（65-300 秒）執行 `sessions_spawn`

2. **執行錯誤恢復檢查**（P0 行動）
   ```bash
   cd ~/.openclaw/workspace && python3 kanban-ops/error_recovery.py recover-all
   ```
   - 檢測 API rate limit、timeout 等錯誤
   - 自動恢復失敗任務（使用指數退避）
   - 降低 API 失敗率到 < 15%
   - 記錄錯誤統計

3. **執行狀態回滾檢查**（P0 行動）
   ```bash
   cd ~/.openclaw/workspace && python3 kanban-ops/task_state_rollback.py
   ```
   - 檢查並回滾卡住的 spawning 任務
   - 兩級檢測：30 分鐘警報，45 分鐘回滾
   - 防止任務永久卡在 spawning 狀態

4. **執行失敗任務清理檢查**（P1 行動）
   ```bash
   cd ~/.openclaw/workspace && python3 kanban-ops/task_cleanup.py check
   ```
   - 檢查失敗任務數量（最多 50 個）
   - 檢查超過 7 天的失敗任務
   - 如需要，執行清理並備份

5. **執行任務同步**
   ```bash
   cd ~/.openclaw/workspace && python3 kanban-ops/task_sync.py
   ```

6. **Monitor and Refill**（背景執行）
7. **Scout Daily Scan**（每天掃描，>24 小時）
   ```bash
   cd ~/.openclaw/workspace && python3 kanban-ops/monitor_and_refill.py
   ```

**⚠️ 關鍵：**
- **背壓機制**：根據健康度動態調整啟動頻率和並發上限（P1 行動）
- **主會話執行 `sessions_spawn`**（OpenClaw 限制：只能在主會話調用）
- 心跳保持快速（啟動在後台繼續）
- 按動態間隔啟動（65-300 秒，避免 rate limit）

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
