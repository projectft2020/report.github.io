"""
相關性策略參數優化
系統性測試不同的分位數和回看窗口組合
"""

import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime
import itertools
import warnings
warnings.filterwarnings('ignore')


class CorrelationStrategyOptimizer:
    """相關性策略參數優化"""
    
    def __init__(self):
        self.results = []
    
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
    
    def get_dynamic_threshold(self, correlation_history, high_percentile, low_percentile, window=252):
        """基於歷史分位數計算動態閾值"""
        if len(correlation_history) < window:
            window = len(correlation_history)
        
        recent_corr = correlation_history.tail(window)
        
        # 動態分位數
        high_threshold = recent_corr.quantile(high_percentile / 100)
        low_threshold = recent_corr.quantile(low_percentile / 100)
        
        return high_threshold, low_threshold
    
    def calculate_position_size(self, correlation, high_threshold, low_threshold):
        """根據相關性計算倉位大小"""
        if correlation < low_threshold:
            return 1.0, '正常市場'
        elif correlation > high_threshold:
            return 0.0, '危機市場'
        else:
            return 0.5, '過渡市場'
    
    def run_backtest(self, prices, index_prices, high_percentile, low_percentile, lookback_window):
        """運行回測"""
        correlation_series = self.calculate_correlation(prices)
        
        # 對齊數據
        aligned_data = pd.concat([
            correlation_series,
            index_prices
        ], axis=1).dropna()
        
        aligned_data.columns = ['correlation', 'index_price']
        
        signals = []
        for i in range(len(aligned_data)):
            if i >= lookback_window:
                history = aligned_data['correlation'].iloc[:i]
                high_threshold, low_threshold = self.get_dynamic_threshold(
                    history,
                    high_percentile,
                    low_percentile,
                    window=lookback_window
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
                strategy_return = position_size * index_return
                
                signals.append({
                    'date': aligned_data.index[i],
                    'correlation': current_corr,
                    'high_threshold': high_threshold,
                    'low_threshold': low_threshold,
                    'market_state': market_state,
                    'position_size': position_size,
                    'index_return': index_return,
                    'strategy_return': strategy_return,
                    'high_percentile': high_percentile,
                    'low_percentile': low_percentile,
                    'lookback_window': lookback_window
                })
        
        backtest_df = pd.DataFrame(signals)
        if not backtest_df.empty:
            backtest_df.set_index('date', inplace=True)
        
        return backtest_df
    
    def calculate_metrics(self, backtest_df):
        """計算回測指標"""
        if backtest_df.empty:
            return None
        
        # 獲取參數（從第一行）
        high_percentile = backtest_df['high_percentile'].iloc[0]
        low_percentile = backtest_df['low_percentile'].iloc[0]
        lookback_window = backtest_df['lookback_window'].iloc[0]
        
        # 計算累積收益率
        backtest_df['index_cumulative'] = (1 + backtest_df['index_return']).cumprod()
        backtest_df['strategy_cumulative'] = (1 + backtest_df['strategy_return']).cumprod()
        
        # 計算年化收益率
        total_days = len(backtest_df)
        total_years = total_days / 252
        
        index_total_return = backtest_df['index_cumulative'].iloc[-1] - 1
        strategy_total_return = backtest_df['strategy_cumulative'].iloc[-1] - 1
        
        index_annual_return = (1 + index_total_return) ** (1 / total_years) - 1 if total_years > 0 else 0
        strategy_annual_return = (1 + strategy_total_return) ** (1 / total_years) - 1 if total_years > 0 else 0
        
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
        
        # 計算夏普比率
        index_sharpe = index_annual_return / index_volatility if index_volatility > 0 else 0
        strategy_sharpe = strategy_annual_return / strategy_volatility if strategy_volatility > 0 else 0
        
        # 計算卡爾馬比率
        index_calmar = index_annual_return / abs(index_max_drawdown) if abs(index_max_drawdown) > 0 else 0
        strategy_calmar = strategy_annual_return / abs(strategy_max_drawdown) if abs(strategy_max_drawdown) > 0 else 0
        
        # 計算超額收益
        excess_total_return = strategy_total_return - index_total_return
        excess_annual_return = strategy_annual_return - index_annual_return
        
        # 計算倉位統計
        avg_position_size = backtest_df['position_size'].mean()
        
        # 市場狀態分佈
        state_counts = backtest_df['market_state'].value_counts()
        
        return {
            'high_percentile': high_percentile,
            'low_percentile': low_percentile,
            'lookback_window': lookback_window,
            'index_total_return': float(index_total_return),
            'index_annual_return': float(index_annual_return),
            'index_volatility': float(index_volatility),
            'index_max_drawdown': float(index_max_drawdown),
            'index_sharpe': float(index_sharpe),
            'index_calmar': float(index_calmar),
            'strategy_total_return': float(strategy_total_return),
            'strategy_annual_return': float(strategy_annual_return),
            'strategy_volatility': float(strategy_volatility),
            'strategy_max_drawdown': float(strategy_max_drawdown),
            'strategy_sharpe': float(strategy_sharpe),
            'strategy_calmar': float(strategy_calmar),
            'excess_total_return': float(excess_total_return),
            'excess_annual_return': float(excess_annual_return),
            'avg_position_size': float(avg_position_size),
            'total_days': total_days
        }
    
    def optimize(self, prices, index_prices, high_percentiles, low_percentiles, lookback_windows):
        """執行參數優化"""
        total_combinations = len(high_percentiles) * len(low_percentiles) * len(lookback_windows)
        current = 0
        
        print(f"開始參數優化...")
        print(f"  - 高分位數: {high_percentiles}")
        print(f"  - 低分位數: {low_percentiles}")
        print(f"  - 回看窗口: {lookback_windows}")
        print(f"  - 總組合數: {total_combinations}")
        print()
        
        results = []
        for high_percentile in high_percentiles:
            for low_percentile in low_percentiles:
                for lookback_window in lookback_windows:
                    current += 1
                    print(f"[{current}/{total_combinations}] 測試: 高分位數={high_percentile}%, 低分位數={low_percentile}%, 回看窗口={lookback_window}天")
                    
                    # 運行回測
                    backtest_df = self.run_backtest(
                        prices,
                        index_prices,
                        high_percentile,
                        low_percentile,
                        lookback_window
                    )
                    
                    # 計算指標
                    metrics = self.calculate_metrics(backtest_df)
                    
                    if metrics:
                        results.append(metrics)
        
        # 轉換為 DataFrame
        results_df = pd.DataFrame(results)
        
        # 排序（根據夏普比率）
        results_df = results_df.sort_values('strategy_sharpe', ascending=False)
        
        return results_df
    
    def print_top_results(self, results_df, top_n=10):
        """打印最優結果"""
        print("="*100)
        print("🏆 參數優化結果（前 {top_n} 名）".format(top_n=top_n))
        print("="*100)
        
        top_results = results_df.head(top_n)
        
        print("\n📊 最優參數組合（根據夏普比率排序）:\n")
        
        for idx, row in enumerate(top_results.itertuples(), 1):
            print(f"#{idx}")
            print(f"  參數:")
            print(f"    - 高分位數: {row.high_percentile}%")
            print(f"    - 低分位數: {row.low_percentile}%")
            print(f"    - 回看窗口: {row.lookback_window} 天")
            print(f"  指數（全倉）:")
            print(f"    - 年化收益率: {row.index_annual_return:.2%}")
            print(f"    - 波動率: {row.index_volatility:.2%}")
            print(f"    - 最大回撤: {row.index_max_drawdown:.2%}")
            print(f"    - 夏普比率: {row.index_sharpe:.2f}")
            print(f"    - 卡爾馬比率: {row.index_calmar:.2f}")
            print(f"  相關性策略（動態倉位）:")
            print(f"    - 年化收益率: {row.strategy_annual_return:.2%}")
            print(f"    - 波動率: {row.strategy_volatility:.2%}")
            print(f"    - 最大回撤: {row.strategy_max_drawdown:.2%}")
            print(f"    - 夏普比率: {row.strategy_sharpe:.2f}")
            print(f"    - 卡爾馬比率: {row.strategy_calmar:.2f}")
            print(f"  超額收益:")
            print(f"    - 總超額收益: {row.excess_total_return:.2%}")
            print(f"    - 年化超額收益: {row.excess_annual_return:.2%}")
            print(f"  其他:")
            print(f"    - 平均倉位: {row.avg_position_size:.2%}")
            print()
        
        # 總結統計
        print("="*100)
        print("📈 總結統計")
        print("="*100)
        print(f"\n測試組合數: {len(results_df)}")
        print(f"\n最佳夏普比率: {results_df['strategy_sharpe'].max():.2f}")
        print(f"最佳卡爾馬比率: {results_df['strategy_calmar'].max():.2f}")
        print(f"最佳超額收益: {results_df['excess_annual_return'].max():.2%}")
        
        # 找到最優組合
        best_sharpe = results_df.loc[results_df['strategy_sharpe'].idxmax()]
        best_calmar = results_df.loc[results_df['strategy_calmar'].idxmax()]
        
        print(f"\n最優夏普比率組合:")
        print(f"  - 高分位數: {best_sharpe['high_percentile']}%")
        print(f"  - 低分位數: {best_sharpe['low_percentile']}%")
        print(f"  - 回看窗口: {best_sharpe['lookback_window']} 天")
        print(f"  - 夏普比率: {best_sharpe['strategy_sharpe']:.2f}")
        
        print(f"\n最優卡爾馬比率組合:")
        print(f"  - 高分位數: {best_calmar['high_percentile']}%")
        print(f"  - 低分位數: {best_calmar['low_percentile']}%")
        print(f"  - 回看窗口: {best_calmar['lookback_window']} 天")
        print(f"  - 卡爾馬比率: {best_calmar['strategy_calmar']:.2f}")
        
        print()
        
        return results_df, best_sharpe, best_calmar


def main():
    """主函數"""
    print("="*100)
    print("🚀 相關性策略參數優化")
    print("="*100)
    
    # 創建優化實例
    optimizer = CorrelationStrategyOptimizer()
    
    # 測試資產
    tickers = ['SPY', 'QQQ', 'IWM', 'XLI', 'XLV', 'XLK', 'XLF', 'XLE']
    
    print(f"\n下載 {len(tickers)} 個資產的數據...")
    prices = yf.download(tickers, period='10y', progress=False, auto_adjust=True)['Close']
    
    # 下載指數數據
    print("下載 SPY 指數數據...")
    index_prices = yf.download('SPY', period='10y', progress=False, auto_adjust=True)['Close']
    
    # 定義參數空間
    high_percentiles = [70, 80, 90]  # 高分位數
    low_percentiles = [10, 20, 30]    # 低分位數
    lookback_windows = [60, 120, 252]  # 回看窗口
    
    # 執行優化
    results_df = optimizer.optimize(
        prices,
        index_prices,
        high_percentiles,
        low_percentiles,
        lookback_windows
    )
    
    # 打印最優結果
    results_df, best_sharpe, best_calmar = optimizer.print_top_results(results_df, top_n=10)
    
    # 保存結果
    results_df.to_csv('correlation_optimization_results.csv', index=False)
    print(f"\n💾 優化結果已保存: correlation_optimization_results.csv")
    
    print("\n✅ 優化完成！")


if __name__ == '__main__':
    main()
