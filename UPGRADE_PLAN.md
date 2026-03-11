# OpenClaw 升級計劃

## 版本資訊
- 當前版本: 2026.2.15
- 目標版本: 2026.3.3
- 版本差距: 11 個版本（2026.2.17, 2026.2.19, 2026.2.21-26, 2026.3.1-3）
- 升級策略: 相容準備 → 測試環境驗證 → 生產環境更新
- 創建時間: 2026-03-06 01:05

## 系統盤點結果（Phase 1 完成）

### 代碼規模
- Python 腳本: 64 個
- 總代碼行數: 19,276 行
- 技能文檔: 29 個

### 關鍵依賴檢查
- ✅ 不使用 `host=node` 執行批准
- ✅ 不使用 `registerHttpHandler` (舊 Plugin SDK API)
- ✅ 不使用 Docker `network: "container:<id>"` 模式
- ✅ 不使用 Zalo 插件
- ⚠️ 心跳系統高度自定化，可能受 DM 遞送策略影響
- ❓ ACP 路由未使用（僅在文檔中提及）

### Heartbeat 系統依賴
```bash
# 心跳核心腳本
- kanban-ops/auto_spawn_heartbeat.py（自動任務啟動器）
- kanban-ops/task_state_rollback.py（狀態回滾檢查）
- kanban-ops/error_recovery.py（錯誤恢復）
- kanban-ops/task_cleanup.py（失敗任務清理）
- kanban-ops/task_sync.py（任務同步）
- kanban-ops/monitor_and_refill.py（監控和補充）

# 背壓機制
- kanban-ops/backpressure.py（背壓檢查和調整）

# 配置文件
- HEARTBEAT.md（心跳任務定義）
```

---

## Breaking Checks 影響評估

### 🔴 高影響 Breaking Changes

#### 1. Heartbeat DM 遞送策略變更
**版本**: 2026.2.24
**變更內容**:
```
BREAKING: Heartbeat direct/DM delivery default is now "allow" again.
BREAKING: Heartbeat delivery now blocks direct/DM targets when destination
parsing identifies a direct chat (for example user:<id>, Telegram user chat IDs,
or WhatsApp direct numbers/JIDs).
```

**我們的系統**:
- 心跳通過 HEARTBEAT.md 配置
- 主要在 webchat 頻道運作（非 DM）
- 使用 `sessions_spawn` 啟動子代理（不依賴 DM 遞送）

**影響評估**:
- 🟡 **中等影響**: 如果心跳在 DM 中運作，會被阻止
- 🟢 **低影響**: 我們主要在 webchat 運作，DM 遞送變更影響有限

**應對措施**:
```bash
# 1. 檢查當前心跳頻道
# 我們在 webchat，影響較小

# 2. 準備配置（如果需要）
{
  "agents": {
    "defaults": {
      "heartbeat": {
        "directPolicy": "block"  // 保持舊行為（如果需要）
      }
    }
  }
}

# 3. 測試驗證（Phase 3）
# 確認心跳在 webchat 運作正常
```

#### 2. Node 執行批准載荷變更
**版本**: 2026.2.x
**變更內容**:
```
BREAKING: Node exec approval payloads now require systemRunPlan.
host=node approval requests without that plan are rejected.
```

**我們的系統**:
- ✅ 不使用 `host=node` 執行
- ✅ 所有腳本在本地執行（host=sandbox）

**影響評估**:
- 🟢 **無影響**

#### 3. Node system.run 路徑解析變更
**版本**: 2026.2.x
**變更內容**:
```
BREAKING: Node system.run execution now pins path-token commands to the
canonical executable path (realpath).
```

**我們的系統**:
- ✅ 主要使用完整路徑（如 `/usr/bin/python3`）
- ✅ 很少使用簡寫命令

**影響評估**:
- 🟢 **低影響**: 可能需要檢查幾個腳本

