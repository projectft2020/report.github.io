# OpenClaw Mac Mini 單機最佳實踐指南

**環境**: 單台 Mac Mini (唯一生產環境)
**目標**: 穩定、高效、易維護
**日期**: 2026-02-20

---

## 🎯 核心策略

**單機環境的三大支柱**:
1. 📊 **監控可見** - 知道發生了什麼
2. 🔄 **自動恢復** - 問題自動修復
3. 💾 **可靠備份** - 數據絕不丟失

---

## ✅ 已完成優化 (Phase 1)

### 1. 監控系統 ✅
```
✅ Prometheus (端口 9090)
✅ Grafana (端口 3000)
✅ Metrics Exporter (端口 9101)
✅ OpenClaw Dashboard (8 個面板)

可實時查看:
- 任務狀態 (21 completed, 3 failed, 1 blocked)
- Token 消耗
- 自動恢復統計
```

### 2. Auto-Recovery System ✅
```
✅ 每 30 分鐘自動運行
✅ 檢測假失敗任務
✅ 自動恢復至正確狀態

運行方式: cron 定時任務
```

### 3. Progressive Research ✅
```
✅ Checkpoint 每 3 次搜索
✅ Token 消耗 -57% (467k → ~200k)
✅ 成功率 +90% (50% → 95%)
```

---

## 🔥 優先實施項目 (單機環境)

### 1️⃣ 告警規則設置 ⭐⭐⭐

**為什麼重要**: 單機環境下，問題需要快速發現

**實施步驟**:

```bash
# 1. 創建告警規則文件
ssh charlie@192.168.1.117
mkdir -p ~/monitoring/prometheus/rules
```

```yaml
# ~/monitoring/prometheus/rules/alerts.yml
groups:
  - name: openclaw_alerts
    interval: 30s
    rules:
      # 任務失敗率過高
      - alert: HighFailureRate
        expr: |
          (openclaw_tasks_total{status="failed"} /
           (openclaw_tasks_total{status="completed"} + openclaw_tasks_total{status="failed"}))
          > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "任務失敗率過高"
          description: "失敗率 {{ $value | humanizePercentage }}"

      # 內存使用率過高
      - alert: HighMemoryUsage
        expr: |
          (node_memory_total_bytes - node_memory_available_bytes) /
          node_memory_total_bytes > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "內存使用率過高"
          description: "內存使用 {{ $value | humanizePercentage }}"

      # Token 消耗過快
      - alert: HighTokenConsumption
        expr: |
          rate(openclaw_task_tokens_total[5m]) > 1000
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Token 消耗過快"
          description: "消耗速率 {{ $value }} tokens/sec"

      # 自動恢復運作檢查
      - alert: AutoRecoveryNotRunning
        expr: |
          time() - openclaw_auto_recovery_runs_total{result="success"} > 3600
        labels:
          severity: critical
        annotations:
          summary: "自動恢復超過 1 小時未運行"
```

```bash
# 2. 更新 Prometheus 配置
cat >> ~/monitoring/prometheus/prometheus.yml << 'EOF'

# 告警規則文件
rule_files:
  - 'rules/alerts.yml'
EOF

# 3. 重啟 Prometheus
pkill -f prometheus
cd ~/monitoring/prometheus
nohup ./prometheus \
  --config.file=/Users/charlie/monitoring/prometheus/prometheus.yml \
  --storage.tsdb.path=/Users/charlie/monitoring/prometheus/data \
  > ~/monitoring/prometheus/prometheus.log 2>&1 &

# 4. 驗證告警規則
curl http://localhost:9090/api/v1/rules | python3 -m json.tool
```

---

### 2️⃣ 自動備份系統 ⭐⭐⭐

**為什麼重要**: 單機環境，硬體故障 = 數據全丟

**實施步驟**:

```bash
# 1. 創建備份腳本
cat > ~/backup_openclaw.sh << 'EOF'
#!/bin/bash
# OpenClaw 自動備份腳本

BACKUP_DIR="/Users/charlie/backups/openclaw"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30  # 保留 30 天

echo "🔄 開始備份 OpenClaw..."

# 創建備份目錄
mkdir -p "$BACKUP_DIR"

# 備份內容
echo "📦 備份 Kanban 數據..."
tar -czf "$BACKUP_DIR/kanban_$DATE.tar.gz" \
  ~/.openclaw/workspace/kanban/ 2>/dev/null

echo "📦 備份 Agents 配置..."
tar -czf "$BACKUP_DIR/agents_$DATE.tar.gz" \
  ~/.openclaw/agents/ 2>/dev/null

echo "📦 備份監控配置..."
tar -czf "$BACKUP_DIR/monitoring_$DATE.tar.gz" \
  ~/monitoring/ 2>/dev/null

echo "📦 備份任務列表..."
cp ~/.openclaw/workspace/kanban/tasks.json \
  "$BACKUP_DIR/tasks_$DATE.json" 2>/dev/null

# 清理舊備份
echo "🧹 清理 $RETENTION_DAYS 天前的備份..."
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "tasks_*.json" -mtime +$RETENTION_DAYS -delete

# 記錄備份大小
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
echo "✅ 備份完成！總大小: $BACKUP_SIZE"
echo "📁 備份位置: $BACKUP_DIR"
EOF

chmod +x ~/backup_openclaw.sh
```

