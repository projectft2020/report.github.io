# 記憶系統 v2.0
## 自動流入模式（2026-03-01）

---

## 一、背景問題

### 1.1 當前記憶系統架構

**v1.0 結構**：
- **短期記憶**：每日日誌（`memory/YYYY-MM-DD.md`）
- **中期記憶**：主題知識（`memory/topics/*.md`）
- **長期記憶**：主索引（`MEMORY.md`）

**v1.0 問題**：
- ❌ 手動整理：需要主動觸發，容易遺漏
- ❌ 人工判斷：每日日誌→主題文件的轉換是人工判斷
- ❌ 分界不清：用「時間」而非「重要性」分界
- ❌ 缺少自動化：沒有自動提取、自動分類、自動索引

### 1.2 實際問題案例

**案例 1：重要洞察遺漏**
- Supertrend 策略深度分析的關鍵洞察（第 7 天虧損是關鍵預測因子）
- 沒有自動更新到 `memory/topics/quantitative-research.md`
- 需要手動整理才能轉移到中期記憶

**案例 2：記憶整理滯後**
- 2 月 26-28 日的記憶，直到 3 月 1 日才整理
- 如果沒有主動觸發，可能一直沒有整理

**案例 3：重要信息淹沒**
- 日常瑣事、系統事件、運行狀態等低價值信息
- 混在高價值信息中，難以提取

---

## 二、v2.0 自動流入模式

### 2.1 核心理念

**v1.0**：手動整理 → 人工分類 → 手動索引
**v2.0**：自動流入 → 智能評分 → 自動分級

**關鍵改進**：
- 🔄 自動流入：新信息自動進入記憶系統
- 🧠 智能評分：根據內容自動評估重要性
- 📊 自動分級：高重要性自動提升到中長期記憶
- 🔍 自動索引：更新向量索引，支持語義搜索

### 2.2 三層記憶架構（v2.0）

#### 短期記憶（Daily Log）
- **位置**：`memory/YYYY-MM-DD.md`
- **內容**：當日所有活動、事件、學習、思考
- **特點**：原始、未經篩選、按時間順序
- **保留期限**：7 天（自動清理）

#### 中期記憶（Topic Knowledge）
- **位置**：`memory/topics/*.md`
- **內容**：主題知識、策略研究、技術學習、系統改進
- **特點**：結構化、可檢索、分類整理
- **觸發條件**：高重要性信息自動提升

#### 長期記憶（Master Index）
- **位置**：`MEMORY.md`
- **內容**：關鍵決策、重要洞察、用戶偏好、核心原則
- **特點**：高度凝練、快速查詢、核心價值
- **觸發條件**：極高重要性信息自動提升

---

## 三、重要性評分機制

### 3.1 評分維度

#### 維度 1：內容類型（0-2 分）

| 類型 | 分數 | 說明 |
|------|------|------|
| 策略洞察 | 2 | 策略研究發現、模式識別、數據驗證教訓 |
| 錯誤教訓 | 2 | 失敗案例、錯誤原因、改進措施 |
| 系統改進 | 2 | 流程優化、自動化改進、架構升級 |
| 技術學習 | 1 | 新技術、新工具、新框架 |
| 日常工作 | 0 | 日常事務、系統事件、運行狀態 |
| 瑣碎事項 | 0 | 聊天記錄、無意義信息 |

#### 維度 2：頻率與持續性（0-2 分）

| 頻率 | 分數 | 說明 |
|------|------|------|
| 多次提及 | 2 | 同一主題在不同日誌中多次出現 |
| 首次提及但深入 | 1 | 首次提及，但內容詳細、有分析 |
| 首次提及簡單 | 0 | 首次提及，內容簡單 |

#### 維度 3：影響力（0-2 分）

| 影響力 | 分數 | 說明 |
|------|------|------|
| 改變決策或行動 | 2 | 導致新的決策、改變現有流程 |
| 提供重要信息 | 1 | 為未來工作提供基礎 |
| 僅記錄 | 0 | 簡單記錄，無明確影響 |

#### 維度 4：用戶標記（0-2 分）

| 標記 | 分數 | 說明 |
|------|------|------|
| 用戶明確標記重要 | 2 | 用戶說「記住這個」、「這很重要」 |
| 系統判斷高價值 | 1 | 符合系統定義的高價值模式 |
| 無標記 | 0 | 無明確標記 |

### 3.2 總分計算

**公式**：
```
重要性分數 = 內容類型 + 頻率 + 影響力 + 用戶標記
總分範圍：0-8 分
```

