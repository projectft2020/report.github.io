# 多模型架構 - 使用指南

## 概述

多模型架構為系統提供了靈活的模型分配能力，支持：
- 自動模型選擇（根據任務類型、優先級）
- 負載平衡（分散請求到不同模型）
- Rate limit 保護（自動切換到備用模型）
- 實時監控（模型健康度、利用率、成功率）

## 架構組件

### 1. 模型配置（models.json）

配置文件位置：`kanban-ops/models.json`

```json
{
  "version": "1.0.0",
  "default_model": "zai/glm-4.7",
  "models": {
    "zai/glm-4.7": {
      "id": "zai/glm-4.7",
      "name": "GLM-4.7",
      "provider": "zai",
      "quality": "high",
      "speed": "medium",
      "cost": "medium",
      "concurrent_limit": 1,
      "priority": 1,
      "enabled": true,
      "description": "高品質模型，適合分析、創作、複雜推理",
      "suitable_agents": ["analyst", "creative", "architect", "mentors"],
      "health": { ... },
      "stats": { ... }
    },
    "zai/glm-4.5": {
      "id": "zai/glm-4.5",
      "name": "GLM-4.5",
      "provider": "zai",
      "quality": "medium",
      "speed": "fast",
      "cost": "low",
      "concurrent_limit": 10,
      "priority": 2,
      "enabled": false,
      "description": "快速模型，適合研究、自動化、簡單任務",
      "suitable_agents": ["research", "automation", "developer"],
      "health": { ... },
      "stats": { ... }
    }
  },
  "agent_model_mapping": {
    "research": {
      "default": "zai/glm-4.7",
      "fallback": ["zai/glm-4.5"],
      "min_quality": "medium"
    },
    "analyst": {
      "default": "zai/glm-4.7",
      "fallback": [],
      "min_quality": "high"
    }
  }
}
```

**關鍵配置項：**
- `enabled`: 是否啟用該模型
- `concurrent_limit`: 並發限制
- `quality`: 品質等級（high, medium, low）
- `speed`: 速度等級（fast, medium, slow）
- `suitable_agents`: 適合的代理類型

### 2. 模型分配器（model_allocator.py）

核心功能：
- 根據代理類型選擇最佳模型
- 檢查模型可用性（enabled, rate limit, 並發限制）
- 分配策略（默認、高品質優先、快速優先）
- 更新模型統計

**使用示例：**

```python
from model_allocator import ModelAllocator

# 初始化分配器
allocator = ModelAllocator()

# 分配任務（默認策略）
result = allocator.allocate_task("analyst")
print(result)
# {
#   "model_id": "zai/glm-4.7",
#   "agent_id": "analyst",
#   "quality": "high",
#   "speed": "medium",
#   "priority": "default"
# }

# 高品質優先
result = allocator.allocate_task("analyst", priority="high_quality")

# 快速優先
result = allocator.allocate_task("research", priority="fast")

# 標記任務完成
allocator.complete_task("zai/glm-4.7", success=True)

# 標記 rate limit
allocator.mark_rate_limit("zai/glm-4.7", cooldown_minutes=30)
```

### 3. 模型監控器（model_monitor.py）

核心功能：
- 監控模型健康度
- 檢測 rate limit 模式
- 計算模型利用率
- 生成系統建議

**使用示例：**

```python
from model_monitor import ModelMonitor

# 初始化監控器
monitor = ModelMonitor()

# 獲取所有模型健康度
health_list = monitor.get_all_models_health()
for health in health_list:
    print(f"{health['model_id']}: {health['status']}")

# 獲取模型利用率
utilization = monitor.get_model_utilization()
for model_id, util in utilization.items():
    print(f"{model_id}: {util['active']}/{util['limit']} ({util['percentage']:.1f}%)")

# 檢測 rate limit 模式
pattern = monitor.detect_rate_limit_pattern("zai/glm-4.7")
if pattern["has_pattern"]:
    print(f"⚠️ {pattern['message']}")

# 獲取系統建議
recommendations = monitor.get_system_recommendations()
for rec in recommendations:
    print(rec)

# 記錄狀態到日誌
monitor.log_status()
```

### 4. 集成到心跳流程（auto_spawn_heartbeat.py）

自動任務啟動器已集成多模型分配器：
- 自動為每個任務選擇最佳模型
- 優先級：metadata.model > task.model > ModelAllocator > 默認 glm-4.7
- 支持模型回退（fallback）

## 工作流程

### 正常流程

