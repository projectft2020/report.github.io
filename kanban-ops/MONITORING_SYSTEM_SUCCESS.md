# 🔍 OpenClaw 監控系統部署完成

**日期**: 2026-02-20
**狀態**: ✅ **完全部署成功**

---

## 🎯 部署摘要

成功部署完整的 Prometheus + Grafana 監控系統，實時追蹤 OpenClaw 系統運行狀況。

---

## ✅ 已部署組件

### 1. Prometheus (指標存儲)
- **版本**: 2.48.0
- **端口**: 9090
- **狀態**: ✅ 運行中
- **位置**: ~/monitoring/prometheus/
- **PID**: 96040

**配置的採集目標**:
- Prometheus 自身 (localhost:9090)
- Kanban Metrics Exporter (localhost:9101)
- Node Exporter (localhost:9100) - 待安裝
- Gateway metrics (localhost:18790) - 待配置

### 2. Grafana (可視化)
- **版本**: 10.2.3
- **端口**: 3000
- **狀態**: ✅ 運行中
- **位置**: ~/monitoring/grafana/
- **訪問地址**: http://localhost:3000

**登入憑證**:
- **默認**: admin / admin
- **修改後**: admin / 2sEbyKR68N-MrD- (2026-03-03 22:49 GMT+8)
- **端口**: 3000
- **狀態**: ✅ 運行中
- **位置**: ~/monitoring/grafana/
- **PID**: 97069
- **默認登入**: admin / admin

**已配置**:
- ✅ Prometheus 數據源 (自動配置)
- ✅ OpenClaw System Dashboard (8 個面板)

### 3. Kanban Metrics Exporter (自定義指標)
- **端口**: 9101
- **狀態**: ✅ 運行中
- **位置**: ~/.openclaw/workspace/kanban-ops/kanban_metrics_exporter.py

**導出的指標**:
- 任務計數 (按狀態、按 agent)
- 任務完成時間 (直方圖)
- Token 消耗
- 自動恢復統計
- 假失敗檢測
- Progressive Research 統計

---

## 📊 Dashboard 面板

OpenClaw System Dashboard 包含 8 個可視化面板:

1. **Completed Tasks** - 已完成任務總數
2. **Failed Tasks** - 失敗任務總數
3. **Auto Recoveries** - 自動恢復次數
4. **False Failures Detected** - 檢測到的假失敗
5. **Tasks by Agent** - 按 agent 類型的任務分佈 (時序圖)
6. **Token Consumption Rate** - Token 消耗速率
7. **Task Duration (P95)** - 任務耗時 P95 百分位
8. **Tasks by Status** - 任務狀態分佈 (餅圖)

---

## 🚀 訪問監控系統

### 方式 1: 本地端口轉發 (推薦)

```bash
# 在本地機器執行
ssh -L 9090:localhost:9090 -L 3000:localhost:3000 charlie@192.168.1.117

# 然後在瀏覽器訪問:
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000
```

### 方式 2: 直接訪問 (在生產服務器上)

```bash
# Prometheus
http://localhost:9090

# Grafana (admin/admin)
http://localhost:3000
```

### 方式 3: 通過 SSH Tunnel

```bash
# 創建持久隧道
ssh -N -L 9090:localhost:9090 -L 3000:localhost:3000 charlie@192.168.1.117
```

---

## 📈 實時數據查看

### Prometheus 查詢範例

1. **查看所有指標**:
   ```promql
   {job="kanban-metrics"}
   ```

2. **任務成功率**:
   ```promql
   rate(openclaw_tasks_total{status="completed"}[5m]) /
   rate(openclaw_tasks_total[5m])
   ```

3. **Token 消耗趨勢**:
   ```promql
   rate(openclaw_task_tokens_total[5m])
   ```

4. **平均任務時長**:
   ```promql
   rate(openclaw_task_duration_minutes_sum[5m]) /
   rate(openclaw_task_duration_minutes_count[5m])
   ```

### Grafana 查看方式

