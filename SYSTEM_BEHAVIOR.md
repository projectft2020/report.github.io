# 系統行為文檔

**文檔版本**: v1.0
**創建時間**: 2026-03-06 01:20
**目的**: 文檔化當前系統行為，為升級到 OpenClaw 2026.3.3 做準備

---

## 概述

本文檔記錄了當前系統的關鍵行為、錯誤處理模式、以及升級準備事項。

---

## 1. 系統架構

### 1.1 核心組件

| 組件 | 路徑 | 功能 | 依賴 |
|------|------|------|------|
| 自動任務啟動器 | `kanban-ops/auto_spawn_heartbeat.py` | 心跳時自動啟動 pending 任務 | backpressure.py |
| 背壓機制 | `kanban-ops/backpressure.py` | 動態調整啟動頻率和並發上限 | tasks.json |
| 錯誤恢復 | `kanban-ops/error_recovery.py` | 檢測和恢復失敗任務 | tasks.json, .status files |
| 任務同步 | `kanban-ops/task_sync.py` | 同步子代理狀態到 tasks.json | .status files |
| 狀態回滾 | `kanban-ops/task_state_rollback.py` | 回滾卡住的 spawning 任務 | tasks.json, subagents |
| 任務清理 | `kanban-ops/task_cleanup.py` | 清理失敗任務 | tasks.json |
| 監控和補充 | `kanban-ops/monitor_and_refill.py` | 監控任務並觸發 Scout | tasks.json, Scout |

### 1.2 數據流

```
心跳
  ↓
auto_spawn_heartbeat.py
  ├→ 檢查背壓 → backpressure.py
  ├→ 檢查錯誤恢復 → error_recovery.py
  ├→ 生成啟動命令 → spawn_commands.jsonl
  ↓
執行 sessions_spawn
  ↓
子代理執行任務
  ↓
創建 .status 文件 + 輸出文件
  ↓
task_sync.py 同步狀態
  ↓
更新 tasks.json
  ↓
下一次心跳
```

---

## 2. 當前錯誤處理模式

### 2.1 調查結果

#### 2.1.1 高級錯誤處理模式（已實現）

以下腳本已經使用了現代的錯誤處理模式：

**✅ error_recovery.py**:
- 使用 `logging` 模塊（標準化日誌）
- 使用 `dataclass` 定義結構化數據
- 使用 `Enum` 定義錯誤類型
- 完整的統計和報告機制
- 指數退避重試邏輯

```python
# 示例：錯誤記錄結構
@dataclass
class ErrorRecord:
    task_id: str
    error_type: str  # 使用 ErrorType enum
    error_message: str
    timestamp: str
    retry_count: int = 0
    max_retries: int = 3
    backoff_seconds: int = 0
    recovered: bool = False

# 示例：日誌配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(ERROR_LOG, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
```

**✅ backpressure.py**:
- 使用 `logging` 模塊
- 使用 `dataclass` 定義結構化數據
- 完整的統計和歷史記錄
- 健康度計算和動態調整

```python
# 示例：背壓統計
@dataclass
class BackpressureStats:
    max_concurrent: int = 3
    current_concurrent: int = 0
    stuck_count: int = 0
    health: float = 1.0  # 0.0-1.0
    spawn_interval: int = 65  # 秒
    reduced_concurrent: bool = False
    last_adjusted: str = ""
    adjustment_count: int = 0
    health_history: list = None
```

#### 2.1.2 中級錯誤處理模式（已實現）

以下腳本使用了標準的錯誤處理模式：

**✅ task_sync.py**:
- 使用 `logging` 模塊
- 使用 `try-except` 包裹關鍵操作
- 使用類型提示（typing）
- 完整的錯誤處理

```python
def update_task_status(task_id: str, status: str, completed_at: Optional[str] = None) -> bool:
    try:
        tasks = load_tasks()
        for i, task in enumerate(tasks):
            if task['id'] == task_id:
                tasks[i]['status'] = status
                if completed_at:
                    tasks[i]['completed_at'] = completed_at
        save_tasks(tasks)
        return True
    except Exception as e:
        logger.error(f"更新任務狀態失敗: {e}")
        return False
```

