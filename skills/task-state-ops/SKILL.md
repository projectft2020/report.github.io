# Task State Operations - 任務狀態操作

任務狀態管理的標準化技能，提供一致的識別、更新、回滾和分析流程。

## 核心原則

**1. 狀態機優先**
- 任務狀態必須遵循嚴格的狀態機規則
- 任何狀態轉換都必須符合定義的轉換路徑
- 禁止跳躍式狀態轉換（如 pending → failed）

**2. 事務性更新**
- 狀態更新必須是原子的（成功或失敗，不能部分更新）
- 更新失敗時必須有回滾機制
- 禁止直接手動修改 tasks.json（除非緊急情況）

**3. 時間戳追蹤**
- 每次狀態轉換必須記錄 `updated_at` 時間戳
- 特定狀態需要額外時間戳：
  - spawning → 記錄 `spawned_at`
  - in_progress → 記錄 `started_at`
  - completed/failed → 記錄 `completed_at`

**4. 超時保護**
- 每個狀態都有明確的超時閾值
- 超時後必須自動回滾到安全狀態
- 超時閾值基於任務類型和優先級動態調整

**5. 幂等性保證**
- 狀態更新操作必須是冪等的
- 重複執行相同操作不會產生副作用
- 狀態檢查和更新之間不應有競態條件

---

## 任務狀態機

### 狀態定義

| 狀態 | 說明 | 生命週期 | 典型持續時間 |
|------|------|---------|-------------|
| **pending** | 待處理，等待啟動 | 初始狀態 | 無限期 |
| **spawning** | 正在啟動子代理 | 過渡狀態 | 1-120 分鐘 |
| **in_progress** | 執行中 | 活躍狀態 | 60-180 分鐘（研究類） |
| **completed** | 成功完成 | 終態 | 永久 |
| **failed** | 失敗 | 終態 | 永久 |
| **done** | 手動標記完成（用戶確認） | 終態 | 永久 |

### 狀態轉換圖

```
                    ┌─────────────────┐
                    │     pending     │ ◄───┐
                    └────────┬────────┘      │
                             │             │
                    spawn()  │             │  user_confirm()
                             ▼             │
                    ┌─────────────────┐      │
                    │    spawning     │      │
                    └────────┬────────┘      │
                             │             │
              timeout_2h     │             │
                (fallback)   │             │
                    ┌────────┴────────┐     │
                    ▼                 ▼     │
              rollback()       success() │
                    │                 │     │
                    ▼                 ▼     │
              ┌─────────┐       ┌──────────┐│
              │ pending │       │completed ││
              └─────────┘       └──────────┘│
                                        │
                                        │  (optional)
                                        ▼
                                  ┌──────────┐
                                  │   done   │
                                  └──────────┘

                    ┌─────────────────┐
                    │   in_progress   │
                    └────────┬────────┘
                             │
                    timeout_24h │
                    fail()      ▼
                             ┌──────────┐
                             │  failed  │
                             └──────────┘
```

### 合法的狀態轉換

| 從 | 到 | 觸發條件 | 函數 |
|----|----|---------|------|
| pending | spawning | 有可用並發位置 | `spawn_task()` |
| spawning | pending | 超時（120 分鐘）或啟動失敗 | `rollback_task()` |
| spawning | in_progress | 子代理成功啟動並輸出 .status | `sync_task_status()` |
| spawning | failed | 啟動失敗且無法重試 | `mark_task_failed()` |
| in_progress | completed | 任務成功完成 | `complete_task()` |
| in_progress | failed | 任務執行失敗或超時（24 小時） | `mark_task_failed()` |
| completed | done | 用戶手動確認 | `user_confirm()` |

### 非法轉換（必須避免）

| 從 | 到 | 原因 |
|----|----|------|
| pending | completed | 未執行直接完成 |
| pending | failed | 未執行直接失敗 |
| spawning | completed | 跳過執行階段 |
| in_progress | pending | 執行中無法回到待辦 |
| completed | pending | 已完成無法回到待辦 |
| failed | in_progress | 失敗後無法恢復執行 |

---

## 標準操作流程

### 1. 辨識（Identify）- 識別任務狀態異常

**目標：** 發現需要狀態更新或回滾的任務

**檢查項目：**

