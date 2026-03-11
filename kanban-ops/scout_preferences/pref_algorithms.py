"""
偏好算法模塊

包含所有核心算法：EMA、時間衰減、趨勢分析、偏差校正、打分
"""

import math
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass

import sys
sys.path.insert(0, '/Users/charlie/.openclaw/workspace/kanban-ops/scout_preferences')
from pref_core import (
    TopicPreference,
    TrendDirection,
    InteractionType,
    TopicTrend,
    TopicDecay,
    InteractionRecord
)


# ========== EMA 算法 ==========

def update_ema(
    current_weight: float,
    signal: float,
    alpha: float = 0.3
) -> float:
    """
    使用指數移動平均更新權重
    
    Args:
        current_weight: 當前權重
        signal: 新信號值
        alpha: 平滑因子 (0-1)
        
    Returns:
        更新後的權重
    """
    return alpha * signal + (1 - alpha) * current_weight


def ema_batch_update(
    weights: List[float],
    signals: List[float],
    alpha: float = 0.3
) -> List[float]:
    """
    批量 EMA 更新
    
    Args:
        weights: 當前權重列表
        signals: 信號值列表
        alpha: 平滑因子
        
    Returns:
        更新後的權重列表
    """
    return [update_ema(w, s, alpha) for w, s in zip(weights, signals)]


# ========== 時間衰減算法 ==========

def apply_time_decay(
    weight: float,
    last_interaction: datetime,
    half_life_hours: float = 168,
    current_time: Optional[datetime] = None
) -> Tuple[float, float]:
    """
    應用時間衰減
    
    Args:
        weight: 當前權重
        last_interaction: 最後交互時間
        half_life_hours: 衰減半衰期（小時）
        current_time: 當前時間（默認為現在）
        
    Returns:
        (衰減後的權重, 衰減因子)
    """
    if current_time is None:
        current_time = datetime.now(timezone.utc)
    
    time_elapsed_hours = (current_time - last_interaction).total_seconds() / 3600
    decay_factor = 0.5 ** (time_elapsed_hours / half_life_hours)
    
    return weight * decay_factor, decay_factor


# ========== 置信度校準 ==========

def update_confidence(
    current_confidence: float,
    interaction_count: int,
    interaction_quality: float,
    growth_rate: float = 0.1
) -> float:
    """
    更新偏好置信度
    
    Args:
        current_confidence: 當前置信度
        interaction_count: 交互次數
        interaction_quality: 交互質量 (0-1)
        growth_rate: 成長速率
        
    Returns:
        更新後的置信度
    """
    # 交互次數越多，置信度增長越慢
    count_factor = 1 / (1 + interaction_count * 0.1)
    
    # 質量越高，增長越快
    quality_factor = interaction_quality
    
    # 計算增長量
    growth = growth_rate * count_factor * quality_factor * (1 - current_confidence)
    
    return min(current_confidence + growth, 1.0)


def get_interaction_weight(interaction_type: str) -> float:
    """
    獲取交互類型對應的權重影響
    
    Args:
        interaction_type: 交互類型
        
    Returns:
        權重值
    """
    weights = {
        "click": 0.05,
        "save": 0.15,
        "share": 0.12,
        "positive_feedback": 0.20,
        "negative_feedback": -0.25,
        "ignore": -0.02,
        "dwell_time": 0.05
    }
    return weights.get(interaction_type, 0.0)


# ========== 趨勢分析 ==========

def analyze_trend(
    history: List[Dict],
    window_size: int = 5
) -> Dict[str, any]:
    """
    分析主題權重趨勢
    
    Args:
        history: 歷史交互記錄
        window_size: 分析窗口大小
        
    Returns:
        趨勢信息字典
    """
    if len(history) < window_size:
        return {
            "direction": TrendDirection.STABLE.value,
            "slope": 0.0,
            "confidence": 0.0
        }
    
    recent = [h["weight"] for h in history[-window_size:]]
    
    # 計算線性回歸斜率
    x = list(range(len(recent)))
    n = len(recent)
    
    sum_x = sum(x)
    sum_y = sum(recent)
    sum_xy = sum(xi * yi for xi, yi in zip(x, recent))
    sum_x2 = sum(xi * xi for xi in x)
    
    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
    
    # 分類趨勢方向
    if slope > 0.05:
        direction = TrendDirection.RISING
    elif slope < -0.05:
        direction = TrendDirection.DECLINING
    else:
        direction = TrendDirection.STABLE
    
    return {
        "direction": direction.value,
        "slope": slope,
        "confidence": min(len(history) / 10.0, 1.0),
        "lastChange": history[-1]["timestamp"]
    }


