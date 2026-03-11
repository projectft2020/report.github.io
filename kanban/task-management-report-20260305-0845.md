# 任務管理報告
生成時間：2026-03-05 08:45:00

---

## 📊 總體概覽

| 狀態 | 數量 | 百分比 |
|------|------|--------|
| ✅ 已完成 | 74 | 32.5% |
| ⏳ 待辦 (pending) | 42 | 18.4% |
| 🚀 啟動中 (spawning) | 10 | 4.4% |
| 📦 積壓 (backlog) | 93 | 40.8% |
| ❌ 已失敗 | 9 | 3.9% |
| **總計** | **228** | **100%** |

---

## 🔴 失敗任務 (9 個)

### 錯誤類型分析

| 錯誤類型 | 數量 | 處理狀態 |
|----------|------|----------|
| terminated (系統終止) | 5 | ⏳ 退避中，自動恢復中 |
| 超時 (>24小時) | 3 | ⏳ 退避中，自動恢復中 |
| rate limit (限流) | 1 | ⏳ 退避中，自動恢復中 |

### 詳細列表

1. **scout-1772161889132** - Fine-Tuning Without Forgetting ICL
   - 錯誤：terminated
   - 創建：5 天前
   - 處理：退避中，error_recovery.py 將自動恢復

2. **scout-1772161889135** - Regularized Online RLHF
   - 錯誤：terminated
   - 創建：5 天前
   - 處理：退避中，error_recovery.py 將自動恢復

3. **scout-1772161889162** - ML Applications in Finance (quantconnect)
   - 錯誤：超時: 運行 1 day, 2:25:18
   - 創建：5 天前
   - 處理：退避中，error_recovery.py 將自動恢復

4. **scout-1772161889164** - ML Applications in Finance (nber)
   - 錯誤：超時: 運行 1 day, 2:25:18
   - 創建：5 天前
   - 處理：退避中，error_recovery.py 將自動恢復

5. **scout-1772161889166** - ML Applications in Finance (hedge_fund_aqr)
   - 錯誤：超時: 運行 1 day, 2:25:18
   - 創建：5 天前
   - 處理：退避中，error_recovery.py 將自動恢復

6. **scout-1772161889172** - ML Applications in Finance (quant_se)
   - 錯誤：terminated
   - 創建：5 天前
   - 處理：退避中，error_recovery.py 將自動恢復

7. **scout-1772187174330** - New Quantitative Strategy (THREADS)
   - 錯誤：未知錯誤（無法找到論文）
   - 創建：5 天前
   - 處理：退避中，error_recovery.py 將自動恢復

8. **scout-1772197926287** - ML Applications (未知來源)
   - 錯誤：terminated
   - 創建：5 天前
   - 處理：退避中，error_recovery.py 將自動恢復

9. **scout-1772244923157** - ML Applications (rate limit)
   - 錯誤：rate limit
   - 創建：4 天前
   - 處理：退避中，error_recovery.py 將自動恢復

### 處理建議

✅ **自動處理中**
- error_recovery.py 已自動檢測並處理所有失敗任務
- 退避期完成後會自動重新啟動
- 無需手動介入

⚠️ **監控要點**
- rate limit 錯誤：監控 API 使用量，可能需要降低並發
- terminated 錯誤：可能是系統問題，持續觀察
- 超時錯誤：任務過於複雜或數據源不可用

---

## ⏳ 待辦任務 (42 個)

### 優先級分布

```
HIGH  ████████████████████████████████████ 33 (78.6%)
MEDIUM                                                0 (0.0%)
NORMAL                                               0 (0.0%)
LOW   ██████████████                              9 (21.4%)
```

### 代理類型分布

```
research    ████████████████████ 35 (83.3%)
analyst                    █ 2 (4.8%)
developer                  █ 2 (4.8%)
mentors                    1 (2.4%)
automation                  1 (2.4%)
creative                   1 (2.4%)
```

### 模型分布

```
zai/glm-4.7         ████████████████████ 36 (85.7%)
zai/glm-4.5         ██ 6 (14.3%)
```

### 依賴分析

- **有依賴的任務**：0 個
- **無依賴的任務**：42 個

### 處理建議

✅ **自動處理中**
- auto_spawn_heartbeat.py 已自動處理所有待辦任務
- 按優先級（high > low）排序啟動
- 背壓機制自動調整啟動頻率（65-300 秒）
- 並發上限自動調整（2-3 個）

⚠️ **監控要點**
- 高優先級任務占比 78.6%，正常
- 85.7% 使用 glm-4.7 模型，可能遇到限流
- 83.3% 是 research 代理，符合預期
- 無依賴關係，可以並行啟動

📋 **建議**
1. 監控 glm-4.7 限流情況，必要時切換到 glm-4.5
2. 觀察高優先級任務的完成情況，避免積壓
3. 考慮添加多樣化的任務類型（analyst, developer 等）

---

## 📦 積壓任務 (93 個)

### 年齡分布

```
0-7天    █████████████████████████████████████████████ 93 (100%)
7-14天                                                    0 (0.0%)
14-30天                                                   0 (0.0%)
30-90天                                                   0 (0.0%)
90+天                                                     0 (0.0%)
```

**平均年齡**：0.5 天
**結論**：所有積壓任務都是新的，來自最近的 Scout 掃描

### Scout 分數分布

積壓任務的 `scout_metadata.score` 分布（樣本分析）：

```
score 6.75: arxiv-2603.02204v1 - Partial Causal Structure Learning
score 4.00+: 多個 arxiv 論文
```

