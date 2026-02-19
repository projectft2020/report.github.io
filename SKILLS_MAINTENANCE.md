# Skills System — 維護手冊

**適用版本：** OpenClaw v2026.2.15+
**架構版本：** Charlie v4.0 (Orchestrator-Worker)
**最後更新：** 2026-02-18 (r3 — context overflow + Telegram drop fix)

---

## 系統概覽

Charlie 的 Skills 系統採用三層架構，控制每個 agent 在 session 啟動時載入哪些行為規範：

```
~/.openclaw/skills/                        共用層 — 所有 agent 繼承
~/.openclaw/workspace/skills/              主代理層 — 只有 main 看到
~/.openclaw/workspace-[id]/skills/         專屬層 — 只有該 agent 看到
```

**優先級（同名 skill 時）：** workspace 專屬 > 共用層
**載入時機：** 每次 session 啟動時，eligible skills 全部載入進 system prompt

---

## 現有 Skills 清單

### 共用層 (`~/.openclaw/skills/`)

| Skill | 用途 | 適用 agent |
|-------|------|-----------|
| `agent-output` | 輸出檔案格式基礎標準 + announce 協定 | 所有 sub-agent（作為 fallback） |

### 主代理層 (`~/.openclaw/workspace/skills/`)

| Skill | 用途 |
|-------|------|
| `spawn-protocol` | Spawn 前置清單 + 各 agent 任務模板 dispatch table |
| `kanban-ops` | tasks.json 讀寫、看板 keyword 回應、任務狀態更新、stale task 自動偵測與修復 |

### 專屬層（各 workspace 覆蓋共用 `agent-output`）

| Agent | 路徑 | 特有 section |
|-------|------|-------------|
| research | `workspace-research/skills/agent-output/` | Key Findings、Sources（強制 URL）、Confidence |
| analyst | `workspace-analyst/skills/agent-output/` | Executive Summary、Risk Assessment table、Recommendations |
| creative | `workspace-creative/skills/agent-output/` | Content（完整交付物）、Type、Word count |
| automation | `workspace-automation/skills/agent-output/` | Operations table、Verification、Rollback needed |

---

## 新增 Sub-Agent SOP

當需要新增一個專門的 sub-agent（例如 `quant`、`notifier`、`summarizer`）：

### Step 1：建立 workspace

```bash
ssh charlie@192.168.1.117
mkdir -p ~/.openclaw/workspace-[agent-id]/skills/agent-output
```

### Step 2：寫 AGENTS.md

參考現有的 `workspace-research/AGENTS.md` 格式，建立：
```
~/.openclaw/workspace-[agent-id]/AGENTS.md
```

必填 section：
- 身分定義（名稱、specialty）
- When Spawned: Your Workflow（7 步驟流程）
- Task Message Format（含 INPUT FILES 說明）
- Tools Available / Denied
- Safety Rules（如適用）

### Step 3：寫專屬 agent-output skill

```
~/.openclaw/workspace-[agent-id]/skills/agent-output/SKILL.md
```

複製 `shared agent-output` 的格式，修改：
- Required output sections（針對該 agent 的專業領域）
- Announce format（成功/失敗兩種）

### Step 4：更新 openclaw.json

```bash
python3 << 'EOF'
import json
with open('/Users/charlie/.openclaw/openclaw.json') as f:
    cfg = json.load(f)

cfg['agents']['list'].append({
    "id": "[agent-id]",
    "workspace": "/Users/charlie/.openclaw/workspace-[agent-id]",
    "model": {"primary": "zai/glm-4.5"},     # 或 glm-4.7 視需求
    "tools": {"deny": ["exec", "cron"]}       # 視需求調整
})

with open('/Users/charlie/.openclaw/openclaw.json', 'w') as f:
    json.dump(cfg, f, indent=2)
print("Done")
EOF
```

也要把新 agent id 加進 main agent 的 `allowAgents`：

