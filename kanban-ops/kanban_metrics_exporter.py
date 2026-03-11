#!/usr/bin/env python3
"""
OpenClaw Kanban Metrics Exporter
導出 Prometheus 格式的業務指標

追蹤指標:
- 任務計數和狀態
- 任務完成時間
- Token 消耗
- 自動恢復統計
- 假失敗檢測
"""

import json
import time
import sys
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

# ============================================================================
# Prometheus Metrics
# ============================================================================

class Metric:
    """Prometheus metric 基類"""
    def __init__(self, name, help_text, type_='gauge'):
        self.name = name
        self.help_text = help_text
        self.type_ = type_
        self.labels = {}
        self.value = 0

    def set(self, value, **labels):
        self.value = value
        self.labels = labels

    def inc(self, amount=1, **labels):
        self.value += amount
        self.labels = labels

    def observe(self, value, **labels):
        self.value = value
        self.labels = labels

    def format_prometheus(self):
        """格式化為 Prometheus 輸出格式"""
        labels_str = ''
        if self.labels:
            labels_str = '{' + ', '.join([f'{k}="{v}"' for k, v in self.labels.items()]) + '}'

        output = []
        output.append(f'# HELP {self.name} {self.help_text}')
        output.append(f'# TYPE {self.name} {self.type_}')
        output.append(f'{self.name}{labels_str} {self.value}')
        return '\n'.join(output)


class Counter(Metric):
    """Counter 計數器"""
    def __init__(self, name, help_text, labels=None):
        super().__init__(name, help_text, 'counter')
        self.label_names = labels or []
        self.metrics = {}

    def inc(self, amount=1, **labels):
        key = tuple(sorted(labels.items())) if labels else ()
        if key not in self.metrics:
            self.metrics[key] = 0
        self.metrics[key] += amount

    def format_prometheus(self):
        output = []
        output.append(f'# HELP {self.name} {self.help_text}')
        output.append(f'# TYPE {self.name} counter')

        for key, value in self.metrics.items():
            labels_dict = dict(key) if key else {}
            labels_str = ''
            if labels_dict:
                labels_str = '{' + ', '.join([f'{k}="{v}"' for k, v in labels_dict.items()]) + '}'
            output.append(f'{self.name}{labels_str} {value}')

        return '\n'.join(output)


class Gauge(Metric):
    """Gauge 測量值"""
    def __init__(self, name, help_text, labels=None):
        super().__init__(name, help_text, 'gauge')
        self.label_names = labels or []
        self.metrics = {}

    def set(self, value, **labels):
        key = tuple(sorted(labels.items())) if labels else ()
        self.metrics[key] = value

    def inc(self, amount=1, **labels):
        key = tuple(sorted(labels.items())) if labels else ()
        if key not in self.metrics:
            self.metrics[key] = 0
        self.metrics[key] += amount

    def format_prometheus(self):
        output = []
        output.append(f'# HELP {self.name} {self.help_text}')
        output.append(f'# TYPE {self.name} gauge')

        for key, value in self.metrics.items():
            labels_dict = dict(key) if key else {}
            labels_str = ''
            if labels_dict:
                labels_str = '{' + ', '.join([f'{k}="{v}"' for k, v in labels_dict.items()]) + '}'
            output.append(f'{self.name}{labels_str} {value}')

        return '\n'.join(output)


