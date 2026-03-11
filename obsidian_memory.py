#!/usr/bin/env python3
"""
Obsidian 記憶系統整合

這個模塊提供了記憶系統與 Obsidian CLI 的整合接口。

使用方式：
    from obsidian_memory import ObsidianMemory

    memory = ObsidianMemory()
    memory.store("This is a memory")
    results = memory.search("memory")
"""

from obsidian_wrapper import ObsidianCLI
from typing import List, Dict, Any, Optional
import logging

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ObsidianMemory:
    """Obsidian 記憶系統"""

    def __init__(self, obsidian: Optional[ObsidianCLI] = None):
        """
        初始化 Obsidian 記憶系統

        參數:
            obsidian: ObsidianCLI 實例（默認：自動創建）
        """
        self.obsidian = obsidian or ObsidianCLI()

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
        # 添加時間戳和分類
        timestamp = self._get_timestamp()
        formatted_content = f"\n\n## {category or 'Memory'} ({timestamp})\n\n{content}"

        # 添加標籤
        if tags:
            tag_line = " " + " ".join([f"#{tag}" for tag in tags])
            formatted_content += tag_line

        # 存儲到 Obsidian
        result = self.obsidian.append(file=path, content=formatted_content)
        logger.info(f"Stored memory to {path}")
        return result

    def search(
        self,
        query: str,
        limit: int = 10,
        path: Optional[str] = None
    ) -> List[str]:
        """
        搜索記憶

        參數:
            query: 搜索查詢
            limit: 最大結果數
            path: 搜索路徑（可選）

        返回:
            搜索結果（檔案路徑列表）
        """
        results = self.obsidian.search(query=query, limit=limit, path=path)
        logger.info(f"Search for '{query}' found {len(results)} results")
        return results

    def search_context(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        搜索記憶（包含上下文）

        參數:
            query: 搜索查詢
            limit: 最大結果數

        返回:
            搜索結果（包含上下文）
        """
        results = self.obsidian.search_context(query=query, limit=limit)
        logger.info(f"Context search for '{query}' found {len(results)} results")
        return results

    def read(self, path: str) -> str:
        """
        讀取記憶

        參數:
            path: 記憶路徑

        返回:
            記憶內容
        """
        content = self.obsidian.read(file=path)
        logger.info(f"Read memory from {path}")
        return content

    def find_orphans(self) -> List[str]:
        """
        找出孤立的記憶（沒有反向連結）

        返回:
            孤立記憶列表
        """
        orphans = self.obsidian.get_orphans()
        logger.info(f"Found {len(orphans)} orphaned memories")
        return orphans

    def analyze_connections(self, path: str) -> Dict[str, Any]:
        """
        分析記憶的連結

        參數:
            path: 記憶路徑

        返回:
            連結分析結果
        """
        backlinks = self.obsidian.get_backlinks(file=path)
        links = self.obsidian.get_links(file=path)

        analysis = {
            "path": path,
            "backlinks": len(backlinks),
            "links": links,
            "is_orphan": len(backlinks) == 0,
            "is_deadend": links == 0
        }

        logger.info(f"Analyzed connections for {path}")
        return analysis

    def daily_log(self, content: str) -> str:
        """
        添加到每日日記

        參數:
            content: 日記內容

        返回:
            添加結果
        """
        timestamp = self._get_timestamp()
        formatted_content = f"\n\n### Log ({timestamp})\n\n{content}"

        result = self.obsidian.daily_append(content=formatted_content)
        logger.info("Added to daily note")
        return result

    def get_all_files(self, folder: Optional[str] = None) -> List[str]:
        """
        獲取所有檔案

        參數:
            folder: 資料夾（可選）

        返回:
            檔案列表
        """
        files = self.obsidian.get_files(folder=folder)
        files_list = [line.strip() for line in files.split('\n') if line.strip()]
        logger.info(f"Got {len(files_list)} files")
        return files_list

    def get_tags(self) -> List[str]:
        """
        獲取所有標籤

        返回:
            標籤列表
        """
        tags_data = self.obsidian.get_tags()

        if isinstance(tags_data, list):
            return tags_data
        elif isinstance(tags_data, dict):
            return list(tags_data.keys())
        else:
            # 解析 TSV 格式
            return [line.strip().split('\t')[0] for line in tags_data.strip().split('\n') if line.strip()]

    def create_research_note(
        self,
        title: str,
        content: str,
        tags: List[str],
        path: str = "Research/"
    ) -> str:
        """
        創建研究筆記

        參數:
            title: 標題
            content: 內容
            tags: 標籤列表
            path: 路徑

        返回:
            創建結果
        """
        # 格式化內容
        formatted_content = f"""# {title}

{content}

---

Tags: {" ".join([f"#{tag}" for tag in tags])}
Created: {self._get_timestamp()}
"""

        # 創建檔案名稱
        filename = title.lower().replace(" ", "-") + ".md"

        result = self.obsidian.create(name=filename, content=formatted_content, path=path)
        logger.info(f"Created research note: {filename}")
        return result

    def get_vault_stats(self) -> Dict[str, Any]:
        """
        獲取 Vault 統計資訊

        返回:
            Vault 統計資訊
        """
        files = self.get_all_files()
        orphans = self.find_orphans()
        tags = self.get_tags()

        stats = {
            "total_files": len(files),
            "orphans": len(orphans),
            "total_tags": len(tags),
            "files": files[:10],  # 只返回前 10 個
            "orphans_preview": orphans[:5],  # 只返回前 5 個
            "tags_preview": tags[:10]  # 只返回前 10 個
        }

        logger.info(f"Vault stats: {stats['total_files']} files, {stats['orphans']} orphans, {stats['total_tags']} tags")
        return stats

    def _get_timestamp(self) -> str:
        """
        獲取當前時間戳

        返回:
            時間戳字符串
        """
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# 便捷函數
def get_memory() -> ObsidianMemory:
    """
    獲取預設的 Obsidian 記憶實例

    返回:
        ObsidianMemory 實例
    """
    return ObsidianMemory()


# 向後兼容函數（與現有記憶系統接口保持一致）
def store_memory(content: str, path: str = "MEMORY.md") -> str:
    """
    存儲記憶（向後兼容）

    參數:
        content: 記憶內容
        path: 存儲路徑

    返回:
        存儲結果
    """
    memory = ObsidianMemory()
    return memory.store(content=content, path=path)


def search_memory(query: str, limit: int = 10) -> List[str]:
    """
    搜索記憶（向後兼容）

    參數:
        query: 搜索查詢
        limit: 最大結果數

    返回:
        搜索結果
    """
    memory = ObsidianMemory()
    return memory.search(query=query, limit=limit)
