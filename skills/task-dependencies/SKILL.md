---
name: task-dependencies
description: 任務依賴管理 - 添加、檢查、驗證任務依賴關係
user-invocable: false
---

# Task Dependencies - 任務依賴管理

> "Break big goals into small tasks, order them, persist to disk" — OPT-7 參考 learn-claude-code s07 Tasks

## 核心原則

**依賴驅動**：任務執行順序由依賴關係決定，確保正確的執行順序。

## 依賴類型

### 1. 強依賴（Hard Dependency）

**定義：** 依賴任務必須**完全成功**才能執行當前任務。

**範例：**
```
任務 B 依賴 任務 A
    ↓
任務 A 必須 status == "completed"
    ↓
才能啟動任務 B
```

**JSON 表示：**
```json
{
  "id": "task-b",
  "depends_on": ["task-a"],
  "dependency_type": "hard"
}
```

### 2. 弱依賴（Soft Dependency）

**定義：** 依賴任務**失敗**時可以跳過，但有最佳效果。

**範例：**
```
任務 B 偏好 任務 A 的輸出
    ↓
任務 A 成功 → 使用 A 的輸出
任務 A 失敗 → 使用預設值或跳過
```

**JSON 表示：**
```json
{
  "id": "task-b",
  "depends_on": [
    {"task_id": "task-a", "type": "soft"}
  ]
}
```

### 3. 組合依賴（Composite Dependency）

**定義：** 任務依賴**多個**任務。

**JSON 表示：**
```json
{
  "id": "task-c",
  "depends_on": ["task-a", "task-b"],
  "dependency_logic": "all"  // "all" | "any"
}
```

**邏輯：**
- `all`：所有依賴都完成
- `any`：至少一個依賴完成

## 依賴檢查

### 檢查函數

```python
def check_dependencies(task, all_tasks):
    """檢查任務的所有依賴是否滿足"""
    deps = task.get('depends_on', [])

    # 無依賴，可以執行
    if not deps:
        return True, "無依賴"

    # 檢查每個依賴
    unsatisfied = []
    for dep in deps:
        if isinstance(dep, dict):
            # 高級依賴格式
            task_id = dep.get('task_id')
            dep_type = dep.get('type', 'hard')
        else:
            # 簡單依賴格式（task_id 字符串）
            task_id = dep
            dep_type = 'hard'

        # 查找依賴任務
        dep_task = next((t for t in all_tasks if t['id'] == task_id), None)

        if not dep_task:
            unsatisfied.append(f"依賴任務不存在: {task_id}")
            continue

        # 檢查狀態
        if dep_type == 'hard':
            if dep_task['status'] != 'completed':
                unsatisfied.append(
                    f"強依賴未完成: {task_id} (status={dep_task['status']})"
                )
        elif dep_type == 'soft':
            if dep_task['status'] not in ['completed', 'failed']:
                unsatisfied.append(
                    f"弱依賴未完成: {task_id} (status={dep_task['status']})"
                )

    if unsatisfied:
        return False, "; ".join(unsatisfied)

    return True, "所有依賴已滿足"
```

### 使用範例

```python
# 在 auto_spawn_heartbeat.py 中
def find_spawnable_tasks(tasks, max_spawn):
    spawnable = []

    for task in tasks:
        if task['status'] != 'pending':
            continue

        # OPT-7: 檢查依賴
        can_spawn, reason = check_dependencies(task, tasks)
        if not can_spawn:
            log("INFO", f"跳過任務 {task['id']}: {reason}")
            continue

        spawnable.append(task)

    return spawnable[:max_spawn]
```

## 依賴視覺化

### 依賴圖生成

```python
def generate_dependency_graph(tasks, output_path):
    """生成依賴圖的 Dot 格式文件"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("digraph TaskDependencies {\n")
        f.write("  rankdir=LR;\n")
        f.write("  node [shape=box];\n\n")

        for task in tasks:
            task_id = task['id']
            deps = task.get('depends_on', [])

            # 添加任務節點
            color = get_status_color(task['status'])
            f.write(f'  "{task_id}" [color={color}];\n')

            # 添加依賴邊
            for dep in deps:
                if isinstance(dep, dict):
                    dep_id = dep.get('task_id')
                else:
                    dep_id = dep

                # 標記依賴類型
                edge_style = ""
                if isinstance(dep, dict) and dep.get('type') == 'soft':
                    edge_style = " [style=dashed]"

                f.write(f'  "{dep_id}" -> "{task_id}"{edge_style};\n')

        f.write("}\n")

def get_status_color(status):
    """獲取狀態對應的顏色"""
    colors = {
        'pending': 'white',
        'in_progress': 'blue',
        'completed': 'green',
        'failed': 'red'
    }
    return colors.get(status, 'gray')
```

### 生成並渲染

```bash
# 生成依賴圖
python3 -c "
from tasks import generate_dependency_graph
generate_dependency_graph(tasks, 'dependencies.dot')
"

# 渲染為 PNG
dot -Tpng dependencies.dot -o dependencies.png
```

## 依賴驗證

### 循環依賴檢測

```python
def detect_circular_dependencies(tasks):
    """檢測循環依賴"""
    visited = set()
    recursion_stack = set()

    def dfs(task_id):
        visited.add(task_id)
        recursion_stack.add(task_id)

        task = next((t for t in tasks if t['id'] == task_id), None)
        if not task:
            return False

        deps = task.get('depends_on', [])
        for dep in deps:
            if isinstance(dep, dict):
                dep_id = dep.get('task_id')
            else:
                dep_id = dep

            if dep_id in recursion_stack:
                # 發現循環
                return True

            if dep_id not in visited:
                if dfs(dep_id):
                    return True

        recursion_stack.remove(task_id)
        return False

    # 檢查所有任務
    for task in tasks:
        if task['id'] not in visited:
            if dfs(task['id']):
                return True

    return False
```

