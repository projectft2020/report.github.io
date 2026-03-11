"""
系統數據服務

處理系統健康檢查、統計信息和 Scout 數據。
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List

from app.config import settings
from app.models.system import (
    SystemHealth, SystemStats, ComponentStatus,
    ScoutInfo, TaskStats, AgentStats, ScoutStats,
    ScanRequest, ScanResponse
)
from app.services.task_service import task_service
from app.services.agent_service import agent_service
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SystemService:
    """系統服務類"""
    
    def __init__(self):
        self.scout_directory = Path(settings.scout_directory)
    
    def get_system_health(self) -> SystemHealth:
        """獲取系統健康狀態"""
        
        # 檢查各個組件的狀態
        components = {
            "tasks_file": self._check_tasks_file(),
            "scout_directory": self._check_scout_directory(),
            "api_service": ComponentStatus(status="healthy"),
            "database": ComponentStatus(status="healthy")  # JSON 文件作為數據庫
        }
        
        # 判斷整體狀態
        unhealthy_components = [
            name for name, comp in components.items()
            if comp.status != "healthy"
        ]
        
        overall_status = "healthy"
        if unhealthy_components:
            overall_status = "degraded" if len(unhealthy_components) == 1 else "unhealthy"
        
        return SystemHealth(
            status=overall_status,
            timestamp=datetime.now(),
            components=components
        )
    
    def get_system_stats(self) -> SystemStats:
        """獲取系統統計信息"""
        
        # 獲取任務統計
        task_stats_data = task_service.get_task_stats()
        task_stats = TaskStats(**task_stats_data)
        
        # 獲取代理統計
        agent_stats_data = agent_service.get_agent_stats()
        agent_stats = AgentStats(**agent_stats_data)
        
        # 獲取 Scout 統計
        scout_stats = self._get_scout_stats()
        
        return SystemStats(
            tasks=task_stats,
            agents=agent_stats,
            scout=scout_stats
        )
    
    def get_scout_info(self) -> ScoutInfo:
        """獲取 Scout 詳細信息"""
        
        # 讀取 Scout 數據
        scan_log = self._read_scan_log()
        topics_cache = self._read_topics_cache()
        preferences = self._read_preferences()
        
        last_scan_time = None
        if scan_log:
            # 從日誌中提取最後掃描時間
            for line in reversed(scan_log.split('\n')):
                if "開始掃描" in line:
                    # 解析時間格式：[2026-02-24 01:16:00 UTC] [INFO] 開始掃描
                    try:
                        time_str = line.split(']')[0][1:]
                        last_scan_time = datetime.strptime(
                            time_str, "%Y-%m-%d %H:%M:%S %Z"
                        )
                        break
                    except ValueError:
                        continue
        
        return ScoutInfo(
            last_scan_time=last_scan_time,
            topics_found=len(topics_cache.get("cache", {})),
            tasks_created=0,  # TODO: 計算 Scout 創建的任務數
            sources_scanned=["arxiv", "reddit", "threads", "quantocracy"],
            preferences=preferences.get("preferences", {})
        )
    
    def trigger_scan(self, scan_request: ScanRequest) -> ScanResponse:
        """觸發 Scout 掃描"""
        
        # 模擬掃描過程
        scan_id = datetime.now().strftime("%Y%m%d-%H%M%S")
        
        # 實際實現應該調用 Scout Agent
        logger.info(f"Triggering scout scan: {scan_id}")
        
        return ScanResponse(
            scan_id=scan_id,
            status="triggered",
            estimated_duration=60
        )
    
    def _check_tasks_file(self) -> ComponentStatus:
        """檢查任務文件狀態"""
        try:
            tasks_file = Path(settings.tasks_file)
            if not tasks_file.exists():
                return ComponentStatus(
                    status="unhealthy",
                    details={"reason": "Tasks file not found"}
                )
            
            # 嘗試讀取文件
            with open(tasks_file, 'r', encoding='utf-8') as f:
                json.load(f)
            
            file_size = tasks_file.stat().st_size
            modified_time = datetime.fromtimestamp(
                tasks_file.stat().st_mtime
            )
            
            return ComponentStatus(
                status="healthy",
                details={
                    "file_size": file_size,
                    "last_modified": modified_time.isoformat()
                }
            )
            
        except Exception as e:
            return ComponentStatus(
                status="unhealthy",
                details={"reason": str(e)}
            )
    
    def _check_scout_directory(self) -> ComponentStatus:
        """檢查 Scout 目錄狀態"""
        try:
            if not self.scout_directory.exists():
                return ComponentStatus(
                    status="unhealthy",
                    details={"reason": "Scout directory not found"}
                )
            
            # 檢查關鍵文件
            required_files = [
                "SCAN_LOG.md",
                "TOPICS_CACHE.json",
                "PREFERENCES.json"
            ]
            
            missing_files = []
            for file_name in required_files:
                if not (self.scout_directory / file_name).exists():
                    missing_files.append(file_name)
            
            if missing_files:
                return ComponentStatus(
                    status="degraded",
                    details={"missing_files": missing_files}
                )
            
            return ComponentStatus(
                status="healthy",
                details={"scout_directory": str(self.scout_directory)}
            )
            
        except Exception as e:
            return ComponentStatus(
                status="unhealthy",
                details={"reason": str(e)}
            )
    
    def _read_scan_log(self) -> Optional[str]:
        """讀取 Scout 掃描日誌"""
        try:
            scan_log_file = self.scout_directory / "SCAN_LOG.md"
            if scan_log_file.exists():
                with open(scan_log_file, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            logger.error(f"Error reading SCAN_LOG.md: {e}")
        return None
    
    def _read_topics_cache(self) -> Dict[str, Any]:
        """讀取 Scout 主題緩存"""
        try:
            cache_file = self.scout_directory / "TOPICS_CACHE.json"
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error reading TOPICS_CACHE.json: {e}")
        return {"version": "1.0", "cache": {}}
    
    def _read_preferences(self) -> Dict[str, Any]:
        """讀取 Scout 偏好設置"""
        try:
            pref_file = self.scout_directory / "PREFERENCES.json"
            if pref_file.exists():
                with open(pref_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error reading PREFERENCES.json: {e}")
        return {"version": "1.0", "preferences": {}}
    
    def _get_scout_stats(self) -> ScoutStats:
        """獲取 Scout 統計信息"""
        topics_cache = self._read_topics_cache()
        
        # 計算 Scout 創建的任務數
        task_stats_data = task_service.get_task_stats()
        scout_tasks = [
            t for t in task_stats_data.get("tasks", [])
            if t.get("created_by") == "scout"
        ]
        
        # 獲取最後掃描時間
        last_scan_time = None
        scan_log = self._read_scan_log()
        if scan_log:
            for line in reversed(scan_log.split('\n')):
                if "創建" in line and "個任務" in line:
                    try:
                        time_str = line.split(']')[0][1:]
                        last_scan_time = datetime.strptime(
                            time_str, "%Y-%m-%d %H:%M:%S %Z"
                        )
                        break
                    except ValueError:
                        continue
        
        return ScoutStats(
            topics_found=len(topics_cache.get("cache", {})),
            tasks_created=len(scout_tasks),
            last_scan_time=last_scan_time
        )


# 創建全局服務實例
system_service = SystemService()