#!/usr/bin/env python3
"""
任務註冊系統

確保所有任務在啟動前都已正確註冊到 tasks.json

功能：
1. 驗證任務是否已註冊
2. 註冊新任務到 tasks.json
3. 更新任務狀態
4. 修復未註冊的運行中任務
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

# 路徑配置
WORKSPACE = Path.home() / ".openclaw" / "workspace"
TASKS_JSON = WORKSPACE / "kanban" / "tasks.json"


def log(level, message):
    """記錄日誌"""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    icon = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}
    print(f"{icon.get(level, '📝')} [{timestamp}] {message}")


def load_tasks() -> List[Dict]:
    """載入 tasks.json"""
    if not TASKS_JSON.exists():
        log("WARNING", f"tasks.json 不存在：{TASKS_JSON}")
        return []

    try:
        with open(TASKS_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)

            # 處理多種格式
            if isinstance(data, dict):
                if 'tasks' in data:
                    return data['tasks']
                else:
                    # 舊格式：{"task_id": {...}}
                    return list(data.values())
            elif isinstance(data, list):
                return data
            else:
                log("ERROR", f"未知 tasks.json 格式：{type(data)}")
                return []
    except Exception as e:
        log("ERROR", f"載入 tasks.json 失敗：{e}")
        return []


def save_tasks(tasks: List[Dict]) -> bool:
    """保存任務到 tasks.json"""
    try:
        # 確保目錄存在
        TASKS_JSON.parent.mkdir(parents=True, exist_ok=True)

        # 檢查是否使用舊格式或新格式
        use_old_format = False

        if TASKS_JSON.exists():
            with open(TASKS_JSON, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    if isinstance(data, dict) and 'tasks' not in data:
                        use_old_format = True
                except:
                    pass

        if use_old_format:
            # 舊格式：{"task_id": {...}}
            tasks_dict = {t['id']: t for t in tasks}
            with open(TASKS_JSON, 'w', encoding='utf-8') as f:
                json.dump(tasks_dict, f, indent=2, ensure_ascii=False)
        else:
            # 新格式：{"tasks": [{...}, {...}]} 或直接列表
            data = {"tasks": tasks}
            with open(TASKS_JSON, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        return True
    except Exception as e:
        log("ERROR", f"保存 tasks.json 失敗：{e}")
        return False


def find_task(task_id: str, tasks: List[Dict]) -> Optional[Dict]:
    """查找任務"""
    for task in tasks:
        if task.get('id') == task_id:
            return task
    return None


def register_task(task: Dict) -> bool:
    """註冊新任務到 tasks.json"""
    tasks = load_tasks()

    # 檢查任務是否已存在
    if find_task(task['id'], tasks):
        log("WARNING", f"任務 {task['id']} 已存在，跳過註冊")
        return True

    # 添加任務
    task['created_at'] = task.get('created_at', datetime.now(timezone.utc).isoformat())
    task['updated_at'] = datetime.now(timezone.utc).isoformat()

    tasks.append(task)

    # 保存任務
    if save_tasks(tasks):
        log("SUCCESS", f"任務 {task['id']} 已註冊")
        return True
    else:
        log("ERROR", f"任務 {task['id']} 註冊失敗")
        return False


def verify_task_registered(task_id: str) -> bool:
    """驗證任務是否已註冊"""
    tasks = load_tasks()
    return find_task(task_id, tasks) is not None


def update_task_status(task_id: str, status: str, metadata: Optional[Dict] = None) -> bool:
    """更新任務狀態"""
    tasks = load_tasks()
    task = find_task(task_id, tasks)

    if not task:
        log("WARNING", f"任務 {task_id} 不存在，無法更新狀態")
        return False

    # 更新狀態
    task['status'] = status
    task['updated_at'] = datetime.now(timezone.utc).isoformat()

    # 更新元數據
    if metadata:
        for key, value in metadata.items():
            task[key] = value

    # 保存任務
    if save_tasks(tasks):
        log("SUCCESS", f"任務 {task_id} 狀態已更新為 {status}")
        return True
    else:
        log("ERROR", f"任務 {task_id} 狀態更新失敗")
        return False


def create_task_from_spawn_params(task_id: str, task_message: str, agent_id: str, model: str, output_path: str) -> Dict:
    """從 sessions_spawn 參數創建任務"""
    return {
        "id": task_id,
        "title": task_message.split("TASK: ")[1].split("\n")[0] if "TASK: " in task_message else task_message[:50],
        "status": "pending",
        "agent": agent_id,
        "model": model,
        "priority": "normal",
        "input_paths": [],
        "output_path": output_path,
        "depends_on": [],
        "next_tasks": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
        "notes": task_message,
        "created_by": "system",
        "time_tracking": {
            "estimated_time": {
                "min": 30,
                "max": 60
            },
            "complexity_level": 2,
            "recommended_model": model
        }
    }


def validate_before_spawn(task_id: str, task_message: str, agent_id: str, model: str, output_path: str) -> bool:
    """
    啟動前驗證

    檢查任務是否已註冊，如果未註冊則自動註冊
    """
    if verify_task_registered(task_id):
        log("INFO", f"任務 {task_id} 已註冊")
        return True

    log("WARNING", f"任務 {task_id} 未註冊，自動註冊中...")

    # 創建任務
    task = create_task_from_spawn_params(task_id, task_message, agent_id, model, output_path)

    # 註冊任務
    if register_task(task):
        log("SUCCESS", f"任務 {task_id} 已自動註冊")
        return True
    else:
        log("ERROR", f"任務 {task_id} 自動註冊失敗，阻止啟動")
        return False


def check_unregistered_running_tasks() -> List[str]:
    """
    檢查未註冊的運行中任務

    返回未註冊的任務 ID 列表
    """
    try:
        # 使用 subprocess 獲取運行中的子代理
        import subprocess
        result = subprocess.run(
            ['openclaw', 'sessions', '--json', '--active', '30'],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0 or not result.stdout:
            return []

        sessions = json.loads(result.stdout)

        # 提取子代理會話
        if isinstance(sessions, list):
            subagents = [s for s in sessions if isinstance(s, dict) and s.get('session_type') == 'subagent']
        elif isinstance(sessions, dict) and 'sessions' in sessions:
            subagents = [s for s in sessions['sessions'] if isinstance(s, dict) and s.get('session_type') == 'subagent']
        else:
            return []

        # 檢查每個子代理的任務是否已註冊
        unregistered = []
        tasks = load_tasks()

        for subagent in subagents:
            label = subagent.get('label', '')
            if not label:
                continue

            # 檢查任務是否已註冊
            if not find_task(label, tasks):
                unregistered.append(label)
                log("WARNING", f"發現未註冊的運行中任務：{label}")

        return unregistered

    except Exception as e:
        log("ERROR", f"檢查運行中任務失敗：{e}")
        return []


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='任務註冊系統',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('command', nargs='?', choices=['verify', 'register', 'update-status', 'check-unregistered'],
                        help='命令')

    parser.add_argument('--task-id', help='任務 ID')
    parser.add_argument('--status', help='任務狀態')
    parser.add_argument('--task-message', help='任務消息')
    parser.add_argument('--agent-id', help='代理 ID')
    parser.add_argument('--model', help='模型')
    parser.add_argument('--output-path', help='輸出路徑')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == 'verify':
        if not args.task_id:
            log("ERROR", "請提供 --task-id")
            return

        if verify_task_registered(args.task_id):
            log("SUCCESS", f"任務 {args.task_id} 已註冊")
        else:
            log("WARNING", f"任務 {args.task_id} 未註冊")

    elif args.command == 'register':
        # TODO: 實現從命令行註冊任務
        log("INFO", "register 命令尚未實現")

    elif args.command == 'update-status':
        if not args.task_id or not args.status:
            log("ERROR", "請提供 --task-id 和 --status")
            return

        update_task_status(args.task_id, args.status)

    elif args.command == 'check-unregistered':
        unregistered = check_unregistered_running_tasks()

        if unregistered:
            log("WARNING", f"發現 {len(unregistered)} 個未註冊的運行中任務")
            for task_id in unregistered:
                log("WARNING", f"  - {task_id}")
        else:
            log("SUCCESS", "所有運行中任務都已註冊")


if __name__ == '__main__':
    main()
