#!/usr/bin/env python3
"""
Filter by Score

Filter research reports by score threshold.
"""

import sys
import json
from pathlib import Path

KANBAN_DIR = Path.home() / ".openclaw" / "workspace" / "kanban"
RESEARCH_OUTPUT_DIR = KANBAN_DIR / "projects"

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

def filter_by_score(threshold=7.0, operator="ge"):
    """Filter research by score threshold.

    Args:
        threshold: Score threshold value
        operator: Comparison operator (gt, lt, ge, le)

    Returns:
        List of matching research
    """
    scores = load_scores()

    if not scores:
        print("❌ 未找到評分文件")
        return []

    # Filter based on operator
    filtered = []
    operator_map = {
        "gt": lambda x: x > threshold,
        "lt": lambda x: x < threshold,
        "ge": lambda x: x >= threshold,
        "le": lambda x: x <= threshold
    }

    filter_func = operator_map.get(operator, operator_map["ge"])

    for score_obj in scores:
        if filter_func(score_obj["overall"]):
            filtered.append(score_obj)

    return filtered

def display_filtered(filtered, threshold, operator):
    """Display filtered results."""
    if not filtered:
        print(f"✅ 無研究分數符合條件: {operator} {threshold}")
        return []

    print("=" * 70)
    print(f"🔍 研究過濾結果 (條件: {operator} {threshold})")
    print("=" * 70)
    print()

    print(f"匹配研究數量: {len(filtered)}")
    print()

    # Sort by score (descending)
    sorted_by_score = sorted(filtered, key=lambda x: x["overall"], reverse=True)

    # Display top 20
    for i, score_obj in enumerate(sorted_by_score[:20], 1):
        print(f"{i:2d}. {score_obj['task_id']:25s} - {score_obj['overall']:5.2f} - {score_obj['quality_level']}")
        print(f"     文件: {Path(score_obj['research_file']).name}")
        if score_obj.get("notes"):
            print(f"     說明: {'; '.join(score_obj['notes'][:2])}")
        print()

    if len(sorted_by_score) > 20:
        print(f"... 還有 {len(sorted_by_score) - 20} 個研究")

    print()
    print("=" * 70)

    return sorted_by_score

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Filter research by score")
    parser.add_argument(
        "--threshold", "-t",
        type=float,
        default=7.0,
        help="Score threshold (default: 7.0)"
    )
    parser.add_argument(
        "--operator", "-op",
        choices=["gt", "lt", "ge", "le"],
        default="ge",
        help="Comparison operator (default: ge)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Save filtered list to file"
    )
    args = parser.parse_args()

    filtered = filter_by_score(threshold=args.threshold, operator=args.operator)
    filtered = display_filtered(filtered, args.threshold, args.operator)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(filtered, f, indent=2, ensure_ascii=False)
        print(f"\n✅ 過濾結果已保存: {args.output}")
