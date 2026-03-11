#!/usr/bin/env python3
"""
Extract Insights

Extract structured insights from a research report.
"""

import sys
import re
import json
from pathlib import Path
from datetime import datetime, timezone

def extract_core_method(content):
    """Extract core method (1-2 sentences)."""
    # Look for method sections
    method_patterns = [
        r'#+\s*(方法|Method|核心方法|Core Method|技術|Technique|算法|Algorithm)\n+(.*?)(?=\n#+)',
        r'#+\s*(核心創新|Main Contribution|主要貢獻)\n+(.*?)(?=\n#+)',
        r'#+\s*(摘要|Abstract|總結)\n+(.*?)(?=\n#+)'
    ]

    for pattern in method_patterns:
        match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
        if match:
            text = match.group(1).strip()
            # Take first 1-2 sentences
            sentences = re.split(r'[。！？\.\?]', text)
            if sentences:
                result = sentences[0].strip()
                if len(sentences) > 1 and len(result) < 200:
                    result = result + "。" + sentences[1].strip()[:100]
                return result[:200]

    # Fallback: extract from first substantial paragraph
    paragraphs = content.split('\n\n')
    for para in paragraphs:
        if len(para.strip()) > 100 and len(para.strip()) < 500:
            sentences = re.split(r'[。！？\.\?]', para)
            if sentences:
                return sentences[0].strip()[:200]

    return "無法提取核心方法"

def extract_key_results(content):
    """Extract key results (1-2 sentences)."""
    # Look for results sections
    results_patterns = [
        r'#+\s*(結果|Results|實驗結果|Experimental Results|結論|Conclusion)\n+(.*?)(?=\n#+)',
        r'#+\s*(主要發現|Key Findings|核心貢獻)\n+(.*?)(?=\n#+)'
    ]

    for pattern in results_patterns:
        match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
        if match:
            text = match.group(1).strip()
            # Look for numerical results
            if re.search(r'\d+%|\d+\.\d+|\d+倍', text):
                sentences = re.split(r'[。！？\.\?]', text)
                if sentences:
                    return sentences[0].strip()[:200]

    # Fallback: extract metrics
    metrics = re.findall(r'(準確率|accuracy|改善|improvement|效果|performance)[:50]+.*?(\d+%|\d+\.\d+)', content, re.IGNORECASE)
    if metrics:
        return " ".join(metrics[:2])[:200]

    return "無法提取關鍵結果"

def extract_applications(content):
    """Extract applications (3-5 items)."""
    # Look for application sections
    app_patterns = [
        r'#+\s*(應用|Application|應用價值|Applications|實際應用|Practical Applications|使用場景|Use Cases)\n+(.*?)(?=\n#+)',
    ]

    applications = []

    for pattern in app_patterns:
        match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
        if match:
            text = match.group(1)
            # Extract list items
            items = re.findall(r'[-*]\s*(.+)', text)
            for item in items:
                clean_item = re.sub(r'[`*_\[\]]', '', item).strip()
                if len(clean_item) > 10 and len(clean_item) < 100:
                    if clean_item not in applications:
                        applications.append(clean_item)

            if applications:
                break

    # Fallback: keyword extraction
    app_keywords = ["應用", "application", "使用", "use", "部署", "deploy", "場景", "scenario"]
    if len(applications) < 3:
        for keyword in app_keywords:
            if keyword in content.lower():
                # Extract context around keyword
                matches = re.finditer(f'.{{0,200}}{keyword}.{{0,100}}', content, re.IGNORECASE)
                for match in matches:
                    app = match.group(0).strip()
                    if len(app) > 15 and len(app) < 100 and app not in applications:
                        applications.append(app)
                    if len(applications) >= 5:
                        break

    return applications[:5]

