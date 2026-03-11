# System Architecture

> **Category:** Kanban 系統、監控、自動化、工作流
> **Source:** MEMORY.md 2026-02-19 to 2026-02-21
> **Last Updated:** 2026-02-23

---

## 🎯 Kanban 工作流自動化系統

### 完成時間：2026-02-19
**核心組件：**

#### 1. storage.py - 線程安全存儲系統
- **文件鎖：** fcntl.lockf()
- **原子操作：** 讀寫同步
- **路徑：** kanban/storage/tasks.json
- **功能：** 安全的任務存儲和讀取

#### 2. task_runner.py - 任務執行器
- **並發控制：** 最多 5 個任務同時運行
- **依賴檢查：** 只啟動依賴已完成的任務
- **優先級排序：** 按優先級和時間排序
- **狀態更新：** pending → in_progress

#### 3. spawn_processor.py - 任務隊列處理器
- **隊列讀取：** 讀取 spawn_queue.json
- **參數準備：** 生成 sessions_spawn 調用參數
- **批次處理：** 支持多個任務
- **隊列清空：** clear_spawn_queue.py

#### 4. task_sync.py - 狀態同步器
- **掃描機制：** 掃描子代理的 .status 文件
- **狀態更新：** 更新 tasks.json 中的任務狀態
- **超時檢測：** 超過 24 小時標記為 failed
- **輸出複製：** 複製輸出文件到主工作區

#### 5. clear_spawn_queue.py - 隊列清空工具
- **備份：** 備份到 spawn_queue.json.backup
- **清空隊列：** 清空 spawn_queue.json

---

## 🔄 Monitor and Refill (Scout 自動補充)

### 實現時間：2026-02-19
**類型：** Event-driven task monitoring (no cron needed!)

**核心功能：**
- **任務數量檢查：** pending tasks < 3 AND time since last scan > 2 hours
- **自動觸發：** 當條件滿足時觸發 Scout 掃描
- **2 小時保護窗：** 防止過度掃描
- **無狀態自調整：** 無需記住最後檢查時間

**優點（vs. cron）：**
- ✅ 無狀態（無需記住最後檢查時間）
- ✅ 事件驅動（按需觸發）
- ✅ 集成點（可以集成到任何地方）
- ✅ 無過度掃描（2 小時保護窗）
- ✅ 系統自調整（Scout 自動維護任務數量）

**工作流程：**
```
Pending Tasks < 3 AND Last Scan > 2h
    ↓
Trigger Scout Scan
    ↓
Discover Topics → Dedup → Score → Create Tasks
    ↓
Task Count Increases
```

---

## 📊 Stale Check & Auto Recovery

### Stale Check 機制
- **檢查頻率：** 每 10 分鐘
- **檢查對象：** in_progress 狀態的任務
- **超時閾值：** 24 小時
- **動作：**
  - 如果輸出文件不存在且超時 → 標記為 failed
  - 如果輸出文件存在 → 標記為 completed
  - 避免誤判：任務可能已完成但狀態未更新

### Auto Recovery 機制
- **檢測：** 假失敗（輸出文件存在但標記 failed）
- **恢復：** 重新標記為 completed，更新 completed_at
- **統計：** 追蹤恢復次數和結果

---

## 🚨 監控系統部署

### 完成時間：2026-02-20
**狀態：** ✅ 完全部署

### 組件

| 組件 | 版本 | 端口 | PID | 狀態 |
|------|------|------|-----|------|
| **Prometheus** | 2.48.0 | 9090 | 96040 | ✅ 運行中 |
| **Grafana** | 10.2.3 | 3000 | 97069 | ✅ 運行中 |
| **Kanban Metrics Exporter** | - | 9101 | 96598 | ✅ 運行中 |

### Prometheus 配置
**位置：** `/Users/charlie/monitoring/prometheus/prometheus.yml`
**採集目標：**
- Prometheus 自身 (localhost:9090)
- OpenClaw Gateway (localhost:18790)
- Kanban Metrics (localhost:9101)
**採集頻率：** 每 15 秒

### Grafana Dashboard
**名稱：** OpenClaw System Dashboard
**面板數量：** 8 個
**訪問：** http://localhost:3000
**管理員：** admin/admin（首次登入需修改）

### 監控指標

#### 1. 任務計數
- `openclaw_tasks_total{status}` - 按狀態的任務總數
- `openclaw_tasks_by_agent{agent, status}` - 按 agent 類型的任務分佈

#### 2. 任務時長
- `openclaw_task_duration_minutes{agent}` - 任務耗時直方圖
- Buckets: [1, 5, 10, 15, 20, 30, 45, 60, 90, 120, 180, 240]

#### 3. Token 消耗
- `openclaw_task_tokens_total{agent, direction}` - 總 token 消耗
- `rate(openclaw_task_tokens_total[5m])` - Token 消耗速率

#### 4. 假失敗檢測
- `openclaw_false_failures_total` - 檢測到的假失敗總數
- `openclaw_auto_recoveries_total{confidence}` - 自動恢復次數

