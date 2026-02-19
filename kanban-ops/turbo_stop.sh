#!/bin/bash
#
# 停止加速模式
#
# 使用方式：
#   bash ~/workspace/kanban-ops/turbo_stop.sh
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TURBO_SCRIPT="$SCRIPT_DIR/turbo_mode.py"

echo ""
echo "☀️ 停止加速模式..."
echo ""

# 停止加速模式
python3 "$TURBO_SCRIPT" stop
