# OpenClaw 每週備份指南 (方案 A)

**日期**: 2026-02-20
**方案**: 每週手動備份 (最簡單)

---

## 🎯 使用方式

### 方式 1: 直接執行 (推薦)

```bash
ssh charlie@192.168.1.117
cd ~
./weekly_backup.sh
```

**執行後會**:
1. 顯示將備份的目錄和大小
2. 詢問確認
3. 創建備份文件到桌面
4. 顯示備份結果

### 方式 2: 通過 VNC/遠程桌面

如果在 Mac Mini 上直接操作:
1. 打開 Terminal
2. 執行: `~/weekly_backup.sh`
3. 輸入密碼確認
4. 備份文件會出現在桌面

---

## 📦 備份內容

**包含的目錄**:
- `~/.openclaw/agents/` - 所有 agent 配置
- `~/.openclaw/workspace/` - 任務數據
- `~/monitoring/` - 監控系統配置

**備份位置**:
- 桌面: `openclaw-backup-YYYYMMDD.tar.gz`

**預估大小**: 約 10-50 MB (壓縮後)

---

## 📅 建議備份時刻

**每週日晚上** (或其他方便的時間):
- ✅ 工作週結束
- ✅ 系統相對閒置
- ✅ 有時間處理備份文件

**設置提醒** (可選):
```bash
# macOS 日曆或提醒事項
# 標題: "OpenClaw 週備份"
# 重複: 每週日 晚上 9 點
```

---

## 🎯 備份後的處理

### 步驟 1: 驗證備份

```bash
# 查看備份文件大小
ls -lh ~/Desktop/openclaw-backup-*.tar.gz

# 應該看到類似:
# -rw-r--r-- 1 charlie staff 25M Feb 20 openclaw-backup-20260220.tar.gz
```

### 步驟 2: 複製到外部硬碟

**選項 A: 外接硬碟**
```bash
# 掛載外部硬碟後
cp ~/Desktop/openclaw-backup-*.tar.gz /Volumes/YourExternalDrive/
```

**選項 B: 雲端存儲**
```bash
# 如果有雲端同步目錄 (如 Dropbox, Google Drive)
cp ~/Desktop/openclaw-backup-*.tar.gz ~/Dropbox/Backups/
# 或
cp ~/Desktop/openclaw-backup-*.tar.gz ~/Google\ Drive/Backups/
```

**選項 C: 傳輸到其他電腦**
```bash
# 通過 AFP/SMB 共享
# 或直接用 USB 隨身碟複製
```

### 步驟 3: 清理舊備份

```bash
# 保留最近 4 週的備份即可
cd ~/Desktop
ls -t openclaw-backup-*.tar.gz | tail -n +5 | xargs rm -f

# 或手動刪除桌面上舊的備份文件
```

---

## 🔙 還原方式 (如果需要)

```bash
# 解壓備份
cd ~
tar -xzf openclaw-backup-YYYYMMDD.tar.gz

# 會還原到:
# ~/.openclaw/agents/
# ~/.openclaw/workspace/
# ~/monitoring/
```

**注意**: 還原前會覆蓋現有文件，建議先備份當前狀態！

---

## 📊 備份檢查清單

### 每週執行時

- [ ] 執行備份腳本
- [ ] 確認備份成功 (看到 "✅ 備份成功")
- [ ] 查看備份文件大小 (應該 10-50 MB)
- [ ] 複製到外部硬碟或雲端
- [ ] 刪除超過 4 週的舊備份

### 每月檢查

- [ ] 測試還原一次 (驗證備份可用)
- [ ] 檢查外部硬碟空間
- [ ] 確認備份文件數量 (建議 4 個)

---

## 🎯 備份策略總結

### 已有的自動保護 ✅

**OpenClaw 內建歸檔**:
- ✅ 任務自動歸檔 (2-7-14 天策略)
- ✅ 配置文件自動備份
- ✅ 文件大小超過 200KB 自動觸發
- ✅ 啟動時自動檢查

### 你需要手動做的 ⭐

**每週一次** (5 分鐘):
```bash
1. ssh charlie@192.168.1.117
2. ./weekly_backup.sh
3. 複製備份文件到外部硬碟/雲端
4. 刪除桌面上的舊備份
```

**為什麼還需要手動備份**:
- ✅ 保護整個系統配置
- ✅ 防止硬體故障
- ✅ 可以遷移到新機器
- ✅ 災難恢復保障

---

## 💡 進階選項 (可選)

### 選項 1: 設置自動提醒

在 macOS 上設置週期性提醒:
1. 打開「提醒事項」App
2. 新建提醒: "執行 OpenClaw 週備份"
3. 重複: 每週
4. 提醒: 週日 晚上 9 點

### 選項 2: 使用 Time Machine (推薦)

如果你有 Time Machine:
```bash
# Time Machine 會自動備份整個系統
# 包括 ~/.openclaw 和 ~/monitoring

# 排除不需要的大目錄
sudo tmutil addexclusion ~/.openclaw/browser
sudo tmutil addexclusion ~/.openclaw/node_modules

# 然後每週的手動備份可以只備份關鍵配置
```

### 選項 3: 自動上傳到雲端 (進階)

```bash
# 修改腳本，在備份後自動上傳
# 需要 Google Drive API 或 Dropbox API
```

---

## 🎊 總結

**每週備份流程** (超簡單):

```bash
# 1. SSH 登入 (1 分鐘)
ssh charlie@192.168.1.117

# 2. 執行備份 (2 分鐘)
./weekly_backup.sh

# 3. 複製到外部硬碟 (2 分鐘)
# (通過 Finder 或終端)

# 總計: 5 分鐘/週
```

**你現在擁有**:
- ✅ 自動任務歸檔 (OpenClaw 內建)
- ✅ 每週完整備份 (手動執行)
- ✅ 災難恢復能力

**一個穩定、可靠、易維護的單機系統！** 🎉

---

**腳本位置**: `~/weekly_backup.sh`
**本指南**: `/Users/david/Documents/openclaw_matrix/WEEKLY_BACKUP_GUIDE.md`
**生產環境**: `~/.openclaw/workspace/kanban-ops/WEEKLY_BACKUP_GUIDE.md`

---

**創建日期**: 2026-02-20
**適用環境**: 單機 Mac Mini
**維護**: OpenClaw DevOps Team
