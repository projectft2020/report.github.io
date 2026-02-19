# 數據收集與準備報告

**研究日期：** 2026-02-17  
**狀態：** 準備階段，等待執行  
**優先級：** 高（策略執行的基礎）  

---

## 🎯 數據需求概述

### 策略所需資產
根據跨資產動能策略，我們需要收集以下四個核心資產的歷史數據：

| 資產 | 代碼 | 資產類別 | 數據需求 | 特殊要求 |
|------|------|----------|----------|----------|
| 納斯達克100 | QQQ | 股票ETF | 每日價格數據 | 需要股息調整 |
| 黃金ETF | GLD | 商品ETF | 每日價格數據 | 商品特性 |
| 美元指數ETF | UUP | 貨幣ETF | 每日價格數據 | 匯率影響 |
| 長期公債ETF | TLT | 債券ETF | 每日價格數據 | 利率敏感性 |

### 數據時間範圍
- **開始日期**：2010-01-01（16 年歷史數據）
- **結束日期**：2025-12-31（最近完整年）
- **更新頻率**：每日更新（用於即時策略）

---

## 📊 數據源分析

### 1. 主要數據源評估

#### Yahoo Finance API
**優點：**
- ✅ 完全免費
- ✅ 歷史數據完整（可追溯到 1970 年代）
- ✅ 支援股息和拆分調整
- ✅ Python 集成容易（yfinance 套件）
- ✅ 每日更新及時

**缺點：**
- ❌ 有速率限制（每分鐘約 2000 次請求）
- ❌ 商業使用限制
- ❌ 可能偶爾服務中斷

**適用性：** ⭐⭐⭐⭐⭐（完全滿足研究需求）

#### Alpha Vantage
**優點：**
- ✅ 免費層可用
- ✅ API 文檔完整
- ✅ 支援多種指標

**缺點：**
- ❌ 免費層限制嚴格（每分鐘 5 次請求）
- ❌ 歷史數據長度限制
- ❌ 需要 API key

**適用性：** ⭐⭐（僅適合作為備用）

#### Polygon.io
**優點：**
- ✅ 專業級金融數據
- ✅ 低延遲實時數據
- ✅ 高品質歷史數據
- ✅ 完整的公司行動數據

**缺點：**
- ❌ 付費服務（月費 $99+）
- ❌ 對研究用途可能過度

**適用性：** ⭐⭐⭐（預算允許可考慮）

#### Bloomberg Terminal
**優點：**
- ✅ 業界標準
- ✅ 最完整最準確的數據
- ✅ 即時更新

**缺點：**
- ❌ 非常昂貴（年費 $24,000+）
- ❌ 需要專門的軟體和設備

**適用性：** ⭐（研究階段不適用）

### 2. 最終數據源選擇

**主要數據源：** Yahoo Finance API + yfinance

**原因：**
1. **成本效益**：完全免費，符合研究預算
2. **數據品質**：對於回測研究完全足夠
3. **獲取便利性**：Python 集成簡單
4. **歷史長度**：16 年數據完整可用
5. **更新頻率**：每日更新滿足需求

**備用方案：** Alpha Vantage（當 Yahoo Finance 服務中斷時）

---

## 🔧 數據獲取技術實作

### 1. yfinance 套件安裝與配置

#### 安裝步驟
```bash
# 安裝 yfinance
pip install yfinance

# 安裝相關依賴
pip install pandas
pip install numpy
pip install matplotlib
```

#### 環境檢查
```python
import yfinance as yf
import pandas as pd
import numpy as np

print(f"yfinance 版本：{yf.__version__}")
print(f"pandas 版本：{pd.__version__}")
print(f"numpy 版本：{np.__version__}")
```

### 2. 數據獲取函數設計

