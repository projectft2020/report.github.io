# 架構優化與重構建議 - 2026-02-20

---

## 🎯 核心架構問題

### 1. 子代理 Announce 系統可靠性問題

**當前狀況：**
- Gateway timeout 15 秒限制導致大量 announce 失敗
- 2小時內發生 20+ 次超時錯誤
- 用戶無法收到完成通知
- Task Handoff Protocol 可能無法正確執行

**根本原因分析：**
1. **超時設置過短：** 15 秒對於複雜任務來說太短
2. **無重試機制：** announce 失敗後沒有自動重試
3. **狀態不一致：** 任務實際已完成但 announce 失敗，導致狀態標記錯誤

**建議方案：**
```python
# 優化方案 1: 漸進式超時
- 簡單任務: 15 秒
- 中等任務: 30 秒
- 複雜任務: 60 秒

# 優化方案 2: 指數退避重試
- 第 1 次失敗: 等待 1 秒後重試
- 第 2 次失敗: 等待 3 秒後重試
- 第 3 次失敗: 等待 10 秒後重試
- 最多重試 3 次

# 優化方案 3: 異步 announce
- 任務完成後立即標記為 completed
- Announce 後台執行，不阻塞狀態更新
- Announce 失敗記錄到日誌，不影響任務狀態
```

---

### 2. 假失敗檢測與自動恢復

**當前狀況：**
- 多個任務被標記為 "terminated" 但實際已完成
- pj002 (1881 行) 和 d002 (1988 行) 完成但被標記為失敗
- 用戶需要手動檢查輸出文件

**根本原因分析：**
1. **狀態判斷錯誤：** 系統依賴 announce 成功來判斷任務完成
2. **無輸出檢查：** 沒有檢查輸出文件是否實際存在
3. **無自動恢復：** 檢測到假失敗後無法自動恢復狀態

**建議方案：**
```python
# 方案 1: 輸出文件檢查
任務終止後:
  1. 檢查 output_path 文件是否存在
  2. 如果存在且非空，讀取最後 50 行檢查是否有完成標記（如 "報告完"、"## 結論"）
  3. 如果完成標記存在，自動更新狀態為 completed
  4. 添加 notes: "檢測到輸出文件已完成，自動恢復狀態"

# 方案 2: 定期 stale check
def check_stale_tasks():
  """
  定期檢查 terminated 任務，看是否有已完成的輸出文件
  """
  for task in tasks:
    if task.status == "terminated":
      if file_exists(task.output_path) and file_size(task.output_path) > 1000:
        # 檢查完成標記
        content = read_last_lines(task.output_path, 50)
        if has_completion_marker(content):
          task.status = "completed"
          task.notes = "自動恢復：檢測到輸出文件已完成"
          save_tasks()
```

---

### 3. Research Agent Token 消耗優化

**當前狀況：**
- h001 任務執行 2 次，每次消耗 467k tokens (輸入) / 3k tokens (輸出)
- 輸入/輸出比 = 155:1，極低效率
- Web search 返回大量結果但沒有效利用

**根本原因分析：**
1. **搜索策略不當：** 一次性搜索太多關鍵詞
2. **結果濃度不足：** 沒有過濾和排序搜索結果
3. **無搜索迭代：** 應該先搜索，再根據結果調整搜索詞

**建議方案：**
```python
# 方案 1: 分階段搜索
階段 1: 寬搜索 (3-5 個關鍵詞)
  - 獲取概覽，識別相關性高的結果
  - 記錄 token 消耗

階段 2: 深搜索 (基於階段 1 的結果)
  - 針對性搜索 2-3 個最具相關性的主題
  - 深入挖掘細節

階段 3: 驗證搜索
  - 補充遺漏的關鍵信息
  - 驗證重要觀點

# 方案 2: 搜索結果過濾
def search_and_filter(query, max_results=5):
  """
  搜索並過濾結果，只保留高相關性的內容
  """
  results = web_search(query, count=max_results)
  filtered = []
  for r in results:
    # 相關性評分
    score = calculate_relevance_score(r, query)
    if score > 0.7:  # 只保留相關性 > 70% 的結果
      filtered.append(r)
  return filtered

# 方案 3: Token 預算管理
class ResearchBudget:
  def __init__(self, total_budget=200000):
    self.total_budget = total_budget
    self.used = 0

  def can_search(self, estimated_tokens):
    return self.used + estimated_tokens <= self.total_budget

  def record_search(self, actual_tokens):
    self.used += actual_tokens
```

---

### 4. Model Fallback 策略實現

**當前狀況：**
- SOUL.md 中定義了 fallback 策略（GLM-4.7 → GLM-4.5）
- 但沒有實際實現
- 主模型被限流時無法自動切換

