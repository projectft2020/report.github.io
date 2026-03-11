# 美股前 30 股票相關性分析與組合優化 - 深入研究實施計劃

**項目 ID:** 202602281936-phase2-001
**計劃日期:** 2026-03-06
**負責人:** Charlie

---

## 一、研究目標

### 核心目標

1. **驗證 Preis 等人的相關性破壞現象**：在 2020-2026 年期間的美股市場中，是否仍然存在「市場壓力時相關性增加」的現象？

2. **構建網絡分析系統**：實現 MST、社區檢測等網絡分析方法，識別美股前 30 股票的層級結構。

3. **開發組合優化策略**：基於網絡分析、特徵組合、動態相關性調整等方法，構建優於等權重的投資組合。

4. **回測驗證**：在 2020-2026 年期間回測驗證各種策略，量化其性能優勢。

---

## 二、數據獲取與處理

### 2.1 股票選擇

**美股前 30 股票（道瓊斯工業指數成分股）：**

```python
# 美股前 30 股票列表（2026 年 3 月）
DJIA_30 = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA',
    'NVDA', 'META', 'JPM', 'V', 'WMT',
    'HD', 'MA', 'BAC', 'UNH', 'PFE',
    'DIS', 'KO', 'CSCO', 'XOM', 'CVX',
    'MRK', 'ABBV', 'PEP', 'INTC', 'DHR',
    'CAT', 'NKE', 'MCD', 'IBM', 'GS'
]
```

### 2.2 數據獲取

**使用 yfinance 獲取歷史數據：**

```python
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_stock_data(tickers, start_date, end_date):
    """
    獲取股票歷史數據
    
    參數：
    - tickers: 股票代碼列表
    - start_date: 開始日期（'YYYY-MM-DD'）
    - end_date: 結束日期（'YYYY-MM-DD'）
    
    返回：
    - prices: 調整後收盤價 DataFrame
    - volumes: 成交量 DataFrame
    - returns: 日收益率 DataFrame
    """
    print(f"正在獲取 {len(tickers)} 隻股票的數據...")
    
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
    
    print(f"✅ 數據獲取完成：{prices.shape[0]} 個交易日")
    print(f"   時間範圍：{prices.index[0]} 至 {prices.index[-1]}")
    print(f"   數據質量：{prices.isna().sum().sum()} 個缺失值")
    
    return prices, volumes, returns

# 執行
prices, volumes, returns = get_stock_data(
    tickers=DJIA_30,
    start_date='2020-01-01',
    end_date='2026-03-06'
)
```

### 2.3 數據清理

**處理缺失值、異常值：**

```python
def clean_data(returns, max_missing_pct=0.05):
    """
    清理數據
    
    參數：
    - returns: 收益率 DataFrame
    - max_missing_pct: 最大允許缺失百分比
    
    返回：
    - cleaned_returns: 清理後的收益率 DataFrame
    - removed_tickers: 被移除的股票列表
    """
    print("正在清理數據...")
    
    # 1. 移除缺失值過多的股票
    missing_pct = returns.isna().sum() / len(returns)
    removed_tickers = missing_pct[missing_pct > max_missing_pct].index.tolist()
    
    if removed_tickers:
        print(f"⚠️  移除缺失值過多的股票：{removed_tickers}")
        cleaned_returns = returns.drop(columns=removed_tickers)
    else:
        cleaned_returns = returns.copy()
        print("✅ 沒有缺失值過多的股票")
    
    # 2. 前向填充 + 後向填充（處理少量缺失值）
    cleaned_returns = cleaned_returns.fillna(method='ffill').fillna(method='bfill')
    
    # 3. 移除殘留缺失值
    cleaned_returns = cleaned_returns.dropna()
    
    # 4. 檢測異常值（> 10 個標準差）
    for ticker in cleaned_returns.columns:
        mean = cleaned_returns[ticker].mean()
        std = cleaned_returns[ticker].std()
        outliers = np.abs(cleaned_returns[ticker] - mean) > 10 * std
        
        if outliers.sum() > 0:
            print(f"⚠️  {ticker} 發現 {outliers.sum()} 個異常值")
            # 用平均值替換異常值
            cleaned_returns.loc[outliers, ticker] = mean
    
    print(f"✅ 數據清理完成：{cleaned_returns.shape[1]} 隻股票，{cleaned_returns.shape[0]} 個交易日")
    
    return cleaned_returns, removed_tickers

# 執行
cleaned_returns, removed_tickers = clean_data(returns)
```