**應對措施**:
```bash
# 檢查是否有簡寫命令
cd ~/.openclaw/workspace/kanban-ops
grep -r "tr \|grep \|awk " --include="*.py" | head -10
```

### 🟡 中等影響 Breaking Changes

#### 4. ACP 路由默認啟用
**版本**: 2026.2.x
**變更內容**:
```
BREAKING: ACP dispatch now defaults to enabled unless explicitly disabled
(acp.dispatch.enabled=false).
```

**我們的系統**:
- ✅ 不使用 ACP（Agent Control Protocol）
- ✅ 僅在文檔中提及（TURBO_MODE_V2_OPTIONS.md）
- ✅ 使用 `sessions_spawn` 進行子代理通信

**影響評估**:
- 🟢 **無影響**: ACP 未啟用，默認值變更無影響

#### 5. Docker 容器命名空間默認阻止
**版本**: 2026.2.x
**變更內容**:
```
BREAKING: Security/Sandbox: block Docker network: "container:<id>"
namespace-join mode by default.
```

**我們的系統**:
- ✅ 不使用 Docker `network: "container:<id>"` 模式
- ✅ Dashboard 使用獨立 Docker 網絡

**影響評估**:
- 🟢 **無影響**

### 🟢 低影響 Breaking Changes

#### 6. 工具配置默認值變更
**版本**: 2026.2.x
**變更內容**:
```
BREAKING: Onboarding now defaults tools.profile to "messaging"
for new local installs.
```

**我們的系統**:
- ✅ 系統已安裝（非新安裝）
- ✅ 當前工具配置保持不變

**影響評估**:
- 🟢 **無影響**

#### 7. Plugin SDK API 移除
**版本**: 2026.2.x
**變更內容**:
```
BREAKING: Plugin SDK removed api.registerHttpHandler(...).
Plugins must register explicit HTTP routes via api.registerHttpRoute(...).
```

**我們的系統**:
- ✅ 不使用 `registerHttpHandler`
- ✅ 無自定義插件

**影響評估**:
- 🟢 **無影響**

#### 8. Zalo 插件依賴移除
**版本**: 2026.2.x
**變更內容**:
```
BREAKING: Zalo Personal plugin no longer depends on external zca-compatible
CLI binaries.
```

**我們的系統**:
- ✅ 不使用 Zalo 插件
- ✅ 不使用 Zalo 相關功能

**影響評估**:
- 🟢 **無影響**

---

## Breaking Checks 總結

| Breaking Change | 版本 | 我們受影響？ | 風險等級 | 應對措施 |
|----------------|------|-------------|----------|----------|
| Heartbeat DM 遞送 | 2026.2.24 | ⚠️ 可能受影響 | 🟡 中等 | 測試驗證 |
| Node exec 載荷 | 2026.2.x | ❌ 不受影響 | 🟢 無 | 無需操作 |
| Node system.run 路徑 | 2026.2.x | ⚠️ 可能受影響 | 🟢 低 | 檢查簡寫命令 |
| ACP 路由默認 | 2026.2.x | ❌ 不受影響 | 🟢 無 | 無需操作 |
| Docker 網絡 | 2026.2.x | ❌ 不受影響 | 🟢 無 | 無需操作 |
| tools.profile 默認 | 2026.2.x | ❌ 不受影響 | 🟢 無 | 無需操作 |
| Plugin SDK API | 2026.2.x | ❌ 不受影響 | 🟢 無 | 無需操作 |
| Zalo 插件 | 2026.2.x | ❌ 不受影響 | 🟢 無 | 無需操作 |

**總體風險評估**:
- 🔴 高風險: 0 個
- 🟡 中等風險: 1 個（Heartbeat DM 遞送）
- 🟢 低風險: 1 個（Node system.run 路徑）
- ✅ 無影響: 6 個