```bash
python3 << 'EOF'
import json
with open('/Users/charlie/.openclaw/openclaw.json') as f:
    cfg = json.load(f)

for agent in cfg['agents']['list']:
    if agent['id'] == 'main':
        agent['subagents']['allowAgents'].append('[agent-id]')

with open('/Users/charlie/.openclaw/openclaw.json', 'w') as f:
    json.dump(cfg, f, indent=2)
print("Done")
EOF
```

### Step 5：更新 spawn-protocol skill

在 `~/.openclaw/workspace/skills/spawn-protocol/SKILL.md` 的 **Agent Dispatch Table** 新增一個 section：

```markdown
### `[agent-id]` — [一行說明這個 agent 做什麼]
- Model: GLM-4.5（默認，不需指定）| GLM-4.7（需指定）
- Task message template:
  TASK: ...
  OUTPUT PATH: .../[task-id]-[type].md
```

### Step 6：重啟 OpenClaw

```bash
launchctl stop ai.openclaw.gateway
launchctl start ai.openclaw.gateway
```

---

## 修改現有 Skill SOP

### 修改 SKILL.md

直接 SSH 編輯對應檔案：

```bash
ssh charlie@192.168.1.117 "nano ~/.openclaw/workspace/skills/spawn-protocol/SKILL.md"
```

Skills 有 watcher（`skills.load.watch: true`），修改後通常在**下一個 session** 生效，不需重啟。
若要立刻生效：重啟 OpenClaw 或讓 Charlie `/reset`。

### 確認 skill 是否有載入

```bash
ssh charlie@192.168.1.117 \
  "PATH=/usr/local/bin:/usr/bin:/bin /usr/local/bin/node \
   /usr/local/lib/node_modules/openclaw/dist/index.js \
   agent --agent main --message '列出你現在載入了哪些 skills'"
```

---

## Stale Task 處理邏輯

`kanban-ops` skill 內建兩段式 stale detection，每次讀取 tasks.json 時自動執行：

| 情況 | 判斷條件 | 處理 |
|------|---------|------|
| Mode A：announce 丟失 | age > 10m **且** output 檔案存在 | 自動標 `completed`，notes 記錄 `auto-recovered` |
| Mode B：agent 真的失敗 | age > 10m **且** output 檔案不存在 | 自動標 `failed`，notes 記錄逾時時間 |

觸發點：
- 查看工作看板（`工作看板` / `kanban`）
- Spawn 新任務前
- 收到 announce 後
- 手動輸入 `修復看板` / `recover tasks`

stale 閾值：10 分鐘（可在 skill 內修改）

---

## 故障排除

### Skill 沒有生效

1. 確認 `SKILL.md` 存在且有正確的 frontmatter
2. Frontmatter 必須是 single-line YAML，`metadata` 必須是 single-line JSON
3. 讓 Charlie `/reset` 強制重新載入 snapshot
4. 確認 skill 名稱沒有跟 bundled skill 衝突：
   ```bash
   ssh charlie@192.168.1.117 \
     "/usr/local/bin/node /usr/local/lib/node_modules/openclaw/dist/index.js \
      agent --message 'skills list' 2>&1 | head -20"
   ```

### Sub-agent 沒有繼承共用 skill

確認共用 skill 在 `~/.openclaw/skills/`（不是 `~/.openclaw/workspace/skills/`）：

```bash
ssh charlie@192.168.1.117 "ls ~/.openclaw/skills/"
```

Sub-agent 的 workspace 不是 main 的 workspace，所以 `workspace/skills/` 下的 skill 對 sub-agent 不可見。

### Telegram 訊息被吃掉（Silent Drop）

**症狀：** Charlie 出現 typing indicator，但最終回覆沒有出現在 Telegram。
**頻率：** 在多次 exec 工具呼叫後、或長時間對話後。

**根本原因：Context Overflow + Compaction 失敗連鎖**

1. Charlie 主 session 的 context 超過 GLM-4.7-Flash 的 202K token 上限
2. OpenClaw 觸發 auto-compaction（需要呼叫模型做摘要）
3. Flash 只有 1 個並發限制——對話本身已占用該名額
4. Compaction 呼叫收到 429 Rate Limit 錯誤，失敗
5. 無法生成回覆 → Telegram 收不到任何訊息（無錯誤提示）

