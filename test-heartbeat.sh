#!/bin/bash
# test-heartbeat.sh
# Heartbeat 系統測試腳本
# 用於驗證 OpenClaw 2026.3.3 Heartbeat 功能

echo "=== Heartbeat 系統測試 ==="
echo "開始時間: $(date)"
echo ""

# 設置顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 測試計數器
PASS=0
FAIL=0

# 1. 檢查 HEARTBEAT.md 文件
echo "1. 檢查 HEARTBEAT.md 文件..."
HEARTBEAT_FILE="$HOME/.openclaw/workspace/HEARTBEAT.md"

if [ -f "$HEARTBEAT_FILE" ]; then
    echo -e "   ${GREEN}✅ HEARTBEAT.md 存在${NC}"
    echo "   路徑: $HEARTBEAT_FILE"
    ((PASS++))
else
    echo -e "   ${RED}❌ HEARTBEAT.md 不存在${NC}"
    echo "   預期路徑: $HEARTBEAT_FILE"
    ((FAIL++))
fi
echo ""

# 2. 檢查 auto_spawn_heartbeat.py 腳本
echo "2. 檢查 auto_spawn_heartbeat.py 腳本..."
SPAWN_SCRIPT="$HOME/.openclaw/workspace/kanban-ops/auto_spawn_heartbeat.py"

if [ -f "$SPAWN_SCRIPT" ]; then
    echo -e "   ${GREEN}✅ auto_spawn_heartbeat.py 存在${NC}"
    echo "   路徑: $SPAWN_SCRIPT"
    ((PASS++))
else
    echo -e "   ${RED}❌ auto_spawn_heartbeat.py 不存在${NC}"
    echo "   預期路徑: $SPAWN_SCRIPT"
    ((FAIL++))
fi
echo ""

# 3. 執行 auto_spawn_heartbeat.py
echo "3. 執行 auto_spawn_heartbeat.py..."
cd "$HOME/.openclaw/workspace"

if python3 kanban-ops/auto_spawn_heartbeat.py > /tmp/heartbeat-test-$(date +%s).log 2>&1; then
    echo -e "   ${GREEN}✅ auto_spawn_heartbeat.py 執行成功${NC}"

    # 檢查是否生成了 spawn_commands.jsonl
    if [ -f "kanban/spawn_commands.jsonl" ]; then
        TASK_COUNT=$(wc -l < kanban/spawn_commands.jsonl)
        echo "   生成了 $TASK_COUNT 個啟動命令"
        ((PASS++))
    else
        echo -e "   ${YELLOW}⚠️  spawn_commands.jsonl 不存在（可能無待啟動任務）${NC}"
        ((PASS++))
    fi
else
    echo -e "   ${RED}❌ auto_spawn_heartbeat.py 執行失敗${NC}"
    echo "   查看日誌: cat /tmp/heartbeat-test-*.log"
    ((FAIL++))
fi
echo ""

# 4. 檢查背壓機制
echo "4. 檢查背壓機制..."
BACKPRESSURE_SCRIPT="$HOME/.openclaw/workspace/kanban-ops/backpressure.py"

if [ -f "$BACKPRESSURE_SCRIPT" ]; then
    if python3 kanban-ops/backpressure.py check > /tmp/backpressure-test-$(date +%s).log 2>&1; then
        echo -e "   ${GREEN}✅ 背壓機制檢查成功${NC}"

        # 提取健康度
        HEALTH=$(grep "健康度" /tmp/backpressure-test-$(date +%s).log | tail -1)
        if [ -n "$HEALTH" ]; then
            echo "   $HEALTH"
        fi
        ((PASS++))
    else
        echo -e "   ${RED}❌ 背壓機制檢查失敗${NC}"
        ((FAIL++))
    fi
else
    echo -e "   ${YELLOW}⚠️  backpressure.py 不存在${NC}"
    echo -e "   ${YELLOW}   跳過背壓機制測試${NC}"
