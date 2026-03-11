# Memory Core - 統一記憶操作接口

> **目的：** 統一記憶操作接口，解耦設計，可獨立演化
> **設計模式：** 適配器模式 + 三層抽象
> **版本：** v1.0

```python
"""
Memory Core - 統一記憶操作接口

實現認知矩陣的三層記憶系統：
- Session Memory（短期）：In-Memory + session.json
- Working Memory（中期）：Obsidian Daily Notes + QMD
- Knowledge Base（長期）：Obsidian Topics + QMD
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import uuid

from obsidian_wrapper import ObsidianWrapper
from qmd_adapter import QMDAdapter


class MemoryCore:
    """統一記憶操作接口"""

    def __init__(
        self,
        obsidian_path: str = "~/Documents/Obsidian",
        qmd_path: str = "~/.qmd/qmd",
        session_path: str = "~/session_memory.json"
    ):
        """
        初始化 Memory Core

        Args:
            obsidian_path: Obsidian vault 路徑
            qmd_path: QMD CLI 路徑
            session_path: Session 記憶文件路徑
        """
        # 初始化適配器
        self.obsidian_adapter = ObsidianAdapter(obsidian_path)
        self.qmd_adapter = QMDAdapter(qmd_path)
        self.session_adapter = SessionAdapter(session_path)

        # 適配器映射
        self.adapters = {
            "session": self.session_adapter,
            "working": self.obsidian_adapter,
            "knowledge": self.qmd_adapter
        }

    def store(
        self,
        content: str,
        layer: str = "working",
        tags: List[str] = [],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        存儲記憶

        Args:
            content: 記憶內容
            layer: 記憶層級（session/working/knowledge）
            tags: 標籤列表
            metadata: 元數據

        Returns:
            memory_id: 記憶 ID

        Raises:
            ValueError: 如果 layer 不有效
        """
        # 驗證 layer
        if layer not in self.adapters:
            raise ValueError(
                f"Invalid layer: {layer}. Must be one of: {list(self.adapters.keys())}"
            )

        # 生成記憶 ID
        memory_id = str(uuid.uuid4())

        # 添加元數據
        if metadata is None:
            metadata = {}

        metadata["memory_id"] = memory_id
        metadata["layer"] = layer
        metadata["created_at"] = datetime.now().isoformat()
        metadata["tags"] = tags
        metadata["access_count"] = 0

        # 使用適配器存儲
        adapter = self.adapters[layer]
        adapter.store(memory_id, content, metadata)

        return memory_id

    def query(
        self,
        query: str,
        layers: List[str] = ["working", "knowledge"],
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        查詢記憶

        Args:
            query: 查詢文本
            layers: 查詢層級列表（默認：["working", "knowledge"]）
            limit: 返回結果數量（默認：10）
            filters: 過濾條件

        Returns:
            results: 記憶結果列表

        Raises:
            ValueError: 如果 layer 不有效
        """
        # 驗證 layers
        for layer in layers:
            if layer not in self.adapters:
                raise ValueError(
                    f"Invalid layer: {layer}. Must be one of: {list(self.adapters.keys())}"
                )

        # 並行查詢各層
        results = []
        for layer in layers:
            adapter = self.adapters[layer]

            # 如果適配器支持搜索，使用搜索
            if hasattr(adapter, "search"):
                layer_results = adapter.search(query, limit, filters)
            else:
                # 否則使用默認查詢
                layer_results = adapter.query(query, limit, filters)

            # 添加層級信息
            for result in layer_results:
                result["layer"] = layer

            results.extend(layer_results)

        # 去重（跨層重複）
        results = self._deduplicate(results)

        # 重新排序（綜合分數）
        results = self._rerank(results, query)

        # 限制數量
        results = results[:limit]

        # 更新訪問次數
        for result in results:
            memory_id = result.get("memory_id")
            if memory_id:
                adapter = self.adapters[result["layer"]]
                if hasattr(adapter, "update_metadata"):
                    metadata = adapter.get_metadata(memory_id)
                    if metadata:
                        metadata["access_count"] = metadata.get("access_count", 0) + 1
                        adapter.update_metadata(memory_id, metadata)

        return results

    def link(
        self,
        source_id: str,
        target_id: str,
        relation_type: str = "related",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        創建連結

        Args:
            source_id: 源記憶 ID
            target_id: 目標記憶 ID
            relation_type: 連結類型（默認："related"）
            metadata: 元數據

        Returns:
            link_id: 連結 ID

        Raises:
            ValueError: 如果記憶不存在
        """
        # 生成連結 ID
        link_id = str(uuid.uuid4())

        # 添加元數據
        if metadata is None:
            metadata = {}

        metadata["link_id"] = link_id
        metadata["source_id"] = source_id
        metadata["target_id"] = target_id
        metadata["relation_type"] = relation_type
        metadata["created_at"] = datetime.now().isoformat()

        # 使用 Obsidian adapter 創建連結（因為它支持連結）
        self.obsidian_adapter.link(source_id, target_id, relation_type, metadata)

        return link_id

    def get(
        self,
        memory_id: str,
        layer: str = "working"
    ) -> Optional[Dict[str, Any]]:
        """
        獲取記憶

        Args:
            memory_id: 記憶 ID
            layer: 記憶層級

        Returns:
            memory: 記憶內容，如果不存在返回 None
        """
        adapter = self.adapters.get(layer)
        if not adapter:
            raise ValueError(f"Invalid layer: {layer}")

        return adapter.get(memory_id)

    def delete(
        self,
        memory_id: str,
        layer: str = "working"
    ) -> bool:
        """
        刪除記憶

        Args:
            memory_id: 記憶 ID
            layer: 記憶層級

        Returns:
            success: 是否刪除成功
        """
        adapter = self.adapters.get(layer)
        if not adapter:
            raise ValueError(f"Invalid layer: {layer}")

        return adapter.delete(memory_id)

    def _deduplicate(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重（跨層重複）"""
        seen = set()
        deduplicated = []

        for result in results:
            memory_id = result.get("memory_id")
            if memory_id and memory_id not in seen:
                seen.add(memory_id)
                deduplicated.append(result)

        return deduplicated

    def _rerank(self, results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """重新排序（綜合分數）"""
        # 多因素評分
        for result in results:
            # 語義相似度（35%）
            semantic_score = result.get("score", 0.5) * 0.35

            # 新近度（15%）
            recency_score = self._calculate_recency_score(result) * 0.15

            # 重要性（20%）
            importance_score = result.get("metadata", {}).get("importance", 0.5) * 0.20

            # 訪問頻率（10%）
            access_score = result.get("metadata", {}).get("access_count", 0) / 100 * 0.10

            # 關鍵詞匹配（20%）
            keyword_score = self._calculate_keyword_score(result, query) * 0.20

            # 組合分數
            result["final_score"] = (
                semantic_score +
                recency_score +
                importance_score +
                access_score +
                keyword_score
            )

        # 按最終分數排序
        results.sort(key=lambda x: x.get("final_score", 0), reverse=True)

        return results

    def _calculate_recency_score(self, result: Dict[str, Any]) -> float:
        """計算新近度分數"""
        metadata = result.get("metadata", {})
        created_at = metadata.get("created_at")

        if not created_at:
            return 0.5

        # 轉換為 datetime
        created_at = datetime.fromisoformat(created_at)

        # 計算時間差
        now = datetime.now()
        time_diff = (now - created_at).total_seconds()

        # 指數衰減（7 天半衰期）
        half_life = 7 * 24 * 60 * 60
        recency_score = 2 ** (-time_diff / half_life)

        return recency_score

    def _calculate_keyword_score(self, result: Dict[str, Any], query: str) -> float:
        """計算關鍵詞匹配分數"""
        content = result.get("content", "").lower()
        query_keywords = set(query.lower().split())

        # 計算匹配度
        matched = sum(1 for kw in query_keywords if kw in content)
        match_ratio = matched / len(query_keywords) if query_keywords else 0.0

        return match_ratio


# === 適配器類 ===

class SessionAdapter:
    """Session Memory 適配器（記憶體）"""

    def __init__(self, session_path: str):
        self.session_path = session_path
        self.memory: Dict[str, Dict[str, Any]] = {}
        self._load_from_file()

    def _load_from_file(self):
        """從文件加載記憶"""
        import os
        if os.path.exists(self.session_path):
            with open(self.session_path, "r") as f:
                self.memory = json.load(f)

    def _save_to_file(self):
        """保存到文件"""
        import os
        os.makedirs(os.path.dirname(self.session_path), exist_ok=True)
        with open(self.session_path, "w") as f:
            json.dump(self.memory, f, indent=2)

    def store(self, memory_id: str, content: str, metadata: Dict[str, Any]):
        """存儲記憶"""
        self.memory[memory_id] = {
            "content": content,
            "metadata": metadata
        }
        self._save_to_file()

    def query(self, query: str, limit: int, filters: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """查詢記憶（簡單關鍵詞匹配）"""
        query_keywords = query.lower().split()
        results = []

        for memory_id, memory in self.memory.items():
            content = memory.get("content", "").lower()

            # 關鍵詞匹配
            matched = sum(1 for kw in query_keywords if kw in content)
            if matched > 0:
                match_ratio = matched / len(query_keywords)

                results.append({
                    "memory_id": memory_id,
                    "content": memory.get("content"),
                    "metadata": memory.get("metadata", {}),
                    "score": match_ratio,
                    "final_score": match_ratio
                })

        # 按分數排序
        results.sort(key=lambda x: x["score"], reverse=True)

        return results[:limit]

    def get(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """獲取記憶"""
        return self.memory.get(memory_id)

    def delete(self, memory_id: str) -> bool:
        """刪除記憶"""
        if memory_id in self.memory:
            del self.memory[memory_id]
            self._save_to_file()
            return True
        return False

    def update_metadata(self, memory_id: str, metadata: Dict[str, Any]):
        """更新元數據"""
        if memory_id in self.memory:
            self.memory[memory_id]["metadata"].update(metadata)
            self._save_to_file()

    def get_metadata(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """獲取元數據"""
        memory = self.memory.get(memory_id)
        if memory:
            return memory.get("metadata", {})
        return None


class ObsidianAdapter:
    """Obsidian 適配器（使用現有 obsidian_wrapper.py）"""

    def __init__(self, obsidian_path: str):
        self.obsidian = ObsidianWrapper(vault_path=obsidian_path)

    def store(self, memory_id: str, content: str, metadata: Dict[str, Any]):
        """存儲記憶到 Obsidian"""
        # 創建文件名
        filename = f"{memory_id}.md"

        # 添加 frontmatter
        frontmatter = self._create_frontmatter(metadata)

        # 添加內容
        full_content = f"{frontmatter}\n\n{content}"

        # 創建筆記
        self.obsidian.create_note(filename, full_content)

    def _create_frontmatter(self, metadata: Dict[str, Any]) -> str:
        """創建 frontmatter"""
        frontmatter = "---\n"
        for key, value in metadata.items():
            if key != "content":
                frontmatter += f"{key}: {value}\n"
        frontmatter += "---"
        return frontmatter

    def query(self, query: str, limit: int, filters: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """查詢 Obsidian（使用 search）"""
        # 使用 obsidian_wrapper 的 search
        results = self.obsidian.search(query)

        # 格式化結果
        formatted_results = []
        for result in results[:limit]:
            formatted_results.append({
                "memory_id": result.get("path", "").replace(".md", ""),
                "content": result.get("content", ""),
                "metadata": result.get("metadata", {}),
                "score": result.get("score", 0.5),
                "final_score": result.get("score", 0.5)
            })

        return formatted_results

    def search(self, query: str, limit: int, filters: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """搜索（語義搜索，如果 QMD 可用）"""
        # 默認使用關鍵詞搜索
        return self.query(query, limit, filters)

    def get(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """獲取記憶"""
        filename = f"{memory_id}.md"
        content = self.obsidian.read_note(filename)
        if content:
            return {
                "content": content,
                "metadata": {}
            }
        return None

    def delete(self, memory_id: str) -> bool:
        """刪除記憶"""
        filename = f"{memory_id}.md"
        self.obsidian.delete_note(filename)
        return True

    def link(self, source_id: str, target_id: str, relation_type: str, metadata: Dict[str, Any]):
        """創建連結"""
        # 在 source 記憶中添加連結
        source_filename = f"{source_id}.md"
        content = self.obsidian.read_note(source_filename)
        if content:
            link = f"[[{target_id}|{relation_type}]]"
            new_content = f"{content}\n\n{link}"
            self.obsidian.append_note(source_filename, new_content)

    def update_metadata(self, memory_id: str, metadata: Dict[str, Any]):
        """更新元數據"""
        filename = f"{memory_id}.md"
        content = self.obsidian.read_note(filename)
        if content:
            # 更新 frontmatter
            lines = content.split("\n")
            if lines[0] == "---":
                # 找到 frontmatter 結束
                frontmatter_end = lines.index("---", 1)
                # 更新 frontmatter
                frontmatter_lines = lines[1:frontmatter_end]
                for key, value in metadata.items():
                    line = f"{key}: {value}"
                    if not any(line.startswith(key + ":") for line in frontmatter_lines):
                        frontmatter_lines.append(line)
                # 重組內容
                new_frontmatter = "\n".join(["---"] + frontmatter_lines + ["---"])
                new_content = new_frontmatter + "\n" + "\n".join(lines[frontmatter_end+1:])
                self.obsidian.delete_note(filename)
                self.obsidian.create_note(filename, new_content)

    def get_metadata(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """獲取元數據"""
        filename = f"{memory_id}.md"
        content = self.obsidian.read_note(filename)
        if content:
            lines = content.split("\n")
            if lines[0] == "---":
                frontmatter_end = lines.index("---", 1)
                frontmatter_lines = lines[1:frontmatter_end]
                metadata = {}
                for line in frontmatter_lines:
                    if ":" in line:
                        key, value = line.split(":", 1)
                        metadata[key.strip()] = value.strip()
                return metadata
        return None


# === 導出 ===

if __name__ == "__main__":
    # 測試
    memory_core = MemoryCore()

    # 存儲記憶
    memory_id = memory_core.store(
        content="這是一個測試記憶",
        layer="working",
        tags=["test"],
        metadata={"importance": 0.8}
    )

    print(f"Stored memory: {memory_id}")

    # 查詢記憶
    results = memory_core.query(
        query="測試",
        layers=["working"],
        limit=5
    )

    print(f"Found {len(results)} memories:")
    for result in results:
        print(f"  - {result['memory_id']}: {result['content'][:50]}... (score: {result['final_score']:.2f})")
