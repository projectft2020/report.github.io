#!/usr/bin/env python3
"""
批量轉換所有研究報告到 HTML
"""

import os
import sys
import markdown
from datetime import datetime
import re

# 添加報告目錄到路徑
sys.path.insert(0, '/Users/charlie/report')

def clean_markdown_content(content):
    """清理 Markdown 內容"""
    content = re.sub(r'\[.*?\]\(.*?\.md\)', r'[相關檔案]', content)
    return content

def create_html_template(title, content, filename, description=""):
    """創建 HTML 模板"""

    css_styles = """
    <style>
        :root {
            --primary-color: #2563eb;
            --secondary-color: #64748b;
            --accent-color: #f59e0b;
            --success-color: #10b981;
            --warning-color: #f59e0b;
            --danger-color: #ef4444;
            --text-color: #1e293b;
            --bg-color: #f8fafc;
            --card-bg: #ffffff;
            --border-color: #e2e8f0;
            --code-bg: #1e293b;
            --code-text: #e2e8f0;
            --table-header: #f1f5f9;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            background-color: var(--bg-color);
            margin: 0;
            padding: 0;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 3rem 2rem;
            border-radius: 16px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
        }

        .header .subtitle {
            font-size: 1.1rem;
            opacity: 0.9;
            margin-bottom: 0.5rem;
        }

        .header .description {
            font-size: 1rem;
            opacity: 0.8;
        }

        .content {
            background: var(--card-bg);
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 2rem;
        }

        .content h1, .content h2, .content h3, .content h4, .content h5, .content h6 {
            color: var(--primary-color);
            margin-top: 2rem;
            margin-bottom: 1rem;
        }

        .content h1 { font-size: 2.2rem; }
        .content h2 { font-size: 1.8rem; }
        .content h3 { font-size: 1.5rem; }
        .content h4 { font-size: 1.3rem; }
        .content h5 { font-size: 1.1rem; }
        .content h6 { font-size: 1rem; }

        .content p {
            margin-bottom: 1rem;
            line-height: 1.7;
        }

        .content ul, .content ol {
            margin-bottom: 1rem;
            padding-left: 2rem;
        }

        .content li {
            margin-bottom: 0.5rem;
        }

        .content table {
            width: 100%;
            border-collapse: collapse;
            margin: 1.5rem 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .content th, .content td {
            border: 1px solid var(--border-color);
            padding: 0.75rem;
            text-align: left;
        }

        .content th {
            background-color: var(--table-header);
            font-weight: 600;
            color: var(--primary-color);
        }

        .content tr:nth-child(even) {
            background-color: #f8fafc;
        }

        .content blockquote {
            border-left: 4px solid var(--primary-color);
            padding-left: 1rem;
            margin: 1rem 0;
            color: var(--secondary-color);
            font-style: italic;
        }

        .content code {
            background-color: #f1f5f9;
            color: var(--primary-color);
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 0.9em;
        }

        .content pre {
            background-color: var(--code-bg);
            color: var(--code-text);
            padding: 1.5rem;
            border-radius: 8px;
            overflow-x: auto;
            margin: 1.5rem 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }

        .content pre code {
            background-color: transparent;
            color: inherit;
            padding: 0;
        }

        .back-to-home {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: var(--primary-color);
            color: white;
            text-decoration: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            font-weight: 500;
            margin-bottom: 2rem;
            transition: all 0.3s ease;
        }

        .back-to-home:hover {
            background: #1d4ed8;
            transform: translateX(-4px);
        }

        .footer {
            background: var(--card-bg);
            padding: 2rem;
            border-radius: 12px;
            text-align: center;
            margin-top: 2rem;
            border-top: 1px solid var(--border-color);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .footer p {
            color: var(--secondary-color);
            margin-bottom: 0.5rem;
        }

        .footer .disclaimer {
            font-size: 0.875rem;
            font-style: italic;
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border-color);
        }

        @media (max-width: 768px) {
            .container {
                padding: 1rem;
            }

            .header h1 {
                font-size: 2rem;
            }

            .header {
                padding: 2rem 1rem;
            }

            .content {
                padding: 1.5rem;
            }

            .content h1 { font-size: 1.8rem; }
            .content h2 { font-size: 1.5rem; }
            .content h3 { font-size: 1.3rem; }
        }
    </style>
    """

    html_template = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - 量化交易研究報告</title>
    {css_styles}
