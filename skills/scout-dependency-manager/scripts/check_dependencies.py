#!/usr/bin/env python3
"""
Check Scout Agent Dependencies

Checks if required Scout Agent packages are installed.
"""

import sys
import importlib

# Required Scout Agent dependencies
REQUIRED_PACKAGES = {
    "pybloom_live": "Bloom filter for Scout Agent expansion"
}

def check_package(package_name):
    """Check if a Python package is installed."""
    try:
        if package_name == "pybloom_live":
            import pybloom_live
            return True, f"pybloom_live (version {pybloom_live.__version__})" if hasattr(pybloom_live, "__version__") else "pybloom_live"
        else:
            importlib.import_module(package_name)
            return True, package_name
    except ImportError:
        return False, None

def check_dependencies():
    """Check all required Scout Agent dependencies."""
    print("🔍 檢查 Scout Agent 依賴...")
    print()

    installed = []
    missing = []

    for package, description in REQUIRED_PACKAGES.items():
        is_installed, info = check_package(package)
        if is_installed:
            installed.append(info)
            print(f"✅ {info:30s} - {description}")
        else:
            missing.append(package)
            print(f"❌ {package:30s} - {description} (未安裝)")

    print()
    print("=" * 60)
    print(f"總計: {len(installed)} 已安裝, {len(missing)} 缺失")
    print("=" * 60)

    if missing:
        print()
        print("⚠️  缺失依賴:")
        for pkg in missing:
            print(f"   - {pkg}")
        print()
        print("💡 安裝方法: python3 install_dependencies.py")
    else:
        print()
        print("✅ 所有 Scout Agent 依賴已安裝")

    return {
        "installed": installed,
        "missing": missing,
        "all_present": len(missing) == 0
    }

if __name__ == "__main__":
    result = check_dependencies()
    sys.exit(0 if result["all_present"] else 1)
