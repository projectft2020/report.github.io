# Scout Phase 2 擴展計劃：數據源 + 高級學習

**項目**: Scout Phase 2 擴展  
**日期**: 2026-02-23  
**預估時間**: 2-3 週（分階段實施）  
**狀態**: 📋 計劃中

---

## 📋 執行摘要

Phase 2 將擴展 Scout 系統的數據源和學習能力，從單一 arXiv 掃描擴展到 **9 個類別、25+ 個數據源**，並實現基於用戶反饋的自適應學習系統。

**核心目標：**
- ✅ 擴展至 9 個數據源類別
- ✅ 實現用戶反饋收集系統
- ✅ 實現動態權重調整機制
- ✅ 提升 Scout 推薦品質 30%+

---

## 🎯 擴展數據源

### 優先級分類

#### 🔴 Phase 2.1 - HIGH 優先級（立即實現）

**目標**：實現高價值、高頻率掃描的數據源

##### 1. Reddit API 掃描器（需要 OAuth 配置）

**狀態**: ⚠️ 基礎框架已存在，需要 OAuth 配置

**功能需求：**
- 掃描 r/quant、r/algotrading、r/numerical、r/MachineLearning
- 過濾條件：upvotes >= 10, comments >= 5
- 時間過濾：最近 48 小時
- 排除：基礎問題、求職貼文

**實現步驟：**
```bash
# 1. 配置 Reddit OAuth
# 訪問 https://www.reddit.com/prefs/apps
# 創建應用，獲取 client_id 和 client_secret

# 2. 更新 scout_agent.py
# 配置 praw.Reddit() 實例

# 3. 測試掃描
python3 scout_agent.py reddit
```

**配置文件** (`~/.openclaw/workspace-scout/reddit_config.json`):
```json
{
  "client_id": "YOUR_CLIENT_ID",
  "client_secret": "YOUR_CLIENT_SECRET",
  "user_agent": "ScoutAgent/1.0 by OpenClaw",
  "subreddits": ["quant", "algotrading", "numerical", "MachineLearning"],
  "min_upvotes": 10,
  "min_comments": 5,
  "max_age_hours": 48
}
```

**時間估算**: 1 小時

**API 限制**: 60 requests/minute

---

##### 2. Threads 掃描器（使用 web_reader）

**狀態**: ❌ 未實現

**功能需求：**
- 監控 @top3pct（用戶推薦）
- 掃描貼文：每 2 小時
- 提取：標題、內容、互動數據
- 過濾：技術深度、量化相關

**實現步驟：**
```python
def scan_threads(self, accounts=None, max_results=10):
    """
    掃描 Threads 貼文

    功能：
    - 使用 web_reader MCP tool
    - 提取貼文標題和內容
    - 獲取互動數據（likes, comments）
    - 過濾量化相關貼文
    """
```

**監控帳戶**：
- @top3pct（優先）
- 專業量化交易者帳號（待擴展）

**時間估算**: 1.5 小時

**掃描頻率**: 每 2 小時

---

##### 3. Professional Quant Communities（網頁抓取）

**狀態**: ❌ 未實現

**功能需求：**
- Quantocracy（每 2 小時）
- QuantConnect（每 3 小時）
- Nuclear Phynance（每 4 小時）
- QuantNet（每 4 小時）

**選擇條件**：
- 深度討論（replies >= 5）
- 專業語氣和技術深度
- 最近 48 小時內發布
- 排除：基礎問題、求職廣告

**實現步驟：**
```python
def scan_quant_communities(self, source=None, max_results=10):
    """
    掃描專業量化社群

    功能：
    - 使用 web_reader MCP tool
    - 提取高品質貼文
    - 過濾專業內容
    - 統計互動數據
    """
```

**時間估算**: 2 小時

**可靠性**: Quantocracy (0.90)、QuantConnect (0.85)、Nuclear Phynance (0.85)、QuantNet (0.80)

---

#### 🟡 Phase 2.2 - MEDIUM-HIGH 優先級（本週實現）

**目標**：實現高質量學術和行業研究來源

##### 1. SSRN（Social Science Research Network）

**狀態**: ❌ 未實現

**功能需求：**
- 專注：Financial Economics、Econometrics、Asset Pricing
- 品質：同行評審工作論文
- 選擇：downloads >= 100、最近上傳