### 3.3 分級標準

| 分數 | 級別 | 處理方式 | 存儲位置 |
|------|------|----------|---------|
| 0-1 | 低 | 7 天後自動清理 | 短期記憶 |
| 2-4 | 中 | 保留在主題文件，更新索引 | 中期記憶 |
| 5-8 | 高 | 提升到主索引，永久保存 | 長期記憶 |

---

## 四、自動記憶整理流程

### 4.1 流程圖

```
新信息（每日日誌）
    ↓
智能評分（4 維度評分）
    ↓
分級（低/中/高）
    ↓
    ├── 低分（0-1）→ 7 天後自動清理
    │
    ├── 中分（2-4）→ 提取關鍵詞 → 匹配主題文件 → 更新中期記憶 → 更新向量索引
    │
    └── 高分（5-8）→ 提取關鍵洞察 → 更新長期記憶 → 更新向量索引
```

### 4.2 詳細步驟

#### 步驟 1：讀取每日日誌
```python
# 讀取當前日誌
log_path = f"memory/{date_str}.md"
with open(log_path, 'r') as f:
    daily_log = f.read()
```

#### 步驟 2：分段與評分
```python
# 將日誌分段（按標題、段落）
segments = split_segments(daily_log)

# 對每個段落評分
for segment in segments:
    score = calculate_importance_score(segment)
```

#### 步驟 3：關鍵詞提取（使用 QMD）
```python
# 使用 QMD 語義搜索提取關鍵詞
from qmd import semantic_search

keywords = semantic_search.extract_keywords(segment)
```

#### 步驟 4：匹配主題文件
```python
# 根據關鍵詞匹配主題文件
matched_topics = find_matching_topics(keywords)

for topic in matched_topics:
    append_to_topic_file(topic, segment)
```

#### 步驟 5：更新長期記憶（如果高分）
```python
if score >= 5:
    # 提取關鍵洞察
    insight = extract_insight(segment)

    # 更新長期記憶
    update_long_term_memory(insight)
```

#### 步驟 6：更新向量索引
```python
# 更新 QMD 向量索引
from qmd import update_index

update_index()
```

### 4.3 自動觸發機制

#### 觸發條件
- **每日自動執行**：每天 03:00 自動執行記憶整理
- **主動觸發**：用戶明確要求整理記憶時
- **事件觸發**：完成重要項目時（如策略研究完成）

#### 清理機制
- **短期記憶清理**：7 天前的低分內容（0-1 分）自動清理
- **重複內容去重**：檢測重複內容，合併或刪除
- **過時內容歸檔**：長期未使用的中期記憶歸檔

---

## 五、實現方案

### 5.1 記憶評分腳本

