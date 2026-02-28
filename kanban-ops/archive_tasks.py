#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任務歸檔腳本

將舊的完成任務移到 archive，減少 tasks.json 大小

歸檔規則：
1. 完成超過 7 天的任務
2. 無 completed_at 時間戳的完成任務（使用 updated_at 判斷）

使用方式：
    python3 kanban-ops/archive_tasks.py [dry-run] [--days N]

參數：
    dry-run: 預覽要歸檔的任務，不實際執行
    --days N: 歸檔閾值（天數），默認 7

歸檔位置：
    kanban/archive/tasks-{YYYY-MM-DD}.json
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

# 路徑配置
WORKSPACE = Path.home() / ".openclaw" / "workspace"
TASKS_JSON = WORKSPACE / "kanban" / "tasks.json"
ARCHIVE_DIR = WORKSPACE / "kanban" / "archive"
ARCHIVE_DAYS = 7  # 完成超過 7 天的任務歸檔


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


def archive_tasks(tasks_to_archive):
    """歸檔任務到 archive 文件夾"""
    # 創建 archive 目錄
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    # 生成歸檔文件名
    date_str = datetime.now().strftime("%Y-%m-%d")
    archive_file = ARCHIVE_DIR / f"tasks-{date_str}.json"

    # 如果歸檔文件已存在，加載並合併
    archived = []
    if archive_file.exists():
        try:
            with open(archive_file, 'r', encoding='utf-8') as f:
                archived = json.load(f)
            log("INFO", f"已存在歸檔文件，包含 {len(archived)} 個任務")
        except Exception as e:
            log("WARNING", f"載入歸檔文件失敗：{e}")

    # 添加新任務
    archived.extend(tasks_to_archive)

    # 保存歸檔
    try:
        with open(archive_file, 'w', encoding='utf-8') as f:
            json.dump(archived, f, indent=2, ensure_ascii=False)
        log("SUCCESS", f"已歸檔 {len(tasks_to_archive)} 個任務到 {archive_file}")
        return True
    except Exception as e:
        log("ERROR", f"保存歸檔文件失敗：{e}")
        return False


def find_tasks_to_archive(tasks, days=ARCHIVE_DAYS):
    """
    找出需要歸檔的任務

    Args:
        tasks: 任務列表
        days: 歸檔閾值（天數）

    Returns:
        (to_archive, count_info) - 歸檔任務列表和統計信息
    """
    now = datetime.now(timezone.utc)
    to_archive = []

    stats = {
        'total_completed': 0,
        f'over_{days}_days': 0,
        'no_timestamp': 0,
        'archived': 0
    }

    for task in tasks:
        if task.get('status') != 'completed':
            continue

        stats['total_completed'] += 1

        # 檢查 completed_at
        completed_at = task.get('completed_at')
        if completed_at:
            try:
                ct = datetime.fromisoformat(completed_at.replace('Z', '+00:00'))
                elapsed = now - ct

                # 超過指定天數
                if elapsed > timedelta(days=days):
                    to_archive.append(task)
                    stats[f'over_{days}_days'] += 1
                    stats['archived'] += 1
            except:
                pass

        # 無 completed_at，檢查 updated_at
        elif task.get('updated_at'):
            try:
                ut = datetime.fromisoformat(task['updated_at'].replace('Z', '+00:00'))
                elapsed = now - ut

                # 超過指定天數
                if elapsed > timedelta(days=days):
                    to_archive.append(task)
                    stats['no_timestamp'] += 1
                    stats['archived'] += 1
            except:
                pass

    return to_archive, stats


def main():
    """主函數"""
    # 解析命令行參數
    dry_run = False
    archive_days = ARCHIVE_DAYS

    for arg in sys.argv[1:]:
        if arg == 'dry-run':
            dry_run = True
        elif arg.startswith('--days='):
            try:
                archive_days = int(arg.split('=')[1])
            except:
                log("WARNING", f"無效的 --days 參數：{arg}，使用默認值 {ARCHIVE_DAYS}")

    log("INFO", "任務歸檔檢查啟動")

    if dry_run:
        log("INFO", "預覽模式（不會實際歸檔）")

    log("INFO", f"歸檔閾值：{archive_days} 天")

    # 載入任務
    tasks = load_tasks()
    if not tasks:
        log("WARNING", "無法載入任務或任務列表為空")
        return 0

    log("INFO", f"總任務數：{len(tasks)}")

    # 找出需要歸檔的任務
    to_archive, stats = find_tasks_to_archive(tasks, days=archive_days)

    if not to_archive:
        log("INFO", "沒有需要歸檔的任務")
        return 0

    # 顯示統計
    log("INFO", f"完成任務總數：{stats['total_completed']}")
    log("INFO", f"完成超過 {archive_days} 天：{stats.get(f'over_{archive_days}_days', 0)}")
    log("INFO", f"無時間戳但超過 {archive_days} 天：{stats['no_timestamp']}")
    log("INFO", f"可歸檔任務：{stats['archived']}")

    if dry_run:
        log("INFO", "預覽模式：不會執行歸檔")
        print()
        for t in to_archive[:5]:
            print(f"  - {t['id']}: {t.get('title', '')[:50]}")
        if len(to_archive) > 5:
            print(f"  ... 還有 {len(to_archive) - 5} 個")
        return 0

    # 執行歸檔
    if not archive_tasks(to_archive):
        log("ERROR", "歸檔失敗")
        return -1

    # 從主任務列表中移除歸檔的任務
    archived_ids = {t['id'] for t in to_archive}
    remaining_tasks = [t for t in tasks if t['id'] not in archived_ids]

    log("INFO", f"歸檔前：{len(tasks)} 個任務")
    log("INFO", f"歸檔後：{len(remaining_tasks)} 個任務")
    log("INFO", f"減少：{len(tasks) - len(remaining_tasks)} 個任務")

    # 保存更新後的任務列表
    if save_tasks(remaining_tasks):
        log("SUCCESS", "任務列表已更新")
        return 0
    else:
        log("ERROR", "保存任務列表失敗")
        return -1


if __name__ == '__main__':
    exit(main())
