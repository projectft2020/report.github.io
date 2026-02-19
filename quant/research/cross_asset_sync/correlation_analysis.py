#!/usr/bin/env python3
"""
相關性分析模組
Author: Charlie
Date: 2026-02-17
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class CorrelationAnalyzer:
    """相關性分析器"""

    def analyze(self, returns, window=60):
        """
        分析資產之間的相關性

        Args:
            returns: 回報率 DataFrame (多個資產)
            window: 滾動窗口期

        Returns:
            DataFrame: 相關係數矩陣
        """
        # 選擇非 NaN 的資產
        available_assets = [col for col in returns.columns if not returns[col].isna().all()]

        if len(available_assets) < 2:
            raise ValueError("至少需要 2 個有效資產")

        # 計算滾動相關係數
        corr_matrix = returns[available_assets].rolling(window).corr()

        print(f"  計算滾動相關係數 (window={window})...")

        return corr_matrix

    def calculate_rolling_correlation(self, returns1, returns2, window=60):
        """
        計算兩個資產之間的滾動相關係數

        Args:
            returns1: 資產 1 的回報率
            returns2: 資產 2 的回報率
            window: 滾動窗口期

        Returns:
            Series: 滾動相關係數
        """
        # 計算滾動相關係數
        corr = returns1.rolling(window).corr(returns2)

        return corr

    def calculate_correlation_change(self, corr1, corr2):
        """
        計算相關係數變化

        Args:
            corr1: 資產 1 的相關係數
            corr2: 資產 2 的相關係數

        Returns:
            Series: 相關係數變化
        """
        # 計算變化率
        corr_change = corr2 - corr1

        return corr_change

    def detect_correlation_shift(self, corr_series, threshold=0.3):
        """
        檢測相關性突變

        Args:
            corr_series: 相關係數序列
            threshold: 變化閾值

        Returns:
            DataFrame: 檢測到突變的點
        """
        # 計算變化率
        corr_change = corr_series.diff()

        # 檢測突變
        shifts = corr_change.abs() > threshold

        # 找到變化方向
        shift_directions = np.where(corr_change > 0, 'increase', 'decrease')

        results = pd.DataFrame({
            'correlation': corr_series,
            'change': corr_change,
            'shift': shifts,
            'direction': shift_directions
        })

        return results[results['shift']]

    def plot_correlation_heatmap(self, corr_matrix, title='資產相關性矩陣'):
        """
        繪製相關性熱圖

        Args:
            corr_matrix: 相關係數矩陣
            title: 圖表標題
        """
        plt.figure(figsize=(10, 8))

        im = plt.imshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1)

        # 設定標籤
        plt.xticks(range(len(corr_matrix.columns)), corr_matrix.columns, rotation=45)
        plt.yticks(range(len(corr_matrix.columns)), corr_matrix.columns)

        # 加上相關係數值
        for i in range(len(corr_matrix.columns)):
            for j in range(len(corr_matrix.columns)):
                text = plt.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}',
                              ha="center", va="center", color="black")

        plt.colorbar(im, label='相關係數')
        plt.title(title, fontsize=14)
        plt.tight_layout()

        plt.savefig('correlation_heatmap.png', dpi=150)
        plt.close()

    def calculate_divergence(self, returns1, returns2, window=20):
        """
        計算資產 divergence（分歧）

        Args:
            returns1: 資產 1 的回報率
            returns2: 資產 2 的回報率
            window: 窗口期

        Returns:
            Series: divergence 值
        """
        # 計算兩個資產的滾動標準差
        std1 = returns1.rolling(window).std()
        std2 = returns2.rolling(window).std()

        # divergence = 標準差差異
        divergence = std1 - std2

        return divergence

    def calculate_corr_based_spread(self, returns1, returns2, window=60):
        """
        計算基於相關性的 spread

        Args:
            returns1: 資產 1 的回報率
            returns2: 資產 2 的回報率
            window: 窗口期

        Returns:
            Series: spread 值
        """
        # 計算滾動相關係數
        corr = self.calculate_rolling_correlation(returns1, returns2, window)

        # 計算 spread（標準化差異）
        spread = returns1 - returns2
        normalized_spread = spread / (1 + corr.abs())

        return normalized_spread

    def analyze_correlation_matrix(self, returns, window=60):
        """
        分析相關性矩陣

        Args:
            returns: 回報率 DataFrame
            window: 滾動窗口期

        Returns:
            dict: 分析結果
        """
        # 計算滾動相關係數
        corr_matrix = self.analyze(returns, window)

        # 計算平均相關係數
        avg_corr = corr_matrix.mean()

        # 計算相關係數標準差
        corr_std = corr_matrix.std()

        # 找出高相關資產對
        high_corr_pairs = []
        for i in range(len(avg_corr.columns)):
            for j in range(i+1, len(avg_corr.columns)):
                if avg_corr.iloc[i, j] > 0.7:  # 高相關閾值
                    high_corr_pairs.append({
                        'asset1': avg_corr.columns[i],
                        'asset2': avg_corr.columns[j],
                        'correlation': avg_corr.iloc[i, j]
                    })

        # 找出低相關資產對
        low_corr_pairs = []
        for i in range(len(avg_corr.columns)):
            for j in range(i+1, len(avg_corr.columns)):
                if abs(avg_corr.iloc[i, j]) < 0.3:  # 低相關閾值
                    low_corr_pairs.append({
                        'asset1': avg_corr.columns[i],
                        'asset2': avg_corr.columns[j],
                        'correlation': avg_corr.iloc[i, j]
                    })

        return {
            'correlation_matrix': corr_matrix,
            'avg_correlation': avg_corr,
            'correlation_std': corr_std,
            'high_corr_pairs': pd.DataFrame(high_corr_pairs),
            'low_corr_pairs': pd.DataFrame(low_corr_pairs)
        }

    def plot_correlation_evolution(self, corr_series, title='相關係數演化'):
        """
        繪製相關係數演化曲線

        Args:
            corr_series: 相關係數序列
            title: 圖表標題
        """
        fig, ax = plt.subplots(figsize=(14, 6))

        ax.plot(corr_series.index, corr_series, label='相關係數', color='blue')
        ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        ax.axhline(y=0.7, color='red', linestyle='--', alpha=0.5, label='高相關閾值')
        ax.axhline(y=-0.7, color='red', linestyle='--', alpha=0.5, label='負相關閾值')

        ax.set_title(title, fontsize=14)
        ax.set_xlabel('日期', fontsize=12)
        ax.set_ylabel('相關係數', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig('correlation_evolution.png', dpi=150)
        plt.close()

    def calculate_tail_correlation(self, returns, window=60, alpha=0.05):
        """
        計算尾部相關係數

        Args:
            returns: 回報率 DataFrame
            window: 滾動窗口期
            alpha: 尾部概率

        Returns:
            Series: 尾部相關係數
        """
        # 計算 VaR
        var1 = returns.rolling(window).apply(lambda x: x.quantile(alpha))
        var2 = returns.rolling(window).apply(lambda x: x.quantile(alpha))

        # 計算尾部事件
        tail_event1 = returns < var1
        tail_event2 = returns < var2

        # 計算尾部相關
        tail_corr = tail_event1.rolling(window).corr(tail_event2)

        return tail_corr

    def detect_low_correlation_pair(self, corr_matrix, threshold=0.3):
        """
        檢測低相關資產對

        Args:
            corr_matrix: 相關係數矩陣
            threshold: 相關閾值

        Returns:
            list: 低相關資產對列表
        """
        low_corr_pairs = []

        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr = corr_matrix.iloc[i, j]
                if abs(corr) < threshold:
                    low_corr_pairs.append({
                        'asset1': corr_matrix.columns[i],
                        'asset2': corr_matrix.columns[j],
                        'correlation': corr
                    })

        return low_corr_pairs


if __name__ == '__main__':
    # 測試相關性分析
    import sys
    sys.path.append('..')
    from data_loader import DataLoader

    # 載入數據
    loader = DataLoader()
    nq = loader.load_data('NQ=F')
    gc = loader.load_data('GC=F')
    dx = loader.load_data('DX=F')

    # 計算回報率
    returns = pd.DataFrame({
        'NQ': nq.pct_change().dropna(),
        'GC': gc.pct_change().dropna(),
        'DX': dx.pct_change().dropna()
    })

    # 分析相關性
    analyzer = CorrelationAnalyzer()
    corr_matrix = analyzer.analyze(returns, window=60)

    # 分析低相關資產對
    low_corr = analyzer.detect_low_correlation_pair(corr_matrix, threshold=0.3)

    print("\n低相關資產對:")
    print(low_corr)

    # 計算滾動相關係數
    corr_nq_gc = analyzer.calculate_rolling_correlation(returns['NQ'], returns['GC'])
    print(f"\nNQ 和 GC 的平均相關係數: {corr_nq_gc.mean():.3f}")

    # 檢測相關性突變
    shifts = analyzer.detect_correlation_shift(corr_nq_gc, threshold=0.3)
    print(f"\n相關性突變次數: {len(shifts)}")
    if len(shifts) > 0:
        print("突變點:")
        print(shifts.head())
