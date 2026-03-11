"""
自定義異常類

統一的錯誤處理和響應格式。
"""

from fastapi import HTTPException
from typing import Optional


class MonitorException(Exception):
    """基礎監控異常"""
    
    def __init__(
        self,
        error_code: str,
        message: str,
        status_code: int = 500,
        detail: Optional[str] = None
    ):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(message)


class TaskNotFound(MonitorException):
    """任務不存在異常"""
    
    def __init__(self, task_id: str):
        super().__init__(
            error_code="TASK_NOT_FOUND",
            message=f"Task with ID '{task_id}' not found",
            status_code=404
        )


class AgentNotFound(MonitorException):
    """代理不存在異常"""
    
    def __init__(self, agent_id: str):
        super().__init__(
            error_code="AGENT_NOT_FOUND",
            message=f"Agent with ID '{agent_id}' not found",
            status_code=404
        )


class InvalidTaskStatus(MonitorException):
    """無效的任務狀態異常"""
    
    def __init__(self, status: str):
        super().__init__(
            error_code="INVALID_TASK_STATUS",
            message=f"Invalid task status: '{status}'",
            status_code=400
        )


class FileAccessError(MonitorException):
    """文件訪問錯誤"""
    
    def __init__(self, file_path: str, reason: str):
        super().__init__(
            error_code="FILE_ACCESS_ERROR",
            message=f"Cannot access file '{file_path}': {reason}",
            status_code=500
        )


def http_exception_handler(exc: MonitorException):
    """將 MonitorException 轉換為 HTTPException"""
    raise HTTPException(
        status_code=exc.status_code,
        detail={
            "error_code": exc.error_code,
            "message": exc.message,
            "detail": exc.detail,
            "timestamp": "2026-02-24T01:16:00+00:00"
        }
    )