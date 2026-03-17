#!/bin/bash
# Telegram 錯誤監控腳本
# 定期檢查 Gateway 日誌中的 Telegram 錯誤

LOG_FILE="/tmp/openclaw/openclaw-$(date +%Y-%m-%d).log"
ALERT_THRESHOLD=5  # 5 分鐘內錯誤超過 5 次就警告

# 檢查最近 5 分鐘的 Telegram 錯誤
ERROR_COUNT=$(tail -n 100 "$LOG_FILE" 2>/dev/null | \
  grep -i "telegram" | \
  grep -i "error\|failed\|not found" | \
  wc -l)

if [ "$ERROR_COUNT" -gt "$ALERT_THRESHOLD" ]; then
  echo "⚠️  警告：最近 5 分鐘內發現 $ERROR_COUNT 個 Telegram 錯誤"
  echo "請檢查：tail -20 $LOG_FILE"
  # 可以發送通知（如果需要）
fi

echo "Telegram 錯誤檢查：$ERROR_COUNT 個（閾值：$ALERT_THRESHOLD）"
