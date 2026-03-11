# Phase 3 測試環境驗證 - 快速開始指南

> **目標：** 在隔離的 Docker 環境中驗證 OpenClaw 2026.3.3 的升級安全性
> **預計時間：** 1-2 小時（首次設置） + 30 分鐘（測試執行）
> **風險等級：** 🟡 中等（但完全隔離，不影響主環境）

---

## 📦 環境準備（已完成）

✅ Docker 已安裝（v29.2.0）
✅ 主環境已備份（7.4GB → `~/openclaw-backup-20260306/`）
✅ 測試腳本已創建（5 個腳本）

---

## 🚀 快速開始（3 步）

### 步驟 1：創建 Docker 測試環境

```bash
cd ~/.openclaw/workspace
./setup-docker-test.sh
```

這將會：
1. 檢查 Docker 安裝
2. 檢查現有容器
3. 驗證備份
4. 創建名為 `openclaw-test-2026.3.3` 的 Docker 容器
5. 在容器中安裝 OpenClaw 2026.3.3
6. 驗證安裝

**預計時間：** 5-10 分鐘（首次安裝）

---

### 步驟 2：進入容器並運行測試

```bash
# 進入容器
docker exec -it openclaw-test-2026.3.3 /bin/bash

# 在容器中運行測試
cd /workspace
./run-all-tests.sh
```

這將會：
1. 運行基本功能測試（6 個測試）
2. 運行 Heartbeat 系統測試（7 個測試）
3. 運行 Sub-agent 測試（8 個測試）
4. 生成測試總結
5. 提供下一步建議

**預計時間：** 10-20 分鐘

---

### 步驟 3：查看結果並決策

測試完成後，你會看到：

**✅ 如果所有測試通過：**
```
🎉 所有測試通過！

下一步：
  1. 決定是否升級到 2026.3.3
  2. 如果升級，執行生產環境升級
  3. 如果不升級，保持當前版本
```

**⚠️ 如果有測試失敗：**
```
⚠️  有 X 個測試失敗

下一步：
  1. 查看失敗測試的詳細日誌
  2. 修復發現的問題
  3. 重新運行失敗的測試
  4. 如果無法修復，考慮不升級
```

---

## 📋 測試說明

### 測試 1：基本功能測試（6 個測試）

1. **檢查版本** - 驗證安裝的是 2026.3.3
2. **檢查 Gateway 狀態** - 驗證 Gateway 正常運作
3. **檢查配置加載** - 驗證配置文件正確加載
4. **檢查會話列表** - 驗證會話管理功能
5. **檢查工具可用性** - 驗證關鍵工具可用
6. **檢查日誌系統** - 驗證日誌記錄功能

### 測試 2：Heartbeat 系統測試（7 個測試）

1. **檢查 HEARTBEAT.md 文件** - 驗證心跳配置存在
2. **檢查 auto_spawn_heartbeat.py 腳本** - 驗證自動啟動腳本存在
3. **執行 auto_spawn_heartbeat.py** - 驗證自動啟動功能
4. **檢查背壓機制** - 驗證背壓機制運作
5. **檢查任務狀態回滾機制** - 驗證回滾機制運作
6. **檢查任務同步機制** - 驗證任務同步功能
7. **檢查 Gateway 日誌中的 Heartbeat 記錄** - 驗證心跳日誌

### 測試 3：Sub-agent 測試（8 個測試）

1. **檢查 sessions_list 命令** - 驗證會話列表功能
2. **檢查可用 agent 列表** - 驗證代理列表功能
3. **檢查會話歷史功能** - 驗證歷史記錄功能
4. **檢查 spawn_commands.jsonl** - 驗證啟動命令文件
5. **檢查任務輸出目錄** - 驗證輸出目錄存在
6. **檢查任務工作目錄** - 驗證工作目錄存在
7. **檢查任務狀態文件** - 驗證任務狀態記錄
8. **檢查 subagents 命令** - 驗證子代理管理功能

---

## 🔧 常用命令

### Docker 容器管理

