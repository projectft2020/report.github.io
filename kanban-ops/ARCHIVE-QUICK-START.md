# Kanban 歸檔系統 - 快速開始

## 🚀 快速開始

### 1. 檢查當前狀態

```bash
cd ~/workspace/kanban-ops
python3 archive_tasks.py --stats
```

### 2. 執行歸檔

```bash
# 正常歸檔（當文件大小 > 200 KB 時）
python3 archive_tasks.py

# 試運行（不實際修改文件）
python3 archive_tasks.py --dry-run

# 強制歸檔（用於測試）
python3 archive_tasks.py --force
```

### 3. 自動歸檔（推薦）

```bash
# 手動執行啟動歸檔（模擬重開機）
bash ~/workspace/kanban-ops/archive_on_startup.sh

# 查看日誌
tail -20 ~/workspace/kanban-ops/archive_startup.log
```

---

## 📊 當前狀態

| 項目 | 數值 |
|------|------|
| 任務總數 | 79 個 |
| 檔案大小 | 77.15 KB |
| 歸檔狀態 | ✅ 正常（不需要歸檔）|

---

## 📖 詳細文檔

- **完整策略：** `ARCHIVE-STRATEGY.md`
- **腳本說明：** `archive_tasks.py --help`
- **集成指南：** `ARCHIVE-STRATEGY.md#-自動歸檔配置`

---

## 🔗 自動歸檔配置

### 推薦方案：啟動腳本

```bash
# 測試啟動腸本
bash ~/workspace/kanban-ops/archive_on_startup.sh

# 查看日誌
tail -20 ~/workspace/kanban-ops/archive_startup.log
```

**優勢：**
- ✅ 重開機時自動檢查並執行
- ✅ 只在文件過大時才歸檔
- ✅ 無需手動維護

### 可選方案：集成到 Heartbeat

已在 `HEARTBEAT.md` 中添加每日歸檔檢查。

---

## 📊 歸檔策略（高頻版本 v3.0）

```
今天 ← 2天 ← 7天 ← 14天
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 保留    快速歸檔    月度歸檔    壓縮歸檔
```

- **保留**：最近 2 天的已完成任務
- **快速歸檔**：2-7 天前（快速查詢）
- **月度歸檔**：7-14 天前（月度查詢）
- **壓縮歸檔**：14+ 天前（長期存檔）

---

## ⚠️ 重要提示

- ✅ **當前不需要歸檔**（77 KB < 200 KB 閾值）
- 📅 **建議每日檢查一次**
- 🔄 **重開機時自動檢查**（推薦）
- 📂 **歸檔文件位置：** `~/workspace-automation/kanban/archive/`

---

## 🔧 故障排除

### 歸檔腳本未執行

```bash
# 檢查腳本權限
ls -l ~/workspace/kanban-ops/archive_tasks.py

# 賦予執行權限
chmod +x ~/workspace/kanban-ops/archive_tasks.py
```

### 啟動腳本未執行

```bash
# 手動測試
bash ~/workspace/kanban-ops/archive_on_startup.sh

# 查看日誌
cat ~/workspace/kanban-ops/archive_startup.log
```

### 歸檔文件未創建

```bash
# 檢查歸檔目錄
ls -l ~/workspace-automation/kanban/archive/

# 檢查磁盤空間
df -h
```

---

**創建時間：** 2026-02-20
**更新時間：** 2026-02-20（v3.0 - 高頻版本）
**狀態：** ✅ 就緒
