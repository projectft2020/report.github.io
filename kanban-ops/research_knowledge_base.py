#!/usr/bin/env python3
"""
研究知识库综合分析脚本（改进版）

功能：
1. 扫描所有研究报告文件
2. 提取元数据（标题、摘要、关键词等）
3. 应用四维度评分系统（基于内容分析）
4. 主题聚类和趋势分析
5. 生成综合性知识报告
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
TASKS_FILE = WORKSPACE / "kanban/tasks.json"
OUTPUT_DIR = WORKSPACE / "kanban/outputs"

# 评分权重
SCORE_WEIGHTS = {
    "depth": 0.3,
    "completeness": 0.25,
    "innovation": 0.25,
    "applicability": 0.2
}

# 量化交易相关关键词
QUANT_TRADING_KEYWORDS = [
    "交易", "金融", "市場", "風險", "回測", "策略",
    "資產", "投資", "對沖", "套利", "因子", "價格",
    "股票", "期貨", "選擇權", "貨幣", "加密貨幣", "區塊鏈",
    "收益率", "波動率", "流動性", "訂單簿", "高頻"
]

# ==================== 数据结构 ====================

class ResearchPaper:
    """研究论文数据结构"""

    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self.file_name = file_path.name
        self.title = ""
        self.arxiv_id = ""
        self.authors = ""
        self.year = ""
        self.venue = ""
        self.abstract = ""
        self.keywords = []
        self.content = ""
        self.content_length = 0
        self.sections = []
        self.scores = {
            "depth": 0,
            "completeness": 0,
            "innovation": 0,
            "applicability": 0
        }
        self.total_score = 0

    def load(self):
        """加载研究报告"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
            self.content_length = len(self.content)
            self._extract_metadata()
            self._extract_sections()
            self._auto_score()
            return True
        except Exception as e:
            print(f"加载失败: {self.file_path.name} - {e}")
            return False

    def _extract_metadata(self):
        """提取元数据"""
        # 提取标题（第一个 # 标题）
        title_match = re.search(r'^#\s*(.+)$', self.content, re.MULTILINE)
        if title_match:
            self.title = title_match.group(1).strip()

        # 提取 arXiv ID
        arxiv_match = re.search(r'arXiv[：:]\s*(\d+\.\d+)', self.content)
        if not arxiv_match:
            arxiv_match = re.search(r'(\d{4}\.\d{5})', self.content)
        if arxiv_match:
            self.arxiv_id = arxiv_match.group(1)

        # 提取作者
        authors_match = re.search(r'作者[：:]\s*(.+?)(?:\n|$)', self.content)
        if authors_match:
            self.authors = authors_match.group(1).strip()

        # 提取年份
        year_match = re.search(r'20(\d{2})', self.content)
        if year_match:
            self.year = year_match.group(1)

        # 提取会议/期刊
        venue_patterns = [
            r'(NeurIPS|ICML|ICLR|AISTATS|AAAI|IJCAI|CVPR|ECCV|JMLR)',
            r'(Nature|Science|PNAS)',
            r'(Econometrica|JPE|QJE|AER)'
        ]
        for pattern in venue_patterns:
            venue_match = re.search(pattern, self.content)
            if venue_match:
                self.venue = venue_match.group(1)
                break

        # 提取摘要
        abstract_match = re.search(r'## 研究摘要\s*(.+?)(?=##|$)', self.content, re.DOTALL)
        if abstract_match:
            self.abstract = abstract_match.group(1).strip()[:500]

        # 提取关键词
        keywords_matches = re.findall(r'[、,，]\s*([^、,，\n]{2,10})', self.content)
        # 过滤常见词
        stop_words = {"的", "是", "在", "了", "和", "與", "及", "的", "等", "**", "•", "—", "–"}
        self.keywords = [kw for kw in keywords_matches
                       if kw not in stop_words and len(kw) >= 2][:10]

    def _extract_sections(self):
        """提取章节信息"""
        section_pattern = r'^##\s*(.+)$'
        self.sections = re.findall(section_pattern, self.content, re.MULTILINE)

    def _auto_score(self):
        """自动评分（基于内容特征）"""

        # 1. 深度 (Depth)：基于内容长度、章节数、是否有数学公式
        depth_score = 5

        # 内容长度贡献（最高+3）
        length_score = min(3, self.content_length / 5000)
        depth_score += length_score

        # 章节数贡献（最高+2）
        section_score = min(2, len(self.sections) / 5)
        depth_score += section_score

        # 数学公式检测（LaTeX格式，最高+2）
        formula_patterns = [r'\\[a-zA-Z]', r'\$\$[^$]+\$\$', r'\$[^$]+\$', r'Eq\.\s*\d+']
        formula_count = sum(len(re.findall(p, self.content)) for p in formula_patterns)
        formula_score = min(2, formula_count / 10)
        depth_score += formula_score

        # 2. 完整性 (Completeness)：基于是否有摘要、关键词、多个章节
        completeness_score = 0

        if self.abstract:
            completeness_score += 2

        if self.keywords:
            completeness_score += 1

        if len(self.sections) >= 5:
            completeness_score += 2
        elif len(self.sections) >= 3:
            completeness_score += 1

        if "局限性" in self.content or "Limitations" in self.content:
            completeness_score += 2

        if "應用" in self.content or "Application" in self.content:
            completeness_score += 1

        # 3. 创新性 (Innovation)：基于arXiv年份、是否有"创新"、"首次"等词汇
        innovation_score = 5

        # 年份贡献
        if self.year:
            if int(self.year) >= 26:  # 2026年
                innovation_score += 3
            elif int(self.year) >= 25:  # 2025年
                innovation_score += 2
            elif int(self.year) >= 24:  # 2024年
                innovation_score += 1

        # 创新词汇检测
        innovation_keywords = ["創新", "創新", "首次", "新穎", "突破", "novel", "first", "breakthrough"]
        innovation_word_count = sum(1 for kw in innovation_keywords if kw in self.content)
        innovation_score += min(2, innovation_word_count * 0.5)

        # 4. 适用性 (Applicability)：基于量化交易关键词、实际应用场景
        applicability_score = 5

        # 量化交易关键词匹配
        quant_keyword_count = sum(1 for kw in QUANT_TRADING_KEYWORDS if kw in self.content)
        applicability_score += min(4, quant_keyword_count * 0.5)

        # 实验验证
        if "實驗" in self.content or "驗證" in self.content:
            applicability_score += 1

        # 保存分数
        self.scores = {
            "depth": min(10, max(1, int(depth_score))),
            "completeness": min(10, max(1, int(completeness_score))),
            "innovation": min(10, max(1, int(innovation_score))),
            "applicability": min(10, max(1, int(applicability_score)))
        }

        # 计算总分
        self.total_score = sum(self.scores[k] * SCORE_WEIGHTS[k] for k in SCORE_WEIGHTS)

    def to_dict(self):
        """转换为字典格式"""
        return {
            "file_name": self.file_name,
            "title": self.title[:80] if self.title else self.file_name,
            "arxiv_id": self.arxiv_id,
            "authors": self.authors,
            "scores": self.scores,
            "total_score": round(self.total_score, 2),
            "keywords": self.keywords[:5],
            "content_length": self.content_length,
            "sections_count": len(self.sections)
        }

