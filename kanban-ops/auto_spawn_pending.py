#!/usr/bin/env python3
"""
自動任務啟動器 - 當 sub-agent 閒下來時自動認領 pending 任務

核心機制：
1. 檢查並發限制（最多 5 個）
2. 找出可啟動的 pending 任務
3. 自動啟動直到達到並發限制
4. 優先啟動高優先級任務

使用方式：
    python3 kanban-ops/auto_spawn_pending.py [max_tasks]

集成到心跳：
    每次心跳時執行此腳本，自動補充任務
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# 路徑配置
TASKS_JSON = Path.home() / ".openclaw/workspace/kanban/tasks.json"
MAX_CONCURRENT = 5  # 總體並發限制


def log(level, message):
    """記錄日誌"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}
    print(f"{icons.get(level, '📝')} [{timestamp}] {message}", flush=True)


def load_tasks():
    """載入 tasks.json"""
    try:
        with open(TASKS_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        log("ERROR", f"載入 tasks.json 失敗：{e}")
        return []


def count_in_progress(tasks):
    """統計執行中的任務"""
    return sum(1 for t in tasks if t['status'] == 'in_progress')


def find_spawnable_tasks(tasks, max_spawn=5):
    """
    找出可啟動的任務

    規則：
    1. 狀態為 pending
    2. 沒有依賴或依賴已完成
    3. 按優先級排序（high > medium > low）
    4. 同優先級按創建時間排序

    Returns:
        可啟動的任務列表
    """
    spawnable = []

    for task in tasks:
        if task['status'] != 'pending':
            continue

        # 檢查依賴
        deps = task.get('dependencies', [])
        if deps:
            # 檢查所有依賴是否完成
            all_deps_completed = True
            for dep_id in deps:
                dep_task = next((t for t in tasks if t['id'] == dep_id), None)
                if dep_task and dep_task['status'] != 'completed':
                    all_deps_completed = False
                    break

            if not all_deps_completed:
                continue  # 依賴未完成，跳過

        spawnable.append(task)

    # 按優先級排序
    priority_order = {'high': 0, 'medium': 1, 'low': 2, 'normal': 1}
    spawnable.sort(key=lambda t: (
        priority_order.get(t.get('priority', 'normal'), 1),
        t['created_at']
    ))

    return spawnable[:max_spawn]


def print_spawn_commands(tasks, max_spawn=5):
    """
    打印啟動命令

    Args:
        tasks: 任務列表
        max_spawn: 最多打印多少個命令

    Returns:
        需要啟動的任務數量
    """
    spawnable = find_spawnable_tasks(tasks, max_spawn)

    if not spawnable:
        log("INFO", "沒有可啟動的任務")
        return 0

    log("INFO", f"找到 {len(spawnable)} 個可啟動的任務")
    log("INFO", "=" * 60)

    for i, task in enumerate(spawnable, 1):
        task_id = task['id']
        agent = task.get('agent', 'research')
        priority = task.get('priority', 'normal')
        title = task['title'][:50]

        # 構建 spawn 命令
        spawn_dict = {
            'task': task.get('task', f"TASK: {title}"),
            'agentId': agent,
            'label': task_id
        }

        # 如果指定了 model
        if task.get('model'):
            spawn_dict['model'] = task['model']

        # 轉換為 sessions_spawn 呼叫
        json_str = json.dumps(spawn_dict, ensure_ascii=False, indent=2)

        print(f"\n【任務 {i}】{task_id} [{priority.upper()}]")
        print(f"標題：{title}")
        print(f"代理：{agent}")
        print(f"\n啟動命令：")
        print(f"sessions_spawn({json_str})")

    log("INFO", "=" * 60)

    return len(spawnable)


def main():
    """主函數"""
    log("INFO", "自動任務啟動器啟動")

    # 載入任務
    tasks = load_tasks()
    if not tasks:
        log("ERROR", "無法載入任務")
        sys.exit(1)

    # 統計當前狀態
    in_progress_count = count_in_progress(tasks)
    available_slots = MAX_CONCURRENT - in_progress_count

    log("INFO", f"執行中：{in_progress_count} 個")
    log("INFO", f"可用位置：{available_slots} 個")

    if available_slots <= 0:
        log("INFO", "並發限制已滿，無需啟動新任務")
        sys.exit(0)

    # 找出可啟動的任務
    spawn_count = print_spawn_commands(tasks, available_slots)

    if spawn_count > 0:
        log("WARNING", f"\n📝 請手動執行上述 {spawn_count} 個 sessions_spawn 命令")
        log("WARNING", "執行完成後，系統會自動更新任務狀態")
    else:
        log("INFO", "沒有待處理的任務")


if __name__ == '__main__':
    main()