**診斷方法：**
```bash
# 查看 context overflow 錯誤
grep 'context-overflow\|auto-compaction failed\|Summarization failed' \
  ~/.openclaw/logs/gateway.err.log | tail -10

# 查看 typing TTL（超過 2 分鐘沒有文字輸出 = 可能是 tool call 太多）
grep 'typing TTL' ~/.openclaw/logs/gateway.log | tail -5
```

**修復（已套用於 openclaw.json）：**

```json
// agents.list[main].model — 加 fallback，讓 compaction 在 Flash 429 時用 GLM-4.5
"model": {
  "primary": "zai/glm-4.7-flash",
  "fallbacks": ["zai/glm-4.5"]
}

// agents.defaults.compaction — safeguard 模式，長 history 分段摘要
"compaction": {
  "mode": "safeguard"
}

// channels.telegram.streamMode — 關閉 draft streaming，改用一次性送出
"streamMode": "off"
```

**手動強制 compaction（緊急）：**
```bash
# 讓 Charlie 執行 /compact
/usr/local/bin/node /usr/local/lib/node_modules/openclaw/dist/index.js \
  agent --agent main --message '/compact'
```

---

### tasks.json 格式錯誤

```bash
ssh charlie@192.168.1.117 \
  "python3 -c \"import json; json.load(open('/Users/charlie/.openclaw/workspace/kanban/tasks.json')); print('OK')\""
```

修復（清空並重置）：
```bash
ssh charlie@192.168.1.117 \
  "echo '[]' > ~/.openclaw/workspace/kanban/tasks.json"
```

---

## 重要路徑速查

```
Skills:
  共用層:         /Users/charlie/.openclaw/skills/
  主代理:         /Users/charlie/.openclaw/workspace/skills/
  research:       /Users/charlie/.openclaw/workspace-research/skills/
  analyst:        /Users/charlie/.openclaw/workspace-analyst/skills/
  creative:       /Users/charlie/.openclaw/workspace-creative/skills/
  automation:     /Users/charlie/.openclaw/workspace-automation/skills/

Kanban:
  tasks.json:     /Users/charlie/.openclaw/workspace/kanban/tasks.json
  projects/:      /Users/charlie/.openclaw/workspace/kanban/projects/
  archive/:       /Users/charlie/.openclaw/workspace/kanban/archive/

Config:
  openclaw.json:  /Users/charlie/.openclaw/openclaw.json
  gateway log:    /Users/charlie/.openclaw/logs/gateway.log
  gateway err:    /Users/charlie/.openclaw/logs/gateway.err.log

LaunchAgent:
  plist:          /Users/charlie/Library/LaunchAgents/ai.openclaw.gateway.plist
  restart:        launchctl stop ai.openclaw.gateway && launchctl start ai.openclaw.gateway
```

---

## 設計原則（未來修改時參考）

1. **共用層只放跨 agent 通用的規範**，不放任何 agent 特有的輸出格式
2. **Workspace 專屬 skill 覆蓋共用層同名 skill** — 用覆蓋取代繼承，避免衝突
3. **spawn-protocol 是 dispatch table 的單一來源** — 新增 agent 後只需在這裡加一個 section，IDENTITY.md 不用動
4. **Skills 是 session 啟動時載入的指令集，不是程式碼** — 修改立即可測試，沒有 build 步驟
5. **每個 skill 應單一職責** — `spawn-protocol` 只管 spawn，`kanban-ops` 只管看板，`agent-output` 只管輸出格式

---

## 相關文件

| 文件 | 路徑 |
|------|------|
| 架構設計說明 | `03-agents/26-orchestrator-worker-architecture.md` |
| 生產部署指南 | `03-agents/27-production-deployment-guide.md` |
| Charlie 升級說明（給 Charlie 讀的） | `03-agents/28-charlie-upgrade-briefing.md` |
| 本文件 | `03-agents/29-skills-system-maintenance.md` |
| OpenClaw Skills 官方文件 | `/usr/local/lib/node_modules/openclaw/docs/tools/skills.md` |
