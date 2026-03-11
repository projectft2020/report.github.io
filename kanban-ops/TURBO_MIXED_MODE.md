# Turbo Mode 混合模式使用指南

## 概述

混合模式（Mixed Mode）是 Turbo Mode v4.0 的新功能，結合了手動控制和自動觸發，提供更靈活的自動化解決方案。

## 功能特點

### 三種模式

| 模式 | 說明 | 觸發方式 | 使用場景 |
|------|------|----------|----------|
| **manual** | 手動啟用/禁用 | `python3 turbo_mode.py enable`<br>`python3 turbo_mode.py disable` | 需要批量處理任務時 |
| **auto** | 自動觸發 | 根據 pending 任務數量自動切換 | 任務堆積時自動啟動 |
| **off** | 完全關閉 | 不執行任何檢查 | 平時或不需要自動化時 |

### 核心機制

#### 1. 定時檢查（Cron Job）
- **頻率**：每 15 分鐘
- **作用**：檢查待觸發任務
- **狀態**：默認禁用（需要手動啟用）

#### 2. 任務流程
```
Cron 每 15 分鐘
   ↓
turbo_mode.py mixed-check
   ↓
1. 檢查是否啟用
   ↓
2. 消費隊列 (consume_queue.py)
   ↓
3. 準備任務 (spawn_ready_tasks.py)
   ↓
4. 讀取 ready_to_spawn.jsonl
   ↓
5. 如有待觸發任務 → 主會話自動執行 sessions_spawn
```

#### 3. 自動觸發邏輯
```
pending 任務 ≥ 10
   ↓
檢查冷卻期（60 分鐘）
   ↓
如不在冷卻期 → 啟動混合模式
   ↓
執行任務
   ↓
pending 任務 ≤ 3 → 關閉混合模式
```

## 使用方法

### 手動模式（推薦開始使用）

#### 啟用手動混合模式
```bash
python3 ~/workspace/kanban-ops/turbo_mode.py enable
```

**輸出示例：**
```
🔓 啟用手動混合模式

============================================================
✅ 手動混合模式已啟用

配置：
   模式：manual (手動控制)
   間隔：15 分鐘
   並發：5

💡 說明：
   - Cron 每 15 分鐘會檢查待觸發任務
   - 如有待觸發任務，主會話會自動執行 sessions_spawn
   - 如需停止，請執行：python3 turbo_mode.py disable

============================================================
```

#### 禁用混合模式
```bash
python3 ~/workspace/kanban-ops/turbo_mode.py disable
```

### 自動模式

#### 啟用自動混合模式
```bash
python3 ~/workspace/kanban-ops/turbo_mode.py auto
```

**輸出示例：**
```
🤖 啟用自動混合模式

============================================================
✅ 自動混合模式已啟用

配置：
   模式：auto (自動觸發)
   觸發閾值：10 個 pending 任務
   冷卻時間：60 分鐘
   間隔：15 分鐘

💡 說明：
   - 當 pending 任務 ≥ 10 時自動啟動
   - 當 pending 任務 ≤ 3 時自動停止
   - 防止頻繁切換（冷卻 60 分鐘）

============================================================
```

### 檢查模式
```bash
python3 ~/workspace/kanban-ops/turbo_mode.py mixed-check
```

**輸出示例：**
```
🔄 混合模式檢查
============================================================
ℹ️  混合模式未啟用
```

或（如果啟用）：
```
🔄 混合模式檢查
============================================================

🔍 執行混合模式檢查...

1️⃣  消費任務隊列...
✅ 隊列消費完成

2️⃣  準備待觸發任務...
✅ 任務準備完成

3️⃣  找到 3 個待觸發任務
⚠️  請在主會話中執行 sessions_spawn
💡 或等待主會話自動觸發
```

## Cron Job 管理

### 啟用 Cron Job
使用 OpenClaw cron 工具啟用：

```python
from openclaw_tools import cron

# 更新 cron job，設置 enabled: true
cron({
    "action": "update",
    "jobId": "279daf2e-c242-4b24-9510-b2046928631a",
    "patch": {
        "enabled": true
    }
})
```

或通過主會話命令：
```
啟用 Turbo Mode Cron Job
```

### 禁用 Cron Job
```python
cron({
    "action": "update",
    "jobId": "279daf2e-c242-4b24-9510-b2046928631a",
    "patch": {
        "enabled": false
    }
})
```

### 查看所有 Cron Jobs
```python
cron({"action": "list"})
```

## 配置文件

