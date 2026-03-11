# Obsidian 記憶系統使用指南

## 📚 簡介

這個指南說明如何使用新的統一記憶系統接口，該接口整合了 Obsidian CLI 到現有系統。

## 🚀 快速開始

### 基本使用

```python
from memory_system import MemorySystem, store_memory, search_memory, daily_log

# 方式 1：使用便捷函數（推薦）
store_memory("這是一個測試記憶")
results = search_memory("測試")
daily_log("這是每日日記")

# 方式 2：使用記憶系統實例
memory = MemorySystem(use_obsidian=True)
memory.store("這是一個測試記憶")
results = memory.search("測試")
memory.daily_log("這是每日日記")
```

## 📁 檔案結構

### Obsidian Vault 結構

```
/Users/charlie/.openclaw/workspace/quant/research/
├── Memory/                    # 長期記憶
│   └── MEMORY.md            # 主記憶檔案
├── Daily Notes/              # 每日記錄
│   ├── 2026-03-08.md
│   ├── 2026-03-07.md
│   └── ...
└── Topics/                   # 主題分類
    ├── quantitative-research.md
    ├── risk-management.md
    └── ...
```

### 工作區結構

```
/Users/charlie/.openclaw/workspace/
├── memory/                   # 傳統記憶系統（已遷移）
│   ├── 2026-03-08.md
│   └── topics/
├── backup_20260308_232700/  # 備份
├── obsidian_wrapper.py       # Obsidian CLI 包裝器
├── obsidian_memory.py       # Obsidian 記憶系統
├── obsidian_integration.py   # 整合腳本
└── memory_system.py         # 統一記憶系統接口
```

## 🔧 核心功能

### 1. 記憶存儲

```python
from memory_system import store_memory

# 基本存儲
store_memory("這是一個測試記憶")

# 存儲到特定路徑
store_memory("這是一個測試記憶", path="MEMORY.md")

# 完整參數
from memory_system import MemorySystem
memory = MemorySystem(use_obsidian=True)
memory.store(
    content="這是一個測試記憶",
    path="MEMORY.md",
    category="測試",
    tags=["測試", "obsidian", "記憶"]
)
```

### 2. 記憶搜索

```python
from memory_system import search_memory

# 基本搜索
results = search_memory("測試")

# 限制結果數量
results = search_memory("測試", limit=5)

# 使用記憶系統實例
from memory_system import MemorySystem
memory = MemorySystem(use_obsidian=True)
results = memory.search("測試", limit=10)
```

### 3. 每日日記

```python
from memory_system import daily_log

# 基本記錄
daily_log("這是每日日記")

# 使用記憶系統實例
from memory_system import MemorySystem
memory = MemorySystem(use_obsidian=True)
memory.daily_log("這是每日日記")
```

### 4. 讀取記憶

```python
from memory_system import MemorySystem

memory = MemorySystem(use_obsidian=True)
content = memory.read("MEMORY.md")
print(content)
```

## 🎯 高級功能

### 1. 雙向連結分析

```python
from obsidian_memory import ObsidianMemory

memory = ObsidianMemory()

# 找出孤立檔案
orphans = memory.find_orphans()
print(f"Found {len(orphans)} orphans")

# 分析檔案連結
analysis = memory.analyze_connections("MEMORY.md")
print(f"Backlinks: {analysis['backlinks']}")
print(f"Links: {analysis['links']}")
```

### 2. Vault 統計

```python
from obsidian_memory import ObsidianMemory

memory = ObsidianMemory()
stats = memory.get_vault_stats()
print(f"Total files: {stats['total_files']}")
print(f"Orphans: {stats['orphans']}")
print(f"Total tags: {stats['total_tags']}")
```

### 3. 創建研究筆記

```python
from obsidian_memory import ObsidianMemory

memory = ObsidianMemory()
memory.create_research_note(
    title="Test Research",
    content="This is a test research note.",
    tags=["research", "test"]
)
```

## 🔄 遷移狀態

### 已遷移內容

- ✅ MEMORY.md
- ✅ 24 個每日記錄 (memory/2026-*.md)
- ✅ 9 個主題分類 (memory/topics/*.md)
- ✅ 備份已創建 (backup_20260308_232700)

### 遷移統計

```
每日記錄: 24 個 (100% 遷移)
主題分類: 9 個 (100% 遷移)
MEMORY.md: 已遷移
備份路徑: /Users/charlie/.openclaw/workspace/backup_20260308_232700
```

## 📊 當前 Vault 狀態

```
總檔案數: 57
孤立檔案: 64
總標籤數: 5
```

## 🎨 記憶格式

### 基本格式

```markdown
## 分類 (時間戳)

記憶內容

標籤：#tag1 #tag2
```

### 研究筆記格式

```markdown
# 標題

內容

---

Tags: #tag1 #tag2
Created: 時間戳
```

## 🚀 使用建議

### 1. 優先使用 Obsidian

```python
# ✅ 推薦：使用 Obsidian
memory = MemorySystem(use_obsidian=True)

# ❌ 不推薦：使用傳統 Markdown
memory = MemorySystem(use_obsidian=False)
```

### 2. 使用便捷函數

```python
# ✅ 推薦：使用便捷函數
from memory_system import store_memory, search_memory, daily_log
store_memory("記憶內容")

# ⚠️ 可用：使用記憶系統實例
from memory_system import MemorySystem
memory = MemorySystem(use_obsidian=True)
memory.store("記憶內容")
```

### 3. 添加標籤

```python
# ✅ 推薦：添加標籤
memory.store(
    "記憶內容",
    tags=["quant", "research", "strategy"]
)
```

### 4. 使用分類

```python
# ✅ 推薦：使用分類
memory.store(
    "記憶內容",
    category="研究"
)
```

## 🔧 故障排除

### 問題 1：Obsidian CLI 不工作

**症狀：** `Vault not found` 或 `no output`

**解決方案：**
1. 確認 Obsidian app 正在運行
2. 確認打開的是 `research` vault
3. 檢查 CLI 是否已啟用（Settings → General → Command line interface）

### 問題 2：搜索返回空結果

**症狀：** `search()` 返回空列表

**解決方案：**
1. 確認檔案已創建
2. 確認搜索關鍵詞正確
3. 檢查 Obsidian CLI 搜索功能

### 問題 3：遷移失敗

**症狀：** 遷移腳本報錯

**解決方案：**
1. 檢查檔案路徑
2. 檢查檔案權限
3. 使用備份恢復

## 📝 下一步

### 短期（本週）

1. ✅ 完成 Obsidian CLI 整合
2. ✅ 完成記憶系統遷移
3. ✅ 完成統一接口測試
4. ⏳ 更新所有腳本使用新接口

### 中期（本月）

1. 實現雙向連結分析
2. 自動建立知識圖譜
3. 整合 Kanban 系統
4. 優化記憶搜索

### 長期（未來）

1. 添加自定義工作流
2. 實現記憶自動整理
3. 整合研究系統
4. 創建知識可視化

## 🎉 總結

**已完成：**
- ✅ Obsidian CLI Python 包裝器
- ✅ Obsidian 記憶系統整合
- ✅ 統一記憶系統接口
- ✅ 記憶系統遷移
- ✅ 完整測試通過

**核心價值：**
- ✅ 完全的命令行控制
- ✅ 強大的搜索能力
- ✅ 雙向連結分析
- ✅ 自動化記憶系統
- ✅ 向後兼容

**準備就緒：** 可以開始使用新的記憶系統了！

---

**文檔版本：** v1.0
**最後更新：** 2026-03-08 23:30 PM
**作者：** Charlie 🦄
