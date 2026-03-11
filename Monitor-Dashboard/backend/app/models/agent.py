"""
代理相關的 Pydantic 模型

定義代理的數據結構、狀態和統計信息。
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    """代理狀態枚舉"""
    IDLE = "idle"
    ACTIVE = "active"
    ERROR = "error"
    TERMINATED = "terminated"


class AgentType(str, Enum):
    """代理類型枚舉"""
    MAIN = "main"
    SUBAGENT = "subagent"


class Agent(BaseModel):
    """代理模型"""
    id: str
    type: str  # main, subagent
    model: Optional[str] = None
    status: AgentStatus
    created_at: datetime
    last_activity: datetime
    current_task: Optional[str] = None
    tasks_completed: int = 0

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "id": "agent:main:main",
                "type": "main",
                "model": "zai/glm-4.7",
                "status": "active",
                "created_at": "2026-02-24T01:00:00.000000+00:00",
                "last_activity": "2026-02-24T01:15:00.000000+00:00",
                "current_task": "20260224-011020-a001",
                "tasks_completed": 42
            }
        }


class AgentLogEntry(BaseModel):
    """代理日誌條目模型"""
    timestamp: datetime
    level: str = Field(..., pattern=r"^(DEBUG|INFO|WARNING|ERROR)$")
    message: str

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AgentLogs(BaseModel):
    """代理日誌響應模型"""
    agent_id: str
    logs: List[AgentLogEntry]


class AgentHealth(BaseModel):
    """代理健康狀態模型"""
    status: str = Field(..., pattern=r"^(healthy|unhealthy)$")
    last_heartbeat: datetime
    metrics: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AgentListResponse(BaseModel):
    """代理列表響應模型"""
    agents: List[Agent]
    total: int