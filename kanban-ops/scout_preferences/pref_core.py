"""
Scout 偏好系統核心模塊

提供基礎數據結構和工具函數
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum
import json
import math


class InteractionType(Enum):
    """交互類型枚舉"""
    CLICK = "click"
    SAVE = "save"
    SHARE = "share"
    POSITIVE_FEEDBACK = "positive_feedback"
    NEGATIVE_FEEDBACK = "negative_feedback"
    IGNORE = "ignore"
    DWELL_TIME = "dwell_time"


class TrendDirection(Enum):
    """趨勢方向枚舉"""
    RISING = "rising"
    STABLE = "stable"
    DECLINING = "declining"


@dataclass
class TopicTrend:
    """主題趨勢"""
    direction: TrendDirection
    slope: float
    last_change: datetime
    confidence: float = 0.5


@dataclass
class TopicDecay:
    """主題衰減"""
    half_life: float
    last_interaction: datetime
    decay_factor: float


@dataclass
class TopicAttributes:
    """主題屬性"""
    depth_preference: float = 0.5
    recency_preference: float = 0.5
    source_preference: Dict[str, float] = field(default_factory=dict)


@dataclass
class InteractionRecord:
    """交互記錄"""
    timestamp: datetime
    weight: float
    interaction_type: str
    context: Dict = field(default_factory=dict)


@dataclass
class TopicPreference:
    """主題偏好"""
    topic_id: str
    aliases: List[str] = field(default_factory=list)
    weight: float = 0.1
    confidence: float = 0.1
    trend: Optional[TopicTrend] = None
    decay: Optional[TopicDecay] = None
    attributes: TopicAttributes = field(default_factory=TopicAttributes)
    history: List[InteractionRecord] = field(default_factory=list)


@dataclass
class GlobalSettings:
    """全局設置"""
    exploration_rate: float = 0.15
    decay_half_life: float = 168.0
    ema_alpha: float = 0.3
    confidence_growth_rate: float = 0.1
    min_confidence_threshold: float = 0.3


@dataclass
class BiasMetrics:
    """偏差指標"""
    topic_diversity: float = 0.0
    recency_bias: float = 0.5
    exploration_bias: float = 0.15


@dataclass
class PerformanceMetrics:
    """性能指標"""
    click_through_rate: float = 0.0
    satisfaction_score: float = 0.5
    diversity_score: float = 0.0
    last_calculated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class PreferenceMetadata:
    """偏好元數據"""
    user_id: str
    created_at: datetime
    last_updated: datetime
    total_interactions: int = 0
    confidence_level: float = 0.0


@dataclass
class Preferences:
    """偏好數據結構"""
    version: str = "2.0"
    metadata: Optional[PreferenceMetadata] = None
    topics: Dict[str, TopicPreference] = field(default_factory=dict)
    global_settings: GlobalSettings = field(default_factory=GlobalSettings)
    biases: BiasMetrics = field(default_factory=BiasMetrics)
    performance_metrics: PerformanceMetrics = field(default_factory=PerformanceMetrics)
    
    def to_dict(self) -> Dict:
        """轉換為字典"""
        return {
            "version": self.version,
            "metadata": {
                "userId": self.metadata.user_id,
                "createdAt": self.metadata.created_at.isoformat(),
                "lastUpdated": self.metadata.last_updated.isoformat(),
                "totalInteractions": self.metadata.total_interactions,
                "confidenceLevel": self.metadata.confidence_level
            } if self.metadata else None,
            "topics": {
                tid: {
                    "topicId": t.topic_id,
                    "aliases": t.aliases,
                    "weight": t.weight,
                    "confidence": t.confidence,
                    "trend": {
                        "direction": t.trend.direction.value,
                        "slope": t.trend.slope,
                        "lastChange": t.trend.last_change.isoformat(),
                        "confidence": t.trend.confidence
                    } if t.trend else None,
                    "decay": {
                        "halflife": t.decay.half_life,
                        "lastInteraction": t.decay.last_interaction.isoformat(),
                        "decayFactor": t.decay.decay_factor
                    } if t.decay else None,
                    "attributes": {
                        "depthPreference": t.attributes.depth_preference,
                        "recencyPreference": t.attributes.recency_preference,
                        "sourcePreference": t.attributes.source_preference
                    },
                    "history": [
                        {
                            "timestamp": h.timestamp.isoformat(),
                            "weight": h.weight,
                            "interactionType": h.interaction_type,
                            "context": h.context
                        }
                        for h in t.history
                    ]
                }
                for tid, t in self.topics.items()
            },
            "globalSettings": {
                "explorationRate": self.global_settings.exploration_rate,
                "decayHalfLife": self.global_settings.decay_half_life,
                "emaAlpha": self.global_settings.ema_alpha,
                "confidenceGrowthRate": self.global_settings.confidence_growth_rate,
                "minConfidenceThreshold": self.global_settings.min_confidence_threshold
            },
            "biases": {
                "topicDiversity": self.biases.topic_diversity,
                "recencyBias": self.biases.recency_bias,
                "explorationBias": self.biases.exploration_bias
            },
            "performanceMetrics": {
                "clickThroughRate": self.performance_metrics.click_through_rate,
                "satisfactionScore": self.performance_metrics.satisfaction_score,
                "diversityScore": self.performance_metrics.diversity_score,
                "lastCalculated": self.performance_metrics.last_calculated.isoformat()
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Preferences':
        """從字典創建"""
        prefs = cls()
        
        # Version
        prefs.version = data.get("version", "2.0")
        
        # Metadata
        if "metadata" in data:
            meta = data["metadata"]
            prefs.metadata = PreferenceMetadata(
                user_id=meta["userId"],
                created_at=datetime.fromisoformat(meta["createdAt"]),
                last_updated=datetime.fromisoformat(meta["lastUpdated"]),
                total_interactions=meta.get("totalInteractions", 0),
                confidence_level=meta.get("confidenceLevel", 0.0)
            )
        
        # Topics
        if "topics" in data:
            for tid, tdata in data["topics"].items():
                topic = TopicPreference(
                    topic_id=tdata["topicId"],
                    aliases=tdata.get("aliases", []),
                    weight=tdata["weight"],
                    confidence=tdata["confidence"]
                )
                
                # Trend
                if "trend" in tdata and tdata["trend"]:
                    topic.trend = TopicTrend(
                        direction=TrendDirection(tdata["trend"]["direction"]),
                        slope=tdata["trend"]["slope"],
                        last_change=datetime.fromisoformat(tdata["trend"]["lastChange"]),
                        confidence=tdata["trend"].get("confidence", 0.5)
                    )
                
                # Decay
                if "decay" in tdata and tdata["decay"]:
                    topic.decay = TopicDecay(
                        half_life=tdata["decay"]["halflife"],
                        last_interaction=datetime.fromisoformat(tdata["decay"]["lastInteraction"]),
                        decay_factor=tdata["decay"]["decayFactor"]
                    )
                
                # Attributes
                if "attributes" in tdata:
                    attrs = tdata["attributes"]
                    topic.attributes = TopicAttributes(
                        depth_preference=attrs.get("depthPreference", 0.5),
                        recency_preference=attrs.get("recencyPreference", 0.5),
                        source_preference=attrs.get("sourcePreference", {})
                    )
                
                # History
                if "history" in tdata:
                    topic.history = [
                        InteractionRecord(
                            timestamp=datetime.fromisoformat(h["timestamp"]),
                            weight=h["weight"],
                            interaction_type=h["interactionType"],
                            context=h.get("context", {})
                        )
                        for h in tdata["history"]
                    ]
                
                prefs.topics[tid] = topic
        
        # Global Settings
        if "globalSettings" in data:
            gs = data["globalSettings"]
            prefs.global_settings = GlobalSettings(
                exploration_rate=gs.get("explorationRate", 0.15),
                decay_half_life=gs.get("decayHalfLife", 168.0),
                ema_alpha=gs.get("emaAlpha", 0.3),
                confidence_growth_rate=gs.get("confidenceGrowthRate", 0.1),
                min_confidence_threshold=gs.get("minConfidenceThreshold", 0.3)
            )
        
        # Biases
        if "biases" in data:
            b = data["biases"]
            prefs.biases = BiasMetrics(
                topic_diversity=b.get("topicDiversity", 0.0),
                recency_bias=b.get("recencyBias", 0.5),
                exploration_bias=b.get("explorationBias", 0.15)
            )
        
        # Performance Metrics
        if "performanceMetrics" in data:
            pm = data["performanceMetrics"]
            prefs.performance_metrics = PerformanceMetrics(
                click_through_rate=pm.get("clickThroughRate", 0.0),
                satisfaction_score=pm.get("satisfactionScore", 0.5),
                diversity_score=pm.get("diversityScore", 0.0),
                last_calculated=datetime.fromisoformat(pm.get("lastCalculated", datetime.now(timezone.utc).isoformat()))
            )
        
        return prefs


if __name__ == "__main__":
    # 測試數據結構
    prefs = Preferences()
    prefs.metadata = PreferenceMetadata(
        user_id="test_user",
        created_at=datetime.now(timezone.utc),
        last_updated=datetime.now(timezone.utc)
    )
    
    # 添加測試主題
    topic = TopicPreference(
        topic_id="machine_learning",
        weight=0.8,
        confidence=0.7
    )
    topic.history.append(
        InteractionRecord(
            timestamp=datetime.now(timezone.utc),
            weight=0.8,
            interaction_type="click",
            context={}
        )
    )
    prefs.topics["machine_learning"] = topic
    
    # 轉換為字典
    data = prefs.to_dict()
    print("✅ 核心數據結構測試通過")
    print(f"版本: {data['version']}")
    print(f"主題數: {len(data['topics'])}")
