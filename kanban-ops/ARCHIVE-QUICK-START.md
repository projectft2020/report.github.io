# Kanban 歸檔系統 - 快速開始

## 🚀 快速開始

### 1. 檢查當前狀態

```bash
cd ~/workspace/kanban-ops
python3 archive_tasks.py --stats
```

### 2. 執行歸檔

```bash
# 正常歸檔（當文件大小 > 500 KB 時）
python3 archive_tasks.py

# 試運行（不實際修改文件）
python3 archive_tasks.py --dry-run

# 強制歸檔（用於測試）
python3 archive_tasks.py --force
```

---

## 📊 當前狀態

| 項目 | 數值 |
|------|------|
| 任務總數 | 79 個 |
| 檔案大小 | 77.10 KB |
| 歸檔狀態 | ✅ 正常（不需要歸檔）|

---

## 📖 詳細文檔

- **完整策略：** `ARCHIVE-STRATEGY.md`
- **腳本說明：** `archive_tasks.py --help`
- **集成指南：** `ARCHIVE-STRATEGY.md#-集成建議`

---

## 🔗 集成選項

### 選項 1：Cron（每月 1 日）

```bash
0 0 1 * * python3 ~/workspace/kanban-ops/archive_tasks.py >> ~/workspace/kanban-ops/archive.log 2>&1
```

### 選項 2：Heartbeat（每月第一個週日）

已自動集成到 `~/workspace/HEARTBEAT.md`

### 選項 3：事件驅動（文件大小 > 500 KB）

已添加到 `monitor_and_refill.py`（需要手動整合）

---

## ⚠️ 重要提示

- ✅ **當前不需要歸檔**（77 KB < 500 KB 閾值）
- 📅 **建議每月檢查一次**
- 📂 **歸檔文件位置：** `~/workspace-automation/kanban/archive/`

---

**創建時間：** 2026-02-20
**狀態：** ✅ 就緒