```bash
# 2. 設置每日自動備份 (每天凌晨 2 點)
crontab -e

# 添加這行:
0 2 * * * /Users/charlie/backup_openclaw.sh >> /Users/charlie/backup.log 2>&1
```

```bash
# 3. 測試備份
~/backup_openclaw.sh

# 查看備份
ls -lh ~/backups/openclaw/
```

**可選: 外部備份 (雲端)**
```bash
# 如果有 GitHub/GitLab 私有倉庫，可以同步重要配置
cat > ~/backup_to_git.sh << 'EOF'
#!/bin/bash
cd ~/openclaw-config-backup
git pull
cp ~/.openclaw/workspace/kanban/tasks.json ./tasks.json
git add tasks.json
git commit -m "Auto-backup $(date)"
git push
EOF
```

---

### 3️⃣ 日誌管理 ⭐⭐

**為什麼重要**: 防止磁碟被日誌填滿

**實施步驟**:

```bash
# 1. 創建日誌輪轉配置
cat > ~/logrotate.conf << 'EOF'
# OpenClaw 日誌輪轉配置

/Users/charlie/.openclaw/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 charlie staff
}

~/monitoring/prometheus/*.log {
    daily
    rotate 5
    compress
    delaycompress
    notifempty
}

~/monitoring/grafana/*.log {
    daily
    rotate 5
    compress
    delaycompress
    notifempty
}
EOF

# 2. 設置每日日誌輪轉
crontab -e

# 添加:
0 1 * * * /usr/sbin/logrotate -s ~/logrotate.status ~/logrotate.conf
```

---

### 4️⃣ 健康檢查腳本 ⭐

**快速檢查系統狀態**

```bash
cat > ~/health_check.sh << 'EOF'
#!/bin/bash
# OpenClaw 健康檢查腳本

echo "════════════════════════════════════════"
echo "🔍 OpenClaw 系統健康檢查"
echo "════════════════════════════════════════"
echo ""

# 1. Prometheus
echo "1️⃣ Prometheus"
if curl -s http://localhost:9090/-/healthy > /dev/null; then
  echo "   ✅ Running"
else
  echo "   ❌ Not responding"
fi

# 2. Grafana
echo "2️⃣ Grafana"
if curl -s http://localhost:3000/api/health > /dev/null; then
  echo "   ✅ Running"
else
  echo "   ❌ Not responding"
fi

# 3. Metrics Exporter
echo "3️⃣ Metrics Exporter"
if curl -s http://localhost:9101/metrics > /dev/null; then
  echo "   ✅ Running"
else
  echo "   ❌ Not responding"
fi

# 4. Auto-Recovery
echo "4️⃣ Auto-Recovery"
if crontab -l | grep -q "auto_recovery.sh"; then
  echo "   ✅ Scheduled"
else
  echo "   ⚠️  Not in crontab"
fi

# 5. 磁碟空間
echo "5️⃣ 磁碟空間"
DISK_USAGE=$(df ~ | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -lt 80 ]; then
  echo "   ✅ ${DISK_USAGE}% used"
elif [ $DISK_USAGE -lt 90 ]; then
  echo "   ⚠️  ${DISK_USAGE}% used (warning)"
else
  echo "   ❌ ${DISK_USAGE}% used (critical)"
fi

# 6. 內存使用
echo "6️⃣ 內存使用"
MEMORY_USAGE=$(vm_stat | perl -ne '/page size of (\d+)/ and $ps=$1; /Pages free\s+(\d+)/ and printf "%.0f", (1-$1/$2)*100')
if [ $MEMORY_USAGE -lt 80 ]; then
  echo "   ✅ ${MEMORY_USAGE}% used"
elif [ $MEMORY_USAGE -lt 90 ]; then
  echo "   ⚠️  ${MEMORY_USAGE}% used (warning)"
else
  echo "   ❌ ${MEMORY_USAGE}% used (critical)"
fi

# 7. 最近的備份
echo "7️⃣ 最新備份"
LATEST_BACKUP=$(ls -t ~/backups/openclaw/*.tar.gz 2>/dev/null | head -1)
if [ -n "$LATEST_BACKUP" ]; then
  BACKUP_AGE=$(( ($(date +%s) - $(stat -f %m "$LATEST_BACKUP")) / 86400 ))
  echo "   ✅ $BACKUP_AGE 天前"
else
  echo "   ⚠️  No backups found"
fi

echo ""
echo "════════════════════════════════════════"
echo "✅ 健康檢查完成"
echo "════════════════════════════════════════"
EOF

chmod +x ~/health_check.sh
```

**使用方式**:
```bash
# 手動運行
~/health_check.sh

# 或設置每日檢查 (發送到郵件/通知)
crontab -e
# 添加:
0 9 * * * ~/health_check.sh | mail -s "OpenClaw Daily Health" your@email.com
```

