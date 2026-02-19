# 时间追踪方法

## 时间追踪字段

在 tasks.json 中，每个任务可以包含 `time_tracking` 对象：

```json
{
  "time_tracking": {
    "estimated_time": {
      "min": 3,
      "max": 8
    },
    "complexity_level": 1,
    "recommended_model": "zai/glm-4.5",
    "started_at": "2026-02-19T21:30:00",
    "completed_at": "2026-02-19T21:35:00",
    "actual_time_minutes": 5.2,
    "time_variance_percent": -12.5
  }
}
```

## 时间计算公式

### 预估中点
```
预估中点 = (min + max) / 2
```

**示例：**
```
预估：8-18 分钟
中点 = (8 + 18) / 2 = 13 分钟
```

### 偏差百分比
```
偏差百分比 = (实际时间 - 预估中点) / 预估中点 × 100%
```

**示例：**
```
预估中点：13 分钟
实际时间：10 分钟
偏差 = (10 - 13) / 13 × 100% = -23.1%
```

## 偏差解读

| 偏差范围 | 解读 | 行动 |
|----------|------|------|
| -30% ~ +30% | 正常范围 | 无需调整 |
| +30% ~ +60% | 低于预估 | 考虑增加预估下限 |
| +60% 以上 | 严重低估 | 必须调整系数 |
| -30% ~ -60% | 高于预估 | 考虑减少预估下限 |
| -60% 以上 | 严重高估 | 必须调整系数 |

## 使用流程

### 1. 任务开始时
```python
from time_tracker import TaskTimeTracker

tracker = TaskTimeTracker('/path/to/tasks.json')
tracker.mark_task_started('task-id')
```

### 2. 任务完成时
```python
tracker.mark_task_completed('task-id')
# 自动计算：
# - actual_time_minutes
# - time_variance_percent
```

### 3. 查看统计报告
```bash
python3 task_manager.py stats
```

## 统计指标

### 按复杂度等级
- 每个等级的平均实际时间
- 在预估范围内的任务数量
- 超过/低于预估的任务数量

### 按任务类型
- automation、research、analyst、creative 的平均时间
- 每种类型的成功率
- 每种类型的超时率

### 按模型
- GLM-4.5 vs GLM-4.7 的平均时间
- 每种模型的预估准确度
- 每种模型的超时率

## 持续优化循环

```
1. 收集数据（50+ 任务）
   ↓
2. 分析统计报告
   ↓
3. 识别模式（哪些任务类型偏差大？）
   ↓
4. 调整公式系数
   ↓
5. 重新验证
   ↓
返回步骤 1
```

## 目标指标

**短期（1 个月）：**
- 预估准确度：75%
- 平均偏差：±20%

**中期（3 个月）：**
- 预估准确度：85%
- 平均偏差：±15%

**长期（6 个月）：**
- 预估准确度：90%
- 平均偏差：±10%
