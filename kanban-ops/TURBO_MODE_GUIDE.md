# 加速模式 (Turbo Mode) 使用指南

**創建日期：** 2026-02-20
**版本：** v1.0
**目的：** 在用戶睡覺時自動執行大量深度工作

---

## 🚀 快速開始

### 啟動加速模式

**方式 1：用戶觸發（推薦）**

發送訊息：`我睡了`

我會自動：
1. 啟動加速模式
2. 執行預設任務列表
3. 6 小時後自動停止（或你發送「我醒了」）

**方式 2：手動啟動**

```bash
bash ~/workspace/kanban-ops/turbo_start.sh
```

**方式 3：直接調用腳本**

```bash
python3 ~/workspace/kanban-ops/turbo_mode.py start
```

### 停止加速模式

**方式 1：用戶觸發（推薦）**

發送訊息：`我醒了`

**方式 2：手動停止**

```bash
bash ~/workspace/kanban-ops/turbo_stop.sh
```

**方式 3：直接調用腳本**

```bash
python3 ~/workspace/kanban-ops/turbo_mode.py stop
```

### 查看狀態

```bash
python3 ~/workspace/kanban-ops/turbo_mode.py status
```

---

## 📊 執行階段

加速模式分 4 個階段執行，總時長約 6 小時：

### 階段 1：快速清理（0-30 分鐘）

- 📂 歸檔檢查
- 🔄 過期任務恢復
- 📝 Git 提交檢查

### 階段 2：並行研究（0-2 小時）

- 🚀 觸發最高優先級 Kanban 任務（3 個並行）
- 🔍 Scout 深度掃描（可選）

### 階段 3：深度工作（2-4 小時）

- 📚 知識庫整理
- ⚡ 代碼優化
- 📝 文檔更新

### 階段 4：系統優化（4-6 小時）

- 📊 性能分析
- 🧹 日誌清理
- 💾 數據備份（可選）

---

## ⚙️ 配置

### 任務列表配置

文件：`~/workspace/kanban-ops/TURBO_TASKS.json`

```json
{
  "version": "1.0",
  "turbo_config": {
    "duration_hours": 6,
    "max_concurrent_tasks": 3,
    "stagger_seconds": 30
  },
  "phases": [...]
}
```

### 調整配置

#### 修改運行時長

將 `"duration_hours"` 改為你想要的時長（例如 8 小時）

#### 修改並發任務數

將 `"max_concurrent_tasks"` 改為你想要的並行數量

#### 啟用/禁用任務

在 `phases` 中找到對應任務，修改 `"enabled"` 字段：

```json
{
  "id": "scout_deep_scan",
  "enabled": false  // 改為 true 啟用
}
```

---

## 📋 任務類型

| 任務類型 | 描述 | 依賴 |
|---------|------|------|
| `archive_check` | 檢查並執行歸檔 | archive_tasks.py |
| `stale_recovery` | 恢復過期任務 | check-work-tasks.sh |
| `git_commit` | Git 提交檢查 | git |
| `spawn_kanban_tasks` | 觸發 Kanban 任務 | sessions_spawn |
| `scout_scan` | Scout 掃描 | scout_agent.py |
| `organize_knowledge` | 知識庫整理 | 記憶系統 |
| `optimize_code` | 代碼優化 | 腳本分析 |
| `update_docs` | 文檔更新 | 文檔系統 |
| `cleanup_logs` | 日誌清理 | 文件系統 |
| `backup_data` | 數據備份 | 備份工具 |

---

## 🔧 高級功能

### 恢復未完成的階段

```bash
python3 ~/workspace/kanban-ops/turbo_mode.py resume
```

注意：此功能尚未完全實現。

### 查看執行日誌

```bash
cat ~/workspace/kanban-ops/TURBO_LOG.md
```

### 查看詳細狀態

```bash
cat ~/workspace/kanban-ops/TURBO_STATUS.json
```

---

## 📊 狀態文件

### TURBO_STATUS.json

記錄當前加速模式的執行狀態：

```json
{
  "enabled": false,
  "start_time": null,
  "current_phase": null,
  "completed_phases": [],
  "tasks_completed": 0,
  "total_tasks": 0,
  "last_activity": null
}
```

### TURBO_LOG.md

記錄所有加速模式的執行歷史。

---

## ⚠️ 注意事項

### 權限控制

- ✅ 只執行預設的安全任務
- ✅ 不會修改系統配置
- ✅ 不會刪除重要文件
- ⚠️ Scout 掃描默認禁用（需要手動啟用）

### 緊急停止

隨時可以通過以下方式停止：
- 發送訊息「我醒了」
- 執行 `turbo_stop.sh`
- Ctrl + C（手動運行時）

### 資源監控

加速模式會監控：
- API 使用量
- 磁盤空間
- 任務執行時間

---

## 🎯 使用場景

### 場景 1：日常加速

每天晚上睡覺前發送「我睡了」：
- 自動執行日常維護
- 觸發待辦研究任務
- 整理知識庫

### 場景 2：周末加速

周末外出時發送「我睡了」：
- 執行完整 6 小時加速
- 深度掃描和優化
- 大規模研究任務

### 場景 3：專案衝刺

專案截止前：
- 設置更長運行時長（8-10 小時）
- 啟用所有任務
- 並行執行多個任務

---

## 🔍 故障排除

### 加速模式無法啟動

```bash
# 檢查配置文件
cat ~/workspace/kanban-ops/TURBO_TASKS.json

# 檢查腳本權限
ls -l ~/workspace/kanban-ops/turbo_mode.py

# 查看日誌
cat ~/workspace/kanban-ops/TURBO_LOG.md
```

### 任務執行失敗

```bash
# 查看詳細日誌
tail -100 ~/workspace/kanban-ops/TURBO_LOG.md

# 檢查依賴
which python3
which git
```

### 加速模式無法停止

```bash
# 手動停止
python3 ~/workspace/kanban-ops/turbo_mode.py stop

# 刪除狀態文件（緊急情況）
rm ~/workspace/kanban-ops/TURBO_STATUS.json
```

---

## 📚 相關文檔

- **歸檔系統：** `ARCHIVE-STRATEGY.md`
- **Kanban 運作：** `KANBAN.md`
- **Scout Agent：** `~/workspace-scout/IDENTITY.md`

---

## 🔄 更新日誌

### v1.0 (2026-02-20)

- ✅ 初始版本
- ✅ 4 階段執行流程
- ✅ 狀態管理和日誌記錄
- ✅ 用戶觸發支持
- ✅ 配置化任務列表

---

**文檔創建時間：** 2026-02-20
**版本：** v1.0
**狀態：** ✅ 就緒
