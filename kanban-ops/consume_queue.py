#!/usr/bin/env python3
"""
消費任務隊列

讀取 task_queue/ 目錄中的待執行任務，生成 system event 讓主會話觸發子代理。

注意：此腳本通過 system event 通知主會話執行 sessions_spawn。
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# 路徑配置
WORKSPACE = Path.home() / ".openclaw" / "workspace"
QUEUE_DIR = WORKSPACE / "kanban-ops" / "task_queue"
TASKS_JSON = WORKSPACE / "kanban" / "tasks.json"
CONSUMED_DIR = QUEUE_DIR / "consumed"
READY_TO_SPAWN_FILE = QUEUE_DIR / "ready_to_spawn.jsonl"


def log(level, message):
    """記錄日誌"""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    icon = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}
    print(f"{icon.get(level, '📝')} [{timestamp}] {message}")


def load_tasks():
    """載入 tasks.json"""
    if not os.path.exists(TASKS_JSON):
        log("WARNING", f"tasks.json 不存在：{TASKS_JSON}")
        return []

    try:
        with open(TASKS_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('tasks', [])
    except Exception as e:
        log("ERROR", f"載入 tasks.json 失敗：{e}")
        return []


def save_tasks(tasks):
    """保存任務到 tasks.json"""
    try:
        data = {"tasks": tasks}
        with open(TASKS_JSON, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        log("ERROR", f"保存 tasks.json 失敗：{e}")
        return False


def get_running_sessions():
    """獲取當前運行的子代理會話"""
    try:
        # 使用 subprocess 調用 sessions_list
        import subprocess
        result = subprocess.run(
            ['openclaw', 'sessions', '--json', '--active', '30'],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0 and result.stdout:
            sessions = json.loads(result.stdout)
            # sessions 可能是列表或字典
            if isinstance(sessions, list):
                return [s for s in sessions if isinstance(s, dict) and s.get('session_type') == 'subagent']
            elif isinstance(sessions, dict) and 'sessions' in sessions:
                return [s for s in sessions['sessions'] if isinstance(s, dict) and s.get('session_type') == 'subagent']
            else:
                return []
        else:
            return []
    except Exception as e:
        log("WARNING", f"獲取運行會話失敗：{e}")
        return []


def append_ready_to_spawn(task_data):
    """將任務追加到 ready_to_spawn.jsonl"""
    try:
        with open(READY_TO_SPAWN_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(task_data) + '\n')
        return True
    except Exception as e:
        log("ERROR", f"寫入 ready_to_spawn.jsonl 失敗：{e}")
        return False


def trigger_system_event(message):
    """觸發 system event 通知主會話"""
    try:
        import subprocess
        result = subprocess.run(
            ['openclaw', 'system', 'event', '--text', message],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            log("INFO", f"已發送 system event")
            return True
        else:
            log("WARNING", f"system event 失敗: {result.stderr}")
            return False
    except Exception as e:
        log("WARNING", f"觸發 system event 失敗：{e}")
        return False


def consume_queue(max_tasks=5, max_concurrent=5):
    """消費任務隊列"""
    log("INFO", f"開始消費隊列（max_tasks={max_tasks}, max_concurrent={max_concurrent}）")

    # 確保目錄存在
    CONSUMED_DIR.mkdir(parents=True, exist_ok=True)

    # 獲取當前運行的會話數
    running_sessions = get_running_sessions()
    current_concurrent = len(running_sessions)
    available_slots = max_concurrent - current_concurrent

    if available_slots <= 0:
        log("WARNING", f"並發上限已達（{current_concurrent}/{max_concurrent}），跳過本次消費")
        return []

    # 讀取隊列中的任務（按創建時間排序）
    task_files = sorted(QUEUE_DIR.glob("*.json"), key=lambda f: f.stat().st_mtime)

    if not task_files:
        log("INFO", "隊列為空")
        return []

    log("INFO", f"隊列中有 {len(task_files)} 個任務")

    # 載入 tasks.json
    tasks = load_tasks()
    tasks_dict = {t['id']: t for t in tasks}

    # 消費任務
    triggered = []
    skipped = 0

    for task_file in task_files[:max_tasks]:
        if len(triggered) >= available_slots:
            break

        try:
            with open(task_file, 'r', encoding='utf-8') as f:
                task_data = json.load(f)

            # 檢查任務狀態
            if task_data.get('status') != 'pending':
                log("DEBUG", f"任務 {task_data.get('label')} 狀態為 {task_data.get('status')}，跳過")
                skipped += 1
                continue

            # 檢查任務是否已在運行中
            label = task_data.get('label')
            if tasks_dict.get(label, {}).get('status') == 'in_progress':
                log("DEBUG", f"任務 {label} 已在運行中，跳過")
                skipped += 1
                continue

            # 構建任務參數
            task_message = task_data['task']
            agent_id = task_data['agent_id']
            model = task_data.get('model')
            task_id = label

            log("INFO", f"準備觸發任務：{task_id} (代理: {agent_id}, 模型: {model or '默認'})")

            # 將任務追加到 ready_to_spawn.jsonl
            if not append_ready_to_spawn({
                "task": task_message,
                "agent_id": agent_id,
                "label": task_id,
                "model": model,
                "queued_at": datetime.now(timezone.utc).isoformat()
            }):
                log("ERROR", f"無法將任務加入 ready_to_spawn 隊列")
                continue

            # 更新任務狀態
            task_data['status'] = 'ready_to_spawn'
            task_data['ready_at'] = datetime.now(timezone.utc).isoformat()
            task_data['updated_at'] = datetime.now(timezone.utc).isoformat()

            # 保存任務狀態
            with open(task_file, 'w', encoding='utf-8') as f:
                json.dump(task_data, f, indent=2, ensure_ascii=False)

            # 更新 tasks.json 中的任務
            if task_id in tasks_dict:
                tasks_dict[task_id]['status'] = 'ready_to_spawn'
                tasks_dict[task_id]['updated_at'] = datetime.now(timezone.utc).isoformat()
                save_tasks(tasks)
            else:
                log("WARNING", f"tasks.json 中未找到任務 {task_id}")

            log("SUCCESS", f"任務 {task_id} 已標記為 ready_to_spawn")
            triggered.append(task_id)

            # 移動到已消費目錄
            consumed_file = CONSUMED_DIR / task_file.name
            task_file.rename(consumed_file)

        except Exception as e:
            log("ERROR", f"處理任務文件失敗 {task_file.name}：{e}")
            import traceback
            log("ERROR", traceback.format_exc())

    log("INFO", f"消費完成：觸發 {len(triggered)} 個，跳過 {skipped} 個")

    # 如果有任務被觸發，發送 system event
    if triggered:
        trigger_system_event(f"[Turbo Mode] {len(triggered)} 個任務已準備觸發")

    return triggered


def main():
    """主函數"""
    import argparse

    parser = argparse.ArgumentParser(
        description='消費任務隊列',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--max-tasks', type=int, default=5,
                        help='最多觸發任務數（默認：5）')
    parser.add_argument('--max-concurrent', type=int, default=5,
                        help='最大並發數（默認：5）')
    parser.add_argument('--dry-run', action='store_true',
                        help='試運行模式，不實際觸發')
    parser.add_argument('--list', action='store_true',
                        help='列出隊列中的任務')

    args = parser.parse_args()

    if args.list:
        # 列出隊列中的任務
        print("\n📋 隊列中的任務：\n")
        print("=" * 60)

        task_files = sorted(QUEUE_DIR.glob("*.json"), key=lambda f: f.stat().st_mtime)

        if not task_files:
            print("\n⚠️  隊列為空\n")
        else:
            for i, task_file in enumerate(task_files, 1):
                with open(task_file, 'r') as f:
                    task = json.load(f)

                print(f"\n{i}. {task.get('label', 'N/A')}")
                print(f"   狀態：{task.get('status', 'N/A')}")
                print(f"   代理：{task.get('agent_id', 'N/A')}")
                print(f"   模型：{task.get('model', '默認')}")
                print(f"   創建時間：{task.get('created_at', 'N/A')}")

        print("\n" + "=" * 60)
        return

    if args.dry_run:
        print("\n🔍 試運行模式\n")
        print("=" * 60)

        task_files = list(QUEUE_DIR.glob("*.json"))
        print(f"隊列中有 {len(task_files)} 個任務")
        print(f"最多觸發：{args.max_tasks} 個")
        print(f"最大並發：{args.max_concurrent} 個")

        running_sessions = get_running_sessions()
        available = args.max_concurrent - len(running_sessions)
        print(f"當前運行：{len(running_sessions)} 個")
        print(f"可用槽位：{available} 個")

        print("\n" + "=" * 60)
        return

    # 正常消費
    print("\n🚀 消費任務隊列\n")
    print("=" * 60)

    triggered = consume_queue(
        max_tasks=args.max_tasks,
        max_concurrent=args.max_concurrent
    )

    print("\n" + "=" * 60)

    if triggered:
        print(f"\n✅ 成功觸發 {len(triggered)} 個任務")
        print(f"📄 任務已寫入：{READY_TO_SPAWN_FILE}")
        print(f"💡 請執行：python3 kanban-ops/spawn_ready_tasks.py")
    else:
        print(f"\n📋 本次無任務觸發")


if __name__ == '__main__':
    main()
