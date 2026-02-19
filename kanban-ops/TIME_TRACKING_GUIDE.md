# 第 2 階段使用指南：時間預估 + 追蹤

## 概述

第 2 階段在 tasks.json 中添加了 `time_tracking` 字段，追蹤任務的預估時間和實際執行時間。

---

## 快速開始

### 1. 為任務添加時間預估

```bash
ssh charlie@192.168.1.117
cd ~/.openclaw/workspace/kanban-ops
python3 task_manager.py add p001
```

**輸出**：
```
✅ 已為任務 p001 添加時間預估：3-8 分鐘

   複雜度：等級 1
   預估時間：3-8 分鐘
   推薦模型：zai/glm-4.5
```

### 2. 分析任務複雜度

```bash
python3 task_manager.py analyze p001
```

**輸出**：
```
📊 任務複雜度分析：20260219-001000-p001
標題：建立專案索引地圖

等級：1 - 簡單任務
分數：1.0
預估時間：3-8 分鐘
推薦模型：zai/glm-4.5

評估依據：
  任務類型：自動化 (+1.0)
```

### 3. 查看統計報告

```bash
python3 task_manager.py stats
```

**輸出**：
```
📊 任務時間統計報告
────────────────────────────
總任務數：5
已追蹤任務：5
已完成並記錄時間：0

預估準確度：
  在預估範圍內：0 任務
  超過預估：0 任務
  低於預估：0 任務
```

---

## tasks.json 結構

### 新增字段

```json
{
  "id": "20260219-001000-p001",
  "title": "建立專案索引地圖",
  "status": "pending",
  "agent": "automation",
  ...
  "time_tracking": {
    "estimated_time": {
      "min": 3,
      "max": 8
    },
    "complexity_level": 1,
    "recommended_model": "zai/glm-4.5",
    "started_at": null,
    "completed_at": null,
    "actual_time_minutes": null,
    "time_variance_percent": null
  }
}
```

### 字段說明

| 字段 | 類型 | 說明 |
|------|------|------|
| `time_tracking` | object | 時間追蹤記錄 |
| `estimated_time.min` | int | 預估最小時間（分鐘）|
| `estimated_time.max` | int | 預估最大時間（分鐘）|
| `complexity_level` | int | 複雜度等級（1-4）|
| `recommended_model` | string | 推薦的模型 |
| `started_at` | string | 任務開始時間（ISO 8601）|
| `completed_at` | string | 任務完成時間（ISO 8601）|
| `actual_time_minutes` | float | 實際執行時間（分鐘）|
| `time_variance_percent` | float | 時間偏差百分比 |

---

## 時間偏差計算

```
預估中點 = (estimated_time.min + estimated_time.max) / 2

時間偏差 = ((實際時間 - 預估中點) / 預估中點) × 100%
```

### 判斷標準

| 偏差範圍 | 判斷 | 說明 |
|----------|------|------|
| -20% ~ +20% | ✅ 在預估範圍內 | 實際時間在預估最小和最大之間 |
| < -20% | ⬇️ 低於預估 | 實際時間 < 預估最小值 |
| \> +20% | ⬆️ 超過預估 | 實際時間 > 預估最大值 |

---

## 使用場景

### 場景 1：創建新任務

**步驟**：
1. 創建任務時不指定時間
2. 使用 `task_manager.py add` 添加時間預估
3. 根據推薦選擇模型

```bash
# 1. 創建任務（通過你的系統）
# 2. 添加時間預估
python3 task_manager.py add p006
```

### 場景 2：開始執行任務

```python
from time_tracker import TaskTimeTracker

tracker = TaskTimeTracker('/Users/charlie/.openclaw/workspace/kanban/tasks.json')

# 標記任務開始
tracker.mark_task_started('p001')
```

### 場景 3：任務完成

```python
# 標記任務完成
tracker.mark_task_completed('p001')

# 自動計算：
# - actual_time_minutes
# - time_variance_percent
```

### 場景 4：定期檢查統計

```bash
# 每週查看統計報告
python3 task_manager.py stats
```

**報告內容**：
- 總任務數、已追蹤任務數
- 預估準確度（在範圍內/超過/低於）
- 平均偏差
- 按複雜度分類的統計
- 偏差較大的異常任務

---

## Python API

### TaskTimeTracker 類

```python
from time_tracker import TaskTimeTracker, TimeEstimate

tracker = TaskTimeTracker('/path/to/tasks.json')

# 添加時間預估
tracker.add_time_estimation(
    task_id='p001',
    estimation=TimeEstimate(min_minutes=5, max_minutes=10),
    complexity_level=2,
    recommended_model='zai/glm-4.5'
)

# 標記任務開始
tracker.mark_task_started('p001')

# 標記任務完成
tracker.mark_task_completed('p001')

# 生成統計報告
stats = tracker.generate_statistics()

# 獲取異常任務
outliers = tracker.get_outliers(threshold_percent=30.0)
```

