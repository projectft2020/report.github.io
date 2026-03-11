"""
相關性策略時機篩選回測
只用 position_size 回測指數，驗證相關性篩選時機是否有優勢
"""

import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 設置中文字體
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


class CorrelationTimingBacktest:
    """相關性策略時機篩選回測"""
    
    def __init__(self):
        self.position_sizes = []
        self.dates = []
    
    def calculate_correlation(self, prices, window=60):
        """
        計算滾動相關性
        
        參數:
            prices: 價格數據
            window: 滾動窗口
        
        返回:
            correlation_series: 平均相關性時間序列
        """
        # 計算收益率
        returns = prices.pct_change().dropna()
        
        # 計算滾動相關性矩陣
        rolling_corr = returns.rolling(window=window).corr()
        
        # 計算平均相關性（去除對角線）
        def avg_correlation(corr_matrix):
            if corr_matrix.isna().all().all():
                return np.nan
            values = corr_matrix.values
            # 只取上三角（不包含對角線）
            mask = np.triu_indices_from(values, k=1)
            return values[mask].mean()
        
        avg_corr_series = rolling_corr.groupby(level=0).apply(avg_correlation)
        
        return avg_corr_series
    
    def get_dynamic_threshold(self, correlation_history, window=252):
        """
        基於歷史分位數計算動態閾值
        
        參數:
            correlation_history: 歷史相關性序列
            window: 回看窗口（252 天 = 1 年）
        
        返回:
            high_threshold: 進入危機模式的閾值（75 分位）
            low_threshold: 退出危機模式的閾值（25 分位）
        """
        if len(correlation_history) < window:
            window = len(correlation_history)
        
        recent_corr = correlation_history.tail(window)
        
        # 75 分位：75% 的時間相關性低於此值
        high_threshold = recent_corr.quantile(0.75)
        
        # 25 分位：25% 的時間相關性高於此值
        low_threshold = recent_corr.quantile(0.25)
        
        return high_threshold, low_threshold
    
    def calculate_position_size(self, correlation, high_threshold, low_threshold):
        """
        根據相關性計算倉位大小
        
        參數:
            correlation: 當前相關性
            high_threshold: 高閾值
            low_threshold: 低閾值
        
        返回:
            position_size: 倉位大小（0.0 - 1.0）
            market_state: 市場狀態
        """
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
    
    def run_backtest(self, prices, index_prices, window=252):
        """
        運行回測
        
        參數:
            prices: 資產價格數據（用於計算相關性）
            index_prices: 指數價格數據（用於回測）
            window: 回看窗口
        
        返回:
            backtest_df: 回測數據
        """
        print("計算相關性時間序列...")
        correlation_series = self.calculate_correlation(prices)
        
        # 對齊數據
        aligned_data = pd.concat([
            correlation_series,
            index_prices
        ], axis=1).dropna()
        
        aligned_data.columns = ['correlation', 'index_price']
        
        print("計算動態倉位...")
        signals = []
        for i in range(len(aligned_data)):
            # 只在有足夠歷史數據時計算閾值
            if i >= window:
                history = aligned_data['correlation'].iloc[:i]
                high_threshold, low_threshold = self.get_dynamic_threshold(
                    history, 
                    window=window
                )
                
                current_corr = aligned_data['correlation'].iloc[i]
                current_price = aligned_data['index_price'].iloc[i]
                previous_price = aligned_data['index_price'].iloc[i-1] if i > 0 else current_price
                
                # 計算倉位
                position_size, market_state = self.calculate_position_size(
                    current_corr,
                    high_threshold,
                    low_threshold
                )
                
                # 計算收益率
                index_return = (current_price - previous_price) / previous_price
                
                # 計算策略收益率
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
        
        backtest_df = pd.DataFrame(signals)
        backtest_df.set_index('date', inplace=True)
        
        return backtest_df
    
    def calculate_metrics(self, backtest_df):
        """
        計算回測指標
        
        參數:
            backtest_df: 回測數據
        
        返回:
            metrics: 指標字典
        """
        # 計算累積收益率
        backtest_df['index_cumulative'] = (1 + backtest_df['index_return']).cumprod()
        backtest_df['strategy_cumulative'] = (1 + backtest_df['strategy_return']).cumprod()
        
        # 計算年化收益率
        total_days = len(backtest_df)
        total_years = total_days / 252
        
        index_total_return = backtest_df['index_cumulative'].iloc[-1] - 1
        strategy_total_return = backtest_df['strategy_cumulative'].iloc[-1] - 1
        
        index_annual_return = (1 + index_total_return) ** (1 / total_years) - 1
        strategy_annual_return = (1 + strategy_total_return) ** (1 / total_years) - 1
        
        # 計算波動率
        index_volatility = backtest_df['index_return'].std() * np.sqrt(252)
        strategy_volatility = backtest_df['strategy_return'].std() * np.sqrt(252)
        
        # 計算最大回撤
        index_cummax = backtest_df['index_cumulative'].cummax()
        index_drawdown = (backtest_df['index_cumulative'] - index_cummax) / index_cummax
        index_max_drawdown = index_drawdown.min()
        
        strategy_cummax = backtest_df['strategy_cumulative'].cummax()
        strategy_drawdown = (backtest_df['strategy_cumulative'] - strategy_cummax) / strategy_cummax
        strategy_max_drawdown = strategy_drawdown.min()
        
        # 計算夏普比率（假設無風險利率）
        index_sharpe = index_annual_return / index_volatility
        strategy_sharpe = strategy_annual_return / strategy_volatility
        
        # 計算卡爾馬比率
        index_calmar = index_annual_return / abs(index_max_drawdown)
        strategy_calmar = strategy_annual_return / abs(strategy_max_drawdown)
        
        # 計算勝率
        index_win_rate = (backtest_df['index_return'] > 0).mean()
        strategy_win_rate = (backtest_df['strategy_return'] > 0).mean()
        
        # 計算倉位統計
        avg_position_size = backtest_df['position_size'].mean()
        max_position_size = backtest_df['position_size'].max()
        min_position_size = backtest_df['position_size'].min()
        
        # 市場狀態分佈
        state_counts = backtest_df['market_state'].value_counts()
        total_days = len(backtest_df)
        
        # 統計結果
        metrics = {
            'index': {
                'total_return': float(index_total_return),
                'annual_return': float(index_annual_return),
                'volatility': float(index_volatility),
                'max_drawdown': float(index_max_drawdown),
                'sharpe_ratio': float(index_sharpe),
                'calmar_ratio': float(index_calmar),
                'win_rate': float(index_win_rate)
            },
            'strategy': {
                'total_return': float(strategy_total_return),
                'annual_return': float(strategy_annual_return),
                'volatility': float(strategy_volatility),
                'max_drawdown': float(strategy_max_drawdown),
                'sharpe_ratio': float(strategy_sharpe),
                'calmar_ratio': float(strategy_calmar),
                'win_rate': float(strategy_win_rate)
            },
            'position_size': {
                'avg': float(avg_position_size),
                'max': float(max_position_size),
                'min': float(min_position_size)
            },
            'market_state': {
                '正常市場': int(state_counts.get('正常市場', 0)),
                '過渡市場': int(state_counts.get('過渡市場', 0)),
                '危機市場': int(state_counts.get('危機市場', 0))
            },
            'total_days': total_days,
            'total_years': total_years
        }
        
        return metrics, backtest_df
    
    def plot_backtest(self, backtest_df, title="相關性策略時機篩選回測"):
        """
        繪製回測圖表
        
        參數:
            backtest_df: 回測數據
            title: 圖表標題
        """
        fig, axes = plt.subplots(4, 1, figsize=(15, 16))
        
        # 子圖 1：累積收益率對比
        axes[0].plot(backtest_df.index, backtest_df['index_cumulative'], 
                    label='指數（全倉）', linewidth=2, color='blue')
        axes[0].plot(backtest_df.index, backtest_df['strategy_cumulative'], 
                    label='相關性策略（動態倉位）', linewidth=2, color='green')
        
        axes[0].set_title('累積收益率對比', fontsize=14, fontweight='bold')
        axes[0].set_ylabel('累積收益率', fontsize=12)
        axes[0].legend(loc='upper left')
        axes[0].grid(True, alpha=0.3)
        
        # 子圖 2：相關性與動態閾值
        axes[1].plot(backtest_df.index, backtest_df['correlation'], 
                    label='相關性', linewidth=2, color='purple')
        axes[1].plot(backtest_df.index, backtest_df['high_threshold'], 
                    label='高閾值（進入危機）', linewidth=1.5, color='red', linestyle='--')
        axes[1].plot(backtest_df.index, backtest_df['low_threshold'], 
                    label='低閾值（進入正常）', linewidth=1.5, color='green', linestyle='--')
        
        axes[1].set_title('相關性與動態閾值', fontsize=14, fontweight='bold')
        axes[1].set_ylabel('相關係數', fontsize=12)
        axes[1].legend(loc='upper left')
        axes[1].grid(True, alpha=0.3)
        
        # 子圖 3：市場狀態
        state_colors = {
            '正常市場': 'green',
            '過渡市場': 'yellow',
            '危機市場': 'red'
        }
        
        for state, color in state_colors.items():
            state_data = backtest_df[backtest_df['market_state'] == state]
            if not state_data.empty:
                axes[2].scatter(state_data.index, 
                               [1] * len(state_data), 
                               label=state, color=color, s=10, alpha=0.6)
        
        axes[2].set_title('市場狀態識別', fontsize=14, fontweight='bold')
        axes[2].set_ylabel('市場狀態', fontsize=12)
        axes[2].set_yticks([1])
        axes[2].set_yticklabels(['市場狀態'])
        axes[2].legend(loc='upper left')
        axes[2].grid(True, alpha=0.3)
        
        # 子圖 4：動態倉位
        axes[3].fill_between(backtest_df.index, 0, backtest_df['position_size'], 
                           alpha=0.3, color='orange', label='動態倉位')
        axes[3].plot(backtest_df.index, backtest_df['position_size'], 
                    linewidth=2, color='orange')
        axes[3].axhline(y=1.0, color='green', linestyle='--', 
                       linewidth=1, alpha=0.5, label='100% 倉位')
        axes[3].axhline(y=0.5, color='yellow', linestyle='--', 
                       linewidth=1, alpha=0.5, label='50% 倉位')
        axes[3].axhline(y=0.0, color='red', linestyle='--', 
                       linewidth=1, alpha=0.5, label='0% 倉位')
        
        axes[3].set_title('動態倉位', fontsize=14, fontweight='bold')
        axes[3].set_ylabel('倉位大小', fontsize=12)
        axes[3].set_xlabel('日期', fontsize=12)
        axes[3].set_ylim([-0.1, 1.1])
        axes[3].legend(loc='upper left')
        axes[3].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('correlation_timing_backtest.png', dpi=150, bbox_inches='tight')
        print(f"\n📊 圖表已保存: correlation_timing_backtest.png")
        plt.close()
    
    def print_metrics(self, metrics):
        """
        打印回測指標
        
        參數:
            metrics: 指標字典
        """
        print("="*80)
        print("📊 相關性策略時機篩選回測結果")
        print("="*80)
        
        # 基本統計
        print(f"\n📈 基本統計:")
        print(f"  - 測試期間: {metrics['total_days']} 天 ({metrics['total_years']:.2f} 年)")
        
        # 收益率對比
        print(f"\n💰 收益率對比:")
        print(f"  指數（全倉）:")
        print(f"    - 總收益率: {metrics['index']['total_return']:.2%}")
        print(f"    - 年化收益率: {metrics['index']['annual_return']:.2%}")
        print(f"  相關性策略（動態倉位）:")
        print(f"    - 總收益率: {metrics['strategy']['total_return']:.2%}")
        print(f"    - 年化收益率: {metrics['strategy']['annual_return']:.2%}")
        
        # 超額收益
        excess_return = metrics['strategy']['total_return'] - metrics['index']['total_return']
        excess_annual = metrics['strategy']['annual_return'] - metrics['index']['annual_return']
        print(f"  超額收益:")
        print(f"    - 總超額收益: {excess_return:.2%}")
        print(f"    - 年化超額收益: {excess_annual:.2%}")
        
        # 風險指標
        print(f"\n⚠️  風險指標:")
        print(f"  指數（全倉）:")
        print(f"    - 波動率: {metrics['index']['volatility']:.2%}")
        print(f"    - 最大回撤: {metrics['index']['max_drawdown']:.2%}")
        print(f"    - 夏普比率: {metrics['index']['sharpe_ratio']:.2f}")
        print(f"    - 卡爾馬比率: {metrics['index']['calmar_ratio']:.2f}")
        print(f"  相關性策略（動態倉位）:")
        print(f"    - 波動率: {metrics['strategy']['volatility']:.2%}")
        print(f"    - 最大回撤: {metrics['strategy']['max_drawdown']:.2%}")
        print(f"    - 夏普比率: {metrics['strategy']['sharpe_ratio']:.2f}")
        print(f"    - 卡爾馬比率: {metrics['strategy']['calmar_ratio']:.2f}")
        
        # 風險調整後收益
        sharpe_improvement = metrics['strategy']['sharpe_ratio'] - metrics['index']['sharpe_ratio']
        calmar_improvement = metrics['strategy']['calmar_ratio'] - metrics['index']['calmar_ratio']
        print(f"  風險調整後收益改善:")
        print(f"    - 夏普比率提升: {sharpe_improvement:+.2f}")
        print(f"    - 卡爾馬比率提升: {calmar_improvement:+.2f}")
        
        # 勝率
        print(f"\n🎯 勝率:")
        print(f"  指數（全倉）: {metrics['index']['win_rate']:.2%}")
        print(f"  相關性策略（動態倉位）: {metrics['strategy']['win_rate']:.2%}")
        
        # 倉位統計
        print(f"\n📊 倉位統計:")
        print(f"  - 平均倉位: {metrics['position_size']['avg']:.2%}")
        print(f"  - 最大倉位: {metrics['position_size']['max']:.2%}")
        print(f"  - 最小倉位: {metrics['position_size']['min']:.2%}")
        
        # 市場狀態分佈
        print(f"\n📍 市場狀態分佈:")
        for state, count in metrics['market_state'].items():
            percentage = (count / metrics['total_days']) * 100
            color = "🟢" if state == "正常市場" else ("🟡" if state == "過渡市場" else "🔴")
            print(f"  - {color} {state}: {count} 天 ({percentage:.1f}%)")
        
        # 結論
        print(f"\n💡 結論:")
        if excess_return > 0:
            print(f"  ✅ 相關性策略時機篩選有效！")
            print(f"  ✅ 總超額收益: {excess_return:.2%}")
            print(f"  ✅ 年化超額收益: {excess_annual:.2%}")
            if sharpe_improvement > 0:
                print(f"  ✅ 夏普比率提升: {sharpe_improvement:+.2f}")
            if calmar_improvement > 0:
                print(f"  ✅ 卡爾馬比率提升: {calmar_improvement:+.2f}")
        else:
            print(f"  ❌ 相關性策略時機篩選無效")
            print(f"  ❌ 總超額收益: {excess_return:.2%}")
            print(f"  ❌ 年化超額收益: {excess_annual:.2%}")
        
        if metrics['strategy']['max_drawdown'] > metrics['index']['max_drawdown']:
            drawdown_improvement = metrics['strategy']['max_drawdown'] - metrics['index']['max_drawdown']
            print(f"  ⚠️  最大回撤反而更差: {drawdown_improvement:+.2%}")
        else:
            drawdown_improvement = metrics['strategy']['max_drawdown'] - metrics['index']['max_drawdown']
            print(f"  ✅ 最大回撤改善: {drawdown_improvement:+.2%}")