**✅ auto_spawn_heartbeat.py**:
- 使用簡單的 `log()` 函數（非標準 logging）
- 使用 `try-except` 包裹 I/O 操作
- 基本的錯誤處理

```python
def load_tasks():
    try:
        with open(TASKS_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        log("ERROR", f"載入 tasks.json 失敗：{e}")
        return []
```

#### 2.1.3 基礎錯誤處理模式（已實現）

以下腳本使用了基礎的錯誤處理模式：

**✅ task_state_rollback.py**:
- 使用簡單的 `log()` 函數
- 使用 `try-except` 包裹 I/O 操作
- 基本的錯誤處理

```python
def log(level, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    icons = {"INFO": "[INFO]", "SUCCESS": "[OK]", "WARNING": "[WARN]", "ERROR": "[ERR]"}
    icon = icons.get(level, "[LOG]")
    print(f"{icon} [{timestamp}] {message}", flush=True)
```

### 2.2 推薦改進（Phase 2 可選）

#### 2.2.1 標準化日誌（優先級：低）

**當前問題**:
- 部分腳本使用自定義 `log()` 函數
- 部分腳本使用標準 `logging` 模塊
- 日誌格式不統一

**改進方案**:
```python
# 創建共享的日誌配置模塊
# kanban-ops/logging_config.py

import logging
from pathlib import Path

def get_logger(name: str, log_file: Path) -> logging.Logger:
    """
    獲取標準化的 logger

    Args:
        name: logger 名稱
        log_file: 日誌文件路徑

    Returns:
        配置好的 logger 實例
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # 避免重複添加 handler
    if not logger.handlers:
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # 文件 handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # 控制台 handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
```

**使用示例**:
```python
from kanban-ops.logging_config import get_logger
from pathlib import Path

logger = get_logger(__name__, Path("kanban-ops/myscript.log"))
logger.info("這是一條日誌")
logger.error("這是一條錯誤")
```

**優先級評估**: 🟢 低
- 當前錯誤處理已經足夠穩定
- 統一日誌格式可以提高可維護性
- 不是升級的阻塞點

#### 2.2.2 增強錯誤上下文（優先級：低）

**改進方案**:
```python
# 使用 traceback 記錄完整堆疊
import traceback

try:
    # 操作
    pass
except Exception as e:
    logger.error(f"操作失敗: {e}\n{traceback.format_exc()}")
```

**優先級評估**: 🟢 低
- 大部分錯誤已經有適當的上下文
- 可以在調試時添加

---

## 3. 關鍵系統行為

### 3.1 心跳自動化系統

#### 3.1.1 啟動流程

```
1. 心跳觸發（約 30 分鐘間隔）
   ↓
2. 執行 auto_spawn_heartbeat.py
   ├→ 檢查背壓狀態
   ├→ 檢查並發限制
   ├→ 生成啟動命令
   ↓
3. 讀取 spawn_commands.jsonl
   ↓
4. 按 65-300 秒間隔執行 sessions_spawn
   ↓
5. 任務在後台執行
```

#### 3.1.2 背壓機制

| 健康度 | 啟動頻率 | 並發上限 | 觸發條件 |
|--------|----------|----------|----------|
| ≥ 0.8 | 65 秒 | 3 | 卡住任務 ≤ 1 |
| 0.5 - 0.8 | 120 秒 | 3 | 卡住任務 2-3 |
| < 0.5 | 300 秒 | 2 | 卡住任務 ≥ 4 |

**健康度計算**:
```python
health = 1 - (stuck_count / max_concurrent)
```

#### 3.1.3 並發限制

- 默認並發上限：3 個
- 最多同時運行：3 個子代理
- 啟動間隔：65-300 秒（動態調整）

### 3.2 任務狀態管理

#### 3.2.1 任務狀態

| 狀態 | 說明 | 持續時間 |
|------|------|----------|
| pending | 待處理，等待依賴完成 | 不定 |
| spawning | 正在啟動和執行 | 30-45 分鐘（超時保護） |
| in_progress | 正在執行 | 不定 |
| completed | 已完成 | 永久 |
| failed | 失敗（可恢復） | 不定 |

#### 3.2.2 狀態轉換

