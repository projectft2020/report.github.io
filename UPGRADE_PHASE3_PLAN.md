# Phase 3 測試環境驗證計劃

> **目標：** 在測試環境中驗證 OpenClaw 升級（2026.2.15 → 2026.3.3）的安全性
> **預計時間：** 1 週（5-7 個工作日）
> **風險等級：** 🟡 中等

---

## 📋 驗證準則

### 成功標準
- ✅ 所有高優先級測試通過
- ✅ Heartbeat 系統正常運作
- ✅ Sub-agent 啟動和執行正常
- ✅ 沒有重大 Breaking Changes 影響
- ✅ 回滾計劃驗證可行

### 失敗條件
- ❌ 高優先級測試失敗
- ❌ Heartbeat 系統受影響
- ❌ Sub-agent 無法正常執行
- ❌ 發現無法修復的 Breaking Changes
- ❌ 回滾無法執行

---

## 🏗️ 測試環境架構

### 選項 A：Docker 測試環境（推薦）

```bash
# 1. 創建測試 Docker 容器
docker run -it \
  --name openclaw-test-2026.3.3 \
  -v ~/.openclaw:/home/openclaw/.openclaw \
  -v ~/.openclaw/workspace:/workspace \
  node:22 \
  /bin/bash

# 2. 在容器中安裝 OpenClaw 2026.3.3
npm install -g openclaw@2026.3.3

# 3. 運行驗證測試
cd /workspace
./verify-upgrade.sh

# 4. 測試 Heartbeat
# 手動觸發心跳，檢查是否正常運作

# 5. 測試 Sub-agent
# 啟動一個測試任務，驗證 sub-agent 正常執行

# 6. 清理容器
# 如果驗證失敗，刪除容器，主環境不受影響
docker rm -f openclaw-test-2026.3.3
```

**優點：**
- 完全隔離，不影響主環境
- 易於清理，失敗後快速回滾
- 可重複驗證

**缺點：**
- 需要安裝 Docker
- 配置稍微複雜

---

### 選項 B：NVM 測試環境（備選）

```bash
# 1. 創建測試 Node 版本
nvm install 22
nvm use 22

# 2. 創建測試目錄
mkdir -p ~/openclaw-test-2026.3.3
cd ~/openclaw-test-2026.3.3

# 3. 初始化測試配置
cp -r ~/.openclaw/workspace ./workspace
cp -r ~/.openclaw/memory ./memory

# 4. 安裝 OpenClaw 2026.3.3（本地安裝）
npm install openclaw@2026.3.3

# 5. 運行驗證測試
cd workspace
./kanban-ops/verify-upgrade.sh

# 6. 測試 Heartbeat 和 Sub-agent
# 手動測試

# 7. 清理
# 如果驗證失敗，刪除測試目錄
rm -rf ~/openclaw-test-2026.3.3
```

**優點：**
- 不需要 Docker
- 配置簡單

**缺點：**
- 與主環境共享 Node，可能互相影響
- 清理不徹底

---

## 📝 驗證清單

### 高優先級測試（必須通過）

| # | 測試項目 | 描述 | 預期結果 | 狀態 |
|---|---------|------|---------|------|
| 1 | 基本安裝 | 成功安裝 OpenClaw 2026.3.3 | 版本顯示 2026.3.3 | ⏸️ 待執行 |
| 2 | 系統啟動 | Gateway 成功啟動 | 無錯誤日誌 | ⏸️ 待執行 |
| 3 | 配置加載 | 正確加載配置文件 | 無警告 | ⏸️ 待執行 |
| 4 | Heartbeat 觸發 | 心跳正常觸發 | 識別並執行 | ⏸️ 待執行 |
| 5 | Sub-agent 啟動 | 成功啟動研究任務 | 任務正常執行 | ⏸️ 待執行 |
| 6 | 研究任務完成 | 研究任務成功完成 | 輸出正確 | ⏸️ 待執行 |

### 中優先級測試（建議通過）

| # | 測試項目 | 描述 | 預期結果 | 狀態 |
|---|---------|------|---------|------|
| 7 | Breaking Checks | 驗證 Breaking Checks 影響 | 無影響或可修復 | ⏸️ 待執行 |
| 8 | 背壓機制 | 背壓機制正常運作 | 健康度監控正常 | ⏸️ 待執行 |
| 9 | 任務回滾 | 任務回滾機制正常 | 自動回滾成功 | ⏸️ 待執行 |
| 10 | Scout 系統 | Scout 掃描正常 | 數據源掃描成功 | ⏸️ 待執行 |

