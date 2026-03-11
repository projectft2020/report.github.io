"""
FastAPI 應用主模塊

創建和配置 FastAPI 應用實例。
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import tasks, agents, system


def create_app() -> FastAPI:
    """創建 FastAPI 應用實例"""
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description="OpenClaw Monitor Dashboard API",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # 配置 CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 註冊路由
    app.include_router(tasks.router, prefix=settings.api_prefix)
    app.include_router(agents.router, prefix=settings.api_prefix)
    app.include_router(system.router, prefix=settings.api_prefix)
    
    # 健康檢查端點
    @app.get("/health")
    async def health_check():
        """簡單的健康檢查"""
        return {
            "status": "ok",
            "service": settings.app_name,
            "version": settings.version
        }
    
    # 根路徑
    @app.get("/")
    async def root():
        """API 根路徑"""
        return {
            "service": settings.app_name,
            "version": settings.version,
            "docs": "/docs",
            "api_prefix": settings.api_prefix
        }
    
    return app