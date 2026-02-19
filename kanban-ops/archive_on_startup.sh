#!/bin/bash
#
# 啟動時自動歸檔 Kanban 任務
#
# 在重開機時自動檢查 tasks.json 大小，如果超過 200 KB 則執行歸檔
#
# 安裝方式：
# 1. 添加到 macOS Launch Agents
#    cp ~/workspace/kanban-ops/archive_on_startup.sh ~/Library/LaunchAgents/com.openclaw.kanban-archive.plist
#
# 2. 手動執行
#    bash ~/workspace/kanban-ops/archive_on_startup.sh
#

# 腳本路徑
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARCHIVE_SCRIPT="$SCRIPT_DIR/archive_tasks.py"
LOG_FILE="$SCRIPT_DIR/archive_startup.log"

# 執行歸檔
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 啟動時歸檔檢查" >> "$LOG_FILE"

# 檢查歸檔腳本是否存在
if [ ! -f "$ARCHIVE_SCRIPT" ]; then
    echo "❌ 歸檔腳本不存在：$ARCHIVE_SCRIPT" >> "$LOG_FILE"
    exit 1
fi

# 執行歸檔（自動觸發，根據文件大小）
python3 "$ARCHIVE_SCRIPT" >> "$LOG_FILE" 2>&1

# 檢查執行結果
if [ $? -eq 0 ]; then
    echo "✅ 啟動時歸檔完成" >> "$LOG_FILE"
else
    echo "❌ 啟動時歸檔失敗" >> "$LOG_FILE"
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 啟動時歸檔檢查完成" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

exit 0
