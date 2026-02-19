# Kanban 系統優化方案研究

> 建立時間：2026-02-20
> 目標：提升任務成功率、降低超時、自動化决策

---

## 🎯 優化目標

| 當前問題 | 目標指標 |
|---------|---------|
| 任務成功率 | 88% → 95%+ |
| 平均執行時間 | 4.2 分鐘 → 穩定在 3-5 分鐘 |
| 超時率 | 20% → <5% |
| 手動干預 | 需要診斷失敗 → 自動重試 |

---

## 🏗️ 整體架構

```
┌─────────────────────────────────────────────────────────┐
│           任務預估與規劃層                               │
│  • 時間預估引擎                                         │
│  • 複雜度評估                                           │
│  • 拆分決策引擎                                         │
└──────────────────┬────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────┐
│           任務配置層                                     │
│  • 模型選擇引擎                                         │
│  • 任務模板匹配                                         │
│  • 參數自動配置                                         │
└──────────────────┬────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────┐
│           執行層                                         │
│  • 並行執行管理器                                       │
│  • 進度監控                                             │
│  • 超時預警                                             │
└──────────────────┬────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────┐
│           驗證與重試層                                   │
│  • 輸出驗證引擎                                         │
│  • 失敗診斷引擎                                         │
│  • 自動重試管理器                                       │
└─────────────────────────────────────────────────────────┘
```

---

## 1. 任務預估機制

### 方案 A：基於歷史數據的預估引擎

**原理：**
- 收集歷史任務執行數據（時間、輸入文件數、輸出長度、任務類型）
- 使用機器學習模型預估新任務的執行時間
- 持續學習和更新模型

**技術棧：**
- 數據存儲：`/Users/charlie/.openclaw/workspace-automation/kanban/task_history.jsonl`
- 預估模型：Linear Regression / Random Forest / XGBoost
- 特徵工程：
  - 輸入文件數量
  - 輸入文件總大小
  - 任務類型（research/analyst/automation/creative）
  - Agent 類型
  - 過去執行時間（同類任務的平均、最大、最小）
  - 輸出複雜度（描述中的「完整 Python 代碼」「詳細報告」等關鍵字）

**實作步驟：**

1. **建立任務歷史數據庫**
   ```python
   # task_history.jsonl 格式
   {
     "task_id": "20260219-130000-t001",
     "task_type": "analyst",
     "agent": "analyst",
     "model": "zai/glm-4.7",
     "input_files": 0,
     "input_total_size": 0,
     "output_length": 15000,  # 字數
     "estimated_time": 5,
     "actual_time": 5.3,
     "status": "completed",
     "created_at": "2026-02-19T13:00:00+08:00",
     "completed_at": "2026-02-19T13:38:00+08:00"
   }
   ```

2. **預估模型訓練**
   ```python
   def train_time_estimator():
       # 讀取歷史數據
       history = pd.read_json('task_history.jsonl', lines=True)

       # 特徵工程
       features = [
           'input_files',
           'input_total_size',
           'task_type_encoded',
           'agent_encoded',
           'output_length_estimate'
       ]

       # 訓練模型
       model = XGBoostRegressor()
       model.fit(history[features], history['actual_time'])

       return model

   def estimate_task_time(task):
       # 提取特徵
       features = extract_task_features(task)

       # 預估時間
       estimated_time = time_estimator.predict(features)

       return estimated_time
   ```

3. **集成到 spawn-protocol**
   ```python
   # SKILL.md 修改
   ## Pre-spawn Checklist (增強版)

   3. **預估任務時間**
      - 調用 `estimate_task_time(task)`
      - 在 tasks.json 中寫入 `estimated_time`
      - 如果預估時間 > 10 分鐘，警告用戶並建議拆分
   ```

**優勢：**
- 準確度高（隨著數據增多而提升）
- 自動學習和改進
- 可預測複雜模式

**挑戰：**
- 需要大量歷史數據
- 模型維護成本
- 冷啟動問題（初期沒有數據）

---

### 方案 B：基於規則的預估引擎

**原理：**
- 使用固定的規則和閾值
- 基於任務特徵（輸入文件數、輸出複雜度、任務類型）查表

**技術棧：**
- 規則配置：`/Users/charlie/.openclaw/workspace-automation/kanban/time_estimation_rules.yaml`