---

## 三、相關性分析實施

### 3.1 滾動相關性計算

```python
def calculate_rolling_correlation(returns, window=252):
    """
    計算滾動相關性矩陣
    
    參數：
    - returns: 收益率 DataFrame
    - window: 滾動窗口（默認 252 個交易日 = 1 年）
    
    返回：
    - rolling_corr: 三維數組 [日期, 資產1, 資產2]
    """
    print(f"正在計算滾動相關性（窗口 = {window} 天）...")
    
    # 計算滾動相關性
    rolling_corr = returns.rolling(window=window).corr()
    
    # 移除前 window-1 行（不足 window 的數據）
    rolling_corr = rolling_corr.dropna(how='all')
    
    print(f"✅ 滾動相關性計算完成：{rolling_corr.shape[0]} 個時間點")
    
    return rolling_corr

# 執行
rolling_corr = calculate_rolling_correlation(cleaned_returns, window=252)
```

### 3.2 平均相關性趨勢分析

```python
def analyze_average_correlation_trend(rolling_corr, market_returns):
    """
    分析平均相關性趨勢
    
    參數：
    - rolling_corr: 滾動相關性矩陣
    - market_returns: 市場指數收益率（如 DJIA）
    
    返回：
    - analysis_results: 分析結果字典
    """
    print("正在分析平均相關性趨勢...")
    
    # 1. 計算平均相關性（排除對角線）
    n_assets = rolling_corr.shape[1]
    avg_correlation = []
    
    for date in rolling_corr.index.levels[0]:
        corr_matrix = rolling_corr.loc[date]
        
        # 計算上三角矩陣的平均值（排除對角線）
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
    
    # 5. 線性回歸（Preis 方法）
    from scipy import stats
    
    # 正回報
    slope_pos, intercept_pos, r_value_pos, p_value_pos, std_err_pos = stats.linregress(
        pos_returns, pos_corr
    )
    
    # 負回報
    slope_neg, intercept_neg, r_value_neg, p_value_neg, std_err_neg = stats.linregress(
        neg_returns, neg_corr
    )
    
    # 6. 結果
    analysis_results = {
        'average_correlation': avg_correlation,
        'market_returns': market_returns,
        'positive_returns': {
            'slope': slope_pos,
            'intercept': intercept_pos,
            'r_squared': r_value_pos**2,
            'p_value': p_value_pos,
            'data': pd.DataFrame({'R': pos_returns, 'C': pos_corr})
        },
        'negative_returns': {
            'slope': slope_neg,
            'intercept': intercept_neg,
            'r_squared': r_value_neg**2,
            'p_value': p_value_neg,
            'data': pd.DataFrame({'R': neg_returns, 'C': neg_corr})
        }
    }
    
    print("✅ 平均相關性趨勢分析完成")
    print(f"   正回報：C = {slope_pos:.3f}R + {intercept_pos:.3f} (R² = {r_value_pos**2:.3f})")
    print(f"   負回報：C = {slope_neg:.3f}R + {intercept_neg:.3f} (R² = {r_value_neg**2:.3f})")
    
    # 7. 驗證 Preis 的發現
    print("\n🔍 驗證 Preis 等人的發現：")
    print(f"   |slope_neg| > slope_pos: {abs(slope_neg) > slope_pos} (Preis: |a-| > a+)")
    print(f"   相關性破壞現象: {'✅ 確認' if abs(slope_neg) > slope_pos else '❌ 未確認'}")
    
    return analysis_results

# 執行
# 首先計算市場指數回報（簡化：使用等權重平均）
market_returns = cleaned_returns.mean(axis=1)
analysis_results = analyze_average_correlation_trend(rolling_corr, market_returns)
```

### 3.3 可視化相關性趨勢