#### 基礎數據獲取函數
```python
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def fetch_price_data(tickers, start_date, end_date):
    """
    獲取指定資產的歷史價格數據
    
    Args:
        tickers (list): 資產代碼列表
        start_date (str): 開始日期 'YYYY-MM-DD'
        end_date (str): 結束日期 'YYYY-MM-DD'
    
    Returns:
        pd.DataFrame: 包含調整後收盤價的數據框
    """
    print(f"正在獲取 {len(tickers)} 個資產的數據...")
    print(f"時間範圍：{start_date} 到 {end_date}")
    
    try:
        # 下載數據
        data = yf.download(tickers, 
                         start=start_date, 
                         end=end_date,
                         progress=True)
        
        # 提取調整後收盤價
        adj_close = data['Adj Close']
        
        # 檢查數據完整性
        print(f"成功獲取數據，形狀：{adj_close.shape}")
        print(f"資產列表：{list(adj_close.columns)}")
        print(f"日期範圍：{adj_close.index[0]} 到 {adj_close.index[-1]}")
        
        return adj_close
        
    except Exception as e:
        print(f"數據獲取失敗：{str(e)}")
        return None

def get_ticker_info(ticker):
    """
    獲取單個資產的基本資訊
    
    Args:
        ticker (str): 資產代碼
    
    Returns:
        dict: 資產基本資訊
    """
    try:
        ticker_obj = yf.Ticker(ticker)
        info = ticker_obj.info
        
        relevant_info = {
            'symbol': info.get('symbol', 'N/A'),
            'name': info.get('longName', 'N/A'),
            'category': info.get('category', 'N/A'),
            'expense_ratio': info.get('expenseRatio', 'N/A'),
            'assets_under_management': info.get('totalAssets', 'N/A'),
            'inception_date': info.get('inceptionDate', 'N/A')
        }
        
        return relevant_info
        
    except Exception as e:
        print(f"獲取 {ticker} 資訊失敗：{str(e)}")
        return None
```

#### 高級數據獲取函數
```python
def fetch_complete_data(tickers, start_date, end_date):
    """
    獲取完整的 OHLCV 數據（包含開高低收、成交量）
    
    Args:
        tickers (list): 資產代碼列表
        start_date (str): 開始日期
        end_date (str): 結束日期
    
    Returns:
        dict: 包含完整數據的字典
    """
    try:
        # 下載完整數據
        data = yf.download(tickers, 
                         start=start_date, 
                         end=end_date,
                         group_by='ticker')
        
        # 組織數據結構
        complete_data = {}
        
        for ticker in tickers:
            ticker_data = data[ticker]
            complete_data[ticker] = {
                'Open': ticker_data['Open'],
                'High': ticker_data['High'],
                'Low': ticker_data['Low'],
                'Close': ticker_data['Close'],
                'Adj Close': ticker_data['Adj Close'],
                'Volume': ticker_data['Volume']
            }
        
        return complete_data
        
    except Exception as e:
        print(f"完整數據獲取失敗：{str(e)}")
        return None

def fetch_dividend_data(tickers, start_date, end_date):
    """
    獲取股息數據
    
    Args:
        tickers (list): 資產代碼列表
        start_date (str): 開始日期
        end_date (str): 結束日期
    
    Returns:
        dict: 股息數據字典
    """
    dividend_data = {}
    
    for ticker in tickers:
        try:
            ticker_obj = yf.Ticker(ticker)
            dividends = ticker_obj.dividends[start_date:end_date]
            dividend_data[ticker] = dividends
            
            print(f"{ticker} 股息數據：{len(dividends)} 筆記錄")
            
        except Exception as e:
            print(f"獲取 {ticker} 股息數據失敗：{str(e)}")
            dividend_data[ticker] = pd.Series()
    
    return dividend_data
```

### 3. 數據驗證與品質檢查

