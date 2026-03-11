# 加速模式 v2.0 - 實現選項分析

## 🔍 調查結果

### 當前限制

**無法直接從獨立腳本調用 sessions_spawn：**

```python
# ❌ 獨立腳本中無法工作
from openclaw_tools import sessions_spawn  # ImportError
```

**原因：**
- `sessions_spawn` 是 OpenClaw 工具，只能在主會話中使用
- 獨立腳本運行在子進程中，無法訪問主會話的上下文

### OpenClaw CLI 檢查結果

| 命令 | 功能 | 適用性 |
|------|------|--------|
| `openclaw sessions` | 列出會話 | ❌ 不能創建 |
| `openclaw agents` | 管理隔離代理 | ❌ 不是任務觸發 |
| `openclaw agent` | 運行 agent turn | ⚠️ 需要 recipient |
| `openclaw acp` | ACP bridge | ❌ 互動式客戶端 |

**`openclaw agent` 限制：**
```bash
# 需要指定 recipient number
openclaw agent --to +15555550123 --message "status update"

# 不適合我們的場景：
# - 需要電話號碼/recipient
# - 這是 agent turn，不是 sub-agent
# - 無法輕鬆獲取返回的 sessionKey
```

---

## 📋 三個實現選項

### 選項 A：保持隊列模式（當前實現）

**流程：**
```
Turbo Mode → 寫入隊列 → 主會話消費 → sessions_spawn → 子代理
```

**優點：**
- ✅ 已經實現完成
- ✅ 測試通過
- ✅ 不需要額外權限

**缺點：**
- ❌ 不符合「無狀態」原則
- ❌ 需要主會話定期消費隊列
- ❌ 有延遲（取決於消費頻率）

---

### 選項 B：混合模式（推薦）⭐

**流程：**
```
Turbo Mode (獨立腳本) → 寫入隊列
                                   ↓
主會話 (HEARTBEAT) → 消費隊列 → sessions_spawn → 子代理
```

**實現方式：**

1. **Turbo Mode 端（不變）：**
   - 使用現有的隊列寫入機制
   - 任務寫入 `task_queue/` 目錄

2. **HEARTBEAT 端（新增）：**
   - 在 HEARTBEAT.md 中添加隊列消費邏輯
   - 每 30 分鐘檢查一次隊列
   - 使用 `sessions_spawn` 觸發任務

3. **監控端（新增）：**
   - 使用 `sessions_history` 監控子代理狀態
   - 更新 tasks.json 中的任務狀態
   - 超時檢測和自動重試

**HEARTBEAT.md 添加內容：**

```markdown
## Priority Tasks (Check Every Heartbeat)

### Task Queue Consumer
```bash
# 消費任務隊列
cd ~/workspace && python3 kanban-ops/consume_queue.py
```

**What it does:**
- 讀取 task_queue/ 目錄中的待執行任務
- 使用 sessions_spawn 觸發子代理
- 更新任務狀態為 in_progress
- 記錄 sessionKey 用於後續監控

**Frequency:** Every heartbeat (30 minutes)
**Max concurrent:** 5 (same as turbo_mode config)
```

**優點：**
- ✅ 使用主會話的 `sessions_spawn` 權限
- ✅ 利用現有 HEARTBEAT 機制
- ✅ 事件驅動（檢查時才消費）
- ✅ 實時監控（通過 sessions_history）
- ✅ 改動最小（只需添加消費邏輯）

**缺點：**
- ⚠️ 依賴 HEARTBEAT 頻率（30 分鐘）
- ⚠️ 有輕微延遲（最多 30 分鐘）

---

### 選項 C：Gateway API 模式（複雜）

**流程：**
```
Turbo Mode → Gateway WebSocket API → 觸發任務
```

**實現方式：**
- 直接調用 Gateway 的 WebSocket 或 HTTP API
- 需要 Gateway token 和 password
- 需要手動實現 ACP 協議

**優點：**
- ✅ 完全獨立（不依賴主會話）
- ✅ 實時觸發（無延遲）

**缺點：**
- ❌ 需要實現 ACP 協議
- ❌ 需要處理認證和安全
- ❌ 維護成本高
- ❌ 文檔不足