```python
import matplotlib.pyplot as plt
import seaborn as sns

def plot_correlation_trend(analysis_results, figsize=(15, 10)):
    """
    繪製相關性趨勢圖
    
    參數：
    - analysis_results: 分析結果
    - figsize: 圖形大小
    """
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    
    # 1. 平均相關性時間序列
    ax1 = axes[0, 0]
    ax1.plot(analysis_results['average_correlation'].index, 
             analysis_results['average_correlation'].values, 
             label='平均相關性', color='blue')
    ax1.axhline(y=analysis_results['average_correlation'].mean(), 
                color='red', linestyle='--', label='平均值')
    ax1.set_title('平均相關性時間序列（2020-2026）', fontsize=12, fontweight='bold')
    ax1.set_ylabel('相關係數')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. 正回報：相關性 vs 市場回報
    ax2 = axes[0, 1]
    pos_data = analysis_results['positive_returns']['data']
    ax2.scatter(pos_data['R'], pos_data['C'], alpha=0.3, s=10, color='green')
    
    # 回歸線
    x_pos = np.linspace(pos_data['R'].min(), pos_data['R'].max(), 100)
    y_pos = (analysis_results['positive_returns']['slope'] * x_pos + 
             analysis_results['positive_returns']['intercept'])
    ax2.plot(x_pos, y_pos, color='red', linewidth=2, 
             label=f'C = {analysis_results["positive_returns"]["slope"]:.3f}R + {analysis_results["positive_returns"]["intercept"]:.3f}')
    
    ax2.set_title('正回報：相關性 vs 市場回報', fontsize=12, fontweight='bold')
    ax2.set_xlabel('標準化市場回報 (R)')
    ax2.set_ylabel('平均相關性 (C+)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. 負回報：相關性 vs 市場回報
    ax3 = axes[1, 0]
    neg_data = analysis_results['negative_returns']['data']
    ax3.scatter(neg_data['R'], neg_data['C'], alpha=0.3, s=10, color='red')
    
    # 回歸線
    x_neg = np.linspace(neg_data['R'].min(), neg_data['R'].max(), 100)
    y_neg = (analysis_results['negative_returns']['slope'] * x_neg + 
             analysis_results['negative_returns']['intercept'])
    ax3.plot(x_neg, y_neg, color='blue', linewidth=2,
             label=f'C = {analysis_results["negative_returns"]["slope"]:.3f}R + {analysis_results["negative_returns"]["intercept"]:.3f}')
    
    ax3.set_title('負回報：相關性 vs 市場回報', fontsize=12, fontweight='bold')
    ax3.set_xlabel('標準化市場回報 (R)')
    ax3.set_ylabel('平均相關性 (C-)')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. 對比正負回報
    ax4 = axes[1, 1]
    
    # 正回報
    ax4.scatter(pos_data['R'], pos_data['C'], alpha=0.3, s=10, 
               color='green', label='正回報')
    ax4.plot(x_pos, y_pos, color='green', linewidth=2,
             label=f'C+ (R² = {analysis_results["positive_returns"]["r_squared"]:.3f})')
    
    # 負回報
    ax4.scatter(neg_data['R'], neg_data['C'], alpha=0.3, s=10, 
               color='red', label='負回報')
    ax4.plot(x_neg, y_neg, color='red', linewidth=2,
             label=f'C- (R² = {analysis_results["negative_returns"]["r_squared"]:.3f})')
    
    ax4.set_title('正負回報對比', fontsize=12, fontweight='bold')
    ax4.set_xlabel('標準化市場回報 (R)')
    ax4.set_ylabel('平均相關性 (C)')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('correlation_trend_analysis.png', dpi=300, bbox_inches='tight')
    print("✅ 相關性趨勢圖已保存：correlation_trend_analysis.png")
    plt.show()

# 執行
plot_correlation_trend(analysis_results)
```

---

## 四、網絡分析實施

### 4.1 相關性矩陣轉距離矩陣

```python
def correlation_to_distance(corr_matrix):
    """
    將相關性矩陣轉為距離矩陣（Mantegna 方法）
    
    公式：d_ij = √[2(1 - ρ_ij)]
    
    參數：
    - corr_matrix: 相關性矩陣
    
    返回：
    - distance_matrix: 距離矩陣
    """
    # 處理數值穩定性（避免 sqrt 負數）
    corr_matrix_clipped = np.clip(corr_matrix, -1, 1)
    
    # 計算距離
    distance_matrix = np.sqrt(2 * (1 - corr_matrix_clipped))
    
    # 確保對角線為 0
    np.fill_diagonal(distance_matrix, 0)
    
    return distance_matrix
```