```python
"""
記憶評分器 - 自動評估記憶重要性
用途：為每日日誌中的每個段落評分，決定記憶分級
"""

import re
from typing import Dict, List

class MemoryScorer:
    """記憶評分器"""

    def __init__(self):
        """初始化評分器"""
        # 高價值關鍵詞
        self.high_value_keywords = [
            '策略', '洞察', '發現', '教訓', '錯誤', '失敗', '成功',
            '優化', '改進', '升級', '架構', '系統', '自動化',
            '驗證', '檢查', '測試', '實施', '執行', '完成'
        ]

        # 低價值關鍵詞
        self.low_value_keywords = [
            '系統', '運行', '啟動', '停止', '重啟', '檢查', '日誌',
            '聊天', '訊息', '對話', '討論'
        ]

        # 主題文件映射
        self.topic_mapping = {
            '策略': 'quantitative-research.md',
            '研究': 'quantitative-research.md',
            '數據驗證': 'research-standards.md',
            '用戶偏好': 'user-preferences.md',
            '系統': 'system-design.md',
            '自動化': 'automation.md'
        }

    def calculate_content_type_score(self, segment: str) -> int:
        """
        評估內容類型（0-2 分）

        Parameters:
        -----------
        segment : str
            文本段落

        Returns:
        --------
        int
            分數（0-2）
        """
        # 檢查高價值關鍵詞
        for keyword in self.high_value_keywords:
            if keyword in segment:
                return 2

        # 檢查中等價值關鍵詞
        medium_keywords = ['學習', '了解', '發現', '認識']
        for keyword in medium_keywords:
            if keyword in segment:
                return 1

        # 檢查低價值關鍵詞
        for keyword in self.low_value_keywords:
            if keyword in segment:
                return 0

        # 默認中等
        return 1

    def calculate_frequency_score(self, segment: str, history: List[str]) -> int:
        """
        評估頻率（0-2 分）

        Parameters:
        -----------
        segment : str
            文本段落
        history : List[str]
            歷史記錄

        Returns:
        --------
        int
            分數（0-2）
        """
        # 檢查歷史中是否提及相同關鍵詞
        keywords = self._extract_keywords(segment)

        mention_count = 0
        for past_segment in history:
            for keyword in keywords:
                if keyword in past_segment:
                    mention_count += 1
                    break

        if mention_count >= 3:
            return 2  # 多次提及
        elif mention_count >= 1:
            return 1  # 首次提及但深入
        else:
            return 0  # 首次提及簡單

    def calculate_impact_score(self, segment: str) -> int:
        """
        評估影響力（0-2 分）

        Parameters:
        -----------
        segment : str
            文本段落

        Returns:
        --------
        int
            分數（0-2）
        """
        # 檢查行動導向關鍵詞
        action_keywords = ['執行', '實施', '採取', '決定', '改變', '調整']
        for keyword in action_keywords:
            if keyword in segment:
                return 2  # 改變決策或行動

        # 檢查信息導向關鍵詞
        info_keywords = ['提供', '記錄', '總結', '學習']
        for keyword in info_keywords:
            if keyword in segment:
                return 1  # 提供重要信息

        # 默認
        return 0  # 僅記錄

    def calculate_user_mark_score(self, segment: str) -> int:
        """
        評估用戶標記（0-2 分）

        Parameters:
        -----------
        segment : str
            文本段落

        Returns:
        --------
        int
            分數（0-2）
        """
        # 檢查用戶明確標記
        mark_keywords = ['重要', '關鍵', '記住', '必須', '核心']
        for keyword in mark_keywords:
            if keyword in segment:
                return 2  # 用戶明確標記重要

        # 檢查系統判斷
        if self.calculate_content_type_score(segment) == 2:
            return 1  # 系統判斷高價值

        # 默認
        return 0  # 無標記

    def calculate_total_score(self, segment: str, history: List[str] = None) -> Dict:
        """
        計算總分

        Parameters:
        -----------
        segment : str
            文本段落
        history : List[str] or None
            歷史記錄

        Returns:
        --------
        Dict
            包含各維度分數和總分的字典
        """
        if history is None:
            history = []

        content_type_score = self.calculate_content_type_score(segment)
        frequency_score = self.calculate_frequency_score(segment, history)
        impact_score = self.calculate_impact_score(segment)
        user_mark_score = self.calculate_user_mark_score(segment)

        total_score = (
            content_type_score +
            frequency_score +
            impact_score +
            user_mark_score
        )

        return {
            'content_type': content_type_score,
            'frequency': frequency_score,
            'impact': impact_score,
            'user_mark': user_mark_score,
            'total': total_score,
            'level': self._get_level(total_score)
        }

    def _get_level(self, score: int) -> str:
        """獲取記憶分級"""
        if score <= 1:
            return 'low'
        elif score <= 4:
            return 'medium'
        else:
            return 'high'

    def _extract_keywords(self, segment: str) -> List[str]:
        """提取關鍵詞"""
        # 簡單實現：提取中文詞匯
        keywords = re.findall(r'[\u4e00-\u9fff]{2,}', segment)
        return list(set(keywords))


# 使用示例
if __name__ == "__main__":
    scorer = MemoryScorer()

    # 測試段落
    test_segments = [
        "完成 Supertrend 策略深度分析，發現第 7 天虧損是關鍵預測因子",
        "系統運行正常，日誌記錄完成",
        "調整經濟系統成本結構，固定成本改為動態計算",
        "跟 Mentor 討論數據驗證問題"
    ]

    for segment in test_segments:
        result = scorer.calculate_total_score(segment)
        print(f"段落：{segment[:30]}...")
        print(f"  內容類型：{result['content_type']}")
        print(f"  頻率：{result['frequency']}")
        print(f"  影響力：{result['impact']}")
        print(f"  用戶標記：{result['user_mark']}")
        print(f"  總分：{result['total']} ({result['level']})")
        print()
```

### 5.2 自動記憶整理腳本

