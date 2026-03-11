#!/usr/bin/env python3
"""
Model Monitor - 模型監控器
監控模型使用情況、檢測 rate limit、記錄統計數據
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List
from pathlib import Path
from model_allocator import ModelAllocator

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


class ModelMonitor:
    """模型監控器"""

    def __init__(self, models_path: str = None):
        """初始化模型監控器"""
        self.allocator = ModelAllocator(models_path)
        self.monitor_log_path = Path(__file__).parent / "model_monitor.log"

    def check_model_health(self, model_id: str) -> Dict:
        """
        檢查單個模型健康度

        Args:
            model_id: 模型 ID

        Returns:
            健康度字典
        """
        model = self.allocator.get_model_stats(model_id)

        if not model:
            return {
                "model_id": model_id,
                "status": "not_found",
                "healthy": False
            }

        health = model.get("health", {})
        stats = model.get("stats", {})

        # 檢查 rate limit
        rate_limit_until = health.get("rate_limit_until")
        is_rate_limited = False

        if rate_limit_until:
            rate_limit_time = datetime.fromisoformat(rate_limit_until.replace('Z', '+00:00'))
            if datetime.now(rate_limit_time.tzinfo) < rate_limit_time:
                is_rate_limited = True
            else:
                # 清除過期的 rate limit
                health["rate_limit_until"] = None
                health["status"] = "healthy"

        # 計算健康度指標
        total_requests = stats.get("total_requests", 0)
        success_rate = health.get("success_rate", 1.0)

        # 判斷是否健康
        is_healthy = (
            not is_rate_limited and
            health.get("active_tasks", 0) < model.get("concurrent_limit", 1) and
            success_rate > 0.8
        )

        return {
            "model_id": model_id,
            "status": health.get("status", "unknown"),
            "healthy": is_healthy,
            "active_tasks": health.get("active_tasks", 0),
            "concurrent_limit": model.get("concurrent_limit", 1),
            "success_rate": success_rate,
            "rate_limited": is_rate_limited,
            "rate_limit_until": rate_limit_until,
            "total_requests": total_requests
        }

    def get_all_models_health(self) -> List[Dict]:
        """
        獲取所有模型健康度

        Returns:
            模型健康度列表
        """
        models = self.allocator.get_model_stats()
        health_list = []

        for model_id in models.keys():
            health = self.check_model_health(model_id)
            health_list.append(health)

        return health_list

    def detect_rate_limit_pattern(self, model_id: str, window_minutes: int = 60) -> Dict:
        """
        檢測 rate limit 模式

        Args:
            model_id: 模型 ID
            window_minutes: 時間窗口（分鐘）

        Returns:
            模式分析結果
        """
        model = self.allocator.get_model_stats(model_id)

        if not model:
            return {
                "model_id": model_id,
                "has_pattern": False,
                "message": "模型不存在"
            }

        stats = model.get("stats", {})
        rate_limited_count = stats.get("rate_limited", 0)
        total_requests = stats.get("total_requests", 0)

        if total_requests == 0:
            return {
                "model_id": model_id,
                "has_pattern": False,
                "message": "沒有請求數據"
            }

        # 計算 rate limit 比例
        rate_limit_ratio = rate_limited_count / total_requests

        # 判斷是否有明顯模式
        has_pattern = rate_limit_ratio > 0.1  # 10% 以上請求被限流

        result = {
            "model_id": model_id,
            "has_pattern": has_pattern,
            "rate_limit_ratio": rate_limit_ratio,
            "rate_limited_count": rate_limited_count,
            "total_requests": total_requests
        }

        if has_pattern:
            result["message"] = f"⚠️ 發現 rate limit 模式：{rate_limited_count}/{total_requests} ({rate_limit_ratio:.1%}) 請求被限流"
        else:
            result["message"] = f"✅ 沒有明顯的 rate limit 模式"

        return result

    def get_model_utilization(self) -> Dict:
        """
        获取模型利用率

        Returns:
            利用率字典
        """
        models = self.allocator.get_model_stats()
        utilization = {}

        for model_id, model in models.items():
            health = model.get("health", {})
            active = health.get("active_tasks", 0)
            limit = model.get("concurrent_limit", 1)

            if limit > 0:
                ratio = active / limit
            else:
                ratio = 0.0

            utilization[model_id] = {
                "active": active,
                "limit": limit,
                "ratio": ratio,
                "percentage": ratio * 100
            }

        return utilization

    def get_system_recommendations(self) -> List[str]:
        """
        獲取系統建議

        Returns:
            建議列表
        """
        recommendations = []

        # 檢查所有模型健康度
        health_list = self.get_all_models_health()

        # 檢查是否有健康模型
        healthy_models = [h for h in health_list if h["healthy"]]
        rate_limited_models = [h for h in health_list if h["rate_limited"]]

        # 建議 1：rate limit
        if rate_limited_models:
            for model in rate_limited_models:
                recommendations.append(
                    f"⚠️ 模型 {model['model_id']} 被 rate limit，冷卻直到 {model['rate_limit_until']}"
                )

        # 建議 2：利用率
        utilization = self.get_model_utilization()
        for model_id, util in utilization.items():
            if util["ratio"] > 0.8:
                recommendations.append(
                    f"📈 模型 {model_id} 利用率較高 ({util['percentage']:.1f}%)，考慮增加並發限制或啟用備用模型"
                )

        # 建議 3：啟用備用模型
        enabled_count = sum(1 for m in health_list if m["healthy"])
        if enabled_count < 2 and len(health_list) > 1:
            recommendations.append(
                "💡 建議啟用更多模型以提高可用性和負載平衡"
            )

        # 建議 4：檢測 rate limit 模式
        for model in health_list:
            pattern = self.detect_rate_limit_pattern(model["model_id"])
            if pattern["has_pattern"]:
                recommendations.append(
                    f"🔍 模型 {model['model_id']} 有 rate limit 模式，建議：\n"
                    f"   - 降低並發限制\n"
                    f"   - 增加請求間隔\n"
                    f"   - 啟用備用模型分散負載"
                )

        return recommendations

    def log_status(self):
        """記錄當前狀態到日誌"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(self.monitor_log_path, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"📊 Model Monitor Status - {timestamp}\n")
            f.write(f"{'='*60}\n")

            # 系統狀態
            system_status = self.allocator.get_system_status()
            f.write(f"\n系統統計：\n")
            f.write(f"  總請求：{system_status['total_requests']}\n")
            f.write(f"  成功：{system_status['successful']}\n")
            f.write(f"  失敗：{system_status['failed']}\n")
            f.write(f"  Rate limit：{system_status['rate_limited']}\n")
            f.write(f"  成功率：{system_status['success_rate']:.2%}\n")
            f.write(f"  活躍任務：{system_status['active_tasks']}\n")
            f.write(f"  啟用模型：{system_status['enabled_models']}/{system_status['total_models']}\n")

            # 模型健康度
            health_list = self.get_all_models_health()
            f.write(f"\n模型健康度：\n")
            for health in health_list:
                status_icon = "✅" if health["healthy"] else "❌"
                f.write(f"  {status_icon} {health['model_id']}\n")
                f.write(f"      狀態：{health['status']}\n")
                f.write(f"      活躍：{health['active_tasks']}/{health['concurrent_limit']}\n")
                f.write(f"      成功率：{health['success_rate']:.2%}\n")
                if health['rate_limited']:
                    f.write(f"      ⚠️ Rate limit 直到：{health['rate_limit_until']}\n")

            # 利用率
            utilization = self.get_model_utilization()
            f.write(f"\n模型利用率：\n")
            for model_id, util in utilization.items():
                f.write(f"  {model_id}：{util['active']}/{util['limit']} ({util['percentage']:.1f}%)\n")

            # 建議
            recommendations = self.get_system_recommendations()
            if recommendations:
                f.write(f"\n系統建議：\n")
                for rec in recommendations:
                    f.write(f"  {rec}\n")
            else:
                f.write(f"\n✅ 系統運行良好，沒有特別建議\n")

        logger.info(f"✅ 狀態已記錄到 {self.monitor_log_path}")


if __name__ == "__main__":
    # 測試模型監控器
    monitor = ModelMonitor()

    print("\n=== 模型監控器測試 ===\n")

    print("1. 獲取所有模型健康度：")
    health_list = monitor.get_all_models_health()
    for health in health_list:
        print(f"   {health}\n")

    print("2. 獲取系統統計：")
    system_status = monitor.allocator.get_system_status()
    print(f"   {json.dumps(system_status, indent=2)}\n")

    print("3. 檢測 rate limit 模式：")
    pattern = monitor.detect_rate_limit_pattern("zai/glm-4.7")
    print(f"   {json.dumps(pattern, indent=2)}\n")

    print("4. 獲取模型利用率：")
    utilization = monitor.get_model_utilization()
    print(f"   {json.dumps(utilization, indent=2)}\n")

    print("5. 獲取系統建議：")
    recommendations = monitor.get_system_recommendations()
    for rec in recommendations:
        print(f"   {rec}\n")

    print("6. 記錄狀態：")
    monitor.log_status()
