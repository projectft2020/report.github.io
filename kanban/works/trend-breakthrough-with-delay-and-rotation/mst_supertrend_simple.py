#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MST + Supertrend 整合策略（簡化版本）
使用最小生成樹選擇低相關性資產 + Supertrend 判斷進場時機

作者：Charlie
日期：2026-03-06
"""

import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import networkx as nx
import seaborn as sns
from scipy.spatial.distance import pdist, squareform
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 設置中文顯示
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

# ============================================
# 核心功能函數
# ============================================

def calculate_supertrend(close, period=10, multiplier=3.0):
    """計算 Supertrend"""
    high = close
    low = close
    
    hl2 = (high + low) / 2
    atr = high - low
    
    upper_band = hl2 + multiplier * atr
    lower_band = hl2 - multiplier * atr
    
    supertrend = np.full(len(close), np.nan)
    trend = np.zeros(len(close))
    
    supertrend[0] = lower_band.iloc[0]
    trend[0] = 1
    
    for i in range(1, len(close)):
        if trend[i-1] == 1:
            if close.iloc[i] <= supertrend[i-1]:
                trend[i] = 0
                supertrend[i] = upper_band.iloc[i]
            else:
                trend[i] = 1
                supertrend[i] = max(supertrend[i-1], lower_band.iloc[i])
        else:
            if close.iloc[i] >= supertrend[i-1]:
                trend[i] = 1
                supertrend[i] = lower_band.iloc[i]
            else:
                trend[i] = 0
                supertrend[i] = min(supertrend[i-1], upper_band.iloc[i])
    
    return pd.Series(supertrend, index=close.index), trend

def build_mst_portfolio(returns, num_assets=8):
    """構建 MST 資產組合"""
    # 計算相關性矩陣
    corr_matrix = returns.corr()
    
    # 計算距離矩陣
    distance_matrix = np.sqrt(2 * (1 - corr_matrix))
    
    # 構建 MST
    n = len(corr_matrix)
    graph = nx.complete_graph(n)
    
    for i, j in graph.edges():
        graph[i][j]['weight'] = distance_matrix.iloc[i, j]
    
    mst = nx.minimum_spanning_tree(graph)
    
    # 按中心性排序
    centrality = nx.eigenvector_centrality_numpy(mst)
    sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
    
    # 選擇前 N 個資產
    selected_indices = [node for node, score in sorted_nodes[:num_assets]]
    selected_assets = [returns.columns[i] for i in selected_indices]
    
    return selected_assets, mst, corr_matrix, distance_matrix

# ============================================
# 主程序
# ============================================

def main():
    """主程序"""
    print("\n" + "="*70)
    print("MST + Supertrend 整合策略（簡化版）")
    print("="*70)
    print(f"開始時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 定義資產池
    asset_pool = ['QQQ', 'GLD', 'SPY', 'IWM', 'TLT', 'VTI', 'AGG', 'VNQ', 'XLE', 'XLF', 'XLK']
    
    print(f"\n資產池：{len(asset_pool)} 個資產")
    print("資產類型：美股、債券、商品、房地產、板塊 ETF")
    
    # 2. 獲取數據
    print("\n第一步：獲取數據")
    print("-"*70)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    data = {}
    for ticker in asset_pool:
        print(f"   下載 {ticker}...", end=' ')
        try:
            df = yf.download(ticker, start=start_date, end=end_date, 
                           progress=False, auto_adjust=True)
            if not df.empty:
                data[ticker] = df
                print(f"✅ ({len(df)} 天)")
            else:
                print(f"❌ 無數據")
        except Exception as e:
            print(f"❌ {str(e)[:30]}")
    
    print(f"✅ 成功下載 {len(data)} 個資產")
    
    # 3. 計算收益率
    print("\n第二步：計算收益率（60 日窗口）")
    print("-"*70)
    
    returns_dict = {}
    for ticker, df in data.items():
        if 'Close' in df.columns:
            series = df['Close'].pct_change().dropna().tail(60)
            if len(series) > 0:
                returns_dict[ticker] = series
                print(f"   {ticker}: {len(series)} 天收益率")
    
    # 手動創建 DataFrame
    if not returns_dict:
        raise ValueError("沒有有效的收益率數據")
    
    # 找到共同日期
    common_dates = None
    for ticker, series in returns_dict.items():
        if common_dates is None:
            common_dates = series.index
        else:
            common_dates = common_dates.intersection(series.index)
    
    if len(common_dates) == 0:
        raise ValueError("沒有找到共同日期")
    
    # 使用共同日期創建 DataFrame
    returns_data = {ticker: list(series.loc[common_dates]) for ticker, series in returns_dict.items()}
    returns_df = pd.DataFrame(returns_data, index=common_dates)
    
    print(f"   收益率數據：{len(returns_df)} 天，{len(returns_df.columns)} 個資產")
    
    # 4. 構建 MST 選擇資產
    print("\n第三步：構建 MST（選擇低相關性資產）")
    print("-"*70)
    
    selected_assets, mst, corr_matrix, dist_matrix = \
        build_mst_portfolio(returns_df, num_assets=8)
    
    print(f"   選中資產數量：{len(selected_assets)}")
    print(f"   選中資產：{', '.join(selected_assets)}")
    
    # 計算平均相關性
    selected_corr = corr_matrix.loc[selected_assets, selected_assets]
    avg_corr = selected_corr.values[np.triu_indices_from(selected_corr.values, k=1)].mean()
    print(f"   平均相關性：{avg_corr:.4f}")
    
    # 5. 生成 Supertrend 信號
    print("\n第四步：生成 Supertrend 信號")
    print("-"*70)
    
    entry_assets = []
    asset_signals = {}
    
    for asset in selected_assets:
        if asset not in data:
            continue
        
        df = data[asset]
        supertrend, trend = calculate_supertrend(df['Close'])
        
        # 檢測信號
        trend_change = np.diff(trend, prepend=trend[0])
        long_signal = trend_change == 1
        
        # 當前狀態
        current_trend = trend[-1]
        current_price = df['Close'].iloc[-1]
        has_long_signal = long_signal[-1]
        
        trend_str = "上漲" if current_trend == 1 else "下跌"
        
        print(f"   {asset}:")
        print(f"      當前價格：${current_price:.2f}")
        print(f"      當前趨勢：{trend_str}")
        print(f"      買入信號：{'✓' if has_long_signal else '✗'}")
        
        asset_signals[asset] = {
            'supertrend': supertrend,
            'trend': trend,
            'long_signal': long_signal,
            'trend_str': trend_str,
            'current_price': current_price
        }
        
        # 只選擇有上漲趨勢且有買入信號的資產
        if current_trend == 1 and has_long_signal:
            entry_assets.append(asset)
            print(f"      ✓ 可以進場")
        elif current_trend == 1:
            print(f"      ○ 持有（上漲趨勢）")
        else:
            print(f"      ✗ 不進場（下跌趨勢）")
    
    print(f"\n   當前可進場資產：{len(entry_assets)}")
    if entry_assets:
        print(f"   進場資產：{', '.join(entry_assets)}")
    
    # 6. 可視化
    print("\n第五步：生成可視化")
    print("-"*70)
    
    # 圖 1：MST 網絡
    fig, ax = plt.subplots(1, 2, figsize=(18, 8))
    
    # 左圖：MST 網絡
    ax1 = ax[0]
    pos = nx.spring_layout(mst, k=3, seed=42)
    
    node_colors = ['green' if asset in selected_assets else 'lightgray' 
                 for asset in returns_df.columns]
    
    edges = list(mst.edges(data=True))
    edge_weights = [d['weight'] for u, v, d in edges]
    
    nx.draw_networkx_nodes(mst, pos, node_color=node_colors, node_size=2000, ax=ax1)
    nx.draw_networkx_edges(mst, pos, width=3, edge_color=edge_weights,
                        edge_cmap=plt.cm.RdYlGn, edge_vmin=0, edge_vmax=2, ax=ax1)
    nx.draw_networkx_labels(mst, pos, 
                          labels={i: returns_df.columns[i] for i in mst.nodes()},
                          font_size=10, font_weight='bold', ax=ax1)
    
    ax1.set_title(f'最小生成樹（MST）\n選中 {len(selected_assets)} 個低相關性資產',
                fontsize=14, fontweight='bold')
    ax1.axis('off')
    
    # 右圖：相關性熱圖
    ax2 = ax[1]
    sns.heatmap(selected_corr, annot=True, fmt='.2f', cmap='RdYlGn',
              center=0, vmin=-1, vmax=1, ax=ax2,
              cbar_kws={'label': '相關係數'})
    ax2.set_title('選中資產的相關性矩陣', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('mst_supertrend_network_simple.png', dpi=300, bbox_inches='tight')
    print("   ✅ 網絡可視化已保存：mst_supertrend_network_simple.png")
    
    # 圖 2：Supertrend 信號
    n_selected = len(selected_assets)
    fig, axes = plt.subplots(n_selected, 1, figsize=(16, 4*n_selected))
    if n_selected == 1:
        axes = [axes]
    
    for idx, asset in enumerate(selected_assets):
        if asset not in asset_signals:
            continue
        
        signals = asset_signals[asset]
        ax = axes[idx]
        df = data[asset]
        
        # 繪製價格和 Supertrend
        ax.plot(df.index, df['Close'], label='價格', linewidth=2, color='blue')
        ax.plot(df.index, signals['supertrend'], 
               label='Supertrend', linewidth=2, linestyle='--', color='red')
        
        # 標記買入點
        long_points = df.index[signals['long_signal']]
        if len(long_points) > 0:
            ax.scatter(long_points, df.loc[long_points, 'Close'], 
                     color='green', s=100, label='買入信號', zorder=5, marker='^')
        
        ax.set_title(f'{asset} - Supertrend 策略\n當前趨勢：{signals["trend_str"]}',
                   fontsize=12, fontweight='bold')
        ax.set_ylabel('價格 ($)')
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('mst_supertrend_signals_simple.png', dpi=300, bbox_inches='tight')
    print("   ✅ 信號可視化已保存：mst_supertrend_signals_simple.png")
    
    # 7. 生成摘要報告
    print("\n第六步：生成摘要報告")
    print("-"*70)
    
    summary = f"""