class Histogram(Metric):
    """Histogram 直方圖"""
    def __init__(self, name, help_text, buckets=None, labels=None):
        super().__init__(name, help_text, 'histogram')
        self.label_names = labels or []
        self.buckets = buckets or [1, 5, 10, 25, 50, 100, 250, 500, 1000]
        self.metrics = {}

    def observe(self, value, **labels):
        key = tuple(sorted(labels.items())) if labels else ()
        if key not in self.metrics:
            self.metrics[key] = {'sum': 0, 'count': 0, 'buckets': {b: 0 for b in self.buckets}}

        self.metrics[key]['sum'] += value
        self.metrics[key]['count'] += 1
        for bucket in self.buckets:
            if value <= bucket:
                self.metrics[key]['buckets'][bucket] += 1

    def format_prometheus(self):
        output = []
        output.append(f'# HELP {self.name} {self.help_text}')
        output.append(f'# TYPE {self.name} histogram')

        for key, data in self.metrics.items():
            labels_dict = dict(key) if key else {}
            labels_str = ''
            if labels_dict:
                labels_str = '{' + ', '.join([f'{k}="{v}"' for k, v in labels_dict.items()]) + '}'

            # Bucket 指標
            cumulative = 0
            for bucket in sorted(self.buckets):
                cumulative += data['buckets'][bucket]
                output.append(f'{self.name}_bucket{{le="{bucket}"{labels_str}}} {cumulative}')

            # +Inf bucket
            output.append(f'{self.name}_bucket{{le="+Inf"{labels_str}}} {data["count"]}')
            output.append(f'{self.name}_sum{labels_str} {data["sum"]}')
            output.append(f'{self.name}_count{labels_str} {data["count"]}')

        return '\n'.join(output)


# ============================================================================
# OpenClaw 指標定義
# ============================================================================

# 任務計數
tasks_total = Counter('openclaw_tasks_total', 'Total tasks', ['status'])
tasks_by_agent = Gauge('openclaw_tasks_by_agent', 'Tasks by agent type', ['agent', 'status'])

# 任務時長
task_duration_minutes = Histogram(
    'openclaw_task_duration_minutes',
    'Task duration in minutes',
    buckets=[1, 5, 10, 15, 20, 30, 45, 60, 90, 120, 180, 240],
    labels=['agent']
)

# Token 消耗
task_tokens_total = Counter(
    'openclaw_task_tokens_total',
    'Total tokens consumed',
    ['agent', 'direction']
)

# 假失敗檢測
false_failures_total = Counter('openclaw_false_failures_total', 'Total false failures detected')

# 自動恢復
auto_recoveries_total = Counter('openclaw_auto_recoveries_total', 'Total auto recoveries', ['confidence'])

# Progressive Research 統計
progressive_research_checkpoints = Gauge(
    'openclaw_progressive_research_checkpoints',
    'Number of checkpoints created',
    ['task_id']
)

progressive_research_searches = Counter(
    'openclaw_progressive_research_searches_total',
    'Total research searches',
    ['task_id', 'status']
)

# Auto-Recovery 運行統計
auto_recovery_runs = Counter('openclaw_auto_recovery_runs_total', 'Auto recovery runs', ['result'])
auto_recovery_recovered_tasks = Gauge(
    'openclaw_auto_recovery_recovered_tasks',
    'Number of tasks recovered by auto-recovery'
)


# ============================================================================
# 數據採集
# ============================================================================

