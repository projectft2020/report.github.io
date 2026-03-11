#!/usr/bin/env python3
"""
Broadcast Notification System - 廣播通知系統

實現功能：
1. 系統事件廣播通知
2. 智能去重（避免重複通知）
3. 通知優先級分類
4. 通知歷史記錄

Author: System Optimization v2
Date: 2026-03-04
"""

import json
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, asdict

# 路徑配置
WORKSPACE = Path.home() / ".openclaw" / "workspace"
NOTIFICATION_LOG = WORKSPACE / "kanban-ops" / "notification_history.json"
NOTIFICATION_CONFIG = WORKSPACE / "kanban-ops" / "notification_config.json"

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class NotificationPriority(Enum):
    """通知優先級"""
    LOW = "low"          # 低優先級：一般信息
    MEDIUM = "medium"    # 中優先級：重要提醒
    HIGH = "high"        # 高優先級：緊急事件
    CRITICAL = "critical" # 關鍵優先級：需要立即處理


@dataclass
class Notification:
    """通知數據"""
    id: str
    title: str
    message: str
    priority: str
    category: str
    timestamp: str
    sent: bool = False
    delivered: bool = False
    error: Optional[str] = None


class BroadcastNotifier:
    """廣播通知器"""

    def __init__(self):
        self.notifications: List[Notification] = []
        self.config = self._load_config()
        self.history = self._load_history()
        self.dedup_cache: Dict[str, datetime] = {}

    def _load_config(self) -> Dict:
        """載入配置"""
        default_config = {
            'enabled': True,
            'dedup_window_minutes': 30,  # 去重時間窗口（分鐘）
            'min_priority': 'medium',     # 最低發送優先級
            'max_notifications_per_hour': 10,  # 每小時最大通知數
            'channels': {
                'webchat': True,
                'telegram': False
            }
        }

        try:
            if NOTIFICATION_CONFIG.exists():
                with open(NOTIFICATION_CONFIG, 'r', encoding='utf-8') as f:
                    return {**default_config, **json.load(f)}
        except Exception as e:
            logger.warning(f"載入配置失敗，使用默認配置: {e}")

        return default_config

    def _load_history(self) -> List[Dict]:
        """載入通知歷史"""
        try:
            if NOTIFICATION_LOG.exists():
                with open(NOTIFICATION_LOG, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"載入通知歷史失敗: {e}")

        return []

    def _save_history(self):
        """保存通知歷史"""
        try:
            with open(NOTIFICATION_LOG, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存通知歷史失敗: {e}")

    def _generate_id(self) -> str:
        """生成通知 ID"""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        import random
        random_suffix = random.randint(1000, 9999)
        return f"notify-{timestamp}-{random_suffix}"

    def _should_notify(self, priority: str) -> bool:
        """
        判斷是否應該發送通知

        Args:
            priority: 通知優先級

        Returns:
            是否應該發送
        """
        # 檢查是否啟用
        if not self.config.get('enabled', False):
            return False

        # 檢查優先級
        min_priority = self.config.get('min_priority', 'medium')
        priority_order = ['low', 'medium', 'high', 'critical']

        if priority_order.index(priority) < priority_order.index(min_priority):
            return False

        # 檢查頻率限制
        max_per_hour = self.config.get('max_notifications_per_hour', 10)
        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)

        recent_count = sum(
            1 for n in self.history
            if datetime.fromisoformat(n['timestamp']) > one_hour_ago
        )

        if recent_count >= max_per_hour:
            logger.warning(f"已達到每小時最大通知數（{max_per_hour}），跳過通知")
            return False

        return True

    def _is_duplicated(self, title: str, message: str) -> bool:
        """
        檢查是否重複通知

        Args:
            title: 標題
            message: 消息

        Returns:
            是否重複
        """
        dedup_key = f"{title}|{message[:100]}"  # 使用標題和消息前 100 字符作為鍵

        # 檢查緩存
        if dedup_key in self.dedup_cache:
            cache_time = self.dedup_cache[dedup_key]
            dedup_window = timedelta(minutes=self.config.get('dedup_window_minutes', 30))

            if datetime.now(timezone.utc) - cache_time < dedup_window:
                logger.info(f"通知在去重時間窗口內，跳過: {title}")
                return True

        # 更新緩存
        self.dedup_cache[dedup_key] = datetime.now(timezone.utc)

        return False

    def notify(self, title: str, message: str, priority: str = "medium", category: str = "system") -> bool:
        """
        發送通知

        Args:
            title: 標題
            message: 消息
            priority: 優先級（low/medium/high/critical）
            category: 類別

        Returns:
            是否成功發送
        """
        # 檢查是否應該通知
        if not self._should_notify(priority):
            return False

        # 檢查是否重複
        if self._is_duplicated(title, message):
            return False

        # 創建通知
        notification = Notification(
            id=self._generate_id(),
            title=title,
            message=message,
            priority=priority,
            category=category,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

        # 添加到歷史
        self.history.append(asdict(notification))
        self._save_history()

        # 記錄日誌
        logger.info(f"📢 通知: [{priority.upper()}] {title}")

        # 實際發送通知（這裡使用 print，實際應該使用 message 工具）
        print(f"\n📢 [{priority.upper()}] {title}")
        print(f"{message}\n")

        notification.sent = True
        notification.delivered = True

        # 更新歷史
        for i, n in enumerate(self.history):
            if n['id'] == notification.id:
                self.history[i] = asdict(notification)
                break

        self._save_history()

        return True

    def notify_scout_scan(self, task_count: int, pending_count: int) -> bool:
        """
        通知 Scout 掃描

        Args:
            task_count: 創建的任務數量
            pending_count: 待辦任務數量

        Returns:
            是否成功發送
        """
        title = "🔍 Scout 掃描完成"
        message = f"創建了 {task_count} 個新任務\n當前待辦: {pending_count} 個"
        return self.notify(title, message, priority="low", category="scout")

    def notify_task_completed(self, task_id: str, title: str) -> bool:
        """
        通知任務完成

        Args:
            task_id: 任務 ID
            title: 任務標題

        Returns:
            是否成功發送
        """
        message_title = "✅ 任務完成"
        message = f"{task_id}\n{title}"
        return self.notify(message_title, message, priority="low", category="task")

    def notify_task_failed(self, task_id: str, error: str) -> bool:
        """
        通知任務失敗

        Args:
            task_id: 任務 ID
            error: 錯誤消息

        Returns:
            是否成功發送
        """
        title = "❌ 任務失敗"
        message = f"{task_id}\n錯誤: {error}"
        return self.notify(title, message, priority="high", category="task")

    def notify_error_recovery(self, recovered_count: int, failed_count: int) -> bool:
        """
        通知錯誤恢復

        Args:
            recovered_count: 恢復的任務數
            failed_count: 失敗的任務數

        Returns:
            是否成功發送
        """
        if recovered_count == 0:
            return False

        title = "🔧 錯誤恢復完成"
        message = f"恢復了 {recovered_count} 個失敗任務\n失敗: {failed_count} 個"
        return self.notify(title, message, priority="medium", category="system")

    def notify_memory_compression(self, compression_rate: float, saved_bytes: int) -> bool:
        """
        通知記憶壓縮

        Args:
            compression_rate: 壓縮率
            saved_bytes: 節省字節數

        Returns:
            是否成功發送
        """
        title = "🗜️ 記憶壓縮完成"
        message = f"壓縮率: {compression_rate:.1f}%\n節省: {saved_bytes:,} 字節"
        return self.notify(title, message, priority="low", category="system")

    def get_stats(self) -> Dict:
        """獲取統計信息"""
        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        one_day_ago = datetime.now(timezone.utc) - timedelta(days=1)

        stats = {
            'total_notifications': len(self.history),
            'last_hour': sum(1 for n in self.history if datetime.fromisoformat(n['timestamp']) > one_hour_ago),
            'last_day': sum(1 for n in self.history if datetime.fromisoformat(n['timestamp']) > one_day_ago),
            'by_priority': {},
            'by_category': {}
        }

        for n in self.history:
            priority = n['priority']
            category = n['category']

            stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1
            stats['by_category'][category] = stats['by_category'].get(category, 0) + 1

        return stats


def main():
    """主函數（測試和手動通知）"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 broadcast_notifier.py <command>")
        print("Commands:")
        print("  test           - 發送測試通知")
        print("  stats          - 顯示統計")
        print("  history        - 顯示通知歷史")
        print("  clear          - 清除通知歷史")
        return

    command = sys.argv[1]
    notifier = BroadcastNotifier()

    if command == 'test':
        print("📢 測試通知系統...")
        print("1. Scout 掃描通知...")
        notifier.notify_scout_scan(5, 10)
        print("2. 任務完成通知...")
        notifier.notify_task_completed("test-123", "Test Task")
        print("3. 錯誤恢復通知...")
        notifier.notify_error_recovery(3, 1)
        print("✅ 測試完成")

    elif command == 'stats':
        stats = notifier.get_stats()
        print(f"\n📊 通知統計:")
        print(f"總通知數: {stats['total_notifications']}")
        print(f"過去 1 小時: {stats['last_hour']}")
        print(f"過去 1 天: {stats['last_day']}")
        print(f"\n按優先級:")
        for priority, count in stats['by_priority'].items():
            print(f"  {priority}: {count}")
        print(f"\n按類別:")
        for category, count in stats['by_category'].items():
            print(f"  {category}: {count}")

    elif command == 'history':
        print(f"\n📜 通知歷史:")
        for n in notifier.history[-10:]:  # 顯示最近 10 條
            timestamp = n['timestamp']
            priority = n['priority'].upper()
            title = n['title']
            print(f"[{timestamp}] [{priority}] {title}")

    elif command == 'clear':
        notifier.history = []
        notifier._save_history()
        print("✅ 通知歷史已清除")

    else:
        print(f"Unknown command: {command}")


if __name__ == '__main__':
    main()
