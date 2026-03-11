# Scout 主題偏好系統完整設計文檔

**版本:** v2.0
**日期:** 2026-03-04
**作者:** Mentor Agent
**狀態:** 設計階段

---

## 目錄

1. [系統概述](#系統概述)
2. [數據結構設計](#數據結構設計)
3. [偏好收集機制](#偏好收集機制)
4. [偏好更新算法](#偏好更新算法)
5. [搜尋打分機制](#搜尋打分機制)
6. [系統集成](#系統集成)
7. [模塊化架構](#模塊化架構)
8. [Python 實現](#python-實現)
9. [實現時間表](#實現時間表)
10. [風險和緩解措施](#風險和緩解措施)
11. [成功指標](#成功指標)

---

## 系統概述

### 核心目標

Scout 主題偏好系統旨在：

1. **智能化搜尋** - 根據用戶偏好動態調整搜尋結果排序
2. **持續學習** - 通過用戶反饋不斷優化偏好模型
3. **平衡探索與利用** - 在相關性和新穎性之間找到最佳平衡點
4. **可擴展性** - 模塊化設計支持未來功能擴展

### 系統特點

- **多維度偏好追蹤**: 主題類型、時間窗口、內容深度、情感傾向
- **動態權重調整**: 使用 EMA 和時間衰減算法實時更新
- **置信度校準**: 根據交互頻率和質量調整偏好置信度
- **偏差校正**: 識別並緩解過度專注或探索不足的問題

---

## 數據結構設計

### PREFERENCES.json v2.0

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://openclaw.ai/schemas/preferences-v2.json",
  "title": "Scout Topic Preferences v2.0",
  "description": "User topic preferences data structure for Scout Agent",
  "type": "object",
  "properties": {
    "version": {
      "type": "string",
      "const": "2.0",
      "description": "Schema version"
    },
    "metadata": {
      "type": "object",
      "properties": {
        "userId": {
          "type": "string",
          "description": "Unique user identifier"
        },
        "createdAt": {
          "type": "string",
          "format": "date-time",
          "description": "Timestamp when preferences were first created"
        },
        "lastUpdated": {
          "type": "string",
          "format": "date-time",
          "description": "Last update timestamp"
        },
        "totalInteractions": {
          "type": "integer",
          "minimum": 0,
          "description": "Total number of recorded interactions"
        },
        "confidenceLevel": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 1.0,
          "description": "Overall confidence in preference model"
        }
      },
      "required": ["userId", "createdAt", "lastUpdated"]
    },
    "topics": {
      "type": "object",
      "description": "Topic-specific preferences",
      "additionalProperties": {
        "type": "object",
        "properties": {
          "topicId": {
            "type": "string",
            "description": "Canonical topic identifier"
          },
          "aliases": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "Alternative names for this topic"
          },
          "weight": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
            "description": "Current preference weight (EMA)"
          },
          "confidence": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
            "description": "Confidence in this topic preference"
          },
          "trend": {
            "type": "object",
            "properties": {
              "direction": {
                "type": "string",
                "enum": ["rising", "stable", "declining"]
              },
              "slope": {
                "type": "number",
                "description": "Trend slope value"
              },
              "lastChange": {
                "type": "string",
                "format": "date-time"
              }
            },
            "required": ["direction", "slope"]
          },
          "decay": {
            "type": "object",
            "properties": {
              "halflife": {
                "type": "number",
                "description": "Half-life in hours"
              },
              "lastInteraction": {
                "type": "string",
                "format": "date-time"
              },
              "decayFactor": {
                "type": "number",
                "minimum": 0.0,
                "maximum": 1.0
              }
            }
          },
          "attributes": {
            "type": "object",
            "description": "Additional topic-specific attributes",
            "properties": {
              "depthPreference": {
                "type": "number",
                "minimum": 0.0,
                "maximum": 1.0,
                "description": "Preference for depth vs breadth"
              },
              "recencyPreference": {
                "type": "number",
                "minimum": 0.0,
                "maximum": 1.0,
                "description": "Preference for recent content"
              },
              "sourcePreference": {
                "type": "object",
                "description": "Source type preferences",
                "additionalProperties": {
                  "type": "number",
                  "minimum": 0.0,
                  "maximum": 1.0
                }
              }
            }
          },
          "history": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "timestamp": {
                  "type": "string",
                  "format": "date-time"
                },
                "weight": {
                  "type": "number"
                },
                "interactionType": {
                  "type": "string",
                  "enum": ["click", "save", "share", "positive_feedback", "negative_feedback", "ignore"]
                },
                "context": {
                  "type": "object",
                  "description": "Additional context about the interaction"
                }
              }
            }
          }
        },
        "required": ["topicId", "weight", "confidence"]
      }
    },
    "globalSettings": {
      "type": "object",
      "properties": {
        "explorationRate": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 1.0,
          "default": 0.15,
          "description": "Base exploration rate for novel topics"
        },
        "decayHalfLife": {
          "type": "number",
          "minimum": 1,
          "default": 168,
          "description": "Default decay half-life in hours (7 days)"
        },
        "emaAlpha": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 1.0,
          "default": 0.3,
          "description": "EMA smoothing factor"
        },
        "confidenceGrowthRate": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 1.0,
          "default": 0.1,
          "description": "How fast confidence grows with interactions"
        },
        "minConfidenceThreshold": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 1.0,
          "default": 0.3,
          "description": "Minimum confidence to use a preference"
        }
      }
    },
    "biases": {
      "type": "object",
      "properties": {
        "topicDiversity": {
          "type": "number",
          "minimum": 0.0,
          "description": "Current topic diversity score"
        },
        "recencyBias": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 1.0,
          "description": "Bias towards recent topics"
        },
        "explorationBias": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 1.0,
          "description": "Bias towards exploration vs exploitation"
        }
      }
    },
    "performanceMetrics": {
      "type": "object",
      "properties": {
        "clickThroughRate": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 1.0
        },
        "satisfactionScore": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 1.0
        },
        "diversityScore": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 1.0
        },
        "lastCalculated": {
          "type": "string",
          "format": "date-time"
        }
      }
    }
  },
  "required": ["version", "metadata", "topics", "globalSettings"]
}
```

### 示例數據

```json
{
  "version": "2.0",
  "metadata": {
    "userId": "user_abc123",
    "createdAt": "2026-03-01T00:00:00Z",
    "lastUpdated": "2026-03-04T00:00:00Z",
    "totalInteractions": 156,
    "confidenceLevel": 0.72
  },
  "topics": {
    "machine_learning": {
      "topicId": "machine_learning",
      "aliases": ["ML", "人工智能", "AI"],
      "weight": 0.85,
      "confidence": 0.82,
      "trend": {
        "direction": "rising",
        "slope": 0.12,
        "lastChange": "2026-03-03T10:30:00Z"
      },
      "decay": {
        "halflife": 120,
        "lastInteraction": "2026-03-04T00:00:00Z",
        "decayFactor": 0.94
      },
      "attributes": {
        "depthPreference": 0.78,
        "recencyPreference": 0.65,
        "sourcePreference": {
          "arxiv": 0.85,
          "news": 0.45,
          "blogs": 0.72
        }
      },
      "history": [
        {
          "timestamp": "2026-03-04T00:00:00Z",
          "weight": 0.85,
          "interactionType": "save",
          "context": {"searchQuery": "transformer architecture"}
        }
      ]
    },
    "productivity": {
      "topicId": "productivity",
      "aliases": ["效率", "時間管理"],
      "weight": 0.62,
      "confidence": 0.68,
      "trend": {
        "direction": "stable",
        "slope": 0.02,
        "lastChange": "2026-03-02T14:00:00Z"
      },
      "decay": {
        "halflife": 168,
        "lastInteraction": "2026-03-01T08:00:00Z",
        "decayFactor": 0.87
      },
      "attributes": {
        "depthPreference": 0.45,
        "recencyPreference": 0.55,
        "sourcePreference": {
          "news": 0.70,
          "blogs": 0.65,
          "arxiv": 0.20
        }
      }
    }
  },
  "globalSettings": {
    "explorationRate": 0.15,
    "decayHalfLife": 168,
    "emaAlpha": 0.3,
    "confidenceGrowthRate": 0.1,
    "minConfidenceThreshold": 0.3
  },
  "biases": {
    "topicDiversity": 0.68,
    "recencyBias": 0.55,
    "explorationBias": 0.15
  },
  "performanceMetrics": {
    "clickThroughRate": 0.34,
    "satisfactionScore": 0.71,
    "diversityScore": 0.68,
    "lastCalculated": "2026-03-04T00:00:00Z"
  }
}
```

---

## 偏好收集機制

### 交互類型定義

| 交互類型 | 權重影響 | 置信度影響 | 說明 |
|---------|---------|-----------|------|
| `click` | +0.05 | +0.03 | 點擊結果 |
| `save` | +0.15 | +0.08 | 保存/收藏 |
| `share` | +0.12 | +0.06 | 分享內容 |
| `positive_feedback` | +0.20 | +0.12 | 明確正面反饋 |
| `negative_feedback` | -0.25 | +0.10 | 明確負面反饋 |
| `ignore` | -0.02 | +0.01 | 忽略結果 |
| `dwell_time` | +0.01~0.10 | +0.02~0.05 | 基於停留時間 |

### 收集觸發點

1. **搜尋執行時**
   - 記錄搜尋查詢的關鍵詞
   - 識別主題類別
   - 更新相關主題權重

2. **結果展示時**
   - 追蹤點擊行為
   - 記錄停留時間
   - 監控滾動深度

3. **用戶反饋時**
   - 顯式反饋（點贊/踩）
   - 隱式反饋（收藏、分享）
   - 忽略行為分析

4. **定期更新**
   - 每小時衰減計算
   - 每日趨勢分析
   - 每周偏差校正

---

## 偏好更新算法

### 1. 指數移動平均 (EMA)

**算法公式：**

```
weight_new = alpha * signal + (1 - alpha) * weight_old
```

**實現：**

```python
def update_ema(
    current_weight: float,
    signal: float,
    alpha: float = 0.3
) -> float:
    """
    使用指數移動平均更新權重

    Args:
        current_weight: 當前權重
        signal: 新信號值
        alpha: 平滑因子 (0-1)

    Returns:
        更新後的權重
    """
    return alpha * signal + (1 - alpha) * current_weight
