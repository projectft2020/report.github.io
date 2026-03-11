"""
算法模塊單元測試
"""

import unittest
from datetime import datetime, timezone, timedelta

import sys
sys.path.insert(0, '/Users/charlie/.openclaw/workspace/kanban-ops/scout_preferences')
import pref_algorithms as algos
from pref_core import TopicPreference


class TestEMA(unittest.TestCase):
    """測試 EMA 算法"""
    
    def test_ema_update_basic(self):
        """測試基本 EMA 更新"""
        current = 0.5
        signal = 0.8
        alpha = 0.3
        expected = 0.3 * 0.8 + 0.7 * 0.5
        result = algos.update_ema(current, signal, alpha)
        self.assertAlmostEqual(result, expected, places=5)
    
    def test_ema_batch_update(self):
        """測試批量 EMA 更新"""
        weights = [0.5, 0.6, 0.7]
        signals = [0.8, 0.9, 0.7]
        results = algos.ema_batch_update(weights, signals, 0.3)
        self.assertEqual(len(results), 3)
        for r in results:
            self.assertGreaterEqual(r, 0.0)
            self.assertLessEqual(r, 1.0)


class TestTimeDecay(unittest.TestCase):
    """測試時間衰減算法"""
    
    def test_time_decay_half_life(self):
        """測試半衰期衰減"""
        weight = 1.0
        last_interaction = datetime.now(timezone.utc) - timedelta(hours=168)  # 7天前
        half_life = 168
        
        new_weight, decay_factor = algos.apply_time_decay(
            weight, last_interaction, half_life
        )
        
        # 7天後應該衰減到 50%
        self.assertAlmostEqual(new_weight, 0.5, places=2)
        self.assertAlmostEqual(decay_factor, 0.5, places=2)
    
    def test_time_decay_no_decay(self):
        """測試無衰減情況"""
        weight = 1.0
        last_interaction = datetime.now(timezone.utc)
        
        new_weight, decay_factor = algos.apply_time_decay(
            weight, last_interaction, 168
        )
        
        # 應該幾乎沒有衰減
        self.assertGreater(new_weight, 0.99)
        self.assertGreater(decay_factor, 0.99)
    
    def test_time_decay_custom_current_time(self):
        """測試自定義當前時間"""
        weight = 1.0
        last_interaction = datetime.now(timezone.utc)
        current_time = last_interaction + timedelta(hours=168)
        
        new_weight, decay_factor = algos.apply_time_decay(
            weight, last_interaction, 168, current_time
        )
        
        self.assertAlmostEqual(new_weight, 0.5, places=2)


class TestConfidence(unittest.TestCase):
    """測試置信度算法"""
    
    def test_confidence_growth(self):
        """測試置信度增長"""
        current = 0.5
        count = 5
        quality = 0.8
        growth_rate = 0.1
        
        new_conf = algos.update_confidence(current, count, quality, growth_rate)
        
        # 置信度應該增長
        self.assertGreater(new_conf, current)
        self.assertLessEqual(new_conf, 1.0)
    
    def test_confidence_saturation(self):
        """測試置信度飽和"""
        current = 0.95
        count = 100
        quality = 1.0
        
        new_conf = algos.update_confidence(current, count, quality, 0.1)
        
        # 應該接近 1.0，但不會達到 1.0（漸近行為）
        self.assertGreater(new_conf, 0.95)
        self.assertLessEqual(new_conf, 1.0)


class TestInteractionWeight(unittest.TestCase):
    """測試交互權重"""
    
    def test_positive_interactions(self):
        """測試正面交互"""
        positive_weights = {
            "click": 0.05,
            "save": 0.15,
            "share": 0.12,
            "positive_feedback": 0.20
        }
        
        for interaction, expected in positive_weights.items():
            weight = algos.get_interaction_weight(interaction)
            self.assertEqual(weight, expected)
            self.assertGreater(weight, 0)
    
    def test_negative_interactions(self):
        """測試負面交互"""
        negative_weights = {
            "ignore": -0.02,
            "negative_feedback": -0.25
        }
        
        for interaction, expected in negative_weights.items():
            weight = algos.get_interaction_weight(interaction)
            self.assertEqual(weight, expected)
            self.assertLess(weight, 0)
    
    def test_unknown_interaction(self):
        """測試未知交互"""
        weight = algos.get_interaction_weight("unknown")
        self.assertEqual(weight, 0.0)