```python
"""
自動記憶整理腳本
用途：每日自動整理記憶，評分、分級、更新索引
"""

import os
import re
from datetime import datetime, timedelta
from typing import List, Dict

class MemoryOrganizer:
    """自動記憶整理器"""

    def __init__(self, workspace_path: str):
        """
        初始化整理器

        Parameters:
        -----------
        workspace_path : str
            工作目錄路徑
        """
        self.workspace_path = workspace_path
        self.memory_path = os.path.join(workspace_path, 'memory')
        self.topics_path = os.path.join(self.memory_path, 'topics')
        self.scorer = MemoryScorer()

    def organize_daily_memory(self, date_str: str = None):
        """
        整理每日記憶

        Parameters:
        -----------
        date_str : str or None
            日期字符串（YYYY-MM-DD），如果為 None 則使用當前日期
        """
        if date_str is None:
            date_str = datetime.now().strftime('%Y-%m-%d')

        log_path = os.path.join(self.memory_path, f'{date_str}.md')

        # 檢查文件是否存在
        if not os.path.exists(log_path):
            print(f"⚠️  日誌文件不存在：{log_path}")
            return

        # 讀取日誌
        with open(log_path, 'r', encoding='utf-8') as f:
            daily_log = f.read()

        # 分段
        segments = self._split_segments(daily_log)

        # 讀取歷史記錄（用於頻率評分）
        history = self._load_history(date_str)

        # 評分和分級
        high_importance = []
        medium_importance = []
        low_importance = []

        for segment in segments:
            score_result = self.scorer.calculate_total_score(segment, history)

            if score_result['level'] == 'high':
                high_importance.append((segment, score_result))
            elif score_result['level'] == 'medium':
                medium_importance.append((segment, score_result))
            else:
                low_importance.append((segment, score_result))

        # 更新中期記憶
        self._update_medium_memory(medium_importance)

        # 更新長期記憶
        self._update_long_term_memory(high_importance)

        # 清理低價值記憶（7 天前）
        self._cleanup_low_memory(date_str)

        # 更新向量索引
        self._update_vector_index()

        print(f"✅ 記憶整理完成：{date_str}")
        print(f"  高重要性：{len(high_importance)} 段")
        print(f"  中重要性：{len(medium_importance)} 段")
        print(f"  低重要性：{len(low_importance)} 段")

    def _split_segments(self, text: str) -> List[str]:
        """分段"""
        # 按標題和段落分段
        segments = re.split(r'\n#{1,3}\s+', text)
        return [seg.strip() for seg in segments if seg.strip()]

    def _load_history(self, current_date_str: str) -> List[str]:
        """加載歷史記錄"""
        history = []

        # 加載最近 7 天的日誌
        current_date = datetime.strptime(current_date_str, '%Y-%m-%d')
        for i in range(1, 8):
            past_date = current_date - timedelta(days=i)
            past_date_str = past_date.strftime('%Y-%m-%d')

            log_path = os.path.join(self.memory_path, f'{past_date_str}.md')
            if os.path.exists(log_path):
                with open(log_path, 'r', encoding='utf-8') as f:
                    history.append(f.read())

        return history

    def _update_medium_memory(self, segments: List[tuple]):
        """更新中期記憶"""
        for segment, score_result in segments:
            # 提取關鍵詞
            keywords = self._extract_keywords(segment)

            # 匹配主題文件
            matched_topic = self._match_topic(keywords)

            if matched_topic:
                # 追加到主題文件
                topic_path = os.path.join(self.topics_path, matched_topic)
                self._append_to_file(topic_path, segment)

    def _update_long_term_memory(self, segments: List[tuple]):
        """更新長期記憶"""
        memory_path = os.path.join(self.workspace_path, 'MEMORY.md')

        for segment, score_result in segments:
            # 提取關鍵洞察
            insight = self._extract_insight(segment)

            # 追加到長期記憶
            self._append_to_file(memory_path, insight)

    def _cleanup_low_memory(self, current_date_str: str):
        """清理低價值記憶"""
        current_date = datetime.strptime(current_date_str, '%Y-%m-%d')
        cleanup_date = current_date - timedelta(days=7)
        cleanup_date_str = cleanup_date.strftime('%Y-%m-%d')

        log_path = os.path.join(self.memory_path, f'{cleanup_date_str}.md')
        if os.path.exists(log_path):
            # 評分日誌中的所有段落
            with open(log_path, 'r', encoding='utf-8') as f:
                daily_log = f.read()

            segments = self._split_segments(daily_log)

            # 如果所有段落都是低分，則刪除文件
            all_low = True
            for segment in segments:
                score_result = self.scorer.calculate_total_score(segment)
                if score_result['level'] != 'low':
                    all_low = False
                    break

            if all_low:
                os.remove(log_path)
                print(f"  🗑️  清理低價值記憶：{cleanup_date_str}.md")

    def _update_vector_index(self):
        """更新向量索引"""
        # 調用 QMD 更新索引
        # TODO: 實現 QMD 更新邏輯
        pass

    def _extract_keywords(self, segment: str) -> List[str]:
        """提取關鍵詞"""
        # TODO: 使用 QMD 語義搜索提取關鍵詞
        # 暫時使用簡單的正則表達式
        keywords = re.findall(r'[\u4e00-\u9fff]{2,}', segment)
        return list(set(keywords))[:5]

    def _match_topic(self, keywords: List[str]) -> str:
        """匹配主題文件"""
        # TODO: 實現智能主題匹配
        # 暫時使用簡單的關鍵詞匹配
        for keyword, topic in self.scorer.topic_mapping.items():
            if keyword in keywords:
                return topic
        return None

    def _extract_insight(self, segment: str) -> str:
        """提取關鍵洞察"""
        # TODO: 實現智能洞察提取
        # 暫時返回整個段落
        return f"\n\n## {datetime.now().strftime('%Y-%m-%d')}\n\n{segment}"

    def _append_to_file(self, file_path: str, content: str):
        """追加到文件"""
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(content)


# 使用示例
if __name__ == "__main__":
    organizer = MemoryOrganizer('/Users/charlie/.openclaw/workspace')
    organizer.organize_daily_memory('2026-03-01')
```

