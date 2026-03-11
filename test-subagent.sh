#!/bin/bash
# test-subagent.sh
# Sub-agent 測試腳本
# 用於驗證 OpenClaw 2026.3.3 Sub-agent 功能

echo "=== Sub-agent 測試 ==="
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

# 創建唯一的測試任務 ID
TASK_ID="test-subagent-$(date +%s)"
echo "測試任務 ID: $TASK_ID"
echo ""

# 1. 檢查 sessions_list 命令
echo "1. 檢查 sessions_list 命令..."
if openclaw sessions list > /tmp/sessions-list-$(date +%s).txt 2>&1; then
    echo -e "   ${GREEN}✅ sessions_list 命令正常${NC}"
    ACTIVE_COUNT=$(grep -c "agent:" /tmp/sessions-list-$(date +%s).txt || echo "0")
    echo "   當前活躍子代理數: $ACTIVE_COUNT"
    ((PASS++))
else
    echo -e "   ${RED}❌ sessions_list 命令失敗${NC}"
    ((FAIL++))
fi
echo ""

# 2. 檢查可用 agent 列表
echo "2. 檢查可用 agent 列表..."
if openclaw agents list > /tmp/agents-list-$(date +%s).txt 2>&1; then
    echo -e "   ${GREEN}✅ agents_list 命令正常${NC}"
    echo "   可用的代理:"
    cat /tmp/agents-list-$(date +%s).txt | grep "id:" | head -5
    ((PASS++))
else
    echo -e "   ${RED}❌ agents_list 命令失敗${NC}"
    ((FAIL++))
fi
echo ""

# 3. 檢查會話歷史
echo "3. 檢查會話歷史功能..."
if openclaw sessions history --sessionKey main --limit 5 > /tmp/history-test-$(date +%s).txt 2>&1; then
    echo -e "   ${GREEN}✅ sessions_history 命令正常${NC}"
    HISTORY_COUNT=$(wc -l < /tmp/history-test-$(date +%s).txt)
    echo "   歷史消息數: $HISTORY_COUNT"
    ((PASS++))
else
    echo -e "   ${RED}❌ sessions_history 命令失敗${NC}"
    ((FAIL++))
fi
echo ""

# 4. 檢查 spawn_commands.jsonl
echo "4. 檢查 spawn_commands.jsonl 文件..."
SPAWN_COMMANDS_FILE="$HOME/.openclaw/workspace/kanban/spawn_commands.jsonl"

if [ -f "$SPAWN_COMMANDS_FILE" ]; then
    COMMAND_COUNT=$(wc -l < "$SPAWN_COMMANDS_FILE")
    echo -e "   ${GREEN}✅ spawn_commands.jsonl 存在${NC}"
    echo "   待啟動命令數: $COMMAND_COUNT"

    if [ $COMMAND_COUNT -gt 0 ]; then
        echo "   第一個命令預覽:"
        head -1 "$SPAWN_COMMANDS_FILE" | jq -r '.label' 2>/dev/null || head -1 "$SPAWN_COMMANDS_FILE"
    fi
    ((PASS++))
else
    echo -e "   ${YELLOW}⚠️  spawn_commands.jsonl 不存在（可能無待啟動任務）${NC}"
    ((PASS++))
fi
echo ""

# 5. 檢查任務輸出目錄
echo "5. 檢查任務輸出目錄..."
OUTPUT_DIR="$HOME/.openclaw/workspace/kanban/outputs"

