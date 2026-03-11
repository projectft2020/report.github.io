#!/usr/bin/env python3
"""
Backpressure Mechanism - 背壓機制

根據系統健康度動態調整任務啟動頻率和並發上限：

健康度計算：
  health = 1 - (stuck_count / max_concurrent)

動態調整規則：
- health >= 0.8: 啟動頻率 65 秒，並發上限 3
- 0.5 <= health < 0.8: 啟動頻率 120 秒，並發上限 3
- health < 0.5: 啟動頻率 300 秒，並發上限 2

P1 行動：根據 Mentor 建議實施

Author: System Optimization v2
Date: 2026-03-05
"""

import json
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Tuple, Optional
import traceback

# 路徑配置
WORKSPACE = Path.home() / ".openclaw" / "workspace"
TASKS_FILE = WORKSPACE / "kanban" / "tasks.json"
BACKPRESSURE_STATS_FILE = WORKSPACE / "kanban-ops" / "backpressure_stats.json"
BACKPRESSURE_LOG = WORKSPACE / "kanban-ops" / "backpressure.log"

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(BACKPRESSURE_LOG, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class BackpressureStats:
    """背壓統計"""
    max_concurrent: int = 3
    current_concurrent: int = 0
    stuck_count: int = 0
    health: float = 1.0  # 0.0-1.0
    spawn_interval: int = 65  # 秒
    reduced_concurrent: bool = False
    last_adjusted: str = ""
    adjustment_count: int = 0
    health_history: list = None

    def __post_init__(self):
        if self.health_history is None:
            self.health_history = []


class BackpressureManager:
    """背壓管理器"""

    # 健康度閾值
    HEALTH_THRESHOLD_HIGH = 0.8
    HEALTH_THRESHOLD_LOW = 0.5

    # 啟動頻率配置（秒）
    SPAWN_INTERVAL_NORMAL = 65
    SPAWN_INTERVAL_MEDIUM = 120
    SPAWN_INTERVAL_SLOW = 300

    # 並發上限配置
    MAX_CONCURRENT_NORMAL = 3
    MAX_CONCURRENT_REDUCED = 2

    def __init__(self):
        self.stats = self._load_stats()

    def _load_stats(self) -> BackpressureStats:
        """載入統計數據"""
        try:
            if BACKPRESSURE_STATS_FILE.exists():
                with open(BACKPRESSURE_STATS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    stats = BackpressureStats(**data)
                    # 確保 health_history 是列表
                    if stats.health_history is None:
                        stats.health_history = []
                    return stats
        except Exception as e:
            logger.warning(f"載入背壓統計失敗: {e}")

        return BackpressureStats()

    def _save_stats(self):
        """保存統計數據"""
        try:
            with open(BACKPRESSURE_STATS_FILE, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.stats), f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存背壓統計失敗: {e}")

    def _calculate_health(self) -> float:
        """
        計算系統健康度

        Returns:
            健康度（0.0-1.0）
        """
        try:
            with open(TASKS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 處理不同的 JSON 格式
            if isinstance(data, dict) and 'tasks' in data:
                tasks = data['tasks']
            elif isinstance(data, list):
                tasks = data
            else:
                logger.error(f"未知的 tasks.json 格式: {type(data)}")
                return 1.0

            # 統計卡住任務（spawning > 45 分鐘）
            now = datetime.now(timezone.utc)
            stuck_count = 0
            current_concurrent = 0

            for task in tasks:
                status = task.get('status')

                # 統計當前並發
                if status == 'in_progress' or status == 'spawning':
                    current_concurrent += 1

                    # 檢查是否卡住（spawning > 45 分鐘）
                    if status == 'spawning':
                        updated_at = task.get('updated_at', task.get('spawned_at'))
                        if updated_at:
                            try:
                                updated_time = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                                elapsed = now - updated_time
                                if elapsed > timedelta(minutes=45):
                                    stuck_count += 1
                            except:
                                pass

            # 計算健康度
            health = 1.0
            if self.stats.max_concurrent > 0:
                health = max(0.0, 1.0 - (stuck_count / self.stats.max_concurrent))

            # 更新統計
            self.stats.current_concurrent = current_concurrent
            self.stats.stuck_count = stuck_count
            self.stats.health = round(health, 2)

            # 記錄健康度歷史（最近 24 小時）
            cutoff = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
            self.stats.health_history = [
                (timestamp, h) for timestamp, h in self.stats.health_history
                if timestamp >= cutoff
            ]
            self.stats.health_history.append((datetime.now(timezone.utc).isoformat(), health))

            return health

        except Exception as e:
            logger.error(f"計算健康度失敗: {e}")
            logger.error(traceback.format_exc())
            return 1.0  # 錯誤時返回健康

    def _adjust_backpressure(self):
        """
        根據健康度調整背壓參數

        調整規則：
        - health >= 0.8: 啟動頻率 65 秒，並發上限 3
        - 0.5 <= health < 0.8: 啟動頻率 120 秒，並發上限 3
        - health < 0.5: 啟動頻率 300 秒，並發上限 2
        """
        health = self.stats.health
        old_interval = self.stats.spawn_interval
        old_concurrent = self.stats.max_concurrent

        # 根據健康度調整
        if health >= self.HEALTH_THRESHOLD_HIGH:
            # 健康狀態：正常啟動
            self.stats.spawn_interval = self.SPAWN_INTERVAL_NORMAL
            self.stats.max_concurrent = self.MAX_CONCURRENT_NORMAL
            self.stats.reduced_concurrent = False

        elif health >= self.HEALTH_THRESHOLD_LOW:
            # 中等健康：降低啟動頻率
            self.stats.spawn_interval = self.SPAWN_INTERVAL_MEDIUM
            self.stats.max_concurrent = self.MAX_CONCURRENT_NORMAL
            self.stats.reduced_concurrent = False

        else:
            # 不健康：嚴格限制
            self.stats.spawn_interval = self.SPAWN_INTERVAL_SLOW
            self.stats.max_concurrent = self.MAX_CONCURRENT_REDUCED
            self.stats.reduced_concurrent = True

        # 檢查是否有變化
        if self.stats.spawn_interval != old_interval or self.stats.max_concurrent != old_concurrent:
            self.stats.adjustment_count += 1
            self.stats.last_adjusted = datetime.now(timezone.utc).isoformat()

            logger.info(f"🔧 背壓調整：")
            logger.info(f"   健康度：{health:.2f}")
            logger.info(f"   啟動頻率：{old_interval}秒 → {self.stats.spawn_interval}秒")
            logger.info(f"   並發上限：{old_concurrent} → {self.stats.max_concurrent}")
            logger.info(f"   卡住任務：{self.stats.stuck_count}")

    def check_and_adjust(self) -> dict:
        """
        檢查並調整背壓

        Returns:
            調整結果字典
        """
        # 計算健康度
        health = self._calculate_health()

        # 調整背壓
        self._adjust_backpressure()

        # 保存統計
        self._save_stats()

        # 返回結果
        return {
            'health': self.stats.health,
            'stuck_count': self.stats.stuck_count,
            'current_concurrent': self.stats.current_concurrent,
            'spawn_interval': self.stats.spawn_interval,
            'max_concurrent': self.stats.max_concurrent,
            'reduced_concurrent': self.stats.reduced_concurrent,
            'last_adjusted': self.stats.last_adjusted,
            'adjustment_count': self.stats.adjustment_count
        }

    def get_spawn_interval(self) -> int:
        """獲取當前建議的啟動頻率"""
        return self.stats.spawn_interval

    def get_max_concurrent(self) -> int:
        """獲取當前建議的並發上限"""
        return self.stats.max_concurrent

    def is_reduced_concurrent(self) -> bool:
        """檢查是否降級並發"""
        return self.stats.reduced_concurrent

    def print_status(self):
        """打印當前狀態"""
        print(f"\n{'='*70}")
        print(f"🔄 背壓機制狀態")
        print(f"{'='*70}")
        print(f"健康度: {self.stats.health:.2f} ({'🟢 健康' if self.stats.health >= 0.8 else '🟡 中等' if self.stats.health >= 0.5 else '🔴 不健康'})")
        print(f"當前並發: {self.stats.current_concurrent} 個")
        print(f"卡住任務: {self.stats.stuck_count} 個")
        print(f"並發上限: {self.stats.max_concurrent} 個" + (" (降級)" if self.stats.reduced_concurrent else ""))
        print(f"啟動頻率: {self.stats.spawn_interval} 秒")
        print(f"調整次數: {self.stats.adjustment_count}")
        print(f"最後調整: {self.stats.last_adjusted if self.stats.last_adjusted else '未調整'}")
        print(f"{'='*70}\n")

    def generate_report(self, hours: int = 24) -> str:
        """生成背壓報告"""
        # 計算健康度趨勢
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
        recent_history = [
            (timestamp, health)
            for timestamp, health in self.stats.health_history
            if timestamp >= cutoff
        ]

        report = f"\n{'='*70}\n"
        report += f"📊 背壓機制報告（最近 {hours} 小時）\n"
        report += f"{'='*70}\n\n"

        report += f"當前狀態:\n"
        report += f"  健康度: {self.stats.health:.2f}\n"
        report += f"  卡住任務: {self.stats.stuck_count}\n"
        report += f"  並發上限: {self.stats.max_concurrent}\n"
        report += f"  啟動頻率: {self.stats.spawn_interval} 秒\n"
        report += f"  調整次數: {self.stats.adjustment_count}\n\n"

        if recent_history:
            avg_health = sum(h for _, h in recent_history) / len(recent_history)
            min_health = min(h for _, h in recent_history)
            max_health = max(h for _, h in recent_history)

            report += f"健康度趨勢（最近 {len(recent_history)} 個檢查點）：\n"
            report += f"  平均: {avg_health:.2f}\n"
            report += f"  最低: {min_health:.2f}\n"
            report += f"  最高: {max_health:.2f}\n\n"

        # 分析建議
        report += f"{'='*70}\n"
        report += f"🎯 優化建議:\n"
        report += f"{'='*70}\n"

        if self.stats.health >= 0.8:
            report += f"✅ 系統健康，無需調整\n"
        elif self.stats.health >= 0.5:
            report += f"⚠️ 系統中等健康，建議:\n"
            report += f"  - 持續監控卡住任務趨勢\n"
            report += f"  - 優化任務啟動邏輯\n"
        else:
            report += f"🔴 系統不健康，建議:\n"
            report += f"  - 檢查 API 限流情況：python3 kanban-ops/api_tracker.py report\n"
            report += f"  - 檢查網絡連接穩定性\n"
            report += f"  - 考慮降低任務複雜度\n"

        report += f"{'='*70}\n"

        return report


# 全局實例
_backpressure_manager = None


def get_manager() -> BackpressureManager:
    """獲取全局背壓管理器實例"""
    global _backpressure_manager
    if _backpressure_manager is None:
        _backpressure_manager = BackpressureManager()
    return _backpressure_manager


def check_backpressure() -> dict:
    """檢查背壓並返回調整結果（便捷函數）"""
    manager = get_manager()
    return manager.check_and_adjust()


def get_spawn_interval() -> int:
    """獲取當前啟動頻率（便捷函數）"""
    manager = get_manager()
    return manager.get_spawn_interval()


def get_max_concurrent() -> int:
    """獲取當前並發上限（便捷函數）"""
    manager = get_manager()
    return manager.get_max_concurrent()


def main():
    """主函數"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 backpressure.py <command>")
        print("Commands:")
        print("  check       - 檢查並調整背壓")
        print("  status      - 顯示當前狀態")
        print("  report      - 生成報告")
        print("  interval    - 獲取啟動頻率")
        print("  concurrent  - 獲取並發上限")
        return

    command = sys.argv[1]
    manager = get_manager()

    if command == 'check':
        result = manager.check_and_adjust()
        print(f"\n背壓檢查結果：")
        print(f"  健康度: {result['health']:.2f}")
        print(f"  卡住任務: {result['stuck_count']}")
        print(f"  當前並發: {result['current_concurrent']}")
        print(f"  並發上限: {result['max_concurrent']}")
        print(f"  啟動頻率: {result['spawn_interval']} 秒")

    elif command == 'status':
        manager.print_status()

    elif command == 'report':
        hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
        print(manager.generate_report(hours))

    elif command == 'interval':
        print(manager.get_spawn_interval())

    elif command == 'concurrent':
        print(manager.get_max_concurrent())

    else:
        print(f"Unknown command: {command}")


if __name__ == '__main__':
    main()