```python
def identify_abnormal_tasks(tasks):
    """識別異常任務"""
    abnormal = {
        'stuck_spawnings': [],    # 卡住的 spawning 任務
        'timeout_in_progress': [], # 超時的 in_progress 任務
        'orphan_completed': [],    # 孤兒任務（輸出文件存在但狀態未更新）
        'duplicate_spawn': [],     # 重複啟動的任務
    }

    now = datetime.now(timezone.utc)

    for task in tasks:
        status = task.get('status')
        task_id = task['id']

        # 檢查卡住的 spawning 任務
        if status == 'spawning':
            updated_at = task.get('updated_at', task.get('spawned_at'))
            if updated_at:
                elapsed = now - datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                if elapsed > timedelta(minutes=120):
                    abnormal['stuck_spawnings'].append(task)

        # 檢查超時的 in_progress 任務
        if status == 'in_progress':
            started_at = task.get('started_at', task.get('updated_at'))
            if started_at:
                elapsed = now - datetime.fromisoformat(started_at.replace('Z', '+00:00'))
                if elapsed > timedelta(hours=24):
                    abnormal['timeout_in_progress'].append(task)

        # 檢查孤兒任務（輸出文件存在但狀態未更新）
        output_path = get_task_output_path(task)
        if output_path and output_path.exists() and status in ['spawning', 'in_progress']:
            abnormal['orphan_completed'].append(task)

    return abnormal
```

**最佳實踐：**
- 每次心跳都執行識別檢查
- 使用時間戳區分真正的卡住和正常執行中
- 考慮不同任務類型的不同超時閾值

---

### 2. 更新（Update）- 更新任務狀態

**目標：** 將任務狀態更新為正確的狀態

**更新流程：**

```python
def update_task_status_safely(task_id, new_status, reason=""):
    """安全更新任務狀態"""
    tasks = load_tasks()

    # 檢查任務是否存在
    task = find_task_by_id(tasks, task_id)
    if not task:
        logger.error(f"任務不存在: {task_id}")
        return False

    old_status = task.get('status')

    # 檢查狀態轉換是否合法
    if not is_valid_transition(old_status, new_status):
        logger.error(f"非法狀態轉換: {old_status} → {new_status}")
        return False

    # 記錄轉換原因
    if reason:
        task.setdefault('status_history', []).append({
            'from': old_status,
            'to': new_status,
            'at': datetime.now(timezone.utc).isoformat(),
            'reason': reason
        })

    # 更新狀態和時間戳
    task['status'] = new_status
    task['updated_at'] = datetime.now(timezone.utc).isoformat()

    # 添加額外時間戳
    if new_status == 'spawning':
        task['spawned_at'] = task['updated_at']
    elif new_status == 'in_progress':
        task['started_at'] = task['updated_at']
    elif new_status in ['completed', 'failed']:
        task['completed_at'] = task['updated_at']

    # 保存（事務性更新）
    if save_tasks(tasks):
        logger.info(f"✓ 更新任務 {task_id}: {old_status} → {new_status} ({reason})")
        return True
    else:
        logger.error(f"保存任務失敗: {task_id}")
        return False
```

**最佳實踐：**
- 總是檢查狀態轉換合法性
- 記錄狀態轉換歷史便於調試
- 使用事務性更新（成功或失敗，不能部分更新）

---

### 3. 回滾（Rollback）- 回滾卡住的任務

**目標：** 將卡住的任務回滾到 pending 狀態

**回滾條件：**

| 狀態 | 超時閾值 | 回滾目標 |
|------|---------|---------|
| spawning | 120 分鐘（2 小時） | pending |
| in_progress | 24 小時 | failed |

**回滾流程：**

```python
def rollback_stuck_tasks():
    """回滾卡住的任務"""
    tasks = load_tasks()
    now = datetime.now(timezone.utc)
    rolled_back = []

    for task in tasks:
        status = task.get('status')
        task_id = task['id']

        # 回滾卡住的 spawning 任務
        if status == 'spawning':
            updated_at = task.get('updated_at', task.get('spawned_at'))
            if updated_at:
                elapsed = now - datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                if elapsed > timedelta(minutes=120):
                    if update_task_status_safely(task_id, 'pending', '超時回滾 (120 分鐘)'):
                        rolled_back.append(task_id)

        # 標記超時的 in_progress 任務為 failed
        elif status == 'in_progress':
            started_at = task.get('started_at', task.get('updated_at'))
            if started_at:
                elapsed = now - datetime.fromisoformat(started_at.replace('Z', '+00:00'))
                if elapsed > timedelta(hours=24):
                    if update_task_status_safely(task_id, 'failed', '執行超時 (24 小時)'):
                        rolled_back.append(task_id)

    logger.info(f"已回滾 {len(rolled_back)} 個任務")
    return rolled_back
```

