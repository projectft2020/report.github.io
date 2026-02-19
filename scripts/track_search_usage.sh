#!/bin/bash
# Brave Search API Usage Tracker
# 自動記錄每日使用量並在配額不足時發送警報

set -euo pipefail

# 設定參數
LOG_FILE="/Users/charlie/.openclaw/workspace/QUANT_SEARCH_LOG.md"
ALERT_THRESHOLD=100
MAX_LIMIT=2000

# 當前日期
CURRENT_DATE=$(date +"%Y-%m-%d")

# 記錄當前使用量
echo "---" >> "$LOG_FILE"
echo "## $CURRENT_DATE" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# 計算今日使用量（從今日開始到現在）
TODAY_USAGE=0 # 暫時設為 0，實際應該從日誌中計算
# TODO: 從實際的 Brave Search log 中讀取今日使用量

# 假設使用量（實際應該從 API 檢查）
# 這裡需要實作實際的使用量檢查
REMAINING=$((MAX_LIMIT - TODAY_USAGE))

# 記錄使用量
echo "### 使用量統計" >> "$LOG_FILE"
echo "- **日期**: $CURRENT_DATE" >> "$LOG_FILE"
echo "- **剩餘配額**: $REMAINING 次 / $MAX_LIMIT 次" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# 如果剩餘配額不足，發送警報
if [ $REMAINING -lt $ALERT_THRESHOLD ]; then
    echo "⚠️  **警告**：剩餘配額不足 $REMAINING 次！" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
    echo "建議行動：" >> "$LOG_FILE"
    echo "1. 檢查 Brave Search API 配置" >> "$LOG_FILE"
    echo "2. 確認是否需要增加配額" >> "$LOG_FILE"
    echo "3. 調整使用策略" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"

    # TODO: 發送 email 或其他警報
    # echo "配額警告：剩餘 $REMAINING 次" | mail -s "Brave Search 配額警告" user@example.com
fi

echo "✅ 記錄完成：$CURRENT_DATE - 剩餘配額: $REMAINING 次"