#### 數據完整性檢查
```python
def validate_data_quality(data):
    """
    驗證數據品質
    
    Args:
        data (pd.DataFrame): 價格數據
    
    Returns:
        dict: 品質檢查結果
    """
    quality_report = {
        'data_shape': data.shape,
        'missing_values': data.isnull().sum().to_dict(),
        'date_range': {
            'start': data.index.min(),
            'end': data.index.max(),
            'total_days': len(data)
        },
        'assets': list(data.columns),
        'data_completeness': {},
        'trading_days_anomaly': {}
    }
    
    # 計算每個資產的數據完整性
    for asset in data.columns:
        asset_data = data[asset]
        completeness = (1 - asset_data.isnull().sum() / len(asset_data)) * 100
        quality_report['data_completeness'][asset] = completeness
        
        # 檢查異常交易天數
        trading_days = len(asset_data.dropna())
        expected_days = len(data)
        if trading_days < expected_days * 0.95:  # 少於 95% 預期天數
            quality_report['trading_days_anomaly'][asset] = {
                'actual': trading_days,
                'expected': expected_days,
                'ratio': trading_days / expected_days
            }
    
    return quality_report

def detect_data_anomalies(data):
    """
    檢測數據異常
    
    Args:
        data (pd.DataFrame): 價格數據
    
    Returns:
        dict: 異常檢測結果
    """
    anomalies = {
        'zero_prices': {},
        'negative_prices': {},
        'extreme_returns': {},
        'gaps': {}
    }
    
    for asset in data.columns:
        asset_data = data[asset].dropna()
        
        # 零價格檢測
        zero_prices = asset_data[asset_data == 0]
        if len(zero_prices) > 0:
            anomalies['zero_prices'][asset] = len(zero_prices)
        
        # 負價格檢測
        negative_prices = asset_data[asset_data < 0]
        if len(negative_prices) > 0:
            anomalies['negative_prices'][asset] = len(negative_prices)
        
        # 極端回報檢測（超過 ±20%）
        returns = asset_data.pct_change().dropna()
        extreme_returns = returns[(returns > 0.2) | (returns < -0.2)]
        if len(extreme_returns) > 0:
            anomalies['extreme_returns'][asset] = {
                'count': len(extreme_returns),
                'max': returns.max(),
                'min': returns.min()
            }
        
        # 價格跳空檢測（超過 10%）
        price_gaps = returns[returns.abs() > 0.1]
        if len(price_gaps) > 0:
            anomalies['gaps'][asset] = len(price_gaps)
    
    return anomalies
```

### 4. 數據清洗與預處理

#### 數據清洗函數
```python
def clean_price_data(data):
    """
    清洗價格數據
    
    Args:
        data (pd.DataFrame): 原始價格數據
    
    Returns:
        pd.DataFrame: 清洗後的價格數據
    """
    cleaned_data = data.copy()
    
    # 1. 處理缺失值 - 前向填充
    cleaned_data = cleaned_data.fillna(method='ffill')
    
    # 2. 再次處理剩餘缺失值 - 後向填充
    cleaned_data = cleaned_data.fillna(method='bfill')
    
    # 3. 確保沒有 NaN 值
    if cleaned_data.isnull().any().any():
        print("⚠️  警告：仍有缺失值存在")
        # 填充剩餘缺失值為 0（如果還有的話）
        cleaned_data = cleaned_data.fillna(0)
    
    print(f"數據清洗完成，形狀：{cleaned_data.shape}")
    return cleaned_data

def calculate_technical_indicators(data):
    """
    計算技術指標
    
    Args:
        data (pd.DataFrame): 價格數據
    
    Returns:
        dict: 技術指標字典
    """
    indicators = {}
    
    for asset in data.columns:
        asset_data = data[asset].dropna()
        
        if len(asset_data) < 20:  # 需要足夠數據計算指標
            continue
        
        # 計算各種技術指標
        indicators[asset] = {
            'sma_20': asset_data.rolling(window=20).mean(),
            'sma_50': asset_data.rolling(window=50).mean(),
            'sma_200': asset_data.rolling(window=200).mean(),
            'returns_1d': asset_data.pct_change(),
            'returns_5d': asset_data.pct_change(5),
            'returns_21d': asset_data.pct_change(21),
            'volatility_21d': asset_data.pct_change().rolling(window=21).std() * np.sqrt(21),
            'rsi_14': calculate_rsi(asset_data, 14)
        }
    
    return indicators

def calculate_rsi(prices, period=14):
    """
    計算 RSI 指標
    
    Args:
        prices (pd.Series): 價格序列
        period (int): RSI 週期
    
    Returns:
        pd.Series: RSI 值
    """
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi
```