```
1. 心跳觸發
   ↓
2. 加載模型配置（models.json）
   ↓
3. 檢查模型健康度
   ↓
4. 為每個任務選擇模型
   - 檢查 enabled
   - 檢查 rate limit
   - 檢查並發限制
   ↓
5. 生成 spawn_commands.jsonl
   ↓
6. 主會話執行 sessions_spawn
   ↓
7. 任務完成，更新統計
   ↓
8. 下次心跳
```

### Rate limit 流程

```
1. 檢測到 rate limit（任務失敗）
   ↓
2. 標記模型為 rate limited
   - 設置 cooldown 時間
   - 更新模型狀態
   ↓
3. 下次心跳分配任務
   - 跳過被限流的模型
   - 嘗試備用模型
   ↓
4. Cooldown 過期
   - 清除 rate limit
   - 恢復模型可用
```

## 使用場景

### 場景 1：保持高品質（當前策略）

**目標：** 所有任務使用 glm-4.7

**配置：**
```json
{
  "models": {
    "zai/glm-4.7": { "enabled": true, "concurrent_limit": 1 },
    "zai/glm-4.5": { "enabled": false }
  }
}
```

**結果：**
- 所有任務使用 glm-4.7
- 保持高品質輸出
- 接受 rate limit（背壓機制處理）

### 場景 2：多模型並發（未來）

**目標：** 分散請求到不同模型，提高吞吐量

**配置：**
```json
{
  "models": {
    "zai/glm-4.7": { "enabled": true, "concurrent_limit": 1 },
    "zai/glm-4.5": { "enabled": true, "concurrent_limit": 5 }
  }
}
```

**結果：**
- 高品質任務（analyst, creative）→ glm-4.7
- 快速任務（research, automation）→ glm-4.5
- 自動負載平衡
- 提高整體吞吐量

### 場景 3：Rate limit 保護

**目標：** 自動處理 rate limit，避免任務卡住

**流程：**
1. 檢測到 glm-4.7 rate limit
2. 標記 glm-4.7 為 rate limited（30 分鐘冷卻）
3. 新任務自動分配到 glm-4.5
4. 冷卻過期，恢復 glm-4.7 可用

## 監控和日誌

### 日誌文件

- `model_monitor.log`: 模型監控日誌
- `heartbeat.log`: 心跳日誌（包含模型分配信息）
- `backpressure.log`: 背壓日誌（包含健康度調整）

### 監控指標

**模型級別：**
- 活躍任務數（active_tasks）
- 並發限制（concurrent_limit）
- 成功率（success_rate）
- Rate limit 狀態（rate_limited）

**系統級別：**
- 總請求數（total_requests）
- 成功/失敗/限流（successful/failed/rate_limited）
- 模型利用率（utilization）

### 查看狀態

```bash
# 運行測試腳本
cd ~/.openclaw/workspace/kanban-ops
python3 test_multimodel.py

# 查看模型監控日誌
cat model_monitor.log

# 查看心跳日誌
cat heartbeat.log | tail -50
```

## 故障排除

### 問題 1：無可用模型

**原因：**
- 所有模型被 rate limit
- 並發限制已滿
- 所有模型未啟用

**解決方案：**
- 等待 cooldown 過期
- 增加並發限制
- 啟用備用模型

### 問題 2：模型分配失敗

**原因：**
- models.json 配置錯誤
- 代理類型沒有模型映射

**解決方案：**
- 檢查 models.json 語法
- 添加 agent_model_mapping

### 問題 3：Rate limit 頻繁

**原因：**
- 並發太高
- 請求太頻繁

**解決方案：**
- 降低並發限制
- 增加請求間隔
- 啟用更多模型分散負載

## 未來擴展

### 支持更多模型

添加新模型到 `models.json`：

```json
{
  "claude-3.5": {
    "id": "claude-3.5",
    "name": "Claude 3.5",
    "provider": "anthropic",
    "quality": "high",
    "speed": "fast",
    "cost": "high",
    "concurrent_limit": 3,
    "enabled": true,
    "suitable_agents": ["analyst", "creative"]
  }
}
```

### 智能調度

基於歷史數據自動選擇模型：
- 分析每個模型的性能指標
- 預測最佳模型選擇
- 動態調整分配策略

### 成本優化

根據任務複雜度選擇最經濟的模型：
- 簡單任務 → 低成本模型
- 複雜任務 → 高品質模型
- 實時監控成本

---

**文檔版本：** 1.0.0
**最後更新：** 2026-03-05
**維護者：** Charlie (Orchestrator)
