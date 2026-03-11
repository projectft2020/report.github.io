# Memory Core 使用示例

> **目的：** 提供完整的使用示例和最佳實踐
> **版本：** v1.0

---

## 📋 基本使用

### 初始化

```python
from memory_core import MemoryCore

# 初始化（使用默認路徑）
memory_core = MemoryCore()

# 初始化（自定義路徑）
memory_core = MemoryCore(
    obsidian_path="~/Documents/Obsidian",
    qmd_path="~/.qmd/qmd",
    session_path="~/session_memory.json"
)
```

### 存儲記憶

```python
# 存儲到 Working Memory
memory_id = memory_core.store(
    content="這是一個重要的技術決策",
    layer="working",
    tags=["decision", "important"],
    metadata={
        "importance": 0.9,
        "category": "technical",
        "source": "meeting"
    }
)

print(f"Memory ID: {memory_id}")

# 存儲到 Knowledge Base
memory_id = memory_core.store(
    content="這是一個核心算法實現",
    layer="knowledge",
    tags=["algorithm", "implementation"],
    metadata={
        "importance": 1.0,
        "category": "code",
        "language": "python"
    }
)

# 存儲到 Session Memory（臨時）
memory_id = memory_core.store(
    content="這是當前會話的臨時數據",
    layer="session",
    metadata={"temporary": True}
)
```

### 查詢記憶

```python
# 查詢 Working Memory
results = memory_core.query(
    query="技術決策",
    layers=["working"],
    limit=10
)

print(f"找到 {len(results)} 條記憶：")
for result in results:
    print(f"  - {result['content'][:50]}... (score: {result['final_score']:.2f})")

# 查詢多層記憶
results = memory_core.query(
    query="算法",
    layers=["working", "knowledge"],
    limit=10
)

# 查詢帶過濾
results = memory_core.query(
    query="重要",
    layers=["knowledge"],
    filters={"tags": ["important"]},
    limit=5
)
```

### 獲取記憶

```python
# 獲取記憶
memory = memory_core.get(
    memory_id="your-memory-id",
    layer="working"
)

if memory:
    print(f"內容：{memory['content']}")
    print(f"元數據：{memory['metadata']}")
else:
    print("記憶不存在")
```

### 連結記憶

```python
# 創建相關連結
link_id = memory_core.link(
    source_id="memory-001",
    target_id="memory-002",
    relation_type="related",
    metadata={
        "description": "這兩個記憶相關"
    }
)

print(f"Link ID: {link_id}")

# 創建引用連結
link_id = memory_core.link(
    source_id="memory-003",
    target_id="memory-001",
    relation_type="references"
)
```

### 刪除記憶

```python
# 刪除記憶
success = memory_core.delete(
    memory_id="your-memory-id",
    layer="working"
)

if success:
    print("刪除成功")
else:
    print("刪除失敗")
```

---

## 🎯 高級使用

### 批量存儲

```python
# 批量存儲多個記憶
memories = [
    {
        "content": "記憶 1",
        "layer": "working",
        "tags": ["test"],
        "metadata": {"index": 1}
    },
    {
        "content": "記憶 2",
        "layer": "working",
        "tags": ["test"],
        "metadata": {"index": 2}
    },
    {
        "content": "記憶 3",
        "layer": "working",
        "tags": ["test"],
        "metadata": {"index": 3}
    }
]

memory_ids = []
for memory in memories:
    memory_id = memory_core.store(**memory)
    memory_ids.append(memory_id)

print(f"存儲了 {len(memory_ids)} 條記憶")
```

### 跨層查詢

```python
# 跨層查詢（Session + Working + Knowledge）
results = memory_core.query(
    query="重要",
    layers=["session", "working", "knowledge"],
    limit=20
)

# 分析跨層結果
layer_stats = {}
for result in results:
    layer = result["layer"]
    if layer not in layer_stats:
        layer_stats[layer] = 0
    layer_stats[layer] += 1

print("跨層結果統計：")
for layer, count in layer_stats.items():
    print(f"  - {layer}: {count}")
```

### 智能搜索

```python
# 語義搜索（使用 QMD）
results = memory_core.query(
    query="機器學習 深度學習",
    layers=["knowledge"],
    limit=10
)

# 關鍵詞搜索（使用 Obsidian）
results = memory_core.query(
    query="機器學習 AND 深度學習",
    layers=["working"],
    limit=10
)

# 組合搜索（語義 + 關鍵詞）
results = memory_core.query(
    query="機器學習 深度學習",
    layers=["working", "knowledge"],
    limit=20
)
```

