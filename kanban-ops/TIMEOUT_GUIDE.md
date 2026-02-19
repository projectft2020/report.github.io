# 第 4 階段使用指南：超時處理策略

## 概述

第 4 階段提供自動化的超時檢測和處理機制，自動識別超時任務，檢查輸出文件，提供處理建議和重試策略。

---

## 快速開始

### 1. 檢查超時任務

```bash
ssh charlie@192.168.1.117
cd ~/.openclaw/workspace/kanban-ops
python3 task_manager.py timeout
```

**輸出範例（無超時）**：
```
======================================================================
⏰ 超時任務檢測報告
======================================================================

檢測時間：2026-02-19 22:05:48

✅ 沒有檢測到超時任務

所有 in_progress 任務都在正常執行時間範圍內
======================================================================
```

**輸出範例（有超時）**：
```
======================================================================
⏰ 超時任務檢測報告
======================================================================

檢測時間：2026-02-19 22:05:48

⚠️  發現 1 個超時任務

──────────────────────────────────────────────────────────────────────
超時任務詳情
──────────────────────────────────────────────────────────────────────

任務 1：h004
  標題：adaptive-hedge 回測驗證
  狀態：in_progress
  輸出文件：存在
  輸出完整：是
  推薦動作：mark_completed
  理由：輸出文件存在且完整（35.2 分鐘）

======================================================================
```

---

## 超時定義

### 超時閾值

**默認閾值**：30 分鐘

**判斷條件**：
```
任務狀態 = in_progress
且
(當前時間 - started_at) > 30 分鐘
```

### 自動調整閾值

如果任務有預估時間，閾值會動態調整：

| 情況 | 超時判斷 |
|------|----------|
| 有預估時間 | 執行時間 > 預估最大值 × 1.5 |
| 無預估時間 | 執行時間 > 30 分鐘 |

**範例**：
- 預估 15-35 分 → 35 × 1.5 = 52.5 分
- 執行 53 分 → 判定為超時
- 執行 40 分 → 仍在預估範圍內，不超時

---

## 超時處理策略

### 自動分析

當檢測到超時任務時，系統會自動分析：

1. **檢查輸出文件是否存在**
2. **檢查輸出文件是否完整**（文件大小 > 1KB）
3. **比較執行時間與預估時間**
4. **生成處理建議**

### 四種推薦動作

#### 1. mark_completed（標記為完成）

**條件**：輸出文件存在且完整

**說明**：任務雖然超時，但已經成功產出完整結果

**處理**：
```python
from timeout_handler import TimeoutHandler

handler = TimeoutHandler(
    '/Users/charlie/.openclaw/workspace/kanban/tasks.json',
    '/Users/charlie/.openclaw/workspace'
)
handler.mark_task_completed('h004')
```

**結果**：
- 任務狀態改為 `completed`
- 記錄實際執行時間
- 添加超時恢復標記

#### 2. mark_failed（標記為失敗）

**條件**：輸出文件存在但不完整

**說明**：任務執行中斷，輸出不完整

**處理**：
```python
handler.mark_task_failed('h004', '輸出文件不完整，可能寫入中斷')
```

**結果**：
- 任務狀態改為 `failed`
- 記錄失敗原因

#### 3. retry（建議重試）

**條件**：輸出文件不存在，且執行時間超過預估 150%

**說明**：任務執行失敗，需要重試

**重試策略**：
- 分解任務（如果複雜度 ≥ 3）
- 更換模型（GLM-4.5 → GLM-4.7）
- 增加超時時間

**處理**：
```bash
# 查看重試策略
python3 task_manager.py decompose h004

# 創建分解後的子任務
# 重新執行
```

#### 4. wait（繼續等待）

**條件**：仍在預估時間範圍內

**說明**：任務還沒有超時，只是預估時間較長

**處理**：等待任務完成，定期檢查

---

## 重試策略

### 策略 1：分解任務

**適用**：複雜度等級 ≥ 3

