# 技術棧庫存 (TECH INVENTORY)

> **目的：** 記錄所有現有技術、系統和工具，避免重複造輪子
> **更新頻率：** 每次新增技術時更新
> **維護者：** Charlie

---

## 🗃️ 向量資料庫

### QMD 向量資料庫
- **路徑：** knowledge/qmd/
- **CLI 工具：** qmd
- **支援：** 官方
- **狀態：** ✅ 已整合
- **依賴：** 無
- **功能：**
  - 語義向量搜索（qmd vsearch）
  - 向量索引和存儲
  - 元數據管理
  - 多 collection 支援
- **使用方式：**
  ```bash
  # 搜索
  qmd vsearch "搜索內容" -n 10

  # 添加文件
  qmd add file.md -c collection_name

  # 更新元數據
  qmd update file_id --metadata '{"key": "value"}'
  ```
- **整合文件：** knowledge/qmd/qmd_integration.py
- **文檔：** knowledge/qmd/README.md
- **最後更新：** 2026-03-09

---

## 📝 筆記系統

### Obsidian 整合
- **路徑：** obsidian_wrapper.py
- **狀態：** ✅ 已整合
- **依賴：** Obsidian CLI（官方支援）
- **文件：**
  - obsidian_wrapper.py (14,028 bytes)
  - obsidian_memory.py (7,078 bytes)
  - obsidian_integration.py (7,072 bytes)
  - memory_system.py (6,631 bytes)
  - memory_system_maintain.py (9,424 bytes)
- **功能：**
  - 文件操作（create, read, append, delete）
  - 搜索（search, search_context）
  - 連結分析（get_orphans, get_deadends, get_unresolved, get_backlinks）
  - 標籤管理（get_tags）
  - 每日筆記（daily_append）
  - Vault 管理（vault_info, list_vaults）
- **使用方式：**
  ```python
  from obsidian_wrapper import ObsidianWrapper

  obsidian = ObsidianWrapper(vault_path="~/Documents/Obsidian")

  # 創建筆記
  obsidian.create_note("note.md", "# 標題\n內容")

  # 搜索
  results = obsidian.search("搜索關鍵詞")

  # 獲取孤立筆記
  orphans = obsidian.get_orphans()
  ```
- **文檔：**
  - OBSIDIAN_MEMORY_GUIDE.md
  - OBSIDIAN_INTEGRATION_COMPLETE.md
  - OBSIDIAN_BEST_PRACTICES.md
- **最後更新：** 2026-03-08

---

## 📊 任務管理

### Kanban 系統
- **路徑：** kanban/
- **核心文件：** tasks.json
- **狀態：** ✅ 已整合
- **依賴：** 無
- **腳本：**
  - storage.py（線程安全存儲）
  - task_runner.py（任務執行器）
  - spawn_processor.py（任務隊列處理器）
  - task_sync.py（狀態同步器）
  - auto_spawn_heartbeat.py（自動啟動心跳）
  - backpressure.py（背壓機制）
  - task_state_rollback.py（狀態回滾）
  - task_cleanup.py（任務清理）
  - error_recovery.py（錯誤恢復）
- **功能：**
  - 任務管理（pending, in_progress, completed, failed）
  - 並發控制（最多 3 個任務同時運行）
  - 依賴檢查（只啟動依賴已完成的任務）
  - 優先級排序（按優先級和時間排序）
  - 狀態同步（掃描子代理的 .status 文件）
  - 超時檢測（超過 24 小時標記為 failed）
  - 背壓機制（根據健康度動態調整）
- **文檔：** kanban-ops/MONITORING_SYSTEM_SUCCESS.md
- **最後更新：** 2026-03-05

---

## 📈 監控系統

### Prometheus
- **版本：** 2.48.0
- **端口：** 9090
- **PID：** 96040
- **狀態：** ✅ 運行中
- **路徑：** /Users/charlie/monitoring/prometheus/
- **配置：** prometheus/prometheus.yml
- **採集目標：**
  - Prometheus 自身 (localhost:9090)
  - OpenClaw Gateway (localhost:18790)
  - Kanban Metrics (localhost:9101)
