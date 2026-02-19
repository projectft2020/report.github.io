#!/usr/bin/env python3
"""
任務複雜度估算模組

根據任務屬性自動估算複雜度等級、預估時間和推薦模型。
"""

from typing import Dict, Tuple, List
from dataclasses import dataclass


@dataclass
class ComplexityAssessment:
    """複雜度評估結果"""
    level: int              # 複雜度等級 (1-4)
    level_name: str         # 等級名稱
    score: float            # 複雜度分數
    estimated_time: Tuple[int, int]  # (最小分鐘, 最大分鐘)
    recommended_model: str  # 推薦模型
    should_decompose: bool  # 是否建議分解
    reason: str             # 評估理由


class TaskComplexityEstimator:
    """任務複雜度估算器"""

    # 任務類型係數
    TASK_TYPE_COEFFICIENTS = {
        'research': 1.0,
        'analyst': 2.0,
        'automation': 1.0,
        'creative': 1.5,
    }

    # 模型係數（模型處理能力與速度的權衡）
    MODEL_COEFFICIENTS = {
        'glm-4.7': 1.5,   # 處理能力強但較慢
        'glm-4.5': 0.5,   # 速度快但能力較弱
        'glm-4.5-flash': 0.3,
    }

    # 複雜關鍵詞
    COMPLEX_KEYWORDS = [
        '整合', '集成', '分析', '對比', '驗證',
        '回測', '優化', '設計', '實現', '系統',
        '架構', '框架', '多模組', '跨系統',
        '端對端', '端到端', '實證', '模擬'
    ]

    # 複雜度等級定義
    COMPLEXITY_LEVELS = {
        1: {
            'name': '簡單任務',
            'description': '0-1 個輸入，輸出 <10KB',
            'time_range': (3, 8),
            'model': 'zai/glm-4.5',
        },
        2: {
            'name': '中等任務',
            'description': '1-2 個輸入，輸出 10-30KB',
            'time_range': (8, 18),
            'model': 'zai/glm-4.5',
        },
        3: {
            'name': '複雜任務',
            'description': '2-4 個輸入，輸出 30-60KB',
            'time_range': (15, 35),
            'model': 'zai/glm-4.7',
        },
        4: {
            'name': '極複雜任務',
            'description': '4+ 個輸入，輸出 60-100KB',
            'time_range': (30, 50),
            'model': 'zai/glm-4.7',
        }
    }

    def estimate(self, task: Dict) -> ComplexityAssessment:
        """
        估算任務複雜度

        Args:
            task: 任務字典，包含以下欄位：
                - input_paths: 輸入文件路徑列表
                - agent: 代理類型 (research/analyst/automation/creative)
                - model: 模型名稱
                - depends_on: 依賴任務列表
                - notes/notes: 任務描述

        Returns:
            ComplexityAssessment: 複雜度評估結果
        """
        complexity_score = 0.0
        reasons = []

        # 1. 輸入文件數量（每個 +1 分）
        input_paths = task.get('input_paths', [])
        n_inputs = len(input_paths)
        complexity_score += n_inputs
        if n_inputs > 0:
            reasons.append(f"輸入文件：{n_inputs} 個 (+{n_inputs})")

        # 2. 任務類型
        task_type = task.get('agent', '')
        type_coef = self.TASK_TYPE_COEFFICIENTS.get(task_type, 1.0)
        complexity_score += type_coef
        type_name = {
            'research': '研究',
            'analyst': '分析',
            'automation': '自動化',
            'creative': '創作'
        }.get(task_type, task_type)
        reasons.append(f"任務類型：{type_name} (+{type_coef})")

        # 3. 當前選擇的模型（如果已指定）
        current_model = task.get('model', '')
        if current_model:
            # 提取模型版本
            model_key = None
            for key in self.MODEL_COEFFICIENTS:
                if key in current_model:
                    model_key = key
                    break

            if model_key:
                model_coef = self.MODEL_COEFFICIENTS[model_key]
                complexity_score += model_coef
                reasons.append(f"模型：{model_key} (+{model_coef})")

        # 4. 依賴關係
        depends_on = task.get('depends_on', [])
        n_deps = len(depends_on)
        if n_deps > 0:
            dep_score = n_deps * 0.5
            complexity_score += dep_score
            reasons.append(f"依賴任務：{n_deps} 個 (+{dep_score})")

        # 5. 任務描述複雜度（關鍵詞計數）
        notes = task.get('notes', task.get('description', ''))
        notes_lower = notes.lower() if notes else ''

        keyword_count = 0
        found_keywords = []
        for keyword in self.COMPLEX_KEYWORDS:
            if keyword in notes_lower:
                keyword_count += 1
                found_keywords.append(keyword)

        if keyword_count > 0:
            keyword_score = keyword_count * 0.5
            complexity_score += keyword_score
            reasons.append(f"關鍵詞：{', '.join(found_keywords[:3])} (+{keyword_score})")

        # 6. 轉換為複雜度等級
        if complexity_score <= 2:
            level = 1
        elif complexity_score <= 4:
            level = 2
        elif complexity_score <= 7:
            level = 3
        else:
            level = 4

        # 7. 獲取等級資訊
        level_info = self.COMPLEXITY_LEVELS[level]
        level_name = level_info['name']
        estimated_time = level_info['time_range']
        recommended_model = level_info['model']

        # 8. 判斷是否建議分解
        should_decompose = (
            level == 4 or
            (level == 3 and n_inputs >= 3)
        )

        # 9. 建構理由
        reason = " | ".join(reasons)
        if should_decompose:
            reason += " | ⚠️ 建議分解為多個子任務"

        return ComplexityAssessment(
            level=level,
            level_name=level_name,
            score=complexity_score,
            estimated_time=estimated_time,
            recommended_model=recommended_model,
            should_decompose=should_decompose,
            reason=reason
        )

    def format_assessment(self, assessment: ComplexityAssessment) -> str:
        """格式化評估結果為可讀字符串"""
        lines = [
            f"📊 複雜度評估",
            f"",
            f"等級：{assessment.level} - {assessment.level_name}",
            f"分數：{assessment.score:.1f}",
            f"預估時間：{assessment.estimated_time[0]}-{assessment.estimated_time[1]} 分鐘",
            f"推薦模型：{assessment.recommended_model}",
            f"",
            f"評估依據：",
            f"  {assessment.reason}",
        ]

        if assessment.should_decompose:
            lines.extend([
                f"",
                f"⚠️  建議：此任務複雜度較高，建議分解為多個子任務"
            ])

        return "\n".join(lines)


