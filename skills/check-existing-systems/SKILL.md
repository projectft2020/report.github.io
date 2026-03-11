# 設計前檢查現有系統 SOP

> **目的：** 避免重複造輪子，充分利用現有系統和工具
> **應用場景：** 設計新系統、技術選型、架構決策

---

## 📋 SOP 步驟

### 步驟 1：檢查現有系統

**操作：**
```bash
# 查詢 MEMORY.md
memory_search "已有系統"

# 讀取 system-architecture.md
cat memory/topics/system-architecture.md

# 列出現有工具
ls -la skills/
```

**檢查清單：**
- [ ] MEMORY.md 中是否有相關系統？
- [ ] system-architecture.md 中是否有相關系統？
- [ ] skills/ 中是否有相關工具？
- [ ] 其他 memory/topics/ 中是否有相關信息？

### 步驟 2：評估是否需要新系統

**評估標準：**

| 條件 | 使用現有系統 | 設計新系統 |
|------|-------------|-----------|
| 功能匹配度 | ≥ 80% | < 80% |
| 技術棧兼容 | ✅ 兼容 | ❌ 不兼容 |
| 官方支援 | ✅ 有官方支援 | ❌ 無官方支援 |
| 已整合 | ✅ 已整合 | ❌ 未整合 |

**決策流程：**
```python
def evaluate_need(existing, requirements):
    for system in existing["existing_systems"]:
        # 評估功能匹配度
        match_score = calculate_match(system, requirements)
        
        # 評估技術棧兼容
        tech_compatible = check_tech_compatibility(system, requirements)
        
        # 評估官方支援
        official_support = check_official_support(system)
        
        # 評估整合狀態
        integrated = check_integrated(system)
        
        # 綜合評分
        score = (
            match_score * 0.4 +
            tech_compatible * 0.2 +
            official_support * 0.2 +
            integrated * 0.2
        )
        
        # 如果分數 ≥ 80%，使用現有系統
        if score >= 80:
            return use_existing(system)
    
    # 否則設計新系統
    return design_new()
```

### 步驟 3：更新長期記憶

**操作：**
```bash
# 更新 MEMORY.md
# 添加新系統信息

# 更新 system-architecture.md
# 添加新系統架構

# 記錄到 daily log
# 追蹤決策過程
```

**記錄內容：**
- 系統名稱和用途
- 技術棧
- 與其他系統的關聯
- 關鍵決策和理由

---

## 🔍 常見錯誤

### 錯誤 1：忽略現有系統

**問題：** 直接設計新系統，沒有檢查現有系統

**解決方案：** 執行步驟 1，檢查現有系統

**案例：**
- ❌ 建議使用 ChromaDB，忽略了已有的 QMD
- ✅ 檢查後發現 QMD 已經滿足需求

### 錯誤 2：重複造輪子

**問題：** 現有系統已經足夠，卻設計新系統

**解決方案：** 執行步驟 2，評估是否需要新系統

**案例：**
- ❌ 設計新的向量資料庫，已有 QMD
- ✅ 使用 QMD，整合新功能

### 錯誤 3：不更新長期記憶

**問題：** 關鍵技術決策沒有持久化到長期記憶

**解決方案：** 執行步驟 3，更新長期記憶

**案例：**
- ❌ QMD 信息只在對話中，沒有更新到 MEMORY.md
- ✅ 更新 MEMORY.md，記錄 QMD 信息

---

## 💡 最佳實踐

### 實踐 1：記憶檢查優先級

**優先級順序：**
1. MEMORY.md（最優先）
2. system-architecture.md
3. memory/topics/
4. skills/
5. 其他文檔

### 實踐 2：多源交叉驗證

**驗證方式：**
```python
# 從多個源收集信息
info_sources = [
    memory_search("關鍵詞"),
    read("memory/topics/xxx.md"),
    list_files("skills/"),
    list_files("kanban-ops/")
]

# 交叉驗證
cross_validate(info_sources)
```

### 實踐 3：決策記錄

**記錄內容：**
- 決策的背景和理由
- 評估的選項和權衡
- 選擇的結果和後續行動

---

## 🎯 成功案例

### 案例 1：使用現有 QMD

**背景：** 設計記憶系統的向量資料庫

**錯誤做法：**
- ❌ 建議使用 ChromaDB
- ❌ 忽略了已有的 QMD

**正確做法：**
- ✅ 檢查現有系統：發現 QMD
- ✅ 評估：QMD 功能匹配度 ≥ 80%
- ✅ 決策：使用 QMD

**結果：**
- 避免重複造輪子
- 降低複雜度
- 利用官方支援

### 案例 2：使用現有 Kanban

**背景：** 設計任務管理系統

**錯誤做法：**
- ❌ 設計新的任務管理系統
- ❌ 忽略了已有的 Kanban

**正確做法：**
- ✅ 檢查現有系統：發現 Kanban
- ✅ 評估：Kanban 功能匹配度 ≥ 90%
- ✅ 決策：使用 Kanban

**結果：**
- 避免重複造輪子
- 利用現有功能
- 快速部署

---

## 📝 SOP 總結

### 核心原則

1. **檢查優先**：設計前必須檢查現有系統
2. **評估必要**：評估是否需要新系統
3. **記錄決策**：關鍵決策必須持久化

### 關鍵洞察

- 檢查現有系統可以避免 80% 的重複造輪子
- 更新長期記憶可以避免信息丟失
- 建立可以提高效率和質量

---

**最後更新：** 2026-03-09 01:17 AM
**版本：** v1.0