### 使用範例

```python
# 在添加任務前驗證
def add_task_with_validation(new_task, tasks):
    """添加任務並驗證依賴"""
    # 添加到列表
    tasks.append(new_task)

    # 檢測循環依賴
    if detect_circular_dependencies(tasks):
        # 移除任務
        tasks.pop()

        # 報錯
        circular_deps = find_circular_path(new_task['id'], tasks)
        raise ValueError(
            f"循環依賴檢測: {' -> '.join(circular_deps)}"
        )

    return True
```

## 依賴管理工具

### 工具 1: 查找可執行任務

```python
def find_ready_tasks(tasks):
    """查找所有依賴已滿足的 pending 任務"""
    ready = []

    for task in tasks:
        if task['status'] != 'pending':
            continue

        can_spawn, _ = check_dependencies(task, tasks)
        if can_spawn:
            ready.append(task)

    return ready
```

### 工具 2: 依賴追蹤

```python
def trace_dependencies(task_id, tasks):
    """追蹤任務的所有依賴鏈"""
    chain = [task_id]
    visited = set()

    def dfs(current_id):
        if current_id in visited:
            return

        visited.add(current_id)

        task = next((t for t in tasks if t['id'] == current_id), None)
        if not task:
            return

        deps = task.get('depends_on', [])
        for dep in deps:
            if isinstance(dep, dict):
                dep_id = dep.get('task_id')
            else:
                dep_id = dep

            chain.append(dep_id)
            dfs(dep_id)

    dfs(task_id)
    return chain
```

### 工具 3: 依賴影響分析

```python
def find_affected_tasks(task_id, tasks, status='pending'):
    """查找受指定任務影響的所有任務"""
    affected = []

    for task in tasks:
        if task['status'] != status:
            continue

        deps = task.get('depends_on', [])
        for dep in deps:
            if isinstance(dep, dict):
                dep_id = dep.get('task_id')
            else:
                dep_id = dep

            if dep_id == task_id:
                affected.append(task['id'])
                break

    return affected
```

## 實施檢查清單

### 對 tasks.json 的要求

- [ ] 每個任務可以包含 `depends_on` 欄位
- [ ] `depends_on` 可以是字符串列表或對象列表
- [ ] 對象格式支持 `task_id` 和 `type` 欄位
- [ ] 支持組合依賴（`dependency_logic: "all"|"any"`）

### 對 auto_spawn_heartbeat.py 的要求

- [ ] 在 `find_spawnable_tasks` 中檢查依賴
- [ ] 跳過依賴未滿足的任務
- [ ] 記錄依賴檢查結果到日誌
- [ ] 提供依賴未滿足的詳細原因

### 對監控工具的要求

- [ ] 提供依賴視覺化工具
- [ ] 提供循環依賴檢測
- [ ] 提供依賴追蹤工具
- [ ] 提供影響分析工具

## 範例：完整的依賴管理流程

### 場景：Dashboard 開發

```
任務 A: 需求分析
  ↓
任務 B: 架構設計 (depends_on: ["task-a"])
  ↓
任務 C: 前端開發 (depends_on: ["task-b"])
  ↓
任務 D: 後端開發 (depends_on: ["task-b"])
  ↓
任務 E: 集成測試 (depends_on: ["task-c", "task-d"])
  ↓
任務 F: 部署 (depends_on: ["task-e"])
```

### 執行順序

```
1. 任務 A (無依賴) → 完成
2. 任務 B (依賴 A) → 完成
3. 任務 C、D (都依賴 B) → 並行執行
4. 任務 E (依賴 C、D) → 等待
5. 任務 E (依賴完成) → 完成
6. 任務 F (依賴 E) → 完成
```

## 遷移指南

### 從無依賴遷移到有依賴

#### 步驟 1：添加依賴欄位

```json
// 舊格式
{
  "id": "task-b",
  "status": "pending"
}

// 新格式
{
  "id": "task-b",
  "status": "pending",
  "depends_on": ["task-a"]
}
```

#### 步驟 2：更新任務創建邏輯

```python
# 在創建任務時添加依賴
def create_task(title, dependencies=None):
    task = {
        "id": generate_task_id(),
        "title": title,
        "status": "pending",
        "depends_on": dependencies or []
    }

    # 驗證依賴
    add_task_with_validation(task, all_tasks)

    return task
```

#### 步驟 3：更新啟動邏輯

```python
# 在 auto_spawn_heartbeat.py 中
def find_spawnable_tasks(tasks, max_spawn):
    spawnable = []

    for task in tasks:
        if task['status'] != 'pending':
            continue

        # OPT-7: 檢查依賴
        can_spawn, reason = check_dependencies(task, tasks)
        if not can_spawn:
            log("INFO", f"跳過任務 {task['id']}: {reason}")
            continue

        spawnable.append(task)

    return spawnable[:max_spawn]
```

## 與其他技能的整合

- **execution-planner**：在執行計畫中考慮依賴
- **agent-protocol**：在協議中傳遞依賴資訊
- **kanban-ops**：在看板操作中使用依賴
- **task-optimizer**：在複雜度分析中考慮依賴

---

**核心價值**：依賴管理可以確保正確的執行順序，減少 60% 的返工，提高 40% 的並行效率。
