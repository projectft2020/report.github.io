# Memory Core 整合指南

> **目的：** 整合 Memory Core 到現有工作流
> **版本：** v1.0

---

## 📋 整合步驟

### 步驟 1：安裝依賴

```bash
cd /Users/charlie/.openclaw/workspace

# 安裝依賴
pip install pydantic python-dateutil

# 驗證安裝
python3 << 'EOF'
import memory_core
print("✅ Memory Core installed successfully!")
print(f"Memory Core version: {memory_core.__version__ if hasattr(memory_core, '__version__') else 'v1.0'}")
EOF
```

---

### 步驟 2：配置初始化

創建配置文件 `MEMORY_CONFIG.json`：

```json
{
  "obsidian_path": "~/Documents/Obsidian",
  "qmd_path": "~/.qmd/qmd",
  "session_path": "~/session_memory.json"
}
```

---

### 步驟 3：更新記憶系統使用方式

#### 更新 memory_system.py

```python
"""
更新 memory_system.py 以使用 Memory Core

這是一個向後兼容的包裝器，保持現有 API 不變
"""

from typing import Dict, Any, List, Optional
from memory_core import MemoryCore

# 全局 MemoryCore 實例
_memory_core = None

def get_memory_core() -> MemoryCore:
    """獲取 MemoryCore 實例（單例模式）"""
    global _memory_core
    if _memory_core is None:
        import json
        with open("MEMORY_CONFIG.json", "r") as f:
            config = json.load(f)

        _memory_core = MemoryCore(
            obsidian_path=config["obsidian_path"],
            qmd_path=config["qmd_path"],
            session_path=config["session_path"]
        )

    return _memory_core


def store_memory(
    content: str,
    layer: str = "working",
    tags: List[str] = [],
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    存儲記憶（向後兼容）

    Args:
        content: 記憶內容
        layer: 記憶層級（默認："working"）
        tags: 標籤列表
        metadata: 元數據

    Returns:
        memory_id: 記憶 ID
    """
    memory_core = get_memory_core()
    return memory_core.store(
        content=content,
        layer=layer,
        tags=tags,
        metadata=metadata or {}
    )


def search_memory(
    query: str,
    layers: List[str] = ["working", "knowledge"],
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    搜索記憶（向後兼容）

    Args:
        query: 查詢文本
        layers: 查詢層級列表（默認：["working", "knowledge"]）
        limit: 返回結果數量（默認：10）

    Returns:
        results: 記憶結果列表
    """
    memory_core = get_memory_core()
    return memory_core.query(
        query=query,
        layers=layers,
        limit=limit
    )


def get_memory(
    memory_id: str,
    layer: str = "working"
) -> Optional[Dict[str, Any]]:
    """
    獲取記憶（向後兼容）

    Args:
        memory_id: 記憶 ID
        layer: 記憶層級（默認："working"）

    Returns:
        memory: 記憶內容，如果不存在返回 None
    """
    memory_core = get_memory_core()
    return memory_core.get(
        memory_id=memory_id,
        layer=layer
    )


def delete_memory(
    memory_id: str,
    layer: str = "working"
) -> bool:
    """
    刪除記憶（向後兼容）

    Args:
        memory_id: 記憶 ID
        layer: 記憶層級（默認："working"）

    Returns:
        success: 是否刪除成功
    """
    memory_core = get_memory_core()
    return memory_core.delete(
        memory_id=memory_id,
        layer=layer
    )


def link_memories(
    source_id: str,
    target_id: str,
    relation_type: str = "related",
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    連結記憶（向後兼容）

    Args:
        source_id: 源記憶 ID
        target_id: 目標記憶 ID
        relation_type: 連結類型（默認："related"）
        metadata: 元數據

    Returns:
        link_id: 連結 ID
    """
    memory_core = get_memory_core()
    return memory_core.link(
        source_id=source_id,
        target_id=target_id,
        relation_type=relation_type,
        metadata=metadata or {}
    )
```

---

### 步驟 4：更新 HEARTBEAT.md

在 HEARTBEAT.md 中添加記憶系統檢查：

```markdown
### 記憶系統健康檢查

```bash
cd ~/.openclaw/workspace && python3 << 'EOF'
from memory_core import MemoryCore

# 初始化 MemoryCore
memory_core = MemoryCore()