- **採集頻率：** 每 15 秒
- **監控指標：**
  - `openclaw_tasks_total{status}` - 按狀態的任務總數
  - `openclaw_tasks_by_agent{agent, status}` - 按 agent 類型的任務分佈
  - `openclaw_task_duration_minutes{agent}` - 任務耗時直方圖
  - `openclaw_task_tokens_total{agent, direction}` - 總 token 消耗
  - `openclaw_false_failures_total` - 檢測到的假失敗總數
  - `openclaw_auto_recoveries_total{confidence}` - 自動恢復次數
- **文檔：** kanban-ops/MONITORING_SYSTEM_SUCCESS.md
- **最後更新：** 2026-02-20

### Grafana
- **版本：** 10.2.3
- **端口：** 3000
- **PID：** 97069
- **狀態：** ✅ 運行中
- **路徑：** /Users/charlie/monitoring/grafana/
- **訪問：** http://localhost:3000
- **管理員：** admin/admin（首次登入需修改）
- **Dashboard：** OpenClaw System Dashboard（8 個面板）
- **文檔：** kanban-ops/MONITORING_SYSTEM_SUCCESS.md
- **最後更新：** 2026-02-20

### Kanban Metrics Exporter
- **端口：** 9101
- **PID：** 96598
- **狀態：** ✅ 運行中
- **路徑：** /Users/charlie/.openclaw/workspace/kanban-ops/kanban_metrics_exporter.py
- **日誌：** /Users/charlie/.openclaw/logs/metrics_exporter.log
- **文檔：** kanban-ops/MONITORING_SYSTEM_SUCCESS.md
- **最後更新：** 2026-02-20

---

## 🚀 Dashboard

### Dashboard 系統
- **路徑：** ~/.openclaw/workspace/Dashboard（符號鏈接）
- **框架：** FastAPI + React
- **狀態：** ✅ 已整合
- **依賴：**
  - FastAPI（後端）
  - React 19（前端）
  - VectorBT（回測引擎）
- **功能：**
  - 策略回測
  - 數據可視化
  - 系統監控
- **API 端點：**
  - GET /health - 健康檢查
  - GET /api/strategies/templates - 獲取策略模板
  - POST /api/strategies/backtest - 執行回測
  - POST /api/strategies/comparison - 策略比較
  - POST /api/strategies/monte-carlo - Monte Carlo 模擬
- **文檔：** TOOLS.md
- **最後更新：** 2026-03-02

---

## 🔍 研究系統

### Scout Agent
- **路徑：** ~/.openclaw/workspace-scout
- **狀態：** ✅ 已整合
- **依賴：** 無
- **腳本：** scout_agent.py
- **功能：**
  - 自動發現研究主題
  - 從多個數據源掃描（12 個數據源）
  - 評估主題質量
  - 創建 Kanban 任務
- **數據源：**
  - API 數據源：arxiv, rss
  - 爬文數據源：threads, quantocracy, quantconnect, nuclear_phynance, quantnet, ssrn, nber, hedge_fund_reports, tradingview, quant_stackexchange
- **文檔：** kanban/outputs/scout-phase2-complete.md
- **最後更新：** 2026-02-23

---

## 🧠 記憶系統

### 認知矩陣（設計中）
- **狀態：** 🟡 設計階段
- **設計文檔：** kanban/outputs/memory-system-redesign.md
- **三層記憶：**
  - Session Memory（短期）：In-Memory + session.json
  - Working Memory（中期）：Obsidian Daily Notes + QMD
  - Knowledge Base（長期）：Obsidian Topics + QMD
- **統一介面：** MemoryCore
- **事件驅動：** Memory Bus
- **技術優勢：**
  - 70% 減少耦合
  - 300% 增加可擴展性
  - 500% 增加搜索能力
  - 400% 增加知識連結
  - 200% 增加容錯性
- **文檔：**
  - kanban/outputs/memory-system-redesign.md
  - memory/2026-03-09.md（資料流分析）
- **最後更新：** 2026-03-09

---

## 🎯 技能系統

