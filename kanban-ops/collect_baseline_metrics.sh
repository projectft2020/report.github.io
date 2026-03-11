#!/bin/bash
#
# collect_baseline_metrics.sh
#
# 收集基準數據用於系統優化決策
#
# 使用方法：
#   ./collect_baseline_metrics.sh --days 7
#   ./collect_baseline_metrics.sh --hours 24
#   ./collect_baseline_metrics.sh --from 2026-02-25 --to 2026-03-03
#

set -e

# 默認參數
DAYS=7
HOURS=""
FROM_DATE=""
TO_DATE=""

# 工作目錄
WORKSPACE_ROOT="${HOME}/.openclaw/workspace"
METRICS_DIR="${WORKSPACE_ROOT}/metrics/baseline"
DATA_FILE="${METRICS_DIR}/baseline_metrics_$(date +%Y%m%d_%H%M%S).json"

# 解析參數
while [[ $# -gt 0 ]]; do
    case $1 in
        --days)
            DAYS="$2"
            shift 2
            ;;
        --hours)
            HOURS="$2"
            shift 2
            ;;
        --from)
            FROM_DATE="$2"
            shift 2
            ;;
        --to)
            TO_DATE="$2"
            shift 2
            ;;
        -h|--help)
            echo "使用方法："
            echo "  $0 --days 7          # 收集過去 7 天的數據"
            echo "  $0 --hours 24        # 收集過去 24 小時的數據"
            echo "  $0 --from 2026-02-25 --to 2026-03-03  # 收集指定日期範圍的數據"
            exit 0
            ;;
        *)
            echo "未知參數: $1"
            echo "使用 -h 或 --help 查看幫助"
            exit 1
            ;;
    esac
done

# 計算時間範圍
if [[ -n "$FROM_DATE" && -n "$TO_DATE" ]]; then
    # 使用指定的日期範圍
    START_DATE=$(date -j -f "%Y-%m-%d" "$FROM_DATE" +"%Y-%m-%d")
    END_DATE=$(date -j -f "%Y-%m-%d" "$TO_DATE" +"%Y-%m-%d")
elif [[ -n "$HOURS" ]]; then
    # 使用小時數 (Python 計算)
    START_DATE=$(python3 -c "from datetime import datetime, timedelta; print((datetime.now() - timedelta(hours=${HOURS})).strftime('%Y-%m-%d'))")
    END_DATE=$(date +"%Y-%m-%d")
else
    # 使用天數（默認，Python 計算）
    START_DATE=$(python3 -c "from datetime import datetime, timedelta; print((datetime.now() - timedelta(days=${DAYS})).strftime('%Y-%m-%d'))")
    END_DATE=$(date +"%Y-%m-%d")
fi

echo "============================================================"
echo "📊 基準數據收集"
echo "============================================================"
echo "時間範圍: ${START_DATE} 至 ${END_DATE}"
echo "輸出文件: ${DATA_FILE}"
echo ""

# 創建目錄
mkdir -p "${METRICS_DIR}"

# 導出環境變量供 Python 腳本使用
export START_DATE
export END_DATE
export DATA_FILE

# Python 腳本來收集數據
python3 - <<'PYTHON_SCRIPT'
import json
import os
import subprocess
import re
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import statistics

# 配置
WORKSPACE_ROOT = Path.home() / ".openclaw" / "workspace"
DATA_FILE = Path(os.environ['DATA_FILE'])
START_DATE = datetime.strptime(os.environ['START_DATE'], '%Y-%m-%d')
END_DATE = datetime.strptime(os.environ['END_DATE'], '%Y-%m-%d')

# 存儲所有指標
metrics = {
    'collection_info': {
        'start_date': START_DATE.isoformat(),
        'end_date': END_DATE.isoformat(),
        'collected_at': datetime.now().isoformat(),
    },
    'heartbeat': {},
    'monitoring': {},
    'tasks': {},
    'scout': {},
}

print("📈 收集心跳指標...")

# 1. 心跳執行時間
# 從心跳日誌中提取執行時間
heartbeat_log = WORKSPACE_ROOT / "kanban-ops" / "heartbeat.log"
if heartbeat_log.exists():
    heartbeat_times = []
    with open(heartbeat_log, 'r', encoding='utf-8') as f:
        for line in f:
            # 查找執行時間模式
            match = re.search(r'執行時間: ([\d.]+)秒', line)
            if match:
                heartbeat_times.append(float(match.group(1)))

    if heartbeat_times:
        metrics['heartbeat']['execution_times'] = {
            'count': len(heartbeat_times),
            'min': min(heartbeat_times),
            'max': max(heartbeat_times),
            'mean': statistics.mean(heartbeat_times),
            'median': statistics.median(heartbeat_times),
            'p95': statistics.quantiles(heartbeat_times, n=20)[18] if len(heartbeat_times) > 20 else max(heartbeat_times),
            'p99': statistics.quantiles(heartbeat_times, n=100)[98] if len(heartbeat_times) > 100 else max(heartbeat_times),
        }
        print(f"  ✓ 收集到 {len(heartbeat_times)} 條心跳記錄")
        print(f"  - 平均: {metrics['heartbeat']['execution_times']['mean']:.2f}秒")
        print(f"  - P95: {metrics['heartbeat']['execution_times']['p95']:.2f}秒")
        print(f"  - P99: {metrics['heartbeat']['execution_times']['p99']:.2f}秒")
    else:
        print(f"  ⚠️ 未找到心跳執行時間記錄")