### 4.2 構建最小生成樹（MST）

```python
import networkx as nx
from scipy.spatial.distance import squareform

def build_mst(returns, window=252, date=None):
    """
    構建最小生成樹
    
    參數：
    - returns: 收益率 DataFrame
    - window: 滾動窗口
    - date: 特定日期（默認使用最新）
    
    返回：
    - mst: NetworkX Graph 對象
    - distance_matrix: 距離矩陣
    - corr_matrix: 相關性矩陣
    """
    print(f"正在構建最小生成樹...")
    
    # 1. 計算相關性矩陣
    if date is None:
        # 使用最新的完整窗口
        corr_matrix = returns.iloc[-window:].corr()
    else:
        # 使用特定日期的滾動相關性
        corr_matrix = returns.loc[:date].iloc[-window:].corr()
    
    # 2. 轉為距離矩陣
    distance_matrix = correlation_to_distance(corr_matrix.values)
    
    # 3. 構建完全圖
    G = nx.from_numpy_array(distance_matrix)
    
    # 4. 計算最小生成樹
    mst = nx.minimum_spanning_tree(G)
    
    # 5. 添加節點標籤（股票代碼）
    node_labels = {i: ticker for i, ticker in enumerate(returns.columns)}
    mst = nx.relabel_nodes(mst, node_labels)
    
    print(f"✅ 最小生成樹構建完成：{mst.number_of_nodes()} 個節點，{mst.number_of_edges()} 條邊")
    
    return mst, distance_matrix, corr_matrix

# 執行
mst, distance_matrix, corr_matrix = build_mst(cleaned_returns, window=252)
```

### 4.3 計算網絡指標

```python
def calculate_network_metrics(mst):
    """
    計算網絡指標
    
    參數：
    - mst: NetworkX Graph 對象
    
    返回：
    - metrics: 網絡指標字典
    """
    print("正在計算網絡指標...")
    
    # 1. 度中心性
    degree_centrality = nx.degree_centrality(mst)
    
    # 2. 介數中心性
    betweenness_centrality = nx.betweenness_centrality(mst)
    
    # 3. 特徵向量中心性
    eigenvector_centrality = nx.eigenvector_centrality(mst, max_iter=1000)
    
    # 4. 接近中心性（Closeness）
    closeness_centrality = nx.closeness_centrality(mst)
    
    # 5. 聚集係數
    clustering_coefficient = nx.clustering(mst)
    
    # 6. 網絡直徑
    diameter = nx.diameter(mst)
    
    # 7. 平均路徑長度
    avg_path_length = nx.average_shortest_path_length(mst)
    
    # 8. 密度
    density = nx.density(mst)
    
    # 9. 組織成 DataFrame
    metrics_df = pd.DataFrame({
        'Degree Centrality': degree_centrality,
        'Betweenness Centrality': betweenness_centrality,
        'Eigenvector Centrality': eigenvector_centrality,
        'Closeness Centrality': closeness_centrality,
        'Clustering Coefficient': clustering_coefficient
    })
    
    # 按度中心性排序
    metrics_df = metrics_df.sort_values('Degree Centrality', ascending=False)
    
    # 統計信息
    metrics = {
        'metrics_df': metrics_df,
        'diameter': diameter,
        'avg_path_length': avg_path_length,
        'density': density,
        'top_5_degree': metrics_df.head(5)
    }
    
    print("✅ 網絡指標計算完成")
    print(f"   網絡直徑：{diameter}")
    print(f"   平均路徑長度：{avg_path_length:.2f}")
    print(f"   網絡密度：{density:.3f}")
    print(f"\n   度中心性前 5 名：")
    print(metrics['top_5_degree'].to_string())
    
    return metrics

# 執行
network_metrics = calculate_network_metrics(mst)
```

### 4.4 社群檢測（社區發現）