**原因**：分解可提高成功率從 60% 到 95%

**執行**：
```bash
python3 task_manager.py decompose <task_id>
```

### 策略 2：升級模型

**適用**：使用 GLM-4.5 且失敗

**原因**：GLM-4.7 處理能力更強

**執行**：
```bash
# 創建新任務時指定模型
# 將 model 改為 zai/glm-4.7
```

### 策略 3：增加超時

**適用**：任務執行時間較長

**原因**：某些任務確實需要更長時間

**執行**：
```python
# 在創建任務時設置更長的超時
# 或者分解為更小的子任務
```

---

## Python API

### TimeoutHandler 類

```python
from timeout_handler import TimeoutHandler

handler = TimeoutHandler(
    tasks_json_path='/Users/charlie/.openclaw/workspace/kanban/tasks.json',
    workspace_path='/Users/charlie/.openclaw/workspace'
)

# 檢查超時任務
timeouts = handler.check_timeouts(timeout_threshold_minutes=30.0)

for analysis in timeouts:
    print(f"任務：{analysis.task_id}")
    print(f"推薦動作：{analysis.recommended_action}")
    print(f"理由：{analysis.reason}")

# 標記完成
handler.mark_task_completed('h004')

# 標記失敗
handler.mark_task_failed('h004', '輸出文件不存在')

# 獲取重試建議
suggestions = handler.suggest_retry('h004')
for strategy in suggestions['strategies']:
    print(f"{strategy['name']}: {strategy['description']}")
```

### TaskManager 整合

```python
from task_manager import TaskManager

manager = TaskManager('/path/to/tasks.json')

# 檢查超時
manager.check_timeouts()
```

---

## 實際案例

### 案例 1：超時但成功（ap002）

**情況**：
```
任務：ap002
執行時間：35 分鐘
輸出文件：存在（49KB）
狀態：terminated（被系統終止）
```

**分析**：
```
推薦動作：mark_completed
理由：輸出文件存在且完整（49KB > 1KB）
```

**處理**：
```python
handler.mark_task_completed('ap002')
```

**結果**：
- 任務狀態改為 `completed`
- 實際時間：35 分鐘
- 標記：超時恢復成功

### 案例 2：超時且失敗（h004 第一次嘗試）

**情況**：
```
任務：h004
執行時間：16 分鐘
輸出文件：不存在
模型：GLM-4.5
複雜度：等級 3
```

**分析**：
```
推薦動作：retry
理由：超時 16 分鐘，無輸出文件
重試策略：
  - decompose_task: 分解為 2 個子任務
  - upgrade_model: 使用 GLM-4.7
```

**處理**：
```bash
# 方案 1：分解
python3 task_manager.py decompose h004
# 創建 h004-a, h004-b

# 方案 2：更換模型重試
# 創建新任務，使用 GLM-4.7
```

### 案例 3：仍在預估範圍內

**情況**：
```
任務：m002
執行時間：20 分鐘
預估時間：15-35 分
```

**分析**：
```
推薦動作：wait
理由：已執行 20 分鐘，仍在預估範圍內（35 分鐘）
```

**處理**：等待完成

---

## 定期檢查

### 自動化檢查腳本

創建 cron job 定期檢查：

```bash
#!/bin/bash
# check_timeouts.sh

cd ~/.openclaw/workspace/kanban-ops
python3 task_manager.py timeout > /tmp/timeout_report.txt 2>&1

# 如果有超時，發送通知
if grep -q "發現.*超時任務" /tmp/timeout_report.txt; then
    # 發送 Telegram 通知
    cat /tmp/timeout_report.txt
fi
```

### 設置 cron

```bash
# 每 15 分鐘檢查一次
crontab -e

# 添加以下行
*/15 * * * * /home/charlie/scripts/check_timeouts.sh
```

---

## 命令行工具

### task_manager.py

```bash
# 檢查超時
python3 task_manager.py timeout
```

### timeout_handler.py

