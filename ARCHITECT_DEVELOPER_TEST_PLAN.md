# Architect & Developer Agent 測試計劃

> **測試目標：** 驗證新的 Architect 和 Developer sub-agent 能否協作完成 Dashboard 功能開發
> **測試場景：** 實現雙市場確認策略（Dual Market Confirm Strategy）
> **測試時間：** 2026-02-21（晚點執行）

---

## 📋 測試概述

### 測試任務
**功能描述：** 實現雙市場確認策略
- 結合台灣 Market Score（120MA 斜率）和美國 Market Score（20MA 斜率）
- 使用三態倉位控制（全倉/半倉/空倉）
- 遵循 Dashboard 現有架構模式

### 測試目標
1. ✅ Architect 能否正確分析現有架構
2. ✅ Architect 能否設計清晰的實現方案
3. ✅ Developer 能否按照設計正確實現
4. ✅ Developer 能否編寫完整的測試
5. ✅ Architect 能否進行有效的代碼審查
6. ✅ 協作流程是否順暢高效

---

## 🎬 測試流程

### 階段 1：架構分析（Architect）

**任務：** 分析 Dashboard 策略架構和相關服務

**輸入：**
```
TASK: 分析 Dashboard 策略系統架構，為雙市場確認策略的實現做準備

CONTEXT:
- 需求實現的功能：雙市場確認策略（結合 TW/US Market Score，三態倉位控制）
- Dashboard 路徑：/Users/charlie/.openclaw/workspace/Dashboard/backend/
- 相關文件：
  - IStrategy 接口：backend/services/strategies/core/interface.py
  - DualMomentumStrategy：backend/services/strategies/implementations/dual_momentum_strategy.py
  - MarketThermometerService：backend/services/market_thermometer_service.py

REQUIREMENTS:
1. 分析現有策略架構模式（IStrategy 接口、SignalAction、ExecutionContext 等）
2. 分析現有的高級策略實現（DualMomentumStrategy）
3. 分析 MarketThermometerService 的功能和用法
4. 分析數據流和服務依賴關係
5. 識別可重用的組件和需要新增的組件

輸出格式：
- 模塊架構分析
- 關鍵接口總結
- 數據流分析
- 可重用組件清單
- 技術債務識別（如有）

OUTPUT PATH: /Users/charlie/.openclaw/workspace/kanban/outputs/test-arch-001-analysis.md
```

**預期輸出：**
- `test-arch-001-analysis.md` - 架構分析報告

**驗收標準：**
- [ ] 正確識別了 IStrategy 接口和關鍵類型
- [ ] 理解了 DualMomentumStrategy 的實現模式
- [ ] 理解了 MarketThermometerService 的用法
- [ ] 識別了可重用的組件
- [ ] 輸出清晰易懂

---

### 階段 2：技術設計（Architect）

**任務：** 設計雙市場確認策略的實現方案

**輸入：**
```
TASK: 設計雙市場確認策略的完整實現方案

CONTEXT:
- 需求：結合台灣 Market Score（120MA 斜率）和美國 Market Score（20MA 斜率），使用三態倉位控制（全倉/半倉/空倉）
- 架構分析報告：/Users/charlie/.openclaw/workspace/kanban/outputs/test-arch-001-analysis.md

三態倉位邏輯：
- 全倉 (1.0): TW MS > 50 AND US MS > 50 AND 0050 > 120MA AND QQQ > 20MA
- 半倉 (0.5): 其他所有情況（過渡狀態）
- 空倉 (0.0): TW MS < 40 AND US MS < 40 AND 0050 < 120MA AND QQQ < 20MA

REQUIREMENTS:
1. 設計完整的技術方案（必須遵循現有架構模式）
2. 定義清晰的接口和類型
3. 設計數據流和依賴注入
4. 提供詳細的實現步驟
5. 定義驗收標準

輸出格式：
- 技術設計文檔（參考 skills/architect-agent/SKILL.md 中的格式）
- 接口定義
- 實現步驟（詳細到每個文件、每個方法）
- 測試方案
- 驗收標準

OUTPUT PATH: /Users/charlie/.openclaw/workspace/kanban/outputs/test-arch-002-design.md
```

**預期輸出：**
- `test-arch-002-design.md` - 技術設計文檔

**驗收標準：**
- [ ] 方案遵循現有架構模式
- [ ] 重用了現有服務（MarketThermometerService 等）
- [ ] 接口定義清晰
- [ ] 實現步驟詳細可執行
- [ ] 測試方案完整
- [ ] 驗收標準明確

---

### 階段 3：功能實現（Developer）

**任務：** 按照技術設計實現雙市場確認策略