### 低優先級測試（可選）

| # | 測試項目 | 描述 | 預期結果 | 狀態 |
|---|---------|------|---------|------|
| 11 | QMD 檢索 | QMD 語義檢索 | 檢索結果正常 | ⏸️ 待執行 |
| 12 | Dashboard 連接 | Dashboard API 連接 | API 響應正常 | ⏸️ 待執行 |

---

## 🧪 測試腳本

### 測試腳本 1：基本功能測試

```bash
#!/bin/bash
# test-basic-functionality.sh

echo "=== OpenClaw 基本功能測試 ==="

# 1. 檢查版本
echo "1. 檢查版本..."
VERSION=$(openclaw --version)
echo "   當前版本: $VERSION"
if [ "$VERSION" = "2026.3.3" ]; then
    echo "   ✅ 版本正確"
else
    echo "   ❌ 版本不正確（預期：2026.3.3，實際：$VERSION）"
    exit 1
fi

# 2. 檢查 Gateway 狀態
echo "2. 檢查 Gateway 狀態..."
openclaw gateway status
if [ $? -eq 0 ]; then
    echo "   ✅ Gateway 狀態正常"
else
    echo "   ❌ Gateway 狀態異常"
    exit 1
fi

# 3. 檢查配置加載
echo "3. 檢查配置加載..."
openclaw gateway config.get > /tmp/config-check.json
if [ $? -eq 0 ]; then
    echo "   ✅ 配置加載成功"
else
    echo "   ❌ 配置加載失敗"
    exit 1
fi

echo "=== 所有基本功能測試通過 ==="
```

---

### 測試腳本 2：Heartbeat 測試

```bash
#!/bin/bash
# test-heartbeat.sh

echo "=== Heartbeat 系統測試 ==="

# 1. 發送心跳測試消息
echo "1. 發送心跳測試消息..."
echo "HEARTBEAT_TEST" | openclaw session send --to main
if [ $? -eq 0 ]; then
    echo "   ✅ 心跳消息發送成功"
else
    echo "   ❌ 心跳消息發送失敗"
    exit 1
fi

# 2. 等待心跳響應（30 秒）
echo "2. 等待心跳響應..."
sleep 30

# 3. 檢查心跳日誌
echo "3. 檢查心跳日誌..."
LOGS=$(openclaw gateway logs --tail 50 | grep -i "heartbeat")
if [ -n "$LOGS" ]; then
    echo "   ✅ 心跳日誌正常"
    echo "   日誌：$LOGS"
else
    echo "   ⚠️  未找到心跳日誌"
fi

echo "=== Heartbeat 系統測試完成 ==="
```

---

### 測試腳本 3：Sub-agent 測試

```bash
#!/bin/bash
# test-subagent.sh

echo "=== Sub-agent 測試 ==="

# 1. 啟動一個測試研究任務
echo "1. 啟動測試研究任務..."
TASK_ID="test-subagent-$(date +%s)"

# 創建測試任務
cat > /tmp/test-task.json << EOF
{
  "title": "測試任務：驗證 Sub-agent 功能",
  "agent": "research",
  "description": "這是一個測試任務，用於驗證 sub-agent 在 2026.3.3 版本下能否正常啟動和執行。",
  "task": "請總結 OpenClaw 2026.3.3 版本的主要更新內容。"
}
EOF

# 啟動任務（通過 sessions_send）
openclaw session send --to main < /tmp/test-task.json
if [ $? -eq 0 ]; then
    echo "   ✅ 測試任務啟動成功"
else
    echo "   ❌ 測試任務啟動失敗"
    exit 1
fi

# 2. 等待任務完成（5 分鐘）
echo "2. 等待任務完成（最多 5 分鐘）..."
for i in {1..60}; do
    STATUS=$(openclaw sessions list | grep "$TASK_ID" | awk '{print $3}')
    if [ "$STATUS" = "completed" ]; then
        echo "   ✅ 任務完成"
        break
    fi
    sleep 5
done

# 3. 檢查任務輸出
echo "3. 檢查任務輸出..."
OUTPUT=$(ls -la ~/.openclaw/workspace/kanban/outputs/ | grep "$TASK_ID")
if [ -n "$OUTPUT" ]; then
    echo "   ✅ 任務輸出正常"
    echo "   輸出：$OUTPUT"
else
    echo "   ❌ 未找到任務輸出"
    exit 1
fi

echo "=== Sub-agent 測試完成 ==="
```

