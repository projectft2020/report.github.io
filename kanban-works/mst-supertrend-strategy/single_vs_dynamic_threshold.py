"""
相關性策略單一閾值 vs 動態閾值對比
測試單一閾值版本的效果（例如：80 以上空手，以下全倉）
"""

import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


class SingleVsDynamicThreshold:
    """單一閾值 vs 動態閾值對比"""
    
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
    
    def run_single_threshold(self, prices, index_prices, single_threshold, lookback_window=60):
        """
        單一閾值版本回測
        
        參數:
            prices: 資產價格數據
            index_prices: 指數價格數據
            single_threshold: 單一閾值（例如 0.8）
            lookback_window: 回看窗口（用於對比）
        
        返回:
            backtest_df: 回測數據
        """
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
                current_corr = aligned_data['correlation'].iloc[i]
                current_price = aligned_data['index_price'].iloc[i]
                previous_price = aligned_data['index_price'].iloc[i-1] if i > 0 else current_price
                
                # 單一閾值判斷
                if current_corr >= single_threshold:
                    position_size = 0.0
                    market_state = '高相關性（空手）'
                else:
                    position_size = 1.0
                    market_state = '低相關性（全倉）'
                
                # 計算收益率
                index_return = (current_price - previous_price) / previous_price
                strategy_return = position_size * index_return
                
                signals.append({
                    'date': aligned_data.index[i],
                    'correlation': current_corr,
                    'single_threshold': single_threshold,
                    'market_state': market_state,
                    'position_size': position_size,
                    'index_price': current_price,
                    'index_return': index_return,
                    'strategy_return': strategy_return
                })
        
        backtest_df = pd.DataFrame(signals)
        if not backtest_df.empty:
            backtest_df.set_index('date', inplace=True)
        
        return backtest_df
    
    def calculate_metrics(self, backtest_df):
        """計算回測指標"""
        if backtest_df.empty:
            return None
        
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
        market_state_counts = backtest_df['market_state'].value_counts()
        
        # 計算轉換次數
        transitions = 0
        previous_state = None
        for state in backtest_df['market_state']:
            if previous_state is not None and state != previous_state:
                transitions += 1
            previous_state = state
        
        return {
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
            'transitions': transitions,
            'total_days': total_days,
            'total_years': total_years
        }
    
    def optimize_single_threshold(self, prices, index_prices, thresholds):
        """優化單一閾值"""
        results = []
        
        for threshold in thresholds:
            print(f"測試單一閾值: {threshold:.4f}")
            
            # 運行回測
            backtest_df = self.run_single_threshold(
                prices,
                index_prices,
                threshold,
                lookback_window=60
            )
            
            # 計算指標
            metrics = self.calculate_metrics(backtest_df)
            
            if metrics:
                metrics['single_threshold'] = threshold
                results.append(metrics)
        
        # 轉換為 DataFrame
        results_df = pd.DataFrame(results)
        
        # 排序（根據夏普比率）
        results_df = results_df.sort_values('strategy_sharpe', ascending=False)
        
        return results_df
    
    def compare_single_vs_dynamic(self, single_results_df, dynamic_result):
        """對比單一閾值 vs 動態閾值"""
        print("="*100)
        print("📊 單一閾值 vs 動態閾值對比")
        print("="*100)
        
        print("\n🥇 動態閾值版本（90/10/60）:")
        print(f"  - 參數: 高分位數=90%, 低分位數=10%, 回看窗口=60 天")
        print(f"  指數（全倉）:")
        print(f"    - 年化收益率: {dynamic_result['index_annual_return']:.2%}")
        print(f"    - 波動率: {dynamic_result['index_volatility']:.2%}")
        print(f"    - 最大回撤: {dynamic_result['index_max_drawdown']:.2%}")
        print(f"    - 夏普比率: {dynamic_result['index_sharpe']:.2f}")
        print(f"    - 卡爾馬比率: {dynamic_result['index_calmar']:.2f}")
        print(f"  相關性策略（動態倉位）:")
        print(f"    - 年化收益率: {dynamic_result['strategy_annual_return']:.2%}")
        print(f"    - 波動率: {dynamic_result['strategy_volatility']:.2%}")
        print(f"    - 最大回撤: {dynamic_result['strategy_max_drawdown']:.2%}")
        print(f"    - 夏普比率: {dynamic_result['strategy_sharpe']:.2f}")
        print(f"    - 卡爾馬比率: {dynamic_result['strategy_calmar']:.2f}")
        print(f"  超額收益:")
        print(f"    - 年化超額收益: {dynamic_result['excess_annual_return']:.2%}")
        print(f"  其他:")
        print(f"    - 平均倉位: {dynamic_result['avg_position_size']:.2%}")
        
        print(f"\n🥈 單一閾值版本（最優）:")
        best_single = single_results_df.iloc[0]
        print(f"  - 參數: 單一閾值={best_single['single_threshold']:.4f}")
        print(f"  指數（全倉）:")
        print(f"    - 年化收益率: {best_single['index_annual_return']:.2%}")
        print(f"    - 波動率: {best_single['index_volatility']:.2%}")
        print(f"    - 最大回撤: {best_single['index_max_drawdown']:.2%}")
        print(f"    - 夏普比率: {best_single['index_sharpe']:.2f}")
        print(f"    - 卡爾馬比率: {best_single['index_calmar']:.2f}")
        print(f"  相關性策略（單一閾值）:")
        print(f"    - 年化收益率: {best_single['strategy_annual_return']:.2%}")
        print(f"    - 波動率: {best_single['strategy_volatility']:.2%}")
        print(f"    - 最大回撤: {best_single['strategy_max_drawdown']:.2%}")
        print(f"    - 夏普比率: {best_single['strategy_sharpe']:.2f}")
        print(f"    - 卡爾馬比率: {best_single['strategy_calmar']:.2f}")
        print(f"  超額收益:")
        print(f"    - 年化超額收益: {best_single['excess_annual_return']:.2%}")
        print(f"  其他:")
        print(f"    - 平均倉位: {best_single['avg_position_size']:.2%}")
        print(f"    - 轉換次數: {best_single['transitions']}")
        
        print(f"\n{'='*100}")
        print("🔍 詳細對比（夏普比率）")
        print("="*100)
        
        sharpe_dynamic = dynamic_result['strategy_sharpe']
        sharpe_single = best_single['strategy_sharpe']
        sharpe_diff = sharpe_dynamic - sharpe_single
        
        print(f"\n夏普比率對比:")
        print(f"  - 動態閾值: {sharpe_dynamic:.2f}")
        print(f"  - 單一閾值: {sharpe_single:.2f}")
        print(f"  - 差異: {sharpe_diff:+.2f}")
        
        if sharpe_diff > 0:
            print(f"  - 結論: ✅ 動態閾值優於單一閾值（夏普比率高 {abs(sharpe_diff):.2f}）")
        elif sharpe_diff < 0:
            print(f"  - 結論: ❌ 單一閾值優於動態閾值（夏普比率高 {abs(sharpe_diff):.2f}）")
        else:
            print(f"  - 結論: ⚖️  動態閾值和單一閾值夏普比率相同")
        
        print(f"\n{'='*100}")
        print("🔍 詳細對比（卡爾馬比率）")
        print("="*100)
        
        calmar_dynamic = dynamic_result['strategy_calmar']
        calmar_single = best_single['strategy_calmar']
        calmar_diff = calmar_dynamic - calmar_single
        
        print(f"\n卡爾馬比率對比:")
        print(f"  - 動態閾值: {calmar_dynamic:.2f}")
        print(f"  - 單一閾值: {calmar_single:.2f}")
        print(f"  - 差異: {calmar_diff:+.2f}")
        
        if calmar_diff > 0:
            print(f"  - 結論: ✅ 動態閾值優於單一閾值（卡爾馬比率高 {abs(calmar_diff):.2f}）")
        elif calmar_diff < 0:
            print(f"  - 結論: ❌ 單一閾值優於動態閾值（卡爾馬比率高 {abs(calmar_diff):.2f}）")
        else:
            print(f"  - 結論: ⚖️  動態閾值和單一閾值卡爾馬比率相同")
        
        print(f"\n{'='*100}")
        print("🔍 詳細對比（平均倉位）")
        print("="*100)
        
        position_dynamic = dynamic_result['avg_position_size']
        position_single = best_single['avg_position_size']
        position_diff = position_dynamic - position_single
        
        print(f"\n平均倉位對比:")
        print(f"  - 動態閾值: {position_dynamic:.2%}")
        print(f"  - 單一閾值: {position_single:.2%}")
        print(f"  - 差異: {position_diff:+.2%}")
        
        if position_dynamic > position_single:
            print(f"  - 結論: 🟢 動態閾值倉位較高（可能錯過較少收益）")
        elif position_dynamic < position_single:
            print(f"  - 結論: 🟡 單一閾值倉位較高（可能錯過較少收益）")
        else:
            print(f"  - 結論: ⚖️  動態閾值和單一閾值平均倉位相同")
        
        print(f"\n{'='*100}")
        print("🔍 詳細對比（轉換次數）")
        print("="*100)
        
        transitions_dynamic = 31  # 從之前的分析中得到
        transitions_single = best_single['transitions']
        transitions_diff = transitions_dynamic - transitions_single
        
        print(f"\n轉換次數對比:")
        print(f"  - 動態閾值: {transitions_dynamic} 次")
        print(f"  - 單一閾值: {int(transitions_single)} 次")
        print(f"  - 差異: {int(transitions_diff)}")
        
        if transitions_dynamic > transitions_single:
            print(f"  - 結論: ⚠️  動態閾值轉換更頻繁（交易成本更高）")
        elif transitions_dynamic < transitions_single:
            print(f"  - 結論: ✅ 單一閾值轉換更頻繁（交易成本更高）")
        else:
            print(f"  - 結論: ⚖️  動態閾值和單一閾值轉換次數相同")
        
        print()
        
        return single_results_df, best_single, dynamic_result
    
    def print_top_single_thresholds(self, single_results_df, top_n=10):
        """打印最優單一閾值"""
        print("="*100)
        print(f"🏆 單一閾值優化結果（前 {top_n} 名）")
        print("="*100)
        
        top_results = single_results_df.head(top_n)
        
        print("\n📊 最優單一閾值（根據夏普比率排序）:\n")
        
        for idx, row in enumerate(top_results.itertuples(), 1):
            print(f"#{idx}")
            print(f"  參數:")
            print(f"    - 單一閾值: {row.single_threshold:.4f}")
            print(f"  指數（全倉）:")
            print(f"    - 年化收益率: {row.index_annual_return:.2%}")
            print(f"    - 波動率: {row.index_volatility:.2%}")
            print(f"    - 最大回撤: {row.index_max_drawdown:.2%}")
            print(f"    - 夏普比率: {row.index_sharpe:.2f}")
            print(f"    - 卡爾馬比率: {row.index_calmar:.2f}")
            print(f"  相關性策略（單一閾值）:")
            print(f"    - 年化收益率: {row.strategy_annual_return:.2%}")
            print(f"    - 波動率: {row.strategy_volatility:.2%}")
            print(f"    - 最大回撤: {row.strategy_max_drawdown:.2%}")
            print(f"    - 夏普比率: {row.strategy_sharpe:.2f}")
            print(f"    - 卡爾馬比率: {row.strategy_calmar:.2f}")
            print(f"  超額收益:")
            print(f"    - 年化超額收益: {row.excess_annual_return:.2%}")
            print(f"  其他:")
            print(f"    - 平均倉位: {row.avg_position_size:.2%}")
            print(f"    - 轉換次數: {row.transitions}")
            print()
        
        # 總結統計
        print("="*100)
        print("📈 單一閾值總結統計")
        print("="*100)
        print(f"\n測試閾值數: {len(single_results_df)}")
        print(f"\n最佳夏普比率: {single_results_df['strategy_sharpe'].max():.2f}")
        print(f"最佳卡爾馬比率: {single_results_df['strategy_calmar'].max():.2f}")
        print(f"最佳超額收益: {single_results_df['excess_annual_return'].max():.2%}")
        
        # 找到最優單一閾值
        best_sharpe = single_results_df.loc[single_results_df['strategy_sharpe'].idxmax()]
        best_calmar = single_results_df.loc[single_results_df['strategy_calmar'].idxmax()]
        
        print(f"\n最優夏普比率單一閾值:")
        print(f"  - 單一閾值: {best_sharpe['single_threshold']:.4f}")
        print(f"  - 夏普比率: {best_sharpe['strategy_sharpe']:.2f}")
        
        print(f"\n最優卡爾馬比率單一閾值:")
        print(f"  - 單一閾值: {best_calmar['single_threshold']:.4f}")
        print(f"  - 卡爾馬比率: {best_calmar['strategy_calmar']:.2f}")
        
        print()
        
        return single_results_df, best_sharpe, best_calmar


