#!/usr/bin/env python3
"""
Model Allocator - 多模型分配器
根據任務類型、模型健康度、並發限制分配任務到最佳模型
"""

import json
import logging
from datetime import datetime
from typing import Optional, Dict, List
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


class ModelAllocator:
    """模型分配器"""

    def __init__(self, models_path: str = None):
        """初始化模型分配器"""
        if models_path is None:
            models_path = Path(__file__).parent / "models.json"
        self.models_path = models_path
        self.models_config = self._load_models()

    def _load_models(self) -> dict:
        """加載模型配置"""
        try:
            with open(self.models_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"✅ 模型配置已加載：{len(config['models'])} 個模型")
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

    def get_model_for_agent(self, agent_id: str, priority: str = "default") -> Optional[str]:
        """
        為指定代理選擇最佳模型

        Args:
            agent_id: 代理 ID（research, analyst, creative 等）
            priority: 優先級（default, fast, high_quality）

        Returns:
            模型 ID，如果沒有可用模型則返回 None
        """
        # 獲取代理的模型映射
        agent_mapping = self.models_config.get("agent_model_mapping", {}).get(agent_id, {})

        if not agent_mapping:
            logger.warning(f"⚠️  代理 {agent_id} 沒有模型映射配置")
            return None

        # 根據優先級調整模型列表
        if priority == "high_quality":
            # 高品質優先：使用 default，如果不可用則返回 None
            model_id = agent_mapping.get("default")
            if self._is_model_available(model_id):
                return model_id
            logger.warning(f"⚠️  高品質優先但 {model_id} 不可用")
            return None

        elif priority == "fast":
            # 快速優先：先嘗試 fallback 中的快速模型
            fallback_models = agent_mapping.get("fallback", [])
            for model_id in fallback_models:
                if self._is_model_available(model_id):
                    logger.info(f"🚀 快速優先：選擇 {model_id}")
                    return model_id
            # 如果沒有可用的 fallback，使用 default
            model_id = agent_mapping.get("default")
            if self._is_model_available(model_id):
                return model_id
            return None

        else:
            # 默認策略：先 default，後 fallback
            model_id = agent_mapping.get("default")
            if self._is_model_available(model_id):
                return model_id

            # 嘗試 fallback 模型
            fallback_models = agent_mapping.get("fallback", [])
            for fallback_model_id in fallback_models:
                if self._is_model_available(fallback_model_id):
                    logger.info(f"🔄 默認模型不可用，使用備用：{fallback_model_id}")
                    return fallback_model_id

            return None

    def _is_model_available(self, model_id: str) -> bool:
        """
        檢查模型是否可用

        檢查條件：
        1. 模型已啟用
        2. 沒有 rate limit
        3. 未超過並發限制

        Args:
            model_id: 模型 ID

        Returns:
            True 如果可用，False 否則
        """
        model = self.models_config["models"].get(model_id)

        if not model:
            logger.warning(f"⚠️  模型 {model_id} 不存在")
            return False

        # 檢查是否啟用
        if not model.get("enabled", True):
            logger.debug(f"🚫 模型 {model_id} 未啟用")
            return False

        # 檢查是否被 rate limit
        health = model.get("health", {})
        rate_limit_until = health.get("rate_limit_until")

        if rate_limit_until:
            rate_limit_time = datetime.fromisoformat(rate_limit_until.replace('Z', '+00:00'))
            if datetime.now(rate_limit_time.tzinfo) < rate_limit_time:
                logger.debug(f"🚫 模型 {model_id} 被 rate limit 直到 {rate_limit_until}")
                return False
            else:
                # rate limit 已過期，清除
                health["rate_limit_until"] = None
                health["status"] = "healthy"
                logger.info(f"✅ 模型 {model_id} 的 rate limit 已過期，恢復可用")

        # 檢查並發限制
        active_tasks = health.get("active_tasks", 0)
        concurrent_limit = model.get("concurrent_limit", 1)

        if active_tasks >= concurrent_limit:
            logger.debug(f"🚫 模型 {model_id} 已達並發限制 ({active_tasks}/{concurrent_limit})")
            return False

        return True

    def allocate_task(self, agent_id: str, priority: str = "default") -> Optional[Dict]:
        """
        分配任務到可用模型

        Args:
            agent_id: 代理 ID
            priority: 優先級

        Returns:
            包含模型信息的字典，如果沒有可用模型則返回 None
        """
        model_id = self.get_model_for_agent(agent_id, priority)

        if not model_id:
            return None

        model = self.models_config["models"][model_id]

        # 增加活躍任務計數
        model["health"]["active_tasks"] += 1

        # 記錄統計
        model["stats"]["total_requests"] += 1

        # 保存配置
        self._save_models()

        logger.info(f"✅ 任務分配：{agent_id} → {model_id}")

        return {
            "model_id": model_id,
            "agent_id": agent_id,
            "quality": model.get("quality"),
            "speed": model.get("speed"),
            "priority": priority
        }

    def complete_task(self, model_id: str, success: bool = True, rate_limited: bool = False):
        """
        標記任務完成，更新模型統計

        Args:
            model_id: 模型 ID
            success: 是否成功
            rate_limited: 是否觸發 rate limit
        """
        if model_id not in self.models_config["models"]:
            logger.warning(f"⚠️  模型 {model_id} 不存在")
            return

        model = self.models_config["models"][model_id]

        # 減少活躍任務計數
        if model["health"]["active_tasks"] > 0:
            model["health"]["active_tasks"] -= 1

        # 更新統計
        if success:
            model["stats"]["successful"] += 1
        else:
            model["stats"]["failed"] += 1

        if rate_limited:
            model["stats"]["rate_limited"] += 1

        # 重新計算成功率
        total = model["stats"]["total_requests"]
        if total > 0:
            success_rate = model["stats"]["successful"] / total
            model["health"]["success_rate"] = success_rate

        # 保存配置
        self._save_models()

        logger.info(f"✅ 任務完成：{model_id}，成功={success}, rate_limited={rate_limited}")

    def mark_rate_limit(self, model_id: str, cooldown_minutes: int = 30):
        """
        標記模型被 rate limit，設置冷卻時間

        Args:
            model_id: 模型 ID
            cooldown_minutes: 冷卻時間（分鐘）
        """
        if model_id not in self.models_config["models"]:
            logger.warning(f"⚠️  模型 {model_id} 不存在")
            return

        model = self.models_config["models"][model_id]

        # 計算冷卻結束時間
        from datetime import timedelta
        cooldown_end = datetime.now() + timedelta(minutes=cooldown_minutes)
        model["health"]["rate_limit_until"] = cooldown_end.isoformat()
        model["health"]["status"] = "rate_limited"

        # 保存配置
        self._save_models()

        logger.warning(f"⚠️  模型 {model_id} 被 rate limit，冷卻直到 {cooldown_end}")

    def get_model_stats(self, model_id: str = None) -> dict:
        """
        獲取模型統計信息

        Args:
            model_id: 模型 ID，如果為 None 則返回所有模型

        Returns:
            模型統計信息字典
        """
        if model_id:
            return self.models_config["models"].get(model_id, {})
        else:
            return self.models_config["models"]

    def get_system_status(self) -> dict:
        """
        獲取系統狀態概覽

        Returns:
            系統狀態字典
        """
        total_requests = 0
        successful = 0
        failed = 0
        rate_limited = 0
        active_tasks = 0

        for model_id, model in self.models_config["models"].items():
            stats = model.get("stats", {})
            health = model.get("health", {})

            total_requests += stats.get("total_requests", 0)
            successful += stats.get("successful", 0)
            failed += stats.get("failed", 0)
            rate_limited += stats.get("rate_limited", 0)
            active_tasks += health.get("active_tasks", 0)

        success_rate = successful / total_requests if total_requests > 0 else 0.0

        return {
            "total_requests": total_requests,
            "successful": successful,
            "failed": failed,
            "rate_limited": rate_limited,
            "active_tasks": active_tasks,
            "success_rate": success_rate,
            "enabled_models": sum(1 for m in self.models_config["models"].values() if m.get("enabled", True)),
            "total_models": len(self.models_config["models"])
        }


if __name__ == "__main__":
    # 測試模型分配器
    allocator = ModelAllocator()

    print("\n=== 模型分配器測試 ===\n")

    # 測試分配
    print("1. 為 analyst 分配任務（高品質優先）：")
    result = allocator.allocate_task("analyst", priority="high_quality")
    print(f"   結果：{result}\n")

    print("2. 為 research 分配任務（默認）：")
    result = allocator.allocate_task("research")
    print(f"   結果：{result}\n")

    print("3. 標記任務完成：")
    allocator.complete_task("zai/glm-4.7", success=True)

    print("4. 獲取系統狀態：")
    status = allocator.get_system_status()
    print(f"   狀態：{json.dumps(status, indent=2)}\n")

    print("5. 標記 rate limit：")
    allocator.mark_rate_limit("zai/glm-4.7", cooldown_minutes=30)

    print("6. 再次嘗試分配（應該返回 None）：")
    result = allocator.allocate_task("analyst", priority="high_quality")
    print(f"   結果：{result}\n")