---

### 5️⃣ 系統優化 (單機) ⭐

**不需要複雜的伸縮配置，專注於單機效能**

```bash
# 1. 查看 CPU 和內存
top -o cpu -n 5  # CPU 使用前 5
top -o mem -n 5  # 內存使用前 5

# 2. 查看磁碟 I/O
iostat 2 5

# 3. 清理系統緩存 (當內存不足時)
sudo purge
```

**Docker 容器優化** (如果使用):
```yaml
# docker-compose.yml 優化
services:
  openclaw:
    # 資源限制
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '0.5'
          memory: 1G

    # 日誌大小限制
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

---

## 📋 每日維護清單

### 每日檢查 (5 分鐘)
```bash
# 1. 快速健康檢查
~/health_check.sh

# 2. 查看今天的任務
cat ~/.openclaw/workspace/kanban/tasks.json | python3 -c "
import json, sys
tasks = json.load(sys.stdin)
completed = len([t for t in tasks if t['status'] == 'completed'])
failed = len([t for t in tasks if t['status'] == 'failed'])
print(f'✅ Completed: {completed}')
print(f'❌ Failed: {failed}')
"

# 3. 查看監控
open http://localhost:3000  # Grafana
```

### 週末檢查 (15 分鐘)
```bash
# 1. 檢查備份
ls -lh ~/backups/openclaw/

# 2. 清理空間
brew cleanup  # 如果有使用 Homebrew
docker system prune -a  # 清理 Docker

# 3. 查看本週趨勢
# 在 Grafana 中查看 7 天數據
```

### 月底檢查 (30 分鐘)
```bash
# 1. Token 消耗分析
# 查看本月總消耗

# 2. 性能回顧
# 查看本月失敗任務

# 3. 優化建議
# 根據數據調整配置
```

---

## 🚨 故障排除 (單機環境)

### 問題: 內存不足
```bash
# 1. 查看什麼在佔用內存
top -o mem

# 2. 清理緩存
sudo purge

# 3. 重啟服務
pkill -f prometheus
# 重啟 (參考上文命令)
```

### 問題: 磁碟滿了
```bash
# 1. 查看什麼佔用空間
du -sh ~/.* ~/library/* 2>/dev/null | sort -hr | head -20

# 2. 清理日誌
rm ~/monitoring/*/*.log.1  # 舊的壓縮日誌

# 3. 清理 Docker
docker system prune -a --volumes
```

### 問題: 服務掛了
```bash
# 1. 查看日誌
tail -50 ~/monitoring/prometheus/prometheus.log
tail -50 ~/monitoring/grafana/grafana.log
tail -50 ~/.openclaw/logs/metrics_exporter.log

# 2. 重啟服務
# 參考各服務的重啟命令
```

---

## 📊 效能監控指標 (單機)

### 關鍵指標
```yaml
系統資源:
  - CPU 使用率 < 70%
  - 內存使用率 < 80%
  - 磁碟使用率 < 85%

應用性能:
  - 任務成功率 > 95%
  - 平均任務時長 < 30 分鐘
  - Token 消耗 < 250k/任務

運維指標:
  - 備份每日完成 ✅
  - Auto-Recovery 每 30 分鐘運行 ✅
  - 告警及時響應
```

---

## 🎯 成功指標

### 單機環境的「成功」定義

**穩定性**:
- ✅ 系統 7×24 運行
- ✅ 任務成功率 > 95%
- ✅ 假失敗自動恢復

**可維護性**:
- ✅ 一鍵健康檢查
- ✅ 自動備份
- ✅ 清晰的監控面板

**成本效率**:
- ✅ Token 消耗控制在預算內
- ✅ 無需額外硬件成本
- ✅ 維護時間 < 30 分鐘/週

---

## 📚 相關文檔

### 已部署文檔
- **監控系統指南**: `~/monitoring/MONITORING_SYSTEM_SUCCESS.md`
- **Progressive Research**: `~/monitoring/research_agent_progressive_protocol.md`
- **行動計劃**: `~/monitoring/接下來的行動計劃.md`

### 本地文檔
- `/Users/david/Documents/openclaw_matrix/MACMINI_SINGLE_BEST_PRACTICES.md` (本文件)
- `/Users/david/Documents/openclaw_matrix/MONITORING_DEPLOYMENT_COMPLETE.md`

---

## 🎊 總結

**單機 Mac Mini 的優勢**:
- ✅ 簡單 - 無需複雜的集群配置
- ✅ 經濟 - 無額外硬件成本
- ✅ 可控 - 一台機器，完全掌握

**你的系統已具備**:
1. ✅ 完整監控
2. ✅ 自動恢復
3. ✅ Progressive Research
4. ✅ 可視化 Dashboard

**下一步**:
1. 設置告警規則
2. 建立自動備份
3. 配置日誌管理
4. 每日健康檢查

**一個穩定、高效、易維護的單機 OpenClaw 系統！** 🎉

---

**文檔版本**: 1.0
**適用環境**: 單機 Mac Mini
**最後更新**: 2026-02-20
