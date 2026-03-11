#!/bin/bash
# test-basic-functionality.sh
# OpenClaw 基本功能測試腳本
# 用於驗證 OpenClaw 2026.3.3 基本功能

echo "=== OpenClaw 基本功能測試 ==="
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

# 1. 檢查版本
echo "1. 檢查版本..."
VERSION=$(openclaw --version 2>&1 | head -1)
echo "   當前版本: $VERSION"

if echo "$VERSION" | grep -q "2026.3.3"; then
    echo -e "   ${GREEN}✅ 版本正確${NC}"
    ((PASS++))
else
    echo -e "   ${RED}❌ 版本不正確（預期：2026.3.3，實際：$VERSION）${NC}"
    ((FAIL++))
fi
echo ""

# 2. 檢查 Gateway 狀態
echo "2. 檢查 Gateway 狀態..."
if openclaw gateway status > /dev/null 2>&1; then
    echo -e "   ${GREEN}✅ Gateway 狀態正常${NC}"
    ((PASS++))
else
    echo -e "   ${RED}❌ Gateway 狀態異常${NC}"
    ((FAIL++))
fi
echo ""

# 3. 檢查配置加載
echo "3. 檢查配置加載..."
CONFIG_FILE="/tmp/config-check-$(date +%s).json"
if openclaw gateway config.get > "$CONFIG_FILE" 2>&1; then
    if [ -s "$CONFIG_FILE" ]; then
        echo -e "   ${GREEN}✅ 配置加載成功${NC}"
        echo "   配置大小: $(wc -c < "$CONFIG_FILE") bytes"
        ((PASS++))
    else
        echo -e "   ${RED}❌ 配置文件為空${NC}"
        ((FAIL++))
    fi
else
    echo -e "   ${RED}❌ 配置加載失敗${NC}"
    ((FAIL++))
fi
echo ""

# 4. 檢查會話列表
echo "4. 檢查會話列表..."
if openclaw sessions list > /dev/null 2>&1; then
    SESSION_COUNT=$(openclaw sessions list | grep -c "agent:" || echo "0")
    echo -e "   ${GREEN}✅ 會話列表正常${NC}"
    echo "   活躍會話數: $SESSION_COUNT"
    ((PASS++))
else
    echo -e "   ${RED}❌ 會話列表異常${NC}"
    ((FAIL++))
fi
echo ""

# 5. 檢查工具可用性
echo "5. 檢查工具可用性..."
TOOLS_MISSING=0

# 檢查關鍵工具
for tool in read write exec web_search web_fetch; do
    if ! openclaw help | grep -q "$tool"; then
        echo -e "   ${RED}   ❌ 工具 $tool 不可用${NC}"
        ((TOOLS_MISSING++))
    fi
done

if [ $TOOLS_MISSING -eq 0 ]; then
    echo -e "   ${GREEN}✅ 關鍵工具可用${NC}"
    ((PASS++))
else
    echo -e "   ${RED}❌ $TOOLS_MISSING 個工具不可用${NC}"
    ((FAIL++))
fi
echo ""

# 6. 檢查日誌系統
echo "6. 檢查日誌系統..."
if openclaw gateway logs --tail 10 > /tmp/logs-check-$(date +%s).txt 2>&1; then
    echo -e "   ${GREEN}✅ 日誌系統正常${NC}"
    ((PASS++))
else
    echo -e "   ${RED}❌ 日誌系統異常${NC}"
    ((FAIL++))
fi
echo ""

# 清理臨時文件
rm -f /tmp/config-check-*.json
rm -f /tmp/logs-check-*.txt

# 總結
echo "=== 測試總結 ==="
echo "通過: $PASS"
echo "失敗: $FAIL"
echo "總計: $((PASS + FAIL))"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✅ 所有基本功能測試通過！${NC}"
    echo "結束時間: $(date)"
    exit 0
else
    echo -e "${RED}❌ 有 $FAIL 個測試失敗${NC}"
    echo "結束時間: $(date)"
    exit 1
fi