```yaml
# time_estimation_rules.yaml
rules:
  research:
    base_time: 5  # 分鐘
    input_file_penalty: 1  # 每個輸入文件 +1 分鐘
    output_multiplier: 0.0005  # 每1000字 +0.5 分鐘

  analyst:
    base_time: 6
    input_file_penalty: 1.5
    output_multiplier: 0.0008

  automation:
    base_time: 4
    input_file_penalty: 0.5
    output_multiplier: 0.0003

  creative:
    base_time: 8
    input_file_penalty: 2
    output_multiplier: 0.001

output_complexity_keywords:
  - "完整 Python 代碼"  # +3 分鐘
  - "詳細報告"  # +2 分鐘
  - "實證測試"  # +4 分鐘
  - "回測驗證"  # +3 分鐘
```

**實作：**

```python
def estimate_task_time_rules(task):
    # 讀取規則
    rules = load_yaml('time_estimation_rules.yaml')

    # 基礎時間
    base_time = rules[task['type']]['base_time']

    # 輸入文件懲罰
    input_penalty = len(task['input_paths']) * rules[task['type']]['input_file_penalty']

    # 輸出複雜度懲罰
    output_penalty = 0
    for keyword, penalty in rules['output_complexity_keywords'].items():
        if keyword in task.get('notes', ''):
            output_penalty += penalty

    # 總預估
    total = base_time + input_penalty + output_penalty

    return total
```

**優勢：**
- 實作簡單
- 立即可用
- 可解釋性強

**挑戰：**
- 準確度有限
- 需要手動調整規則
- 不適應變化

---

### 推薦方案：混合方案

**階段 1（立即）：方案 B（規則）**
- 快速部署，立即可用
- 收集歷史數據

**階段 2（2-4週後）：方案 A（ML）**
- 使用收集的數據訓練模型
- 逐步替換規則引擎

**實作路徑：**
1. 立即實施規則引擎
2. 每個任務執行完畢後記錄數據
3. 每週訓練新的 ML 模型
4. 當 ML 模型準確度 > 90% 時切換

---

## 2. 自動化任務拆分

### 方案 A：基於預估時間的自動拆分

**觸發條件：**
- 預估時間 > 10 分鐘
- 輸入文件數量 > 3
- 輸出複雜度關鍵字 > 2

**拆分策略：**

1. **輸入文件並行處理**
   ```python
   def split_by_input_files(task):
       # 如果輸入文件獨立，可以並行處理
       if are_inputs_independent(task['input_paths']):
           # 拆分為 N 個子任務
           subtasks = []
           for i, input_path in enumerate(task['input_paths']):
               subtask = {
                   "id": f"{task['id']}-{i}",
                   "title": f"{task['title']} (Part {i+1})",
                   "input_paths": [input_path],
                   "depends_on": []
               }
               subtasks.append(subtask)

           # 創建合併任務
           merge_task = {
               "id": f"{task['id']}-merge",
               "title": f"{task['title']} (Merge)",
               "input_paths": [st['output_path'] for st in subtasks],
               "depends_on": [st['id'] for st in subtasks]
           }

           return subtasks + [merge_task]
   ```

2. **輸出分段生成**
   ```python
   def split_by_output_sections(task):
       # 根據任務描述拆分輸出段落
       sections = parse_output_sections(task['notes'])

       subtasks = []
       for i, section in enumerate(sections):
           subtask = {
               "id": f"{task['id']}-{i}",
               "title": f"{section['title']}",
               "notes": section['description'],
               "depends_on": []
           }
           subtasks.append(subtask)

       return subtasks
   ```

**自動拆分模板庫：**

```python
# task_split_templates.yaml
templates:
  backtest_validation:
    pattern: "回測驗證"
    split_strategy: "sequential"
    subtasks:
      - title: "回測框架設計"
        agent: "analyst"
        estimated_time: 3
      - title: "實證測試執行"
        agent: "automation"
        estimated_time: 5
      - title: "結論與建議"
        agent: "analyst"
        estimated_time: 2

  cost_benefit_analysis:
    pattern: "成本收益分析"
    split_strategy: "parallel"
    subtasks:
      - title: "成本計算"
        agent: "analyst"
        input_files: ["h002-dynamic-hedge-decision.md"]
      - title: "收益評估"
        agent: "analyst"
        input_files: ["h002-dynamic-hedge-decision.md"]
      - title: "優化與建議"
        agent: "analyst"
        input_files: ["cost-calculation.md", "benefit-assessment.md"]
        depends_on: ["成本計算", "收益評估"]
```

