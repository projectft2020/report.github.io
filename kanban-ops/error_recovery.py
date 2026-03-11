#!/usr/bin/env python3
"""
Error Recovery Module - 錯誤處理和恢復機制

實現功能：
1. API Rate Limit 檢測
2. 指數退避重試邏輯
3. 失敗任務自動恢復
4. 錯誤統計和報告

Author: System Optimization v2
Date: 2026-03-04
"""

import json
import logging
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import traceback

# 路徑配置
WORKSPACE = Path.home() / ".openclaw" / "workspace"
TASKS_FILE = WORKSPACE / "kanban" / "tasks.json"
ERROR_LOG = WORKSPACE / "kanban-ops" / "error_recovery.log"
RECOVERY_STATS_FILE = WORKSPACE / "kanban-ops" / "error_recovery_stats.json"

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(ERROR_LOG, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """錯誤類型"""
    RATE_LIMIT = "rate_limit"
    TIMEOUT = "timeout"
    NETWORK = "network"
    PARSING = "parsing"
    UNKNOWN = "unknown"


@dataclass
class ErrorRecord:
    """錯誤記錄"""
    task_id: str
    error_type: str
    error_message: str
    timestamp: str
    retry_count: int = 0
    max_retries: int = 3
    backoff_seconds: int = 0
    recovered: bool = False


@dataclass
class RecoveryStats:
    """恢復統計"""
    total_errors: int = 0
    recovered_errors: int = 0
    failed_recoveries: int = 0
    rate_limit_errors: int = 0
    timeout_errors: int = 0
    last_update: str = ""


class ErrorRecoveryManager:
    """錯誤恢復管理器"""

    def __init__(self):
        self.stats = self._load_stats()
        self.error_records: List[ErrorRecord] = []

    def _load_stats(self) -> RecoveryStats:
        """載入統計數據"""
        try:
            if RECOVERY_STATS_FILE.exists():
                with open(RECOVERY_STATS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return RecoveryStats(**data)
        except Exception as e:
            logger.warning(f"載入統計數據失敗: {e}")

        return RecoveryStats()

    def _save_stats(self):
        """保存統計數據"""
        try:
            with open(RECOVERY_STATS_FILE, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.stats), f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存統計數據失敗: {e}")

    def _update_stats(self, error_type: ErrorType, recovered: bool):
        """更新統計"""
        self.stats.total_errors += 1
        self.stats.last_update = datetime.now(timezone.utc).isoformat()

        if error_type == ErrorType.RATE_LIMIT:
            self.stats.rate_limit_errors += 1
        elif error_type == ErrorType.TIMEOUT:
            self.stats.timeout_errors += 1

        if recovered:
            self.stats.recovered_errors += 1
        else:
            self.stats.failed_recoveries += 1

        self._save_stats()

    def detect_error_type(self, error_message: str) -> ErrorType:
        """
        檢測錯誤類型

        Args:
            error_message: 錯誤消息

        Returns:
            錯誤類型
        """
        error_msg_lower = error_message.lower()

        # Rate limit 檢測
        if any(keyword in error_msg_lower for keyword in [
            'rate limit', '429', 'too many requests',
            'quota exceeded', 'rate_limit', 'api limit'
        ]):
            return ErrorType.RATE_LIMIT

        # Timeout 檢測
        if any(keyword in error_msg_lower for keyword in [
            'timeout', 'timed out', 'deadline exceeded'
        ]):
            return ErrorType.TIMEOUT

        # Network 檢測
        if any(keyword in error_msg_lower for keyword in [
            'connection', 'network', 'dns', 'unreachable'
        ]):
            return ErrorType.NETWORK

        # Parsing 檢測
        if any(keyword in error_msg_lower for keyword in [
            'parse', 'decode', 'json', 'yaml'
        ]):
            return ErrorType.PARSING

        return ErrorType.UNKNOWN

    def calculate_backoff(self, retry_count: int, base_seconds: int = 60, max_seconds: int = 3600) -> int:
        """
        計算指數退避時間

        Args:
            retry_count: 重試次數
            base_seconds: 基礎秒數（默認 60 秒）
            max_seconds: 最大秒數（默認 3600 秒 = 1 小時）

        Returns:
            退避時間（秒）
        """
        backoff = min(base_seconds * (2 ** retry_count), max_seconds)
        return backoff

    def should_retry(self, error_record: ErrorRecord) -> bool:
        """
        判斷是否應該重試

        Args:
            error_record: 錯誤記錄

        Returns:
            是否應該重試
        """
        # 檢查重試次數
        if error_record.retry_count >= error_record.max_retries:
            logger.warning(f"任務 {error_record.task_id} 已達到最大重試次數 ({error_record.max_retries})")
            return False

        # 檢查退避時間
        if error_record.backoff_seconds > 0:
            # 檢查是否已經過退避時間
            error_time = datetime.fromisoformat(error_record.timestamp.replace('Z', '+00:00'))
            wait_until = error_time + timedelta(seconds=error_record.backoff_seconds)
            if datetime.now(timezone.utc) < wait_until:
                logger.info(f"任務 {error_record.task_id} 正在退避中，還需 {wait_until - datetime.now(timezone.utc)}")
                return False

        return True

    def recover_task(self, task_id: str, error_message: str) -> Tuple[bool, Optional[str]]:
        """
        恢復失敗的任務

        Args:
            task_id: 任務 ID
            error_message: 錯誤消息

        Returns:
            (是否成功恢復, 錯誤消息)
        """
        try:
            # 檢測錯誤類型
            error_type = self.detect_error_type(error_message)
            logger.info(f"檢測到錯誤類型: {error_type.value}")

            # 載入任務
            with open(TASKS_FILE, 'r', encoding='utf-8') as f:
                tasks = json.load(f)

            task = next((t for t in tasks if t.get('id') == task_id), None)
            if not task:
                return False, f"任務 {task_id} 不存在"

            # 檢查任務狀態
            if task.get('status') != 'failed':
                return False, f"任務 {task_id} 狀態不是 failed"

            # 創建錯誤記錄
            error_record = ErrorRecord(
                task_id=task_id,
                error_type=error_type.value,
                error_message=error_message[:500],  # 限制長度
                timestamp=datetime.now(timezone.utc).isoformat(),
                retry_count=task.get('retry_count', 0),
                max_retries=task.get('max_retries', 3)
            )

            # 計算退避時間
            error_record.backoff_seconds = self.calculate_backoff(error_record.retry_count)

            # 判斷是否應該重試
            if not self.should_retry(error_record):
                self._update_stats(error_type, False)
                return False, "不應該重試（達到最大重試次數或正在退避中）"

            # 執行恢復
            task['status'] = 'pending'
            task['retry_count'] = error_record.retry_count + 1
            task['error_recovery'] = {
                'last_error': error_message[:500],
                'error_type': error_type.value,
                'recovered_at': datetime.now(timezone.utc).isoformat(),
                'backoff_seconds': error_record.backoff_seconds
            }
            task['updated_at'] = datetime.now(timezone.utc).isoformat()

            # 保存任務
            with open(TASKS_FILE, 'w', encoding='utf-8') as f:
                json.dump(tasks, f, indent=2, ensure_ascii=False)

            # 更新統計
            self._update_stats(error_type, True)

            logger.info(f"✅ 任務 {task_id} 已恢復為 pending，重試次數: {error_record.retry_count + 1}")
            logger.info(f"⏱️ 退避時間: {error_record.backoff_seconds} 秒")

            return True, None

        except Exception as e:
            logger.error(f"恢復任務 {task_id} 時出錯: {e}")
            logger.error(traceback.format_exc())
            return False, str(e)

    def check_and_recover_all_failed_tasks(self) -> Dict[str, int]:
        """
        檢查並恢復所有失敗任務

        Returns:
            恢復統計字典
        """
        stats = {
            'total_failed': 0,
            'recovered': 0,
            'skipped': 0,
            'failed': 0
        }

        try:
            # 載入任務
            with open(TASKS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 處理不同的 JSON 格式
            if isinstance(data, dict) and 'tasks' in data:
                tasks = data['tasks']
            elif isinstance(data, list):
                tasks = data
            else:
                logger.error(f"未知的 tasks.json 格式: {type(data)}")
                return stats

            # 找出失敗任務
            failed_tasks = [t for t in tasks if t.get('status') == 'failed']
            stats['total_failed'] = len(failed_tasks)

            if not failed_tasks:
                logger.info("沒有失敗的任務需要恢復")
                return stats

            logger.info(f"找到 {len(failed_tasks)} 個失敗任務")

            # 逐個恢復
            for task in failed_tasks:
                task_id = task.get('id')
                error_message = task.get('error', 'Unknown error')

                success, error = self.recover_task(task_id, error_message)

                if success:
                    stats['recovered'] += 1
                else:
                    if '不應該重試' in (error or ''):
                        stats['skipped'] += 1
                    else:
                        stats['failed'] += 1
                        logger.error(f"恢復失敗: {task_id} - {error}")

        except Exception as e:
            logger.error(f"檢查失敗任務時出錯: {e}")
            logger.error(traceback.format_exc())

        return stats

    def get_stats(self) -> Dict:
        """獲取統計信息"""
        return asdict(self.stats)

    def print_stats(self):
        """打印統計信息"""
        print(f"\n{'='*60}")
        print(f"📊 錯誤恢復統計")
        print(f"{'='*60}")
        print(f"總錯誤數: {self.stats.total_errors}")
        print(f"已恢復: {self.stats.recovered_errors}")
        print(f"恢復失敗: {self.stats.failed_recoveries}")
        print(f"Rate Limit 錯誤: {self.stats.rate_limit_errors}")
        print(f"Timeout 錯誤: {self.stats.timeout_errors}")
        print(f"成功率: {(self.stats.recovered_errors / self.stats.total_errors * 100) if self.stats.total_errors > 0 else 0:.1f}%")
        print(f"最後更新: {self.stats.last_update}")
        print(f"{'='*60}\n")


def main():
    """主函數（測試和手動恢復）"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 error_recovery.py <command>")
        print("Commands:")
        print("  recover-all - 檢查並恢復所有失敗任務")
        print("  stats      - 顯示統計信息")
        print("  test       - 測試錯誤檢測")
        return

    command = sys.argv[1]
    manager = ErrorRecoveryManager()

    if command == 'recover-all':
        print("🔧 檢查並恢復所有失敗任務...")
        stats = manager.check_and_recover_all_failed_tasks()
        print(f"\n恢復完成：")
        print(f"  總失敗: {stats['total_failed']}")
        print(f"  已恢復: {stats['recovered']}")
        print(f"  跳過: {stats['skipped']}")
        print(f"  失敗: {stats['failed']}")

    elif command == 'stats':
        manager.print_stats()

    elif command == 'test':
        print("🧪 測試錯誤檢測...")

        test_cases = [
            ("Rate limit exceeded", ErrorType.RATE_LIMIT),
            ("429 Too Many Requests", ErrorType.RATE_LIMIT),
            ("Request timed out", ErrorType.TIMEOUT),
            ("Network unreachable", ErrorType.NETWORK),
            ("JSON parse error", ErrorType.PARSING),
            ("Unknown error", ErrorType.UNKNOWN)
        ]

        for msg, expected in test_cases:
            detected = manager.detect_error_type(msg)
            status = "✅" if detected == expected else "❌"
            print(f"{status} '{msg}' -> {detected.value} (expected: {expected.value})")

    else:
        print(f"Unknown command: {command}")


if __name__ == '__main__':
    main()
