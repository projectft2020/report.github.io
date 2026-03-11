#!/usr/bin/env python3
"""
Trigger Scout Agent Scan

Manually trigger Scout Agent topic discovery scan.
"""

import sys
import argparse
from pathlib import Path

SCOUT_WORKSPACE = Path.home() / ".openclaw" / "workspace-scout"
SCOUT_AGENT = SCOUT_WORKSPACE / "scout_agent.py"

def trigger_scan(force=False, quiet=False):
    """Trigger Scout Agent scan."""
    if not SCOUT_AGENT.exists():
        print(f"❌ Scout Agent 不存在: {SCOUT_AGENT}")
        return False

    if not quiet:
        print("=" * 60)
        print("🔍 觸發 Scout Agent 掃描")
        print("=" * 60)
        print()

    if force:
        if not quiet:
            print("⚡ 強制模式: 無視待辦任務數量")
        print()

    try:
        import subprocess

        cmd = [sys.executable, str(SCOUT_AGENT)]

        if force:
            cmd.append("--force-scan")

        result = subprocess.run(
            cmd,
            cwd=str(SCOUT_WORKSPACE),
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes
        )

        if result.returncode == 0:
            if not quiet:
                print("✅ Scout 掃描啟動成功")
                print()
                print("📊 掃描輸出:")
                print(result.stdout)
            return True
        else:
            print(f"❌ Scout 掃描啟動失敗")
            print(f"錯誤: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print(f"❌ Scout 掃描超時（超過 5 分鐘）")
        return False
    except Exception as e:
        print(f"❌ 觸發掃描時發生錯誤: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trigger Scout Agent scan")
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Force scan regardless of pending task count"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress verbose output"
    )
    args = parser.parse_args()

    success = trigger_scan(force=args.force, quiet=args.quiet)
    sys.exit(0 if success else 1)