---

## 📈 數據收集執行計畫

### 1. 第一階段：核心資產數據獲取

#### 執行步驟
```python
# 第一步：定義參數
tickers = ['QQQ', 'GLD', 'UUP', 'TLT']
start_date = '2010-01-01'
end_date = '2025-12-31'

# 第二步：獲取基本資訊
print("=== 資產基本資訊 ===")
asset_info = {}
for ticker in tickers:
    info = get_ticker_info(ticker)
    asset_info[ticker] = info
    print(f"{ticker}: {info['name'] if info else 'N/A'}")

# 第三步：獲取價格數據
print("\n=== 獲取價格數據 ===")
price_data = fetch_price_data(tickers, start_date, end_date)

if price_data is not None:
    # 第四步：數據品質檢查
    print("\n=== 數據品質檢查 ===")
    quality_report = validate_data_quality(price_data)
    print(f"數據形狀：{quality_report['data_shape']}")
    print(f"數據完整性：{quality_report['data_completeness']}")
    
    # 第五步：異常檢測
    print("\n=== 異常檢測 ===")
    anomalies = detect_data_anomalies(price_data)
    print(f"零價格異常：{anomalies['zero_prices']}")
    print(f"負價格異常：{anomalies['negative_prices']}")
    
    # 第六步：數據清洗
    print("\n=== 數據清洗 ===")
    cleaned_data = clean_price_data(price_data)
    
    # 第七步：保存數據
    print("\n=== 保存數據 ===")
    cleaned_data.to_csv('/Users/charlie/.openclaw/workspace/quant/data/asset_prices_2010_2025.csv')
    print("數據已保存至 asset_prices_2010_2025.csv")
    
    # 第八步：計算技術指標
    print("\n=== 計算技術指標 ===")
    indicators = calculate_technical_indicators(cleaned_data)
    print("技術指標計算完成")

else:
    print("數據獲取失敗，請檢查網路連接和參數設定")
```

### 2. 第二階段：補充數據獲取

#### 額外數據源
```python
def fetch_supplementary_data():
    """獲取補充數據（市場指標、經濟數據等）"""
    
    # 獲取市場指標數據
    market_tickers = ['SPY', 'DIA', 'IWM']  # 市場基準
    market_data = fetch_price_data(market_tickers, start_date, end_date)
    
    # 獲取波動率指數
    vix_data = fetch_price_data(['^VIX'], start_date, end_date)
    
    # 獲取利率數據（10年期國債收益率）
    # 注意：這可能需要使用其他數據源
    
    return {
        'market_data': market_data,
        'vix_data': vix_data
    }

def fetch_macro_data():
    """獲取宏觀經濟數據"""
    
    # 這裡可以添加 FRED 等宏觀數據源的獲取
    # 目前先返回空字典，可以後續擴展
    
    macro_data = {
        'interest_rates': None,  # 利率數據
        'inflation': None,        # 通膨數據
        'gdp': None,             # GDP 數據
        'unemployment': None     # 失業率數據
    }
    
    return macro_data
```

---

## 💾 數據存儲方案

### 1. 本地存儲結構

