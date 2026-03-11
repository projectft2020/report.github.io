#!/usr/bin/env python3
"""
Check Task Timeouts

Scan tasks.json for tasks that have exceeded timeout thresholds.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone
import argparse

KANBAN_DIR = Path.home() / ".openclaw" / "workspace" / "kanban"
TASKS_FILE = KANBAN_DIR / "tasks.json"

DEFAULT_TIMEOUT_HOURS = {
    "spawning": 2,
    "in_progress": 24
}

def parse_task_time(task_time_str):
    """Parse task timestamp with timezone handling."""
    if not task_time_str:
        return None

    try:
        # Try ISO format with timezone
        if "Z" in task_time_str or "+" in task_time_str or "-" in task_time_str[10:]:
            return datetime.fromisoformat(task_time_str.replace("Z", "+00:00"))
        else:
            # Naive datetime - assume UTC
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

def check_timeouts(hours=None, status=None):
    """Check for task timeouts.

    Args:
        hours: Timeout threshold in hours (default: 24)
        status: Filter by status (spawning, in_progress, or all)

    Returns:
        List of timeout tasks with details
    """
    if not TASKS_FILE.exists():
        print(f"❌ tasks.json 不存在: {TASKS_FILE}")
        return []

    try:
        with open(TASKS_FILE, "r") as f:
            tasks = json.load(f)
    except Exception as e:
        print(f"❌ 讀取 tasks.json 失敗: {e}")
        return []

    timeout_tasks = []

    for task in tasks:
        task_status = task.get("status", "")
        task_id = task.get("id", "")
        task_title = task.get("title", "")[:50]

        # Filter by status if specified
        if status and task_status != status:
            continue

        # Skip completed/failed tasks
        if task_status in ["completed", "failed"]:
            continue

        # Get timestamp based on status
        if task_status == "spawning":
            time_str = task.get("updated_at")
            threshold = hours if hours else DEFAULT_TIMEOUT_HOURS["spawning"]
        elif task_status == "in_progress":
            time_str = task.get("updated_at") or task.get("created_at")
            threshold = hours if hours else DEFAULT_TIMEOUT_HOURS["in_progress"]
        else:
            continue

        if not time_str:
            continue

        duration = get_duration_hours(time_str)

        if duration and duration > threshold:
            timeout_tasks.append({
                "id": task_id,
                "title": task_title,
                "status": task_status,
                "duration_hours": duration,
                "threshold_hours": threshold,
                "time_str": time_str,
                "excess_hours": duration - threshold
            })

    return timeout_tasks

def display_timeouts(timeout_tasks):
    """Display timeout tasks in formatted output."""
    if not timeout_tasks:
        print("✅ 無超時任務")
        return

    print("=" * 70)
    print(f"⏰ 發現 {len(timeout_tasks)} 個超時任務")
    print("=" * 70)
    print()

    for task in timeout_tasks:
        print(f"📋 任務 ID: {task['id']}")
        print(f"   標題: {task['title']}")
        print(f"   狀態: {task['status']}")
        print(f"   持續時間: {task['duration_hours']:.1f} 小時")
        print(f"   超時閾值: {task['threshold_hours']} 小時")
        print(f"   超出時間: {task['excess_hours']:.1f} 小時")
        print(f"   更新時間: {task['time_str']}")
        print()

    print("=" * 70)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check task timeouts")
    parser.add_argument(
        "--hours",
        type=float,
        help="Timeout threshold in hours (default: 24 for in_progress, 2 for spawning)"
    )
    parser.add_argument(
        "--status", "-s",
        choices=["spawning", "in_progress", "all"],
        help="Filter by status (default: all)"
    )
    args = parser.parse_args()

    timeout_tasks = check_timeouts(hours=args.hours, status=args.status)
    display_timeouts(timeout_tasks)

    sys.exit(0 if not timeout_tasks else 1)
