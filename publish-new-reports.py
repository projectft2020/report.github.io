#!/usr/bin/env python3
"""
GitHub Pages 新報告發布腳本
將 kanban/projects/ 中的新報告轉換成 HTML 並更新 index.html
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path

# 配置
WORKSPACE = Path.home() / '.openclaw' / 'workspace'
GITHUB_PAGES = Path.home() / 'report'
MD_TO_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        :root {{
            --primary-color: #2563eb;
            --secondary-color: #64748b;
            --bg-color: #f8fafc;
            --text-color: #1e293b;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            background-color: var(--bg-color);
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
        }}
        h1 {{ color: var(--primary-color); margin-bottom: 0.5rem; }}
        h2 {{ color: var(--primary-color); margin-top: 2rem; border-bottom: 2px solid var(--secondary-color); padding-bottom: 0.5rem; }}
        h3 {{ color: var(--secondary-color); margin-top: 1.5rem; }}
        .meta {{ color: var(--secondary-color); font-size: 0.9rem; margin-bottom: 2rem; }}
        .updated {{ background: #fef3c7; padding: 0.5rem 1rem; border-radius: 8px; display: inline-block; margin-bottom: 1rem; font-size: 0.85rem; }}
        pre {{ background: #1e293b; color: #f8fafc; padding: 1rem; border-radius: 8px; overflow-x: auto; }}
        code {{ background: #e2e8f0; padding: 0.2rem 0.4rem; border-radius: 4px; }}
        pre code {{ background: none; padding: 0; }}
        table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; }}
        th, td {{ border: 1px solid #e2e8f0; padding: 0.75rem; text-align: left; }}
        th {{ background: var(--primary-color); color: white; }}
        .back-link {{ display: inline-block; margin-bottom: 2rem; color: var(--primary-color); text-decoration: none; }}
        .back-link:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <a href="index.html" class="back-link">← 返回研究報告列表</a>
    <div class="updated">📅 更新時間：{update_time}</div>
    <div class="content">
{content}
    </div>
</body>
</html>
"""