#### 5. Progressive Research
- `openclaw_progressive_research_checkpoints{task_id}` - 檢查點數量
- `openclaw_progressive_research_searches_total{task_id}` - 搜索總數

### 通過監控可發現的問題

#### 1. Gateway Timeout 問題
- **監控：** `openclaw_auto_recoveries_total` 遞增
- **原因：** announce 超時導致任務完成但未通知
- **解決：** 檢查 Gateway 日誌，優化超時機制

#### 2. 假失敗檢測
- **監控：** `openclaw_false_failures_total` > 0
- **原因：** 子代理被終止但輸出完整
- **解決：** 自動恢復系統已部署

#### 3. Token 消耗異常
- **監控：** `rate(openclaw_task_tokens_total[5m])` 飙升
- **原因：** 研究 agent token 爆炸（467k）
- **解決：** 使用漸進式研究協議

#### 4. 任務執行時間異常
- **監控：** `openclaw_task_duration_minutes` P95 過高
- **原因：** 任務複雜度超出預期
- **解決：** 任務分解或調整模型

#### 5. Agent 可靠性問題
- **監控：** 按 agent 的失敗率
- **原因：** 某個 agent 不可靠（automation 代理 0% 可靠）
- **解決：** 切換到可靠 agent（research/analyst）

---

## 🔧 系統優化成果

### 並發能力驗證
- **成功：** 一次觸發 5 個任務，100% 成功率
- **優點：** 充分利用並發能力

### API 文檔問題
- **發現：** Matrix Dashboard 端點路徑錯誤
- **文檔：** `/api/strategies/backtest`
- **實際：** `/api/strategies/backtest/run`
- **記錄：** 已記錄到相關文檔

### 問題診斷方法
- **流程：**
  1. 檢查輸出文件是否存在
  2. 如果文件存在且完整 → 任務可能成功，狀態錯誤
  3. 如果文件不存在 → 任務確實失敗
  4. 創建診斷任務找出根本原因
  5. 重新執行失敗任務

---

## 📁 文件位置

### 監控系統
- **Prometheus 配置：** `/Users/charlie/monitoring/prometheus/prometheus.yml`
- **Prometheus 數據：** `/Users/charlie/monitoring/prometheus/data/`
- **Prometheus 日誌：** `/Users/charlie/monitoring/prometheus/prometheus.log`
- **Grafana 配置：** `/Users/charlie/monitoring/grafana/conf/defaults.ini`
- **Grafana 數據：** `/Users/charlie/monitoring/grafana/data/`
- **Grafana 日誌：** `/Users/charlie/monitoring/grafana/grafana.log`
- **Metrics Exporter 腳本：** `/Users/charlie/.openclaw/workspace/kanban-ops/kanban_metrics_exporter.py`
- **Metrics 日誌：** `/Users/charlie/.openclaw/logs/metrics_exporter.log`

### Kanban 系統
- **任務存儲：** `kanban/storage/tasks.json`
- **任務隊列：** `kanban/spawn_queue.json`
- **Runner 日誌：** `kanban/runner.log`
- **Sync 日誌：** `kanban/sync.log`

### 文檔
- **監控系統文檔：** `/Users/charlie/.openclaw/workspace/kanban-ops/MONITORING_SYSTEM_SUCCESS.md`
- **相關優化報告：**
  - `/Users/charlie/.openclaw/workspace/P0_optimization_summary_20260220.md`
  - `/Users/charlie/.openclaw/workspace/engineer_report_20260220.md`
  - `/Users/charlie/.openclaw/workspace/architecture_optimization_report.md`

---

## 📈 Prometheus 查詢範例

### 任務成功率
```promql
rate(openclaw_tasks_total{status="completed"}[5m]) /
rate(openclaw_tasks_total[5m])
```

### 平均任務時長
```promql
rate(openclaw_task_duration_minutes_sum[5m]) /
rate(openclaw_task_duration_minutes_count[5m])
```

### Token 消耗速率
```promql
rate(openclaw_task_tokens_total[5m])
```

---

## 🚀 系統優化 Phase 1 (2026-03-05)

### P0 優化：緊急保護（24 小時內）

#### 1. Spawning 超時保護
**問題：** 卡住任務從 2-4 個增加到 6 個，代表系統達到穩定性邊界

**實現方案：**
- 30 分鐘警報：spawning 狀態持續超過 30 分鐘發出警報
- 45 分鐘回滾：spawning 狀態持續超過 45 分鐘自動回滾到 pending
- 腳本：`kanban-ops/task_state_rollback.py`

**效果：** 卡住任務從 6 個降至 0 個（100% 改善）

#### 2. API 錯誤追蹤
**問題：** 缺少 API 錯誤診斷能力

**實現方案：**
- 記錄每次 sessions_spawn 的：回應時間、HTTP 狀態碼、錯誤訊息、X-RateLimit-* 標頭
- 聚合統計錯誤類型、頻率、趨勢
- 腳本：擴展 task_runner.py 的錯誤追蹤

**效果：** 可診斷卡住任務的根本原因

---

### P1 優化：預防性保護（3-7 天內）

#### 1. 背壓機制（Backpressure）
**問題：** Scout 發現 → 待辦 → 啟動 → 研究，但沒有回饋給 Scout