1. 登入 Grafana (http://localhost:3000)
2. 首次登入需修改密碼
3. 選擇 "OpenClaw System Dashboard"
4. 實時查看所有指標

---

## 🔄 進程管理

### 查看運行狀態

```bash
ssh charlie@192.168.1.117

# Prometheus
ps aux | grep prometheus | grep -v grep

# Grafana
ps aux | grep "grafana server" | grep -v grep

# Metrics Exporter
ps aux | grep kanban_metrics_exporter | grep -v grep
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

## 📁 重要文件位置

### Prometheus
- 配置: `~/monitoring/prometheus/prometheus.yml`
- 數據: `~/monitoring/prometheus/data/`
- 日誌: `~/monitoring/prometheus/prometheus.log`

### Grafana
- 配置: `~/monitoring/grafana/conf/defaults.ini`
- 數據: `~/monitoring/grafana/data/`
- 日誌: `~/monitoring/grafana/grafana.log`
- Dashboard: `~/monitoring/grafana/provisioning/dashboards/`

### Metrics Exporter
- 腳本: `~/.openclaw/workspace/kanban-ops/kanban_metrics_exporter.py`
- 日誌: `~/.openclaw/logs/metrics_exporter.log`

---

## 🎯 當前收集的數據

根據首次採集結果：

### 任務狀態 (截至 2026-02-20)
- ✅ Completed: 21
- ❌ Failed: 3
- 🚫 Blocked: 1

### 按 Agent 分類
- Automation: 1 completed
- Analyst: 1 completed, 1 failed, 1 blocked
- Research: 1 completed, 1 failed
- Creative: 1 completed

---

## 🔧 自動啟動配置 (可選)

### 創建啟動腳本

```bash
cat > ~/start_monitoring.sh << 'EOF'
#!/bin/bash
# 啟動 OpenClaw 監控系統

echo "🚀 Starting OpenClaw Monitoring System..."

# Start Prometheus
if ! ps aux | grep prometheus | grep -v grep > /dev/null; then
  cd ~/monitoring/prometheus
  nohup ./prometheus --config.file=/Users/charlie/monitoring/prometheus/prometheus.yml \
    --storage.tsdb.path=/Users/charlie/monitoring/prometheus/data \
    > ~/monitoring/prometheus/prometheus.log 2>&1 &
  echo "✅ Prometheus started"
else
  echo "✓ Prometheus already running"
fi

# Start Grafana
if ! ps aux | grep "grafana server" | grep -v grep > /dev/null; then
  cd ~/monitoring/grafana
  nohup ./bin/grafana server --homepath=/Users/charlie/monitoring/grafana \
    --config=/Users/charlie/monitoring/grafana/conf/defaults.ini \
    > ~/monitoring/grafana/grafana.log 2>&1 &
  echo "✅ Grafana started"
else
  echo "✓ Grafana already running"
fi

# Start Metrics Exporter
if ! ps aux | grep kanban_metrics_exporter | grep -v grep > /dev/null; then
  cd ~/.openclaw/workspace/kanban-ops
  nohup python3 kanban_metrics_exporter.py \
    > ~/.openclaw/logs/metrics_exporter.log 2>&1 &
  echo "✅ Metrics Exporter started"
else
  echo "✓ Metrics Exporter already running"
fi

echo ""
echo "✅ All monitoring components started!"
echo "Prometheus: http://localhost:9090"
echo "Grafana: http://localhost:3000"
EOF

chmod +x ~/start_monitoring.sh
```

### 添加到 crontab (自動啟動)

```bash
crontab -e

# 添加：
@reboot /Users/charlie/start_monitoring.sh
```

---

## 🎊 成功指標

✅ **部署完成**
- Prometheus: 運行正常
- Grafana: 運行正常
- Metrics Exporter: 運行正常
- Dashboard: 已加載

✅ **數據採集**
- 實時任務統計
- Token 消耗追蹤
- 自動恢復監控
- Progressive Research 追蹤

✅ **可視化**
- 8 個監控面板
- 實時數據更新 (30秒)
- 歷史數據查詢

---

## 📝 下一步建議

### 立即可做
1. ✅ 通過端口轉發訪問 Grafana
2. ✅ 修改 Grafana 默認密碼
3. ✅ 查看 Dashboard 顯示
4. ✅ 探索 Prometheus 查詢語言

### 本週
1. 監控指標趨勢
2. 根據實際使用調整 Dashboard
3. 設置告警規則 (可選)

### 未來擴展
1. 添加 Gateway metrics endpoint
2. 安裝 Node Exporter (系統指標)
3. 配置告警通知
4. 添加更多業務指標

---

## 📚 參考文檔

- **Prometheus 查詢語言**: https://prometheus.io/docs/prometheus/latest/querying/basics/
- **Grafana Dashboard**: https://grafana.com/docs/grafana/latest/dashboards/
- **Prometheus 配置**: https://prometheus.io/docs/prometheus/latest/configuration/configuration/

---

**創建時間**: 2026-02-20 22:35
**狀態**: ✅ 完全運行
**維護**: OpenClaw DevOps Team
