"""
任務 API 路由

提供任務管理的所有 API 端點。
"""

from typing import List, Optional

from fastapi import APIRouter, Query, Depends
from fastapi.responses import JSONResponse

from app.models.task import (
    Task, TaskCreate, TaskUpdate, TaskStatus,
    TaskListResponse, TaskStatusUpdate, BatchOperation
)
from app.services.task_service import task_service
from app.utils.exceptions import http_exception_handler

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("/", response_model=TaskListResponse)
async def list_tasks(
    status: Optional[TaskStatus] = Query(None, description="按狀態過濾"),
    agent: Optional[str] = Query(None, description="按代理過濾"),
    priority: Optional[str] = Query(None, description="按優先級過濾"),
    page: int = Query(1, ge=1, description="頁碼"),
    page_size: int = Query(50, ge=1, le=200, description="每頁大小"),
    sort_by: str = Query("created_at", regex=r"^(created_at|updated_at|priority)$"),
    sort_order: str = Query("desc", regex=r"^(asc|desc)$")
):
    """獲取任務列表"""
    try:
        return task_service.get_tasks(
            status=status,
            agent=agent,
            priority=priority,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order
        )
    except Exception as e:
        http_exception_handler(e)


@router.post("/", response_model=Task, status_code=201)
async def create_task(task_create: TaskCreate):
    """創建新任務"""
    try:
        return task_service.create_task(task_create)
    except Exception as e:
        http_exception_handler(e)


@router.get("/{task_id}", response_model=Task)
async def get_task(task_id: str):
    """獲取單個任務詳情"""
    try:
        return task_service.get_task(task_id)
    except Exception as e:
        http_exception_handler(e)


@router.put("/{task_id}", response_model=Task)
async def update_task(task_id: str, task_update: TaskUpdate):
    """更新任務"""
    try:
        return task_service.update_task(task_id, task_update)
    except Exception as e:
        http_exception_handler(e)


@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: str):
    """刪除任務"""
    try:
        task_service.delete_task(task_id)
        return JSONResponse(content={"message": "Task deleted successfully"})
    except Exception as e:
        http_exception_handler(e)


@router.patch("/{task_id}/status", response_model=Task)
async def update_task_status(
    task_id: str,
    status_update: TaskStatusUpdate
):
    """更新任務狀態"""
    try:
        return task_service.update_task_status(task_id, status_update.status)
    except Exception as e:
        http_exception_handler(e)


@router.post("/{task_id}/restart", response_model=Task)
async def restart_task(task_id: str):
    """重新啟動任務"""
    try:
        return task_service.restart_task(task_id)
    except Exception as e:
        http_exception_handler(e)


@router.post("/batch", response_model=dict)
async def batch_tasks_operation(batch_op: BatchOperation):
    """批量操作任務"""
    try:
        return task_service.batch_operation(batch_op)
    except Exception as e:
        http_exception_handler(e)