def main():
    """測試範例"""
    estimator = TaskComplexityEstimator()

    # 測試案例 1：h004（失敗案例）
    task_h004 = {
        'input_paths': ['h003c', 'h002', 'h003a', 'h003b'],
        'agent': 'automation',
        'model': 'zai/glm-4.5',
        'depends_on': [],
        'notes': 'adaptive-hedge 回測驗證：歷史崩盤事件實證測試'
    }

    # 測試案例 2：m002（成功案例）
    task_m002 = {
        'input_paths': ['m001'],
        'agent': 'analyst',
        'model': 'zai/glm-4.7',
        'depends_on': [],
        'notes': 'momentum-dist-risk 風險評估：VaR/CVaR 計算、極端場景分析'
    }

    # 測試案例 3：簡單任務
    task_simple = {
        'input_paths': [],
        'agent': 'automation',
        'model': 'zai/glm-4.5',
        'depends_on': [],
        'notes': '文件整理'
    }

    print("=" * 60)
    print("測試案例 1：h004（adaptive-hedge 回測驗證）")
    print("=" * 60)
    assessment = estimator.estimate(task_h004)
    print(estimator.format_assessment(assessment))
    print()

    print("=" * 60)
    print("測試案例 2：m002（風險評估）")
    print("=" * 60)
    assessment = estimator.estimate(task_m002)
    print(estimator.format_assessment(assessment))
    print()

    print("=" * 60)
    print("測試案例 3：簡單文件整理")
    print("=" * 60)
    assessment = estimator.estimate(task_simple)
    print(estimator.format_assessment(assessment))


if __name__ == '__main__':
    main()
