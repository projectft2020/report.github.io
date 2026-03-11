# Scout Phase 2 - 爬文類型數據源實施計劃

**版本**: v1.0
**日期**: 2026-02-23
**策略**: 優先實現爬文類型數據源，跳過 API key/OAuth

---

## 🎯 實施策略

### 選擇標準

**實現** ✅：
- 使用 web_reader MCP tool
- 無需 API key 或 OAuth
- 可通過 HTTP 請求獲取數據

**跳過** ❌：
- 需要 OAuth 配置（Reddit）
- 需要 API key（GitHub API、Kaggle API）
- 需要應用註冊

---

## 📋 爬文類型數據源清單

### 🔴 Phase 2.1-W - HIGH 優先級（立即實現）

| 數據源 | 掃描方法 | 掃描頻率 | 可靠性 | 時間估算 |
|--------|---------|---------|--------|---------|
| **Threads** | web_reader | 2 小時 | 0.70 | 1.5 小時 |
| **Quantocracy** | web_reader | 2 小時 | 0.90 | 1.5 小時 |
| **QuantConnect** | web_reader | 3 小時 | 0.85 | 1.5 小時 |
| **Nuclear Phynance** | web_reader | 4 小時 | 0.85 | 1 小時 |
| **QuantNet** | web_reader | 4 小時 | 0.80 | 1 小時 |

**小計**：6.5 小時

---

### 🟡 Phase 2.2-W - MEDIUM-HIGH 優先級（本週實現）

| 數據源 | 掃描方法 | 掃描頻率 | 可靠性 | 時間估算 |
|--------|---------|---------|--------|---------|
| **SSRN** | web_reader | 4 小時 | 0.90 | 1.5 小時 |
| **NBER** | web_reader | 8 小時 | 0.95 | 1.5 小時 |
| **Hedge Fund Reports** | web_reader | 12 小時 | 0.95 | 2 小時 |
| **TradingView Community** | web_reader | 4 小時 | 0.80 | 1.5 小時 |
| **QuantStackExchange** | web_reader | 6 小時 | 0.90 | 1 小時 |

**小計**：7.5 小時

---

### 🟢 Phase 2.3-W - MEDIUM 優先級（下週實現）

| 數據源 | 掃描方法 | 掃描頻率 | 可靠性 | 時間估算 |
|--------|---------|---------|--------|---------|
| **券商量化報告** | web_reader | 12 小時 | 0.90 | 2 小時 |
| **Fintech Media** | web_reader | 6 小時 | 0.80 | 1.5 小時 |

**小計**：3.5 小時

---

### 🔵 跳過（需要 API/OAuth）

| 數據源 | 原因 | 時間估算 |
|--------|------|---------|
| **Reddit** | 需要 OAuth 配置 | 1 小時（暫跳過） |
| **GitHub** | 需要 API key | 1.5 小時（暫跳過） |
| **Kaggle** | 需要 API key | 1 小時（暫跳過） |

**跳過合計**：3.5 小時

---

## 🛠 實現方案

### 通用爬文掃描器設計

```python
def scan_web_source(self, source_config: Dict) -> List[Dict]:
    """
    通用網頁掃描器

    功能：
    - 使用 web_reader MCP tool
    - 根據配置提取數據
    - 應用過濾條件
    - 返回標準化主題列表
    """
    # 1. 使用 web_reader 獲取網頁內容
    # 2. 解析 HTML 提取主題
    # 3. 應用過濾條件
    # 4. 返回標準化結果
```

**配置格式**：
```json
{
  "source_id": "quantocracy",
  "source_name": "Quantocracy",
  "base_url": "https://quantocracy.com/",
  "scan_frequency_hours": 2,
  "reliability": 0.90,
  "selector": {
    "posts": ".post-item",
    "title": ".post-title",
    "description": ".post-excerpt",
    "url": "a",
    "published_at": ".post-date"
  },
  "filters": {
    "min_engagement": 5,
    "max_age_hours": 48,
    "exclude_keywords": ["job", "hiring", "apply"]
  }
}
```

---

### 詳細實現計劃

#### 1. Threads 掃描器

**配置**：
```json
{
  "source_id": "threads",
  "source_name": "Threads",
  "base_url": "https://www.threads.com/",
  "accounts": ["@top3pct"],
  "scan_frequency_hours": 2,
  "reliability": 0.70,
  "filters": {
    "min_engagement": 10,
    "max_age_hours": 24,
    "keywords": ["trading", "strategy", "quant", "algorithm"]
  }
}
```

**實現步驟**：
1. 使用 web_reader 訪問帳號頁面
2. 提取貼文標題和內容
3. 獲取互動數據（likes, comments）
4. 應用關鍵詞和互動過濾
5. 返回標準化主題

