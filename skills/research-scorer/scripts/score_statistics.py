#!/usr/bin/env python3
"""
Score Statistics

Analyze score distribution across all research.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter, defaultdict

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

def generate_statistics():
    """Generate score statistics report."""
    scores = load_scores()

    if not scores:
        print("❌ 未找到評分文件")
        return

    print("=" * 70)
    print("📊 評分統計報告")
    print("=" * 70)
    print()

    # Overall statistics
    overall_scores = [s["overall"] for s in scores]
    print("整體統計:")
    print("-" * 70)
    print(f"評分研究數量:    {len(scores)}")
    print(f"平均分:          {sum(overall_scores) / len(overall_scores):.2f}")
    print(f"中位數:          {sorted(overall_scores)[len(overall_scores)//2]:.2f}")
    print(f"最高分:          {max(overall_scores):.2f}")
    print(f"最低分:          {min(overall_scores):.2f}")
    print()

    # Dimension averages
    print("各維度平均分:")
    print("-" * 70)

    for dimension in ["depth", "completeness", "innovation", "applicability"]:
        dimension_scores = [s["scores"][dimension] for s in scores]
        avg_score = sum(dimension_scores) / len(dimension_scores)
        max_score = max(dimension_scores)
        min_score = min(dimension_scores)

        print(f"{dimension:20s}: 平均 {avg_score:5.2f}/10, 最高 {max_score:5.2f}, 最低 {min_score:5.2f}")

    print()

    # Quality distribution
    print("品質等級分佈:")
    print("-" * 70)

    quality_levels = Counter([s["quality_level"] for s in scores])
    total = len(scores)

    for level in ["High Quality", "Good Quality", "Moderate Quality", "Low Quality"]:
        count = quality_levels.get(level, 0)
        pct = (count / total * 100) if total > 0 else 0
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        print(f"{level:15s}: {count:3d} ({pct:5.1f}%) {bar}")

    print()

    # High-score research (>= 8.0)
    high_quality = [s for s in scores if s["overall"] >= 8.0]
    if high_quality:
        print(f"高品質研究 (分數 >= 8.0): {len(high_quality)} 個")
        print("-" * 70)
        for i, score_obj in enumerate(sorted(high_quality, key=lambda x: x["overall"], reverse=True)[:10], 1):
            print(f"{i:2d}. {score_obj['task_id']:25s} - {score_obj['overall']:5.2f}")
    else:
        print("無高品質研究")
    print()

    # Low-score research (< 6.0)
    low_quality = [s for s in scores if s["overall"] < 6.0]
    if low_quality:
        print(f"低品質研究 (分數 < 6.0): {len(low_quality)} 個")
        print("-" * 70)
        for i, score_obj in enumerate(sorted(low_quality, key=lambda x: x["overall"])[:10], 1):
            print(f"{i:2d}. {score_obj['task_id']:25s} - {score_obj['overall']:5.2f}")
    else:
        print("無低品質研究")
    print()

    # Time trend (last 30 scores)
    print("評分趨勢 (最近 30 個):")
    print("-" * 70)

    sorted_by_time = sorted(scores, key=lambda x: x["timestamp"], reverse=True)
    recent_30 = sorted_by_time[:30]

    if recent_30:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        times = [datetime.fromisoformat(s["timestamp"]) for s in recent_30]
        overall_scores = [s["overall"] for s in recent_30]

        # Create trend line
        plt.figure(figsize=(12, 4))
        plt.plot(range(len(overall_scores)), overall_scores, marker='o', linewidth=2, markersize=4)
        plt.axhline(y=8.0, color='g', linestyle='--', alpha=0.5, label='High Quality (8.0)')
        plt.axhline(y=6.0, color='y', linestyle='--', alpha=0.5, label='Moderate (6.0)')
        plt.xlabel('研究 (最近 -> 最早)')
        plt.ylabel('總分')
        plt.title('研究品質趨勢 (最近 30 個)')
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()

        # Save chart
        chart_file = RESEARCH_OUTPUT_DIR / "quality_trend.png"
        plt.savefig(chart_file, dpi=100)
        plt.close()

        print(f"✅ 趨勢圖已生成: {chart_file}")

        # Calculate trend
        if len(overall_scores) >= 10:
            first_half = overall_scores[:len(overall_scores)//2]
            second_half = overall_scores[len(overall_scores)//2:]

            avg_first = sum(first_half) / len(first_half)
            avg_second = sum(second_half) / len(second_half)

            if avg_second > avg_first + 0.5:
                print(f"趨勢: 📈 上升 (平均從 {avg_first:.2f} 提升到 {avg_second:.2f})")
            elif avg_second < avg_first - 0.5:
                print(f"趨勢: 📉 下降 (平均從 {avg_first:.2f} 下降到 {avg_second:.2f})")
            else:
                print(f"趨勢: ➡️ 穩定 (平均 {avg_first:.2f} -> {avg_second:.2f})")
        else:
            print("數據不足，無法判斷趨勢")
    else:
        print("數據不足，無法生成趨勢圖")

    print()
    print("=" * 70)
    print(f"報告生成時間: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 70)

if __name__ == "__main__":
    generate_statistics()
