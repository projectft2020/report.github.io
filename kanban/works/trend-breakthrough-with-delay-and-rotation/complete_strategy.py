#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
趨勢突破策略 - 結合延遲進場優化與板塊輪動

三層架構：
1. 板塊輪動（動態選擇強勢板塊）
2. 延遲進場（過濾假突破）
3. 動態倉位（ATR 風險控制）

作者：Charlie
日期：2026-03-06
"""

import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# 設置中文顯示
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

# ============================================
# 配置
# ============================================

# 板塊 ETF 列表
SECTOR_ETFS = {
    '科技': 'XLK',      # Technology Select Sector SPDR
    '金融': 'XLF',      # Financial Select Sector SPDR
    '醫療': 'XLV',      # Health Care Select Sector SPDR
    '消費': 'XLY',      # Consumer Discretionary Select Sector SPDR
    '必需消費': 'XLP',   # Consumer Staples Select Sector SPDR
    '能源': 'XLE',      # Energy Select Sector SPDR
    '工業': 'XLI',      # Industrial Select Sector SPDR
    '材料': 'XLB',      # Materials Select Sector SPDR
    '公用事業': 'XLU',   # Utilities Select Sector SPDR
    '房地產': 'XLRE',    # Real Estate Select Sector SPDR
    '市場基準': 'SPY'    # S&P 500 ETF
}

# 策略參數
STRATEGY_PARAMS = {
    'supertrend': {
        'period': 10,
        'multiplier': 3.0
    },
    'delayed_entry': {
        'delay_bars': 2,
        'confidence_threshold': 0.6
    },
    'atr': {
        'period': 14
    },
    'dynamic_position': {
        'risk_per_trade': 0.02,  # 每筆交易風險 2%
        'stop_loss_atr_multiplier': 2.0
    },
    'sector_rotation': {
        'lookback': 20,          # 20 天
        'top_n': 3,             # 選擇前 3 個強勢板塊
        'sector_weight_max': 0.3  # 單一板塊最大權重 30%
    }
}

# ============================================
# 第一部分：技術指標
# ============================================

def calculate_atr(high, low, close, period=14):
    """
    計算 ATR（Average True Range）
    
    參數：
    - high: 最高價序列
    - low: 最低價序列
    - close: 收盤價序列
    - period: 週期（默認 14）
    
    返回：
    - atr: ATR 序列
    """
    high = high.values
    low = low.values
    close = close.values
    
    # 計算 True Range
    tr1 = high - low
    tr2 = np.abs(high - np.roll(close, 1))
    tr3 = np.abs(low - np.roll(close, 1))
    
    tr = np.maximum(tr1, np.maximum(tr2, tr3))
    tr[0] = 0  # 第一天沒有 True Range
    
    # 計算 ATR（使用 Wilder's smoothing）
    atr = np.zeros(len(close))
    atr[0] = np.mean(tr[1:period+1]) if len(tr) > period else 0
    
    for i in range(1, len(atr)):
        if i >= period:
            atr[i] = (atr[i-1] * (period-1) + tr[i]) / period
        else:
            atr[i] = np.nan
    
    return pd.Series(atr, index=close.index)

def calculate_supertrend(high, low, close, period=10, multiplier=3.0):
    """
    計算 Supertrend 指標
    
    參數：
    - high: 最高價序列
    - low: 最低價序列
    - close: 收盤價序列
    - period: 週期
    - multiplier: 倍數
    
    返回：
    - supertrend: Supertrend 線
    - trend: 趨勢（1=上漲，0=下跌）
    """
    # 計算 ATR
    atr = calculate_atr(high, low, close, period=period)
    
    # 計算基本帶（Basic Bands）
    hl2 = (high + low) / 2
    
    upper_band = hl2 + multiplier * atr
    lower_band = hl2 - multiplier * atr
    
    # 初始化
    supertrend = [np.nan] * len(close)
    trend = [0] * len(close)
    
    supertrend[0] = lower_band.iloc[0]
    trend[0] = 1
    
    for i in range(1, len(close)):
        if trend[i-1] == 1:  # 當前是上漲趨勢
            if close.iloc[i] <= supertrend[i-1]:
                # 趨勢轉為下跌
                trend[i] = 0
                supertrend[i] = upper_band.iloc[i]
            else:
                # 維持上漲趨勢
                trend[i] = 1
                supertrend[i] = max(supertrend[i-1], lower_band.iloc[i])
        else:  # 當前是下跌趨勢
            if close.iloc[i] >= supertrend[i-1]:
                # 趨勢轉為上漲
                trend[i] = 1
                supertrend[i] = lower_band.iloc[i]
            else:
                # 維持下跌趨勢
                trend[i] = 0
                supertrend[i] = min(supertrend[i-1], upper_band.iloc[i])
    
    return pd.Series(supertrend, index=close.index), pd.Series(trend, index=close.index)

def calculate_rsi(close, period=14):
    """
    計算 RSI（Relative Strength Index）
    
    參數：
    - close: 收盤價序列
    - period: 週期
    
    返回：
    - rsi: RSI 序列
    """
    delta = close.diff()
    
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

def calculate_macd(close, fast=12, slow=26, signal=9):
    """
    計算 MACD
    
    參數：
    - close: 收盤價序列
    - fast: 快線週期
    - slow: 慢線週期
    - signal: 信號線週期
    
    返回：
    - macd: MACD 線
    - signal: 信號線
    - histogram: 柱狀圖
    """
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    histogram = macd - signal_line
    
    return macd, signal_line, histogram

# ============================================
# 第二部分：板塊輪動系統
# ============================================

class SectorRotationSystem:
    """板塊輪動系統"""
    
    def __init__(self, sector_etfs, lookback=20, top_n=3):
        """
        初始化板塊輪動系統
        
        參數：
        - sector_etfs: 板塊 ETF 字典
        - lookback: 回看天數
        - top_n: 選擇前 N 個強勢板塊
        """
        self.sector_etfs = sector_etfs
        self.lookback = lookback
        self.top_n = top_n
        self.sector_strengths = None
        self.current_weights = None
    
    def update_strengths(self, data):
        """
        更新板塊強度
        
        參數：
        - data: 數據字典 {ticker: DataFrame}
        """
        self.sector_strengths = {}
        
        for sector, ticker in self.sector_etfs.items():
            if ticker == 'SPY':
                continue  # 跳過市場基準
            
            if ticker not in data:
                continue
            
            df = data[ticker]
            
            # 計算指標
            strength = self._calculate_sector_metrics(df, data['SPY'])
            self.sector_strengths[sector] = strength
    
    def _calculate_sector_metrics(self, df, spy_df):
        """計算單個板塊的強度指標"""
        # 1. 累積收益（20 天）
        returns = df['Close'].pct_change()
        cumulative_return = (1 + returns.iloc[-self.lookback:]).prod() - 1
        
        # 2. 動量因子
        momentum = returns.mean() * np.sqrt(252) / returns.std()
        
        # 3. 相對強度（相對於 SPY）
        spy_returns = spy_df['Close'].pct_change()
        relative_strength = returns.mean() / spy_returns.mean()
        
        # 4. RSI（14 天）
        rsi = calculate_rsi(df['Close'], period=14)
        
        # 5. MACD
        macd, signal, histogram = calculate_macd(df['Close'])
        
        # 6. 綜合評分
        # 標準化各個指標到 0-1 範圍
        normalized_return = np.clip(cumulative_return / 0.1, 0, 1)  # 假設 10% 收益是滿分
        normalized_momentum = np.clip((momentum + 1) / 2, 0, 1)
        normalized_relative_strength = np.clip(relative_strength / 1.5, 0, 1)
        normalized_rsi = np.clip(rsi.iloc[-1] / 100, 0, 1)
        normalized_macd = 1 if histogram.iloc[-1] > 0 else 0
        
        # 權重分配
        strength_score = (
            0.3 * normalized_return +
            0.2 * normalized_momentum +
            0.2 * normalized_relative_strength +
            0.15 * normalized_rsi +
            0.15 * normalized_macd
        )
        
        return {
            'cumulative_return': cumulative_return,
            'momentum': momentum,
            'relative_strength': relative_strength,
            'rsi': rsi.iloc[-1],
            'macd_signal': histogram.iloc[-1],
            'strength_score': strength_score
        }
    
    def calculate_weights(self):
        """計算板塊權重"""
        if self.sector_strengths is None:
            raise ValueError("請先調用 update_strengths()")
        
        # 按強度排序
        sorted_sectors = sorted(
            self.sector_strengths.items(),
            key=lambda x: x[1]['strength_score'],
            reverse=True
        )
        
        # 選擇前 N 個板塊
        top_sectors = sorted_sectors[:self.top_n]
        
        # 計算權重
        total_score = sum(item[1]['strength_score'] for item in top_sectors)
        weights = {}
        
        for sector, strength in top_sectors:
            # 限制單一板塊最大權重
            raw_weight = strength['strength_score'] / total_score
            max_weight = STRATEGY_PARAMS['sector_rotation']['sector_weight_max']
            weight = min(raw_weight, max_weight)
            weights[sector] = weight
        
        # 重新歸一化（限制後）
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: v / total_weight * 0.6 for k, v in weights.items()}  # 60% 分配給強勢板塊
        
        # 剩餘 40% 分配給現金
        weights['現金'] = 0.4
        
        self.current_weights = weights
        return weights
    
    def get_top_sectors(self):
        """獲取強勢板塊"""
        if self.current_weights is None:
            self.calculate_weights()
        
        return [sector for sector, weight in self.current_weights.items() 
                if weight > 0 and sector != '現金']

# ============================================
# 第三部分：延遲進場系統
# ============================================

class DelayedEntrySystem:
    """延遲進場系統"""
    
    def __init__(self, delay_bars=2, confidence_threshold=0.6):
        """
        初始化延遲進場系統
        
        參數：
        - delay_bars: 延遲確認根數
        - confidence_threshold: 信號置信度閾值
        """
        self.delay_bars = delay_bars
        self.confidence_threshold = confidence_threshold
        self.pending_signals = {}
    
    def generate_signal(self, df, current_idx):
        """
        生成進場信號
        
        參數：
        - df: 數據 DataFrame（包含 High, Low, Close）
        - current_idx: 當前索引
        
        返回：
        - signal: 信號 {'long', 'short', 'hold'}
        - confidence: 置信度
        - false_break_prob: 假突破概率
        """
        # 計算 Supertrend
        supertrend, trend = calculate_supertrend(
            df['High'],
            df['Low'],
            df['Close'],
            period=STRATEGY_PARAMS['supertrend']['period'],
            multiplier=STRATEGY_PARAMS['supertrend']['multiplier']
        )
        
        # 檢測突破
        breakthrough_detected, direction = self._detect_breakthrough(
            df, current_idx, supertrend, trend
        )
        
        if breakthrough_detected:
            # 添加到待確認信號
            self.pending_signals[current_idx] = {
                'direction': direction,
                'initial_idx': current_idx,
                'initial_price': df['Close'].iloc[current_idx],
                'initial_supertrend': supertrend.iloc[current_idx]
            }
        
        # 確認信號
        confirmed_signals = self._confirm_signals(df, current_idx, supertrend, trend)
        
        # 返回當前信號
        if current_idx in confirmed_signals:
            return confirmed_signals[current_idx]
        else:
            return {
                'signal': 'hold',
                'confidence': 0.5,
                'false_break_prob': 0.5
            }
    
    def _detect_breakthrough(self, df, idx, supertrend, trend):
        """檢測突破"""
        if idx == 0:
            return False, None
        
        current_price = df['Close'].iloc[idx]
        current_supertrend = supertrend.iloc[idx]
        current_trend = trend.iloc[idx]
        prev_trend = trend.iloc[idx-1]
        
        # 檢測趨勢轉變
        if current_trend != prev_trend:
            # 趨勢轉為上漲
            if current_trend == 1:
                return True, 'long'
            # 趨勢轉為下跌
            elif current_trend == 0:
                return True, 'short'
        
        return False, None
    
    def _confirm_signals(self, df, current_idx, supertrend, trend):
        """確認信號（延遲檢查）"""
        confirmed = {}
        
        for signal_idx, signal in list(self.pending_signals.items()):
            elapsed = current_idx - signal['initial_idx']
            
            # 如果超過延遲時間，進行確認
            if elapsed >= self.delay_bars:
                # 檢查趨勢是否持續
                current_trend = trend.iloc[current_idx]
                initial_trend = 1 if signal['direction'] == 'long' else 0
                
                if current_trend == initial_trend:
                    # 計算假突破概率
                    false_break_prob = self._calculate_false_break_probability(
                        df, signal['initial_idx'], current_idx
                    )
                    
                    confidence = 1.0 - false_break_prob
                    
                    # 如果置信度達到閾值
                    if confidence >= self.confidence_threshold:
                        confirmed[signal_idx] = {
                            'signal': signal['direction'],
                            'confidence': confidence,
                            'false_break_prob': false_break_prob
                        }
                
                # 移除已處理的信號
                del self.pending_signals[signal_idx]
        
        return confirmed
    
    def _calculate_false_break_probability(self, df, initial_idx, current_idx):
        """計算假突破概率"""
        # 1. 檢查價格回撤
        price_slice = df['Close'].iloc[initial_idx:current_idx+1]
        initial_price = price_slice.iloc[0]
        min_price = price_slice.min()
        max_price = price_slice.max()
        
        # 計算回撤幅度
        drawdown = (max_price - min_price) / max_price
        
        # 2. 檢查波動率
        atr = calculate_atr(
            df['High'].iloc[initial_idx:current_idx+1],
            df['Low'].iloc[initial_idx:current_idx+1],
            df['Close'].iloc[initial_idx:current_idx+1],
            period=14
        )
        current_atr = atr.iloc[-1]
        
        # 3. 基於指標的基準概率
        base_prob = 0.3
        
        # 4. 調整概率
        if drawdown > 0.02:  # 回撤超過 2%
            base_prob += 0.3  # 增加假突破概率
        
        if current_atr > atr.mean() * 1.5:  # 波動率過高
            base_prob += 0.2
        
        # 限制在 0-1 範圍
        return np.clip(base_prob, 0, 1)

# ============================================
# 第四部分：動態倉位系統
# ============================================

class DynamicPositionSystem:
    """動態倉位系統"""
    
    def __init__(self, account_value, risk_per_trade=0.02):
        """
        初始化動態倉位系統
        
        參數：
        - account_value: 賬戶價值
        - risk_per_trade: 每筆交易風險比例
        """
        self.account_value = account_value
        self.risk_per_trade = risk_per_trade
    
    def calculate_position(self, df, ticker, current_idx):
        """
        計算單一資產倉位
        
        參數：
        - df: 數據 DataFrame
        - ticker: 資產代碼
        - current_idx: 當前索引
        
        返回：
        - position: 倉位信息字典
        """
        # 計算 ATR
        atr = calculate_atr(
            df['High'],
            df['Low'],
            df['Close'],
            period=STRATEGY_PARAMS['atr']['period']
        )
        
        current_atr = atr.iloc[current_idx]
        current_price = df['Close'].iloc[current_idx]
        
        # 計算止損距離
        stop_loss_distance = (
            current_atr * 
            STRATEGY_PARAMS['dynamic_position']['stop_loss_atr_multiplier']
        )
        
        # 計算風險金額
        risk_amount = self.account_value * self.risk_per_trade
        
        # 計算倉位大小
        position_size = risk_amount / stop_loss_distance
        
        # 計算股數
        number_of_shares = int(position_size / current_price)
        
        # 計算實際倉位金額
        position_value = number_of_shares * current_price
        
        # 計算實際權重
        weight = position_value / self.account_value
        
        # 計算實際風險
        actual_risk = (position_value * stop_loss_distance / current_price) / self.account_value
        
        return {
            'ticker': ticker,
            'shares': number_of_shares,
            'value': position_value,
            'weight': weight,
            'actual_risk': actual_risk,
            'atr': current_atr,
            'stop_loss': current_price - stop_loss_distance
        }

# ============================================
# 第五部分：整合策略
# ============================================

class IntegratedStrategy:
    """整合策略（板塊輪動 + 延遲進場 + 動態倉位）"""
    
    def __init__(self, account_value=100000):
        """
        初始化整合策略
        
        參數：
        - account_value: 賬戶價值
        """
        self.account_value = account_value
        
        # 初始化子系統
        self.sector_rotation = SectorRotationSystem(
            SECTOR_ETFS,
            lookback=STRATEGY_PARAMS['sector_rotation']['lookback'],
            top_n=STRATEGY_PARAMS['sector_rotation']['top_n']
        )
        
        self.delayed_entry = DelayedEntrySystem(
            delay_bars=STRATEGY_PARAMS['delayed_entry']['delay_bars'],
            confidence_threshold=STRATEGY_PARAMS['delayed_entry']['confidence_threshold']
        )
        
        self.dynamic_position = DynamicPositionSystem(
            account_value=account_value,
            risk_per_trade=STRATEGY_PARAMS['dynamic_position']['risk_per_trade']
        )
        
        # 歷史記錄
        self.trades = []
        self.positions = {}
    
    def run_backtest(self, data, start_idx=100):
        """
        運行回測
        
        參數：
        - data: 數據字典 {ticker: DataFrame}
        - start_idx: 開始索引
        
        返回：
        - results: 回測結果
        """
        print("\n" + "="*60)
        print("開始回測整合策略")
        print("="*60)
        
        portfolio_value = self.account_value
        positions = {}
        trades = []
        
        # 滾動執行
        for idx in range(start_idx, len(data['SPY'])):
            current_date = data['SPY'].index[idx]
            
            # 1. 更新板塊強度（每週一次）
            if idx % 5 == 0:
                self.sector_rotation.update_strengths(data)
                sector_weights = self.sector_rotation.calculate_weights()
                top_sectors = self.sector_rotation.get_top_sectors()
            
            # 2. 為每個板塊生成信號
            sector_signals = {}
            for sector in top_sectors:
                if sector not in SECTOR_ETFS or SECTOR_ETFS[sector] == 'SPY':
                    continue
                
                ticker = SECTOR_ETFS[sector]
                if ticker not in data:
                    continue
                
                signal_info = self.delayed_entry.generate_signal(data[ticker], idx)
                sector_signals[sector] = signal_info
            
            # 3. 計算倉位
            total_weight = 0
            new_positions = {}
            
            for sector, signal in sector_signals.items():
                if signal['signal'] == 'hold':
                    continue
                
                # 檢查權重限制
                if sector in self.sector_rotation.current_weights:
                    sector_weight = (
                        self.sector_rotation.current_weights[sector] *
                        signal['confidence']
                    )
                    
                    if sector_weight > 0.01:  # 最小權重 1%
                        ticker = SECTOR_ETFS[sector]
                        
                        # 計算倉位
                        position = self.dynamic_position.calculate_position(
                            data[ticker], ticker, idx
                        )
                        
                        # 限制倉位
                        max_weight = min(sector_weight, 0.3)
                        if position['weight'] > max_weight:
                            position['shares'] = int(
                                (portfolio_value * max_weight) / 
                                data[ticker]['Close'].iloc[idx]
                            )
                            position['value'] = (
                                position['shares'] * 
                                data[ticker]['Close'].iloc[idx]
                            )
                            position['weight'] = max_weight
                        
                        position['sector'] = sector
                        position['signal'] = signal['signal']
                        position['entry_date'] = current_date
                        
                        new_positions[ticker] = position
                        total_weight += position['weight']
            
            # 4. 記錄交易
            for ticker, position in new_positions.items():
                if ticker not in positions:
                    # 新倉位
                    trades.append({
                        'type': 'entry',
                        'ticker': ticker,
                        'date': position['entry_date'],
                        'shares': position['shares'],
                        'price': data[ticker]['Close'].iloc[idx],
                        'value': position['value'],
                        'signal': position['signal']
                    })
            
            for ticker, position in positions.items():
                if ticker not in new_positions:
                    # 平倉
                    exit_price = data[ticker]['Close'].iloc[idx]
                    exit_value = position['shares'] * exit_price
                    
                    trades.append({
                        'type': 'exit',
                        'ticker': ticker,
                        'date': current_date,
                        'shares': position['shares'],
                        'price': exit_price,
                        'value': exit_value,
                        'pnl': exit_value - position['value']
                    })
            
            positions = new_positions
            
            # 5. 計算組合價值
            position_value = sum(
                pos['shares'] * data[ticker]['Close'].iloc[idx]
                for ticker, pos in positions.items()
                if ticker in data
            )
            
            cash = portfolio_value - position_value
            portfolio_value = position_value + cash
            
            # 記錄
            trades.append({
                'type': 'snapshot',
                'date': current_date,
                'portfolio_value': portfolio_value,
                'position_value': position_value,
                'cash': cash,
                'num_positions': len(positions)
            })
        
        # 6. 平倉所有倉位
        for ticker, position in positions.items():
            exit_price = data[ticker]['Close'].iloc[-1]
            exit_value = position['shares'] * exit_price
            
            trades.append({
                'type': 'final_exit',
                'ticker': ticker,
                'date': data[ticker].index[-1],
                'shares': position['shares'],
                'price': exit_price,
                'value': exit_value,
                'pnl': exit_value - position['value']
            })
        
        self.trades = trades
        
        # 7. 計算績效
        results = self._calculate_performance(trades)
        
        return results
    
    def _calculate_performance(self, trades):
        """計算績效指標"""
        # 提取快照
        snapshots = [t for t in trades if t['type'] == 'snapshot']
        
        if not snapshots:
            return {}
        
        # 轉為 DataFrame
        df = pd.DataFrame(snapshots)
        df.set_index('date', inplace=True)
        
        # 計算日收益率
        df['daily_return'] = df['portfolio_value'].pct_change()
        
        # 計算績效指標
        total_return = (df['portfolio_value'].iloc[-1] / df['portfolio_value'].iloc[0]) - 1
        annual_return = df['daily_return'].mean() * 252
        annual_volatility = df['daily_return'].std() * np.sqrt(252)
        sharpe_ratio = annual_return / annual_volatility if annual_volatility > 0 else 0
        
        # 最大回撤
        cumulative = (1 + df['daily_return']).cumprod()
        max_drawdown = (cumulative / cumulative.cummax() - 1).min()
        calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        # 交易統計
        entry_trades = [t for t in trades if t['type'] == 'entry']
        exit_trades = [t for t in trades if t['type'] in ['exit', 'final_exit']]
        
        total_trades = len(entry_trades)
        winning_trades = len([t for t in exit_trades if t.get('pnl', 0) > 0])
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # 計算假突破率
        signals = [
            t for t in trades 
            if t['type'] == 'entry' and 'signal' in t
        ]
        if signals:
            avg_confidence = np.mean([t['signal']['confidence'] for t in signals])
            avg_false_break_prob = np.mean([t['signal']['false_break_prob'] for t in signals])
        else:
            avg_confidence = 0.5
            avg_false_break_prob = 0.5
        
        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'annual_volatility': annual_volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'calmar_ratio': calmar_ratio,
            'total_trades': total_trades,
            'win_rate': win_rate,
            'avg_confidence': avg_confidence,
            'avg_false_break_prob': avg_false_break_prob,
            'equity_curve': df['portfolio_value']
        }

# ============================================
# 主程序
# ============================================

def main():
    """主程序"""
    print("\n" + "="*60)
    print("趨勢突破策略 - 結合延遲進場優化與板塊輪動")
    print("="*60)
    print(f"開始時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 獲取數據
    print(f"\n{'='*60}")
    print("第一步：獲取數據")
    print(f"{'='*60}")
    
    tickers = list(SECTOR_ETFS.values())
    print(f"下載 {len(tickers)} 個 ETF 的數據...")
    
    data = {}
    for ticker in tickers:
        print(f"   正在下載 {ticker}...", end=' ')
        try:
            df = yf.download(ticker, start='2020-01-01', end='2026-03-06', progress=False)
            if not df.empty:
                data[ticker] = df
                print(f"✅ ({len(df)} 個交易日)")
            else:
                print(f"❌ (無數據）")
        except Exception as e:
            print(f"❌ (錯誤: {str(e)[:50]})")
    
    print(f"\n✅ 數據獲取完成：{len(data)} 個 ETF")
    
    # 2. 對齊數據
    print(f"\n{'='*60}")
    print("第二步：對齊數據")
    print(f"{'='*60}")
    
    common_dates = None
    for ticker, df in data.items():
        if common_dates is None:
            common_dates = set(df.index)
        else:
            common_dates = common_dates.intersection(set(df.index))
    
    common_dates = sorted(list(common_dates))
    print(f"共同交易日數量：{len(common_dates)}")
    
    # 對齊數據
    aligned_data = {}
    for ticker, df in data.items():
        aligned_data[ticker] = df.loc[common_dates].copy()
    
    data = aligned_data
    
    # 3. 運行回測
    print(f"\n{'='*60}")
    print("第三步：運行回測")
    print(f"{'='*60}")
    
    strategy = IntegratedStrategy(account_value=100000)
    results = strategy.run_backtest(data, start_idx=100)
    
    # 4. 顯示結果
    print(f"\n{'='*60}")
    print("第四步：回測結果")
    print(f"{'='*60}")
    
    if results:
        print(f"\n📊 績效指標：")
        print(f"   總收益：{results['total_return']:.2%}")
        print(f"   年化收益：{results['annual_return']:.2%}")
        print(f"   年化波動：{results['annual_volatility']:.2%}")
        print(f"   夏普比率：{results['sharpe_ratio']:.2f}")
        print(f"   最大回撤：{results['max_drawdown']:.2%}")
        print(f"   Calmar比率：{results['calmar_ratio']:.2f}")
        print(f"\n📈 交易統計：")
        print(f"   總交易次數：{results['total_trades']}")
        print(f"   勝率：{results['win_rate']:.2%}")
        print(f"   平均置信度：{results['avg_confidence']:.2%}")
        print(f"   平均假突破概率：{results['avg_false_break_prob']:.2%}")
        
        # 繪製權益曲線
        if 'equity_curve' in results:
            plt.figure(figsize=(14, 7))
            plt.plot(results['equity_curve'].index, results['equity_curve'].values, 
                     label='整合策略', linewidth=2)
            plt.title('整合策略權益曲線（2020-2026）', fontsize=14, fontweight='bold')
            plt.xlabel('日期')
            plt.ylabel('資產價值 ($)')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig('integrated_strategy_equity_curve.png', dpi=300, bbox_inches='tight')
            print(f"\n✅ 權益曲線已保存：integrated_strategy_equity_curve.png")
            plt.show()
    else:
        print("❌ 回測失敗")
    
    # 5. 對比基準
    print(f"\n{'='*60}")
    print("第五步：與基準對比")
    print(f"{'='*60}")
    
    spy_returns = data['SPY']['Close'].pct_change().dropna()
    spy_annual_return = spy_returns.mean() * 252
    spy_annual_volatility = spy_returns.std() * np.sqrt(252)
    spy_sharpe = spy_annual_return / spy_annual_volatility
    spy_cumulative = (1 + spy_returns).cumprod()
    spy_max_dd = (spy_cumulative / spy_cumulative.cummax() - 1).min()
    
    print(f"\n📊 SPY（市場基準）績效：")
    print(f"   年化收益：{spy_annual_return:.2%}")
    print(f"   年化波動：{spy_annual_volatility:.2%}")
    print(f"   夏普比率：{spy_sharpe:.2f}")
    print(f"   最大回撤：{spy_max_dd:.2%}")
    
    if results:
        print(f"\n📊 對比結果：")
        print(f"   收益超越：{results['annual_return'] - spy_annual_return:+.2%}")
        print(f"   夏普超越：{results['sharpe_ratio'] - spy_sharpe:+.2f}")
        print(f"   回撤改善：{results['max_drawdown'] - spy_max_dd:+.2%}")
    
    print(f"\n{'='*60}")
    print(f"分析完成！結束時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
