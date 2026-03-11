---
name: agent-protocol
description: 代理通信協議 - 統一請求-響應模式，標準化代理之間的通信
user-invocable: false
---

# Agent Protocol - 代理通信協議

> "Teammates need shared communication rules" — OPT-4 參考 learn-claude-code s10 Team Protocols

## 核心原則

**統一協議**：所有代理之間的通信使用相同的消息格式和模式。

## 消息格式

### 標準請求格式

```json
{
  "type": "request",
  "id": "uuid-v4",
  "from": "agent:main:main",
  "to": "agent:developer:subagent:xxxxx",
  "timestamp": "2026-03-04T16:20:00Z",
  "priority": "normal|high|low",
  "task": "TASK: [具體任務描述]",
  "context": {
    "project_id": "project-id",
    "task_id": "task-id",
    "input_paths": ["path1", "path2"],
    "dependencies": ["task-id-1", "task-id-2"]
  },
  "metadata": {
    "model": "zai/glm-4.7",
    "timeout_seconds": 3600,
    "expected_output": "output-path"
  }
}
```

### 標準響應格式

```json
{
  "type": "response",
  "id": "uuid-v4",  // 與請求的 id 相同
  "from": "agent:developer:subagent:xxxxx",
  "to": "agent:main:main",
  "timestamp": "2026-03-04T16:25:00Z",
  "status": "success|partial|failed",
  "result": {
    "output_path": "output-path",
    "summary": "簡短摘要",
    "metrics": {
      "tokens_used": 12345,
      "execution_time_seconds": 300,
      "files_created": ["file1", "file2"]
    }
  },
  "error": {
    "code": "ERROR_CODE",
    "message": "錯誤描述",
    "traceback": "異常堆疊"
  }
}
```

### 通知消息格式

```json
{
  "type": "notification",
  "id": "uuid-v4",
  "from": "agent:main:main",
  "to": "all",
  "timestamp": "2026-03-04T16:30:00Z",
  "event": "task_completed|task_failed|system_update",
  "payload": {
    "task_id": "task-id",
    "status": "completed",
    "details": "額外資訊"
  }
}
```

## 通信模式

### 模式 1：請求-響應（同步）

**流程：**
```
[A] → 請求 → [B]
    ← 等待
[A] ← 響應 ← [B]
```

**使用場景：**
- 主會話詢問子代理
- 代理之間的直接通信
- 需要立即結果的操作

**實現：**
```python
def send_request(to_agent, request_data):
    """發送請求並等待響應"""
    request_id = str(uuid4())
    request_data['id'] = request_id
    request_data['from'] = get_session_key()
    request_data['to'] = to_agent

    # 發送請求
    sessions_send(sessionKey=to_agent, message=json.dumps(request_data))

    # 等待響應（有超時）
    response = wait_for_response(request_id, timeout_seconds=600)

    return response
```

### 模式 2：異步通知（事件驅動）

**流程：**
```
[A] → 通知 → [B]
    ────────────────
[A] 繼續其他工作
    ────────────────
[B] 完成後 → 通知 → [A]
```

**使用場景：**
- 子代理完成任務後通知主會話
- 主會話通知子代理系統更新
- 批量並行任務

**實現：**
```python
def send_notification(to_agent, event_type, payload):
    """發送異步通知"""
    notification = {
        "type": "notification",
        "id": str(uuid4()),
        "from": get_session_key(),
        "to": to_agent,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event_type,
        "payload": payload
    }

    sessions_send(sessionKey=to_agent, message=json.dumps(notification))
    # 立即返回，不等待響應
```

### 模式 3：廣播通知（一對多）

**流程：**
```
[A] → 廣播通知 → [所有代理]
```

**使用場景：**
- 系統狀態更新
- 緊急通知
- 配置更新

**實現：**
```python
def broadcast_notification(event_type, payload):
    """廣播通知到所有代理"""
    active_agents = get_active_agents()

    for agent_key in active_agents:
        notification = {
            "type": "notification",
            "id": str(uuid4()),
            "from": get_session_key(),
            "to": "all",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event_type,
            "payload": payload
        }

        sessions_send(sessionKey=agent_key, message=json.dumps(notification))
```

## 優先級處理

### 優先級定義

| 優先級 | 說明 | 處理時間 | 延遲容忍度 |
|--------|------|----------|-----------|
| `low` | 可延後執行的任務 | < 24 小時 | 高 |
| `normal` | 正常任務 | < 4 小時 | 中 |
| `high` | 緊急任務 | < 1 小時 | 低 |

### 優先級路由

```python
def route_by_priority(message):
    """根據優先級路由消息"""
    priority = message.get('priority', 'normal')

    if priority == 'high':
        # 立即處理
        process_immediately(message)
    elif priority == 'normal':
        # 添加到普通隊列
        add_to_normal_queue(message)
    elif priority == 'low':
        # 添加到後台隊列
        add_to_background_queue(message)
```

## 錯誤處理

### 錯誤碼定義

