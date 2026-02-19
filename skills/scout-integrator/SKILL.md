---
name: scout-integrator
description: Scout 整合器 - 當看板任務過少時自動觸發 Scout 掃描新主題，實現無狀態、事件驅動的自動任務補充系統。
---

# Scout Integrator - Scout 整合器

當看板任務數量低於閾值時，自動觸發 Scout Agent 掃描新主題，實現**事件驅動、無狀態**的自動任務補充。

## 核心設計哲學

**傳統方式（錯誤）：**
```
時間到 → Cron 觸發 → Scout 掃描 → 創建任務
```
問題：基於時間，不看當前狀態

**事件驅動（正確）：**
```
任務過少 → 自動觸發 → Scout 掃描 → 創建任務
```
優點：基於狀態，按需觸發

## 觸發條件

```python
if pending_task_count < TRIGGER_THRESHOLD:
    if time_since_last_scan > MIN_SCAN_INTERVAL_HOURS:
        trigger_scout_scan()
```

**配置：**
- `TRIGGER_THRESHOLD = 3` - 最低任務數量
- `MIN_SCAN_INTERVAL_HOURS = 2` - 最小掃描間隔

## 使用場景

### 場景 1：檢查是否需要觸發 Scout

在任何檢查看板任務的時候，同時檢查是否需要觸發 Scout：

```bash
python3 kanban-ops/scout_agent.py check
```

輸出：
- 當前任務數
- 是否觸發掃描
- 掃描結果（如果觸發）

### 場景 2：整合到現有任務流程

在檢查 pending 任務時，自動檢查 Scout：

```python
# 檢查任務
pending_count = get_pending_task_count()

print(f"Pending tasks: {pending_count}")

# 如果任務過少，觸發 Scout
if pending_count < 3:
    print("Task count low, triggering Scout...")
    result = subprocess.run([
        'python3', 'kanban-ops/scout_agent.py', 'check'
    ], capture_output=True, text=True)
    print(result.stdout)
```

### 場景 3：Heartbeat 整合

在定期 heartbeat 時自動檢查：

```bash
# 在 HEARTBEAT.md 中
每次 heartbeat 時執行：
1. 檢查任務數量
2. 如果 < 3，自動觸發 Scout check
3. 報告 Scout 發現的新任務
```

## 核心邏輯

### check_and_trigger()

```
1. 讀取 tasks.json
2. 計算 pending 任務數量
3. 如果 pending_count >= 3:
     → 不觸發，返回 "任務充足"
4. 如果 pending_count < 3:
     → 檢查上次掃描時間
     → 如果距上次掃描 < 2 小時:
         → 不觸發，返回 "剛掃描過"
     → 如果距上次掃描 >= 2 小時:
         → 觸發掃描
         → 執行 run_scan_cycle()
         → 返回掃描結果
```

### run_scan_cycle()

```
1. 掃描數據源（arXiv、Reddit、News）
2. 評分主題（4 維度）
3. 過濾（score >= 6.0）
4. 創建任務（最多 3 個）
5. 記錄日誌
```

## 整合到現有系統

### 方式 1：在 task-optimizer 中整合

修改 task-optimizer，在檢查任務時同時檢查 Scout：

```python
def check_tasks_with_scout():
    """檢查任務並自動觸發 Scout"""
    # 檢查任務
    pending_count = len(get_pending_tasks())

    # 如果任務過少，觸發 Scout
    if pending_count < 3:
        from scout_agent import ScoutAgent
        scout = ScoutAgent()
        scout.check_and_trigger()

    return pending_count
```

### 方式 2：在 Heartbeat 中整合

在每次 heartbeat 時檢查：

```bash
# HEARTBEAT.md
## Priority Tasks

### 1. 檢查任務數量並觸發 Scout
\`\`\`bash
python3 kanban-ops/scout_agent.py check
\`\`\`

如果返回 "Scan triggered"，報告新發現的任務。
```

### 方式 3：創建獨立監控腳本

創建一個簡單的監控腳本：