```
pending → spawning → in_progress → completed
   ↓           ↓
   ↓       （超時 45 分鐘）
   ↓           ↓
   ↓→ pending (回滾)
```

#### 3.2.3 超時機制

**Spawning 超時**:
- 疑似卡住：30 分鐘（發出警報）
- 自動回滾：45 分鐘（回滾為 pending）

**任務超時**:
- 任務執行超過 24 小時 → 標記為 failed

### 3.3 錯誤恢復機制

#### 3.3.1 錯誤類型

| 錯誤類型 | 檢測方法 | 恢復策略 |
|----------|----------|----------|
| rate_limit | 檢測 "rate limit" 錯誤消息 | 指數退避重試 |
| timeout | 檢測超時錯誤 | 標記為 pending，延後重試 |
| network | 檢測網絡錯誤 | 指數退避重試 |
| parsing | 檢測解析錯誤 | 記錄錯誤，手動處理 |
| unknown | 未知錯誤 | 記錄錯誤，手動處理 |

#### 3.3.2 指數退避

```python
# 退避時間計算
backoff = min(2 ** retry_count, 3600)  # 最多 1 小時

# 示例：
# 重試 1: 2^1 = 2 秒
# 重試 2: 2^2 = 4 秒
# 重試 3: 2^3 = 8 秒
# ...
# 重試 10: 2^10 = 1024 秒 ≈ 17 分鐘
# 重試 11: 3600 秒 = 1 小時
```

#### 3.3.3 最多重試次數

- 默認：3 次
- 超過次數：標記為 failed

### 3.4 任務依賴管理

#### 3.4.1 依賴檢查

```python
def check_dependencies(task, tasks):
    deps = task.get('dependencies', [])
    for dep_id in deps:
        dep_task = next((t for t in tasks if t['id'] == dep_id), None)
        if dep_task and dep_task['status'] != 'completed':
            return False
    return True
```

#### 3.4.2 啟動順序

```
1. 按優先級排序：high > medium > low
2. 同優先級按創建時間排序
3. 只啟動依賴已完成的任務
```

---

## 4. 配置文件

### 4.1 HEARTBEAT.md

**用途**: 定義心跳時執行的任務

**核心任務**:
1. auto_spawn_heartbeat.py - 自動任務啟動
2. task_state_rollback.py - 狀態回滾
3. error_recovery.py - 錯誤恢復
4. task_cleanup.py - 任務清理
5. task_sync.py - 任務同步
6. monitor_and_refill.py - 監控和補充

**頻率**: 每 30 分鐘（心跳觸發）

### 4.2 tasks.json

**用途**: 存儲所有任務狀態

**關鍵字段**:
```json
{
  "id": "task-id",
  "title": "任務標題",
  "status": "pending|spawning|in_progress|completed|failed",
  "priority": "high|medium|low",
  "created_at": "2026-03-06T01:00:00Z",
  "completed_at": "2026-03-06T02:00:00Z",
  "dependencies": ["task-id-1", "task-id-2"],
  "metadata": {
    "model": "zai/glm-4.5"
  }
}
```

### 4.3 spawn_commands.jsonl

**用途**: 存儲待執行的啟動命令

**格式**:
```json
{
  "task": "TASK: ...",
  "agentId": "research",
  "label": "task-id",
  "model": "zai/glm-4.5"
}
```

**清理規則**:
- 每次心跳讀取後清空
- 避免重複執行

---

## 5. 關鍵監控指標

### 5.1 系統健康度

```python
health = 1 - (stuck_count / max_concurrent)
```

**目標**: ≥ 0.8
**警報**: < 0.5

### 5.2 任務統計

| 指標 | 目標 | 警報 |
|------|------|------|
| pending 任務 | 10-20 | < 5 或 > 50 |
| spawning 任務 | 0-2 | > 5 |
| in_progress 任務 | 0-3 | > 5 |
| failed 任務 | < 20 | > 50 |

### 5.3 錯誤統計

| 指標 | 目標 | 警報 |
|------|------|------|
| rate limit 錯誤 | < 15% | > 30% |
| 錯誤恢復率 | > 80% | < 50% |

---

## 6. 升級準備事項

### 6.1 Breaking Checks 應對