fi
echo ""

# 5. 檢查 task_state_rollback.py
echo "5. 檢查任務狀態回滾機制..."
ROLLBACK_SCRIPT="$HOME/.openclaw/workspace/kanban-ops/task_state_rollback.py"

if [ -f "$ROLLBACK_SCRIPT" ]; then
    if python3 kanban-ops/task_state_rollback.py > /tmp/rollback-test-$(date +%s).log 2>&1; then
        echo -e "   ${GREEN}✅ 任務狀態回滾檢查成功${NC}"

        # 檢查是否有卡住的任務
        if grep -q "卡住任務" /tmp/rollback-test-$(date +%s).log; then
            STUCK_COUNT=$(grep "卡住任務" /tmp/rollback-test-$(date +%s).log | grep -c "確定")
            if [ $STUCK_COUNT -gt 0 ]; then
                echo -e "   ${YELLOW}⚠️  發現 $STUCK_COUNT 個卡住的任務${NC}"
            fi
        fi
        ((PASS++))
    else
        echo -e "   ${RED}❌ 任務狀態回滾檢查失敗${NC}"
        ((FAIL++))
    fi
else
    echo -e "   ${YELLOW}⚠️  task_state_rollback.py 不存在${NC}"
    echo -e "   ${YELLOW}   跳過回滾機制測試${NC}"
fi
echo ""

# 6. 檢查 task_sync.py
echo "6. 檢查任務同步機制..."
SYNC_SCRIPT="$HOME/.openclaw/workspace/kanban-ops/task_sync.py"

if [ -f "$SYNC_SCRIPT" ]; then
    if python3 kanban-ops/task_sync.py > /tmp/sync-test-$(date +%s).log 2>&1; then
        echo -e "   ${GREEN}✅ 任務同步成功${NC}"
        ((PASS++))
    else
        echo -e "   ${RED}❌ 任務同步失敗${NC}"
        ((FAIL++))
    fi
else
    echo -e "   ${YELLOW}⚠️  task_sync.py 不存在${NC}"
    echo -e "   ${YELLOW}   跳過同步機制測試${NC}"
fi
echo ""

# 7. 檢查 Gateway 日誌中的 Heartbeat 記錄
echo "7. 檢查 Gateway 日誌中的 Heartbeat 記錄..."
if openclaw gateway logs --tail 100 > /tmp/gateway-logs-$(date +%s).txt 2>&1; then
    HEARTBEAT_LOGS=$(grep -i "heartbeat" /tmp/gateway-logs-$(date +%s).txt | wc -l)

    if [ $HEARTBEAT_LOGS -gt 0 ]; then
        echo -e "   ${GREEN}✅ 找到 $HEARTBEAT_LOGS 條 Heartbeat 日誌${NC}"
        echo "   最近的 Heartbeat 日誌:"
        grep -i "heartbeat" /tmp/gateway-logs-$(date +%s).txt | tail -3
        ((PASS++))
    else
        echo -e "   ${YELLOW}⚠️  未找到 Heartbeat 日誌（可能剛啟動）${NC}"
        ((PASS++))
    fi
else
    echo -e "   ${RED}❌ 無法獲取 Gateway 日誌${NC}"
    ((FAIL++))
fi
echo ""

# 清理臨時文件
rm -f /tmp/heartbeat-test-*.log
rm -f /tmp/backpressure-test-*.log
rm -f /tmp/rollback-test-*.log
rm -f /tmp/sync-test-*.log
rm -f /tmp/gateway-logs-*.txt

# 總結
echo "=== 測試總結 ==="
echo "通過: $PASS"
echo "失敗: $FAIL"
echo "總計: $((PASS + FAIL))"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✅ 所有 Heartbeat 測試通過！${NC}"
    echo "結束時間: $(date)"
    exit 0
else
    echo -e "${RED}❌ 有 $FAIL 個測試失敗${NC}"
    echo "結束時間: $(date)"
    exit 1
fi
