#!/usr/bin/env python3
"""
Research Quality Check

研究品質檢查：自動評分研究報告並提取洞察。
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone

# Skills 路徑
SKILLS_DIR = Path.home() / ".openclaw" / "workspace" / "skills"
KANBAN_DIR = Path.home() / ".openclaw" / "workspace" / "kanban"
RESEARCH_OUTPUT_DIR = KANBAN_DIR / "projects"

def run_skill(script_path, *args):
    """運行 skill 腳本並返回結果。"""
    import subprocess

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)] + list(args),
            capture_output=True,
            text=True,
            timeout=120
        )

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": "Timeout",
            "code": -1
        }

def find_recent_research(hours=24):
    """查找最近完成的研究報告。"""
    cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=hours) - timedelta(hours=8)  # 調整時區

    research_files = []

    for research_file in RESEARCH_OUTPUT_DIR.rglob("*-research.md"):
        try:
            # 獲取文件修改時間
            mod_time = datetime.fromtimestamp(research_file.stat().st_mtime)

            if mod_time > cutoff:
                research_files.append(research_file)
        except:
            continue

    return research_files

def score_research(research_file):
    """評分研究報告。"""
    script = SKILLS_DIR / "research-scorer" / "scripts" / "score_research.py"

    # 檢查是否已經評分過
    score_file = research_file.parent / f"{research_file.stem}.score"
    if score_file.exists():
        print(f"⏭  已評分: {research_file.name}")
        return True

    result = run_skill(script, str(research_file))

    if result["success"]:
        print(f"✅ 評分成功: {research_file.name}")

        # 如果分數 >= 7.0，自動提取洞察
        try:
            with open(score_file, "r") as f:
                score_obj = json.load(f)

            if score_obj.get("overall", 0) >= 7.0:
                print(f"   → 高品質研究 (7.0+)，自動提取洞察...")
                extract_insights(research_file)
        except:
            pass

        return True
    else:
        print(f"❌ 評分失敗: {research_file.name}")
        if result["stderr"]:
            print(f"   {result['stderr']}")
        return False

def extract_insights(research_file):
    """提取研究洞察。"""
    script = SKILLS_DIR / "insight-extractor" / "scripts" / "extract_insights.py"

    # 檢查是否已經提取過
    insights_file = research_file.parent / f"{research_file.stem}.insights"
    if insights_file.exists():
        print(f"   ⏭  已提取洞察")
        return True

    result = run_skill(script, str(research_file))

    if result["success"]:
        print(f"   ✅ 洞察提取成功")
        return True
    else:
        print(f"   ❌ 洞察提取失敗")
        if result["stderr"]:
            print(f"      {result['stderr']}")
        return False

def run_quality_check(hours=24):
    """運行研究品質檢查。"""
    print()
    print("=" * 60)
    print("📊 研究品質檢查")
    print("=" * 60)
    print()

    # 查找最近的研究
    research_files = find_recent_research(hours)

    if not research_files:
        print(f"✅ 最近 {hours} 小時內無新的研究報告")
        return

    print(f"找到 {len(research_files)} 個研究報告（最近 {hours} 小時）")
    print()

    # 評分每個研究
    success_count = 0
    failed_count = 0

    for research_file in research_files:
        print(f"📄 {research_file.name}")

        if score_research(research_file):
            success_count += 1
        else:
            failed_count += 1

        print()

    # 總結
    print("=" * 60)
    print("✅ 品質檢查完成")
    print("=" * 60)
    print()

    print(f"總結: {success_count} 個成功, {failed_count} 個失敗")

    if failed_count > 0:
        print("⚠️  部分研究評分失敗，請查看上述輸出")

def show_statistics():
    """顯示評分統計。"""
    script = SKILLS_DIR / "research-scorer" / "scripts" / "score_statistics.py"

    print()
    print("=" * 60)
    print("📈 評分統計報告")
    print("=" * 60)
    print()

    result = run_skill(script)

    print(result["stdout"])

    if result["stderr"]:
        print(result["stderr"])

if __name__ == "__main__":
    from datetime import timedelta

    import argparse

    parser = argparse.ArgumentParser(description="Research quality check")
    parser.add_argument(
        "--hours",
        type=int,
        default=24,
        help="Check research completed in last N hours (default: 24)"
    )
    parser.add_argument(
        "--stats", "-s",
        action="store_true",
        help="Show scoring statistics instead of checking"
    )
    args = parser.parse_args()

    if args.stats:
        show_statistics()
    else:
        run_quality_check(hours=args.hours)
