#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QQQ vs GLD 相關性分析
計算過去 200 天的 60 日滾動相關性

作者：Charlie
日期：2026-03-06
"""

import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 設置中文顯示
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

def calculate_rolling_correlation_analysis():
    """計算 QQQ vs GLD 的滾動相關性分析"""
    
    print("\n" + "="*60)
    print("QQQ vs GLD 相關性分析")
    print("="*60)
    
    # 1. 獲取數據
    print("\n第一步：獲取數據")
    print("-"*60)
    
    tickers = ['QQQ', 'GLD']
    
    # 計算日期範圍（過去 200 天 + 60 天緩衝）
    end_date = datetime.now()
    start_date = end_date - timedelta(days=260)
    
    print(f"下載數據：{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}")
    print("正在下載 QQQ 和 GLD 的數據...")
    
    data = yf.download(
        tickers,
        start=start_date.strftime('%Y-%m-%d'),
        end=end_date.strftime('%Y-%m-%d'),
        progress=False,
        auto_adjust=True
    )
    
    # 提取價格數據（優先使用 Adj Close，否則使用 Close）
    if 'Adj Close' in data.columns.levels[0]:
        prices = data['Adj Close']
        print("使用調整後收盤價 (Adj Close)")
    else:
        prices = data['Close']
        print("注意：使用收盤價 (Close) 代替調整後收盤價")
    
    # 檢查數據完整性
    print(f"\n數據質量：")
    print(f"   QQQ：{prices['QQQ'].notna().sum()} 個交易日")
    print(f"   GLD：{prices['GLD'].notna().sum()} 個交易日")
    print(f"   共同交易日：{prices.notna().all(axis=1).sum()} 個")
    
    # 對齊數據（移除任何缺失值）
    prices = prices.dropna()
    
    # 計算日收益率
    returns = prices.pct_change().dropna()
    
    print(f"\n✅ 數據準備完成：{len(returns)} 個交易日")
    print(f"   時間範圍：{returns.index[0]} 至 {returns.index[-1]}")
    
    # 2. 計算滾動相關性
    print("\n第二步：計算滾動相關性（60 日窗口）")
    print("-"*60)
    
    window = 60
    
    # 計算 60 日滾動相關性
    rolling_corr = returns['QQQ'].rolling(window=window).corr(returns['GLD'])
    
    # 只取最近 200 天
    rolling_corr = rolling_corr.iloc[-200:]
    
    print(f"\n滾動相關性統計（最近 200 天）：")
    print(f"   平均值：{rolling_corr.mean():.4f}")
    print(f"   最大值：{rolling_corr.max():.4f}")
    print(f"   最小值：{rolling_corr.min():.4f}")
    print(f"   標準差：{rolling_corr.std():.4f}")
    print(f"   中位數：{rolling_corr.median():.4f}")
    
    # 計算當前相關性
    current_corr = rolling_corr.iloc[-1]
    print(f"\n當前相關性（{rolling_corr.index[-1].strftime('%Y-%m-%d')}）：{current_corr:.4f}")
    
    # 判斷相關性水平
    if abs(current_corr) < 0.2:
        corr_level = "弱相關"
    elif abs(current_corr) < 0.4:
        corr_level = "中等相關"
    elif abs(current_corr) < 0.6:
        corr_level = "較強相關"
    else:
        corr_level = "強相關"
    
    print(f"   相關性水平：{corr_level}")
    
    # 3. 生成每日相關性表格
    print("\n第三步：生成每日相關性表格")
    print("-"*60)
    
    correlation_df = pd.DataFrame({
        '日期': rolling_corr.index,
        '相關係數': rolling_corr.values,
        '相關性水平': pd.cut(
            rolling_corr.abs(),
            bins=[0, 0.2, 0.4, 0.6, 1.0],
            labels=['弱相關', '中等相關', '較強相關', '強相關']
        ),
        '標準化分數': (rolling_corr - rolling_corr.mean()) / rolling_corr.std()
    })
    
    correlation_df['日期'] = correlation_df['日期'].dt.strftime('%Y-%m-%d (%A)')
    
    # 顯示表格
    print("\n最近 30 天的相關性：")
    print(correlation_df[['日期', '相關係數', '相關性水平']].tail(30).to_string(index=False))
    
    # 4. 計算相關性變化趨勢
    print("\n第四步：分析相關性變化趨勢")
    print("-"*60)
    
    # 計算滾動變化（5 日、10 日、20 日）
    rolling_5d = rolling_corr.diff(5)
    rolling_10d = rolling_corr.diff(10)
    rolling_20d = rolling_corr.diff(20)
    
    # 當前趨勢判斷
    recent_5d = rolling_5d.iloc[-1]
    recent_10d = rolling_10d.iloc[-1]
    recent_20d = rolling_20d.iloc[-1]
    
    print(f"\n滾動變化：")
    print(f"   5 日變化：{recent_5d:+.4f}")
    print(f"   10 日變化：{recent_10d:+.4f}")
    print(f"   20 日變化：{recent_20d:+.4f}")
    
    # 判斷趨勢
    if recent_5d > 0.05 and recent_10d > 0.05:
        trend = "顯著上升"
    elif recent_5d < -0.05 and recent_10d < -0.05:
        trend = "顯著下降"
    elif recent_5d > 0:
        trend = "輕微上升"
    elif recent_5d < 0:
        trend = "輕微下降"
    else:
        trend = "穩定"
    
    print(f"\n短期趨勢（5 日）：{trend}")
    
    # 5. 檢測相關性破裂（Crisis Detection）
    print("\n第五步：檢測相關性破裂（Crisis Detection）")
    print("-"*60)
    
    crisis_threshold = 0.2  # 相關性增幅超過 20% 視為異常
    
    # 計算基準相關性（過去 60 天的平均）
    baseline_corr = rolling_corr.rolling(window=60).mean()
    corr_change = (rolling_corr - baseline_corr).abs()
    
    # 檢測異常
    crisis_days = correlation_df[correlation_df['標準化分數'] > 2.0]  # 超過 2 個標準差
    
    print(f"\n相關性異常檢測（|z-score| > 2）：")
    print(f"   發現異常天數：{len(crisis_days)}")
    
    if len(crisis_days) > 0:
        print(f"\n   最近異常日期：")
        for _, row in crisis_days.tail(5).iterrows():
            print(f"     {row['日期']}：相關係數 = {row['相關係數']:.4f} ({row['相關性水平']})")
    else:
        print("   最近 200 天沒有發現顯著相關性異常")
    
    # 6. 區間分析
    print("\n第六步：相關性區間分析")
    print("-"*60)
    
    # 區間分佈
    strong_days = len(correlation_df[correlation_df['相關性水平'] == '強相關'])
    high_days = len(correlation_df[correlation_df['相關性水平'] == '較強相關'])
    medium_days = len(correlation_df[correlation_df['相關性水平'] == '中等相關'])
    low_days = len(correlation_df[correlation_df['相關性水平'] == '弱相關'])
    
    total_days = len(correlation_df)
    
    print(f"\n相關性水平分佈：")
    print(f"   強相關（> 0.6）：{strong_days:3d} 天 ({strong_days/total_days*100:.1f}%)")
    print(f"   較強相關（0.4-0.6）：{high_days:3d} 天 ({high_days/total_days*100:.1f}%)")
    print(f"   中等相關（0.2-0.4）：{medium_days:3d} 天 ({medium_days/total_days*100:.1f}%)")
    print(f"   弱相關（< 0.2）：{low_days:3d} 天 ({low_days/total_days*100:.1f}%)")
    
    # 正負相關
    positive_days = len(correlation_df[correlation_df['相關係數'] > 0])
    negative_days = len(correlation_df[correlation_df['相關係數'] < 0])
    
    print(f"\n相關性方向：")
    print(f"   正相關：{positive_days:3d} 天 ({positive_days/total_days*100:.1f}%)")
    print(f"   負相關：{negative_days:3d} 天 ({negative_days/total_days*100:.1f}%)")
    print(f"   無相關（≈ 0）：{total_days - positive_days - negative_days:3d} 天 ({(total_days - positive_days - negative_days)/total_days*100:.1f}%)")
    
    # 7. 保存結果
    print("\n第七步：保存結果")
    print("-"*60)
    
    # 保存完整表格
    correlation_df.to_csv('qqq_gld_correlation.csv', index=False, encoding='utf-8-sig')
    print("✅ 完整相關性表格已保存：qqq_gld_correlation.csv")
    
    # 8. 繪製圖表
    print("\n第八步：繪製相關性趨勢圖")
    print("-"*60)
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # 圖 1：相關性時間序列
    ax1 = axes[0, 0]
    ax1.plot(rolling_corr.index, rolling_corr.values, 
             color='blue', linewidth=1.5, label='60 日滾動相關性')
    ax1.axhline(y=rolling_corr.mean(), color='red', linestyle='--', 
                linewidth=2, label=f'平均值 ({rolling_corr.mean():.4f})')
    ax1.axhline(y=0, color='gray', linestyle='-', linewidth=1, alpha=0.5)
    ax1.fill_between(rolling_corr.index, 0, rolling_corr.values, 
                     where=(rolling_corr.values > 0), alpha=0.3, color='green', label='正相關區間')
    ax1.fill_between(rolling_corr.index, 0, rolling_corr.values, 
                     where=(rolling_corr.values < 0), alpha=0.3, color='red', label='負相關區間')
    ax1.set_title('QQQ vs GLD 60 日滾動相關性趨勢', fontsize=12, fontweight='bold')
    ax1.set_ylabel('相關係數')
    ax1.legend(loc='upper left', fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim([-1, 1])
    
    # 圖 2：相關性分佈直方圖
    ax2 = axes[0, 1]
    ax2.hist(rolling_corr.values, bins=30, color='skyblue', edgecolor='black', alpha=0.7)
    ax2.axvline(x=rolling_corr.mean(), color='red', linestyle='--', linewidth=2, 
                label=f'平均值 ({rolling_corr.mean():.4f})')
    ax2.axvline(x=rolling_corr.median(), color='green', linestyle='--', linewidth=2, 
                label=f'中位數 ({rolling_corr.median():.4f})')
    ax2.set_title('相關性分佈', fontsize=12, fontweight='bold')
    ax2.set_xlabel('相關係數')
    ax2.set_ylabel('頻率')
    ax2.legend(loc='upper left', fontsize=9)
    ax2.grid(True, alpha=0.3, axis='y')
    
    # 圖 3：相關性區間時間分佈
    ax3 = axes[1, 0]
    ax3.scatter(rolling_corr.index, rolling_corr.values, 
                c=rolling_corr.values, cmap='RdYlGn', 
                s=20, alpha=0.6, vmin=-1, vmax=1)
    ax3.axhline(y=0.6, color='green', linestyle='--', linewidth=1, alpha=0.5, label='強相關閾值')
    ax3.axhline(y=0.4, color='yellow', linestyle='--', linewidth=1, alpha=0.5, label='較強相關閾值')
    ax3.axhline(y=0.2, color='orange', linestyle='--', linewidth=1, alpha=0.5, label='中等相關閾值')
    ax3.axhline(y=-0.2, color='orange', linestyle='--', linewidth=1, alpha=0.5, label='中等負相關閾值')
    ax3.axhline(y=-0.4, color='yellow', linestyle='--', linewidth=1, alpha=0.5, label='較強負相關閾值')
    ax3.axhline(y=-0.6, color='green', linestyle='--', linewidth=1, alpha=0.5, label='強負相關閾值')
    ax3.set_title('相關性時間分佈（顏色表示相關性強度）', fontsize=12, fontweight='bold')
    ax3.set_ylabel('相關係數')
    ax3.legend(loc='upper left', fontsize=8)
    ax3.grid(True, alpha=0.3)
    ax3.set_ylim([-1, 1])
    
    # 添加顏色條
    cbar_ax = fig.add_axes([0.92, 0.54, 0.02, 0.35])
    sm = plt.cm.ScalarMappable(cmap='RdYlGn', norm=plt.Normalize(vmin=-1, vmax=1))
    sm.set_array([])
    cbar = plt.colorbar(sm, cax=cbar_ax)
    cbar.set_label('相關係數')
    
    # 圖 4：滾動變化趨勢
    ax4 = axes[1, 1]
    ax4.plot(rolling_corr.index, rolling_5d.values, 
             color='orange', linewidth=1.5, label='5 日變化', alpha=0.7)
    ax4.plot(rolling_corr.index, rolling_10d.values, 
             color='green', linewidth=1.5, label='10 日變化', alpha=0.7)
    ax4.plot(rolling_corr.index, rolling_20d.values, 
             color='blue', linewidth=1.5, label='20 日變化', alpha=0.7)
    ax4.axhline(y=0, color='gray', linestyle='-', linewidth=1, alpha=0.5)
    ax4.fill_between(rolling_corr.index, 0, rolling_5d.values, 
                     where=(rolling_5d.values > 0), alpha=0.3, color='green')
    ax4.fill_between(rolling_corr.index, 0, rolling_5d.values, 
                     where=(rolling_5d.values < 0), alpha=0.3, color='red')
    ax4.set_title('相關性滾動變化趨勢', fontsize=12, fontweight='bold')
    ax4.set_ylabel('相關性變化')
    ax4.legend(loc='upper left', fontsize=9)
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout(rect=[0, 0, 0.9, 1])
    plt.savefig('qqq_gld_correlation_analysis.png', dpi=300, bbox_inches='tight')
    print("✅ 相關性分析圖已保存：qqq_gld_correlation_analysis.png")
    plt.show()
    
    # 9. 生成摘要報告
    print("\n第九步：生成摘要報告")
    print("-"*60)
    
    summary = f"""