</head>
<body>
    <div class="container">
        <a href="index.html" class="back-to-home">← 返回研究目錄</a>

        <div class="header">
            <h1>{title}</h1>
            <p class="subtitle">量化交易研究報告 - {datetime.now().strftime('%Y-%m-%d')}</p>
            {f'<p class="description">{description}</p>' if description else ''}
        </div>

        <div class="content">
            {content}
        </div>

        <div class="footer">
            <p>© 2026 Charlie's Quantitative Trading Research Hub</p>
            <p class="disclaimer">⚠️ 免責聲明：研究內容僅供學術參考，不構成任何投資建議。投資有風險，請謹慎評估。</p>
        </div>
    </div>
</body>
</html>
"""

    return html_template

def convert_markdown_to_html(md_content, title):
    """將 Markdown 內容轉換為 HTML"""

    md_content = clean_markdown_content(md_content)

    md_extensions = [
        'tables',
        'fenced_code',
        'codehilite',
        'toc',
        'footnotes',
        'attr_list',
        'def_list',
    ]

    html_content = markdown.markdown(
        md_content,
        extensions=md_extensions,
        extension_configs={
            'codehilite': {
                'use_pygments': False,
                'css_class': 'highlight'
            },
            'toc': {
                'permalink': True,
                'permalink_title': '連結到此標題'
            }
        }
    )

    return html_content

def extract_title_from_md(content):
    """從 Markdown 內容中提取標題"""
    lines = content.split('\n')
    for line in lines[:20]:  # 只檢查前 20 行
        if line.startswith('# '):
            return line[2:].strip()
    return None

def batch_convert_reports():
    """批量轉換所有研究報告"""

    kanban_dir = "/Users/charlie/.openclaw/workspace/kanban/projects"
    report_dir = "/Users/charlie/report"

    os.makedirs(report_dir, exist_ok=True)

    print("🚀 開始批量轉換研究報告...")

    # 掃描所有 .md 文件
    md_files = []
    for root, dirs, files in os.walk(kanban_dir):
        for file in files:
            if file.endswith('.md') and not file.startswith('.'):
                filepath = os.path.join(root, file)
                md_files.append(filepath)

    print(f"📊 發現 {len(md_files)} 個 Markdown 文件")

    converted = 0
    skipped = 0
    failed = 0

    for md_path in md_files:
        filename = os.path.basename(md_path)
        html_filename = filename.replace('.md', '.html')
        html_path = os.path.join(report_dir, html_filename)

        # 檢查是否已存在
        if os.path.exists(html_path):
            skipped += 1
            continue

        # 轉換
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                md_content = f.read()

            # 提取標題
            title = extract_title_from_md(md_content)
            if not title:
                title = os.path.splitext(filename)[0]
                title = title.replace('-', ' ').replace('_', ' ').title()

            html_content = convert_markdown_to_html(md_content, title)

            full_html = create_html_template(
                title,
                html_content,
                filename,
                ""
            )

            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(full_html)

            converted += 1
            if converted % 10 == 0:
                print(f"  ✅ 已轉換: {converted} 個文件")

        except Exception as e:
            failed += 1
            print(f"❌ 轉換失敗: {filename} - {str(e)}")

    print(f"\n✨ 批量轉換完成！")
    print(f"  ✅ 轉換成功: {converted} 個")
    print(f"  ⏭️  已存在跳過: {skipped} 個")
    print(f"  ❌ 轉換失敗: {failed} 個")

if __name__ == "__main__":
    batch_convert_reports()
