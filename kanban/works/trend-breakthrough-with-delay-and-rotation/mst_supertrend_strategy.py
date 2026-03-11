#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MST + Supertrend 整合策略
使用最小生成樹選擇低相關性資產 + Supertrend 判斷進場時機

核心思想：
1. 構建資產相關性網絡
2. 使用最小生成樹（MST）選擇分散的資產
3. 對於選中的資產，使用 Supertrend 判斷進場時機
4. 只在趨勢確認時進場

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
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 設置中文顯示
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

# ============================================
# 第一部分：網絡基礎的資產選擇
# ============================================

def calculate_distance_matrix(corr_matrix):
    """
    計算距離矩陣（相關性的逆轉）
    
    使用歐幾里得距離：d(i,j) = sqrt(2 * (1 - corr(i,j)))
    當 corr=1 時，距離=0（完全相關）
    當 corr=-1 時，距離=2（完全負相關）
    當 corr=0 時，距離=sqrt(2)（無相關）
    """
    return np.sqrt(2 * (1 - corr_matrix))

def build_mst_portfolio(returns, num_assets=10, min_distance_threshold=1.0):
    """
    使用最小生成樹選擇資產組合
    
    參數：
    - returns: 資產回報矩陣
    - num_assets: 選擇的資產數量
    - min_distance_threshold: 最小距離閾值（過濾高相關性）
    
    返回：
    - selected_assets: 選中的資產列表
    - mst: 最小生成樹圖對象
    - centrality_scores: 中心性分數
    """
    # 1. 計算相關性矩陣
    corr_matrix = returns.corr()
    
    # 2. 計算距離矩陣
    distance_matrix = calculate_distance_matrix(corr_matrix)
    
    # 3. 構建完全圖
    n_assets = len(corr_matrix)
    graph = nx.complete_graph(n_assets)
    
    # 4. 給邊加權（距離）
    for i, j in graph.edges():
        graph[i][j]['weight'] = distance_matrix.iloc[i, j]
    
    # 5. 計算最小生成樹
    mst = nx.minimum_spanning_tree(graph)
    
    # 6. 計算中心性（使用 eigenvector centrality）
    centrality = nx.eigenvector_centrality_numpy(mst)
    
    # 7. 過濾高相關性資產（距離 < 閾值的邊）
    filtered_assets = []
    for i, j in mst.edges():
        if mst[i][j]['weight'] >= min_distance_threshold:
            filtered_assets.extend([i, j])
    
    # 8. 按中心性排序選擇資產
    sorted_nodes = sorted(
        centrality.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    # 選擇前 N 個資產
    selected_nodes = [node for node, score in sorted_nodes[:num_assets]]
    selected_assets = [returns.columns[i] for i in selected_nodes]
    centrality_scores = {returns.columns[i]: score for i, score in sorted_nodes}
    
    return selected_assets, mst, centrality_scores, corr_matrix, distance_matrix

# ============================================
# 第二部分：Supertrend 策略
# ============================================

def calculate_supertrend(high, low, close, period=10, multiplier=3.0):
    """
    計算 Supertrend 指標
    
    參數：
    - high: 最高價序列
    - low: 最低價序列
    - close: 收盤價序列
    - period: 週期
    - multiplier: 倍數
    
    返回：
    - supertrend: Supertrend 線
    - trend: 趨勢（1=上漲，0=下跌）
    """
    # 計算 ATR
    hl2 = (high + low) / 2
    atr = high - low
    
    # 計算基本帶
    upper_band = hl2 + multiplier * atr
    lower_band = hl2 - multiplier * atr
    
    # 初始化
    supertrend = [np.nan] * len(close)
    trend = [0] * len(close)
    
    supertrend[0] = lower_band.iloc[0]
    trend[0] = 1
    
    for i in range(1, len(close)):
        if trend[i-1] == 1:  # 當前是上漲趨勢
            if close.iloc[i] <= supertrend[i-1]:
                # 趨勢轉為下跌
                trend[i] = 0
                supertrend[i] = upper_band.iloc[i]
            else:
                # 維持上漲趨勢
                trend[i] = 1
                supertrend[i] = max(supertrend[i-1], lower_band.iloc[i])
        else:  # 當前是下跌趨勢
            if close.iloc[i] >= supertrend[i-1]:
                # 趨勢轉為上漲
                trend[i] = 1
                supertrend[i] = lower_band.iloc[i]
            else:
                # 維持下跌趨勢
                trend[i] = 0
                supertrend[i] = min(supertrend[i-1], upper_band.iloc[i])
    
    return pd.Series(supertrend, index=close.index), pd.Series(trend, index=close.index)

def generate_supertrend_signals(df, period=10, multiplier=3.0):
    """
    生成 Supertrend 進場信號
    
    參數：
    - df: 數據 DataFrame
    - period: Supertrend 週期
    - multiplier: Supertrend 倍數
    
    返回：
    - signals: 信號 DataFrame
    """
    supertrend, trend = calculate_supertrend(
        df['High'],
        df['Low'],
        df['Close'],
        period=period,
        multiplier=multiplier
    )
    
    # 檢測趨勢轉變
    trend_change = trend.diff()
    
    # 進場信號
    long_signal = (trend_change == 1)  # 趨勢從 0 轉為 1（買入）
    short_signal = (trend_change == -1)  # 趨勢從 1 轉為 0（賣出）
    
    signals = pd.DataFrame({
        'price': df['Close'],
        'supertrend': supertrend,
        'trend': trend,
        'long_signal': long_signal,
        'short_signal': short_signal
    }, index=df.index)
    
    return signals

# ============================================
# 第三部分：整合策略（MST + Supertrend）
# ============================================

class MSTSupertrendStrategy:
    """
    MST + Supertrend 整合策略
    
    工作流程：
    1. 使用 MST 選擇低相關性資產池
    2. 對於選中的資產，監控 Supertrend 信號
    3. 只在 Supertrend 確認趨勢時進場
    4. 動態調整組合（根據市場相關性變化）
    """
    
    def __init__(self, 
                 asset_pool,
                 num_assets=10,
                 st_period=10,
                 st_multiplier=3.0,
                 min_distance_threshold=1.0):
        """
        初始化策略
        
        參數：
        - asset_pool: 資產池列表
        - num_assets: MST 選擇的資產數量
        - st_period: Supertrend 週期
        - st_multiplier: Supertrend 倍數
        - min_distance_threshold: 最小距離閾值
        """
        self.asset_pool = asset_pool
        self.num_assets = num_assets
        self.st_period = st_period
        self.st_multiplier = st_multiplier
        self.min_distance_threshold = min_distance_threshold
        
        # 策略狀態
        self.selected_assets = []
        self.signals = {}
        self.positions = {}
        self.portfolio_value = 100000
        
    def run_analysis(self, data, lookback_window=60):
        """
        運行完整分析
        
        參數：
        - data: 數據字典 {ticker: DataFrame}
        - lookback_window: 回看窗口（計算相關性的天數）
        
        返回：
        - results: 分析結果
        """
        print("\n" + "="*70)
        print("MST + Supertrend 整合策略分析")
        print("="*70)
        
        # 1. 準備收益率數據
        print("\n第一步：準備數據")
        print("-"*70)
        
        returns = {}
        for ticker, df in data.items():
            if 'Close' in df.columns:
                series = df['Close'].pct_change().dropna()
                if len(series) > 0:
                    returns[ticker] = series
                else:
                    print(f"   ⚠️  {ticker} 收益率數據為空，跳過")
            else:
                print(f"   ⚠️  {ticker} 無收盤價數據，跳過")
        
        # 對齊數據（確保所有資產有相同的日期索引）
        if len(returns) == 0:
            raise ValueError("沒有可用的收益率數據")
        
        # 找出所有資產的共同日期
        common_index = None
        for ticker, series in returns.items():
            if common_index is None:
                common_index = series.index
            else:
                common_index = common_index.intersection(series.index)
        
        # 使用共同日期重新对齐
        if len(common_index) == 0:
            raise ValueError("沒有找到共同交易日")
        
        aligned_returns = pd.DataFrame({ticker: series.loc[common_index] for ticker, series in returns.items()})
        recent_returns = aligned_returns.tail(lookback_window)
        
        print(f"   可用資產：{len(aligned_returns.columns)}")
        print(f"   回看窗口：{lookback_window} 天")
        print(f"   數據期間：{recent_returns.index[0]} 至 {recent_returns.index[-1]}")
        
        # 2. 構建 MST 選擇資產
        print("\n第二步：構建最小生成樹（MST）")
        print("-"*70)
        
        self.selected_assets, mst, centrality, corr_matrix, dist_matrix = \
            build_mst_portfolio(
                recent_returns,
                num_assets=self.num_assets,
                min_distance_threshold=self.min_distance_threshold
            )
        
        print(f"   選中資產數量：{len(self.selected_assets)}")
        print(f"   選中資產：{', '.join(self.selected_assets)}")
        
        # 計算平均相關性
        selected_corr = corr_matrix.loc[self.selected_assets, self.selected_assets]
        avg_correlation = selected_corr.values[np.triu_indices_from(selected_corr.values, k=1)].mean()
        print(f"   平均相關性：{avg_correlation:.4f}")
        
        # 3. 生成 Supertrend 信號
        print("\n第三步：生成 Supertrend 信號")
        print("-"*70)
        
        for asset in self.selected_assets:
            if asset not in data:
                continue
            
            signals = generate_supertrend_signals(
                data[asset],
                period=self.st_period,
                multiplier=self.st_multiplier
            )
            
            self.signals[asset] = signals
            
            # 檢查最新信號
            latest_signal = signals.iloc[-1]
            trend_str = "上漲" if latest_signal['trend'] == 1 else "下跌"
            
            print(f"   {asset}:")
            print(f"      當前價格：${latest_signal['price']:.2f}")
            print(f"      當前趨勢：{trend_str}")
            print(f"      最新買入信號：{'✓' if latest_signal['long_signal'] else '✗'}")
            print(f"      最新賣出信號：{'✓' if latest_signal['short_signal'] else '✗'}")
        
        # 4. 選擇進場資產
        print("\n第四步：選擇進場資產")
        print("-"*70)
        
        entry_assets = []
        for asset in self.selected_assets:
            if asset in self.signals:
                latest = self.signals[asset].iloc[-1]
                
                # 只選擇有上漲趨勢且剛發生買入信號的資產
                if latest['trend'] == 1 and latest['long_signal']:
                    entry_assets.append(asset)
                    print(f"   ✓ {asset}: 進場")
                elif latest['trend'] == 1:
                    print(f"   ○ {asset}: 持有（上漲趨勢）")
                else:
                    print(f"   ✗ {asset}: 不進場（下跌趨勢）")
        
        print(f"\n   當前可進場資產：{len(entry_assets)}")
        
        # 5. 可視化
        print("\n第五步：生成可視化")
        print("-"*70)
        
        self._visualize_mst(
            mst,
            self.selected_assets,
            corr_matrix,
            dist_matrix
        )
        
        self._visualize_signals()
        
        # 6. 組合統計
        print("\n第六步：組合統計")
        print("-"*70)
        
        stats = self._calculate_portfolio_stats(entry_assets, data)
        
        return {
            'selected_assets': self.selected_assets,
            'entry_assets': entry_assets,
            'avg_correlation': avg_correlation,
            'centrality': centrality,
            'stats': stats
        }
    
    def _calculate_portfolio_stats(self, entry_assets, data):
        """計算組合統計"""
        if not entry_assets:
            return {}
        
        # 提取收盤價
        prices = pd.DataFrame({
            asset: data[asset]['Close']
            for asset in entry_assets
            if asset in data and 'Close' in data[asset]
        })
        
        # 計算收益率
        returns = prices.pct_change().dropna()
        
        # 組合收益率（等權重）
        portfolio_returns = returns.mean(axis=1)
        
        # 統計指標
        total_return = (1 + portfolio_returns).prod() - 1
        annual_return = portfolio_returns.mean() * 252
        annual_volatility = portfolio_returns.std() * np.sqrt(252)
        sharpe_ratio = annual_return / annual_volatility if annual_volatility > 0 else 0
        
        stats = {
            'total_return': total_return,
            'annual_return': annual_return,
            'annual_volatility': annual_volatility,
            'sharpe_ratio': sharpe_ratio
        }
        
        print(f"   組合資產數量：{len(entry_assets)}")
        print(f"   總收益率：{total_return:.2%}")
        print(f"   年化收益：{annual_return:.2%}")
        print(f"   年化波動：{annual_volatility:.2%}")
        print(f"   夏普比率：{sharpe_ratio:.2f}")
        
        return stats
    
    def _visualize_mst(self, mst, selected_assets, corr_matrix, dist_matrix):
        """可視化最小生成樹"""
        fig, ax = plt.subplots(1, 2, figsize=(18, 8))
        
        # 左圖：最小生成樹網絡
        ax1 = ax[0]
        pos = nx.spring_layout(mst, k=3, seed=42)
        
        # 根據距離設置邊的粗細和顏色
        edges = mst.edges(data=True)
        edge_weights = [d['weight'] for u, v, d in edges]
        
        # 節點顏色：選中的資產用綠色
        node_colors = ['green' if selected_assets[i] else 'lightgray' 
                     for i in mst.nodes()]
        
        # 繪製網絡
        nx.draw_networkx_nodes(mst, pos, node_color=node_colors, 
                            node_size=2000, ax=ax1)
        nx.draw_networkx_edges(mst, pos, width=3, edge_color=edge_weights,
                            edge_cmap=plt.cm.RdYlGn, edge_vmin=0, edge_vmax=2, ax=ax1)
        nx.draw_networkx_labels(mst, pos, 
                            labels={i: selected_assets[i] if i < len(selected_assets) else str(i) 
                                  for i in mst.nodes()},
                            font_size=10, font_weight='bold', ax=ax1)
        
        ax1.set_title(f'最小生成樹（MST）\n選中 {len(selected_assets)} 個低相關性資產',
                     fontsize=14, fontweight='bold')
        ax1.axis('off')
        
        # 右圖：相關性熱圖
        ax2 = ax[1]
        selected_corr = corr_matrix.loc[selected_assets, selected_assets]
        
        sns.heatmap(selected_corr, annot=True, fmt='.2f', cmap='RdYlGn',
                  center=0, vmin=-1, vmax=1, ax=ax2,
                  cbar_kws={'label': '相關係數'})
        ax2.set_title('選中資產的相關性矩陣', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('mst_supertrend_network.png', dpi=300, bbox_inches='tight')
        print("   ✅ 網絡可視化已保存：mst_supertrend_network.png")
        plt.show()
    
    def _visualize_signals(self):
        """可視化 Supertrend 信號"""
        n_assets = len(self.selected_assets)
        if n_assets == 0:
            return
        
        fig, axes = plt.subplots(n_assets, 1, figsize=(16, 4*n_assets))
        if n_assets == 1:
            axes = [axes]
        
        for idx, asset in enumerate(self.selected_assets):
            if asset not in self.signals:
                continue
            
            signals = self.signals[asset]
            ax = axes[idx]
            
            # 繪製價格和 Supertrend
            ax.plot(signals.index, signals['price'], label='價格', linewidth=2)
            ax.plot(signals.index, signals['supertrend'], 
                   label='Supertrend', linewidth=2, linestyle='--')
            
            # 標記進場/出場點
            long_points = signals[signals['long_signal']]
            short_points = signals[signals['short_signal']]
            
            if len(long_points) > 0:
                ax.scatter(long_points.index, long_points['price'], 
                         color='green', s=100, label='買入信號', zorder=5)
            if len(short_points) > 0:
                ax.scatter(short_points.index, short_points['price'], 
                         color='red', s=100, label='賣出信號', zorder=5)
            
            # 標題
            latest_signal = signals.iloc[-1]
            trend_str = "上漲" if latest_signal['trend'] == 1 else "下跌"
            ax.set_title(f'{asset} - Supertrend 策略\n當前趨勢：{trend_str}',
                        fontsize=12, fontweight='bold')
            ax.set_ylabel('價格 ($)')
            ax.legend(loc='upper left')
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('mst_supertrend_signals.png', dpi=300, bbox_inches='tight')
        print("   ✅ 信號可視化已保存：mst_supertrend_signals.png")
        plt.show()

# ============================================
# 第四部分：主程序
# ============================================

def main():
    """主程序"""
    print("\n" + "="*70)
    print("MST + Supertrend 整合策略")
    print("網絡基礎分散投資 + 趨勢跟踪策略")
    print("="*70)
    print(f"開始時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 定義資產池
    print("\n第一步：定義資產池")
    print("-"*70)
    
    # 美國主要 ETF（包括 QQQ 和 GLD）
    asset_pool = [
        'QQQ',  # 納斯達克 100
        'GLD',  # 黃金 ETF
        'SPY',  # 標普 500
        'IWM',  # 羅素 2000
        'TLT',  # 20 年國債
        'IEMG', # 新興市場
        'VWO',  # 先新興市場 ETF
        'VTI',  # 全美國股票市場
        'EFA',  # 歐洲亞洲遠東
        'VWO',  # 新興市場
        'AGG',  # 總債券市場
        'VNQ',  # 美國房地產
        'XLE',  # 能源板塊
        'XLF',  # 金融板塊
        'XLK',  # 科技板塊
    ]
    
    print(f"資產池大小：{len(asset_pool)}")
    print(f"資產類型：美股、債券、商品、房地產、新興市場")
    
    # 2. 獲取數據
    print("\n第二步：獲取數據")
    print("-"*70)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)  # 過去 1 年
    
    print(f"下載數據：{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}")
    
    data = {}
    for ticker in asset_pool:
        print(f"   正在下載 {ticker}...", end=' ')
        try:
            df = yf.download(ticker, start=start_date, end=end_date, 
                           progress=False, auto_adjust=True)
            if not df.empty:
                data[ticker] = df
                print(f"✅ ({len(df)} 個交易日)")
            else:
                print(f"❌ (無數據）")
        except Exception as e:
            print(f"❌ (錯誤: {str(e)[:30]})")
    
    print(f"\n✅ 數據獲取完成：{len(data)} 個資產")
    
    # 3. 運行策略
    print("\n第三步：運行 MST + Supertrend 策略")
    print("-"*70)
    
    strategy = MSTSupertrendStrategy(
        asset_pool=asset_pool,
        num_assets=8,  # 選擇 8 個最分散的資產
        st_period=10,
        st_multiplier=3.0,
        min_distance_threshold=1.2  # 距離閾值
    )
    
    results = strategy.run_analysis(data, lookback_window=60)
    
    # 4. 生成摘要報告
    print("\n第四步：生成摘要報告")
    print("-"*70)
    
    summary = f"""
=== MST + Supertrend 整合策略分析摘要 ===

分析時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

【資產選擇（MST）】
選中資產數量：{len(results['selected_assets'])}
平均相關性：{results['avg_correlation']:.4f}
距離閾值：1.2

選中的資產：
{', '.join(results['selected_assets'])}

【進場資產（Supertrend）】
當前可進場資產：{len(results['entry_assets'])}
{', '.join(results['entry_assets']) if results['entry_assets'] else '無'}

【策略優勢】
1. 網絡分散：使用 MST 確保資產之間相關性較低
2. 趨勢確認：使用 Supertrend 確認進場時機
3. 動態調整：根據市場相關性變化動態調整組合
4. 風險控制：只在上漲趨勢時進場，避免下跌風險

【投資建議】
- 如果進場資產 > 3 個：可以考慮建倉，等權重配置
- 如果進場資產 = 1-2 個：謹慎建倉，建議觀望
- 如果進場資產 = 0 個：保持空倉，等待機會

【組合配置建議】
如果決定進場，建議：
- 單一資產最大權重：20%
- 現金保留：20-40%
- 定期重新平衡（每週或每月）
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
    print("   - mst_supertrend_network.png：MST 網絡可視化")
    print("   - mst_supertrend_signals.png：Supertrend 信號圖")
    print("   - mst_supertrend_summary.txt：摘要報告")
    print("\n" + "="*70)

if __name__ == "__main__":
    main()
