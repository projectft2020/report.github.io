#!/usr/bin/env python3
"""
Monitor Dashboard 單元測試

測試 Monitor Dashboard 的核心功能：
- 任務 CRUD 操作
- 代理查詢
- 系統健康檢查
- API 端點
"""

import sys
import os
import json
import unittest
from datetime import datetime
from pathlib import Path

# 添加 app 目錄到 Python 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from app.services.task_service import task_service
from app.services.agent_service import agent_service
from app.services.system_service import system_service
from app.models.task import TaskCreate, TaskStatus, TaskPriority
from app.config import settings


class TestTaskService(unittest.TestCase):
    """測試任務服務"""
    
    def setUp(self):
        """測試前設置"""
        # 備份現有 tasks.json
        self.tasks_file = Path(settings.tasks_file)
        self.backup_file = self.tasks_file.with_suffix('.json.test_backup')
        
        if self.tasks_file.exists():
            self.tasks_file.rename(self.backup_file)
        
        # 創建測試用的 tasks.json
        self.tasks_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.tasks_file, 'w', encoding='utf-8') as f:
            json.dump([], f)
    
    def tearDown(self):
        """測試後清理"""
        # 還原原始 tasks.json
        if self.backup_file.exists():
            self.backup_file.replace(self.tasks_file)
        elif self.tasks_file.exists():
            self.tasks_file.unlink()
    
    def test_create_task(self):
        """測試創建任務"""
        task_create = TaskCreate(
            title="測試任務",
            agent="test_agent",
            project_id="test-project"
        )
        
        task = task_service.create_task(task_create)
        
        self.assertIsNotNone(task.id)
        self.assertEqual(task.title, "測試任務")
        self.assertEqual(task.status, TaskStatus.PENDING)
        self.assertEqual(task.agent, "test_agent")
    
    def test_get_task(self):
        """測試獲取任務"""
        # 先創建一個任務
        task_create = TaskCreate(
            title="測試獲取任務",
            agent="test_agent"
        )
        created_task = task_service.create_task(task_create)
        
        # 獲取任務
        task = task_service.get_task(created_task.id)
        
        self.assertEqual(task.id, created_task.id)
        self.assertEqual(task.title, "測試獲取任務")
    
    def test_update_task_status(self):
        """測試更新任務狀態"""
        # 先創建一個任務
        task_create = TaskCreate(
            title="測試狀態更新",
            agent="test_agent"
        )
        created_task = task_service.create_task(task_create)
        
        # 更新狀態為進行中
        task = task_service.update_task_status(
            created_task.id, TaskStatus.IN_PROGRESS
        )
        
        self.assertEqual(task.status, TaskStatus.IN_PROGRESS)
    
    def test_delete_task(self):
        """測試刪除任務"""
        # 先創建一個任務
        task_create = TaskCreate(
            title="測試刪除任務",
            agent="test_agent"
        )
        created_task = task_service.create_task(task_create)
        
        # 刪除任務
        result = task_service.delete_task(created_task.id)
        
        self.assertTrue(result)
        
        # 驗證任務已不存在
        with self.assertRaises(Exception):
            task_service.get_task(created_task.id)
    
    def test_get_tasks_with_filtering(self):
        """測試獲取任務列表與過濾"""
        # 創建多個測試任務
        tasks_to_create = [
            TaskCreate(title="任務1", agent="agent1", priority=TaskPriority.HIGH),
            TaskCreate(title="任務2", agent="agent2", priority=TaskPriority.NORMAL),
            TaskCreate(title="任務3", agent="agent1", priority=TaskPriority.HIGH),
        ]
        
        for task_create in tasks_to_create:
            task_service.create_task(task_create)
        
        # 測試獲取所有任務
        all_tasks = task_service.get_tasks()
        self.assertGreaterEqual(all_tasks.total, 3)
        
        # 測試按代理過濾
        agent1_tasks = task_service.get_tasks(agent="agent1")
        self.assertEqual(len(agent1_tasks.tasks), 2)
        
        # 測試按優先級過濾
        high_priority_tasks = task_service.get_tasks(priority="high")
        self.assertEqual(len(high_priority_tasks.tasks), 2)


class TestAgentService(unittest.TestCase):
    """測試代理服務"""
    
    def test_get_agents(self):
        """測試獲取代理列表"""
        response = agent_service.get_agents()
        
        self.assertIsNotNone(response.agents)
        self.assertGreater(response.total, 0)
        
        # 驗證主代理存在
        main_agents = [a for a in response.agents if a.type == "main"]
        self.assertGreater(len(main_agents), 0)
    
    def test_get_agent(self):
        """測試獲取單個代理"""
        # 獲取代理列表
        response = agent_service.get_agents()
        
        if response.agents:
            agent = agent_service.get_agent(response.agents[0].id)
            self.assertEqual(agent.id, response.agents[0].id)
    
    def test_get_agent_logs(self):
        """測試獲取代理日誌"""
        # 獲取代理列表
        response = agent_service.get_agents()
        
        if response.agents:
            logs = agent_service.get_agent_logs(response.agents[0].id)
            self.assertEqual(logs.agent_id, response.agents[0].id)
            self.assertIsNotNone(logs.logs)
    
    def test_check_agent_health(self):
        """測試代理健康檢查"""
        # 獲取代理列表
        response = agent_service.get_agents()
        
        if response.agents:
            health = agent_service.check_agent_health(response.agents[0].id)
            self.assertIn(health.status, ["healthy", "unhealthy"])
            self.assertIsNotNone(health.last_heartbeat)


