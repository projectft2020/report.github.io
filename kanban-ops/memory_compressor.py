#!/usr/bin/env python3
"""
記憶檔案壓縮器

壓縮記憶檔案到指定大小限制（預設 100 KB）
保留關鍵決策、學習點、模式，移除冗餘內容
"""

import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict


def compress_memory_file(input_path: Path, output_path: Path = None, max_size_kb: int = 100) -> Dict:
    """
    壓縮記憶檔案

    Args:
        input_path: 輸入檔案路徑
        output_path: 輸出檔案路徑（如果為 None，則覆蓋輸入）
        max_size_kb: 最大檔案大小（KB）

    Returns:
        壓縮結果字典
    """
    if output_path is None:
        output_path = input_path

    # 使用檔案系統大小（而不是內容長度）
    original_size = input_path.stat().st_size
    original_size_kb = original_size / 1024

    print(f"原始檔案：{input_path}")
    print(f"原始大小：{original_size_kb:.1f} KB")
    print(f"目標大小：{max_size_kb} KB")

    # 如果已經小於目標，直接返回
    if original_size_kb <= max_size_kb:
        print("✅ 檔案已經小於目標大小，無需壓縮")
        return {
            'compressed': False,
            'original_size': original_size_kb,
            'compressed_size': original_size_kb,
            'ratio': 0.0
        }

    # 讀取檔案內容
    content = input_path.read_text(encoding='utf-8')

    # 壓縮策略
    compressed = compress_memory_content(content, target_ratio=max_size_kb / original_size_kb)

    # 寫入壓縮後的內容
    output_path.write_text(compressed, encoding='utf-8')

    compressed_size = len(compressed)
    compressed_size_kb = compressed_size / 1024
    ratio = (1 - compressed_size / original_size) * 100

    print(f"壓縮後：{compressed_size_kb:.1f} KB")
    print(f"壓縮比例：{ratio:.1f}%")

    return {
        'compressed': True,
        'original_size': original_size_kb,
        'compressed_size': compressed_size_kb,
        'ratio': ratio
    }


def compress_memory_content(content: str, target_ratio: float) -> str:
    """
    壓縮記憶內容（激進策略）

    壓縮策略：
    1. 保留所有一級標題（##）
    2. 對於每個章節，只保留前 5 個二級標題（###）
    3. 只保留簡短的清單項（< 80 字符）
    4. 移除所有段落和詳細解釋
    5. 移除所有代碼塊
    6. 限制總行數到 1000 行
    """
    lines = content.split('\n')
    compressed_lines = []

    i = 0
    current_section_title = None
    section_count = 0

    while i < len(lines) and len(compressed_lines) < 1000:  # 限制總行數
        line = lines[i].strip()

        # 保留一級標題（##）
        if line.startswith('## '):
            current_section_title = line
            section_count += 1
            compressed_lines.append(line)
            compressed_lines.append('')  # 添加空行
            i += 1
            continue

        # 保留二級標題（###），但每個章節只保留前 5 個
        if line.startswith('### '):
            # 重置計數器
            subsection_count = 0
            if i + 1 < len(lines):
                next_lines = lines[i+1:min(i+50, len(lines))]
                subsection_count = sum(1 for l in next_lines if l.strip().startswith('### '))

            # 只保留前 5 個二級標題
            if subsection_count < 5:
                compressed_lines.append(line)
            i += 1
            continue

        # 處理清單項（- 或 *）
        if line.startswith('- ') or line.startswith('* '):
            # 只保留非常短的清單項（< 80 字符）
            if len(line) < 80:
                compressed_lines.append(line)
            i += 1
            continue

        # 處理標記（- **xxx**：）
        if re.match(r'^- \*\*.*\*\*：', line):
            if len(line) < 80:  # 只保留短的標記
                compressed_lines.append(line)
            i += 1
            continue

        # 跳過代碼塊
        if line.startswith('```'):
            # 跳過整個代碼塊
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                i += 1
            i += 1
            continue

        # 跳過其他內容（詳細的段落、空行）
        i += 1

    # 移除連續的空行（最多保留 1 個）
    result_lines = []
    empty_count = 0
    for line in compressed_lines:
        if line.strip() == '':
            empty_count += 1
            if empty_count <= 1:
                result_lines.append(line)
        else:
            result_lines.append(line)
            empty_count = 0

    return '\n'.join(result_lines)


def extract_key_sections(content: str, max_sections: int = 10) -> str:
    """
    提取關鍵章節

    提取前 max_sections 個一級標題（##）及其下的二級標題（###）
    """
    lines = content.split('\n')
    extracted = []

    section_count = 0
    i = 0

    while i < len(lines) and section_count < max_sections:
        line = lines[i].strip()

        # 識別一級標題
        if line.startswith('## '):
            extracted.append(line)
            extracted.append('')
            section_count += 1
            i += 1

            # 提取該章節下的所有二級標題（最多 5 個）
            subsection_count = 0
            while i < len(lines) and subsection_count < 5:
                subline = lines[i].strip()
                if subline.startswith('### '):
                    extracted.append(subline)
                    subsection_count += 1
                elif subline.startswith('## '):
                    # 新章節開始
                    break
                i += 1
        else:
            i += 1

    return '\n'.join(extracted)


def main():
    """
    主函數：壓縮記憶檔案
    """
    memory_dir = Path('/Users/charlie/.openclaw/workspace/memory')

    # 找出大於 100 KB 的記憶檔案
    large_files = [f for f in memory_dir.glob('2026-*.md') if f.stat().st_size > 100 * 1024]

    print(f"找到 {len(large_files)} 個大於 100 KB 的記憶檔案")
    print("=" * 60)

    results = []

    for memory_file in large_files:
        size_kb = memory_file.stat().st_size / 1024
        print(f"\n處理: {memory_file.name} ({size_kb:.1f} KB)")

        result = compress_memory_file(memory_file, max_size_kb=100)
        results.append({
            'file': memory_file.name,
            'original_size': result['original_size'],
            'compressed_size': result['compressed_size'],
            'ratio': result['ratio'],
            'compressed': result['compressed']
        })

    # 生成報告
    if results:
        report = f"""# 記憶壓縮報告

> **生成時間：** {datetime.now().isoformat()}
> **處理檔案數：** {len(results)}

---

## 壓縮結果

| 檔案 | 原始大小 (KB) | 壓縮後 (KB) | 壓縮比例 |
|------|----------------|-------------|-----------|
"""

        for r in results:
            status = "✅" if r['compressed'] else "⏭️"
            report += f"| {r['file']} | {r['original_size']:.1f} | {r['compressed_size']:.1f} | {r['ratio']:.1f}% |\n"

        report += f"""

---

## 總計

- **壓縮檔案數：** {sum(1 for r in results if r['compressed'])} / {len(results)}
- **平均壓縮比例：** {sum(r['ratio'] for r in results if r['compressed']) / len(results) if results else 0:.1f}%
- **總節省空間：** {sum(r['original_size'] - r['compressed_size'] for r in results if r['compressed']) / 1024:.1f} KB
"""

        # 寫入報告
        report_path = Path('/Users/charlie/.openclaw/workspace/memory/compression-report.md')
        report_path.write_text(report, encoding='utf-8')

        print("\n" + "=" * 60)
        print(f"壓縮報告：{report_path}")
        print(f"壓縮檔案數：{sum(1 for r in results if r['compressed'])} / {len(results)}")
        print(f"平均壓縮比例：{sum(r['ratio'] for r in results if r['compressed']) / len(results) if results else 0:.1f}%")
    else:
        print("沒有需要壓縮的檔案")


if __name__ == '__main__':
    main()
