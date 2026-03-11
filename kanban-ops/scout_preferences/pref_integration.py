"""
系統集成模塊

提供與 Scout Agent、Kanban、監控系統的集成接口
"""

from typing import Dict, List, Optional, Set
from datetime import datetime, timezone, timedelta
import json

import sys
sys.path.insert(0, '/Users/charlie/.openclaw/workspace/kanban-ops/scout_preferences')
import pref_core
from pref_core import (
    Preferences,
    TopicPreference,
    InteractionRecord,
    TopicDecay
)
import pref_algorithms as algorithms


class ScoutPreferenceManager:
    """Scout Agent 的偏好管理器"""
    
    def __init__(self, preferences_path: str):
        self.preferences_path = preferences_path
        self.preferences = self._load_preferences()
        self.recent_topics = set()
        self.recent_window = timedelta(hours=24)
    
    def record_interaction(
        self,
        query: str,
        result: Optional[Dict],
        interaction_type: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        記錄用戶交互
        
        Args:
            query: 搜尋查詢
            result: 交互的結果
            interaction_type: 交互類型
            metadata: 額外元數據
        """
        # 提取主題
        query_topics = algorithms.extract_topics_from_query(query)
        result_topics = algorithms.extract_topics_from_result(result) if result else []
        all_topics = query_topics + result_topics
        
        if not all_topics:
            return
        
        # 更新每個主題
        for topic_id, relevance in all_topics:
            self._update_topic(
                topic_id,
                relevance,
                interaction_type,
                metadata
            )
            
            # 更新最近主題
            self.recent_topics.add(topic_id)
        
        # 更新元數據
        self.preferences.metadata.last_updated = datetime.now(timezone.utc)
        self.preferences.metadata.total_interactions += 1
        
        # 更新整體置信度
        self._update_confidence_level()
        
        # 保存
        self._save_preferences()
    
    def _update_topic(
        self,
        topic_id: str,
        relevance: float,
        interaction_type: str,
        metadata: Optional[Dict]
    ) -> None:
        """更新單個主題"""
        # 確保主題存在
        if topic_id not in self.preferences.topics:
            self._initialize_topic(topic_id)
        
        topic = self.preferences.topics[topic_id]
        
        # 獲取交互權重
        signal_weight = algorithms.get_interaction_weight(interaction_type)
        signal = signal_weight * relevance
        
        # 使用 EMA 更新權重
        topic.weight = algorithms.update_ema(
            topic.weight,
            signal,
            self.preferences.global_settings.ema_alpha
        )
        
        # 更新置信度
        topic.confidence = algorithms.update_confidence(
            topic.confidence,
            len(topic.history),
            relevance,
            self.preferences.global_settings.confidence_growth_rate
        )
        
        # 記錄歷史
        record = InteractionRecord(
            timestamp=datetime.now(timezone.utc),
            weight=topic.weight,
            interaction_type=interaction_type,
            context=metadata or {}
        )
        topic.history.append(record)
        
        # 限制歷史記錄長度
        if len(topic.history) > 100:
            topic.history = topic.history[-100:]
        
        # 更新衰減
        topic.decay = TopicDecay(
            half_life=self.preferences.global_settings.decay_half_life,
            last_interaction=datetime.now(timezone.utc),
            decay_factor=1.0
        )
    
    def get_ranked_results(
        self,
        query: str,
        raw_results: List[Dict],
        top_k: Optional[int] = None
    ) -> List[Dict]:
        """
        獲取排序後的搜尋結果
        
        Args:
            query: 搜尋查詢
            raw_results: 原始搜尋結果
            top_k: 返回前 k 個結果
            
        Returns:
            排序後的結果列表
        """
        # 清理過期的最近主題
        self._cleanup_recent_topics()
        
        # 對每個結果打分
        scored = []
        for result in raw_results:
            components = algorithms.score_result(
                result,
                self.preferences.topics,
                self.recent_topics,
                self.preferences.global_settings.exploration_rate
            )
            
            scored.append({
                **result,
                "_preference_score": components.final_score,
                "_affinity": components.affinity,
                "_novelty": components.novelty,
                "_exploration_bonus": components.exploration_bonus
            })
        
        # 按分數降序排序
        scored.sort(key=lambda x: x["_preference_score"], reverse=True)
        
        # 截取前 k 個
        if top_k is not None:
            scored = scored[:top_k]
        
        return scored
    
    def apply_time_decay(self) -> None:
        """應用時間衰減到所有主題"""
        current_time = datetime.now(timezone.utc)
        half_life = self.preferences.global_settings.decay_half_life
        
        for topic in self.preferences.topics.values():
            if topic.decay is None:
                continue
            
            last_interaction = topic.decay.last_interaction
            
            # 應用衰減
            topic.weight, decay_factor = algorithms.apply_time_decay(
                topic.weight,
                last_interaction,
                half_life,
                current_time
            )
            
            # 更新衰減因子
            topic.decay.decay_factor = decay_factor
            topic.decay.last_interaction = current_time
        
        self.preferences.metadata.last_updated = current_time
        self._save_preferences()
    
    def analyze_trends(self) -> Dict[str, any]:
        """分析所有主題的趨勢"""
        trends = {}
        
        for topic_id, topic in self.preferences.topics.items():
            history_data = [
                {
                    "timestamp": h.timestamp.isoformat(),
                    "weight": h.weight
                }
                for h in topic.history
            ]
            
            if len(history_data) >= 3:
                trend_info = algorithms.analyze_trend(history_data)
                trends[topic_id] = trend_info
        
        return trends
    
    def correct_biases(self) -> None:
        """檢測並校正偏差"""
        # 檢測過度專注
        if algorithms.detect_overfocus(self.preferences.topics):
            self.preferences.topics = algorithms.correct_bias(
                self.preferences.topics,
                self.preferences.global_settings.exploration_rate,
                strategy="boost_low_weight"
            )
        
        # 更新偏差指標
        self._update_bias_metrics()
        
        self._save_preferences()
    
    def get_preference_summary(self) -> Dict:
        """獲取偏好摘要"""
        sorted_topics = sorted(
            self.preferences.topics.items(),
            key=lambda x: x[1].weight,
            reverse=True
        )[:10]
        
        return {
            "top_topics": [
                {
                    "id": tid,
                    "weight": t.weight,
                    "confidence": t.confidence,
                    "trend": t.trend.direction.value if t.trend else "stable"
                }
                for tid, t in sorted_topics
            ],
            "diversity": self.preferences.biases.topic_diversity,
            "exploration_rate": self.preferences.global_settings.exploration_rate,
            "total_interactions": self.preferences.metadata.total_interactions
        }
    
    def _initialize_topic(self, topic_id: str) -> None:
        """初始化新主題"""
        self.preferences.topics[topic_id] = TopicPreference(
            topic_id=topic_id,
            weight=0.1,
            confidence=0.1
        )
    
    def _update_confidence_level(self) -> None:
        """更新整體置信度"""
        if not self.preferences.topics:
            return
        
        confidences = [t.confidence for t in self.preferences.topics.values()]
        self.preferences.metadata.confidence_level = sum(confidences) / len(confidences)
    
    def _cleanup_recent_topics(self) -> None:
        """清理過期的最近主題"""
        if len(self.recent_topics) > 50:
            self.recent_topics = set(list(self.recent_topics)[-50:])
    
    def _update_bias_metrics(self) -> None:
        """更新偏差指標"""
        diversity = algorithms.calculate_diversity_score(self.preferences.topics)
        
        self.preferences.biases.topic_diversity = diversity
        self.preferences.biases.exploration_bias = self.preferences.global_settings.exploration_rate
        self.preferences.performance_metrics.diversity_score = diversity
        self.preferences.performance_metrics.last_calculated = datetime.now(timezone.utc)
    
    def _load_preferences(self) -> Preferences:
        """加載偏好數據"""
        try:
            with open(self.preferences_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return Preferences.from_dict(data)
        except FileNotFoundError:
            return self._create_default_preferences()
        except Exception as e:
            print(f"⚠️ 加載偏好失敗: {e}")
            return self._create_default_preferences()
    
    def _save_preferences(self) -> None:
        """保存偏好數據"""
        try:
            with open(self.preferences_path, 'w', encoding='utf-8') as f:
                json.dump(self.preferences.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ 保存偏好失敗: {e}")
    
    def _create_default_preferences(self) -> Preferences:
        """創建默認偏好結構"""
        prefs = Preferences()
        prefs.metadata = PreferenceMetadata(
            user_id="default",
            created_at=datetime.now(timezone.utc),
            last_updated=datetime.now(timezone.utc)
        )
        return prefs


if __name__ == "__main__":
    import pref_core
    
    print("測試 Scout 偏好管理器...\n")
    
    # 創建測試文件路徑
    test_path = "/tmp/test_preferences.json"
    
    # 初始化管理器
    manager = ScoutPreferenceManager(test_path)
    
    # 記錄一些交互
    print("記錄交互...")
    manager.record_interaction(
        query="machine learning transformer",
        result={"title": "Attention Is All You Need", "snippet": "Transformer architecture"},
        interaction_type="click"
    )
    
    manager.record_interaction(
        query="productivity tips",
        result={"title": "How to be productive", "snippet": "Time management strategies"},
        interaction_type="save"
    )
    
    # 測試排序結果
    print("\n測試結果排序...")
    raw_results = [
        {"title": "Machine Learning Tutorial", "relevance": 0.85},
        {"title": "Productivity Hacks", "relevance": 0.75},
        {"title": "Python Programming", "relevance": 0.70}
    ]
    
    ranked = manager.get_ranked_results("machine learning", raw_results, top_k=5)
    for i, r in enumerate(ranked, 1):
        print(f"{i}. {r['title'][:30]:30} | 分數: {r['_preference_score']:.3f} | 親和度: {r['_affinity']:.3f}")
    
    # 測試時間衰減
    print("\n測試時間衰減...")
    manager.apply_time_decay()
    print("✅ 時間衰減已應用")
    
    # 測試趨勢分析
    print("\n測試趨勢分析...")
    trends = manager.analyze_trends()
    print(f"分析的主題數: {len(trends)}")
    
    # 測試偏差校正
    print("\n測試偏差校正...")
    manager.correct_biases()
    print("✅ 偏差校正已完成")
    
    # 獲取偏好摘要
    print("\n偏好摘要:")
    summary = manager.get_preference_summary()
    print(f"  主題數: {len(summary['top_topics'])}")
    print(f"  多樣性: {summary['diversity']:.3f}")
    print(f"  探索率: {summary['exploration_rate']:.1%}")
    print(f"  總交互: {summary['total_interactions']}")
    
    print("\n🎉 Scout 偏好管理器測試通過！")
    
    # 清理測試文件
    import os
    if os.path.exists(test_path):
        os.remove(test_path)
