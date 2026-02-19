#!/usr/bin/env python3
"""
同步破位檢測模組
Author: Charlie
Date: 2026-02-17
"""

import pandas as pd
import numpy as np


class BreakdownDetector:
    """同步破位檢測器"""

    def __init__(self, windows=[20, 50, 200]):
        """
        初始化檢測器

        Args:
            windows: 移動平均線窗口期列表
        """
        self.windows = windows

    def analyze(self, data):
        """
        分析所有資產的同步破位

        Args:
            data: 價格數據字典 {'asset': prices}

        Returns:
            dict: 每個資產的破位時間序列
        """
        breakdowns = {}

        for asset, prices in data.items():
            breakdowns[asset] = self.detect_breakdown(prices)

        return breakdowns

    def detect_breakdown(self, prices, ma_window=20, lookback=5):
        """
        檢測破位事件

        破位定義：當前價格低於移動平均，且過去 lookback 天都在 MA 下方

        Args:
            prices: 價格序列
            ma_window: 移動平均線窗口期
            lookback: 回顧天數

        Returns:
            Series: 破位時間序列 (True/False)
        """
        # 計算移動平均線
        ma = prices.rolling(ma_window).mean()

        # 初始化破位序列
        breakdown = pd.Series(False, index=prices.index)

        # 檢測破位
        for i in range(lookback, len(prices)):
            # 當前價格低於 MA
            current_price_below_ma = prices.iloc[i] < ma.iloc[i]

            # 過去 lookback 天都在 MA 下方
            all_below_ma = all(prices.iloc[i-lookback:i] <= ma.iloc[i-lookback:i])

            # 滿足條件時標記破位
            if current_price_below_ma and all_below_ma:
                breakdown.iloc[i] = True

        return breakdown

    def detect_breakout(self, prices, ma_window=20, lookback=5):
        """
        檢測突破事件

        突破定義：當前價格高於移動平均，且過去 lookback 天都在 MA 上方

        Args:
            prices: 價格序列
            ma_window: 移動平均線窗口期
            lookback: 回顧天數

        Returns:
            Series: 突破時間序列 (True/False)
        """
        # 計算移動平均線
        ma = prices.rolling(ma_window).mean()

        # 初始化突破序列
        breakout = pd.Series(False, index=prices.index)

        # 檢測突破
        for i in range(lookback, len(prices)):
            # 當前價格高於 MA
            current_price_above_ma = prices.iloc[i] > ma.iloc[i]

            # 過去 lookback 天都在 MA 上方
            all_above_ma = all(prices.iloc[i-lookback:i] >= ma.iloc[i-lookback:i])

            # 滿足條件時標記突破
            if current_price_above_ma and all_above_ma:
                breakout.iloc[i] = True

        return breakout

    def detect_cross(self, prices, fast_window=10, slow_window=20):
        """
        檢測交叉事件

        金交叉：快線從下往上穿過慢線
        死交叉：快線從上往下穿過慢線

        Args:
            prices: 價格序列
            fast_window: 快線窗口期
            slow_window: 慢線窗口期

        Returns:
            dict: {'golden_cross': Series, 'death_cross': Series}
        """
        # 計算移動平均線
        fast_ma = prices.rolling(fast_window).mean()
        slow_ma = prices.rolling(slow_window).mean()

        # 初始化交叉序列
        golden_cross = pd.Series(False, index=prices.index)
        death_cross = pd.Series(False, index=prices.index)

        # 檢測金交叉
        for i in range(1, len(prices)):
            # 前一天快線在慢線下方，今天在上方
            if fast_ma.iloc[i-1] <= slow_ma.iloc[i-1] and fast_ma.iloc[i] > slow_ma.iloc[i]:
                golden_cross.iloc[i] = True

        # 檢測死交叉
        for i in range(1, len(prices)):
            # 前一天快線在慢線上方，今天在下方
            if fast_ma.iloc[i-1] >= slow_ma.iloc[i-1] and fast_ma.iloc[i] < slow_ma.iloc[i]:
                death_cross.iloc[i] = True

        return {
            'golden_cross': golden_cross,
            'death_cross': death_cross
        }

    def detect_breakdown_multiple_windows(self, prices):
        """
        檢測多個窗口期的破位

        Args:
            prices: 價格序列

        Returns:
            dict: 各窗口期的破位時間序列
        """
        results = {}

        for window in self.windows:
            results[f'{window}_ma'] = self.detect_breakdown(prices, ma_window=window)

        return results

    def analyze_breakdown_frequency(self, breakdowns, asset):
        """
        分析破位頻率

        Args:
            breakdowns: 破位時間序列
            asset: 資產代碼

        Returns:
            dict: 破位頻率分析結果
        """
        # 計算破位次數
        breakdown_count = breakdowns.sum()

        # 計算破位頻率
        breakdown_frequency = breakdown_count / len(breakdowns)

        # 計算平均間隔天數
        breakdowns_idx = breakdowns[breakdowns].index
        if len(breakdowns_idx) > 1:
            avg_interval = breakdowns_idx.diff().mean()
        else:
            avg_interval = np.nan

        return {
            'breakdown_count': breakdown_count,
            'breakdown_frequency': breakdown_frequency,
            'avg_interval_days': avg_interval,
            'breakdown_dates': breakdowns_idx.tolist()
        }

    def calculate_breakdown_strength(self, prices, breakdown_events, days_after=20):
        """
        計算破位後的強度

        Args:
            prices: 價格序列
            breakdown_events: 破位事件時間序列
            days_after: 計算未來 days_after 天的回報

        Returns:
            DataFrame: 包含破位日期、前後回報、強度
        """
        results = []

        for date in breakdown_events[breakdown_events].index:
            # 計算破位後的回報
            if date + pd.Timedelta(days=days_after) <= prices.index[-1]:
                forward_return = (prices.loc[date + pd.Timedelta(days=days_after)] /
                                 prices.loc[date] - 1)

                # 計算破位後的累積回報
                after_prices = prices.loc[date:date + pd.Timedelta(days=days_after)]
                cumulative_return = (after_prices.iloc[-1] / after_prices.iloc[0] - 1)

                # 計算前後回報
                before_prices = prices.loc[date - pd.Timedelta(days=days_after):date]
                if len(before_prices) > 0:
                    forward_return_days_5 = (before_prices.iloc[-1] / before_prices.iloc[0] - 1)
                else:
                    forward_return_days_5 = 0

                results.append({
                    'breakdown_date': date,
                    'forward_return_20d': forward_return,
                    'cumulative_return_20d': cumulative_return,
                    'return_5d_before': forward_return_days_5,
                    'breakdown_strength': cumulative_return
                })

        return pd.DataFrame(results)

    def find_most_common_breakdown_asset(self, breakdowns_dict):
        """
        找出最常破位的資產

        Args:
            breakdowns_dict: 各資產的破位時間序列

        Returns:
            tuple: (asset, count, frequency)
        """
        results = {}

        for asset, breakdowns in breakdowns_dict.items():
            result = self.analyze_breakdown_frequency(breakdowns, asset)
            results[asset] = result

        # 找出破位次數最多的資產
        most_common = max(results.items(), key=lambda x: x[1]['breakdown_count'])

        return most_common

    def plot_breakdown_timeline(self, breakdowns_dict):
        """
        繪製破位時間軸

        Args:
            breakdowns_dict: 各資產的破位時間序列
        """
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(14, 6))

        # 為每個資產標記破位時間
        for asset, breakdowns in breakdowns_dict.items():
            if len(breakdowns[breakdowns]) > 0:
                ax.scatter(breakdowns[breakdowns].index, [1]*len(breakdowns[breakdowns]),
                          color='red', alpha=0.5, label=asset if asset == list(breakdowns_dict.keys())[0] else "")

        ax.set_yticks([1])
        ax.set_yticklabels(['同步破位'])
        ax.set_title('同步破位時間軸', fontsize=14)
        ax.set_xlabel('日期', fontsize=12)
        ax.grid(True, alpha=0.3)

        # 只顯示前 10 個破位
        for breakdowns in breakdowns_dict.values():
            if len(breakdowns[breakdowns]) > 0:
                ax.set_xlim(left=breakdowns[breakdowns].index.min(),
                           right=breakdowns[breakdowns].index.max())
                break

        plt.tight_layout()
        plt.savefig('breakdown_timeline.png', dpi=150)
        plt.close()

    def compare_breakdown_strategies(self, prices1, prices2, ma_window1=20, ma_window2=50):
        """
        比較兩個資產的破位策略

        Args:
            prices1: 資產 1 價格
            prices2: 資產 2 價格
            ma_window1: 資產 1 MA 窗口
            ma_window2: 資產 2 MA 窗口

        Returns:
            dict: 比較結果
        """
        # 檢測破位
        breakdown1 = self.detect_breakdown(prices1, ma_window=ma_window1)
        breakdown2 = self.detect_breakdown(prices2, ma_window=ma_window2)

        # 計算強度
        strength1 = self.calculate_breakdown_strength(prices1, breakdown1)
        strength2 = self.calculate_breakdown_strength(prices2, breakdown2)

        # 分析同步破位
        # 兩者都在破位時的 forward return
        common_breakdown_dates = breakdown1[breakdown1 & breakdown2].index
        common_strength = []

        for date in common_breakdown_dates:
            if date + pd.Timedelta(days=20) <= prices1.index[-1]:
                return_20d = (prices1.loc[date + pd.Timedelta(days=20)] /
                             prices1.loc[date] - 1)
                common_strength.append(return_20d)

        return {
            'asset1_breakdowns': len(breakdown1[breakdown1]),
            'asset2_breakdowns': len(breakdown2[breakdown2]),
            'common_breakdowns': len(common_breakdown_dates),
            'asset1_avg_strength': strength1['cumulative_return_20d'].mean() if len(strength1) > 0 else np.nan,
            'asset2_avg_strength': strength2['cumulative_return_20d'].mean() if len(strength2) > 0 else np.nan,
            'common_avg_strength': np.mean(common_strength) if len(common_strength) > 0 else np.nan
        }