**實作流程：**

```python
def auto_split_task(task):
    # 1. 檢查是否需要拆分
    if not should_split(task):
        return [task]

    # 2. 查找匹配的模板
    template = find_split_template(task)

    if template:
        # 3. 使用模板拆分
        return apply_template(task, template)
    else:
        # 4. 基於輸入文件拆分
        return split_by_input_files(task)
```

---

### 方案 B：智能拆分建議（人機協作）

**原理：**
- 系統分析任務，建議拆分方案
- 用戶確認後執行

**實作：**

```python
def suggest_task_split(task):
    # 分析任務
    analysis = {
        "estimated_time": estimate_task_time(task),
        "input_files": len(task['input_paths']),
        "complexity": analyze_complexity(task['notes'])
    }

    # 生成建議
    suggestions = []

    if analysis['estimated_time'] > 10:
        suggestions.append({
            "reason": "預估時間過長",
            "suggestion": "拆分為 3 個子任務",
            "estimated_time_each": 4
        })

    if analysis['input_files'] > 3:
        suggestions.append({
            "reason": "輸入文件過多",
            "suggestion": "並行處理輸入文件",
            "parallel_tasks": analysis['input_files']
        })

    # 發送建議給用戶
    send_split_suggestions(task, suggestions)
```

**用戶確認：**

```yaml
# Telegram 訊息
⚠️ 任務 t004 預估時間：16 分鐘

建議拆分：
1. 回測框架設計（3 分鐘）- analyst
2. 實證測試執行（8 分鐘）- automation
3. 結論與建議（2 分鐘）- analyst

是否執行拆分？
[確認拆分] [保持原樣]
```

---

### 推薦方案：混合方案

**階段 1：自動拆分（簡單場景）**
- 匹配模板庫的任務自動拆分
- 輸入文件並行處理

**階段 2：智能建議（複雜場景）**
- 複雜任務發送建議給用戶
- 用戶確認後執行

---

## 3. 模型選擇自動化

### 方案 A：基於規則的模型選擇引擎

**規則庫：**

```yaml
# model_selection_rules.yaml
rules:
  # 高複雜度分析任務 → GLM-4.7
  - condition:
      task_type: "analyst"
      complexity_keywords: ["實證測試", "回測驗證", "完整分析"]
    model: "zai/glm-4.7"
    reason: "複雜分析需要更強模型"

  # 創意寫作任務 → GLM-4.7
  - condition:
      task_type: "creative"
    model: "zai/glm-4.7"
    reason: "創意寫作需要更強模型"

  # 簡單自動化 → GLM-4.5
  - condition:
      task_type: "automation"
      input_files: "< 2"
    model: "zai/glm-4.5"
    reason: "簡單自動化，GLM-4.5 足夠"

  # 複雜自動化 → GLM-4.7
  - condition:
      task_type: "automation"
      complexity_keywords: ["完整代碼", "實證測試"]
    model: "zai/glm-4.7"
    reason: "複雜自動化需要更強模型"

  # 默認規則
  - condition:
      task_type: "any"
    model: "zai/glm-4.7"
    reason: "默認使用最強模型"
```

**實作：**

```python
def select_model(task):
    rules = load_yaml('model_selection_rules.yaml')

    # 遍歷規則
    for rule in rules:
        if match_condition(task, rule['condition']):
            return rule['model'], rule['reason']

    # 默認
    return "zai/glm-4.7", "默認選擇"

def match_condition(task, condition):
    # 檢查任務類型
    if 'task_type' in condition and task['type'] != condition['task_type']:
        return False

    # 檢查輸入文件數
    if 'input_files' in condition:
        min_files, max_files = parse_range(condition['input_files'])
        if not (min_files <= len(task['input_paths']) <= max_files):
            return False

    # 檢查複雜度關鍵字
    if 'complexity_keywords' in condition:
        if not any(kw in task.get('notes', '') for kw in condition['complexity_keywords']):
            return False

    return True
```

---

### 方案 B：基於歷史成功率的動態調整

**原理：**
- 追蹤每個模型在每種任務類型上的成功率
- 動態調整模型選擇策略

**數據結構：**

```python
# model_performance.json
{
  "zai/glm-4.7": {
    "analyst": {
      "total": 20,
      "success": 19,
      "avg_time": 6.2,
      "success_rate": 0.95
    },
    "automation": {
      "total": 15,
      "success": 12,
      "avg_time": 4.8,
      "success_rate": 0.80
    }
  },
  "zai/glm-4.5": {
    "automation": {
      "total": 25,
      "success": 23,
      "avg_time": 3.5,
      "success_rate": 0.92
    }
  }
}
```

