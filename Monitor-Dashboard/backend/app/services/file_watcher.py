"""
文件監控服務

監控 tasks.json 文件的變化，支持實時更新。
"""

import time
from pathlib import Path
from threading import Thread
from typing import Callable, Optional

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TasksFileHandler(FileSystemEventHandler):
    """任務文件變化處理器"""
    
    def __init__(self, callback: Callable[[str], None]):
        self.callback = callback
        self.last_modified = 0
    
    def on_modified(self, event):
        """文件修改事件"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        if file_path.name != "tasks.json":
            return
        
        # 防抖動：避免頻繁觸發
        current_time = time.time()
        if current_time - self.last_modified < 1.0:  # 1秒內的變化忽略
            return
        
        self.last_modified = current_time
        
        try:
            logger.info(f"Tasks file modified: {file_path}")
            self.callback(str(file_path))
        except Exception as e:
            logger.error(f"Error in file change callback: {e}")


class FileWatcherService:
    """文件監控服務類"""
    
    def __init__(self):
        self.observer: Optional[Observer] = None
        self.tasks_file = Path(settings.tasks_file)
        self.watch_thread: Optional[Thread] = None
        self.running = False
    
    def start_watching(self, callback: Callable[[str], None]):
        """開始監控文件"""
        if not settings.watch_files:
            logger.info("File watching is disabled")
            return
        
        if self.running:
            logger.warning("File watcher is already running")
            return
        
        try:
            # 創建觀察者
            self.observer = Observer()
            
            # 設置處理器
            event_handler = TasksFileHandler(callback)
            
            # 添加監控
            watch_path = self.tasks_file.parent
            self.observer.schedule(
                event_handler,
                str(watch_path),
                recursive=False
            )
            
            # 啟動觀察者
            self.observer.start()
            self.running = True
            
            logger.info(f"Started watching tasks file: {self.tasks_file}")
            
        except Exception as e:
            logger.error(f"Failed to start file watcher: {e}")
            self.running = False
    
    def stop_watching(self):
        """停止監控"""
        if not self.running:
            return
        
        try:
            if self.observer:
                self.observer.stop()
                self.observer.join()
                self.observer = None
            
            self.running = False
            logger.info("Stopped file watcher")
            
        except Exception as e:
            logger.error(f"Error stopping file watcher: {e}")


# 全局文件監控服務實例
file_watcher = FileWatcherService()


def start_file_watcher():
    """啟動文件監控的便捷函數"""
    
    def file_changed_callback(file_path: str):
        """文件變化回調函數"""
        # 這裡可以添加實時更新邏輯，例如：
        # - 發送 WebSocket 通知
        # - 更新緩存
        # - 觸發事件處理
        logger.info(f"File changed event processed: {file_path}")
    
    file_watcher.start_watching(file_changed_callback)


def stop_file_watcher():
    """停止文件監控的便捷函數"""
    file_watcher.stop_watching()