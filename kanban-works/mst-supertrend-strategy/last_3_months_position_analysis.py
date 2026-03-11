"""
相關性策略 90/10/60 動態閾值 - 過去 3 個月倉位調整詳情分析
詳細分析每次倉位調整的時機、原因和效果
"""

import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class Last1YearPositionAnalysis:
    """過去 3 個月倉位調整詳情分析"""
    
    def __init__(self):
        pass
    
    def calculate_correlation(self, prices, window=60):
        """計算滾動相關性"""
        returns = prices.pct_change().dropna()
        rolling_corr = returns.rolling(window=window).corr()
        
        def avg_correlation(corr_matrix):
            if corr_matrix.isna().all().all():
                return np.nan
            values = corr_matrix.values
            mask = np.triu_indices_from(values, k=1)
            return values[mask].mean()
        
        avg_corr_series = rolling_corr.groupby(level=0).apply(avg_correlation)
        return avg_corr_series
    
    def get_dynamic_threshold_901060(self, correlation_history):
        """90/10/60 版本的動態閾值計算"""
        high_threshold = correlation_history.quantile(0.90)
        low_threshold = correlation_history.quantile(0.10)
        return high_threshold, low_threshold
    
    def calculate_position_size_901060(self, correlation, high_threshold, low_threshold):
        """90/10/60 版本的倉位計算"""
        if correlation < low_threshold:
            position_size = 1.0
            market_state = '正常市場'
        elif correlation > high_threshold:
            position_size = 0.0
            market_state = '危機市場'
        else:
            position_size = 0.5
            market_state = '過渡市場'
        
        return position_size, market_state
    
    def analyze_last_1_year(self, prices, index_prices):
        """分析過去 1 年的倉位調整"""
        correlation_series = self.calculate_correlation(prices)
        
        # 對齊數據
        aligned_data = pd.concat([
            correlation_series,
            index_prices
        ], axis=1).dropna()
        
        aligned_data.columns = ['correlation', 'index_price']
        
        # 過濾過去 1 年的數據
        one_year_ago = datetime.now() - timedelta(days=365)
        recent_data = aligned_data[aligned_data.index >= one_year_ago]
        
        if recent_data.empty:
            print("沒有足夠的數據（過去 1 年）")
            return None, None, None
        
        signals = []
        position_changes = []
        previous_state = None
        previous_position = None
        
        for i in range(len(recent_data)):
            history = aligned_data[aligned_data.index < recent_data.index[i]]
            
            if len(history) < 60:
                continue
            
            current_corr = recent_data['correlation'].iloc[i]
            current_price = recent_data['index_price'].iloc[i]
            previous_price = recent_data['index_price'].iloc[i-1] if i > 0 else current_price
            
            # 計算動態閾值
            high_threshold, low_threshold = self.get_dynamic_threshold_901060(history['correlation'])
            
            # 計算倉位
            position_size, market_state = self.calculate_position_size_901060(
                current_corr,
                high_threshold,
                low_threshold
            )
            
            # 計算收益率
            index_return = (current_price - previous_price) / previous_price
            strategy_return = position_size * index_return
            
            signals.append({
                'date': recent_data.index[i],
                'correlation': current_corr,
                'high_threshold': high_threshold,
                'low_threshold': low_threshold,
                'market_state': market_state,
                'position_size': position_size,
                'index_price': current_price,
                'index_return': index_return,
                'strategy_return': strategy_return,
                'threshold_width': high_threshold - low_threshold
            })
            
            # 檢測倉位變化
            if previous_position is not None and position_size != previous_position:
                position_change = {
                    'date': recent_data.index[i],
                    'from_position': previous_position,
                    'to_position': position_size,
                    'from_state': previous_state,
                    'to_state': market_state,
                    'position_change': position_size - previous_position,
                    'index_price': current_price,
                    'correlation': current_corr,
                    'high_threshold': high_threshold,
                    'low_threshold': low_threshold,
                    'change_type': self.get_change_type(previous_position, position_size)
                }
                position_changes.append(position_change)
            
            previous_state = market_state
            previous_position = position_size
        
        signals_df = pd.DataFrame(signals)
        if not signals_df.empty:
            signals_df.set_index('date', inplace=True)
        
        position_changes_df = pd.DataFrame(position_changes)
        
        return signals_df, position_changes_df, recent_data
    
    def get_change_type(self, from_position, to_position):
        """獲取倉位變化類型"""
        if from_position == 0 and to_position == 0.5:
            return '加倉（空手 → 50%）'
        elif from_position == 0.5 and to_position == 1.0:
            return '加倉（50% → 100%）'
        elif from_position == 1.0 and to_position == 0.5:
            return '減倉（100% → 50%）'
        elif from_position == 0.5 and to_position == 0:
            return '減倉（50% → 空手）'
        elif from_position == 0 and to_position == 1.0:
            return '加倉（空手 → 100%）'
        elif from_position == 1.0 and to_position == 0:
            return '減倉（100% → 空手）'
        else:
            return f'倉位變化（{int(from_position*100)}% → {int(to_position*100)}%）'
    
    def analyze_position_change_effect(self, position_changes_df, index_prices):
        """分析倉位變化後的效果（10/20/30 天）"""
        if position_changes_df.empty:
            return None
        
        results = []
        
        for idx, change in position_changes_df.iterrows():
            change_date = change['date']
            change_price = change['index_price']
            change_type = change['change_type']
            from_position = change['from_position']
            to_position = change['to_position']
            
            # 計算 10/20/30 天後的收益
            for days in [10, 20, 30]:
                future_idx = index_prices.index.get_indexer([change_date], method='nearest')[0] + days
                
                if future_idx < len(index_prices):
                    future_date = index_prices.index[future_idx]
                    future_price = float(index_prices.iloc[future_idx].iloc[0])
                    
                    # 計算收益
                    future_return = (future_price - change_price) / change_price
                    
                    results.append({
                        'change_date': change_date,
                        'days_after': days,
                        'future_date': future_date,
                        'change_type': change_type,
                        'from_position': from_position,
                        'to_position': to_position,
                        'change_price': change_price,
                        'future_price': future_price,
                        'future_return': future_return,
                        'future_return_pct': future_return * 100
                    })
        
        results_df = pd.DataFrame(results)
        
        return results_df
    
    def print_position_changes_summary(self, position_changes_df, signals_df):
        """打印倉位變化總結"""
        print("="*100)
        print("📊 過去 1 年倉位調整總結")
        print("="*100)
        
        if position_changes_df.empty:
            print("沒有倉位調整")
            return
        
        print(f"\n總倉位調整次數: {len(position_changes_df)}")
        
        # 統計各種倉位變化類型
        change_type_counts = position_changes_df['change_type'].value_counts()
        print(f"\n倉位變化類型統計:")
        for change_type, count in change_type_counts.items():
            print(f"  - {change_type}: {count} 次")
        
        # 統計市場狀態變化
        market_state_counts = signals_df['market_state'].value_counts()
        print(f"\n市場狀態統計:")
        for state, count in market_state_counts.items():
            percentage = count / len(signals_df) * 100
            print(f"  - {state}: {count} 天 ({percentage:.1f}%)")
        
        # 計算平均倉位
        avg_position_size = signals_df['position_size'].mean()
        print(f"\n平均倉位: {avg_position_size:.2%}")
        
        # 計算相關性統計
        correlation_mean = signals_df['correlation'].mean()
        correlation_std = signals_df['correlation'].std()
        correlation_min = signals_df['correlation'].min()
        correlation_max = signals_df['correlation'].max()
        
        print(f"\n相關性統計:")
        print(f"  - 平均值: {correlation_mean:.4f}")
        print(f"  - 標準差: {correlation_std:.4f}")
        print(f"  - 最小值: {correlation_min:.4f}")
        print(f"  - 最大值: {correlation_max:.4f}")
        
        # 計算閾值統計
        high_threshold_mean = signals_df['high_threshold'].mean()
        low_threshold_mean = signals_df['low_threshold'].mean()
        threshold_width_mean = signals_df['threshold_width'].mean()
        
        print(f"\n動態閾值統計:")
        print(f"  - 高閾值（90%）平均: {high_threshold_mean:.4f}")
        print(f"  - 低閾值（10%）平均: {low_threshold_mean:.4f}")
        print(f"  - 閾值寬度平均: {threshold_width_mean:.4f}")
        
        # 打印詳細倉位變化信息
        print(f"\n{'='*100}")
        print("📅 詳細倉位變化信息")
        print("="*100)
        
        for idx, change in position_changes_df.iterrows():
            print(f"\n{idx + 1}. {change['date'].strftime('%Y-%m-%d %A')}")
            print(f"   變化類型: {change['change_type']}")
            print(f"   市場狀態: {change['from_state']} → {change['to_state']}")
            print(f"   相關性: {change['correlation']:.4f}")
            print(f"   高閾值: {change['high_threshold']:.4f}")
            print(f"   低閾值: {change['low_threshold']:.4f}")
            print(f"   SPY 價格: {change['index_price']:.2f}")
            
            # 判斷倉位變化方向
            if change['position_change'] > 0:
                print(f"   方向: 🟢 加倉 {abs(change['position_change']*100):.0f}%")
            elif change['position_change'] < 0:
                print(f"   方向: 🔴 減倉 {abs(change['position_change']*100):.0f}%")
            else:
                print(f"   方向: ➡️ 無變化")
    
    def print_position_change_effects(self, effects_df):
        """打印倉位變化效果"""
        print(f"\n{'='*100}")
        print("💰 倉位變化效果分析（10/20/30 天後）")
        print("="*100)
        
        if effects_df.empty:
            print("沒有倉位變化效果數據")
            return
        
        # 統計各種天數的平均收益
        for days in [10, 20, 30]:
            days_data = effects_df[effects_df['days_after'] == days]
            
            print(f"\n{days} 天後效果分析:")
            print(f"  - 平均收益: {days_data['future_return_pct'].mean():.2f}%")
            print(f"  - 標準差: {days_data['future_return_pct'].std():.2f}%")
            print(f"  - 勝率: {(days_data['future_return_pct'] > 0).sum() / len(days_data) * 100:.1f}%")
            print(f"  - 最大收益: {days_data['future_return_pct'].max():.2f}%")
            print(f"  - 最小收益: {days_data['future_return_pct'].min():.2f}%")
            
            # 統計各種變化類型的收益
            print(f"  各種變化類型的平均收益:")
            for change_type in days_data['change_type'].unique():
                type_data = days_data[days_data['change_type'] == change_type]
                avg_return = type_data['future_return_pct'].mean()
                count = len(type_data)
                print(f"    - {change_type}: {avg_return:.2f}% ({count} 次)")
        
        # 打印詳細效果信息
        print(f"\n{'='*100}")
        print("📅 詳細倉位變化效果")
        print("="*100)
        
        for idx, effect in effects_df.iterrows():
            emoji = "✅" if effect['future_return'] > 0 else "❌"
            print(f"\n{emoji} {effect['change_date'].strftime('%Y-%m-%d')} ({effect['days_after']} 天後)")
            print(f"   變化類型: {effect['change_type']}")
            print(f"   變化時價格: {effect['change_price']:.2f}")
            print(f"   {effect['days_after']} 天後價格: {effect['future_price']:.2f}")
            print(f"   收益率: {effect['future_return_pct']:.2f}%")
            print(f"   未來日期: {effect['future_date'].strftime('%Y-%m-%d')}")
    
    def plot_last_1_year(self, signals_df, position_changes_df, index_prices):
        """繪製過去 3 個月倉位變化圖表"""
        import matplotlib.pyplot as plt
        
        fig, axes = plt.subplots(3, 1, figsize=(18, 16))
        
        # 過濾過去 1 年的數據
        one_year_ago = datetime.now() - timedelta(days=365)
        recent_index_prices = index_prices[index_prices.index >= one_year_ago]
        
        # 子圖 1：SPY 價格與倉位變化點
        axes[0].plot(recent_index_prices.index, recent_index_prices.values, 
                    label='SPY 價格', linewidth=2, color='black', alpha=0.7)
        
        # 標記倉位變化點
        for idx, change in position_changes_df.iterrows():
            change_date = change['date']
            change_price = change['index_price']
            to_position = change['to_position']
            change_type = change['change_type']
            
            if to_position == 1.0:
                marker = '^'
                color = 'green'
                label = '加倉到 100%' if idx == 0 else ''
            elif to_position == 0:
                marker = 'v'
                color = 'red'
                label = '減倉到 0%' if idx == 0 else ''
            elif to_position == 0.5:
                if change['from_position'] == 1.0:
                    marker = 'v'
                    color = 'orange'
                    label = '減倉到 50%' if idx == 0 else ''
                else:
                    marker = '^'
                    color = 'lightgreen'
                    label = '加倉到 50%' if idx == 0 else ''
            
            axes[0].scatter(change_date, change_price, 
                           marker=marker, s=200, color=color, 
                           label=label, alpha=0.8, edgecolors='white', linewidth=2)
        
        axes[0].set_title('SPY 價格與倉位變化點（過去 1 年）', fontsize=16, fontweight='bold')
        axes[0].set_ylabel('價格', fontsize=14)
        axes[0].legend(loc='upper left', fontsize=12)
        axes[0].grid(True, alpha=0.3)
        
        # 子圖 2：相關性與動態閾值
        axes[1].plot(signals_df.index, signals_df['correlation'], 
                    label='相關性', linewidth=2, color='purple', alpha=0.7)
        axes[1].plot(signals_df.index, signals_df['high_threshold'], 
                    label='高閾值（90 分位）', linewidth=1.5, color='red', 
                    linestyle='--', alpha=0.6)
        axes[1].plot(signals_df.index, signals_df['low_threshold'], 
                    label='低閾值（10 分位）', linewidth=1.5, color='green', 
                    linestyle='--', alpha=0.6)
        
        # 標記倉位變化點
        for idx, change in position_changes_df.iterrows():
            change_date = change['date']
            current_corr = change['correlation']
            
            to_position = change['to_position']
            
            if to_position == 1.0:
                marker = '^'
                color = 'green'
            elif to_position == 0:
                marker = 'v'
                color = 'red'
            elif to_position == 0.5:
                if change['from_position'] == 1.0:
                    marker = 'v'
                    color = 'orange'
                else:
                    marker = '^'
                    color = 'lightgreen'
            
            axes[1].scatter(change_date, current_corr, 
                           marker=marker, s=150, color=color, 
                           alpha=0.8, edgecolors='white', linewidth=2)
        
        axes[1].set_title('相關性與動態閾值（過去 1 年）', fontsize=16, fontweight='bold')
        axes[1].set_ylabel('相關係數', fontsize=14)
        axes[1].legend(loc='upper left', fontsize=12)
        axes[1].grid(True, alpha=0.3)
        
        # 子圖 3：動態倉位
        axes[2].fill_between(signals_df.index, 0, signals_df['position_size'], 
                           alpha=0.3, color='orange', label='動態倉位')
        axes[2].plot(signals_df.index, signals_df['position_size'], 
                    linewidth=2, color='orange', alpha=0.7)
        
        # 標記倉位變化點
        for idx, change in position_changes_df.iterrows():
            change_date = change['date']
            to_position = change['to_position']
            from_position = change['from_position']
            
            axes[2].scatter(change_date, to_position, 
                           marker='o', s=200, color='blue', 
                           alpha=0.8, edgecolors='white', linewidth=2)
            
            # 標註倉位變化
            axes[2].annotate(f'{int(from_position*100)}%→{int(to_position*100)}%',
                           xy=(change_date, to_position),
                           xytext=(10, 10), textcoords='offset points',
                           fontsize=9, bbox=dict(boxstyle='round,pad=0.3', 
                                                 facecolor='white', alpha=0.8),
                           arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
        
        # 標記倉位水平線
        axes[2].axhline(y=1.0, color='green', linestyle='--', 
                       linewidth=1, alpha=0.5, label='100% 倉位')
        axes[2].axhline(y=0.5, color='yellow', linestyle='--', 
                       linewidth=1, alpha=0.5, label='50% 倉位')
        axes[2].axhline(y=0.0, color='red', linestyle='--', 
                       linewidth=1, alpha=0.5, label='0% 倉位')
        
        axes[2].set_title('動態倉位（過去 1 年）', fontsize=16, fontweight='bold')
        axes[2].set_ylabel('倉位大小', fontsize=14)
        axes[2].set_xlabel('日期', fontsize=14)
        axes[2].set_ylim([-0.1, 1.1])
        axes[2].legend(loc='upper left', fontsize=10)
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('last_1_year_position_changes.png', dpi=150, bbox_inches='tight')
        print(f"\n📊 圖表已保存: last_1_year_position_changes.png")
        plt.close()


def main():
    """主函數"""
    print("="*100)
    print("🚀 相關性策略 90/10/60 - 過去 1 年倉位調整詳情分析")
    print("="*100)
    
    # 創建分析實例
    analyzer = Last1YearPositionAnalysis()
    
    # 測試資產
    tickers = ['SPY', 'QQQ', 'IWM', 'XLI', 'XLV', 'XLK', 'XLF', 'XLE']
    
    print(f"\n下載 {len(tickers)} 個資產的數據...")
    prices = yf.download(tickers, period='2y', progress=False, auto_adjust=True)['Close']
    
    # 下載指數數據
    print("下載 SPY 指數數據...")
    index_prices = yf.download('SPY', period='2y', progress=False, auto_adjust=True)['Close']
    
    # 分析過去 1 年的倉位調整
    print("\n分析過去 1 年的倉位調整...")
    signals_df, position_changes_df, recent_data = analyzer.analyze_last_1_year(prices, index_prices)
    
    if signals_df is None or position_changes_df is None:
        print("沒有足夠的數據")
        return
    
    # 打印倉位變化總結
    analyzer.print_position_changes_summary(position_changes_df, signals_df)
    
    # 分析倉位變化效果
    print("\n分析倉位變化效果...")
    effects_df = analyzer.analyze_position_change_effect(position_changes_df, index_prices)
    
    if effects_df is not None:
        analyzer.print_position_change_effects(effects_df)
    
    # 繪製倉位變化圖表
    print("\n繪製倉位變化圖表...")
    analyzer.plot_last_1_year(signals_df, position_changes_df, index_prices)
    
    # 保存結果
    if not position_changes_df.empty:
        position_changes_df.to_csv('last_1_year_position_changes.csv', index=False)
        print(f"\n💾 倉位變化數據已保存: last_1_year_position_changes.csv")
    
    if effects_df is not None:
        effects_df.to_csv('last_1_year_position_effects.csv', index=False)
        print(f"💾 倉位變化效果已保存: last_1_year_position_effects.csv")
    
    print("\n✅ 分析完成！")


if __name__ == '__main__':
    main()
