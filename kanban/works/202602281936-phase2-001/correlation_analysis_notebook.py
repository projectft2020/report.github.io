#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
美股前 30 股票相關性分析與組合優化
完整可執行腳本

作者：Charlie
日期：2026-03-06
"""

import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from datetime import datetime, timedelta
from scipy import stats
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')

# 設置中文顯示
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

# ============================================
# 第一部分：數據獲取與處理
# ============================================

# 美股前 30 股票（道瓊斯工業指數成分股）
DJIA_30 = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA',
    'NVDA', 'META', 'JPM', 'V', 'WMT',
    'HD', 'MA', 'BAC', 'UNH', 'PFE',
    'DIS', 'KO', 'CSCO', 'XOM', 'CVX',
    'MRK', 'ABBV', 'PEP', 'INTC', 'DHR',
    'CAT', 'NKE', 'MCD', 'IBM', 'GS'
]

def get_stock_data(tickers, start_date, end_date):
    """獲取股票歷史數據"""
    print(f"\n{'='*60}")
    print(f"第一步：獲取 {len(tickers)} 隻股票的歷史數據")
    print(f"{'='*60}")
    
    print(f"時間範圍：{start_date} 至 {end_date}")
    print("正在下載數據（這可能需要幾分鐘）...")
    
    # 下載數據
    data = yf.download(
        tickers,
        start=start_date,
        end=end_date,
        progress=True
    )
    
    # 提取調整後收盤價
    prices = data['Adj Close']
    
    # 計算日收益率
    returns = prices.pct_change().dropna()
    
    # 提取成交量
    volumes = data['Volume']
    
    print(f"\n✅ 數據獲取完成")
    print(f"   交易日數量：{prices.shape[0]}")
    print(f"   股票數量：{prices.shape[1]}")
    print(f"   時間範圍：{prices.index[0]} 至 {prices.index[-1]}")
    print(f"   缺失值：{prices.isna().sum().sum()} 個")
    
    return prices, volumes, returns

def clean_data(returns, max_missing_pct=0.05):
    """清理數據"""
    print(f"\n{'='*60}")
    print("第二步：數據清理")
    print(f"{'='*60}")
    
    # 1. 移除缺失值過多的股票
    missing_pct = returns.isna().sum() / len(returns)
    removed_tickers = missing_pct[missing_pct > max_missing_pct].index.tolist()
    
    if removed_tickers:
        print(f"⚠️  移除缺失值過多的股票：{removed_tickers}")
        cleaned_returns = returns.drop(columns=removed_tickers)
    else:
        cleaned_returns = returns.copy()
        print("✅ 沒有缺失值過多的股票")
    
    # 2. 前向填充 + 後向填充
    cleaned_returns = cleaned_returns.fillna(method='ffill').fillna(method='bfill')
    
    # 3. 移除殘留缺失值
    cleaned_returns = cleaned_returns.dropna()
    
    # 4. 檢測異常值
    for ticker in cleaned_returns.columns:
        mean = cleaned_returns[ticker].mean()
        std = cleaned_returns[ticker].std()
        outliers = np.abs(cleaned_returns[ticker] - mean) > 10 * std
        
        if outliers.sum() > 0:
            print(f"⚠️  {ticker} 發現 {outliers.sum()} 個異常值（已替換為平均值）")
            cleaned_returns.loc[outliers, ticker] = mean
    
    print(f"\n✅ 數據清理完成")
    print(f"   股票數量：{cleaned_returns.shape[1]}")
    print(f"   交易日數量：{cleaned_returns.shape[0]}")
    
    return cleaned_returns, removed_tickers

# ============================================
# 第二部分：相關性分析
# ============================================

def calculate_rolling_correlation(returns, window=252):
    """計算滾動相關性矩陣"""
    print(f"\n{'='*60}")
    print(f"第三步：計算滾動相關性（窗口 = {window} 天）")
    print(f"{'='*60}")
    
    # 計算滾動相關性
    rolling_corr = returns.rolling(window=window).corr()
    
    # 移除前 window-1 行
    rolling_corr = rolling_corr.dropna(how='all')
    
    print(f"\n✅ 滾動相關性計算完成")
    print(f"   時間點數量：{rolling_corr.shape[0]}")
    print(f"   資產數量：{rolling_corr.shape[1]}")
    
    return rolling_corr

def analyze_average_correlation_trend(rolling_corr, market_returns):
    """分析平均相關性趨勢（Preis 方法）"""
    print(f"\n{'='*60}")
    print("第四步：分析平均相關性趨勢（驗證 Preis 等人的發現）")
    print(f"{'='*60}")
    
    # 1. 計算平均相關性（排除對角線）
    n_assets = rolling_corr.shape[1]
    avg_correlation = []
    
    for date in rolling_corr.index.levels[0]:
        corr_matrix = rolling_corr.loc[date]
        
        # 計算上三角矩陣的平均值
        upper_triangle = []
        for i in range(n_assets):
            for j in range(i+1, n_assets):
                upper_triangle.append(corr_matrix.iloc[i, j])
        
        avg_corr = np.mean(upper_triangle)
        avg_correlation.append(avg_corr)
    
    avg_correlation = pd.Series(avg_correlation, index=rolling_corr.index.levels[0])
    
    # 2. 標準化市場回報
    market_returns_norm = (market_returns - market_returns.mean()) / market_returns.std()
    
    # 3. 分離正負市場回報
    pos_returns = market_returns_norm[market_returns_norm > 0]
    neg_returns = market_returns_norm[market_returns_norm < 0]
    
    # 4. 對應的平均相關性
    pos_corr = avg_correlation.loc[pos_returns.index]
    neg_corr = avg_correlation.loc[neg_returns.index]
    
    # 5. 線性回歸
    slope_pos, intercept_pos, r_value_pos, p_value_pos, std_err_pos = stats.linregress(
        pos_returns, pos_corr
    )
    
    slope_neg, intercept_neg, r_value_neg, p_value_neg, std_err_neg = stats.linregress(
        neg_returns, neg_corr
    )
    
    # 6. 結果
    print("\n📊 線性回歸結果：")
    print(f"\n正回報（上升市場）：")
    print(f"   方程：C = {slope_pos:.3f} × R + {intercept_pos:.3f}")
    print(f"   R² = {r_value_pos**2:.3f}")
    print(f"   p-value = {p_value_pos:.2e}")
    print(f"   (a+ = {slope_pos:.3f} ± {std_err_pos:.3f})")
    
    print(f"\n負回報（下跌市場）：")
    print(f"   方程：C = {slope_neg:.3f} × R + {intercept_neg:.3f}")
    print(f"   R² = {r_value_neg**2:.3f}")
    print(f"   p-value = {p_value_neg:.2e}")
    print(f"   (a- = {slope_neg:.3f} ± {std_err_neg:.3f})")
    
    # 7. 驗證 Preis 的發現
    print(f"\n🔍 驗證 Preis 等人的發現（Nature Scientific Reports 2012）：")
    print(f"   Preis 的發現：|a-| > a+（負回報時相關性斜率更大）")
    print(f"   我們的結果：|{slope_neg:.3f}| > {slope_pos:.3f}")
    print(f"   結論：{'✅ 確認' if abs(slope_neg) > slope_pos else '❌ 未確認'}")
    
    if abs(slope_neg) > slope_pos:
        print(f"\n   ⚠️  相關性破壞現象確認！")
        print(f"   當市場下跌時，股票相關性會顯著增加，")
        print(f"   這導致分散投資在最需要的時候失效。")
    
    return {
        'avg_correlation': avg_correlation,
        'market_returns': market_returns,
        'pos_slope': slope_pos,
        'pos_intercept': intercept_pos,
        'pos_r2': r_value_pos**2,
        'neg_slope': slope_neg,
        'neg_intercept': intercept_neg,
        'neg_r2': r_value_neg**2,
        'pos_data': pd.DataFrame({'R': pos_returns, 'C': pos_corr}),
        'neg_data': pd.DataFrame({'R': neg_returns, 'C': neg_corr})
    }

def plot_correlation_trend(analysis_results):
    """繪製相關性趨勢圖"""
    print(f"\n{'='*60}")
    print("第五步：繪製相關性趨勢圖")
    print(f"{'='*60}")
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. 平均相關性時間序列
    ax1 = axes[0, 0]
    ax1.plot(analysis_results['avg_correlation'].index,
             analysis_results['avg_correlation'].values,
             label='平均相關性', color='blue', linewidth=1.5)
    ax1.axhline(y=analysis_results['avg_correlation'].mean(),
                color='red', linestyle='--', linewidth=2, label='平均值')
    ax1.set_title('平均相關性時間序列（2020-2026）', fontsize=12, fontweight='bold')
    ax1.set_ylabel('相關係數')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. 正回報：相關性 vs 市場回報
    ax2 = axes[0, 1]
    pos_data = analysis_results['pos_data']
    ax2.scatter(pos_data['R'], pos_data['C'], alpha=0.3, s=10, color='green')
    
    x_pos = np.linspace(pos_data['R'].min(), pos_data['R'].max(), 100)
    y_pos = (analysis_results['pos_slope'] * x_pos +
             analysis_results['pos_intercept'])
    ax2.plot(x_pos, y_pos, color='red', linewidth=2,
             label=f'C = {analysis_results["pos_slope"]:.3f}R + {analysis_results["pos_intercept"]:.3f}')
    
    ax2.set_title('正回報：相關性 vs 市場回報', fontsize=12, fontweight='bold')
    ax2.set_xlabel('標準化市場回報 (R)')
    ax2.set_ylabel('平均相關性 (C+)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. 負回報：相關性 vs 市場回報
    ax3 = axes[1, 0]
    neg_data = analysis_results['neg_data']
    ax3.scatter(neg_data['R'], neg_data['C'], alpha=0.3, s=10, color='red')
    
    x_neg = np.linspace(neg_data['R'].min(), neg_data['R'].max(), 100)
    y_neg = (analysis_results['neg_slope'] * x_neg +
             analysis_results['neg_intercept'])
    ax3.plot(x_neg, y_neg, color='blue', linewidth=2,
             label=f'C = {analysis_results["neg_slope"]:.3f}R + {analysis_results["neg_intercept"]:.3f}')
    
    ax3.set_title('負回報：相關性 vs 市場回報', fontsize=12, fontweight='bold')
    ax3.set_xlabel('標準化市場回報 (R)')
    ax3.set_ylabel('平均相關性 (C-)')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. 對比正負回報
    ax4 = axes[1, 1]
    
    ax4.scatter(pos_data['R'], pos_data['C'], alpha=0.3, s=10,
               color='green', label='正回報')
    ax4.plot(x_pos, y_pos, color='green', linewidth=2,
             label=f'C+ (R² = {analysis_results["pos_r2"]:.3f})')
    
    ax4.scatter(neg_data['R'], neg_data['C'], alpha=0.3, s=10,
               color='red', label='負回報')
    ax4.plot(x_neg, y_neg, color='red', linewidth=2,
             label=f'C- (R² = {analysis_results["neg_r2"]:.3f})')
    
    ax4.set_title('正負回報對比', fontsize=12, fontweight='bold')
    ax4.set_xlabel('標準化市場回報 (R)')
    ax4.set_ylabel('平均相關性 (C)')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('correlation_trend_analysis.png', dpi=300, bbox_inches='tight')
    print("\n✅ 相關性趨勢圖已保存：correlation_trend_analysis.png")
    plt.show()

# ============================================
# 第三部分：網絡分析
# ============================================

def correlation_to_distance(corr_matrix):
    """將相關性矩陣轉為距離矩陣（Mantegna 方法）"""
    corr_matrix_clipped = np.clip(corr_matrix, -1, 1)
    distance_matrix = np.sqrt(2 * (1 - corr_matrix_clipped))
    np.fill_diagonal(distance_matrix, 0)
    return distance_matrix

def build_mst(returns, window=252):
    """構建最小生成樹"""
    print(f"\n{'='*60}")
    print(f"第六步：構建最小生成樹（MST）")
    print(f"{'='*60}")
    
    # 1. 計算相關性矩陣
    corr_matrix = returns.iloc[-window:].corr()
    
    # 2. 轉為距離矩陣
    distance_matrix = correlation_to_distance(corr_matrix.values)
    
    # 3. 構建完全圖
    G = nx.from_numpy_array(distance_matrix)
    
    # 4. 計算最小生成樹
    mst = nx.minimum_spanning_tree(G)
    
    # 5. 添加節點標籤
    node_labels = {i: ticker for i, ticker in enumerate(returns.columns)}
    mst = nx.relabel_nodes(mst, node_labels)
    
    print(f"\n✅ 最小生成樹構建完成")
    print(f"   節點數量：{mst.number_of_nodes()}")
    print(f"   邊數量：{mst.number_of_edges()}")
    print(f"   網絡密度：{nx.density(mst):.3f}")
    print(f"   網絡直徑：{nx.diameter(mst)}")
    print(f"   平均路徑長度：{nx.average_shortest_path_length(mst):.2f}")
    
    return mst, corr_matrix

def calculate_network_metrics(mst):
    """計算網絡指標"""
    print(f"\n{'='*60}")
    print("第七步：計算網絡指標")
    print(f"{'='*60}")
    
    # 1. 度中心性
    degree_centrality = nx.degree_centrality(mst)
    
    # 2. 介數中心性
    betweenness_centrality = nx.betweenness_centrality(mst)
    
    # 3. 特徵向量中心性
    eigenvector_centrality = nx.eigenvector_centrality(mst, max_iter=1000)
    
    # 4. 接近中心性
    closeness_centrality = nx.closeness_centrality(mst)
    
    # 5. 組織成 DataFrame
    metrics_df = pd.DataFrame({
        'Degree Centrality': degree_centrality,
        'Betweenness Centrality': betweenness_centrality,
        'Eigenvector Centrality': eigenvector_centrality,
        'Closeness Centrality': closeness_centrality
    })
    
    # 按度中心性排序
    metrics_df = metrics_df.sort_values('Degree Centrality', ascending=False)
    
    print(f"\n📊 網絡指標統計：")
    print(f"\n度中心性前 5 名（系統性重要股票）：")
    print(metrics_df.head(5).to_string())
    
    print(f"\n度中心性後 5 名（獨立性較高股票）：")
    print(metrics_df.tail(5).to_string())
    
    return metrics_df

def detect_communities(mst):
    """社群檢測"""
    print(f"\n{'='*60}")
    print("第八步：社群檢測（Louvain 算法）")
    print(f"{'='*60}")
    
    # 使用標籤傳播算法（不需要額外套件）
    communities = list(nx.community.label_propagation_communities(mst))
    
    # 按社群大小排序
    communities = sorted(communities, key=len, reverse=True)
    
    # 創建 {股票: 社群ID} 字典
    community_dict = {}
    for i, community in enumerate(communities):
        for stock in community:
            community_dict[stock] = i
    
    print(f"\n✅ 社群檢測完成")
    print(f"   發現 {len(communities)} 個社群")
    
    for i, community in enumerate(communities):
        print(f"\n   社群 {i} ({len(community)} 隻股票):")
        print(f"   {', '.join(community)}")
    
    return communities, community_dict

def plot_mst_network(mst, community_dict=None):
    """繪製 MST 網絡"""
    print(f"\n{'='*60}")
    print("第九步：繪製 MST 網絡")
    print(f"{'='*60}")
    
    fig, ax = plt.subplots(figsize=(20, 16))
    
    # 計算佈局
    pos = nx.spring_layout(mst, k=3, iterations=50, seed=42)
    
    # 1. 社群著色
    if community_dict is not None:
        colors = plt.cm.Set3(range(len(set(community_dict.values()))))
        node_colors = [colors[community_dict[node]] for node in mst.nodes()]
    else:
        node_colors = 'lightblue'
    
    # 2. 節點大小（根據度中心性）
    degree_centrality = nx.degree_centrality(mst)
    node_sizes = [degree_centrality[node] * 5000 for node in mst.nodes()]
    
    # 3. 繪製邊
    nx.draw_networkx_edges(
        mst,
        pos,
        width=2,
        alpha=0.5,
        edge_color='gray',
        ax=ax
    )
    
    # 4. 繪製節點
    nx.draw_networkx_nodes(
        mst,
        pos,
        node_color=node_colors,
        node_size=node_sizes,
        alpha=0.8,
        ax=ax
    )
    
    # 5. 繪製標籤
    nx.draw_networkx_labels(
        mst,
        pos,
        font_size=10,
        font_weight='bold',
        ax=ax
    )
    
    ax.set_title(
        '美股前 30 股票最小生成樹（MST）網絡\n'
        '節點大小 = 度中心性，顏色 = 社群',
        fontsize=16,
        fontweight='bold'
    )
    
    # 6. 添加圖例
    if community_dict is not None:
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], marker='o', color='w',
                   markerfacecolor=colors[i], markersize=15,
                   label=f'社群 {i}')
            for i in range(len(set(community_dict.values())))
        ]
        ax.legend(handles=legend_elements, loc='upper left', fontsize=10)
    
    ax.axis('off')
    plt.tight_layout()
    plt.savefig('mst_network.png', dpi=300, bbox_inches='tight')
    print("\n✅ MST 網絡圖已保存：mst_network.png")
    plt.show()

# ============================================
# 第四部分：投資組合優化
# ============================================

def mst_based_portfolio(mst, returns, method='inverse_degree'):
    """基於 MST 的投資組合"""
    print(f"\n{'='*60}")
    print(f"第十步：構建基於 MST 的投資組合（方法：{method}）")
    print(f"{'='*60}")
    
    # 計算度中心性
    degree_centrality = nx.degree_centrality(mst)
    
    # 計算權重
    if method == 'inverse_degree':
        weights = pd.Series({node: 1.0 / (dc + 0.01)
                            for node, dc in degree_centrality.items()})
    elif method == 'equal':
        weights = pd.Series({node: 1.0 / len(mst.nodes())
                            for node in mst.nodes()})
    elif method == 'random':
        weights = pd.Series({node: np.random.rand()
                            for node in mst.nodes()})
    
    # 歸一化
    weights = weights / weights.sum()
    
    # 只包含有數據的股票
    valid_stocks = list(set(weights.index) & set(returns.columns))
    weights = weights[valid_stocks]
    weights = weights / weights.sum()
    
    print(f"\n✅ MST 投資組合構建完成")
    print(f"   股票數量：{len(weights)}")
    print(f"\n權重前 5 名：")
    print(weights.head(5).to_string())
    
    return weights

def eigen_portfolios(returns, n_components=5):
    """構建特徵組合"""
    print(f"\n{'='*60}")
    print(f"第十一步：構建特徵組合（n_components = {n_components}）")
    print(f"{'='*60}")
    
    # 1. 標準化收益率
    returns_standardized = (returns - returns.mean()) / returns.std()
    
    # 2. 計算相關性矩陣
    corr_matrix = returns_standardized.corr()
    
    # 3. PCA 分解
    pca = PCA(n_components=n_components)
    pca.fit(corr_matrix)
    
    # 4. 獲取特徵向量
    eigenvectors = pca.components_.T
    
    # 5. 構建特徵組合權重
    eigen_weights = pd.DataFrame(
        eigenvectors,
        index=returns.columns,
        columns=[f'EP{i+1}' for i in range(n_components)]
    )
    
    # 6. 計算每個特徵組合的夏普比率（樣本內）
    eigen_sharpe = {}
    for i in range(n_components):
        ep_returns = (returns_standardized * eigen_weights[f'EP{i+1}']).sum(axis=1)
        sharpe = ep_returns.mean() / ep_returns.std() * np.sqrt(252)
        eigen_sharpe[f'EP{i+1}'] = sharpe
    
    # 7. 解釋方差
    explained_variance = pca.explained_variance_ratio_
    
    print(f"\n✅ 特徵組合構建完成")
    print(f"   解釋方差：{explained_variance}")
    print(f"   樣本內夏普比率：{eigen_sharpe}")
    
    # 8. 組合策略（等權重）
    ensemble_weight = 1.0 / n_components
    ensemble_weights = eigen_weights * ensemble_weight
    
    # 計算組合回報
    ensemble_returns = (returns_standardized * ensemble_weights).sum(axis=1)
    ensemble_sharpe = ensemble_returns.mean() / ensemble_returns.std() * np.sqrt(252)
    
    print(f"\n   組合策略夏普比率：{ensemble_sharpe:.3f}")
    
    return eigen_weights, ensemble_weights

def equal_weight_portfolio(returns):
    """等權重組合（基準）"""
    print(f"\n{'='*60}")
    print("第十二步：構建等權重組合（基準）")
    print(f"{'='*60}")
    
    weights = pd.Series(1.0 / len(returns.columns), index=returns.columns)
    
    print(f"\n✅ 等權重組合構建完成")
    print(f"   股票數量：{len(weights)}")
    print(f"   每隻股票權重：{1.0/len(returns.columns):.4f}")
    
    return weights

# ============================================
# 第五部分：回測驗證
# ============================================

def backtest_strategy(weights, returns, name="Strategy"):
    """回測單一策略"""
    print(f"\n{'='*60}")
    print(f"第十三步：回測 {name}")
    print(f"{'='*60}")
    
    # 計算組合回報
    portfolio_returns = (returns * weights).sum(axis=1)
    
    # 計算績效指標
    annual_return = portfolio_returns.mean() * 252
    annual_volatility = portfolio_returns.std() * np.sqrt(252)
    sharpe_ratio = annual_return / annual_volatility
    sortino_ratio = portfolio_returns.mean() / portfolio_returns[portfolio_returns < 0].std() * np.sqrt(252)
    
    cumulative_returns = (1 + portfolio_returns).cumprod()
    max_drawdown = (cumulative_returns / cumulative_returns.cummax() - 1).min()
    calmar_ratio = annual_return / abs(max_drawdown)
    
    results = {
        'returns': portfolio_returns,
        'cumulative_returns': cumulative_returns,
        'annual_return': annual_return,
        'annual_volatility': annual_volatility,
        'sharpe_ratio': sharpe_ratio,
        'sortino_ratio': sortino_ratio,
        'max_drawdown': max_drawdown,
        'calmar_ratio': calmar_ratio
    }
    
    print(f"\n📊 {name} 回測結果：")
    print(f"   年化收益：{annual_return:.2%}")
    print(f"   年化波動：{annual_volatility:.2%}")
    print(f"   夏普比率：{sharpe_ratio:.2f}")
    print(f"   Sortino比率：{sortino_ratio:.2f}")
    print(f"   最大回撤：{max_drawdown:.2%}")
    print(f"   Calmar比率：{calmar_ratio:.2f}")
    
    return results

def compare_strategies(results_dict):
    """比較多個策略"""
    print(f"\n{'='*60}")
    print("第十四步：比較策略績效")
    print(f"{'='*60}")
    
    # 1. 構建績效對比表
    comparison_df = pd.DataFrame({
        strategy: {
            '年化收益': result['annual_return'],
            '年化波動': result['annual_volatility'],
            '夏普比率': result['sharpe_ratio'],
            'Sortino比率': result['sortino_ratio'],
            '最大回撤': result['max_drawdown'],
            'Calmar比率': result['calmar_ratio']
        }
        for strategy, result in results_dict.items()
    }).T
    
    print(f"\n📊 策略績效對比：")
    print(comparison_df.to_string())
    
    # 2. 繪製累積收益曲線
    fig, ax = plt.subplots(figsize=(16, 10))
    
    for strategy, result in results_dict.items():
        ax.plot(result['cumulative_returns'].index,
                result['cumulative_returns'].values,
                label=strategy, linewidth=2, alpha=0.8)
    
    ax.set_title('策略累積收益曲線對比（2020-2026）', fontsize=14, fontweight='bold')
    ax.set_xlabel('日期')
    ax.set_ylabel('累積收益')
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('strategy_comparison.png', dpi=300, bbox_inches='tight')
    print(f"\n✅ 策略對比圖已保存：strategy_comparison.png")
    plt.show()
    
    return comparison_df

# ============================================
# 主程序
# ============================================

def main():
    """主程序"""
    print("\n" + "="*60)
    print("美股前 30 股票相關性分析與組合優化")
    print("="*60)
    print(f"開始時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 獲取數據
    prices, volumes, returns = get_stock_data(
        tickers=DJIA_30,
        start_date='2020-01-01',
        end_date='2026-03-06'
    )
    
    # 2. 清理數據
    cleaned_returns, removed_tickers = clean_data(returns)
    
    # 3. 計算市場指數回報（等權重平均）
    market_returns = cleaned_returns.mean(axis=1)
    
    # 4. 相關性分析
    rolling_corr = calculate_rolling_correlation(cleaned_returns, window=252)
    analysis_results = analyze_average_correlation_trend(rolling_corr, market_returns)
    plot_correlation_trend(analysis_results)
    
    # 5. 網絡分析
    mst, corr_matrix = build_mst(cleaned_returns, window=252)
    network_metrics = calculate_network_metrics(mst)
    communities, community_dict = detect_communities(mst)
    plot_mst_network(mst, community_dict=community_dict)
    
    # 6. 投資組合構建
    mst_weights = mst_based_portfolio(mst, cleaned_returns, method='inverse_degree')
    eigen_weights, ensemble_weights = eigen_portfolios(cleaned_returns, n_components=5)
    equal_weights = equal_weight_portfolio(cleaned_returns)
    
    # 7. 回測
    mst_results = backtest_strategy(mst_weights, cleaned_returns, name="MST投資組合")
    ensemble_results = backtest_strategy(ensemble_weights, cleaned_returns, name="特徵組合")
    equal_results = backtest_strategy(equal_weights, cleaned_returns, name="等權重基準")
    
    # 8. 比較
    comparison_df = compare_strategies({
        '等權重基準': equal_results,
        'MST投資組合': mst_results,
        '特徵組合': ensemble_results
    })
    
    # 9. 保存結果
    print(f"\n{'='*60}")
    print("第十五步：保存結果")
    print(f"{'='*60}")
    
    # 保存權重
    mst_weights.to_csv('mst_weights.csv')
    ensemble_weights.to_csv('ensemble_weights.csv')
    equal_weights.to_csv('equal_weights.csv')
    
    # 保存績效對比
    comparison_df.to_csv('strategy_comparison.csv')
    
    # 保存網絡指標
    network_metrics.to_csv('network_metrics.csv')
    
    print("\n✅ 所有結果已保存：")
    print("   - mst_weights.csv")
    print("   - ensemble_weights.csv")
    print("   - equal_weights.csv")
    print("   - strategy_comparison.csv")
    print("   - network_metrics.csv")
    print("   - correlation_trend_analysis.png")
    print("   - mst_network.png")
    print("   - strategy_comparison.png")
    
    print(f"\n{'='*60}")
    print(f"分析完成！結束時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
