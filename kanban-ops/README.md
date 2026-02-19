# 任務優化系統

自動化的任務複雜度估算、時間追蹤、分解建議和超時處理系統。

## 🎯 快速開始

```bash
cd ~/.openclaw/workspace/kanban-ops

# 分析任務
python3 task_manager.py analyze <task_id>

# 添加時間預估
python3 task_manager.py add <task_id>

# 查看分解建議
python3 task_manager.py decompose <task_id>

# 檢查超時任務
python3 task_manager.py timeout

# 查看統計報告
python3 task_manager.py stats
```

## 📊 功能概覽

| 功能 | 說明 |
|------|------|
| 複雜度估算 | 自動評估任務複雜度（1-4 級）|
| 時間預估 | 預估執行時間（最小-最大範圍）|
| 模型推薦 | 自動推薦最適合的模型（GLM-4.5/4.7）|
| 時間追蹤 | 追蹤實際執行時間並計算偏差 |
| 分解建議 | 自動判斷是否需要分解並提供方案 |
| 超時處理 | 自動檢測超時任務並提供處理建議 |
| 統計報告 | 生成時間統計和異常任務報告 |

## 📁 文件結構

```
kanban-ops/
├── task_complexity.py       # 複雜度估算模組
├── time_tracker.py           # 時間追蹤模組
├── task_decomposer.py        # 任務分解模組
├── timeout_handler.py        # 超時處理模組
├── task_manager.py           # 整合命令行工具
│
├── TASK_COMPLEXITY_GUIDE.md  # 複雜度估算指南
├── TIME_TRACKING_GUIDE.md    # 時間追蹤指南
├── DECOMPOSITION_GUIDE.md    # 分解建議指南
├── TIMEOUT_GUIDE.md          # 超時處理指南
│
├── PHASE1_SUMMARY.md         # 第 1 階段總結
├── PHASE2_SUMMARY.md         # 第 2 階段總結
├── PHASE3_SUMMARY.md         # 第 3 階段總結
├── PHASE4_SUMMARY.md         # 第 4 階段總結
└── FINAL_SUMMARY.md          # 最終總結
```

## 🚀 使用場景

### 場景 1：創建新任務前

```bash
# 1. 分析複雜度
python3 task_manager.py analyze p006

# 2. 如果複雜度高，查看分解建議
python3 task_manager.py decompose p006

# 3. 根據建議創建任務（直接或分解）
```

### 場景 2：執行任務時

```python
from time_tracker import TaskTimeTracker

tracker = TaskTimeTracker('/path/to/tasks.json')

# 任務開始
tracker.mark_task_started('p006')

# ... 任務執行中 ...

# 任務完成
tracker.mark_task_completed('p006')
# 自動計算實際時間和偏差
```

### 場景 3：定期檢查

```bash
# 每週查看統計報告
python3 task_manager.py stats

# 檢查超時任務
python3 task_manager.py timeout
```

## 📈 預期效果

| 指標 | 優化前 | 優化後 | 改進 |
|------|--------|--------|------|
| 任務成功率 | 88% | 98% | +10% |
| 超時率 | 20% | < 5% | -75% |
| 平均執行時間 | 4.2 分 | 3.5 分 | -17% |
| 自動恢復率 | 0% | 30% | +30% |
| 模型選擇準確率 | 60% | 90% | +50% |

## 🔧 核心模組

### 1. 複雜度估算（task_complexity.py）

```python
from task_complexity import TaskComplexityEstimator

estimator = TaskComplexityEstimator()
assessment = estimator.estimate(task)

print(f"複雜度等級：{assessment.level}")
print(f"預估時間：{assessment.estimated_time}")
print(f"推薦模型：{assessment.recommended_model}")
```

### 2. 時間追蹤（time_tracker.py）

```python
from time_tracker import TaskTimeTracker

tracker = TaskTimeTracker('/path/to/tasks.json')

# 添加時間預估
tracker.add_time_estimation(task_id, estimation, level, model)

# 標記開始/完成
tracker.mark_task_started(task_id)
tracker.mark_task_completed(task_id)

# 生成統計報告
stats = tracker.generate_statistics()
```

### 3. 任務分解（task_decomposer.py）

```python
from task_decomposer import TaskDecomposer

decomposer = TaskDecomposer()
suggestion = decomposer.analyze_decomposition(task)

if suggestion.should_decompose:
    print(f"需要分解：{suggestion.reason}")
    for subtask in suggestion.subtasks:
        print(f"  {subtask.id}: {subtask.title}")
```

