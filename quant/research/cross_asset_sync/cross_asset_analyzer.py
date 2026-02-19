#!/usr/bin/env python3
"""
跨資產同步極端事件分析器
Author: Charlie
Date: 2026-02-17
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from data_loader import DataLoader
from correlation_analysis import CorrelationAnalyzer
from breakdown_detector import BreakdownDetector
from regime_analysis import RegimeAnalyzer
from trade_signal_generator import TradeSignalGenerator
from backtest_engine import BacktestEngine

class CrossAssetAnalyzer:
    """跨資產同步分析器"""

    def __init__(self, assets=['NQ', 'GC', 'DX'], windows=[20, 50, 200]):
        """
        初始化分析器

        Args:
            assets: 資產代碼列表
            windows: 移動平均線窗口期
        """
        self.assets = assets
        self.windows = windows
        self.data = {}
        self.results = {}

    def load_data(self):
        """加載數據"""
        print("加載數據...")
        loader = DataLoader()

        for asset in self.assets:
            print(f"  - 載入 {asset} 數據")
            self.data[asset] = loader.load_data(asset, period='daily')

        print(f"✓ 完成載入 {len(self.assets)} 個資產\n")

    def calculate_returns(self):
        """計算回報率"""
        print("計算回報率...")
        returns = {}

        for asset, prices in self.data.items():
            returns[asset] = prices.pct_change().dropna()

        self.returns = returns
        print(f"✓ 完成 {len(returns)} 個資產的回報率計算\n")

        return returns

    def analyze_correlations(self):
        """分析相關性"""
        print("分析相關性...")

        analyzer = CorrelationAnalyzer()
        corr_matrix = analyzer.analyze(self.returns, window=60)

        self.corr_matrix = corr_matrix
        print("✓ 相關性分析完成\n")

        return corr_matrix

    def analyze_breakdowns(self):
        """分析同步破位"""
        print("分析同步破位...")

        detector = BreakdownDetector(windows=self.windows)
        breakdowns = detector.analyze(self.data)

        self.breakdowns = breakdowns
        print("✓ 同步破位分析完成\n")

        return breakdowns

    def analyze_regimes(self):
        """分析波動 regime"""
        print("分析波動 regime...")

        regime_analyzer = RegimeAnalyzer()
        regime_results = regime_analyzer.analyze(self.data)

        self.regime_results = regime_results
        print("✓ 波動 regime 分析完成\n")

        return regime_results

    def generate_signals(self):
        """生成交易信號"""
        print("生成交易信號...")

        signal_gen = TradeSignalGenerator(
            breakdowns=self.breakdowns,
            returns=self.returns
        )
        signals = signal_gen.generate_all_signals()

        self.signals = signals
        print("✓ 交易信號生成完成\n")

        return signals

    def backtest(self):
        """回測策略"""
        print("開始回測...")

        engine = BacktestEngine(self.signals, self.data)
        results = engine.run()

        self.backtest_results = results
        print("✓ 回測完成\n")

        return results

    def save_results(self, results, filename='cross_asset_results.csv'):
        """儲存結果"""
        print(f"儲存結果到 {filename}...")
        results.to_csv(filename, encoding='utf-8-sig')
        print(f"✓ 結果已儲存\n")

    def visualize(self):
        """可視化結果"""
        print("生成可視化圖表...")

        # 1. 相關性矩陣熱圖
        self._plot_correlation_heatmap()

        # 2. 同步破位時間軸
        self._plot_breakdown_timeline()

        # 3. 回報曲線
        self._plot_returns()

        # 4. 策略績效
        self._plot_performance()

        print("✓ 可視化完成\n")

    def _plot_correlation_heatmap(self):
        """繪製相關性熱圖"""
        fig, ax = plt.subplots(figsize=(10, 8))

        # 計算平均相關係數
        avg_corr = self.corr_matrix.mean()

        im = ax.imshow(avg_corr, cmap='coolwarm', vmin=-1, vmax=1)

        # 設定標籤
        ax.set_xticks(range(len(self.assets)))
        ax.set_yticks(range(len(self.assets)))
        ax.set_xticklabels(self.assets)
        ax.set_yticklabels(self.assets)

        # 加上相關係數值
        for i in range(len(self.assets)):
            for j in range(len(self.assets)):
                text = ax.text(j, i, f'{avg_corr.iloc[i, j]:.2f}',
                             ha="center", va="center", color="black")

        ax.set_title('資產相關性矩陣', fontsize=14)
        fig.colorbar(im, ax=ax, label='相關係數')

        plt.tight_layout()
        plt.savefig('correlation_heatmap.png', dpi=150)
        plt.close()

    def _plot_breakdown_timeline(self):
        """繪製同步破位時間軸"""
        fig, ax = plt.subplots(figsize=(14, 6))

        # 為每個資產標記破位時間
        for asset, breakdowns in self.breakdowns.items():
            if len(breakdowns) > 0:
                ax.scatter(breakdowns.index, [1]*len(breakdowns),
                          color='red', alpha=0.5, label=asset if asset == self.assets[0] else "")

        ax.set_yticks([1])
        ax.set_yticklabels(['同步破位'])
        ax.set_title('同步破位時間軸', fontsize=14)
        ax.set_xlabel('日期', fontsize=12)
        ax.grid(True, alpha=0.3)

        # 只顯示前 10 個破位
        if len(self.breakdowns) > 0:
            ax.set_xlim(left=self.breakdowns.index.min(),
                       right=self.breakdowns.index.max())

        plt.tight_layout()
        plt.savefig('breakdown_timeline.png', dpi=150)
        plt.close()

    def _plot_returns(self):
        """繪製回報曲線"""
        fig, ax = plt.subplots(figsize=(14, 6))

        for asset, prices in self.data.items():
            ax.plot(prices.index, prices, label=asset, alpha=0.7)

        ax.set_title('資產價格走勢', fontsize=14)
        ax.set_xlabel('日期', fontsize=12)
        ax.set_ylabel('價格', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('asset_prices.png', dpi=150)
        plt.close()

    def _plot_performance(self):
        """繪製策略績效"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # 回報曲線
        axes[0, 0].plot(self.signals.index, self.signals['strategy_return'].cumsum())
        axes[0, 0].set_title('策略累積回報', fontsize=12)
        axes[0, 0].grid(True, alpha=0.3)

        # Sharpe Ratio
        axes[0, 1].bar(['Sharpe Ratio'], [self.backtest_results['sharpe']])
        axes[0, 1].set_ylim([0, max(self.backtest_results['sharpe']*1.2, 1)])
        axes[0, 1].set_title('策略績效指標', fontsize=12)
        axes[0, 1].grid(True, alpha=0.3, axis='y')

        # 最大回撤
        axes[1, 0].bar(['Max Drawdown'], [abs(self.backtest_results['max_drawdown'])])
        axes[1, 0].set_title('最大回撤', fontsize=12)
        axes[1, 0].grid(True, alpha=0.3, axis='y')

        # Win Rate
        axes[1, 1].bar(['Win Rate'], [self.backtest_results['win_rate']])
        axes[1, 1].set_ylim([0, 1])
        axes[1, 1].set_title('勝率', fontsize=12)
        axes[1, 1].grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.savefig('strategy_performance.png', dpi=150)
        plt.close()

    def run_analysis(self):
        """執行完整分析流程"""
        print("="*60)
        print("跨資產同步極端事件分析")
        print("="*60 + "\n")

        # 1. 載入數據
        self.load_data()

        # 2. 計算回報率
        self.calculate_returns()

        # 3. 分析相關性
        self.analyze_correlations()

        # 4. 分析同步破位
        self.analyze_breakdowns()

        # 5. 分析波動 regime
        self.analyze_regimes()

        # 6. 生成交易信號
        self.generate_signals()

        # 7. 回測
        self.backtest()

        # 8. 儲存結果
        self.save_results(self.backtest_results)

        # 9. 可視化
        self.visualize()

        print("="*60)
        print("分析完成！")
        print("="*60)

        # 顯示摘要
        self._print_summary()

    def _print_summary(self):
        """印出摘要"""
        print("\n" + "="*60)
        print("策略摘要")
        print("="*60)

        print(f"\n總回報率: {self.backtest_results['total_return']:.2%}")
        print(f"年化回報率: {self.backtest_results['annual_return']:.2%}")
        print(f"Sharpe Ratio: {self.backtest_results['sharpe']:.2f}")
        print(f"最大回撤: {abs(self.backtest_results['max_drawdown']):.2%}")
        print(f"勝率: {self.backtest_results['win_rate']:.2%}")
        print(f"交易次數: {self.backtest_results['trades']}")
        print(f"平均回報: {self.backtest_results['avg_return']:.2%}")
        print("="*60)


if __name__ == '__main__':
    # 創建分析器並執行分析
    analyzer = CrossAssetAnalyzer(
        assets=['NQ', 'GC', 'DX'],
        windows=[20, 50, 200]
    )

    analyzer.run_analysis()
