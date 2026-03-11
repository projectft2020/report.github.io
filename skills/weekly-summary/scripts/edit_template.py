#!/usr/bin/env python3
"""
Edit Summary Template

Open template in text editor for customization.
"""

import sys
import subprocess
from pathlib import Path

DEFAULT_TEMPLATE = Path(__file__).parent.parent / "references" / "summary_template.md"

def edit_template(template_path=None):
    """Open template in editor."""
    if template_path is None:
        template_path = DEFAULT_TEMPLATE

    template_file = Path(template_path)

    if not template_file.exists():
        print(f"❌ 模板文件不存在: {template_file}")
        return False

    print(f"📝 打開模板: {template_file}")
    print()
    print("編輯完成後，運行:")
    print(f"  python3 generate_summary.py --template {template_file}")

    # Open in default editor
    editors = ["code", "vim", "nano", "open"]
    for editor in editors:
        try:
            subprocess.run([editor, str(template_file)], check=True)
            return True
        except FileNotFoundError:
            continue

    print("❌ 未找到文字編輯器，請手動打開模板文件")
    return False

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Edit summary template")
    parser.add_argument(
        "--template", "-t",
        help="Path to template file (default: references/summary_template.md)"
    )
    args = parser.parse_args()

    edit_template(args.template)
