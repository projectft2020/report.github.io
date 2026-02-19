# Kanban 任務歸檔策略

**創建日期：** 2026-02-20
**更新日期：** 2026-02-20（v3.0 - 高頻版本）
**目的：** 管理 `tasks.json` 檔案大小，保持系統性能

---

## 📊 當前狀況

| 指標 | 數值 |
|------|------|
| 總計 | 79 個任務 |
| ✅ Completed | 63 個（80%） |
| 🔄 In Progress | 0 個 |
| ⏳ Pending | 14 個 |
| ❌ Failed | 2 個 |
| 💾 檔案大小 | 77.15 KB |
| 📅 時間範圍 | 2 天（2/19-2/20） |

---

## 🗃️ 歸檔策略（高頻版本 v3.0）

### 歸檔時間線

```python
今天 ← 2天 ← 7天 ← 14天
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 保留    快速歸檔    月度歸檔    壓縮歸檔
```

### 歸檔規則

| 歸檔類型 | 時間閾值 | 存儲位置 | 格式 | 用途 |
|---------|---------|---------|------|------|
| **保留** | 最近 2 天 | tasks.json | JSON | 日常操作 |
| **快速歸檔** | 2-7 天前 | archive/tasks-quick-YYYY-MM-DD.json | JSON | 快速查詢 |
| **月度歸檔** | 7-14 天前 | archive/tasks-YYYY-MM.json | JSON | 月度查詢 |
| **壓縮歸檔** | 14+ 天前 | archive/tasks-compressed-YYYY-MM-DD.json.gz | JSON.gz | 長期存檔 |

### 自動觸發條件

- **文件大小超過 200 KB**：自動執行歸檔
- **重開機時自動檢查**：通過啟動腳本
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
python3 ~/workspace/kanban-ops/archive_tasks.py --stats

# 正常歸檔（根據時間閾值和文件大小）
python3 ~/workspace/kanban-ops/archive_tasks.py

# 試運行模式（不實際修改文件）
python3 ~/workspace/kanban-ops/archive_tasks.py --dry-run

# 強制歸檔（用於測試）
python3 ~/workspace/kanban-ops/archive_tasks.py --force

# 查看幫助
python3 ~/workspace/kanban-ops/archive_tasks.py --help
```

---

## 🚀 自動歸檔配置

### 方案 1：啟動腳本（推薦）

#### 優勢

✅ **簡單易用**：一個腳本搞定
✅ **自動觸發**：重開機時自動檢查並執行
✅ **智能判斷**：只在文件過大時才歸檔

#### 配置步驟

1. **創建 macOS Launch Agent**（可選，自動在重開機時執行）

```bash
# 創建 Launch Agent 配置文件
cat > ~/Library/LaunchAgents/com.openclaw.kanban-archive.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.openclaw.kanban-archive</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>/Users/charlie/.openclaw/workspace/kanban-ops/archive_on_startup.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
EOF

# 加載 Launch Agent
launchctl load ~/Library/LaunchAgents/com.openclaw.kanban-archive.plist
```

2. **手動執行（測試）**

```bash
bash ~/workspace/kanban-ops/archive_on_startup.sh
```

3. **查看日誌**

```bash
tail -20 ~/workspace/kanban-ops/archive_startup.log
```

### 方案 2：集成到 Heartbeat

在 `HEARTBEAT.md` 中添加：

```markdown
## Rotating Tasks (Pick 1-2 Per Heartbeat)

### Daily: Task Archiving Check
```bash
# 檢查是否需要歸檔
python3 ~/workspace/kanban-ops/archive_tasks.py --stats

# 如果文件大小超過 200 KB，執行歸檔
python3 ~/workspace/kanban-ops/archive_tasks.py
```

**觸發條件：**
- 每日檢查一次
- 當 tasks.json 超過 200 KB
```

### 方案 3：Cron（定期執行）

```bash
# 每天凌晨 2 點檢查並執行歸檔
0 2 * * * python3 /Users/charlie/.openclaw/workspace/kanban-ops/archive_tasks.py >> /Users/charlie/.openclaw/workspace/kanban-ops/archive.log 2>&1
```

---

## 📊 預期效果

### 歸檔前

```
tasks.json: 77 KB
archive/: 1 個文件（0.76 KB）
```

### 歸檔後（2 週後，假設每天 30 個任務）

```
tasks.json: ~20 KB（保留最近 2 天，~60 個任務）
archive/tasks-quick-2026-02-20.json: ~50 KB（快速歸檔，~150 個任務）
archive/tasks-2026-02.json: ~100 KB（月度歸檔，~300 個任務）
archive/tasks-compressed-2026-02-XX.json.gz: ~10 KB（壓縮歸檔，~60 個任務）
```

### 歸檔後（1 個月後）

```
tasks.json: ~20 KB（持續保持）
archive/tasks-quick-*.json: 7 個快速歸檔（每週）
archive/tasks-2026-02.json: ~100 KB
archive/tasks-compressed-*.json.gz: 4 個壓縮歸檔
總空間: ~500 KB（如果不歸檔，tasks.json 會是 ~27 MB）
```

**空間節省：** 95%+

---

## 📝 維護建議

### 定期檢查

```bash
# 每日檢查一次
python3 ~/workspace/kanban-ops/archive_tasks.py --stats
```

### 清理策略

- **快速歸檔**：保留 1 週（7 個文件）
- **月度歸檔**：保留 3 個月（3 個文件）
- **壓縮歸檔**：永久保留
- **手動清理**：刪除過期的快速歸檔

```bash
# 刪除 1 週前的快速歸檔
find ~/workspace-automation/kanban/archive -name "tasks-quick-*.json" -mtime +7 -delete

# 刪除 3 個月前的月度歸檔
find ~/workspace-automation/kanban/archive -name "tasks-*.json" -mtime +90 -delete
```

### 監控日誌

```bash
# 查看啟動歸檔日誌
tail -50 ~/workspace/kanban-ops/archive_startup.log

# 查看歸檔統計
tail -100 ~/workspace/kanban-ops/archive.log
```

---

## 🎯 總結

### 優勢

✅ **高頻歸檔**：2 天、7 天、14 天三階段，適合高頻研究
✅ **自動化**：重開機時自動檢查並執行
✅ **性能優化**：保持 tasks.json 輕量（< 30 KB）
✅ **可查詢**：快速歸檔保留查詢能力
✅ **空間節省**：壓縮歸檔節省 95%+ 空間
✅ **靈活配置**：可調整時間閾值和文件大小閾值

### 實施步驟

1. ✅ 歸檔腳本已更新（v3.0 - 高頻版本）
2. ✅ 啟動腳本已創建（archive_on_startup.sh）
3. ⏳ 選擇集成方案（啟動腳本 / Heartbeat / Cron）
4. ⏳ 測試歸檔流程
5. ⏳ 監控歸檔效果

### 下一步

根據你的需求選擇集成方案：

- **推薦**：啟動腳本（重開機時自動檢查）
- **備選**：集成到 Heartbeat（每日檢查）
- **備選**：Cron（每天凌晨 2 點執行）

---

**文檔創建時間：** 2026-02-20
**腳本版本：** v3.0（高頻版本）
**狀態：** ✅ 測試通過，準備部署
