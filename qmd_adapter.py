# QMD Adapter - 適配 QMD CLI

> **目的：** 適配 QMD CLI 到 Memory Core 接口
> **版本：** v1.0

```python
"""
QMD Adapter - 適配 QMD CLI

適配 QMD CLI 到 Memory Core 接口：
- 語義向量搜索
- 向量索引和存儲
- 元數據管理
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, Any, List, Optional


class QMDAdapter:
    """QMD 適配器 - 整合現有 QMD 系統"""

    def __init__(self, qmd_path: str = "~/.qmd/qmd"):
        """
        初始化 QMD Adapter

        Args:
            qmd_path: QMD CLI 路徑
        """
        self.qmd_path = Path(qmd_path).expanduser()

        # 檢查 QMD CLI 是否存在
        if not self.qmd_path.exists():
            raise RuntimeError(f"QMD CLI not found at: {self.qmd_path}")

    def store(
        self,
        memory_id: str,
        content: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """
        添加記憶到 QMD

        Args:
            memory_id: 記憶 ID
            content: 記憶內容
            metadata: 元數據

        Returns:
            success: 是否成功

        Raises:
            RuntimeError: 如果 QMD add 失敗
        """
        import tempfile
        import os

        # 創建臨時文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            temp_file = f.name

            # 添加 frontmatter
            frontmatter = self._create_frontmatter(metadata)
            full_content = f"{frontmatter}\n\n{content}"
            f.write(full_content)

        try:
            # 構建 collection 名稱
            layer = metadata.get("layer", "working")
            collection = f"memory-{layer}"

            # 構建 QMD add 命令
            cmd = [
                str(self.qmd_path),
                "add",
                temp_file,
                "-c", collection,
                "--id", memory_id
            ]

            # 添加標籤（如果有）
            tags = metadata.get("tags", [])
            if tags:
                cmd.extend(["--tags", ",".join(tags)])

            # 執行 QMD add
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                raise RuntimeError(f"QMD add failed: {result.stderr}")

            return True

        finally:
            # 清理臨時文件
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def _create_frontmatter(self, metadata: Dict[str, Any]) -> str:
        """創建 frontmatter"""
        frontmatter = "---\n"
        for key, value in metadata.items():
            if key != "content":
                frontmatter += f"{key}: {value}\n"
        frontmatter += "---"
        return frontmatter

    def search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        搜索 QMD

        Args:
            query: 查詢文本
            limit: 返回結果數量
            filters: 過濾條件

        Returns:
            results: 記憶結果列表

        Raises:
            RuntimeError: 如果 QMD search 失敗
        """
        # 構建 QMD search 命令
        cmd = [
            str(self.qmd_path),
            "vsearch",  # 語義搜索
            query,
            "-n", str(limit),
            "--json"  # JSON 輸出
        ]

        # 添加過濾條件（如果需要）
        if filters:
            layer = filters.get("layer", "working")
            collection = f"memory-{layer}"
            cmd.extend(["-c", collection])

            # 添加標籤過濾（如果有）
            tags = filters.get("tags", [])
            if tags:
                cmd.extend(["--tags", ",".join(tags)])

        # 執行搜索
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            raise RuntimeError(f"QMD search failed: {result.stderr}")

        # 解析 JSON 結果
        try:
            results_data = json.loads(result.stdout)
        except json.JSONDecodeError:
            # 如果 JSON 解析失敗，返回空列表
            return []

        # 格式化結果
        formatted_results = []
        if isinstance(results_data, list):
            for item in results_data:
                formatted_results.append({
                    'memory_id': item.get('id', ''),
                    'content': item.get('content', ''),
                    'metadata': item.get('metadata', {}),
                    'score': item.get('score', 0.5),
                    'final_score': item.get('score', 0.5)
                })

        return formatted_results

    def query(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """查詢（調用 search）"""
        return self.search(query, limit, filters)

    def get(
        self,
        memory_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        獲取記憶

        Args:
            memory_id: 記憶 ID

        Returns:
            memory: 記憶內容，如果不存在返回 None
        """
        # 構建 QMD get 命令
        cmd = [
            str(self.qmd_path),
            "get",
            memory_id,
            "--json"
        ]

        # 執行獲取
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            # 如果記憶不存在，返回 None
            return None

        # 解析 JSON 結果
        try:
            memory_data = json.loads(result.stdout)
            return {
                'content': memory_data.get('content', ''),
                'metadata': memory_data.get('metadata', {})
            }
        except json.JSONDecodeError:
            return None

    def delete(
        self,
        memory_id: str
    ) -> bool:
        """
        刪除記憶

        Args:
            memory_id: 記憶 ID

        Returns:
            success: 是否刪除成功
        """
        # 構建 QMD delete 命令
        cmd = [
            str(self.qmd_path),
            "delete",
            memory_id
        ]

        # 執行刪除
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            return False

        return True

    def update_metadata(
        self,
        memory_id: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """
        更新元數據

        Args:
            memory_id: 記憶 ID
            metadata: 元數據

        Returns:
            success: 是否更新成功
        """
        # 構建 QMD update 命令
        cmd = [
            str(self.qmd_path),
            "update",
            memory_id,
            "--metadata", json.dumps(metadata)
        ]

        # 執行更新
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            return False

        return True

    def get_metadata(
        self,
        memory_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        獲取元數據

        Args:
            memory_id: 記憶 ID

        Returns:
            metadata: 元數據，如果不存在返回 None
        """
        memory = self.get(memory_id)
        if memory:
            return memory.get('metadata', {})
        return None


# === 導出 ===

if __name__ == "__main__":
    # 測試
    qmd_adapter = QMDAdapter()

    # 存儲記憶
    success = qmd_adapter.store(
        memory_id="test-memory-001",
        content="這是一個測試記憶",
        metadata={
            "layer": "working",
            "tags": ["test", "qmd"],
            "created_at": "2026-03-09T01:27:00"
        }
    )

    print(f"Stored memory: {success}")

    # 搜索記憶
    results = qmd_adapter.search(
        query="測試",
        limit=5
    )

    print(f"Found {len(results)} memories:")
    for result in results:
        print(f"  - {result['memory_id']}: {result['content'][:50]}... (score: {result['score']:.2f})")
```