```python
#!/usr/bin/env python3
# kanban-ops/monitor_and_refill.py

import json
import subprocess
from pathlib import Path

TASKS_JSON = Path.home() / '.openclaw/workspace/kanban/tasks.json'
THRESHOLD = 3

def check_and_refill():
    """檢查任務數量並自動補充"""
    with open(TASKS_JSON, 'r') as f:
        tasks = json.load(f)

    pending = [t for t in tasks if t['status'] == 'pending']
    print(f"Pending tasks: {len(pending)}")

    if len(pending) < THRESHOLD:
        print("Task count low, triggering Scout...")
        result = subprocess.run([
            'python3', 'kanban-ops/scout_agent.py', 'check'
        ], capture_output=True, text=True)
        print(result.stdout)
    else:
        print("Task count OK")

if __name__ == '__main__':
    check_and_refill()
```

## 反饋循環

### 查看統計

```bash
python3 kanban-ops/scout_agent.py stats
```

重點關注：
- `tasks.pending_count` - 當前任務數
- `tasks.should_scan` - 是否該掃描
- `feedback.total_feedbacks` - 反饋數量
- `preferences.average_rating` - 推薦品質

### 提供反饋

```bash
python3 kanban-ops/scout_agent.py feedback \
  --task-id 20260219-170653-s000 \
  --rating 5 \
  --depth deep
```

## 監控指標

### 成功指標

- **自動觸發率**：當任務 < 3 時，有多少比例自動觸發了掃描
- **推薦準確率**：推薦任務的評分 >= 4 星的比例
- **任務執行率**：Scout 推薦的任務被執行的比例
- **反饋提交率**：用戶提供反饋的比例

### 系統健康度

```python
system_health = {
    "pending_tasks": 4,          # 當前任務數
    "last_scan": "2h ago",       # 上次掃描
    "scout_tasks_created": 12,   # Scout 創建的任務數
    "feedback_received": 8,      # 收到的反饋數
    "average_rating": 4.2        # 平均評分
}
```

## 避免過度掃描

### 保護機制

1. **最小間隔** - 2 小時內不重複掃描
2. **任務閾值** - 只在任務真的少時觸發
3. **最大創建數** - 每次最多創建 3 個任務
4. **分數閾值** - 只創建高品質任務（>= 6.0）

### 檢查掃描日誌

```bash
cat ~/.openclaw/workspace-scout/SCAN_LOG.md
```

## 故障排除

### Scout 沒有觸發

**原因 1**：任務數 >= 3
```bash
python3 kanban-ops/scout_agent.py stats | grep pending_count
```

**原因 2**：距上次掃描 < 2 小時
```bash
cat ~/.openclaw/workspace-scout/TOPICS_CACHE.json | grep last_scan
```

**原因 3**：Scout 異常
```bash
python3 kanban-ops/scout_agent.py scan
```

### 沒有創建任務

**原因**：沒有高分主題
- 查看 SCAN_LOG.md 確認掃描結果
- 調整 SCORE_THRESHOLD（目前 6.0）

### 推薦品質差

**解決**：提供更多反饋
- 對每個 Scout 任務提供評分
- Scout 會從反饋中學習偏好

## 配置調整

### 調整觸發閾值

在 `scout_agent.py` 中修改：

```python
TRIGGER_THRESHOLD = 3  # 改為 2 或 4
SCORE_THRESHOLD = 6.0  # 改為 5.0 或 7.0
MAX_TASKS_PER_SCAN = 3  # 改為 2 或 5
MIN_SCAN_INTERVAL_HOURS = 2  # 改為 1 或 4
```

## 工作流程示例

```
【用戶使用系統】
    ↓
【完成一些任務】pending: 5 → 2
    ↓
【系統檢查任務】發現 pending < 3
    ↓
【自動觸發 Scout】執行 check_and_trigger()
    ↓
【Scout 掃描】發現 29 個主題
    ↓
【評分並過濾】13 個高分主題
    ↓
【創建任務】加入 3 個新任務到 Kanban
    ↓
【pending: 2 → 5】任務補充完成
    ↓
【繼續工作】
```

## 總結

這個整合器實現了：

✅ **事件驅動** - 基於任務數量，不是時間
✅ **無狀態服務** - 不需要記住上次掃描
✅ **自動補充** - 任務少時自動尋找新任務
✅ **學習優化** - 從反饋中改進推薦
✅ **避免過度** - 有保護機制防止過度掃描

---

**無需 Cron，無需定時，純粹事件驅動！**