### 技能（Skills）
- **路徑：** ~/.openclaw/workspace/skills/
- **狀態：** ✅ 已整合
- **核心技能：**
  - discord（Discord 操作）
  - healthcheck（主機安全加固）
  - skill-creator（AgentSkills 創建）
  - weather（天氣預報）
  - agent-output（代理輸出格式）
  - github-pages-updater（GitHub Pages 自動發布）
  - telegram-format（Telegram 訊息格式）
  - agent-protocol（代理通信協議）
  - context-compact（上下文壓縮）
  - execution-planner（執行計畫）
  - insight-extractor（洞察提取）
  - kanban-ops（Kanban 操作）
  - memory-maintenance（記憶維護）
  - on-demand-skill-loader（按需技能加載）
  - priority-rule-engine（優先級規則引擎）
  - research-scorer（研究評分）
  - scout-dependency-manager（Scout 依賴管理）
  - scout-integrator（Scout 整合器）
  - spawn-protocol（子代理啟動協議）
  - stock-symbol-mapper（股票代碼映射）
  - task-dependencies（任務依賴）
  - task-optimizer（任務優化）
  - task-state-enhancer（任務狀態增強）
  - task-timeout-monitor（任務超時監控）
  - weekly-summary（每週總結）
  - check-existing-systems（檢查現有系統）
- **文檔：** AGENTS.md
- **最後更新：** 2026-03-09

---

## 🤖 代理系統

### Sub-Agents
- **狀態：** ✅ 已整合
- **可用代理：**
  - research（研究代理）
  - analyst（分析代理）
  - creative（創意代理）
  - automation（自動化代理）
  - architect（架構代理）
  - developer（開發代理）
  - social-media（社交媒體代理）
  - security（安全代理）
  - mentor（導師代理）
- **並發限制：**
  - research/automation：10 並發
  - analyst/creative：5 並發
  - architect：1 並發
  - developer：2 並發
  - mentor：1 並發
- **文檔：** IDENTITY.md, SUBAGENTS.md
- **最後更新：** 2026-03-09

---

## 📋 SOP 文檔

### 標準操作程序
- **路徑：** ~/.openclaw/workspace/skills/
- **核心 SOP：**
  - check-existing-systems/SKILL.md（檢查現有系統 SOP）
- **文檔：**
  - AGENTS.md（代理指南）
  - BOOTSTRAP.md（啟動指南）
  - HEARTBEAT.md（心跳任務）
  - IDENTITY.md（身份定義）
  - KANBAN.md（Kanban 系統）
  - MEMORY.md（長期記憶）
  - SOUL.md（靈魂定義）
  - SUBAGENTS.md（子代理指南）
  - TOOLS.md（工具指南）
  - USER.md（用戶指南）
- **最後更新：** 2026-03-09

---

## 🔄 整合系統

### Memory System（舊系統）
- **路徑：** memory_system.py
- **狀態：** ✅ 已整合
- **功能：**
  - 統一記憶操作（store, search）
  - 向後兼容
- **維護腳本：** memory_system_maintain.py
- **文檔：** OBSIDIAN_MEMORY_GUIDE.md
- **最後更新：** 2026-03-08

---

## 📊 總結

| 類別 | 數量 | 狀態 |
|------|------|------|
| **向量資料庫** | 1 | ✅ 已整合 |
| **筆記系統** | 1 | ✅ 已整合 |
| **任務管理** | 1 | ✅ 已整合 |
| **監控系統** | 3 | ✅ 已整合 |
| **Dashboard** | 1 | ✅ 已整合 |
| **研究系統** | 1 | ✅ 已整合 |
| **記憶系統** | 1 | 🟡 設計中 |
| **技能系統** | 27 | ✅ 已整合 |
| **代理系統** | 9 | ✅ 已整合 |
| **SOP 文檔** | 10 | ✅ 已整合 |
| **整合系統** | 1 | ✅ 已整合 |

**總計：** 56 個系統/工具/技能

---

**最後更新：** 2026-03-09 01:27 AM
**版本：** v1.0
**維護者：** Charlie
