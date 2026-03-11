#!/bin/bash
# setup-docker-test.sh
# Docker 測試環境設置腳本
# 用於創建隔離的 OpenClaw 2026.3.3 測試環境

echo "=========================================="
echo "  Docker 測試環境設置"
echo "  OpenClaw 2026.3.3"
echo "=========================================="
echo "開始時間: $(date)"
echo ""

# 設置顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 容器名稱
CONTAINER_NAME="openclaw-test-2026.3.3"

# 檢查 Docker 是否安裝
echo -e "${BLUE}步驟 1：檢查 Docker${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker 未安裝${NC}"
    echo "請先安裝 Docker：https://www.docker.com/get-started"
    exit 1
fi

DOCKER_VERSION=$(docker --version)
echo -e "${GREEN}✅ Docker 已安裝${NC}"
echo "版本: $DOCKER_VERSION"
echo ""

# 檢查容器是否已存在
echo -e "${BLUE}步驟 2：檢查現有容器${NC}"
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${YELLOW}⚠️  容器 $CONTAINER_NAME 已存在${NC}"
    echo ""
    read -p "是否刪除現有容器並重建？(y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "刪除現有容器..."
        docker rm -f "$CONTAINER_NAME"
        echo -e "${GREEN}✅ 容器已刪除${NC}"
    else
        echo "退出設置..."
        exit 0
    fi
else
    echo -e "${GREEN}✅ 沒有現有容器${NC}"
fi
echo ""

# 檢查備份目錄
echo -e "${BLUE}步驟 3：檢查備份${NC}"
BACKUP_DIR="$HOME/openclaw-backup-$(date +%Y%m%d)"
if [ -d "$BACKUP_DIR/.openclaw" ]; then
    BACKUP_SIZE=$(du -sh "$BACKUP_DIR/.openclaw" | cut -f1)
    echo -e "${GREEN}✅ 備份已找到${NC}"
    echo "備份路徑: $BACKUP_DIR/.openclaw"
    echo "備份大小: $BACKUP_SIZE"
else
    echo -e "${YELLOW}⚠️  備份目錄不存在${NC}"
    echo "建議先備份："
    echo "  mkdir -p ~/openclaw-backup-\$(date +%Y%m%d)"
    echo "  cp -r ~/.openclaw ~/openclaw-backup-\$(date +%Y%m%d)/.openclaw"
    echo ""
    read -p "是否繼續而不備份？(不建議) (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "退出設置..."
        exit 0
    fi
fi
echo ""

# 創建 Docker 容器
echo -e "${BLUE}步驟 4：創建 Docker 容器${NC}"
echo "容器名稱: $CONTAINER_NAME"
echo "鏡像: node:22"
echo ""

docker run -it \
  --name "$CONTAINER_NAME" \
  -v ~/.openclaw:/home/openclaw/.openclaw:ro \
  -v ~/.openclaw/workspace:/workspace:rw \
  -v "$HOME/.npm:/home/openclaw/.npm" \
  -w /workspace \
  node:22 \
  /bin/bash << 'EOF'

echo ""
echo "=========================================="
echo "  容器內部設置"
echo "=========================================="
echo "開始時間: $(date)"
echo ""

# 檢查 Node 版本
echo "步驟 1：檢查 Node 版本"
NODE_VERSION=$(node --version)
NPM_VERSION=$(npm --version)
echo "Node 版本: $NODE_VERSION"
echo "NPM 版本: $NPM_VERSION"
echo ""

# 檢查工作目錄
echo "步驟 2：檢查工作目錄"
echo "當前目錄: $(pwd)"
echo "工作目錄內容:"
ls -la /workspace | head -10
echo ""

# 安裝 OpenClaw 2026.3.3
echo "步驟 3：安裝 OpenClaw 2026.3.3"
echo "這可能需要幾分鐘..."
npm install -g openclaw@2026.3.3

# 檢查安裝
echo ""
echo "步驟 4：檢查 OpenClaw 安裝"
if command -v openclaw &> /dev/null; then
    OPENCLAW_VERSION=$(openclaw --version 2>&1 | head -1)
    echo "✅ OpenClaw 安裝成功"
    echo "版本: $OPENCLAW_VERSION"
else
    echo "❌ OpenClaw 安裝失敗"
    exit 1
fi
echo ""

# 檢查 Gateway 配置
echo "步驟 5：檢查 Gateway 配置"
if [ -f ~/.openclaw/gateway/config.json ]; then
    echo "✅ Gateway 配置文件存在"
    echo "配置路徑: ~/.openclaw/gateway/config.json"
else
    echo "⚠️  Gateway 配置文件不存在"
    echo "這可能是因為 ~/.openclaw 被掛載為只讀"
fi
echo ""

# 創建測試腳本目錄
echo "步驟 6：準備測試腳本"
if [ -d /workspace ]; then
    echo "✅ 工作目錄可寫"
    echo "測試腳本:"
    ls -la /workspace/test-*.sh 2>/dev/null | head -5
else
    echo "❌ 工作目錄不可寫"
    exit 1
fi
echo ""

# 總結
echo "=========================================="
echo "  容器設置完成"
echo "=========================================="
echo "結束時間: $(date)"
echo ""
echo "環境信息:"
echo "  容器名稱: $CONTAINER_NAME"
echo "  Node 版本: $NODE_VERSION"
echo "  NPM 版本: $NPM_VERSION"
echo "  OpenClaw 版本: $OPENCLAW_VERSION"
echo ""
echo "下一步:"
echo "  1. 在容器中運行測試: ./run-all-tests.sh"
echo "  2. 查看測試結果"
echo "  3. 退出容器: exit"
echo ""
echo "容器外部命令:"
echo "  重新進入容器: docker exec -it $CONTAINER_NAME /bin/bash"
echo "  停止容器: docker stop $CONTAINER_NAME"
echo "  啟動容器: docker start $CONTAINER_NAME"
echo "  刪除容器: docker rm -f $CONTAINER_NAME"
echo ""

EOF

echo ""
echo -e "${GREEN}✅ Docker 容器設置完成${NC}"
echo ""
echo "容器信息:"
echo "  名稱: $CONTAINER_NAME"
echo "  狀態: $(docker ps -a --filter "name=$CONTAINER_NAME" --format '{{.Status}}')"
echo ""
echo "下一步:"
echo "  1. 進入容器: docker exec -it $CONTAINER_NAME /bin/bash"
echo "  2. 運行測試: cd /workspace && ./run-all-tests.sh"
echo "  3. 查看結果"
echo ""