def collect_kanban_metrics(tasks_json_path: str):
    """從 tasks.json 採集指標"""
    try:
        with open(tasks_json_path, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
    except Exception as e:
        print(f"Error reading tasks.json: {e}", file=sys.stderr)
        return

    # 重置 gauge 指標
    tasks_by_agent.metrics = {}
    progressive_research_checkpoints.metrics = {}
    auto_recovery_recovered_tasks.metrics = {}

    for task in tasks:
        status = task.get('status', 'unknown')
        agent = task.get('agent', 'unknown')
        task_id = task.get('id', 'unknown')

        # 任務計數
        tasks_total.inc(status=status)
        tasks_by_agent.set(
            tasks_by_agent.metrics.get((agent, status), 0) + 1,
            agent=agent,
            status=status
        )

        # 如果已完成，記錄時長和 token
        if status == 'completed':
            time_tracking = task.get('time_tracking', {})

            # 時長
            if 'actual_time_minutes' in time_tracking:
                duration = time_tracking.get('actual_time_minutes')
                if duration is not None and isinstance(duration, (int, float)):
                    task_duration_minutes.observe(
                        duration,
                        agent=agent
                    )

            # Token
            if 'token_usage' in task:
                token_usage = task['token_usage']
                task_tokens_total.inc(
                    token_usage.get('input', 0),
                    agent=agent,
                    direction='input'
                )
                task_tokens_total.inc(
                    token_usage.get('output', 0),
                    agent=agent,
                    direction='output'
                )

            # 自動恢復
            if time_tracking.get('auto_recovered'):
                confidence = time_tracking.get('recovery_confidence', 'unknown')
                auto_recoveries_total.inc(confidence=confidence)

            # 假失敗檢測
            if time_tracking.get('false_failure_detected'):
                false_failures_total.inc()

        # Progressive Research 檢查點統計
        if 'progressive_research' in task:
            pr_data = task['progressive_research']
            if 'checkpoint_count' in pr_data:
                progressive_research_checkpoints.set(
                    pr_data['checkpoint_count'],
                    task_id=task_id
                )
            if 'search_count' in pr_data:
                progressive_research_searches.inc(
                    pr_data['search_count'],
                    task_id=task_id,
                    status='completed'
                )


def collect_auto_recovery_metrics(log_path: str):
    """從 auto-recovery 日誌採集指標"""
    try:
        with open(log_path, 'r') as f:
            log_content = f.read()

        # 簡單統計：計算成功運行的次數
        success_count = log_content.count('✅ Auto-recovery completed')
        error_count = log_content.count('❌ Auto-recovery failed')

        auto_recovery_runs.inc(success_count, result='success')
        auto_recovery_runs.inc(error_count, result='error')

        # 統計恢復的任務數（需要解析日誌）
        recovered_count = log_content.count('Recovered task:')
        auto_recovery_recovered_tasks.set(recovered_count)

    except Exception as e:
        print(f"Error reading auto-recovery log: {e}", file=sys.stderr)


# ============================================================================
# HTTP Server
# ============================================================================

class MetricsHandler(BaseHTTPRequestHandler):
    """處理 /metrics 請求"""

    def do_GET(self):
        parsed_path = urlparse(self.path)

        if parsed_path.path == '/metrics':
            # 採集最新指標
            collect_kanban_metrics(TASKS_JSON_PATH)
            collect_auto_recovery_metrics(AUTO_RECOVERY_LOG_PATH)

            # 生成 Prometheus 格式輸出
            output = []
            output.append('# OpenClaw Kanban Metrics Exporter')
            output.append(f'# Generated at: {datetime.now().isoformat()}')
            output.append('')

            # 所有指標
            metrics = [
                tasks_total,
                tasks_by_agent,
                task_duration_minutes,
                task_tokens_total,
                false_failures_total,
                auto_recoveries_total,
                progressive_research_checkpoints,
                progressive_research_searches,
                auto_recovery_runs,
                auto_recovery_recovered_tasks,
            ]

            for metric in metrics:
                output.append(metric.format_prometheus())
                output.append('')

            # 發送響應
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write('\n'.join(output).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """禁用默認日誌輸出"""
        pass


# ============================================================================
# 主程序
# ============================================================================

def run_metrics_server(port: int):
    """運行指標 HTTP 服務器"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, MetricsHandler)
    print(f"✅ OpenClaw Metrics Exporter started on port {port}", flush=True)
    print(f"   Metrics endpoint: http://localhost:{port}/metrics", flush=True)
    httpd.serve_forever()


if __name__ == '__main__':
    # 配置
    METRICS_PORT = 9101
    TASKS_JSON_PATH = '/Users/charlie/.openclaw/workspace/kanban/tasks.json'
    AUTO_RECOVERY_LOG_PATH = '/Users/charlie/.openclaw/logs/auto_recovery.log'

    print("=" * 60)
    print("🔬 OpenClaw Kanban Metrics Exporter")
    print("=" * 60)
    print(f"Port: {METRICS_PORT}")
    print(f"Tasks JSON: {TASKS_JSON_PATH}")
    print(f"Auto-Recovery Log: {AUTO_RECOVERY_LOG_PATH}")
    print("=" * 60)

    run_metrics_server(METRICS_PORT)
