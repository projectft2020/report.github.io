---
name: task-optimizer
description: 任务复杂度分析、时间预估、自动分解建议和超时处理的完整系统。在创建或执行任务前使用此技能自动分析复杂度、推荐模型、判断是否需要分解、预估执行时间，并处理超时任务。
---

# Task Optimizer - 任务优化系统

此技能提供完整的任务优化系统，帮助你在创建或执行任务时做出数据驱动的决策。

## 核心功能

1. **复杂度分析** - 5 维度评估任务复杂度（1-4 级）
2. **时间预估** - 基于复杂度的准确时间范围预测
3. **模型推荐** - GLM-4.5 vs GLM-4.7 自动选择
4. **分解建议** - 智能判断是否需要拆分任务
5. **时间追踪** - 记录实际时间，计算偏差
6. **超时处理** - 自动检测和处理超时任务

## 快速开始

### 场景 1：创建任务前分析

当你需要创建一个新任务时，先分析其复杂度：

```bash
python3 scripts/task_manager.py analyze <task-id>
```

输出包括：
- 复杂度等级（1-4）
- 预估时间范围
- 推荐模型
- 是否需要分解

### 场景 2：复杂任务分解建议

如果任务复杂度高（等级 3-4），查看分解建议：

```bash
python3 scripts/task_manager.py decompose <task-id>
```

输出包括：
- 是否需要分解
- 推荐的分解策略
- 具体的子任务方案
- 预估时间节省

### 场景 3：追踪任务时间

在执行任务时记录开始和完成时间：

```python
from scripts.time_tracker import TaskTimeTracker

tracker = TaskTimeTracker('/path/to/tasks.json')

# 任务开始
tracker.mark_task_started('task-id')

# ... 执行任务 ...

# 任务完成
tracker.mark_task_completed('task-id')
```

### 场景 4：检查超时任务

定期检查是否有任务超时（默认阈值 30 分钟）：

```bash
python3 scripts/task_manager.py timeout
```

输出包括：
- 超时任务列表
- 推荐处理动作（mark_completed、mark_failed、retry、wait）
- 输出文件完整性检查

### 场景 5：查看统计报告

定期查看时间追踪统计：

```bash
python3 scripts/task_manager.py stats
```

输出包括：
- 按复杂度等级的时间统计
- 预估准确度
- 按任务类型和模型的统计

## 核心规则

### 复杂度等级

| 等级 | 输入文件 | 预估时间 | 推荐模型 |
|------|---------|----------|---------|
| 1 | 0-1 | 3-8 分钟 | GLM-4.5 |
| 2 | 1-2 | 8-18 分钟 | GLM-4.5 |
| 3 | 2-4 | 15-35 分钟 | GLM-4.7 |
| 4 | 4+ | 30-50 分钟 | GLM-4.7 + 分解 |

### 需要分解的条件

满足以下任一条件时，建议分解任务：
- 复杂度等级 = 4 ✅
- 复杂度等级 = 3 且 输入文件 ≥ 3 ✅
- 复杂度等级 = 3 且 agent = analyst ✅
- 复杂度分数 > 7 ✅

### 模型选择规则

- **GLM-4.5**：复杂度等级 1-2，或 automation 简单任务
- **GLM-4.7**：复杂度等级 3-4，或 analyst 任务（强制）
- **GLM-4.7-Flash**：仅用于主 Orchestrator 协调，子代理永远不要使用

### 超时处理

**阈值**：30 分钟

**四种推荐动作：**
| 动作 | 条件 | 说明 |
|------|------|------|
| mark_completed | 输出存在且完整 | 超时但成功 |
| mark_failed | 输出存在但不完整 | 执行中断 |
| retry | 输出不存在且超时 | 需要重试 |
| wait | 仍在预估范围内 | 继续等待 |

## 参考文档

### 详细指南

- **[COMPLEXITY_FORMULA.md](references/COMPLEXITY_FORMULA.md)** - 复杂度计算公式和示例
- **[MODEL_SELECTION.md](references/MODEL_SELECTION.md)** - 模型选择规则和决策树
- **[DECOMPOSITION_STRATEGIES.md](references/DECOMPOSITION_STRATEGIES.md)** - 三种分解策略详解
- **[TIME_TRACKING.md](references/TIME_TRACKING.md)** - 时间追踪和统计方法

### 何时读取参考文档

- **创建任务时** → 读取 COMPLEXITY_FORMULA.md 理解复杂度计算
- **选择模型时** → 读取 MODEL_SELECTION.md 确认选择规则
- **需要分解时** → 读取 DECOMPOSITION_STRATEGIES.md 选择分解策略
- **分析统计时** → 读取 TIME_TRACKING.md 理解偏差解读

## 使用工作流

### 完整任务生命周期

```
1. 创建任务前分析
   ↓ python3 task_manager.py analyze <task-id>
   ↓
2. 如果复杂度高，查看分解建议
   ↓ python3 task_manager.py decompose <task-id>
   ↓
3. 决定：直接执行 OR 分解
   ↓
4. 执行时记录时间
   ↓ tracker.mark_task_started('task-id')
   ↓ [执行任务]
   ↓ tracker.mark_task_completed('task-id')
   ↓
5. 定期检查超时
   ↓ python3 task_manager.py timeout
   ↓
6. 定期查看统计
   ↓ python3 task_manager.py stats
   ↓
7. 根据统计优化规则
   ↓ 调整复杂度系数和预估时间
   ↓ 返回步骤 1
```

## 预期效果

使用此系统后，预期达到：

- **任务成功率**：88% → 98%（+10%）
- **超时率**：20% → < 5%（-75%）
- **平均执行时间**：4.2 分 → 3.5 分（-17%）
- **自动恢复率**：0% → 30%（+30%）
- **模型选择准确率**：60% → 90%（+50%）

## 注意事项

1. **优先使用脚本工具**
   - 脚本提供了标准化的分析和执行流程
   - 避免重复编写相同代码

2. **遵循渐进式原则**
   - 从简单任务开始，逐步增加复杂度
   - 先验证规则，再调整参数

3. **持续优化**
   - 收集至少 50 个任务的数据
   - 定期查看统计报告
   - 根据实际数据调整公式

4. **记录所有学习**
   - 成功和失败都要记录
   - 分析异常任务的根本原因
   - 更新参考文档

## 独立模块测试

每个脚本都可以独立运行进行测试：

```bash
# 复杂度估算测试
python3 scripts/task_complexity.py

# 时间追踪测试
python3 scripts/time_tracker.py

# 分解建议测试
python3 scripts/task_decomposer.py

# 超时检测测试
python3 scripts/timeout_handler.py
```
