# OpenClaw Gateway 定期重啟設定

**設定日期：** 2026-02-17
**目標：** 定期重啟 OpenClaw gateway 以保持穩定性

---

## 重啟頻率建議

### 每日重啟（推薦）
- **時間**：凌晨 3:00 AM
- **原因**：
  - 深夜低使用時間
  - 減少對日常使用影響
  - 定期清理內存
- **週期**：每天一次

### 每 2 天重啟
- **時間**：凌晨 3:00 AM
- **原因**：減少重啟頻率，但仍保持穩定性
- **週期**：每 2 天一次

### 每 7 天重啟
- **時間**：週日凌晨 3:00 AM
- **原因**：週日使用較少
- **週期**：每 7 天一次

---

## 系統 cron job 設定

### 使用 crontab

```bash
# 1. 開啟 crontab 編輯器
crontab -e

# 2. 加入以下行（每日重啟）
0 3 * * * /usr/local/bin/openclaw gateway restart

# 或者每 2 天重啟
0 3 */2 * * /usr/local/bin/openclaw gateway restart

# 或者每 7 天重啟（週日）
0 3 * * 0 /usr/local/bin/openclaw gateway restart
```

### 使用 launchd（macOS）

建立 plist 檔案：
```bash
# 建立服務檔案
sudo nano /Library/LaunchDaemons/com.openclaw.gateway.restart.plist
```

內容：
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.openclaw.gateway.restart</string>

    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/openclaw</string>
        <string>gateway</string>
        <string>restart</string>
    </array>

    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>3</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>

    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
```

### 設定後
```bash
# 授予正確權限
sudo chown root:wheel /Library/LaunchDaemons/com.openclaw.gateway.restart.plist
sudo chmod 644 /Library/LaunchDaemons/com.openclaw.gateway.restart.plist

# 載入服務
sudo launchctl load -w /Library/LaunchDaemons/com.openclaw.gateway.restart.plist
```

---

## 檢查 cron job

### 查看當前 cron jobs
```bash
crontab -l
```

### 測試 cron job
```bash
# 手動執行測試
openclaw gateway restart
```

### 查看系統日誌
```bash
log show --predicate 'process == "openclaw"' --last 1h
```

---

## 注意事項

### 重啟前
- ✅ 確認沒有重要的未保存工作
- ✅ 確認沒有正在運行的關鍵任務
- ✅ 重啟過程約 30 秒

### 重啟後
- ✅ 確認 OpenClaw 正常啟動
- ✅ 測試基本功能（瀏\
覽器、sessions 等）
- ✅ 檢查日誌是否有錯誤

### 推薦設定
- **最佳頻率**：每 1-2 天
- **最佳時間**：凌晨 3:00 AM
- **不推薦**：高使用時段重啟（如晚上 8-10 PM）

---

## 取消 cron job

```bash
# 查看當前 jobs
crontab -l

# 刪除所有 jobs
crontab -r

# 刪除特定 job（需要編輯 crontab）
crontab -e
```

---

## 記錄

- **設定日期**：2026-02-17
- **重啟頻率**：每日凌晨 3:00 AM
- **下次重啟**：2026-02-18 3:00 AM
