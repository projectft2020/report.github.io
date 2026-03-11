---
name: memory-maintenance
description: 記憶維護：知識內化、記憶更新、記憶整理、優化記錄。每週執行一次，掃描最近 7 天的 daily logs，提取重要學習點、模式、洞察，更新 MEMORY.md、SOUL.md、topics/。在以下情況使用：(1) 每週定期記憶維護，(2) 完成重要項目後記錄優化成果，(3) 需要整理和歸類知識，(4) 清理過時記憶。
---

# Memory Maintenance

> 記憶維護系統：知識內化、記憶更新、記憶整理、優化記錄

## 概述

記憶維護是一個自動化的知識管理系統，用於：

1. **知識提取**：掃描 daily logs，提取學習點、模式、洞察
2. **記憶更新**：更新 MEMORY.md、SOUL.md、topics/
3. **記憶整理**：清理過時記憶，優化結構
4. **優化記錄**：記錄優化成果和關鍵決策

**執行頻率：** 每週一次（約 28 個 heartbeat）

**觸發方式：**
- 手動執行
- 心跳檢測到 7 天未執行
- 完成重要項目後（如系統優化 Phase 1）

---

## 快速開始

### 基本用法

```bash
# 執行完整的記憶維護流程
cd ~/.openclaw/workspace && python3 skills/memory-maintenance/scripts/maintain.py

# 只顯示計劃，不執行（dry run）
python3 skills/memory-maintenance/scripts/maintain.py --dry-run

# 跳過清理步驟
python3 skills/memory-maintenance/scripts/maintain.py --skip-cleanup

# 掃描最近 14 天（默認 7 天）
python3 skills/memory-maintenance/scripts/maintain.py --days 14
```

### 執行流程

記憶維護腳本會按順序執行以下步驟：

