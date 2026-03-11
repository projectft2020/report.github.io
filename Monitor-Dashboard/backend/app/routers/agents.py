"""
代理 API 路由

提供代理監控的所有 API 端點。
"""

from typing import Optional

from fastapi import APIRouter, Query

from app.models.agent import (
    Agent, AgentLogs, AgentHealth, AgentListResponse
)
from app.services.agent_service import agent_service
from app.utils.exceptions import http_exception_handler

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.get("/", response_model=AgentListResponse)
async def list_agents():
    """獲取所有代理"""
    try:
        return agent_service.get_agents()
    except Exception as e:
        http_exception_handler(e)


@router.get("/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str):
    """獲取單個代理詳情"""
    try:
        return agent_service.get_agent(agent_id)
    except Exception as e:
        http_exception_handler(e)


@router.get("/{agent_id}/logs", response_model=AgentLogs)
async def get_agent_logs(
    agent_id: str,
    limit: int = Query(100, ge=1, le=1000, description="日誌條目限制"),
    level: Optional[str] = Query(None, description="日誌級別過濾")
):
    """獲取代理日誌"""
    try:
        return agent_service.get_agent_logs(
            agent_id=agent_id,
            limit=limit,
            level=level
        )
    except Exception as e:
        http_exception_handler(e)


@router.get("/{agent_id}/health", response_model=AgentHealth)
async def check_agent_health(agent_id: str):
    """檢查代理健康狀態"""
    try:
        return agent_service.check_agent_health(agent_id)
    except Exception as e:
        http_exception_handler(e)