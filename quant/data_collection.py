#!/usr/bin/env python3
"""
量化交易數據收集系統
執行日期：2026-02-18
狀態：正在執行
"""

import yfinance as yf
import pandas as pd
import numpy as np
import os
import json
from datetime import datetime, timedelta
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataCollectionSystem:
    """量化交易數據收集系統"""
    
    def __init__(self):
        self.base_dir = '/Users/charlie/.openclaw/workspace/quant/data'
        self.tickers = ['QQQ', 'GLD', 'UUP', 'TLT']
        self.start_date = '2010-01-01'
        self.end_date = '2025-12-31'
        
    def setup_directories(self):
        """設置數據目錄結構"""
        directories = ['raw', 'processed', 'cache', 'metadata']
        
        for directory in directories:
            dir_path = os.path.join(self.base_dir, directory)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                logger.info(f"創建目錄：{dir_path}")
        
        logger.info("✅ 數據目錄設置完成")
        
    def fetch_price_data(self):
        """獲取歷史價格數據"""
        logger.info(f"開始獲取 {len(self.tickers)} 個資產的歷史數據")
        logger.info(f"時間範圍：{self.start_date} 到 {self.end_date}")
        
        try:
            # 下載數據
            data = yf.download(self.tickers, 
                             start=self.start_date, 
                             end=self.end_date,
                             progress=False)
            
            # 提取調整後收盤價
            adj_close = data['Adj Close']
            
            logger.info(f"✅ 數據獲取成功")
            logger.info(f"數據形狀：{adj_close.shape}")
            logger.info(f"資產列表：{list(adj_close.columns)}")
            logger.info(f"日期範圍：{adj_close.index[0]} 到 {adj_close.index[-1]}")
            
            return adj_close
            
        except Exception as e:
            logger.error(f"❌ 數據獲取失敗：{str(e)}")
            return None
    
    def validate_data_quality(self, data):
        """驗證數據品質"""
        quality_report = {
            'data_shape': data.shape,
            'missing_values': data.isnull().sum().to_dict(),
            'date_range': {
                'start': str(data.index.min()),
                'end': str(data.index.max()),
                'total_days': len(data)
            },
            'assets': list(data.columns),
            'data_completeness': {}
        }
        
        # 計算每個資產的數據完整性
        for asset in data.columns:
            asset_data = data[asset]
            completeness = (1 - asset_data.isnull().sum() / len(asset_data)) * 100
            quality_report['data_completeness'][asset] = completeness
            
        logger.info("✅ 數據品質驗證完成")
        return quality_report
    
    def clean_data(self, data):
        """清洗數據"""
        cleaned_data = data.copy()
        
        # 處理缺失值 - 前向填充
        cleaned_data = cleaned_data.fillna(method='ffill')
        
        # 再次處理剩餘缺失值 - 後向填充
        cleaned_data = cleaned_data.fillna(method='bfill')
        
        # 確保沒有 NaN 值
        if cleaned_data.isnull().any().any():
            logger.warning("⚠️ 仍有缺失值存在，填充為 0")
            cleaned_data = cleaned_data.fillna(0)
        
        logger.info(f"✅ 數據清洗完成，形狀：{cleaned_data.shape}")
        return cleaned_data
    
    def save_data(self, data, filename):
        """保存數據和元數據"""
        # 保存路徑
        raw_path = os.path.join(self.base_dir, 'raw', filename)
        
        # 保存主數據
        data.to_csv(raw_path)
        logger.info(f"數據已保存至：{raw_path}")
        
        # 保存元數據
        metadata = {
            'filename': filename,
            'data_type': 'raw',
            'shape': data.shape,
            'columns': list(data.columns),
            'date_range': {
                'start': str(data.index[0]),
                'end': str(data.index[-1])
            },
            'save_time': datetime.now().isoformat(),
            'tickers': self.tickers,
            'data_source': 'Yahoo Finance API'
        }
        
        metadata_path = os.path.join(self.base_dir, 'metadata', f"{filename}_metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        logger.info(f"元數據已保存至：{metadata_path}")
    
    def calculate_technical_indicators(self, data):
        """計算技術指標"""
        indicators = {}
        
        for asset in data.columns:
            asset_data = data[asset].dropna()
            
            if len(asset_data) < 20:
                continue
                
            # 計算各種技術指標
            indicators[asset] = {
                'sma_20': asset_data.rolling(window=20).mean(),
                'sma_50': asset_data.rolling(window=50).mean(),
                'sma_200': asset_data.rolling(window=200).mean(),
                'returns_1d': asset_data.pct_change(),
                'returns_5d': asset_data.pct_change(5),
                'returns_21d': asset_data.pct_change(21),
                'volatility_21d': asset_data.pct_change().rolling(window=21).std() * np.sqrt(21)
            }
            
            # 計算 RSI
            delta = asset_data.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            indicators[asset]['rsi_14'] = 100 - (100 / (1 + rs))
        
        logger.info("✅ 技術指標計算完成")
        return indicators
    
    def save_processed_data(self, data, indicators):
        """保存處理後的數據"""
        processed_dir = os.path.join(self.base_dir, 'processed')
        
        # 保存清洗後的價格數據
        cleaned_path = os.path.join(processed_dir, 'cleaned_prices_2010_2025.csv')
        data.to_csv(cleaned_path)
        logger.info(f"清洗後數據已保存至：{cleaned_path}")
        
        # 保存技術指標
        indicators_path = os.path.join(processed_dir, 'technical_indicators_2010_2025.csv')
        
        # 將指標轉換為 DataFrame
        indicators_df = pd.DataFrame()
        for asset, asset_indicators in indicators.items():
            for indicator_name, indicator_data in asset_indicators.items():
                indicators_df[f"{asset}_{indicator_name}"] = indicator_data
        
        indicators_df.to_csv(indicators_path)
        logger.info(f"技術指標已保存至：{indicators_path}")
        
        # 保存回報率數據
        returns_path = os.path.join(processed_dir, 'returns_2010_2025.csv')
        returns_df = data.pct_change()
        returns_df.to_csv(returns_path)
        logger.info(f"回報率數據已保存至：{returns_path}")
    
    def run_collection(self):
        """執行完整的數據收集流程"""
        logger.info("🚀 開始執行數據收集系統")
        
        # 步驟 1：設置目錄
        self.setup_directories()
        
        # 步驟 2：獲取數據
        price_data = self.fetch_price_data()
        
        if price_data is None:
            logger.error("❌ 數據獲取失敗，停止執行")
            return False
        
        # 步驟 3：驗證數據品質
        quality_report = self.validate_data_quality(price_data)
        logger.info(f"數據完整性：{quality_report['data_completeness']}")
        
        # 步驟 4：清洗數據
        cleaned_data = self.clean_data(price_data)
        
        # 步驟 5：保存原始數據
        self.save_data(price_data, 'asset_prices_2010_2025.csv')
        
        # 步驟 6：計算技術指標
        indicators = self.calculate_technical_indicators(cleaned_data)
        
        # 步驟 7：保存處理後數據
        self.save_processed_data(cleaned_data, indicators)
        
        logger.info("🎉 數據收集系統執行完成")
        return True

def main():
    """主函數"""
    system = DataCollectionSystem()
    success = system.run_collection()
    
    if success:
        logger.info("✅ 數據收集任務成功完成")
        return 0
    else:
        logger.error("❌ 數據收集任務失敗")
        return 1

if __name__ == "__main__":
    exit(main())