# ==================== 主函数 ====================

def find_research_files():
    """找出所有研究报告文件"""
    research_files = []

    for file_path in PROJECTS_DIR.rglob("*research.md"):
        research_files.append(file_path)

    print(f"找到 {len(research_files)} 个研究报告文件")
    return research_files

def load_research_files(research_files):
    """加载所有研究报告"""
    papers = []

    for file_path in research_files:
        paper = ResearchPaper(file_path)
        if paper.load():
            papers.append(paper)

    print(f"成功加载 {len(papers)} 篇研究报告")
    return papers

def analyze_papers(papers):
    """分析所有论文"""
    print("\n=== 论文统计 ===")

    # 基本统计
    if papers:
        print(f"总论文数: {len(papers)}")
        print(f"平均内容长度: {int(statistics.mean([p.content_length for p in papers])):,} 字符")
        print(f"平均总分: {statistics.mean([p.total_score for p in papers]):.2f}/10")

        # 分数分布
        high_score = [p for p in papers if p.total_score >= 7.5]
        mid_score = [p for p in papers if 7.0 <= p.total_score < 7.5]
        low_score = [p for p in papers if p.total_score < 7.0]

        print(f"\n高分论文 (≥7.5): {len(high_score)} 篇 ({len(high_score)/len(papers)*100:.1f}%)")
        print(f"中分论文 (7.0-7.5): {len(mid_score)} 篇 ({len(mid_score)/len(papers)*100:.1f}%)")
        print(f"低分论文 (<7.0): {len(low_score)} 篇 ({len(low_score)/len(papers)*100:.1f}%)")
    else:
        print("没有找到论文")

    return papers

