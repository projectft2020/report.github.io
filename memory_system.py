#!/usr/bin/env python3
"""
統一記憶系統接口

這個模塊提供了統一的記憶系統接口，可以選擇使用 Obsidian 或傳統 Markdown。

使用方式：
    from memory_system import MemorySystem

    # 使用 Obsidian（推薦）
    memory = MemorySystem(use_obsidian=True)
    memory.store("This is a memory")
    results = memory.search("memory")

    # 使用傳統 Markdown
    memory = MemorySystem(use_obsidian=False)
    memory.store("This is a memory")
"""

from obsidian_memory import ObsidianMemory
from pathlib import Path
from typing import List, Optional
import logging
import os

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MemorySystem:
    """統一記憶系統"""

    def __init__(self, use_obsidian: bool = True):
        """
        初始化記憶系統

        參數:
            use_obsidian: 是否使用 Obsidian（默認：True）
        """
        self.use_obsidian = use_obsidian
        
        # Use environment variables or fall back to defaults
        workspace_path = os.environ.get('WORKSPACE_PATH', '/Users/charlie/.openclaw/workspace')
        memory_path = os.environ.get('MEMORY_PATH', '/app/memory')
        
        self.workspace_path = Path(workspace_path)
        self.memory_path = Path(memory_path)

        if use_obsidian:
            self.obsidian_memory = ObsidianMemory()
            logger.info(f"Using Obsidian memory system with workspace: {self.workspace_path}")
        else:
            logger.info(f"Using traditional Markdown memory system with memory: {self.memory_path}")

    def store(
        self,
        content: str,
        path: str = "MEMORY.md",
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        """
        存儲記憶

        參數:
            content: 記憶內容
            path: 存儲路徑（默認：MEMORY.md）
            category: 分類（可選）
            tags: 標籤列表（可選）

        返回:
            存儲結果
        """
        if self.use_obsidian:
            return self.obsidian_memory.store(content, path, category, tags)
        else:
            return self._store_traditional(content, path, category, tags)

    def search(
        self,
        query: str,
        limit: int = 10
    ) -> List[str]:
        """
        搜索記憶

        參數:
            query: 搜索查詢
            limit: 最大結果數

        返回:
            搜索結果
        """
        if self.use_obsidian:
            return self.obsidian_memory.search(query, limit)
        else:
            return self._search_traditional(query, limit)

    def read(self, path: str) -> str:
        """
        讀取記憶

        參數:
            path: 記憶路徑

        返回:
            記憶內容
        """
        if self.use_obsidian:
            return self.obsidian_memory.read(path)
        else:
            return self._read_traditional(path)

    def daily_log(self, content: str) -> str:
        """
        添加到每日日記

        參數:
            content: 日記內容

        返回:
            添加結果
        """
        if self.use_obsidian:
            return self.obsidian_memory.daily_log(content)
        else:
            return self._daily_log_traditional(content)

    def _store_traditional(
        self,
        content: str,
        path: str,
        category: Optional[str],
        tags: Optional[List[str]]
    ) -> str:
        """
        傳統方式存儲記憶

        參數:
            content: 記憶內容
            path: 存儲路徑
            category: 分類
            tags: 標籤列表

        返回:
            存儲結果
        """
        # 添加時間戳和分類
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        formatted_content = f"\n\n## {category or 'Memory'} ({timestamp})\n\n{content}"

        # 添加標籤
        if tags:
            formatted_content += "\n\nTags: " + " ".join([f"#{tag}" for tag in tags])

        # 存儲到檔案
        file_path = self.workspace_path / path
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(formatted_content)

        logger.info(f"Stored memory to {file_path}")
        return f"Stored to {file_path}"

    def _search_traditional(self, query: str, limit: int) -> List[str]:
        """
        傳統方式搜索記憶

        參數:
            query: 搜索查詢
            limit: 最大結果數

        返回:
            搜索結果
        """
        results = []

        # 搜索 MEMORY.md
        memory_file = self.workspace_path / "MEMORY.md"
        if memory_file.exists():
            with open(memory_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if query.lower() in content.lower():
                    results.append("MEMORY.md")

        # 搜索 memory/ 目錄
        if self.memory_path.exists():
            for md_file in self.memory_path.glob("*.md"):
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if query.lower() in content.lower():
                        results.append(md_file.name)

        return results[:limit]

    def _read_traditional(self, path: str) -> str:
        """
        傳統方式讀取記憶

        參數:
            path: 記憶路徑

        返回:
            記憶內容
        """
        # 處理相對路徑
        if not path.startswith('/'):
            file_path = self.workspace_path / path
        else:
            file_path = Path(path)

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        logger.info(f"Read memory from {file_path}")
        return content

    def _daily_log_traditional(self, content: str) -> str:
        """
        傳統方式添加到每日日記

        參數:
            content: 日記內容

        返回:
            添加結果
        """
        from datetime import datetime

        # 創建今日日記檔案
        today = datetime.now().strftime("%Y-%m-%d")
        daily_file = self.memory_path / f"{today}.md"

        # 確保目錄存在
        self.memory_path.mkdir(parents=True, exist_ok=True)

        # 添加時間戳和內容
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_content = f"\n\n### {timestamp}\n\n{content}"

        # 寫入檔案
        with open(daily_file, 'a', encoding='utf-8') as f:
            f.write(formatted_content)

        logger.info(f"Added to daily note: {daily_file}")
        return f"Added to {daily_file.name}"


# 全局實例（使用 Obsidian）
memory_system = MemorySystem(use_obsidian=True)


# 便捷函數（向後兼容）
def store_memory(content: str, path: str = "MEMORY.md") -> str:
    """
    存儲記憶（向後兼容）

    參數:
        content: 記憶內容
        path: 存儲路徑

    返回:
        存儲結果
    """
    return memory_system.store(content, path)


def search_memory(query: str, limit: int = 10) -> List[str]:
    """
    搜索記憶（向後兼容）

    參數:
        query: 搜索查詢
        limit: 最大結果數

    返回:
        搜索結果
    """
    return memory_system.search(query, limit)


def daily_log(content: str) -> str:
    """
    添加到每日日記（向後兼容）

    參數:
        content: 日記內容

    返回:
        添加結果
    """
    return memory_system.daily_log(content)


def get_memory_system() -> MemorySystem:
    """
    獲取全局記憶系統實例

    返回:
        MemorySystem 實例
    """
    return memory_system