**動態選擇邏輯：**

```python
def select_model_dynamic(task):
    # 獲取可用模型
    available_models = ["zai/glm-4.7", "zai/glm-4.5"]

    # 計算每個模型的得分
    scores = {}
    for model in available_models:
        performance = model_performance.get(model, {}).get(task['type'], {})

        # 成功率權重：0.6
        success_rate = performance.get('success_rate', 0.5)
        score = success_rate * 0.6

        # 速度權重：0.4（時間越短越好）
        avg_time = performance.get('avg_time', 5)
        speed_score = 1 / avg_time
        score += speed_score * 0.4

        scores[model] = score

    # 選擇得分最高的模型
    best_model = max(scores, key=scores.get)

    return best_model, f"成功率 {scores[best_model]:.2f}"
```

---

### 推薦方案：混合方案

**階段 1：規則引擎（基礎）**
- 使用規則庫進行初始選擇
- 覆蓋常見場景

**階段 2：動態調整（優化）**
- 收集歷史數據
- 根據成功率動態調整

**階段 3：ML 預測（進階）**
- 訓練模型預測成功率
- 使用 ML 模型選擇最佳模型

---

## 4. 失敗任務自動重試

### 方案架構

```
┌─────────────────────────────────────────────────┐
│ 任務執行                                         │
└────────────┬────────────────────────────────────┘
             ↓ (失敗)
┌─────────────────────────────────────────────────┐
│ 失敗診斷引擎                                     │
│ • 解析錯誤訊息                                   │
│ • 識別失敗類型                                   │
│ • 生成修復建議                                   │
└────────────┬────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────────┐
│ 修復決策引擎                                     │
│ • 模型切換？                                     │
│ • 任務拆分？                                     │
│ • 參數調整？                                     │
└────────────┬────────────────────────────────────┘
             ↓
┌─────────────────────────────────────────────────┐
│ 自動重試管理器                                   │
│ • 執行修復後的任務                               │
│ • 追蹤重試次數                                   │
│ • 最大重試 3 次                                  │
└─────────────────────────────────────────────────┘
```

### 失敗類型分類

| 失敗類型 | 症狀 | 修復策略 | 成功率 |
|---------|------|---------|--------|
| **Timeout** | 執行超過預估時間 150% | 拆分任務、換更強模型 | 70% |
| **Rate Limit** | 429 錯誤 | 等待後重試、換模型 | 90% |
| **Output Missing** | 輸出文件不存在 | 重試、檢查權限 | 60% |
| **Output Incomplete** | 輸出文件太短（< 1000字） | 重試、增強提示 | 50% |
| **Terminated** | 會話被終止 | 重試、檢查系統 | 80% |

### 實作代碼

