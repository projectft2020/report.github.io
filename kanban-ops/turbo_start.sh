#!/bin/bash
# Turbo Mode 啟動腳本

TURBO_DIR="$HOME/.openclaw/workspace/kanban-ops"
STATUS_FILE="$TURBO_DIR/TURBO_STATUS.json"
LOG_FILE="$TURBO_DIR/TURBO_LOG.md"

# 檢查是否已啟動
if [ -f "$STATUS_FILE" ]; then
    ACTIVE=$(python3 -c "import json; print(json.load(open('$STATUS_FILE')).get('active', False))" 2>/dev/null || echo "false")
    if [ "$ACTIVE" = "True" ]; then
        echo "⚠️  Turbo Mode 已經在運行中"
        exit 1
    fi
fi

# 獲取當前時間（ISO 8601）
NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
# 計算結束時間（6 小時後）
END_TIME=$(date -v+6H -u +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -u -d "+6 hours" +"%Y-%m-%dT%H:%M:%SZ")

# 更新狀態文件
python3 << EOF
import json
from datetime import datetime

status = {
    "active": True,
    "started_at": "$NOW",
    "estimated_end_at": "$END_TIME",
    "duration_hours": 6,
    "current_phase": "idle",
    "phases": [
        {
            "name": "快速清理",
            "duration_minutes": 30,
            "description": "歸檔、恢復任務、提交"
        },
        {
            "name": "並行研究",
            "duration_minutes": 120,
            "description": "觸發 Kanban 任務、Scout 掃描"
        },
        {
            "name": "深度工作",
            "duration_minutes": 120,
            "description": "知識庫、代碼優化、文檔"
        },
        {
            "name": "系統優化",
            "duration_minutes": 120,
            "description": "性能分析、日誌清理、備份"
        }
    ],
    "stats": {
        "tasks_triggered": 0,
        "scans_performed": 0,
        "documents_created": 0,
        "errors_encountered": 0
    }
}

with open('$STATUS_FILE', 'w') as f:
    json.dump(status, f, indent=2, ensure_ascii=False)

print(f"✅ Turbo Mode 已啟動")
print(f"   開始時間: {status['started_at']}")
print(f"   預計結束: {status['estimated_end_at']}")
print(f"   總時長: {status['duration_hours']} 小時")
EOF

# 記錄日誌
echo "- [$NOW] Turbo Mode 啟動 (預計結束: $END_TIME)" >> "$LOG_FILE"

echo "🚀 Turbo Mode 已啟動！"
echo "   持續時間: 6 小時"
echo "   預計結束: $(date -j -f '%Y-%m-%dT%H:%M:%SZ' "$END_TIME" '+%Y-%m-%d %H:%M:%S' 2>/dev/null || echo "$END_TIME")"
echo ""
echo "📝 使用 'bash ~/workspace/kanban-ops/turbo_stop.sh' 停止加速模式"
echo "📊 使用 'python3 ~/workspace/kanban-ops/turbo_mode.py status' 查看狀態"