### TURBO_TASKS.json
```json
{
  "turbo_config": {
    "mode": "mixed",
    "enabled": false,
    "mixed_mode": {
      "enabled": false,
      "auto_trigger": {
        "enabled": false,
        "min_pending": 10,
        "cooldown_minutes": 60
      },
      "schedule": {
        "enabled": false,
        "check_interval_minutes": 15
      },
      "limits": {
        "max_concurrent": 5,
        "max_tasks_per_check": 5,
        "timeout_minutes": 15
      }
    }
  }
}
```

### 配置參數說明

| 參數 | 類型 | 默認值 | 說明 |
|------|------|--------|------|
| `mode` | string | "mixed" | 模式類型 |
| `enabled` | boolean | false | 是否啟用混合模式 |
| `auto_trigger.enabled` | boolean | false | 是否啟用自動觸發 |
| `auto_trigger.min_pending` | integer | 10 | 觸發閾值 |
| `auto_trigger.cooldown_minutes` | integer | 60 | 冷卻時間（分鐘） |
| `schedule.enabled` | boolean | false | 是否啟用定時檢查 |
| `schedule.check_interval_minutes` | integer | 15 | 檢查間隔（分鐘） |
| `limits.max_concurrent` | integer | 5 | 最大並發數 |
| `limits.max_tasks_per_check` | integer | 5 | 每次檢查最大任務數 |
| `limits.timeout_minutes` | integer | 15 | 超時時間（分鐘） |

## 使用場景

### 場景 1：日常使用（手動模式）
```bash
# 1. 啟用手動模式
python3 turbo_mode.py enable

# 2. 啟用 Cron Job
（在主會話中執行）

# 3. 等待自動執行

# 4. 完成後禁用
python3 turbo_mode.py disable
```

### 場景 2：自動管理（自動模式）
```bash
# 1. 啟用自動模式
python3 turbo_mode.py auto

# 2. 啟用 Cron Job
（在主會話中執行）

# 3. 系統自動根據 pending 任務數量切換

# 4. 如需停止，禁用即可
python3 turbo_mode.py disable
```

### 場景 3：平時（關閉）
```bash
# 保持關閉狀態，不執行任何檢查
python3 turbo_mode.py disable
```

## Token 消耗優化

### 頻率對比

| 頻率 | 次/天 | Token 消耗（無任務） |
|------|-------|---------------------|
| 每 5 分鐘 | 288 | ~20k |
| 每 15 分鐘 | 96 | ~7k |
| 每 30 分鐘 | 48 | ~3k |

### 優化建議

1. **一般時期**：保持關閉或使用 15 分鐘頻率
2. **任務堆積時**：使用 15 分鐘頻率
3. **深度工作時**：暫時關閉，避免干擾

## 故障排查

### Cron Job 未執行
```bash
# 檢查 cron job 狀態
from openclaw_tools import cron
cron({"action": "list"})

# 檢查是否啟用
cron({"action": "list"}) → 查看 "enabled": true?
```

### 任務未觸發
```bash
# 手動執行檢查
python3 ~/workspace/kanban-ops/turbo_mode.py mixed-check

# 檢查隊列
ls ~/.openclaw/workspace/kanban-ops/task_queue/

# 檢查配置
cat ~/workspace/kanban-ops/TURBO_TASKS.json
```

### 冷卻期過長
```bash
# 刪除冷卻標記
rm ~/workspace/kanban-ops/turbo_cooldown.txt
```

## 與原版 Turbo Mode 的區別

| 特性 | 原版（睡眠模式） | 混合模式 |
|------|------------------|----------|
| 觸發方式 | 用戶「我睡了」 | Cron 定時檢查 |
| 模式 | 連續執行 6 小時 | 按需執行 |
| 控制方式 | 手動停止 | 手動/自動 |
| 適用場景 | 用戶睡覺時 | 任何時間 |

## 未來改進

- [ ] 添加 Web UI 控制面板
- [ ] 實現任務優先級智能調度
- [ ] 添加 Token 使用監控和預警
- [ ] 實現跨會話任務同步
- [ ] 添加日誌分析和可視化

## 版本歷史

### v4.0 (2026-02-20)
- ✅ 添加混合模式
- ✅ 支持手動/自動/關閉三種模式
- ✅ 實現 Cron Job 集成
- ✅ 添加冷卻機制
- ✅ 實現 pending 任務統計

## 反饋

如有問題或建議，請聯繫：
- Issue: 在 workspace 中提出
- Email: 通過 Telegram 消息