**結論**: 系統整體風險較低，大部分 Breaking Changes 不受影響。主要風險點是 Heartbeat DM 遞送策略，但由於我們主要在 webchat 運作，影響有限。

---

## 關鍵功能驗證清單（Phase 3 使用）

### 高優先級驗證（必須通過）
- [ ] **心跳自動化系統**
  - [ ] `auto_spawn_heartbeat.py` 正常運作
  - [ ] 任務啟動頻率正常（65-300 秒）
  - [ ] 背壓機制調整正常
  - [ ] webchat 頻道心跳不被阻止

- [ ] **子代理通信**
  - [ ] `sessions_spawn` 正常啟動
  - [ ] 子代理完成後狀態同步
  - [ ] `subagents list` 正常運作

- [ ] **背壓機制**
  - [ ] 健康度計算正常
  - [ ] 動態調整並發上限（2-3）
  - [ ] 動態調整啟動頻率（65-300 秒）

### 中優先級驗證（建議通過）
- [ ] **任務同步**
  - [ ] `task_sync.py` 正常同步狀態
  - [ ] 超時任務標記為 failed

- [ ] **錯誤恢復**
  - [ ] `error_recovery.py` 檢測 rate limit
  - [ ] 指數退避正常運作

- [ ] **狀態回滾**
  - [ ] `task_state_rollback.py` 檢測卡住任務
  - [ ] 自動回滾正常運作

### 低優先級驗證（可選）
- [ ] **Scout 系統**（如果可用）
  - [ ] Scout 掃描正常
  - [ ] 任務補充正常

- [ ] **Dashboard**（如果使用）
  - [ ] Docker 啟動正常
  - [ ] API 端點可訪問

---

## 升級對 Sub-Agent 的影響（2026-03-06 01:23 新增）

### ⚠️ 關鍵注意事項

**OpenClaw 升級會重啟 Gateway 進程，這會中斷所有正在運行的 sub-agent！**

### 影響分析

#### 1. Gateway 重啟的影響

**升級時會發生什麼**：
- OpenClaw Gateway 是一個獨立的守護進程
- 升級通常會重啟 Gateway 進程
- 重啟會中斷所有正在運行的 session（包括 sub-agent）

**對 sub-agent 的影響**：
- ⚠️ **正在執行的 sub-agent 會被中斷**
- ⚠️ **未完成的任務會丟失**
- ✅ **已完成的任務（有 .status 文件）會保留**

#### 2. 狀態恢復機制

**OpenClaw 的狀態存儲**：
- Session 狀態存儲在 `~/.openclaw/agents/main/sessions/sessions.json`
- Task 狀態存儲在 `~/.openclaw/workspace/kanban/tasks.json`
- Sub-agent 輸出存儲在 `~/.openclaw/workspace/kanban/works/[task-id]/`

**重啟後的恢復**：
- ✅ Session 列表會保留（但狀態可能過期）
- ✅ Task 狀態會保留（已持久化到 tasks.json）
- ⚠️ 正在執行的 task 會停留在 spawning 狀態
- ⚠️ 需要運行 `task_state_rollback.py` 清理卡住的任務

### 升級前的最佳實踐

#### ✅ 升級前檢查清單（必須執行）

```bash
# 1. 檢查正在運行的 sub-agent
openclaw sessions list --kinds isolated --active-minutes 60

# 2. 檢查 spawning 任務
python3 -c "
import json
with open('~/.openclaw/workspace/kanban/tasks.json') as f:
    tasks = json.load(f)
    spawning = [t for t in tasks if t['status'] == 'spawning']
    print(f'Spawning 任務: {len(spawning)}')
"

# 3. 如果有運行中的 sub-agent，等待完成或手動清理
# 等待完成：建議等待所有 sub-agent 完成
# 手動清理：如果卡住，運行回滾腳本
python3 kanban-ops/task_state_rollback.py

# 4. 備份關鍵數據
mkdir -p ~/.openclaw/backup-before-upgrade
cp -r ~/.openclaw/workspace/kanban ~/.openclaw/backup-before-upgrade/
cp -r ~/.openclaw/workspace/kanban-ops ~/.openclaw/backup-before-upgrade/
```