**實現步驟：**
```python
def scan_ssrn(self, categories=None, max_results=20):
    """
    掃描 SSRN 研究論文

    功能：
    - 使用 web_reader MCP tool
    - 提取工作論文摘要
    - 過濾金融相關研究
    - 統計下載數量
    """
```

**時間估算**: 1.5 小時

**掃描頻率**: 每 4 小時

**可靠性**: 0.90

---

##### 2. NBER（National Bureau of Economic Research）

**狀態**: ❌ 未實現

**功能需求：**
- 專注：經濟研究、貨幣政策、市場分析
- 品質：頂級經濟學研究
- 選擇：最近工作論文

**時間估算**: 1.5 小時

**掃描頻率**: 每 8 小時

**可靠性**: 0.95

---

##### 3. Hedge Fund Research Reports

**狀態**: ❌ 未實現

**功能需求：**
- AQR Capital Management
- Two Sigma
- Citadel
- Man AHL

**選擇條件**：
- 最近發布（30 天內）
- 關鍵詞：quantitative、factor、portfolio、risk management
- 排除：通用市場評論

**時間估算**: 2 小時

**掃描頻率**: 每 12 小時

**可靠性**: 0.95

---

#### 🟢 Phase 2.3 - MEDIUM 優先級（下週實現）

**目標**：實現實用工具和數據平台

##### 1. GitHub（開源量化專案）

**狀態**: ❌ 未實現

**功能需求：**
- 搜索查詢：
  - "quantitative trading" stars:>100
  - "backtesting framework" stars:>50
  - "portfolio optimization" stars:>50
- 選擇條件：
  - Stars >= 50
  - 最近 6 個月內有 commit
  - 活躍維護

**實現步驟：**
```python
def scan_github(self, queries=None, max_results=10):
    """
    掃描 GitHub 開源專案

    功能：
    - 使用 GitHub API
    - 搜索量化相關專案
    - 過濾高品質專案
    - 統計活躍度
    """
```

**時間估算**: 1.5 小時

**掃描頻率**: 每 6 小時

**可靠性**: 0.85

---

##### 2. Kaggle（金融數據集和競賽）

**狀態**: ❌ 未實現

**功能需求：**
- Notebook kernels
- 數據集
- 競賽解決方案

**選擇條件**：
- Upvotes >= 10
- 最近活躍

**時間估算**: 1 小時

**掃描頻率**: 每 6 小時

**可靠性**: 0.85

---

##### 3. TradingView Community

**狀態**: ❌ 未實現

**功能需求：**
- Pine Script 策略分享
- 策略代碼、指標、回測結果

**選擇條件**：
- Stars >= 50
- Comments >= 10

**時間估算**: 1.5 小時

**掃描頻率**: 每 4 小時

**可靠性**: 0.80

---

#### 🔵 Phase 2.4 - LOW-MEDIUM 優先級（未來擴展）

**目標**：實現新聞媒體和券商研究報告

##### 1. 券商量化報告

**來源**：
- Goldman Sachs Quantitative Strategies
- Morgan Stanley Quantitative Strategies
- UBS Wealth Management Research
- J.P. Morgan Quantitative Strategies

**選擇條件**：
- 最近發布（30 天內）
- 關鍵詞：quantitative、factor、portfolio、risk management

**時間估算**: 2 小時

**掃描頻率**: 每 12 小時

**可靠性**: 0.90

---

##### 2. Fintech Media

**來源**：
- QuantNews
- FINRA
- CFA Institute Research Foundation

**時間估算**: 1.5 小時

**掃描頻率**: 每 6 小時

**可靠性**: 0.80

---

##### 3. 新聞媒體（RSS）

**來源**：
- Bloomberg Markets
- Reuters Business News
- Financial Times
- Wall Street Journal

**選擇條件**：
- 最近 24 小時
- 關鍵詞：quantitative、algorithmic、trading、strategy、research
- 排除：收益報告、通用市場新聞

**時間估算**: 1 小時

**掃描頻率**: 每 6 小時

**可靠性**: 0.75

---

## 🧠 高級學習功能

### 1. 用戶反饋整合系統

