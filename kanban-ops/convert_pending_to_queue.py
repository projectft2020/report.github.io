#!/usr/bin/env python3
"""
將 tasks.json 中的 pending 任務轉換成 task_queue/*.json 格式

用法:
    python3 convert_pending_to_queue.py           # 轉換所有可執行的 pending 任務
    python3 convert_pending_to_queue.py --list   # 列出可執行的任務
    python3 convert_pending_to_queue.py --dry-run # 試運行，不實際創建文件
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# 路徑配置
WORKSPACE = Path.home() / ".openclaw" / "workspace"
TASKS_JSON = WORKSPACE / "kanban" / "tasks.json"
QUEUE_DIR = WORKSPACE / "kanban-ops" / "task_queue"


def load_tasks():
    """載入 tasks.json"""
    with open(TASKS_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_executable_tasks(tasks):
    """獲取可執行的任務（無依賴或依賴已完成）"""
    tasks_by_id = {t['id']: t for t in tasks}
    executable_tasks = []

    for t in tasks:
        if t.get('status') != 'pending':
            continue

        depends = t.get('depends_on', [])

        if not depends:
            # 無依賴，可執行
            executable_tasks.append(t)
        else:
            # 檢查依賴是否都已完成
            all_completed = all(
                tasks_by_id.get(dep, {}).get('status') == 'completed'
                for dep in depends
            )
            if all_completed:
                executable_tasks.append(t)

    return executable_tasks


def task_to_queue_format(task):
    """將任務轉換成 task_queue/*.json 格式"""
    # 構建任務消息
    task_message = f"TASK: {task.get('title', task.get('description', ''))}\n\n"

    # 添加描述
    if task.get('description'):
        task_message += f"描述: {task['description']}\n\n"

    # 添加輸出路徑
    if task.get('output_path'):
        task_message += f"OUTPUT PATH: ~/{task['output_path']}\n"

    # 構建隊列格式
    queue_task = {
        "task_id": task['id'],
        "label": task['id'],
        "task": task_message,
        "agent_id": task.get('agent', 'research'),
        "model": task.get('model'),
        "status": "pending",
        "created_at": task.get('created_at'),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }

    return queue_task


def list_executable_tasks():
    """列出可執行的任務"""
    tasks = load_tasks()
    executable_tasks = get_executable_tasks(tasks)

    print(f"\n📋 可執行的任務: {len(executable_tasks)}\n")
    print("=" * 80)

    if not executable_tasks:
        print("⚠️  沒有可執行的任務\n")
        return

    for i, t in enumerate(executable_tasks, 1):
        depends = t.get('depends_on', [])
        dep_str = f", 依賴: {len(depends)} 個" if depends else ""
        print(f"{i}. [{t['id']}] {t.get('title', 'N/A')[:60]}...")
        print(f"   代理: {t.get('agent', 'N/A')} | 模型: {t.get('model', '默認')}{dep_str}")

    print("\n" + "=" * 80)


def convert_tasks(dry_run=False):
    """轉換任務到 task_queue"""
    tasks = load_tasks()
    executable_tasks = get_executable_tasks(tasks)

    if not executable_tasks:
        print("⚠️  沒有可執行的任務")
        return []

    print(f"\n🚀 開始轉換 {len(executable_tasks)} 個任務\n")
    print("=" * 80)

    converted = []

    for t in executable_tasks:
        queue_task = task_to_queue_format(t)
        task_file = QUEUE_DIR / f"{t['id']}.json"

        if task_file.exists():
            print(f"⚠️  跳過 {t['id']}（文件已存在）")
            continue

        if dry_run:
            print(f"✓ [DRY] {t['id']}: {t.get('title', 'N/A')[:50]}")
        else:
            with open(task_file, 'w', encoding='utf-8') as f:
                json.dump(queue_task, f, indent=2, ensure_ascii=False)
            print(f"✓ {t['id']}: {t.get('title', 'N/A')[:50]}")

        converted.append(t['id'])

    print("\n" + "=" * 80)
    print(f"✅ 轉換完成: {len(converted)} 個任務")

    if not dry_run:
        print(f"📁 文件位置: {QUEUE_DIR}")

    return converted


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='轉換 pending 任務到 task_queue',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--list', action='store_true',
                        help='列出可執行的任務')
    parser.add_argument('--dry-run', action='store_true',
                        help='試運行，不實際創建文件')

    args = parser.parse_args()

    # 確保目錄存在
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)

    if args.list:
        list_executable_tasks()
    else:
        convert_tasks(dry_run=args.dry_run)


if __name__ == '__main__':
    main()