#### 目錄結構設計
```
/Users/charlie/.openclaw/workspace/quant/data/
├── raw/                          # 原始數據
│   ├── asset_prices_2010_2025.csv
│   ├── dividends_2010_2025.csv
│   └── market_indicators_2010_2025.csv
├── processed/                    # 處理後數據
│   ├── cleaned_prices_2010_2025.csv
│   ├── returns_2010_2025.csv
│   ├── technical_indicators_2010_2025.csv
│   └── momentum_scores_2010_2025.csv
├── cache/                        # 快取數據
│   ├── yfinance_cache/
│   └── indicator_cache/
└── metadata/                     # 元數據
    ├── data_sources.json
    ├── data_quality_report.json
    └── update_log.json
```

#### 數據存儲函數
```python
import os
import json
from datetime import datetime

def setup_data_directory():
    """設置數據目錄結構"""
    base_dir = '/Users/charlie/.openclaw/workspace/quant/data'
    
    directories = [
        'raw',
        'processed', 
        'cache',
        'cache/yfinance_cache',
        'cache/indicator_cache',
        'metadata'
    ]
    
    for directory in directories:
        dir_path = os.path.join(base_dir, directory)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"創建目錄：{dir_path}")
    
    return base_dir

def save_data_with_metadata(data, filename, data_type='raw', metadata=None):
    """
    保存數據並包含元數據
    
    Args:
        data (pd.DataFrame): 要保存的數據
        filename (str): 文件名
        data_type (str): 數據類型
        metadata (dict): 元數據
    """
    base_dir = setup_data_directory()
    
    # 確定保存路徑
    if data_type == 'raw':
        save_path = os.path.join(base_dir, 'raw', filename)
    elif data_type == 'processed':
        save_path = os.path.join(base_dir, 'processed', filename)
    else:
        save_path = os.path.join(base_dir, filename)
    
    # 保存主數據
    data.to_csv(save_path)
    print(f"數據已保存至：{save_path}")
    
    # 保存元數據
    if metadata is None:
        metadata = {
            'filename': filename,
            'data_type': data_type,
            'shape': data.shape,
            'columns': list(data.columns),
            'date_range': {
                'start': str(data.index[0]),
                'end': str(data.index[-1])
            },
            'save_time': datetime.now().isoformat()
        }
    
    metadata_path = os.path.join(base_dir, 'metadata', f"{filename}_metadata.json")
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    print(f"元數據已保存至：{metadata_path}")

def load_data_with_metadata(filename, data_type='raw'):
    """
    載入數據和元數據
    
    Args:
        filename (str): 文件名
        data_type (str): 數據類型
    
    Returns:
        tuple: (數據, 元數據)
    """
    base_dir = '/Users/charlie/.openclaw/workspace/quant/data'
    
    # 確定載入路徑
    if data_type == 'raw':
        load_path = os.path.join(base_dir, 'raw', filename)
    elif data_type == 'processed':
        load_path = os.path.join(base_dir, 'processed', filename)
    else:
        load_path = os.path.join(base_dir, filename)
    
    # 載入主數據
    if os.path.exists(load_path):
        data = pd.read_csv(load_path, index_col=0, parse_dates=True)
        print(f"數據已載入：{load_path}")
    else:
        print(f"數據文件不存在：{load_path}")
        return None, None
    
    # 載入元數據
    metadata_path = os.path.join(base_dir, 'metadata', f"{filename}_metadata.json")
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        print(f"元數據已載入：{metadata_path}")
    else:
        metadata = None
    
    return data, metadata
```

---

## 🔄 數據更新策略

### 1. 自動化更新機制