#### ⚠️ 升級策略建議

**策略 A: 等待完成（推薦）**
- 等待所有 sub-agent 完成
- 運行 `task_state_rollback.py` 清理卡住的任務
- 確認沒有正在執行的任務
- 進行升級

**策略 B: 低峰期升級**
- 選擇 sub-agent 數量最少的時段（如深夜）
- 接受少量任務可能被中斷
- 運行 `task_state_rollback.py` 快速恢復
- 進行升級

**策略 C: 測試環境驗證（Phase 3）**
- 在測試環境驗證升級對 sub-agent 的影響
- 記錄升級過程和恢復步驟
- 應用到生產環境

### 當前狀態檢查結果（2026-03-06 01:23）

✅ **好消息：當前沒有正在運行的 sub-agent！**

| 檢查項 | 結果 |
|--------|------|
| Isolated sessions（sub-agent） | 0 個 |
| Direct sessions（主會話） | 1 個（當前） |
| Cron sessions | 1 個 |
| Group sessions | 1 個 |
| **執行中的 sub-agent** | **0 個** ✅ |

### Spawning 任務狀態

- **回滾前**: 16 個 spawning 任務（已卡住超過 5 天）
- **回滾後**: 11 個 spawning 任務（3 個疑似卡住，將在 45 分鐘自動回滾）
- **結論**: 這些任務已經失敗，升級不會造成額外影響

### 升級恢復流程

升級後，如果發現任務被中斷：

```bash
# 1. 檢查 spawning 任務
python3 -c "
import json
with open('~/.openclaw/workspace/kanban/tasks.json') as f:
    tasks = json.load(f)
    spawning = [t for t in tasks if t['status'] == 'spawning']
    print(f'Spawning 任務: {len(spawning)}')
"

# 2. 運行回滾腳本清理卡住的任務
python3 kanban-ops/task_state_rollback.py

# 3. 這些任務會在下次心跳時自動重新啟動
```

---

## 回滾計劃

### 備份位置
```bash
# 創建備份目錄
mkdir -p ~/.openclaw/backup-20260306

# 備份關鍵文件
cp -r ~/.openclaw/workspace ~/.openclaw/backup-20260306/workspace
cp -r ~/.openclaw/skills ~/.openclaw/backup-20260306/skills
cp -r ~/.openclaw/memory ~/.openclaw/backup-20260306/memory

# 備份配置（如果存在）
cp ~/.openclaw/config.json ~/.openclaw/backup-20260306/config.json.backup 2>/dev/null || true
```

### 回滾命令
```bash
# 方案 A: Git 回滾（推薦）
cd ~/.openclaw
git log --oneline -10  # 查看最近的提交
git checkout <commit-hash-before-upgrade>

# 方案 B: 恢復備份
rm -rf ~/.openclaw/workspace
rm -rf ~/.openclaw/skills
rm -rf ~/.openclaw/memory
cp -r ~/.openclaw/backup-20260306/workspace ~/.openclaw/
cp -r ~/.openclaw/backup-20260306/skills ~/.openclaw/
cp -r ~/.openclaw/backup-20260306/memory ~/.openclaw/

# 方案 C: 降級版本
openclaw update 2026.2.15
```

### 回滾觸發條件
- 心跳自動化失敗（無法啟動任務）
- 子代理通信失敗（無法 `sessions_spawn`）
- 背壓機制失效（無法調整並發）
- 關鍵腳本執行失敗（語法錯誤、API 變更）
- 任務同步失敗（無法更新狀態）

---

## 時間表（預估）