---

## 🎯 推薦方案：選項 B（混合模式）

### 理由

1. **符合設計原則**
   - 事件驅動（通過 HEARTBEAT）
   - 自我調節（根據並發限制）

2. **利用現有機制**
   - HEARTBEAT 已經定期運行
   - sessions_spawn 已經在主會話中可用
   - 不需要額外架構

3. **改動最小**
   - 只需添加一個消費腳本
   - 在 HEARTBEAT.md 中添加一行
   - turbo_mode.py 幾乎不用改

4. **可調試性好**
   - 日誌集中在主會話
   - 可以直接使用 sessions_history 監控

---

## 📝 實現計劃

### Phase 1: 消費腳本（30 分鐘）

**文件：** `kanban-ops/consume_queue.py`

```python
#!/usr/bin/env python3
"""
消費任務隊列

讀取 task_queue/ 目錄中的待執行任務，使用 sessions_spawn 觸發子代理。
"""

import json
import os
from pathlib import Path

# 注意：這個腳本需要在主會話中運行
# 才能使用 sessions_spawn 工具

def consume_queue(max_tasks=5):
    """消費任務隊列"""
    queue_dir = Path.home() / ".openclaw" / "workspace" / "kanban-ops" / "task_queue"

    # 讀取隊列中的任務
    tasks = []
    for task_file in queue_dir.glob("*.json"):
        with open(task_file, 'r') as f:
            task = json.load(f)
            tasks.append((task_file, task))

    # 最多觸發 max_tasks 個任務
    triggered = 0
    for task_file, task in tasks[:max_tasks]:
        if task.get('status') != 'pending':
            continue

        # 構建任務消息
        task_message = task['task']
        agent_id = task['agent_id']
        label = task['label']
        model = task['model']

        # TODO: 使用 sessions_spawn 觸發
        # result = sessions_spawn({
        #     "task": task_message,
        #     "agentId": agent_id,
        #     "label": label,
        #     "model": model
        # })

        # 更新狀態
        task['status'] = 'triggered'
        task['triggered_at'] = datetime.now().isoformat()

        # 保存更新
        with open(task_file, 'w') as f:
            json.dump(task, f, indent=2)

        triggered += 1

    return triggered

if __name__ == '__main__':
    import sys
    max_tasks = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    count = consume_queue(max_tasks)
    print(f"✅ 觸發 {count} 個任務")
```

### Phase 2: HEARTBEAT 集成（5 分鐘）

**修改 HEARTBEAT.md：**

```markdown
## Priority Tasks (Check Every Heartbeat)

### Task Queue Consumer
```bash
cd ~/workspace && python3 kanban-ops/consume_queue.py
```

**What it does:**
- 消費 task_queue/ 目錄中的待執行任務
- 最多觸發 5 個任務（遵循 turbo_mode 的並發限制）
- 使用 sessions_spawn 觸發子代理
- 更新任務狀態為 triggered

**注意：** 此腳本依賴主會話的 sessions_spawn 權限
```

### Phase 3: 監控腳本（30 分鐘）

**文件：** `kanban-ops/monitor_spawned_tasks.py`

```python
#!/usr/bin/env python3
"""
監控已觸發的任務

使用 sessions_history 檢查子代理狀態，更新 tasks.json。
"""

def monitor_tasks():
    """監控已觸發的任務"""
    # TODO: 實現
    pass

if __name__ == '__main__':
    monitor_tasks()
```

### Phase 4: 測試驗證（15 分鐘）

1. 啟動 Turbo Mode（測試模式）
2. 檢查隊列是否生成
3. 觸發 HEARTBEAT（手動）
4. 驗證任務是否被觸發
5. 檢查 sessions_history

---

## 🚀 總結

**推薦方案：選項 B（混合模式）**

**優勢：**
- 符合設計原則
- 利用現有機制
- 改動最小
- 可調試性好

**實現時間：** ~1.5 小時

**下一步：**
1. 實現 consume_queue.py
2. 更新 HEARTBEAT.md
3. 測試驗證

---

**需要開始實現嗎？** 🤔
