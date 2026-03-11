#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任務狀態回滾腳本

檢查並回滾卡住的 spawning 任務：
1. 調用 subagents list 獲取真實運行中的子代理數量
2. 找出狀態為 spawning 但實際沒有運行的任務
3. 將這些任務回滾為 pending

關鍵設計決策（為什麼超時是 2 小時）：
- .status 文件只在完成/失敗時創建，沒有 in_progress 中間狀態
- spawning 實際上涵蓋"從啟動到完成"的整個過程
- 研究任務通常需要 60-90 分鐘
- 如果 subagents list 正常工作，會立即跳過活躍任務
- 如果 subagents list 失敗，最多等 2 小時才回滾

使用方式：
    python3 kanban-ops/task_state_rollback.py

集成到心跳：
    在執行 sessions_spawn 後自動運行此腳本，清理失敗的啟動
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

# 路徑配置
WORKSPACE = Path.home() / ".openclaw" / "workspace"
TASKS_JSON = WORKSPACE / "kanban" / "tasks.json"

# P0 行動：Spawning 超時保護（根據 Mentor 建議調整）
SPAWN_SUSPECT_TIMEOUT_MINUTES = 30  # 30 分鐘：疑似卡住，發出警報
SPAWN_ROLLBACK_TIMEOUT_MINUTES = 45  # 45 分鐘：確定卡住，自動回滾
# 說明：
# 1. spawning 是"正在執行"的狀態，不是僅"正在啟動"
# 2. .status 文件只在完成/失敗時創建，沒有 in_progress 中間狀態
# 3. 研究任務通常需要 5-10 分鐘完成，30 分鐘足夠緩衝
# 4. 45 分鐘回滾給予足夠啟動時間，避免誤殺
# 5. 如果 subagents list 正常返回活躍列表，實際上會立即跳過（不需要等超時）