=== QQQ vs GLD 相關性分析摘要 ===

分析期間：{rolling_corr.index[0].strftime('%Y-%m-%d')} 至 {rolling_corr.index[-1].strftime('%Y-%m-%d')}
（共 {len(rolling_corr)} 個交易日）

【相關性統計】
當前相關性：{current_corr:.4f}
平均相關性：{rolling_corr.mean():.4f}
最大相關性：{rolling_corr.max():.4f}
最小相關性：{rolling_corr.min():.4f}
標準差：{rolling_corr.std():.4f}

【相關性水平】
當前水平：{corr_level}
強相關（> 0.6）：{strong_days:3d} 天 ({strong_days/total_days*100:.1f}%)
較強相關（0.4-0.6）：{high_days:3d} 天 ({high_days/total_days*100:.1f}%)
中等相關（0.2-0.4）：{medium_days:3d} 天 ({medium_days/total_days*100:.1f}%)
弱相關（< 0.2）：{low_days:3d} 天 ({low_days/total_days*100:.1f}%)

【相關性方向】
正相關：{positive_days:3d} 天 ({positive_days/total_days*100:.1f}%)
負相關：{negative_days:3d} 天 ({negative_days/total_days*100:.1f}%)
無相關（≈ 0）：{total_days - positive_days - negative_days:3d} 天 ({(total_days - positive_days - negative_days)/total_days*100:.1f}%)

