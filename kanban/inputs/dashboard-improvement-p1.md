# Dashboard Improvement Tasks - P1 (Short-term)

**Created:** 2026-03-05
**Priority:** P1 (Short-term improvements)
**Status:** Ready to assign

---

## Task 1: API 使用範例完善

### Overview
為 Dashboard Trading System v2.0 的所有 API 端點提供完整的使用範例，提升開發者體驗和文檔質量。

### Requirements
- 為每個 API 端點提供完整的請求/響應範例
- 涵蓋常見使用場景和邊界情況
- 整合到現有 API 文檔（http://localhost:8000/docs）
- 提供錯誤處理和最佳實踐指南

### Sub-tasks

#### 1.1 掃描現有 API 端點
- [ ] 使用 `curl http://localhost:8000/docs` 或 `curl http://localhost:8000/openapi.json` 獲取所有 API 端點
- [ ] 列出所有端點：路徑、方法、參數、響應格式
- [ ] 分類：策略相關、市場數據、系統操作、其他

#### 1.2 為每個端點撰寫完整範例
對於每個 API 端點，提供：
- [ ] 基本請求範例（使用 curl 和 Python requests）
- [ ] 完整的請求 body 範例（JSON 格式）
- [ ] 成功響應範例（實際輸出）
- [ ] 錯誤響應範例（常見錯誤代碼）
- [ ] 參數說明和可選值列表

#### 1.3 常見使用場景 Workflow
提供以下場景的完整 workflow：
- [ ] **場景 1：策略開發**
  - 創建策略模板 → 執行回測 → 查看結果 → 比較多個策略
- [ ] **場景 2：市場數據管理**
  - 回補市場數據 → 查詢股價數據 → 獲取市場篩選器結果
- [ ] **場景 3：系統監控**
  - 檢查系統健康 → 查看操作日誌 → 監控系統狀態
- [ ] **場景 4：Monte Carlo 分析**
  - 執行回測 → Monte Carlo 模擬 → 分析風險分佈

#### 1.4 錯誤處理和最佳實踐
- [ ] 列出常見錯誤代碼和處理建議
- [ ] 提供重試機制範例（exponential backoff）
- [ ] 認證最佳實踐（如何管理 Admin Token）
- [ ] 性能優化建議（批量請求、並發限制）

#### 1.5 整合到文檔
- [ ] 更新 Dashboard API 文檔（docs/api-endpoints.md 或類似）
- [ ] 在 Swagger/OpenAPI 文檔中添加示例
- [ ] 創建快速入門指南（Quick Start Guide）
- [ ] 提供 curl 和 Python 的即用範例代碼

### Deliverables
- [ ] API 端點清單（Markdown 格式）
- [ ] 每個端點的完整範例（JSON + curl + Python）
- [ ] 常見場景 Workflow 文檔（4 個場景）
- [ ] 錯誤處理指南（Markdown 格式）
- [ ] 更新後的 API 文檔（整合所有範例）

### Output Path
- `/Users/charlie/.openclaw/workspace/Dashboard/docs/api-examples.md`
- `/Users/charlie/.openclaw/workspace/Dashboard/docs/quick-start-guide.md`

---

## Task 2: 策略模板系統研究

### Overview
研究如何為 Dashboard Trading System 實現策略模板系統，支持快速創建常用策略，降低開發門檻。

### Requirements
- 分析常用策略類型並確定優先支持哪些
- 設計策略模板的數據結構和接口
- 評估實現難度和開發工作量
- 提供具體的實現建議和技術方案

### Sub-tasks

#### 2.1 分析常用策略類型
- [ ] 掃描現有策略模板（GET /api/strategies/templates）
- [ ] 列出當前支持的策略類型（rsi, macd, momentum, supertrend 等）
- [ ] 分析每種策略的核心參數和計算邏輯
- [ ] 調研量化交易常見策略類型：
  - 趨勢跟蹤類（雙均線、Supertrend、布林帶）
  - 震盪類（RSI、KDJ、CCI）
  - 動量類（MACD、KDJ、ROC）
  - 價值類（市盈率、市淨率）
  - 多因子類（基本面、技術面組合）