**輸入：**
```
TASK: 實現雙市場確認策略

CONTEXT:
- 技術設計文檔：/Users/charlie/.openclaw/workspace/kanban/outputs/test-arch-002-design.md
- Dashboard 路徑：/Users/charlie/.openclaw/workspace/Dashboard/backend/

REQUIREMENTS:
1. 嚴格按照技術設計文檔實現（不擅自修改架構）
2. 編寫完整的單元測試和集成測試
3. 遵循代碼規範（參考 skills/developer-agent/SKILL.md）
4. 添加完整的類型註解和文檔字串
5. 運行所有測試並確保通過

輸出格式：
- 實現完成報告（參考 skills/developer-agent/SKILL.md 中的格式）
- 代碼文件清單
- 測試結果
- 驗收檢查清單

OUTPUT PATH: /Users/charlie/.openclaw/workspace/kanban/outputs/test-dev-001-implementation.md
```

**預期輸出：**
- `test-dev-001-implementation.md` - 實現完成報告
- `backend/services/strategies/implementations/dual_market_confirm_strategy.py` - 策略實現
- `backend/tests/strategies/test_dual_market_confirm_strategy.py` - 測試代碼

**驗收標準：**
- [ ] 所有文件正確創建
- [ ] 代碼嚴格遵循設計
- [ ] 測試覆蓋率 > 80%
- [ ] 所有測試通過
- [ ] 類型註解 100%
- [ ] 文檔字串 100%

---

### 階段 4：代碼審查（Architect）

**任務：** 審查 Developer 實現的代碼

**輸入：**
```
TASK: 審查雙市場確認策略的實現代碼

CONTEXT:
- 實現報告：/Users/charlie/.openclaw/workspace/kanban/outputs/test-dev-001-implementation.md
- 技術設計文檔：/Users/charlie/.openclaw/workspace/kanban/outputs/test-arch-002-design.md
- 實現文件：backend/services/strategies/implementations/dual_market_confirm_strategy.py
- 測試文件：backend/tests/strategies/test_dual_market_confirm_strategy.py

REQUIREMENTS:
1. 檢查代碼是否遵循技術設計
2. 檢查代碼是否符合架構規範
3. 檢查測試覆蓋率和測試品質
4. 檢查類型註解和文檔字串
5. 識別潛在問題和改進建議

輸出格式：
- 代碼審查報告（參考 skills/architect-agent/SKILL.md 中的格式）
- 問題清單（如有）
- 改進建議
- 審查結論（通過/需修復/建議改進）

OUTPUT PATH: /Users/charlie/.openclaw/workspace/kanban/outputs/test-arch-003-review.md
```

**預期輸出：**
- `test-arch-003-review.md` - 代碼審查報告

**驗收標準：**
- [ ] 審查全面徹底
- [ ] 問題清晰明確
- [ ] 建議具體可行
- [ ] 審查結論明確
- [ ] 無遺漏重大問題

---

### 階段 5：Bug 修復（Developer，如有需要）

**觸發條件：** Architect 審查發現必須修復的問題

**任務：** 修復 Architect 發現的問題

**輸入：**
```
TASK: 修復代碼審查發現的問題

CONTEXT:
- 代碼審查報告：/Users/charlie/.openclaw/workspace/kanban/outputs/test-arch-003-review.md

REQUIREMENTS:
1. 修復所有必須修復的問題
2. 添加相關測試（如需要）
3. 確保所有測試通過
4. 更新實現報告

輸出格式：
- 修復報告
- 測試結果

OUTPUT PATH: /Users/charlie/.openclaw/workspace/kanban/outputs/test-dev-002-fixes.md
```

**驗收標準：**
- [ ] 所有問題已修復
- [ ] 所有測試通過
- [ ] 代碼品質提升

---

## 📊 測試評估標準

### Architect Agent 評估

| 評估項目 | 優秀 | 合格 | 不合格 |
|---------|------|------|--------|
| 架構分析深度 | 全面深入，識別所有關鍵組件 | 基本完整，遺漏次要細節 | 分析不完整或有錯誤 |
| 設計方案質量 | 清晰可執行，完全遵循架構 | 基本可執行，有少量問題 | 不清晰或不符合架構 |
| 代碼審查能力 | 全面徹底，識別所有問題 | 基本完整，遺漏次要問題 | 審查不完整或有錯誤 |
| 文檔質量 | 清晰易懂，格式規範 | 基本清晰，格式基本規範 | 不清晰或格式混亂 |

### Developer Agent 評估