**目標**：收集用戶對 Scout 推薦任務的反饋，持續改進推薦品質

#### 1.1 反饋收集機制

**反饋類型**：

1. **任務品質評分**（1-5 分）
   - 1 分：不推薦，浪費時間
   - 2 分：品質較差，有問題
   - 3 分：品質一般，可以接受
   - 4 分：品質良好，有價值
   - 5 分：優秀，非常推薦

2. **反饋類別**
   - 內容過於基礎
   - 內容過於複雜
   - 數據不足
   - 實現困難
   - 與興趣不符
   - 其他（自由輸入）

3. **自由文字反饋**
   - 用戶可以添加詳細評論
   - 記錄學習點和改進建議

**實現方案**：

```python
class FeedbackCollector:
    """用戶反饋收集器"""

    def __init__(self):
        self.feedback_file = FEEDBACK_FILE
        self.feedback = self._load_feedback()

    def submit_feedback(self, task_id: str, rating: int, category: str = None, comment: str = None):
        """
        提交任務反饋

        參數：
        - task_id: 任務 ID
        - rating: 評分 (1-5)
        - category: 反饋類別（可選）
        - comment: 自由評論（可選）
        """
        feedback_entry = {
            "task_id": task_id,
            "rating": rating,
            "category": category,
            "comment": comment,
            "timestamp": datetime.now().isoformat()
        }

        # 記錄反饋
        self.feedback.append(feedback_entry)
        self._save_feedback()

        # 觸發學習
        self._trigger_learning(feedback_entry)

        return {"status": "success", "feedback_id": feedback_entry["feedback_id"]}
```

**反饋文件格式** (`~/.openclaw/workspace-scout/feedback.json`):
```json
{
  "feedbacks": [
    {
      "feedback_id": "fb-1771789500000",
      "task_id": "scout-1771789383872",
      "rating": 4,
      "category": "品質良好，有價值",
      "comment": "論文很有深度的研究，建議提前數學基礎要求",
      "timestamp": "2026-02-23T04:00:00Z",
      "task_metadata": {
        "title": "Neural Tangent Kernel Analysis",
        "score": 6.06,
        "source": "arxiv"
      }
    }
  ]
}
```

**命令行介面**：
```bash
# 提交反饋
python3 scout_agent.py feedback <task_id> <rating> [category] [comment]

# 示例
python3 scout_agent.py feedback scout-1771789383872 4 "品質良好，有價值" "論文很有深度的研究"

# 查看反饋統計
python3 scout_agent.py feedback-stats
```

**時間估算**: 2 小時

---

#### 1.2 反饋分析引擎

**目標**：分析反饋數據，提取洞察，改進推薦系統

**分析指標**：

1. **整體品質指標**
   - 平均評分
   - 評分分佈
   - 高品質任務比例（評分 >= 4）

2. **數據源分析**
   - 每個數據源的平均評分
   - 每個數據源的高品質比例
   - 數據源可靠性動態更新

3. **主題類別分析**
   - 高品質主題的共同特徵
   - 低品質主題的共同特徵
   - 主題親和度調整

4. **評分維度分析**
   - 哪個維度與評分相關性最高
   - 維度權重是否需要調整
   - 評分規則是否需要修改

**實現方案**：

