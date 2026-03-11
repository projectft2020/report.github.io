# 智能並發任務啟動器 - 使用指南

## 📋 概述

`spawn_tasks_intelligent.py` 實現了**方案 B：智能並發啟動**，解決同時啟動多個高 Token 任務導致的 rate limit 問題。

### 核心問題

**當前 Scout 行為（問題）：**
```
觸發掃描 → 發現 N 個高品質主題 → 同時創建 N 個任務
                                   → 同時啟動 N 個子代理
                                   → 大量 Token 同時請求（337k in）
                                   → 🚨 Rate limit ❌
```

**方案 B 解決（正確）：**
```
觸發掃描 → 發現 N 個主題 → 預估 Token 使用
                           → 按 300k Token 限制分組
                           → 組 1: 同時啟動
                           → 等待 5 分鐘
                           → 組 2: 同時啟動
                           → ...
                           → ✅ 避免 rate limit ✅
```

---

## 🎯 核心功能

### 1. Token 預估

基於以下因素預估每個任務的 Token 使用：
- **代理類型**：Research (80k-150k), Analyst (50k-100k), Developer (40k-80k)
- **任務複雜度**：1 (簡單) - 5 (非常複雜)
- **任務描述長度**：描述越長，輸入 Token 越多

**預估準確度：**
- 置信度：70%-90%（基於可用信息）
- 範圍：min - max（保守估算）

### 2. 智能分組

**分組策略：**
1. 按 Token 預估排序（小到大）
2. 貪心算法：盡量填滿每組，不超過限制
3. 每組限制：
   - Token 限制：300k * 0.8（安全係數）= 240k
   - 最大並發：5 個任務

**分組示例：**
```
組 1: 2 個任務, 預估 200,000 tokens
  - s146 (Research): 100,000 tokens
  - s148 (Research): 100,000 tokens

組 2: 2 個任務, 預估 200,000 tokens
  - s147 (Research): 100,000 tokens
  - s149 (Research): 100,000 tokens

組 3: 2 個任務, 預估 200,000 tokens
  ...
```

### 3. 序列啟動

**啟動流程：**
```
批次 1/3:
  → 同時啟動 2 個任務
  → 等待子代理啟動驗證
  → 繼續...

等待 5 分鐘...

批次 2/3:
  → 同時啟動 2 個任務
  → 繼續...

等待 5 分鐘...

批次 3/3:
  → 同時啟動 2 個任務
  → 完成
```

---

## 🚀 使用方法

### 基本命令

```bash
# 啟動任務（智能分組 + 序列啟動）
python3 kanban-ops/spawn_tasks_intelligent.py spawn [max_tasks]

# 只預估 Token，不啟動
python3 kanban-ops/spawn_tasks_intelligent.py estimate [max_tasks]

# 只分組，不啟動
python3 kanban-ops/spawn_tasks_intelligent.py group [max_tasks]

# 只打印計劃，不實際啟動
python3 kanban-ops/spawn_tasks_intelligent.py spawn --dry-run
```

### 示例

#### 示例 1：預估隊列中的任務

```bash
$ python3 kanban-ops/spawn_tasks_intelligent.py estimate

ℹ️ [2026-02-22 08:28:12 UTC] ============================================================
ℹ️ [2026-02-22 08:28:12 UTC] 任務 Token 預估
ℹ️ [2026-02-22 08:28:12 UTC] ============================================================
ℹ️ [2026-02-22 08:28:12 UTC] 1. a004d | unknown      |  50000 - 100000 avg  75000 | 置信度 70%
ℹ️ [2026-02-22 08:28:12 UTC] 2. q005a | unknown      |  50000 - 100000 avg  75000 | 置信度 70%
ℹ️ [2026-02-22 08:28:12 UTC] 3. q005b | unknown      |  50000 - 100000 avg  75000 | 置信度 70%
...
ℹ️ [2026-02-22 08:28:12 UTC] 總計：400,000 - 800,000 avg 600,000 tokens
```

#### 示例 2：查看分組計劃