```python
def detect_communities(mst, method='louvain'):
    """
    社群檢測
    
    參數：
    - mst: NetworkX Graph 對象
    - method: 檢測方法 ('louvain', 'label_propagation', 'girvan_newman')
    
    返回：
    - communities: 社群列表
    - community_dict: {股票: 社群ID} 字典
    """
    print(f"正在進行社群檢測（方法：{method}）...")
    
    if method == 'louvain':
        # Louvain 算法（需要 python-louvain 套件）
        try:
            import community as community_louvain
            partition = community_louvain.best_partition(mst)
            communities = {}
            for node, comm_id in partition.items():
                if comm_id not in communities:
                    communities[comm_id] = []
                communities[comm_id].append(node)
            communities = list(communities.values())
        except ImportError:
            print("⚠️  python-louvain 未安裝，使用標籤傳播算法")
            communities = list(nx.community.label_propagation_communities(mst))
    
    elif method == 'label_propagation':
        # 標籤傳播算法
        communities = list(nx.community.label_propagation_communities(mst))
    
    elif method == 'girvan_newman':
        # Girvan-Newman 算法（較慢）
        comp = nx.community.girvan_newman(mst)
        # 取第一層
        communities = list(comp)[0]
    
    # 創建 {股票: 社群ID} 字典
    community_dict = {}
    for i, community in enumerate(communities):
        for stock in community:
            community_dict[stock] = i
    
    print(f"✅ 社群檢測完成：發現 {len(communities)} 個社群")
    
    for i, community in enumerate(communities):
        print(f"   社群 {i}: {', '.join(community)}")
    
    return communities, community_dict

# 執行
communities, community_dict = detect_communities(mst, method='louvain')
```

### 4.5 可視化 MST 網絡

```python
def plot_mst_network(mst, community_dict=None, figsize=(20, 16)):
    """
    繪製 MST 網絡
    
    參數：
    - mst: NetworkX Graph 對象
    - community_dict: 社群字典 {股票: 社群ID}
    - figsize: 圖形大小
    """
    print("正在繪製 MST 網絡...")
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # 計算佈局（使用 spring 佈局）
    pos = nx.spring_layout(mst, k=3, iterations=50, seed=42)
    
    # 1. 如果有社群檢測結果，按社群著色
    if community_dict is not None:
        # 社群顏色
        colors = plt.cm.Set3(range(len(set(community_dict.values()))))
        node_colors = [colors[community_dict[node]] for node in mst.nodes()]
    else:
        node_colors = 'lightblue'
    
    # 2. 繪製節點（大小根據度中心性）
    degree_centrality = nx.degree_centrality(mst)
    node_sizes = [degree_centrality[node] * 3000 for node in mst.nodes()]
    
    nx.draw_networkx_nodes(
        mst, 
        pos, 
        node_color=node_colors,
        node_size=node_sizes,
        alpha=0.7,
        ax=ax
    )
    
    # 3. 繪製邊
    nx.draw_networkx_edges(
        mst, 
        pos, 
        width=2,
        alpha=0.5,
        edge_color='gray',
        ax=ax
    )
    
    # 4. 繪製標籤
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
    
    # 5. 添加圖例（如果使用社群著色）
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
    print("✅ MST 網絡圖已保存：mst_network.png")
    plt.show()

# 執行
plot_mst_network(mst, community_dict=community_dict)
```

---

## 五、投資組合優化策略

### 5.1 基於 MST 的投資組合

```python
def mst_based_portfolio(mst, returns, method='inverse_degree', leverage=1.0):
    """
    基於 MST 的投資組合
    
    參數：
    - mst: NetworkX Graph 對象
    - returns: 收益率 DataFrame
    - method: 權重方法 ('inverse_degree', 'equal', 'random')
    - leverage: 槓桿倍數
    
    返回：
    - weights: 權重 Series {股票: 權重}
    """
    print(f"正在構建基於 MST 的投資組合（方法：{method}）...")
    
    # 1. 計算度中心性
    degree_centrality = nx.degree_centrality(mst)
    
    # 2. 計算權重
    if method == 'inverse_degree':
        # 反度權重（懲罰中心性高的節點）
        weights = pd.Series({node: 1.0 / (dc + 0.01) 
                            for node, dc in degree_centrality.items()})
    
    elif method == 'equal':
        # 等權重
        weights = pd.Series({node: 1.0 / len(mst.nodes()) 
                            for node in mst.nodes()})
    
    elif method == 'random':
        # 隨機權重
        weights = pd.Series({node: np.random.rand() 
                            for node in mst.nodes()})
    
    # 3. 歸一化
    weights = weights / weights.sum()
    
    # 4. 應用槓桿
    weights = weights * leverage
    
    # 5. 只包含有數據的股票
    valid_stocks = list(set(weights.index) & set(returns.columns))
    weights = weights[valid_stocks]
    weights = weights / weights.sum() * leverage  # 重新歸一化
    
    print(f"✅ MST 投資組合構建完成：{len(weights)} 隻股票")
    print(f"   權重前 5 名：")
    print(weights.head().to_string())
    
    return weights

# 執行
mst_weights = mst_based_portfolio(mst, cleaned_returns, method='inverse_degree')
```