**最佳實踐：**
- 使用合理的超時閾值（考慮任務類型）
- 記錄回滾原因便於分析
- 定期執行回滾檢查（如每次心跳）

---

### 4. 分析（Analyze）- 分析任務狀態分佈

**目標：** 統計和分析任務狀態，發現潛在問題

**分析指標：**

```python
def analyze_task_status(tasks):
    """分析任務狀態"""
    now = datetime.now(timezone.utc)

    # 基礎統計
    status_counts = defaultdict(int)
    age_distribution = defaultdict(list)

    for task in tasks:
        status = task.get('status')
        status_counts[status] += 1

        # 計算任務年齡
        created_at = task.get('created_at')
        if created_at:
            age = (now - datetime.fromisoformat(created_at.replace('Z', '+00:00'))).total_seconds()
            age_distribution[status].append(age)

    # 計算平均年齡
    avg_age = {}
    for status, ages in age_distribution.items():
        if ages:
            avg_age[status] = sum(ages) / len(ages) / 60  # 分鐘

    # 警告檢查
    warnings = []

    if status_counts.get('spawning', 0) > 10:
        warnings.append(f"⚠️ 有 {status_counts['spawning']} 個 spawning 任務，可能卡住")

    if avg_age.get('spawning', 0) > 60:
        warnings.append(f"⚠️ spawning 任務平均年齡 {avg_age['spawning']:.1f} 分鐘，異常")

    if status_counts.get('pending', 0) == 0 and status_counts.get('in_progress', 0) == 0:
        warnings.append("⚠️ 沒有待辦和執行中任務，可能需要觸發 Scout 掃描")

    return {
        'status_counts': dict(status_counts),
        'avg_age_minutes': avg_age,
        'warnings': warnings,
        'total_tasks': len(tasks)
    }
```

**最佳實踐：**
- 定期執行分析（如每次心跳或每小時）
- 設置警告閾值自動檢測異常
- 將分析結果保存到日誌或數據庫便於趨勢分析

---

## 超時配置

### 默認超時閾值

| 任務類型 | spawning 超時 | in_progress 超時 | 理由 |
|---------|--------------|-----------------|------|
| 研究類（research） | 120 分鐘 | 24 小時 | 需要時間搜索和閱讀論文 |
| 分析類（analyst） | 90 分鐘 | 6 小時 | 數據處理和計算密集 |
| 創意類（creative） | 60 分鐘 | 4 小時 | 文本生成，相對快速 |
| 自動化（automation） | 30 分鐘 | 1 小時 | 命令執行，相對快速 |

### 優先級調整

| 優先級 | 超時係數 | 說明 |
|-------|---------|------|
| critical | 2.0x | 高優先級任務給予更長時間 |
| high | 1.5x | 高優先級任務 |
| medium | 1.0x | 標準優先級 |
| low | 0.8x | 低優先級任務可以更快失敗 |

**計算公式：**
```python
def get_timeout(task, status):
    """獲取任務超時閾值"""
    base_timeout = BASE_TIMEOUTS[task['agent']][status]
    priority_factor = PRIORITY_FACTORS.get(task.get('priority', 'medium'), 1.0)
    return int(base_timeout * priority_factor)
```

---

## 工具腳本

### 可用腳本

| 腳本 | 功能 | 頻率 |
|------|------|------|
| `kanban-ops/auto_spawn_heartbeat.py` | 自動啟動 pending 任務 | 每次心跳 |
| `kanban-ops/task_state_rollback.py` | 回滾卡住的任務 | 每次心跳 |
| `kanban-ops/task_sync.py` | 同步子代理狀態 | 每次心跳 |
| `kanban-ops/monitor_and_refill.py` | 監控並補充任務 | 每次心跳 |

### 使用方式

**在心跳中執行：**
```bash
# 標準心跳流程
python3 kanban-ops/auto_spawn_heartbeat.py      # 識別並啟動任務
python3 kanban-ops/task_state_rollback.py       # 回滾卡住任務
python3 kanban-ops/task_sync.py                # 同步完成任務
python3 kanban-ops/monitor_and_refill.py       # 監控並補充
```

**手動執行：**
```bash
# 查看任務狀態分析
python3 kanban-ops/task_state_rollback.py --analyze

# 強制回滾特定任務
python3 kanban-ops/task_state_rollback.py --force <task-id>
```

---

## 常見問題

### Q1: 為什麼 spawning 超時是 120 分鐘？

