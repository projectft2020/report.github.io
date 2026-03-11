# 成本優化 - 構建完成報告

## 時間：2026-03-05 17:50

## 執行摘要

成功實現成本優化框架，為多模型架構添加了成本追蹤、複雜度評估和預算管理能力。當前處於 P0 階段，基礎框架已建立，可以逐步啟用成本優化功能。

## 完成的工作

### 1. 模型配置增強 ✅
**文件：** `kanban-ops/models.json`（版本 1.1.0）

**新增內容：**

#### 預算配置
```json
{
  "budget": {
    "daily_limit": 50,
    "weekly_limit": 300,
    "monthly_limit": 1200,
    "currency": "CNY",
    "current_spend": 0.0,
    "spend_today": 0.0,
    "spend_this_week": 0.0,
    "spend_this_month": 0.0,
    "spend_history": []
  }
}
```

#### 複雜度等級定義
```json
{
  "complexity_levels": {
    "L1": {
      "name": "簡單",
      "estimated_time_max": 15,
      "allowed_agents": ["research", "automation", "developer"],
      "min_priority": "low",
      "recommended_models": ["zai/glm-4.5"],
      "cost_optimal": true
    },
    "L2": {
      "name": "中等",
      "estimated_time_min": 15,
      "estimated_time_max": 45,
      "recommended_models": ["zai/glm-4.7", "zai/glm-4.5"],
      "cost_optimal": false
    },
    "L3": {
      "name": "複雜",
      "estimated_time_min": 45,
      "recommended_models": ["zai/glm-4.7"],
      "cost_optimal": false
    }
  }
}
```

#### 模型成本元數據
```json
{
  "cost_metadata": {
    "cost_per_1k_tokens": 0.005,
    "cost_per_1k_output": 0.01,
    "cost_factor": 1.0,
    "currency": "CNY",
    "estimated_cost_per_request": 0.15,
    "estimated_time_per_request": 45
  }
}
```

### 2. 成本優化器 ✅
**文件：** `kanban-ops/cost_optimizer.py`

**核心功能：**

#### 任務複雜度評估
```python
def calculate_complexity(task: dict) -> str:
    """
    評估維度：
    1. 預估時間（從 task.time_tracking.estimated_time）
    2. 任務類型（task.agent）
    3. 依賴數量（len(task.dependencies)）
    4. 優先級（task.priority）

    返回：L1（簡單）, L2（中等）, L3（複雜）
    """
```

**評估公式：**
```
複雜度分數 = 平均時間 × 代理權重 × 依賴權重 × 優先級權重

代理權重：
  research: 1.0
  automation: 0.8
  developer: 0.9
  analyst: 1.5
  creative: 1.3
  architect: 1.6
  mentors: 1.7

依賴權重：1.0 + (依賴數量 × 0.1)

優先級權重：
  low: 0.8
  normal/medium: 1.0
  high: 1.5

分數範圍：
  L1（簡單）: ≤ 20
  L2（中等）: 20-60
  L3（複雜）: > 60
```

#### 成本感知的模型選擇
```python
def select_cost_optimal_model(task: dict, budget_mode: str) -> Optional[str]:
    """
    預算模式：
    - normal: 正常模式（品質優先）
    - warning: 預算警告（>70%，L1 任務使用低成本）
    - critical: 預算緊張（>90%，L1+L2 任務使用低成本）
    - exceeded: 預算超支（停止新任務）

    返回：最佳模型 ID
    """
```

**選擇策略：**

| 預算模式 | L1（簡單） | L2（中等） | L3（複雜） |
|---------|----------|----------|----------|
| normal  | glm-4.7  | glm-4.7  | glm-4.7  |
| warning | glm-4.5 → glm-4.7 | glm-4.7 | glm-4.7 |
| critical| glm-4.5 → glm-4.7 | glm-4.5 → glm-4.7 | glm-4.7 |
| exceeded| 停止新任務 | 停止新任務 | 停止新任務 |

#### 預算狀態檢查
```python
def check_budget_status(self) -> dict:
    """
    檢查：
    - 每日預算使用率
    - 每週預算使用率
    - 預算模式判斷
    - 生成建議

    返回：預算狀態字典
    """
```

#### 成本追蹤
```python
def track_cost(model_id: str, cost: float, task_id: str):
    """
    追蹤成本到：
    - 模型統計（total_cost, cost_by_date）
    - 總預算（current_spend, spend_today, spend_this_week）
    - 歷史記錄（spend_history）
    """
```

#### 任務成本預估
```python
def estimate_task_cost(model_id: str, task: dict) -> float:
    """
    預估公式：
    預估成本 = 模型基準成本 × 複雜度因子

    複雜度因子：
    - L1: 0.8
    - L2: 1.0
    - L3: 1.5
    """
```

### 3. 集成到自動啟動流程 ✅
**文件：** `kanban-ops/auto_spawn_heartbeat.py`（已更新）

**改進內容：**

#### 導入成本優化器
```python
try:
    from cost_optimizer import CostOptimizer
    COST_OPTIMIZER_AVAILABLE = True
except ImportError:
    COST_OPTIMIZER_AVAILABLE = False
```

#### 主函數中檢查預算狀態
```python
# 成本優化器狀態檢查
if COST_OPTIMIZER_AVAILABLE:
    optimizer = CostOptimizer(str(MODELS_JSON))
    budget_status = optimizer.check_budget_status()
    budget_mode = budget_status.get("budget_mode", "normal")
    log("INFO", f"💰 成本優化器：預算模式 {budget_mode}")
    # ...
```