# 新報告映射（從 MD 文件路徑到 HTML 文件名和元數據）
NEW_REPORTS = [
    {
        'md_path': 'kanban/projects/ml-derivatives-pricing-20260220/d001-research.md',
        'html_file': 'd001-derivatives-pricing.html',
        'title': 'ML for Derivatives Pricing Research',
        'description': '機器學習在衍生品定價中的應用研究',
        'category': 'ml',
        'tags': ['機器學習', '衍生品', '定價模型']
    },
    {
        'md_path': 'kanban/projects/ml-multifactor-research-20260220/m001-research.md',
        'html_file': 'm001-ml-multifactor.html',
        'title': 'ML Enhanced Multi-Factor Models Research',
        'description': '機器學習增強的多因子模型研究',
        'category': 'ml',
        'tags': ['機器學習', '多因子', '模型優化']
    },
    {
        'md_path': 'kanban/projects/ml-multifactor-research-20260220/20260220-143743-m002-research.md',
        'html_file': 'm002-ml-multifactor-cn.html',
        'title': '機器學習增強多因子模型研究（中文）',
        'description': '機器學習如何增強傳統多因子模型的完整研究',
        'category': 'ml',
        'tags': ['機器學習', '多因子', '模型優化']
    },
    {
        'md_path': 'kanban/projects/multi-agent-evolutionary-20260220/e001-research.md',
        'html_file': 'e001-multi-agent.html',
        'title': 'Multi-Agent Evolutionary Strategy Discovery',
        'description': '多智能體演化策略發現機制',
        'category': 'quant-evolve',
        'tags': ['多智能體', '演化算法', '策略發現']
    },
    {
        'md_path': 'kanban/projects/scout-scan-20260220/20260220-135359-s001-scout-scan.md',
        'html_file': 's001-scout-scan.html',
        'title': 'Scout 掃描發現新研究主題',
        'description': 'Scout 自動掃描發現的量化交易研究主題',
        'category': 'research',
        'tags': ['Scout', '自動掃描', '研究發現']
    },
    {
        'md_path': 'kanban/projects/scout-scan-20260220/20260220-163239-s002-research.md',
        'html_file': 's002-scout-research.html',
        'title': 'Scout 研究報告',
        'description': 'Scout 自動生成的研究報告',
        'category': 'research',
        'tags': ['Scout', '自動研究', 'AI 助手']
    },
    # 2026-02-20 Scout 發現的新研究主題
    {
        'md_path': 'kanban/projects/ai-risk-management-20260220/ai001-research.md',
        'html_file': 'ai001-risk-management.html',
        'title': 'AI 智能體在自動化風險管理系統中的應用研究',
        'description': 'AI Agents 在金融風險管理中的架構設計與實施',
        'category': 'ai',
        'tags': ['AI', '風險管理', '智能體', 'TRiSM']
    },
    {
        'md_path': 'kanban/projects/blockchain-tokenization-20260220/b001-research.md',
        'html_file': 'b001-blockchain-tokenization.html',
        'title': '區塊鏈代幣化與傳統金融整合研究',
        'description': 'RWA 代幣化與傳統金融系統的整合機制',
        'category': 'fintech',
        'tags': ['區塊鏈', '代幣化', 'RWA', '金融整合']
    },
    {
        'md_path': 'kanban/projects/defi-market-making-20260220/d002-research.md',
        'html_file': 'd002-defi-market-making.html',
        'title': '多智能體強化學習在 DeFi 做市中的應用',
        'description': 'MARL 在 DeFi 流動性提供中的應用研究',
        'category': 'defi',
        'tags': ['DeFi', '做市', '多智能體', '強化學習']
    },
    {
        'md_path': 'kanban/projects/explainable-ai-trading-20260220/x001-research.md',
        'html_file': 'x001-explainable-ai.html',
        'title': '可解釋人工智慧在交易策略透明化中的應用',
        'description': 'XAI 技術在量化交易策略中的透明化實現',
        'category': 'ai',
        'tags': ['XAI', '交易策略', '透明化', '監管合規']
    },
    {
        'md_path': 'kanban/projects/federated-learning-quant-20260220/f001-research.md',
        'html_file': 'f001-federated-learning.html',
        'title': '聯邦學習在協作量化研究中的應用',
        'description': '跨機構協作而不共享數據的量化研究方法',
        'category': 'ml',
        'tags': ['聯邦學習', '量化研究', '數據隱私', '協作']
    },
    {
        'md_path': 'kanban/projects/gan-synthetic-data-20260220/g001-research.md',
        'html_file': 'g001-gan-synthetic-data.html',
        'title': '生成對抗網絡用於合成金融數據研究',
        'description': 'GAN 生成真實金融數據用於回測和壓力測試',
        'category': 'ml',
        'tags': ['GAN', '合成數據', '金融數據', '回測']
    },
    {
        'md_path': 'kanban/projects/hf-microstructure-20260220/h001-research.md',
        'html_file': 'h001-hf-microstructure.html',
        'title': '高頻交易微結構分析與機器學習應用',
        'description': 'ML 模型在高頻訂單簿數據分析中的應用',
        'category': 'hft',
        'tags': ['高頻交易', '微結構', '機器學習', '訂單簿']
    },
    {
        'md_path': 'kanban/projects/llm-sentiment-analysis-20260220/s001-research.md',
        'html_file': 's001-llm-sentiment.html',
        'title': '大語言模型實時情感分析在交易中的應用',
        'description': 'LLM 從新聞、社交媒體提取情感信號',
        'category': 'nlp',
        'tags': ['LLM', '情感分析', '實時', '交易決策']
    },
    {
        'md_path': 'kanban/projects/transformer-volatility-20260220/v001-research.md',
        'html_file': 'v001-transformer-volatility.html',
        'title': '基於 Transformer 的波動率預測研究',
        'description': 'Transformer 和 Attention 機制多範圍波動率預測',
        'category': 'ml',
        'tags': ['Transformer', '波動率', 'Attention', '風險管理']
    },
]