【近期趨勢】
5 日變化：{recent_5d:+.4f}
10 日變化：{recent_10d:+.4f}
20 日變化：{recent_20d:+.4f}
短期趨勢：{trend}

【相關性異常】
發現異常天數：{len(crisis_days)} 天
（|z-score| > 2 的天數）

【投資啟示】
1. QQQ 和 GLD 的相關性{corr_level}，{"適合" if abs(current_corr) < 0.4 else "需要謹慎"}作為分散投資組合。
2. 近期相關性呈{trend}趨勢，{"可以增加配置" if recent_5d > 0 else "需要減少配置"}。
3. 相關性波動較{"大" if rolling_corr.std() > 0.15 else "小"}，{"建議密切監控" if rolling_corr.std() > 0.15 else "相對穩定"}。
"""
    
    print(summary)
    
    # 保存摘要報告
    with open('qqq_gld_correlation_summary.txt', 'w', encoding='utf-8') as f:
        f.write(summary)
    print("\n✅ 摘要報告已保存：qqq_gld_correlation_summary.txt")
    
    return {
        'current_corr': current_corr,
        'mean_corr': rolling_corr.mean(),
        'max_corr': rolling_corr.max(),
        'min_corr': rolling_corr.min(),
        'std_corr': rolling_corr.std(),
        'trend': trend
    }

if __name__ == "__main__":
    results = calculate_rolling_correlation_analysis()
    
    print("\n" + "="*60)
    print("分析完成！")
    print("="*60)
    print(f"分析時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n生成的文件：")
    print("   - qqq_gld_correlation.csv：完整的相關性數據")
    print("   - qqq_gld_correlation_analysis.png：相關性分析圖表")
    print("   - qqq_gld_correlation_summary.txt：摘要報告")
    print("\n" + "="*60)
