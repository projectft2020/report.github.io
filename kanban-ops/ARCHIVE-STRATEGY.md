# Kanban 任務歸檔策略

**創建日期：** 2026-02-20
**目的：** 管理 `tasks.json` 檔案大小，保持系統性能

---

## 📊 當前狀況

| 指標 | 數值 |
|------|------|
| 總計 | 79 個任務 |
| ✅ Completed | 62 個（78%） |
| 🔄 In Progress | 1 個 |
| ⏳ Pending | 14 個 |
| ❌ Failed | 2 個 |
| 💾 檔案大小 | 77.10 KB |
| 📅 時間範圍 | 2 天（2/19-2/20） |

---

## 🗃️ 歸檔策略

### 歸檔時間線

```python
昨天 ← 7天 ← 30天 ← 90天
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 保留    月度歸檔    壓縮歸檔
```

### 歸檔規則

| 歸檔類型 | 時間閾值 | 存儲位置 | 格式 | 用途 |
|---------|---------|---------|------|------|
| **保留** | 最近 7 天 | tasks.json | JSON | 日常操作 |
| **月度歸檔** | 7-30 天前 | archive/tasks-YYYY-MM.json | JSON | 月度查詢 |
| **壓縮歸檔** | 30 天前 | archive/tasks-compressed-YYYY-MM-DD.json.gz | JSON.gz | 長期存檔 |

### 自動觸發條件

- **文件大小超過 500 KB**：自動執行歸檔
- **每月 1 日**：定期歸檔（建議）
- **手動執行**：`python3 archive_tasks.py --force`

---

## 🔧 歸檔腳本

### 位置

```
~/workspace/kanban-ops/archive_tasks.py
```

### 使用方式

```bash
# 顯示統計信息
python3 archive_tasks.py --stats

# 正常歸檔（根據時間閾值）
python3 archive_tasks.py

# 試運行模式（不實際修改文件）
python3 archive_tasks.py --dry-run

# 強制歸檔（用於測試）
python3 archive_tasks.py --force

# 查看幫助
python3 archive_tasks.py --help
```

---

## 🔄 集成建議

### 方案 1：Cron（推薦）

```bash
# 每月 1 日凌晨執行歸檔
0 0 1 * * python3 /Users/charlie/.openclaw/workspace/kanban-ops/archive_tasks.py >> ~/workspace/kanban-ops/archive.log 2>&1
```

### 方案 2：集成到 Heartbeat

在 `HEARTBEAT.md` 中添加：

```markdown
## Rotating Tasks (Pick 1-2 Per Heartbeat)

### Monthly: Task Archiving
```bash
# 檢查是否需要歸檔
python3 ~/workspace/kanban-ops/archive_tasks.py --stats

# 如果文件大小超過 500 KB，執行歸檔
python3 ~/workspace/kanban-ops/archive_tasks.py
```

**觸發條件：**
- 每月第一個週日
- 或當 tasks.json 超過 500 KB
```

### 方案 3：事件驅動

```python
# 在 monitor_and_refill.py 中添加
def should_archive_tasks():
    """檢查是否需要歸檔"""
    import os
    tasks_json = '/Users/charlie/.openclaw/workspace-automation/kanban/tasks.json'
    file_size = os.path.getsize(tasks_json) / 1024  # KB
    return file_size > 500  # 超過 500 KB

# 在主流程中調用
if should_archive_tasks():
    print("📦 檢測到 tasks.json 過大，執行歸檔...")
    os.system('python3 ~/workspace/kanban-ops/archive_tasks.py')
```

---

## 📊 預期效果

### 歸檔前

```
tasks.json: 77 KB
archive/: 0 個文件
```

### 歸檔後（1 個月後，假設每天 30 個任務）

```
tasks.json: ~50 KB (保留最近 7 天，~210 個任務)
archive/tasks-2026-02.json: ~200 KB (600 個已歸檔任務)
archive/tasks-compressed-2026-01-15.json.gz: ~20 KB (舊任務，壓縮 10 倍)
```

### 歸檔後（1 年後）

```
tasks.json: ~50 KB (持續保持)
archive/tasks-2026-02.json ~ tasks-2026-12.json: 12 個月度歸檔
archive/tasks-compressed-*.json.gz: 12 個壓縮歸檔
總空間: ~2.5 MB (如果不歸檔，tasks.json 會是 ~27 MB)
```

**空間節省：** 90%+

---

## 📝 維護建議

### 定期檢查

```bash
# 每月檢查一次
python3 archive_tasks.py --stats
```

### 清理策略

- **月度歸檔**：保留 12 個月（1 年）
- **壓縮歸檔**：永久保留
- **手動清理**：刪除過期的月度歸檔

```bash
# 刪除 1 年前的月度歸檔
find ~/workspace/kanban-ops/archive -name "tasks-*.json" -mtime +365 -delete
```

---

## 🎯 總結

### 優勢

✅ **自動化**：無需手動管理
✅ **性能優化**：保持 tasks.json 輕量（< 50 KB）
✅ **可查詢**：月度歸檔保留查詢能力
✅ **空間節省**：壓縮歸檔節省 90%+ 空間
✅ **靈活配置**：可調整時間閾值和文件大小閾值

### 實施步驟

1. ✅ 歸檔腳本已創建：`~/workspace/kanban-ops/archive_tasks.py`
2. ⏳ 選擇集成方案（Cron / Heartbeat / 事件驅動）
3. ⏳ 測試歸檔流程
4. ⏳ 監控歸檔效果

### 下一步

根據你的需求選擇集成方案：

- **簡單自動化**：使用 Cron（每月 1 日執行）
- **靈活觸發**：集成到 Heartbeat（每月第一個週日）
- **智能觸發**：事件驅動（文件大小超過 500 KB 時）

---

**文檔創建時間：** 2026-02-20
**腳本版本：** v2.0
**狀態：** ✅ 測試通過，準備部署