---

## 🔄 回滾計劃

### 回滾觸發條件

如果以下任何一個條件滿足，立即回滾：
1. 任何高優先級測試失敗
2. Heartbeat 系統受影響
3. Sub-agent 無法正常執行
4. 發現無法修復的 Breaking Changes

### 回滾步驟

```bash
# 1. 停止測試環境（如果是 Docker）
docker stop openclaw-test-2026.3.3
docker rm openclaw-test-2026.3.3

# 或（如果是 NVM）
# 刪除測試目錄
rm -rf ~/openclaw-test-2026.3.3

# 2. 驗證主環境未受影響
openclaw --version  # 應該顯示 2026.2.15
openclaw gateway status  # 應該顯示正常

# 3. 恢復主環境（如果受影響）
nvm use 22
npm install -g openclaw@2026.2.15
openclaw gateway restart

# 4. 驗證主環境恢復
openclaw --version  # 應該顯示 2026.2.15
./kanban-ops/verify-upgrade.sh  # 應該通過
```

### 回滾驗證清單

| # | 驗證項目 | 描述 | 預期結果 | 狀態 |
|---|---------|------|---------|------|
| 1 | 版本回滾 | 版本恢復到 2026.2.15 | 版本顯示 2026.2.15 | ⏸️ 待驗證 |
| 2 | Gateway 恢復 | Gateway 正常運作 | 無錯誤日誌 | ⏸️ 待驗證 |
| 3 | Heartbeat 恢復 | Heartbeat 正常觸發 | 心跳日誌正常 | ⏸️ 待驗證 |
| 4 | Sub-agent 恢復 | Sub-agent 正常執行 | 任務正常完成 | ⏸️ 待驗證 |

---

## 📊 決策矩陣

### 升級 vs 不升級

| 因素 | 升級 | 不升級 | 權重 |
|------|------|--------|------|
| 新功能價值 | 中等（修復關鍵 bug） | 低（錯過改進） | 0.3 |
| 風險程度 | 中等（Breaking Checks） | 無風險 | 0.4 |
| 測試成本 | 1 週 | 0 | 0.2 |
| 維護成本 | 降低（跟上更新） | 增加（版本差距） | 0.1 |
| **總分** | **0.3** | **0.4** | **1.0** |

**初步結論：不升級（分數更高）**

---

## 📅 時間表

### Day 1：環境準備
- [ ] 選擇測試環境（Docker / NVM）
- [ ] 準備測試腳本
- [ ] 備份主環境配置

### Day 2-3：基本功能測試
- [ ] 安裝 OpenClaw 2026.3.3
- [ ] 運行基本功能測試
- [ ] 運行 verify-upgrade.sh

### Day 4-5：集成測試
- [ ] Heartbeat 系統測試
- [ ] Sub-agent 測試
- [ ] Breaking Checks 驗證

### Day 6：問題修復
- [ ] 修復發現的問題
- [ ] 重新運行失敗的測試
- [ ] 記錄問題和解決方案

### Day 7：決策和文檔
- [ ] 總結測試結果
- [ ] 製作決策報告
- [ ] 更新 UPGRADE_PLAN.md

---

## 📝 測試日誌模板

```markdown
## 測試日誌 - [日期]

### 環境
- 測試環境：[Docker / NVM]
- OpenClaw 版本：2026.3.3
- Node 版本：22.x.x
- 測試人員：[名字]

### 執行的測試

| 測試項目 | 狀態 | 開始時間 | 結束時間 | 備註 |
|---------|------|---------|---------|------|
| 基本安裝 | ✅ / ❌ | HH:MM | HH:MM | [備註] |
| 系統啟動 | ✅ / ❌ | HH:MM | HH:MM | [備註] |
| ... | ... | ... | ... | ... |

### 發現的問題

| 問題 | 嚴重程度 | 狀態 | 解決方案 |
|------|---------|------|---------|
| [描述] | 高/中/低 | 開啟/修復/關閉 | [解決方案] |

### 決策
- [ ] 升級到 2026.3.3
- [ ] 保持當前版本（2026.2.15）
- [ ] 推遲升級，等待穩定版

### 備註
[其他觀察和建議]
```

---

## 🎯 成功標準總結

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

**文檔版本：** v1.0
**創建時間：** 2026-03-06 02:15
**預計完成時間：** 2026-03-13（1 週）
**維護者：** Charlie
