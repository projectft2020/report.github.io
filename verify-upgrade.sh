#!/bin/bash

# OpenClaw 升級驗證腳本
# 版本: 2026.3.3
# 用途: 驗證升級後的關鍵功能是否正常

set -e  # 遇到錯誤立即退出

echo "========================================"
echo "OpenClaw 升級驗證清單"
echo "========================================"
echo "時間: $(date '+%Y-%m-%d %H:%M:%S')"
echo "目標版本: 2026.3.3"
echo ""

# 顏色定義
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 計數器
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0

# 測試函數
run_test() {
    local test_name="$1"
    local test_command="$2"
    local should_pass="$3"  # true 或 false

    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -n "[$TOTAL_TESTS] 測試: $test_name ... "

    if eval "$test_command" > /dev/null 2>&1; then
        if [ "$should_pass" = "true" ]; then
            echo -e "${GREEN}✅ 通過${NC}"
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            echo -e "${RED}❌ 失敗（應該失敗但通過）${NC}"
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
    else
        if [ "$should_pass" = "false" ]; then
            echo -e "${GREEN}✅ 通過${NC}"
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            echo -e "${RED}❌ 失敗${NC}"
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
    fi
}

skip_test() {
    local test_name="$1"
    local reason="$2"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    SKIPPED_TESTS=$((SKIPPED_TESTS + 1))
    echo -e "[$TOTAL_TESTS] ${YELLOW}⏭️ 跳過${NC}: $test_name"
    echo "    原因: $reason"
}

echo "========================================"
echo "高優先級驗證（必須通過）"
echo "========================================"
echo ""

# 1. Python 環境檢查
echo "--- Python 環境檢查 ---"
run_test "Python 3.9+ 可用" "python3 --version" true
run_test "OpenClaw 命令可用" "command -v openclaw" true
echo ""

# 2. 心跳自動化系統
echo "--- 心跳自動化系統 ---"
if [ -f "kanban-ops/auto_spawn_heartbeat.py" ]; then
    run_test "auto_spawn_heartbeat.py 可執行" "python3 kanban-ops/auto_spawn_heartbeat.py --help" true
else
    skip_test "auto_spawn_heartbeat.py" "文件不存在"
fi

if [ -f "kanban-ops/backpressure.py" ]; then
    run_test "背壓機制檢查" "python3 kanban-ops/backpressure.py check" true
else
    skip_test "背壓機制檢查" "文件不存在"
fi

if [ -f "kanban-ops/task_state_rollback.py" ]; then
    run_test "狀態回滾檢查" "python3 kanban-ops/task_state_rollback.py" true
else
    skip_test "狀態回滾檢查" "文件不存在"
fi
echo ""

# 3. 子代理通信
echo "--- 子代理通信 ---"
if [ -f "kanban-ops/tasks.json" ]; then
    run_test "tasks.json 格式正確" "python3 -c \"import json; json.load(open('kanban-ops/tasks.json'))\"" true
else
    skip_test "tasks.json 格式檢查" "文件不存在"
fi

if [ -d "kanban/works" ]; then
    run_test "工作目錄存在" "test -d kanban/works" true
else
    skip_test "工作目錄檢查" "目錄不存在"
fi
echo ""

# 4. 任務同步
echo "--- 任務同步 ---"
if [ -f "kanban-ops/task_sync.py" ]; then
    run_test "task_sync.py 可執行" "python3 kanban-ops/task_sync.py" true
else
    skip_test "task_sync.py" "可執行" "文件不存在"
fi
echo ""

# 5. 錯誤恢復
echo "--- 錯誤恢復 ---"
if [ -f "kanban-ops/error_recovery.py" ]; then
    run_test "error_recovery.py 可執行" "python3 kanban-ops/error_recovery.py --help" true
else
    skip_test "error_recovery.py" "可執行" "文件不存在"
fi
echo ""

# 6. 任務清理
echo "--- 任務清理 ---"
if [ -f "kanban-ops/task_cleanup.py" ]; then
    run_test "task_cleanup.py 檢查" "python3 kanban-ops/task_cleanup.py check" true
else
    skip_test "task_cleanup.py 檢查" "文件不存在"
fi
echo ""

echo "========================================"
echo "中優先級驗證（建議通過）"
echo "========================================"
echo ""

# 7. Scout 系統（可選）
echo "--- Scout 系統 ---"
if [ -f "kanban-ops/scout_agent.py" ]; then
    run_test "scout_agent.py 可執行" "python3 kanban-ops/scout_agent.py --help" true
else
    skip_test "scout_agent.py" "文件不存在"
fi

if [ -f "kanban-ops/monitor_and_refill.py" ]; then
    run_test "monitor_and_refill.py 可執行" "python3 kanban-ops/monitor_and_refill.py" true
else
    skip_test "monitor_and_refill.py" "可執行" "文件不存在"
fi
echo ""

# 8. Dashboard（可選）
echo "--- Dashboard ---"
if [ -d "Dashboard" ]; then
    if [ -f "Dashboard/docker-compose.dev.yml" ]; then
        run_test "docker-compose.dev.yml 存在" "test -f Dashboard/docker-compose.dev.yml" true
    else
        skip_test "docker-compose.dev.yml" "文件不存在"
    fi
else
    skip_test "Dashboard" "目錄不存在"
fi
echo ""

echo "========================================"
echo "低優先級驗證（可選）"
echo "========================================"
echo ""

# 9. 配置文件
echo "--- 配置文件 ---"
if [ -f "HEARTBEAT.md" ]; then
    run_test "HEARTBEAT.md 可讀" "test -r HEARTBEAT.md" true
else
    skip_test "HEARTBEAT.md" "文件不存在"
fi

if [ -f "UPGRADE_PLAN.md" ]; then
    run_test "UPGRADE_PLAN.md 可讀" "test -r UPGRADE_PLAN.md" true
else
    skip_test "UPGRADE_PLAN.md" "文件不存在"
fi
echo ""

# 10. 技能系統
echo "--- 技能系統 ---"
if [ -d "skills" ]; then
    run_test "skills 目錄存在" "test -d skills" true
    SKILL_COUNT=$(find skills -name "*.md" 2>/dev/null | wc -l | xargs)
    echo "    找到 $SKILL_COUNT 個技能文檔"
else
    skip_test "skills 目錄" "目錄不存在"
fi
echo ""

# 11. 記憶系統
echo "--- 記憶系統 ---"
if [ -d "memory" ]; then
    run_test "memory 目錄存在" "test -d memory" true
    if [ -f "memory/$(date +%Y-%m-%d).md" ]; then
        echo "    ✅ 今天的記憶文件存在"
    else
        echo "    ⚠️  今天的記憶文件不存在"
    fi
else
    skip_test "memory 目錄" "目錄不存在"
fi
echo ""

echo "========================================"
echo "驗證結果總結"
echo "========================================"
echo ""
echo "總測試數: $TOTAL_TESTS"
echo -e "通過: ${GREEN}$PASSED_TESTS${NC}"
echo -e "失敗: ${RED}$FAILED_TESTS${NC}"
echo -e "跳過: ${YELLOW}$SKIPPED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✅ 所有必要測試通過！可以繼續升級。${NC}"
    exit 0
else
    echo -e "${RED}❌ 有 $FAILED_TESTS 個測試失敗。請檢查並修復後再繼續。${NC}"
    exit 1
fi
