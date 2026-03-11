#!/usr/bin/env python3
"""
Preview Summary

Preview summary content without saving.
"""

import sys

def preview_summary(days=7, min_score=7.0, template_path=None):
    """Preview summary content."""
    import generate_summary

    result = generate_summary.generate_summary(
        days=days,
        min_score=min_score,
        template_path=template_path
    )

    if result:
        print("=" * 70)
        print("每週摘要預覽")
        print("=" * 70)
        print()
        print(result["summary"])
        print()
        print("=" * 70)
        print("💡 預覽完成，不會保存文件")
        print("💡 保存摘要運行: python3 generate_summary.py --days 7")

        return True

    return False

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Preview summary")
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
    args = parser.parse_args()

    preview_summary(
        days=args.days,
        min_score=args.min_score,
        template_path=args.template
    )