def extract_limitations(content):
    """Extract limitations (2-3 items)."""
    # Look for limitation sections
    lim_patterns = [
        r'#+\s*(局限性|Limitations|限制|挑戰|Challenges|未來工作|Future Work|注意事項|Considerations)\n+(.*?)(?=\n#+)',
    ]

    limitations = []

    for pattern in lim_patterns:
        match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
        if match:
            text = match.group(1)
            # Extract list items
            items = re.findall(r'[-*]\s*(.+)', text)
            for item in items:
                clean_item = re.sub(r'[`*_\[\]]', '', item).strip()
                if len(clean_item) > 10 and len(clean_item) < 150:
                    if clean_item not in limitations:
                        limitations.append(clean_item)

            if limitations:
                break

    # Fallback: keyword extraction
    lim_keywords = ["限制", "limitation", "缺點", "drawback", "問題", "issue", "挑戰", "challenge"]
    if len(limitations) < 2:
        for keyword in lim_keywords:
            if keyword in content.lower():
                matches = re.finditer(f'.{{0,150}}{keyword}.{{0,80}}', content, re.IGNORECASE)
                for match in matches:
                    lim = match.group(0).strip()
                    if len(lim) > 15 and len(lim) < 120 and lim not in limitations:
                        limitations.append(lim)
                    if len(limitations) >= 3:
                        break

    return limitations[:3]

def extract_related_papers(content):
    """Extract related arXiv papers."""
    # arXiv ID patterns
    arxiv_patterns = [
        r'arXiv:(\d{4}\.\d{4,5})',
        r'arxiv:(\d{4}\.\d{4,5})',
        r'(\d{4}\.\d{4,5})(?=v\d+|\.pdf|\s*\[)'
    ]

    papers = set()

    for pattern in arxiv_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            if len(match) == 2:
                arxiv_id = match[0]
            else:
                arxiv_id = match
            papers.add(arxiv_id)

    return list(papers)

def extract_insights(research_file, verbose=False):
    """Extract insights from research report.

    Returns:
        Insights object
    """
    research_path = Path(research_file)

    if not research_path.exists():
        print(f"❌ 研究文件不存在: {research_file}")
        return None

    # Load content
    try:
        with open(research_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"❌ 讀取研究文件失敗: {e}")
        return None

    # Extract insights
    insights = {
        "core_method": extract_core_method(content),
        "key_results": [extract_key_results(content)],
        "applications": extract_applications(content),
        "limitations": extract_limitations(content),
        "related_papers": extract_related_papers(content)
    }

    if verbose:
        print("=" * 60)
        print(f"🔍 提取洞察: {research_path.name}")
        print("=" * 60)
        print()
        print(f"核心方法: {insights['core_method']}")
        print(f"關鍵結果: {insights['key_results'][0] if insights['key_results'] else 'N/A'}")
        print(f"應用場景 ({len(insights['applications'])}):")
        for app in insights['applications']:
            print(f"  - {app}")
        print(f"局限性 ({len(insights['limitations'])}):")
        for lim in insights['limitations']:
            print(f"  - {lim}")
        print(f"相關論文 ({len(insights['related_papers'])}):")
        for paper in insights['related_papers']:
            print(f"  - arXiv:{paper}")
        print()

    # Prepare insights object
    task_id = re.search(r'(scout|task)-(\d+)', research_file)
    task_id = task_id.group(0) if task_id else research_path.stem

    insights_obj = {
        "research_file": str(research_path),
        "task_id": task_id,
        "insights": insights,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "extraction_method": "automatic",
        "confidence": "high" if len(insights['core_method']) > 50 else "medium"
    }

    # Save to .insights file
    insights_file = research_path.parent / f"{research_path.stem}.insights"
    with open(insights_file, "w", encoding="utf-8") as f:
        json.dump(insights_obj, f, indent=2, ensure_ascii=False)

    print(f"✅ 洞察已保存: {insights_file}")

    return insights_obj

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python3 extract_insights.py <research-file> [--verbose]")
        print()
        print("參數:")
        print("  research-file  研究報告文件路徑")
        print("  --verbose     顯示詳細提取")
        sys.exit(1)

    research_file = sys.argv[1]
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    extract_insights(research_file, verbose=verbose)
