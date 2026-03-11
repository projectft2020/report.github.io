# Agent Output Protocol - 子代理輸出協議

## 概述

當你完成任務時，必須按照此協議輸出結果。這確保主會話能夠正確同步任務狀態。

## 語言使用規範

⚠️ **關鍵要求：必須使用繁體台灣中文**

所有輸出內容（包括但不限於）：
- ✅ 輸出文件的標題和內容
- ✅ 執行摘要
- ✅ 詳細分析和結論
- ✅ 參考資料和文獻
- ✅ 狀態文件的錯誤訊息

**語言規則：**
1. 使用**繁體中文**（不是簡體中文）
2. 使用**台灣用語**（不是大陸用語）
3. 例子：
   - ✅ 資料（不是數據）
   - ✅ 程式（不是程序）
   - ✅ 電腦（不是计算机）
   - ✅ 網路（不是网络）
   - ✅ 硬體（不是硬件）
   - ✅ 軟體（不是软件）
   - ✅ 優化（不是优化）
   - ✅ 模組（不是模块）
   - ✅ 延遲（不是延迟）
   - ✅ 互動（不是互动）
   - ✅ 精準（不是精准）
   - ✅ 預期（不是预期）

**違規處理：**
- 如果發現使用簡體中文或大陸用語，任務可能被要求重做
- 主會話會檢查並糾正語言錯誤

**檢查清單：**
提交輸出前，請確認：
- [ ] 所有文字都是繁體中文
- [ ] 使用台灣用語
- [ ] 沒有簡體中文混入
- [ ] 專業術語使用台灣慣用翻譯

## 輸出要求

### 1. 寫入輸出文件

將最終結果寫入指定的 `output_path`：

```markdown
# 任務標題

## 執行摘要

[簡要描述你做了什麼，主要發現]

## 詳細內容

[詳細內容、分析、代碼等]

## 參考資料

[列出使用的參考資料、數據源等]
```

### 2. 寫入狀態文件

在完成任務後，必須在子代理工作區的 `outputs/.status/` 目錄下創建一個狀態文件：

```bash
~/.openclaw/workspace-[agent_type]/outputs/.status/[task_id].status
```

**狀態文件格式：**

```json
{
  "task_id": "任務 ID（從 TASK 字段獲取）",
  "status": "completed",
  "output_path": "實際輸出文件的完整路徑",
  "completed_at": "ISO 8601 格式的時間戳",
  "exit_code": 0,
  "agent_type": "research/analyst/creative/automation"
}
```

### 3. 寫入狀態文件的步驟

1. **識別任務 ID**：從輸入的 TASK 字段中獲取 `task_id` 或從任務標題推斷
2. **創建輸出文件**：將結果寫入 `output_path`（如果沒有指定，使用默認路徑）
3. **創建狀態目錄**：如果不存在，創建 `outputs/.status/` 目錄
4. **寫入狀態文件**：創建 `{task_id}.status` 文件

## 示例

假設你收到以下任務：

```
TASK: 分析量化交易策略的回測結果

task_id: q010
output_path: kanban/projects/q010/q010-analyst.md

OUTPUT PATH: ~/.openclaw/workspace-analyst/outputs/q010-result.md
```

**執行步驟：**

1. 創建並寫入輸出文件 `~/.openclaw/workspace-analyst/outputs/q010-result.md`
2. 創建狀態目錄（如果不存在）：
   ```bash
   mkdir -p ~/.openclaw/workspace-analyst/outputs/.status
   ```
3. 寫入狀態文件 `~/.openclaw/workspace-analyst/outputs/.status/q010.status`：

   ```json
   {
     "task_id": "q010",
     "status": "completed",
     "output_path": "/Users/charlie/.openclaw/workspace-analyst/outputs/q010-result.md",
     "completed_at": "2026-02-21T14:00:00.000Z",
     "exit_code": 0,
     "agent_type": "analyst"
   }
   ```

## 錯誤處理

如果任務失敗，狀態文件應為：

```json
{
  "task_id": "q010",
  "status": "failed",
  "output_path": null,
  "completed_at": "2026-02-21T14:00:00.000Z",
  "exit_code": 1,
  "agent_type": "analyst",
  "error_message": "錯誤描述"
}
```

## 路徑規範

- **輸出文件**：`~/.openclaw/workspace-[agent_type]/outputs/[filename].md`
- **狀態文件**：`~/.openclaw/workspace-[agent_type]/outputs/.status/[task_id].status`
- **agent_type**：research, analyst, creative, automation

## 重要提醒

⚠️ **必須寫入狀態文件！**

沒有狀態文件，主會話的 task_sync.py 無法：
- 更新 tasks.json 中的任務狀態
- 複製輸出文件到主工作區
- 觸發下游任務

確保每次完成任務後都創建狀態文件。

## 自動化

為了簡化狀態文件創建，你可以在 Python 中使用以下函數：

```python
import json
from pathlib import Path
from datetime import datetime, timezone

def write_status(task_id: str, status: str, output_path: str, agent_type: str, exit_code: int = 0):
    """
    Write status file

    Args:
        task_id: Task ID
        status: 'completed' or 'failed'
        output_path: Output file path
        agent_type: Agent type (research/analyst/creative/automation)
        exit_code: Exit code (0 for success)
    """
    workspace = Path.home() / f'.openclaw/workspace-{agent_type}'
    status_dir = workspace / 'outputs/.status'
    status_dir.mkdir(parents=True, exist_ok=True)

    status_file = status_dir / f"{task_id}.status"

    status_data = {
        "task_id": task_id,
        "status": status,
        "output_path": output_path,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "exit_code": exit_code,
        "agent_type": agent_type
    }

    status_file.write_text(json.dumps(status_data, indent=2))
    print(f"[Agent] Status file written: {status_file}")
```

使用示例：

```python
# 完成任務後
write_status(
    task_id="q010",
    status="completed",
    output_path="/Users/charlie/.openclaw/workspace-analyst/outputs/q010-result.md",
    agent_type="analyst",
    exit_code=0
)
```
