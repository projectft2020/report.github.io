#!/usr/bin/env python3
"""
Monitor Dashboard FastAPI 應用

主應用入口，包含：
- FastAPI 應用初始化
- 路由註冊
- 中間件配置
- 異常處理
- 文件監控啟動

Author: Monitor Dashboard Team
Version: 1.0
Date: 2026-02-24
"""

import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.main import create_app
from app.config import settings
from app.utils.logger import setup_logging
from app.services.file_watcher import start_file_watcher

# 設置日誌
setup_logging(level=settings.log_level)
logger = logging.getLogger(__name__)

app = create_app()

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """全局異常處理"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_code": "INTERNAL_ERROR",
            "timestamp": "2026-02-24T01:16:00+00:00"
        }
    )

@app.on_event("startup")
async def startup_event():
    """應用啟動事件"""
    logger.info("Starting Monitor Dashboard Backend...")
    
    # 啟動文件監控
    if settings.watch_files:
        logger.info("Starting file watcher...")
        start_file_watcher()
    
    logger.info(f"Backend started successfully on port {settings.port}")

@app.on_event("shutdown")
async def shutdown_event():
    """應用關閉事件"""
    logger.info("Shutting down Monitor Dashboard Backend...")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
        access_log=True
    )