class TestSystemService(unittest.TestCase):
    """測試系統服務"""
    
    def test_get_system_health(self):
        """測試獲取系統健康狀態"""
        health = system_service.get_system_health()
        
        self.assertIn(health.status, ["healthy", "degraded", "unhealthy"])
        self.assertIsNotNone(health.components)
        self.assertIn("tasks_file", health.components)
    
    def test_get_system_stats(self):
        """測試獲取系統統計"""
        stats = system_service.get_system_stats()
        
        self.assertIsNotNone(stats.tasks)
        self.assertIsNotNone(stats.agents)
        self.assertIsNotNone(stats.scout)
        
        # 驗證任務統計
        self.assertIsInstance(stats.tasks.total, int)
        self.assertGreaterEqual(stats.tasks.total, 0)
    
    def test_get_scout_info(self):
        """測試獲取 Scout 信息"""
        scout_info = system_service.get_scout_info()
        
        self.assertIsInstance(scout_info.topics_found, int)
        self.assertIsInstance(scout_info.tasks_created, int)
        self.assertIsInstance(scout_info.sources_scanned, list)
    
    def test_trigger_scan(self):
        """測試觸發 Scout 掃描"""
        from app.models.system import ScanRequest
        
        scan_request = ScanRequest(force=False)
        scan_response = system_service.trigger_scan(scan_request)
        
        self.assertIsNotNone(scan_response.scan_id)
        self.assertIn(scan_response.status, ["triggered"])
        self.assertIsInstance(scan_response.estimated_duration, int)


class TestMarketConditions(unittest.TestCase):
    """測試各種市場條件下的監控功能"""
    
    def test_high_volume_scenario(self):
        """高交易量場景測試"""
        # 模擬創建大量任務
        tasks_created = []
        for i in range(100):
            task_create = TaskCreate(
                title=f"高交易量任務 {i}",
                agent="volume_test_agent",
                priority=TaskPriority.HIGH if i < 20 else TaskPriority.NORMAL
            )
            task = task_service.create_task(task_create)
            tasks_created.append(task)
        
        # 驗證系統能夠處理
        high_priority_tasks = task_service.get_tasks(
            status=TaskStatus.PENDING,
            priority="high"
        )
        
        self.assertGreaterEqual(len(high_priority_tasks.tasks), 20)
        
        # 清理測試數據
        for task in tasks_created:
            try:
                task_service.delete_task(task.id)
            except:
                pass
    
    def test_error_recovery_scenario(self):
        """錯誤恢復場景測試"""
        # 創建一些失敗的任務
        failed_tasks = []
        for i in range(5):
            task_create = TaskCreate(
                title=f"失敗任務 {i}",
                agent="error_test_agent"
            )
            task = task_service.create_task(task_create)
            
            # 模擬任務失敗
            task_service.update_task_status(task.id, TaskStatus.FAILED)
            failed_tasks.append(task)
        
        # 獲取失敗任務統計
        failed_tasks_response = task_service.get_tasks(status=TaskStatus.FAILED)
        
        self.assertGreaterEqual(len(failed_tasks_response.tasks), 5)
        
        # 測試重新啟動失敗任務
        for task in failed_tasks[:2]:  # 只重新啟動前兩個
            restarted_task = task_service.restart_task(task.id)
            self.assertEqual(restarted_task.status, TaskStatus.PENDING)
        
        # 清理測試數據
        for task in failed_tasks:
            try:
                task_service.delete_task(task.id)
            except:
                pass
    
    def test_concurrent_operations_scenario(self):
        """並發操作場景測試"""
        import threading
        import time
        
        results = []
        errors = []
        
        def create_task_thread(task_id):
            try:
                task_create = TaskCreate(
                    title=f"並發任務 {task_id}",
                    agent="concurrent_agent"
                )
                task = task_service.create_task(task_create)
                results.append(task.id)
            except Exception as e:
                errors.append(str(e))
        
        # 啟動多個線程同時創建任務
        threads = []
        for i in range(10):
            thread = threading.Thread(target=create_task_thread, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待所有線程完成
        for thread in threads:
            thread.join()
        
        # 驗證結果
        self.assertEqual(len(errors), 0, f"並發操作出錯: {errors}")
        self.assertEqual(len(results), 10)
        
        # 清理測試數據
        for task_id in results:
            try:
                task_service.delete_task(task_id)
            except:
                pass


def run_all_tests():
    """運行所有測試"""
    print("=== Monitor Dashboard 單元測試 ===\n")
    
    # 創建測試套件
    test_suite = unittest.TestSuite()
    
    # 添加測試類
    test_classes = [
        TestTaskService,
        TestAgentService,
        TestSystemService,
        TestMarketConditions
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 運行測試
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 輸出測試結果
    print(f"\n=== 測試結果摘要 ===")
    print(f"總測試數: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失敗: {len(result.failures)}")
    print(f"錯誤: {len(result.errors)}")
    
    if result.failures:
        print(f"\n=== 失敗詳情 ===")
        for test, traceback in result.failures:
            print(f"\n{test}:")
            print(traceback)
    
    if result.errors:
        print(f"\n=== 錯誤詳情 ===")
        for test, traceback in result.errors:
            print(f"\n{test}:")
            print(traceback)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)