```

### 2. 時間衰減

**算法公式：**

```
decay_factor = 0.5 ^ (time_elapsed / half_life)
weight = weight * decay_factor
```

### 3. 置信度校準

**算法公式：**

```
confidence_new = confidence_old + (1 - confidence_old) * growth_rate * signal_strength
```

---

## 搜尋打分機制

### 親和度分數 (Affinity Score)

計算結果與用戶偏好的親和度，考慮主題權重和置信度。

### 新穎性分數 (Novelty Score)

基於主題的新穎程度、最近交互歷史計算。

### 探索獎勵 (Exploration Bonus)

鼓勵探索新內容，基於新穎性和多樣性分數。

### 綜合打分

最終分數 = 0.45 * 親和度 + 0.15 * 新穎性 + 0.10 * 探索獎勵 + 0.30 * 基礎相關性

---

## 系統集成

### 1. Scout Agent 集成

提供 `ScoutPreferenceManager` 類，用於記錄交互、獲取排序結果。

### 2. Kanban 集成

創建偏好看板卡片，顯示熱門主題、偏差警報、最近活動。

### 3. 監控集成

收集性能指標、健康指標、趨勢指標、偏差指標。

---

## 模塊化架構

### 核心模塊

1. **pref_core.py** - 核心數據結構和工具函數
2. **pref_algorithms.py** - 所有核心算法實現
3. **pref_integration.py** - 系統集成接口

---

## Python 實現

### 完整的模塊實現

（包含在設計文檔中，可直接使用）

---

## 實現時間表

### 階段 1: 基礎設施 (1-2 週)

- 設計 PREFERENCES.json v2.0 Schema
- 實現 `pref_core.py` 模塊
- 實現基礎算法 (EMA, 時間衰減)
- 建立數據持久化機制
- 編寫單元測試

### 階段 2: 核心功能 (2-3 週)

- 實現置信度校準算法
- 實現趨勢分析算法
- 實現偏差檢測與校正
- 實現完整打分機制
- 實現 ScoutPreferenceManager

### 階段 3: 系統集成 (2 週)

- Scout Agent API 集成
- Kanban 看板集成
- 監控指標收集
- 定時任務設置
- 錯誤處理和日誌

### 階段 4: 優化和部署 (1-2 週)

- 性能分析和優化
- 端到端測試
- 用戶接受測試
- 文檔完善
- 部署和監控

---

## 風險和緩解措施

### 技術風險

| 風險 | 影響 | 概率 | 緩解措施 |
|------|------|------|---------|
| **算法效果不佳** | 高 | 中 | A/B 測試不同參數、快速迭代機制、用戶反饋循環 |
| **性能瓶頸** | 中 | 中 | 異步處理、緩存機制、批量操作 |
| **數據不一致** | 高 | 低 | 事務處理、數據校驗、備份恢復 |
| **模型收斂慢** | 中 | 中 | 優化初始參數、熱啟動機制、預訓練模型 |

---

## 成功指標

### 定量指標

| 指標 | 目標值 | 測量方法 |
|------|--------|---------|
| **點擊率 (CTR)** | +15% vs 基線 | (偏好系統點擊 / 總展示) / 基線 CTR |
| **用戶滿意度** | > 70% | 用戶反饋調查 |
| **主題多樣性** | > 0.6 | 熵計算 |
| **響應時間** | < 200ms | 系統監控 |
| **模型收斂時間** | < 7 天 | 置信度達到 0.7 |
| **偏差檢測準確率** | > 80% | 人工審計 |
| **探索-利用平衡** | 85:15 | 探索結果占比 |

---

**文檔結束**
