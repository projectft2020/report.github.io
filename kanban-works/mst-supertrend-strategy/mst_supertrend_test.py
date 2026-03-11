"""
MST + Supertrend 策略測試腳本
立即可以運行，測試三個場景的實際效果
"""

import numpy as np
import pandas as pd
import yfinance as yf
import networkx as nx
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# 設置中文字體
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

class MSTSupertrendStrategy:
    """MST + Supertrend 整合策略"""
    
    def __init__(self):
        self.asset_pool = self._create_asset_pool()
        
    def _create_asset_pool(self):
        """創建資產池（簡化版，主要 ETF）"""
        return {
            'core': ['SPY', 'QQQ', 'IWM', 'VTI'],
            'sectors': ['XLK', 'XLF', 'XLE', 'XLV', 'XLY', 'XLP', 'XLI'],
            'bonds': ['TLT', 'AGG', 'SHY'],
            'commodities': ['GLD', 'SLV'],
            'currencies': ['UUP', 'FXE']
        }
    
    def fetch_data(self, tickers, period='1y'):
        """獲取價格數據"""
        print(f"下載 {len(tickers)} 個資產的數據...")
        data = yf.download(tickers, period=period, progress=False, auto_adjust=True)
        return data['Close']
    
    def calculate_correlation(self, returns, window=60):
        """計算滾動相關性"""
        return returns.rolling(window=window).corr()
    
    def calculate_mst(self, correlation_matrix):
        """
        構建最小生成樹
        
        參數:
            correlation_matrix: 相關性矩陣
        
        返回:
            selected_assets: 選中的資產
            mst_graph: 最小生成樹圖
        """
        # 計算距離矩陣
        distance_matrix = np.sqrt(2 * (1 - correlation_matrix))
        
        # 構建完全圖
        n_assets = len(correlation_matrix)
        graph = nx.complete_graph(n_assets)
        
        # 給邊加權
        for i, j in graph.edges():
            graph[i][j]['weight'] = distance_matrix.iloc[i, j]
        
        # 計算最小生成樹
        mst = nx.minimum_spanning_tree(graph)
        
        # 計算中心性並選擇資產
        centrality = nx.eigenvector_centrality_numpy(mst)
        sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
        
        # 選擇前 8 個資產
        selected_indices = [node for node, score in sorted_nodes[:8]]
        selected_assets = [correlation_matrix.columns[i] for i in selected_indices]
        
        # 計算平均相關性
        selected_corr = correlation_matrix.loc[selected_assets, selected_assets]
        avg_corr = selected_corr.values[
            np.triu_indices_from(selected_corr.values, k=1)
        ].mean()
        
        return selected_assets, mst, avg_corr
    
    def calculate_supertrend(self, high, low, close, period=10, multiplier=3.0):
        """
        計算 Supertrend 指標
        
        參數:
            high, low, close: 價格序列
            period: ATR 週期
            multiplier: ATR 倍數
        
        返回:
            supertrend: Supertrend 線
            trend: 趨勢（1=上漲，0=下跌）
        """
        # 計算 ATR
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        # 計算基本帶
        hl2 = (high + low) / 2
        upper_band = hl2 + multiplier * atr
        lower_band = hl2 - multiplier * atr
        
        # 初始化
        supertrend = np.full(len(close), np.nan)
        trend = np.zeros(len(close))
        
        supertrend[0] = lower_band.iloc[0]
        trend[0] = 1
        
        for i in range(1, len(close)):
            if trend[i-1] == 1:  # 當前是上漲趨勢
                if close.iloc[i] <= supertrend[i-1]:
                    trend[i] = 0
                    supertrend[i] = upper_band.iloc[i]
                else:
                    trend[i] = 1
                    supertrend[i] = max(supertrend[i-1], lower_band.iloc[i])
            else:  # 當前是下跌趨勢
                if close.iloc[i] >= supertrend[i-1]:
                    trend[i] = 1
                    supertrend[i] = lower_band.iloc[i]
                else:
                    trend[i] = 0
                    supertrend[i] = min(supertrend[i-1], upper_band.iloc[i])
        
        return pd.Series(supertrend, index=close.index), pd.Series(trend, index=close.index)
    
    def check_entry_signals(self, prices, selected_assets, period=10, multiplier=3.0):
        """
        檢查進場信號
        
        參數:
            prices: 價格數據
            selected_assets: MST 選中的資產
            period, multiplier: Supertrend 參數
        
        返回:
            signals_df: 信號 DataFrame
        """
        signals = {}
        
        for asset in selected_assets:
            if asset not in prices.columns:
                continue
            
            supertrend, trend = self.calculate_supertrend(
                prices[asset],
                prices[asset],  # 高價 = 收盤價（簡化）
                prices[asset],  # 低價 = 收盤價（簡化）
                period=period,
                multiplier=multiplier
            )
            
            # 檢測買入信號
            trend_change = trend.diff()
            long_signal = (trend_change == 1)  # 趨勢從 0 轉為 1
            
            signals[asset] = {
                'current_trend': 'UP' if trend.iloc[-1] == 1 else 'DOWN',
                'has_signal': bool(long_signal.iloc[-1]),
                'can_entry': bool(trend.iloc[-1] == 1 and long_signal.iloc[-1]),
                'current_price': float(prices[asset].iloc[-1])
            }
        
        return pd.DataFrame(signals).T
    
    def run_scenario_analysis(self, pool_type='core'):
        """
        運行場景分析
        
        參數:
            pool_type: 資產池類型（'core', 'sectors', 'bonds', 'commodities', 'currencies'）
        
        返回:
            results: 分析結果字典
        """
        print(f"\n{'='*60}")
        print(f"場景分析：{pool_type} 資產池")
        print(f"{'='*60}\n")
        
        # 1. 獲取數據
        tickers = self.asset_pool[pool_type]
        prices = self.fetch_data(tickers)
        returns = prices.pct_change().dropna()
        
        # 2. 計算相關性
        corr_matrix = returns.corr()
        avg_correlation = corr_matrix.values[
            np.triu_indices_from(corr_matrix.values, k=1)
        ].mean()
        
        print(f"📊 資產池相關性分析")
        print(f"  - 資產數量: {len(tickers)}")
        print(f"  - 平均相關性: {avg_correlation:.4f}")
        
        # 3. MST 選擇
        selected_assets, mst_graph, mst_avg_corr = self.calculate_mst(corr_matrix)
        
        print(f"\n🎯 MST 選擇結果")
        print(f"  - 選中資產: {len(selected_assets)} 個")
        print(f"  - 平均相關性: {mst_avg_corr:.4f}")
        print(f"  - 選中資產: {', '.join(selected_assets)}")
        
        # 4. Supertrend 信號檢查
        signals_df = self.check_entry_signals(prices, selected_assets)
        
        print(f"\n🚀 Supertrend 信號分析")
        print(f"  - 上漲趨勢: {sum(signals_df['current_trend'] == 'UP')} 個")
        print(f"  - 買入信號: {sum(signals_df['has_signal'])} 個")
        print(f"  - 可進場: {sum(signals_df['can_entry'])} 個")
        
        # 5. 顯示詳細信號
        print(f"\n📋 詳細信號:")
        entry_assets = []
        for asset, signal in signals_df.iterrows():
            status = "✓ 可進場" if signal['can_entry'] else (
                "⚠ 趨勢上漲但無信號" if signal['current_trend'] == 'UP' else "✗ 無信號"
            )
            print(f"  - {asset}: {status} (${signal['current_price']:.2f})")
            if signal['can_entry']:
                entry_assets.append(asset)
        
        # 6. 結論
        print(f"\n💡 策略結論:")
        if len(entry_assets) == 0:
            print("  - 🔴 無可進場資產，保持現金")
        else:
            print(f"  - 🟢 可進場資產: {len(entry_assets)} 個")
            print(f"  - 📊 等權重配置: 每個資產 {100/len(entry_assets):.1f}%")
            print(f"  - 🎯 推薦配置: {', '.join(entry_assets)}")
        
        # 7. 相關性場景判斷
        if avg_correlation < 0.3:
            scenario = "正常市場（低相關性）"
            suggestion = "MST 選擇 + Supertrend 過濾 = 精準進場"
        elif avg_correlation < 0.6:
            scenario = "過渡市場（中等相關性）"
            suggestion = "謹慎配置，增加現金比例"
        else:
            scenario = "危機市場（高相關性）"
            suggestion = "保持現金，避免虧損"
        
        print(f"\n📈 市場場景: {scenario}")
        print(f"💭 建議: {suggestion}")
        
        return {
            'pool_type': pool_type,
            'tickers': tickers,
            'avg_correlation': avg_correlation,
            'selected_assets': selected_assets,
            'mst_avg_correlation': mst_avg_corr,
            'signals': signals_df,
            'entry_assets': entry_assets,
            'scenario': scenario,
            'suggestion': suggestion
        }
    
    def plot_mst_graph(self, results):
        """繪製 MST 網絡圖"""
        import matplotlib.pyplot as plt
        
        plt.figure(figsize=(12, 8))
        
        # 繪製相關性熱圖
        plt.subplot(2, 2, 1)
        tickers = results['tickers']
        prices = self.fetch_data(tickers)
        returns = prices.pct_change().dropna()
        corr_matrix = returns.corr()
        
        plt.imshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1)
        plt.colorbar(label='相關性')
        plt.title('資產相關性矩陣')
        plt.xticks(range(len(tickers)), tickers, rotation=45, ha='right')
        plt.yticks(range(len(tickers)), tickers)
        
        # 繪製相關性分佈
        plt.subplot(2, 2, 2)
        corr_values = corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)]
        plt.hist(corr_values, bins=20, edgecolor='black')
        plt.axvline(results['avg_correlation'], color='red', linestyle='--', 
                   label=f'平均: {results["avg_correlation"]:.3f}')
        plt.xlabel('相關係數')
        plt.ylabel('頻率')
        plt.title('相關性分佈')
        plt.legend()
        
        # 繪製選中資產的 Supertrend 信號
        plt.subplot(2, 2, 3)
        selected = results['selected_assets']
        signals = results['signals']
        
        entry_status = ['可進場' if s['can_entry'] else '不可進場' for _, s in signals.iterrows()]
        colors = ['green' if s == '可進場' else 'red' for s in entry_status]
        
        plt.bar(selected, colors, alpha=0.7)
        plt.title('Supertrend 進場信號')
        plt.xticks(rotation=45, ha='right')
        plt.ylabel('信號狀態')
        
        # 繪製策略結論
        plt.subplot(2, 2, 4)
        plt.text(0.5, 0.7, f"市場場景: {results['scenario']}", 
                ha='center', fontsize=12, weight='bold')
        plt.text(0.5, 0.5, f"平均相關性: {results['avg_correlation']:.3f}", 
                ha='center', fontsize=11)
        plt.text(0.5, 0.3, f"MST 選中: {len(results['selected_assets'])} 個", 
                ha='center', fontsize=11)
        plt.text(0.5, 0.1, f"可進場: {len(results['entry_assets'])} 個", 
                ha='center', fontsize=11, weight='bold', color='green')
        
        plt.axis('off')
        
        plt.tight_layout()
        plt.savefig('mst_supertrend_analysis.png', dpi=150, bbox_inches='tight')
        print(f"\n📊 圖表已保存: mst_supertrend_analysis.png")
        plt.close()