# ========== 偏差檢測與校正 ==========

def calculate_diversity_score(topics: Dict[str, TopicPreference]) -> float:
    """
    計算主題多樣性分數（使用熵）
    
    Args:
        topics: 主題偏好字典
        
    Returns:
        多樣性分數 (0-1)
    """
    weights = [t.weight for t in topics.values()]
    total = sum(weights)
    
    if total == 0:
        return 0.0
    
    normalized = [w / total for w in weights if w > 0]
    
    if not normalized:
        return 0.0
    
    # 計算熵
    entropy = -sum(p * math.log(p) for p in normalized)
    max_entropy = math.log(len(normalized)) if len(normalized) > 1 else 1.0
    
    return entropy / max_entropy if max_entropy > 0 else 0.0


def detect_overfocus(
    topics: Dict[str, TopicPreference],
    threshold: float = 0.7
) -> bool:
    """
    檢測是否過度專注於少數主題
    
    Args:
        topics: 主題偏好數據
        threshold: 閾值
        
    Returns:
        是否過度專注
    """
    if not topics:
        return False
    
    # 計算前 3 個主題的權重占比
    sorted_topics = sorted(
        topics.values(),
        key=lambda t: t.weight,
        reverse=True
    )
    
    top_n_weight = sum(t.weight for t in sorted_topics[:3])
    total_weight = sum(t.weight for t in sorted_topics)
    
    ratio = top_n_weight / total_weight if total_weight > 0 else 0
    
    return ratio > threshold


def correct_bias(
    topics: Dict[str, TopicPreference],
    exploration_rate: float,
    strategy: str = "boost_low_weight"
) -> Dict[str, TopicPreference]:
    """
    應用偏差校正
    
    Args:
        topics: 主題偏好數據
        exploration_rate: 探索率
        strategy: 校正策略
        
    Returns:
        校正後的主題數據
    """
    if not topics:
        return topics
    
    if strategy == "boost_low_weight":
        # 提升低權重主題
        for topic in topics.values():
            if topic.weight < 0.3:
                boost = exploration_rate * (0.3 - topic.weight)
                topic.weight += boost
    
    elif strategy == "decay_high_weight":
        # 衰減高權重主題
        for topic in topics.values():
            if topic.weight > 0.7:
                decay = exploration_rate * (topic.weight - 0.7) * 0.5
                topic.weight = max(0.0, topic.weight - decay)
    
    elif strategy == "normalize":
        # 歸一化所有權重
        total = sum(t.weight for t in topics.values())
        if total > 0:
            for topic in topics.values():
                topic.weight = topic.weight / total
    
    return topics


# ========== 打分算法 ==========

@dataclass
class ScoreComponents:
    """打分組件"""
    affinity: float = 0.0
    novelty: float = 0.0
    exploration_bonus: float = 0.0
    base_relevance: float = 0.0
    final_score: float = 0.0


def calculate_affinity(
    result_topics: List[Tuple[str, float]],
    preferences: Dict[str, TopicPreference],
    min_confidence: float = 0.3
) -> float:
    """
    計算結果與用戶偏好的親和度
    
    Args:
        result_topics: 結果相關的主題列表 [(topic_id, relevance), ...]
        preferences: 用戶偏好數據
        min_confidence: 最低置信度閾值
        
    Returns:
        親和度分數 (0-1)
    """
    if not result_topics:
        return 0.0
    
    total_affinity = 0.0
    total_relevance = 0.0
    
    for topic_id, relevance in result_topics:
        if topic_id in preferences:
            topic = preferences[topic_id]
            
            # 只使用高置信度的偏好
            if topic.confidence >= min_confidence:
                # 親和度 = 主題權重 * 主題相關性
                affinity = topic.weight * relevance
                total_affinity += affinity
                total_relevance += relevance
    
    # 歸一化
    return total_affinity / total_relevance if total_relevance > 0 else 0.0


def calculate_novelty(
    result_topics: List[Tuple[str, float]],
    preferences: Dict[str, TopicPreference],
    recent_topics: Set[str],
    time_window_hours: float = 24
) -> float:
    """
    計算結果的新穎性
    
    Args:
        result_topics: 結果相關的主題列表
        preferences: 用戶偏好數據
        recent_topics: 最近交互過的主題集合
        time_window_hours: 時間窗口（小時）
        
    Returns:
        新穎性分數 (0-1)
    """
    if not result_topics:
        return 0.5  # 中等新穎性
    
    novelty_scores = []
    
    for topic_id, relevance in result_topics:
        # 因素1: 主題是否在偏好中
        in_preferences = topic_id in preferences
        
        # 因素2: 主題是否最近交互過
        recently_viewed = topic_id in recent_topics
        
        # 因素3: 如果在偏好中，權重如何
        weight = preferences[topic_id].weight if in_preferences else 0.0
        
        # 計算新穎性
        if not in_preferences:
            # 新主題 = 高新穎性
            topic_novelty = 1.0
        elif recently_viewed:
            # 最近看過 = 低新穎性
            topic_novelty = 0.2
        else:
            # 認識但不常看 = 中等新穎性
            topic_novelty = 1.0 - weight
        
        novelty_scores.append(topic_novelty * relevance)
    
    # 加權平均
    total_relevance = sum(relevance for _, relevance in result_topics)
    return sum(novelty_scores) / total_relevance if total_relevance > 0 else 0.5


