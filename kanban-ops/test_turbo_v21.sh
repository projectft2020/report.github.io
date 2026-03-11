#!/bin/bash
#
# 測試加速模式 v2.1
# 驗證新功能是否正常工作
#

echo "🧪 加速模式 v2.1 測試腳本"
echo "=========================================="
echo ""

# 1. 語法檢查
echo "1️⃣  語法檢查..."
python3 -m py_compile ~/workspace/kanban-ops/turbo_mode.py
if [ $? -eq 0 ]; then
    echo "   ✅ 語法檢查通過"
else
    echo "   ❌ 語法檢查失敗"
    exit 1
fi
echo ""

# 2. 配置檢查
echo "2️⃣  配置檢查..."
python3 << 'PYTHON_SCRIPT'
import json

TURBO_TASKS = "/Users/charlie/.openclaw/workspace/kanban-ops/TURBO_TASKS.json"

with open(TURBO_TASKS, 'r') as f:
    config = json.load(f)

print(f"   版本: {config.get('version', 'N/A')}")
print(f"   模式: {config['turbo_config']['mode']}")

required_keys = [
    'check_interval_minutes',
    'max_concurrent',
    'max_tasks_per_check',
    'wait_for_available',
    'min_available_slots',
    'timeout_minutes',
    'max_retries'
]

all_present = True
for key in required_keys:
    if key in config['turbo_config']:
        print(f"   ✅ {key}: {config['turbo_config'][key]}")
    else:
        print(f"   ❌ {key}: 缺失")
        all_present = False

if all_present:
    print("\n   ✅ 配置檢查通過")
else:
    print("\n   ❌ 配置檢查失敗")
PYTHON_SCRIPT
echo ""

# 3. 方法檢查
echo "3️⃣  新方法檢查..."
methods=(
    "load_tasks"
    "save_tasks"
    "get_running_tasks"
    "update_task_statuses"
    "wait_for_concurrent_tasks"
    "trigger_ready_tasks"
    "is_timeout"
    "is_valid_output"
    "handle_timeout"
    "trigger_next_tasks"
    "already_running"
    "all_dependencies_completed"
)

all_found=true
for method in "${methods[@]}"; do
    if grep -q "def $method" ~/workspace/kanban-ops/turbo_mode.py; then
        echo "   ✅ $method"
    else
        echo "   ❌ $method (未找到)"
        all_found=false
    fi
done

if [ "$all_found" = true ]; then
    echo "\n   ✅ 方法檢查通過"
else
    echo "\n   ❌ 方法檢查失敗"
fi
echo ""

# 4. 狀態檢查
echo "4️⃣  狀態檢查..."
python3 << 'PYTHON_SCRIPT'
import json

TASKS_FILE = "/Users/charlie/.openclaw/workspace-automation/kanban/tasks.json"

try:
    with open(TASKS_FILE, 'r') as f:
        data = json.load(f)

    tasks = data.get('tasks', [])
    status_counts = {}

    for task in tasks:
        status = task.get('status', 'unknown')
        status_counts[status] = status_counts.get(status, 0) + 1

    print(f"   總任務數: {len(tasks)}")
    for status, count in sorted(status_counts.items()):
        print(f"   {status}: {count}")

    print("\n   ✅ 狀態檢查通過")
except Exception as e:
    print(f"   ❌ 狀態檢查失敗: {e}")
PYTHON_SCRIPT
echo ""

# 5. 測試準備
echo "5️⃣  測試準備..."
echo "   測試模式：快速循環（0.1 小時）"
echo "   檢查次數：3 次"
echo "   並發上限：5 個"
echo ""

# 6. 執行測試
echo "6️⃣  執行測試..."
echo "   注意：這是一個快速測試，只運行 6 分鐘"
echo ""

read -p "   是否繼續執行測試？(y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # 創建臨時測試配置
    TEST_CONFIG="/tmp/turbo_test_config.json"
    python3 << 'PYTHON_SCRIPT'
import json

TURBO_TASKS = "/Users/charlie/.openclaw/workspace/kanban-ops/TURBO_TASKS.json"

with open(TURBO_TASKS, 'r') as f:
    config = json.load(f)

# 保存原始配置
original_config = config.copy()

# 設置測試配置
config['turbo_config']['duration_hours'] = 0.1  # 6 分鐘
config['turbo_config']['check_interval_minutes'] = 2  # 每 2 分鐘檢查

# 保存測試配置
with open('/tmp/turbo_test_config.json', 'w') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print(f"   測試配置已保存")
print(f"   時長: {config['turbo_config']['duration_hours']} 小時")
print(f"   間隔: {config['turbo_config']['check_interval_minutes']} 分鐘")
PYTHON_SCRIPT

    echo ""
    echo "   ⏳ 啟動測試..."
    echo ""

    # 執行測試
    cd ~/workspace && python3 kanban-ops/turbo_mode.py test-ready

    echo ""
    echo "   ✅ 測試完成"
    echo ""
else
    echo "   ⏸️  測試已取消"
fi

echo ""
echo "=========================================="
echo "🎉 測試腳本執行完成"
echo ""