def main():
    """主函數"""
    print("="*80)
    print("🚀 相關性策略時機篩選回測")
    print("="*80)
    
    # 創建回測實例
    backtest = CorrelationTimingBacktest()
    
    # 測試資產（用於計算相關性）
    tickers = ['SPY', 'QQQ', 'IWM', 'XLI', 'XLV', 'XLK', 'XLF', 'XLE']
    
    print(f"\n下載 {len(tickers)} 個資產的數據（用於計算相關性）...")
    prices = yf.download(tickers, period='10y', progress=False, auto_adjust=True)['Close']
    
    # 下載指數數據（用於回測）
    print("下載 SPY 指數數據（用於回測）...")
    index_prices = yf.download('SPY', period='10y', progress=False, auto_adjust=True)['Close']
    
    # 運行回測
    print("\n運行回測...")
    backtest_df = backtest.run_backtest(prices, index_prices, window=252)
    
    # 計算指標
    print("計算回測指標...")
    metrics, backtest_df = backtest.calculate_metrics(backtest_df)
    
    # 打印指標
    backtest.print_metrics(metrics)
    
    # 繪製圖表
    print("\n繪製圖表...")
    backtest.plot_backtest(backtest_df)
    
    # 保存結果
    backtest_df.to_csv('correlation_timing_backtest_data.csv')
    print(f"\n💾 回測數據已保存: correlation_timing_backtest_data.csv")
    
    print("\n✅ 回測完成！")


if __name__ == '__main__':
    main()