```python
class FailureDiagnoser:
    """失敗診斷引擎"""

    FAILURE_PATTERNS = {
        "timeout": ["timeout", "時間過長", "超過"],
        "rate_limit": ["429", "rate limit", "限流"],
        "terminated": ["terminated", "終止"],
        "output_missing": ["no such file", "找不到文件"],
        "output_incomplete": ["輸出異常少", "token 不足"]
    }

    def diagnose(self, task, error_message, execution_time, output_size):
        """診斷失敗原因"""

        # 1. 解析錯誤訊息
        failure_type = self._parse_error_type(error_message)

        # 2. 分析執行數據
        if execution_time > task['estimated_time'] * 1.5:
            failure_type = "timeout"

        if output_size < 1000:  # 輸出太短
            failure_type = "output_incomplete"

        # 3. 生成診斷報告
        diagnosis = {
            "type": failure_type,
            "reason": error_message,
            "suggested_fixes": self._get_suggested_fixes(failure_type, task),
            "success_probability": self._estimate_success_rate(failure_type)
        }

        return diagnosis

    def _parse_error_type(self, error_message):
        """解析錯誤類型"""
        for type_name, patterns in self.FAILURE_PATTERNS.items():
            if any(pattern in error_message.lower() for pattern in patterns):
                return type_name
        return "unknown"

    def _get_suggested_fixes(self, failure_type, task):
        """獲取修復建議"""
        fixes = []

        if failure_type == "timeout":
            fixes.append({
                "action": "split_task",
                "description": "拆分任務為多個子任務",
                "priority": "high"
            })
            fixes.append({
                "action": "change_model",
                "description": "換用更強的模型（GLM-4.7）",
                "priority": "medium"
            })

        elif failure_type == "rate_limit":
            fixes.append({
                "action": "wait_and_retry",
                "description": "等待 5 分鐘後重試",
                "priority": "high"
            })
            fixes.append({
                "action": "change_model",
                "description": "換用 GLM-4.5（並發限制更寬）",
                "priority": "medium"
            })

        return fixes

    def _estimate_success_rate(self, failure_type):
        """估算修復成功率"""
        SUCCESS_RATES = {
            "timeout": 0.70,
            "rate_limit": 0.90,
            "terminated": 0.80,
            "output_missing": 0.60,
            "output_incomplete": 0.50,
            "unknown": 0.40
        }
        return SUCCESS_RATES.get(failure_type, 0.40)


class AutoRetryManager:
    """自動重試管理器"""

    MAX_RETRIES = 3

    def __init__(self, diagnoser):
        self.diagnoser = diagnoser
        self.retry_count = {}
        self.performance_data = load_model_performance()

    def handle_failure(self, task, error_message, execution_time, output_size):
        """處理失敗任務"""

        # 1. 檢查重試次數
        if self.retry_count.get(task['id'], 0) >= self.MAX_RETRIES:
            return {"action": "give_up", "reason": "超過最大重試次數"}

        # 2. 診斷失敗
        diagnosis = self.diagnoser.diagnose(
            task, error_message, execution_time, output_size
        )

        # 3. 選擇最佳修復策略
        best_fix = self._select_best_fix(diagnosis, task)

        # 4. 執行修復
        if best_fix['action'] == "split_task":
            return self._split_and_retry(task)
        elif best_fix['action'] == "change_model":
            return self._change_model_and_retry(task, diagnosis)
        elif best_fix['action'] == "wait_and_retry":
            return self._wait_and_retry(task)
        else:
            return {"action": "retry", "fix": best_fix}

    def _select_best_fix(self, diagnosis, task):
        """選擇最佳修復策略"""
        fixes = diagnosis['suggested_fixes']

        # 根據成功率排序
        best_fix = max(fixes, key=lambda f: f.get('success_rate', 0.5))
        return best_fix

    def _change_model_and_retry(self, task, diagnosis):
        """換模型重試"""
        current_model = task.get('model', 'zai/glm-4.7')

        # 選擇替代模型
        alternative_model = self._select_alternative_model(task)

        # 更新任務
        task['model'] = alternative_model
        task['retry_reason'] = f"{diagnosis['type']}: {diagnosis['reason']}"

        # 記錄重試
        self.retry_count[task['id']] = self.retry_count.get(task['id'], 0) + 1

        return {
            "action": "retry_with_new_model",
            "model": alternative_model,
            "reason": diagnosis['reason']
        }

    def _select_alternative_model(self, task):
        """選擇替代模型"""
        current_model = task.get('model', 'zai/glm-4.7')

        # 根據歷史成功率選擇
        task_type = task['type']

        # 找到成功率最高的模型
        best_model = current_model
        best_rate = 0

        for model in ['zai/glm-4.7', 'zai/glm-4.5']:
            perf = self.performance_data.get(model, {}).get(task_type, {})
            rate = perf.get('success_rate', 0)
            if rate > best_rate and model != current_model:
                best_rate = rate
                best_model = model

        return best_model
```

---

## 5. Stale Check 增強

### 當前問題

現有的 Stale Check 只檢查文件是否存在，不檢查：
- 文件內容是否完整
- 任務執行時間是否合理
- 輸出是否符合預期

### 增強方案

