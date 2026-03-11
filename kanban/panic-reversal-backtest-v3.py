#!/usr/bin/env python3
"""
恐慌逆勢策略 - 簡化版 V3（純時間出場）
Backtest for Panic Reversal Strategy - Simplified V3 (Time-Exit Only)

核心改進：
- 完全移除停損、停利、加減碼
- 只保留固定持有期間出場
- 測試不同持有期間的效果

這是最簡單的版本：進場 → 持有 X 天 → 出場
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import requests
import json
from typing import Dict, List, Tuple, Optional

# ============================================================
# 策略配置 - 簡化版 V3
# ============================================================

# 進場信號配置（使用 V2 的改進閾值和加權評分）
ENTRY_CONFIG = {
    'EXTREME': {
        'z_qqq_threshold': -1.75,
        'z_gld_threshold': -1.4,
        'z_uup_threshold': -1.4,
        'position_size': 0.40,
    },
    'HIGH': {
        'z_qqq_threshold': -1.4,
        'z_gld_threshold': -1.05,
        'z_uup_threshold': -1.05,
        'position_size': 0.25,
    },
    'MODERATE': {
        'z_qqq_threshold': -1.05,
        'z_gld_threshold': -0.7,
        'z_uup_threshold': -0.7,
        'position_size': 0.15,
    },
    'ULTRA_EXTREME': {
        'z_qqq_threshold': -0.8,
        'z_gld_threshold': -0.6,
        'z_uup_threshold': -0.6,
        'position_size': 0.10,
    },
}

# 加權評分配置
WEIGHTS = {
    'qqq': 0.50,
    'gld': 0.25,
    'uup': 0.25,
}
WEIGHTED_THRESHOLD = 0.50

# 測試不同的持有期間（天數）
HOLDING_PERIODS = [5, 7, 10, 15, 20]

# ============================================================
# 數據獲取
# ============================================================

def fetch_price_data(symbol: str, days: int = 3650) -> pd.DataFrame:
    """從 Dashboard API 獲取價格數據"""
    try:
        url = f"http://localhost:8000/api/stocks/{symbol}/history?days={days}"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()

        if not data or len(data) == 0:
            return None

        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['trade_date'])
        df = df.sort_values('date').reset_index(drop=True)
        df = df[['date', 'close']].rename(columns={'close': symbol})

        return df

    except Exception as e:
        print(f"❌ 獲取 {symbol} 數據失敗: {e}")
        return None

def fetch_all_data(symbols: List[str], days: int = 3650) -> pd.DataFrame:
    """獲取所有需要的數據並合併"""
    dfs = []

    for symbol in symbols:
        print(f"📥 獲取 {symbol} 數據...")
        df = fetch_price_data(symbol, days)
        if df is not None:
            dfs.append(df)

    if not dfs:
        raise ValueError("無法獲取任何數據")

    merged = dfs[0]
    for df in dfs[1:]:
        merged = pd.merge(merged, df, on='date', how='inner')

    merged = merged.sort_values('date').reset_index(drop=True)
    print(f"✅ 數據獲取完成: {len(merged)} 天")
    return merged

# ============================================================
# 進場檢測（使用 V2 的加權評分邏輯）
# ============================================================

class PanicReversalEntry:
    """進場檢測 - 使用 V2 的加權評分"""

    def __init__(self, lookback_days: int = 60):
        self.lookback_days = lookback_days

    def calculate_z_scores(self, data: pd.DataFrame, idx: int) -> Dict[str, float]:
        """計算 Z-scores"""
        if idx < self.lookback_days:
            return {'z_qqq': 0, 'z_gld': 0, 'z_uup': 0}

        window = data.iloc[idx - self.lookback_days:idx]
        z_scores = {}

        for symbol in ['QQQ', 'GLD', 'UUP']:
            returns = window[symbol].pct_change().dropna()
            mean = returns.mean()
            std = returns.std()

            if std > 0:
                current_return = data.iloc[idx][symbol] / data.iloc[idx - 1][symbol] - 1
                z_scores[f'z_{symbol.lower()}'] = (current_return - mean) / std
            else:
                z_scores[f'z_{symbol.lower()}'] = 0

        return z_scores

    def calculate_weighted_score(self, z_scores: Dict[str, float], config: Dict) -> float:
        """計算加權評分"""
        score = 0
        if z_scores['z_qqq'] < config['z_qqq_threshold']:
            score += WEIGHTS['qqq']
        if z_scores['z_gld'] < config['z_gld_threshold']:
            score += WEIGHTS['gld']
        if z_scores['z_uup'] < config['z_uup_threshold']:
            score += WEIGHTS['uup']
        return score

    def check_entry_signal(self, data: pd.DataFrame, idx: int) -> Tuple[Optional[str], Dict[str, float]]:
        """檢查進場信號"""
        if idx < self.lookback_days:
            return None, {'z_qqq': 0, 'z_gld': 0, 'z_uup': 0}

        z_scores = self.calculate_z_scores(data, idx)

        signal_levels = ['EXTREME', 'HIGH', 'MODERATE', 'ULTRA_EXTREME']

        for signal_level in signal_levels:
            config = ENTRY_CONFIG[signal_level]
            weighted_score = self.calculate_weighted_score(z_scores, config)

            if weighted_score >= WEIGHTED_THRESHOLD:
                return signal_level, z_scores

        return None, z_scores


# ============================================================
# 簡化策略：只有進場和時間出場
# ============================================================

class SimpleTimeExitStrategy:
    """簡化策略：進場 → 固定時間 → 出場"""

    def __init__(self, holding_days: int = 10, initial_capital: float = 100000):
        self.holding_days = holding_days
        self.account_value = initial_capital
        self.initial_account_value = initial_capital

        self.entry = PanicReversalEntry()
        self.position = None
        self.in_trade = False

        self.trades = []
        self.daily_values = []

    def on_new_day(self, data: pd.DataFrame, idx: int):
        """每日檢查"""
        current_date = data.iloc[idx]['date']
        current_price_qqq = data.iloc[idx]['QQQ']

        # 檢查出場（如果持倉中）
        if self.in_trade:
            holding_period = (current_date - self.position['entry_date']).days

            if holding_period >= self.holding_days:
                # 時間到，出場
                self.exit_trade(current_date, current_price_qqq, 'TIME_EXIT')

        # 檢查進場（如果沒有持倉）
        if not self.in_trade:
            signal, z_scores = self.entry.check_entry_signal(data, idx)

            if signal:
                position_size = ENTRY_CONFIG[signal]['position_size']
                self.enter_trade(signal, position_size, data.iloc[idx], current_date, idx, z_scores)

        # 更新賬戶價值
        if self.in_trade:
            current_return = (current_price_qqq - self.position['entry_price_qqq']) / self.position['entry_price_qqq']
            self.account_value = self.account_value * (1 + current_return * self.position['position_size'])
        else:
            self.account_value = self.account_value  # 持有現金

        self.daily_values.append({
            'date': current_date,
            'account_value': self.account_value,
            'in_trade': self.in_trade,
        })

    def enter_trade(self, signal: str, position_size: float, prices: Dict,
                   date: pd.Timestamp, idx: int, z_scores: Dict):
        """進場"""
        self.position = {
            'signal_level': signal,
            'entry_price_qqq': prices['QQQ'],
            'entry_date': date,
            'position_size': position_size,
            'z_scores': z_scores,
        }
        self.in_trade = True

    def exit_trade(self, date: pd.Timestamp, exit_price_qqq: float, exit_signal: str):
        """出場"""
        if self.position:
            current_return = (exit_price_qqq - self.position['entry_price_qqq']) / self.position['entry_price_qqq']
            pnl = self.account_value * current_return * self.position['position_size']

            self.trades.append({
                'entry_date': self.position['entry_date'],
                'exit_date': date,
                'signal_level': self.position['signal_level'],
                'entry_price_qqq': self.position['entry_price_qqq'],
                'exit_price_qqq': exit_price_qqq,
                'position_size': self.position['position_size'],
                'holding_days': (date - self.position['entry_date']).days,
                'exit_signal': exit_signal,
                'return': current_return,
                'pnl': pnl,
                'z_scores': self.position['z_scores'],
            })

            self.position = None
            self.in_trade = False


# ============================================================
# 回測引擎
# ============================================================

def run_backtest(data: pd.DataFrame, holding_days: int, initial_capital: float = 100000) -> Dict:
    """執行回測（測試特定持有期間）"""
    strategy = SimpleTimeExitStrategy(holding_days=holding_days, initial_capital=initial_capital)
    start_idx = 60

    for idx in range(start_idx, len(data)):
        strategy.on_new_day(data, idx)

    results = calculate_performance(strategy, initial_capital, holding_days)
    return results


def calculate_performance(strategy: SimpleTimeExitStrategy, initial_capital: float, holding_days: int) -> Dict:
    """計算績效"""
    daily_values = pd.DataFrame(strategy.daily_values)

    if len(daily_values) == 0:
        return {'error': 'No data'}

    daily_values['daily_return'] = daily_values['account_value'].pct_change()
    daily_values = daily_values.dropna(subset=['daily_return'])

    total_days = len(daily_values)
    total_years = total_days / 252

    final_value = daily_values['account_value'].iloc[-1]
    total_return = (final_value - initial_capital) / initial_capital
    annual_return = (1 + total_return) ** (1 / total_years) - 1

    daily_std = daily_values['daily_return'].std()
    annual_std = daily_std * np.sqrt(252)
    sharpe_ratio = annual_return / annual_std if annual_std > 0 else 0

    cum_returns = (1 + daily_values['daily_return']).cumprod()
    cum_max = cum_returns.expanding().max()
    drawdown = (cum_returns - cum_max) / cum_max
    max_drawdown = drawdown.min()

    trades = strategy.trades
    num_trades = len(trades)

    if num_trades > 0:
        winning_trades = [t for t in trades if t['return'] > 0]
        losing_trades = [t for t in trades if t['return'] <= 0]

        win_rate = len(winning_trades) / num_trades

        if winning_trades:
            avg_win = np.mean([t['return'] for t in winning_trades])
            max_win = max([t['return'] for t in winning_trades])
        else:
            avg_win = 0
            max_win = 0

        if losing_trades:
            avg_loss = np.mean([t['return'] for t in losing_trades])
            max_loss = min([t['return'] for t in losing_trades])
        else:
            avg_loss = 0
            max_loss = 0

        avg_holding_days = np.mean([t['holding_days'] for t in trades])

        trades_by_level = {}
        for level in ['EXTREME', 'HIGH', 'MODERATE', 'ULTRA_EXTREME']:
            level_trades = [t for t in trades if t['signal_level'] == level]
            if level_trades:
                trades_by_level[level] = {
                    'count': len(level_trades),
                    'win_rate': len([t for t in level_trades if t['return'] > 0]) / len(level_trades),
                    'avg_return': np.mean([t['return'] for t in level_trades]),
                }
            else:
                trades_by_level[level] = {'count': 0, 'win_rate': 0, 'avg_return': 0}
    else:
        win_rate = 0
        avg_win = 0
        avg_loss = 0
        max_win = 0
        max_loss = 0
        avg_holding_days = 0
        trades_by_level = {}

    return {
        'holding_days': holding_days,
        'daily_values': daily_values,
        'trades': trades,
        'performance': {
            'initial_capital': initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'annual_return': annual_return,
            'annual_volatility': annual_std,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'total_days': total_days,
            'total_years': total_years,
        },
        'trading_stats': {
            'num_trades': num_trades,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'max_win': max_win,
            'max_loss': max_loss,
            'avg_holding_days': avg_holding_days,
            'trades_by_level': trades_by_level,
        },
    }


# ============================================================
# 主程序
# ============================================================

def main():
    """主程序"""
    print(f"\n{'='*60}")
    print(f"恐慌逆勢策略 - 簡化版 V3（純時間出場）")
    print(f"核心改進：")
    print(f"  - 完全移除停損、停利、加減碼")
    print(f"  - 只保留固定持有期間出場")
    print(f"  - 測試不同持有期間：{', '.join(map(str, HOLDING_PERIODS))} 天")
    print(f"{'='*60}\n")

    # 獲取數據
    symbols = ['QQQ', 'GLD', 'UUP']
    data = fetch_all_data(symbols, days=3650)

    if data is None or len(data) == 0:
        print("❌ 無法獲取數據，回測終止")
        return

    # 測試不同持有期間
    all_results = {}
    print(f"\n{'='*60}")
    print(f"🔬 開始測試不同持有期間")
    print(f"{'='*60}\n")

    for holding_days in HOLDING_PERIODS:
        print(f"\n--- 測試持有期間：{holding_days} 天 ---\n")
        results = run_backtest(data, holding_days=holding_days, initial_capital=100000)
        all_results[holding_days] = results
        print_summary(results, holding_days)

    # 比較不同持有期間
    print(f"\n{'='*60}")
    print(f"📊 持有期間比較分析")
    print(f"{'='*60}\n")

    comparison_table = []
    for holding_days in HOLDING_PERIODS:
        perf = all_results[holding_days]['performance']
        stats = all_results[holding_days]['trading_stats']
        comparison_table.append({
            '持有期間 (天)': holding_days,
            '總回報': f"{perf['total_return']:.2%}",
            '年化回報': f"{perf['annual_return']:.2%}",
            'Sharpe': f"{perf['sharpe_ratio']:.2f}",
            '最大回撤': f"{perf['max_drawdown']:.2%}",
            '交易次數': stats['num_trades'],
            '勝率': f"{stats['win_rate']:.2%}",
            '平均獲利': f"{stats['avg_win']:.2%}",
            '平均虧損': f"{stats['avg_loss']:.2%}",
        })

    df_comparison = pd.DataFrame(comparison_table)
    print(df_comparison.to_string(index=False))

    # 找出最佳持有期間
    print(f"\n{'='*60}")
    print(f"🏆 最佳持有期間分析")
    print(f"{'='*60}\n")

    best_by_return = max(all_results.items(), key=lambda x: x[1]['performance']['annual_return'])
    best_by_sharpe = max(all_results.items(), key=lambda x: x[1]['performance']['sharpe_ratio'])
    best_by_drawdown = min(all_results.items(), key=lambda x: x[1]['performance']['max_drawdown'])

    print(f"📈 最佳年化回報：{best_by_return[0]} 天 ({best_by_return[1]['performance']['annual_return']:.2%})")
    print(f"⚖️  最佳 Sharpe 比率：{best_by_sharpe[0]} 天 ({best_by_sharpe[1]['performance']['sharpe_ratio']:.2f})")
    print(f"🛡️  最小回撤：{best_by_drawdown[0]} 天 ({best_by_drawdown[1]['performance']['max_drawdown']:.2%})")

    # 保存所有結果
    output_file = '/Users/charlie/.openclaw/workspace/kanban/panic-reversal-backtest-v3-results.json'
    serializable_results = {}
    for holding_days, results in all_results.items():
        serializable_results[str(holding_days)] = {
            'performance': results['performance'],
            'trading_stats': results['trading_stats'],
            'trades': [
                {
                    'entry_date': t['entry_date'].strftime('%Y-%m-%d'),
                    'exit_date': t['exit_date'].strftime('%Y-%m-%d'),
                    'signal_level': t['signal_level'],
                    'entry_price_qqq': t['entry_price_qqq'],
                    'exit_price_qqq': t['exit_price_qqq'],
                    'position_size': t['position_size'],
                    'holding_days': t['holding_days'],
                    'exit_signal': t['exit_signal'],
                    'return': t['return'],
                    'pnl': t['pnl'],
                }
                for t in results['trades']
            ],
        }

    with open(output_file, 'w') as f:
        json.dump(serializable_results, f, indent=2)

    print(f"\n💾 完整結果已保存到：{output_file}")


def print_summary(results: Dict, holding_days: int):
    """打印回測摘要"""
    performance = results['performance']
    trading_stats = results['trading_stats']

    print(f"【績效指標（{holding_days} 天持有期間）】")
    print(f"  初始資金：${performance['initial_capital']:,.2f}")
    print(f"  最終價值：${performance['final_value']:,.2f}")
    print(f"  總回報：{performance['total_return']:.2%}")
    print(f"  年化回報：{performance['annual_return']:.2%}")
    print(f"  年化波動率：{performance['annual_volatility']:.2%}")
    print(f"  Sharpe 比率：{performance['sharpe_ratio']:.2f}")
    print(f"  最大回撤：{performance['max_drawdown']:.2%}")

    print(f"\n【交易統計】")
    print(f"  總交易次數：{trading_stats['num_trades']}")
    print(f"  年交易頻率：{trading_stats['num_trades'] / performance['total_years']:.1f} 次/年")
    print(f"  勝率：{trading_stats['win_rate']:.2%}")
    print(f"  平均獲利：{trading_stats['avg_win']:.2%}")
    print(f"  平均虧損：{trading_stats['avg_loss']:.2%}")
    print(f"  最大獲利：{trading_stats['max_win']:.2%}")
    print(f"  最大虧損：{trading_stats['max_loss']:.2%}")


if __name__ == '__main__':
    main()