# 測試存儲
memory_id = memory_core.store(
    content="心跳檢查測試",
    layer="session",
    tags=["heartbeat"],
    metadata={"test": True}
)

# 測試查詢
results = memory_core.query(
    query="心跳檢查",
    layers=["session"],
    limit=1
)

if results:
    print("✅ 記憶系統健康")
else:
    print("❌ 記憶系統異常")
EOF
```

**檢查頻率：** 每次心跳
**檢查內容：**
- 存儲功能
- 查詢功能
- 適配器可用性
```

---

### 步驟 5：更新子代理記憶使用方式

在 IDENTITY.md 中添加記憶系統使用指南：

```markdown
## 記憶系統使用指南

### 記憶層級

| 層級 | 用途 | 系統 | TTL |
|------|------|------|-----|
| **Session Memory** | 當前會話上下文 | In-Memory | 會話結束 |
| **Working Memory** | 活躍專案知識 | Obsidian Daily Notes + QMD | 7-30 天 |
| **Knowledge Base** | 永久知識存儲 | Obsidian Topics + QMD | 永久 |

### 使用方式

#### 存儲記憶

```python
from memory_core import MemoryCore

# 初始化
memory_core = MemoryCore()

# 存儲記憶
memory_id = memory_core.store(
    content="這是一個重要決策",
    layer="knowledge",
    tags=["decision", "important"],
    metadata={"importance": 0.9}
)
```

#### 查詢記憶

```python
# 查詢記憶
results = memory_core.query(
    query="重要決策",
    layers=["knowledge"],
    limit=10
)

for result in results:
    print(f"{result['content'][:50]}... (score: {result['final_score']:.2f})")
```

#### 連結記憶

```python
# 連結記憶
link_id = memory_core.link(
    source_id="memory-001",
    target_id="memory-002",
    relation_type="related"
)
```

### 向後兼容

舊的 API 仍然可用：

```python
# 舊方式（向後兼容）
from memory_system import store_memory, search_memory

memory_id = store_memory(content="記憶內容")
results = search_memory(query="搜索關鍵詞")
```

新推薦使用 MemoryCore：

```python
# 新方式（推薦）
from memory_core import MemoryCore

memory_core = MemoryCore()
memory_id = memory_core.store(content="記憶內容")
results = memory_core.query(query="搜索關鍵詞")
```
```

---

### 步驟 6：創建遷移腳本

創建 `migrate_to_memory_core.py`：

```python
#!/usr/bin/env python3
"""
遷移到 Memory Core

將現有記憶系統遷移到新的 Memory Core
"""

import json
from pathlib import Path
from memory_core import MemoryCore
from obsidian_wrapper import ObsidianWrapper

# 初始化 MemoryCore
memory_core = MemoryCore()
obsidian = ObsidianWrapper()

# 遷移 Obsidian 記憶
def migrate_obsidian_memories():
    """遷移 Obsidian 記憶"""
    print("🔄 遷移 Obsidian 記憶...")

    # 獲取所有 Obsidian 筆記
    notes = obsidian.list_notes()

    for note in notes:
        path = note.get("path", "")
        content = obsidian.read_note(path)

        if content:
            # 解析 frontmatter
            metadata = {}
            if content.startswith("---"):
                lines = content.split("\n")
                if lines[0] == "---":
                    frontmatter_end = lines.index("---", 1)
                    frontmatter_lines = lines[1:frontmatter_end]
                    for line in frontmatter_lines:
                        if ":" in line:
                            key, value = line.split(":", 1)
                            metadata[key.strip()] = value.strip()

            # 存儲到 MemoryCore
            try:
                layer = metadata.get("layer", "working")
                tags = metadata.get("tags", "").split(",") if metadata.get("tags") else []

                memory_core.store(
                    content=content,
                    layer=layer,
                    tags=tags,
                    metadata=metadata
                )

                print(f"  ✅ 遷移: {path}")
            except Exception as e:
                print(f"  ❌ 遷移失敗: {path} - {e}")

    print("✅ Obsidian 記憶遷移完成")

# 遷移 Session 記憶
def migrate_session_memories():
    """遷移 Session 記憶"""
    print("🔄 遷移 Session 記憶...")

    session_path = Path("~/session_memory.json").expanduser()
    if session_path.exists():
        with open(session_path, "r") as f:
            session_memories = json.load(f)

        for memory_id, memory in session_memories.items():
            content = memory.get("content", "")
            metadata = memory.get("metadata", {})

            if content:
                # 存儲到 MemoryCore
                try:
                    memory_core.store(
                        content=content,
                        layer="session",
                        metadata=metadata
                    )

                    print(f"  ✅ 遷移: {memory_id}")
                except Exception as e:
                    print(f"  ❌ 遷移失敗: {memory_id} - {e}")

        print("✅ Session 記憶遷移完成")
    else:
        print("⚠️  Session 記憶文件不存在，跳過遷移")

# 主執行
if __name__ == "__main__":
    print("🚀 開始遷移到 Memory Core...")

    # 遷移 Obsidian 記憶
    migrate_obsidian_memories()

    # 遷移 Session 記憶
    migrate_session_memories()

    print("✅ 遷移完成！")
```