```bash
$ python3 kanban-ops/spawn_tasks_intelligent.py group

ℹ️ [2026-02-22 08:28:14 UTC] 分組配置：Token 限制 240,000 (300,000 * 0.8)
ℹ️ [2026-02-22 08:28:14 UTC]            最大並發 5 個任務/組
ℹ️ [2026-02-22 08:28:14 UTC] 分組結果：4 組
ℹ️ [2026-02-22 08:28:14 UTC] 組 1: 2 個任務, 預估 200,000 tokens
ℹ️ [2026-02-22 08:28:14 UTC] 組 2: 2 個任務, 預估 200,000 tokens
ℹ️ [2026-02-22 08:28:14 UTC] 組 3: 2 個任務, 預估 200,000 tokens
ℹ️ [2026-02-22 08:28:14 UTC] 組 4: 2 個任務, 預估 200,000 tokens
```

#### 示例 3：實際啟動（dry-run）

```bash
$ python3 kanban-ops/spawn_tasks_intelligent.py spawn --dry-run

ℹ️ [2026-02-22 08:28:15 UTC] 步驟 1/4: 載入隊列任務...
ℹ️ [2026-02-22 08:28:15 UTC] 成功載入 8 個任務
ℹ️ [2026-02-22 08:28:15 UTC] 步驟 2/4: 預估 Token 使用...
ℹ️ [2026-02-22 08:28:15 UTC] 步驟 3/4: 按 Token 限制分組...
ℹ️ [2026-02-22 08:28:15 UTC] 分組結果：4 組
ℹ️ [2026-02-22 08:28:15 UTC] 步驟 4/4: 序列啟動各組...

⚠️ [2026-02-22 08:28:15 UTC] 需要在主會話中執行以下命令：
⚠️ [2026-02-22 08:28:15 UTC] ============================================================
⚠️ [2026-02-22 08:28:15 UTC] 組 1: sessions_spawn({"agentId": "unknown", "task": "...", "label": "a004d"})
⚠️ [2026-02-22 08:28:15 UTC] 組 1: sessions_spawn({"agentId": "unknown", "task": "...", "label": "q005a"})
⚠️ [2026-02-22 08:28:15 UTC] ============================================================

ℹ️ [2026-02-22 08:28:15 UTC] 等待 2 個子代理啟動...
ℹ️ [2026-02-22 08:28:15 UTC] 等待 5 分鐘後啟動下一批次...
```

#### 示例 4：實際啟動（執行）

```bash
$ python3 kanban-ops/spawn_tasks_intelligent.py spawn 5

# 將執行以下步驟：
# 1. 載入隊列中的 5 個任務
# 2. 預估 Token 使用
# 3. 分組
# 4. 序列啟動各組（等待 5 分鐘間隔）
```

---

## ⚙️ 配置參數

在 `spawn_tasks_intelligent.py` 的 `SPAWN_CONFIG` 中調整：

```python
SPAWN_CONFIG = {
    # Token 限制配置
    'TOKEN_LIMIT_PER_BATCH': 300_000,  # 每組最大 Token（輸入 + 輸出）
    'TOKEN_SAFETY_MARGIN': 0.8,         # 安全係數（實際使用 80%）
    
    # 時間配置
    'BATCH_DELAY_MINUTES': 5,            # 組間隔（分鐘）
    'TASK_VERIFICATION_TIMEOUT': 10,      # 每個任務驗證超時（秒）
    
    # 並發配置
    'MAX_CONCURRENT_TASKS': 5,           # 每組最大並發任務數
}
```

### 調整建議

**場景 1：經常遇到 rate limit**
```python
'TOKEN_LIMIT_PER_BATCH': 200_000,  # 降低到 200k
'TOKEN_SAFETY_MARGIN': 0.7,         # 降低安全係數
'BATCH_DELAY_MINUTES': 8,           # 增加等待時間
```

**場景 2：API 穩定，想提高效率**
```python
'TOKEN_LIMIT_PER_BATCH': 400_000,  # 提高到 400k
'TOKEN_SAFETY_MARGIN': 0.9,         # 提高安全係數
'BATCH_DELAY_MINUTES': 3,           # 減少等待時間
'MAX_CONCURRENT_TASKS': 8,           # 增加並發數
```

**場景 3：大量低 Token 任務**
```python
'TOKEN_LIMIT_PER_BATCH': 500_000,  # 提高到 500k
'TOKEN_SAFETY_MARGIN': 0.85,
'MAX_CONCURRENT_TASKS': 10,          # 增加並發數
'BATCH_DELAY_MINUTES': 2,           # 減少等待時間
```

