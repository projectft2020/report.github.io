#!/usr/bin/env python3
"""
任務時間追蹤模組

追蹤任務的預估時間和實際執行時間，生成統計報告。
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class TimeEstimate:
    """時間預估"""
    min_minutes: int
    max_minutes: int

    def __str__(self):
        return f"{self.min_minutes}-{self.max_minutes} 分鐘"


@dataclass
class TimeTracking:
    """時間追蹤記錄"""
    estimated_time: Optional[TimeEstimate] = None
    complexity_level: Optional[int] = None
    recommended_model: Optional[str] = None
    actual_time_minutes: Optional[float] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    time_variance_percent: Optional[float] = None  # (實際 - 預估中點) / 預估中點 * 100

    def to_dict(self):
        """轉換為字典"""
        result = {}
        if self.estimated_time:
            result['estimated_time'] = {
                'min': self.estimated_time.min_minutes,
                'max': self.estimated_time.max_minutes
            }
        if self.complexity_level is not None:
            result['complexity_level'] = self.complexity_level
        if self.recommended_model:
            result['recommended_model'] = self.recommended_model
        if self.actual_time_minutes is not None:
            result['actual_time_minutes'] = round(self.actual_time_minutes, 2)
        if self.started_at:
            result['started_at'] = self.started_at
        if self.completed_at:
            result['completed_at'] = self.completed_at
        if self.time_variance_percent is not None:
            result['time_variance_percent'] = round(self.time_variance_percent, 2)
        return result


class TaskTimeTracker:
    """任務時間追蹤器"""

    def __init__(self, tasks_json_path: str):
        """
        初始化追蹤器

        Args:
            tasks_json_path: tasks.json 文件路徑
        """
        self.tasks_json_path = Path(tasks_json_path)
        self.tasks = self._load_tasks()

    def _load_tasks(self) -> List[Dict]:
        """載入任務"""
        if not self.tasks_json_path.exists():
            return []

        with open(self.tasks_json_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_tasks(self):
        """保存任務"""
        with open(self.tasks_json_path, 'w', encoding='utf-8') as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)

    def add_time_estimation(self, task_id: str, estimation: TimeEstimate,
                           complexity_level: int, recommended_model: str):
        """
        為任務添加時間預估

        Args:
            task_id: 任務 ID
            estimation: 時間預估
            complexity_level: 複雜度等級
            recommended_model: 推薦模型
        """
        task = self._find_task(task_id)
        if not task:
            raise ValueError(f"找不到任務：{task_id}")

        # 創建時間追蹤記錄
        if 'time_tracking' not in task:
            task['time_tracking'] = {}

        task['time_tracking']['estimated_time'] = {
            'min': estimation.min_minutes,
            'max': estimation.max_minutes
        }
        task['time_tracking']['complexity_level'] = complexity_level
        task['time_tracking']['recommended_model'] = recommended_model

        self._save_tasks()
        print(f"✅ 已為任務 {task_id} 添加時間預估：{estimation}")

    def mark_task_started(self, task_id: str):
        """
        標記任務開始

        Args:
            task_id: 任務 ID
        """
        task = self._find_task(task_id)
        if not task:
            raise ValueError(f"找不到任務：{task_id}")

        if 'time_tracking' not in task:
            task['time_tracking'] = {}

        task['time_tracking']['started_at'] = datetime.now().isoformat()
        task['status'] = 'in_progress'

        self._save_tasks()
        print(f"✅ 任務 {task_id} 已標記為開始")

    def mark_task_completed(self, task_id: str):
        """
        標記任務完成並計算實際時間

        Args:
            task_id: 任務 ID
        """
        task = self._find_task(task_id)
        if not task:
            raise ValueError(f"找不到任務：{task_id}")

        if 'time_tracking' not in task:
            task['time_tracking'] = {}

        # 記錄完成時間
        completed_at = datetime.now()
        task['time_tracking']['completed_at'] = completed_at.isoformat()
        task['status'] = 'completed'

        # 計算實際時間
        started_at_str = task['time_tracking'].get('started_at')
        if started_at_str:
            started_at = datetime.fromisoformat(started_at_str)
            actual_duration = completed_at - started_at
            actual_minutes = actual_duration.total_seconds() / 60

            task['time_tracking']['actual_time_minutes'] = round(actual_minutes, 2)

            # 計算偏差百分比
            estimated = task['time_tracking'].get('estimated_time')
            if estimated:
                estimated_mid = (estimated['min'] + estimated['max']) / 2
                variance = ((actual_minutes - estimated_mid) / estimated_mid) * 100
                task['time_tracking']['time_variance_percent'] = round(variance, 2)

            self._save_tasks()
            print(f"✅ 任務 {task_id} 已完成，實際時間：{actual_minutes:.1f} 分鐘")
        else:
            self._save_tasks()
            print(f"⚠️ 任務 {task_id} 已完成，但沒有開始時間")

    def _find_task(self, task_id: str) -> Optional[Dict]:
        """查找任務"""
        for task in self.tasks:
            if task['id'] == task_id or task['id'].endswith(task_id):
                return task
        return None

    def generate_statistics(self) -> Dict:
        """
        生成時間統計報告

        Returns:
            統計報告字典
        """
        stats = {
            'total_tasks': len(self.tasks),
            'tracked_tasks': 0,
            'completed_with_time': 0,
            'within_estimate': 0,
            'over_estimate': 0,
            'under_estimate': 0,
            'average_variance': 0.0,
            'by_complexity': {},
            'recent_tasks': []
        }

        variances = []

        for task in self.tasks:
            time_tracking = task.get('time_tracking', {})
            if not time_tracking:
                continue

            stats['tracked_tasks'] += 1

            # 統計已完成且有時間的任務
            if time_tracking.get('actual_time_minutes'):
                stats['completed_with_time'] += 1

                actual = time_tracking['actual_time_minutes']
                estimated = time_tracking.get('estimated_time')
                variance = time_tracking.get('time_variance_percent')

                if variance is not None:
                    variances.append(variance)

                    if variance > 20:
                        stats['over_estimate'] += 1
                    elif variance < -20:
                        stats['under_estimate'] += 1
                    else:
                        stats['within_estimate'] += 1

                # 按複雜度統計
                complexity = time_tracking.get('complexity_level')
                if complexity:
                    if complexity not in stats['by_complexity']:
                        stats['by_complexity'][complexity] = {
                            'count': 0,
                            'total_actual': 0.0,
                            'over_count': 0,
                            'under_count': 0,
                            'within_count': 0
                        }

                    stats['by_complexity'][complexity]['count'] += 1
                    stats['by_complexity'][complexity]['total_actual'] += actual

                    if variance is not None:
                        if variance > 20:
                            stats['by_complexity'][complexity]['over_count'] += 1
                        elif variance < -20:
                            stats['by_complexity'][complexity]['under_count'] += 1
                        else:
                            stats['by_complexity'][complexity]['within_count'] += 1

        # 計算平均偏差
        if variances:
            stats['average_variance'] = round(sum(variances) / len(variances), 2)

        # 計算各複雜度的平均時間
        for complexity, data in stats['by_complexity'].items():
            if data['count'] > 0:
                data['average_time'] = round(data['total_actual'] / data['count'], 2)

        return stats

    def format_statistics(self, stats: Dict) -> str:
        """格式化統計報告"""
        lines = [
            "=" * 70,
            "📊 任務時間統計報告",
            "=" * 70,
            "",
            f"總任務數：{stats['total_tasks']}",
            f"已追蹤任務：{stats['tracked_tasks']}",
            f"已完成並記錄時間：{stats['completed_with_time']}",
            "",
            "─" * 70,
            "預估準確度",
            "─" * 70,
            "",
            f"在預估範圍內：{stats['within_estimate']} 任務",
            f"超過預估：{stats['over_estimate']} 任務",
            f"低於預估：{stats['under_estimate']} 任務",
            f"平均偏差：{stats['average_variance']:+.1f}%",
        ]

        if stats['by_complexity']:
            lines.extend([
                "",
                "─" * 70,
                "按複雜度統計",
                "─" * 70,
                ""
            ])

            for complexity in sorted(stats['by_complexity'].keys()):
                data = stats['by_complexity'][complexity]
                lines.extend([
                    f"等級 {complexity}：",
                    f"  任務數：{data['count']}",
                    f"  平均時間：{data.get('average_time', 'N/A')} 分鐘",
                    f"  在範圍內：{data['within_count']} | 超預估：{data['over_count']} | 低預估：{data['under_count']}",
                    ""
                ])

        lines.extend([
            "=" * 70,
            "",
            "說明：",
            "• 在預估範圍內：實際時間在 [預估最小, 預估最大] 範圍內",
            "• 超過預估：實際時間 > 預估最大值",
            "• 低於預估：實際時間 < 預估最小值",
            "• 平均偏差：正值表示平均超時，負值表示平均提前完成"
        ])

        return "\n".join(lines)

    def get_outliers(self, threshold_percent: float = 50.0) -> List[Dict]:
        """
        獲取偏差超過閾值的任務

        Args:
            threshold_percent: 偏差百分比閾值

        Returns:
            異常任務列表
        """
        outliers = []

        for task in self.tasks:
            time_tracking = task.get('time_tracking', {})
            if not time_tracking:
                continue

            variance = time_tracking.get('time_variance_percent')
            if variance is None:
                continue

            if abs(variance) > threshold_percent:
                outliers.append({
                    'task_id': task['id'],
                    'title': task['title'],
                    'variance_percent': variance,
                    'estimated': time_tracking.get('estimated_time'),
                    'actual_minutes': time_tracking.get('actual_time_minutes'),
                    'complexity': time_tracking.get('complexity_level'),
                    'model': time_tracking.get('recommended_model')
                })

        # 按偏差絕對值排序
        outliers.sort(key=lambda x: abs(x['variance_percent']), reverse=True)

        return outliers


def main():
    """測試範例"""
    # 創建追蹤器
    tracker = TaskTimeTracker('/Users/charlie/.openclaw/workspace/kanban/tasks.json')

    # 生成統計報告
    stats = tracker.generate_statistics()
    print(tracker.format_statistics(stats))

    # 獲取異常任務
    print("\n")
    outliers = tracker.get_outliers(threshold_percent=30.0)
    if outliers:
        print("=" * 70)
        print("⚠️  偏差較大的任務（> 30%）")
        print("=" * 70)
        for outlier in outliers[:10]:  # 顯示前 10 個
            print(f"\n{outlier['task_id']}: {outlier['title']}")
            print(f"  偏差：{outlier['variance_percent']:+.1f}%")
            print(f"  預估：{outlier['estimated']['min']}-{outlier['estimated']['max']} 分鐘")
            print(f"  實際：{outlier['actual_minutes']:.1f} 分鐘")
            print(f"  複雜度：{outlier['complexity']} | 模型：{outlier['model']}")


if __name__ == '__main__':
    main()