class TestTrendAnalysis(unittest.TestCase):
    """測試趨勢分析"""
    
    def test_rising_trend(self):
        """測試上升趨勢"""
        history = [
            {"timestamp": "2026-01-01T00:00:00Z", "weight": 0.1},
            {"timestamp": "2026-01-02T00:00:00Z", "weight": 0.3},
            {"timestamp": "2026-01-03T00:00:00Z", "weight": 0.5},
            {"timestamp": "2026-01-04T00:00:00Z", "weight": 0.7},
            {"timestamp": "2026-01-05T00:00:00Z", "weight": 0.9}
        ]
        
        trend = algos.analyze_trend(history)
        self.assertEqual(trend["direction"], "rising")
        self.assertGreater(trend["slope"], 0)
    
    def test_declining_trend(self):
        """測試下降趨勢"""
        history = [
            {"timestamp": "2026-01-01T00:00:00Z", "weight": 0.9},
            {"timestamp": "2026-01-02T00:00:00Z", "weight": 0.7},
            {"timestamp": "2026-01-03T00:00:00Z", "weight": 0.5},
            {"timestamp": "2026-01-04T00:00:00Z", "weight": 0.3},
            {"timestamp": "2026-01-05T00:00:00Z", "weight": 0.1}
        ]
        
        trend = algos.analyze_trend(history)
        self.assertEqual(trend["direction"], "declining")
        self.assertLess(trend["slope"], 0)
    
    def test_stable_trend(self):
        """測試穩定趨勢"""
        history = [
            {"timestamp": "2026-01-01T00:00:00Z", "weight": 0.5},
            {"timestamp": "2026-01-02T00:00:00Z", "weight": 0.5},
            {"timestamp": "2026-01-03T00:00:00Z", "weight": 0.5},
            {"timestamp": "2026-01-04T00:00:00Z", "weight": 0.5},
            {"timestamp": "2026-01-05T00:00:00Z", "weight": 0.5}
        ]
        
        trend = algos.analyze_trend(history)
        self.assertEqual(trend["direction"], "stable")
    
    def test_insufficient_data(self):
        """測試數據不足"""
        history = [
            {"timestamp": "2026-01-01T00:00:00Z", "weight": 0.5}
        ]
        
        trend = algos.analyze_trend(history)
        self.assertEqual(trend["direction"], "stable")
        self.assertEqual(trend["slope"], 0.0)
        self.assertEqual(trend["confidence"], 0.0)


class TestDiversity(unittest.TestCase):
    """測試多樣性計算"""
    
    def test_high_diversity(self):
        """測試高多樣性"""
        topics = {
            "a": TopicPreference(topic_id="a", weight=0.33),
            "b": TopicPreference(topic_id="b", weight=0.33),
            "c": TopicPreference(topic_id="c", weight=0.34)
        }
        
        diversity = algos.calculate_diversity_score(topics)
        # 均勻分布應該有高多樣性
        self.assertGreater(diversity, 0.8)
    
    def test_low_diversity(self):
        """測試低多樣性"""
        topics = {
            "a": TopicPreference(topic_id="a", weight=0.9),
            "b": TopicPreference(topic_id="b", weight=0.05),
            "c": TopicPreference(topic_id="c", weight=0.05)
        }
        
        diversity = algos.calculate_diversity_score(topics)
        # 偏斜分布應該有低多樣性
        self.assertLess(diversity, 0.5)
    
    def test_empty_topics(self):
        """測試空主題"""
        topics = {}
        diversity = algos.calculate_diversity_score(topics)
        self.assertEqual(diversity, 0.0)


class TestOverfocus(unittest.TestCase):
    """測試過度專注檢測"""
    
    def test_overfocus_detected(self):
        """測試檢測到過度專注"""
        topics = {
            "a": TopicPreference(topic_id="a", weight=0.8),
            "b": TopicPreference(topic_id="b", weight=0.1),
            "c": TopicPreference(topic_id="c", weight=0.1)
        }
        
        is_overfocused = algos.detect_overfocus(topics, 0.7)
        self.assertTrue(is_overfocused)
    
    def test_no_overfocus(self):
        """測試無過度專注"""
        topics = {
            "a": TopicPreference(topic_id="a", weight=0.4),
            "b": TopicPreference(topic_id="b", weight=0.35),
            "c": TopicPreference(topic_id="c", weight=0.25),
            "d": TopicPreference(topic_id="d", weight=0.15),
            "e": TopicPreference(topic_id="e", weight=0.10)
        }
        
        # 前3個權重：0.4 + 0.35 + 0.25 = 1.0
        # 總權重：1.25
        # 比例：1.0/1.25 = 0.8 < 0.9 (使用更寬鬆的閾值)
        is_overfocused = algos.detect_overfocus(topics, 0.9)
        self.assertFalse(is_overfocused)
    
    def test_empty_topics(self):
        """測試空主題"""
        topics = {}
        is_overfocused = algos.detect_overfocus(topics, 0.7)
        self.assertFalse(is_overfocused)