### Phase 1: 評估與盤點 ✅ 已完成
- 時間: 2026-03-06 01:05
- 狀態: 已完成
- 產出:
  - ✅ 系統盤點完成（64 個腳本，19,276 行代碼）
  - ✅ Breaking Checks 影響評估完成
  - ✅ 關鍵功能驗證清單創建
  - ✅ 回滾計劃準備

### Phase 2: 向前相容準備（待執行）
- 時間: 1-2 週
- 狀態: 待執行
- 任務:
  - [ ] 採用新的錯誤處理模式
  - [ ] 準備新版本配置模板
  - [ ] 檢查簡寫命令使用情況
  - [ ] 文檔化當前系統行為

### Phase 3: 測試環境驗證（待執行）
- 時間: 1 週
- 狀態: 待執行
- 任務:
  - [ ] 創建測試分支
  - [ ] 更新到測試版本（2026.3.3）
  - [ ] 運行驗證清單
  - [ ] 記錄問題和解決方案

### 決策點（待執行）
- 時間: 3-4 週後
- 狀態: 待決策
- 選項:
  - ✅ 測試通過 → 安排生產環境更新時間
  - ⚠️ 測試部分失敗 → 調整準備工作，重試 Phase 3
  - ❌ 測試嚴重失敗 → 放棄更新，保持當前版本

---

## 新版本配置模板

### config-v2026.3.3.json（推薦配置）
```json
{
  "agents": {
    "defaults": {
      "heartbeat": {
        "directPolicy": "block"
      },
      "sandbox": {
        "docker": {
          "dangerouslyAllowContainerNamespaceJoin": false
        }
      }
    }
  },
  "acp": {
    "dispatch": {
      "enabled": false
    }
  }
}
```

**配置說明**:
- `heartbeat.directPolicy: "block"` - 保持舊行為，阻止 DM 遞送（如果需要）
- `dangerouslyAllowContainerNamespaceJoin: false` - 使用新默認值，增強安全性
- `acp.dispatch.enabled: false` - 明確禁用 ACP（我們不使用）

---

## 下一步行動

### 立即可行動（今天）
- [x] 創建 UPGRADE_PLAN.md ✅
- [x] 完成系統盤點 ✅
- [x] 完成 Breaking Checks 影響評估 ✅
- [ ] 檢查簡寫命令使用情況
  ```bash
  grep -r "tr \|grep \|awk " kanban-ops/ --include="*.py"
  ```

### 本週可行動
- [ ] 創建測試驗證腳本
  ```bash
  cat > ~/.openclaw/workspace/verify-upgrade.sh << 'EOF'
  #!/bin/bash
  echo "========== 升級驗證清單 =========="
  # 測試心跳、任務啟動、背壓機制...
  EOF
  chmod +x ~/.openclaw/workspace/verify-upgrade.sh
  ```

### 下週可行動
- [ ] 開始 Phase 2: 向前相容準備
- [ ] 準備測試環境

---

## 結論

### 風險評估
- **總體風險**: 🟡 中等偏低
- **高風險 Breaking Changes**: 0 個
- **中等風險 Breaking Changes**: 1 個（Heartbeat DM 遞送）
- **低風險 Breaking Changes**: 1 個（Node system.run 路徑）
- **無影響 Breaking Changes**: 6 個

### 升級建議
- ✅ **推薦升級**: 風險可控，Breaking Changes 影響有限
- 🛡️ **必須準備**: 備份 + 測試環境驗證
- ⏰ **建議時間**: 3-4 週後（完成 Phase 2 和 Phase 3）
- 🎯 **目標**: 確保關鍵功能正常，無中斷風險

### 備註
- 系統高度自定化，但大部分 Breaking Changes 不受影響
- Heartbeat 系統是最關鍵的風險點，需要優先測試驗證
- 建立升級流程比單次升級更有價值，可以重複使用

---

**文檔版本**: v1.0
**最後更新**: 2026-03-06 01:05
**負責人**: Charlie (Orchestrator)
**審核者**: David