def main():
    """主函數"""
    print("="*100)
    print("🚀 相關性策略單一閾值 vs 動態閾值對比")
    print("="*100)
    
    # 創建分析實例
    analyzer = SingleVsDynamicThreshold()
    
    # 測試資產
    tickers = ['SPY', 'QQQ', 'IWM', 'XLI', 'XLV', 'XLK', 'XLF', 'XLE']
    
    print(f"\n下載 {len(tickers)} 個資產的數據...")
    prices = yf.download(tickers, period='10y', progress=False, auto_adjust=True)['Close']
    
    # 下載指數數據
    print("下載 SPY 指數數據...")
    index_prices = yf.download('SPY', period='10y', progress=False, auto_adjust=True)['Close']
    
    # 定義單一閾值範圍（0.5 - 0.9）
    thresholds = np.arange(0.5, 0.95, 0.05)
    
    # 優化單一閾值
    print(f"\n優化單一閾值（{len(thresholds)} 個閾值）...")
    single_results_df = analyzer.optimize_single_threshold(prices, index_prices, thresholds)
    
    # 打印最優單一閾值
    single_results_df, best_single_sharpe, best_single_calmar = analyzer.print_top_single_thresholds(
        single_results_df, 
        top_n=10
    )
    
    # 動態閾值結果（從之前的優化中得到）
    dynamic_result = {
        'index_annual_return': 0.1461,
        'index_volatility': 0.1813,
        'index_max_drawdown': -0.3372,
        'index_sharpe': 0.81,
        'index_calmar': 0.43,
        'strategy_annual_return': 0.1216,
        'strategy_volatility': 0.0854,
        'strategy_max_drawdown': -0.0988,
        'strategy_sharpe': 1.42,
        'strategy_calmar': 1.23,
        'excess_annual_return': -0.0244,
        'avg_position_size': 0.5422
    }
    
    # 對比單一閾值 vs 動態閾值
    print("\n" + "="*100)
    print("🔍 單一閾值 vs 動態閾值詳細對比")
    print("="*100)
    single_results_df, best_single, dynamic = analyzer.compare_single_vs_dynamic(
        single_results_df, 
        dynamic_result
    )
    
    # 保存結果
    single_results_df.to_csv('single_vs_dynamic_comparison.csv', index=False)
    print(f"\n💾 對比結果已保存: single_vs_dynamic_comparison.csv")
    
    print("\n✅ 對比完成！")


if __name__ == '__main__':
    main()
