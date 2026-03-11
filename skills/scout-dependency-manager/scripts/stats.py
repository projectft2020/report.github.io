#!/usr/bin/env python3
"""
Scout Agent Statistics

Display Scout Agent statistics and recent activity.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

SCOUT_WORKSPACE = Path.home() / ".openclaw" / "workspace-scout"
KANBAN_DIR = Path.home() / ".openclaw" / "workspace" / "kanban"

def get_kanban_stats():
    """Get Kanban task statistics."""
    tasks_file = KANBAN_DIR / "tasks.json"

    if not tasks_file.exists():
        return None

    try:
        with open(tasks_file, "r") as f:
            tasks = json.load(f)

        stats = {
            "total": len(tasks),
            "pending": sum(1 for t in tasks if t.get("status") == "pending"),
            "in_progress": sum(1 for t in tasks if t.get("status") == "in_progress"),
            "completed": sum(1 for t in tasks if t.get("status") == "completed"),
            "failed": sum(1 for t in tasks if t.get("status") == "failed"),
            "high_priority": sum(1 for t in tasks if t.get("priority") == "high" and t.get("status") == "pending")
        }

        return stats

    except Exception as e:
        print(f"❌ 讀取 tasks.json 失敗: {e}")
        return None

def get_scout_preferences():
    """Get Scout Agent preferences."""
    prefs_file = SCOUT_WORKSPACE / "PREFERENCES.json"

    if not prefs_file.exists():
        return None

    try:
        with open(prefs_file, "r") as f:
            prefs = json.load(f)

        return prefs

    except Exception as e:
        print(f"❌ 讀取 PREFERENCES.json 失敗: {e}")
        return None

def get_last_scan_info():
    """Get last Scout scan information."""
    scan_log = SCOUT_WORKSPACE / "SCAN_LOG.md"

    if not scan_log.exists():
        return None

    try:
        with open(scan_log, "r") as f:
            content = f.read()

        # Find last scan entry
        lines = content.split("\n")
        for line in reversed(lines):
            if line.strip().startswith("##"):
                return {
                    "timestamp": line.replace("##", "").strip(),
                    "raw": line
                }

        return None

    except Exception as e:
        print(f"❌ 讀取 SCAN_LOG.md 失敗: {e}")
        return None

def display_stats():
    """Display comprehensive Scout Agent statistics."""
    print("=" * 60)
    print("📊 Scout Agent 統計信息")
    print("=" * 60)
    print()

    # Kanban Stats
    print("📋 Kanban 任務狀態:")
    print("-" * 60)
    kanban_stats = get_kanban_stats()
    if kanban_stats:
        print(f"總任務:          {kanban_stats['total']:>5}")
        print(f"待辦:            {kanban_stats['pending']:>5}")
        print(f"進行中:          {kanban_stats['in_progress']:>5}")
        print(f"已完成:          {kanban_stats['completed']:>5}")
        print(f"失敗:            {kanban_stats['failed']:>5}")
        print(f"高優先級待辦:    {kanban_stats['high_priority']:>5}")
    else:
        print("⚠️  無法獲取 Kanban 統計")
    print()

    # Last Scan
    print("🔍 最近掃描:")
    print("-" * 60)
    last_scan = get_last_scan_info()
    if last_scan:
        print(f"最後掃描: {last_scan['timestamp']}")

        # Calculate time since last scan
        try:
            # Parse timestamp from format like "2026-03-04 10:00:00"
            scan_time = datetime.strptime(last_scan['timestamp'].split(' -')[0], "%Y-%m-%d %H:%M:%S")
            time_since = datetime.now() - scan_time
            hours = int(time_since.total_seconds() // 3600)
            if hours < 1:
                minutes = int(time_since.total_seconds() // 60)
                print(f"距離現在: {minutes} 分鐘前")
            else:
                print(f"距離現在: {hours} 小時前")
        except:
            pass
    else:
        print("⚠️  無掃描記錄")
    print()

    # Preferences
    print("⚙️  Scout 偏好設置:")
    print("-" * 60)
    prefs = get_scout_preferences()
    if prefs:
        if "topics" in prefs:
            print(f"關注主題: {len(prefs['topics'])} 個")
            print(f"         前 3: {', '.join(prefs['topics'][:3])}")
        if "total_feedbacks" in prefs:
            print(f"總反饋數: {prefs['total_feedbacks']}")
        if "average_rating" in prefs:
            rating = prefs['average_rating']
            print(f"平均評分: {rating:.2f}/5.0")
            if rating >= 4.0:
                print(f"         品質: 優秀 ⭐")
            elif rating >= 3.0:
                print(f"         品質: 良好 ✅")
            else:
                print(f"         品質: 需改進 ⚠️")
    else:
        print("⚠️  無偏好設置")
    print()

    # Recommendations
    print("💡 系統建議:")
    print("-" * 60)

    if kanban_stats and kanban_stats['pending'] < 3 and last_scan:
        try:
            scan_time = datetime.strptime(last_scan['timestamp'].split(' -')[0], "%Y-%m-%d %H:%M:%S")
            hours_since = (datetime.now() - scan_time).total_seconds() / 3600
            if hours_since > 2:
                print("✓ 待辦任務少，建議觸發 Scout 掃描")
                print("  執行: python3 trigger_scan.py")
        except:
            pass

    if prefs and "average_rating" in prefs and prefs['average_rating'] < 3.0:
        print("⚠️  推薦品質較低，建議檢查並調整 Scout 偏好")

    if not prefs:
        print("⚠️  Scout 尚未收集足夠反饋，需要更多使用")

    print()
    print("=" * 60)

if __name__ == "__main__":
    display_stats()
