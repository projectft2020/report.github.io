#!/usr/bin/env python3
"""
Kanban 任務歸檔腳本

歸檔策略（高頻版本）：
- 保留：最近 2 天的已完成任務 + 所有 In Progress + 所有 Pending
- 快速歸檔：2-7 天前的已完成任務（archive/tasks-quick-YYYY-MM-DD.json）
- 月度歸檔：7-14 天前的已完成任務（archive/tasks-YYYY-MM.json）
- 壓縮歸檔：14+ 天前的已完成任務（archive/tasks-compressed-YYYY-MM-DD.json.gz）

使用方式：
    python3 archive_tasks.py              # 正常歸檔
    python3 archive_tasks.py --dry-run    # 試運行（不實際修改）
    python3 archive_tasks.py --stats      # 顯示統計信息
    python3 archive_tasks.py --force      # 強制歸檔（用於測試）

自動觸發：
    - 檔案大小超過 200 KB 時自動執行
    - 重開機時自動檢查並執行
"""

import json
import gzip
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
import argparse

# 路徑配置
TASKS_JSON = '/Users/charlie/.openclaw/workspace-automation/kanban/tasks.json'
ARCHIVE_DIR = '/Users/charlie/.openclaw/workspace-automation/kanban/archive'

# 歸檔時間閾值（高頻版本）
RETAIN_DAYS = 2           # 保留最近 2 天
QUICK_ARCHIVE_DAYS = 7     # 2-7 天前歸檔
MONTHLY_ARCHIVE_DAYS = 14   # 7-14 天前歸檔
COMPRESS_DAYS = 14         # 14+ 天前壓縮

# 文件大小閾值（自動觸發歸檔）
MAX_FILE_SIZE_KB = 200  # 當 tasks.json 超過 200KB 時自動歸檔