**A:** 考慮以下因素：
1. **研究任務特性**：需要搜索論文、下載 PDF、閱讀和分析，通常需要 60-90 分鐘
2. **網絡延遲**：arXiv 下載可能因網絡問題變慢
3. **API 限流**：GLM API 可能有暫時性限流
4. **緩衝餘量**：120 分鐘留有 30-60 分鐘的緩衝，避免誤殺

### Q2: 為什麼不能直接從 pending 到 completed？

**A:** 違反狀態機原則：
1. **可追溯性**：無法追蹤任務是否真的執行過
2. **調試困難**：失敗時不知道在哪个階段失敗
3. **統計失真**：無法統計執行時間、成功率等指標

### Q3: 如何處理重複啟動？

**A:** 識別和預防：
```python
def check_duplicate_spawn(task):
    """檢查重複啟動"""
    # 方法 1：檢查輸出文件是否已存在
    output_path = get_task_output_path(task)
    if output_path.exists():
        logger.warning(f"輸出文件已存在，跳過: {task['id']}")
        return True

    # 方法 2：檢查最近是否有相同任務完成
    recent_completed = find_recent_completed(task['title'], hours=24)
    if recent_completed:
        logger.warning(f"最近已有相同任務完成，跳過: {task['id']}")
        return True

    return False
```

### Q4: 如何處理子代理 session 失敗？

**A:** 檢測和恢復：
1. **識別**：spawning 超時 + 無 .status 文件
2. **回滾**：狀態改為 pending
3. **重試**：下次心跳重新啟動
4. **記錄**：標記為"重試"避免無限循環

### Q5: 如何優化狀態檢查性能？

**A:** 性能優化：
1. **索引**：為 tasks.json 建立狀態索引
2. **增量檢查**：只檢查最近更新的任務
3. **批量更新**：一次更新多個任務狀態
4. **緩存**：緩存任務狀態避免重複讀取

---

## 監控和告警

### 關鍵指標

| 指標 | 正常範圍 | 警告閾值 | 嚴重閾值 |
|------|---------|---------|---------|
| spawning 任務數 | < 5 | > 10 | > 20 |
| pending 任務數 | 10-100 | < 5 | = 0 |
| in_progress 任務數 | 1-3 | > 5 | > 10 |
| 任務失敗率 | < 10% | > 15% | > 25% |
| spawning 平均年齡 | < 60 分鐘 | > 90 分鐘 | > 120 分鐘 |

### Prometheus 告警規則

```yaml
# kanban-ops/prometheus/rules/task_alerts.yml
groups:
  - name: kanban_task_alerts
    rules:
      - alert: TooManySpawningTasks
        expr: kanban_tasks_spawnings > 10
        for: 15m
        annotations:
          summary: " spawning 任務過多"
          description: "有 {{ $value }} 個 spawning 任務，可能卡住"

      - alert: TaskFailureRateHigh
        expr: rate(kanban_tasks_failed[1h]) > 0.25
        for: 30m
        annotations:
          summary: "任務失敗率過高"
          description: "任務失敗率為 {{ $value | humanizePercentage }}"

      - alert: NoPendingTasks
        expr: kanban_tasks_pending == 0
        for: 10m
        annotations:
          summary: "沒有待辦任務"
          description: "待辦任務為 0，可能需要觸發 Scout 掃描"
```

---

## 最佳實踐總結

**✅ 應該做的：**
1. 嚴格遵循狀態機規則
2. 每次狀態轉換都記錄時間戳
3. 定期檢查和回滾卡住任務
4. 設置合理的超時閾值
5. 監控關鍵指標並設置告警

**❌ 不應該做的：**
1. 直接手動修改 tasks.json（除非緊急情況）
2. 跳過狀態機規則進行狀態轉換
3. 忽略超時任務
4. 在狀態檢查和更新之間有競態條件
5. 使用固定的超時閾值（不考慮任務類型和優先級）

---

## 相關文檔

- `kanban-ops/auto_spawn_heartbeat.py` - 自動任務啟動器
- `kanban-ops/task_state_rollback.py` - 任務狀態回滾
- `kanban-ops/task_sync.py` - 任務狀態同步
- `kanban-ops/monitor_and_refill.py` - 監控和補充
- `kanban-ops/MONITORING_SYSTEM_SUCCESS.md` - 監控系統文檔

---

**最後更新：** 2026-03-03
**版本：** v1.0
**作者：** Charlie
**基於：** Mentor 建議和實際運營經驗