```bash
# 進入容器
docker exec -it openclaw-test-2026.3.3 /bin/bash

# 查看容器日誌
docker logs openclaw-test-2026.3.3

# 停止容器
docker stop openclaw-test-2026.3.3

# 啟動容器
docker start openclaw-test-2026.3.3

# 刪除容器（如果測試失敗，需要重建）
docker rm -f openclaw-test-2026.3.3
```

### 單獨運行測試

```bash
# 在容器中
cd /workspace

# 只運行基本功能測試
./test-basic-functionality.sh

# 只運行 Heartbeat 測試
./test-heartbeat.sh

# 只運行 Sub-agent 測試
./test-subagent.sh
```

### 查看測試日誌

```bash
# 在容器中
cd /workspace
cat phase3-test-log.md
```

---

## 🆘 故障排除

### 問題 1：Docker 容器無法啟動

**症狀：**
```
docker: Error response from daemon: ...
```

**解決方案：**
```bash
# 檢查 Docker 狀態
docker info

# 重啟 Docker
sudo systemctl restart docker  # Linux
# 或
open -a Docker  # macOS
```

---

### 問題 2：npm install 失敗

**症狀：**
```
npm ERR! code ECONNREFUSED
npm ERR! syscall connect
```

**解決方案：**
```bash
# 檢查網絡連接
ping registry.npmjs.org

# 使用 npm 鏡像
npm config set registry https://registry.npmmirror.com

# 重新安裝
npm install -g openclaw@2026.3.3
```

---

### 問題 3：測試腳本無法執行

**症狀：**
```
zsh: permission denied: ./test-basic-functionality.sh
```

**解決方案：**
```bash
# 在容器中
chmod +x /workspace/test-*.sh
```

---

### 問題 4：Gateway 啟動失敗

**症狀：**
```
❌ Gateway 狀態異常
```

**解決方案：**
```bash
# 在容器中
openclaw gateway logs --tail 50

# 檢查配置
openclaw gateway config.get

# 重啟 Gateway
openclaw gateway restart
```

---

## 📊 成功標準

### 最低要求（必須滿足）
- ✅ 所有高優先級測試通過（6 個）
- ✅ Heartbeat 系統正常運作
- ✅ Sub-agent 正常執行
- ✅ 無無法修復的 Breaking Changes

### 理想標準（建議滿足）
- ✅ 中優先級測試通過（至少 3 個）
- ✅ 回滾計劃驗證可行
- ✅ 測試文檔完整

---

## 🔄 回滾計劃

### 如果測試失敗，回滾步驟：

```bash
# 1. 停止並刪除測試容器
docker stop openclaw-test-2026.3.3
docker rm -f openclaw-test-2026.3.3

# 2. 驗證主環境未受影響
openclaw --version  # 應該顯示 2026.2.15
openclaw gateway status  # 應該顯示正常

# 3. 如果主環境受影響，恢復備份
# 備份已保存至：~/openclaw-backup-20260306/.openclaw
# 但通常不需要，因為測試環境完全隔離
```

---

## 📝 文檔

- **詳細測試計劃：** `UPGRADE_PHASE3_PLAN.md`
- **測試日誌：** `phase3-test-log.md`
- **Mentor 評估報告：** `kanban/outputs/mentor-openclaw-upgrade-assessment.md`

---

## ⏱️ 時間估算

| 步驟 | 任務 | 預計時間 |
|------|------|---------|
| 1 | 創建 Docker 測試環境 | 5-10 分鐘 |
| 2 | 進入容器 | < 1 分鐘 |
| 3 | 運行基本功能測試 | 2-3 分鐘 |
| 4 | 運行 Heartbeat 測試 | 3-5 分鐘 |
| 5 | 運行 Sub-agent 測試 | 2-3 分鐘 |
| 6 | 查看結果並決策 | 5-10 分鐘 |
| **總計** | **首次測試** | **20-35 分鐘** |

---

**文檔版本：** v1.0
**創建時間：** 2026-03-06 02:45 GMT+8
**維護者：** Charlie