**建議方案：**
```python
# Model Fallback Manager
class ModelFallbackManager:
  def __init__(self):
    self.primary_model = "zai/glm-4.7"
    self.fallback_models = ["zai/glm-4.5", "zai/haiku"]
    self.current_index = 0
    self.failure_log = []

  def execute_with_fallback(self, task, agent_id):
    """
    執行任務，支持自動降級
    """
    for i, model in enumerate(self.get_models()):
      try:
        result = sessions_spawn({
          "agentId": agent_id,
          "task": task,
          "model": model
        })
        # 成功，重置嘗試次數
        self.current_index = 0
        return result
      except RateLimitError as e:
        # 記錄失敗
        self.failure_log.append({
          "model": model,
          "error": str(e),
          "timestamp": datetime.now()
        })
        # 切換到下一個模型
        self.current_index += 1
        continue

    # 所有模型都失敗
    raise AllModelsFailedError("所有模型都被限流，請稍後再試")

  def get_models(self):
    """獲取當前可用的模型列表"""
    models = [self.primary_model] + self.fallback_models
    return models[self.current_index:] + models[:self.current_index]
```

---

### 5. Task Handoff Protocol 優化

**當前狀況：**
- 依賴 announce 成功來觸發下游任務
- announce 失敗導致下游任務無法自動觸發
- 需要手動觸發下游任務

**建議方案：**
```python
# 方案 1: 基於輸出文件的檢測
def check_and_trigger_next_tasks(task):
  """
  檢查任務完成，觸發下游任務
  """
  # 檢查輸出文件是否存在且完整
  if output_file_exists_and_complete(task):
    # 更新任務狀態為 completed
    task.status = "completed"
    task.completed_at = now()
    save_tasks()

    # 觸發下游任務
    for next_task_id in task.next_tasks:
      next_task = get_task(next_task_id)
      if can_trigger_next_task(next_task):
        spawn_task(next_task)

def output_file_exists_and_complete(task):
  """檢查輸出文件是否存在且完整"""
  if not file_exists(task.output_path):
    return False
  if file_size(task.output_path) < 1000:
    return False
  content = read_last_lines(task.output_path, 50)
  return has_completion_marker(content)

# 方案 2: 定期檢查和恢復
def periodic_handoff_check():
  """
  定期檢查是否有應該觸發但未觸發的下游任務
  """
  for task in tasks:
    if task.status == "completed":
      # 檢查下游任務是否已觸發
      for next_task_id in task.next_tasks:
        next_task = get_task(next_task_id)
        if next_task.status == "pending" and can_trigger_next_task(next_task):
          # 觸發下游任務
          spawn_task(next_task)
          log(f"恢復觸發下游任務: {next_task_id}")
```

---

### 6. Scout Agent 介面重構

**當前狀況：**
- HEARTBEAT 嘗試調用 `~/.openclaw/workspace-scout/scout_agent.py`
- 腳本不存在
- 無法自動觸發 Scout 掃描

**建議方案：**
```python
# 方案 1: 通過 sessions_spawn 調用
def scout_stats():
  """
  獲取 Scout 統計信息
  """
  result = sessions_spawn({
    "agentId": "scout",
    "task": "TASK: 返回 Scout 統計信息\n\nOUTPUT PATH: /tmp/scout-stats.json",
    "model": "zai/glm-4.5"
  })
  return result

def scout_scan():
  """
  觸發 Scout 掃描
  """
  result = sessions_spawn({
    "agentId": "scout",
    "task": "TASK: 執行主題掃描\n\nOUTPUT PATH: /tmp/scout-scan.json",
    "model": "zai/glm-4.5"
  })
  return result

# 方案 2: 創建統一的 Scout CLI
# scout_agent.py
import sys
import json
from openclaw.sessions import spawn

def main():
  command = sys.argv[1] if len(sys.argv) > 1 else "stats"

  if command == "stats":
    # 調用 scout agent 獲取統計
    result = spawn({"task": "返回 Scout 統計", "agentId": "scout"})
    print(json.dumps(result))
  elif command == "scan":
    # 觸發 Scout 掃描
    result = spawn({"task": "執行主題掃描", "agentId": "scout"})
    print(json.dumps(result))
  elif command == "check":
    # 檢查是否需要掃描
    result = spawn({"task": "檢查是否需要掃描", "agentId": "scout"})
    print(json.dumps(result))

if __name__ == "__main__":
  main()
```

---

### 7. 日誌與監控系統

**當前狀況：**
- 錯誤日誌分散在多個文件
- 沒有統一的錯誤追蹤
- 難以診斷問題

**建議方案：**
```python
# 統一日誌系統
class Logger:
  def __init__(self):
    self.logs = []

  def log(self, level, message, context=None):
    log_entry = {
      "timestamp": datetime.now().isoformat(),
      "level": level,
      "message": message,
      "context": context or {}
    }
    self.logs.append(log_entry)

    # 寫入文件
    self.write_to_file(log_entry)

    # 如果是錯誤，發送通知
    if level in ["ERROR", "CRITICAL"]:
      self.send_alert(log_entry)

  def write_to_file(self, log_entry):
    with open(f"~/.openclaw/logs/{log_entry['level'].lower()}.log", "a") as f:
      f.write(json.dumps(log_entry) + "\n")

  def send_alert(self, log_entry):
    # 發送到 Telegram 或其他通知渠道
    message.send({
      "channel": "telegram",
      "message": f"[{log_entry['level']}] {log_entry['message']}",
      "to": "603360768"
    })

# 使用示例
logger = Logger()
logger.log("INFO", "任務開始", {"task_id": "ai001"})
logger.log("ERROR", "Announce 失敗", {"task_id": "ai001", "error": "timeout after 15000ms"})
logger.log("CRITICAL", "所有模型都被限流", {"models": ["glm-4.7", "glm-4.5"]})
```