```python
class EnhancedStaleChecker:
    """增強版 Stale Check"""

    def check_task(self, task):
        """檢查任務狀態"""

        # 1. 檢查輸出文件是否存在
        if not self._check_output_exists(task):
            return "missing_output"

        # 2. 檢查執行時間是否合理
        execution_time = self._get_execution_time(task)
        if execution_time > task['estimated_time'] * 1.5:
            return "timeout_risk"

        # 3. 檢查輸出完整性
        if not self._check_output_complete(task):
            return "incomplete_output"

        # 4. 檢查輸出質量
        if not self._check_output_quality(task):
            return "low_quality"

        return "completed"

    def _check_output_exists(self, task):
        """檢查輸出文件是否存在"""
        output_path = task['output_path']
        return os.path.exists(output_path)

    def _check_output_complete(self, task):
        """檢查輸出是否完整"""
        output_path = task['output_path']

        # 讀取文件
        content = read_file(output_path)

        # 檢查長度
        if len(content) < 1000:
            return False

        # 檢查必需的標題
        required_sections = ["摘要", "結論", "實施"]
        for section in required_sections:
            if section not in content:
                return False

        return True

    def _check_output_quality(self, task):
        """檢查輸出質量"""
        output_path = task['output_path']

        # 讀取文件
        content = read_file(output_path)

        # 質量指標
        quality_score = 0

        # 1. 代碼塊數量（技術任務需要代碼）
        if "```" in content:
            quality_score += 2

        # 2. 連結數量（研究任務需要引用）
        if "http" in content:
            quality_score += 1

        # 3. 表格/列表數量
        if "|" in content or "•" in content:
            quality_score += 1

        # 4. 關鍵詞覆蓋（任務描述中的關鍵詞）
        keywords = extract_keywords(task['notes'])
        for kw in keywords:
            if kw in content:
                quality_score += 0.5

        # 閾值判斷
        return quality_score >= 3

    def get_execution_time(self, task):
        """獲取執行時間"""
        created_at = datetime.fromisoformat(task['created_at'])
        updated_at = datetime.fromisoformat(task['updated_at'])
        return (updated_at - created_at).total_seconds() / 60  # 分鐘
```

### 自動修復策略

```python
def auto_recover_stale_task(task, check_result):
    """自動恢復 Stale 任務"""

    if check_result == "missing_output":
        # 輸出文件缺失 → 重試
        return {"action": "retry", "reason": "輸出文件不存在"}

    elif check_result == "timeout_risk":
        # 超時風險 → 檢查子代理狀態
        return check_subagent_status(task)

    elif check_result == "incomplete_output":
        # 輸出不完整 → 重試並增強提示
        task['enhanced_prompt'] = generate_enhanced_prompt(task)
        return {"action": "retry", "reason": "輸出不完整"}

    elif check_result == "low_quality":
        # 低質量 → 標記為失敗，讓用戶決定
        return {"action": "flag_low_quality", "reason": "輸出質量不足"}

    return {"action": "mark_completed"}
```

---

## 6. 建立任務模板庫

### 模板結構

```yaml
# task_templates.yaml
templates:
  research_paper_analysis:
    type: "research"
    agent: "research"
    model: "zai/glm-4.7"
    estimated_time: 8
    sections:
      - "論文背景"
      - "核心貢獻"
      - "技術方法"
      - "實驗結果"
      - "應用價值"
      - "實施建議"

  backtest_validation:
    type: "hybrid"  # analyst + automation
    subtasks:
      - id: "framework"
        title: "回測框架設計"
        agent: "analyst"
        estimated_time: 3
        output_format: "完整 Python 代碼"
      - id: "execution"
        title: "實證測試執行"
        agent: "automation"
        depends_on: ["framework"]
        estimated_time: 5
        output_format: "測試結果數據"
      - id: "analysis"
        title: "結果分析"
        agent: "analyst"
        depends_on: ["execution"]
        estimated_time: 2
        output_format: "詳細報告"

  cost_benefit_analysis:
    type: "parallel"  # 並行執行
    subtasks:
      - id: "cost"
        title: "成本計算"
        agent: "analyst"
        estimated_time: 3
      - id: "benefit"
        title: "收益評估"
        agent: "analyst"
        estimated_time: 3
      - id: "optimization"
        title: "優化與建議"
        agent: "analyst"
        depends_on: ["cost", "benefit"]
        estimated_time: 2
