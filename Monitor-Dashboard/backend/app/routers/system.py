"""
系統 API 路由

提供系統監控的所有 API 端點。
"""

from fastapi import APIRouter

from app.models.system import (
    SystemHealth, SystemStats, ScoutInfo,
    ScanRequest, ScanResponse
)
from app.services.system_service import system_service
from app.utils.exceptions import http_exception_handler

router = APIRouter(prefix="/system", tags=["System"])


@router.get("/health", response_model=SystemHealth)
async def get_system_health():
    """獲取系統健康狀態"""
    try:
        return system_service.get_system_health()
    except Exception as e:
        http_exception_handler(e)


@router.get("/stats", response_model=SystemStats)
async def get_system_stats():
    """獲取系統統計信息"""
    try:
        return system_service.get_system_stats()
    except Exception as e:
        http_exception_handler(e)


@router.get("/scout", response_model=ScoutInfo)
async def get_scout_info():
    """獲取 Scout 信息"""
    try:
        return system_service.get_scout_info()
    except Exception as e:
        http_exception_handler(e)


@router.post("/scan", response_model=ScanResponse)
async def trigger_scout_scan(scan_request: ScanRequest):
    """觸發 Scout 掃描"""
    try:
        return system_service.trigger_scan(scan_request)
    except Exception as e:
        http_exception_handler(e)