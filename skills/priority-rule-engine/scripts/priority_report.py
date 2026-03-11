#!/usr/bin/env python3
"""
Generate Priority Report

Display current priority distribution.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import Counter

KANBAN_DIR = Path.home() / ".openclaw" / "workspace" / "kanban"
TASKS_FILE = KANBAN_DIR / "tasks.json"

def load_tasks():
    """Load tasks from tasks.json."""
    if not TASKS_FILE.exists():
        return []

    try:
        with open(TASKS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def get_days_pending(created_at):
    """Calculate days pending from creation time."""
    if not created_at:
        return 0

    try:
        if "Z" in created_at or "+" in created_at:
            task_time = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        else:
            task_time = datetime.fromisoformat(created_at).replace(tzinfo=timezone.utc)

        return (datetime.now(timezone.utc) - task_time).days
    except:
        return 0

def generate_report():
    """Generate priority distribution report."""
    tasks = load_tasks()

    if not tasks:
        print("❌ 無任務數據")
        return

    print("=" * 60)
    print("📊 任務優先級報告")
    print("=" * 60)
    print()

    # Overall statistics
    total = len(tasks)
    pending = sum(1 for t in tasks if t.get("status") == "pending")
    in_progress = sum(1 for t in tasks if t.get("status") == "in_progress")
    completed = sum(1 for t in tasks if t.get("status") == "completed")

    print(f"總任務: {total}")
    print(f"待辦:   {pending}")
    print(f"進行中: {in_progress}")
    print(f"已完成:   {completed}")
    print()

    # Priority distribution for pending tasks
    print("-" * 60)
    print("待辦任務優先級分佈:")
    print("-" * 60)

    pending_tasks = [t for t in tasks if t.get("status") == "pending"]
    priorities = Counter([t.get("priority", "normal") for t in pending_tasks])

    for priority in ["high", "medium", "normal", "low"]:
        count = priorities.get(priority, 0)
        if total > 0:
            percentage = (count / len(pending_tasks) * 100) if pending_tasks else 0
            bar = "█" * int(percentage / 5) + "░" * (20 - int(percentage / 5))
            print(f"{priority:10s}: {count:3d} ({percentage:5.1f}%) {bar}")
        else:
            print(f"{priority:10s}: {count:3d}")

    print()

    # Age distribution
    print("-" * 60)
    print("待辦任務年齡分佈:")
    print("-" * 60)

    age_buckets = {
        "< 1 天": 0,
        "1-3 天": 0,
        "3-7 天": 0,
        "7-14 天": 0,
        "> 14 天": 0
    }

    for task in pending_tasks:
        days = get_days_pending(task.get("created_at"))
        if days < 1:
            age_buckets["< 1 天"] += 1
        elif days < 3:
            age_buckets["1-3 天"] += 1
        elif days < 7:
            age_buckets["3-7 天"] += 1
        elif days < 14:
            age_buckets["7-14 天"] += 1
        else:
            age_buckets["> 14 天"] += 1

    for bucket, count in age_buckets.items():
        if len(pending_tasks) > 0:
            percentage = (count / len(pending_tasks) * 100)
            bar = "█" * int(percentage / 5) + "░" * (20 - int(percentage / 5))
            print(f"{bucket:10s}: {count:3d} ({percentage:5.1f}%) {bar}")
        else:
            print(f"{bucket:10s}: {count:3d}")

    print()

    # High priority tasks
    print("-" * 60)
    print("高優先級待辦任務:")
    print("-" * 60)

    high_priority = [t for t in pending_tasks if t.get("priority") == "high"]
    if high_priority:
        for i, task in enumerate(high_priority[:10], 1):
            title = task.get("title", "")[:50]
            days = get_days_pending(task.get("created_at"))
            print(f"{i}. {task.get('id')}")
            print(f"   標題: {title}")
            print(f"   待辦天數: {days} 天")
            print()
    else:
        print("無高優先級待辦任務")

    print()

    # Recommendations
    print("-" * 60)
    print("💡 系統建議:")
    print("-" * 60)

    recommendations = []

    if len(pending_tasks) > 50:
        recommendations.append("待辦任務較多，建議考慮降低某些任務優先級")

    if priorities.get("high", 0) > len(pending_tasks) * 0.5:
        recommendations.append("高優先級任務過多，建議重新評估優先級分佈")

    if age_buckets["> 14 天"] > len(pending_tasks) * 0.3:
        recommendations.append("大量任務待辦超過 14 天，建議清理或降低優先級")

    if age_buckets["< 1 天"] < 3 and len(pending_tasks) > 10:
        recommendations.append("新任務較少，考慮觸發 Scout 掃描")

    if not high_priority and len(pending_tasks) > 5:
        recommendations.append("無高優先級任務，應用優先級規則調整")

    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
    else:
        print("當前優先級分佈合理")

    print()
    print("=" * 60)
    print(f"報告生成時間: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 60)

if __name__ == "__main__":
    generate_report()
