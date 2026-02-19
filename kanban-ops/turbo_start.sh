#!/bin/bash
#
# 啟動加速模式
#
# 使用方式：
#   bash ~/workspace/kanban-ops/turbo_start.sh
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TURBO_SCRIPT="$SCRIPT_DIR/turbo_mode.py"

echo ""
echo "🌙 啟動加速模式..."
echo "⏰ 預計運行時間：6 小時"
echo "📝 隨時發送「我醒了」可以停止"
echo ""

# 執行加速模式
python3 "$TURBO_SCRIPT" start
