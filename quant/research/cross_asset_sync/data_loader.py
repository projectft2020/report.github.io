#!/usr/bin/env python3
"""
數據載入模組
Author: Charlie
Date: 2026-02-17
"""

import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta


class DataLoader:
    """數據載入器"""

    def __init__(self, cache_dir='data'):
        """
        初始化數據載入器

        Args:
            cache_dir: 數據快取目錄
        """
        self.cache_dir = cache_dir

    def load_data(self, asset, period='daily'):
        """
        載入資產數據

        Args:
            asset: 資產代碼（如 'NQ=F', 'GC=F', 'DX=Y'）
            period: 周期 ('daily', 'weekly', 'monthly')

        Returns:
            DataFrame: 包含日期和價格的 DataFrame
        """
        # 計算日期範圍
        end_date = datetime.now()
        start_date = end_date - timedelta(days=3650)  # 10 年數據

        # 載入數據
        print(f"  從 Yahoo Finance 載入 {asset} 數據...")
        data = yf.download(asset, start=start_date, end=end_date)

        if len(data) == 0:
            raise ValueError(f"無法載入 {asset} 的數據")

        # 只保留價格數據
        if 'Adj Close' in data.columns:
            prices = data['Adj Close']
        elif 'Close' in data.columns:
            prices = data['Close']
        else:
            raise ValueError(f"{asset} 不包含價格數據")

        # 重設索引
        prices = prices.reset_index()
        prices.columns = ['date', 'price']

        # 轉換為 datetime
        prices['date'] = pd.to_datetime(prices['date'])

        # 依週期處理
        if period == 'weekly':
            prices = self._resample_to_weekly(prices)
        elif period == 'monthly':
            prices = self._resample_to_monthly(prices)

        # 設定日期為索引
        prices = prices.set_index('date')
        prices = prices.sort_index()

        # 保存到快取
        self._save_to_cache(asset, prices)

        print(f"  ✓ 成功載入 {len(prices)} 天數據")

        return prices

    def _resample_to_weekly(self, df):
        """轉換為週線數據"""
        # 取週一的價格
        df = df[df.index.dayofweek == 0]

        if len(df) > 0:
            df = df.resample('W').first()
        else:
            df = df.resample('W').first()

        return df

    def _resample_to_monthly(self, df):
        """轉換為月線數據"""
        # 取月初的價格
        df = df[df.index.day == 1]

        if len(df) > 0:
            df = df.resample('M').first()
        else:
            df = df.resample('M').first()

        return df

    def _save_to_cache(self, asset, data):
        """保存數據到快取"""
        import os

        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        filename = f"{self.cache_dir}/{asset}.csv"
        data.to_csv(filename, encoding='utf-8-sig')

    def load_from_cache(self, asset):
        """
        從快取載入數據

        Args:
            asset: 資產代碼

        Returns:
            DataFrame: 價格數據
        """
        filename = f"{self.cache_dir}/{asset}.csv"

        try:
            data = pd.read_csv(filename, index_col='date', parse_dates=True)
            print(f"  從快取載入 {asset}")
            return data
        except FileNotFoundError:
            print(f"  未找到快取: {asset}")
            return None


if __name__ == '__main__':
    # 測試數據載入
    loader = DataLoader()

    # 測試載入 NQ（納斯達克 100 期貨）
    nq = loader.load_data('NQ=F', period='daily')
    print("\nNQ 數據:")
    print(nq.head())

    # 測試載入 GC（黃金期貨）
    gc = loader.load_data('GC=F', period='daily')
    print("\nGC 數據:")
    print(gc.head())

    # 測試載入 DX（美元指數 - 期貨）
    dx = loader.load_data('DX=F', period='daily')
    print("\nDX 數據:")
    print(dx.head())