```python
class FeedbackAnalyzer:
    """反饋分析引擎"""

    def __init__(self):
        self.feedback_collector = FeedbackCollector()
        self.preferences = self._load_preferences()

    def analyze_feedbacks(self):
        """
        分析所有反饋數據

        返回：
        - 整體品質統計
        - 數據源品質分析
        - 主題類別分析
        - 評分維度分析
        """
        feedbacks = self.feedback_collector.get_all_feedbacks()

        # 整體品質
        overall_quality = self._calculate_overall_quality(feedbacks)

        # 數據源品質
        source_quality = self._analyze_source_quality(feedbacks)

        # 主題類別
        topic_quality = self._analyze_topic_quality(feedbacks)

        # 評分維度
        dimension_analysis = self._analyze_dimensions(feedbacks)

        return {
            "overall_quality": overall_quality,
            "source_quality": source_quality,
            "topic_quality": topic_quality,
            "dimension_analysis": dimension_analysis
        }

    def _calculate_overall_quality(self, feedbacks):
        """計算整體品質"""
        ratings = [f["rating"] for f in feedbacks]
        return {
            "average_rating": sum(ratings) / len(ratings),
            "rating_distribution": self._get_rating_distribution(ratings),
            "high_quality_ratio": len([r for r in ratings if r >= 4]) / len(ratings)
        }

    def _analyze_source_quality(self, feedbacks):
        """分析數據源品質"""
        source_stats = {}

        for feedback in feedbacks:
            source = feedback["task_metadata"]["source"]
            if source not in source_stats:
                source_stats[source] = {"ratings": [], "count": 0}

            source_stats[source]["ratings"].append(feedback["rating"])
            source_stats[source]["count"] += 1

        # 計算統計
        for source, stats in source_stats.items():
            ratings = stats["ratings"]
            source_stats[source] = {
                "average_rating": sum(ratings) / len(ratings),
                "high_quality_ratio": len([r for r in ratings if r >= 4]) / len(ratings),
                "total_feedbacks": len(ratings)
            }

        # 動態更新數據源可靠性
        self._update_source_reliability(source_stats)

        return source_stats

    def _update_source_reliability(self, source_stats):
        """動態更新數據源可靠性"""
        for source, stats in source_stats.items():
            # 根據反饋調整可靠性
            current_reliability = self.preferences["sources"][source]["reliability"]
            new_reliability = self._calculate_new_reliability(
                current_reliability,
                stats["average_rating"]
            )

            # 更新可靠性
            self.preferences["sources"][source]["reliability"] = new_reliability

        # 保存更新
        self._save_preferences()
```

**時間估算**: 2 小時

---

### 2. 動態權重調整機制

**目標**：根據反饋數據動態調整評分系統的權重，提高推薦準確度

#### 2.1 評分維度權重調整

**當前權重**：
- Relevance: 35%
- Innovation: 25%
- Practicality: 25%
- Data Availability: 15%

**調整策略**：

1. **相關性分析**
   - 計算每個維度與用戶評分的相關性
   - 使用皮爾遜相關係數
   - 相關性高 → 提高權重
   - 相關性低 → 降低權重

2. **權重調整算法**
   ```python
   def adjust_weights(self, feedbacks):
       """
       根據反饋調整評分權重

       算法：
       1. 計算每個維度與評分的相關性
       2. 根據相關性調整權重
       3. 歸一化權重（總和 = 1）
       """
       # 計算相關性
       correlations = self._calculate_dimension_correlations(feedbacks)

       # 調整權重
       current_weights = self.preferences["scoring_weights"]
       new_weights = {}

       for dimension, weight in current_weights.items():
           correlation = correlations.get(dimension, 0)
           # 相關性高 → 權重增加
           adjustment = correlation * 0.1  # 調整幅度 10%
           new_weights[dimension] = weight * (1 + adjustment)

       # 歸一化
       total = sum(new_weights.values())
       new_weights = {k: v/total for k, v in new_weights.items()}

       # 保存權重
       self.preferences["scoring_weights"] = new_weights
       self._save_preferences()

       return new_weights
   ```

**時間估算**: 1.5 小時

---

#### 2.2 主題親和度動態調整

**調整策略**：

1. **基於反饋的親和度更新**
   ```python
   def update_topic_affinity(self, task_id, rating):
       """
       根據反饋更新主題親和度

       算法：
       - 高評分（>=4）→ 增加相關主題親和度
       - 低評分（<=2）→ 降低相關主題親和度
       - 中評分（3）→ 不調整
       """
       # 獲取任務關鍵詞
       task = self._get_task(task_id)
       keywords = task["keywords"]

       # 根據評分調整親和度
       if rating >= 4:
           # 高評分，增加親和度
           for keyword in keywords:
               self._increase_affinity(keyword, amount=0.1)
       elif rating <= 2:
           # 低評分，降低親和度
           for keyword in keywords:
               self._decrease_affinity(keyword, amount=0.1)

       # 保存更新
       self._save_preferences()
   ```

2. **關鍵詞親和度擴散**
   - 將親和度擴散到相關關鍵詞
   - 使用詞向量相似度
   - 提高推薦的多樣性

**時間估算**: 1.5 小時

---

#### 2.3 數據源可靠性動態更新