---

## 🔍 Token 預估數據

### 代理類型預估（基於歷史統計）

| 代理類型 | 最小 Token | 最大 Token | 平均 Token | 典型場景 |
|---------|-----------|-----------|-----------|---------|
| **research** | 80k | 150k | 115k | Web 搜索 + 文獻分析 + 深度報告 |
| **analyst** | 50k | 100k | 75k | 數據分析 + 邏輯推理 + 策略設計 |
| **architect** | 60k | 120k | 90k | 架構設計 + 技術文檔 + 審查 |
| **developer** | 40k | 80k | 60k | 代碼實現 + 測試 + 文檔 |
| **automation** | 20k | 50k | 35k | 文件操作 + 腳本執行 + 簡單任務 |
| **creative** | 40k | 90k | 65k | 寫作 + 內容創作 + 編輯 |
| **mentors** | 50k | 100k | 75k | 深度對話 + 指導 + 反思 |

### 複雜度調整係數

| 複雜度 | 係數 | 說明 |
|-------|-----|------|
| 1 (簡單) | 1.0x | 基準 Token 使用 |
| 2 (中等) | 1.25x | +25% Token |
| 3 (複雜) | 1.50x | +50% Token |
| 4 (很複雜) | 1.75x | +75% Token |
| 5 (非常複雜) | 2.0x | +100% Token |

### 任務描述長度調整

| 描述長度 | 調整係數 |
|---------|---------|
| < 5,000 字符 | 1.0x |
| 5,000 - 10,000 | 1.2x |
| > 10,000 | 1.4x |

---

## 📊 性能對比

### 方案 A：序列啟動（簡單）

```
8 個任務，每個 100k tokens：
- 時間：8 * 10 分鐘 = 80 分鐘
- Token 峰值：100k（任何時刻）
- Rate limit 風險：❌ 無
```

### 方案 B：智能並發（本方案）

```
8 個任務，分為 4 組，每組 2 個：
- 時間：4 * (10 分鐘 + 5 分鐘) = 60 分鐘
- Token 峰值：200k（每組）
- Rate limit 風險：✅ 低
```

### 當前方式（有問題）

```
8 個任務，同時啟動：
- 時間：10 分鐘
- Token 峰值：800k（初始衝擊）
- Rate limit 風險：🚨 高
```

**結論：**
- 序列啟動：安全但慢
- 智能並發：平衡效率和安全性 ✅
- 當前方式：不安全

---

## 🔧 故障排除

### 問題 1：預估 Token 不準確

**症狀：**
- 實際 Token 使用遠超預估
- 仍然觸發 rate limit

**解決方案：**
1. 降低 `TOKEN_LIMIT_PER_BATCH`（從 300k 降到 200k）
2. 降低 `TOKEN_SAFETY_MARGIN`（從 0.8 降到 0.7）
3. 增加 `BATCH_DELAY_MINUTES`（從 5 分鐘增加到 8 分鐘）

### 問題 2：分組不合理

**症狀：**
- 每組只有 1 個任務
- 總批次数太多

**解決方案：**
1. 提高 `TOKEN_LIMIT_PER_BATCH`
2. 提高 `MAX_CONCURRENT_TASKS`
3. 檢查隊列中任務的實際 Token 使用

### 問題 3：等待時間太長

**症狀：**
- 總啟動時間超過預期
- 影響工作效率

**解決方案：**
1. 減少 `BATCH_DELAY_MINUTES`（從 5 分鐘降到 3 分鐘）
2. 提高 `TOKEN_LIMIT_PER_BATCH`（每組更多任務）
3. 考慮使用方案 A（序列啟動）如果任務數量少

### 問題 4：任務啟動失敗

**症狀：**
- 子代理啟動失敗
- 任務狀態卡在 spawning

**解決方案：**
1. 運行 `python3 kanban-ops/spawn_tasks_safe.py cleanup` 清理卡住的任務
2. 檢查 OpenClaw Gateway 狀態
3. 檢查子代理配置

---

## 📚 與其他工具的集成

### 與 Scout 集成

在 Scout 掃描後，自動使用智能啟動：