**時間估算**：1.5 小時

---

#### 2. Quantocracy 掃描器

**配置**：
```json
{
  "source_id": "quantocracy",
  "source_name": "Quantocracy",
  "base_url": "https://quantocracy.com/",
  "url": "https://quantocracy.com/",
  "scan_frequency_hours": 2,
  "reliability": 0.90,
  "selector": {
    "posts": ".post-item",
    "title": ".post-title",
    "description": ".post-excerpt",
    "url": "a"
  },
  "filters": {
    "min_engagement": 5,
    "max_age_hours": 48
  }
}
```

**實現步驟**：
1. 使用 web_reader 訪問首頁
2. 提取日誌聚合貼文
3. 獲取標題、摘要、URL
4. 過濾低品質內容
5. 返回標準化主題

**時間估算**：1.5 小時

---

#### 3. QuantConnect 掃描器

**配置**：
```json
{
  "source_id": "quantconnect",
  "source_name": "QuantConnect",
  "base_url": "https://www.quantconnect.com/forum",
  "url": "https://www.quantconnect.com/forum",
  "scan_frequency_hours": 3,
  "reliability": 0.85,
  "selector": {
    "posts": ".forum-post",
    "title": ".post-title",
    "description": ".post-content",
    "url": "a"
  },
  "filters": {
    "min_replies": 5,
    "max_age_hours": 48,
    "exclude_categories": ["help", "getting started"]
  }
}
```

**實現步驟**：
1. 使用 web_reader 訪問論壇
2. 提取策略討論貼文
3. 獲取回覆數和內容
4. 過濾基礎問題和幫助貼文
5. 返回標準化主題

**時間估算**：1.5 小時

---

#### 4. Nuclear Phynance 掃描器

**配置**：
```json
{
  "source_id": "nuclearphynance",
  "source_name": "Nuclear Phynance",
  "base_url": "https://nuclearphynance.com/",
  "url": "https://nuclearphynance.com/",
  "scan_frequency_hours": 4,
  "reliability": 0.85,
  "filters": {
    "min_replies": 3,
    "max_age_hours": 48,
    "required_keywords": ["quant", "finance", "math"]
  }
}
```

**實現步驟**：
1. 使用 web_reader 訪問論壇
2. 提取高級量化討論
3. 過濾基礎問題
4. 返回標準化主題

**時間估算**：1 小時

---

#### 5. QuantNet 掃描器

**配置**：
```json
{
  "source_id": "quantnet",
  "source_name": "QuantNet",
  "base_url": "https://www.quantnet.com/",
  "url": "https://www.quantnet.com/",
  "scan_frequency_hours": 4,
  "reliability": 0.80,
  "filters": {
    "min_replies": 5,
    "max_age_hours": 48,
    "exclude_categories": ["career", "job", "salary"]
  }
}
```

**實現步驟**：
1. 使用 web_reader 訪問論壇
2. 提取量化教育和職業討論
3. 過濾求職和薪資貼文
4. 返回標準化主題

**時間估算**：1 小時

---

#### 6. SSRN 掃描器

**配置**：
```json
{
  "source_id": "ssrn",
  "source_name": "SSRN",
  "base_url": "https://www.ssrn.com/",
  "categories": ["Financial Economics", "Econometrics", "Asset Pricing"],
  "scan_frequency_hours": 4,
  "reliability": 0.90,
  "filters": {
    "min_downloads": 100,
    "max_age_days": 30,
    "has_abstract": true
  }
}
```

**實現步驟**：
1. 使用 web_reader 訪問分類頁面
2. 提取工作論文標題和摘要
3. 獲取下載數和發布日期
4. 過濾低品質論文
5. 返回標準化主題

**時間估算**：1.5 小時

---

#### 7. NBER 掃描器

**配置**：
```json
{
  "source_id": "nber",
  "source_name": "NBER",
  "base_url": "https://www.nber.org/",
  "categories": ["economics", "monetary policy", "market analysis"],
  "scan_frequency_hours": 8,
  "reliability": 0.95,
  "filters": {
    "max_age_months": 6,
    "has_abstract": true
  }
}
```

**實現步驟**：
1. 使用 web_reader 訪問工作論文頁面
2. 提取經濟研究標題和摘要
3. 過濾舊論文
4. 返回標準化主題

**時間估算**：1.5 小時

---

#### 8. Hedge Fund Reports 掃描器

