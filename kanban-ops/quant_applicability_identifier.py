#!/usr/bin/env python3
"""
量化交易應用潛力識別系統

功能：
1. 掃描所有研究報告，識別量化交易應用潛力
2. 提取具體應用場景和實現思路
3. 建立應用案例庫（分類、評級、索引）
4. 生成應用潛力評估報告
"""

import json
import re
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict, Counter
import statistics

# ==================== 配置 ====================

WORKSPACE = Path("/Users/charlie/.openclaw/workspace")
PROJECTS_DIR = WORKSPACE / "kanban/projects"
OUTPUT_DIR = WORKSPACE / "kanban/outputs"

# 量化交易領域分類
QUANT_DOMAINS = {
    "因子投資": {
        "keywords": ["因子", "Fama", "French", "Smart Beta", "動量", "價值", "質量", "規模", "溢酬", "暴露"],
        "applicability": "高"
    },
    "算法交易": {
        "keywords": ["算法交易", "高頻", "訂單簿", "流動性", "市場微結構", "執行算法", "TWAP", "VWAP"],
        "applicability": "高"
    },
    "風險管理": {
        "keywords": ["風險", "風險管理", "風險模型", "VaR", "CVaR", "風險預算", "風險平價", "風險因子"],
        "applicability": "高"
    },
    "情緒分析": {
        "keywords": ["情緒", "Twitter", "新聞", "情感", "過度反應", "市場情緒", "投資者情緒"],
        "applicability": "中"
    },
    "機器學習": {
        "keywords": ["機器學習", "深度學習", "神經網絡", "XGBoost", "隨機森林", "預測", "分類", "回歸"],
        "applicability": "高"
    },
    "時間序列": {
        "keywords": ["時間序列", "預測", "預測模型", "趨勢", "季節性", "變點檢測", "因果推斷"],
        "applicability": "高"
    },
    "優化算法": {
        "keywords": ["優化", "優化算法", "組合優化", "投資組合優化", "均值方差", "Black-Litterman"],
        "applicability": "高"
    },
    "市場微結構": {
        "keywords": ["市場微結構", "買賣價差", "衝擊成本", "滑點", "訂單流", "深度"],
        "applicability": "中"
    },
    "行為金融": {
        "keywords": ["行為金融", "過度反應", "過度自信", "錨定效應", "損失厭惡", "異常現象"],
        "applicability": "中"
    },
    "加密貨幣": {
        "keywords": ["加密貨幣", "區塊鏈", "Bitcoin", "Ethereum", "DeFi", "交易對", "DEX"],
        "applicability": "中"
    }
}

# 實現難度評估指標
IMPLEMENTATION_DIFFICULTY = {
    "高": ["深度學習", "神經網絡", "強化學習", "因果推斷"],
    "中": ["機器學習", "時間序列", "優化算法", "貝葉斯"],
    "低": ["統計模型", "回歸", "指標", "簡單規則"]
}

# ==================== 數據結構 ====================

