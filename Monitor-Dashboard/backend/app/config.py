"""
配置管理

包含所有應用配置，支持環境變量覆蓋。
"""

import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """應用配置"""
    
    # 基礎配置
    app_name: str = "Monitor Dashboard"
    version: str = "1.0.0"
    debug: bool = False
    
    # 服務配置
    host: str = "0.0.0.0"
    port: int = 8001
    reload: bool = False
    
    # 日誌配置
    log_level: str = "INFO"
    
    # 文件監控配置
    watch_files: bool = True
    watch_directories: list[str] = [
        "/Users/charlie/.openclaw/workspace/kanban"
    ]
    
    # 數據文件配置
    tasks_file: str = "/Users/charlie/.openclaw/workspace/kanban/tasks.json"
    scout_directory: str = "/Users/charlie/.openclaw/workspace-scout"
    
    # API 配置
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = ["*"]
    
    # 監控配置
    health_check_interval: int = 30  # 秒
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 創建全局配置實例
settings = Settings()