#### 任務分配時使用成本優化
```python
# 模型選擇邏輯（優先級：metadata.model > task.model > CostOptimizer > ModelAllocator > 默認 glm-4.7）
if not model and cost_optimizer:
    try:
        model = cost_optimizer.select_cost_optimal_model(task, budget_mode)
        # ...
```

### 4. 測試套件 ✅

**測試結果：** 所有測試通過 ✅

**測試覆蓋：**
1. 任務複雜度評估（3 個測試任務）
2. 預算狀態檢查
3. 成本最優模型選擇（3 種預算模式）
4. 任務成本預估（2 個模型 × 3 個複雜度）
5. 成本追蹤
6. 成本報告生成

## 系統特性

### ✅ 已實現（P0）

1. **複雜度評估**
   - 基於任務元數據的評估
   - 多維度權重計算
   - 三級複雜度分類（L1, L2, L3）

2. **成本追蹤**
   - 模型級別成本統計
   - 日期級別成本統計
   - 預算使用率追蹤
   - 成本歷史記錄

3. **預算管理**
   - 每日/每週/每月預算限制
   - 預算使用率計算
   - 預算模式判斷（normal, warning, critical, exceeded）

4. **成本感知的模型選擇**
   - 根據預算模式調整策略
   - 支持分層降級
   - 優先級邏輯集成

5. **集成到心跳流程**
   - 自動檢查預算狀態
   - 自動選擇成本最優模型
   - 預算超支時自動停止

### 🚧 待實現（P1+）

**P1（短期 1-2 週）：**
- [ ] 成本報告生成和發送
- [ ] 預算警告通知
- [ ] 成本趨勢分析

**P2（中期 2-4 週）：**
- [ ] 智能批次處理（批量執行相同類型任務）
- [ ] 緩存機制優化（避免重複計算）
- [ ] 自動成本優化策略（基於歷史數據）

**P3（長期 1-3 個月）：**
- [ ] 成本效益分析
- [ ] 實時成本預測
- [ ] 動態預算調整

## 當前狀態

### 配置狀態

**預算配置：**
- 每日預算：¥50
- 每週預算：¥300
- 每月預算：¥1200
- 當前花費：¥0（剛啟動）

**模型配置：**
- glm-4.7: cost_factor = 1.0, estimated_cost_per_request = ¥0.15
- glm-4.5: cost_factor = 0.4, estimated_cost_per_request = ¥0.06

**預算模式：** normal（預算充足）

### 行為

**正常模式（預算充足）：**
- 所有任務使用 glm-4.7
- 保持高品質輸出
- 成本追蹤啟用

**預算警告模式（>70%）：**
- L1 任務優先使用 glm-4.5
- L2、L3 任務保持 glm-4.7
- 降低整體成本

**預算緊張模式（>90%）：**
- L1、L2 任務優先使用 glm-4.5
- L3 任務保持 glm-4.7（保證核心品質）
- 嚴格控制新任務

**預算超支模式（>100%）：**
- 停止啟動新任務
- 只完成已啟動的任務
- 等待預算重置

## 測試結果

### 複雜度評估測試

```
任務 1: research, low, 10-15 min → L1（簡單）✅
任務 2: analyst, high, 45-60 min, 3 依賴 → L3（複雜）✅
任務 3: creative, medium, 30-45 min, 1 依賴 → L2（中等）✅
```

### 成本預估測試

```
L1 任務使用 glm-4.7: ¥0.120
L1 任務使用 glm-4.5: ¥0.048（節省 60%）

L2 任務使用 glm-4.7: ¥0.150
L2 任務使用 glm-4.5: ¥0.060（節省 60%）

L3 任務使用 glm-4.7: ¥0.225
L3 任務使用 glm-4.5: ¥0.090（節省 60%）
```

### 成本追蹤測試

```
✅ 成本追蹤：zai/glm-4.7 +¥0.15 (任務: test-task-001)
✅ 成本追蹤：zai/glm-4.5 +¥0.06 (任務: test-task-002)
```

## 下一步行動

### 短期（1-2 週）

1. **監控成本追蹤**
   - 觀察實際成本記錄
   - 驗證成本預估準確性
   - 調整預估因子

2. **實現成本報告**
   - 每日成本報告
   - 每週成本報告
   - 成本趨勢圖表

3. **實現預算警告**
   - 預算警告通知
   - 預算超支警報
   - 自動提醒機制

### 中期（2-4 週）

4. **啟用成本優化（可選）**
   - 根據實際情況決定是否啟用
   - 評驗成本優化效果
   - 調整優化策略

5. **智能批次處理**
   - 識別可批量處理的任務
   - 實現批次執行邏輯
   - 測試批次處理效果

### 長期（1-3 個月）

6. **成本效益分析**
   - 分析花費與產出的關係
   - 識別高成本任務
   - 優化任務流程

7. **實時成本預測**
   - 基於歷史數據預測
   - 動態調整預算
   - 智能成本控制

## 關鍵洞察

1. **漸進式實施**
   - 先建立基礎（P0），再逐步優化（P1+）
   - 避免一次性改變太大
   - 確保系統穩定

2. **品質優先原則**
   - 成本優化不犧牲核心品質
   - L3 任務始終使用高品質模型
   - 分層降級策略

3. **數據驅動決策**
   - 基於實際數據調整策略
   - 持續監控和優化
   - 避免盲目優化

4. **靈活配置**
   - 預算限制可調整
   - 複雜度因子可優化
   - 選擇策略可擴展

---

**構建完成時間：** 2026-03-05 17:50
**構建者：** Charlie (Orchestrator)
**狀態：** ✅ P0 完成
**版本：** 1.0.0
**下一步：** 監控成本追蹤，實現成本報告