else:
    print(f"  ⚠️ 心跳日誌不存在")

print("")
print("📈 收集監控指標...")

# 2. 監控告警
# 從 Prometheus/Grafana 日誌中提取告警信息
prometheus_log = Path.home() / "monitoring" / "logs" / "prometheus.log"
alerts = defaultdict(lambda: defaultdict(int))

if prometheus_log.exists():
    with open(prometheus_log, 'r', encoding='utf-8') as f:
        for line in f:
            # 查找告警觸發模式
            if 'ALERT' in line or 'Alert' in line:
                # 提取告警類型
                match = re.search(r'alertname="([^"]+)"', line)
                if match:
                    alert_name = match.group(1)
                    alerts[alert_name]['total'] += 1

if alerts:
    metrics['monitoring']['alerts'] = {k: dict(v) for k, v in alerts.items()}
    total_alerts = sum(v['total'] for v in alerts.values())
    print(f"  ✓ 收集到 {len(alerts)} 種告警類型")
    print(f"  - 總觸發次數: {total_alerts}")
    for alert_name, alert_data in alerts.items():
        print(f"  - {alert_name}: {alert_data['total']} 次")
else:
    print(f"  ⚠️ 未找到告警記錄")

print("")
print("📈 收集任務指標...")

# 3. 任務狀態轉換
tasks_file = WORKSPACE_ROOT / "kanban" / "tasks.json"
if tasks_file.exists():
    with open(tasks_file, 'r', encoding='utf-8') as f:
        tasks_data = json.load(f)

    # 處理多種格式
    if isinstance(tasks_data, dict):
        if 'tasks' in tasks_data:
            tasks = tasks_data['tasks']
        else:
            tasks = list(tasks_data.values())
    elif isinstance(tasks_data, list):
        tasks = tasks_data
    else:
        tasks = []

    # 統計任務狀態
    status_counts = defaultdict(int)
    for task in tasks:
        status = task.get('status', 'unknown')
        status_counts[status] += 1

    metrics['tasks']['status_distribution'] = dict(status_counts)
    metrics['tasks']['total'] = len(tasks)

    print(f"  ✓ 收集到 {len(tasks)} 個任務")
    print(f"  - 狀態分佈:")
    for status, count in status_counts.items():
        print(f"    - {status}: {count}")
else:
    print(f"  ⚠️ 任務文件不存在")

print("")
print("📈 收集 Scout 指標...")

# 4. Scout 死鎖次數
scout_log = Path.home() / ".openclaw" / "workspace-scout" / "SCAN_LOG.md"
stuck_count = 0

if scout_log.exists():
    with open(scout_log, 'r', encoding='utf-8') as f:
        content = f.read()
        # 查找卡住任務的記錄
        stuck_count = len(re.findall(r'卡住任務|stuck task', content, re.IGNORECASE))

metrics['scout']['stuck_count'] = stuck_count
print(f"  ✓ 收集到 Scout 數據")
print(f"  - 卡住任務次數: {stuck_count}")

print("")
print("💾 保存數據...")

# 保存到 JSON 文件
DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
with open(DATA_FILE, 'w', encoding='utf-8') as f:
    json.dump(metrics, f, indent=2, ensure_ascii=False)

print(f"✅ 基準數據已保存到: {DATA_FILE}")

print("")
print("============================================================")
print("📊 基準數據收集完成")
print("============================================================")
print("")
print("📋 數據摘要:")
print(f"  時間範圍: {START_DATE.strftime('%Y-%m-%d')} 至 {END_DATE.strftime('%Y-%m-%d')}")
if 'execution_times' in metrics['heartbeat']:
    print(f"  心跳平均時間: {metrics['heartbeat']['execution_times']['mean']:.2f}秒")
if 'alerts' in metrics['monitoring']:
    total_alerts = sum(v['total'] for v in metrics['monitoring']['alerts'].values())
    print(f"  監控告警次數: {total_alerts}")
if 'status_distribution' in metrics['tasks']:
    print(f"  任務總數: {metrics['tasks']['total']}")
print(f"  Scout 卡住次數: {metrics['scout']['stuck_count']}")

PYTHON_SCRIPT

echo ""
echo "✅ 完成！"
