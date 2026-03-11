#!/usr/bin/env python3
"""
Maintenance Check

整合所有系統維護任務的統一腳本。
在心跳時調用，執行所有維護檢查。
"""

import sys
import json
from pathlib import Path

# Skills 路徑
SKILLS_DIR = Path.home() / ".openclaw" / "workspace" / "skills"

def run_skill(script_path, *args):
    """運行 skill 腳本並返回結果。"""
    import subprocess

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)] + list(args),
            capture_output=True,
            text=True,
            timeout=60
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

def check_dependencies():
    """檢查 Scout 依賴。"""
    script = SKILLS_DIR / "scout-dependency-manager" / "scripts" / "check_dependencies.py"
    result = run_skill(script)

    print("=" * 60)
    print("🔍 Scout 依賴檢查")
    print("=" * 60)
    print(result["stdout"])

    if result["stderr"]:
        print(result["stderr"])

    return result["success"]

def check_timeouts():
    """檢查任務超時。"""
    script = SKILLS_DIR / "task-timeout-monitor" / "scripts" / "check_timeouts.py"
    result = run_skill(script, "--hours", "24")

    print()
    print("=" * 60)
    print("⏰ 任務超時檢查")
    print("=" * 60)
    print(result["stdout"])

    if result["stderr"]:
        print(result["stderr"])

    return result["success"]

def identify_anomalies():
    """識別任務異常。"""
    script = SKILLS_DIR / "task-state-enhancer" / "scripts" / "identify_anomalies.py"
    result = run_skill(script)

    print()
    print("=" * 60)
    print("⚠️  任務異常檢測")
    print("=" * 60)
    print(result["stdout"])

    if result["stderr"]:
        print(result["stderr"])

    return result["success"]

def validate_rules():
    """驗證優先級規則。"""
    script = SKILLS_DIR / "priority-rule-engine" / "scripts" / "validate_rules.py"
    result = run_skill(script)

    print()
    print("=" * 60)
    print("📋 優先級規則驗證")
    print("=" * 60)
    print(result["stdout"])

    if result["stderr"]:
        print(result["stderr"])

    return result["success"]

def generate_state_report():
    """生成任務狀態報告。"""
    script = SKILLS_DIR / "task-state-enhancer" / "scripts" / "state_report.py"
    result = run_skill(script)

    print()
    print("=" * 60)
    print("📊 任務狀態報告")
    print("=" * 60)
    print(result["stdout"])

    if result["stderr"]:
        print(result["stderr"])

    return result["success"]

def run_all():
    """運行所有維護檢查。"""
    print()
    print("🔧 開始系統維護檢查")
    print("=" * 60)
    print()

    results = {
        "dependencies": check_dependencies(),
        "timeouts": check_timeouts(),
        "anomalies": identify_anomalies(),
        "rules": validate_rules(),
        "state": generate_state_report()
    }

    print()
    print("=" * 60)
    print("✅ 維護檢查完成")
    print("=" * 60)
    print()

    success_count = sum(1 for r in results.values() if r)
    total_count = len(results)

    print(f"總結: {success_count}/{total_count} 個檢查通過")

    if success_count < total_count:
        print()
        print("⚠️  部分檢查失敗，請查看上述輸出詳情")

        # 返回非 0 狀態碼
        sys.exit(1)

if __name__ == "__main__":
    # 命令行參數
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "dependencies":
            check_dependencies()
        elif command == "timeouts":
            check_timeouts()
        elif command == "anomalies":
            identify_anomalies()
        elif command == "rules":
            validate_rules()
        elif command == "state":
            generate_state_report()
        else:
            print(f"未知命令: {command}")
            print()
            print("可用命令:")
            print("  dependencies  - 檢查 Scout 依賴")
            print("  timeouts      - 檢查任務超時")
            print("  anomalies     - 識別任務異常")
            print("  rules         - 驗證優先級規則")
            print("  state         - 生成任務狀態報告")
            print("  (無參數)     - 運行所有檢查")
            sys.exit(1)
    else:
        # 運行所有檢查
        run_all()