```

### 模板匹配與應用

```python
class TaskTemplateEngine:
    """任務模板引擎"""

    def __init__(self):
        self.templates = load_yaml('task_templates.yaml')

    def find_matching_template(self, task):
        """查找匹配的模板"""

        task_title = task['title'].lower()
        task_notes = task.get('notes', '').lower()

        for template_id, template in self.templates.items():
            # 檢查關鍵字匹配
            template_keywords = template.get('keywords', [])

            if any(kw in task_title for kw in template_keywords):
                return template

            if any(kw in task_notes for kw in template_keywords):
                return template

        return None

    def apply_template(self, task, template):
        """應用模板生成任務"""

        if template.get('type') == "parallel":
            # 並行任務
            return self._generate_parallel_tasks(task, template)
        elif template.get('type') == "hybrid":
            # 混合任務
            return self._generate_hybrid_tasks(task, template)
        else:
            # 單一任務
            return [self._enrich_task_with_template(task, template)]

    def _generate_parallel_tasks(self, task, template):
        """生成並行任務"""

        tasks = []

        # 1. 生成並行子任務
        for subtask_def in template['subtasks']:
            if not subtask_def.get('depends_on'):
                subtask = self._create_subtask(task, subtask_def)
                tasks.append(subtask)

        # 2. 生成合併任務
        merge_subtask_def = template['subtasks'][-1]  # 最後一個是合併任務
        merge_task = self._create_subtask(task, merge_subtask_def)
        tasks.append(merge_task)

        return tasks

    def _create_subtask(self, parent_task, subtask_def):
        """創建子任務"""

        return {
            "id": f"{parent_task['id']}-{subtask_def['id']}",
            "title": f"{parent_task['title']} - {subtask_def['title']}",
            "type": subtask_def['agent'],
            "agent": subtask_def['agent'],
            "model": subtask_def.get('model', self._select_model(subtask_def)),
            "estimated_time": subtask_def['estimated_time'],
            "input_paths": parent_task['input_paths'],
            "depends_on": [
                f"{parent_task['id']}-{dep}"
                for dep in subtask_def.get('depends_on', [])
            ],
            "output_path": f"{parent_task['output_path'].replace('.md', '')}-{subtask_def['id']}.md"
        }
```

---

## 🗺️ 實施路徑

### 第 1 週（立即）

**優先級：P0（最高）**

1. **任務預估機制 - 方案 B（規則）**
   - 實作規則引擎
   - 集成到 spawn-protocol
   - 預期效果：預估準確度 70%

2. **模型選擇自動化 - 方案 A（規則）**
   - 建立規則庫
   - 集成到 spawn-protocol
   - 預期效果：減少模型選擇錯誤 50%

3. **Stale Check 增強**
   - 實作輸出完整性檢查
   - 實作執行時間合理性檢查
   - 預期效果：提早發現 80% 的問題任務

### 第 2-3 週

**優先級：P1（高）**

4. **自動化任務拆分 - 方案 A（自動）**
   - 建立拆分模板庫
   - 實作自動拆分邏輯
   - 預期效果：超時率降低 40%

5. **失敗任務自動重試**
   - 實作失敗診斷引擎
   - 實作自動重試管理器
   - 預期效果：失敗任務自動恢復率 60%

### 第 4-6 週

**優先級：P2（中）**

6. **任務預估機制 - 方案 B（ML）**
   - 收集歷史數據
   - 訓練 ML 模型
   - 預期效果：預估準確度 90%

7. **模型選擇動態調整**
   - 收集成功率數據
   - 實作動態選擇引擎
   - 預期效果：成功率提升 5-10%

### 第 7-8 週

**優先級：P3（低）**

8. **建立任務模板庫**
   - 建立完整模板庫
   - 實作模板匹配引擎
   - 預期效果：提高一致性 30%

9. **智能拆分建議**
   - 實作拆分建議引擎
   - 人機協作拆分
   - 預期效果：提高用戶滿意度

---

## 📊 預期效果

| 指標 | 當前 | 第 1 週後 | 第 4 週後 | 第 8 週後 |
|------|------|----------|----------|----------|
| 任務成功率 | 88% | 92% | 95% | 98% |
| 超時率 | 20% | 12% | 6% | 3% |
| 平均執行時間 | 4.2 分鐘 | 4.0 分鐘 | 3.8 分鐘 | 3.5 分鐘 |
| 手動干預 | 高 | 中 | 低 | 極低 |
| 自動恢復率 | 0% | 30% | 50% | 70% |

---

## 🎯 成功指標

### 第 1 週（基準）
- ✅ 任務預估準確度 > 70%
- ✅ 模型選擇正確率 > 90%
- ✅ Stale Check 發現問題率 > 80%

### 第 4 週（改進）
- ✅ 任務成功率 > 95%
- ✅ 超時率 < 10%
- ✅ 自動恢復率 > 50%

### 第 8 週（優化）
- ✅ 任務成功率 > 98%
- ✅ 超時率 < 5%
- ✅ 自動恢復率 > 70%

---

**下一步：** 從第 1 週的 P0 任務開始實施。