class QuantApplication:
    """量化交易應用案例"""

    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self.file_name = file_path.name
        self.title = ""
        self.arxiv_id = ""
        self.domains = []  # 適用的量化領域
        self.applicability_score = 0  # 應用潛力評分 (0-10)
        self.implementation_difficulty = "中"  # 實現難度：高/中/低
        self.estimated_development_time = ""  # 預估開發時間
        self.application_scenarios = []  # 具體應用場景
        self.research_gaps = []  # 研究空白
        self.notes = []  # 實現要點

    def analyze(self, content):
        """分析應用潛力"""
        # 提取標題
        title_match = re.search(r'^#\s*(.+)$', content, re.MULTILINE)
        if title_match:
            self.title = title_match.group(1).strip()

        # 提取 arXiv ID
        arxiv_match = re.search(r'arXiv[：:]\s*(\d+\.\d+)', content)
        if not arxiv_match:
            arxiv_match = re.search(r'(\d{4}\.\d{5})', content)
        if arxiv_match:
            self.arxiv_id = arxiv_match.group(1)

        # 識別適用的量化領域
        self.domains = self._identify_domains(content)

        # 評估應用潛力
        self.applicability_score = self._evaluate_applicability(content)

        # 評估實現難度
        self.implementation_difficulty = self._evaluate_difficulty(content)

        # 預估開發時間
        self.estimated_development_time = self._estimate_dev_time()

        # 提取應用場景
        self.application_scenarios = self._extract_scenarios(content)

        # 識別研究空白
        self.research_gaps = self._identify_gaps(content)

        # 提取實現要點
        self.notes = self._extract_notes(content)

    def _identify_domains(self, content):
        """識別適用的量化領域"""
        applicable_domains = []

        for domain, config in QUANT_DOMAINS.items():
            keyword_matches = sum(1 for kw in config["keywords"] if kw.lower() in content.lower())

            if keyword_matches >= 2:  # 至少匹配 2 個關鍵詞
                applicable_domains.append({
                    "name": domain,
                    "keyword_matches": keyword_matches,
                    "base_applicability": config["applicability"]
                })

        return applicable_domains

    def _evaluate_applicability(self, content):
        """評估應用潛力 (0-10)"""
        score = 5  # 基礎分

        # 領域匹配加分
        domain_bonus = min(3, len(self.domains) * 0.6)
        score += domain_bonus

        # 實驗驗證加分
        if any(kw in content for kw in ["實驗", "驗證", "實證", "回測", "backtest"]):
            score += 1

        # 具體應用場景加分
        if any(kw in content for kw in ["應用", "應用場景", "實際應用", "應用於"]):
            score += 1

        # 數據要求評估
        if any(kw in content for kw in ["市場數據", "價格數據", "歷史數據", "交易數據"]):
            score += 0.5

        # 實現細節加分
        if any(kw in content for kw in ["實現", "代碼", "Python", "R語言", "實踐"]):
            score += 0.5

        return min(10, max(0, score))

    def _evaluate_difficulty(self, content):
        """評估實現難度"""
        for difficulty, keywords in IMPLEMENTATION_DIFFICULTY.items():
            if any(kw in content for kw in keywords):
                return difficulty

        return "中"

    def _estimate_dev_time(self):
        """預估開發時間"""
        # 基於應用潛力和實現難度預估
        if self.applicability_score >= 8:
            base_time = "4-6 週"
        elif self.applicability_score >= 6:
            base_time = "3-4 週"
        else:
            base_time = "1-2 週"

        # 根據難度調整
        if self.implementation_difficulty == "高":
            time_map = {"4-6 週": "8-12 週", "3-4 週": "6-8 週", "1-2 週": "2-3 週"}
        elif self.implementation_difficulty == "中":
            time_map = {"4-6 週": "6-8 週", "3-4 週": "4-6 週", "1-2 週": "2-3 週"}
        else:  # 低
            time_map = {"4-6 週": "4-6 週", "3-4 週": "2-3 週", "1-2 週": "1-2 週"}

        return time_map.get(base_time, base_time)

    def _extract_scenarios(self, content):
        """提取具體應用場景"""
        scenarios = []

        # 常見應用場景模式
        scenario_patterns = [
            r'應用場景[：:]\s*(.+?)(?:\n|$)',
            r'適用於[：:]\s*(.+?)(?:\n|$)',
            r'應用於[：:]\s*(.+?)(?:\n|$)',
            r'實際應用[：:]\s*(.+?)(?:\n|$)'
        ]

        for pattern in scenario_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                scenario = match.strip()[:100]  # 限制長度
                if scenario and scenario not in scenarios:
                    scenarios.append(scenario)

        return scenarios[:5]  # 最多保留 5 個

    def _identify_gaps(self, content):
        """識別研究空白"""
        gaps = []

        gap_patterns = [
            r'局限性[：:]\s*(.+?)(?:\n|##)',
            r'未來研究方向[：:]\s*(.+?)(?:\n|##)',
            r'改進方向[：:]\s*(.+?)(?:\n|##)',
            r'挑戰[：:]\s*(.+?)(?:\n|##)'
        ]

        for pattern in gap_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                gap = match.strip()[:80]  # 限制長度
                if gap and gap not in gaps:
                    gaps.append(gap)

        return gaps[:5]  # 最多保留 5 個

    def _extract_notes(self, content):
        """提取實現要點"""
        notes = []

        # 實現相關關鍵詞
        implementation_keywords = [
            "實現", "實踐", "代碼", "算法", "步驟", "流程",
            "Python", "R", "實際", "具體", "建議"
        ]

        for keyword in implementation_keywords:
            if keyword in content:
                notes.append(f"包含 '{keyword}' 相關內容")

        # 限制要點數量
        return notes[:10]

    def to_dict(self):
        """轉換為字典格式"""
        return {
            "file_name": self.file_name,
            "title": self.title[:80] if self.title else self.file_name,
            "arxiv_id": self.arxiv_id,
            "domains": self.domains,
            "applicability_score": round(self.applicability_score, 2),
            "implementation_difficulty": self.implementation_difficulty,
            "estimated_development_time": self.estimated_development_time,
            "application_scenarios": self.application_scenarios,
            "research_gaps": self.research_gaps,
            "notes": self.notes
        }