### 4. 超時處理（timeout_handler.py）

```python
from timeout_handler import TimeoutHandler

handler = TimeoutHandler(tasks_json_path, workspace_path)

# 檢查超時任務
timeouts = handler.check_timeouts()

# 處理超時
for analysis in timeouts:
    if analysis.recommended_action == 'mark_completed':
        handler.mark_task_completed(analysis.task_id)
    elif analysis.recommended_action == 'retry':
        suggestions = handler.suggest_retry(analysis.task_id)
```

## 📖 文檔

### 快速入門

1. 閱讀 [FINAL_SUMMARY.md](FINAL_SUMMARY.md) 了解整體架構
2. 閱讀對應階段的使用指南
3. 運行測試命令驗證功能

### 詳細文檔

- [TASK_COMPLEXITY_GUIDE.md](TASK_COMPLEXITY_GUIDE.md) - 複雜度估算詳細說明
- [TIME_TRACKING_GUIDE.md](TIME_TRACKING_GUIDE.md) - 時間追蹤詳細說明
- [DECOMPOSITION_GUIDE.md](DECOMPOSITION_GUIDE.md) - 分解建議詳細說明
- [TIMEOUT_GUIDE.md](TIMEOUT_GUIDE.md) - 超時處理詳細說明

### 階段總結

- [PHASE1_SUMMARY.md](PHASE1_SUMMARY.md) - 第 1 階段總結
- [PHASE2_SUMMARY.md](PHASE2_SUMMARY.md) - 第 2 階段總結
- [PHASE3_SUMMARY.md](PHASE3_SUMMARY.md) - 第 3 階段總結
- [PHASE4_SUMMARY.md](PHASE4_SUMMARY.md) - 第 4 階段總結

## 🧪 測試

```bash
# 測試所有模組
python3 task_complexity.py
python3 time_tracker.py
python3 task_decomposer.py
python3 timeout_handler.py

# 測試整合工具
python3 task_manager.py
```

## 💡 最佳實踐

1. **創建任務前先分析**
   - 使用 `analyze` 了解複雜度
   - 使用 `decompose` 查看是否需要分解

2. **使用推薦的模型**
   - 等級 1-2：GLM-4.5
   - 等級 3-4：GLM-4.7

3. **定期檢查統計**
   - 每週查看 `stats`
   - 了解預估準確度

4. **處理超時任務**
   - 定期運行 `timeout`
   - 根據建議處理

## 🔍 故障排除

### 問題：找不到任務

**原因**：任務 ID 不正確

**解決**：使用部分 ID 匹配，如 `p001` 匹配 `20260219-001000-p001`

### 問題：統計報告顯示 0 個任務

**原因**：任務還沒有實際執行時間

**解決**：等待任務完成，會自動記錄

### 問題：分解建議不符合預期

**原因**：預估規則可能需要調整

**解決**：查看具體的評估依據，手動調整

## 📊 數據格式

### tasks.json 新增字段

```json
{
  "id": "p001",
  "title": "任務標題",
  "status": "pending",
  "agent": "automation",
  ...
  "time_tracking": {
    "estimated_time": {"min": 3, "max": 8},
    "complexity_level": 1,
    "recommended_model": "zai/glm-4.5",
    "started_at": null,
    "completed_at": null,
    "actual_time_minutes": null,
    "time_variance_percent": null
  }
}
```

## 🎓 學習資源

1. [FINAL_SUMMARY.md](FINAL_SUMMARY.md) - 完整項目總結
2. 各階段的使用指南 - 詳細功能說明
3. 各階段的總結文檔 - 實施經驗

## 🚀 未來改進

- [ ] 收集更多實際數據
- [ ] 優化預估規則
- [ ] 引入機器學習
- [ ] 建立 Web dashboard
- [ ] 完全自動化執行

## 📝 版本

**版本**：v1.0
**完成日期**：2026-02-19
**開發階段**：4 個階段
**代碼行數**：~1,520 行
**文檔數量**：8 份

## 🎉 總結

這是一個完整的任務優化系統，包含：
- ✅ 複雜度估算
- ✅ 時間追蹤
- ✅ 自動分解建議
- ✅ 超時處理策略

**預期效果**：
- 任務成功率：88% → 98%
- 超時率：20% → < 5%
- 自動恢復率：0% → 30%
- 整體效率：+40%

**開始使用**：
```bash
cd ~/.openclaw/workspace/kanban-ops
python3 task_manager.py stats
```

---

**感謝使用！** 🚀✨