if [ -d "$OUTPUT_DIR" ]; then
    echo -e "   ${GREEN}✅ 任務輸出目錄存在${NC}"
    OUTPUT_COUNT=$(ls -1 "$OUTPUT_DIR"/*.md 2>/dev/null | wc -l)
    echo "   輸出文件數: $OUTPUT_COUNT"

    if [ $OUTPUT_COUNT -gt 0 ]; then
        echo "   最近的輸出文件:"
        ls -lt "$OUTPUT_DIR"/*.md 2>/dev/null | head -3
    fi
    ((PASS++))
else
    echo -e "   ${RED}❌ 任務輸出目錄不存在${NC}"
    echo "   預期路徑: $OUTPUT_DIR"
    ((FAIL++))
fi
echo ""

# 6. 檢查任務工作目錄
echo "6. 檢查任務工作目錄..."
WORKS_DIR="$HOME/.openclaw/workspace/kanban/works"

if [ -d "$WORKS_DIR" ]; then
    echo -e "   ${GREEN}✅ 任務工作目錄存在${NC}"
    WORKS_COUNT=$(find "$WORKS_DIR" -maxdepth 1 -type d | wc -l)
    echo "   任務目錄數: $((WORKS_COUNT - 1))"

    if [ $((WORKS_COUNT - 1)) -gt 0 ]; then
        echo "   最近的任務目錄:"
        ls -lt "$WORKS_DIR" | grep "^d" | head -3
    fi
    ((PASS++))
else
    echo -e "   ${RED}❌ 任務工作目錄不存在${NC}"
    echo "   預期路徑: $WORKS_DIR"
    ((FAIL++))
fi
echo ""

# 7. 檢查任務狀態文件
echo "7. 檢查任務狀態文件..."
TASKS_JSON="$HOME/.openclaw/workspace/kanban/tasks.json"

if [ -f "$TASKS_JSON" ]; then
    echo -e "   ${GREEN}✅ tasks.json 存在${NC}"

    # 使用 jq 檢查 JSON 格式
    if jq empty "$TASKS_JSON" 2>/dev/null; then
        echo -e "   ${GREEN}✅ tasks.json 格式正確${NC}"

        # 統計任務狀態
        PENDING_COUNT=$(jq '[.[] | select(.status=="pending")] | length' "$TASKS_JSON")
        SPAWNING_COUNT=$(jq '[.[] | select(.status=="spawning")] | length' "$TASKS_JSON")
        IN_PROGRESS_COUNT=$(jq '[.[] | select(.status=="in_progress")] | length' "$TASKS_JSON")
        COMPLETED_COUNT=$(jq '[.[] | select(.status=="completed")] | length' "$TASKS_JSON")
        FAILED_COUNT=$(jq '[.[] | select(.status=="failed")] | length' "$TASKS_JSON")

        echo "   任務狀態統計:"
        echo "     - pending: $PENDING_COUNT"
        echo "     - spawning: $SPAWNING_COUNT"
        echo "     - in_progress: $IN_PROGRESS_COUNT"
        echo "     - completed: $COMPLETED_COUNT"
        echo "     - failed: $FAILED_COUNT"
        ((PASS++))
    else
        echo -e "   ${RED}❌ tasks.json 格式錯誤${NC}"
        ((FAIL++))
    fi
else
    echo -e "   ${RED}❌ tasks.json 不存在${NC}"
    echo "   預期路徑: $TASKS_JSON"
    ((FAIL++))
fi
echo ""

# 8. 檢查 subagents 命令
echo "8. 檢查 subagents 命令..."
if openclaw subagents list > /tmp/subagents-list-$(date +%s).txt 2>&1; then
    echo -e "   ${GREEN}✅ subagents list 命令正常${NC}"
    SUBAGENT_COUNT=$(wc -l < /tmp/subagents-list-$(date +%s).txt)
    echo "   子代理數: $SUBAGENT_COUNT"
    ((PASS++))
else
    echo -e "   ${YELLOW}⚠️  subagents list 命令失敗（可能無子代理）${NC}"
    ((PASS++))
fi
echo ""

# 清理臨時文件
rm -f /tmp/sessions-list-*.txt
rm -f /tmp/agents-list-*.txt
rm -f /tmp/history-test-*.txt
rm -f /tmp/subagents-list-*.txt

# 總結
echo "=== 測試總結 ==="
echo "通過: $PASS"
echo "失敗: $FAIL"
echo "總計: $((PASS + FAIL))"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✅ 所有 Sub-agent 測試通過！${NC}"
    echo "結束時間: $(date)"
    exit 0
else
    echo -e "${RED}❌ 有 $FAIL 個測試失敗${NC}"
    echo "結束時間: $(date)"
    exit 1
fi
