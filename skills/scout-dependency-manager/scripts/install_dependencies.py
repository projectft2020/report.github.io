#!/usr/bin/env python3
"""
Install Scout Agent Dependencies

Automatically installs missing Scout Agent packages.
"""

import sys
import subprocess

def install_package(package_name):
    """Install a Python package using pip."""
    print(f"📦 安裝 {package_name}...")

    try:
        # Run pip install
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package_name],
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode == 0:
            print(f"✅ {package_name} 安裝成功")
            return True
        else:
            print(f"❌ {package_name} 安裝失敗")
            print(f"錯誤: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print(f"❌ {package_name} 安裝超時")
        return False
    except Exception as e:
        print(f"❌ {package_name} 安裝時發生錯誤: {e}")
        return False

def install_dependencies(packages=None):
    """Install missing Scout Agent dependencies."""
    if packages is None:
        from check_dependencies import check_dependencies
        result = check_dependencies()
        packages = result["missing"]

    if not packages:
        print("✅ 所有依賴已安裝，無需安裝")
        return True

    print()
    print("🚀 開始安裝缺失的依賴...")
    print()

    success_count = 0
    fail_count = 0

    for package in packages:
        if install_package(package):
            success_count += 1
        else:
            fail_count += 1
        print()

    print("=" * 60)
    print(f"安裝結果: {success_count} 成功, {fail_count} 失敗")
    print("=" * 60)

    if fail_count == 0:
        print()
        print("✅ 所有依賴安裝完成")
        print("💡 建議運行: python3 health_check.py")
        return True
    else:
        print()
        print("❌ 部分依賴安裝失敗")
        print("💡 請檢查錯誤信息並手動安裝")
        return False

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Install Scout Agent dependencies")
    parser.add_argument(
        "--packages",
        nargs="*",
        help="Specific packages to install (default: all missing)"
    )
    args = parser.parse_args()

    success = install_dependencies(args.packages)
    sys.exit(0 if success else 1)
