"""
系統相關的 Pydantic 模型

定義系統健康、統計和 Scout 信息的數據結構。
"""

from datetime import datetime
from typing import Dict, Any, Optional, List

from pydantic import BaseModel, Field


class ComponentStatus(BaseModel):
    """組件狀態模型"""
    status: str
    details: Dict[str, Any] = Field(default_factory=dict)


class SystemHealth(BaseModel):
    """系統健康狀態模型"""
    status: str = Field(..., pattern=r"^(healthy|degraded|unhealthy)$")
    timestamp: datetime
    components: Dict[str, ComponentStatus] = Field(default_factory=dict)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TaskStats(BaseModel):
    """任務統計模型"""
    total: int
    pending: int
    in_progress: int
    completed: int
    failed: int


class AgentStats(BaseModel):
    """代理統計模型"""
    total: int
    active: int
    idle: int
    error: int


class ScoutStats(BaseModel):
    """Scout 統計模型"""
    topics_found: int
    tasks_created: int
    last_scan_time: Optional[datetime]

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SystemStats(BaseModel):
    """系統統計模型"""
    tasks: TaskStats
    agents: AgentStats
    scout: ScoutStats


class ScoutInfo(BaseModel):
    """Scout 詳細信息模型"""
    last_scan_time: Optional[datetime]
    topics_found: int
    tasks_created: int
    sources_scanned: List[str] = Field(default_factory=list)
    preferences: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ScanRequest(BaseModel):
    """掃描請求模型"""
    force: bool = Field(default=False, description="強制掃描，忽略時間間隔")


class ScanResponse(BaseModel):
    """掃描響應模型"""
    scan_id: str
    status: str
    estimated_duration: int = Field(..., description="預估掃描時間（秒）")