**實現方案：**
- 健康度計算：`健康度 = 1 - (卡住任務數 / 並發上限)`
- 動態調整啟動頻率：
  - 健康度 ≥ 0.75 → 65 秒
  - 健康度 0.50-0.75 → 120 秒
  - 健康度 < 0.50 → 300 秒
- 動態並發上限：
  - 健康度 < 0.50 → 降低到 2
  - 健康度 ≥ 0.50 → 恢復到 3

**腳本：** `kanban-ops/auto_spawn_heartbeat.py`（整合背壓邏輯）

**效果：** 系統健康度穩定在 0.67-1.00 之間

#### 2. 失敗任務上限和清理
**問題：** 失敗任務可能無限增長

**實現方案：**
- 最多保留 50 個失敗任務
- 每 24 小時清理超過 7 天的失敗任務
- 腳本：`kanban-ops/task_cleanup.py`

**效果：** 失敗任務數量穩定在 9 個（< 50 個閾值）

#### 3. Scout 掃描自動觸發
**整合點：** auto_spawn_heartbeat.py 檢查待辦任務數量

**觸發條件：** 待辦任務 < 5 個

**效果：** 自動維護待辦任務數量

---

### P2 優化：系統性問題（深度修復）

#### 1. 任務優先級系統整合
**問題：** 手動執行優先級規則，缺乏自動化

**實現方案：**
- 通過 subprocess 調用 `priority-rule-engine/scripts/apply_rules.py`
- 每次心跳在載入任務後執行優先級規則
- 重新載入 tasks.json 以獲取更新後的優先級

**修復的問題：**
- 退出碼邏輯錯誤：`sys.exit(0)`（總是成功退出）
- task["notes"] 類型問題：檢查並轉換字串為列表

**修改檔案：**
- `kanban-ops/auto_spawn_heartbeat.py` - 整合優先級規則引擎
- `skills/priority-rule-engine/scripts/apply_rules.py` - 修復退出碼和 notes 問題
- `skills/priority-rule-engine/__init__.py` - 新增 Python 包初始化文件

**效果：** 每次心跳自動應用優先級規則

#### 2. 修復持久 datetime 解析錯誤
**問題：** `task_state_rollback.py` 在計算任務持續時間時遇到錯誤：`can't subtract offset-naive and offset-aware datetimes`

**根本原因：**
- `datetime.now(timezone.utc)` 是時區感知的（offset-aware）
- 某些任務的時間戳沒有時區信息（如 `"2026-03-01T02:29:37.567065"`）
- offset-aware - offset-naive = 錯誤

**修復方案：**
```python
updated_time = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
# 如果沒有時區信息，假設是 UTC（修復 offset-naive 問題）
if updated_time.tzinfo is None:
    updated_time = updated_time.replace(tzinfo=timezone.utc)
elapsed = now - updated_time
```

**效果：**
- tw-double-confirm-1772332177 不再產生解析錯誤
- 正確計算 spawning 持續時間（5276 分鐘）
- 成功回滾到 pending 狀態

---

### 優化成果總結

| 指標 | 修改前 | 修改後 | 改善 |
|------|--------|--------|------|
| 卡住任務數 | 6 個 | 0 個 | ⬇️ 100% |
| 回滾時間 | 120 分鐘 | 45 分鐘 | ⬇️ 62.5% |
| 啟動頻率 | 固定 65 秒 | 動態 65-300 秒 | ✅ 自適應 |
| 健康度監控 | ❌ | ✅ | ✅ 新增 |
| 自我保護 | ❌ | ✅ | ✅ 新增 |
| 優先級調整 | 手動執行 | 每次心跳自動 | ✅ 自動化 |
| datetime 錯誤 | 每次心跳都出現 | 0 次 | ⬇️ 100% |

**當前系統狀態：**
- 健康度：1.00 (🟢 完全健康)
- 失敗任務數：9 個（< 50 個閾值）
- 卡住任務數：0 個
- 執行中任務：0-3 個（動態調整）

---

## 🚀 下一步優化

### Phase 2（未來考慮）
1. P3 行動：進一步優化（如更精細的資源分配）
2. 驗證背壓機制長期穩定性
3. 優化優先級規則引擎效率

### 立即可做
1. 修改 Grafana 默認密碼
2. 檢查 Dashboard 顯示
3. 探索 Prometheus 查詢語言

### 本週
1. 監控指標趨勢
2. 根據實際使用調整 Dashboard
3. 設置告警規則（可選）

### 未來擴展
1. 添加 Gateway metrics endpoint
2. 安裝 Node Exporter（系統指標）
3. 配置告警通知
4. 添加更多業務指標

---

**關鍵學習：**
- Event-driven 優於 cron 定時器
- 無狀態架構更易維護
- 監控指標是診斷和優化的關鍵
- **背壓機制是必需品**：可複用模式（監測 → 計算健康度 → 動態調整）
- **容量規劃**：不在 100% 容量運作，80% 是安全線，50% 是舒適線
- **系統成熟度**：卡住任務增加不是失敗，而是需要更精細控制的信號