def main():
    """主函數"""
    print("="*60)
    print("MST + Supertrend 策略測試")
    print("="*60)
    
    # 創建策略實例
    strategy = MSTSupertrendStrategy()
    
    # 測試不同場景
    scenarios = ['core', 'sectors', 'bonds', 'commodities', 'currencies']
    results = {}
    
    for scenario in scenarios:
        try:
            results[scenario] = strategy.run_scenario_analysis(scenario)
        except Exception as e:
            print(f"\n❌ 錯誤: {scenario} - {e}")
            continue
    
    # 繪製圖表（使用第一個成功的場景）
    for scenario, result in results.items():
        try:
            strategy.plot_mst_graph(result)
            break
        except Exception as e:
            print(f"\n❌ 繪圖錯誤: {e}")
            continue
    
    # 總結
    print(f"\n{'='*60}")
    print("📊 測試總結")
    print(f"{'='*60}")
    
    total_assets = sum(len(r['tickers']) for r in results.values())
    total_selected = sum(len(r['selected_assets']) for r in results.values())
    total_entry = sum(len(r['entry_assets']) for r in results.values())
    
    print(f"  - 測試場景: {len(results)} 個")
    print(f"  - 總資產數: {total_assets} 個")
    print(f"  - MST 選中: {total_selected} 個")
    print(f"  - 可進場: {total_entry} 個")
    
    if total_entry > 0:
        print(f"\n🎯 推薦操作:")
        for scenario, result in results.items():
            if len(result['entry_assets']) > 0:
                print(f"  - {scenario}: {', '.join(result['entry_assets'])}")
    else:
        print(f"\n🔴 當前無可進場資產，建議保持現金")

if __name__ == '__main__':
    main()
