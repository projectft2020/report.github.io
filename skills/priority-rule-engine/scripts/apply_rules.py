#!/usr/bin/env python3
"""
Apply Priority Rules

Apply priority rules to pending tasks.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
import argparse

KANBAN_DIR = Path.home() / ".openclaw" / "workspace" / "kanban"
TASKS_FILE = KANBAN_DIR / "tasks.json"
DEFAULT_RULES_FILE = Path(__file__).parent.parent / "references" / "priority_rules.json"

def load_tasks():
    """Load tasks from tasks.json."""
    if not TASKS_FILE.exists():
        print(f"❌ tasks.json 不存在: {TASKS_FILE}")
        return []

    try:
        with open(TASKS_FILE, "r") as f:
            data = json.load(f)

            # 處理不同的 JSON 格式
            if isinstance(data, dict) and 'tasks' in data:
                return data['tasks']
            elif isinstance(data, list):
                return data
            else:
                print(f"❌ 未知的 tasks.json 格式: {type(data)}")
                return []
    except Exception as e:
        print(f"❌ 讀取 tasks.json 失敗: {e}")
        return []

def save_tasks(tasks):
    """Save tasks to tasks.json with backup."""
    # Create backup
    backup_dir = KANBAN_DIR / "backups"
    backup_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"tasks_backup_{timestamp}.json"

    # 檢查原始格式以保持一致性
    original_format = "dict"  # 默認為 dict 格式
    if TASKS_FILE.exists():
        try:
            with open(TASKS_FILE, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    original_format = "list"
                elif isinstance(data, dict) and 'tasks' in data:
                    original_format = "dict"
        except:
            pass

    # 保存備份
    if original_format == "dict":
        backup_data = {"tasks": tasks}
    else:
        backup_data = tasks

    with open(backup_file, "w") as f:
        json.dump(backup_data, f, indent=2, ensure_ascii=False)

    # 保存任務
    if original_format == "dict":
        save_data = {"tasks": tasks}
    else:
        save_data = tasks

    with open(TASKS_FILE, "w") as f:
        json.dump(save_data, f, indent=2, ensure_ascii=False)

    print(f"✅ 已備份: {backup_file}")

def load_rules(rules_path=None):
    """Load priority rules from JSON file."""
    if rules_path is None:
        rules_path = DEFAULT_RULES_FILE

    try:
        with open(rules_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 讀取規則文件失敗: {e}")
        return []

def evaluate_condition(task, condition):
    """Evaluate if task matches rule condition."""
    # Check status
    if "status" in condition and task.get("status") != condition["status"]:
        return False

    # Check current priority
    if "current_priority" in condition:
        current_prio = task.get("priority", "normal")
        if current_prio not in condition["current_priority"]:
            return False

    # Check days pending
    if "days_pending" in condition:
        created_at = task.get("created_at")
        if not created_at:
            return False

        try:
            # Parse timestamp
            if "Z" in created_at or "+" in created_at:
                task_time = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            else:
                task_time = datetime.fromisoformat(created_at).replace(tzinfo=timezone.utc)

            days_pending = (datetime.now(timezone.utc) - task_time).days

            # Evaluate comparison
            op = condition["days_pending"]
            if op.startswith(">"):
                if days_pending <= int(op[1:]):
                    return False
            elif op.startswith("<"):
                if days_pending >= int(op[1:]):
                    return False
            elif op.startswith(">="):
                if days_pending < int(op[2:]):
                    return False
            elif op.startswith("<="):
                if days_pending > int(op[2:]):
                    return False
        except:
            return False

    # Check tags
    if "tags" in condition:
        task_tags = task.get("tags", [])
        if not any(tag in task_tags for tag in condition["tags"]):
            return False

    # Check keywords
    if "keywords" in condition:
        task_title = task.get("title", "").lower()
        task_desc = task.get("description", "").lower()
        combined = task_title + " " + task_desc

        if not any(kw.lower() in combined for kw in condition["keywords"]):
            return False

    # Check related score (requires research output analysis)
    if "related_score" in condition:
        # This would require analyzing related research outputs
        # For now, skip this condition
        pass

    return True

def apply_rule(task, rule, verbose=False):
    """Apply a single rule to a task."""
    if not evaluate_condition(task, rule.get("condition", {})):
        return False

    if verbose:
        print(f"  ✅ 匹配規則: {rule['name']}")
        print(f"     當前優先級: {task.get('priority', 'normal')}")
        print(f"     新優先級: {rule['priority']}")

    # Apply action
    if rule.get("action") == "set_priority":
        task["priority"] = rule["priority"]
        task["updated_at"] = datetime.now(timezone.utc).isoformat()

        # Add note
        if "notes" not in task:
            task["notes"] = []
        elif isinstance(task["notes"], str):
            # 如果 notes 是字串，轉換為列表
            task["notes"] = [{"message": task["notes"]}]
        task["notes"].append({
            "type": "priority_update",
            "rule": rule["name"],
            "message": f"優先級根據規則 '{rule['name']}' 更新為 {rule['priority']}"
        })

        return True

    return False

def apply_rules(rules_path=None, dry_run=False, verbose=False, tasks=None):
    """Apply priority rules to pending tasks.

    Args:
        rules_path: Path to rules configuration file
        dry_run: Preview changes without executing
        verbose: Show detailed evaluation
        tasks: Optional pre-loaded tasks list (for integration)

    Returns:
        Number of updated tasks
    """
    # 如果沒有提供 tasks，就載入它
    if tasks is None:
        tasks = load_tasks()
        should_save = True  # 需要保存到文件
    else:
        should_save = False  # 外部會保存

    if not tasks:
        return 0

    rules = load_rules(rules_path)
    if not rules:
        print("❌ 無規則可應用")
        return 0

    updated_count = 0
    updated_tasks = []

    for task in tasks:
        if task.get("status") != "pending":
            continue

        if verbose:
            print(f"\n📋 評估任務: {task.get('id')}")
            print(f"   標題: {task.get('title', '')[:50]}")

        # Apply rules in order (first match wins)
        for rule in rules:
            if apply_rule(task, rule, verbose):
                updated_count += 1
                updated_tasks.append(task.get("id"))
                break

    print()
    print("=" * 60)
    if dry_run:
        print(f"🔍 Dry Run - 將更新 {updated_count} 個任務")
    else:
        print(f"✅ 已更新 {updated_count} 個任務的優先級")
        if updated_count > 0 and should_save:
            save_tasks(tasks)
    print("=" * 60)

    if updated_tasks and verbose:
        print()
        print("更新的任務:")
        for task_id in updated_tasks:
            print(f"  - {task_id}")
        print()

    return updated_count

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Apply priority rules")
    parser.add_argument(
        "--rules", "-r",
        help="Path to rules configuration file"
    )
    parser.add_argument(
        "--dry-run", "-d",
        action="store_true",
        help="Preview changes without executing"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed rule evaluation"
    )
    args = parser.parse_args()

    count = apply_rules(
        rules_path=args.rules,
        dry_run=args.dry_run,
        verbose=args.verbose
    )

    sys.exit(0)  # 總是成功退出，無論是否有任務被更新
