#!/usr/bin/env python3
"""
Scout Agent Health Check

Verify Scout Agent connectivity and configuration.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Default workspace paths
WORKSPACE_DIR = Path.home() / ".openclaw" / "workspace"
SCOUT_WORKSPACE = Path.home() / ".openclaw" / "workspace-scout"
KANBAN_DIR = WORKSPACE_DIR / "kanban"

def check_package(package_name):
    """Check if a package is installed."""
    try:
        import importlib
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False

def check_scout_workspace():
    """Check if Scout workspace exists and is accessible."""
    print("🔍 檢查 Scout 工作區...")

    if not SCOUT_WORKSPACE.exists():
        print(f"❌ Scout 工作區不存在: {SCOUT_WORKSPACE}")
        return False

    if not SCOUT_WORKSPACE.is_dir():
        print(f"❌ Scout 工作區不是目錄: {SCOUT_WORKSPACE}")
        return False

    print(f"✅ Scout 工作區: {SCOUT_WORKSPACE}")
    return True

def check_scout_config():
    """Check Scout Agent configuration files."""
    print()
    print("🔍 檢查 Scout 配置...")

    config_files = ["PREFERENCES.json", "SCAN_LOG.md"]

    missing = []
    present = []

    for config_file in config_files:
        file_path = SCOUT_WORKSPACE / config_file
        if file_path.exists():
            present.append(config_file)
            print(f"✅ {config_file}")
        else:
            missing.append(config_file)
            print(f"⚠️  {config_file} (缺失)")

    return len(missing) == 0

def check_kanban_tasks():
    """Check Kanban task counts."""
    print()
    print("🔍 檢查 Kanban 任務...")

    tasks_file = KANBAN_DIR / "tasks.json"

    if not tasks_file.exists():
        print(f"❌ tasks.json 不存在: {tasks_file}")
        return False

    try:
        with open(tasks_file, "r") as f:
            tasks = json.load(f)

        total = len(tasks)
        pending = sum(1 for t in tasks if t.get("status") == "pending")
        completed = sum(1 for t in tasks if t.get("status") == "completed")

        print(f"✅ 總任務: {total}")
        print(f"✅ 待辦: {pending}")
        print(f"✅ 已完成: {completed}")

        return True

    except Exception as e:
        print(f"❌ 讀取 tasks.json 失敗: {e}")
        return False

def check_last_scan():
    """Check last Scout scan timestamp."""
    print()
    print("🔍 檢查最後掃描...")

    scan_log = SCOUT_WORKSPACE / "SCAN_LOG.md"

    if not scan_log.exists():
        print("⚠️  SCAN_LOG.md 不存在 (無掃描記錄)")
        return False

    try:
        with open(scan_log, "r") as f:
            content = f.read()

        # Find last scan entry
        lines = content.split("\n")
        for line in reversed(lines):
            if line.strip().startswith("##"):
                print(f"✅ 最後掃描: {line.replace('##', '').strip()}")
                return True

        print("⚠️  未找到掃描記錄")
        return False

    except Exception as e:
        print(f"❌ 讀取 SCAN_LOG.md 失敗: {e}")
        return False

def run_health_check():
    """Run comprehensive Scout Agent health check."""
    print("=" * 60)
    print("🏥 Scout Agent 健康檢查")
    print("=" * 60)
    print()

    checks = {
        "pybloom_live": check_package("pybloom_live"),
        "workspace": check_scout_workspace(),
        "config": check_scout_config(),
        "kanban": check_kanban_tasks(),
        "scan_log": check_last_scan()
    }

    print()
    print("=" * 60)
    print("健康檢查結果")
    print("=" * 60)

    all_passed = True
    for name, result in checks.items():
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{name:20s} {status}")
        if not result:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print()
        print("🎉 所有檢查通過！Scout Agent 準備就緒")
        return True
    else:
        print()
        print("⚠️  部分檢查失敗，建議:")
        if not checks["pybloom_live"]:
            print("   - 運行: python3 install_dependencies.py")
        if not checks["workspace"]:
            print("   - 檢查 Scout 工作區路徑")
        if not checks["config"]:
            print("   - 初始化 Scout Agent 配置")
        return False

if __name__ == "__main__":
    success = run_health_check()
    sys.exit(0 if success else 1)
