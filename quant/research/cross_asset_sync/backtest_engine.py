#!/usr/bin/env python3
"""
回測引擎模組
Author: Charlie
Date: 2026-02-17
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List


class BacktestEngine:
    """回測引擎"""

    def __init__(self, signals, data, initial_capital=100000, 
                 transaction_cost=0.0001, slippage=0.00005):
        """
        初始化回測引擎

        Args:
            signals: 交易信號序列
            data: 價格數據
            initial_capital: 初始資本
            transaction_cost: 交易成本
            slippage: 滑點
        """
        self.signals = signals
        self.data = data
        self.initial_capital = initial_capital
        self.transaction_cost = transaction_cost
        self.slippage = slippage

        # 策略參數
        self.position_size = 0.1  # 每次交易 10% 資金
        self.max_drawdown_threshold = 0.15  # 最大回撤閾值

        # 回測結果
        self.portfolio_value = []
        self.positions = {}
        self.equity_curve = []
        self.trades = []
        self.daily_returns = []

    def run(self):
        """
        執行回測

        Returns:
            DataFrame: 回測結果
        """
        print("  開始回測...")
        print(f"  初始資本: ${self.initial_capital:,.2f}")
        print(f"  交易成本: {self.transaction_cost*100:.2f}%")
        print(f"  滑點: {self.slippage*100:.3f}%")

        # 初始化
        current_capital = self.initial_capital
        positions = {}

        # 遍歷每一天
        for i in range(len(self.signals)):
            date = self.signals.index[i]
            signal = self.signals.iloc[i]

            # 計算回報率
            daily_return = self.calculate_daily_return(i, positions)
            current_capital *= (1 + daily_return)

            # 儲存資產
            portfolio_value = current_capital + self.calculate_position_value(positions)
            self.portfolio_value.append(portfolio_value)

            # 儲存回報
            self.daily_returns.append(daily_return)

            # 如果有信號，執行交易
            if signal > 0:
                self.execute_trade(i, date, positions, current_capital)

            # 更新倉位價值
            positions_value = self.calculate_position_value(positions)

            # 計算權益曲線
            equity_curve = current_capital + positions_value
            self.equity_curve.append(equity_curve)

            # 更新倉位
            positions = self.update_positions(date, positions)

        # 轉換為 DataFrame
        results = pd.DataFrame({
            'date': self.signals.index,
            'signal': self.signals,
            'portfolio_value': self.portfolio_value,
            'equity_curve': self.equity_curve,
            'daily_return': self.daily_returns
        }).set_index('date')

        print("  ✓ 回測完成")

        # 計算績效指標
        metrics = self.calculate_metrics(results)

        # 保存回測結果
        self.backtest_results = results
        self.metrics = metrics

        return results, metrics

    def calculate_daily_return(self, index, positions):
        """
        計算每日回報

        Args:
            index: 當前索引
            positions: 倉位字典

        Returns:
            float: 每日回報
        """
        total_return = 0

        # 倉位回報
        for asset, position in positions.items():
            if index < len(self.data[asset]):
                current_price = self.data[asset].iloc[index]
                prev_price = self.data[asset].iloc[index-1] if index > 0 else current_price

                position_return = (current_price / prev_price - 1) * position
                total_return += position_return

        return total_return

    def calculate_position_value(self, positions):
        """
        計算倉位總價值

        Args:
            positions: 倉位字典

        Returns:
            float: 倉位總價值
        """
        total_value = 0

        for asset, position in positions.items():
            if len(self.data[asset]) > 0:
                current_price = self.data[asset].iloc[-1]
                total_value += position * current_price

        return total_value

    def execute_trade(self, index, date, positions, capital):
        """
        執行交易

        Args:
            index: 當前索引
            date: 日期
            positions: 倉位字典
            capital: 當前資本
        """
        # 獲取信號
        signal = self.signals.iloc[index]

        # 計算目標倉位
        target_position_value = capital * self.position_size

        # 如果信號為正，增加倉位
        if signal > 0:
            # 計算需要多少資金
            remaining_capital = capital - self.calculate_position_value(positions)

            if remaining_capital > 0:
                # 找到回報率最高的資產
                best_asset = self.find_best_asset(index)

                if best_asset is not None:
                    # 計算買入數量
                    quantity = self.calculate_buy_quantity(
                        remaining_capital, best_asset, index
                    )

                    if quantity > 0:
                        # 記錄交易
                        trade = {
                            'date': date,
                            'asset': best_asset,
                            'action': 'buy',
                            'quantity': quantity,
                            'price': self.data[best_asset].iloc[index],
                            'value': quantity * self.data[best_asset].iloc[index]
                        }
                        self.trades.append(trade)

                        # 更新倉位
                        positions[best_asset] = positions.get(best_asset, 0) + quantity

        # 如果信號為負，減少倉位
        elif signal < 0:
            # 平掉所有倉位
            for asset in list(positions.keys()):
                quantity = positions[asset]

                if quantity > 0:
                    # 記錄交易
                    trade = {
                        'date': date,
                        'asset': asset,
                        'action': 'sell',
                        'quantity': quantity,
                        'price': self.data[asset].iloc[index],
                        'value': quantity * self.data[asset].iloc[index]
                    }
                    self.trades.append(trade)

                    # 更新倉位
                    del positions[asset]

    def calculate_buy_quantity(self, capital, asset, index):
        """
        計算買入數量

        Args:
            capital: 可用資本
            asset: 資產代碼
            index: 當前索引

        Returns:
            float: 買入數量
        """
        if index >= len(self.data[asset]):
            return 0

        # 考慮交易成本和滑點
        current_price = self.data[asset].iloc[index]
        adjusted_price = current_price * (1 + self.transaction_cost + self.slippage)

        quantity = capital / adjusted_price

        return quantity

    def find_best_asset(self, index):
        """
        找到最佳資產

        Args:
            index: 當前索引

        Returns:
            str: 最佳資產代碼
        """
        best_asset = None
        best_return = -np.inf

        # 計算回報率
        for asset in self.data.keys():
            if index >= len(self.data[asset]):
                continue

            current_price = self.data[asset].iloc[index]
            prev_price = self.data[asset].iloc[index-1] if index > 0 else current_price

            if prev_price > 0:
                return_rate = (current_price / prev_price - 1)

                if return_rate > best_return:
                    best_return = return_rate
                    best_asset = asset

        return best_asset

    def update_positions(self, date, positions):
        """
        更新倉位

        Args:
            date: 日期
            positions: 倉位字典

        Returns:
            dict: 更新後的倉位
        """
        new_positions = {}

        # 檢查是否有需要平倉的倉位
        for asset, quantity in positions.items():
            if len(self.data[asset]) > 0:
                current_price = self.data[asset].iloc[-1]

                # 如果資產價格跌超過 5%，平倉
                if index >= 1:
                    prev_price = self.data[asset].iloc[-2]
                    loss = (current_price / prev_price - 1)

                    if loss < -0.05:
                        trade = {
                            'date': date,
                            'asset': asset,
                            'action': 'stop_loss',
                            'quantity': quantity,
                            'price': current_price,
                            'value': quantity * current_price
                        }
                        self.trades.append(trade)
                    else:
                        new_positions[asset] = quantity
                else:
                    new_positions[asset] = quantity

        return new_positions

    def calculate_metrics(self, results):
        """
        計算績效指標

        Args:
            results: 回測結果 DataFrame

        Returns:
            dict: 績效指標
        """
        # 總回報率
        total_return = results['equity_curve'].iloc[-1] / self.initial_capital - 1

        # 年化回報率
        n_days = len(results)
        annual_return = total_return * (252 / n_days)

        # 日均回報率
        daily_return_mean = results['daily_return'].mean()

        # 日均波動率
        daily_return_std = results['daily_return'].std()

        # 年化波動率
        annual_volatility = daily_return_std * np.sqrt(252)

        # Sharpe Ratio
        risk_free_rate = 0.02
        sharpe = (daily_return_mean - risk_free_rate / 252) / daily_return_std * np.sqrt(252) if daily_return_std > 0 else 0

        # 最大回撤
        cumulative_max = results['equity_curve'].cummax()
        drawdown = (results['equity_curve'] - cumulative_max) / cumulative_max
        max_drawdown = drawdown.min()

        # 勝率
        winning_days = (results['daily_return'] > 0).sum()
        win_rate = winning_days / len(results) if len(results) > 0 else 0

        # 平均回報
        avg_return = results['daily_return'].mean()

        # Alpha
        alpha = daily_return_mean - 0.0001  # 簡化計算

        # Beta
        benchmark_returns = results['daily_return'].values
        market_returns = np.random.normal(0.0001, 0.01, len(benchmark_returns))  # 模擬市場回報

        if np.var(market_returns) > 0:
            beta = np.cov(benchmark_returns, daily_return_mean)[0, 1] / np.var(market_returns)
        else:
            beta = 0

        # 交易次數
        trade_count = len(self.trades)

        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'daily_return_mean': daily_return_mean,
            'daily_return_std': daily_return_std,
            'annual_volatility': annual_volatility,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'avg_return': avg_return,
            'alpha': alpha,
            'beta': beta,
            'trade_count': trade_count,
            'trades': pd.DataFrame(self.trades)
        }

    def plot_results(self):
        """繪製回測結果"""
        fig, axes = plt.subplots(3, 1, figsize=(14, 12), sharex=True)

        # 權益曲線
        axes[0].plot(self.backtest_results.index, self.backtest_results['equity_curve'],
                    color='blue', label='權益曲線')
        axes[0].set_title('權益曲線', fontsize=14)
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)

        # 顯示初始資本
        axes[0].axhline(y=self.initial_capital, color='green', linestyle='--',
                      label='初始資本')
        axes[0].legend()

        # 日回報率
        axes[1].plot(self.backtest_results.index, self.backtest_results['daily_return'],
                    color='red', label='日回報率')
        axes[1].axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        axes[1].set_title('日回報率', fontsize=12)
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)

        # 累積回報
        cumulative_return = (self.backtest_results['equity_curve'] - self.initial_capital) / self.initial_capital
        axes[2].plot(self.backtest_results.index, cumulative_return,
                    color='green', label='累積回報')
        axes[2].set_title('累積回報', fontsize=12)
        axes[2].legend()
        axes[2].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('backtest_results.png', dpi=150)
        plt.close()

    def plot_trades(self):
        """繪製交易點"""
        fig, ax = plt.subplots(figsize=(14, 6))

        # 繪製權益曲線
        ax.plot(self.backtest_results.index, self.backtest_results['equity_curve'],
               color='blue', label='權益曲線')

        # 繪製交易點
        for trade in self.trades:
            if trade['action'] == 'buy':
                color = 'green'
                marker = '^'
            else:
                color = 'red'
                marker = 'v'

            ax.scatter(trade['date'], self.backtest_results.loc[trade['date'], 'equity_curve'],
                      color=color, marker=marker, alpha=0.5)

        ax.set_title('交易點', fontsize=14)
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('trades.png', dpi=150)
        plt.close()


if __name__ == '__main__':
    # 測試回測
    import sys
    sys.path.append('..')
    from data_loader import DataLoader

    # 載入數據
    loader = DataLoader()
    nq = loader.load_data('NQ=F')
    gc = loader.load_data('GC=F')

    # 計算回報率
    returns = pd.DataFrame({
        'NQ': nq.pct_change().dropna(),
        'GC': gc.pct_change().dropna()
    })

    # 檢測破位
    from breakdown_detector import BreakdownDetector
    from trade_signal_generator import TradeSignalGenerator

    detector = BreakdownDetector(windows=[20])
    breakdown_nq = detector.detect_breakdown(nq)
    breakdown_gc = detector.detect_breakdown(gc)

    breakdowns = pd.DataFrame({
        'NQ': breakdown_nq,
        'GC': breakdown_gc
    })

    # 生成信號
    generator = TradeSignalGenerator(breakdowns=breakdowns, returns=returns)
    signals = generator.generate_composite_signals(breakdowns)

    # 執行回測
    backtest = BacktestEngine(signals, {'NQ': nq, 'GC': gc})
    results, metrics = backtest.run()

    print("\n績效指標:")
    print(f"總回報率: {metrics['total_return']:.2%}")
    print(f"年化回報率: {metrics['annual_return']:.2%}")
    print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
    print(f"最大回撤: {metrics['max_drawdown']:.2%}")
    print(f"勝率: {metrics['win_rate']:.2%}")
    print(f"交易次數: {metrics['trade_count']}")