### 5.2 特徵組合（Eigen Portfolios）

```python
def eigen_portfolios(returns, n_components=5):
    """
    構建特徵組合（Eigen Portfolios）
    
    參數：
    - returns: 收益率 DataFrame
    - n_components: 選擇的特徵向量數量
    
    返回：
    - eigen_weights: 特徵組合權重 DataFrame
    - explained_variance: 解釋方差比率
    """
    print(f"正在構建特徵組合（n_components = {n_components}）...")
    
    # 1. 標準化收益率
    returns_standardized = (returns - returns.mean()) / returns.std()
    
    # 2. 計算相關性矩陣
    corr_matrix = returns_standardized.corr()
    
    # 3. PCA 分解
    from sklearn.decomposition import PCA
    
    pca = PCA(n_components=n_components)
    pca.fit(corr_matrix)
    
    # 4. 獲取特徵向量
    eigenvectors = pca.components_.T  # [資產, 特徵向量]
    
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
    
    print(f"✅ 特徵組合構建完成")
    print(f"   解釋方差：{explained_variance}")
    print(f"   樣本內夏普比率：{eigen_sharpe}")
    
    # 8. 組合策略（等權重組合）
    ensemble_weight = 1.0 / n_components
    ensemble_weights = eigen_weights * ensemble_weight
    
    # 計算組合回報
    ensemble_returns = (returns_standardized * ensemble_weights).sum(axis=1)
    ensemble_sharpe = ensemble_returns.mean() / ensemble_returns.std() * np.sqrt(252)
    
    print(f"   組合策略夏普比率：{ensemble_sharpe:.3f}")
    
    return eigen_weights, explained_variance, ensemble_weights

# 執行
eigen_weights, explained_variance, ensemble_weights = eigen_portfolios(cleaned_returns, n_components=5)
```

### 5.3 動態相關性調整策略

```python
def dynamic_correlation_adjustment(returns, window=252, target_volatility=0.10):
    """
    動態相關性調整策略
    
    參數：
    - returns: 收益率 DataFrame
    - window: 滾動窗口
    - target_volatility: 目標波動率
    
    返回：
    - weights_history: 權重歷史 DataFrame
    - portfolio_returns: 組合回報 Series
    """
    print(f"正在執行動態相關性調整策略...")
    
    # 初始化
    weights_history = []
    portfolio_returns = []
    
    # 滾動窗口
    for i in range(window, len(returns)):
        # 1. 訓練數據
        train_returns = returns.iloc[i-window:i]
        
        # 2. 計算相關性矩陣
        corr_matrix = train_returns.corr()
        
        # 3. 計算波動率
        volatilities = train_returns.std() * np.sqrt(252)
        
        # 4. 構建 MST
        distance_matrix = correlation_to_distance(corr_matrix.values)
        G = nx.from_numpy_array(distance_matrix)
        mst = nx.minimum_spanning_tree(G)
        
        # 5. 計算 MST 基礎權重（反度）
        degree_centrality = nx.degree_centrality(mst)
        base_weights = pd.Series({node: 1.0 / (dc + 0.01) 
                                 for node, dc in degree_centrality.items()})
        base_weights = base_weights / base_weights.sum()
        
        # 6. 根據波動率調整
        adjusted_weights = base_weights.copy()
        for stock in base_weights.index:
            if stock in volatilities.index:
                # 目標權重 = 基礎權重 × (目標波動率 / 資產波動率)
                adjusted_weights[stock] = (base_weights[stock] * 
                                         target_volatility / volatilities[stock])
        
        # 7. 歸一化
        adjusted_weights = adjusted_weights / adjusted_weights.sum()
        
        # 8. 保存權重
        weights_history.append(adjusted_weights)
        
        # 9. 計算當期回報
        current_returns = returns.iloc[i]
        portfolio_return = (adjusted_weights * current_returns).sum()
        portfolio_returns.append(portfolio_return)
    
    # 轉為 DataFrame/Series
    weights_history = pd.DataFrame(weights_history, index=returns.index[window:])
    portfolio_returns = pd.Series(portfolio_returns, index=returns.index[window:])
    
    print(f"✅ 動態相關性調整策略執行完成")
    print(f"   期間：{portfolio_returns.index[0]} 至 {portfolio_returns.index[-1]}")
    print(f"   年化收益：{portfolio_returns.mean() * 252:.2%}")
    print(f"   年化波動：{portfolio_returns.std() * np.sqrt(252):.2%}")
    print(f"   夏普比率：{portfolio_returns.mean() / portfolio_returns.std() * np.sqrt(252):.2f}")
    
    return weights_history, portfolio_returns

# 執行
dyn_weights, dyn_returns = dynamic_correlation_adjustment(cleaned_returns)
```

