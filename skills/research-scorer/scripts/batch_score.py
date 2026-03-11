#!/usr/bin/env python3
"""
Batch Score Research Reports

Score multiple research reports in a directory.
"""

import sys
import json
from pathlib import Path

def score_directory(directory, recursive=False, min_score=None, verbose=False):
    """Score all research reports in a directory.

    Returns:
        Summary statistics and scored research list
    """
    dir_path = Path(directory)

    if not dir_path.exists():
        print(f"❌ 目錄不存在: {directory}")
        return None

    # Find research files
    if recursive:
        research_files = list(dir_path.rglob("*-research.md"))
    else:
        research_files = list(dir_path.glob("*-research.md"))

    if not research_files:
        print("❌ 未找到研究報告文件")
        return None

    print(f"找到 {len(research_files)} 個研究報告")
    print()

    # Import score_research
    import score_research

    scored = []
    skipped = []

    for i, research_file in enumerate(research_files, 1):
        if verbose:
            print(f"[{i}/{len(research_files)}] 評分: {research_file.name}")

        score_obj = score_research.score_research(
            str(research_file),
            verbose=False
        )

        if score_obj and (min_score is None or score_obj["overall"] >= min_score):
            scored.append(score_obj)
        elif score_obj:
            skipped.append({
                "file": research_file.name,
                "score": score_obj["overall"],
                "reason": f"低於閾值 {min_score}"
            })
            if verbose:
                print(f"  ⏭ 跳過: 分數 {score_obj['overall']} < {min_score}")

    # Generate summary
    print()
    print("=" * 60)
    print("批量評分摘要")
    print("=" * 60)
    print()

    # Statistics
    if scored:
        overall_scores = [s["overall"] for s in scored]
        print(f"✅ 評分完成: {len(scored)} 個")
        print(f"⏭ 跳過: {len(skipped)} 個")
        print()
        print("分數統計:")
        print(f"  平均分: {sum(overall_scores) / len(overall_scores):.2f}")
        print(f"  最高分: {max(overall_scores):.2f}")
        print(f"  最低分: {min(overall_scores):.2f}")

        # Quality distribution
        quality_levels = [s["quality_level"] for s in scored]
        for level in ["High Quality", "Good Quality", "Moderate Quality", "Low Quality"]:
            count = quality_levels.count(level)
            pct = (count / len(scored) * 100) if scored else 0
            print(f"  {level:15s}: {count:3d} ({pct:5.1f}%)")
        print()

        # Top 10 highest scored
        sorted_by_score = sorted(scored, key=lambda x: x["overall"], reverse=True)
        print("高分研究 (Top 10):")
        for i, score_obj in enumerate(sorted_by_score[:10], 1):
            print(f"  {i}. {score_obj['task_id']:25s} - {score_obj['overall']:5.2f} - {score_obj['quality_level']}")

    print()
    if skipped and min_score:
        print("跳過的研究 (低於閾值):")
        for item in skipped:
            print(f"  - {item['file']:40s} ({item['score']:.2f})")

    return {
        "scored": scored,
        "skipped": skipped,
        "summary": {
            "count": len(scored),
            "average": sum([s["overall"] for s in scored]) / len(scored) if scored else 0,
            "max": max([s["overall"] for s in scored]) if scored else 0,
            "min": min([s["overall"] for s in scored]) if scored else 0
        }
    }

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Batch score research reports")
    parser.add_argument(
        "directory",
        help="Directory containing research files"
    )
    parser.add_argument(
        "--recursive", "-r",
        action="store_true",
        help="Score in subdirectories"
    )
    parser.add_argument(
        "--min-score", "-m",
        type=float,
        help="Only show scores >= threshold"
    )
    parser.add_argument(
        "--output", "-o",
        help="Save summary to file"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed progress"
    )
    args = parser.parse_args()

    if not args.directory:
        print("錯誤: 必須指定目錄")
        sys.exit(1)

    result = score_directory(
        args.directory,
        recursive=args.recursive,
        min_score=args.min_score,
        verbose=args.verbose
    )

    if result and args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n✅ 摘要已保存: {args.output}")
