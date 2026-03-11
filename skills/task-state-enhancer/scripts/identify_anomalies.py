#!/usr/bin/env python3
"""
Identify Task Anomalies

Detect tasks with unusual characteristics.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

KANBAN_DIR = Path.home() / ".openclaw" / "workspace" / "kanban"
TASKS_FILE = KANBAN_DIR / "tasks.json"
RESEARCH_OUTPUT_DIR = KANBAN_DIR / "projects"

VALID_PRIORITIES = ["high", "medium", "normal", "low"]

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

def get_duration_hours(timestamp):
    """Calculate duration in hours from timestamp."""
    dt = parse_timestamp(timestamp)
    if not dt:
        return None

    return (datetime.now(timezone.utc) - dt).total_seconds() / 3600

def identify_stuck_tasks(tasks, threshold_hours=2):
    """Identify tasks stuck in spawning state."""
    anomalies = []

    for task in tasks:
        if task.get("status") != "spawning":
            continue

        updated_at = task.get("updated_at") or task.get("created_at")
        if not updated_at:
            continue

        duration = get_duration_hours(updated_at)

        if duration and duration > threshold_hours:
            anomalies.append({
                "type": "stuck_spawning",
                "id": task.get("id"),
                "title": task.get("title", "")[:50],
                "duration_hours": duration,
                "threshold_hours": threshold_hours,
                "excess_hours": duration - threshold_hours,
                "updated_at": updated_at
            })

    return anomalies

def identify_missing_metadata(tasks):
    """Identify tasks with missing critical metadata."""
    anomalies = []

    required_fields = ["id", "title", "status", "priority", "created_at"]

    for task in tasks:
        missing = []

        for field in required_fields:
            if field not in task or not task[field]:
                missing.append(field)

        if missing:
            anomalies.append({
                "type": "missing_metadata",
                "id": task.get("id", "unknown"),
                "missing_fields": missing,
                "title": task.get("title", "")[:50]
            })

    return anomalies

def identify_invalid_priorities(tasks):
    """Identify tasks with invalid priority values."""
    anomalies = []

    for task in tasks:
        priority = task.get("priority", "")

        if priority and priority not in VALID_PRIORITIES:
            anomalies.append({
                "type": "invalid_priority",
                "id": task.get("id"),
                "invalid_priority": priority,
                "title": task.get("title", "")[:50]
            })

    return anomalies

def identify_orphaned_tasks(tasks):
    """Identify completed tasks missing output files."""
    anomalies = []

    completed_tasks = [t for t in tasks if t.get("status") == "completed"]

    for task in completed_tasks:
        task_id = task.get("id", "")

        # Check if research output exists
        output_found = False

        if RESEARCH_OUTPUT_DIR.exists():
            # Search for output files
            for pattern in [f"*-{task_id}-research.md", f"*{task_id}*"]:
                matches = list(RESEARCH_OUTPUT_DIR.rglob(pattern))
                if matches:
                    output_found = True
                    break

        if not output_found:
            anomalies.append({
                "type": "orphaned",
                "id": task_id,
                "title": task.get("title", "")[:50],
                "completed_at": task.get("completed_at")
            })

    return anomalies

def identify_anomalies():
    """Identify all types of anomalies."""
    tasks = load_tasks()

    if not tasks:
        print("❌ 無任務數據")
        return []

    print("=" * 70)
    print("🔍 任務異常檢測")
    print("=" * 70)
    print()

    all_anomalies = []

    # 1. Stuck spawning tasks
    stuck = identify_stuck_tasks(tasks, threshold_hours=2)
    all_anomalies.extend(stuck)

    # 2. Missing metadata
    missing_meta = identify_missing_metadata(tasks)
    all_anomalies.extend(missing_meta)

    # 3. Invalid priorities
    invalid_prio = identify_invalid_priorities(tasks)
    all_anomalies.extend(invalid_prio)

    # 4. Orphaned tasks
    orphaned = identify_orphaned_tasks(tasks)
    all_anomalies.extend(orphaned)

    # Display results
    if not all_anomalies:
        print("✅ 無異常任務")
        return []

    print(f"⚠️  發現 {len(all_anomalies)} 個異常")
    print()

    # Group by type
    by_type = {}
    for anomaly in all_anomalies:
        anomaly_type = anomaly["type"]
        if anomaly_type not in by_type:
            by_type[anomaly_type] = []
        by_type[anomaly_type].append(anomaly)

    # Display each type
    for anomaly_type, items in by_type.items():
        count = len(items)
        print(f"📌 {anomaly_type}: {count} 個")
        print("-" * 70)

        for item in items[:10]:  # Limit to 10 per type
            if anomaly_type == "stuck_spawning":
                print(f"  ❌ {item['id']}")
                print(f"     標題: {item['title']}")
                print(f"     卡住: {item['duration_hours']:.1f} 小時 (超出 {item['excess_hours']:.1f} 小時)")
                print(f"     更新時間: {item['updated_at']}")

            elif anomaly_type == "missing_metadata":
                print(f"  ⚠️  {item['id']}")
                print(f"     標題: {item['title']}")
                print(f"     缺失字段: {', '.join(item['missing_fields'])}")

            elif anomaly_type == "invalid_priority":
                print(f"  ⚠️  {item['id']}")
                print(f"     標題: {item['title']}")
                print(f"     無效優先級: '{item['invalid_priority']}'")

            elif anomaly_type == "orphaned":
                print(f"  ⚠️  {item['id']}")
                print(f"     標題: {item['title']}")
                print(f"     完成時間: {item['completed_at']}")
                print(f"     缺失輸出文件")

            print()

        if len(items) > 10:
            print(f"  ... 還有 {len(items) - 10} 個")
            print()

    print("=" * 70)
    print("💡 建議操作:")
    print()

    if stuck:
        print(f"1. 卡住的任務 ({len(stuck)} 個):")
        print("   - 運行: python3 rollback_stuck.py")
        print("   - 或手動檢查任務狀態")
        print()

    if missing_meta:
        print(f"2. 缺失元數據的任務 ({len(missing_meta)} 個):")
        print("   - 補充缺失的字段")
        print("   - 刪除不完整的任務")
        print()

    if invalid_prio:
        print(f"3. 無效優先級的任務 ({len(invalid_prio)} 個):")
        print("   - 更正優先級為: high, medium, normal, 或 low")
        print()

    if orphaned:
        print(f"4. 孤兒任務 ({len(orphaned)} 個):")
        print("   - 重新生成研究輸出")
        print("   - 檢查輸出目錄路徑")
        print()

    print("=" * 70)

    return all_anomalies

if __name__ == "__main__":
    anomalies = identify_anomalies()
    sys.exit(0 if len(anomalies) == 0 else 1)