def markdown_to_simple_html(md_text):
    """簡單的 Markdown 到 HTML 轉換"""
    html = md_text

    # 標題轉換
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)

    # 粗體和斜體
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

    # 程式碼塊
    html = re.sub(r'```(\w+)?\n(.+?)```', r'<pre><code>\2</code></pre>', html, flags=re.DOTALL)

    # 行內程式碼
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)

    # 表格（簡單處理）
    html = re.sub(r'\|(.+?)\|\n\|[-|\s]+\|', r'<table>\n<tr>', html)
    html = re.sub(r'\|(.+?)\|', lambda m: '<td>' + m.group(1).strip() + '</td>', html)

    # 段落
    paragraphs = re.split(r'\n\n+', html)
    html = '\n\n'.join(f'<p>{p}</p>' if not p.startswith('<') else p for p in paragraphs)

    return html

def convert_markdown_to_html(md_path, html_path, title):
    """將 Markdown 文件轉換為 HTML"""
    print(f"🔄 轉換 {md_path} -> {html_path}")

    # 讀取 Markdown 文件
    md_full_path = WORKSPACE / md_path
    if not md_full_path.exists():
        print(f"  ⚠️ 文件不存在：{md_full_path}")
        return False

    with open(md_full_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # 轉換為 HTML
    html_content = markdown_to_simple_html(md_content)

    # 添加元數據
    update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 生成完整 HTML
    full_html = MD_TO_HTML_TEMPLATE.format(
        title=title,
        content=html_content,
        update_time=update_time
    )

    # 寫入 HTML 文件
    html_full_path = GITHUB_PAGES / html_path
    with open(html_full_path, 'w', encoding='utf-8') as f:
        f.write(full_html)

    print(f"  ✅ 成功生成 {html_path}")
    return True

def update_index_html(new_reports):
    """更新 index.html 添加新報告"""
    index_path = GITHUB_PAGES / 'index.html'

    print(f"🔄 更新 {index_path}")

    with open(index_path, 'r', encoding='utf-8') as f:
        index_content = f.read()

    # 找到 reports 數組
    reports_match = re.search(r'const reports = \[(.*?)\];', index_content, re.DOTALL)
    if not reports_match:
        print("  ❌ 找不到 reports 數組")
        return False

    reports_array = reports_match.group(1)

    # 構建新報告條目
    today = datetime.now().strftime('%Y-%m-%d')
    new_entries = []

    for report in new_reports:
        entry = f"""            {{
                id: '{report['html_file'].replace('.html', '')}',
                title: '{report['title']}',
                description: '{report['description']}',
                date: '{today}',
                category: '{report['category']}',
                tags: {json.dumps(report['tags'])},
                file: '{report['html_file']}'
            }},"""
        new_entries.append(entry)

    # 在 reports 數組開頭插入新報告
    new_reports_text = '\n'.join(new_entries) + '\n\n        '

    new_reports_array = new_reports_text + reports_array

    # 替換 reports 數組
    new_index_content = index_content.replace(
        f'const reports = [{reports_array}];',
        f'const reports = [{new_reports_array}];'
    )

    # 更新報告統計
    old_stats = r'📊 <strong>(\d+) 份</strong> 研究報告'
    current_count = len(re.findall(r'id: \'[^\']+\',', new_index_content))
    new_stats = f'📊 <strong>{current_count} 份</strong> 研究報告'
    new_index_content = re.sub(old_stats, new_stats, new_index_content)

    # 寫入更新後的 index.html
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(new_index_content)

    print(f"  ✅ 成功更新 index.html（新增 {len(new_reports)} 份報告，總計 {current_count} 份）")
    return True

def main():
    print("=" * 60)
    print("GitHub Pages 新報告發布腳本")
    print("=" * 60)

    # 轉換所有新報告
    converted_reports = []
    for report in NEW_REPORTS:
        if convert_markdown_to_html(report['md_path'], report['html_file'], report['title']):
            converted_reports.append(report)

    if not converted_reports:
        print("\n⚠️ 沒有成功轉換任何報告")
        return

    # 更新 index.html
    if update_index_html(converted_reports):
        print("\n✅ 所有新報告已成功發布到 GitHub Pages")
        print("\n下一步：")
        print("  1. cd ~/report")
        print("  2. git add .")
        print("  3. git commit -m '自動發布新研究報告'")
        print("  4. git push")

if __name__ == '__main__':
    main()