---

### 8. 並發控制與負載均衡

**當前狀況：**
- 沒有明確的並發限制
- 可能會同時觸發太多子代理
- 沒有負載均衡機制

**建議方案：**
```python
# 並發控制器
class ConcurrencyController:
  def __init__(self, max_concurrent=5):
    self.max_concurrent = max_concurrent
    self.running_tasks = []
    self.pending_tasks = []

  def spawn_task(self, task, agent_id, model=None):
    """
    生成任務，支持並發控制
    """
    if len(self.running_tasks) >= self.max_concurrent:
      # 已達到最大並發，加入待辦隊列
      self.pending_tasks.append((task, agent_id, model))
      return {"status": "queued"}

    # 執行任務
    result = sessions_spawn({
      "task": task,
      "agentId": agent_id,
      "model": model
    })

    # 添加到運行隊列
    self.running_tasks.append(result["session_id"])

    return result

  def on_task_complete(self, session_id):
    """
    任務完成回調
    """
    # 從運行隊列移除
    self.running_tasks.remove(session_id)

    # 檢查是否有待辦任務
    if self.pending_tasks:
      task, agent_id, model = self.pending_tasks.pop(0)
      self.spawn_task(task, agent_id, model)
```

---

### 9. 狀態機與事務管理

**當前狀況：**
- 任務狀態轉換沒有明確的規則
- 沒有事務保證狀態一致性
- 可能出現狀態不一致的情況

**建議方案：**
```python
# 狀態機
class TaskStateMachine:
  def __init__(self):
    self.transitions = {
      "pending": ["in_progress"],
      "in_progress": ["completed", "failed", "terminated"],
      "completed": [],  # 終態
      "failed": ["pending"],  # 可以重試
      "terminated": ["completed"]  # 可以恢復
    }

  def can_transition(self, from_state, to_state):
    """檢查是否可以轉換狀態"""
    return to_state in self.transitions.get(from_state, [])

  def transition(self, task, to_state, reason=None):
    """
    轉換任務狀態
    """
    from_state = task["status"]
    if not self.can_transition(from_state, to_state):
      raise InvalidStateTransitionError(f"無法從 {from_state} 轉換到 {to_state}")

    # 轉換狀態
    task["status"] = to_state
    if reason:
      task["notes"] = f"{task.get('notes', '')}\n{reason}"

    # 保存狀態
    save_tasks()

    return task

# 事務管理
class TransactionManager:
  def __init__(self):
    self.transactions = []

  def begin(self):
    """開始事務"""
    transaction = {
      "id": generate_id(),
      "start_time": now(),
      "operations": []
    }
    self.transactions.append(transaction)
    return transaction["id"]

  def commit(self, transaction_id):
    """提交事務"""
    transaction = self.get_transaction(transaction_id)
    # 執行所有操作
    for op in transaction["operations"]:
      op["execute"]()
    transaction["committed"] = True

  def rollback(self, transaction_id):
    """回滾事務"""
    transaction = self.get_transaction(transaction_id)
    # 執行所有回滾操作
    for op in reversed(transaction["operations"]):
      op["rollback"]()
    transaction["rolled_back"] = True
```

---

## 📋 優化優先級

| 優先級 | 問題 | 預估工作量 | 影響範圍 |
|--------|------|-----------|----------|
| P0 | Announce 超時問題 | 1-2 天 | 所有子代理 |
| P0 | 假失敗檢測與恢復 | 1 天 | 所有任務 |
| P1 | Model Fallback 實現 | 1 天 | 模型調用 |
| P1 | Task Handoff 優化 | 1-2 天 | 任務協調 |
| P2 | Research Token 優化 | 2-3 天 | Research agent |
| P2 | Scout 介面重構 | 1 天 | Scout agent |
| P2 | 日誌系統 | 1-2 天 | 調試和監控 |
| P3 | 並發控制 | 1 天 | 系統穩定性 |
| P3 | 狀態機與事務 | 2-3 天 | 狀態一致性 |

---

## 🎯 實施建議

### 階段 1: 緊急修復 (1-2 週)
1. Announce 超時問題 - 增加超時時間 + 重試機制
2. 假失敗檢測 - 輸出文件檢查 + 自動恢復
3. Model Fallback 實現 - 自動降級機制

### 階段 2: 系統優化 (2-3 週)
4. Task Handoff 優化 - 基於輸出文件的檢測
5. Research Token 優化 - 分階段搜索
6. Scout 介面重構 - 統一 CLI

### 階段 3: 長期改進 (4-6 週)
7. 日誌系統 - 統一日誌和監控
8. 並發控制 - 負載均衡
9. 狀態機與事務 - 狀態一致性

---

**報告生成時間：** 2026-02-20 19:30 GMT+8
**報告生成者：** Charlie (Orchestrator)