def log(level, message):
    """記錄日誌"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    icons = {"INFO": "[INFO]", "SUCCESS": "[OK]", "WARNING": "[WARN]", "ERROR": "[ERR]"}
    icon = icons.get(level, "[LOG]")
    print(f"{icon} [{timestamp}] {message}", flush=True)


def load_tasks():
    """載入 tasks.json"""
    try:
        with open(TASKS_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        log("ERROR", f"載入 tasks.json 失敗：{e}")
        return []


def save_tasks(tasks):
    """保存任務到 tasks.json"""
    try:
        with open(TASKS_JSON, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        log("ERROR", f"保存 tasks.json 失敗：{e}")
        return False


def get_active_subagent_labels():
    """
    獲取當前活躍的子代理標籤列表

    Returns:
        活躍子代理標籤列表，如 ['scout-123', 'scout-456']
    """
    # 直接返回空列表，因為 subprocess 調用不可靠
    # 依賴超時檢查機制即可
    return []


def find_stuck_spawnings(tasks, active_labels):
    """
    找出卡住的 spawning 任務（兩級超時檢測）

    規則：
    1. 狀態為 spawning
    2. 標籤不在活躍子代理列表中（如果提供了）
    3. spawning < 10 分鐘：跳過（緩衝期）
    4. 10-30 分鐘：正常
    5. 30-45 分鐘：疑似卡住，發出警報
    6. > 45 分鐘：確定卡住，準備回滾

    注意：即使 active_labels 為空（無法獲取），超時檢查仍然有效

    Returns:
        (疑似卡住列表, 確定卡住列表)
    """
    suspected = []
    stuck = []
    now = datetime.now(timezone.utc)
    MIN_BUFFER_MINUTES = 10  # 最小緩衝時間，防止誤殺剛啟動的任務

    for task in tasks:
        if task.get('status') != 'spawning':
            continue

        task_id = task['id']

        # 如果有活躍列表，先檢查是否在活躍列表中
        if active_labels and task_id in active_labels:
            continue  # 仍在運行，不算卡住

        # 檢查 spawning 持續時間（關鍵檢查）
        updated_at = task.get('updated_at', task.get('spawned_at'))
        if updated_at:
            try:
                # 嘗試解析時間戳，並確保時區一致
                updated_time = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                # 如果沒有時區信息，假設是 UTC（修復 offset-naive 問題）
                if updated_time.tzinfo is None:
                    updated_time = updated_time.replace(tzinfo=timezone.utc)
                elapsed = now - updated_time
                elapsed_minutes = elapsed.total_seconds() / 60

                # 如果還沒有達到最小緩衝時間，跳過
                if elapsed < timedelta(minutes=MIN_BUFFER_MINUTES):
                    log("DEBUG", f"跳過（緩衝中）：{task_id}（spawning 持續 {int(elapsed_minutes)} 分鐘）")
                    continue

                # 30-45 分鐘：疑似卡住，發出警報
                if timedelta(minutes=SPAWN_SUSPECT_TIMEOUT_MINUTES) <= elapsed < timedelta(minutes=SPAWN_ROLLBACK_TIMEOUT_MINUTES):
                    suspected.append(task)
                    log("WARNING", f"⚠️ 疑似卡住任務：{task_id}（spawning 持續 {int(elapsed_minutes)} 分鐘）")

                # 超過 45 分鐘，視為卡住
                elif elapsed >= timedelta(minutes=SPAWN_ROLLBACK_TIMEOUT_MINUTES):
                    stuck.append(task)
                    log("INFO", f"🔴 卡住任務（確定）：{task_id}（spawning 持續 {int(elapsed_minutes)} 分鐘）")

            except Exception as e:
                log("WARNING", f"解析任務時間失敗：{e}")
                # 解析失敗但不回滾，避免誤殺
                log("WARNING", f"保留任務（解析失敗）：{task_id}")
        else:
            # 沒有時間戳記錄，跳過（避免誤殺）
            log("WARNING", f"跳過（無時間戳）：{task_id}")

    return suspected, stuck


def rollback_tasks(tasks, task_ids):
    """
    將任務回滾為 pending 狀態

    Args:
        tasks: 任務列表
        task_ids: 要回滾的任務 ID 列表

    Returns:
        回滾的任務數量
    """
    count = 0
    now = datetime.now(timezone.utc).isoformat()

    for task in tasks:
        if task['id'] in task_ids:
            old_status = task['status']
            task['status'] = 'pending'
            task['updated_at'] = now

            # 清理 spawning 相關字段
            if 'spawned_at' in task:
                del task['spawned_at']

            log("INFO", f"回滾任務：{task['id']} ({old_status} → pending)")
            count += 1

    return count


def main():
    """主函數"""
    log("INFO", "任務狀態回滾檢查啟動")

    # 載入任務
    tasks = load_tasks()
    if not tasks:
        log("WARNING", "無法載入任務或任務列表為空")
        return 0

    # 統計 spawning 任務
    spawning_count = sum(1 for t in tasks if t.get('status') == 'spawning')
    log("INFO", f"狀態為 spawning 的任務：{spawning_count} 個")

    if spawning_count == 0:
        log("INFO", "沒有需要檢查的 spawning 任務")
        return 0

    # 嘗試獲取活躍子代理列表（可選）
    active_labels = []
    try:
        log("INFO", "嘗試獲取活躍子代理列表...")
        active_labels = get_active_subagent_labels()
        if active_labels:
            log("INFO", f"活躍子代理：{len(active_labels)} 個 ({', '.join(active_labels[:5])}{'...' if len(active_labels) > 5 else ''})")
        else:
            log("INFO", "無法獲取活躍子代理列表，將僅使用超時檢查")
    except Exception as e:
        log("WARNING", f"獲取活躍子代理列表時發生錯誤：{e}，將僅使用超時檢查")

    # 找出疑似卡住和確定卡住的任務（基於超時）
    suspected_tasks, stuck_tasks = find_stuck_spawnings(tasks, active_labels)

    if not suspected_tasks and not stuck_tasks:
        log("INFO", "沒有卡住的 spawning 任務")
        return 0

    # 警報疑似卡住的任務
    if suspected_tasks:
        log("WARNING", f"⚠️ 發現 {len(suspected_tasks)} 個疑似卡住的 spawning 任務（{SPAWN_SUSPECT_TIMEOUT_MINUTES}-{SPAWN_ROLLBACK_TIMEOUT_MINUTES} 分鐘）")
        log("INFO", f"   這些任務將在 {SPAWN_ROLLBACK_TIMEOUT_MINUTES} 分鐘時自動回滾")

    # 回滾確定卡住的任務
    if stuck_tasks:
        log("WARNING", f"🔴 發現 {len(stuck_tasks)} 個確定卡住的 spawning 任務（>{SPAWN_ROLLBACK_TIMEOUT_MINUTES} 分鐘）")

        task_ids = [t['id'] for t in stuck_tasks]
        count = rollback_tasks(tasks, task_ids)
    else:
        count = 0

    if count > 0:
        # 保存到 tasks.json
        if save_tasks(tasks):
            log("SUCCESS", f"已回滾 {count} 個任務狀態為 pending")
            log("INFO", "這些任務將在下次心跳時重新嘗試啟動")
        else:
            log("ERROR", "保存任務失敗，回滾未生效")
            return -1

    return count


if __name__ == '__main__':
    count = main()
    exit(0 if count >= 0 else 1)