```python
# scout_agent.py 中修改
def create_tasks_batch(tasks):
    """創建任務並智能啟動"""
    
    # 創建任務到隊列
    for task in tasks:
        write_to_queue(task)
    
    # 使用智能啟動
    import subprocess
    result = subprocess.run([
        'python3', 'kanban-ops/spawn_tasks_intelligent.py',
        'spawn', str(len(tasks))
    ])
    
    return result.returncode == 0
```

### 與 Monitor and Refill 集成

在 monitor_and_refill.py 中，檢查到 Scout 掃描後自動啟動：

```python
# monitor_and_refill.py 中修改
def monitor_and_refill():
    """監控並補充任務"""
    pending_count = get_pending_count()
    
    if pending_count < 3:
        # 觸發 Scout 掃描
        scout.run_scan()
        
        # 智能啟動新任務
        subprocess.run([
            'python3', 'kanban-ops/spawn_tasks_intelligent.py',
            'spawn', '10'
        ])
```

### 與 Heartbeat 集成

在 HEARTBEAT.md 中添加檢查：

```bash
## Priority Tasks

### 1. 檢查任務隊列並智能啟動
\`\`\`bash
# 檢查隊列
ls ~/.openclaw/workspace/kanban-ops/task_queue/

# 如果有任務，智能啟動
cd ~/.openclaw/workspace
python3 kanban-ops/spawn_tasks_intelligent.py spawn 5
\`\`\`
```

---

## 🎓 最佳實踐

### 1. 定期預估和檢查

**建議：**
- 每次 Scout 掃描前，運行 `estimate` 檢查隊列
- 每週運行 `group` 檢查分組合理性
- 根據實際情況調整配置

### 2. 監控 Token 使用

**建議：**
- 記錄每次啟動的實際 Token 使用
- 與預估進行對比
- 更新 `TOKEN_ESTIMATES` 數據

### 3. 靈活調整策略

**場景 1：大量高 Token 任務（Research 很多）**
- 降低 `TOKEN_LIMIT_PER_BATCH` 到 200k
- 增加等待時間到 8 分鐘

**場景 2：大量低 Token 任務（Automation 很多）**
- 提高 `TOKEN_LIMIT_PER_BATCH` 到 500k
- 增加 `MAX_CONCURRENT_TASKS` 到 10
- 減少等待時間到 2 分鐘

**場景 3：混合任務（Research + Automation）**
- 使用預設配置
- 貪心分組會自動平衡

### 4. 錯誤處理

**建議：**
- 如果某批次失敗，重試該批次
- 不要跳過失敗的批次
- 記錄失敗原因和 Token 使用

---

## 🚀 未來改進

### 短期（本週）

- [ ] 實現自動重試機制
- [ ] 添加實時 Token 使用監控
- [ ] 改進預估準確性（基於歷史數據）

### 中期（本月）

- [ ] 學習型預估（根據實際數據動態調整）
- [ ] 自適應配置（根據 rate limit 情況自動調整參數）
- [ ] 可視化報告（Token 使用、批次時間、成功率）

### 長期（下個月）

- [ ] 機器學習預估模型
- [ ] 實時 API 限流檢測
- [ ] 智能調度算法（優化啟動順序）

---

## 📝 總結

**智能並發啟動器（方案 B）實現了：**

✅ **智能 Token 預估** - 基於代理類型、複雜度、描述長度
✅ **安全分組策略** - 貪心算法，確保不超過限制
✅ **序列啟動流程** - 組間隔 5 分鐘，避免 rate limit
✅ **靈活配置** - 可根據實際情況調整參數
✅ **監控和日誌** - 詳細的預估和分組報告

**相較於方案 A（序列啟動）：**
- 效率提高 25%（60 分鐘 vs 80 分鐘）
- Token 峰值可控（200k vs 100k）
- Rate limit 風險低

**相較於當前方式（同時啟動）：**
- 安全性大幅提升
- 避免 rate limit
- 可預測的啟動時間

---

**使用方式：**
```bash
python3 kanban-ops/spawn_tasks_intelligent.py spawn [max_tasks]
```

**配置位置：**
`~/.openclaw/workspace/kanban-ops/spawn_tasks_intelligent.py`

**文檔位置：**
`~/.openclaw/workspace/kanban-ops/INTELLIGENT_SPAWN_GUIDE.md`