#### 2.2 設計策略模板結構
為策略模板設計數據結構，包括：
- [ ] 模板元數據（name, description, category, risk_level）
- [ ] 參數定義（parameter_name, type, default_value, range, description）
- [ ] 計算邏輯（使用什麼指標、計算公式）
- [ ] 信號生成規則（買入/賣出條件）
- [ ] 風控參數（止損、止盈、倉位管理）

設計建議：
```json
{
  "template_id": "supertrend-basic",
  "name": "Supertrend 趨勢策略",
  "category": "trend_following",
  "risk_level": "medium",
  "parameters": [
    {
      "name": "length",
      "type": "integer",
      "default": 10,
      "range": [1, 100],
      "description": "Supertrend 週期"
    },
    {
      "name": "multiplier",
      "type": "float",
      "default": 3.0,
      "range": [1.0, 5.0],
      "description": "ATR 倍數"
    }
  ],
  "signals": {
    "buy": "close > supertrend",
    "sell": "close < supertrend"
  },
  "risk_control": {
    "stop_loss_pct": 0.05,
    "take_profit_pct": 0.15,
    "position_size": "fixed_percent"
  }
}
```

#### 2.3 評估實現難度
評估以下方面的實現難度：
- [ ] **後端實現**：
  - 模板存儲（數據庫 vs 文件系統）
  - 模板解析和參數驗證
  - 策略實例化（從模板到可執行策略）
- [ ] **前端實現**：
  - 模板選擇和參數配置 UI
  - 實時預覽和驗證
  - 一鍵啟動回測
- [ ] **兼容性**：
  - 與現有回測系統的整合
  - 與現有策略代碼的兼容性
  - 向後兼容性（如何遷移現有策略）

估計開發工作量：
- [ ] 後端開發：X 人天
- [ ] 前端開發：X 人天
- [ ] 測試和文檔：X 人天
- [ ] 總計：X 人天

#### 2.4 提供實現建議
提供具體的技術方案：
- [ ] **推薦技術方案**：
  - 模板存儲：JSON 文件 / SQLite / PostgreSQL？
  - 策略實例化：Python 工廠模式 / 動態代碼生成？
  - 參數驗證：Pydantic / 自定義驗證器？
- [ ] **實現優先級**：
  - Phase 1：支持 3-5 個最常用模板（Supertrend、雙均線、RSI、MACD）
  - Phase 2：支持自定義參數範圍和默認值
  - Phase 3：支持模板組合和多策略混合
- [ ] **潛在風險和緩解措施**：
  - 策略過度優化：如何避免？
  - 參數爆炸：如何管理？
  - 性能問題：如何優化？

### Deliverables
- [ ] 常用策略類型分析報告（Markdown 格式）
- [ ] 策略模板數據結構設計（JSON Schema + 範例）
- [ ] 實現難度評估報告（工作量估算、技術風險）
- [ ] 實現建議和技術方案（Markdown 格式）
- [ ] Phase 1 實現路線圖（3-5 個常用模板）

### Output Path
- `/Users/charlie/.openclaw/workspace/Dashboard/docs/strategy-template-research.md`
- `/Users/charlie/.openclaw/workspace/Dashboard/docs/strategy-template-design.json`

---

## Notes for Agent

### Agent Selection
- **Task 1 (API 範例完善)**: `automation` agent (GLM-4.5) - 文檔和範例編寫
- **Task 2 (策略模板研究)**: `analyst` agent (GLM-4.7) - 需要深度分析和設計

### Execution Order
1. 先完成 Task 1（API 範例完善）- 相對簡單，可立即交付價值
2. 再完成 Task 2（策略模板研究）- 需要更多時間和分析

### Prerequisites
- Dashboard 服務必須運行（http://localhost:8000 可訪問）
- Admin Token 已知：`admin995`

### Success Criteria
- **Task 1**: 所有 API 端點都有完整範例，文檔可直接使用
- **Task 2**: 有明確的實現路線圖，技術方案可落地執行

---

## Questions for Agent
如果遇到以下情況，請：
1. **無法訪問 API 文檔**：嘗試重啟 Dashboard 服務，或詢問用戶
2. **發現 API 端點不一致**：記錄問題並報告給用戶
3. **策略模板設計有爭議**：提供多個方案供用戶選擇
4. **實現工作量估算困難**：基於類似項目經驗估算，並說明不確定性

---

**End of Requirements**
