#!/usr/bin/env python3
"""
Generate Timeout Alerts

Generate formatted alerts for timeout monitoring.
"""

import sys
import json
from pathlib import Path
import argparse
from datetime import datetime, timezone

KANBAN_DIR = Path.home() / ".openclaw" / "workspace" / "kanban"
TASKS_FILE = KANBAN_DIR / "tasks.json"

DEFAULT_ALERT_THRESHOLD = 12  # hours

def parse_task_time(task_time_str):
    """Parse task timestamp with timezone handling."""
    if not task_time_str:
        return None

    try:
        if "Z" in task_time_str or "+" in task_time_str or "-" in task_time_str[10:]:
            return datetime.fromisoformat(task_time_str.replace("Z", "+00:00"))
        else:
            dt = datetime.fromisoformat(task_time_str)
            return dt.replace(tzinfo=timezone.utc)
    except Exception as e:
        return None

def get_duration_hours(task_time_str):
    """Calculate duration in hours from task timestamp."""
    task_time = parse_task_time(task_time_str)
    if not task_time:
        return None

    now = datetime.now(timezone.utc)
    duration = (now - task_time).total_seconds() / 3600
    return duration

def check_timeouts(threshold=None):
    """Check for task timeouts.

    Args:
        threshold: Alert threshold in hours (default: 12)

    Returns:
        List of timeout tasks
    """
    if not TASKS_FILE.exists():
        return []

    try:
        with open(TASKS_FILE, "r") as f:
            tasks = json.load(f)
    except Exception as e:
        return []

    threshold = threshold if threshold else DEFAULT_ALERT_THRESHOLD
    timeout_tasks = []

    for task in tasks:
        task_status = task.get("status", "")
        task_id = task.get("id", "")

        # Skip completed/failed tasks
        if task_status in ["completed", "failed"]:
            continue

        # Get timestamp based on status
        if task_status == "spawning":
            time_str = task.get("updated_at")
        elif task_status == "in_progress":
            time_str = task.get("updated_at") or task.get("created_at")
        else:
            continue

        if not time_str:
            continue

        duration = get_duration_hours(time_str)

        if duration and duration > threshold:
            timeout_tasks.append({
                "id": task_id,
                "title": task.get("title", "")[:60],
                "status": task_status,
                "duration_hours": duration
            })

    return timeout_tasks

def generate_alert(timeout_tasks=None, threshold=None):
    """Generate formatted timeout alert.

    Args:
        timeout_tasks: List of timeout tasks (optional, will check if not provided)
        threshold: Alert threshold in hours

    Returns:
        Formatted alert message string
    """
    if timeout_tasks is None:
        timeout_tasks = check_timeouts(threshold=threshold)

    if not timeout_tasks:
        return "✅ 無超時任務警報"

    threshold = threshold if threshold else DEFAULT_ALERT_THRESHOLD

    alert_lines = [
        "=" * 60,
        f"⏰ 任務超時警報 (閾值: {threshold} 小時)",
        "=" * 60,
        "",
        f"📊 發現 {len(timeout_tasks)} 個超時任務",
        ""
    ]

    for i, task in enumerate(timeout_tasks[:10], 1):
        alert_lines.append(f"{i}. {task['id']}")
        alert_lines.append(f"   標題: {task['title']}")
        alert_lines.append(f"   狀態: {task['status']}")
        alert_lines.append(f"   持續時間: {task['duration_hours']:.1f} 小時")
        alert_lines.append("")

    if len(timeout_tasks) > 10:
        alert_lines.append(f"... 還有 {len(timeout_tasks) - 10} 個任務")
        alert_lines.append("")

    alert_lines.extend([
        "=" * 60,
        "💡 建議操作:",
        "",
        "1. 檢查任務執行情況",
        "2. 回滾卡住的 spawning 任務: python3 rollback_stuck.py",
        "3. 必要時調整超時閾值",
        "",
        f"📅 警報時間: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "=" * 60
    ])

    return "\n".join(alert_lines)

def display_alert(alert):
    """Display alert message."""
    print(alert)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate timeout alerts")
    parser.add_argument(
        "--threshold", "-t",
        type=float,
        help=f"Alert threshold in hours (default: {DEFAULT_ALERT_THRESHOLD})"
    )
    args = parser.parse_args()

    alert = generate_alert(threshold=args.threshold)
    display_alert(alert)

    sys.exit(0 if "無超時任務警報" in alert else 1)