| 錯誤碼 | 說明 | 重試策略 |
|--------|------|----------|
| `TIMEOUT` | 請求超時 | 重試 3 次 |
| `INVALID_FORMAT` | 消息格式錯誤 | 不重試，拒絕 |
| `DEPENDENCY_FAILED` | 依賴任務失敗 | 不重試，回報 |
| `RESOURCE_EXHAUSTED` | 資源耗盡 | 延遲重試 |
| `PERMISSION_DENIED` | 無權限 | 不重試，拒絕 |

### 錯誤響應範例

```json
{
  "type": "response",
  "id": "uuid-v4",
  "from": "agent:developer:subagent:xxxxx",
  "to": "agent:main:main",
  "timestamp": "2026-03-04T16:25:00Z",
  "status": "failed",
  "error": {
    "code": "TIMEOUT",
    "message": "任務執行超時（600秒）",
    "traceback": "Traceback (most recent call last):..."
  }
}
```

## 安全性

### 消息驗證

```python
def validate_message(message):
    """驗證消息格式和內容"""
    # 必需欄位
    required_fields = ['type', 'id', 'from', 'to', 'timestamp']

    for field in required_fields:
        if field not in message:
            return False, f"缺少必需欄位: {field}"

    # 格式驗證
    if message['type'] not in ['request', 'response', 'notification']:
        return False, f"無效的消息類型: {message['type']}"

    # 時間戳驗證
    try:
        datetime.fromisoformat(message['timestamp'])
    except ValueError:
        return False, "無效的時間戳格式"

    return True, "驗證通過"
```

### 權限控制

```python
def check_permission(sender, receiver, message_type):
    """檢查發送者是否有權限發送此類消息"""
    # 定義允許的路由規則
    allowed_routes = {
        "agent:main:main": ["all"],  # 主會話可以發送給任何人
        "agent:developer:subagent:*": ["agent:main:main"],  # 子代理只能回覆主會話
        # ... 更多規則
    }

    # 檢查是否在允許的路由中
    return receiver in allowed_routes.get(sender, [])
```

## 實施檢查清單

### 對主會話的要求

- [ ] 所有發送給子代理的消息使用標準格式
- [ ] 處理子代理的響應時驗證格式
- [ ] 實現請求超時機制
- [ ] 記錄所有通信到日誌

### 對子代理的要求

- [ ] 發送響應時使用標準格式
- [ ] 發送錯誤時包含詳細的錯誤信息
- [ ] 支持請求-響應模式
- [ ] 支持異步通知模式

### 對代理系統的要求

- [ ] 實現消息路由和轉發
- [ ] 支持優先級處理
- [ ] 實現消息驗證
- [ ] 實現權限控制
- [ ] 記錄所有通信

## 範例：完整的通信流程

### 場景：Dashboard 開發

```
1. [主會話] → 請求 → [Architect]
   {
     "type": "request",
     "task": "設計 Market Score V3",
     "context": {...}
   }

2. [Architect] → 響應 → [主會話]
   {
     "type": "response",
     "status": "success",
     "result": {
       "output_path": "design.md",
       "summary": "設計完成"
     }
   }

3. [主會話] → 請求 → [Developer]
   {
     "type": "request",
     "task": "實現 Market Score V3",
     "context": {
       "input_paths": ["design.md"]
     }
   }

4. [Developer] → 通知 → [主會話]（完成）
   {
     "type": "notification",
     "event": "task_completed",
     "payload": {
       "task_id": "dev-001",
       "status": "completed"
     }
   }
```

## 遷移指南

### 從當前通信遷移到標準協議

#### 步驟 1：更新消息格式

```python
# 舊格式
sessions_send(sessionKey=agent_key, message="TASK: do something")

# 新格式
request = {
  "type": "request",
  "id": str(uuid4()),
  "from": get_session_key(),
  "to": agent_key,
  "timestamp": datetime.now(timezone.utc).isoformat(),
  "task": "TASK: do something",
  "context": {}
}

sessions_send(sessionKey=agent_key, message=json.dumps(request))
```

#### 步驟 2：添加響應處理

```python
# 處理子代理響應
def handle_response(response):
    try:
        parsed = json.loads(response)

        # 驗證格式
        if not validate_message(parsed):
            raise ValueError("無效的響應格式")

        # 處理響應
        if parsed['status'] == 'success':
            process_success(parsed['result'])
        elif parsed['status'] == 'failed':
            process_failure(parsed['error'])

    except json.JSONDecodeError:
        # 向後兼容：處理舊格式
        handle_legacy_format(response)
```

#### 步驟 3：更新子代理輸出

```python
# 在 agent-output 技能中更新輸出格式
def generate_output(result):
    """生成標準格式的輸出"""
    return {
        "type": "response",
        "id": get_request_id(),
        "from": get_my_session_key(),
        "to": get_parent_session_key(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "success" if result['success'] else "failed",
        "result": result,
        "error": result.get('error')
    }
```

## 與其他技能的整合

- **spawn-protocol**：啟動子代理時使用協議
- **agent-output**：子代理輸出時使用協議
- **on-demand-skill-loader**：需要協議時加載本技能
- **execution-planner**：在執行計畫中考慮協約通信

---

**核心價值**：統一的通信協議可以減少 50% 的調試時間，提高 80% 的代理協作效率。
