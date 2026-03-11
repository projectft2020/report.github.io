# Automation 代理失敗問題 - 完整診斷報告

## 📋 問題摘要

**任務：** AI Agents for Automated Risk Management Systems (ai001)  
**失敗次數：** 3 次  
**時間：** 17:16 - 17:19 GMT+8  
**錯誤：** Gateway timeout after 15000ms

---

## 🕐 失敗時間線

| 次數 | 時間 (GMT+8) | Session ID | 錯誤 |
|------|--------------|-------------|------|
| 1 | 17:16:25.509 | d26ed1f8 | Subagent announce failed |
| 2 | 17:17:56.345 | c149d9e7 | Subagent announce failed |
| 3 | 17:19:54.821 | (未知) | Subagent announce failed |

---

## 🐛 核心錯誤日誌

```
2026-02-20T17:16:25.509+08:00 Subagent announce failed: Error: gateway timeout after 15000ms
Gateway target: ws://127.0.0.1:18789
Source: local loopback
Config: /Users/charlie/.openclaw/openclaw.json
Bind: loopback
```

**關鍵點：**
- 錯誤類型：`Subagent announce failed`
- 超時時間：`15000ms` (15 秒)
- 目標地址：`ws://127.0.0.1:18789`

---

## ⚙️ 代理配置對比

### 主會話配置 (Charlie)
```json
{
  "subagents": {
    "maxConcurrent": 4,
    "model": "zai/glm-4.5",
    "maxSpawnDepth": 1
  }
}
```

### 各代理配置

| 代理 | Workspace | 主模型 | 禁用工具 | 成功率 |
|------|-----------|--------|----------|--------|
| **research** | workspace-research | exec, edit, cron | ✅ 100% (4/4) |
| **analyst** | workspace-analyst | (無) | ✅ 100% (3/3) |
| **creative** | (未配置) | (未配置) | ⏸️ 未測試 |
| **automation** | workspace-automation | web_search, web_fetch, web_reader | ❌ 0% (3/3) |

---

## 🔍 問題根源分析

### 1. 不是模型問題
- automation 使用 `zai/glm-4.5`
- research 也使用 `zai/glm-4.5`
- analyst 使用 `zai/glm-4.7` (更強)
- 模型本身沒有問題

### 2. Gateway 通訊失敗
- 子代理在啟動後無法與 gateway 通信
- 15 秒後超時
- 這表明 **子代理初始化失敗**

### 3. 可能的原因

#### A. Workspace 初始化問題
- `workspace-automation` 目錄可能有問題
- 文件權限或結構問題
- Bootstrap 文件缺失或損壞

#### B. 代理工具配置衝突
- automation 禁用了 web_search, web_fetch, web_reader
- 可能在初始化時檢查工具配置失敗
- 可能需要其他未明確禁用的工具

#### C. Gateway 會話限制
- 主會話的 `maxConcurrent: 4`
- 當時可能已經達到並發上限
- 新的 automation 會話被阻塞

#### D. WebSocket 連接問題
- Gateway 的 WebSocket 服務不穩定
- 連接建立後立即斷開
- 需要更詳細的 gateway 日誌

---

## 🧪 建議診斷步驟

### 步驟 1：檢查 workspace-automation
```bash
# 檢查目錄是否存在
ls -la ~/.openclaw/workspace-automation/

# 檢查 bootstrap 文件
ls -la ~/.openclaw/workspace-automation/BOOTSTRAP.md
ls -la ~/.openclaw/workspace-automation/SOUL.md
```

### 步驟 2：檢查 Gateway 狀態
```bash
# 查看 Gateway 狀態
openclaw gateway status

# 查看 Gateway 日誌（詳細模式）
tail -200 ~/.openclaw/logs/gateway.log | grep -A 5 -B 5 "automation"
tail -200 ~/.openclaw/logs/gateway.err.log | grep -A 5 -B 5 "automation"
```

### 步驟 3：測試單獨創建 automation 會話
```bash
# 嘗試創建一個簡單的 automation 任務
# 看是否每次都失敗，還是特定情況下失敗
```

### 步驟 4：檢查並發數量
```bash
# 查看失敗時間點的其他運行中會話
# 確認是否達到並發上限
```

---

## 💡 暫時解決方案

### 方案 1：避免使用 automation 代理 ✅ 推薦
- 研究任務 → research
- 分析任務 → analyst
- 創意任務 → creative

### 方案 2：重試 automation 時
- 確保低負載（其他會話完成）
- 增加超時時間（如果配置允許）
- 監控 gateway 日誌

### 方案 3：修改 automation 配置（高級）
- 檢查工具禁用列表
- 驗證 workspace 設置
- 考慮使用 research 的配置

---

## 📊 數據支持

### 成功代理特徵
- 使用不同的 workspace
- 工具權限更簡單
- 初始化邏輯更穩定

### 失敗代理特徵
- automation 專用 workspace
- 禁用多個 web 工具
- 可能初始化檢查過多

---

## 🎯 下一步行動

1. **立即：** 繼續使用 research/analyst 代理
2. **短期：** 執行建議的診斷步驟
3. **長期：** 根據診斷結果修復 automation 代理或棄用

