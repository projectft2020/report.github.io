#!/usr/bin/env python3
"""
將新的優化動能策略報告轉換為 HTML 格式
"""

import os
import markdown
from datetime import datetime
import re

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

def convert_new_reports():
    """轉換新的優化動能策略報告"""

    target_dir = "/Users/charlie/report"

    os.makedirs(target_dir, exist_ok=True)

    reports = [
        {
            'filepath': '/Users/charlie/.openclaw/workspace-automation/kanban/projects/quant-evolve-20260219/q005-final-report.md',
            'title': 'QuantEvolve 多智能體演化框架完整報告',
            'description': '多智能體演化策略發現機制 - 技術可行性評估與實作路徑'
        },
        {
            'filepath': '/Users/charlie/.openclaw/workspace-automation/kanban/projects/quant-evolve-20260219/q001-paper-analysis.md',
            'title': 'QuantEvolve 論文深度分析',
            'description': '多智能體演化機制與自動化策略發現原理解析'
        },
        {
            'filepath': '/Users/charlie/.openclaw/workspace-automation/kanban/projects/quant-evolve-20260219/q002-framework-design.md',
            'title': 'QuantEvolve 策略框架設計',
            'description': '智能體設計、適應度函數、演化算法架構'
        },
        {
            'filepath': '/Users/charlie/.openclaw/workspace-automation/kanban/projects/quant-evolve-20260219/q003-prototype.md',
            'title': 'QuantEvolve 原型實作',
            'description': '原型系統開發與策略演化能力測試'
        },
        {
            'filepath': '/Users/charlie/.openclaw/workspace-automation/kanban/projects/quant-evolve-20260219/q004-backtest.md',
            'title': 'QuantEvolve 回測驗證',
            'description': '歷史數據驗證演化策略有效性'
        },
        {
            'filepath': '/Users/charlie/.openclaw/workspace-automation/kanban/projects/work/w008-final-report.md',
            'title': '優化動能策略完整報告',
            'description': '策略優化、回測驗證與改進建議 - 年化回報 14.65%，夏普比率 18.58'
        },
        {
            'filepath': '/Users/charlie/.openclaw/workspace-automation/kanban/projects/quant-research-20260217/r002-momentum-backtest.md',
            'title': '基礎動能策略回測最終報告',
            'description': '10/60/200 MA 動能策略完整回測結果 - 15年總回報 674.48%'
        },
        {
            'filepath': '/Users/charlie/.openclaw/workspace-automation/kanban/projects/work/w007-strategy-verification.md',
            'title': '動能策略驗證報告',
            'description': '策略代碼驗證與初步回測結果'
        },
        {
            'filepath': '/Users/charlie/.openclaw/workspace-automation/kanban/projects/trend-trading-20260219/t006-ml-trend.md',
            'title': '完整趨勢交易系統整合',
            'description': '六層系統架構：數據處理 → 策略分析 → 風險管理 → 執行 → 監控 → 優化'
        },
        {
            'filepath': '/Users/charlie/.openclaw/workspace-automation/kanban/projects/trend-trading-20260219/t005-tail-hedge.md',
            'title': '趨勢跟隮 + 尾部風險對沖',
            'description': '看跌期權、VIX 期權、CPPI、Delta 對沖等四種對沖方法與動態對沖比例調整'
        },
        {
            'filepath': '/Users/charlie/.openclaw/workspace-automation/kanban/projects/trend-trading-20260219/t004-volatility-adaptive.md',
            'title': '波動率適應性趨勢跟隮',
            'description': '四種波動率測量方法 + 五級波動率分類 + Kelly 公式集成'
        },
        {
            'filepath': '/Users/charlie/.openclaw/workspace-automation/kanban/projects/trend-trading-20260219/t003-failure-monitor.md',
            'title': '趨勢策略失效監控系統',
            'description': '四大失效模式監控 + 四級預警系統 + 自動應對措施'
        },
        {
            'filepath': '/Users/charlie/.openclaw/workspace-automation/kanban/projects/trend-trading-20260219/t002-multi-timeframe.md',
            'title': '多時間框架趨勢確認策略',
            'description': '三層結構（D1/H4/H1）+ 多層驗證機制 + 動態倉位管理'
        },
        {
            'filepath': '/Users/charlie/.openclaw/workspace-automation/kanban/projects/trend-trading-20260219/t001-strength-score.md',
            'title': '趨勢強度評分系統',
            'description': '綜合 ADX、MACD、趨勢線分析算法與智能信號過濾'
        },
        {
            'filepath': '/Users/charlie/.openclaw/workspace-automation/kanban/projects/risk-management-20260219/s001-distribution-metrics.md',
            'title': '收益分佈作為策略評估指標研究',
            'description': '三維度評估框架（偏度 + 峰度 + 肥尾指數）- 替代 Sharpe Ratio 的風險度量方法'
        },
        {
            'filepath': '/Users/charlie/.openclaw/workspace-automation/kanban/projects/risk-management-20260219/s002-fat-tail-risks.md',
            'title': '肥尾市場下傳統風險指標失效研究',
            'description': 'VaR/CVaR/標準差失效分析與替代風險度量方法'
        },
        {
            'filepath': '/Users/charlie/.openclaw/workspace-automation/kanban/projects/risk-management-20260219/s003-dynamic-risk-control.md',
            'title': '非傳統止損策略研究',
            'description': '動態風控系統（年化淨收益 +11.1%）- 漸進式降風險 vs 傳統止損'
        },
        {
            'filepath': '/Users/charlie/.openclaw/workspace-automation/kanban/projects/adaptive-hedge-20260219/h001-risk-state-assessment.md',
            'title': '風險狀態評估系統',
            'description': '四級風險狀態機（低/中/高/極高）- 提前 12 天預警 2008 危機'
        },
        {
            'filepath': '/Users/charlie/.openclaw/workspace-automation/kanban/projects/adaptive-hedge-20260219/h002-dynamic-hedge-decision.md',
            'title': '動態對沖決策機制',
            'description': '智能對沖系統 - 漸進式對沖比例調整與四種對沖方式整合'
        },
        {
            'filepath': '/Users/charlie/.openclaw/workspace-automation/kanban/projects/momentum-dist-risk-20260219/m001-momentum-distribution.md',
            'title': '動能策略收益分佈分析',
            'description': '動能策略偏度、峰度、肥尾指數計算與風險評估'
        }
    ]
    
    print("🚀 開始轉換新的優化動能策略報告...")

    for report in reports:
        source_path = report['filepath']

        if os.path.exists(source_path):
            filename = os.path.basename(source_path)
            print(f"📖 正在處理: {filename}")

            try:
                with open(source_path, 'r', encoding='utf-8') as f:
                    md_content = f.read()

                html_content = convert_markdown_to_html(md_content, report['title'])

                full_html = create_html_template(
                    report['title'],
                    html_content,
                    filename,
                    report.get('description', '')
                )

                output_filename = filename.replace('.md', '.html')
                output_path = os.path.join(target_dir, output_filename)

                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(full_html)

                print(f"✅ 轉換完成: {filename} → {output_filename}")

            except Exception as e:
                print(f"❌ 轉換失敗: {filename} - {str(e)}")
        else:
            print(f"❌ 檔案不存在: {report['filepath']}")

    print("✨ 新報告轉換完成！")

if __name__ == "__main__":
    convert_new_reports()
