#!/usr/bin/env python3
"""
處理任務隊列

讀取由 turbo_mode.py 生成的任務隊列，並使用 sessions_spawn 實際啟動任務。

使用方式：
    python3 process_task_queue.py list          # 列出隊列中的任務
    python3 process_task_queue.py pop            # 彈出並執行一個任務
    python3 process_task_queue.py pop-all       # 彈出並執行所有任務
    python3 process_task_queue.py clear          # 清空隊列
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

# 路徑配置
WORKSPACE = Path.home() / ".openclaw" / "workspace"
QUEUE_DIR = WORKSPACE / "kanban-ops" / "task_queue"


def list_queue():
    """列出隊列中的任務"""
    if not QUEUE_DIR.exists():
        print("📋 隊列為空（目錄不存在）")
        return []

    task_files = sorted(QUEUE_DIR.glob("*.json"))

    if not task_files:
        print("📋 隊列為空")
        return []

    print(f"📋 隊列中共有 {len(task_files)} 個任務：\n")

    tasks = []

    for task_file in task_files:
        with open(task_file, 'r', encoding='utf-8') as f:
            task_data = json.load(f)

        print(f"📄 {task_file.name}")
        print(f"   標籤：{task_data.get('label', 'N/A')}")
        print(f"   代理：{task_data.get('agent_id', 'N/A')}")
        print(f"   模型：{task_data.get('model', '默認')}")
        print(f"   狀態：{task_data.get('status', 'N/A')}")
        print(f"   創建時間：{task_data.get('created_at', 'N/A')}")

        if task_data.get('session_key'):
            print(f"   會話：{task_data.get('session_key')}")

        print()

        tasks.append(task_data)

    return tasks


def pop_task():
    """彈出並執行一個任務"""
    task_files = sorted(QUEUE_DIR.glob("*.json"))

    if not task_files:
        print("📋 隊列為空，沒有任務可執行")
        return None

    task_file = task_files[0]

    print(f"🚀 彈出任務：{task_file.name}")

    # 讀取任務
    with open(task_file, 'r', encoding='utf-8') as f:
        task_data = json.load(f)

    # 更新狀態為 in_progress
    task_data['status'] = 'in_progress'
    with open(task_file, 'w', encoding='utf-8') as f:
        json.dump(task_data, f, indent=2, ensure_ascii=False)

    # 準備執行
    print(f"   標籤：{task_data.get('label')}")
    print(f"   代理：{task_data.get('agent_id')}")
    print(f"   模型：{task_data.get('model', '默認')}")

    # 返回任務數據，讓主會話調用 sessions_spawn
    return task_data


def pop_all_tasks():
    """彈出並執行所有任務"""
    tasks = []
    while True:
        task = pop_task()
        if task is None:
            break
        tasks.append(task)
        print()  # 空行分隔

    print(f"\n✅ 共彈出 {len(tasks)} 個任務")
    return tasks


def clear_queue():
    """清空隊列"""
    task_files = sorted(QUEUE_DIR.glob("*.json"))

    if not task_files:
        print("📋 隊列為空，無需清空")
        return

    print(f"🧹 清空隊列：{len(task_files)} 個任務")

    for task_file in task_files:
        task_file.unlink()
        print(f"   已刪除：{task_file.name}")

    print(f"\n✅ 隊列已清空")


def main():
    """主函數"""
    if len(sys.argv) < 2:
        print("用法：")
        print("  python3 process_task_queue.py list          列出隊列中的任務")
        print("  python3 process_task_queue.py pop            彈出並執行一個任務")
        print("  python3 process_task_queue.py pop-all       彈出並執行所有任務")
        print("  python3 process_task_queue.py clear          清空隊列")
        sys.exit(1)

    command = sys.argv[1]

    if command == 'list':
        list_queue()
    elif command == 'pop':
        task = pop_task()
        if task:
            print(f"\n💡 請使用 sessions_spawn 工具執行此任務：")
            print(f"   sessions_spawn({{")
            print(f"     'task': {repr(task['task'][:100])}...,")
            print(f"     'agentId': '{task['agent_id']}',")
            print(f"     'label': '{task['label']}'")
            if task.get('model'):
                print(f"     'model': '{task['model']}'")
            print(f"   }})")
    elif command == 'pop-all':
        tasks = pop_all_tasks()
        if tasks:
            print(f"\n💡 請使用 sessions_spawn 工具依次執行這些任務")
    elif command == 'clear':
        clear_queue()
    else:
        print(f"❌ 未知命令：{command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
