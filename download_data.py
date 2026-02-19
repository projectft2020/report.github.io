#!/usr/bin/env python3
"""
下載 QQQ, GLD, UUP, TLT 歷史數據
使用 yfinance 從 Yahoo Finance 獲取至少 10 年歷史數據
"""

import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta

def download_historical_data():
    """下載指定資產的歷史數據"""
    
    # 定義要下載的資產
    tickers = ['QQQ', 'GLD', 'UUP', 'TLT']
    
    # 計算開始日期（大約 10 年前）
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * 12)  # 12 年以確保有足夠數據
    
    print(f"下載數據期間: {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}")
    
    # 創建輸出目錄
    output_dir = '/Users/charlie/.openclaw/workspace/quant/data'
    os.makedirs(output_dir, exist_ok=True)
    
    # 存儲所有數據的字典
    all_data = {}
    
    for ticker in tickers:
        print(f"\n正在下載 {ticker}...")
        
        try:
            # 下載數據
            stock = yf.Ticker(ticker)
            hist_data = stock.history(start=start_date, end=end_date)
            
            if hist_data.empty:
                print(f"⚠️  {ticker} 沒有獲取到數據")
                continue
                
            # 重設索引並清理數據
            hist_data = hist_data.reset_index()
            hist_data['Date'] = pd.to_datetime(hist_data['Date'])
            
            # 移除沒有交易量的數據點（通常是非交易日）
            hist_data = hist_data[hist_data['Volume'] > 0]
            
            # 按日期排序
            hist_data = hist_data.sort_values('Date').reset_index(drop=True)
            
            # 保存為 CSV
            csv_path = os.path.join(output_dir, f"{ticker}_historical.csv")
            hist_data.to_csv(csv_path, index=False)
            
            print(f"✅ {ticker} 數據已保存到 {csv_path}")
            print(f"   數據點數: {len(hist_data)}")
            print(f"   日期範圍: {hist_data['Date'].min().strftime('%Y-%m-%d')} 到 {hist_data['Date'].max().strftime('%Y-%m-%d')}")
            
            # 檢查數據完整性
            check_data_quality(hist_data, ticker)
            
            all_data[ticker] = hist_data
            
        except Exception as e:
            print(f"❌ 下載 {ticker} 時發生錯誤: {e}")
    
    return all_data

def check_data_quality(data, ticker):
    """檢查數據質量"""
    print(f"\n📊 {ticker} 數據質量檢查:")
    
    # 檢查缺失值
    missing_values = data.isnull().sum()
    print(f"   缺失值: {missing_values.sum()}")
    if missing_values.sum() > 0:
        print(f"   缺失值詳情: {missing_values.to_dict()}")
    
    # 檢查日期連續性
    dates = pd.to_datetime(data['Date'])
    date_range = pd.date_range(start=dates.min(), end=dates.max(), freq='D')
    trading_days = [d for d in date_range if d.weekday() < 5]  # 週一到週五
    
    missing_dates = set(trading_days) - set(dates)
    print(f"   缺失交易日數量: {len(missing_dates)}")
    
    # 檢查數據統計
    print(f"   收盤價統計:")
    print(f"     平均: {data['Close'].mean():.2f}")
    print(f"     標準差: {data['Close'].std():.2f}")
    print(f"     最小值: {data['Close'].min():.2f}")
    print(f"     最大值: {data['Close'].max():.2f}")

def create_combined_data(all_data):
    """創建合併的數據集"""
    if not all_data:
        print("❌ 沒有數據可以合併")
        return
    
    # 創建合併的收盤價數據
    close_prices = pd.DataFrame()
    
    for ticker, data in all_data.items():
        # 使用日期作為索引
        df = data.set_index('Date')['Close'].rename(ticker)
        close_prices = pd.concat([close_prices, df], axis=1)
    
    # 移除任何時間點有缺失值的行
    close_prices = close_prices.dropna()
    
    # 保存合併數據
    combined_path = '/Users/charlie/.openclaw/workspace/quant/data/combined_close_prices.csv'
    close_prices.to_csv(combined_path)
    
    print(f"\n✅ 合併數據已保存到 {combined_path}")
    print(f"   合併後數據點數: {len(close_prices)}")
    print(f"   日期範圍: {close_prices.index.min().strftime('%Y-%m-%d')} 到 {close_prices.index.max().strftime('%Y-%m-%d')}")

if __name__ == "__main__":
    print("🚀 開始下載歷史數據...")
    
    # 檢查是否安裝了 yfinance
    try:
        import yfinance
    except ImportError:
        print("❌ yfinance 未安裝，正在安裝...")
        import subprocess
        subprocess.run(['pip', 'install', 'yfinance'])
        import yfinance
    
    # 下載數據
    all_data = download_historical_data()
    
    # 創建合併數據
    create_combined_data(all_data)
    
    print("\n🎉 數據下載完成！")