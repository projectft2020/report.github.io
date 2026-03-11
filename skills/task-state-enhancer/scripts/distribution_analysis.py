#!/usr/bin/env python3
"""
Task Distribution Analysis

Analyze task distribution by various dimensions.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import Counter, defaultdict

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

def analyze_by_priority(tasks):
    """Analyze task distribution by priority."""
    pending_tasks = [t for t in tasks if t.get("status") == "pending"]
    priorities = Counter([t.get("priority", "normal") for t in pending_tasks])

    print("📌 按優先級分析 (待辦任務):")
    print("-" * 70)

    for priority in ["high", "medium", "normal", "low"]:
        count = priorities.get(priority, 0)
        pct = (count / len(pending_tasks) * 100) if pending_tasks else 0
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        print(f"{priority:10s}: {count:4d} ({pct:5.1f}%) {bar}")

    print()

def analyze_by_status(tasks):
    """Analyze task distribution by status."""
    statuses = Counter([t.get("status", "unknown") for t in tasks])
    total = len(tasks)

    print("📋 按狀態分析:")
    print("-" * 70)

    for status in ["pending", "spawning", "in_progress", "completed", "failed"]:
        count = statuses.get(status, 0)
        pct = (count / total * 100) if total > 0 else 0
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        print(f"{status:15s}: {count:4d} ({pct:5.1f}%) {bar}")

    print()

def analyze_by_agent(tasks):
    """Analyze task distribution by agent type."""
    agent_counts = defaultdict(int)

    for task in tasks:
        agent = task.get("agent", "unknown")
        agent_counts[agent] += 1

    print("🤖 按代理類型分析:")
    print("-" * 70)

    total = len(tasks)
    sorted_agents = sorted(agent_counts.items(), key=lambda x: x[1], reverse=True)

    for agent, count in sorted_agents:
        pct = (count / total * 100) if total > 0 else 0
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        print(f"{agent:15s}: {count:4d} ({pct:5.1f}%) {bar}")

    print()

def analyze_by_age(tasks):
    """Analyze task distribution by age."""
    pending_tasks = [t for t in tasks if t.get("status") == "pending"]

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

    print("⏰ 按年齡分析 (待辦任務):")
    print("-" * 70)

    pending_total = len(pending_tasks)
    for bucket, count in age_buckets.items():
        if pending_total > 0:
            pct = (count / pending_total * 100)
            bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
            print(f"{bucket:10s}: {count:4d} ({pct:5.1f}%) {bar}")
        else:
            print(f"{bucket:10s}: {count:4d}")

    print()

def analyze_distribution(tasks, by_priority=False, by_status=False, by_agent=False, by_age=False):
    """Run distribution analysis based on flags."""
    print("=" * 70)
    print("📊 任務分佈分析")
    print("=" * 70)
    print()

    if by_priority:
        analyze_by_priority(tasks)

    if by_status:
        analyze_by_status(tasks)

    if by_agent:
        analyze_by_agent(tasks)

    if by_age:
        analyze_by_age(tasks)

    # If no flags specified, run all
    if not (by_priority or by_status or by_agent or by_age):
        analyze_by_priority(tasks)
        analyze_by_status(tasks)
        analyze_by_agent(tasks)
        analyze_by_age(tasks)

    print("=" * 70)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Analyze task distribution")
    parser.add_argument("--by-priority", action="store_true", help="Group by priority")
    parser.add_argument("--by-status", action="store_true", help="Group by status")
    parser.add_argument("--by-agent", action="store_true", help="Group by agent")
    parser.add_argument("--by-age", action="store_true", help="Group by age")
    args = parser.parse_args()

    tasks = load_tasks()

    if not tasks:
        print("❌ 無任務數據")
        sys.exit(1)

    analyze_distribution(
        tasks,
        by_priority=args.by_priority,
        by_status=args.by_status,
        by_agent=args.by_agent,
        by_age=args.by_age
    )
