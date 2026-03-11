# Programmer Sub-Agent 設計規劃

**文檔 ID:** a006-design-plan
**版本:** 1.0
**狀態:** Active
**創建日期:** 2026-02-21
**適用對象:** Programmer Sub-Agent 實施團隊
**基於文件:** a005-competencies.md, a006a-5.md, a006c-1.md

---

## 目錄

1. [概述和目標](#1-概述和目標)
2. [能力模型和技能矩陣](#2-能力模型和技能矩陣)
3. [實施路徑](#3-實施路徑)
4. [知識庫架構](#4-知識庫架構)
5. [工作流程和最佳實踐](#5-工作流程和最佳實踐)
6. [評估和持續改進機制](#6-評估和持續改進機制)
7. [風險管理和後備方案](#7-風險管理和後備方案)
8. [時間線和里程碑](#8-時間線和里程碑)

---

## 1. 概述和目標

### 1.1 項目背景

本設計規劃基於 Dashboard 量化交易系統的完整技術架構分析，旨在為 Programmer Sub-Agent 提供一套完整的能力建設和實施路徑。Dashboard 系統採用**前後端分離架構**、**統一策略引擎**、**微服務化後端**、**測試驅動開發**，具備**完善的 CI/CD 基礎設施**（待實施）和**嚴格的代碼規範**（100% Conventional Commits）。

### 1.2 核心目標

| 目標類別 | 具體目標 | 成功指標 |
|---------|---------|---------|
| **能力建設** | 建立從初級到架構師的完整能力模型 | 4 階段路徑覆蓋率 100% |
| **知識整合** | 統一後端、前端、策略引擎、Git 開發模式知識庫 | 知識庫覆蓋率 ≥ 95% |
| **質量保證** | 建立測試驅動開發和代碼審查文化 | 測試覆蓋率 ≥ 80%，審查通過率 ≥ 90% |
| **持續改進** | 建立評估機制和反饋循環 | 每季度評估一次，改進措施執行率 ≥ 80% |
| **風險管理** | 識別和緩解實施風險 | 風險緩解覆蓋率 100% |

### 1.3 設計原則

本實施規劃基於以下核心原則：

| 原則 | 說明 |
|------|------|
| **漸進式複雜度** | 從簡單的 CRUD 開始，逐步增加到複雜的策略架構 |
| **測試驅動** | 每個階段都強調 TDD，確保代碼質量 |
| **實踐優先** | 通過實際項目和代碼示例學習，而非理論堆砌 |
| **知識整合** | 前後端、策略引擎、數據庫知識逐步融合 |
| **反饋循環** | 每個階段都有明確的驗證標準和評估機制 |

### 1.4 架構概覽

```
┌─────────────────────────────────────────────────────────────────┐
│                        前端層 (Frontend)                        │
│  React 19 + Vite + Zustand + React Query + Bootstrap 5        │
├─────────────────────────────────────────────────────────────────┤
│                        API 網關層 (API Gateway)                   │
│  FastAPI Middleware (Auth, CORS, Rate Limit)                   │
├─────────────────────────────────────────────────────────────────┤
│                        後端服務層 (Backend Services)             │
│  策略服務 | 市場數據服務 | 分析服務 | 執行服務                  │
├─────────────────────────────────────────────────────────────────┤
│                        策略引擎層 (Strategy Engine)              │
│  IStrategy 接口 | VectorBT | Backtrader | Signal Adapter      │
├─────────────────────────────────────────────────────────────────┤
│                        數據存儲層 (Storage)                      │
│  PostgreSQL | DuckDB | Redis | File System                    │
├─────────────────────────────────────────────────────────────────┤
│                        開發工具層 (DevTools)                    │
│  Git | GitHub Actions | Docker | pytest | Vitest               │
└─────────────────────────────────────────────────────────────────┘
```

### 1.5 預期成果

- **文檔成果**: 完整的設計規劃文檔，包含 8 個章節和具體執行計劃
- **能力成果**: 清晰的能力模型和技能矩陣，支持 4 階段能力建設
- **實施成果**: 可執行的實施路徑，包含 8-9 週初級、10-11 週中級、12-16 週高級、持續架構師階段
- **質量成果**: 測試驅動開發文化和代碼審查機制
- **風險成果**: 完整的風險識別和後備方案

---

## 2. 能力模型和技能矩陣

### 2.1 能力模型總覽

基於 a005-competencies.md 的高級架構師能力定義，能力模型分為 4 個層級：

| 層級 | 時間範圍 | 代碼能力 | 架構能力 | 測試能力 | 領域知識 | 領導力 |
|------|---------|---------|---------|---------|---------|--------|
| **初級開發者** | 0-3 個月 | P0 基礎 | 理解分層 | TDD 基礎 | 基礎概念 | 無 |
| **中級開發者** | 3-6 個月 | P0+P1 | 設計 API | 集成測試 | 技術指標 | 代碼審查 |
| **高級開發者** | 6-12 個月 | P0+P1+P2 | 微服務 | E2E 測試 | 策略引擎 | 技術指導 |
| **高級架構師** | 12+ 個月 | P0-P3 全部 | 架構演進 | 測試策略 | 跨領域 | 技術領導 |

### 2.2 技能優先級層級

```
┌─────────────────────────────────────────────────────┐
│ P0 (必備) - 基礎生存技能                             │
│ Python/FastAPI, React 19, 測試驅動開發, Git 提交規範 │
├─────────────────────────────────────────────────────┤
│ P1 (重要) - 核心開發技能                             │
│ VectorBT/Backtrader, Zustand, React Query, 策略引擎  │
├─────────────────────────────────────────────────────┤
│ P2 (可選) - 進階技能                                 │
│ Three.js, Celery, 高級圖表, 性能優化                 │
├─────────────────────────────────────────────────────┤
│ P3 (未來擴展) - 專家技能                             │
│ 機器學習, 實時數據流, Kubernetes, 架構設計           │
└─────────────────────────────────────────────────────┘
```

### 2.3 初級開發者技能矩陣 (0-3 個月)

#### 後端開發 (P0)

| 技能 | 內容 | 掌握程度 | 驗證方式 |
|------|------|---------|---------|
| **Python 基礎** | 數據類型、函數、類、異步編程 | ⭐⭐⭐⭐⭐ | 代碼審查 |
| **FastAPI 基礎** | 路由、依賴注入、請求/響應模型 | ⭐⭐⭐⭐⭐ | 單元測試 |
| **Pydantic 驗證** | 數據模型、驗證規則、錯誤處理 | ⭐⭐⭐⭐⭐ | 測試覆蓋率 |
| **DuckDB 基礎** | 連接、查詢、CRUD 操作 | ⭐⭐⭐⭐ | 集成測試 |
| **錯誤處理** | 自定義異常、全局異常處理器 | ⭐⭐⭐⭐ | 代碼審查 |

#### 前端開發 (P0)

| 技能 | 內容 | 掌握程度 | 驗證方式 |
|------|------|---------|---------|
| **React 19 基礎** | 函數組件、Hooks (useState, useEffect) | ⭐⭐⭐⭐⭐ | 組件測試 |
| **Bootstrap 5** | 響應式佈局、組件使用 | ⭐⭐⭐⭐ | UI 審查 |
| **Axios** | HTTP 客戶端配置、GET/POST/PUT/DELETE | ⭐⭐⭐⭐⭐ | 測試 Mock |
| **狀態管理基礎** | useState, useContext | ⭐⭐⭐⭐ | 單元測試 |
| **表單處理** | 受控組件、表單驗證 | ⭐⭐⭐⭐ | E2E 測試 |

#### 測試驅動開發 (P0)

| 技能 | 內容 | 掌握程度 | 驗證方式 |
|------|------|---------|---------|
| **pytest 基礎** | 測試編寫、fixture、mock | ⭐⭐⭐⭐⭐ | 測試覆蓋率 |
| **vitest 基礎** | 單元測試、組件測試 | ⭐⭐⭐⭐ | 測試覆蓋率 |
| **TDD 流程** | Red-Green-Refactor | ⭐⭐⭐⭐⭐ | 代碼審查 |
| **AAA 模式** | Arrange-Act-Assert | ⭐⭐⭐⭐⭐ | 測試審查 |
| **測試覆蓋率** | pytest-cov, vitest coverage | ⭐⭐⭐ | CI/CD 報告 |

#### Git 開發規範 (P0)

| 技能 | 內容 | 掌握程度 | 驗證方式 |
|------|------|---------|---------|
| **Conventional Commits** | feat/fix/refactor/docs/chore | ⭐⭐⭐⭐⭐ | Git 歷史檢查 |
| **分支管理** | feature 分支創建、合併 | ⭐⭐⭐⭐ | PR 審查 |
| **PR 流程** | Pull Request 創建、審查 | ⭐⭐⭐⭐ | PR 審查記錄 |

### 2.4 中級開發者技能矩陣 (3-6 個月)

#### 回測引擎 (P1)

| 技能 | 內容 | 掌握程度 | 驗證方式 |
|------|------|---------|---------|
| **VectorBT 基礎** | 數據加載、信號生成、組合創建 | ⭐⭐⭐⭐⭐ | 回測結果驗證 |
| **Backtrader 基礎** | Cerebro、策略類、數據 feed | ⭐⭐⭐⭐ | 回測對比 |
| **績效指標計算** | Sharpe Ratio、Max Drawdown、Win Rate | ⭐⭐⭐⭐ | 指標驗證 |
| **參數優化** | 網格搜索、並行回測 | ⭐⭐⭐ | 優化結果 |

#### 策略引擎 (P1)

| 技能 | 內容 | 掌握程度 | 驗證方式 |
|------|------|---------|---------|
| **IStrategy 接口** | generate_signals 實現 | ⭐⭐⭐⭐⭐ | 接口契約測試 |
| **策略模式** | 工廠模式、適配器模式、組合策略 | ⭐⭐⭐⭐ | 設計審查 |
| **信號處理** | 信號生成、合併、過濾 | ⭐⭐⭐⭐ | 信號測試 |
| **策略工廠** | 策略註冊、實例化 | ⭐⭐⭐⭐ | 工廠測試 |

#### 狀態管理 (P1)

| 技能 | 內容 | 掌握程度 | 驗證方式 |
|------|------|---------|---------|
| **Zustand** | Store 定義、actions、selectors | ⭐⭐⭐⭐⭐ | Store 測試 |
| **React Query** | useApiCache、useApiMutation、cache 管理 | ⭐⭐⭐⭐⭐ | 緩存測試 |
| **狀態分類原則** | 全局狀態、服務端狀態、本地狀態 | ⭐⭐⭐⭐ | 代碼審查 |
| **快取策略** | staleTime、gcTime、invalidate | ⭐⭐⭐⭐ | 性能測試 |

#### 集成測試 (P1)

| 技能 | 內容 | 掌握程度 | 驗證方式 |
|------|------|---------|---------|
| **API 集成測試** | 端到端 API 測試 | ⭐⭐⭐⭐ | CI/CD 報告 |
| **E2E 測試** | Cypress 測試流程 | ⭐⭐⭐ | E2E 報告 |
| **測試數據庫** | 測試環境數據庫設置 | ⭐⭐⭐ | 測試環境驗證 |

### 2.5 高級開發者技能矩陣 (6-12 個月)

#### 複合策略 (P2)

| 技能 | 內容 | 掌握程度 | 驗證方式 |
|------|------|---------|---------|
| **組合策略** | CompositeStrategy、多策略組合 | ⭐⭐⭐⭐⭐ | 回測驗證 |
| **信號合併算法** | 多數決、一緻同意、加權投票 | ⭐⭐⭐⭐ | 算法測試 |
| **策略共識機制** | 信號共振、多指標匯合 | ⭐⭐⭐ | 共識測試 |
| **策略優化** | 參數掃描、網格搜索 | ⭐⭐⭐ | 優化結果 |

#### 性能優化 (P2)

| 技能 | 內容 | 掌握程度 | 驗證方式 |
|------|------|---------|---------|
| **向量化優化** | NumPy、pandas 向量化操作 | ⭐⭐⭐⭐⭐ | 性能基準測試 |
| **緩存優化** | Redis 緩存、React Query 緩存 | ⭐⭐⭐⭐ | 緩存命中率 |
| **數據庫優化** | 索引、查詢優化、批量操作 | ⭐⭐⭐⭐ | 查詢性能 |
| **並行處理** | pytest-xdist、多進程回測 | ⭐⭐⭐ | 並行效率 |

#### E2E 測試 (P2)

| 技能 | 內容 | 掌握程度 | 驗證方式 |
|------|------|---------|---------|
| **Cypress 測試** | 完整用戶流程測試 | ⭐⭐⭐⭐⭐ | E2E 報告 |
| **測�试策略** | 測試金字塔、測試優先級 | ⭐⭐⭐⭐ | 測試計劃審查 |
| **測試數據管理** | 測試數據工廠、數據清理 | ⭐⭐⭐ | 測試穩定性 |

#### 技術指導 (P2)

| 技能 | 內容 | 掌握程度 | 驗證方式 |
|------|------|---------|---------|
| **代碼審查** | 建設性反饋、最佳實踐指導 | ⭐⭐⭐⭐⭐ | 審查記錄 |
| **技術分享** | 技術講座、文檔編寫 | ⭐⭐⭐⭐ | 分享記錄 |
| **導師制度** | 導師計劃、技能傳承 | ⭐⭐⭐ | 導師評估 |

### 2.6 高級架構師技能矩陣 (12+ 個月)

#### 系統架構 (P3)

| 技能 | 內容 | 掌握程度 | 驗證方式 |
|------|------|---------|---------|
| **微服務架構** | 服務拆分、服務間通信 | ⭐⭐⭐⭐⭐ | 架構審查 |
| **API 設計** | RESTful、GraphQL、版本化 | ⭐⭐⭐⭐⭐ | API 設計審查 |
| **數據架構** | 數據庫設計、數據流設計 | ⭐⭐⭐⭐⭐ | 架構審查 |
| **可擴展性設計** | 水平擴展、垂直擴展 | ⭐⭐⭐⭐ | 擴展性測試 |

#### 技術決策 (P3)

| 技能 | 內容 | 掌握程度 | 驗證方式 |
|------|------|---------|---------|
| **技術選型** | 框架和庫選型 | ⭐⭐⭐⭐⭐ | ADR 文檔 |
| **性能決策** | 性能優化決策 | ⭐⭐⭐⭐ | 性能報告 |
| **安全決策** | 安全性決策 | ⭐⭐⭐⭐ | 安全審計 |
| **技術債管理** | 識別和償還技術債 | ⭐⭐⭐⭐ | 技術債報告 |

#### 架構演進 (P3)

| 技能 | 內容 | 掌握程度 | 驗證方式 |
|------|------|---------|---------|
| **重構策略** | 漸進式重構、大重壓 | ⭐⭐⭐⭐⭐ | 重構計劃 |
| **架構優化** | 架構層次優化 | ⭐⭐⭐⭐ | 優化效果 |
| **遷移計劃** | 技術遷移、數據遷移 | ⭐⭐⭐ | 遷移計劃 |

#### 技術領導 (P3)

| 技能 | 內容 | 掌握程度 | 驗證方式 |
|------|------|---------|---------|
| **技術路線圖** | 技術發展路線圖制定 | ⭐⭐⭐⭐⭐ | 路線圖審查 |
| **團隊建設** | 技術團隊建設 | ⭐⭐⭐⭐ | 團隊評估 |
| **技術文化** | 建立技術文化 | ⭐⭐⭐⭐ | 文化評估 |

---

## 3. 實施路徑

本實施路徑基於 a006c-1.md 的 4 階段框架，整合所有前期成果。

### 3.1 階段間依賴關係

```
階段 1: 初級 (0-3個月)
   ↓ [必須完成]
階段 2: 中級 (3-6個月)
   ↓ [必須完成]
階段 3: 高級 (6-12個月)
   ↓ [必須完成]
階段 4: 架構師 (12+個月)

每個階段的驗證標準是下一階段的入門門檻
```

### 3.2 階段 1: 初級開發者 (0-3 個月)

#### 3.2.1 核心學習目標

1. **掌握全棧基礎技能**：能夠獨立完成簡單的前後端功能
2. **建立測試驅動開發習慣**：TDD 成為開發的默認模式
3. **理解系統架構**：掌握分層架構和 API 設計基本概念
4. **熟悉開發工作流**：Git 提交規範、代碼審查流程

#### 3.2.2 可執行的實踐任務

##### 任務 1.1: 創建第一個 API 端點 (1 週)

**目標**: 實現完整的 CRUD API

**後端實現** (參考 a006c-1.md):
```python
# backend/routers/items.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import duckdb

router = APIRouter(prefix="/api/v1/items", tags=["Items"])

class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    price: float = Field(..., gt=0)

class ItemResponse(ItemCreate):
    id: int
    created_at: str

@router.post("/", response_model=ItemResponse)
async def create_item(item: ItemCreate, db=Depends(get_db)):
    """創建新項目"""
    result = db.execute("""
        INSERT INTO items (name, description, price, created_at)
        VALUES (?, ?, ?, NOW())
        RETURNING id, name, description, price, created_at
    """, (item.name, item.description, item.price)).fetchone()

    return ItemResponse(
        id=result[0],
        name=result[1],
        description=result[2],
        price=result[3],
        created_at=str(result[4])
    )

@router.get("/", response_model=List[ItemResponse])
async def list_items(skip: int = 0, limit: int = 10, db=Depends(get_db)):
    """列出項目"""
    results = db.execute("""
        SELECT id, name, description, price, created_at
        FROM items
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
    """, (limit, skip)).fetchall()

    return [
        ItemResponse(id=r[0], name=r[1], description=r[2],
                     price=r[3], created_at=str(r[4]))
        for r in results
    ]

@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int, db=Depends(get_db)):
    """獲取單個項目"""
    result = db.execute("""
        SELECT id, name, description, price, created_at
        FROM items WHERE id = ?
    """, (item_id,)).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Item not found")

    return ItemResponse(id=result[0], name=result[1], description=result[2],
                       price=result[3], created_at=str(result[4]))

@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(item_id: int, item: ItemCreate, db=Depends(get_db)):
    """更新項目"""
    result = db.execute("""
        UPDATE items
        SET name = ?, description = ?, price = ?
        WHERE id = ?
        RETURNING id, name, description, price, created_at
    """, (item.name, item.description, item.price, item_id)).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Item not found")

    return ItemResponse(id=result[0], name=result[1], description=result[2],
                       price=result[3], created_at=str(result[4]))

@router.delete("/{item_id}")
async def delete_item(item_id: int, db=Depends(get_db)):
    """刪除項目"""
    db.execute("DELETE FROM items WHERE id = ?", (item_id,))
    return {"message": "Item deleted"}
```

**前端實現** (參考 a006c-1.md):
```jsx
// frontend/src/pages/ItemsPage/index.jsx
import React, { useState } from 'react';
import { useApiCache, useApiMutation } from '../../hooks/useApiCache';

const ItemsPage = () => {
  const [showModal, setShowModal] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [formData, setFormData] = useState({ name: '', description: '', price: '' });

  // 獲取項目列表
  const { data: items, isLoading, error, refetch } = useApiCache(
    ['items'],
    () => fetch('/api/v1/items').then(r => r.json())
  );

  // 創建項目
  const { mutate: createItem, isLoading: isCreating } = useApiMutation(
    (data) => fetch('/api/v1/items', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(r => r.json()),
    {
      invalidateKeys: [['items']],
      onSuccess: () => {
        setShowModal(false);
        setFormData({ name: '', description: '', price: '' });
      }
    }
  );

  // 更新項目
  const { mutate: updateItem, isLoading: isUpdating } = useApiMutation(
    ({ id, data }) => fetch(`/api/v1/items/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }).then(r => r.json()),
    {
      invalidateKeys: [['items']],
      onSuccess: () => {
        setShowModal(false);
        setEditingItem(null);
        setFormData({ name: '', description: '', price: '' });
      }
    }
  );

  // 刪除項目
  const { mutate: deleteItem } = useApiMutation(
    (id) => fetch(`/api/v1/items/${id}`, { method: 'DELETE' }).then(r => r.json()),
    {
      invalidateKeys: [['items']]
    }
  );

  const handleSubmit = (e) => {
    e.preventDefault();
    const data = {
      name: formData.name,
      description: formData.description || null,
      price: parseFloat(formData.price)
    };

    if (editingItem) {
      updateItem({ id: editingItem.id, data });
    } else {
      createItem(data);
    }
  };

  const handleEdit = (item) => {
    setEditingItem(item);
    setFormData({
      name: item.name,
      description: item.description || '',
      price: item.price.toString()
    });
    setShowModal(true);
  };

  if (isLoading && !items) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div className="container-fluid py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Items Management</h1>
        <button
          className="btn btn-primary"
          onClick={() => {
            setEditingItem(null);
            setFormData({ name: '', description: '', price: '' });
            setShowModal(true);
          }}
        >
          Add New Item
        </button>
      </div>

      <table className="table table-striped">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Description</th>
            <th>Price</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {items?.map(item => (
            <tr key={item.id}>
              <td>{item.id}</td>
              <td>{item.name}</td>
              <td>{item.description || '-'}</td>
              <td>${item.price.toFixed(2)}</td>
              <td>
                <button
                  className="btn btn-sm btn-outline-primary me-2"
                  onClick={() => handleEdit(item)}
                >
                  Edit
                </button>
                <button
                  className="btn btn-sm btn-outline-danger"
                  onClick={() => deleteItem(item.id)}
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {showModal && (
        <div className="modal show" style={{ display: 'block' }}>
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">
                  {editingItem ? 'Edit Item' : 'Add New Item'}
                </h5>
                <button
                  type="button"
                  className="btn-close"
                  onClick={() => setShowModal(false)}
                />
              </div>
              <div className="modal-body">
                <form onSubmit={handleSubmit}>
                  <div className="mb-3">
                    <label className="form-label">Name</label>
                    <input
                      type="text"
                      className="form-control"
                      value={formData.name}
                      onChange={(e) => setFormData({...formData, name: e.target.value})}
                      required
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Description</label>
                    <textarea
                      className="form-control"
                      value={formData.description}
                      onChange={(e) => setFormData({...formData, description: e.target.value})}
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Price</label>
                    <input
                      type="number"
                      step="0.01"
                      className="form-control"
                      value={formData.price}
                      onChange={(e) => setFormData({...formData, price: e.target.value})}
                      required
                    />
                  </div>
                </form>
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowModal(false)}
                >
                  Cancel
                </button>
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={handleSubmit}
                  disabled={isCreating || isUpdating}
                >
                  {isCreating || isUpdating ? 'Saving...' : 'Save'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ItemsPage;
```

**驗證標準**:
- [ ] 所有 API 端點有完整的單元測試（覆蓋率 ≥ 80%）
- [ ] 所有前端組件有組件測試
- [ ] 前後端能夠正確交互
- [ ] 能夠處理常見錯誤情況

##### 任務 1.2: 實現簡單的技術指標計算 (1 週)

**目標**: 掌握 pandas 數據處理和技術指標計算

**實現示例** (參考 a006c-1.md):
```python
# backend/indicators/simple_rsi.py
import pandas as pd
import numpy as np

class SimpleRSI:
    """簡單的 RSI 計算實現"""

    def __init__(self, period: int = 14):
        if period <= 0:
            raise ValueError("Period must be positive")
        self.period = period

    def calculate(self, prices: pd.Series) -> pd.Series:
        """
        計算 RSI 指標

        Args:
            prices: 價格序列

        Returns:
            RSI 值序列
        """
        # 計算價格變化
        delta = prices.diff()

        # 分離漲跌幅
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)

        # 計算平均漲跌幅（簡單移動平均）
        avg_gains = gains.rolling(window=self.period).mean()
        avg_losses = losses.rolling(window=self.period).mean()

        # 避免除以零
        avg_losses = avg_losses.replace(0, np.nan)

        # 計算 RSI
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))

        return rsi
```

**驗證標準**:
- [ ] RSI 計算正確（對比標準庫）
- [ ] 處理極值情況
- [ ] 測試覆蓋率 ≥ 80%

##### 任務 1.3: Git 提交規範練習 (持續)

**練習**: 對所有任務使用 Conventional Commits

```bash
# 功能開發
git commit -m "feat(items): add CRUD API for items management"
git commit -m "feat(indicators): implement simple RSI calculation"

# Bug 修復
git commit -m "fix(items): handle empty items list gracefully"

# 重構
git commit -m "refactor(items): extract validation logic to separate function"

# 文檔
git commit -m "docs(items): add API documentation for items endpoint"

# 測試
git commit -m "test(items): add comprehensive tests for items API"

# 樣式
git commit -m "style(items): format code with black and ruff"
```

**驗證標準**:
- [ ] 所有提交遵循 Conventional Commits 規範（100%）
- [ ] 提交信息清晰且具體
- [ ] 無"WIP"或臨時提交

#### 3.2.3 預估學習時間

| 任務類別 | 預估時間 | 優先級 |
|---------|---------|--------|
| Python/FastAPI 基礎 | 2 週 | P0 |
| React 19 基礎 | 2 週 | P0 |
| 測試驅動開發 | 1 週 | P0 |
| DuckDB 基礎 | 3 天 | P0 |
| Git 規範 | 2 天 | P0 |
| 實踐項目 (任務 1.1-1.3) | 4 週 | P0 |
| **總計** | **8-9 週** | |

#### 3.2.4 驗證標準

**代碼質量驗證**:
- [ ] 所有 API 端點有完整的單元測試（覆蓋率 ≥ 80%）
- [ ] 所有前端組件有組件測試
- [ ] 所有提交遵循 Conventional Commits 規範（100%）
- [ ] 代碼通過 linter 檢查（ruff, eslint）
- [ ] 代碼通過格式化工具（black, prettier）

**功能驗證**:
- [ ] 能夠獨立完成完整的 CRUD API 實現
- [ ] 能夠實現簡單的技術指標計算
- [ ] 前後端能夠正確交互
- [ ] 能夠處理常見錯誤情況

**知識驗證**:
- [ ] 能夠解釋分層架構的概念
- [ ] 能夠解釋 TDD 的 Red-Green-Refactor 流程
- [ ] 能夠解釋 RESTful API 的設計原則
- [ ] 能夠閱讀和理解現有代碼

**通過標準**: 所有檢查項目必須完成，並且通過代碼審查

### 3.3 階段 2: 中級開發者 (3-6 個月)

#### 3.3.1 核心學習目標

1. **掌握回測引擎使用**：能夠使用 VectorBT 和 Backtrader 進行策略回測
2. **理解策略引擎架構**：掌握 IStrategy 接口和策略模式
3. **熟練狀態管理**：精通 Zustand 和 React Query
4. **建立代碼審查能力**：能夠審查他人代碼並提供建設性反饋

#### 3.3.2 可執行的實踐任務

##### 任務 2.1: 實現完整的 RSI 策略 (2 週)

**目標**: 掌握 IStrategy 接口和 VectorBT 回測

**策略實現** (參考 a006a-5.md 和 a006c-1.md):
```python
# backend/strategies/rsi_strategy.py
from .base import IStrategy, Signal, SignalAction, ExecutionContext
from datetime import date, timedelta
from typing import List
import pandas as pd
import pandas_ta as ta

class RSIStrategy(IStrategy):
    """RSI 均值回歸策略"""

    name = "rsi_mean_reversion"

    def __init__(
        self,
        period: int = 14,
        buy_threshold: float = 30,
        sell_threshold: float = 70,
        min_trade_size: float = 1000.0
    ):
        if not (0 < buy_threshold < sell_threshold < 100):
            raise ValueError("Invalid threshold values")
        if period <= 0:
            raise ValueError("Period must be positive")

        self.period = period
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold
        self.min_trade_size = min_trade_size
        self.rsi_cache = {}

    def generate_signals(
        self,
        context: ExecutionContext,
        symbols: List[str]
    ) -> List[Signal]:
        """生成交易信號"""
        signals = []

        for symbol in symbols:
            # 檢查市場狀態
            if context.market_status != 'CLOSED':
                continue

            # 檢查是否已持有
            existing_position = next(
                (p for p in context.current_positions if p.symbol == symbol),
                None
            )

            # 獲取 RSI 值
            rsi = self._get_rsi(symbol, context.market_date)

            if pd.isna(rsi):
                continue

            # 生成買入信號（僅當未持有時）
            if rsi < self.buy_threshold and not existing_position:
                confidence = self._calculate_confidence(rsi, self.buy_threshold)
                if confidence >= 0.5:  # 只在信心高於 50% 時交易
                    signals.append(Signal(
                        symbol=symbol,
                        action=SignalAction.BUY,
                        confidence=confidence,
                        reason=f"RSI ({rsi:.2f}) below buy threshold ({self.buy_threshold})"
                    ))

            # 生成賣出信號（僅當持有时）
            elif rsi > self.sell_threshold and existing_position:
                confidence = self._calculate_confidence(rsi, self.sell_threshold)
                if confidence >= 0.5:
                    signals.append(Signal(
                        symbol=symbol,
                        action=SignalAction.SELL,
                        confidence=confidence,
                        reason=f"RSI ({rsi:.2f}) above sell threshold ({self.sell_threshold})"
                    ))

        return signals

    def _get_rsi(self, symbol: str, date: date) -> float:
        """獲取 RSI 值並緩存"""
        cache_key = f"{symbol}_{date}"

        if cache_key not in self.rsi_cache:
            # 使用 pandas-ta 計算 RSI
            prices = self._load_prices(symbol, date - timedelta(days=self.period * 3), date)

            if len(prices) < self.period:
                return float('nan')

            rsi_values = ta.momentum.RSIIndicator(prices['close'], window=self.period).rsi()
            self.rsi_cache[cache_key] = rsi_values.iloc[-1] if len(rsi_values) > 0 else float('nan')

        return self.rsi_cache[cache_key]

    def _load_prices(self, symbol: str, start_date: date, end_date: date) -> pd.DataFrame:
        """從數據庫加載價格數據"""
        # 實際實現會從數據庫查詢
        pass

    def _calculate_confidence(self, rsi: float, threshold: float) -> float:
        """根據距離閾值的距離計算信心分數"""
        if rsi < threshold:  # 買入情況
            return min(1.0, (threshold - rsi) / threshold)
        else:  # 賣出情況
            return min(1.0, (rsi - threshold) / (100 - threshold))
```

**VectorBT 回測實現** (參考 a006a-5.md):
```python
# backend/backtest/vectorbt_executor.py
import vectorbt as vbt
import pandas as pd
from typing import List, Dict, Any
from datetime import date
from backend.strategies.rsi_strategy import RSIStrategy

class VectorBTExecutor:
    """VectorBT 回測執行器"""

    def __init__(self, data_loader):
        self.data_loader = data_loader

    def run_backtest(
        self,
        strategy: RSIStrategy,
        symbols: List[str],
        start_date: date,
        end_date: date,
        initial_cash: float = 100000
    ) -> Dict[str, Any]:
        """執行回測"""

        # 1. 加載數據
        prices = self.data_loader.load_prices(symbols, start_date, end_date)

        # 2. 生成 RSI 指標
        rsi_values = self._calculate_rsi_vectorized(prices, strategy.period)

        # 3. 生成信號
        entries, exits = self._generate_signals(rsi_values, strategy)

        # 4. 創建組合
        pf = vbt.Portfolio.from_signals(
            prices,
            entries=entries,
            exits=exits,
            init_cash=initial_cash,
            fees=0.001,
            slippage=0.0001,
            freq='1D'
        )

        # 5. 提取指標
        stats = pf.stats()

        return {
            'strategy': strategy.name,
            'symbols': symbols,
            'start_date': str(start_date),
            'end_date': str(end_date),
            'initial_cash': initial_cash,
            'final_value': float(pf.value().iloc[-1]),
            'total_return': float(stats['total_return']),
            'sharpe_ratio': float(stats['sharpe_ratio']),
            'max_drawdown': float(stats['max_drawdown']),
            'win_rate': float(stats['win_rate']),
            'num_trades': int(stats['num_trades']),
            'equity_curve': pf.value().tolist()
        }

    def _calculate_rsi_vectorized(
        self,
        prices: pd.DataFrame,
        period: int
    ) -> pd.DataFrame:
        """向量化計算 RSI"""
        rsi_values = pd.DataFrame(index=prices.index, columns=prices.columns)

        for symbol in prices.columns:
            rsi_values[symbol] = ta.momentum.RSIIndicator(
                prices[symbol],
                window=period
            ).rsi()

        return rsi_values

    def _generate_signals(
        self,
        rsi_values: pd.DataFrame,
        strategy: RSIStrategy
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """生成進入和退出信號"""
        entries = rsi_values.lt(strategy.buy_threshold)
        exits = rsi_values.gt(strategy.sell_threshold)

        return entries, exits
```

**驗證標準**:
- [ ] 策略實現遵循 IStrategy 接口契約
- [ ] 回測結果正確（對比手動計算）
- [ ] 測試覆蓋率 ≥ 85%
- [ ] 性能優化（向量化計算）

##### 任務 2.2: 實現策略工廠 (1 週)

**目標**: 掌握工廠模式和策略註冊機制

**工廠實現** (參考 a006a-5.md 和 a006c-1.md):
```python
# backend/strategies/factory.py
from typing import Dict, Type, Any
from .base import IStrategy
from .rsi_strategy import RSIStrategy

class StrategyFactory:
    """策略工廠"""

    _strategies: Dict[str, Type[IStrategy]] = {}

    @classmethod
    def register(cls, strategy_type: str, strategy_class: Type[IStrategy]):
        """註冊策略類"""
        if strategy_type in cls._strategies:
            raise ValueError(f"Strategy type {strategy_type} already registered")
        cls._strategies[strategy_type] = strategy_class

    @classmethod
    def create(cls, strategy_type: str, params: Dict[str, Any] = None) -> IStrategy:
        """創建策略實例"""
        params = params or {}

        if strategy_type not in cls._strategies:
            raise ValueError(f"Unknown strategy type: {strategy_type}")

        strategy_class = cls._strategies[strategy_type]
        return strategy_class(**params)

    @classmethod
    def list_strategies(cls) -> list:
        """列出所有已註冊的策略類型"""
        return list(cls._strategies.keys())

# 註冊內置策略
StrategyFactory.register("rsi", RSIStrategy)
```

**驗證標準**:
- [ ] 工廠模式正確實現
- [ ] 策略註冊和創建正常工作
- [ ] 錯誤處理完善
- [ ] 測試覆蓋率 ≥ 85%

##### 任務 2.3: 實現 React Query 緩存管理 (1 週)

**目標**: 掌握 React Query 的緩存和狀態管理

**實現** (參考 a006a-5.md 和 a006c-1.md):
```javascript
// frontend/src/hooks/useApiCache.js
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-toastify';

// 緩存預設
export const cachePresets = {
  static: {
    staleTime: 60 * 60 * 1000,      // 1 小時
    gcTime: 24 * 60 * 60 * 1000,   // 24 小時
  },
  user: {
    staleTime: 5 * 60 * 1000,      // 5 分鐘
    gcTime: 30 * 60 * 1000,        // 30 分鐘
  },
  dynamic: {
    staleTime: 30 * 1000,         // 30 秒
    gcTime: 5 * 60 * 1000,        // 5 分鐘
  },
  realtime: {
    staleTime: 0,
    gcTime: 0,
  },
};

export const useApiCache = (queryKey, fetcher, options = {}) => {
  const {
    staleTime = cachePresets.user.staleTime,
    gcTime = cachePresets.user.gcTime,
    ...restOptions
  } = options;

  return useQuery({
    queryKey,
    queryFn: fetcher,
    staleTime,
    gcTime,
    retry: 1,
    ...restOptions,
  });
};

export const useApiMutation = (mutationFn, options = {}) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn,
    onSuccess: (data, variables, context) => {
      // 使相關查詢失效
      if (options.invalidateKeys) {
        options.invalidateKeys.forEach(key => {
          queryClient.invalidateQueries(key);
        });
      }
      // 調用成功回調
      if (options.onSuccess) {
        options.onSuccess(data, variables, context);
      }
    },
    onError: (error) => {
      // 顯示錯誤通知
      const message = error.response?.data?.detail || error.message || 'Operation failed';
      toast.error(message);
      if (options.onError) {
        options.onError(error);
      }
    },
  });
};

// 緩存工具
export const cacheUtils = {
  invalidate: (key) => {
    queryClient.invalidateQueries(key);
  },

  clear: () => {
    queryClient.clear();
  },

  prefetch: async (key, fetcher) => {
    await queryClient.prefetchQuery(key, fetcher);
  },

  getData: (key) => {
    return queryClient.getQueryData(key);
  },

  setData: (key, data) => {
    queryClient.setQueryData(key, data);
  },
};
```

**驗證標準**:
- [ ] 緩存預設正確配置
- [ ] 緩存失效邏輯正確
- [ ] 錯誤處理完善
- [ ] 測試覆蓋率 ≥ 85%

##### 任務 2.4: 實現 Zustand Store (1 週)

**目標**: 掌握 Zustand 全局狀態管理

**實現** (參考 a006a-5.md 和 a006c-1.md):
```javascript
// frontend/src/store/dashboardStore.js
import { create } from 'zustand';

const useDashboardStore = create((set, get) => ({
  // 狀態
  watchlist: [],
  marketMovers: {
    gainers: [],
    losers: [],
    most_active: []
  },
  heatmapData: [],
  marketScore: {
    current: null,
    history: []
  },
  stockDetails: {},
  loadingStatus: 'idle', // idle, loading, success, error
  error: null,
  lastUpdated: null,

  // Actions
  fetchStage1Overview: async (force = false, targetDate = null, market = 'US') => {
    const { loadingStatus, lastUpdated } = get();

    // 檢查是否需要重新獲取
    if (!force && loadingStatus === 'success') {
      const now = new Date();
      const lastUpdatedTime = lastUpdated ? new Date(lastUpdated) : null;
      if (lastUpdatedTime && (now - lastUpdatedTime) < 5 * 60 * 1000) {
        return; // 5 分鐘內不重新獲取
      }
    }

    set({ loadingStatus: 'loading', error: null });

    try {
      // 並行獲取數據
      const [movers, heatmap, score] = await Promise.all([
        fetch(`/api/v1/market/movers?market=${market}`).then(r => r.json()),
        fetch(`/api/v1/market/heatmap?targetDate=${targetDate}&market=${market}`).then(r => r.json()),
        fetch('/api/v1/market/score').then(r => r.json())
      ]);

      set({
        marketMovers: movers,
        heatmapData: heatmap,
        marketScore: score,
        loadingStatus: 'success',
        error: null,
        lastUpdated: new Date().toISOString()
      });
    } catch (error) {
      set({
        error: error.message,
        loadingStatus: 'error'
      });
    }
  },

  addWatchlistItem: (symbol) => {
    const watchlist = get().watchlist;
    if (!watchlist.includes(symbol)) {
      set({ watchlist: [...watchlist, symbol] });
    }
  },

  removeWatchlistItem: (symbol) => {
    const watchlist = get().watchlist;
    set({ watchlist: watchlist.filter(s => s !== symbol) });
  },

  updateStockDetail: (symbol, detail) => {
    const stockDetails = get().stockDetails;
    set({
      stockDetails: {
        ...stockDetails,
        [symbol]: detail
      }
    });
  },

  reset: () => {
    set({
      watchlist: [],
      marketMovers: { gainers: [], losers: [], most_active: [] },
      heatmapData: [],
      marketScore: { current: null, history: [] },
      stockDetails: {},
      loadingStatus: 'idle',
      error: null,
      lastUpdated: null
    });
  }
}));

export default useDashboardStore;
```

**驗證標準**:
- [ ] Store 結構清晰
- [ ] Actions 正確實現
- [ ] 狀態更新正確
- [ ] 測試覆蓋率 ≥ 85%

#### 3.3.3 預估學習時間

| 任務類別 | 預估時間 | 優先級 |
|---------|---------|--------|
| VectorBT 學習 | 1 週 | P1 |
| Backtrader 學習 | 1 週 | P1 |
| 策略引擎架構 | 1 週 | P1 |
| Zustand 精通 | 3 天 | P1 |
| React Query 精通 | 3 天 | P1 |
| 集成測試 | 3 天 | P1 |
| 實踐項目 (任務 2.1-2.4) | 5 週 | P1 |
| **總計** | **10-11 週** | |

#### 3.3.4 驗證標準

**代碼質量驗證**:
- [ ] 策略實現遵循 IStrategy 接口契約
- [ ] 回測代碼有完整的單元測試和集成測試
- [ ] 測試覆蓋率 ≥ 85%
- [ ] 所有提交遵循 Conventional Commits
- [ ] 代碼審查通過（至少 1 次他人審查）

**功能驗證**:
- [ ] 能夠使用 VectorBT 執行策略回測
- [ ] 能夠正確實現並使用策略工廠
- [ ] 能夠使用 React Query 管理服務端狀態
- [ ] 能夠使用 Zustand 管理全局狀態
- [ ] 能夠編寫集成測試

**知識驗證**:
- [ ] 能夠解釋策略模式的工作原理
- [ ] 能夠解釋向量化計算的性能優勢
- [ ] 能夠解釋 React Query 的緩存策略
- [ ] 能夠審查他人代碼並提供建設性反饋
- [ ] 能夠設計測試策略

**通過標準**: 所有檢查項目必須完成，並且通過代碼審查

### 3.4 階段 3: 高級開發者 (6-12 個月)

#### 3.4.1 核心學習目標

1. **掌握複合策略設計**：能夠設計和實現組合策略和信號合併算法
2. **精通性能優化**：能夠識別和解決性能瓶頸
3. **建立架構思維**：能夠進行技術選型和架構設計決策
4. **具備技術指導能力**：能夠指導初級和中級開發者

#### 3.4.2 可執行的實踐任務

##### 任務 3.1: 實現複合策略 (3 週)

**目標**: 掌握組合策略和信號合併算法

**複合策略實現** (參考 a006a-5.md):
```python
# backend/strategies/composite_strategy.py
from .base import IStrategy, Signal, SignalAction, ExecutionContext
from typing import List
import pandas as pd

class CompositeStrategy(IStrategy):
    """使用可配置合併算法組合多個策略"""

    name = "composite_strategy"

    MERGE_ALGORITHMS = [
        'majority_vote',  # 多數決
        'unanimous',      # 一致同意
        'weighted',       # 加權
        'any'             # 任一
    ]

    def __init__(
        self,
        strategies: List[IStrategy],
        merge_algorithm: str = 'majority_vote',
        weights: List[float] = None
    ):
        if merge_algorithm not in self.MERGE_ALGORITHMS:
            raise ValueError(f"Invalid merge algorithm: {merge_algorithm}")

        if merge_algorithm == 'weighted' and weights and len(weights) != len(strategies):
            raise ValueError("Weights length must match strategies length")

        self.strategies = strategies
        self.merge_algorithm = merge_algorithm
        self.weights = weights or [1.0 / len(strategies)] * len(strategies)

    def generate_signals(
        self,
        context: ExecutionContext,
        symbols: List[str]
    ) -> List[Signal]:
        # 收集所有策略的信號
        all_signals_by_symbol = {symbol: [] for symbol in symbols}

        for strategy in self.strategies:
            strategy_signals = strategy.generate_signals(context, symbols)
            for signal in strategy_signals:
                all_signals_by_symbol[signal.symbol].append(signal)

        # 合併每個標的的信號
        merged_signals = []
        for symbol, signals in all_signals_by_symbol.items():
            if not signals:
                continue

            merged_signal = self._merge_signals(symbol, signals)
            if merged_signal:
                merged_signals.append(merged_signal)

        return merged_signals

    def _merge_signals(self, symbol: str, signals: List[Signal]) -> Signal:
        """使用配置的算法合併多個信號"""

        if self.merge_algorithm == 'majority_vote':
            return self._majority_vote_merge(symbol, signals)
        elif self.merge_algorithm == 'unanimous':
            return self._unanimous_merge(symbol, signals)
        elif self.merge_algorithm == 'weighted':
            return self._weighted_merge(symbol, signals)
        elif self.merge_algorithm == 'any':
            return self._any_merge(symbol, signals)

        return None

    def _majority_vote_merge(self, symbol: str, signals: List[Signal]) -> Signal:
        """多數決合併"""
        buy_count = sum(1 for s in signals if s.action == SignalAction.BUY)
        sell_count = sum(1 for s in signals if s.action == SignalAction.SELL)

        if buy_count > sell_count:
            return Signal(
                symbol=symbol,
                action=SignalAction.BUY,
                confidence=buy_count / len(signals),
                reason=f"Majority vote: {buy_count}/{len(signals)} BUY"
            )
        elif sell_count > buy_count:
            return Signal(
                symbol=symbol,
                action=SignalAction.SELL,
                confidence=sell_count / len(signals),
                reason=f"Majority vote: {sell_count}/{len(signals)} SELL"
            )

        return None

    def _unanimous_merge(self, symbol: str, signals: List[Signal]) -> Signal:
        """一致同意合併"""
        actions = [s.action for s in signals]

        if all(a == SignalAction.BUY for a in actions):
            return Signal(
                symbol=symbol,
                action=SignalAction.BUY,
                confidence=1.0,
                reason="Unanimous BUY"
            )
        elif all(a == SignalAction.SELL for a in actions):
            return Signal(
                symbol=symbol,
                action=SignalAction.SELL,
                confidence=1.0,
                reason="Unanimous SELL"
            )

        return None

    def _weighted_merge(self, symbol: str, signals: List[Signal]) -> Signal:
        """加權合併"""
        buy_weight = sum(
            weight * signal.confidence
            for weight, signal in zip(self.weights, signals)
            if signal.action == SignalAction.BUY
        )
        sell_weight = sum(
            weight * signal.confidence
            for weight, signal in zip(self.weights, signals)
            if signal.action == SignalAction.SELL
        )

        if buy_weight > sell_weight:
            return Signal(
                symbol=symbol,
                action=SignalAction.BUY,
                confidence=min(1.0, buy_weight),
                reason=f"Weighted: BUY weight {buy_weight:.2f}"
            )
        elif sell_weight > buy_weight:
            return Signal(
                symbol=symbol,
                action=SignalAction.SELL,
                confidence=min(1.0, sell_weight),
                reason=f"Weighted: SELL weight {sell_weight:.2f}"
            )

        return None

    def _any_merge(self, symbol: str, signals: List[Signal]) -> Signal:
        """任一合併"""
        buy_signals = [s for s in signals if s.action == SignalAction.BUY]
        sell_signals = [s for s in signals if s.action == SignalAction.SELL]

        if buy_signals:
            # 返回最高信心的買入信號
            best_signal = max(buy_signals, key=lambda s: s.confidence)
            return Signal(
                symbol=symbol,
                action=SignalAction.BUY,
                confidence=best_signal.confidence,
                reason=f"Any: {best_signal.reason}"
            )
        elif sell_signals:
            # 返回最高信心的賣出信號
            best_signal = max(sell_signals, key=lambda s: s.confidence)
            return Signal(
                symbol=symbol,
                action=SignalAction.SELL,
                confidence=best_signal.confidence,
                reason=f"Any: {best_signal.reason}"
            )

        return None
```

**驗證標準**:
- [ ] 所有合併算法正確實現
- [ ] 複合策略能夠正確組合子策略
- [ ] 測試覆蓋率 ≥ 90%
- [ ] 性能優化（並行計算）

##### 任務 3.2: 性能優化 (2 週)

**目標**: 識別和解決性能瓶頸

**優化策略** (參考 a005-competencies.md):

1. **向量化優化**
```python
# 使用向量化操作替代循環
def calculate_rsi_vectorized(prices: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """向量化計算多個標的的 RSI"""
    delta = prices.diff()
    gains = delta.where(delta > 0, 0)
    losses = -delta.where(delta < 0, 0)

    avg_gains = gains.ewm(span=period, adjust=False).mean()
    avg_losses = losses.ewm(span=period, adjust=False).mean()

    rs = avg_gains / avg_losses
    rsi = 100 - (100 / (1 + rs))

    return rsi
```

2. **緩存優化**
```python
# 指標緩存
from functools import lru_cache

class IndicatorCache:
    def __init__(self):
        self.cache = {}

    def get_or_compute(self, symbol: str, indicator_fn: callable, prices: pd.Series, **params) -> pd.Series:
        cache_key = (symbol, indicator_fn.__name__, tuple(sorted(params.items())))

        if cache_key not in self.cache:
            self.cache[cache_key] = indicator_fn(prices, **params)

        return self.cache[cache_key]

    def clear(self):
        self.cache.clear()
```

3. **並行處理**
```python
# 使用 pytest-xdist 並行運行測試
# pytest.ini
[pytest]
addopts = -n auto

# 多進程回測
from concurrent.futures import ProcessPoolExecutor

def parallel_backtest(strategies, symbols, start_date, end_date):
    """並行執行多個策略回測"""
    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = []
        for strategy in strategies:
            future = executor.submit(
                run_single_backtest,
                strategy,
                symbols,
                start_date,
                end_date
            )
            futures.append(future)

        results = [future.result() for future in futures]

    return results
```

**驗證標準**:
- [ ] 性能提升 ≥ 30%
- [ ] 測試覆蓋率 ≥ 90%
- [ ] 性能基準測試建立

##### 任務 3.3: E2E 測試 (2 週)

**目標**: 掌握完整的端到端測試

**Cypress 測試示例** (參考 a005-competencies.md):
```javascript
// cypress/e2e/strategy_flow.cy.js
describe('Strategy Flow', () => {
  beforeEach(() => {
    cy.login('admin', 'password');
    cy.visit('/strategies/builder');
  });

  it('should create a new strategy', () => {
    // 創建策略
    cy.get('[data-testid="strategy-name-input"]').type('Test RSI Strategy');
    cy.get('[data-testid="strategy-type-select"]').select('rsi');
    cy.get('[data-testid="strategy-params-period"]').type('14');
    cy.get('[data-testid="submit-button"]').click();

    // 驗證創建成功
    cy.contains('Strategy created successfully').should('be.visible');

    // 導航到回測頁面
    cy.get('[data-testid="backtest-tab"]').click();
    cy.get('[data-testid="start-backtest-button"]').click();

    // 等待回測完成
    cy.get('[data-testid="backtest-status"]', { timeout: 60000 })
      .should('contain', 'completed');

    // 驗證結果
    cy.get('[data-testid="sharpe-ratio"]').should('be.visible');
    cy.get('[data-testid="total-return"]').should('be.visible');
  });

  it('should update strategy parameters', () => {
    // 創建策略
    cy.get('[data-testid="strategy-name-input"]').type('Test RSI Strategy');
    cy.get('[data-testid="strategy-type-select"]').select('rsi');
    cy.get('[data-testid="strategy-params-period"]').type('14');
    cy.get('[data-testid="submit-button"]').click();

    // 編輯策略
    cy.get('[data-testid="edit-strategy-button"]').click();
    cy.get('[data-testid="strategy-params-period"]').clear().type('21');
    cy.get('[data-testid="save-button"]').click();

    // 驗證更新成功
    cy.contains('Strategy updated successfully').should('be.visible');
    cy.get('[data-testid="strategy-params-period"]').should('have.value', '21');
  });
});
```

**驗證標準**:
- [ ] E2E 測試覆蓋關鍵流程
- [ ] 測試穩定性 ≥ 95%
- [ ] 測試執行時間 ≤ 10 分鐘

#### 3.4.3 預估學習時間

| 任務類別 | 預估時間 | 優先級 |
|---------|---------|--------|
| 複合策略設計 | 2 週 | P2 |
| 信號合併算法 | 1 週 | P2 |
| 性能優化 | 2 週 | P2 |
| E2E 測試 | 2 週 | P2 |
| 技術指導 | 1 週 | P2 |
| 實踐項目 (任務 3.1-3.3) | 4 週 | P2 |
| **總計** | **12-16 週** | |

#### 3.4.4 驗證標準

**代碼質量驗證**:
- [ ] 複合策略實現正確
- [ ] 性能優化效果顯著（≥ 30%）
- [ ] E2E 測試覆蓋率 ≥ 70%
- [ ] 測試覆蓋率 ≥ 90%
- [ ] 代碼審查通過（至少 2 次他人審查）

**功能驗證**:
- [ ] 能夠設計和實現複合策略
- [ ] 能夠使用多種信號合併算法
- [ ] 能夠識別和解決性能瓶頸
- [ ] 能夠編寫穩定的 E2E 測試
- [ ] 能夠指導初級和中級開發者

**知識驗證**:
- [ ] 能夠解釋複合策略的設計原則
- [ ] 能夠進行性能分析和優化
- [ ] 能夠設計 E2E 測試策略
- [ ] 能夠進行技術選型和架構設計
- [ ] 能夠提供建設性的代碼審查反饋

**通過標準**: 所有檢查項目必須完成，並且通過代碼審查

### 3.5 階段 4: 高級架構師 (12+ 個月)

#### 3.5.1 核心學習目標

1. **掌握系統架構設計**：能夠設計可擴展的微服務架構
2. **精通技術決策**：能夠進行技術選型和架構演進
3. **建立技術領導力**：能夠制定技術路線圖和建立技術文化
4. **具備跨領域整合能力**：能夠整合金融、數據科學、軟件工程知識

#### 3.5.2 可執行的實踐任務

##### 任務 4.1: 系統架構設計 (4 週)

**目標**: 設計可擴展的微服務架構

**架構設計** (參考 a005-competencies.md):

1. **服務拆分**
```
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway                               │
│  (Kong / AWS API Gateway)                                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  策略服務     │  │  市場數據服務 │  │  分析服務     │      │
│  │ Strategy Svc  │  │ Market Data  │  │ Analysis     │      │
│  │              │  │ Service      │  │ Service      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  執行服務     │  │  用戶服務     │  │  通知服務     │      │
│  │ Execution Svc │  │ User Svc     │  │ Notification │      │
│  │              │  │              │  │ Service      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│                        消息隊列                              │
│  (Redis Pub/Sub / RabbitMQ / Kafka)                          │
├─────────────────────────────────────────────────────────────┤
│                        數據存儲                              │
│  PostgreSQL │ DuckDB │ Redis │ S3                            │
└─────────────────────────────────────────────────────────────┘
```

2. **服務間通信**
```python
# 使用 REST + gRPC 混合通信
from fastapi import FastAPI
import grpc

class StrategyService(FastAPI):
    """策略服務"""

    def __init__(self):
        self.market_data_client = MarketDataGrpcClient()
        self.analysis_client = AnalysisHttpClient()

    async def create_strategy(self, strategy_data: StrategyCreate):
        # 使用 gRPC 調用市場數據服務（高性能）
        symbols = await self.market_data_client.get_symbols(
            universe=strategy_data.universe
        )

        # 使用 HTTP 調用分析服務（靈活）
        backtest_result = await self.analysis_client.run_backtest(
            strategy=strategy_data,
            symbols=symbols
        )

        return backtest_result
```

3. **服務發現和負載均衡**
```python
# 使用 Consul 進行服務發現
import consul

class ServiceDiscovery:
    def __init__(self, consul_host='localhost', consul_port=8500):
        self.consul = consul.Consul(host=consul_host, port=consul_port)

    def register_service(self, service_name: str, service_port: int):
        """註冊服務"""
        self.consul.agent.service.register(
            name=service_name,
            service_port=service_port,
            check=consul.Check.http(
                f"http://localhost:{service_port}/health",
                interval="10s"
            )
        )

    def discover_service(self, service_name: str) -> list:
        """發現服務實例"""
        _, services = self.consul.health.service(service_name, passing=True)
        return [
            f"http://{service['Address']}:{service['Port']}"
            for service in services[1]
        ]
```

**驗證標準**:
- [ ] 架構設計文檔完整
- [ ] 服務邊界清晰
- [ ] 服務間通信機制定義明確
- [ ] 可擴展性驗證通過

##### 任務 4.2: 技術決策記錄 (ADR) (2 週)

**目標**: 建立技術決策記錄機制

**ADR 範例** (參考 a005-competencies.md):

```markdown
# ADR-001: 選擇 FastAPI 作為後端框架

## 狀態
已採用

## 背景
我們需要選擇一個 Python Web 框架來構建 Dashboard 的後端 API。

## 決策
選擇 FastAPI 作為後端框架。

## 理由
1. **性能優勢**: FastAPI 基於 Starlette 和 Pydantic，性能接近 Node.js 和 Go
2. **自動文檔**: 自動生成 OpenAPI 文檔，減少文檔維護成本
3. **類型驗證**: Pydantic 提供運行時類型驗證，減少運行時錯誤
4. **異步支持**: 原生支持 async/await，適合 I/O 密集型應用
5. **生態系統**: 與現有工具（如 pytest、uvicorn）集成良好

## 後果
- **正面**: 開發效率高，性能優異，文檔自動生成
- **負面**: 相對於 Django，生態系統較小，但對於 API 服務已足夠

## 替代方案考慮
1. **Django REST Framework**: 功能豐富，但性能較差，學習曲線陡峭
2. **Flask**: 輕量級，但需要手動組裝各種組件
3. **Starlette**: FastAPI 的底層框架，但缺少高級功能

## 參考
- FastAPI 文檔: https://fastapi.tiangolo.com/
- 性能基準測試: https://www.techempower.com/benchmarks/
```

**驗證標準**:
- [ ] 至少 5 個 ADR 文檔
- [ ] ADR 格式統一
- [ ] 決策理由充分
- [ ] 替代方案考慮完整

##### 任務 4.3: 技術路線圖制定 (2 週)

**目標**: 制定技術發展路線圖

**技術路線圖範例** (參考 a005-competencies.md):

```markdown
# Dashboard 技術路線圖 2026-2027

## Q1 2026 (3 個月)
- [ ] 統一策略引擎完成
- [ ] React Query 遷移完成
- [ ] CI/CD 自動化基礎設施建立

## Q2 2026 (3 個月)
- [ ] 微服務拆分（策略服務、市場數據服務）
- [ ] API Gateway 部署
- [ ] 監控和日誌系統建立（Prometheus + Grafana）

## Q3 2026 (3 個月)
- [ ] 實時數據流處理（WebSocket + Redis Pub/Sub）
- [ ] 機器學習模型集成
- [ ] 性能優化（緩存、並行處理）

## Q4 2026 (3 個月)
- [ ] Kubernetes 部署
- [ ] 自動化測試覆蓋率達到 90%
- [ ] 技術債償還計劃完成

## 2027 年度目標
- [ ] 支持更多資產類型（期貨、期權、加密貨幣）
- [ ] 實時交易執行
- [ ] 多租戶支持
- [ ] 國際化支持
```

**驗證標準**:
- [ ] 路線圖覆盖 12-24 個月
- [ ] 季度目標具體可衡量
- [ ] 與業務目標對齊
- [ ] 定期更新和調整

#### 3.5.3 預估學習時間

| 任務類別 | 預估時間 | 優先級 |
|---------|---------|--------|
| 系統架構設計 | 4 週 | P3 |
| 技術決策記錄 | 2 週 | P3 |
| 技術路線圖 | 2 週 | P3 |
| 技術領導力 | 持續 | P3 |
| 跨領域整合 | 持續 | P3 |
| **總計** | **8 週 + 持續** | |

#### 3.5.4 驗證標準

**代碼質量驗證**:
- [ ] 架構設計文檔完整且通過審查
- [ ] ADR 文檔數量 ≥ 5
- [ ] 技術路線圖制定完成
- [ ] 測試覆蓋率 ≥ 90%
- [ ] 代碼審查通過（至少 3 次他人審查）

**功能驗證**:
- [ ] 能夠設計可擴展的系統架構
- [ ] 能夠進行技術選型和決策
- [ ] 能夠制定技術路線圖
- [ ] 能夠進行跨領域知識整合
- [ ] 能夠領導技術團隊

**知識驗證**:
- [ ] 能夠解釋微服務架構的優缺點
- [ ] 能夠進行架構演進設計
- [ ] 能夠制定技術債償還計劃
- [ ] 能夠建立技術文化
- [ ] 能夠進行技術規劃和路線圖制定

**通過標準**: 所有檢查項目必須完成，並且通過架構審查

---

## 4. 知識庫架構

本知識庫架構基於 a006a-5.md 的統一知識庫設計，整合所有技術知識。

### 4.1 知識庫結構

```
KB-UNIFIED-001 (統一知識庫)
├── 1. 知識庫概述
│   ├── 目的和範圍
│   ├── 架構概覽
│   └── 核心設計原則
├── 2. 快速開始指南
│   ├── 環境準備
│   ├── 創建第一個策略
│   ├── 創建第一個前端頁面
│   ├── 提交代碼
│   └── 快速參考命令
├── 3. 後端架構
│   ├── API 端點
│   ├── 服務層
│   ├── 數據結構
│   ├── 錯誤處理
│   └── 緩存機制
├── 4. 前端架構
│   ├── React 組件層級
│   ├── 共享組件庫
│   ├── 狀態管理
│   ├── UI 模式
│   ├── API 集成
│   └── 頁面組件類別
├── 5. 策略引擎
│   ├── IStrategy 接口
│   ├── 策略模板
│   ├── VectorBT 集成
│   ├── 策略工廠
│   └── 核心算法
├── 6. Git 開發模式
│   ├── 分支策略
│   ├── Conventional Commits
│   ├── Pull Request 流程
│   ├── 代碼審查
│   └── CI/CD 集成
├── 7. 代碼模式和最佳實踐
│   ├── 設計模式
│   ├── Python 最佳實踐
│   ├── JavaScript 最佳實踐
│   ├── 測試最佳實踐
│   └── 性能優化技巧
├── 8. 測試和驗證方法
│   ├── 單元測試
│   ├── 集成測試
│   ├── E2E 測試
│   ├── 測試金字塔
│   └── 測試策略
├── 9. 故障排除常見問題
│   ├── 後端問題
│   ├── 前端問題
│   ├── 策略引擎問題
│   ├── Git 問題
│   └── 性能問題
└── 10. 技術棧清單
    ├── 後端技術棧
    ├── 前端技術棧
    ├── 回測引擎技術棧
    ├── 開發工具技術棧
    └── 部署技術棧
```

### 4.2 知識庫使用指南

#### 4.2.1 快速開始 (5 分鐘上手)

**環境準備**:
```bash
# 1. 克隆專案
git clone <repo-url>
cd Dashboard

# 2. 設置 Python 環境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r backend/requirements.txt

# 3. 設置 Node 環境
cd frontend
npm install

# 4. 啟動開發服務器
# 終端 1: 後端
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 終端 2: 前端
cd frontend
npm run dev
```

**創建第一個策略** (參考 a006a-5.md 第 5 節):
```python
# backend/strategies/my_strategy.py
from .base import IStrategy, Signal, SignalAction, ExecutionContext
from datetime import date
from typing import List

class MyFirstStrategy(IStrategy):
    """簡單的趨勢跟隨策略"""
    name = "my_first_strategy"

    def __init__(self, short_period: int = 5, long_period: int = 20):
        self.short_period = short_period
        self.long_period = long_period

    def generate_signals(
        self,
        context: ExecutionContext,
        symbols: List[str]
    ) -> List[Signal]:
        """生成交易信號"""
        signals = []

        for symbol in symbols:
            # 獲取移動平均線數據
            short_ma = self._get_ma(symbol, context.market_date, self.short_period)
            long_ma = self._get_ma(symbol, context.market_date, self.long_period)

            # 簡單的交叉策略
            if short_ma > long_ma:
                signals.append(Signal(
                    symbol=symbol,
                    action=SignalAction.BUY,
                    confidence=0.8
                ))

        return signals

    def _get_ma(self, symbol: str, date: date, period: int) -> float:
        """獲取移動平均線值"""
        # 實現略
        pass
```

#### 4.2.2 API 端點參考

**策略管理端點** (參考 a006a-5.md 第 3.1 節):

| 方法 | 路徑 | 描述 | 認證 |
|------|------|------|------|
| GET | `/api/v1/strategies` | 列出策略 | ✅ |
| POST | `/api/v1/strategies` | 創建策略 | ✅ |
| GET | `/api/v1/strategies/{strategy_id}` | 獲取策略詳情 | ✅ |
| PUT | `/api/v1/strategies/{strategy_id}` | 更新策略配置 | ✅ |
| DELETE | `/api/v1/strategies/{strategy_id}` | 刪除策略 | ✅ |
| PATCH | `/api/v1/strategies/{strategy_id}/status` | 切換策略狀態 | ✅ |

**請求示例**:
```json
POST /api/v1/strategies
{
  "name": "Moving Average Crossover",
  "description": "雙均線交叉策略",
  "type": "trend_following",
  "parameters": {
    "short_period": 5,
    "long_period": 20,
    "symbol": "AAPL"
  },
  "risk_limits": {
    "max_position_size": 1000,
    "max_drawdown": 0.15
  }
}
```

#### 4.2.3 共享組件庫

**核心共享組件** (參考 a006a-5.md 第 4.2 節):

| 組件名稱 | 用途 | 複用度 |
|---------|------|--------|
| **ErrorBoundary** | 錯誤邊界，捕獲 React 錯誤 | ⭐⭐⭐⭐⭐ |
| **ToastProvider** | Toast 通知系統 | ⭐⭐⭐⭐⭐ |
| **Skeleton** | 骨架屏加載狀態 | ⭐⭐⭐⭐⭐ |
| **EmptyState** | 空狀態顯示組件 | ⭐⭐⭐⭐ |
| **EmptyStatePresets** | 預設空狀態模板 | ⭐⭐⭐⭐ |

**Skeleton 組件模式**:
```javascript
// 卡片骨架
<Skeleton.Card count={3} />

// 表格骨架
<Skeleton.Table rows={5} columns={4} />

// 文本骨架
<Skeleton.Text lines={3} />

// 圖表骨架
<Skeleton.Chart height={300} />

// 全頁加載器
<Skeleton.PageLoader text="Loading..." />
```

**EmptyState 組件模式**:
```javascript
// 基本用法
<EmptyState
  icon="bi-inbox"
  title="No Data"
  message="There is no data to display."
  action={<button onClick={...}>Load Data</button>}
  size="medium"
/>

// 預設模板
<EmptyStatePresets.NoSearchResults />
<EmptyStatePresets.NoItems />
<EmptyStatePresets.NoSignals />
<EmptyStatePresets.NoStrategies />
<EmptyStatePresets.LoadError />
```

### 4.3 知識庫維護

#### 4.3.1 更新頻率

| 知識類型 | 更新頻率 | 責任人 |
|---------|---------|--------|
| **快速開始指南** | 每季度 | 技術領導 |
| **API 文檔** | 每次發布 | API 負責人 |
| **前端組件** | 每週 | 前端負責人 |
| **策略模板** | 每月 | 策略負責人 |
| **故障排除** | 按需 | 全體開發者 |

#### 4.3.2 貢獻指南

1. **知識提交**: 所有新知識必須通過 Pull Request 提交
2. **審查流程**: 每個提交必須經過至少 1 人審查
3. **格式要求**: 遵循統一的 Markdown 格式
4. **測試驗證**: 代碼示例必須經過測試驗證

---

## 5. 工作流程和最佳實踐

### 5.1 開發工作流程

#### 5.1.1 Git Flow 分支策略

```
main (生產代碼)
  ↑
  develop (開發整合)
  ↑
  ├── feature/* (功能分支)
  ├── hotfix/* (緊急修復)
  ├── release/* (發布準備)
  ├── fix/* (一般修復)
  └── refactor/* (代碼重構)
```

**分支使用規則** (參考 a006a-5.md 第 6 節):

| 分支類型 | 命名規範 | 用途 | 合併目標 |
|---------|---------|------|---------|
| `main` | - | 生產代碼 | - |
| `develop` | - | 開發整合 | - |
| `feature/xxx` | feature/feature-name | 新功能開發 | develop |
| `fix/xxx` | fix/issue-id-description | Bug 修復 | develop |
| `hotfix/xxx` | hotfix/issue-id-description | 緊急生產修復 | main + develop |
| `release/v1.x.x` | release/version | 發布準備 | main + develop |
| `refactor/xxx` | refactor/component-name | 代碼重構 | develop |

#### 5.1.2 Conventional Commits 規範

**提交格式** (參考 a005-competencies.md):
```
<type>(<scope>): <subject>

<body>

<footer>
```

**提交類型**:
| 類型 | 描述 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(strategies): add RSI strategy implementation` |
| `fix` | Bug 修復 | `fix(items): handle empty items list gracefully` |
| `docs` | 文檔更新 | `docs(api): update API documentation for strategies` |
| `style` | 代碼格式 | `style(backend): format code with black` |
| `refactor` | 重構 | `refactor(items): extract validation logic to separate function` |
| `test` | 測試 | `test(items): add comprehensive tests for items API` |
| `chore` | 構建/工具 | `chore(deps): update FastAPI to version 0.104` |

**提交示例**:
```bash
# 功能開發
git commit -m "feat(strategies): add MACD strategy implementation

- Implement MACD strategy with configurable parameters
- Add backtest support for MACD strategy
- Update strategy registry

Closes #123"

# Bug 修復
git commit -m "fix(items): handle null description in items list

Previously, null descriptions would cause rendering errors.
Now, null values are handled gracefully and displayed as '-'."

# 重構
git commit -m "refactor(items): extract item validation logic to separate module

This improves code reusability and makes the code easier to test."
```

#### 5.1.3 Pull Request 流程

**PR 模板**:
```markdown
## 描述
簡短描述此 PR 的目的和內容。

## 類型
- [ ] Bug 修復
- [ ] 新功能
- [ ] 重構
- [ ] 文檔更新
- [ ] 性能優化
- [ ] 其他

## 變更
- 列出主要的變更

## 測試
- [ ] 單元測試通過
- [ ] 集成測試通過
- [ ] E2E 測試通過（如適用）
- [ ] 手動測試完成

## 檢查清單
- [ ] 代碼遵循項目風格指南
- [ ] 代碼通過 linter 檢查
- [ ] 測試覆蓋率達到要求
- [ ] 文檔已更新（如需要）
- [ ] Conventional Commits 遵循
- [ ] 所有提交信息清晰

## 相關 Issue
Closes #issue-id

## 截圖/演示
（如適用，添加截圖或演示鏈接）
```

**審查標準** (參考 a005-competencies.md):

**功能正確性**:
- [ ] 功能符合需求
- [ ] 邊界情況已處理
- [ ] 錯誤處理完善

**代碼質量**:
- [ ] 代碼可讀性好
- [ ] 遵循項目風格
- [ ] 無重複代碼
- [ ] 適當的註釋

**測試覆蓋**:
- [ ] 新功能有測試覆蓋
- [ ] 測試通過率 100%
- [ ] 覆蓋率未下降

**安全性**:
- [ ] 無硬編碼密碼/API keys
- [ ] 適當的權限檢查
- [ ] 輸入驗證完善

**性能**:
- [ ] 無明顯性能退化
- [ ] 數據庫查詢優化
- [ ] 前端渲染優化

**文檔**:
- [ ] README 已更新（如需要）
- [ ] API 文檔已更新
- [ ] 註釋清晰

### 5.2 測試驅動開發 (TDD)

#### 5.2.1 TDD 流程

```
Red (寫失敗測試)
    ↓
Green (寫最少代碼通過測試)
    ↓
Refactor (重構代碼)
    ↓
重復
```

**示例**:

**1. Red - 寫失敗測試**:
```python
def test_calculate_rsi():
    """測試 RSI 計算"""
    prices = pd.Series([100, 101, 102, 103, 104, 105, 106, 107, 108, 109,
                       110, 111, 112, 113, 114, 113, 112, 111, 110, 109])

    rsi_calculator = SimpleRSI(period=14)
    rsi = rsi_calculator.calculate(prices)

    assert 0 <= rsi.iloc[-1] <= 100
    assert not pd.isna(rsi.iloc[-1])
```

**2. Green - 寫最少代碼通過測試**:
```python
class SimpleRSI:
    def __init__(self, period: int = 14):
        self.period = period

    def calculate(self, prices: pd.Series) -> pd.Series:
        delta = prices.diff()
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)

        avg_gains = gains.rolling(window=self.period).mean()
        avg_losses = losses.rolling(window=self.period).mean()

        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))

        return rsi
```

**3. Refactor - 重構代碼**:
```python
class SimpleRSI:
    def __init__(self, period: int = 14):
        self.period = period

    def calculate(self, prices: pd.Series) -> pd.Series:
        """
        計算 RSI 指標

        Args:
            prices: 價格序列

        Returns:
            RSI 值序列
        """
        delta = self._calculate_delta(prices)
        gains, losses = self._separate_gains_losses(delta)
        avg_gains, avg_losses = self._calculate_average_gains_losses(gains, losses)
        rs = self._calculate_rs(avg_gains, avg_losses)
        rsi = self._calculate_rsi_from_rs(rs)

        return rsi

    def _calculate_delta(self, prices: pd.Series) -> pd.Series:
        return prices.diff()

    def _separate_gains_losses(self, delta: pd.Series) -> tuple[pd.Series, pd.Series]:
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)
        return gains, losses

    def _calculate_average_gains_losses(
        self,
        gains: pd.Series,
        losses: pd.Series
    ) -> tuple[pd.Series, pd.Series]:
        avg_gains = gains.rolling(window=self.period).mean()
        avg_losses = losses.rolling(window=self.period).mean()
        return avg_gains, avg_losses

    def _calculate_rs(self, avg_gains: pd.Series, avg_losses: pd.Series) -> pd.Series:
        return avg_gains / avg_losses

    def _calculate_rsi_from_rs(self, rs: pd.Series) -> pd.Series:
        return 100 - (100 / (1 + rs))
```

#### 5.2.2 測試金字塔

```
          ┌──────────────┐
          │   E2E Tests  │  關鍵流程，數量少 (5-10%)
          ├──────────────┤
          │ Integration  │  API 層級，中等數量 (20-30%)
          ├──────────────┤
          │  Unit Tests  │  核心邏輯，數量多 (60-75%)
          └──────────────┘
```

**測試覆蓋率目標** (參考 a005-competencies.md):

| 類別 | 測試數 | 通過率 | 覆蓋率 | 目標 |
|----------|-------|-----------|----------|------|
| 🐍 後端 | 244 | 91% | 70% | 80% |
| ⚛️ 前端工具 | 152 | 100% | 100% | ✅ |
| ⚛️ 前端組件 | 110 | 63% | ~30% | 70% |
| **總計** | **506** | **86%** | **60%** | **80%** |

#### 5.2.3 AAA 模式

**Arrange-Act-Assert** 模式示例:

```python
def test_strategy_calculate_rsi():
    # Arrange (準備)
    strategy = RSIStrategy(period=14)
    prices = pd.Series([100, 101, 102, 103, 104, 105, 106, 107, 108, 109,
                       110, 111, 112, 113])

    # Act (執行)
    rsi = strategy.calculate_rsi(prices)

    # Assert (斷言)
    assert 0 <= rsi <= 100
    assert not pd.isna(rsi)
```

### 5.3 代碼審查最佳實踐

#### 5.3.1 審查流程

**1. 快速審查** (5-10 分鐘):
- 確認 PR 描述清晰
- 確認測試覆蓋充分
- 確認沒有明顯問題

**2. 深入審查** (20-30 分鐘):
- 代碼邏輯正確性
- 代碼質量和風格
- 性能影響
- 安全性

**3. 建設性反饋**:
- 解釋為什麼要修改
- 提供具體建議
- 對代碼不對人

#### 5.3.2 反饋示例

❌ **壞例子**:
```
這段代碼有問題，改一下。
```

✅ **好例子** (參考 a005-competencies.md):
```
我注意到這裡使用 `for` 循環計算 RSI，這在大型數據集上可能會很慢。建議使用 `pandas_ta` 的向量化操作：

```python
# 當前
for i in range(len(prices)):
    rsi = calculate_rsi(prices[:i+1])

# 建議
rsi = ta.momentum.RSIIndicator(prices, window=14).rsi()
```

這樣可以提升性能 5-10x。如果需要更多幫助，請告訴我。
```

### 5.4 常見陷阱和最佳實踐

#### 5.4.1 React 最佳實踐

**✅ 好的做法**:
```javascript
// 使用 refs 避免 useEffect 重新運行
const { fetchStage1Overview } = useStore();
const fetchStage1Ref = useRef(fetchStage1Overview);

useEffect(() => {
  fetchStage1Ref.current();
}, []);
```

**❌ 不好的做法**:
```javascript
// 直接使用會導致重新運行
const { fetchStage1Overview } = useStore();

useEffect(() => {
  fetchStage1Overview();  // 每次狀態更新都會運行
}, [fetchStage1Overview]);
```

#### 5.4.2 狀態管理最佳實踐

**狀態分類原則** (參考 a006a-5.md):

| 狀態類型 | 推薦方案 | 理由 |
|---------|----------|------|
| **全局應用狀態** | Zustand | 跨多個組件共享 |
| **服務器狀態** | React Query | 需要從 API 獲取，需要緩存和同步 |
| **功能特定狀態** | Context | 特定功能的狀態共享 |
| **表單/UI 狀態** | useState | 組件內部狀態，不需要共享 |
| **持久化狀態** | LocalStorage | 需要跨會話保存 |

#### 5.4.3 性能優化技巧

**前端性能優化**:
```javascript
// ✅ 使用 React.memo 避免不必要的重新渲染
const MemoizedComponent = React.memo(({ data }) => {
  return <div>{data.value}</div>;
});

// ✅ 使用 useMemo 緩存計算結果
const sortedData = useMemo(
  () => data.sort((a, b) => a.name.localeCompare(b.name)),
  [data]
);

// ✅ 使用 useCallback 穩定回調函數
const handleSave = useCallback(async () => {
  await saveData(data);
}, [data]);
```

**後端性能優化**:
```python
# ✅ 使用向量化操作
# 慢
for symbol in symbols:
    rsi = calculate_rsi(prices[symbol])

# 快
rsi = ta.momentum.RSIIndicator(prices, window=14).rsi()

# ✅ 使用批量查詢
# 慢
for symbol in symbols:
    db.execute(f"SELECT * FROM prices WHERE symbol = '{symbol}'")

# 快
db.execute(f"SELECT * FROM prices WHERE symbol IN ({','.join(symbols)})")

# ✅ 使用緩存
@lru_cache(maxsize=128)
def get_strategy_params(strategy_id: str) -> dict:
    return db.execute("SELECT params FROM strategies WHERE id = ?", (strategy_id,))
```

---

## 6. 評估和持續改進機制

### 6.1 評估框架

#### 6.1.1 階段評估

每個階段結束時進行綜合評估：

| 階段 | 評估時間 | 評估人 | 評估方式 |
|------|---------|--------|---------|
| **階段 1** | 3 個月後 | 導師 + 技術領導 | 代碼審查 + 技能測試 |
| **階段 2** | 6 個月後 | 導師 + 技術領導 | 代碼審查 + 回測項目 |
| **階段 3** | 12 個月後 | 技術領導 + 架構師 | 架構設計 + 技術決策 |
| **階段 4** | 每年 | 架構師 + 團隊 | 技術路線圖 + 團隊評估 |

#### 6.1.2 評估指標

**代碼質量指標**:
- 測試覆蓋率：目標 ≥ 80%
- 代碼審查通過率：目標 ≥ 90%
- Bug 率：目標 < 5%
- 代碼複雜度：目標 < 10

**技術能力指標**:
- 技能矩陣完成度：目標 100%
- 任務完成率：目標 ≥ 90%
- 技術分享次數：目標 ≥ 1 次/季度
- 文檔貢獻：目標 ≥ 2 篇/季度

**工作流指標**:
- Conventional Commits 遵循率：目標 100%
- PR 平均審查時間：目標 < 24 小時
- CI/CD 通過率：目標 ≥ 95%
- 部署頻率：目標 ≥ 1 次/週

### 6.2 反饋機制

#### 6.2.1 每週回顧

**形式**: 每週團隊會議（30 分鐘）

**議程**:
1. 本週完成的工作
2. 遇到的問題和挑戰
3. 下週計劃
4. 需要的支持

**輸出**: 週報文檔

#### 6.2.2 每月評估

**形式**: 一對一面談（1 小時）

**議程**:
1. 過去一個月的成績
2. 技能發展進展
3. 需要改進的領域
4. 設定下月目標

**輸出**: 月度評估報告

#### 6.2.3 每季度審查

**形式**: 全面評估（2 小時）

**議程**:
1. 季度目標達成情況
2. 技能矩陣更新
3. 個人發展計劃調整
4. 下一季度目標設定

**輸出**: 季度審查報告

### 6.3 持續改進計劃

#### 6.3.1 改進循環

```
設定目標 → 執行 → 測量 → 分析 → 改進 → 設定目標
```

#### 6.3.2 改進措施記錄

**改進建議模板**:
```markdown
## 改進建議

### 問題描述
簡要描述需要改進的問題。

### 影響範圍
描述問題的影響範圍和嚴重程度。

### 建議方案
描述建議的改進方案。

### 預期效果
描述預期的改進效果。

### 實施計劃
1. 時間線：YYYY-MM-DD
2. 責任人：XXX
3. 所需資源：XXX

### 實施結果
記錄實施結果和實際效果。
```

**改進措施示例**:
```markdown
## 改進建議：提升測試覆蓋率

### 問題描述
當前測試覆蓋率為 60%，未達到目標 80%。部分關鍵功能缺乏測試覆蓋。

### 影響範圍
- 代碼質量：Bug 率高於預期
- 重構風險：缺乏測試保護，重構風險高
- 開發效率：手動測試耗時

### 建議方案
1. 建立測試優先級清單
2. 為每個新功能要求測試覆蓋
3. 定期進行測試覆蓋率審查

### 預期效果
- 測試覆蓋率提升到 80%
- Bug 率降低 30%
- 重構風險降低

### 實施計劃
1. 時間線：2026-03-01 至 2026-06-30
2. 責任人：測試負責人 + 所有開發者
3. 所需資源：20% 開發時間用於編寫測試

### 實施結果
- 2026-03-31：測試覆蓋率達到 70%
- 2026-06-30：測試覆蓋率達到 82% ✅
- Bug 率降低 35% ✅
```

### 6.4 技能矩陣更新

#### 6.4.1 更新頻率

- **每週更新**: 實時記錄學習進度
- **每月審查**: 評估技能掌握程度
- **季度總結**: 更新技能矩陣

#### 6.4.2 評估標準

| 掌握程度 | 描述 | 驗證方式 |
|---------|------|---------|
| ⭐ | 了解概念 | 通過理論測試 |
| ⭐⭐ | 理解並能應用 | 獨立完成簡單任務 |
| ⭐⭐⭐ | 熟練掌握 | 獨立完成複雜任務 |
| ⭐⭐⭐⭐ | 精通 | 能夠指導他人 |
| ⭐⭐⭐⭐⭐ | 專家 | 能夠制定最佳實踐 |

---

## 7. 風險管理和後備方案

### 7.1 風險識別

#### 7.1.1 學習風險

| 風險 | 可能性 | 影響 | 緩解措施 |
|------|--------|------|---------|
| **學習能力不足** | 中 | 高 | 提供額外培訓、導師指導 |
| **時間不足** | 高 | 高 | 調整時間線、優先級管理 |
| **知識缺口** | 中 | 中 | 補充學習資源、定期評估 |
| **實踐機會少** | 低 | 中 | 實踐項目、內部開源 |

#### 7.1.2 技術風險

| 風險 | 可能性 | 影響 | 緩解措施 |
|------|--------|------|---------|
| **技術棧變更** | 中 | 高 | 定期技術棧審查、漸進式遷移 |
| **依賴更新** | 高 | 中 | 版本鎖定、定期測試 |
| **性能瓶頸** | 中 | 高 | 性能監控、預防性優化 |
| **安全漏洞** | 低 | 高 | 安全審計、定期掃描 |

#### 7.1.3 項目風險

| 風險 | 可能性 | 影響 | 緩解措施 |
|------|--------|------|---------|
| **需求變更** | 高 | 中 | 靈活設計、模塊化架構 |
| **資源不足** | 中 | 高 | 資源規劃、外部支持 |
| **團隊變動** | 低 | 高 | 知識共享、文檔完善 |
| **截止日期壓力** | 中 | 中 | 合理規劃、優先級管理 |

### 7.2 後備方案

#### 7.2.1 學習後備方案

**方案 A: 延長學習時間**
- 在原計劃基礎上增加 20-30% 的時間
- 調整各階段時間分配
- 保持核心技能優先

**方案 B: 降低技能目標**
- 專注 P0 和 P1 技能
- P2 和 P3 作為可選目標
- 實施後續能力建設計劃

**方案 C: 尋求外部支持**
- 引入外部導師
- 參加培訓課程
- 加入技術社區

#### 7.2.2 技術後備方案

**方案 A: 技術棧調整**
- 如果特定技術不適用，替換為替代技術
- 例如：如果 VectorBT 不適用，改用 Backtrader

**方案 B: 架構簡化**
- 簡化微服務架構為單體應用
- 簡化狀態管理為 Redux
- 保留核心功能，延遲高級功能

**方案 C: 逐步實施**
- 分階段實施高級功能
- 優先實施高價值功能
- 使用 MVP 方法

#### 7.2.3 項目後備方案

**方案 A: 範圍調整**
- 縮小項目範圍
- 專注核心功能
- 延遲非核心功能

**方案 B: 資源重新分配**
- 重新評估優先級
- 集中資源到關鍵任務
- 尋求額外資源

**方案 C: 截止日期調整**
- 重新評估時間線
- 調整里程碑
- 通報利益相關者

### 7.3 風險監控

#### 7.3.1 監控指標

| 類別 | 指標 | 警告閾值 | 危機閾值 |
|------|------|---------|---------|
| **學習進度** | 階段完成率 | < 80% | < 60% |
| **技術質量** | 測試覆蓋率 | < 70% | < 50% |
| **項目進度** | 里程碑延遲 | > 1 週 | > 2 週 |
| **團隊健康** | 加班時間 | > 10 小時/週 | > 20 小時/週 |

#### 7.3.2 監控頻率

- **每日**: 團隊站會
- **每週**: 進度審查會議
- **每月**: 風險評估會議
- **每季度**: 全面風險審查

#### 7.3.3 響應機制

**警告級別**:
1. 識別問題
2. 分析原因
3. 制定行動計劃
4. 執行並監控

**危機級別**:
1. 立即通報利益相關者
2. 啟動後備方案
3. 集中資源解決問題
4. 定期進度通報

---

## 8. 時間線和里程碑

### 8.1 總體時間線

```
┌─────────────────────────────────────────────────────────────────────┐
│                          總體時間線 (12+ 個月)                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  階段 1: 初級開發者                                                  │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 週 1-3:   Python/FastAPI 基礎                                │   │
│  │ 週 4-5:   React 19 基礎                                      │   │
│  │ 週 6:     測試驅動開發                                       │   │
│  │ 週 7:     DuckDB 基礎                                        │   │
│  │ 週 8-9:   實踐項目 (CRUD API, 技術指標, Git 規範)            │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                       ↓ 里程碑 1: 初級開發者驗證                   │
│                                                                     │
│  階段 2: 中級開發者                                                  │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 週 10:    VectorBT 學習                                       │   │
│  │ 週 11:    Backtrader 學習                                     │   │
│  │ 週 12:    策略引擎架構                                       │   │
│  │ 週 13:    Zustand 精通                                        │   │
│  │ 週 14:    React Query 精通                                   │   │
│  │ 週 15:    集成測試                                           │   │
│  │ 週 16-20: 實踐項目 (RSI 策略, 策略工廠, 緩存管理, Store)    │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                       ↓ 里程碑 2: 中級開發者驗證                   │
│                                                                     │
│  階段 3: 高級開發者                                                  │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 週 21-23: 複合策略設計                                       │   │
│  │ 週 24-25: 信號合併算法                                       │   │
│  │ 週 26-27: 性能優化                                          │   │
│  │ 週 28-29: E2E 測試                                          │   │
│  │ 週 30:    技術指導                                           │   │
│  │ 週 31-36: 實踐項目 (複合策略, 性能優化, E2E 測試)            │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                       ↓ 里程碑 3: 高級開發者驗證                   │
│                                                                     │
│  階段 4: 高級架構師 (持續)                                          │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 週 37-40: 系統架構設計                                       │   │
│  │ 週 41-42: 技術決策記錄 (ADR)                                 │   │
│  │ 週 43-44: 技術路線圖制定                                     │   │
│  │ 持續:    技術領導力、跨領域整合、團隊建設                    │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                       ↓ 持續成長                                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 8.2 詳細里程碑

#### 里程碑 1: 初級開發者驗證 (第 9 週)

**目標**: 完成階段 1 所有技能和任務

**驗證標準**:
- [ ] 所有 API 端點有完整的單元測試（覆蓋率 ≥ 80%）
- [ ] 所有前端組件有組件測試
- [ ] 所有提交遵循 Conventional Commits 規範（100%）
- [ ] 代碼通過 linter 檢查（ruff, eslint）
- [ ] 代碼通過格式化工具（black, prettier）
- [ ] 能夠獨立完成完整的 CRUD API 實現
- [ ] 能夠實現簡單的技術指標計算
- [ ] 前後端能夠正確交互
- [ ] 能夠處理常見錯誤情況
- [ ] 能夠解釋分層架構的概念
- [ ] 能夠解釋 TDD 的 Red-Green-Refactor 流程
- [ ] 能夠解釋 RESTful API 的設計原則
- [ ] 能夠閱讀和理解現有代碼

**成功標準**: 所有檢查項目必須完成，並且通過代碼審查

**交付物**:
- 完整的 CRUD API 實現
- 簡單的技術指標計算實現
- 單元測試和組件測試
- 代碼審查記錄

#### 里程碑 2: 中級開發者驗證 (第 20 週)

**目標**: 完成階段 2 所有技能和任務

**驗證標準**:
- [ ] 策略實現遵循 IStrategy 接口契約
- [ ] 回測代碼有完整的單元測試和集成測試
- [ ] 測試覆蓋率 ≥ 85%
- [ ] 所有提交遵循 Conventional Commits
- [ ] 代碼審查通過（至少 1 次他人審查）
- [ ] 能夠使用 VectorBT 執行策略回測
- [ ] 能夠正確實現並使用策略工廠
- [ ] 能夠使用 React Query 管理服務端狀態
- [ ] 能夠使用 Zustand 管理全局狀態
- [ ] 能夠編寫集成測試
- [ ] 能夠解釋策略模式的工作原理
- [ ] 能夠解釋向量化計算的性能優勢
- [ ] 能夠解釋 React Query 的緩存策略
- [ ] 能夠審查他人代碼並提供建設性反饋
- [ ] 能夠設計測試策略

**成功標準**: 所有檢查項目必須完成，並且通過代碼審查

**交付物**:
- 完整的 RSI 策略實現
- 策略工廠實現
- React Query 緩存管理實現
- Zustand Store 實現
- 集成測試

#### 里程碑 3: 高級開發者驗證 (第 36 週)

**目標**: 完成階段 3 所有技能和任務

**驗證標準**:
- [ ] 複合策略實現正確
- [ ] 性能優化效果顯著（≥ 30%）
- [ ] E2E 測試覆蓋率 ≥ 70%
- [ ] 測試覆蓋率 ≥ 90%
- [ ] 代碼審查通過（至少 2 次他人審查）
- [ ] 能夠設計和實現複合策略
- [ ] 能夠使用多種信號合併算法
- [ ] 能夠識別和解決性能瓶頸
- [ ] 能夠編寫穩定的 E2E 測試
- [ ] 能夠指導初級和中級開發者
- [ ] 能夠解釋複合策略的設計原則
- [ ] 能夠進行性能分析和優化
- [ ] 能夠設計 E2E 測試策略
- [ ] 能夠進行技術選型和架構設計
- [ ] 能夠提供建設性的代碼審查反饋

**成功標準**: 所有檢查項目必須完成，並且通過代碼審查

**交付物**:
- 複合策略實現
- 性能優化報告
- E2E 測試套件
- 技術指導記錄

#### 里程碑 4: 高級架構師驗證 (持續)

**目標**: 持續達到架構師級別能力

**驗證標準**:
- [ ] 架構設計文檔完整且通過審查
- [ ] ADR 文檔數量 ≥ 5
- [ ] 技術路線圖制定完成
- [ ] 測試覆蓋率 ≥ 90%
- [ ] 代碼審查通過（至少 3 次他人審查）
- [ ] 能夠設計可擴展的系統架構
- [ ] 能夠進行技術選型和決策
- [ ] 能夠制定技術路線圖
- [ ] 能夠進行跨領域知識整合
- [ ] 能夠領導技術團隊
- [ ] 能夠解釋微服務架構的優缺點
- [ ] 能夠進行架構演進設計
- [ ] 能夠制定技術債償還計劃
- [ ] 能夠建立技術文化
- [ ] 能夠進行技術規劃和路線圖制定

**成功標準**: 所有檢查項目必須完成，並且通過架構審查

**交付物**:
- 系統架構設計文檔
- 技術決策記錄 (ADR)
- 技術路線圖
- 團隊建設計劃

### 8.3 季度評估點

#### Q1 2026 (第 1-12 週)

**目標**: 完成階段 1，開始階段 2

**關鍵成就**:
- ✅ 掌握 Python/FastAPI 基礎
- ✅ 掌握 React 19 基礎
- ✅ 建立測試驅動開發習慣
- ✅ 完成 CRUD API 實現
- ✅ 完成簡單技術指標計算

**評估指標**:
- 測試覆蓋率: ≥ 70%
- 代碼審查通過率: ≥ 85%
- 任務完成率: ≥ 90%

#### Q2 2026 (第 13-24 週)

**目標**: 完成階段 2

**關鍵成就**:
- ✅ 掌握 VectorBT 和 Backtrader
- ✅ 實現完整的 RSI 策略
- ✅ 實現策略工廠
- ✅ 掌握 React Query 和 Zustand
- ✅ 建立集成測試能力

**評估指標**:
- 測試覆蓋率: ≥ 80%
- 代碼審查通過率: ≥ 90%
- 任務完成率: ≥ 90%

#### Q3 2026 (第 25-36 週)

**目標**: 完成階段 3

**關鍵成就**:
- ✅ 掌握複合策略設計
- ✅ 實現性能優化
- ✅ 建立 E2E 測試能力
- ✅ 建立技術指導能力

**評估指標**:
- 測試覆蓋率: ≥ 85%
- 代碼審查通過率: ≥ 90%
- 任務完成率: ≥ 90%

#### Q4 2026 (第 37-48 週)

**目標**: 開始階段 4

**關鍵成就**:
- ✅ 設計系統架構
- ✅ 建立技術決策記錄機制
- ✅ 制定技術路線圖
- ✅ 建立技術領導力

**評估指標**:
- 測試覆蓋率: ≥ 90%
- 代碼審查通過率: ≥ 95%
- 任務完成率: ≥ 90%

### 8.4 年度總結

#### 2026 年度目標

**技術目標**:
- ✅ 完成從初級到高級開發者的能力建設
- ✅ 建立測試驅動開發文化
- ✅ 建立代碼審查機制
- ✅ 完成統一策略引擎
- ✅ 完成 React Query 遷移
- ✅ 建立 CI/CD 自動化基礎設施

**個人目標**:
- ✅ 掌握全棧開發技能
- ✅ 建立系統架構思維
- ✅ 建立技術指導能力
- ✅ 建立技術領導力

**團隊目標**:
- ✅ 提升整體代碼質量
- ✅ 建立技術文化
- ✅ 建立知識共享機制
- ✅ 建立持續改進機制

---

## 結論

本設計規劃文檔整合了 a005-competencies.md、a006a-5.md 和 a006c-1.md 的所有前期成果，為 Programmer Sub-Agent 提供了一套完整的能力建設和實施路徑。

### 核心價值

1. **漸進式能力建設**: 4 階段路徑，從初級到架構師
2. **實踐優先**: 通過實際項目和代碼示例學習
3. **測試驅動**: 每個階段都強調 TDD，確保代碼質量
4. **持續改進**: 建立評估機制和反饋循環
5. **風險管理**: 完整的風險識別和後備方案

### 預期成果

- **文檔成果**: 完整的設計規劃文檔，包含 8 個章節和具體執行計劃
- **能力成果**: 清晰的能力模型和技能矩陣，支持 4 階段能力建設
- **實施成果**: 可執行的實施路徑，包含 8-9 週初級、10-11 週中級、12-16 週高級、持續架構師階段
- **質量成果**: 測試驅動開發文化和代碼審查機制
- **風險成果**: 完整的風險識別和後備方案

### 下一步行動

1. **立即開始**: 從階段 1 的任務 1.1 開始實施
2. **定期評估**: 每週、每月、每季度進行評估
3. **持續改進**: 根據評估結果調整計劃
4. **知識分享**: 定期進行技術分享和知識沉淀
5. **團隊協作**: 與團隊成員協作，共同成長

---

**文檔版本**: 1.0
**創建日期**: 2026-02-21
**最後更新**: 2026-02-21
**狀態**: Active
**下次審查**: 2026-05-21 (3 個月後)