**配置**：
```json
{
  "source_id": "hedge_funds",
  "source_name": "Hedge Fund Reports",
  "sources": [
    {"name": "AQR", "url": "https://www.aqr.com/Insights/Research"},
    {"name": "Two Sigma", "url": "https://www.twosigma.com/articles"},
    {"name": "Citadel", "url": "https://www.citadel.com/insights"},
    {"name": "Man AHL", "url": "https://www.man.com/manahl/our-thinking"}
  ],
  "scan_frequency_hours": 12,
  "reliability": 0.95,
  "filters": {
    "max_age_days": 30,
    "required_keywords": ["quantitative", "factor", "portfolio", "risk"]
  }
}
```

**實現步驟**：
1. 使用 web_reader 訪問每個對沖基金的研究頁面
2. 提取研究報告標題和摘要
3. 獲取發布日期
4. 過濾非量化內容
5. 返回標準化主題

**時間估算**：2 小時

---

#### 9. TradingView Community 掃描器

**配置**：
```json
{
  "source_id": "tradingview",
  "source_name": "TradingView Community",
  "base_url": "https://www.tradingview.com/scripts/",
  "url": "https://www.tradingview.com/scripts/",
  "scan_frequency_hours": 4,
  "reliability": 0.80,
  "filters": {
    "min_stars": 50,
    "min_comments": 10,
    "max_age_months": 6
  }
}
```

**實現步驟**：
1. 使用 web_reader 訪問策略腳本頁面
2. 提取 Pine Script 策略
3. 獲取 stars 和 comments
4. 過濾低品質策略
5. 返回標準化主題

**時間估算**：1.5 小時

---

#### 10. QuantStackExchange 掃描器

**配置**：
```json
{
  "source_id": "quant_se",
  "source_name": "QuantStackExchange",
  "base_url": "https://quant.stackexchange.com/",
  "url": "https://quant.stackexchange.com/questions",
  "scan_frequency_hours": 6,
  "reliability": 0.90,
  "filters": {
    "min_score": 5,
    "has_answer": true,
    "max_age_days": 30
  }
}
```

**實現步驟**：
1. 使用 web_reader 訪問問答頁面
2. 提取已回答的問題
3. 獲取分數和答案
4. 過濾低分問題
5. 返回標準化主題

**時間估算**：1 小時

---

#### 11. 券商量化報告掃描器

**配置**：
```json
{
  "source_id": "brokerage_reports",
  "source_name": "Brokerage Quant Reports",
  "sources": [
    {"name": "Goldman Sachs", "url": "https://www.goldmansachs.com/insights/pages/macro-research.html"},
    {"name": "Morgan Stanley", "url": "https://www.morganstanley.com/ideas/quantitative-strategies"},
    {"name": "UBS", "url": "https://www.ubs.com/global/en/wealth-management/insights.html"},
    {"name": "J.P. Morgan", "url": "https://www.jpmorgan.com/insights/quantitative-solutions"}
  ],
  "scan_frequency_hours": 12,
  "reliability": 0.90,
  "filters": {
    "max_age_days": 30,
    "required_keywords": ["quantitative", "factor", "portfolio", "risk management"]
  }
}
```

**實現步驟**：
1. 使用 web_reader 訪問每個券商的研究頁面
2. 提取量化策略報告
3. 過濾通用市場評論
4. 返回標準化主題

**時間估算**：2 小時

---

#### 12. Fintech Media 掃描器

**配置**：
```json
{
  "source_id": "fintech_media",
  "source_name": "Fintech Media",
  "sources": [
    {"name": "QuantNews", "url": "https://www.quantnews.com/"},
    {"name": "FINRA", "url": "https://www.finra.org/"},
    {"name": "CFA Institute", "url": "https://www.cfainstitute.org/research-foundation"}
  ],
  "scan_frequency_hours": 6,
  "reliability": 0.80,
  "filters": {
    "max_age_days": 7,
    "required_keywords": ["quantitative", "algorithm", "trading", "strategy"]
  }
}
```

**實現步驟**：
1. 使用 web_reader 訪問每個媒體網站
2. 提取量化相關文章
3. 過濾非量化內容
4. 返回標準化主題

**時間估算**：1.5 小時

---

## 📅 實施時間表

### Phase 2.1-W - HIGH 優先級（今天）

| 任務 | 時間估算 | 累計時間 |
|------|---------|---------|
| Threads 掃描器 | 1.5 小時 | 1.5h |
| Quantocracy 掃描器 | 1.5 小時 | 3h |
| QuantConnect 掃描器 | 1.5 小時 | 4.5h |
| Nuclear Phynance 掃描器 | 1 小時 | 5.5h |
| QuantNet 掃描器 | 1 小時 | 6.5h |

**預計完成時間**：6.5 小時（1 天）

---

### Phase 2.2-W - MEDIUM-HIGH 優先級（本週）

