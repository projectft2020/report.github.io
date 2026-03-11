#!/usr/bin/env python3
"""
Batch Extract Insights

Extract insights from all research reports in a directory.
"""

import sys
from pathlib import Path

def batch_extract(directory, recursive=False, verbose=False):
    """Extract insights from all research reports.

    Returns:
        Summary statistics
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

    # Import extract_insights
    import extract_insights

    extracted = []
    failed = []

    for i, research_file in enumerate(research_files, 1):
        if verbose:
            print(f"[{i}/{len(research_files)}] 提取: {research_file.name}")

        insights = extract_insights.extract_insights(
            str(research_file),
            verbose=False
        )

        if insights:
            extracted.append(insights)
        else:
            failed.append({
                "file": research_file.name,
                "reason": "提取失敗"
            })
            if verbose:
                print(f"  ❌ 提取失敗")

    # Generate summary
    print()
    print("=" * 60)
    print("批量提取摘要")
    print("=" * 60)
    print()

    print(f"✅ 成功提取: {len(extracted)} 個")
    print(f"❌ 提取失敗: {len(failed)} 個")

    if extracted:
        # Statistics
        confidence_levels = [s["confidence"] for s in extracted]
        print()
        print("提取統計:")
        print(f"  高置信度: {confidence_levels.count('high')} 個")
        print(f"  中置信度: {confidence_levels.count('medium')} 個")
        print(f"  低置信度: {confidence_levels.count('low')} 個")

        # Applications count
        app_counts = [len(s["insights"]["applications"]) for s in extracted]
        print()
        print(f"應用場景數量:")
        print(f"  平均: {sum(app_counts) / len(app_counts):.1f} 個/研究")
        print(f"  最多: {max(app_counts)} 個")
        print(f"  最少: {min(app_counts)} 個")

        # Limitations count
        lim_counts = [len(s["insights"]["limitations"]) for s in extracted]
        print()
        print(f"局限性數量:")
        print(f"  平均: {sum(lim_counts) / len(lim_counts):.1f} 個/研究")
        print(f"  最多: {max(lim_counts)} 個")
        print(f"  最少: {min(lim_counts)} 個")

    if failed:
        print()
        print("提取失敗的文件:")
        for item in failed:
            print(f"  - {item['file']:40s}")

    return {
        "extracted": extracted,
        "failed": failed,
        "summary": {
            "count": len(extracted),
            "success_rate": len(extracted) / len(research_files) if research_files else 0
        }
    }

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Batch extract insights")
    parser.add_argument(
        "directory",
        help="Directory containing research files"
    )
    parser.add_argument(
        "--recursive", "-r",
        action="store_true",
        help="Extract from subdirectories"
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

    result = batch_extract(
        args.directory,
        recursive=args.recursive,
        verbose=args.verbose
    )

    if result and args.output:
        import json
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n✅ 摘要已保存: {args.output}")
