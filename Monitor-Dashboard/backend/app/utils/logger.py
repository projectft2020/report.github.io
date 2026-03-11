"""
日誌工具配置

統一日誌格式和輸出。
"""

import logging
import sys
from pathlib import Path
from pythonjsonlogger import jsonlogger


def setup_logging(level: str = "INFO"):
    """設置日誌配置"""
    
    # 創建日誌目錄
    log_dir = Path("/Users/charlie/.openclaw/workspace/Monitor-Dashboard/backend/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 創建格式化器
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 創建根日誌器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # 清除現有處理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 添加控制台處理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 添加文件處理器
    file_handler = logging.FileHandler(
        log_dir / "monitor-dashboard.log",
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # 設置第三方日誌級別
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """獲取指定名稱的日誌器"""
    return logging.getLogger(name)