if __name__ == '__main__':
    # 測試破位檢測
    import sys
    sys.path.append('..')
    from data_loader import DataLoader

    # 載入數據
    loader = DataLoader()
    nq = loader.load_data('NQ=F')
    gc = loader.load_data('GC=F')
    dx = loader.load_data('DX=F')

    # 檢測破位
    detector = BreakdownDetector(windows=[20, 50])

    breakdown_nq = detector.detect_breakdown(nq, ma_window=20)
    breakdown_gc = detector.detect_breakdown(gc, ma_window=20)
    breakdown_dx = detector.detect_breakdown(dx, ma_window=20)

    # 分析頻率
    freq_nq = detector.analyze_breakdown_frequency(breakdown_nq, 'NQ')
    freq_gc = detector.analyze_breakdown_frequency(breakdown_gc, 'GC')
    freq_dx = detector.analyze_breakdown_frequency(breakdown_dx, 'DX')

    print("破位頻率分析:")
    print(f"NQ: {freq_nq['breakdown_count']} 次, 頻率: {freq_nq['breakdown_frequency']:.3f}")
    print(f"GC: {freq_gc['breakdown_count']} 次, 頻率: {freq_gc['breakdown_frequency']:.3f}")
    print(f"DX: {freq_dx['breakdown_count']} 次, 頻率: {freq_dx['breakdown_frequency']:.3f}")

    # 找出最常破位的資產
    most_common = detector.find_most_common_breakdown_asset({
        'NQ': breakdown_nq,
        'GC': breakdown_gc,
        'DX': breakdown_dx
    })

    print(f"\n最常破位的資產: {most_common[0]}")
    print(f"破位次數: {most_common[1]['breakdown_count']}")
    print(f"平均間隔: {most_common[1]['avg_interval_days'].days:.1f} 天")

    # 比較策略
    comparison = detector.compare_breakdown_strategies(nq, gc)
    print(f"\n破位策略比較: {comparison}")
