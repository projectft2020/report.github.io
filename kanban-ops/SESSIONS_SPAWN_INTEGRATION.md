# sessions_spawn 集成說明

## 概述

加速模式現在已經集成了 sessions_spawn 機制，可以實際觸發並執行 Kanban 任務。

## 架構設計

```
turbo_mode.py (決策層)
    ↓
task_queue/ (隊列層)
    ↓
process_task_queue.py (處理層)
    ↓
sessions_spawn (執行層)
```

## 職責分工

### 1. turbo_mode.py - 決策層

**職責：**
- 決定哪些任務應該被觸發
- 構建任務消息
- 將任務寫入隊列
- 記錄日誌

**優勢：**
- 不直接調用 sessions_spawn（避免複雜性）
- 職責單一：只負責決策
- 易於測試：可以使用模擬模式

### 2. process_task_queue.py - 處理層

**職責：**
- 讀取隊列中的任務
- 準備執行數據
- 清空隊列

**優勢：**
- 獨立腳本，可單獨運行
- 提供多種操作（list/pop/clear）
- 易於集成到主會話

### 3. sessions_spawn - 執行層

**職責：**
- 實際啟動子代理
- 管理子會話
- 返回執行結果

**優勢：**
- OpenClaw 原生工具
- 可靠穩定
- 完整的生命週期管理

## 使用流程

### 方式 1：手動執行

1. **啟動加速模式**
   ```bash
   python3 turbo_mode.py start
   ```

2. **檢查隊列**
   ```bash
   python3 process_task_queue.py list
   ```

3. **彈出任務**
   ```bash
   python3 process_task_queue.py pop
   ```

4. **執行任務**
   ```
   # 使用返回的任務數據
   sessions_spawn({
     "task": "TASK: ...",
     "agentId": "analyst",
     "label": "task-id",
     "model": "zai/glm-4.7"
   })
   ```

### 方式 2：自動執行（推薦）

**在主會話中創建一個腳本：**

```python
# auto_execute_tasks.py

import subprocess
import json
import time

while True:
    # 彈出任務
    result = subprocess.run(
        ['python3', '/path/to/process_task_queue.py', 'pop'],
        capture_output=True,
        text=True
    )

    if "隊列為空" in result.stdout:
        break

    # 解析任務數據
    # （需要改進 process_task_queue.py 輸出 JSON）

    # 執行任務
    sessions_spawn({...})

    # 等待
    time.sleep(10)
```

## 測試命令

### 測試 1：列出準備好的任務

```bash
python3 turbo_mode.py test-ready
```

**輸出示例：**
```
📋 測試：列出準備好的任務

============================================================

✅ 找到 3 個準備好的任務：

📌 20260220-020000-r004
   標題：動態策略切換系統
   代理：analyst
   優先級：medium
   項目：regime-detection-20260220

📌 20260220-030000-f001
   標題：擁擠度指標開發
   代理：analyst
   優先級：high
   項目：factor-crowding-20260220

📌 20260220-050000-st002
   標題：配對交易策略
   代理：analyst
   優先級：highest
   項目：statistical-arb-renaissance-20260220

============================================================
```

### 測試 2：觸發任務（模擬模式）

```bash
python3 turbo_mode.py test-spawn
```

**輸出示例：**
```
🧪 測試：觸發任務（模擬模式）

============================================================
🎯 觸發任務：20260220-020000-r004

🚀 觸發任務：20260220-020000-r004
   標題：動態策略切換系統
   代理：analyst
   模型：zai/glm-4.7
   優先級：medium
   項目：regime-detection-20260220
ℹ️ 觸發任務：20260220-020000-r004 (代理: analyst, 模型: zai/glm-4.7)
ℹ️ 任務已加入隊列: /Users/charlie/.openclaw/workspace/kanban-ops/task_queue/20260220-020000-r004_20260220_034722.json
✅ 任務 20260220-020000-r004 已成功啟動
ℹ️   Session Key: N/A

✅ 任務觸發成功

📋 檢查隊列：
============================================================
📋 隊列中共有 1 個任務：

📄 20260220-020000-r004_20260220_034722.json
   標籤：20260220-020000-r004
   代理：analyst
   模型：zai/glm-4.7
   狀態：pending
   創建時間：2026-02-20T03:47:22.675219

============================================================
```

### 測試 3：管理隊列

```bash
# 列出隊列
python3 process_task_queue.py list

# 彈出任務
python3 process_task_queue.py pop

# 彈出所有任務
python3 process_task_queue.py pop-all

# 清空隊列
python3 process_task_queue.py clear
```

## 隊列文件格式

```json
{
  "task": "TASK: 動態策略切換系統\n\nCONTEXT:\n...",
  "agent_id": "analyst",
  "label": "20260220-020000-r004",
  "model": "zai/glm-4.7",
  "created_at": "2026-02-20T03:47:22.675219",
  "status": "pending",
  "session_key": null
}
```

## 下一步改進

### 優先級 1：自動執行腳本

創建一個自動執行腳本，讀取隊列並調用 sessions_spawn：

```python
# auto_execute_queue.py

def execute_queue():
    while True:
        task = pop_task()
        if task is None:
            break

        # 調用 sessions_spawn
        sessions_spawn({
            "task": task["task"],
            "agentId": task["agent_id"],
            "label": task["label"],
            "model": task.get("model")
        })

        # 更新任務狀態
        # ...

        # 等待任務完成（可選）
        time.sleep(10)
```

### 優先級 2：改進 process_task_queue.py

添加 JSON 輸出模式，方便解析：

```python
elif command == 'pop':
    task = pop_task()
    if task:
        print(json.dumps(task, indent=2))
```

### 優先級 3：並行任務管理

添加並行任務追蹤和等待機制：

```python
# 等待並行任務完成
def wait_for_concurrent_tasks(max_concurrent=1):
    running_tasks = get_running_tasks()
    while len(running_tasks) >= max_concurrent:
        time.sleep(10)
        running_tasks = get_running_tasks()
```

## 總結

- ✅ turbo_mode.py 已集成 sessions_spawn（通過隊列）
- ✅ process_task_queue.py 已創建
- ✅ 測試命令已驗證
- ⏳ 自動執行腳本待創建
- ⏳ 並行任務管理待實現

**核心優勢：**
1. 職責清晰：決策 → 隊列 → 處理 → 執行
2. 易於測試：可以使用模擬模式
3. 易於維護：每層職責單一
4. 靈活擴展：可以添加多種執行策略