**更新算法**：

```python
def update_source_reliability(self, source, feedbacks):
    """
    動態更新數據源可靠性

    算法：
    1. 計算該數據源的平均評分
    2. 根據評分調整可靠性
    3. 應用衰減（避免快速變化）
    """
    # 計算平均評分
    ratings = [f["rating"] for f in feedbacks if f["task_metadata"]["source"] == source]
    avg_rating = sum(ratings) / len(ratings)

    # 獲取當前可靠性
    current_reliability = self.preferences["sources"][source]["reliability"]

    # 調整可靠性
    if avg_rating >= 4:
        # 高評分，提高可靠性
        adjustment = 0.05
    elif avg_rating <= 2:
        # 低評分，降低可靠性
        adjustment = -0.05
    else:
        # 中評分，不調整
        adjustment = 0

    # 應用調整
    new_reliability = current_reliability + adjustment

    # 限制在 [0, 1] 範圍
    new_reliability = max(0.0, min(1.0, new_reliability))

    # 保存更新
    self.preferences["sources"][source]["reliability"] = new_reliability
    self._save_preferences()

    return new_reliability
```

**時間估算**: 1 小時

---

## 📅 實施時間表

### Phase 2.1 - HIGH 優先級（立即實現）

| 任務 | 時間估算 | 優先級 | 依賴 |
|------|---------|--------|------|
| Reddit API 掃描器（OAuth 配置） | 1 小時 | 🔴 最高 | 無 |
| Threads 掃描器（web_reader） | 1.5 小時 | 🔴 最高 | 無 |
| Professional Quant Communities | 2 小時 | 🔴 最高 | 無 |
| 用戶反饋收集系統 | 2 小時 | 🔴 最高 | 無 |
| 反饋分析引擎 | 2 小時 | 🔴 最高 | 用戶反饋收集 |
| **小計** | **8.5 小時** | - | - |

**預計完成時間**: 1-2 天

---

### Phase 2.2 - MEDIUM-HIGH 優先級（本週實現）

| 任務 | 時間估算 | 優先級 | 依賴 |
|------|---------|--------|------|
| SSRN 掃描器 | 1.5 小時 | 🟡 高 | 無 |
| NBER 掃描器 | 1.5 小時 | 🟡 高 | 無 |
| Hedge Fund Reports | 2 小時 | 🟡 高 | 無 |
| 評分維度權重調整 | 1.5 小時 | 🟡 高 | 反饋分析 |
| 主題親和度動態調整 | 1.5 小時 | 🟡 高 | 反饋分析 |
| 數據源可靠性動態更新 | 1 小時 | 🟡 高 | 反饋分析 |
| **小計** | **9 小時** | - | - |

**預計完成時間**: 3-4 天

---

### Phase 2.3 - MEDIUM 優先級（下週實現）

| 任務 | 時間估算 | 優先級 | 依賴 |
|------|---------|--------|------|
| GitHub 掃描器 | 1.5 小時 | 🟢 中 | 無 |
| Kaggle 掃描器 | 1 小時 | 🟢 中 | 無 |
| TradingView Community | 1.5 小時 | 🟢 中 | 無 |
| 券商量化報告 | 2 小時 | 🟢 中 | 無 |
| Fintech Media | 1.5 小時 | 🟢 中 | 無 |
| 新聞媒體（RSS） | 1 小時 | 🟢 中 | 無 |
| **小計** | **8.5 小時** | - | - |

**預計完成時間**: 2-3 天

---

### 總計

| Phase | 任務數 | 時間估算 | 預計完成時間 |
|-------|-------|---------|------------|
| Phase 2.1 | 6 個 | 8.5 小時 | 1-2 天 |
| Phase 2.2 | 6 個 | 9 小時 | 3-4 天 |
| Phase 2.3 | 6 個 | 8.5 小時 | 2-3 天 |
| **總計** | **18 個** | **26 小時** | **1-2 週** |

---

## 🎯 成功指標

### 數據源擴展指標

- ✅ 實現 **9 個**數據源類別
- ✅ 覆蓋 **25+ 個**個別來源
- ✅ 每天掃描 **100+ 個**主題
- ✅ 去重效率 > 90%

### 學習功能指標

