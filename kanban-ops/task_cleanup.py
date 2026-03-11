#!/usr/bin/env python3
"""
Task Cleanup - 失敗任務清理模塊

P1 行動：清理過期和過多的失敗任務

規則：
- 最多保留 50 個失敗任務
- 清理超過 7 天的失敗任務
- 保留最近修改的失敗任務

使用方式：
    python3 kanban-ops/task_cleanup.py check      # 檢查需要清理的任務
    python3 kanban-ops/task_cleanup.py cleanup    # 執行清理
    python3 kanban-ops/task_cleanup.py dry-run    # 模擬清理（不實際刪除）

Author: System Optimization v2
Date: 2026-03-05
"""

import json
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Dict, Tuple
import traceback

# 路徑配置
WORKSPACE = Path.home() / ".openclaw" / "workspace"
TASKS_FILE = WORKSPACE / "kanban" / "tasks.json"
BACKUP_DIR = WORKSPACE / "kanban" / "backups" / "failed_tasks"

# 清理配置
MAX_FAILED_TASKS = 50  # 最多保留的失敗任務數量
FAILED_AGE_DAYS = 7  # 清理超過 7 天的失敗任務

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class TaskCleanupManager:
    """失敗任務清理管理器"""

    def __init__(self):
        self.tasks = self._load_tasks()
        self.failed_tasks = self._get_failed_tasks()
        self.to_cleanup = []

    def _load_tasks(self) -> List[Dict]:
        """載入任務"""
        try:
            with open(TASKS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)

                # 處理多種格式
                if isinstance(data, dict):
                    if 'tasks' in data:
                        return data['tasks']
                    else:
                        return list(data.values())
                elif isinstance(data, list):
                    return data
                else:
                    logger.warning(f"未知 tasks.json 格式: {type(data)}")
                    return []

        except FileNotFoundError:
            logger.error(f"tasks.json 不存在: {TASKS_FILE}")
            return []
        except Exception as e:
            logger.error(f"載入任務失敗: {e}")
            logger.error(traceback.format_exc())
            return []

    def _save_tasks(self, tasks: List[Dict]):
        """保存任務"""
        try:
            with open(TASKS_FILE, 'w', encoding='utf-8') as f:
                json.dump(tasks, f, indent=2, ensure_ascii=False)
            logger.info(f"已保存 {len(tasks)} 個任務到 tasks.json")
        except Exception as e:
            logger.error(f"保存任務失敗: {e}")

    def _get_failed_tasks(self) -> List[Dict]:
        """獲取所有失敗任務"""
        failed = [
            task for task in self.tasks
            if task.get('status') == 'failed'
        ]
        logger.info(f"找到 {len(failed)} 個失敗任務")
        return failed

    def _parse_datetime(self, dt_str: str) -> datetime:
        """解析時間字符串，確保返回帶時區的 datetime"""
        try:
            if dt_str.endswith('Z'):
                dt_str = dt_str[:-1] + '+00:00'
            dt = datetime.fromisoformat(dt_str)
            # 如果解析結果沒有時區信息，默認為 UTC
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except:
            return None

    def check_cleanup_needed(self) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """
        檢查需要清理的任務

        Returns:
            (too_many, too_old, all_to_cleanup)
        """
        now = datetime.now(timezone.utc)

        # 1. 檢查是否超過最大數量
        if len(self.failed_tasks) > MAX_FAILED_TASKS:
            too_many_count = len(self.failed_tasks) - MAX_FAILED_TASKS
            # 按更新時間排序（舊的在前）
            sorted_by_age = sorted(
                self.failed_tasks,
                key=lambda t: self._parse_datetime(t.get('updated_at', '')) or datetime.min
            )
            too_many = sorted_by_age[:too_many_count]
            logger.info(f"⚠️ 失敗任務超過限制（{len(self.failed_tasks)} > {MAX_FAILED_TASKS}）")
            logger.info(f"   需要清理 {too_many_count} 個任務")
        else:
            too_many = []
            logger.info(f"✅ 失敗任務數量正常（{len(self.failed_tasks)} / {MAX_FAILED_TASKS}）")

        # 2. 檢查是否超過時間限制
        too_old = []
        for task in self.failed_tasks:
            updated_at = self._parse_datetime(task.get('updated_at', ''))
            if updated_at and (now - updated_at) > timedelta(days=FAILED_AGE_DAYS):
                too_old.append(task)

        if too_old:
            logger.info(f"⚠️ 找到 {len(too_old)} 個超過 {FAILED_AGE_DAYS} 天的失敗任務")
        else:
            logger.info(f"✅ 沒有超過 {FAILED_AGE_DAYS} 天的失敗任務")

        # 3. 合併去重
        all_ids = set()
        all_to_cleanup = []

        for task in too_many + too_old:
            if task['id'] not in all_ids:
                all_ids.add(task['id'])
                all_to_cleanup.append(task)

        self.to_cleanup = all_to_cleanup

        if all_to_cleanup:
            logger.info(f"📋 總共需要清理 {len(all_to_cleanup)} 個失敗任務")
        else:
            logger.info(f"✅ 不需要清理任何失敗任務")

        return too_many, too_old, all_to_cleanup

    def backup_tasks(self, tasks: List[Dict]):
        """備份失敗任務"""
        if not tasks:
            return

        try:
            BACKUP_DIR.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
            backup_file = BACKUP_DIR / f"failed_tasks_{timestamp}.json"

            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(tasks, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ 已備份 {len(tasks)} 個失敗任務到 {backup_file}")
        except Exception as e:
            logger.error(f"備份失敗任務失敗: {e}")

    def cleanup_tasks(self, dry_run: bool = False):
        """
        清理失敗任務

        Args:
            dry_run: 是否模擬模式（不實際刪除）
        """
        if not self.to_cleanup:
            logger.info("沒有需要清理的任務")
            return

        task_ids = [task['id'] for task in self.to_cleanup]
        task_titles = [
            f"  - {task['id'][:30]}: {task.get('title', 'N/A')[:50]}"
            for task in self.to_cleanup
        ]

        if dry_run:
            logger.info(f"\n🔍 模擬清理模式（不實際刪除）")
            logger.info(f"將清理 {len(task_ids)} 個失敗任務：")
            for title in task_titles:
                logger.info(title)
            return

        # 備份
        self.backup_tasks(self.to_cleanup)

        # 從 tasks 中移除
        cleaned_tasks = [
            task for task in self.tasks
            if task['id'] not in task_ids
        ]

        logger.info(f"\n🗑️  清理 {len(task_ids)} 個失敗任務：")
        for title in task_titles:
            logger.info(title)

        # 保存
        self._save_tasks(cleaned_tasks)

        logger.info(f"\n✅ 清理完成：{len(self.tasks) - len(cleaned_tasks)} → {len(cleaned_tasks)} 個任務")

    def print_stats(self):
        """打印統計信息"""
        print(f"\n{'='*70}")
        print(f"🗑️  失敗任務清理統計")
        print(f"{'='*70}")
        print(f"總任務數: {len(self.tasks)}")
        print(f"失敗任務數: {len(self.failed_tasks)}")
        print(f"最大保留數: {MAX_FAILED_TASKS}")
        print(f"清理閾值: {FAILED_AGE_DAYS} 天")
        print(f"{'='*70}\n")


def main():
    """主函數"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 task_cleanup.py <command>")
        print("Commands:")
        print("  check       - 檢查需要清理的任務")
        print("  cleanup     - 執行清理")
        print("  dry-run     - 模擬清理（不實際刪除）")
        print("  stats       - 顯示統計信息")
        return

    command = sys.argv[1]

    if command == 'stats':
        manager = TaskCleanupManager()
        manager.print_stats()

    elif command in ['check', 'cleanup', 'dry-run']:
        manager = TaskCleanupManager()
        manager.print_stats()

        too_many, too_old, all_to_cleanup = manager.check_cleanup_needed()

        if command == 'check':
            # 只檢查，不執行
            pass
        elif command == 'dry-run':
            # 模擬模式
            manager.cleanup_tasks(dry_run=True)
        elif command == 'cleanup':
            # 執行清理
            manager.cleanup_tasks(dry_run=False)

    else:
        print(f"Unknown command: {command}")


if __name__ == '__main__':
    main()
