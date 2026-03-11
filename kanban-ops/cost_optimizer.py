#!/usr/bin/env python3
"""
成本優化器 - 實現複雜度評估和成本感知的模型選擇
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from pathlib import Path
from model_allocator import ModelAllocator

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


class CostOptimizer:
    """成本優化器"""

    def __init__(self, models_path: str = None):
        """初始化成本優化器"""
        if models_path is None:
            models_path = Path(__file__).parent / "models.json"
        self.models_path = models_path
        self.allocator = ModelAllocator(models_path)
        self.models_config = self._load_models()

    def _load_models(self) -> dict:
        """加載模型配置"""
        try:
            with open(self.models_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except Exception as e:
            logger.error(f"❌ 加載模型配置失敗：{e}")
            raise

    def _save_models(self):
        """保存模型配置"""
        try:
            with open(self.models_path, 'w', encoding='utf-8') as f:
                json.dump(self.models_config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ 保存模型配置失敗：{e}")

    def calculate_complexity(self, task: dict) -> str:
        """
        計算任務複雜度

        評估維度：
        1. 預估時間（從 task.time_tracking.estimated_time）
        2. 任務類型（task.agent）
        3. 依賴數量（len(task.dependencies)）
        4. 優先級（task.priority）

        Args:
            task: 任務字典

        Returns:
            複雜度等級（"L1", "L2", "L3"）
        """
        # 提取預估時間
        time_tracking = task.get('time_tracking', {})
        estimated = time_tracking.get('estimated_time', {})
        min_minutes = estimated.get('min', 30)  # 默認 30 分鐘
        max_minutes = estimated.get('max', 60)  # 默認 60 分鐘

        # 使用平均時間作為評估基準
        avg_minutes = (min_minutes + max_minutes) / 2

        # 任務類型權重
        agent = task.get('agent', 'research')
        agent_weights = {
            'research': 1.0,
            'automation': 0.8,
            'developer': 0.9,
            'analyst': 1.5,
            'creative': 1.3,
            'architect': 1.6,
            'mentors': 1.7
        }
        agent_weight = agent_weights.get(agent, 1.0)

        # 依賴數量權重
        dependencies = task.get('dependencies', task.get('depends_on', []))
        dependency_weight = 1.0 + (len(dependencies) * 0.1)

        # 優先級權重
        priority = task.get('priority', 'normal')
        priority_weights = {
            'low': 0.8,
            'normal': 1.0,
            'medium': 1.0,
            'high': 1.5
        }
        priority_weight = priority_weights.get(priority, 1.0)

        # 計算複雜度分數
        complexity_score = avg_minutes * agent_weight * dependency_weight * priority_weight

        # 根據分數決定複雜度等級
        if complexity_score <= 20:
            return "L1"  # 簡單
        elif complexity_score <= 60:
            return "L2"  # 中等
        else:
            return "L3"  # 複雜

    def get_complexity_info(self, complexity_level: str) -> dict:
        """
        獲取複雜度等級信息

        Args:
            complexity_level: 複雜度等級（"L1", "L2", "L3"）

        Returns:
            複雜度信息字典
        """
        levels = self.models_config.get("complexity_levels", {})
        return levels.get(complexity_level, {})

    def select_cost_optimal_model(self, task: dict, budget_mode: str = "normal") -> Optional[str]:
        """
        選擇成本最優的模型

        策略：
        1. 評估任務複雜度
        2. 檢查預算狀態
        3. 根據預算模式和複雜度選擇模型

        Args:
            task: 任務字典
            budget_mode: 預算模式（"normal", "warning", "critical"）

        Returns:
            模型 ID，如果沒有可用模型則返回 None
        """
        # 計算任務複雜度
        complexity = self.calculate_complexity(task)
        complexity_info = self.get_complexity_info(complexity)

        logger.info(f"📊 任務複雜度：{complexity} ({complexity_info.get('name', 'Unknown')})")
        logger.info(f"   任務類型：{task.get('agent')}")
        logger.info(f"   預估時間：{task.get('time_tracking', {}).get('estimated_time', {})}")
        logger.info(f"   優先級：{task.get('priority')}")
        logger.info(f"   預算模式：{budget_mode}")

        # 根據預算模式和複雜度選擇策略
        agent = task.get('agent', 'research')

        if budget_mode == "critical":
            # 預算緊張：所有任務嘗試低成本模型
            logger.info("⚠️  預算緊張模式：嘗試低成本模型")
            if complexity == "L1":
                return self._try_models(["zai/glm-4.5"], agent)
            elif complexity == "L2":
                return self._try_models(["zai/glm-4.5", "zai/glm-4.7"], agent)
            else:  # L3
                # 複雜任務保持品質，或者返回 None
                return self._try_models(["zai/glm-4.7"], agent)

        elif budget_mode == "warning":
            # 預算警告：L1 任務使用低成本
            logger.info("⚠️  預算警告模式：L1 任務使用低成本模型")
            if complexity == "L1":
                return self._try_models(["zai/glm-4.5", "zai/glm-4.7"], agent)
            else:
                # L2 和 L3 保持正常策略
                return self._try_models(["zai/glm-4.7", "zai/glm-4.5"], agent)

        else:  # normal
            # 正常模式：品質優先
            logger.info("✅ 正常模式：品質優先")
            # 所有任務優先使用 glm-4.7（當前策略）
            return self._try_models(["zai/glm-4.7", "zai/glm-4.5"], agent)

    def _try_models(self, model_ids: List[str], agent: str) -> Optional[str]:
        """
        嘗試按優先級分配模型

        Args:
            model_ids: 模型 ID 列表（按優先級排序）
            agent: 代理 ID

        Returns:
            可用模型的 ID，如果都不可用則返回 None
        """
        for model_id in model_ids:
            # 檢查模型是否啟用
            model = self.models_config["models"].get(model_id)
            if not model or not model.get("enabled", True):
                logger.debug(f"🚫 模型 {model_id} 未啟用")
                continue

            # 檢查模型是否適合該代理
            suitable_agents = model.get("suitable_agents", [])
            if agent not in suitable_agents:
                logger.debug(f"🚫 模型 {model_id} 不適合代理 {agent}")
                continue

            # 檢查模型是否可用（使用 allocator 的檢查）
            if self.allocator._is_model_available(model_id):
                return model_id
            else:
                logger.debug(f"🚫 模型 {model_id} 不可用（rate limit 或並發限制）")

        return None

    def check_budget_status(self) -> dict:
        """
        檢查預算狀態

        Returns:
            預算狀態字典
        """
        budget = self.models_config.get("budget", {})
        daily_limit = budget.get("daily_limit", 50)
        weekly_limit = budget.get("weekly_limit", 300)
        spend_today = budget.get("spend_today", 0.0)
        spend_this_week = budget.get("spend_this_week", 0.0)

        # 計算使用率
        daily_usage = (spend_today / daily_limit) if daily_limit > 0 else 0
        weekly_usage = (spend_this_week / weekly_limit) if weekly_limit > 0 else 0

        # 判斷預算模式
        if daily_usage >= 1.0 or weekly_usage >= 1.0:
            budget_mode = "exceeded"
        elif daily_usage >= 0.9 or weekly_usage >= 0.9:
            budget_mode = "critical"
        elif daily_usage >= 0.7 or weekly_usage >= 0.7:
            budget_mode = "warning"
        else:
            budget_mode = "normal"

        return {
            "daily_limit": daily_limit,
            "weekly_limit": weekly_limit,
            "spend_today": spend_today,
            "spend_this_week": spend_this_week,
            "daily_usage": daily_usage,
            "weekly_usage": weekly_usage,
            "budget_mode": budget_mode,
            "recommendations": self._generate_budget_recommendations(budget_mode)
        }

    def _generate_budget_recommendations(self, budget_mode: str) -> List[str]:
        """
        根據預算模式生成建議

        Args:
            budget_mode: 預算模式

        Returns:
            建議列表
        """
        recommendations = []

        if budget_mode == "exceeded":
            recommendations.append("⛔ 預算已超支，停止啟動新任務")
            recommendations.append("⚠️ 只完成已啟動的任務")
            recommendations.append("📊 檢查成本報告，找出高成本任務")
        elif budget_mode == "critical":
            recommendations.append("⚠️ 預算緊張（>90%），嚴格控制新任務")
            recommendations.append("💡 將 L1 任務降級到低成本模型")
            recommendations.append("💡 推遲非緊急任務")
        elif budget_mode == "warning":
            recommendations.append("⚠️ 預算警告（>70%），注意控制成本")
            recommendations.append("💡 考慮將 L1 任務使用低成本模型")
            recommendations.append("💡 監控成本趨勢，避免超支")
        else:
            recommendations.append("✅ 預算充足，正常運作")
            recommendations.append("💡 繼續執行任務，保持品質優先")

        return recommendations

    def track_cost(self, model_id: str, cost: float, task_id: str = None):
        """
        追蹤成本

        Args:
            model_id: 模型 ID
            cost: 成本
            task_id: 任務 ID（可選）
        """
        # 更新模型統計
        model = self.models_config["models"].get(model_id)
        if not model:
            logger.warning(f"⚠️ 模型 {model_id} 不存在")
            return

        # 更新模型成本
        model["stats"]["total_cost"] = model["stats"].get("total_cost", 0.0) + cost

        # 更新日期成本
        today = datetime.now().strftime("%Y-%m-%d")
        cost_by_date = model["stats"].get("cost_by_date", {})
        cost_by_date[today] = cost_by_date.get(today, 0.0) + cost
        model["stats"]["cost_by_date"] = cost_by_date

        # 更新總預算
        budget = self.models_config.get("budget", {})
        budget["current_spend"] = budget.get("current_spend", 0.0) + cost
        budget["spend_today"] = budget.get("spend_today", 0.0) + cost
        budget["spend_this_week"] = budget.get("spend_this_week", 0.0) + cost
        budget["spend_this_month"] = budget.get("spend_this_month", 0.0) + cost

        # 記錄成本歷史
        spend_history = budget.get("spend_history", [])
        spend_history.append({
            "timestamp": datetime.now().isoformat(),
            "model_id": model_id,
            "cost": cost,
            "task_id": task_id
        })
        budget["spend_history"] = spend_history

        # 保存配置
        self._save_models()

        logger.info(f"💰 成本追蹤：{model_id} +¥{cost:.2f} (任務: {task_id})")

    def estimate_task_cost(self, model_id: str, task: dict) -> float:
        """
        預估任務成本

        Args:
            model_id: 模型 ID
            task: 任務字典

        Returns:
            預估成本
        """
        model = self.models_config["models"].get(model_id)
        if not model:
            logger.warning(f"⚠️ 模型 {model_id} 不存在")
            return 0.0

        # 獲取成本元數據
        cost_metadata = model.get("cost_metadata", {})
        estimated_cost_per_request = cost_metadata.get("estimated_cost_per_request", 0.1)

        # 根據任務複雜度調整
        complexity = self.calculate_complexity(task)
        complexity_factors = {
            "L1": 0.8,
            "L2": 1.0,
            "L3": 1.5
        }

        estimated_cost = estimated_cost_per_request * complexity_factors.get(complexity, 1.0)

        return estimated_cost

    def generate_cost_report(self) -> dict:
        """
        生成成本報告

        Returns:
            成本報告字典
        """
        budget = self.models_config.get("budget", {})
        budget_status = self.check_budget_status()

        # 統計每個模型的成本
        model_costs = {}
        for model_id, model in self.models_config["models"].items():
            stats = model.get("stats", {})
            total_cost = stats.get("total_cost", 0.0)
            total_requests = stats.get("total_requests", 0)
            avg_cost = total_cost / total_requests if total_requests > 0 else 0.0

            model_costs[model_id] = {
                "total_cost": total_cost,
                "total_requests": total_requests,
                "avg_cost": avg_cost,
                "cost_by_date": stats.get("cost_by_date", {})
            }

        # 統計每個代理類型的成本
        agent_costs = {}
        # TODO: 需要從任務歷史統計，這裡先留空

        return {
            "generated_at": datetime.now().isoformat(),
            "budget_status": budget_status,
            "model_costs": model_costs,
            "agent_costs": agent_costs
        }


if __name__ == "__main__":
    # 測試成本優化器
    optimizer = CostOptimizer()

    print("\n" + "=" * 60)
    print("🧪 成本優化器測試")
    print("=" * 60)

    # 測試 1：計算任務複雜度
    print("\n1. 測試任務複雜度評估：")
    test_tasks = [
        {
            "agent": "research",
            "priority": "low",
            "time_tracking": {"estimated_time": {"min": 10, "max": 15}},
            "dependencies": []
        },
        {
            "agent": "analyst",
            "priority": "high",
            "time_tracking": {"estimated_time": {"min": 45, "max": 60}},
            "dependencies": ["task1", "task2", "task3"]
        },
        {
            "agent": "creative",
            "priority": "medium",
            "time_tracking": {"estimated_time": {"min": 30, "max": 45}},
            "dependencies": ["task1"]
        }
    ]

    for i, task in enumerate(test_tasks, 1):
        complexity = optimizer.calculate_complexity(task)
        complexity_info = optimizer.get_complexity_info(complexity)
        print(f"   任務 {i}: {complexity} - {complexity_info.get('name', 'Unknown')}")
        print(f"      代理：{task['agent']}, 優先級：{task['priority']}, 預估時間：{task['time_tracking']['estimated_time']}")

    # 測試 2：檢查預算狀態
    print("\n2. 檢查預算狀態：")
    budget_status = optimizer.check_budget_status()
    print(f"   預算模式：{budget_status['budget_mode']}")
    print(f"   今日花費：¥{budget_status['spend_today']:.2f} / ¥{budget_status['daily_limit']} ({budget_status['daily_usage']:.1%})")
    print(f"   本週花費：¥{budget_status['spend_this_week']:.2f} / ¥{budget_status['weekly_limit']} ({budget_status['weekly_usage']:.1%})")
    print("   建議：")
    for rec in budget_status['recommendations']:
        print(f"      {rec}")

    # 測試 3：選擇成本最優模型
    print("\n3. 選擇成本最優模型（正常模式）：")
    for i, task in enumerate(test_tasks, 1):
        model_id = optimizer.select_cost_optimal_model(task, budget_mode="normal")
        if model_id:
            model = optimizer.models_config["models"][model_id]
            cost_metadata = model.get("cost_metadata", {})
            print(f"   任務 {i} → {model_id} (成本因子: {cost_metadata.get('cost_factor', 1.0)})")
        else:
            print(f"   任務 {i} → 無可用模型")

    # 測試 4：預估任務成本
    print("\n4. 預估任務成本：")
    for i, task in enumerate(test_tasks, 1):
        complexity = optimizer.calculate_complexity(task)
        for model_id in ["zai/glm-4.7", "zai/glm-4.5"]:
            cost = optimizer.estimate_task_cost(model_id, task)
            print(f"   任務 {i} ({complexity}) 使用 {model_id}: ¥{cost:.3f}")

    # 測試 5：追蹤成本
    print("\n5. 追蹤成本：")
    optimizer.track_cost("zai/glm-4.7", 0.15, "test-task-001")
    optimizer.track_cost("zai/glm-4.5", 0.06, "test-task-002")

    # 測試 6：生成成本報告
    print("\n6. 生成成本報告：")
    report = optimizer.generate_cost_report()
    print(f"   生成時間：{report['generated_at']}")
    print("   模型成本：")
    for model_id, costs in report['model_costs'].items():
        print(f"      {model_id}: ¥{costs['total_cost']:.2f} ({costs['total_requests']} 請求, 平均 ¥{costs['avg_cost']:.3f}/請求)")

    print("\n✅ 測試完成")
