#!/usr/bin/env python3
"""
轉換今天（2026-02-20）完成的研究報告到 HTML
"""

import os
import sys
sys.path.insert(0, '/Users/charlie/report')

from convert_new_reports import clean_markdown_content, create_html_template
import markdown

# 今天完成的研究報告列表
reports = [
    # Skewness-Kurtosis Research
    {
        'filepath': '/Users/charlie/.openclaw/workspace/kanban/projects/skewness-kurtosis-research-20260220/k001-skewness-factor.md',
        'title': '偏度因子實作與回測',
        'description': '偏度因子計算與回測框架（年化收益 11.5%，夏普比率 0.76）'
    },
    {
        'filepath': '/Users/charlie/.openclaw/workspace/kanban/projects/skewness-kurtosis-research-20260220/k002-coskewness-portfolio.md',
        'title': '協偏度組合構建',
        'description': '協偏度優化顯著降低尾部風險（1% VaR 改善 40%，最大回撤減少 25-35%）'
    },
    {
        'filepath': '/Users/charlie/.openclaw/workspace/kanban/projects/skewness-kurtosis-research-20260220/k003-risk-adjusted-metrics.md',
        'title': '風險調整指標評估',
        'description': '完整的風險調整指標評估框架（11+ 指標），推薦 SKTASR 為主要指標'
    },
    {
        'filepath': '/Users/charlie/.openclaw/workspace/kanban/projects/skewness-kurtosis-research-20260220/k004-final-report.md',
        'title': '協偏度綜合研究報告',
        'description': '偏度因子、協偏度組合、風險調整指標的完整研究總結'
    },
    
    # Barra Multi-Factor Research
    {
        'filepath': '/Users/charlie/.openclaw/workspace/kanban/projects/barra-multifactor-research-20260220/b001-architecture.md',
        'title': 'Barra 模型基礎架構設計',
        'description': 'Barra 多因子模型的完整架構設計與實施路徑'
    },
    {
        'filepath': '/Users/charlie/.openclaw/workspace/kanban/projects/barra-multifactor-research-20260220/b002-factor-library.md',
        'title': '核心因子庫構建',
        'description': '8 大核心風格因子實現（Size、Momentum、Volatility、Value、Profitability、Growth、Leverage、Liquidity）'
    },
    {
        'filepath': '/Users/charlie/.openclaw/workspace/kanban/projects/barra-multifactor-research-20260220/b003-attribution.md',
        'title': '因子歸因系統',
        'description': 'Brinson 歸因模型 + Barra 因子歸因，完整 Python 實現'
    },
    {
        'filepath': '/Users/charlie/.openclaw/workspace/kanban/projects/barra-multifactor-research-20260220/b004-validation.md',
        'title': '模型驗證與優化',
        'description': '最佳策略：動態權重多因子組合（年化收益 9.2%，夏普比率 0.63）'
    },
    
    # Regime Detection
    {
        'filepath': '/Users/charlie/.openclaw/workspace/kanban/projects/regime-detection-20260220/r001-model-selection.md',
        'title': 'Regime Detection 模型選擇',
        'description': 'Transformer 性能最佳（RMSE 41.87），推薦 HMM + Bayesian Change Point 混合模型'
    },
    {
        'filepath': '/Users/charlie/.openclaw/workspace/kanban/projects/regime-detection-20260220/r002-feature-engineering.md',
        'title': '狀態識別特徵工程',
        'description': '80+ 種特徵設計（價格、波動率、趨勢、情緒、宏觀、關聯性）'
    },
    {
        'filepath': '/Users/charlie/.openclaw/workspace/kanban/projects/regime-detection-20260220/r003-trend-integration.md',
        'title': '趨勢強度集成',
        'description': 'TrendStrengthIntegrator + RegimeTrendHybrid + BayesianTrendDetector 類實現'
    },
    
    # Advanced Performance Metrics
    {
        'filepath': '/Users/charlie/.openclaw/workspace/kanban/projects/advanced-performance-metrics-research-20260220/m001-advanced-metrics.md',
        'title': '高級績效指標研究',
        'description': 'Omega Ratio、Conditional Sharpe Ratio、Kappa Ratio、Expected Shortfall 完整研究'
    },
    
    # Black Monday Research
    {
        'filepath': '/Users/charlie/.openclaw/workspace/kanban/projects/black-monday-1987-20260220/pj001-black-monday-analysis.md',
        'title': 'Black Monday 事件研究',
        'description': '1987 年股市崩盤深度分析，歷史事件研究與啟示'
    }
]

def convert_markdown_to_html(md_content, title):
    """轉換 Markdown 到 HTML"""
    # 清理內容
    md_content = clean_markdown_content(md_content)
    
    # 轉換為 HTML
    html_content = markdown.markdown(
        md_content,
        extensions=[
            'tables',
            'fenced_code',
            'codehilite',
            'toc',
            'nl2br',
            'sane_lists'
        ]
    )
    
    return html_content

# 目標目錄
target_dir = '/Users/charlie/report'
os.makedirs(target_dir, exist_ok=True)

print("🚀 開始轉換今天（2026-02-20）完成的研究報告...")

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

print("✨ 今天的研究報告轉換完成！")
