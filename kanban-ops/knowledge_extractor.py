#!/usr/bin/env python3
"""
Knowledge Extractor - 研究報告知識點提取器

自動從研究報告中提取關鍵發現、關鍵詞和主題分類。

使用方式：
    python3 kanban-ops/knowledge_extractor.py
"""

import json
import re
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime


def print_header(title):
    """打印標題"""
    print("\n" + "=" * 100)
    print(f" {title}")
    print("=" * 100)


def print_section(title):
    """打印分區標題"""
    print(f"\n{title}")
    print("-" * 100)


def extract_key_findings(content):
    """提取關鍵發現"""
    findings = []

    if '## Key Findings' in content:
        findings_section = content.split('## Key Findings')[1].split('##')[0]

        # 提取每個發現
        lines = findings_section.split('\n')
        for line in lines:
            # 匹配 1. **Title** — Description
            match = re.search(r'(\d+)\.\s*\*\*([^*]+)\*\*\s*—\s*(.+)', line.strip())
            if match:
                num, title, desc = match.groups()
                findings.append({
                    'number': num,
                    'title': title.strip(),
                    'desc': desc.split('|')[0].strip() if '|' in desc else desc.strip(),
                    'raw': line.strip()
                })

    return findings


def analyze_keywords(findings):
    """分析關鍵詞"""
    keywords = Counter()

    for finding in findings:
        combined = (finding['title'] + ' ' + finding['desc']).lower()

        # 統計常見關鍵詞
        if 'timeframe' in combined:
            keywords['Timeframe'] += 1
        if 'filter' in combined:
            keywords['Filtering'] += 1
        if 'volatility' in combined:
            keywords['Volatility'] += 1
        if 'signal' in combined:
            keywords['Signal Quality'] += 1
        if 'trend' in combined:
            keywords['Trend Analysis'] += 1
        if 'volume' in combined:
            keywords['Volume'] += 1
        if 'risk' in combined:
            keywords['Risk Management'] += 1
        if 'ema' in combined or 'sma' in combined:
            keywords['Moving Averages'] += 1
        if 'futures' in combined:
            keywords['Futures'] += 1
        if 'ensemble' in combined or 'bayesian' in combined:
            keywords['Uncertainty Quantification'] += 1
        if 'rnd' in combined or 'inference' in combined:
            keywords['Uncertainty Quantification'] += 1

    return keywords


def classify_by_theme(findings):
    """按主題分類"""
    themes = {
        '多時間框架分析': [],
        '技術指標過濾': [],
        '市場特性分析': [],
        '信號質量優化': [],
        '不確定性量化': [],
        '風險管理': [],
    }

    for finding in findings:
        combined = (finding['title'] + ' ' + finding['desc']).lower()

        if 'timeframe' in combined:
            themes['多時間框架分析'].append(finding)
        if 'filter' in combined or 'ema' in combined or 'sma' in combined:
            themes['技術指標過濾'].append(finding)
        if 'volatility' in combined or 'futures' in combined:
            themes['市場特性分析'].append(finding)
        if 'signal' in combined:
            themes['信號質量優化'].append(finding)
        if 'ensemble' in combined or 'bayesian' in combined or 'rnd' in combined:
            themes['不確定性量化'].append(finding)
        if 'risk' in combined:
            themes['風險管理'].append(finding)

    return themes


def generate_knowledge_summary(directory="outputs"):
    """生成知識摘要"""
    print_header("研究報告知識點提取與匯總")

    # 掃描所有研究報告
    research_reports = []
    for filepath in Path(directory).glob('*research.md'):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            research_reports.append({
                'path': str(filepath),
                'filename': filepath.name,
                'content': content
            })
        except Exception as e:
            print(f"讀取 {filepath} 失敗: {e}")
            continue

    print(f"\n📁 找到 {len(research_reports)} 份研究報告")

    if not research_reports:
        print("\n沒有研究報告可以分析")
        return

    # 提取所有關鍵發現
    all_findings = []
    for report in research_reports:
        findings = extract_key_findings(report['content'])
        for finding in findings:
            finding['source'] = report['filename']
            all_findings.append(finding)

    print(f"🔍 提取 {len(all_findings)} 個關鍵發現")

    # 關鍵詞統計
    keywords = analyze_keywords(all_findings)

    print_section("📊 關鍵詞統計")
    for keyword, count in keywords.most_common():
        bar = '█' * count
        print(f"  {keyword:<25} : {count} {bar}")

    # 主題分類
    themes = classify_by_theme(all_findings)

    print_section("💡 知識主題地圖")
    for theme, findings in themes.items():
        if findings:
            print(f"\n{theme} ({len(findings)} 個發現):")
            print("  ──────────────────────────────────────────────────────────────")
            for i, finding in enumerate(findings[:3], 1):
                print(f"  {i}. {finding['title'][:70]}...")
            if len(findings) > 3:
                print(f"  ... 還有 {len(findings) - 3} 個發現")

    # 核心洞察
    print_section("📌 核心洞察")

    if keywords:
        top_keyword = keywords.most_common(1)[0]
        print(f"  • 最熱門的主題：{top_keyword[0]}（{top_keyword[1]} 次提及）")

        print(f"  • 知識覆蓋範圍：{len([k for k, c in keywords.items() if c > 0])} 個關鍵詞")

        print(f"  • 主題多樣性：{len([t for t, f in themes.items() if f])} 個主題類別")

    print("\n" + print_header.__doc__)
    print("🔧 後續改進建議")
    print("  • 自動生成知識圖譜（節點關聯）")
    print("  • 識別重複主題和衝突發現")
    print("  • 按時間分析研究趨勢")
    print("  • 與用戶偏好匹配")


def main():
    """主函數"""
    import sys
    directory = sys.argv[1] if len(sys.argv) > 1 else "outputs"
    generate_knowledge_summary(directory)


if __name__ == '__main__':
    main()
