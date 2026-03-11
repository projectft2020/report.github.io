#!/usr/bin/env python3
"""
Generate State Report

Comprehensive task state analysis.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import Counter

KANBAN_DIR = Path.home() / ".openclaw" / "workspace" / "kanban"
TASKS_FILE = KANBAN_DIR / "tasks.json"
RESEARCH_OUTPUT_DIR = KANBAN_DIR / "projects"

def load_tasks():
    """Load tasks from tasks.json."""
    if not TASKS_FILE.exists():
        return []

    try:
        with open(TASKS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def parse_timestamp(ts_str):
    """Parse timestamp with timezone handling."""
    if not ts_str:
        return None

    try:
        if "Z" in ts_str or "+" in ts_str:
            return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        else:
            return datetime.fromisoformat(ts_str).replace(tzinfo=timezone.utc)
    except:
        return None

def get_age_in_days(timestamp):
    """Calculate age in days."""
    if not timestamp:
        return None

    try:
        dt = parse_timestamp(timestamp)
        if dt:
            return (datetime.now(timezone.utc) - dt).days
    except:
        return None

def get_recent_activity(tasks, hours=24):
    """Get recent activity statistics."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

    recent = {
        "completed": [],
        "started": [],
        "failed": []
    }

    for task in tasks:
        # Check completed_at
        completed_at = task.get("completed_at")
        if completed_at:
            ct = parse_timestamp(completed_at)
            if ct and ct > cutoff:
                recent["completed"].append({
                    "id": task.get("id"),
                    "title": task.get("title", "")[:50],
                    "time": completed_at
                })

        # Check updated_at for spawning/in_progress
        if task.get("status") in ["spawning", "in_progress"]:
            updated_at = task.get("updated_at")
            if updated_at:
                ut = parse_timestamp(updated_at)
                if ut and ut > cutoff:
                    recent["started"].append({
                        "id": task.get("id"),
                        "title": task.get("title", "")[:50],
                        "time": updated_at
                    })

    return recent

def generate_state_report():
    """Generate comprehensive task state report."""
    tasks = load_tasks()

    if not tasks:
        print("❌ 無任務數據")
        return

    print("=" * 70)
    print("📊 任務狀態報告")
    print("=" * 70)
    print()

    # Status distribution
    print("📋 狀態分佈:")
    print("-" * 70)

    status_counts = Counter([t.get("status", "unknown") for t in tasks])
    total = len(tasks)

    for status in ["pending", "spawning", "in_progress", "completed", "failed"]:
        count = status_counts.get(status, 0)
        pct = (count / total * 100) if total > 0 else 0
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        print(f"{status:15s}: {count:4d} ({pct:5.1f}%) {bar}")

    print()

    # Priority distribution (pending tasks only)
    pending_tasks = [t for t in tasks if t.get("status") == "pending"]

    if pending_tasks:
        print("📌 待辦任務優先級分佈:")
        print("-" * 70)

        prio_counts = Counter([t.get("priority", "normal") for t in pending_tasks])
        pending_total = len(pending_tasks)

        for priority in ["high", "medium", "normal", "low"]:
            count = prio_counts.get(priority, 0)
            pct = (count / pending_total * 100) if pending_total > 0 else 0
            bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
            print(f"{priority:10s}: {count:4d} ({pct:5.1f}%) {bar}")

        print()

    # Age distribution (pending tasks only)
    if pending_tasks:
        print("⏰ 待辦任務年齡分佈:")
        print("-" * 70)

        age_buckets = {
            "< 1 天": 0,
            "1-3 天": 0,
            "3-7 天": 0,
            "7-14 天": 0,
            "> 14 天": 0
        }

        for task in pending_tasks:
            created_at = task.get("created_at")
            age = get_age_in_days(created_at)

            if age is not None:
                if age < 1:
                    age_buckets["< 1 天"] += 1
                elif age < 3:
                    age_buckets["1-3 天"] += 1
                elif age < 7:
                    age_buckets["3-7 天"] += 1
                elif age < 14:
                    age_buckets["7-14 天"] += 1
                else:
                    age_buckets["> 14 天"] += 1

        for bucket, count in age_buckets.items():
            if pending_total > 0:
                pct = (count / pending_total * 100)
                bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
                print(f"{bucket:10s}: {count:4d} ({pct:5.1f}%) {bar}")

        print()

    # Recent activity
    print("🕐 最近 24 小時活動:")
    print("-" * 70)

    recent = get_recent_activity(tasks, hours=24)

    if recent["completed"]:
        print(f"✅ 完成任務: {len(recent['completed'])} 個")
        for task in recent["completed"][:5]:
            print(f"   - {task['id']}")
            print(f"     {task['title']}")
            print(f"     時間: {task['time']}")
        print()

    if recent["started"]:
        print(f"🚀 啟動任務: {len(recent['started'])} 個")
        for task in recent["started"][:5]:
            print(f"   - {task['id']}")
            print(f"     {task['title']}")
            print(f"     時間: {task['time']}")
        print()

    if not recent["completed"] and not recent["started"]:
        print("📉 無最近活動")

    print()
    print("=" * 70)
    print(f"報告生成時間: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 70)

if __name__ == "__main__":
    generate_state_report()