# ==================== 主函數 ====================

def find_research_files():
    """找出所有研究報告文件"""
    research_files = []

    for file_path in PROJECTS_DIR.rglob("*research.md"):
        research_files.append(file_path)

    print(f"找到 {len(research_files)} 個研究報告文件")
    return research_files

def analyze_applicability(research_files):
    """分析所有研究的應用潛力"""
    applications = []

    for file_path in research_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            app = QuantApplication(file_path)
            app.analyze(content)

            # 只保留有量化交易應用潛力的研究
            if app.domains or app.applicability_score >= 6:
                applications.append(app)

        except Exception as e:
            print(f"分析失敗: {file_path.name} - {e}")

    print(f"識別出 {len(applications)} 個有量化交易應用潛力的研究")
    return applications

def generate_domain_summary(applications):
    """生成領域統計摘要"""
    domain_stats = defaultdict(lambda: {
        "count": 0,
        "avg_score": 0,
        "high_priority": 0
    })

    for app in applications:
        for domain_info in app.domains:
            domain_name = domain_info["name"]
            domain_stats[domain_name]["count"] += 1
            domain_stats[domain_name]["avg_score"] += app.applicability_score

            if app.applicability_score >= 8:
                domain_stats[domain_name]["high_priority"] += 1

    # 計算平均分
    for domain_name in domain_stats:
        if domain_stats[domain_name]["count"] > 0:
            domain_stats[domain_name]["avg_score"] /= domain_stats[domain_name]["count"]

    return domain_stats

