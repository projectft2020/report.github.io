#!/usr/bin/env python3
"""為 index.html 中的新報告添加時間字段"""

import re
from datetime import datetime

REPORTS_WITH_TIME = [
    'd001-derivatives-pricing',
    'm001-ml-multifactor',
    'm002-ml-multifactor-cn',
    'e001-multi-agent',
    's001-scout-scan',
    's002-scout-research',
    'ai001-risk-management',
    'b001-blockchain-tokenization',
    'd002-defi-market-making',
    'f001-federated-learning',
    'g001-gan-synthetic-data',
    'h001-hf-microstructure',
    's001-llm-sentiment',
    'v001-transformer-volatility',
    'x001-explainable-ai',
]

def add_time_to_reports(content):
    """為指定報告添加 time 字段"""

    def update_report(match):
        report_content = match.group(0)

        # 檢查是否是我們要更新的報告
        for report_id in REPORTS_WITH_TIME:
            if f"id: '{report_id}'" in report_content:
                # 檢查是否已經有 time 字段
                if 'time:' in report_content:
                    return report_content

                # 添加 time 字段
                # 在 category 之前插入 time 字段
                updated = re.sub(
                    r"(date: '[^']+',)\s*(category:)",
                    r"\1\n                time: '04:00:00',\n                \2",
                    report_content
                )
                print(f"✅ 添加時間到 {report_id}")
                return updated

        return report_content

    # 匹配整個報告對象（從 { 到 }）
    pattern = r'\{[^}]*id:\s*[\'"][^\'"]+[\'"][^}]*\}(?:\s*,\s*\{|\s*\])'

    # 這個模式太複雜，讓我們用更簡單的方法
    # 直接在每個 date 行後面添加 time 行

    lines = content.split('\n')
    result_lines = []

    i = 0
    while i < len(lines):
        line = lines[i]
        result_lines.append(line)

        # 檢查是否是 date 行，且下一行不是 time
        if re.match(r"                date: '2026-02-21',", line):
            # 檢查接下來的幾行是否有 time
            has_time = False
            for j in range(i + 1, min(i + 5, len(lines))):
                if 'time:' in lines[j]:
                    has_time = True
                    break
                if 'category:' in lines[j]:
                    break

            if not has_time:
                # 添加 time 行
                result_lines.append("                time: '04:00:00',")
                # 打印哪個報告被更新（需要找到 id）
                # 往回找 id
                for j in range(max(0, i - 10), i):
                    if "id: '" in lines[j]:
                        match = re.search(r"id: '([^']+)'", lines[j])
                        if match:
                            report_id = match.group(1)
                            if report_id in REPORTS_WITH_TIME:
                                print(f"✅ 添加時間到 {report_id}")
                        break

        i += 1

    return '\n'.join(result_lines)

def update_date_display(content):
    """更新日期顯示，包含時間"""
    # 查找並替換日期顯示行
    old_pattern = r'<span class="report-date">📅 \${report\.date}<\/span>'
    new_pattern = r'<span class="report-date">📅 ${report.date}${report.time ? " " + report.time : ""}</span>'

    new_content = re.sub(old_pattern, new_pattern, content)

    if new_content != content:
        print("✅ 更新日期顯示邏輯")

    return new_content

def main():
    index_path = '/Users/charlie/report/index.html'

    print("=" * 60)
    print("為 index.html 中的新報告添加時間字段")
    print("=" * 60)

    # 讀取文件
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 添加 time 字段
    content = add_time_to_reports(content)

    # 更新日期顯示邏輯
    content = update_date_display(content)

    # 寫回文件
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("\n✅ 完成！")

if __name__ == '__main__':
    main()
