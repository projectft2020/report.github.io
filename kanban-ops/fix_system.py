#!/usr/bin/env python3
"""
系統修復腳本

修復任務系統的完整性問題：
1. 檢查 tasks.json 路徑一致性
2. 檢查未註冊的任務
3. 檢查孤立的任務文件
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

# 路徑配置
WORKSPACE = Path.home() / ".openclaw" / "workspace"
TASKS_JSON = WORKSPACE / "kanban" / "tasks.json"
ALT_TASKS_JSON = Path.home() / ".openclaw" / "workspace-automation" / "kanban" / "tasks.json"
QUEUE_DIR = WORKSPACE / "kanban-ops" / "task_queue"
CONSUMED_DIR = QUEUE_DIR / "consumed"


def log(level, message):
    """記錄日誌"""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    icon = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}
    print(f"{icon.get(level, '📝')} [{timestamp}] {message}")


def check_tasks_json_path():
    """檢查 tasks.json 路徑一致性"""
    log("INFO", "檢查 tasks.json 路徑一致性...")

    main_exists = TASKS_JSON.exists()
    alt_exists = ALT_TASKS_JSON.exists()

    if main_exists and alt_exists:
        # 兩個文件都存在
        with open(TASKS_JSON, 'r', encoding='utf-8') as f:
            main_tasks = json.load(f)
        with open(ALT_TASKS_JSON, 'r', encoding='utf-8') as f:
            alt_tasks = json.load(f)

        main_count = len(main_tasks) if isinstance(main_tasks, list) else len(main_tasks.get('tasks', []))
        alt_count = len(alt_tasks) if isinstance(alt_tasks, list) else len(alt_tasks.get('tasks', []))

        log("WARNING", f"發現兩個 tasks.json 文件：")
        log("WARNING", f"  - {TASKS_JSON}: {main_count} 個任務")
        log("WARNING", f"  - {ALT_TASKS_JSON}: {alt_count} 個任務")
        log("WARNING", f"  建議：合併任務並統一路徑")

        return False

    elif main_exists:
        log("SUCCESS", f"tasks.json 路徑正確：{TASKS_JSON}")
        return True

    elif alt_exists:
        log("ERROR", f"tasks.json 路徑錯誤：{ALT_TASKS_JSON}")
        log("ERROR", f"應該使用：{TASKS_JSON}")
        return False

    else:
        log("ERROR", "未找到 tasks.json 文件")
        return False


def check_orphaned_task_files():
    """檢查孤立的任務文件"""
    log("INFO", "檢查孤立的任務文件...")

    # 載入 tasks.json
    if not TASKS_JSON.exists():
        log("WARNING", "tasks.json 不存在，跳過檢查")
        return []

    with open(TASKS_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    tasks = data if isinstance(data, list) else data.get('tasks', [])
    task_ids = {t['id'] for t in tasks}

    # 檢查 task_queue/ 目錄
    orphaned = []

    if QUEUE_DIR.exists():
        for task_file in QUEUE_DIR.glob("*.json"):
            task_id = task_file.stem

            if task_id not in task_ids:
                orphaned.append({
                    'file': str(task_file),
                    'task_id': task_id,
                    'type': 'queue'
                })
                log("WARNING", f"發現孤立的任務文件（隊列）：{task_file}")

    # 檢查 consumed/ 目錄
    if CONSUMED_DIR.exists():
        for task_file in CONSUMED_DIR.glob("*.json"):
            task_id = task_file.stem

            if task_id not in task_ids:
                orphaned.append({
                    'file': str(task_file),
                    'task_id': task_id,
                    'type': 'consumed'
                })
                log("WARNING", f"發現孤立的任務文件（已消費）：{task_file}")

    if not orphaned:
        log("SUCCESS", "沒有發現孤立的任務文件")

    return orphaned


def check_duplicate_task_ids():
    """檢查重複的任務 ID"""
    log("INFO", "檢查重複的任務 ID...")

    if not TASKS_JSON.exists():
        log("WARNING", "tasks.json 不存在，跳過檢查")
        return []

    with open(TASKS_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    tasks = data if isinstance(data, list) else data.get('tasks', [])
    task_ids = [t['id'] for t in tasks]

    # 檢查重複
    seen = set()
    duplicates = []

    for task_id in task_ids:
        if task_id in seen:
            duplicates.append(task_id)
        else:
            seen.add(task_id)

    if duplicates:
        log("ERROR", f"發現 {len(duplicates)} 個重複的任務 ID：")
        for task_id in duplicates:
            log("ERROR", f"  - {task_id}")
    else:
        log("SUCCESS", "沒有發現重複的任務 ID")

    return duplicates


def check_inconsistent_status():
    """檢查狀態不一致的任務"""
    log("INFO", "檢查狀態不一致的任務...")

    if not TASKS_JSON.exists():
        log("WARNING", "tasks.json 不存在，跳過檢查")
        return []

    with open(TASKS_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    tasks = data if isinstance(data, list) else data.get('tasks', [])
    issues = []

    for task in tasks:
        status = task.get('status')

        # 檢查 completed_at 時間是否合理
        if status == 'completed' and not task.get('completed_at'):
            issues.append({
                'task_id': task['id'],
                'issue': 'completed 任務缺少 completed_at 時間'
            })
            log("WARNING", f"{task['id']}: completed 任務缺少 completed_at 時間")

        # 檢查是否有不合理的狀態組合
        if status == 'in_progress' and task.get('completed_at'):
            issues.append({
                'task_id': task['id'],
                'issue': 'in_progress 任務有 completed_at 時間'
            })
            log("WARNING", f"{task['id']}: in_progress 任務有 completed_at 時間")

        if status == 'pending' and task.get('completed_at'):
            issues.append({
                'task_id': task['id'],
                'issue': 'pending 任務有 completed_at 時間'
            })
            log("WARNING", f"{task['id']}: pending 任務有 completed_at 時間")

    if not issues:
        log("SUCCESS", "沒有發現狀態不一致的問題")

    return issues


def generate_report():
    """生成修復報告"""
    log("INFO", "生成修復報告...")

    report_file = WORKSPACE / "kanban-ops" / f"fix-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"# 系統修復報告\n\n")
        f.write(f"生成時間：{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")

        # 1. tasks.json 路徑
        f.write("## 1. tasks.json 路徑檢查\n\n")
        if TASKS_JSON.exists():
            with open(TASKS_JSON, 'r', encoding='utf-8') as f2:
                data = json.load(f2)
            count = len(data) if isinstance(data, list) else len(data.get('tasks', []))
            f.write(f"- ✅ 主路徑：{TASKS_JSON} ({count} 個任務)\n")
        else:
            f.write(f"- ❌ 主路徑不存在：{TASKS_JSON}\n")

        if ALT_TASKS_JSON.exists():
            with open(ALT_TASKS_JSON, 'r', encoding='utf-8') as f2:
                data = json.load(f2)
            count = len(data) if isinstance(data, list) else len(data.get('tasks', []))
            f.write(f"- ⚠️ 備用路徑：{ALT_TASKS_JSON} ({count} 個任務)\n")
        else:
            f.write(f"- ✅ 備用路徑不存在\n")

    log("SUCCESS", f"報告已生成：{report_file}")
    return report_file


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='系統修復腳本',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--fix', action='store_true',
                        help='自動修復發現的問題')
    parser.add_argument('--report', action='store_true',
                        help='生成修復報告')

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("🔧 系統修復腳本")
    print("=" * 60 + "\n")

    # 檢查 1：tasks.json 路徑
    path_ok = check_tasks_json_path()
    print()

    # 檢查 2：孤立任務文件
    orphaned = check_orphaned_task_files()
    print()

    # 檢查 3：重複任務 ID
    duplicates = check_duplicate_task_ids()
    print()

    # 檢查 4：狀態不一致
    inconsistent = check_inconsistent_status()
    print()

    # 生成報告
    if args.report:
        generate_report()

    # 總結
    print("\n" + "=" * 60)
    print("📊 修復檢查總結")
    print("=" * 60)
    print(f"\n✅ 路徑檢查：{'通過' if path_ok else '失敗'}")
    print(f"✅ 孤立文件：{len(orphaned)} 個")
    print(f"✅ 重複 ID：{len(duplicates)} 個")
    print(f"✅ 狀態不一致：{len(inconsistent)} 個")

    total_issues = len(orphaned) + len(duplicates) + len(inconsistent)

    if total_issues == 0 and path_ok:
        print(f"\n✅ 系統健康，無需修復")
        sys.exit(0)
    else:
        print(f"\n⚠️ 發現 {total_issues} 個問題需要處理")

        if args.fix:
            print(f"\n🔧 自動修復模式已啟用")
            print(f"   （待實現）")
        else:
            print(f"\n💡 使用 --fix 自動修復問題")
            print(f"💡 使用 --report 生成詳細報告")

        sys.exit(1)


if __name__ == '__main__':
    main()
