"""
相關性策略 90/10/60 版本 - 過去 3 年進場出時機分析
識別市場狀態轉換點，分析進場和出場時機
"""

import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 設置中文字體
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


class CorrelationStrategyEntryExit:
    """相關性策略進場出時機分析"""
    
    def __init__(self):
        self.transitions = []
    
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
    
    def analyze_entry_exit(self, prices, index_prices):
        """分析進場出時機"""
        correlation_series = self.calculate_correlation(prices)
        
        # 對齊數據
        aligned_data = pd.concat([
            correlation_series,
            index_prices
        ], axis=1).dropna()
        
        aligned_data.columns = ['correlation', 'index_price']
        
        signals = []
        transitions = []
        previous_state = None
        
        for i in range(len(aligned_data)):
            if i >= 60:
                history = aligned_data['correlation'].iloc[:i]
                high_threshold, low_threshold = self.get_dynamic_threshold_901060(history)
                
                current_corr = aligned_data['correlation'].iloc[i]
                current_price = aligned_data['index_price'].iloc[i]
                previous_price = aligned_data['index_price'].iloc[i-1] if i > 0 else current_price
                
                # 計算倉位
                position_size, market_state = self.calculate_position_size_901060(
                    current_corr,
                    high_threshold,
                    low_threshold
                )
                
                # 檢測市場狀態轉換
                if previous_state is not None and market_state != previous_state:
                    transition = {
                        'date': aligned_data.index[i],
                        'from_state': previous_state,
                        'to_state': market_state,
                        'from_position': 1.0 if previous_state == '正常市場' else (0.5 if previous_state == '過渡市場' else 0.0),
                        'to_position': position_size,
                        'index_price': current_price,
                        'correlation': current_corr,
                        'high_threshold': high_threshold,
                        'low_threshold': low_threshold,
                        'transition_type': self.get_transition_type(previous_state, market_state)
                    }
                    transitions.append(transition)
                
                # 計算收益率
                index_return = (current_price - previous_price) / previous_price
                strategy_return = position_size * index_return
                
                signals.append({
                    'date': aligned_data.index[i],
                    'correlation': current_corr,
                    'high_threshold': high_threshold,
                    'low_threshold': low_threshold,
                    'market_state': market_state,
                    'position_size': position_size,
                    'index_price': current_price,
                    'index_return': index_return,
                    'strategy_return': strategy_return
                })
                
                previous_state = market_state
        
        signals_df = pd.DataFrame(signals)
        if not signals_df.empty:
            signals_df.set_index('date', inplace=True)
        
        transitions_df = pd.DataFrame(transitions)
        
        return signals_df, transitions_df
    
    def get_transition_type(self, from_state, to_state):
        """獲取轉換類型"""
        transition = f"{from_state} → {to_state}"
        
        if transition == '正常市場 → 過渡市場':
            return '減倉（出場 50%）'
        elif transition == '過渡市場 → 危機市場':
            return '減倉（出場 100%）'
        elif transition == '危機市場 → 過渡市場':
            return '加倉（進場 50%）'
        elif transition == '過渡市場 → 正常市場':
            return '加倉（進場 100%）'
        else:
            return transition
    
    def analyze_transitions(self, transitions_df, index_prices):
        """分析轉換點的收益"""
        if transitions_df.empty:
            print("沒有市場狀態轉換")
            return
        
        results = []
        
        for idx, transition in transitions_df.iterrows():
            transition_date = transition['date']
            transition_type = transition['transition_type']
            from_state = transition['from_state']
            to_state = transition['to_state']
            transition_price = transition['index_price']
            
            # 計算轉換後的收益（60 天後）
            future_idx = index_prices.index.get_indexer([transition_date], method='nearest')[0] + 60
            
            if future_idx < len(index_prices):
                future_date = index_prices.index[future_idx]
                future_price = float(index_prices.iloc[future_idx].iloc[0])  # 轉換為 float
                
                # 計算收益
                future_return = (future_price - transition_price) / transition_price
                
                results.append({
                    'transition_date': transition_date,
                    'transition_type': transition_type,
                    'from_state': from_state,
                    'to_state': to_state,
                    'transition_price': transition_price,
                    'future_date': future_date,
                    'future_price': future_price,
                    'future_return': future_return,
                    'future_return_pct': future_return * 100
                })
        
        results_df = pd.DataFrame(results)
        
        return results_df
    
    def print_transitions_summary(self, transitions_df, transitions_analysis_df):
        """打印轉換點總結"""
        print("="*100)
        print("📊 市場狀態轉換點分析")
        print("="*100)
        
        if transitions_df.empty:
            print("沒有市場狀態轉換")
            return
        
        print(f"\n總轉換次數: {len(transitions_df)}")
        
        # 統計各種轉換類型
        transition_counts = transitions_df['transition_type'].value_counts()
        print(f"\n轉換類型統計:")
        for transition_type, count in transition_counts.items():
            print(f"  - {transition_type}: {count} 次")
        
        # 統計各種市場狀態
        from_state_counts = transitions_df['from_state'].value_counts()
        print(f"\n出現的市場狀態:")
        for state, count in from_state_counts.items():
            print(f"  - {state}: {count} 次")
        
        # 打印詳細轉換信息
        print(f"\n{'='*100}")
        print("📅 詳細轉換信息")
        print("="*100)
        
        for idx, transition in transitions_df.iterrows():
            print(f"\n{idx + 1}. {transition['date'].strftime('%Y-%m-%d')}")
            print(f"   轉換: {transition['from_state']} → {transition['to_state']}")
            print(f"   操作: {transition['transition_type']}")
            print(f"   相關性: {transition['correlation']:.4f}")
            print(f"   高閾值: {transition['high_threshold']:.4f}")
            print(f"   低閾值: {transition['low_threshold']:.4f}")
            print(f"   SPY 價格: {transition['index_price']:.2f}")
        
        # 分析轉換後的收益
        if not transitions_analysis_df.empty:
            print(f"\n{'='*100}")
            print("💰 轉換後收益分析（60 天後）")
            print("="*100)
            
            # 統計各種轉換類型的平均收益
            avg_return_by_type = transitions_analysis_df.groupby('transition_type')['future_return_pct'].agg(['mean', 'std', 'count'])
            print(f"\n各種轉換類型的平均收益:")
            for transition_type, row in avg_return_by_type.iterrows():
                print(f"  - {transition_type}:")
                print(f"      平均收益: {row['mean']:.2f}%")
                print(f"      標準差: {row['std']:.2f}%")
                print(f"      次數: {int(row['count'])}")
            
            # 統計總體表現
            print(f"\n總體表現:")
            print(f"  - 平均收益: {transitions_analysis_df['future_return_pct'].mean():.2f}%")
            print(f"  - 標準差: {transitions_analysis_df['future_return_pct'].std():.2f}%")
            print(f"  - 勝率: {(transitions_analysis_df['future_return_pct'] > 0).sum() / len(transitions_analysis_df) * 100:.2f}%")
            
            # 打印詳細收益信息
            print(f"\n{'='*100}")
            print("📅 詳細收益信息（60 天後）")
            print("="*100)
            
            for idx, result in transitions_analysis_df.iterrows():
                emoji = "✅" if result['future_return'] > 0 else "❌"
                print(f"\n{emoji} {result['transition_date'].strftime('%Y-%m-%d')}")
                print(f"   操作: {result['transition_type']}")
                print(f"   轉換時價格: {result['transition_price']:.2f}")
                print(f"   60 天後價格: {result['future_price']:.2f}")
                print(f"   收益率: {result['future_return_pct']:.2f}%")
    
    def plot_entry_exit(self, signals_df, transitions_df, index_prices):
        """繪製進場出時機圖表"""
        fig, axes = plt.subplots(3, 1, figsize=(18, 16))
        
        # 子圖 1：SPY 價格與進場出點
        axes[0].plot(index_prices.index, index_prices.values, 
                    label='SPY 價格', linewidth=2, color='black', alpha=0.7)
        
        # 標記進場出點
        for idx, transition in transitions_df.iterrows():
            transition_date = transition['date']
            transition_price = transition['index_price']
            transition_type = transition['transition_type']
            
            if '進場' in transition_type:
                axes[0].scatter(transition_date, transition_price, 
                               marker='^', s=200, color='green', 
                               label='進場' if idx == 0 else '', alpha=0.8)
            elif '出場' in transition_type:
                axes[0].scatter(transition_date, transition_price, 
                               marker='v', s=200, color='red', 
                               label='出場' if idx == 0 else '', alpha=0.8)
        
        axes[0].set_title('SPY 價格與進場出時機', fontsize=16, fontweight='bold')
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
        
        # 標記市場狀態區域
        state_colors = {
            '正常市場': 'green',
            '過渡市場': 'yellow',
            '危機市場': 'red'
        }
        
        previous_state = None
        state_start = None
        
        for idx, row in signals_df.iterrows():
            current_state = row['market_state']
            
            if current_state != previous_state:
                if previous_state is not None:
                    axes[1].axvspan(state_start, idx, 
                                   alpha=0.1, color=state_colors[previous_state],
                                   label=previous_state if state_start is not None else '')
                
                previous_state = current_state
                state_start = idx
        
        if previous_state is not None:
            axes[1].axvspan(state_start, len(signals_df), 
                           alpha=0.1, color=state_colors[previous_state])
        
        axes[1].set_title('相關性與動態閾值', fontsize=16, fontweight='bold')
        axes[1].set_ylabel('相關係數', fontsize=14)
        axes[1].legend(loc='upper left', fontsize=10)
        axes[1].grid(True, alpha=0.3)
        
        # 子圖 3：動態倉位
        axes[2].fill_between(signals_df.index, 0, signals_df['position_size'], 
                           alpha=0.3, color='orange', label='動態倉位')
        axes[2].plot(signals_df.index, signals_df['position_size'], 
                    linewidth=2, color='orange', alpha=0.7)
        
        # 標記倉位變化點
        for idx, transition in transitions_df.iterrows():
            transition_date = transition['date']
            from_position = transition['from_position']
            to_position = transition['to_position']
            
            axes[2].scatter(transition_date, to_position, 
                           marker='o', s=200, color='blue', 
                           alpha=0.8, edgecolors='white', linewidth=2)
            
            # 標註倉位變化
            axes[2].annotate(f'{int(from_position*100)}%→{int(to_position*100)}%',
                           xy=(transition_date, to_position),
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
        
        axes[2].set_title('動態倉位', fontsize=16, fontweight='bold')
        axes[2].set_ylabel('倉位大小', fontsize=14)
        axes[2].set_xlabel('日期', fontsize=14)
        axes[2].set_ylim([-0.1, 1.1])
        axes[2].legend(loc='upper left', fontsize=10)
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('correlation_entry_exit_3years.png', dpi=150, bbox_inches='tight')
        print(f"\n📊 圖表已保存: correlation_entry_exit_3years.png")
        plt.close()


def main():
    """主函數"""
    print("="*100)
    print("🚀 相關性策略 90/10/60 版本 - 過去 3 年進場出時機分析")
    print("="*100)
    
    # 創建分析實例
    analyzer = CorrelationStrategyEntryExit()
    
    # 測試資產
    tickers = ['SPY', 'QQQ', 'IWM', 'XLI', 'XLV', 'XLK', 'XLF', 'XLE']
    
    print(f"\n下載 {len(tickers)} 個資產的數據（過去 3 年）...")
    prices = yf.download(tickers, period='3y', progress=False, auto_adjust=True)['Close']
    
    # 下載指數數據
    print("下載 SPY 指數數據（過去 3 年）...")
    index_prices = yf.download('SPY', period='3y', progress=False, auto_adjust=True)['Close']
    
    # 分析進場出時機
    print("\n分析進場出時機...")
    signals_df, transitions_df = analyzer.analyze_entry_exit(prices, index_prices)
    
    # 分析轉換點收益
    print("分析轉換點收益...")
    transitions_analysis_df = analyzer.analyze_transitions(transitions_df, index_prices)
    
    # 打印轉換點總結
    analyzer.print_transitions_summary(transitions_df, transitions_analysis_df)
    
    # 繪製進場出時機圖表
    print("\n繪製進場出時機圖表...")
    analyzer.plot_entry_exit(signals_df, transitions_df, index_prices)
    
    # 保存結果
    if not transitions_df.empty:
        transitions_df.to_csv('correlation_transitions_3years.csv', index=False)
        print(f"\n💾 轉換點數據已保存: correlation_transitions_3years.csv")
    
    if not transitions_analysis_df.empty:
        transitions_analysis_df.to_csv('correlation_transitions_analysis_3years.csv', index=False)
        print(f"💾 轉換點收益分析已保存: correlation_transitions_analysis_3years.csv")
    
    print("\n✅ 分析完成！")


if __name__ == '__main__':
    main()
