#!/usr/bin/env python3
"""
Generate Weekly Summary

Generate a weekly research summary report.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import Counter

KANBAN_DIR = Path.home() / ".openclaw" / "workspace" / "kanban"
RESEARCH_OUTPUT_DIR = KANBAN_DIR / "projects"
DEFAULT_TEMPLATE = Path(__file__).parent.parent / "references" / "summary_template.md"

def load_scores():
    """Load all .score files."""
    scores = []

    if RESEARCH_OUTPUT_DIR.exists():
        for score_file in RESEARCH_OUTPUT_DIR.rglob("*.score"):
            try:
                with open(score_file, "r", encoding="utf-8") as f:
                    score_obj = json.load(f)
                    scores.append(score_obj)
            except:
                pass

    return scores

def load_insights():
    """Load all .insights files."""
    insights_list = {}

    if RESEARCH_OUTPUT_DIR.exists():
        for insights_file in RESEARCH_OUTPUT_DIR.rglob("*.insights"):
            try:
                with open(insights_file, "r", encoding="utf-8") as f:
                    insights_obj = json.load(f)
                    task_id = insights_obj.get("task_id", "")
                    insights_list[task_id] = insights_obj.get("insights", {})
            except:
                pass

    return insights_list

def generate_summary(days=7, min_score=7.0, template_path=None):
    """Generate weekly summary.

    Returns:
        Summary object
    """
    # Load data
    scores = load_scores()
    insights_list = load_insights()

    if not scores:
        print("❌ 未找到評分文件")
        return None

    # Filter by time and score
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    filtered_scores = [
        s for s in scores
        if s.get("overall", 0) >= min_score
        and datetime.fromisoformat(s["timestamp"]) > cutoff
    ]

    if not filtered_scores:
        print(f"❌ 過去 {days} 天內無符合條件的研究 (分數 >= {min_score})")
        return None

    # Sort by score (descending)
    sorted_by_score = sorted(filtered_scores, key=lambda x: x["overall"], reverse=True)
    top_10 = sorted_by_score[:10]

    # Load template
    if template_path is None:
        template_path = DEFAULT_TEMPLATE

    try:
        with open(template_path, "r", encoding="utf-8") as f:
            template = f.read()
    except Exception as e:
        print(f"❌ 讀取模板失敗: {e}")
        return None

    # Calculate statistics
    avg_score = sum([s["overall"] for s in filtered_scores]) / len(filtered_scores)
    high_quality_count = sum(1 for s in filtered_scores if s["overall"] >= 8.0)

    # Quality distribution
    quality_levels = Counter([s["quality_level"] for s in filtered_scores])
    quality_dist = " | ".join([
        f"{level}: {count}" for level, count in quality_levels.items()
    ])

    # Trend
    prev_scores = [
        s for s in scores
        if datetime.fromisoformat(s["timestamp"]) < cutoff
    ]
    if prev_scores:
        prev_avg = sum([s["overall"] for s in prev_scores]) / len(prev_scores)
        trend = f"📈 上升 ({avg_score - prev_avg:+.2f})" if avg_score > prev_avg + 0.5 else \
                f"📉 下降 ({avg_score - prev_avg:+.2f})" if avg_score < prev_avg - 0.5 else \
                f"➡️ 穩定 ({avg_score - prev_avg:+.2f})"
    else:
        trend = "無法判斷趨勢"

    # Top 10 research
    top_10_research = []
    for i, score_obj in enumerate(top_10, 1):
        insights = insights_list.get(score_obj.get("task_id", ""), {})
        core_method = insights.get("core_method", "N/A")[:80]
        key_results = insights.get("key_results", ["N/A"])[0][:80] if insights.get("key_results") else "N/A"

        top_10_research.append(f"""
{i}. **{score_obj['task_id']}** - {score_obj['overall']:.2f} - {score_obj['quality_level']}
   - **核心方法:** {core_method}
   - **關鍵結果:** {key_results}
   - **應用:** {len(insights.get('applications', []))} 個
   - **限制:** {len(insights.get('limitations', []))} 個