1. **掃描 daily logs** - 找出最近 N 天的記錄文件
2. **提取知識** - 從日誌中提取學習點、模式、決策、成就
3. **更新 MEMORY.md** - 更新主索引文件
4. **更新 SOUL.md** - 更新核心身份文件
5. **整理 topics/** - 統計和驗證主題文件
6. **清理舊記憶** - 清理超過 30 天的日誌
7. **生成報告** - 生成維護報告

---

## 工作流程

### 完整維護流程

```
1. 掃描 daily logs
   ↓
2. 提取知識（學習點、模式、決策、成就）
   ↓
3. 更新 MEMORY.md（主索引）
   ↓
4. 更新 SOUL.md（核心身份）
   ↓
5. 整理 topics/（主題分類）
   ↓
6. 清理舊記憶（>30 天）
   ↓
7. 生成維護報告
   ↓
8. 完成
```

---

## 知識提取

### 自動識別的標記

腳本會自動識別以下標記並提取內容：

| 標記 | 用途 | 目標文件 |
|------|------|----------|
| `### 我學到` | 今天學到的新知識 | SOUL.md |
| `### What I've Learned` | 學習總結 | SOUL.md |
| `### 學習總結` | 系統性學習記錄 | SOUL.md |
| `### 核心模式` | 可重用的框架 | topics/ |
| `### 關鍵洞察` | 深度理解 | topics/ |
| `### 可複用` | 可直接應用的模式 | topics/ |
| `### 關鍵決策` | 重要決策和理由 | MEMORY.md |
| `### 重要決策` | 重大方向調整 | MEMORY.md |
| `### Key Decisions` | 決策記錄 | MEMORY.md |
| `### 完成項目` | 項目完成 | MEMORY.md |
| `### 成就` | 重要成就 | MEMORY.md |
| `### 實證成果` | 可量化的成果 | MEMORY.md |

### 提取規則

1. **按日期分組**：每個 daily log 的知識按日期分組
2. **去重處理**：檢查知識是否已存在，避免重複
3. **智能過濾**：移除過時或無效的記憶
4. **結構化存儲**：將知識按類別組織（JSON 格式）

---

## 記憶更新

### MEMORY.md 更新

**更新內容：**
- Update Log：添加今天的維護記錄
- Recent Major Achievements：添加最新成就
- Key Decisions & Insights：添加關鍵決策

**更新規則：**
- 只添加今天的記錄（避免重複）
- 保留歷史記錄
- 更新版本號和日期

### SOUL.md 更新

**更新內容：**
- What I've Learned：添加今天學到的知識
- Tools I've building：添加新工具
- 版本和日期更新

**更新規則：**
- 只保留最近 5 個學習點
- 移除舊的學習點
- 更新版本號

### topics/ 整理

**整理內容：**
- 統計每個主題文件
- 驗證文件格式
- 檢查交叉引用

**整理規則：**
- 不刪除主題文件
- 不修改主題內容
- 只統計和驗證

---

## 記憶清理

### 清理規則

**保留：**
- 最近 30 天的 daily logs
- 所有 topics/ 文件
- MEMORY.md 和 SOUL.md

**清理：**
- 超過 30 天的詳細日誌
- 過時的技術細節
- 已解決的問題記錄

### 清理策略

1. **識別舊檔案**：找出超過 30 天的 daily logs
2. **備份**：在清理前備份（可選）
3. **刪除**：刪除舊檔案
4. **記錄**：在維護報告中記錄清理結果

---

## 維護報告

### 報告內容

維護報告包含以下內容：

1. **執行時間**：開始和結束時間
2. **統計摘要**：學習點、模式、決策、成就數量
3. **最近學習點**：列出具體內容
4. **最近模式**：列出具體模式
5. **清理結果**：清理了多少舊記憶

### 報告位置

報告保存在 `memory/maintenance-report-YYYYMMDD.md`

### 報告範例

```markdown
# 記憶維護報告

**執行時間:** 2026-03-05 03:00:00

## 📊 統計摘要

- 📚 學習點: 15 個
- 🔄 核心模式: 5 個
- 🎯 關鍵決策: 3 個
- 🏆 成就: 2 個

## 🔍 最近學習點

1. 2026-03-05
   背壓機制是必需品：可複用模式（監測 → 計算健康度 → 動態調整）

2. 2026-03-04
   Scout Reports 項目設計完成：106 KB 技術文檔

...
```

---

## 高級功能

### 自動化整合

**整合到 HEARTBEAT.md：**

在 HEARTBEAT.md 添加記憶維護任務：

```markdown
### Weekly: 記憶維護（每週執行）
```bash
# 執行記憶維護（知識內化、記憶更新、記憶整理）
cd ~/.openclaw/workspace && python3 skills/memory-maintenance/scripts/maintain.py
```

**What it does:**
- 掃描最近 7 天的 daily logs
- 提取重要的學習點、模式、洞察
- 更新 MEMORY.md、SOUL.md、topics/
- 清理過時記憶

**檢查頻率：** 每週一次（約 28 個 heartbeat）
```

---

### 自觸發規則

**條件：**
- 7 天未執行記憶維護
- 完成重要項目後（如系統優化 Phase 1）
- 手動執行

**執行方式：**
- 自動執行腳本
- 生成維護報告
- 通知用戶（如需要）

---

## 參考文件

### patterns.md

包含記憶維護中常用的模式和框架：

- **知識提取模式**：學習點、模式、決策、成就識別
- **記憶分類模式**：分層、去重、時效性
- **記憶整理模式**：清理規則、檢查清單
- **常見問題**：重複處理、層次決定、清理時機、質量驗證

**參考方式：**
```bash
cat ~/.openclaw/workspace/skills/memory-maintenance/references/patterns.md
```

---

## 最佳實踐

### 1. 定期執行

**建議頻率：** 每週一次

**理由：**
- 避免 daily logs 過多
- 及時提取新知識
- 保持記憶結構清晰

### 2. 使用標記

**在 daily logs 中使用統一標記：**

```markdown
### 我學到

**背壓機制（Backpressure）：**
- 可複用模式：監測 → 計算健康度 → 動態調整
```

### 3. 驗證輸出

**執行後檢查：**
- MEMORY.md 格式正確
- SOUL.md 格式正確
- topics/ 文件可讀
- 維護報告已生成

### 4. 備份重要記憶

**備份策略：**
- 使用 git 追蹤變更
- 定期推送到遠端倉庫
- 重要維護前手動備份

---

## 故障排除

### 問題 1：沒有找到 daily log 文件

**原因：**
- 路徑錯誤
- 日期範圍過小
- 文件格式錯誤

**解決方案：**
```bash
# 檢查路徑
ls -la ~/.openclaw/workspace/memory/

# 增加日期範圍
python3 skills/memory-maintenance/scripts/maintain.py --days 14
```

---

### 問題 2：知識提取失敗

**原因：**
- 標記格式不一致
- Markdown 格式錯誤
- 正則表達式匹配失敗

**解決方案：**
- 檢查 daily logs 格式
- 使用統一標記
- 查看錯誤日誌

---

### 問題 3：記憶文件損壞

**原因：**
- 磁碟空間不足
- 權限問題
- 並發寫入衝突

**解決方案：**
```bash
# 備份現有記憶
cp MEMORY.md MEMORY.md.backup
cp SOUL.md SOUL.md.backup

# 檢查磁碟空間
df -h

# 檢查權限
ls -la MEMORY.md
```

---

## 相關技能

- **HEARTBEAT.md** - 心跳驅動的任務系統
- **kanban-ops** - Kanban 任務管理
- **agent-output** - 子代理輸出格式
- **spawn-protocol** - 子代理啟動協議

---

**版本：** v1.0
**最後更新：** 2026-03-05
