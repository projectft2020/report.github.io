#!/usr/bin/env python3
"""
Rollback Stuck Spawning Tasks

Automatically rollback tasks stuck in spawning state.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone
import argparse

KANBAN_DIR = Path.home() / ".openclaw" / "workspace" / "kanban"
TASKS_FILE = KANBAN_DIR / "tasks.json"
BACKUP_DIR = KANBAN_DIR / "backups"

DEFAULT_SPAWNING_TIMEOUT = 2  # hours

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

def backup_tasks(tasks):
    """Backup tasks.json before modifications."""
    BACKUP_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"tasks_backup_{timestamp}.json"

    with open(backup_file, "w") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)

    print(f"✅ 已備份: {backup_file}")
    return backup_file

def rollback_stuck(hours=None, dry_run=False):
    """Rollback tasks stuck in spawning state.

    Args:
        hours: Timeout threshold in hours (default: 2)
        dry_run: Preview changes without executing

    Returns:
        Number of rolled back tasks
    """
    if not TASKS_FILE.exists():
        print(f"❌ tasks.json 不存在: {TASKS_FILE}")
        return 0

    try:
        with open(TASKS_FILE, "r") as f:
            tasks = json.load(f)
    except Exception as e:
        print(f"❌ 讀取 tasks.json 失敗: {e}")
        return 0

    threshold = hours if hours else DEFAULT_SPAWNING_TIMEOUT
    rolled_back = []

    for task in tasks:
        task_status = task.get("status", "")
        task_id = task.get("id", "")

        # Only process spawning tasks
        if task_status != "spawning":
            continue

        time_str = task.get("updated_at") or task.get("created_at")
        if not time_str:
            continue

        duration = get_duration_hours(time_str)

        if duration and duration > threshold:
            rolled_back.append({
                "id": task_id,
                "title": task.get("title", "")[:50],
                "duration": duration,
                "excess": duration - threshold
            })

            if not dry_run:
                task["status"] = "pending"
                task["updated_at"] = datetime.now(timezone.utc).isoformat()

                # Add timeout note
                if "notes" not in task:
                    task["notes"] = []
                task["notes"].append({
                    "type": "timeout_rollback",
                    "message": f"任務卡在 spawning 狀態 {duration:.1f} 小時，超過閾值 {threshold} 小時，已自動回滾"
                })

    if not rolled_back:
        print("✅ 無需要回滾的任務")
        return 0

    if dry_run:
        print("=" * 70)
        print("🔍 Dry Run - 預覽回滾操作")
        print("=" * 70)
        print(f"將回滾 {len(rolled_back)} 個任務:")
        print()

        for task in rolled_back:
            print(f"📋 {task['id']}")
            print(f"   標題: {task['title']}")
            print(f"   持續時間: {task['duration']:.1f} 小時")
            print(f"   超出時間: {task['excess']:.1f} 小時")
            print()

        print("=" * 70)
        print(f"💡 執行: python3 rollback_stuck.py --hours {threshold}")
        print("=" * 70)
        return len(rolled_back)

    # Backup before modification
    backup_tasks(tasks)

    # Save updated tasks
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)

    print("=" * 70)
    print(f"🔄 已回滾 {len(rolled_back)} 個卡住的任務")
    print("=" * 70)
    print()

    for task in rolled_back:
        print(f"✅ {task['id']}")
        print(f"   標題: {task['title']}")
        print(f"   持續: {task['duration']:.1f} 小時 (超出 {task['excess']:.1f} 小時)")
        print()

    print("=" * 70)
    print(f"💡 這些任務已回滾到 pending 狀態，下次心跳時可重新啟動")
    print("=" * 70)

    return len(rolled_back)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rollback stuck spawning tasks")
    parser.add_argument(
        "--hours", "-h",
        type=float,
        help=f"Timeout threshold in hours (default: {DEFAULT_SPAWNING_TIMEOUT})"
    )
    parser.add_argument(
        "--dry-run", "-d",
        action="store_true",
        help="Preview changes without executing"
    )
    args = parser.parse_args()

    count = rollback_stuck(hours=args.hours, dry_run=args.dry_run)
    sys.exit(0 if count == 0 else 1)