---

## 六、實施步驟

### 6.1 文件更新
- [ ] 保存本文檔到 `workspace/kanban/outputs/memory-system-v2.md`
- [ ] 保存腳本到 `workspace/tools/memory_scorer.py`
- [ ] 保存腳本到 `workspace/tools/memory_organizer.py`
- [ ] 更新 `MEMORY.md`（加入新的記憶系統說明）

### 6.2 測試驗證
- [ ] 用 2 月 26-28 日的日誌測試評分器
- [ ] 驗證分級是否合理
- [ ] 驗證主題匹配是否準確
- [ ] 驗證清理機制是否正常

### 6.3 自動化整合
- [ ] 設置每日定時任務（03:00 執行）
- [ ] 整合到 cron 作業
- [ ] 建立監控日誌
- [ ] 建立失敗重試機制

### 6.4 持續優化
- [ ] 根據實際使用調整評分權重
- [ ] 優化關鍵詞提取算法（使用 QMD）
- [ ] 優化主題匹配算法
- [ ] 建立用戶反饋機制

---

## 七、預期效果

### 7.1 對比 v1.0

| 維度 | v1.0 | v2.0 | 改進 |
|------|------|------|------|
| 整理方式 | 手動 | 自動 | ✅ 無需手動干預 |
| 評分機制 | 無 | 4 維度智能評分 | ✅ 自動評估重要性 |
| 分級標準 | 時間 | 重要性 | ✅ 更合理的分級 |
| 遺漏風險 | 高 | 低 | ✅ 自動提取 |
| 過時清理 | 無 | 自動 | ✅ 自動清理 |
| 向量索引 | 手動 | 自動 | ✅ 即時更新 |

### 7.2 效率提升

**v1.0**：
- 記憶整理時間：每週 1-2 小時
- 遺漏重要信息：每月 1-2 次
- 索引更新：手動，每月 1 次

**v2.0**：
- 記憶整理時間：0 小時（自動）
- 遺漏重要信息：幾乎不發生
- 索引更新：每日自動

**節省時間**：每週 1-2 小時 → 0 小時

---

## 八、總結

### 8.1 核心優勢
1. **自動化**：無需手動整理，每日自動執行
2. **智能化**：4 維度評分，自動評估重要性
3. **自動分級**：根據重要性自動提升到中長期記憶
4. **自動清理**：7 天後自動清理低價值記憶
5. **即時索引**：更新向量索引，支持語義搜索

### 8.2 實施建議
- ✅ **立即實施**：建立 v1.0 後，立即開始 v2.0 開發
- ✅ **測試優化**：用實際數據測試，調整評分權重
- ✅ **持續改進**：根據使用情況持續優化算法

### 8.3 後續優化
- 使用 QMD 語義搜索優化關鍵詞提取
- 使用機器學習優化評分算法
- 建立用戶反饋機制
- 優化主題匹配算法

---

**文檔版本**：v2.0
**創建日期**：2026-03-01
**創建者**：Charlie + Mentor
**狀態**：⏳ 等待實施
