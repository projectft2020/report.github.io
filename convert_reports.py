#!/usr/bin/env python3
"""
量化研究報告 HTML 轉換器
將 Markdown 研究報告轉換為 HTML 格式
"""

import os
import markdown
from datetime import datetime
import re

def clean_markdown_content(content):
    """清理 Markdown 內容，移除不必要的格式"""
    
    # 移除 Markdown 檔案中的相對路徑引用
    content = re.sub(r'\[.*?\]\(.*?\.md\)', r'[相關檔案]', content)
    
    # 簡化一些複雜的 Markdown 語法
    content = re.sub(r'`{3}.*?\n', '```python\n', content, flags=re.DOTALL)
    
    return content

def create_html_template(title, content, filename):
    """創建 HTML 模板"""
    
    # 從內容中提取簡短描述
    first_paragraph = ""
    lines = content.split('\n')
    for line in lines:
        if line.strip() and not line.startswith('#') and not line.startswith('**'):
            first_paragraph = line.strip()
            break
    
    css_styles = """
    <style>
        :root {
            --primary-color: #2563eb;
            --secondary-color: #64748b;
            --accent-color: #f59e0b;
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
        
        .toc {
            background: #f8fafc;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .toc h3 {
            color: var(--primary-color);
            margin-bottom: 1rem;
        }
        
        .toc ul {
            list-style-type: none;
            padding-left: 0;
        }
        
        .toc li {
            margin-bottom: 0.5rem;
        }
        
        .toc a {
            color: var(--primary-color);
            text-decoration: none;
        }
        
        .toc a:hover {
            text-decoration: underline;
        }
        
        .info-box {
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            border-left: 4px solid var(--primary-color);
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 0 8px 8px 0;
        }
        
        .warning-box {
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            border-left: 4px solid var(--accent-color);
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 0 8px 8px 0;
        }
        
        .success-box {
            background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
            border-left: 4px solid var(--success-color);
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 0 8px 8px 0;
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
            
            table {
                font-size: 0.9rem;
            }
            
            th, td {
                padding: 0.5rem;
            }
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
            <p class="subtitle">{first_paragraph}</p>
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
    
    # 清理內容
    md_content = clean_markdown_content(md_content)
    
    # 設定 Markdown 擴展
    md_extensions = [
        'tables',           # 表格支援
        'fenced_code',      # 程式碼區塊
        'codehilite',       # 程式碼高亮
        'toc',              # 目錄
        'footnotes',        # 註解
        'attr_list',        # 屬性列表
        'def_list',         # 定義列表
        'abbr',             # 縮寫
    ]
    
    # 轉換 Markdown 為 HTML
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

def convert_research_reports():
    """轉換所有研究報告"""
    
    # 設置路徑
    source_dir = "/Users/charlie/.openclaw/workspace/quant/research"
    target_dir = "/Users/charlie/report"
    
    # 確保目標目錄存在
    os.makedirs(target_dir, exist_ok=True)
    
    # 要轉換的報告列表
    reports = [
        {
            'filename': 'momentum_strategy_foundation.md',
            'title': '基礎動能策略 - 第一週研究報告'
        },
        {
            'filename': 'matrix_system_integration.md',
            'title': 'Matrix 系統整合報告'
        },
        {
            'filename': 'data_collection_preparation.md',
            'title': '數據收集與準備報告'
        },
        {
            'filename': 'cross_asset_complete_plan.md',
            'title': '跨資產完整計畫'
        },
        {
            'filename': 'top-quant-hedge-funds.md',
            'title': '全球頂尖量化對沖基金研究'
        },
        {
            'filename': 'research_topics.md',
            'title': '研究主題清單'
        }
    ]
    
    print("🚀 開始轉換研究報告...")
    
    for report in reports:
        source_path = os.path.join(source_dir, report['filename'])
        
        if os.path.exists(source_path):
            print(f"📖 正在處理: {report['filename']}")
            
            try:
                # 讀取 Markdown 檔案
                with open(source_path, 'r', encoding='utf-8') as f:
                    md_content = f.read()
                
                # 轉換 Markdown 為 HTML
                html_content = convert_markdown_to_html(md_content, report['title'])
                
                # 創建完整 HTML
                full_html = create_html_template(
                    report['title'], 
                    html_content, 
                    report['filename']
                )
                
                # 生成輸出檔名
                output_filename = report['filename'].replace('.md', '.html')
                output_path = os.path.join(target_dir, output_filename)
                
                # 保存 HTML 檔案
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(full_html)
                
                print(f"✅ 轉換完成: {report['filename']} → {output_filename}")
                
            except Exception as e:
                print(f"❌ 轉換失敗: {report['filename']} - {str(e)}")
        else:
            print(f"❌ 檔案不存在: {report['filename']}")
    
    print("✨ 所有報告轉換完成！")

if __name__ == "__main__":
    convert_research_reports()