=== MST + Supertrend 整合策略分析摘要 ===

分析時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

【資產選擇（MST）】
總資產池：{len(asset_pool)} 個
選中資產：{len(selected_assets)} 個
平均相關性：{avg_corr:.4f}

選中的資產：
{', '.join(selected_assets)}

【進場資產（Supertrend）】
當前可進場資產：{len(entry_assets)} 個
{', '.join(entry_assets) if entry_assets else '無'}

【策略優勢】
1. 網絡分散：使用 MST 確保資產之間相關性較低（平均 {avg_corr:.2f}）
2. 趨勢確認：使用 Supertrend 確認進場時機
3. 動態調整：根據市場相關性變化動態調整組合
4. 風險控制：只在上漲趨勢時進場，避免下跌風險

【投資建議】
- 如果進場資產 >= 3 個：可以考慮建倉，等權重配置
- 如果進場資產 = 1-2 個：謹慎建倉，建議觀望
- 如果進場資產 = 0 個：保持空倉，等待機會

【組合配置建議】
如果決定進場，建議：
- 單一資產最大權重：20%
- 現金保留：20-40%
- 定期重新平衡（每週或每月）
- 監控相關性變化（每週檢查 MST）
"""
    
    print(summary)
    
    # 保存摘要
    with open('mst_supertrend_summary.txt', 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print("\n" + "="*70)
    print("分析完成！")
    print("="*70)
    print(f"結束時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n生成的文件：")
    print("   - mst_supertrend_network_simple.png：MST 網絡可視化")
    print("   - mst_supertrend_signals_simple.png：Supertrend 信號圖")
    print("   - mst_supertrend_summary.txt：摘要報告")
    print("\n" + "="*70)

if __name__ == "__main__":
    main()