| 評估項目 | 優秀 | 合格 | 不合格 |
|---------|------|------|--------|
| 實現正確性 | 完全正確，嚴格遵循設計 | 基本正確，有少量偏差 | 有明顯錯誤或偏離設計 |
| 代碼規範遵循 | 100% 符合 | 基本符合，有少量問題 | 不符合規範 |
| 測試覆蓋率 | > 90% | 80% - 90% | < 80% |
| 類型註解 | 100% | 基本完整 | 不完整 |
| 文檔字串 | 100% | 基本完整 | 不完整 |

### 協作流程評估

| 評估項目 | 優秀 | 合格 | 不合格 |
|---------|------|------|--------|
| 溝通清晰度 | 信息完整，無需額外澄清 | 基本完整，偶需澄清 | 信息不完整，頻繁需要澄清 |
| 流程效率 | 無返工，一次性通過 | 少量返工，最終通過 | 多次返工，難以通過 |
| 整體質量 | 高品質，可直接上線 | 基本品質，需少量改進 | 低品質，需大量改進 |

---

## 🎯 測試成功標準

測試被認為成功，如果：
1. ✅ 所有 5 個階段都完成
2. ✅ Architect 和 Developer 的所有評估項目都達到「合格」或「優秀」
3. ✅ 協作流程評估達到「合格」或「優秀」
4. ✅ 最終實現的代碼通過所有測試
5. ✅ 整體流程在合理時間內完成（< 2 小時）

---

## 📝 測試記錄模板

```
## 測試執行記錄

### 測試時間
- 開始：2026-02-21 XX:XX GMT+8
- 結束：2026-02-21 XX:XX GMT+8
- 總時長：X 分鐘

### 階段執行記錄

#### 階段 1：架構分析
- Agent：architect
- 開始：XX:XX
- 結束：XX:XX
- 時長：X 分鐘
- 輸出：test-arch-001-analysis.md
- 狀態：✅ 成功 / ⚠️ 有問題 / ❌ 失敗
- 備註：...

#### 階段 2：技術設計
- Agent：architect
- 開始：XX:XX
- 結束：XX:XX
- 時長：X 分鐘
- 輸出：test-arch-002-design.md
- 狀態：✅ 成功 / ⚠️ 有問題 / ❌ 失敗
- 備註：...

#### 階段 3：功能實現
- Agent：developer
- 開始：XX:XX
- 結束：XX:XX
- 時長：X 分鐘
- 輸出：test-dev-001-implementation.md
- 狀態：✅ 成功 / ⚠️ 有問題 / ❌ 失敗
- 備註：...

#### 階段 4：代碼審查
- Agent：architect
- 開始：XX:XX
- 結束：XX:XX
- 時長：X 分鐘
- 輸出：test-arch-003-review.md
- 狀態：✅ 成功 / ⚠️ 有問題 / ❌ 失敗
- 備註：...

#### 階段 5：Bug 修復（如需要）
- Agent：developer
- 開始：XX:XX
- 結束：XX:XX
- 時長：X 分鐘
- 輸出：test-dev-002-fixes.md
- 狀態：✅ 成功 / ⚠️ 有問題 / ❌ 失敗
- 備註：...

### 評估結果

#### Architect Agent
- 架構分析深度：優秀 / 合格 / 不合格
- 設計方案質量：優秀 / 合格 / 不合格
- 代碼審查能力：優秀 / 合格 / 不合格
- 文檔質量：優秀 / 合格 / 不合格

#### Developer Agent
- 實現正確性：優秀 / 合格 / 不合格
- 代碼規範遵循：優秀 / 合格 / 不合格
- 測試覆蓋率：優秀 / 合格 / 不合格
- 類型註解：優秀 / 合格 / 不合格
- 文檔字串：優秀 / 合格 / 不合格

#### 協作流程
- 溝通清晰度：優秀 / 合格 / 不合格
- 流程效率：優秀 / 合格 / 不合格
- 整體質量：優秀 / 合格 / 不合格

### 總結
- 測試結果：✅ 成功 / ❌ 失敗
- 成功項目：X / 13
- 改進建議：
  1. ...
  2. ...

### 後續行動
- [ ] 更新 sub-agent 配置（如需要）
- [ ] 添加新的測試場景
- [ ] 優化協作流程
```

---

## 🔄 測試後優化

根據測試結果，可能需要：

### 如果測試失敗
1. 分析失敗原因
2. 更新 sub-agent 的系統提示詞
3. 調整工作流程
4. 重新測試

### 如果測試成功但發現問題
1. 記錄問題和改進建議
2. 更新技能文檔（SKILL.md）
3. 添加更多測試場景
4. 持續優化

---

**創建時間：** 2026-02-21 19:05 GMT+8
**預計執行時間：** 2026-02-21 晚點
**預計測試時長：** 90 - 120 分鐘
