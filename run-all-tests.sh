#!/bin/bash
# run-all-tests.sh
# 主測試腳本 - 執行所有 Phase 3 測試

echo "=========================================="
echo "  OpenClaw 2026.3.3 升級測試套件"
echo "=========================================="
echo "開始時間: $(date)"
echo ""

# 設置顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 測試結果
RESULTS=()

# 測試目錄
TEST_DIR="$HOME/.openclaw/workspace"
cd "$TEST_DIR" || exit 1

# 測試 1：基本功能測試
echo -e "${BLUE}=== 測試 1：基本功能測試 ===${NC}"
./test-basic-functionality.sh
RESULT=$?
if [ $RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ 測試 1 通過${NC}"
    RESULTS+=("✅ 基本功能測試")
else
    echo -e "${RED}❌ 測試 1 失敗${NC}"
    RESULTS+=("❌ 基本功能測試")
fi
echo ""
read -p "按 Enter 繼續..."
echo ""

# 測試 2：Heartbeat 系統測試
echo -e "${BLUE}=== 測試 2：Heartbeat 系統測試 ===${NC}"
./test-heartbeat.sh
RESULT=$?
if [ $RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ 測試 2 通過${NC}"
    RESULTS+=("✅ Heartbeat 系統測試")
else
    echo -e "${RED}❌ 測試 2 失敗${NC}"
    RESULTS+=("❌ Heartbeat 系統測試")
fi
echo ""
read -p "按 Enter 繼續..."
echo ""

# 測試 3：Sub-agent 測試
echo -e "${BLUE}=== 測試 3：Sub-agent 測試 ===${NC}"
./test-subagent.sh
RESULT=$?
if [ $RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ 測試 3 通過${NC}"
    RESULTS+=("✅ Sub-agent 測試")
else
    echo -e "${RED}❌ 測試 3 失敗${NC}"
    RESULTS+=("❌ Sub-agent 測試")
fi
echo ""

# 總結
echo "=========================================="
echo "  測試總結"
echo "=========================================="
echo "結束時間: $(date)"
echo ""

echo "測試結果:"
for result in "${RESULTS[@]}"; do
    echo "  $result"
done
echo ""

# 統計
PASS_COUNT=$(echo "${RESULTS[@]}" | grep -c "✅" || echo "0")
FAIL_COUNT=$(echo "${RESULTS[@]}" | grep -c "❌" || echo "0")

echo "統計:"
echo "  通過: $PASS_COUNT"
echo "  失敗: $FAIL_COUNT"
echo "  總計: $((PASS_COUNT + FAIL_COUNT))"
echo ""

# 決策
if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "${GREEN}🎉 所有測試通過！${NC}"
    echo ""
    echo "下一步："
    echo "  1. 決定是否升級到 2026.3.3"
    echo "  2. 如果升級，執行生產環境升級"
    echo "  3. 如果不升級，保持當前版本"
    exit 0
else
    echo -e "${RED}⚠️  有 $FAIL_COUNT 個測試失敗${NC}"
    echo ""
    echo "下一步："
    echo "  1. 查看失敗測試的詳細日誌"
    echo "  2. 修復發現的問題"
    echo "  3. 重新運行失敗的測試"
    echo "  4. 如果無法修復，考慮不升級"
    exit 1
fi
