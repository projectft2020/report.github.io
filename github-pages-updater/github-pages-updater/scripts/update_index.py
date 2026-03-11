#!/usr/bin/env python3
"""
自動更新 index.html 的 reports 數組
"""

import os
import re
from datetime import datetime

def extract_metadata_from_html(html_path):
    """從 HTML 文件中提取元數據"""

    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取標題（從 header h1）
        title_match = re.search(r'<h1>(.*?)</h1>', content, re.DOTALL)
        title = title_match.group(1).strip() if title_match else None

        # 提取描述（從 header .description）
        desc_match = re.search(r'<p class="description">(.*?)</p>', content, re.DOTALL)
        description = desc_match.group(1).strip() if desc_match else ''

        # 如果沒有找到標題，使用文件名
        if not title:
            filename = os.path.basename(html_path)
            title = filename.replace('.html', '').replace('-', ' ').title()

        # 提取文件修改時間作為日期
        mtime = os.path.getmtime(html_path)
        date = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')

        # 根據文件前綴推斷 category
        filename = os.path.basename(html_path)
        category = 'research'  # 默認

        if filename.startswith('q'):
            category = 'quant-evolve'
        elif filename.startswith('t'):
            category = 'trend-trading'
        elif filename.startswith('m'):
            category = 'momentum'
        elif filename.startswith('s') and 'stat' in filename.lower():
            category = 'statistical-arb'
        elif filename.startswith('st'):
            category = 'statistical-arb'
        elif filename.startswith('s'):
            category = 'trend-trading'
        elif filename.startswith('b') and 'barra' in filename.lower():
            category = 'barra'
        elif filename.startswith('b'):
            category = 'blockchain'
        elif filename.startswith('k'):
            category = 'skewness'
        elif filename.startswith('r') and 'regime' in filename.lower():
            category = 'regime'
        elif filename.startswith('r'):
            category = 'risk-management'
        elif filename.startswith('d') and 'dhri' in filename.lower():
            category = 'tools'
        elif filename.startswith('d'):
            category = 'derivatives'
        elif filename.startswith('f'):
            category = 'factor-analysis'
        elif filename.startswith('h'):
            category = 'hft'
        elif filename.startswith('e'):
            category = 'quant-evolve'
        elif filename.startswith('g'):
            category = 'ml'
        elif filename.startswith('v'):
            category = 'ml'
        elif filename.startswith('x'):
            category = 'ai'
        elif filename.startswith('a'):
            category = 'system'
        elif filename.startswith('w'):
            category = 'system'
        elif filename.startswith('p'):
            category = 'system'
        elif filename.startswith('pj'):
            category = 'crisis'

        return {
            'id': filename.replace('.html', ''),
            'title': title,
            'description': description[:200] + '...' if len(description) > 200 else description,
            'date': date,
            'category': category,
            'file': filename,
            'tags': [category]
        }

    except Exception as e:
        print(f"❌ 提取失敗: {html_path} - {str(e)}")
        return None

def generate_reports_array():
    """生成 reports 數組"""

    report_dir = "/Users/charlie/report"
    html_files = []

    # 掃描所有 HTML 文件
    for file in sorted(os.listdir(report_dir), reverse=True):
        if file.endswith('.html') and file != 'index.html':
            html_path = os.path.join(report_dir, file)
            metadata = extract_metadata_from_html(html_path)
            if metadata:
                html_files.append(metadata)

    return html_files

def escape_js_string(s):
    """轉義 JavaScript 字符串"""
    return s.replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'").replace('\n', '\\n')

def update_index_html():
    """更新 index.html"""

    report_dir = "/Users/charlie/report"
    index_path = os.path.join(report_dir, 'index.html')

    print("🚀 開始生成 reports 數組...")

    # 生成 reports 數組
    reports = generate_reports_array()

    print(f"📊 發現 {len(reports)} 個報告")

    # 生成 JavaScript 數組
    reports_js = "        const reports = [\n"

    for report in reports:  # 添加所有報告
        reports_js += f"            {{\n"
        reports_js += f"                id: '{escape_js_string(report['id'])}',\n"
        reports_js += f"                title: '{escape_js_string(report['title'])}',\n"
        reports_js += f"                description: '{escape_js_string(report['description'])}',\n"
        reports_js += f"                date: '{escape_js_string(report['date'])}',\n"
        reports_js += f"                category: '{escape_js_string(report['category'])}',\n"
        reports_js += f"                tags: {report['tags']},\n"
        reports_js += f"                file: '{escape_js_string(report['file'])}'\n"
        reports_js += f"            }},\n"

    reports_js += "        ];\n"

    # 讀取原始 index.html
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 替換 reports 數組
    pattern = r"        const reports = \[.*?\];"
    new_content = re.sub(pattern, reports_js.strip(), content, flags=re.DOTALL)

    # 更新統計數字
    stats_pattern = r'📊 <strong>\d+ 份</strong> 研究報告'
    new_stats = f'📊 <strong>{len(reports)} 份</strong> 研究報告'
    new_content = re.sub(stats_pattern, new_stats, new_content)

    # 寫回文件
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"✅ index.html 已更新！包含 {len(reports)} 個報告")

if __name__ == "__main__":
    update_index_html()
