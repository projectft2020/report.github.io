"""
核心模塊單元測試
"""

import unittest
from datetime import datetime, timezone, timedelta
import os
import tempfile
import json

import sys
sys.path.insert(0, '/Users/charlie/.openclaw/workspace/kanban-ops/scout_preferences')
from pref_core import (
    Preferences,
    TopicPreference,
    TopicTrend,
    TopicDecay,
    InteractionRecord,
    PreferenceMetadata,
    GlobalSettings,
    BiasMetrics,
    PerformanceMetrics,
    TrendDirection
)


class TestPreferences(unittest.TestCase):
    """測試 Preferences 數據結構"""
    
    def test_create_preferences(self):
        """測試創建 Preferences"""
        prefs = Preferences()
        self.assertEqual(prefs.version, "2.0")
        self.assertIsNotNone(prefs.global_settings)
        self.assertIsNotNone(prefs.biases)
        self.assertIsNotNone(prefs.performance_metrics)
    
    def test_preferences_to_dict(self):
        """測試 Preferences 轉換為字典"""
        prefs = Preferences()
        prefs.metadata = PreferenceMetadata(
            user_id="test_user",
            created_at=datetime.now(timezone.utc),
            last_updated=datetime.now(timezone.utc)
        )
        
        topic = TopicPreference(
            topic_id="test_topic",
            weight=0.8,
            confidence=0.7
        )
        prefs.topics["test_topic"] = topic
        
        data = prefs.to_dict()
        self.assertEqual(data["version"], "2.0")
        self.assertEqual(len(data["topics"]), 1)
        self.assertEqual(data["topics"]["test_topic"]["topicId"], "test_topic")
    
    def test_preferences_from_dict(self):
        """測試從字典創建 Preferences"""
        data = {
            "version": "2.0",
            "metadata": {
                "userId": "test_user",
                "createdAt": datetime.now(timezone.utc).isoformat(),
                "lastUpdated": datetime.now(timezone.utc).isoformat()
            },
            "topics": {
                "test_topic": {
                    "topicId": "test_topic",
                    "weight": 0.8,
                    "confidence": 0.7
                }
            },
            "globalSettings": {},
            "biases": {},
            "performanceMetrics": {}
        }
        
        prefs = Preferences.from_dict(data)
        self.assertEqual(prefs.version, "2.0")
        self.assertEqual(len(prefs.topics), 1)
        self.assertEqual(prefs.topics["test_topic"].weight, 0.8)


class TestTopicPreference(unittest.TestCase):
    """測試 TopicPreference"""
    
    def test_create_topic(self):
        """測試創建主題偏好"""
        topic = TopicPreference(
            topic_id="test",
            weight=0.5,
            confidence=0.7
        )
        self.assertEqual(topic.topic_id, "test")
        self.assertEqual(topic.weight, 0.5)
        self.assertEqual(topic.confidence, 0.7)
    
    def test_topic_with_history(self):
        """測試帶歷史記錄的主題"""
        topic = TopicPreference(topic_id="test")
        record = InteractionRecord(
            timestamp=datetime.now(timezone.utc),
            weight=0.5,
            interaction_type="click"
        )
        topic.history.append(record)
        self.assertEqual(len(topic.history), 1)


class TestTopicTrend(unittest.TestCase):
    """測試 TopicTrend"""
    
    def test_trend_creation(self):
        """測試趨勢創建"""
        trend = TopicTrend(
            direction=TrendDirection.RISING,
            slope=0.1,
            last_change=datetime.now(timezone.utc)
        )
        self.assertEqual(trend.direction, TrendDirection.RISING)
        self.assertEqual(trend.slope, 0.1)
    
    def test_all_trend_directions(self):
        """測試所有趨勢方向"""
        for direction in [TrendDirection.RISING, TrendDirection.STABLE, TrendDirection.DECLINING]:
            trend = TopicTrend(
                direction=direction,
                slope=0.0,
                last_change=datetime.now(timezone.utc)
            )
            self.assertEqual(trend.direction, direction)


class TestPersistence(unittest.TestCase):
    """測試數據持久化"""
    
    def setUp(self):
        """設置測試環境"""
        self.test_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.test_path = self.test_file.name
        self.test_file.close()
    
    def tearDown(self):
        """清理測試環境"""
        if os.path.exists(self.test_path):
            os.remove(self.test_path)
    
    def test_save_and_load_preferences(self):
        """測試保存和加載偏好"""
        # 創建測試數據
        prefs = Preferences()
        prefs.metadata = PreferenceMetadata(
            user_id="test_user",
            created_at=datetime.now(timezone.utc),
            last_updated=datetime.now(timezone.utc)
        )
        
        topic = TopicPreference(
            topic_id="test_topic",
            weight=0.8,
            confidence=0.7
        )
        prefs.topics["test_topic"] = topic
        
        # 保存
        data = prefs.to_dict()
        with open(self.test_path, 'w') as f:
            json.dump(data, f)
        
        # 加載
        with open(self.test_path, 'r') as f:
            loaded_data = json.load(f)
        
        loaded_prefs = Preferences.from_dict(loaded_data)
        
        # 驗證
        self.assertEqual(loaded_prefs.version, prefs.version)
        self.assertEqual(len(loaded_prefs.topics), len(prefs.topics))
        self.assertEqual(
            loaded_prefs.topics["test_topic"].weight,
            prefs.topics["test_topic"].weight
        )


if __name__ == '__main__':
    unittest.main(verbosity=2)