---

## 📝 最佳實踐

### 實踐 1：使用適當的記憶層級

| 記憶類型 | 推薦層級 | 理由 |
|----------|----------|------|
| 當前會話臨時數據 | session | 易失性，不需要持久化 |
| 活躍專案知識 | working | 頻繁訪問，需要快速檢索 |
| 永久知識 | knowledge | 穩定，長期保存 |

### 實踐 2：添加豐富的元數據

```python
# 好的元數據
metadata = {
    "importance": 0.9,
    "category": "technical",
    "source": "meeting",
    "author": "Charlie",
    "project": "Memory Core",
    "created_at": "2026-03-09T01:27:00",
    "tags": ["decision", "important"]
}

# 壞的元數據
metadata = {}  # 空元數據
```

### 實踐 3：使用標準化標籤

```python
# 好的標籤（標準化）
tags = [
    "decision",
    "technical",
    "important",
    "algorithm",
    "implementation"
]

# 壞的標籤（不一致）
tags = [
    "decision",
    "Technical",  # 大小寫不一致
    "Important",  # 大小寫不一致
    "algo",  # 縮寫
    "impl"   # 縮寫
]
```

### 實踐 4：定期清理記憶

```python
# 清理 Session Memory（每次會話結束）
session_memories = memory_core.query(
    query="",
    layers=["session"],
    limit=1000
)

for memory in session_memories:
    memory_core.delete(
        memory_id=memory["memory_id"],
        layer="session"
    )

# 清理 Working Memory（每週）
old_memories = memory_core.query(
    query="",
    layers=["working"],
    filters={"age": ">30 days"}
)

for memory in old_memories:
    memory_core.delete(
        memory_id=memory["memory_id"],
        layer="working"
    )
```

---

## 🔧 故障排除

### 問題 1：存儲失敗

**錯誤信息：** `RuntimeError: QMD CLI not found`

**解決方案：**
```bash
# 檢查 QMD CLI 路徑
ls -la ~/.qmd/qmd

# 更新配置
cat > MEMORY_CONFIG.json << 'EOF'
{
  "qmd_path": "~/.qmd/qmd"
}
EOF
```

### 問題 2：查詢結果為空

**可能原因：**
1. 查詢關鍵詞太具體
2. 沒有存儲相關記憶
3. 搜索層級錯誤

**解決方案：**
```python
# 嘗試更一般的查詢
results = memory_core.query(
    query="算法",  # 更一般
    layers=["knowledge"],
    limit=10
)

# 嘗試多個層級
results = memory_core.query(
    query="算法",
    layers=["working", "knowledge"],  # 多層
    limit=10
)
```

### 問題 3：連結失敗

**錯誤信息：** `ValueError: Invalid layer`

**解決方案：**
```python
# 確保使用有效的層級
valid_layers = ["session", "working", "knowledge"]

# 檢查層級
if layer not in valid_layers:
    raise ValueError(f"Invalid layer: {layer}")
```

---

## 📊 性能優化

### 優化 1：使用緩存

```python
from functools import lru_cache

class CachedMemoryCore(MemoryCore):
    @lru_cache(maxsize=100)
    def cached_query(self, query, layers, limit):
        return self.query(query, layers, limit)

# 使用緩存
cached_core = CachedMemoryCore()
results = cached_core.cached_query(
    query="算法",
    layers=["knowledge"],
    limit=10
)
```

### 優化 2：批量操作

```python
# 批量存儲（減少 I/O）
def batch_store(memories):
    for memory in memories:
        memory_core.store(**memory)

# 批量查詢（減少 I/O）
def batch_query(queries):
    results = []
    for query in queries:
        results.extend(
            memory_core.query(query, layers=["knowledge"], limit=10)
        )
    return results
```

---

## 🎓 學習資源

### 官方文檔

- **Memory Core 文檔：** memory_core.py（docstring）
- **QMD 文檔：** knowledge/qmd/README.md
- **Obsidian 文檔：** OBSIDIAN_MEMORY_GUIDE.md

### 相關技能

- **check-existing-systems：** 設計前檢查現有系統
- **memory-maintenance：** 記憶維護和清理

### 示例項目

- **Obsidian 整合：** obsidian_wrapper.py
- **QMD 適配器：** qmd_adapter.py
- **記憶系統：** memory_system.py

---

**完成時間：** 2026-03-09 01:27 AM
**版本：** v1.0
**作者：** Charlie
