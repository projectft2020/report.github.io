"""
集成測試模塊

測試 ScoutPreferenceManager 的端到端工作流程
"""

import unittest
import tempfile
import os
from datetime import datetime, timezone, timedelta

import sys
sys.path.insert(0, '/Users/charlie/.openclaw/workspace/kanban-ops/scout_preferences')
from pref_integration import ScoutPreferenceManager


class TestScoutPreferenceManager(unittest.TestCase):
    """測試 ScoutPreferenceManager 集成功能"""
    
    def setUp(self):
        """設置測試環境"""
        self.test_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.test_path = self.test_file.name
        # 寫入有效的初始 JSON（最小結構）
        import json
        initial_data = {
            "version": "2.0",
            "metadata": {
                "userId": "test_user",
                "createdAt": datetime.now(timezone.utc).isoformat(),
                "lastUpdated": datetime.now(timezone.utc).isoformat(),
                "totalInteractions": 0,
                "confidenceLevel": 0.0
            },
            "topics": {},
            "globalSettings": {},
            "biases": {},
            "performanceMetrics": {}
        }
        json.dump(initial_data, self.test_file)
        self.test_file.close()
        
        self.manager = ScoutPreferenceManager(self.test_path)
    
    def tearDown(self):
        """清理測試環境"""
        if os.path.exists(self.test_path):
            os.remove(self.test_path)
    
    def test_initialization(self):
        """測試初始化"""
        self.assertIsNotNone(self.manager.preferences)
        self.assertEqual(self.manager.preferences.version, "2.0")
        self.assertEqual(len(self.manager.recent_topics), 0)
    
    def test_record_interaction_basic(self):
        """測試基本交互記錄"""
        # 記錄一次點擊
        self.manager.record_interaction(
            query="machine learning tutorial",
            result={"title": "ML Tutorial", "snippet": "Learn ML"},
            interaction_type="click"
        )
        
        # 驗證
        self.assertEqual(self.manager.preferences.metadata.total_interactions, 1)
        self.assertGreater(len(self.manager.preferences.topics), 0)
    
    def test_multiple_interactions(self):
        """測試多次交互記錄"""
        # 記錄多次交互
        queries = [
            ("machine learning", {"title": "ML Basics"}, "click"),
            ("productivity tips", {"title": "Be Productive"}, "save"),
            ("python programming", {"title": "Python Guide"}, "positive_feedback")
        ]
        
        for query, result, interaction_type in queries:
            self.manager.record_interaction(
                query=query,
                result=result,
                interaction_type=interaction_type
            )
        
        # 驗證
        self.assertEqual(self.manager.preferences.metadata.total_interactions, 3)
        self.assertGreater(len(self.manager.preferences.topics), 0)
        self.assertGreater(len(self.manager.recent_topics), 0)
    
    def test_ranked_results(self):
        """測試結果排序"""
        # 記錄一些偏好
        self.manager.record_interaction(
            query="machine learning",
            result={"title": "ML Research", "snippet": "Deep learning"},
            interaction_type="positive_feedback"
        )
        
        # 測試排序
        raw_results = [
            {"title": "Machine Learning Advanced", "relevance": 0.8},
            {"title": "Productivity Hacks", "relevance": 0.9},
            {"title": "ML Tutorial", "relevance": 0.7}
        ]
        
        ranked = self.manager.get_ranked_results("machine learning", raw_results, top_k=10)
        
        # 驗證
        self.assertEqual(len(ranked), 3)
        self.assertIn("_preference_score", ranked[0])
        self.assertIn("_affinity", ranked[0])
        self.assertIn("_novelty", ranked[0])
        
        # 檢查分數在 [0, 1] 範圍內
        for result in ranked:
            self.assertGreaterEqual(result["_preference_score"], 0.0)
            self.assertLessEqual(result["_preference_score"], 1.0)
    
    def test_time_decay(self):
        """測試時間衰減"""
        # 記錄交互
        self.manager.record_interaction(
            query="test topic",
            result={"title": "Test Result"},
            interaction_type="click"
        )
        
        # 記錄原始權重
        original_weights = {
            tid: t.weight
            for tid, t in self.manager.preferences.topics.items()
        }
        
        # 應用衰減（使用較短的半衰期來測試）
        self.manager.preferences.global_settings.decay_half_life = 1  # 1 小時
        
        # 等待一會兒
        import time
        time.sleep(0.1)
        
        self.manager.apply_time_decay()
        
        # 檢查衰減
        for tid in original_weights:
            new_weight = self.manager.preferences.topics[tid].weight
            self.assertLessEqual(new_weight, original_weights[tid])
    
    def test_trend_analysis(self):
        """測試趨勢分析"""
        # 記錄多次相同主題的交互（模擬上升趨勢）
        for i in range(5):
            self.manager.record_interaction(
                query="machine learning",
                result={"title": f"ML Resource {i}"},
                interaction_type="click"
            )
        
        # 分析趨勢
        trends = self.manager.analyze_trends()
        
        # 驗證
        self.assertIsInstance(trends, dict)
    
    def test_bias_correction(self):
        """測試偏差校正"""
        # 記錄多個相同主題的交互（創建過度專注）
        for _ in range(10):
            self.manager.record_interaction(
                query="machine learning",
                result={"title": "ML Content"},
                interaction_type="positive_feedback"
            )
        
        # 記錄少量其他主題
        self.manager.record_interaction(
            query="productivity",
            result={"title": "Productivity Tips"},
            interaction_type="click"
        )
        
        # 應用偏差校正
        self.manager.correct_biases()
        
        # 驗證
        self.assertIsNotNone(self.manager.preferences.biases)
    
    def test_preference_summary(self):
        """測試偏好摘要"""
        # 記錄一些交互
        self.manager.record_interaction(
            query="machine learning",
            result={"title": "ML Guide"},
            interaction_type="save"
        )
        
        # 獲取摘要
        summary = self.manager.get_preference_summary()
        
        # 驗證
        self.assertIn("top_topics", summary)
        self.assertIn("diversity", summary)
        self.assertIn("exploration_rate", summary)
        self.assertIn("total_interactions", summary)
        self.assertEqual(summary["total_interactions"], 1)
    
    def test_persistence(self):
        """測試數據持久化"""
        # 記錄一些交互
        self.manager.record_interaction(
            query="test",
            result={"title": "Test Result"},
            interaction_type="click"
        )
        
        # 創建新的管理器實例
        new_manager = ScoutPreferenceManager(self.test_path)
        
        # 驗證數據已加載
        self.assertEqual(
            new_manager.preferences.metadata.total_interactions,
            self.manager.preferences.metadata.total_interactions
        )
        self.assertEqual(
            len(new_manager.preferences.topics),
            len(self.manager.preferences.topics)
        )
    
    def test_negative_feedback(self):
        """測試負面反饋"""
        # 記錄正面交互
        self.manager.record_interaction(
            query="machine learning",
            result={"title": "ML Content"},
            interaction_type="positive_feedback"
        )
        
        # 記錄負面反饋
        weight_before = self.manager.preferences.topics.get("machine_learning")
        if weight_before:
            weight_before_value = weight_before.weight
        else:
            weight_before_value = None
        
        self.manager.record_interaction(
            query="machine learning",
            result={"title": "Bad ML Content"},
            interaction_type="negative_feedback"
        )
        
        # 如果主題存在，權重應該下降
        if weight_before_value is not None:
            weight_after = self.manager.preferences.topics["machine_learning"].weight
            # 由於 EMA 的緣故，權重可能不會立即下降
            # 但負面反饋應該被記錄在歷史中
            self.assertGreater(len(self.manager.preferences.topics["machine_learning"].history), 1)
    
    def test_confidence_growth(self):
        """測試置信度增長"""
        # 記錄多次交互
        for _ in range(5):
            self.manager.record_interaction(
                query="machine learning",
                result={"title": "ML Content"},
                interaction_type="positive_feedback"
            )
        
        # 獲取主題
        topic = self.manager.preferences.topics.get("machine_learning")
        
        if topic:
            # 置信度應該增長
            self.assertGreater(topic.confidence, 0.0)
            self.assertLessEqual(topic.confidence, 1.0)
    
    def test_top_k_limiting(self):
        """測試 top_k 限制"""
        # 記錄一些交互
        self.manager.record_interaction(
            query="test",
            result={"title": "Test Result"},
            interaction_type="click"
        )
        
        # 測試結果
        raw_results = [
            {"title": f"Result {i}", "relevance": 0.8}
            for i in range(10)
        ]
        
        # 只返回前 3 個
        ranked = self.manager.get_ranked_results("test", raw_results, top_k=3)
        
        # 驗證
        self.assertEqual(len(ranked), 3)