class TestBiasCorrection(unittest.TestCase):
    """測試偏差校正"""
    
    def test_boost_low_weight(self):
        """測試提升低權重"""
        from dataclasses import asdict, replace
        
        original_a = TopicPreference(topic_id="a", weight=0.2)
        original_b = TopicPreference(topic_id="b", weight=0.1)
        original_c = TopicPreference(topic_id="c", weight=0.7)
        
        topics = {
            "a": original_a,
            "b": original_b,
            "c": original_c
        }
        
        # 記錄原始權重
        original_weights = {
            "a": original_a.weight,
            "b": original_b.weight,
            "c": original_c.weight
        }
        
        corrected = algos.correct_bias(
            topics,
            0.15,
            strategy="boost_low_weight"
        )
        
        # 低權重應該提升
        self.assertGreater(corrected["a"].weight, original_weights["a"])
        self.assertGreater(corrected["b"].weight, original_weights["b"])
    
    def test_decay_high_weight(self):
        """測試衰減高權重"""
        original_a = TopicPreference(topic_id="a", weight=0.8)
        original_b = TopicPreference(topic_id="b", weight=0.1)
        original_c = TopicPreference(topic_id="c", weight=0.1)
        
        topics = {
            "a": original_a,
            "b": original_b,
            "c": original_c
        }
        
        # 記錄原始權重
        original_weight_a = original_a.weight
        
        corrected = algos.correct_bias(
            topics,
            0.15,
            strategy="decay_high_weight"
        )
        
        # 高權重應該衰減
        self.assertLess(corrected["a"].weight, original_weight_a)


class TestScoring(unittest.TestCase):
    """測試打分算法"""
    
    def test_affinity_calculation(self):
        """測試親和度計算"""
        result_topics = [("machine_learning", 0.9)]
        preferences = {
            "machine_learning": TopicPreference(
                topic_id="machine_learning",
                weight=0.8,
                confidence=0.7
            )
        }
        
        affinity = algos.calculate_affinity(result_topics, preferences)
        
        # 親和度 = 權重 * 相關性 = 0.8 * 0.9 = 0.72
        # 歸一化 = 0.72 / 0.9 = 0.8
        self.assertAlmostEqual(affinity, 0.8, places=2)
    
    def test_novelty_new_topic(self):
        """測試新主題新穎性"""
        result_topics = [("new_topic", 0.8)]
        preferences = {}
        recent_topics = set()
        
        novelty = algos.calculate_novelty(result_topics, preferences, recent_topics)
        
        # 新主題應該有高新穎性
        self.assertGreater(novelty, 0.8)
    
    def test_exploration_bonus(self):
        """測試探索獎勵"""
        bonus = algos.calculate_exploration_bonus(
            novelty=0.9,
            diversity_score=0.7,
            exploration_rate=0.15
        )
        
        # 應該有獎勵
        self.assertGreater(bonus, 0.0)
        self.assertLess(bonus, 1.0)
    
    def test_final_score(self):
        """測試最終分數"""
        score = algos.calculate_final_score(
            affinity=0.8,
            novelty=0.6,
            exploration_bonus=0.1,
            base_relevance=0.7
        )
        
        # 應該在 [0, 1] 範圍內
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
    
    def test_full_scoring(self):
        """測試完整打分"""
        result = {
            "title": "Machine Learning Tutorial",
            "relevance": 0.8
        }
        
        preferences = {
            "machine_learning": TopicPreference(
                topic_id="machine_learning",
                weight=0.7,
                confidence=0.8
            )
        }
        
        components = algos.score_result(
            result,
            preferences,
            recent_topics=set(),
            exploration_rate=0.15
        )
        
        # 驗證各項分數
        self.assertGreaterEqual(components.affinity, 0.0)
        self.assertLessEqual(components.affinity, 1.0)
        self.assertGreaterEqual(components.novelty, 0.0)
        self.assertLessEqual(components.novelty, 1.0)
        self.assertGreaterEqual(components.final_score, 0.0)
        self.assertLessEqual(components.final_score, 1.0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