---

## 六、回測驗證

### 6.1 回測框架

```python
def backtest_strategy(weights_strategy, returns, transaction_cost=0.001):
    """
    回測框架
    
    參數：
    - weights_strategy: 策略權重（可以是靜態或動態）
    - returns: 收益率 DataFrame
    - transaction_cost: 交易成本（單向）
    
    返回：
    - results: 回測結果字典
    """
    print("正在進行回測...")
    
    # 1. 計算組合回報
    if isinstance(weights_strategy, pd.DataFrame):
        # 動態權重
        portfolio_returns = []
        turnover = []
        
        for i in range(1, len(weights_strategy)):
            # 當前權重
            current_weights = weights_strategy.iloc[i-1]
            prev_weights = weights_strategy.iloc[i-2] if i > 1 else current_weights
            
            # 組合回報
            current_returns = returns.iloc[i-1]
            portfolio_return = (current_weights * current_returns).sum()
            portfolio_returns.append(portfolio_return)
            
            # 換手率
            turnover_change = (current_weights - prev_weights).abs().sum() / 2
            turnover.append(turnover_change)
        
        portfolio_returns = pd.Series(portfolio_returns, index=returns.index[1:len(weights_strategy)])
        turnover = pd.Series(turnover, index=returns.index[1:len(weights_strategy)])
        
    elif isinstance(weights_strategy, pd.Series):
        # 靜態權重
        portfolio_returns = (returns * weights_strategy).sum(axis=1)
        turnover = pd.Series(0, index=returns.index)
    
    # 2. 扣除交易成本
    portfolio_returns_net = portfolio_returns - turnover * transaction_cost
    
    # 3. 計算績效指標
    results = {
        'returns': portfolio_returns,
        'returns_net': portfolio_returns_net,
        'turnover': turnover,
        'cumulative_returns': (1 + portfolio_returns_net).cumprod(),
        
        # 績效指標
        'annual_return': portfolio_returns_net.mean() * 252,
        'annual_volatility': portfolio_returns_net.std() * np.sqrt(252),
        'sharpe_ratio': portfolio_returns_net.mean() / portfolio_returns_net.std() * np.sqrt(252),
        'sortino_ratio': portfolio_returns_net.mean() / portfolio_returns_net[portfolio_returns_net < 0].std() * np.sqrt(252),
        'max_drawdown': (1 + portfolio_returns_net).cumprod().div((1 + portfolio_returns_net).cumprod().cummax()).sub(1).min(),
        'calmar_ratio': portfolio_returns_net.mean() * 252 / abs((1 + portfolio_returns_net).cumprod().div((1 + portfolio_returns_net).cumprod().cummax()).sub(1).min()),
        
        # 交易成本
        'total_turnover': turnover.sum(),
        'total_transaction_cost': (turnover * transaction_cost).sum()
    }
    
    print("✅ 回測完成")
    print(f"   年化收益：{results['annual_return']:.2%}")
    print(f"   年化波動：{results['annual_volatility']:.2%}")
    print(f"   夏普比率：{results['sharpe_ratio']:.2f}")
    print(f"   最大回撤：{results['max_drawdown']:.2%}")
    print(f"   Calmar 比率：{results['calmar_ratio']:.2f}")
    print(f"   總換手率：{results['total_turnover']:.2%}")
    print(f"   總交易成本：{results['total_transaction_cost']:.2%}")
    
    return results

# 執行回測
# 1. MST 投資組合
mst_results = backtest_strategy(mst_weights, cleaned_returns)

# 2. 特徵組合（組合策略）
ensemble_results = backtest_strategy(ensemble_weights, cleaned_returns)

# 3. 動態相關性調整策略
dyn_results = backtest_strategy(dyn_weights, cleaned_returns)

# 4. 等權重基準
equal_weights = pd.Series(1.0 / len(cleaned_returns.columns), index=cleaned_returns.columns)
equal_results = backtest_strategy(equal_weights, cleaned_returns)
```