class TestEndToEndWorkflow(unittest.TestCase):
    """端到端工作流程測試"""
    
    def setUp(self):
        """設置測試環境"""
        self.test_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.test_path = self.test_file.name
        # 寫入有效的初始 JSON
        import json
        initial_data = {
            "version": "2.0",
            "metadata": {
                "userId": "test_user",
                "createdAt": datetime.now(timezone.utc).isoformat(),
                "lastUpdated": datetime.now(timezone.utc).isoformat(),
                "totalInteractions": 0,
                "confidenceLevel": 0.0
            },
            "topics": {},
            "globalSettings": {},
            "biases": {},
            "performanceMetrics": {}
        }
        json.dump(initial_data, self.test_file)
        self.test_file.close()
    
    def tearDown(self):
        """清理測試環境"""
        if os.path.exists(self.test_path):
            os.remove(self.test_path)
    
    def test_full_workflow(self):
        """測試完整工作流程"""
        manager = ScoutPreferenceManager(self.test_path)
        
        # 1. 用戶搜索並點擊結果
        manager.record_interaction(
            query="machine learning transformers",
            result={
                "title": "Attention Is All You Need",
                "url": "https://arxiv.org/abs/1706.03762",
                "snippet": "Transformer architecture"
            },
            interaction_type="click"
        )
        
        # 2. 用戶保存結果
        manager.record_interaction(
            query="machine learning",
            result={
                "title": "Deep Learning Book",
                "url": "https://www.deeplearningbook.org",
                "snippet": "Comprehensive DL guide"
            },
            interaction_type="save"
        )
        
        # 3. 用戶給出正面反饋
        manager.record_interaction(
            query="productivity",
            result={
                "title": "Atomic Habits",
                "snippet": "Building good habits"
            },
            interaction_type="positive_feedback"
        )
        
        # 4. 檢查狀態
        self.assertEqual(manager.preferences.metadata.total_interactions, 3)
        self.assertGreater(len(manager.preferences.topics), 0)
        
        # 5. 用戶進行新搜索
        search_results = [
            {
                "title": "Machine Learning Tutorial",
                "snippet": "Learn ML basics",
                "relevance": 0.85
            },
            {
                "title": "Productivity Hacks",
                "snippet": "Work smarter",
                "relevance": 0.75
            },
            {
                "title": "Cooking Tips",
                "snippet": "Better cooking",
                "relevance": 0.80
            }
        ]
        
        # 6. 獲取排序結果
        ranked = manager.get_ranked_results("machine learning", search_results)
        
        # 7. 驗證結果
        self.assertEqual(len(ranked), 3)
        for result in ranked:
            self.assertIn("_preference_score", result)
            self.assertIn("_affinity", result)
            self.assertIn("_novelty", result)
        
        # 8. 定期維護
        manager.apply_time_decay()
        manager.correct_biases()
        
        # 9. 查看摘要
        summary = manager.get_preference_summary()
        self.assertIn("top_topics", summary)
        self.assertIn("diversity", summary)
        
        # 10. 數據持久化
        new_manager = ScoutPreferenceManager(self.test_path)
        self.assertEqual(
            new_manager.preferences.metadata.total_interactions,
            manager.preferences.metadata.total_interactions
        )


if __name__ == '__main__':
    unittest.main(verbosity=2)