#### 6.1.1 Heartbeat DM 遞送策略變更

**影響**: 🟡 中等

**應對措施**:
1. 確認心跳運作頻道（webchat）
2. 準備配置模板（`config-template-v2026.3.3.json`）
3. 測試驗證（Phase 3）

**配置**:
```json
{
  "agents": {
    "defaults": {
      "heartbeat": {
        "directPolicy": "block"
      }
    }
  }
}
```

#### 6.1.2 其他 Breaking Checks

| Breaking Change | 影響 | 應對措施 |
|----------------|------|----------|
| Node exec 載荷 | 🟢 無 | 無需操作 |
| Node system.run 路徑 | 🟢 低 | 檢查簡寫命令（已完成 ✅） |
| ACP 路由默認 | 🟢 無 | 無需操作 |
| Docker 網絡 | 🟢 無 | 無需操作 |
| tools.profile 默認 | 🟢 無 | 無需操作 |
| Plugin SDK API | 🟢 無 | 無需操作 |
| Zalo 插件 | 🟢 無 | 無需操作 |

### 6.2 配置準備

**已準備**:
- ✅ `config-template-v2026.3.3.json`

**配置內容**:
```json
{
  "agents": {
    "defaults": {
      "heartbeat": {
        "directPolicy": "block"
      },
      "sandbox": {
        "docker": {
          "dangerouslyAllowContainerNamespaceJoin": false
        }
      }
    }
  },
  "acp": {
    "dispatch": {
      "enabled": false
    }
  }
}
```

### 6.3 驗證腳本準備

**已準備**:
- ✅ `verify-upgrade.sh`

**測試結果**:
- 總測試數: 17
- 通過: 15
- 失敗: 0
- 跳過: 2

---

## 7. 建議和下一步

### 7.1 Phase 2 改進建議

#### 優先級：低（可選）

1. **標準化日誌**
   - 創建共享的日誌配置模塊
   - 統一日誌格式
   - 改進可維護性

2. **增強錯誤上下文**
   - 使用 traceback 記錄完整堆疊
   - 改進調試效率

#### 說明

這些改進是**可選的**，因為：
- 當前錯誤處理已經足夠穩定
- 系統運作良好，無關鍵問題
- 升級的主要風險已經識別和應對

如果時間允許，可以在升級後逐步實施這些改進。

### 7.2 Phase 3 準備

**測試環境準備**:
1. 創建測試分支
2. 準備備份
3. 準備回滾計劃

**驗證清單**:
1. 心跳自動化系統正常
2. 子代理通信正常
3. 背壓機制正常
4. 任務同步正常
5. 錯誤恢復正常
6. 狀態回滾正常

---

## 8. 總結

### 8.1 當前系統狀態

- ✅ 系統運作穩定
- ✅ 錯誤處理完善
- ✅ 背壓機制有效
- ✅ 自動化程度高

### 8.2 升級準備完成度

| 項目 | 狀態 | 完成度 |
|------|------|--------|
| 系統盤點 | ✅ | 100% |
| Breaking Checks 評估 | ✅ | 100% |
| 配置模板準備 | ✅ | 100% |
| 驗證腳本準備 | ✅ | 100% |
| 系統行為文檔化 | ✅ | 100% |
| 錯誤處理模式採用 | ✅ | 95% |
| 標準化日誌（可選） | ⏸️ | 0% |

### 8.3 升級風險評估

**總體風險**: 🟡 中等偏低

**高風險 Breaking Changes**: 0 個
**中等風險 Breaking Changes**: 1 個（Heartbeat DM 遞送）
**低風險 Breaking Changes**: 1 個（Node system.run 路徑）
**無影響 Breaking Changes**: 6 個

### 8.4 建議

1. ✅ **推薦升級**: 風險可控，Breaking Changes 影響有限
2. 🛡️ **必須準備**: 備份 + 測試環境驗證
3. ⏰ **建議時間**: 3-4 週後（完成 Phase 2 和 Phase 3）
4. 🎯 **目標**: 確保關鍵功能正常，無中斷風險

---

**文檔版本**: v1.0
**最後更新**: 2026-03-06 01:20
**負責人**: Charlie (Orchestrator)
**審核者**: David
