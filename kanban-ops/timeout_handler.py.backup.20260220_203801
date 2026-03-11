#!/usr/bin/env python3
"""
超時處理模組

自動檢測超時任務，檢查輸出文件，提供處理建議。
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

from time_tracker import TaskTimeTracker


@dataclass
class TimeoutAnalysis:
    """超時分析結果"""
    task_id: str
    title: str
    status: str
    is_timeout: bool
    output_exists: bool
    output_complete: bool
    recommended_action: str  # 'mark_completed', 'retry', 'mark_failed', 'decompose'
    reason: str
    retry_strategy: Optional[str] = None


class TimeoutHandler:
    """超時處理器"""

    def __init__(self, tasks_json_path: str, workspace_path: str):
        """
        初始化超時處理器

        Args:
            tasks_json_path: tasks.json 文件路徑
            workspace_path: 工作區路徑（用於檢查輸出文件）
        """
        self.tasks_json_path = Path(tasks_json_path)
        self.workspace_path = Path(workspace_path)
        self.time_tracker = TaskTimeTracker(tasks_json_path)
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

    def check_timeouts(self, timeout_threshold_minutes: float = 30.0) -> List[TimeoutAnalysis]:
        """
        檢查超時任務

        Args:
            timeout_threshold_minutes: 超時閾值（分鐘）

        Returns:
            超時分析結果列表
        """
        results = []
        now = datetime.now()

        for task in self.tasks:
            # 只檢查 in_progress 狀態的任務
            if task.get('status') != 'in_progress':
                continue

            # 獲取開始時間
            time_tracking = task.get('time_tracking', {})
            started_at_str = time_tracking.get('started_at')

            if not started_at_str:
                continue

            started_at = datetime.fromisoformat(started_at_str)
            duration_minutes = (now - started_at).total_seconds() / 60

            # 檢查是否超時
            is_timeout = duration_minutes > timeout_threshold_minutes

            if is_timeout:
                analysis = self._analyze_timeout(task, duration_minutes)
                results.append(analysis)

        return results

    def _analyze_timeout(self, task: Dict, duration_minutes: float) -> TimeoutAnalysis:
        """
        分析超時任務

        Args:
            task: 任務字典
            duration_minutes: 已執行時間（分鐘）

        Returns:
            超時分析結果
        """
        task_id = task['id']
        title = task['title']

        # 檢查輸出文件
        output_path = task.get('output_path')
        output_exists = False
        output_complete = False

        if output_path:
            full_output_path = self.workspace_path / output_path
            output_exists = full_output_path.exists()

            if output_exists:
                # 檢查文件是否完整（簡單檢查：文件大小）
                file_size = full_output_path.stat().st_size
                output_complete = file_size > 1000  # 至少 1KB

        # 決定推薦動作
        recommended_action, reason, retry_strategy = self._determine_action(
            task, output_exists, output_complete, duration_minutes
        )

        return TimeoutAnalysis(
            task_id=task_id,
            title=title,
            status=task.get('status', ''),
            is_timeout=True,
            output_exists=output_exists,
            output_complete=output_complete,
            recommended_action=recommended_action,
            reason=reason,
            retry_strategy=retry_strategy
        )

    def _determine_action(self, task: Dict, output_exists: bool,
                         output_complete: bool, duration_minutes: float) -> Tuple[str, str, Optional[str]]:
        """
        決定推薦動作

        Returns:
            (recommended_action, reason, retry_strategy)
        """
        time_tracking = task.get('time_tracking', {})
        estimated = time_tracking.get('estimated_time')

        # 情況 1：輸出文件存在且完整
        if output_exists and output_complete:
            return (
                'mark_completed',
                f'輸出文件存在且完整（{duration_minutes:.1f} 分鐘）',
                None
            )

        # 情況 2：輸出文件存在但不完整
        if output_exists and not output_complete:
            return (
                'mark_failed',
                f'輸出文件存在但不完整（可能寫入中斷）',
                'retry_with_higher_timeout'
            )

        # 情況 3：輸出文件不存在
        if not output_exists:
            # 檢查是否有預估時間
            if estimated:
                max_estimated = estimated['max']
                if duration_minutes > max_estimated * 1.5:
                    # 超過預估時間 150%
                    return (
                        'retry',
                        f'超時 {duration_minutes:.1f} 分鐘，超過預估 {max_estimated} 分鐘的 150%',
                        'retry_with_decomposition'
                    )
                else:
                    # 還在預估範圍內
                    return (
                        'wait',
                        f'已執行 {duration_minutes:.1f} 分鐘，仍在預估範圍內（{max_estimated} 分鐘）',
                        None
                    )
            else:
                # 沒有預估時間
                return (
                    'retry',
                    f'超時 {duration_minutes:.1f} 分鐘，無輸出文件',
                    'retry_with_different_model'
                )

        return ('unknown', '未知情況', None)

    def mark_task_completed(self, task_id: str):
        """標記任務為完成（超時但成功）"""
        task = self._find_task(task_id)
        if not task:
            raise ValueError(f"找不到任務：{task_id}")

        task['status'] = 'completed'
        task['completed_at'] = datetime.now().isoformat()

        # 計算實際時間
        time_tracking = task.get('time_tracking', {})
        if 'started_at' in time_tracking:
            started_at = datetime.fromisoformat(time_tracking['started_at'])
            completed_at = datetime.fromisoformat(task['completed_at'])
            actual_minutes = (completed_at - started_at).total_seconds() / 60
            time_tracking['actual_time_minutes'] = round(actual_minutes, 2)

            # 添加超時標記
            time_tracking['timeout_recovery'] = True
            time_tracking['timeout_note'] = '任務超時但輸出完整，已標記為完成'

        self._save_tasks()
        print(f"✅ 任務 {task_id} 已標記為完成（超時恢復）")

    def mark_task_failed(self, task_id: str, reason: str):
        """標記任務為失敗"""
        task = self._find_task(task_id)
        if not task:
            raise ValueError(f"找不到任務：{task_id}")

        task['status'] = 'failed'
        task['failed_at'] = datetime.now().isoformat()
        task['failure_reason'] = reason

        self._save_tasks()
        print(f"❌ 任務 {task_id} 已標記為失敗：{reason}")

    def suggest_retry(self, task_id: str) -> Dict:
        """
        生成重試建議

        Args:
            task_id: 任務 ID

        Returns:
            重試建議字典
        """
        task = self._find_task(task_id)
        if not task:
            raise ValueError(f"找不到任務：{task_id}")

        time_tracking = task.get('time_tracking', {})
        complexity = time_tracking.get('complexity_level')
        model = time_tracking.get('recommended_model')

        suggestions = {
            'task_id': task_id,
            'strategies': []
        }

        # 策略 1：分解任務
        if complexity and complexity >= 3:
            suggestions['strategies'].append({
                'name': 'decompose_task',
                'description': '將任務分解為 2-3 個子任務',
                'reason': '複雜度等級 3+，分解可提高成功率',
                'command': f'python3 task_manager.py decompose {task_id}'
            })

        # 策略 2：更換模型
        if model and '4.5' in model:
            suggestions['strategies'].append({
                'name': 'upgrade_model',
                'description': '使用 GLM-4.7 替代 GLM-4.5',
                'reason': 'GLM-4.7 處理能力更強',
                'new_model': 'zai/glm-4.7'
            })

        # 策略 3：增加超時時間
        suggestions['strategies'].append({
            'name': 'increase_timeout',
            'description': '增加超時時間限制',
            'reason': '任務可能需要更長時間',
            'suggested_timeout': '60 分鐘'
        })

        return suggestions

    def _find_task(self, task_id: str) -> Optional[Dict]:
        """查找任務"""
        for task in self.tasks:
            if task['id'] == task_id or task['id'].endswith(task_id):
                return task
        return None

    def generate_timeout_report(self) -> str:
        """生成超時報告"""
        lines = [
            "=" * 70,
            "⏰ 超時任務檢測報告",
            "=" * 70,
            "",
            f"檢測時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]

        # 檢查超時任務
        timeouts = self.check_timeouts(timeout_threshold_minutes=30.0)

        if not timeouts:
            lines.extend([
                "✅ 沒有檢測到超時任務",
                "",
                "所有 in_progress 任務都在正常執行時間範圍內",
                ""
            ])
        else:
            lines.extend([
                f"⚠️  發現 {len(timeouts)} 個超時任務",
                "",
                "─" * 70,
                "超時任務詳情",
                "─" * 70,
                ""
            ])

            for i, analysis in enumerate(timeouts, 1):
                lines.extend([
                    f"任務 {i}：{analysis.task_id}",
                    f"  標題：{analysis.title}",
                    f"  狀態：{analysis.status}",
                    f"  輸出文件：{'存在' if analysis.output_exists else '不存在'}",
                    f"  輸出完整：{'是' if analysis.output_complete else '否'}",
                    f"  推薦動作：{analysis.recommended_action}",
                    f"  理由：{analysis.reason}",
                    ""
                ])

                if analysis.retry_strategy:
                    suggestions = self.suggest_retry(analysis.task_id)
                    if suggestions['strategies']:
                        lines.extend([
                            "  重試策略：",
                            ""
                        ])
                        for strategy in suggestions['strategies']:
                            lines.extend([
                                f"    • {strategy['description']}",
                                f"      理由：{strategy['reason']}",
                                ""
                            ])

        lines.extend([
            "=" * 70,
            "",
            "說明：",
            "• 超時閾值：30 分鐘",
            "• 輸出完整：文件大小 > 1KB",
            "• 推薦動作：",
            "  - mark_completed：標記為完成（超時但成功）",
            "  - mark_failed：標記為失敗",
            "  - retry：建議重試",
            "  - wait：繼續等待",
            "",
            "處理建議：",
            "• 對於 mark_completed：使用 handler.mark_task_completed(task_id)",
            "• 對於 mark_failed：使用 handler.mark_task_failed(task_id, reason)",
            "• 對於 retry：查看重試策略並執行",
            ""
        ])

        return "\n".join(lines)

    def format_analysis(self, analysis: TimeoutAnalysis) -> str:
        """格式化單個超時分析"""
        lines = [
            "=" * 70,
            "⏰ 超時任務分析",
            "=" * 70,
            "",
            f"任務 ID：{analysis.task_id}",
            f"標題：{analysis.title}",
            f"狀態：{analysis.status}",
            f"輸出文件存在：{'是' if analysis.output_exists else '否'}",
            f"輸出完整：{'是' if analysis.output_complete else '否'}",
            "",
            "─" * 70,
            "推薦處理",
            "─" * 70,
            "",
            f"動作：{analysis.recommended_action}",
            f"理由：{analysis.reason}",
            ""
        ]

        if analysis.retry_strategy:
            suggestions = self.suggest_retry(analysis.task_id)
            if suggestions['strategies']:
                lines.extend([
                    "重試策略：",
                    ""
                ])
                for strategy in suggestions['strategies']:
                    lines.extend([
                        f"• {strategy['description']}",
                        f"  理由：{strategy['reason']}",
                        ""
                    ])

        lines.extend([
            "=" * 70,
            "",
            "處理命令：",
            f"  python3 -c \"",
            f"  from timeout_handler import TimeoutHandler;",
            f"  handler = TimeoutHandler('/Users/charlie/.openclaw/workspace/kanban/tasks.json', '/Users/charlie/.openclaw/workspace');",
            f"  handler.mark_task_completed('{analysis.task_id}')",
            f"  \""
        ])

        return "\n".join(lines)


def main():
    """測試範例"""
    handler = TimeoutHandler(
        '/Users/charlie/.openclaw/workspace/kanban/tasks.json',
        '/Users/charlie/.openclaw/workspace'
    )

    # 生成超時報告
    print(handler.generate_timeout_report())


if __name__ == '__main__':
    main()