### 6.2 績效對比

```python
def compare_strategies(results_dict, figsize=(15, 10)):
    """
    比較多個策略的績效
    
    參數：
    - results_dict: {策略名: 回測結果}
    - figsize: 圖形大小
    """
    print("正在比較策略績效...")
    
    # 1. 構建績效對比表
    comparison_df = pd.DataFrame({
        strategy: {
            '年化收益': result['annual_return'],
            '年化波動': result['annual_volatility'],
            '夏普比率': result['sharpe_ratio'],
            'Sortino比率': result['sortino_ratio'],
            '最大回撤': result['max_drawdown'],
            'Calmar比率': result['calmar_ratio'],
            '總換手率': result['total_turnover']
        }
        for strategy, result in results_dict.items()
    }).T
    
    print("\n策略績效對比：")
    print(comparison_df.to_string())
    
    # 2. 繪製累積收益曲線
    fig, ax = plt.subplots(figsize=figsize)
    
    for strategy, result in results_dict.items():
        ax.plot(result['cumulative_returns'].index, 
                result['cumulative_returns'].values, 
                label=strategy, linewidth=2)
    
    ax.set_title('策略累積收益曲線對比（2020-2026）', fontsize=14, fontweight='bold')
    ax.set_xlabel('日期')
    ax.set_ylabel('累積收益')
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('strategy_comparison.png', dpi=300, bbox_inches='tight')
    print("\n✅ 策略對比圖已保存：strategy_comparison.png")
    plt.show()
    
    return comparison_df

# 執行
comparison_df = compare_strategies({
    '等權重基準': equal_results,
    'MST投資組合': mst_results,
    '特徵組合': ensemble_results,
    '動態相關性調整': dyn_results
})
```

---

## 七、下一步行動

### 短期（本週）

1. ✅ **完成數據獲取與清理**：獲取美股前 30 股票 2020-2026 年數據
2. ✅ **驗證 Preis 現象**：驗證「市場壓力時相關性增加」是否仍然存在
3. ✅ **構建 MST 網絡**：分析股票間的層級結構

### 中期（本月）

1. ✅ **實施網絡分析**：社群檢測、中心性分析
2. ✅ **開發投資組合策略**：MST 基礎、特徵組合、動態調整
3. ✅ **回測驗證**：在 2020-2026 年期間回測各種策略

### 長期（下月）

1. ✅ **機器學習擴展**：使用 LSTM/Transformer 預測相關性變化
2. ✅ **強化學習應用**：使用 RL 動態調整倉位
3. ✅ **跨資產擴展**：整合債券、大宗商品、外匯

---

## 八、預期成果

### 研究報告

- **完整的研究報告**（約 30,000 字）
- **可重現的代碼**（Python Jupyter Notebook）
- **可視化圖表**（相關性趨勢、網絡結構、績效對比）

### 實際應用

- **投資組合優化工具**：可實際運行的 Python 套件
- **風險管理系統**：相關性風險監控和預警
- **交易信號系統**：基於相關性變化的交易信號

---

**計劃完成日期：** 2026-03-15
**負責人：** Charlie
**狀態：** 進行中 🚀
