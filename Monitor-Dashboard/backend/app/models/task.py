"""
任務相關的 Pydantic 模型

定義任務的數據結構、驗證規則和序列化格式。
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, validator


class TaskStatus(str, Enum):
    """任務狀態枚舉"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """任務優先級枚舉"""
    HIGHEST = "highest"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class TimeTracking(BaseModel):
    """時間追蹤信息"""
    estimated_time: Dict[str, int]  # {"min": 240, "max": 360}
    complexity_level: int = Field(ge=1, le=5)
    recommended_model: str


class ScoutMetadata(BaseModel):
    """Scout 元數據"""
    score: float
    confidence: str
    scoring_details: Dict[str, float]
    estimated_months: str
    source: str


class TaskBase(BaseModel):
    """基礎任務模型"""
    project_id: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=200)
    status: TaskStatus = TaskStatus.PENDING
    agent: str = Field(..., min_length=1)
    model: Optional[str] = None
    priority: TaskPriority = TaskPriority.NORMAL
    input_paths: List[str] = Field(default_factory=list)
    output_path: Optional[str] = None
    depends_on: List[str] = Field(default_factory=list)
    next_tasks: List[str] = Field(default_factory=list)
    notes: Optional[str] = Field(None, max_length=2000)
    time_tracking: Optional[TimeTracking] = None
    scout_metadata: Optional[ScoutMetadata] = None

    @validator('depends_on', 'next_tasks')
    def validate_task_ids(cls, v):
        """驗證任務 ID 格式"""
        for task_id in v:
            if not task_id or len(task_id.strip()) == 0:
                raise ValueError("Task ID cannot be empty")
        return v


class TaskCreate(TaskBase):
    """創建任務的請求模型"""
    pass


class TaskUpdate(BaseModel):
    """更新任務的請求模型"""
    status: Optional[TaskStatus] = None
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    notes: Optional[str] = Field(None, max_length=2000)
    completed_at: Optional[datetime] = None


class Task(TaskBase):
    """完整的任務模型"""
    id: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    created_by: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "id": "20260224-011020-a001",
                "project_id": "monitor-dashboard-20260224",
                "title": "Monitor Dashboard 架構設計",
                "status": "pending",
                "agent": "architect",
                "model": "zai/glm-4.7",
                "priority": "high",
                "input_paths": ["kanban/projects/monitor-dashboard-20260224"],
                "output_path": "kanban/projects/monitor-dashboard-20260224/design.md",
                "depends_on": [],
                "next_tasks": [],
                "created_at": "2026-02-24T01:10:20.000000+00:00",
                "updated_at": "2026-02-24T01:10:20.000000+00:00",
                "completed_at": None,
                "notes": "設計 Monitor Dashboard 的完整架構",
                "time_tracking": {
                    "estimated_time": {"min": 240, "max": 360},
                    "complexity_level": 4,
                    "recommended_model": "zai/glm-4.7"
                },
                "created_by": "charlie"
            }
        }


class TaskListResponse(BaseModel):
    """任務列表響應模型"""
    tasks: List[Task]
    total: int
    page: int = 1
    page_size: int = 50


class TaskStatusUpdate(BaseModel):
    """任務狀態更新模型"""
    status: TaskStatus


class BatchOperation(BaseModel):
    """批量操作模型"""
    task_ids: List[str]
    operation: str = Field(..., pattern=r"^(restart|cancel|delete|update_status)$")
    status: Optional[TaskStatus] = None