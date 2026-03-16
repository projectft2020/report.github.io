#!/bin/bash

# 自動部署「量化交易研究精選集 2026」到 GitHub Pages
# 使用方式：./deploy_to_github_pages.sh

set -e  # 遇到錯誤立即退出

# 顏色定義
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 路徑配置
PRODUCT_DIR="/Users/charlie/.openclaw/workspace/products/quant-research-bundle"
REPORT_DIR="/Users/charlie/report"
DEPLOY_SUBDIR="quant-research-bundle"
DEPLOY_PATH="${REPORT_DIR}/${DEPLOY_SUBDIR}"

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}🚀 開始部署量化交易研究精選集 2026${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

# 步驟 1：創建部署目錄
echo -e "${YELLOW}📁 步驟 1/5：創建部署目錄${NC}"
mkdir -p "${DEPLOY_PATH}"
echo -e "${GREEN}   ✅ 部署目錄已創建：${DEPLOY_PATH}${NC}"
echo ""

# 步驟 2：複製產品頁面
echo -e "${YELLOW}📄 步驟 2/5：複製產品頁面${NC}"
cp "${PRODUCT_DIR}/index.html" "${DEPLOY_PATH}/"
echo -e "${GREEN}   ✅ index.html 已複製${NC}"
echo ""

# 步驟 3：複製購買說明
echo -e "${YELLOW}📄 步驟 3/5：複製購買說明${NC}"
cp "${PRODUCT_DIR}/購買說明.md" "${DEPLOY_PATH}/"
echo -e "${GREEN}   ✅ 購買說明.md 已複製${NC}"
echo ""

# 步驟 4：提交到 Git
echo -e "${YELLOW}📤 步驟 4/5：提交到 Git${NC}"
cd "${REPORT_DIR}"

# 檢查是否有變更
if git diff --quiet && git diff --cached --quiet; then
    echo -e "${YELLOW}   ⚠️  沒有變更需要提交${NC}"
else
    git add "${DEPLOY_SUBDIR}/"
    git commit -m "新增：量化交易研究精選集 2026 產品頁面

- 產品頁面：index.html
- 購買說明：購買說明.md
- 部署路徑：/quant-research-bundle/
- 產品 URL：https://projectft2020.github.io/report/quant-research-bundle/"
    echo -e "${GREEN}   ✅ Git 提交完成${NC}"
fi
echo ""

# 步驟 5：推送到 GitHub
echo -e "${YELLOW}📤 步驟 5/5：推送到 GitHub${NC}"
git push origin main
echo -e "${GREEN}   ✅ 推送完成${NC}"
echo ""

# 完成
echo -e "${BLUE}============================================================${NC}"
echo -e "${GREEN}🎉 部署完成！${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""
echo -e "${GREEN}產品 URL：${NC}"
echo -e "   https://projectft2020.github.io/report/quant-research-bundle/"
echo ""
echo -e "${GREEN}下一步：${NC}"
echo -e "   1. 添加銀行帳號到「購買說明.md」"
echo -e "   2. 更新購買說明並重新推送"
echo -e "   3. 宣傳推廣（Threads、Telegram）"
echo ""