- ✅ 用戶反饋收集率 > 80%
- ✅ 平均評分提升到 >= 4.0
- ✅ 高品質任務比例提升到 >= 60%
- ✅ Scout 推薦品質提升 30%+

### 系統性能指標

- ✅ 完整掃描時間 < 5 分鐘
- ✅ 單個數據源掃描時間 < 30 秒
- ✅ 評分引擎一致性 >= 95%
- ✅ 系統穩定性 >= 99%

---

## 🚧 風險和緩解措施

### 技術風險

| 風險 | 影響 | 概率 | 緩解措施 |
|------|------|------|---------|
| Reddit API 限流 | 高 | 中 | 實現速率限制、錯誤重試、降級策略 |
| web_reader 不穩定 | 高 | 中 | 實現錯誤處理、重試機制、緩存策略 |
| 數據源結構變化 | 中 | 低 | 定期檢查、更新解析器、版本控制 |
| 反饋數據不足 | 中 | 高 | 主動收集、激勵機制、定期提醒 |

### 資源風險

| 風險 | 影響 | 概率 | 緩解措施 |
|------|------|------|---------|
| 開發時間超預算 | 中 | 中 | 優先實現高價值功能、分階段交付 |
| Token 消耗過高 | 高 | 中 | 實現智能緩存、批量處理、降級策略 |
| API 費用 | 中 | 低 | 使用免費 API、限制請求頻率、優化查詢 |

---

## 📋 檢查清單

### Phase 2.1 檢查清單

- [ ] 配置 Reddit OAuth
- [ ] 實現 Reddit API 掃描器
- [ ] 測試 Reddit 掃描（返回真實數據）
- [ ] 實現 Threads 掃描器
- [ ] 測試 Threads 掃描
- [ ] 實現 Professional Quant Communities 掃描器
- [ ] 測試 Quantocracy、QuantConnect、Nuclear Phynance、QuantNet
- [ ] 實現用戶反饋收集系統
- [ ] 實現反饋分析引擎
- [ ] 測試反饋收集和分析
- [ ] 完整測試和文檔

### Phase 2.2 檢查清單

- [ ] 實現 SSRN 掃描器
- [ ] 測試 SSRN 掃描
- [ ] 實現 NBER 掃描器
- [ ] 測試 NBER 掃描
- [ ] 實現 Hedge Fund Reports 掃描器
- [ ] 測試 AQR、Two Sigma、Citadel、Man AHL
- [ ] 實現評分維度權重調整
- [ ] 實現主題親和度動態調整
- [ ] 實現數據源可靠性動態更新
- [ ] 完整測試和文檔

### Phase 2.3 檢查清單

- [ ] 實現 GitHub 掃描器
- [ ] 測試 GitHub 掃描
- [ ] 實現 Kaggle 掃描器
- [ ] 測試 Kaggle 掃描
- [ ] 實現 TradingView Community 掃描器
- [ ] 測試 TradingView 掃描
- [ ] 實現券商量化報告掃描器
- [ ] 測試券商報告掃描
- [ ] 實現 Fintech Media 掃描器
- [ ] 測試 Fintech Media 掃描
- [ ] 實現新聞媒體 RSS 掃描器
- [ ] 測試新聞媒體掃描
- [ ] 完整測試和文檔

---

## 📝 結論

Phase 2 擴展計劃將 Scout 系統從單一 arXiv 掃描擴展到**全面的量化研究發現平台**，涵蓋：

✅ **9 個數據源類別** - 從學術研究到社群討論
✅ **25+ 個個別來源** - 多樣化的研究主題
✅ **用戶反饋系統** - 持續改進推薦品質
✅ **動態學習機制** - 自適應調整權重和親和度

**預期收益**：
- 每天發現 100+ 個研究主題
- 推薦品質提升 30%+
- 高品質任務比例 >= 60%
- 系統智能化程度顯著提升

**推薦實施順序**：
1. **立即開始**：Phase 2.1（HIGH 優先級）
2. **本週完成**：Phase 2.2（MEDIUM-HIGH 優先級）
3. **下週實施**：Phase 2.3（MEDIUM 優先級）

---

**計劃制定**: Scout System Enhancement Team  
**最終更新**: 2026-02-23 04:00 GMT+8