| 任務 | 時間估算 | 累計時間 |
|------|---------|---------|
| SSRN 掃描器 | 1.5 小時 | 1.5h |
| NBER 掃描器 | 1.5 小時 | 3h |
| Hedge Fund Reports 掃描器 | 2 小時 | 5h |
| TradingView Community 掃描器 | 1.5 小時 | 6.5h |
| QuantStackExchange 掃描器 | 1 小時 | 7.5h |

**預計完成時間**：7.5 小時（2 天）

---

### Phase 2.3-W - MEDIUM 優先級（下週）

| 任務 | 時間估算 | 累計時間 |
|------|---------|---------|
| 券商量化報告掃描器 | 2 小時 | 2h |
| Fintech Media 掃描器 | 1.5 小時 | 3.5h |

**預計完成時間**：3.5 小時（1 天）

---

## 🎯 成功指標

### Phase 2.1-W 指標

- ✅ 實現 5 個爬文掃描器
- ✅ 每天掃描 50+ 個主題
- ✅ 去重效率 >= 90%
- ✅ 測試通過率 100%

### Phase 2.2-W 指標

- ✅ 實現 5 個爬文掃描器
- ✅ 每天掃描 100+ 個主題
- ✅ 高品質任務比例 >= 60%
- ✅ 系統響應時間 < 5 秒

### Phase 2.3-W 指標

- ✅ 實現 2 個爬文掃描器
- ✅ 每天掃描 150+ 個主題
- ✅ 數據源覆蓋率 100%（跳過 API/OAuth）
- ✅ 系統穩定性 >= 99%

---

## 🚧 風險和緩解措施

### 技術風險

| 風險 | 影響 | 概率 | 緩解措施 |
|------|------|------|---------|
| web_reader 不穩定 | 高 | 中 | 實現錯誤處理、重試機制、降級策略 |
| 網站結構變化 | 中 | 低 | 定期檢查、更新選擇器、版本控制 |
| 反爬蟲機制 | 中 | 中 | 尊重速率限制、使用瀏覽器 User-Agent |
| 數據提取困難 | 中 | 中 | 使用多種選擇器、備用解析方案 |

### 資源風險

| 風險 | 影響 | 概率 | 緩解措施 |
|------|------|------|---------|
| 開發時間超預算 | 中 | 中 | 優先實現高價值功能、分階段交付 |
| web_reader 調用次數限制 | 中 | 低 | 實現智能緩存、批量處理 |
| 網站訪問頻率限制 | 低 | 低 | 尊重掃描頻率、使用隨機延遲 |

---

## 📋 檢查清單

### Phase 2.1-W 檢查清單

- [ ] 實現通用 web_reader 掃描器框架
- [ ] 實現 Threads 掃描器
- [ ] 測試 Threads 掃描（返回真實數據）
- [ ] 實現 Quantocracy 掃描器
- [ ] 測試 Quantocracy 掃描
- [ ] 實現 QuantConnect 掃描器
- [ ] 測試 QuantConnect 掃描
- [ ] 實現 Nuclear Phynance 掃描器
- [ ] 測試 Nuclear Phynance 掃描
- [ ] 實現 QuantNet 掃描器
- [ ] 測試 QuantNet 掃描
- [ ] 完整測試和文檔

### Phase 2.2-W 檢查清單

- [ ] 實現 SSRN 掃描器
- [ ] 測試 SSRN 掃描
- [ ] 實現 NBER 掃描器
- [ ] 測試 NBER 掃描
- [ ] 實現 Hedge Fund Reports 掃描器
- [ ] 測試 Hedge Fund Reports 掃描
- [ ] 實現 TradingView Community 掃描器
- [ ] 測試 TradingView 掃描
- [ ] 實現 QuantStackExchange 掃描器
- [ ] 測試 QuantStackExchange 掃描
- [ ] 完整測試和文檔

### Phase 2.3-W 檢查清單

- [ ] 實現券商量化報告掃描器
- [ ] 測試券商報告掃描
- [ ] 實現 Fintech Media 掃描器
- [ ] 測試 Fintech Media 掃描
- [ ] 完整測試和文檔

---

## 📝 結論

本計劃專注於**爬文類型數據源**，無需 API key 或 OAuth 配置，可以立即開始實現。

**優勢**：
- ✅ 無需外部配置
- ✅ 快速實現
- ✅ 易於測試
- ✅ 立即可用

**總時間估算**：
- Phase 2.1-W：6.5 小時（1 天）
- Phase 2.2-W：7.5 小時（2 天）
- Phase 2.3-W：3.5 小時（1 天）
- **總計**：17.5 小時（4 天）

**數據源覆蓋率**：12 個爬文數據源，跳過 3 個 API/OAuth 數據源

---

**計劃制定**: Scout System Enhancement Team
**最終更新**: 2026-02-23 04:20 GMT+8
