#!/usr/bin/env python3
"""
Code Quality Helper - 代碼質量輔助工具

基於心跳時代碼異味分析的結果，提供實用的重構建議。

使用方式：
    python3 kanban-ops/code_quality_helper.py
"""

import os
import re
from pathlib import Path
from collections import Counter, defaultdict


def print_header(title):
    """打印標題"""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def print_section(title):
    """打印分區標題"""
    print(f"\n{title}")
    print("-" * 80)


def analyze_deep_nesting(directory="."):
    """分析深層嵌套"""
    print_section("📊 深層嵌套分析")

    nested_lines = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                except:
                    continue

                for i, line in enumerate(lines, 1):
                    stripped = line.lstrip()
                    indent = len(line) - len(stripped)
                    if indent > 24:  # 6 層嵌套
                        nested_lines.append((filepath, i, indent // 4, line.strip()[:60]))

    if not nested_lines:
        print("✅ 未發現深層嵌套（>3層）")
        return

    # 按文件分組
    by_file = defaultdict(list)
    for filepath, line_num, depth, code in nested_lines:
        by_file[filepath].append((line_num, depth, code))

    print(f"發現 {len(nested_lines)} 處深層嵌套\n")

    for filepath, items in sorted(by_file.items()):
        print(f"📁 {filepath}")
        for line_num, depth, code in sorted(items, key=lambda x: x[1], reverse=True)[:3]:
            print(f"  行 {line_num:>3} (深度 {depth} 層): {code}...")
        print()


def analyze_magic_numbers(directory="."):
    """分析魔法數字"""
    print_section("🔢 魔法數字分析")

    magic_numbers = Counter()
    common_numbers = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                      '10', '60', '3600', '86400', '1000', '10000',
                      '100', '256', '512', '1024', '2048', '4096'}

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                except:
                    continue

                for line in lines:
                    # 跳過注釋
                    if '#' in line:
                        line = line[:line.index('#')]

                    for match in re.finditer(r'\b(\d{2,4})\b', line):
                        num = match.group(1)
                        # 過濾日期和常見數字
                        if 1990 <= int(num) <= 2100:
                            continue
                        if num in common_numbers:
                            continue
                        magic_numbers[num] += 1

    if not magic_numbers:
        print("✅ 未發現明顯的魔法數字")
        return

    print("頻率前 10 的數字（排除日期和常見常量）：\n")

    for num, count in magic_numbers.most_common(10):
        bar = '█' * min(count // 5, 20)
        print(f"  {num:>6} : {count:>3} 次 {bar}")

    print("\n💡 常見魔法數字建議：")
    print("  • 300000 → TOKEN_LIMIT (常量定義)")
    print("  • 1800    → SCAN_INTERVAL (常量定義)")
    print("  • 65      → SPAWN_DELAY (常量定義)")


def analyze_error_handling(directory="."):
    """分析錯誤處理模式"""
    print_section("🚨 錯誤處理模式分析")

    patterns = {
        '標準日誌記錄': [],
        'silent 失敗 (pass)': [],
        '簡單返回 False': [],
    }

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                except:
                    continue

                for match in re.finditer(r'except Exception as e:\s*\n\s+print\(\[?\"(ERROR|WARNING|INFO)\"', content):
                    patterns['標準日誌記錄'].append(filepath)

                for match in re.finditer(r'except Exception.*:\s*\n\s+pass', content, re.MULTILINE):
                    patterns['silent 失敗 (pass)'].append(filepath)

                for match in re.finditer(r'except Exception.*:\s*\n\s+return False', content, re.MULTILINE):
                    patterns['簡單返回 False'].append(filepath)

    for pattern, files in patterns.items():
        unique_files = len(set(files))
        status = '✅' if unique_files == 0 else '⚠️'
        print(f"  {status} {pattern:<25} : {unique_files:>2} 個文件")


def show_refactoring_tips():
    """顯示重構建議"""
    print_section("💡 重構建議")

    print("""
1. **減少深層嵌套**
   ❌ 複雜的 if-else 嵌套
   ✅ 使用 Guard Clauses 和早返回

   示例：
   ```python
   # 壞
   if condition1:
       if condition2:
           if condition3:
               do_something()

   # 好
   if not condition1:
       return
   if not condition2:
       return
   if not condition3:
       return
   do_something()
   ```

2. **消除魔法數字**
   ❌ if timeout > 300:
   ✅ DEFAULT_TIMEOUT = 300
      if timeout > DEFAULT_TIMEOUT:

3. **統一錯誤處理**
   ❌ 分散的 try-except 塊
   ✅ 使用裝飾器或上下文管理器

   示例：
   ```python
   from functools import wraps

   def handle_errors(default_return=None, log_errors=True):
       def decorator(func):
           @wraps(func)
           def wrapper(*args, **kwargs):
               try:
                   return func(*args, **kwargs)
               except Exception as e:
                   if log_errors:
                       print(f\"[ERROR] {func.__name__}: {e}\")
                   return default_return
           return wrapper
       return decorator

   @handle_errors(default_return=False, log_errors=True)
   def some_function():
       ...
   ```

4. **提取重複邏輯**
   ❌ 相同代碼出現多次
   ✅ 提取為獨立函數或類

   原則：DRY (Don't Repeat Yourself)
    """)


def generate_refactoring_report(directory="."):
    """生成完整的重構報告"""
    print_header("Code Quality Report - 代碼質量報告")

    analyze_deep_nesting(directory)
    analyze_magic_numbers(directory)
    analyze_error_handling(directory)
    show_refactoring_tips()

    print_header("報告完成")
    print("提示：定期運行此工具以監控代碼質量")


def main():
    """主函數"""
    directory = os.path.dirname(os.path.abspath(__file__))
    generate_refactoring_report(directory)


if __name__ == '__main__':
    main()
