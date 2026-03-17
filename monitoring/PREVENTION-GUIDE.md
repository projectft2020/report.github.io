# OpenClaw 預防性措施指南

## 目標
防止 Telegram Gateway 問題再次發生，確保系統穩定運行。

---

## 當前狀態

### ✅ 已執行
- Telegram 已禁用（防止 404 錯誤導致 Gateway 崩潰）
- Gateway 重新安裝並正常運行
- 系統監控腳本已創建

### ⚠️ 限制
- 失去 Telegram 功能（不能推送通知）
- 需要手動檢查系統狀態

---

## 預防性措施

### 層次 1：短期措施（當前可用）

#### 1.1 保持禁用狀態
- **狀態：** ✅ 已執行
- **位置：** `~/.openclaw/openclaw.json` → `channels.telegram.enabled = false`
- **優點：** 簡單直接，立即生效
- **缺點：** 失去 Telegram 功能

#### 1.2 定期監控
- **腳本：** `~/workspace/monitoring/telegram-monitor.sh`
- **執行頻率：** 每小時一次
- **監控內容：**
  - Telegram 錯誤數量
  - Gateway 運行狀態
  - 系統資源使用

**使用方式：**
```bash
# 手動執行
~/workspace/monitoring/telegram-monitor.sh

# 設置 cron 每小時執行
# (需要手動設置)
```

---

### 層次 2：中期措施（需要配置）

#### 2.1 系統健康檢查
- **腳本：** `~/workspace/monitoring/system-health-check.sh`
- **執行頻率：** 每天一次（早上 8:00）
- **檢查內容：**
  - Gateway 狀態
  - Telegram 錯誤
  - 其他服務（monitoring、cleanup）
  - 磁盤空間
  - Git 狀態

**使用方式：**
```bash
# 手動執行
~/workspace/monitoring/system-health-check.sh

# 測試運行
~/workspace/monitoring/system-health-check.sh
```

**預期輸出：**
```
=== OpenClaw 系統健康檢查 ===
時間：2026-03-18 01:30:00

1. Gateway 狀態：
  ✅ 運行中（PID: 29278）

2. Telegram 錯誤（最近 5 分鐘）：
  ✅ 沒有錯誤

3. 其他服務：
  ✅ monitoring 運行中
  ✅ cleanup 運行中

4. 磁盤空間：
  ✅ 足夠（45%）

5. Git 狀態：
  ✅ 乾淨（無未提交更改）

=== 健康檢查完成 ===
```

#### 2.2 配置選項探索
- **目標：** 找到跳過 webhook 清理的配置選項
- **待查詢：**
  - `skipWebhookCleanup`
  - `ignoreWebhookErrors`
  - `webhook.cleanupOnStart`

**下一步：**
1. 查詢 OpenClaw 文檔
2. 聯繫 OpenClaw 社群（Discord）
3. 測試配置選項（如果存在）

#### 2.3 Webhook 模式（可選）
- **需求：** 公網 IP 或 tunneling（ngrok）
- **優點：** 避免 polling 模式的問題
- **缺點：** 需要額外配置

**實施步驟：**
```bash
# 1. 安裝 ngrok
brew install ngrok

# 2. 啟動 ngrok tunnel
ngrok http 18789

# 3. 獲取 ngrok URL（例如：https://abc123.ngrok.io）

# 4. 設置 Telegram webhook
curl -X POST "https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d "{\"url\":\"https://abc123.ngrok.io/telegram/webhook\"}"
```

---

### 層次 3：長期措施（需要 OpenClaw 團隊修復）

#### 3.1 報告 Bug
- **Bug 描述：**
  ```
  Gateway 在啟動時會嘗試刪除舊的 webhook（deleteWebhook），
  但如果 webhook 不存在（返回 404），會把這當作錯誤並退出。

  預期行為：404 應該被忽略（webhook 未設置是正常的）
  實際行為：Gateway 把 404 當作錯誤並退出
  ```

- **報告途徑：**
  - Discord: https://discord.com/invite/clawd
  - GitHub Issues: https://github.com/openclaw/openclaw/issues

#### 3.2 等待修復並重新啟用
- **修復後操作：**
  ```bash
  # 重新啟用 Telegram
  cat ~/.openclaw/openclaw.json | python3 -c "
  import sys, json
  d = json.load(sys.stdin)
  d['channels']['telegram']['enabled'] = True
  with open('/Users/charlie/.openclaw/openclaw.json', 'w') as f:
      json.dump(d, f, indent=2)
  "

  # 重啟 Gateway
  openclaw gateway restart
  ```

---

## 推薦執行計劃

### 立即執行（今天）
- [x] 禁用 Telegram（已執行）
- [ ] 測試系統健康檢查腳本
- [ ] 設置 cron 每天執行健康檢查

### 本週執行
- [ ] 查詢 OpenClaw 文檔尋找配置選項
- [ ] 在 Discord 社群詢問其他用戶
- [ ] 準備 Bug 報告

### 本月執行
- [ ] 提交 Bug 報告
- [ ] 關注 OpenClaw 更新
- [ ] 評估是否需要 webhook 模式

---

## 應急方案

### 如果 Gateway 再次崩潰
```bash
# 1. 檢查錯誤日誌
tail -50 /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log

# 2. 禁用 Telegram（如果未禁用）
cat ~/.openclaw/openclaw.json | python3 -c "
import sys, json
d = json.load(sys.stdin)
d['channels']['telegram']['enabled'] = False
with open('/Users/charlie/.openclaw/openclaw.json', 'w') as f:
    json.dump(d, f, indent=2)
"

# 3. 重啟 Gateway
openclaw gateway restart

# 4. 驗證狀態
openclaw gateway status
```

---

## 相關資源

### OpenClaw 文檔
- Gateway: https://docs.openclaw.ai/gateway
- Troubleshooting: https://docs.openclaw.ai/troubleshooting
- Discord: https://discord.com/invite/clawd

### 監控腳本
- Telegram 監控：`~/workspace/monitoring/telegram-monitor.sh`
- 系統健康檢查：`~/workspace/monitoring/system-health-check.sh`

### 配置文件
- OpenClaw 配置：`~/.openclaw/openclaw.json`
- LaunchAgent：`~/Library/LaunchAgents/ai.openclaw.gateway.plist`

---

## 總結

**當前最佳策略：**
1. ✅ 保持 Telegram 禁用（防止崩潰）
2. ✅ 實施系統健康檢查（監控狀態）
3. ⏳ 等待 OpenClaw 修復 bug
4. ⏳ 探索配置選項（如果存在）

**長期目標：**
- 重新啟用 Telegram 功能
- 避免類似問題再次發生
- 建立穩定的系統運行環境

---

**最後更新：** 2026-03-18 01:30
**狀態：** 系統穩定運行中
