#!/usr/bin/env python3
"""
任務自動分解建議模組

根據複雜度自動生成任務分解方案。
"""

import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

from task_complexity import TaskComplexityEstimator, ComplexityAssessment


@dataclass
class SubTaskSuggestion:
    """子任務建議"""
    id: str
    title: str
    description: str
    agent: str
    input_paths: List[str]
    estimated_level: int
    reason: str


@dataclass
class DecompositionSuggestion:
    """分解建議"""
    should_decompose: bool
    reason: str
    subtasks: List[SubTaskSuggestion]
    strategy: str  # 'by_input', 'by_phase', 'by_component'
    estimated_time_reduction: float  # 預估節省的時間百分比


class TaskDecomposer:
    """任務分解器"""

    def __init__(self):
        self.complexity_estimator = TaskComplexityEstimator()

    def analyze_decomposition(self, task: Dict) -> DecompositionSuggestion:
        """
        分析任務是否需要分解，並生成分解建議

        Args:
            task: 任務字典

        Returns:
            DecompositionSuggestion: 分解建議
        """
        # 1. 評估複雜度
        assessment = self.complexity_estimator.estimate(task)

        # 2. 判斷是否需要分解
        should_decompose = self._should_decompose(task, assessment)

        if not should_decompose:
            return DecompositionSuggestion(
                should_decompose=False,
                reason=f"任務複雜度等級 {assessment.level}，不需要分解",
                subtasks=[],
                strategy="none",
                estimated_time_reduction=0.0
            )

        # 3. 選擇分解策略
        strategy = self._select_strategy(task, assessment)

        # 4. 生成子任務
        subtasks = self._generate_subtasks(task, assessment, strategy)

        # 5. 計算預估時間節省
        time_reduction = self._estimate_time_reduction(assessment, subtasks)

        # 6. 生成理由
        reason = self._generate_reason(task, assessment, strategy, subtasks)

        return DecompositionSuggestion(
            should_decompose=True,
            reason=reason,
            subtasks=subtasks,
            strategy=strategy,
            estimated_time_reduction=time_reduction
        )

    def _should_decompose(self, task: Dict, assessment: ComplexityAssessment) -> bool:
        """判斷是否需要分解"""
        # 規則 1：複雜度等級 4 必須分解
        if assessment.level >= 4:
            return True

        # 規則 2：複雜度等級 3 且輸入文件 >= 3 個
        n_inputs = len(task.get('input_paths', []))
        if assessment.level >= 3 and n_inputs >= 3:
            return True

        # 規則 3：複雜度等級 3 且 analyst 代理
        if assessment.level >= 3 and task.get('agent') == 'analyst':
            return True

        # 規則 4：複雜度分數 > 7
        if assessment.score > 7.0:
            return True

        return False

    def _select_strategy(self, task: Dict, assessment: ComplexityAssessment) -> str:
        """選擇分解策略"""
        n_inputs = len(task.get('input_paths', []))
        notes = task.get('notes', '').lower()

        # 策略 1：按輸入文件分解
        if n_inputs >= 3:
            return 'by_input'

        # 策略 2：按階段分解
        if any(keyword in notes for keyword in ['分析', '驗證', '實證', '測試']):
            return 'by_phase'

        # 策略 3：按組件分解
        if any(keyword in notes for keyword in ['集成', '整合', '系統', '框架']):
            return 'by_component'

        # 默認按輸入文件
        return 'by_input'

    def _generate_subtasks(self, task: Dict, assessment: ComplexityAssessment,
                          strategy: str) -> List[SubTaskSuggestion]:
        """生成子任務"""
        task_id = task.get('id', 'unknown')
        input_paths = task.get('input_paths', [])
        agent = task.get('agent', 'automation')
        notes = task.get('notes', '')

        if strategy == 'by_input':
            return self._decompose_by_input(task_id, input_paths, agent, notes)
        elif strategy == 'by_phase':
            return self._decompose_by_phase(task_id, agent, notes)
        elif strategy == 'by_component':
            return self._decompose_by_component(task_id, agent, notes)
        else:
            return []

    def _decompose_by_input(self, task_id: str, input_paths: List[str],
                           agent: str, notes: str) -> List[SubTaskSuggestion]:
        """按輸入文件分解"""
        subtasks = []

        # 將輸入文件分組（每組 1-2 個）
        for i, group in enumerate(self._group_inputs(input_paths, group_size=2)):
            subtask_id = f"{task_id}-{chr(97 + i)}"  # -a, -b, -c, ...

            subtasks.append(SubTaskSuggestion(
                id=subtask_id,
                title=f"處理輸入組 {chr(65 + i)}",
                description=f"處理以下輸入文件：{', '.join(group)}",
                agent=agent,
                input_paths=group,
                estimated_level=2,  # 降低到等級 2
                reason=f"減少輸入文件數從 {len(input_paths)} 到 {len(group)}"
            ))

        return subtasks

    def _decompose_by_phase(self, task_id: str, agent: str,
                           notes: str) -> List[SubTaskSuggestion]:
        """按階段分解"""
        subtasks = []

        # 分析階段
        if '分析' in notes or '驗證' in notes:
            subtasks.append(SubTaskSuggestion(
                id=f"{task_id}-a",
                title="階段 1：準備與分析",
                description="分析輸入文件，理解需求，設計方案",
                agent='analyst' if agent == 'analyst' else 'automation',
                input_paths=[],
                estimated_level=2,
                reason="將分析階段獨立出來，降低複雜度"
            ))

        # 實作階段
        subtasks.append(SubTaskSuggestion(
            id=f"{task_id}-b",
            title="階段 2：實作與生成",
            description="根據分析結果實作核心功能",
            agent=agent,
            input_paths=[f"{task_id}-a"],
            estimated_level=2,
            reason="基於階段 1 的輸出，聚焦於實作"
        ))

        # 驗證階段
        if '驗證' in notes or '測試' in notes or '實證' in notes:
            subtasks.append(SubTaskSuggestion(
                id=f"{task_id}-c",
                title="階段 3：驗證與測試",
                description="驗證實作結果，運行測試",
                agent='automation',
                input_paths=[f"{task_id}-b"],
                estimated_level=2,
                reason="獨立驗證階段，確保質量"
            ))

        return subtasks

    def _decompose_by_component(self, task_id: str, agent: str,
                               notes: str) -> List[SubTaskSuggestion]:
        """按組件分解"""
        subtasks = []

        # 組件 1：設計
        subtasks.append(SubTaskSuggestion(
            id=f"{task_id}-a",
            title="組件 1：架構設計",
            description="設計系統架構，定義接口和數據流",
            agent='analyst',
            input_paths=[],
            estimated_level=2,
            reason="將架構設計獨立出來"
        ))

        # 組件 2：核心實作
        subtasks.append(SubTaskSuggestion(
            id=f"{task_id}-b",
            title="組件 2：核心實作",
            description="實作核心功能和主要邏輯",
            agent=agent,
            input_paths=[f"{task_id}-a"],
            estimated_level=2,
            reason="基於設計文檔實作核心功能"
        ))

        # 組件 3：集成與測試
        subtasks.append(SubTaskSuggestion(
            id=f"{task_id}-c",
            title="組件 3：集成與測試",
            description="集成各組件，進行端對端測試",
            agent='automation',
            input_paths=[f"{task_id}-a", f"{task_id}-b"],
            estimated_level=2,
            reason="最後集成所有組件"
        ))

        return subtasks

    def _group_inputs(self, inputs: List[str], group_size: int) -> List[List[str]]:
        """將輸入文件分組"""
        groups = []
        for i in range(0, len(inputs), group_size):
            groups.append(inputs[i:i + group_size])
        return groups

    def _estimate_time_reduction(self, assessment: ComplexityAssessment,
                                subtasks: List[SubTaskSuggestion]) -> float:
        """估算時間節省百分比"""
        if not subtasks:
            return 0.0

        # 原始預估時間（使用中點）
        original_time = (assessment.estimated_time[0] + assessment.estimated_time[1]) / 2

        # 分解後的時間（每個子任務等級 2，預估 8-18 分）
        subtask_time = 13  # (8 + 18) / 2
        total_subtask_time = subtask_time * len(subtasks)

        # 並行執行可以節省時間（假設 50% 可並行）
        parallel_time = total_subtask_time * 0.7

        time_reduction = ((original_time - parallel_time) / original_time) * 100
        return round(time_reduction, 1)

    def _generate_reason(self, task: Dict, assessment: ComplexityAssessment,
                        strategy: str, subtasks: List[SubTaskSuggestion]) -> str:
        """生成分解理由"""
        n_inputs = len(task.get('input_paths', []))

        reasons = [
            f"複雜度等級 {assessment.level}，分數 {assessment.score:.1f}",
            f"輸入文件 {n_inputs} 個"
        ]

        if strategy == 'by_input':
            reasons.append(f"按輸入文件分解為 {len(subtasks)} 個子任務")
            reasons.append(f"每個子任務處理 1-2 個輸入文件")
        elif strategy == 'by_phase':
            reasons.append(f"按階段分解為 {len(subtasks)} 個階段")
            reasons.append("降低單個階段的複雜度")
        elif strategy == 'by_component':
            reasons.append(f"按組件分解為 {len(subtasks)} 個組件")
            reasons.append("每個組件獨立開發和測試")

        return " | ".join(reasons)

    def format_suggestion(self, suggestion: DecompositionSuggestion, task: Dict) -> str:
        """格式化分解建議"""
        lines = [
            "=" * 70,
            "🔪 任務分解建議",
            "=" * 70,
            "",
            f"任務 ID：{task.get('id', 'unknown')}",
            f"任務標題：{task.get('title', 'unknown')}",
            ""
        ]

        if not suggestion.should_decompose:
            lines.extend([
                "✅ 此任務不需要分解",
                "",
                f"理由：{suggestion.reason}",
                "",
                "建議：直接執行此任務"
            ])
        else:
            lines.extend([
                "⚠️  建議：將此任務分解為多個子任務",
                "",
                f"理由：{suggestion.reason}",
                "",
                f"分解策略：{suggestion.strategy}",
                f"預估節省時間：{suggestion.estimated_time_reduction}%",
                "",
                "─" * 70,
                "子任務清單",
                "─" * 70,
                ""
            ])

            for i, subtask in enumerate(suggestion.subtasks, 1):
                lines.extend([
                    f"子任務 {i}：{subtask.id}",
                    f"  標題：{subtask.title}",
                    f"  描述：{subtask.description}",
                    f"  代理：{subtask.agent}",
                    f"  預估複雜度：等級 {subtask.estimated_level}",
                    f"  理由：{subtask.reason}",
                    ""
                ])

            lines.extend([
                "─" * 70,
                "執行建議",
                "─" * 70,
                "",
                f"1. 創建 {len(suggestion.subtasks)} 個子任務",
                "2. 設置依賴關係（按順序執行）",
                "3. 確保每個子任務的複雜度 ≤ 等級 2",
                "4. 使用推薦的模型",
                "",
                "預期效果：",
                f"• 成功率提升（從 ~60% 到 ~95%）",
                f"• 時間節省：{suggestion.estimated_time_reduction}%",
                "• 更好的錯誤隔離"
            ])

        lines.extend(["", "=" * 70])

        return "\n".join(lines)


def main():
    """測試範例"""
    decomposer = TaskDecomposer()

    # 測試案例 1：h004（需要分解）
    task_h004 = {
        'id': 'h004',
        'title': 'adaptive-hedge 回測驗證',
        'agent': 'automation',
        'input_paths': ['h003c', 'h002', 'h003a', 'h003b'],
        'notes': 'adaptive-hedge 回測驗證：歷史崩盤事件實證測試'
    }

    # 測試案例 2：簡單任務（不需要分解）
    task_simple = {
        'id': 'p001',
        'title': '建立專案索引地圖',
        'agent': 'automation',
        'input_paths': [],
        'notes': '掃描專案，建立索引'
    }

    # 測試案例 3：複雜分析任務（需要分解）
    task_complex = {
        'id': 'qe002',
        'title': 'QuantEvolve 集成',
        'agent': 'automation',
        'input_paths': ['qe001'],
        'notes': '整合 QuantEvolve 系統到主框架'
    }

    for task in [task_h004, task_simple, task_complex]:
        suggestion = decomposer.analyze_decomposition(task)
        print(decomposer.format_suggestion(suggestion, task))
        print()


if __name__ == '__main__':
    main()