### TaskManager 類

```python
from task_manager import TaskManager

manager = TaskManager('/path/to/tasks.json')

# 分析任務
manager.analyze_task('p001')

# 添加時間預估
manager.add_estimation_to_task('p001')

# 顯示統計
manager.show_statistics()
```

---

## 命令行工具

### task_manager.py

```bash
# 分析任務
python3 task_manager.py analyze <task_id>

# 添加時間預估
python3 task_manager.py add <task_id>

# 顯示統計
python3 task_manager.py stats
```

### time_tracker.py

```bash
# 顯示統計報告
python3 time_tracker.py
```

### task_complexity.py

```bash
# 運行測試案例
python3 task_complexity.py
```

---

## 實際範例

### 範例 1：簡單任務（p001）

**任務**：建立專案索引地圖

**評估**：
```
等級：1 - 簡單任務
分數：1.0
預估時間：3-8 分鐘
推薦模型：zai/glm-4.5
```

**tasks.json**：
```json
{
  "time_tracking": {
    "estimated_time": {"min": 3, "max": 8},
    "complexity_level": 1,
    "recommended_model": "zai/glm-4.5"
  }
}
```

### 範例 2：複雜任務（p002-p005）

**任務**：基礎回測、策略對比、蒙特卡洛模擬、動態風險調整

**評估**：
```
等級：3 - 複雜任務
分數：~5.0
預估時間：15-35 分鐘
推薦模型：zai/glm-4.7
```

**說明**：
- analyst 代理（+2.0 分）
- 需要複雜分析（+0.5 分關鍵詞）
- 推薦使用 GLM-4.7

---

## 統計報告解讀

### 基本統計

```
總任務數：5
已追蹤任務：5
已完成並記錄時間：0
```

**說明**：
- `總任務數`：tasks.json 中的所有任務
- `已追蹤任務`：有 time_tracking 字段的任務
- `已完成並記錄時間`：有 actual_time_minutes 的任務

### 預估準確度

```
在預估範圍內：2 任務
超過預估：1 任務
低於預估：0 任務
平均偏差：+15.3%
```

**說明**：
- `在預估範圍內`：實際時間在 [min, max] 範圍內
- `超過預估`：實際 > max
- `低於預估`：實際 < min
- `平均偏差`：正值表示平均超時，負值表示平均提前

### 按複雜度統計

```
等級 1：
  任務數：3
  平均時間：6.5 分鐘
  在範圍內：2 | 超預估：1 | 低預估：0

等級 3：
  任務數：2
  平均時間：25.3 分鐘
  在範圍內：1 | 超預估：1 | 低預估：0
```

---

## 集成到工作流程

### 在創建任務時

```python
from task_manager import TaskManager

manager = TaskManager('/path/to/tasks.json')

# 創建任務
task = {
    'title': '量化策略回測',
    'agent': 'analyst',
    'input_paths': ['strategy.md'],
    'notes': '回測移動平均線策略'
}

# 自動添加時間預估
full_task = manager.create_task_with_estimation(task)

# 保存到 tasks.json
...
```

### 在執行任務時

```python
from time_tracker import TaskTimeTracker

tracker = TaskTimeTracker('/path/to/tasks.json')

# 任務開始
tracker.mark_task_started(task_id)

# ... 執行任務 ...

# 任務完成
tracker.mark_task_completed(task_id)
```

### 在查看結果時

```bash
# 查看統計報告
python3 task_manager.py stats

# 查看異常任務（偏差 > 30%）
python3 time_tracker.py | grep -A 10 "偏差較大"
```

---

## 故障排除

### 問題 1：找不到任務

```
❌ 找不到任務：p001
```

**解決**：
- 檢查任務 ID 是否正確
- 可以使用部分 ID（如 `p001` 匹配 `20260219-001000-p001`）

### 問題 2：任務沒有 time_tracking 字段

**解決**：
- 使用 `python3 task_manager.py add <task_id>` 添加
- 複雜度會自動計算

### 問題 3：統計報告顯示 0 個任務

**原因**：
- 任務還沒有 `actual_time_minutes`

**解決**：
- 等待任務完成
- 使用 `tracker.mark_task_completed(task_id)` 記錄完成時間

---

## 下一步

### 第 3 階段：自動分解建議（後天）

**計劃**：
- 根據複雜度自動建議分解方案
- 生成子任務模板
- 驗證分解後的成功率

### 第 4 階段：超時處理策略（本週）

**計劃**：
- 自動檢測超時任務
- 檢查輸出文件是否存在
- 自動重試或標記失敗

---

## 總結

第 2 階段完成後，我們可以：

✅ 自動估算任務時間
✅ 追蹤實際執行時間
✅ 計算預估準確度
✅ 識別異常任務
✅ 生成統計報告

**預期效果**：
- 建立歷史數據庫
- 持續優化預估準確度
- 提前識別問題任務
