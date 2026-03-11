"""
代理數據服務

處理代理的查詢、健康檢查和日誌獲取。
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any

from app.config import settings
from app.models.agent import (
    Agent, AgentLogs, AgentHealth, AgentStatus,
    AgentListResponse, AgentLogEntry
)
from app.utils.exceptions import AgentNotFound
from app.utils.logger import get_logger

logger = get_logger(__name__)


class AgentService:
    """代理服務類"""
    
    def __init__(self):
        self.scout_directory = Path(settings.scout_directory)
    
    def get_agents(self) -> AgentListResponse:
        """獲取所有代理"""
        # 模擬代理數據 - 實際應該從子代理系統獲取
        agents = self._get_mock_agents()
        
        return AgentListResponse(
            agents=agents,
            total=len(agents)
        )
    
    def get_agent(self, agent_id: str) -> Agent:
        """獲取單個代理"""
        agents = self._get_mock_agents()
        
        for agent in agents:
            if agent.id == agent_id:
                return agent
        
        raise AgentNotFound(agent_id)
    
    def get_agent_logs(
        self,
        agent_id: str,
        limit: int = 100,
        level: Optional[str] = None
    ) -> AgentLogs:
        """獲取代理日誌"""
        # 驗證代理存在
        self.get_agent(agent_id)
        
        # 模擬日誌數據
        logs = [
            AgentLogEntry(
                timestamp=datetime.now() - timedelta(minutes=i),
                level="INFO" if i % 4 != 0 else "ERROR",
                message=f"Agent {agent_id} log entry {i}"
            )
            for i in range(min(limit, 20))
        ]
        
        # 過濾日誌級別
        if level:
            logs = [log for log in logs if log.level == level.upper()]
        
        return AgentLogs(
            agent_id=agent_id,
            logs=logs
        )
    
    def check_agent_health(self, agent_id: str) -> AgentHealth:
        """檢查代理健康狀態"""
        # 驗證代理存在
        agent = self.get_agent(agent_id)
        
        # 模擬健康檢查
        is_healthy = agent.status == AgentStatus.ACTIVE
        
        return AgentHealth(
            status="healthy" if is_healthy else "unhealthy",
            last_heartbeat=agent.last_activity,
            metrics={
                "cpu_usage": 25.5 if is_healthy else 85.2,
                "memory_usage": 512 if is_healthy else 1024,
                "tasks_per_hour": 12 if is_healthy else 0
            }
        )
    
    def _get_mock_agents(self) -> List[Agent]:
        """獲取模擬代理數據"""
        # 實際實現應該從子代理系統獲取實時數據
        now = datetime.now()
        
        return [
            Agent(
                id="agent:main:main",
                type="main",
                model="zai/glm-4.7",
                status=AgentStatus.ACTIVE,
                created_at=now - timedelta(days=30),
                last_activity=now - timedelta(minutes=5),
                current_task="20260224-011020-d001",
                tasks_completed=142
            ),
            Agent(
                id="agent:developer:subagent:e90335c5-eb2c-4efd-8b2e-4a2e27306a6c",
                type="subagent",
                model="zai/glm-4.5",
                status=AgentStatus.ACTIVE,
                created_at=now - timedelta(hours=1),
                last_activity=now - timedelta(seconds=30),
                current_task="20260224-011020-d001",
                tasks_completed=1
            ),
            Agent(
                id="agent:researcher:subagent:abc123",
                type="subagent",
                model="zai/glm-4.7",
                status=AgentStatus.IDLE,
                created_at=now - timedelta(hours=2),
                last_activity=now - timedelta(minutes=15),
                current_task=None,
                tasks_completed=5
            ),
            Agent(
                id="agent:analyst:subagent:def456",
                type="subagent",
                model="zai/glm-4.7",
                status=AgentStatus.ERROR,
                created_at=now - timedelta(hours=3),
                last_activity=now - timedelta(minutes=45),
                current_task=None,
                tasks_completed=0
            )
        ]
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """獲取代理統計信息"""
        agents = self._get_mock_agents()
        
        stats = {
            "total": len(agents),
            "active": 0,
            "idle": 0,
            "error": 0
        }
        
        for agent in agents:
            if agent.status in stats:
                stats[agent.status.value] += 1
        
        return stats


# 創建全局服務實例
agent_service = AgentService()