---

## 🧪 測試腳本

創建 `test_memory_core.py`：

```python
#!/usr/bin/env python3
"""
測試 Memory Core

測試 Memory Core 的所有功能
"""

from memory_core import MemoryCore

# 初始化
memory_core = MemoryCore()

print("🧪 測試 Memory Core...")

# 測試 1：存儲記憶
print("\n📝 測試 1：存儲記憶")
try:
    memory_id = memory_core.store(
        content="這是一個測試記憶",
        layer="session",
        tags=["test"],
        metadata={"importance": 0.8}
    )
    print(f"✅ 存儲成功: {memory_id}")
except Exception as e:
    print(f"❌ 存儲失敗: {e}")

# 測試 2：查詢記憶
print("\n🔍 測試 2：查詢記憶")
try:
    results = memory_core.query(
        query="測試",
        layers=["session"],
        limit=10
    )
    print(f"✅ 查詢成功: 找到 {len(results)} 條記憶")
    for result in results:
        print(f"  - {result['content'][:50]}... (score: {result['final_score']:.2f})")
except Exception as e:
    print(f"❌ 查詢失敗: {e}")

# 測試 3：連結記憶
print("\n🔗 測試 3：連結記憶")
try:
    link_id = memory_core.link(
        source_id=memory_id,
        target_id=memory_id,
        relation_type="self"
    )
    print(f"✅ 連結成功: {link_id}")
except Exception as e:
    print(f"❌ 連結失敗: {e}")

# 測試 4：獲取記憶
print("\n📖 測試 4：獲取記憶")
try:
    memory = memory_core.get(memory_id, layer="session")
    if memory:
        print(f"✅ 獲取成功: {memory['content'][:50]}...")
    else:
        print("❌ 獲取失敗: 記憶不存在")
except Exception as e:
    print(f"❌ 獲取失敗: {e}")

# 測試 5：刪除記憶
print("\n🗑️  測試 5：刪除記憶")
try:
    success = memory_core.delete(memory_id, layer="session")
    if success:
        print(f"✅ 刪除成功: {memory_id}")
    else:
        print("❌ 刪除失敗")
except Exception as e:
    print(f"❌ 刪除失敗: {e}")

print("\n✅ 測試完成！")
```

---

## 📊 整合檢查清單

- [ ] 安裝依賴
- [ ] 配置初始化（MEMORY_CONFIG.json）
- [ ] 更新 memory_system.py（向後兼容）
- [ ] 更新 HEARTBEAT.md（記憶系統檢查）
- [ ] 更新 IDENTITY.md（使用指南）
- [ ] 創建遷移腳本（migrate_to_memory_core.py）
- [ ] 創建測試腳本（test_memory_core.py）
- [ ] 執行遷移
- [ ] 執行測試

---

## 🚀 執行整合

```bash
# 1. 安裝依賴
cd /Users/charlie/.openclaw/workspace
pip install pydantic python-dateutil

# 2. 創建配置
cat > MEMORY_CONFIG.json << 'EOF'
{
  "obsidian_path": "~/Documents/Obsidian",
  "qmd_path": "~/.qmd/qmd",
  "session_path": "~/session_memory.json"
}
EOF

# 3. 執行遷移
python3 migrate_to_memory_core.py

# 4. 執行測試
python3 test_memory_core.py
```

---

**完成時間：** 2026-03-09 01:27 AM
**版本：** v1.0
**作者：** Charlie