# QMD Adapter 完成說明

## 實現功能

✅ **QMD CLI 適配**
- 初始化 QMD CLI
- 檢查 QMD CLI 是否存在

✅ **記憶操作**
- `store()` - 存儲記憶到 QMD
- `search()` - 語義搜索記憶
- `query()` - 查詢記憶（調用 search）
- `get()` - 獲取記憶
- `delete()` - 刪除記憶

✅ **元數據管理**
- `update_metadata()` - 更新元數據
- `get_metadata()` - 獲取元數據
- Frontmatter 支持（YAML 格式）

✅ **過濾支持**
- Collection 過濾（memory-session/working/knowledge）
- 標籤過濾

## 技術細節

### QMD 命令映射

| 方法 | QMD 命令 | 說明 |
|------|----------|------|
| `store()` | `qmd add` | 添加文件到 QMD |
| `search()` | `qmd vsearch` | 語義搜索 |
| `get()` | `qmd get` | 獲取文件 |
| `delete()` | `qmd delete` | 刪除文件 |
| `update_metadata()` | `qmd update` | 更新元數據 |

### Collection 映射

| 記憶層級 | QMD Collection |
|----------|----------------|
| Session | memory-session |
| Working | memory-working |
| Knowledge | memory-knowledge |

### Frontmatter 格式

```yaml
---
memory_id: xxx
layer: working
tags: test,qmd
created_at: 2026-03-09T01:27:00
importance: 0.8
---

記憶內容...
```

## 使用方式

### 基本使用

```python
from qmd_adapter import QMDAdapter

# 初始化
qmd_adapter = QMDAdapter()

# 存儲記憶
success = qmd_adapter.store(
    memory_id="test-001",
    content="這是一個測試記憶",
    metadata={
        "layer": "working",
        "tags": ["test"]
    }
)

# 搜索記憶
results = qmd_adapter.search(
    query="測試",
    limit=10
)

# 獲取記憶
memory = qmd_adapter.get("test-001")

# 刪除記憶
success = qmd_adapter.delete("test-001")
```

### 與 MemoryCore 整合

```python
from memory_core import MemoryCore

# 初始化 MemoryCore
memory_core = MemoryCore()

# 存儲記憶（自動路由到 QMD Adapter）
memory_id = memory_core.store(
    content="這是一個測試記憶",
    layer="knowledge",  # 使用 QMD
    tags=["test"],
    metadata={"importance": 0.8}
)

# 查詢記憶（自動路由到 QMD Adapter）
results = memory_core.query(
    query="測試",
    layers=["knowledge"],  # 使用 QMD
    limit=10
)
```

## 依賴

- Python 3.8+
- QMD CLI（已安裝）

## 文檔

- QMD CLI 文檔：`qmd --help`
- QMD 官方文檔：knowledge/qmd/README.md

---

**完成時間：** 2026-03-09 01:27 AM
**版本：** v1.0
**作者：** Charlie