```bash
# 直接運行
python3 timeout_handler.py
```

---

## 超時檢測邏輯

### 判斷流程

```
獲取所有 in_progress 任務
    ↓
檢查 started_at 是否存在
    ↓
計算執行時間 = now - started_at
    ↓
執行時間 > 閾值？
    ↓ 是
檢查輸出文件
    ↓
輸出存在？
    ├─ 是 → 檢查完整性
    │    ├─ 完整 → mark_completed
    │    └─ 不完整 → mark_failed
    │
    └─ 否 → 比較預估時間
         ├─ 超過預估 × 1.5 → retry
         └─ 在預估範圍內 → wait
```

### 閾值調整

```python
# 默認閾值
DEFAULT_THRESHOLD = 30.0  # 分鐘

# 有預估時間時
if estimated:
    threshold = max(estimated['max'] * 1.5, DEFAULT_THRESHOLD)
else:
    threshold = DEFAULT_THRESHOLD
```

---

## 數據字段

### time_tracking 新增字段

處理超時後，會添加以下字段：

```json
{
  "time_tracking": {
    "estimated_time": {"min": 15, "max": 35},
    "started_at": "2026-02-19T21:30:00+08:00",
    "completed_at": "2026-02-19T22:05:00+08:00",
    "actual_time_minutes": 35.2,
    "timeout_recovery": true,
    "timeout_note": "任務超時但輸出完整，已標記為完成"
  }
}
```

### 失敗任務字段

```json
{
  "status": "failed",
  "failed_at": "2026-02-19T22:10:00+08:00",
  "failure_reason": "超時且無輸出文件"
}
```

---

## 故障排除

### 問題 1：誤判為超時

**原因**：預估時間不準確

**解決**：
- 檢查預估時間是否合理
- 調整預估規則
- 增加閾值倍數（1.5 → 2.0）

### 問題 2：輸出文件判斷錯誤

**原因**：文件大小檢查太簡單

**解決**：
- 檢查文件內容關鍵詞
- 檢查文件結構完整性
- 添加特定格式的驗證

### 問題 3：重試後仍然失敗

**原因**：
- 分解不夠
- 模型仍不夠強
- 任務本身有問題

**解決**：
- 進一步分解
- 使用 GLM-4.7 + 分解
- 檢查任務描述是否清楚

---

## 最佳實踐

### 1. 定期檢查

每 15-30 分鐘檢查一次超時任務

### 2. 自動處理簡單情況

對於 `mark_completed` 情況，自動標記為完成

### 3. 人工審查複雜情況

對於 `retry` 情況，人工決定重試策略

### 4. 記錄所有處理

記錄超時原因、處理方式、結果

### 5. 分析趨勢

定期分析超時模式，優化預估和執行

---

## 預期效果

### 超時恢復率

| 情況 | 比例 | 處理 |
|------|------|------|
| 超時但成功 | ~30% | 自動標記完成 |
| 超時且失敗 | ~50% | 提供重試建議 |
| 仍在預估內 | ~20% | 繼續等待 |

### 整體改進

| 指標 | 之前 | 第 4 階段後 |
|------|------|-----------|
| 超時恢復率 | 0% | 30% |
| 自動檢測 | ❌ | ✅ |
| 處理建議 | ❌ | ✅ |
| 重試策略 | ❌ | ✅ |

---

## 下一步

### 持續改進

1. 收集超時數據
2. 分析超時模式
3. 優化預估準確度
4. 改進重試策略

### 自動化

1. 自動標記超時但成功的任務
2. 自動重試特定類型的失敗
3. 自動分解並重試

---

## 總結

第 4 階段完成後，我們可以：

✅ 自動檢測超時任務
✅ 檢查輸出文件完整性
✅ 提供處理建議
✅ 生成重試策略
✅ 標記超時恢復的任務
✅ 追蹤超時統計

**預期效果**：
- 超時恢復率：0% → 30%
- 自動檢測：❌ → ✅
- 智能處理：❌ → ✅
