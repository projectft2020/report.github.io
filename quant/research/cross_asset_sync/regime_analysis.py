#!/usr/bin/env python3
"""
波動 regime 分析模組
Author: Charlie
Date: 2026-02-17
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats


class RegimeAnalyzer:
    """波動 regime 分析器"""

    def analyze(self, data):
        """
        分析所有資產的波動 regime

        Args:
            data: 價格數據字典 {'asset': prices}

        Returns:
            dict: 每個資產的 regime 分析結果
        """
        results = {}

        for asset, prices in data.items():
            results[asset] = self.analyze_regime(prices)

        return results

    def analyze_regime(self, prices, vol_windows=[20, 50, 200]):
        """
        分析資產的波動 regime

        Regime 分類：低波動、中等波動、高波動

        Args:
            prices: 價格序列
            vol_windows: 波動率計算窗口期

        Returns:
            dict: regime 分析結果
        """
        # 計算回報率
        returns = prices.pct_change().dropna()

        # 計算不同窗口期的波動率
        volatilities = {}
        for window in vol_windows:
            volatilities[f'{window}d'] = returns.rolling(window).std() * np.sqrt(252)

        # 建立 regime 分類
        regime_labels = pd.Series('unknown', index=returns.index)

        for window in vol_windows:
            vol = volatilities[f'{window}d']
            low_threshold = vol.quantile(0.25)
            high_threshold = vol.quantile(0.75)

            regime_labels[vol > high_threshold] = 'high'
            regime_labels[(vol >= low_threshold) & (vol <= high_threshold)] = 'medium'
            regime_labels[vol < low_threshold] = 'low'

        # 計算 regime 統計
        regime_stats = regime_labels.value_counts(normalize=True)

        # 計算趨勢半衰期
        trend_half_life = self.calculate_trend_half_life(returns)

        return {
            'volatilities': volatilities,
            'regime_labels': regime_labels,
            'regime_stats': regime_stats,
            'trend_half_life': trend_half_life
        }

    def calculate_trend_half_life(self, returns, window=252):
        """
        計算趨勢半衰期

        趨勢半衰期 = 相關係數序列中，相關係數降到 0.5 以下的天數

        Args:
            returns: 回報率序列
            window: 計算窗口期

        Returns:
            dict: 不同 regime 下的趨勢半衰期
        """
        half_life = {}

        regimes = ['low', 'medium', 'high']

        for regime in regimes:
            regime_returns = returns[regime_labels == regime]

            if len(regime_returns) < window:
                continue

            # 計算滾動相關係數
            corr = regime_returns.rolling(window).corr(regime_returns.shift(-1))

            # 找出半衰期
            half_life_days = []
            for date in corr.index:
                current_corr = corr.loc[date]

                # 如果相關係數 < 0.5，開始計算
                if current_corr < 0.5:
                    start_date = date
                    days_passed = 0

                    # 找到相關係數降到 0.5 以下的天數
                    for i in range(len(corr)):
                        if corr.iloc[i] < 0.5:
                            days_passed = i + 1
                            break

                    half_life_days.append(days_passed)

            if len(half_life_days) > 0:
                half_life[regime] = np.mean(half_life_days)
            else:
                half_life[regime] = np.nan

        return half_life

    def classify_regime(self, current_volatility, vol_windows=[20, 50, 200],
                       threshold=0.75):
        """
        分類當前波動 regime

        Args:
            current_volatility: 當前波動率
            vol_windows: 波動率計算窗口期
            threshold: 高波動閾值

        Returns:
            str: regime 分類 ('low', 'medium', 'high')
        """
        # 計算不同窗口期的波動率
        volatilities = []
        for window in vol_windows:
            vol = np.mean(current_volatility[-window:])
            volatilities.append(vol)

        # 計算平均波動率
        avg_vol = np.mean(volatilities)

        if avg_vol > threshold:
            return 'high'
        elif avg_vol > threshold * 0.5:
            return 'medium'
        else:
            return 'low'

    def analyze_regime_transition(self, regime_labels):
        """
        分析 regime 轉換

        Args:
            regime_labels: regime 標籤序列

        Returns:
            dict: regime 轉換統計
        """
        # 計算轉換矩陣
        unique_regimes = regime_labels.unique()
        transition_matrix = pd.DataFrame(0, index=unique_regimes,
                                       columns=unique_regimes)

        for i in range(len(regime_labels)-1):
            from_regime = regime_labels.iloc[i]
            to_regime = regime_labels.iloc[i+1]

            transition_matrix.loc[from_regime, to_regime] += 1

        # 計算轉換概率
        transition_prob = transition_matrix.div(transition_matrix.sum(axis=1), axis=0)

        return transition_matrix, transition_prob

    def calculate_regime_persistence(self, regime_labels):
        """
        計算 regime 持續性

        Args:
            regime_labels: regime 標籤序列

        Returns:
            dict: 持續性統計
        """
        persistence = {}

        for regime in regime_labels.unique():
            regime_mask = regime_labels == regime
            regime_changes = regime_mask.diff().fillna(False)

            # 計算平均持續天數
            current_stay = 0
            stays = []

            for i in range(len(regime_mask)):
                if regime_mask.iloc[i]:
                    current_stay += 1
                else:
                    if current_stay > 0:
                        stays.append(current_stay)
                    current_stay = 0

            # 最後一次持續
            if current_stay > 0:
                stays.append(current_stay)

            if len(stays) > 0:
                persistence[regime] = {
                    'avg_stay_days': np.mean(stays),
                    'min_stay_days': np.min(stays),
                    'max_stay_days': np.max(stays),
                    'avg_stays': stays
                }
            else:
                persistence[regime] = {
                    'avg_stay_days': 0,
                    'min_stay_days': 0,
                    'max_stay_days': 0,
                    'avg_stays': []
                }

        return persistence

    def plot_regime_evolution(self, regime_labels, volatilities, title='波動 regime 演化'):
        """
        繪製 regime 演化圖

        Args:
            regime_labels: regime 標籤序列
            volatilities: 波動率序列
            title: 圖表標題
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

        # Regime 標籤
        unique_regimes = regime_labels.unique()
        regime_colors = {'low': 'green', 'medium': 'yellow', 'high': 'red'}

        for regime in unique_regimes:
            regime_data = regime_labels == regime
            ax1.scatter(regime_data[regime_data].index,
                       [1]*len(regime_data[regime_data]),
                       color=regime_colors[regime], label=regime,
                       alpha=0.5)

        ax1.set_yticks([1])
        ax1.set_yticklabels(['Regime'])
        ax1.set_title(title, fontsize=14)
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # 波動率
        ax2.plot(volatilities.index, volatilities,
                color='blue', label='Volatility')
        ax2.set_xlabel('日期', fontsize=12)
        ax2.set_ylabel('波動率', fontsize=12)
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('regime_evolution.png', dpi=150)
        plt.close()

    def compare_regime_performance(self, returns, regime_labels):
        """
        比較不同 regime 的表現

        Args:
            returns: 回報率序列
            regime_labels: regime 標籤序列

        Returns:
            dict: 各 regime 的統計結果
        """
        results = {}

        for regime in regime_labels.unique():
            regime_returns = returns[regime_labels == regime]

            results[regime] = {
                'count': len(regime_returns),
                'mean_return': regime_returns.mean(),
                'std_return': regime_returns.std(),
                'sharpe': regime_returns.mean() / regime_returns.std() if regime_returns.std() > 0 else 0,
                'max_return': regime_returns.max(),
                'min_return': regime_returns.min(),
                'positive_days': (regime_returns > 0).sum()
            }

        return pd.DataFrame(results).T

    def calculate_volatility_spread(self, returns1, returns2, window=20):
        """
        計算波動率 spread

        Args:
            returns1: 資產 1 回報率
            returns2: 資產 2 回報率
            window: 窗口期

        Returns:
            Series: 波動率 spread
        """
        vol1 = returns1.rolling(window).std()
        vol2 = returns2.rolling(window).std()

        spread = vol1 - vol2

        return spread

    def detect_volatility_regime_shift(self, volatilities, threshold=0.3):
        """
        檢測波動率 regime 轉換

        Args:
            volatilities: 波動率序列
            threshold: 轉換閾值

        Returns:
            DataFrame: regime 轉換點
        """
        # 計算波動率變化
        vol_change = volatilities.diff()

        # 找出轉換點
        shift_up = vol_change > threshold
        shift_down = vol_change < -threshold

        # 合併結果
        regime_shifts = pd.DataFrame({
            'shift_up': shift_up,
            'shift_down': shift_down
        }, index=volatilities.index)

        return regime_shifts

    def analyze_trend_in_regime(self, returns, regime_labels, window=252):
        """
        分析不同 regime 下的趨勢

        Args:
            returns: 回報率序列
            regime_labels: regime 標籤序列
            window: 計算窗口期

        Returns:
            dict: 各 regime 下的趨勢分析
        """
        trends = {}

        for regime in regime_labels.unique():
            regime_returns = returns[regime_labels == regime]

            if len(regime_returns) < window:
                continue

            # 計算滾動回歸斜率
            X = np.arange(window)
            y = regime_returns.iloc[-window:].values

            slope, intercept, r_value, p_value, std_err = stats.linregress(X, y)

            trends[regime] = {
                'slope': slope,
                'intercept': intercept,
                'r_squared': r_value**2,
                'p_value': p_value,
                'trend': 'up' if slope > 0 else 'down'
            }

        return trends


if __name__ == '__main__':
    # 測試 regime 分析
    import sys
    sys.path.append('..')
    from data_loader import DataLoader

    # 載入數據
    loader = DataLoader()
    nq = loader.load_data('NQ=F')
    gc = loader.load_data('GC=F')

    # 分析 regime
    analyzer = RegimeAnalyzer()
    regime_results = analyzer.analyze({
        'NQ': nq,
        'GC': gc
    })

    # 打印結果
    for asset, results in regime_results.items():
        print(f"\n{asset} 波動 regime 統計:")
        print(results['regime_stats'])
        print(f"趨勢半衰期: {results['trend_half_life']}")

    # 分析 regime 轉換
    transition_matrix, transition_prob = analyzer.analyze_regime_transition(
        regime_results['NQ']['regime_labels']
    )

    print("\nRegime 轉換矩陣:")
    print(transition_matrix)
    print("\nRegime 轉換概率:")
    print(transition_prob)

    # 比較 regime 表現
    performance = analyzer.compare_regime_performance(
        nq.pct_change().dropna(),
        regime_results['NQ']['regime_labels']
    )

    print("\nRegime 表現比較:")
    print(performance)