""")

    top_10_research = "\n".join(top_10_research)

    # New methods
    new_methods = []
    for score_obj in sorted_by_score[:20]:
        insights = insights_list.get(score_obj.get("task_id", ""), {})
        quality = score_obj.get("quality_level", "")

        if "High Quality" in quality or "Good Quality" in quality:
            core_method = insights.get("core_method", "")
            if core_method and core_method not in new_methods:
                new_methods.append(f"- {core_method} ({score_obj['task_id']})")

    new_methods_str = "\n".join(new_methods[:10])

    # Application themes
    all_apps = []
    for score_obj in filtered_scores:
        insights = insights_list.get(score_obj.get("task_id", ""), {})
        all_apps.extend(insights.get("applications", []))

    app_counter = Counter(all_apps)
    top_apps = app_counter.most_common(10)

    application_themes = []
    for app, count in top_apps:
        application_themes.append(f"- **{app}**: {count} 個研究")

    application_themes_str = "\n".join(application_themes)

    # Trend summary
    trend_summary = f"研究品質{trend} (平均分從 {prev_avg:.2f} {trend.split()[0]})" if prev_scores else "無法判斷趨勢"

    # Recommendations
    recommendations = []

    if high_quality_count >= len(filtered_scores) * 0.3:
        recommendations.append("- 研究品質優秀，保持現有研究方向")
    elif high_quality_count >= len(filtered_scores) * 0.1:
        recommendations.append("- 高品質研究比例良好，繼續提升")
    else:
        recommendations.append("- 品質有待提升，關注重研究深度和完整性")

    if app_counter:
        top_app = top_apps[0][0]
        recommendations.append(f"- 應用領域「{top_app}」研究活躍，可深入探索")

    # Limit to 5 recommendations
    recommendations_str = "\n".join(recommendations[:5])

    # Fill template
    date_range = f"{(datetime.now(timezone.utc) - timedelta(days=days)).strftime('%Y-%m-%d')} to {datetime.now(timezone.utc).strftime('%Y-%m-%d')}"

    summary_content = template.format(
        date_range=date_range,
        total_completed=len(filtered_scores),
        avg_score=avg_score,
        trend_summary=trend_summary,
        top_10_research=top_10_research,
        new_methods=new_methods_str,
        application_themes=application_themes_str,
        high_quality_count=high_quality_count,
        high_quality_threshold=8.0,
        quality_distribution=quality_dist,
        trend=trend,
        recommendations=recommendations_str,
        timestamp=datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    )

    return {
        "summary": summary_content,
        "statistics": {
            "total": len(filtered_scores),
            "avg_score": avg_score,
            "high_quality": high_quality_count,
            "trend": trend
        }
    }

def save_summary(summary_content, output_path=None):
    """Save summary to file."""
    if output_path is None:
        timestamp = datetime.now().strftime("%Y-%m-%d")
        output_path = KANBAN_DIR / f"weekly-summary-{timestamp}.md"

    output_file = Path(output_path)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(summary_content)

    print(f"✅ 摘要已保存: {output_file}")

    return str(output_file)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate weekly summary")
    parser.add_argument(
        "--days", "-d",
        type=int,
        default=7,
        help="Number of days to summarize (default: 7)"
    )
    parser.add_argument(
        "--min-score", "-m",
        type=float,
        default=7.0,
        help="Minimum score to include (default: 7.0)"
    )
    parser.add_argument(
        "--template", "-t",
        help="Path to custom template"
    )
    parser.add_argument(
        "--output", "-o",
        help="Save summary to file"
    )
    args = parser.parse_args()

    result = generate_summary(
        days=args.days,
        min_score=args.min_score,
        template_path=args.template
    )

    if result:
        save_summary(result["summary"], args.output)