def generate_applicability_report(applications, domain_stats, output_file):
    """生成應用潛力評估報告"""

    # 按應用潛力排序
    sorted_apps = sorted(applications, key=lambda a: a.applicability_score, reverse=True)

    # 高優先級應用 (≥8.0)
    high_priority = [a for a in applications if a.applicability_score >= 8]
    # 中優先級應用 (6.0-8.0)
    medium_priority = [a for a in applications if 6.0 <= a.applicability_score < 8]

    # 統計
    if applications:
        avg_score = statistics.mean([a.applicability_score for a in applications])
        avg_dev_time_high = statistics.mean([
            len(a.estimated_development_time.split('-')[0]) if a.implementation_difficulty == "高" else 0
            for a in applications
        ])
    else:
        avg_score = 0
        avg_dev_time_high = 0

    # 生成報告
    report = f"""# 量化交易應用潛力評估報告

**生成時間：** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}
**數據範圍：** 所有已完成的研究報告
**有應用潛力的研究：** {len(applications)} 篇

---

## 📊 總體統計

### 基本指標

| 指標 | 數值 |
|------|------|
| 有應用潛力的研究 | {len(applications)} 篇 |
| 平均應用潛力評分 | {avg_score:.2f}/10 |
| 高優先級應用 (≥8.0) | {len(high_priority)} 篇 |
| 中優先級應用 (6.0-8.0) | {len(medium_priority)} 篇 |

### 應用潛力分佈

| 分數段 | 數量 | 占比 |
|--------|------|------|
| 高潛力 (≥8.0) | {len(high_priority)} | {len(high_priority)/len(applications)*100:.1f}% |
| 中潛力 (6.0-8.0) | {len(medium_priority)} | {len(medium_priority)/len(applications)*100:.1f}% |

---

## 🎯 按領域統計

| 領域 | 研究數量 | 平均評分 | 高優先級 | 基礎適用性 |
|------|----------|----------|----------|------------|
"""

    for domain_name, stats in sorted(domain_stats.items(),
                                 key=lambda x: x[1]["count"],
                                 reverse=True):
        report += f"| {domain_name} | {stats['count']} | {stats['avg_score']:.2f} | {stats['high_priority']} | {QUANT_DOMAINS[domain_name]['applicability']} |\n"

    report += "\n"

    # 高優先級應用詳細列表
    report += "## 🏆 高優先級應用 (應用潛力 ≥8.0)\n\n"

    for i, app in enumerate(high_priority, 1):
        report += f"""
### {i}. [{app.applicability_score:.2f}] {app.title[:70]}...

**文件：** `{app.file_name}`
**arXiv ID：** {app.arxiv_id or 'N/A'}
**實現難度：** {app.implementation_difficulty}
**預估開發時間：** {app.estimated_development_time}

**適用領域：**
"""

        for domain_info in app.domains:
            report += f"- {domain_info['name']} (匹配 {domain_info['keyword_matches']} 個關鍵詞)\n"

        if app.application_scenarios:
            report += f"\n**應用場景：**\n"
            for scenario in app.application_scenarios[:3]:
                report += f"- {scenario}\n"

        if app.research_gaps:
            report += f"\n**研究空白：**\n"
            for gap in app.research_gaps[:3]:
                report += f"- {gap}\n"

        report += "\n---\n"

    # 中優先級應用簡要列表
    if medium_priority:
        report += "\n## 🎲 中優先級應用 (應用潛力 6.0-8.0)\n\n"
        report += "| 排名 | 標題 | 應用潛力 | 領域 | 實現難度 |\n"
        report += "|------|------|----------|------|----------|\n"

        for i, app in enumerate(medium_priority, len(high_priority) + 1):
            domains = ", ".join([d['name'] for d in app.domains[:2]])
            report += f"| {i} | {app.title[:50]}... | {app.applicability_score:.2f} | {domains} | {app.implementation_difficulty} |\n"

    # 實施建議
    report += """

## 💡 實施建議

### 立即啟動（未來 1-2 個月）

基於應用潛力評分和實現難度，建議優先啟動以下研究：

"""

    # 選擇 3-5 個高優先級且相對容易實現的應用
    quick_wins = [a for a in high_priority if a.implementation_difficulty in ["低", "中"]][:5]

    for i, app in enumerate(quick_wins, 1):
        domains = ", ".join([d['name'] for d in app.domains[:2]])
        report += f"""
{i}. **{app.title[:60]}...**
   - 應用潛力：{app.applicability_score:.2f}/10
   - 實現難度：{app.implementation_difficulty}
   - 預估開發時間：{app.estimated_development_time}
   - 核心領域：{domains}
"""

    # 技術路線圖
    report += """

### 技術路線圖

**階段一：基礎建設 (1-2 個月)**
- 建立應用案例庫索引系統
- 實施高優先級、低難度應用
- 驗證研究結果的可重現性

**階段二：深化應用 (3-6 個月)**
- 實施高優先級、中高難度應用
- 建立應用效果評估機制
- 積累實際應用數據

**階段三：持續優化 (6 個月以上)**
- 優化已有應用
- 探索新的應用場景
- 建立研究-應用閉環

---

## 🔧 實現要點總結

### 通用實現建議

1. **數據準備**
   - 建立統一的數據管道
   - 確保數據質量和一致性
   - 實施數據驗證機制

2. **技術選型**
   - 優先選擇成熟的開源庫
   - 考慮雲計算資源需求
   - 建立監控和日誌系統

3. **風險管理**
   - 實施風險控制措施
   - 建立回滾機制
   - 定期進行風險評估

4. **持續迭代**
   - 建立A/B測試機制
   - 監控應用效果
   - 根據反饋持續優化

---

**報告生成時間：** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
**下次更新：** 建議每 2 週更新一次
"""

    # 保存報告
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(report, encoding='utf-8')
    print(f"✅ 應用潛力評估報告已生成: {output_file}")

def generate_case_library(applications, output_file):
    """生成應用案例庫（JSON 格式）"""

    cases = []

    for app in applications:
        case = app.to_dict()
        cases.append(case)

    # 保存 JSON
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(cases, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"✅ 應用案例庫已生成: {output_file}")

# ==================== 主程序 ====================

def main():
    print("=" * 60)
    print("量化交易應用潛力識別系統")
    print("=" * 60)

    # 1. 找出所有研究報告文件
    research_files = find_research_files()

    # 2. 分析應用潛力
    applications = analyze_applicability(research_files)

    if not applications:
        print("⚠️ 未識別到有量化交易應用潛力的研究")
        return

    # 3. 生成領域統計
    domain_stats = generate_domain_summary(applications)

    # 4. 生成應用潛力評估報告
    report_file = OUTPUT_DIR / f"quant-applicability-report-{datetime.now().strftime('%Y%m%d')}.md"
    generate_applicability_report(applications, domain_stats, report_file)

    # 5. 生成應用案例庫
    library_file = OUTPUT_DIR / f"quant-application-library-{datetime.now().strftime('%Y%m%d')}.json"
    generate_case_library(applications, library_file)

    print("\n" + "=" * 60)
    print("✅ 應用潛力識別完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
