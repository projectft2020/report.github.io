# Monitoring

> **Category:** 監控系統部署、Prometheus、Grafana、Dashboard、指標導出
> **Source:** MEMORY.md 2026-02-20 to 2026-02-21
> **Last Updated:** 2026-02-23

---

## 🚀 監控系統部署

### 完成時間：2026-02-20
**狀態：** ✅ 完全部署成功

### 組件

| 組件 | 版本 | 端口 | PID | 狀態 |
|------|------|------|-----|------|
| **Prometheus** | 2.48.0 | 9090 | 96040 | ✅ 運行中 |
| **Grafana** | 10.2.3 | 3000 | 97069 | ✅ 運行中 |
| **Kanban Metrics Exporter** | - | 9101 | 96598 | ✅ 運行中 |

---

## 📊 Kanban Metrics Exporter

### 導出器位置
**路徑：** `/Users/charlie/.openclaw/workspace/kanban-ops/kanban_metrics_exporter.py`

### 核心指標

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
- `openclaw_auto_recoveries_total{confidence}` - 自動恢復次數（按置信度）
- `openclaw_auto_recovery_recovered_tasks` - 恢復的任務數量

#### 5. Progressive Research
- `openclaw_progressive_research_checkpoints{task_id}` - 檢查點數量
- `openclaw_progressive_research_searches_total{task_id}` - 搜索總數

---

## 📈 Grafana Dashboard

### Dashboard 名稱
**名稱：** OpenClaw System Dashboard
**面板數量：** 8 個

### 面板列表

#### 1. Completed Tasks
- **類型：** Stat Panel
- **指標：** `openclaw_tasks_total{status="completed"}`
- **目的：** 顯示已完成任務總數

#### 2. Failed Tasks
- **類型：** Stat Panel
- **指標：** `openclaw_tasks_total{status="failed"}`
- **目的：** 顯示失敗任務總數

#### 3. Auto Recoveries
- **類型：** Stat Panel
- **指標：** `openclaw_auto_recoveries_total`
- **目的：** 顯示自動恢復次數

#### 4. False Failures Detected
- **類型：** Stat Panel
- **指標：** `openclaw_false_failures_total`
- **目的：** 顯示檢測到的假失敗數

#### 5. Tasks by Agent
- **類型：** Time Series
- **指標：** `openclaw_tasks_by_agent{agent, status}`
- **目的：** 按 agent 類型的任務分佈（時序圖）

#### 6. Token Consumption Rate
- **類型：** Graph Panel
- **指標：** `rate(openclaw_task_tokens_total[5m])`
- **目的：** Token 消耗速率

#### 7. Task Duration (P95)
- **類型：** Stat Panel
- **指標：** `histogram_quantile(openclaw_task_duration_minutes, 0.95)`
- **目的：** 任務耗時 P95 百分位

#### 8. Tasks by Status
- **類型：** Pie Chart
- **指標：** `openclaw_tasks_total{status}`
- **目的：** 任務狀態分佈（餅圖）

---

## 🏹 Prometheus 配置

### 配置文件
**位置：** `/Users/charlie/monitoring/prometheus/prometheus.yml`

### 採集目標
1. **Prometheus 自身** (localhost:9090)
2. **OpenClaw Gateway** (localhost:18790) - 待配置
3. **Kanban Metrics** (localhost:9101) - ✅ 運行中

### 採集頻率
- **頻率：** 每 15 秒

---

## 🌐 訪問方式

### SSH 端口轉發（推薦）
```bash
ssh -L 9090:localhost:9090 -L 3000:localhost:3000 charlie@192.168.1.117
```

### 瀏覽器訪問
- **Prometheus：** http://localhost:9090
- **Grafana：** http://localhost:3000

### Grafana 默認密碼
- **用戶名：** admin
- **密碼：** admin（首次登入需修改）

---

## 📈 當前系統數據（2026-02-20 22:43）

### 任務統計
- **Completed：** 483
- **Failed：** 72
- **Blocked：** 23
- **總計：** 578 個任務

### 按 Agent 分類
- **Automation：** 1 completed
- **Analyst：** 1 completed, 1 failed, 1 blocked
- **Research：** 1 completed, 1 failed

---

## 🚨 通過監控可發現的問題

### 1. Gateway Timeout 問題
- **監控：** `openclaw_auto_recoveries_total` 遞增
- **原因：** announce 超時導致任務完成但未通知
- **解決：** 檢查 Gateway 日誌，優化超時機制

### 2. 假失敗檢測
- **監控：** `openclaw_false_failures_total` > 0
- **原因：** 子代理被終止但輸出完整
- **解決：** 自動恢復系統已部署

### 3. Token 消耗異常
- **監控：** `rate(openclaw_task_tokens_total[5m])` 飙升
- **原因：** 研究 agent token 爆炸（467k）
- **解決：** 使用漸進式研究協議

### 4. 任務執行時間異常
- **監控：** `openclaw_task_duration_minutes` P95 過高
- **原因：** 任務複雜度超出預期
- **解決：** 任務分解或調整模型

### 5. Agent 可靠性問題
- **監控：** 按 agent 的失敗率
- **原因：** 某個 agent 不可靠（automation 代理 0% 可靠）
- **解決：** 切換到可靠 agent（research/analyst）

---

## 🔧 進程管理

### 查看運行狀態
```bash
ps aux | grep -E "(prometheus|grafana|kanban_metrics_exporter)" | grep -v grep
```

### 重啟服務
```bash
# Prometheus
pkill -f prometheus
cd ~/monitoring/prometheus
nohup ./prometheus --config.file=/Users/charlie/monitoring/prometheus/prometheus.yml \
  --storage.tsdb.path=/Users/charlie/monitoring/prometheus/data \
  > ~/monitoring/prometheus/prometheus.log 2>&1 &

# Grafana
pkill -f "grafana server"
cd ~/monitoring/grafana
nohup ./bin/grafana server --homepath=/Users/charlie/monitoring/grafana \
  --config=/Users/charlie/monitoring/grafana/conf/defaults.ini \
  > ~/monitoring/grafana/grafana.log 2>&1 &

# Metrics Exporter
pkill -f kanban_metrics_exporter
cd ~/.openclaw/workspace/kanban-ops
nohup python3 kanban_metrics_exporter.py \
  > ~/.openclaw/logs/metrics_exporter.log 2>&1 &
```

---

## 📝 Prometheus 查詢範例

### 任務成功率
```promql
rate(openclaw_tasks_total{status="completed"}[5m]) /
rate(openclaw_tasks_total[5m])
```

### 按時間的任務分佈
```promql
openclaw_tasks_by_agent
```

### Token 消耗速率
```promql
rate(openclaw_task_tokens_total[5m])
```

### 平均任務時長
```promql
rate(openclaw_task_duration_minutes_sum[5m]) /
rate(openclaw_task_duration_minutes_count[5m])
```

---

## 🚀 下一步優化

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

**關鍵洞察：**
- 監控系統是診斷和優化的關鍵
- Prometheus + Grafana 組合提供了完整的可視化解決方案
- Dashboard 設計應該聚焦於可執行的洞察
- 指標命名應該清晰一致（openclaw_ 前綴）
