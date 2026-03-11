#!/usr/bin/env python3
"""
執行 Spawn 命令並追蹤 API 調用（P0 行動整合）

此腳本由主會話調用，用於：
1. 讀取 spawn_commands.jsonl
2. 執行 sessions_spawn
3. 使用 api_tracker 追蹤 API 調用
4. 更新任務狀態

使用方式：
    python3 kanban-ops/execute_spawn_with_tracking.py

或直接在主會話中使用 sessions_spawn，然後調用 track_spawn_result() 記錄結果。
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

# 路徑配置
WORKSPACE = Path.home() / ".openclaw" / "workspace"
TASKS_JSON = WORKSPACE / "kanban" / "tasks.json"
SPAWN_COMMANDS_FILE = WORKSPACE / "kanban" / "spawn_commands.jsonl"

# 導入 API 追蹤器
sys.path.insert(0, str(WORKSPACE / "kanban-ops"))
from api_tracker import get_tracker


def track_spawn_result(task_id: str, status_code: str, error_message: str = None,
                        rate_limit_headers: dict = None):
    """
    追蹤 spawn 結果（P0 行動：API 追蹤）

    Args:
        task_id: 任務 ID
        status_code: OpenClaw status code (e.g., "accepted", "rejected")
        error_message: 錯誤訊息（如果有）
        rate_limit_headers: Rate limit headers (如果可用)
    """
    # 導入 auto_spawn_heartbeat 獲取啟動開始時間
    from auto_spawn_heartbeat import get_spawn_start_time

    start_time = get_spawn_start_time(task_id)
    if start_time is None:
        # 如果沒有記錄開始時間，使用當前時間（這意味著計算的延遲不準確）
        start_time = datetime.now(timezone.utc)

    tracker = get_tracker()
    tracker.record_call(
        task_id=task_id,
        action='spawn',
        start_time=start_time,
        status_code=status_code,
        error_message=error_message,
        rate_limit_headers=rate_limit_headers or {}
    )


def update_task_from_spawn_result(task_id: str, result: dict):
    """
    根據 spawn 結果更新任務

    Args:
        task_id: 任務 ID
        result: sessions_spawn 返回的結果
            {
                "status": "accepted" | "rejected",
                "childSessionKey": "...",
                "runId": "...",
                "modelApplied": bool
            }
    """
    try:
        with open(TASKS_JSON, 'r', encoding='utf-8') as f:
            tasks = json.load(f)

        task = next((t for t in tasks if t.get('id') == task_id), None)
        if not task:
            print(f"⚠️ 任務 {task_id} 不存在", flush=True)
            return

        # 更新任務狀態
        status_code = result.get('status', 'unknown')

        if status_code == 'accepted':
            task['status'] = 'in_progress'
            task['subagent_session_key'] = result.get('childSessionKey')
            task['run_id'] = result.get('runId')
        else:
            # rejected 或其他錯誤
            task['status'] = 'failed'
            task['error'] = f"Spawn rejected: {status_code}"

        task['updated_at'] = datetime.now(timezone.utc).isoformat()

        # 保存
        with open(TASKS_JSON, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, indent=2, ensure_ascii=False)

        # 追蹤 API 調用
        error_message = None
        if status_code != 'accepted':
            error_message = f"Spawn failed with status: {status_code}"

        track_spawn_result(
            task_id=task_id,
            status_code=status_code,
            error_message=error_message
        )

        print(f"✅ 任務 {task_id} 狀態已更新: {status_code}", flush=True)

    except Exception as e:
        print(f"❌ 更新任務 {task_id} 時出錯: {e}", flush=True)
        # 追蹤錯誤
        track_spawn_result(
            task_id=task_id,
            status_code='error',
            error_message=str(e)
        )


def main():
    """主函數"""
    if not SPAWN_COMMANDS_FILE.exists():
        print("ℹ️ 沒有待執行的 spawn 命令", flush=True)
        return

    print("📋 讀取 spawn 命令...", flush=True)

    with open(SPAWN_COMMANDS_FILE, 'r', encoding='utf-8') as f:
        commands = [json.loads(line) for line in f]

    print(f"📋 找到 {len(commands)} 個 spawn 命令", flush=True)

    # 注意：這裡只是展示如何追蹤 API 調用
    # 實際的 sessions_spawn 應該由主會話執行
    # 執行完成後，調用 track_spawn_result() 或 update_task_from_spawn_result()

    print("\n💡 使用說明：", flush=True)
    print("1. 主會話讀取 spawn_commands.jsonl", flush=True)
    print("2. 執行 sessions_spawn", flush=True)
    print("3. 調用 update_task_from_spawn_result(task_id, result) 更新任務並追蹤", flush=True)
    print("4. 查看統計：python3 kanban-ops/api_tracker.py stats", flush=True)
    print("5. 查看診斷報告：python3 kanban-ops/api_tracker.py report", flush=True)


if __name__ == '__main__':
    main()