def calculate_exploration_bonus(
    novelty: float,
    diversity_score: float,
    exploration_rate: float,
    confidence_penalty: float = 0.0
) -> float:
    """
    計算探索獎勵
    
    Args:
        novelty: 新穎性分數
        diversity_score: 多樣性分數
        exploration_rate: 探索率
        confidence_penalty: 置信度懲罰
        
    Returns:
        探索獎勵分數
    """
    # 基礎獎勵：基於新穎性
    base_bonus = novelty * exploration_rate
    
    # 多樣性加成
    diversity_bonus = diversity_score * exploration_rate * 0.5
    
    # 置信度懲罰
    confidence_adjustment = 1.0 - confidence_penalty * 0.3
    
    return (base_bonus + diversity_bonus) * confidence_adjustment


def calculate_final_score(
    affinity: float,
    novelty: float,
    exploration_bonus: float,
    base_relevance: float,
    weights: Optional[Dict[str, float]] = None
) -> float:
    """
    計算最終綜合分數
    
    Args:
        affinity: 親和度分數
        novelty: 新穎性分數
        exploration_bonus: 探索獎勵
        base_relevance: 基礎相關性分數
        weights: 各項權重配置
        
    Returns:
        最終分數 (0-1)
    """
    if weights is None:
        weights = {
            "affinity": 0.45,
            "novelty": 0.15,
            "exploration": 0.10,
            "base_relevance": 0.30
        }
    
    # 計算加權和
    score = (
        affinity * weights["affinity"] +
        novelty * weights["novelty"] +
        exploration_bonus * weights["exploration"] +
        base_relevance * weights["base_relevance"]
    )
    
    # 確保在 [0, 1] 範圍內
    return max(0.0, min(1.0, score))


def score_result(
    result: Dict,
    preferences: Dict[str, TopicPreference],
    recent_topics: Set[str],
    exploration_rate: float = 0.15,
    weights: Optional[Dict[str, float]] = None
) -> ScoreComponents:
    """
    對單個結果進行完整打分
    
    Args:
        result: 搜尋結果
        preferences: 用戶偏好
        recent_topics: 最近主題
        exploration_rate: 探索率
        weights: 打分權重
        
    Returns:
        打分組件
    """
    # 提取結果主題（簡化版本，實際應該使用 NLP）
    result_topics = extract_topics_from_result(result)
    
    # 計算各項分數
    affinity = calculate_affinity(result_topics, preferences)
    novelty = calculate_novelty(result_topics, preferences, recent_topics)
    
    diversity = calculate_diversity_score(preferences)
    exploration_bonus = calculate_exploration_bonus(
        novelty,
        diversity,
        exploration_rate
    )
    
    base_relevance = result.get("relevance", result.get("score", 0.5))
    
    # 最終分數
    final_score = calculate_final_score(
        affinity,
        novelty,
        exploration_bonus,
        base_relevance,
        weights
    )
    
    return ScoreComponents(
        affinity=affinity,
        novelty=novelty,
        exploration_bonus=exploration_bonus,
        base_relevance=base_relevance,
        final_score=final_score
    )


# ========== 主題提取 ==========

# 這是一個簡化的版本，實際應用中應該使用 NLP 模型

TOPIC_MAPPING = {
    # 技術
    "machine learning": "machine_learning",
    "ml": "machine_learning",
    "人工智能": "ai",
    "ai": "ai",
    "python": "programming",
    "javascript": "programming",
    "code": "programming",
    
    # 生活
    "productivity": "productivity",
    "效率": "productivity",
    "健康": "health",
    "health": "health",
    "運動": "fitness",
    "fitness": "fitness",
    
    # 商業
    "startup": "business",
    "創業": "business",
    "投資": "investment",
    "investment": "investment",
    "股市": "stock_market",
}