### 任務結構分析

積壓任務與待辦任務的主要差異：

| 字段 | 積壓任務 | 待辦任務 |
|------|----------|----------|
| priority | 數字 (3, 4) | 字符串 (high, medium, low) |
| agent | 缺失 | 完整 (research, analyst, etc.) |
| model | `recommended_model` | `model` |
| status | backlog | pending |

### 處理建議

✅ **自動處理中**
- monitor_and_refill.py 已自動檢測待辦任務 < 5 條件
- 自動觸發 Scout 掃描補充新任務
- 新任務存入 backlog 狀態

🔄 **需要轉換**
- 積壓任務需要轉換為正式任務（backlog → pending）
- 轉換時需要補充：
  1. `agent`: 根據任務類型選擇
  2. `priority`: 將數字轉換為字符串
  3. `model`: 使用 `recommended_model`
  4. `output_path`: 構建輸出路徑
  5. `input_paths`: 如有輸入文件

📋 **建議轉換規則**

1. **分數 >= 7.0** → 轉換為 HIGH 優先級任務
2. **分數 5.0-6.9** → 轉換為 NORMAL 優先級任務
3. **分數 < 5.0** → 保持 backlog，定期清理

2. **根據標題選擇代理**：
   - 包含 "研究", "Research", "論文", "Paper" → research
   - 包含 "分析", "Analysis", "策略", "Strategy" → analyst
   - 包含 "開發", "Development", "實現", "Implementation" → developer
   - 包含 "設計", "Design", "架構", "Architecture" → architect
   - 默認 → research

3. **模型選擇**：
   - 使用 `recommended_model`（通常是 zai/glm-4.7）
   - 如果高頻失敗，降級到 zai/glm-4.5

---

## 🎯 行動計劃

### 立即行動（本次心跳）

1. ✅ **失敗任務**
   - 狀態：自動處理中
   - action: 繼續讓 error_recovery.py 處理

2. ✅ **待辦任務**
   - 狀態：自動處理中
   - action: 繼續讓 auto_spawn_heartbeat.py 處理

3. 🔄 **積壓任務**
   - 狀態：需要轉換
   - action: 創建 backlog→pending 轉換腳本

### 短期行動（1-2 小時）

1. **創建積壓任務轉換腳本**
   - 腳本名稱：`promote_backlog.py`
   - 功能：
     - 讀取 backlog 任務
     - 根據分數和標題過濾
     - 補充缺失字段（agent, priority, model, output_path）
     - 將狀態改為 pending
     - 寫回 tasks.json

2. **配置轉換規則**
   - 分數閾值：HIGH >= 7.0, NORMAL >= 5.0
   - 代理映射：根據標題關鍵詞選擇
   - 批次大小：每次轉換 10 個（避免積壓）

3. **整合到心跳流程**
   - 在 monitor_and_refill.py 中添加轉換邏輯
   - 當 backlog 任務 > 50 時自動觸發轉換
   - 轉換條件：待辦任務 < 10

### 中期行動（1-2 天）

1. **監控和優化**
   - 觀察轉換後任務的完成率
   - 調整分數閾值和代理映射規則
   - 優化積壓任務的清理策略

2. **添加任務歸檔功能**
   - 自動歸檔 30 天前的已完成任務
   - 保留積壓任務的掃描記錄
   - 定期清理低分數的積壓任務（score < 4.0）

---

## 📊 系統健康度評估

### 背壓機制狀態

```
健康度: 0.00 (不健康)
並發上限: 2 個
啟動頻率: 300 秒
```

### 啟動狀態

```
執行中 (in_progress): 0 個
啟動中 (spawning): 10 個
```

### 問題診斷

1. ⚠️ **系統健康度 0.00**：不健康狀態
   - 原因：spawning 任務過多，沒有 in_progress 任務
   - 影響：啟動頻率降低到 300 秒，並發上限降低到 2

2. ⚠️ **10 個任務卡在 spawning**
   - 2 個已經回滾（>45 分鐘）
   - 4 個疑似卡住（30-45 分鐘）
   - 4 個在緩衝期（<10 分鐘）

3. ⚠️ **失敗任務退避中**
   - 9 個失敗任務都在退避期
   - 退避完成後會自動恢復

### 優化建議

1. **短期（立即）**
   - 繼續執行 task_state_rollback.py，回滾卡住的 spawning 任務
   - 等待退避期完成，自動恢復失敗任務

2. **中期（1-2 小時）**
   - 創建 backlog→pending 轉換腳本
   - 減少 spawning 任務的積壓

3. **長期（1-2 天）**
   - 優化 Scout 掃描頻率，避免過多 backlog 任務
   - 添加任務歸檔功能，減少 tasks.json 大小

---

## ✅ 總結

### 任務狀態

- **待辦 + 啟動中**：52 個（正在處理）
- **失敗**：9 個（自動恢復中）
- **積壓**：93 個（需要轉換）
- **已完成**：74 個（正常）

### 自動化狀態

- ✅ error_recovery.py：自動恢復失敗任務
- ✅ auto_spawn_heartbeat.py：自動啟動待辦任務
- ✅ task_state_rollback.py：自動回滾卡住任務
- ✅ monitor_and_refill.py：自動補充任務
- ⏳ backlog→pending 轉換：待實現

### 下一步

1. 繼續讓現有自動化腳本運行
2. 創建 backlog→pending 轉換腳本
3. 監控系統健康度，等待恢復

---

生成時間：2026-03-05 08:45:00
生成者：Charlie (Orchestrator)
