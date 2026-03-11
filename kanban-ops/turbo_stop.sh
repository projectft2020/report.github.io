#!/bin/bash
# Turbo Mode 停止腳本

TURBO_DIR="$HOME/.openclaw/workspace/kanban-ops"
STATUS_FILE="$TURBO_DIR/TURBO_STATUS.json"
LOG_FILE="$TURBO_DIR/TURBO_LOG.md"

# 檢查是否已運行
if [ ! -f "$STATUS_FILE" ]; then
    echo "⚠️  Turbo Mode 未運行"
    exit 1
fi

ACTIVE=$(python3 -c "import json; print(json.load(open('$STATUS_FILE')).get('active', False))" 2>/dev/null || echo "false")
if [ "$ACTIVE" != "True" ]; then
    echo "⚠️  Turbo Mode 未運行"
    exit 1
fi

# 獲取統計數據
python3 << EOF
import json

with open('$STATUS_FILE', 'r') as f:
    status = json.load(f)

# 記錄統計
stats = status.get('stats', {})
print(f"觸發任務: {stats.get('tasks_triggered', 0)}")
print(f"執行掃描: {stats.get('scans_performed', 0)}")
print(f"創建文檔: {stats.get('documents_created', 0)}")
print(f"遇到錯誤: {stats.get('errors_encountered', 0)}")
EOF

# 停止 Turbo Mode
python3 << EOF
import json
from datetime import datetime

with open('$STATUS_FILE', 'r') as f:
    status = json.load(f)

status['active'] = False
status['stopped_at'] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
status['current_phase'] = 'stopped'

with open('$STATUS_FILE', 'w') as f:
    json.dump(status, f, indent=2, ensure_ascii=False)

print("✅ Turbo Mode 已停止")
EOF

# 記錄日誌
NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "- [$NOW] Turbo Mode 手動停止" >> "$LOG_FILE"

echo ""
echo "🛑 Turbo Mode 已停止"
echo ""
echo "💡 輸入 '我醒了' 自動停止加速模式"