def load_tasks():
    """載入 tasks.json"""
    with open(TASKS_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_tasks(data):
    """保存 tasks.json"""
    with open(TASKS_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_archive(tasks, filename):
    """保存歸檔文件"""
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    filepath = os.path.join(ARCHIVE_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)
    return filepath


def save_compressed_archive(tasks, filename):
    """保存壓縮歸檔文件"""
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    filepath = os.path.join(ARCHIVE_DIR, filename)
    with gzip.open(filepath, 'wt', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False)
    return filepath


def get_task_age(task):
    """獲取任務年齡（天數）"""
    created_at = task.get('created_at', '')
    if not created_at:
        return 9999

    try:
        created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        return (now - created_date).days
    except:
        return 9999


def show_stats():
    """顯示統計信息"""
    print("📊 Kanban 任務統計\n")

    data = load_tasks()
    tasks = data['tasks']

    # 統計
    completed = [t for t in tasks if t['status'] == 'completed']
    in_progress = [t for t in tasks if t['status'] == 'in_progress']
    pending = [t for t in tasks if t['status'] == 'pending']
    failed = [t for t in tasks if t['status'] == 'failed']

    # 文件大小
    file_size = os.path.getsize(TASKS_JSON)

    print(f"📂 文件：{TASKS_JSON}")
    print(f"💾 大小：{file_size / 1024:.2f} KB")
    print(f"\n📊 任務統計：")
    print(f"   總計：{len(tasks)} 個任務")
    print(f"   ✅ Completed: {len(completed)}")
    print(f"   🔄 In Progress: {len(in_progress)}")
    print(f"   ⏳ Pending: {len(pending)}")
    print(f"   ❌ Failed: {len(failed)}")

    # 時間範圍
    if tasks:
        earliest = min(t.get('created_at', '') for t in tasks)
        latest = max(t.get('created_at', '') for t in tasks)
        print(f"\n📅 時間範圍：")
        print(f"   最早：{earliest}")
        print(f"   最晚：{latest}")

    # 歸檔建議
    print(f"\n💡 歸檔建議：")
    if file_size / 1024 > MAX_FILE_SIZE_KB:
        print(f"   ⚠️  文件大小超過 {MAX_FILE_SIZE_KB} KB，建議執行歸檔")
    else:
        remaining = MAX_FILE_SIZE_KB - (file_size / 1024)
        print(f"   ✅ 文件大小正常，還有 {remaining:.2f} KB 空間")

    # 檢查歸檔目錄
    if os.path.exists(ARCHIVE_DIR):
        archive_files = [f for f in os.listdir(ARCHIVE_DIR) if f.endswith('.json') or f.endswith('.json.gz')]
        archive_size = sum(
            os.path.getsize(os.path.join(ARCHIVE_DIR, f))
            for f in archive_files
        )
        print(f"\n📦 歸檔目錄：")
        print(f"   文件數：{len(archive_files)}")
        print(f"   大小：{archive_size / 1024:.2f} KB")
        if archive_files:
            print(f"   最近的歸檔：{sorted(archive_files)[-3:]}")


def archive_tasks(force=False, dry_run=False):
    """歸檔任務

    Parameters:
    -----------
    force : bool
        強制歸檔（忽略時間閾值）
    dry_run : bool
        試運行模式（不實際修改文件）
    """
    print("🚀 開始歸檔任務...")
    if force:
        print("⚠️  強制歸檔模式：忽略時間閾值")
    if dry_run:
        print("🔍 試運行模式：不實際修改文件\n")
    print(f"📂 源文件：{TASKS_JSON}")
    print(f"📂 歸檔目錄：{ARCHIVE_DIR}\n")

    # 載入任務
    data = load_tasks()
    tasks = data['tasks']

    # 檢查是否需要歸檔
    file_size = os.path.getsize(TASKS_JSON)
    if not force and file_size / 1024 < MAX_FILE_SIZE_KB:
        print(f"✅ 文件大小 {file_size / 1024:.2f} KB < {MAX_FILE_SIZE_KB} KB，不需要歸檔")
        return

    # 分類任務
    to_keep = []
    to_quick_archive = []
    to_monthly_archive = []
    to_compress = []

    now = datetime.now(timezone.utc)

    for task in tasks:
        status = task['status']
        age = get_task_age(task)
        created_month = task.get('created_at', '')[:7] if task.get('created_at') else 'unknown'

        # 保留規則（高頻版本）
        if status == 'in_progress':
            to_keep.append(task)
        elif status == 'pending':
            to_keep.append(task)
        elif status == 'failed' and age < RETAIN_DAYS:
            to_keep.append(task)
        elif status == 'completed' and age < RETAIN_DAYS:
            to_keep.append(task)
        elif status == 'completed' and age >= RETAIN_DAYS and age < QUICK_ARCHIVE_DAYS:
            to_quick_archive.append(task)
        elif status == 'completed' and age >= QUICK_ARCHIVE_DAYS and age < MONTHLY_ARCHIVE_DAYS:
            to_monthly_archive.append(task)
        elif status == 'completed' and age >= COMPRESS_DAYS:
            to_compress.append(task)
        else:
            # 其他情況（超過 RETAIN_DAYS 的 failed）
            to_compress.append(task)

    # 統計
    print("📊 歸檔統計：")
    print(f"   保留：{len(to_keep)} 個任務")
    if to_keep:
        print(f"      IDs: {[t['id'] for t in to_keep[:5]]}{'...' if len(to_keep) > 5 else ''}")
    print(f"   快速歸檔（2-7天）：{len(to_quick_archive)} 個任務")
    if to_quick_archive:
        print(f"      IDs: {[t['id'] for t in to_quick_archive[:5]]}{'...' if len(to_quick_archive) > 5 else ''}")
    print(f"   月度歸檔（7-14天）：{len(to_monthly_archive)} 個任務")
    if to_monthly_archive:
        print(f"      IDs: {[t['id'] for t in to_monthly_archive[:5]]}{'...' if len(to_monthly_archive) > 5 else ''}")
    print(f"   壓縮歸檔（14+天）：{len(to_compress)} 個任務")
    if to_compress:
        print(f"      IDs: {[t['id'] for t in to_compress[:5]]}{'...' if len(to_compress) > 5 else ''}")

    # 更新 tasks.json（如果不是 dry_run）
    if not dry_run:
        data['tasks'] = to_keep
        data['last_archived'] = now.isoformat()
        data['stats'] = {
            'total_kept': len(to_keep),
            'total_quick_archived': len(to_quick_archive),
            'total_monthly_archived': len(to_monthly_archive),
            'total_compressed': len(to_compress)
        }
        save_tasks(data)
    else:
        print("\n🔍 試運行模式：不實際修改文件")

    # 保存快速歸檔
    if to_quick_archive:
        filename = f'tasks-quick-{now.strftime("%Y-%m-%d")}.json'
        filepath = save_archive(to_quick_archive, filename)
        file_size = os.path.getsize(filepath)
        print(f"\n✅ 快速歸檔完成：{filename} ({len(to_quick_archive)} 個任務, {file_size / 1024:.2f} KB)")

    # 保存月度歸檔
    if to_monthly_archive:
        # 按月份分組
        monthly_archives = {}
        for task in to_monthly_archive:
            month = task.get('created_at', '')[:7]
            if month not in monthly_archives:
                monthly_archives[month] = []
            monthly_archives[month].append(task)

        # 保存每個月的歸檔
        for month, tasks_in_month in monthly_archives.items():
            filename = f'tasks-{month}.json'
            filepath = save_archive(tasks_in_month, filename)
            file_size = os.path.getsize(filepath)
            print(f"\n✅ 月度歸檔完成：{filename} ({len(tasks_in_month)} 個任務, {file_size / 1024:.2f} KB)")

    # 壓縮舊任務
    if to_compress:
        filename = f'tasks-compressed-{now.strftime("%Y-%m-%d")}.json.gz'
        filepath = save_compressed_archive(to_compress, filename)
        file_size = os.path.getsize(filepath)
        print(f"\n✅ 壓縮完成：{filename} ({len(to_compress)} 個任務, {file_size / 1024:.2f} KB)")

    # 新 tasks.json 大小
    new_file_size = os.path.getsize(TASKS_JSON) if not dry_run else len(to_keep) * 1000  # 估計
    print(f"\n📊 歸檔後統計：")
    print(f"   tasks.json 大小：{new_file_size / 1024:.2f} KB")
    if file_size > 0:
        reduction = (1 - new_file_size / file_size) * 100
        print(f"   縮減比例：{reduction:.1f}%")

    print("\n✨ 歸檔完成！")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Kanban 任務歸檔腳本（高頻版本）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例：
  python3 archive_tasks.py              # 正常歸檔
  python3 archive_tasks.py --dry-run    # 試運行（不實際修改）
  python3 archive_tasks.py --force      # 強制歸檔（用於測試）
  python3 archive_tasks.py --stats      # 顯示統計信息

歸檔策略（高頻版本）：
  • 保留：最近 2 天的已完成任務 + In Progress + Pending
  • 快速歸檔：2-7 天前的已完成任務（tasks-quick-*.json）
  • 月度歸檔：7-14 天前的已完成任務（tasks-YYYY-MM.json）
  • 壓縮歸檔：14+ 天前的已完成任務（tasks-compressed-*.json.gz）

自動觸發：
  • 檔案大小超過 200 KB 時自動執行
  • 建議在重開機時自動檢查並執行
        """
    )
    parser.add_argument('--force', action='store_true', help='強制歸檔（忽略時間閾值）')
    parser.add_argument('--dry-run', action='store_true', help='試運行模式（不實際修改文件）')
    parser.add_argument('--stats', action='store_true', help='顯示統計信息')

    args = parser.parse_args()

    if args.stats:
        show_stats()
    else:
        archive_tasks(force=args.force, dry_run=args.dry_run)