#### 更新調度函數
```python
def schedule_daily_updates():
    """設置每日數據更新"""
    
    import schedule
    import time
    
    def update_data():
        """更新數據函數"""
        print(f"開執行每日數據更新：{datetime.now()}")
        
        try:
            # 載入現有數據
            existing_data, metadata = load_data_with_metadata(
                'asset_prices_2010_2025.csv', 'raw'
            )
            
            if existing_data is not None:
                # 計算需要更新的日期範圍
                last_date = existing_data.index[-1]
                start_date = (last_date + timedelta(days=1)).strftime('%Y-%m-%d')
                end_date = datetime.now().strftime('%Y-%m-%d')
                
                if start_date <= end_date:
                    print(f"更新數據：{start_date} 到 {end_date}")
                    
                    # 獲取新數據
                    new_data = fetch_price_data(['QQQ', 'GLD', 'UUP', 'TLT'], 
                                              start_date, end_date)
                    
                    if new_data is not None:
                        # 合併數據
                        updated_data = pd.concat([existing_data, new_data])
                        
                        # 保存更新後的數據
                        save_data_with_metadata(
                            updated_data, 
                            'asset_prices_2010_2025.csv',
                            'raw',
                            metadata={
                                'last_update': datetime.now().isoformat(),
                                'update_type': 'daily_append',
                                'new_records': len(new_data)
                            }
                        )
                        
                        print("數據更新完成")
                    else:
                        print("新數據獲取失敗")
                else:
                    print("數據已經是最新的")
            else:
                print("無法載入現有數據")
                
        except Exception as e:
            print(f"數據更新失敗：{str(e)}")
    
    # 設置調度
    schedule.every().day.at("18:00").do(update_data)  # 每天 18:00 更新
    
    print("每日數據更新調度已設置")
    print("按 Ctrl+C 停止調度")
    
    # 運行調度
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分鐘檢查一次
```

#### 手動更新函數
```python
def manual_data_update(start_date=None, end_date=None):
    """
    手動更新數據
    
    Args:
        start_date (str): 開始日期，預設為昨天
        end_date (str): 結束日期，預設為今天
    """
    
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    print(f"手動更新數據：{start_date} 到 {end_date}")
    
    # 載入現有數據
    existing_data, metadata = load_data_with_metadata(
        'asset_prices_2010_2025.csv', 'raw'
    )
    
    if existing_data is not None:
        # 檢查是否需要更新
        last_date = existing_data.index[-1]
        update_start = max(start_date, (last_date + timedelta(days=1)).strftime('%Y-%m-%d'))
        
        if update_start <= end_date:
            # 獲取新數據
            new_data = fetch_price_data(['QQQ', 'GLD', 'UUP', 'TLT'], 
                                      update_start, end_date)
            
            if new_data is not None:
                # 合併數據
                updated_data = pd.concat([existing_data, new_data])
                
                # 保存更新後的數據
                save_data_with_metadata(
                    updated_data, 
                    'asset_prices_2010_2025.csv',
                    'raw',
                    metadata={
                        'last_update': datetime.now().isoformat(),
                        'update_type': 'manual',
                        'update_range': f"{update_start} to {end_date}",
                        'new_records': len(new_data)
                    }
                )
                
                print("手動更新完成")
                return True
            else:
                print("新數據獲取失敗")
                return False
        else:
            print("數據已經是最新的，無需更新")
            return True
    else:
        print("無法載入現有數據")
        return False
```

---

## 📊 數據品質監控

### 1. 品質監控儀表板

