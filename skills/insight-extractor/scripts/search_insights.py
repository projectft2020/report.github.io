#!/usr/bin/env python3
"""
Search Insights

Query extracted insights.
"""

import sys
import json
from pathlib import Path

KANBAN_DIR = Path.home() / ".openclaw" / "workspace" / "kanban"
RESEARCH_OUTPUT_DIR = KANBAN_DIR / "projects"

def load_insights():
    """Load all .insights files."""
    insights = []

    if RESEARCH_OUTPUT_DIR.exists():
        for insights_file in RESEARCH_OUTPUT_DIR.rglob("*.insights"):
            try:
                with open(insights_file, "r", encoding="utf-8") as f:
                    insights_obj = json.load(f)
                    insights.append(insights_obj)
            except:
                pass

    return insights

def search_insights(query, limit=10):
    """Search insights by query.

    Returns:
        List of matching insights with relevance scores
    """
    all_insights = load_insights()

    if not all_insights:
        print("❌ 未找到洞察文件")
        return []

    # Prepare query terms
    query_terms = query.lower().split()

    # Score each insight
    scored_insights = []

    for insights_obj in all_insights:
        score = 0
        insights = insights_obj.get("insights", {})

        # Search in core method
        if "core_method" in insights:
            method = insights["core_method"].lower()
            for term in query_terms:
                if term in method:
                    score += 2

        # Search in key results
        if "key_results" in insights:
            for result in insights["key_results"]:
                result_lower = result.lower()
                for term in query_terms:
                    if term in result_lower:
                        score += 1

        # Search in applications
        if "applications" in insights:
            for app in insights["applications"]:
                app_lower = app.lower()
                for term in query_terms:
                    if term in app_lower:
                        score += 1

        # Search in limitations
        if "limitations" in insights:
            for lim in insights["limitations"]:
                lim_lower = lim.lower()
                for term in query_terms:
                    if term in lim_lower:
                        score += 0.5

        if score > 0:
            scored_insights.append({
                "insights_obj": insights_obj,
                "relevance_score": score,
                "task_id": insights_obj.get("task_id", "")
            })

    # Sort by relevance
    sorted_insights = sorted(scored_insights, key=lambda x: x["relevance_score"], reverse=True)

    return sorted_insights[:limit]

def display_results(results, query, limit):
    """Display search results."""
    if not results:
        print(f"❌ 無匹配的洞察: {query}")
        return []

    print("=" * 70)
    print(f"🔍 洞察搜索結果: {query}")
    print("=" * 70)
    print()

    print(f"找到 {len(results)} 個匹配研究 (最多 {limit} 個)")
    print()

    # Display results
    for i, result in enumerate(results, 1):
        insights_obj = result["insights_obj"]
        insights = insights_obj.get("insights", {})

        print(f"{i}. {result['task_id']:30s} (相關度: {result['relevance_score']})")
        print(f"   核心方法: {insights.get('core_method', 'N/A')[:60]}")
        print(f"   關鍵結果: {insights.get('key_results', ['N/A'])[0][:60] if insights.get('key_results') else 'N/A'}")
        print(f"   應用: {len(insights.get('applications', []))} 個, 限制: {len(insights.get('limitations', []))} 個")
        print()

    print("=" * 70)

    return results

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Search insights")
    parser.add_argument(
        "query",
        help="Search query"
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=10,
        help="Maximum results (default: 10)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Save results to file"
    )
    args = parser.parse_args()

    if not args.query:
        print("錯誤: 必須指定查詢")
        sys.exit(1)

    results = search_insights(args.query, limit=args.limit)
    results = display_results(results, args.query, args.limit)

    if args.output:
        import json
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n✅ 搜索結果已保存: {args.output}")
