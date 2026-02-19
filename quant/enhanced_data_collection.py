#!/usr/bin/env python3
"""
強化的量化交易數據收集系統
包含：錯誤處理、狀態追蹤、自動恢復
"""

import yfinance as yf
import pandas as pd
import numpy as np
import os
import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/Users/charlie/.openclaw/workspace/quant/data_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedDataCollectionSystem:
    """強化的數據收集系統"""
    
    def __init__(self):
        self.base_dir = Path('/Users/charlie/.openclaw/workspace/quant/data')
        self.tickers = ['QQQ', 'GLD', 'UUP', 'TLT']
        self.start_date = '2010-01-01'
        self.end_date = '2025-12-31'
        self.checkpoint_file = self.base_dir / 'metadata' / 'collection_checkpoint.json'
        self.state = self.load_checkpoint()
        
    def setup_directories(self):
        """設置必要的目錄"""
        directories = ['raw', 'processed', 'cache', 'metadata']
        
        for directory in directories:
            dir_path = self.base_dir / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"目錄確認：{dir_path}")
    
    def safe_execute_with_retry(self, func, max_retries=3, initial_delay=1):
        """安全執行函數，帶重試和指數退避"""
        for attempt in range(max_retries):
            try:
                result = func()
                return result, True
            except Exception as e:
                logger.error(f"執行失敗 (嘗試 {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    delay = initial_delay * (2 ** attempt)  # 指數退避
                    logger.info(f"等待 {delay} 秒後重試...")
                    time.sleep(delay)
                else:
                    logger.error("達到最大重試次數，放棄執行")
                    return None, False
    
    def download_price_data(self):
        """下載價格數據"""
        logger.info(f"開始下載 {len(self.tickers)} 個資產的價格數據")
        
        def download_attempt():
            # 設置 yfinance 快取目錄
            cache_dir = Path('/tmp/yfinance_cache')
            cache_dir.mkdir(exist_ok=True)
            os.environ['YFINANCE_CACHE_DIR'] = str(cache_dir)
            
            # 下載數據
            data = yf.download(
                self.tickers,
                start=self.start_date,
                end=self.end_date,
                progress=False,
                auto_adjust=False
            )
            
            # 提取調整後收盤價
            if 'Adj Close' in data.columns:
                adj_close = data['Adj Close']
            else:
                adj_close = data['Close']  # 如果沒有 Adj Close，使用 Close
                
            logger.info(f"下載成功：數據形狀 {adj_close.shape}")
            return adj_close
        
        # 使用安全執行
        price_data, success = self.safe_execute_with_retry(download_attempt)
        
        if not success:
            raise Exception("無法下載價格數據")
        
        return price_data
    
    def validate_and_clean_data(self, data):
        """驗證和清洗數據"""
        logger.info("開始驗證和清洗數據")
        
        # 基本驗證
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
        
        # 計算完整性
        for asset in data.columns:
            asset_data = data[asset]
            completeness = (1 - asset_data.isnull().sum() / len(asset_data)) * 100
            quality_report['data_completeness'][asset] = completeness
            logger.info(f"{asset} 數據完整性：{completeness:.1f}%")
        
        # 清洗數據
        cleaned_data = data.copy()
        
        # 前向填充
        cleaned_data = cleaned_data.fillna(method='ffill')
        # 後向填充
        cleaned_data = cleaned_data.fillna(method='bfill')
        # 最後填充剩餘的 NaN
        cleaned_data = cleaned_data.fillna(0)
        
        logger.info(f"數據清洗完成：形狀 {cleaned_data.shape}")
        return cleaned_data, quality_report
    
    def calculate_technical_indicators(self, data):
        """計算技術指標"""
        logger.info("計算技術指標")
        
        indicators = {}
        
        for asset in data.columns:
            asset_data = data[asset].dropna()
            
            if len(asset_data) < 20:
                continue
                
            try:
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
                
            except Exception as e:
                logger.warning(f"計算 {asset} 技術指標時出錯：{str(e)}")
        
        logger.info("技術指標計算完成")
        return indicators
    
    def save_all_data(self, price_data, cleaned_data, indicators, quality_report):
        """保存所有數據"""
        logger.info("保存所有數據")
        
        # 保存原始數據
        raw_path = self.base_dir / 'raw' / 'asset_prices_2010_2025.csv'
        price_data.to_csv(raw_path)
        logger.info(f"原始數據已保存：{raw_path}")
        
        # 保存清洗後數據
        cleaned_path = self.base_dir / 'processed' / 'cleaned_prices_2010_2025.csv'
        cleaned_data.to_csv(cleaned_path)
        logger.info(f"清洗後數據已保存：{cleaned_path}")
        
        # 保存技術指標
        if indicators:
            indicators_df = pd.DataFrame()
            for asset, asset_indicators in indicators.items():
                for indicator_name, indicator_data in asset_indicators.items():
                    indicators_df[f"{asset}_{indicator_name}"] = indicator_data
            
            indicators_path = self.base_dir / 'processed' / 'technical_indicators_2010_2025.csv'
            indicators_df.to_csv(indicators_path)
            logger.info(f"技術指標已保存：{indicators_path}")
        
        # 保存回報率數據
        returns_df = cleaned_data.pct_change()
        returns_path = self.base_dir / 'processed' / 'returns_2010_2025.csv'
        returns_df.to_csv(returns_path)
        logger.info(f"回報率數據已保存：{returns_path}")
        
        # 保存品質報告
        quality_path = self.base_dir / 'metadata' / 'data_quality_report.json'
        with open(quality_path, 'w', encoding='utf-8') as f:
            json.dump(quality_report, f, ensure_ascii=False, indent=2)
        logger.info(f"品質報告已保存：{quality_path}")
    
    def update_checkpoint(self, stage, status='completed'):
        """更新執行檢查點"""
        self.state[stage] = {
            'timestamp': datetime.now().isoformat(),
            'status': status
        }
        
        # 保存檢查點
        self.checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)
        
        logger.info(f"檢查點更新：{stage} - {status}")
    
    def load_checkpoint(self):
        """載入檢查點"""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def get_next_stage(self):
        """獲取下一個要執行的階段"""
        stages = [
            'setup_directories',
            'download_price_data', 
            'validate_and_clean_data',
            'calculate_technical_indicators',
            'save_all_data'
        ]
        
        for stage in stages:
            if stage not in self.state or self.state[stage]['status'] != 'completed':
                return stage
        
        return None  # 所有階段都已完成
    
    def run_collection(self):
        """執行數據收集流程"""
        logger.info("🚀 開始執行強化數據收集系統")
        
        try:
            # 階段 1：設置目錄
            if 'setup_directories' not in self.state:
                self.update_checkpoint('setup_directories', 'running')
                self.setup_directories()
                self.update_checkpoint('setup_directories', 'completed')
            
            # 階段 2：下載價格數據
            if 'download_price_data' not in self.state:
                self.update_checkpoint('download_price_data', 'running')
                price_data = self.download_price_data()
                self.update_checkpoint('download_price_data', 'completed')
            else:
                # 如果已經下載，載入現有數據
                raw_path = self.base_dir / 'raw' / 'asset_prices_2010_2025.csv'
                if raw_path.exists():
                    price_data = pd.read_csv(raw_path, index_col=0, parse_dates=True)
                    logger.info(f"載入現有價格數據：{price_data.shape}")
                else:
                    price_data = self.download_price_data()
            
            # 階段 3：驗證和清洗數據
            if 'validate_and_clean_data' not in self.state:
                self.update_checkpoint('validate_and_clean_data', 'running')
                cleaned_data, quality_report = self.validate_and_clean_data(price_data)
                self.update_checkpoint('validate_and_clean_data', 'completed')
            else:
                cleaned_data = price_data  # 如果已經清洗，直接使用
                quality_report = {}  # 可以載入現有品質報告
            
            # 階段 4：計算技術指標
            if 'calculate_technical_indicators' not in self.state:
                self.update_checkpoint('calculate_technical_indicators', 'running')
                indicators = self.calculate_technical_indicators(cleaned_data)
                self.update_checkpoint('calculate_technical_indicators', 'completed')
            else:
                indicators = {}  # 可以載入現有指標
            
            # 階段 5：保存所有數據
            if 'save_all_data' not in self.state:
                self.update_checkpoint('save_all_data', 'running')
                self.save_all_data(price_data, cleaned_data, indicators, quality_report)
                self.update_checkpoint('save_all_data', 'completed')
            
            logger.info("🎉 強化數據收集系統執行完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 數據收集失�敗：{str(e)}")
            # 保存錯誤狀態
            current_stage = self.get_next_stage()
            if current_stage:
                self.update_checkpoint(current_stage, 'failed')
            return False

def main():
    """主函數"""
    system = EnhancedDataCollectionSystem()
    success = system.run_collection()
    
    if success:
        logger.info("✅ 強化數據收集任務成功完成")
        return 0
    else:
        logger.error("❌ 強化數據收集任務失敗")
        return 1

if __name__ == "__main__":
    exit(main())