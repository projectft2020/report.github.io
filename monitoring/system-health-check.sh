#!/bin/bash
# OpenClaw 系統健康檢查
# 每天執行一次，檢查所有關鍵服務

echo "=== OpenClaw 系統健康檢查 ==="
echo "時間：$(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 1. 檢查 Gateway 狀態
echo "1. Gateway 狀態："
if launchctl list | grep -q "ai.openclaw.gateway"; then
    PID=$(launchctl list | grep "ai.openclaw.gateway" | awk '{print $1}')
    echo "  ✅ 運行中（PID: $PID）"
else
    echo "  ❌ 未運行"
fi
echo ""

# 2. 檢查 Telegram 錯誤
echo "2. Telegram 錯誤（最近 5 分鐘）："
LOG_FILE="/tmp/openclaw/openclaw-$(date +%Y-%m-%d).log"
ERROR_COUNT=$(tail -n 100 "$LOG_FILE" 2>/dev/null | \
  grep -i "telegram" | \
  grep -i "error\|failed\|not found" | \
  wc -l)
if [ "$ERROR_COUNT" -eq 0 ]; then
    echo "  ✅ 沒有錯誤"
elif [ "$ERROR_COUNT" -lt 5 ]; then
    echo "  ⚠️  少量錯誤（$ERROR_COUNT 個）"
else
    echo "  ❌ 大量錯誤（$ERROR_COUNT 個）"
fi
echo ""

# 3. 檢查其他服務
echo "3. 其他服務："
if launchctl list | grep -q "io.github.openclaw.monitoring"; then
    echo "  ✅ monitoring 運行中"
else
    echo "  ❌ monitoring 未運行"
fi

if launchctl list | grep -q "ai.openclaw.cleanup"; then
    echo "  ✅ cleanup 運行中"
else
    echo "  ❌ cleanup 未運行"
fi
echo ""

# 4. 檢查磁盤空間
echo "4. 磁盤空間："
DISK_USAGE=$(df -h ~ | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    echo "  ✅ 足夠（$DISK_USAGE%）"
elif [ "$DISK_USAGE" -lt 90 ]; then
    echo "  ⚠️  警告（$DISK_USAGE%）"
else
    echo "  ❌ 緊急（$DISK_USAGE%）"
fi
echo ""

# 5. 檢查 Git 狀態
echo "5. Git 狀態："
cd ~/workspace 2>/dev/null
if [ $? -eq 0 ]; then
    GIT_STATUS=$(git status --short 2>/dev/null | wc -l)
    if [ "$GIT_STATUS" -eq 0 ]; then
        echo "  ✅ 乾淨（無未提交更改）"
    else
        echo "  ⚠️  有未提交更改（$GIT_STATUS 個文件）"
    fi
else
    echo "  ⚠️  workspace 不存在"
fi
echo ""

echo "=== 健康檢查完成 ==="