def analyze_keywords(papers):
    """分析关键词"""
    all_keywords = []

    for paper in papers:
        all_keywords.extend(paper.keywords)

    # 统计关键词频率
    keyword_counts = Counter(all_keywords)

    # 找出最常见的关键词（至少出现2次）
    top_keywords = [(kw, count) for kw, count in keyword_counts.most_common(50) if count >= 2]

    print(f"\n=== Top 30 关键词 (出现≥2次) ===")
    for i, (kw, count) in enumerate(top_keywords[:30], 1):
        print(f"{i:2d}. {kw}: {count} 次")

    return top_keywords

def analyze_trends(papers):
    """分析趋势（按arXiv年份）"""
    year_counts = defaultdict(int)

    for paper in papers:
        if paper.year:
            year = int(paper.year)
            year_counts[year] += 1

    print(f"\n=== 按年份分布 (20XX年) ===")
    for year in sorted(year_counts.keys()):
        print(f"  20{year}年: {year_counts[year]} 篇")

    return year_counts

def generate_summary(papers, top_keywords, year_counts, output_file):
    """生成综合摘要报告"""
    # 按总分排序
    sorted_papers = sorted(papers, key=lambda p: p.total_score, reverse=True)

    # 统计
    if papers:
        avg_scores = {
            dim: statistics.mean([p.scores[dim] for p in papers])
            for dim in SCORE_WEIGHTS.keys()
        }

        high_score = len([p for p in papers if p.total_score >= 7.5])
        mid_score = len([p for p in papers if 7.0 <= p.total_score < 7.5])
        low_score = len([p for p in papers if p.total_score < 7.0])
    else:
        avg_scores = {dim: 0 for dim in SCORE_WEIGHTS.keys()}
        high_score = mid_score = low_score = 0

    # Top 15 论文
    top_15 = sorted_papers[:15]

    # 生成报告
    report = f"""# 研究知识库综合分析报告

**生成时间：** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}
**数据范围：** 所有已完成的研究报告
**总论文数：** {len(papers)} 篇

---

## 📊 总体统计

### 基本指标

| 指标 | 数值 |
|------|------|
| 总论文数 | {len(papers)} 篇 |
| 平均内容长度 | {int(statistics.mean([p.content_length for p in papers])):,} 字符 |
| 平均总分 | {statistics.mean([p.total_score for p in papers]):.2f}/10 |
| 总字符数 | {sum(p.content_length for p in papers):,} |

### 分数分布

| 分数段 | 数量 | 占比 |
|--------|------|------|
| 高分 (≥7.5) | {high_score} | {high_score/len(papers)*100:.1f}% |
| 中分 (7.0-7.5) | {mid_score} | {mid_score/len(papers)*100:.1f}% |
| 低分 (<7.0) | {low_score} | {low_score/len(papers)*100:.1f}% |

### 各维度平均分

| 维度 | 平均分 | 权重 | 说明 |
|------|--------|------|------|
| 深度 (Depth) | {avg_scores['depth']:.2f}/10 | 30% | 技术复杂度和理论深度 |
| 完整性 (Completeness) | {avg_scores['completeness']:.2f}/10 | 25% | 分析覆盖面和细节程度 |
| 创新性 (Innovation) | {avg_scores['innovation']:.2f}/10 | 25% | 方法新颖性和突破性 |
| 适用性 (Applicability) | {avg_scores['applicability']:.2f}/10 | 20% | 实际应用价值 |

---

## 🏆 Top 15 高分论文

"""

    for i, paper in enumerate(top_15, 1):
        report += f"""
### {i}. [{paper.total_score:.2f}] {paper.title[:70]}...

**文件：** `{paper.file_name}`
**arXiv ID：** {paper.arxiv_id or 'N/A'}
**作者：** {paper.authors or 'N/A'}
**内容长度：** {paper.content_length:,} 字符

**评分详情：**
- 深度：{paper.scores['depth']}/10
- 完整性：{paper.scores['completeness']}/10
- 创新性：{paper.scores['innovation']}/10
- 适用性：{paper.scores['applicability']}/10

**关键词：** {', '.join(paper.keywords[:5]) if paper.keywords else 'N/A'}

---

"""

    # 关键词统计
    if top_keywords:
        report += """
## 🔑 关键词统计（出现≥2次）

| 排名 | 关键词 | 出现次数 |
|------|--------|----------|
"""
        for i, (kw, count) in enumerate(top_keywords[:30], 1):
            report += f"| {i} | {kw} | {count} |\n"

    # 年份分布
    if year_counts:
        report += """

## 📅 按年份分布（20XX年）

| 年份 | 论文数量 | 占比 |
|------|----------|------|
"""
        total_by_year = sum(year_counts.values())
        for year in sorted(year_counts.keys()):
            report += f"| 20{year}年 | {year_counts[year]} | {year_counts[year]/total_by_year*100:.1f}% |\n"

    # 应用建议
    report += """

## 💡 知识应用建议

### 高优先级应用（高分论文）

以下研究具有最高的实际应用价值，建议优先深入研究：

"""

    for paper in top_15[:5]:
        report += f"- **{paper.title[:60]}...** ({paper.total_score:.2f}/10)\n"
        if paper.keywords:
            report += f"  关键词：{', '.join(paper.keywords[:3])}\n"

    report += """

### 知识库改进方向

基于分析结果，知识库的改进方向：

1. **提升完整性**：完整性平均分较低（{avg_scores['completeness']:.2f}/10），建议：
   - 在研究报告中添加"局限性"章节
   - 增加"实际应用场景"分析
   - 完善实验验证部分

2. **量化应用聚焦**：适用性平均分为 {avg_scores['applicability']:.2f}/10，建议：
   - 增加量化交易相关领域的研究
   - 在现有研究中识别量化应用潜力
   - 建立应用案例库

3. **持续跟踪前沿**：创新性平均分为 {avg_scores['innovation']:.2f}/10，建议：
   - 持续追踪最新arXiv论文
   - 关注突破性方法
   - 建立创新方法库

---

**报告生成时间：** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
**下次更新：** 建议每1-2周更新一次
"""

    # 保存报告
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(report, encoding='utf-8')
    print(f"\n✅ 综合报告已生成: {output_file}")

# ==================== 主程序 ====================

def main():
    print("=" * 60)
    print("研究知识库综合分析")
    print("=" * 60)

    # 1. 找出所有研究报告文件
    research_files = find_research_files()

    # 2. 加载所有研究报告
    papers = load_research_files(research_files)

    # 3. 分析论文
    papers = analyze_papers(papers)

    # 4. 关键词分析
    top_keywords = analyze_keywords(papers)

    # 5. 趋势分析
    year_counts = analyze_trends(papers)

    # 6. 生成综合报告
    output_file = OUTPUT_DIR / f"research-knowledge-base-summary-{datetime.now().strftime('%Y%m%d')}.md"
    generate_summary(papers, top_keywords, year_counts, output_file)

    # 7. 保存JSON数据（便于后续处理）
    json_file = output_file.with_suffix('.json')
    papers_data = [p.to_dict() for p in papers]
    json_file.write_text(json.dumps(papers_data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"✅ JSON数据已保存: {json_file}")

    print("\n" + "=" * 60)
    print("✅ 综合分析完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
