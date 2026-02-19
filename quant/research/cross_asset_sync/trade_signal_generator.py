#!/usr/bin/env python3
"""
交易信號生成模組
Author: Charlie
Date: 2026-02-17
"""

import pandas as pd
import numpy as np


class TradeSignalGenerator:
    """交易信號生成器"""

    def __init__(self, breakdowns=None, returns=None):
        """
        初始化信號生成器

        Args:
            breakdowns: 破位事件時間序列
            returns: 回報率序列
        """
        self.breakdowns = breakdowns
        self.returns = returns

    def generate_all_signals(self):
        """生成所有交易信號"""
        signals = pd.DataFrame(index=self.breakdowns.index)

        # 同步破位信號
        signals['breakdown_signal'] = self.generate_breakdown_signals()

        # 負相關交易信號
        signals['negative_correlation_signal'] = self.generate_negative_correlation_signals()

        # 波動 regime 信號
        signals['regime_signal'] = self.generate_regime_signals()

        # 綜合信號
        signals['composite_signal'] = self.generate_composite_signals(signals)

        return signals

    def generate_breakdown_signals(self, forward_window=20):
        """
        生成同步破位信號

        Args:
            forward_window: 計算 forward return 的天數

        Returns:
            Series: 交易信號
        """
        signals = pd.Series(0, index=self.breakdowns.index)

        # 找出同步破位的時間
        common_breakdowns = self.breakdowns[all(self.breakdowns.values)]

        for date in common_breakdowns[common_breakdowns].index:
            if date + pd.Timedelta(days=forward_window) <= self.breakdowns.index[-1]:
                # 計算 forward return
                forward_return = self.calculate_forward_return(date, forward_window)

                # 如果回報 > 0，發出信號
                if forward_return > 0:
                    signals[date] = 1

        return signals

    def generate_negative_correlation_signals(self, correlation_window=60,
                                              threshold=0.3, lookback=5):
        """
        生成負相關交易信號

        條件：
        1. 兩個資產負相關
        2. 兩個資產同跌

        Args:
            correlation_window: 相關係數計算窗口期
            threshold: 相關閾值
            lookback: 回顧天數

        Returns:
            Series: 交易信號
        """
        signals = pd.Series(0, index=self.returns.index)

        # 檢測負相關且同跌的點
        for i in range(correlation_window + lookback, len(self.returns)):
            # 獲取相關係數
            corr = self.calculate_rolling_correlation(i, correlation_window)

            # 檢查負相關
            if abs(corr) < threshold:
                # 獲取回報率
                ret1 = self.returns.iloc[i-lookback:i].sum()
                ret2 = self.returns.iloc[i-lookback:i].sum()

                # 檢查同跌
                if ret1 < 0 and ret2 < 0:
                    # 計算 forward return
                    forward_return = self.calculate_forward_return(i, 20)

                    # 如果回報 > 0，發出信號
                    if forward_return > 0:
                        signals.iloc[i] = 1

        return signals

    def generate_regime_signals(self, threshold=0.75):
        """
        生成波動 regime 信號

        Args:
            threshold: 高波動閾值

        Returns:
            Series: 交易信號
        """
        signals = pd.Series(0, index=self.returns.index)

        # 計算波動率
        volatilities = self.returns.rolling(20).std() * np.sqrt(252)

        # 高波動 regime = 買入信號
        signals[volatilities > threshold] = 1

        return signals

    def generate_composite_signals(self, signals):
        """
        生成綜合交易信號

        綜合策略：多個信號都為正時才發出信號

        Args:
            signals: 輸入信號

        Returns:
            Series: 綜合信號
        """
        composite = pd.Series(0, index=signals.index)

        # 計算所有信號的總和
        for col in signals.columns:
            composite += signals[col]

        # 總和 >= 2 時發出信號（即至少 2 個信號為正）
        composite[composite >= 2] = 1

        return composite

    def calculate_rolling_correlation(self, index, window=60):
        """
        計算滾動相關係數

        Args:
            index: 當前索引
            window: 窗口期

        Returns:
            float: 相關係數
        """
        # 簡化實現：只計算前兩個資產
        if len(self.returns.columns) < 2:
            return 0

        # 計算滾動相關
        corr = self.returns.iloc[index-window:index].corr()

        return corr.iloc[0, 1]

    def calculate_forward_return(self, index, days=20):
        """
        計算 forward return

        Args:
            index: 當前索引
            days: 天數

        Returns:
            float: forward return
        """
        if index + days <= self.returns.index[-1]:
            forward_return = self.returns.iloc[index + days] / self.returns.iloc[index] - 1
            return forward_return
        else:
            return 0

    def calculate_ic(self, signals, returns, window=60):
        """
        計算信息係數（IC）

        Args:
            signals: 信號序列
            returns: 回報率序列
            window: 窗口期

        Returns:
            Series: IC 序列
        """
        ics = []

        for i in range(window, len(signals)):
            current_signal = signals.iloc[i-window:i]
            current_returns = returns.iloc[i-window:i]

            # 計算相關係數
            ic = current_signal.corr(current_returns)
            ics.append(ic)

        return pd.Series(ics)

    def calculate_ir(self, signals, returns, window=60):
        """
        計算信息比率（IR）

        Args:
            signals: 信號序列
            returns: 回報率序列
            window: 窗口期

        Returns:
            float: IR
        """
        ics = self.calculate_ic(signals, returns, window)

        # 計算平均 IC 和標準差
        mean_ic = ics.mean()
        ic_std = ics.std()

        # 計算 IR
        if ic_std > 0:
            ir = mean_ic / ic_std
        else:
            ir = 0

        return ir

    def filter_signals_by_ic(self, signals, returns, min_ic=0.01):
        """
        根據 IC 篩選信號

        Args:
            signals: 信號序列
            returns: 回報率序列
            min_ic: 最小 IC 閾值

        Returns:
            Series: 篩選後的信號
        """
        # 計算 IC
        ics = self.calculate_ic(signals, returns)

        # 篩選高 IC 信號
        high_ic_signals = signals.copy()

        for i in range(60, len(signals)):
            if ics.iloc[i-60] < min_ic:
                high_ic_signals.iloc[i] = 0

        return high_ic_signals

    def analyze_signal_performance(self, signals):
        """
        分析信號表現

        Args:
            signals: 信號序列

        Returns:
            dict: 表現分析結果
        """
        # 統計信號次數
        total_signals = signals.sum()

        # 計算平均回報
        signal_returns = []

        for i in range(len(signals)):
            if signals.iloc[i] > 0:
                forward_return = self.calculate_forward_return(i, 20)
                signal_returns.append(forward_return)

        avg_return = np.mean(signal_returns) if len(signal_returns) > 0 else 0

        # 計算勝率
        win_rate = np.mean([r > 0 for r in signal_returns]) if len(signal_returns) > 0 else 0

        # 計算 IR
        ir = self.calculate_ir(signals, self.returns) if len(signal_returns) > 0 else 0

        return {
            'total_signals': total_signals,
            'avg_return': avg_return,
            'win_rate': win_rate,
            'ir': ir
        }

    def plot_signal_analysis(self, signals, returns):
        """
        繪製信號分析圖

        Args:
            signals: 信號序列
            returns: 回報率序列

        Returns:
            None
        """
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(3, 1, figsize=(14, 12), sharex=True)

        # 信號時間軸
        axes[0].scatter(signals[signals > 0].index,
                       [1]*len(signals[signals > 0]),
                       color='red', alpha=0.5, label='信號點')
        axes[0].set_yticks([1])
        axes[0].set_yticklabels(['信號'])
        axes[0].set_title('交易信號', fontsize=14)
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)

        # 回報率
        axes[1].plot(returns.index, returns,
                    color='blue', label='回報率')
        axes[1].set_title('回報率', fontsize=12)
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)

        # 累積回報
        cumulative_return = (1 + returns).cumprod()
        axes[2].plot(cumulative_return.index, cumulative_return,
                    color='green', label='累積回報')
        axes[2].set_title('累積回報', fontsize=12)
        axes[2].legend()
        axes[2].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('signal_analysis.png', dpi=150)
        plt.close()

    def generate_alpha_signals(self, alpha_library, returns, min_ic=0.01):
        """
        生成 alpha 信號

        Args:
            alpha_library: Alpha 函數庫
            returns: 回報率序列
            min_ic: 最小 IC 閾值

        Returns:
            DataFrame: 所有 alpha 信號
        """
        alpha_signals = pd.DataFrame()

        for alpha_name, alpha_func in alpha_library.items():
            print(f"  生成 {alpha_name} 信號...")
            alpha_signal = alpha_func(returns)
            alpha_signals[alpha_name] = alpha_signal

            # 計算 IC
            ic = self.calculate_ic(alpha_signal, returns)
            mean_ic = ic.mean()

            print(f"    平均 IC: {mean_ic:.3f}")

            # 如果 IC > min_ic，保留信號
            if mean_ic >= min_ic:
                print(f"    ✓ 保留 {alpha_name} 信號")
            else:
                print(f"    ✗ 跳過 {alpha_name} 信號（IC 低）")
                alpha_signals.drop(columns=[alpha_name], inplace=True)

        return alpha_signals


if __name__ == '__main__':
    # 測試信號生成
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
    detector = BreakdownDetector(windows=[20])

    breakdown_nq = detector.detect_breakdown(nq)
    breakdown_gc = detector.detect_breakdown(gc)

    breakdowns = pd.DataFrame({
        'NQ': breakdown_nq,
        'GC': breakdown_gc
    })

    # 生成信號
    generator = TradeSignalGenerator(breakdowns=breakdowns, returns=returns)
    signals = generator.generate_all_signals()

    print("\n信號統計:")
    print(f"總信號數: {signals['composite_signal'].sum()}")
    print(f"平均回報: {signals['composite_signal'].mean():.3f}")

    # 分析信號表現
    performance = generator.analyze_signal_performance(signals['composite_signal'])
    print(f"勝率: {performance['win_rate']:.3f}")
    print(f"IR: {performance['ir']:.3f}")