#### 監控指標設計
```python
def create_quality_dashboard(data):
    """
    創建數據品質監控儀表板
    
    Args:
        data (pd.DataFrame): 價格數據
    """
    
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    # 設置圖表樣式
    plt.style.use('seaborn-v0_8')
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # 1. 數據完整性圖
    completeness = (data.count() / len(data) * 100).sort_values(ascending=False)
    axes[0, 0].bar(completeness.index, completeness.values, color='skyblue')
    axes[0, 0].set_title('數據完整性 (%)')
    axes[0, 0].set_ylabel('完整性 (%)')
    axes[0, 0].tick_params(axis='x', rotation=45)
    
    # 2. 價格趨勢圖
    for asset in data.columns:
        axes[0, 1].plot(data.index, data[asset], label=asset, alpha=0.7)
    axes[0, 1].set_title('價格趨勢')
    axes[0, 1].set_ylabel('價格')
    axes[0, 1].legend()
    axes[0, 1].tick_params(axis='x', rotation=45)
    
    # 3. 日回報率分佈
    returns = data.pct_change().dropna()
    for i, asset in enumerate(returns.columns):
        axes[1, 0].hist(returns[asset], alpha=0.5, bins=50, label=asset)
    axes[1, 0].set_title('日回報率分佈')
    axes[1, 0].set_xlabel('日回報率')
    axes[1, 0].set_ylabel('頻率')
    axes[1, 0].legend()
    
    # 4. 相關性熱力圖
    correlation_matrix = returns.corr()
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, 
                square=True, ax=axes[1, 1])
    axes[1, 1].set_title('資產相關性矩陣')
    
    plt.tight_layout()
    plt.savefig('/Users/charlie/.openclaw/workspace/quant/data/quality_dashboard.png', 
                dpi=300, bbox_inches='tight')
    plt.show()
    
    print("品質監控儀表板已保存：quality_dashboard.png")

def generate_quality_report(data):
    """
    生成詳細品質報告
    
    Args:
        data (pd.DataFrame): 價格數據
    
    Returns:
        dict: 詳細品質報告
    """
    
    report = {
        'summary': {},
        'detailed_analysis': {},
        'recommendations': []
    }
    
    # 基本統計
    report['summary']['total_records'] = len(data)
    report['summary']['total_assets'] = len(data.columns)
    report['summary']['date_range'] = {
        'start': str(data.index[0]),
        'end': str(data.index[-1]),
        'days': (data.index[-1] - data.index[0]).days
    }
    
    # 詳細分析
    for asset in data.columns:
        asset_data = data[asset].dropna()
        
        report['detailed_analysis'][asset] = {
            'total_records': len(asset_data),
            'missing_records': len(data) - len(asset_data),
            'completeness_pct': (len(asset_data) / len(data)) * 100,
            'start_date': str(asset_data.index[0]),
            'end_date': str(asset_data.index[-1]),
            'min_price': float(asset_data.min()),
            'max_price': float(asset_data.max()),
            'avg_price': float(asset_data.mean()),
            'price_change_pct': float((asset_data.iloc[-1] / asset_data.iloc[0] - 1) * 100)
        }
    
    # 建議
    completeness_scores = [analysis['completeness_pct'] 
                          for analysis in report['detailed_analysis'].values()]
    
    if min(completeness_scores) < 95:
        report['recommendations'].append(
            "⚠️  部分資產數據完整性低於 95%，建議檢查數據源"
        )
    
    if max(completeness_scores) < 99:
        report['recommendations'].append(
            "💡 建議實施自動化數據補充機制"
        )
    
    report['recommendations'].append(
        "✅ 建議設置每日自動數據更新"
    )
    
    return report
```

---

## 🎯 執行檢查清單

### 第一階段：環境準備
- [ ] 確認 Python 環境
- [ ] 安裝 yfinance 和相關套件
- [ ] 設置數據目錄結構
- [ ] 測試網路連接

### 第二階段：數據獲取
- [ ] 獲取資產基本資訊
- [ ] 下載歷史價格數據
- [ ] 驗證數據完整性
- [ ] 檢測數據異常

### 第三階段：數據處理
- [ ] 數據清洗和預處理
- [ ] 計算技術指標
- [ ] 生成品質報告
- [ ] 保存處理後數據

### 第四階段：系統整合
- [ ] 與 Matrix 系統整合
- [ ] 設置自動更新機制
- [ ] 建立監控儀表板
- [ ] 文檔和測試

---

**報告完成日期：** 2026-02-17  
**下次更新：** 數據收集完成後（預計 2026-02-18）  
**負責人：** Charlie (AI Assistant)  
**審核：** David (Researcher)  
**優先級：** 高 🟡