def extract_topics_from_query(query: str) -> List[Tuple[str, float]]:
    """
    從搜尋查詢中提取主題及其相關性
    
    Args:
        query: 搜尋查詢字符串
        
    Returns:
        List of (topic_id, relevance_score) tuples
    """
    topics = []
    query_lower = query.lower()
    
    # 1. 關鍵詞匹配
    for keyword, topic_id in TOPIC_MAPPING.items():
        if keyword.lower() in query_lower:
            relevance = min(1.0, len(keyword) / len(query) * 2)
            topics.append((topic_id, relevance))
    
    # 2. 去重和權重歸一化
    unique_topics = {}
    for topic_id, relevance in topics:
        if topic_id not in unique_topics or relevance > unique_topics[topic_id]:
            unique_topics[topic_id] = relevance
    
    # 歸一化
    total = sum(unique_topics.values())
    if total > 0:
        unique_topics = {k: v/total for k, v in unique_topics.items()}
    
    return sorted(unique_topics.items(), key=lambda x: x[1], reverse=True)


def extract_topics_from_result(result: Dict) -> List[Tuple[str, float]]:
    """
    從搜尋結果中提取主題
    
    Args:
        result: 搜尋結果字典
        
    Returns:
        List of (topic_id, relevance_score) tuples
    """
    topics = []
    
    # 從標題提取
    title = result.get("title", "")
    title_topics = extract_topics_from_query(title)
    topics.extend(title_topics)
    
    # 從摘要提取
    snippet = result.get("snippet", result.get("description", ""))
    snippet_topics = extract_topics_from_query(snippet)
    topics.extend(snippet_topics)
    
    # 去重和合併
    unique_topics = {}
    for topic_id, relevance in topics:
        if topic_id not in unique_topics:
            unique_topics[topic_id] = 0.0
        unique_topics[topic_id] = max(unique_topics[topic_id], relevance)
    
    # 歸一化
    total = sum(unique_topics.values())
    if total > 0:
        unique_topics = {k: v/total for k, v in unique_topics.items()}
    
    return sorted(unique_topics.items(), key=lambda x: x[1], reverse=True)


# ========== 測試 ==========

if __name__ == "__main__":
    print("測試基礎算法模塊...")
    
    # 測試 EMA
    new_weight = update_ema(0.5, 0.8, 0.3)
    expected = 0.3 * 0.8 + 0.7 * 0.5
    assert abs(new_weight - expected) < 0.01, "EMA 測試失敗"
    print(f"✅ EMA 測試通過: {new_weight:.3f}")
    
    # 測試時間衰減
    now = datetime.now(timezone.utc)
    decayed_weight, factor = apply_time_decay(1.0, now - timedelta(hours=168), 168)
    assert abs(decayed_weight - 0.5) < 0.01, "時間衰減測試失敗"
    print(f"✅ 時間衰減測試通過: {decayed_weight:.3f} (factor: {factor:.3f})")
    
    # 測試置信度更新
    new_conf = update_confidence(0.5, 5, 0.8, 0.1)
    assert 0.5 < new_conf <= 1.0, "置信度更新測試失敗"
    print(f"✅ 置信度更新測試通過: {new_conf:.3f}")
    
    # 測試多樣性計算
    from pref_core import TopicPreference
    topics = {
        "a": TopicPreference(topic_id="a", weight=0.5),
        "b": TopicPreference(topic_id="b", weight=0.3),
        "c": TopicPreference(topic_id="c", weight=0.2)
    }
    diversity = calculate_diversity_score(topics)
    assert 0.0 < diversity <= 1.0, "多樣性計算測試失敗"
    print(f"✅ 多樣性計算測試通過: {diversity:.3f}")
    
    # 測試過度專注檢測
    topics_overfocused = {
        "a": TopicPreference(topic_id="a", weight=0.8),
        "b": TopicPreference(topic_id="b", weight=0.1),
        "c": TopicPreference(topic_id="c", weight=0.1)
    }
    is_overfocused = detect_overfocus(topics_overfocused, 0.7)
    assert is_overfocused, "過度專注檢測測試失敗"
    print(f"✅ 過度專注檢測測試通過: {is_overfocused}")
    
    # 測試打分
    result = {
        "title": "Machine Learning Tutorial",
        "relevance": 0.8
    }
    prefs = {
        "machine_learning": TopicPreference(topic_id="machine_learning", weight=0.7, confidence=0.8)
    }
    components = score_result(result, prefs, set())
    assert 0.0 <= components.final_score <= 1.0, "打分測試失敗"
    print(f"✅ 打分測試通過: {components.final_score:.3f}")
    print(f"   - 親和度: {components.affinity:.3f}")
    print(f"   - 新穎性: {components.novelty:.3f}")
    
    print("\n🎉 所有基礎算法測試通過！")
