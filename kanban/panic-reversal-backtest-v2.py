#!/usr/bin/env python3
"""
恐慌逆勢策略完整回測 - 改進版 V2
Backtest for Panic Reversal Strategy - Improved Version

改進內容：
1. 降低 Z-score 閾值 30%
2. 增加 ULTRA_EXTREME 等級
3. 改進信號條件邏輯（加權評分）
4. 延長回測期間到 3650 天（約 10 年）
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import requests
import json
from typing import Dict, List, Tuple, Optional

# ============================================================
# 策略配置 - 改進版
# ============================================================

ENTRY_CONFIG = {
    'EXTREME': {
        'z_qqq_threshold': -1.75,   # 降低 30%（原 -2.5）
        'z_gld_threshold': -1.4,     # 降低 30%（原 -2.0）
        'z_uup_threshold': -1.4,     # 降低 30%（原 -2.0）
        'initial_position': 0.40,
        'max_position': 0.80,
        'stop_loss': -0.05,
        'profit_target': 0.10,
        'max_holding_days': 20,
        'max_adds': 3,
    },
    'HIGH': {
        'z_qqq_threshold': -1.4,     # 降低 30%（原 -2.0）
        'z_gld_threshold': -1.05,   # 降低 30%（原 -1.5）
        'z_uup_threshold': -1.05,   # 降低 30%（原 -1.5）
        'initial_position': 0.25,
        'max_position': 0.50,
        'stop_loss': -0.04,
        'profit_target': 0.08,
        'max_holding_days': 15,
        'max_adds': 2,
    },
    'MODERATE': {
        'z_qqq_threshold': -1.05,   # 降低 30%（原 -1.5）
        'z_gld_threshold': -0.7,    # 降低 30%（原 -1.0）
        'z_uup_threshold': -0.7,    # 降低 30%（原 -1.0）
        'initial_position': 0.15,
        'max_position': 0.30,
        'stop_loss': -0.03,
        'profit_target': 0.06,
        'max_holding_days': 10,
        'max_adds': 1,
    },
    'ULTRA_EXTREME': {  # 新增等級：更容易觸發
        'z_qqq_threshold': -0.8,
        'z_gld_threshold': -0.6,
        'z_uup_threshold': -0.6,
        'initial_position': 0.10,
        'max_position': 0.20,
        'stop_loss': -0.02,
        'profit_target': 0.04,
        'max_holding_days': 7,
        'max_adds': 0,  # 不加碼
    },
}

WIN_STATS = {
    'EXTREME': {
        'win_rate': 0.65,
        'avg_win': 0.12,
        'avg_loss': -0.04,
    },
    'HIGH': {
        'win_rate': 0.60,
        'avg_win': 0.09,
        'avg_loss': -0.03,
    },
    'MODERATE': {
        'win_rate': 0.55,
        'avg_win': 0.07,
        'avg_loss': -0.03,
    },
    'ULTRA_EXTREME': {  # 新增：較低的預期勝率但更頻繁
        'win_rate': 0.50,
        'avg_win': 0.05,
        'avg_loss': -0.02,
    },
}

# 加權評分配置（改進：從 AND 邏輯改為加權評分）
WEIGHTS = {
    'qqq': 0.50,   # QQQ 權重 50%
    'gld': 0.25,   # GLD 權重 25%
    'uup': 0.25,   # UUP 權重 25%
}

# 加權閾值（50% 權重即可觸發）
WEIGHTED_THRESHOLD = 0.50

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
            print(f"⚠️  無法獲取 {symbol} 數據")
            return None

        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['trade_date'])
        df = df.sort_values('date').reset_index(drop=True)

        # 只保留需要的欄位
        df = df[['date', 'close']]
        df = df.rename(columns={'close': symbol})

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

    # 合併所有數據
    merged = dfs[0]
    for df in dfs[1:]:
        merged = pd.merge(merged, df, on='date', how='inner')

    merged = merged.sort_values('date').reset_index(drop=True)

    print(f"✅ 數據獲取完成: {len(merged)} 天")
    return merged

# ============================================================
# 策略類別
# ============================================================

class PanicReversalEntry:
    """進場檢測 - 改進版（加權評分）"""

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
        """計算加權評分（改進：從 AND 邏輯改為加權評分）"""
        score = 0

        # QQQ 權重 50%
        if z_scores['z_qqq'] < config['z_qqq_threshold']:
            score += WEIGHTS['qqq']

        # GLD 權重 25%
        if z_scores['z_gld'] < config['z_gld_threshold']:
            score += WEIGHTS['gld']

        # UUP 權重 25%
        if z_scores['z_uup'] < config['z_uup_threshold']:
            score += WEIGHTS['uup']

        return score

    def check_entry_signal(self, data: pd.DataFrame, idx: int) -> Tuple[Optional[str], Dict[str, float]]:
        """檢查進場信號 - 改進版（加權評分）"""
        if idx < self.lookback_days:
            return None, {'z_qqq': 0, 'z_gld': 0, 'z_uup': 0}

        z_scores = self.calculate_z_scores(data, idx)

        # 檢查各信號等級（按優先級從高到低）
        signal_levels = ['EXTREME', 'HIGH', 'MODERATE', 'ULTRA_EXTREME']

        for signal_level in signal_levels:
            config = ENTRY_CONFIG[signal_level]

            # 改進：使用加權評分而非 AND 邏輯
            weighted_score = self.calculate_weighted_score(z_scores, config)

            if weighted_score >= WEIGHTED_THRESHOLD:
                return signal_level, z_scores

        return None, z_scores


class PanicReversalPositionSizing:
    """部位大小計算"""

    def __init__(self, account_value: float, max_risk_per_trade: float = 0.02):
        self.account_value = account_value
        self.max_risk_per_trade = max_risk_per_trade

    def calculate_position_size(self, signal: str, win_stats: Dict) -> float:
        """計算部位大小"""
        config = ENTRY_CONFIG[signal]
        initial_position = config['initial_position']

        # 根據勝率和風險調整
        win_rate = win_stats['win_rate']
        avg_win = win_stats['avg_win']
        avg_loss = win_stats['avg_loss']

        # Kelly 公式簡化版
        if avg_loss != 0:
            kelly = (win_rate * avg_win + (1 - win_rate) * avg_loss) / abs(avg_loss)
            kelly = max(0, min(kelly, 1.0))  # 限制在 [0, 1]

            # 結合初始部位和 Kelly
            adjusted_position = initial_position * (0.5 + 0.5 * kelly)
        else:
            adjusted_position = initial_position

        # 限制在配置範圍內
        return min(adjusted_position, config['max_position'])


class PanicReversalScaling:
    """部位調整（加碼）"""

    def __init__(self, config: Dict):
        self.config = config
        self.current_add = 0
        self.last_add_price = None
        self.add_threshold = 0.02  # 2% 反彈後加碼

    def should_add_position(self, current_price: float, entry_price: float) -> bool:
        """檢查是否應該加碼"""
        if self.current_add >= self.config['max_adds']:
            return False

        # 價格回彈後加碼
        if current_price > entry_price * (1 + self.add_threshold * (self.current_add + 1)):
            return True

        return False

    def add_position(self) -> float:
        """執行加碼"""
        self.current_add += 1
        # 每次加碼增加 10% 的初始部位
        add_size = self.config['initial_position'] * 0.10
        return add_size

    def get_current_add(self) -> int:
        return self.current_add


class PanicReversalExit:
    """出場檢測"""

    def __init__(self, config: Dict):
        self.config = config
        self.entry_price = None
        self.entry_date = None
        self.highest_price = None

    def set_entry(self, entry_price: float, entry_date: pd.Timestamp):
        """設置進場信息"""
        self.entry_price = entry_price
        self.entry_date = entry_date
        self.highest_price = entry_price

    def check_exit(self, current_price: float, current_date: pd.Timestamp) -> Tuple[Optional[str], float]:
        """檢查出場信號"""
        if self.entry_price is None:
            return None, 0

        # 更新最高價
        self.highest_price = max(self.highest_price, current_price)

        # 計算當前回報
        current_return = (current_price - self.entry_price) / self.entry_price

        # 止損
        if current_return <= self.config['stop_loss']:
            return 'STOP_LOSS', current_return

        # 獲利目標
        if current_return >= self.config['profit_target']:
            return 'PROFIT_TARGET', current_return

        # 最大持有期間
        holding_days = (current_date - self.entry_date).days
        if holding_days >= self.config['max_holding_days']:
            return 'TIME_EXIT', current_return

        # 追蹤止損（Trailing Stop）
        # 最高價回撤 3% 時止損
        if self.highest_price > self.entry_price * 1.02:
            trailing_stop = self.highest_price * 0.97
            if current_price < trailing_stop:
                return 'TRAILING_STOP', current_return

        return None, current_return


class PanicReversalRiskManager:
    """風險管理"""

    def __init__(self, account_value: float):
        self.account_value = account_value
        self.daily_pnl_history = []
        self.weekly_pnl_history = []
        self.max_daily_loss = -0.03  # 最大日損 3%

    def check_risk(self, account_value: float, daily_pnl: float, weekly_pnl: float) -> List[str]:
        """檢查風險"""
        warnings = []

        # 日損限制
        if daily_pnl < self.max_daily_loss:
            warnings.append(f"日損超限: {daily_pnl:.2%}")

        # 周損限制（5%）
        if weekly_pnl < -0.05:
            warnings.append(f"周損超限: {weekly_pnl:.2%}")

        # 賬戶價值下降
        if account_value < self.account_value * 0.90:
            warnings.append(f"賬戶價值下降超過 10%")

        return warnings

    def update_account_value(self, new_value: float):
        """更新賬戶價值"""
        self.account_value = new_value


class PanicReversalStrategy:
    """恐慌逆勢完整策略 - 改進版"""

    def __init__(self, account_value: float = 100000):
        self.account_value = account_value
        self.initial_account_value = account_value

        # 初始化各模組
        self.entry = PanicReversalEntry()
        self.sizing = PanicReversalPositionSizing(account_value)
        self.scaling = None
        self.exit = None
        self.risk_manager = PanicReversalRiskManager(account_value)

        # 策略狀態
        self.position = None
        self.in_trade = False

        # 交易記錄
        self.trades = []
        self.daily_values = []
        self.daily_returns = []

    def on_new_day(self, data: pd.DataFrame, idx: int):
        """每日檢查"""
        current_date = data.iloc[idx]['date']
        current_prices = {
            'QQQ': data.iloc[idx]['QQQ'],
            'GLD': data.iloc[idx]['GLD'],
            'UUP': data.iloc[idx]['UUP'],
        }

        # 檢查進場信號
        if not self.in_trade:
            signal, z_scores = self.entry.check_entry_signal(data, idx)

            if signal:
                print(f"🚀 進場信號：{signal} @ {current_date.strftime('%Y-%m-%d')}")
                print(f"   Z-scores：QQQ={z_scores['z_qqq']:.2f}, "
                      f"GLD={z_scores['z_gld']:.2f}, "
                      f"UUP={z_scores['z_uup']:.2f}")

                # 計算加權評分
                weighted_score = self.entry.calculate_weighted_score(
                    z_scores, ENTRY_CONFIG[signal]
                )
                print(f"   加權評分：{weighted_score:.1%}")

                # 計算部位大小
                position_size = self.sizing.calculate_position_size(signal, WIN_STATS[signal])
                print(f"   部位大小：{position_size:.1%}")

                # 進場
                self.enter_trade(signal, position_size, current_prices, current_date, idx, data)

        # 檢查出場信號
        else:
            exit_signal, current_return = self.exit.check_exit(current_prices['QQQ'], current_date)

            if exit_signal:
                print(f"📤 出場信號：{exit_signal} @ {current_date.strftime('%Y-%m-%d')}")
                print(f"   總回報：{current_return:.2%}")

                self.exit_trade(current_date, current_prices, exit_signal, current_return)

        # 更新賬戶價值
        if self.in_trade:
            current_return = (current_prices['QQQ'] - self.position['entry_price_qqq']) / self.position['entry_price_qqq']
            self.account_value = self.account_value * (1 + current_return * self.position['current_size'])
        else:
            self.account_value = self.account_value  # 持有現金

        self.daily_values.append({
            'date': current_date,
            'account_value': self.account_value,
            'in_trade': self.in_trade,
        })

    def enter_trade(self, signal: str, position_size: float, prices: Dict,
                  date: pd.Timestamp, idx: int, data: pd.DataFrame):
        """進場"""
        self.position = {
            'signal_level': signal,
            'entry_price_qqq': prices['QQQ'],
            'entry_price_gld': prices['GLD'],
            'entry_price_uup': prices['UUP'],
            'entry_date': date,
            'entry_idx': idx,
            'position_size': position_size,
            'current_size': position_size,
        }

        self.scaling = PanicReversalScaling(ENTRY_CONFIG[signal])
        self.exit = PanicReversalExit(ENTRY_CONFIG[signal])
        self.exit.set_entry(prices['QQQ'], date)

        self.in_trade = True

    def exit_trade(self, date: pd.Timestamp, prices: Dict, exit_signal: str, current_return: float):
        """出場"""
        if self.position:
            self.trades.append({
                'entry_date': self.position['entry_date'],
                'exit_date': date,
                'signal_level': self.position['signal_level'],
                'entry_price_qqq': self.position['entry_price_qqq'],
                'exit_price_qqq': prices['QQQ'],
                'position_size': self.position['current_size'],
                'exit_signal': exit_signal,
                'return': current_return,
                'pnl': self.account_value * current_return * self.position['current_size'],
            })

            self.position = None
            self.scaling = None
            self.exit = None
            self.in_trade = False


# ============================================================
# 回測引擎
# ============================================================

def run_backtest(data: pd.DataFrame, initial_capital: float = 100000) -> Dict:
    """執行回測"""
    print(f"\n{'='*60}")
    print(f"🔬 開始回測（初始資金：${initial_capital:,.0f}）")
    print(f"📊 數據期間：{data['date'].min().strftime('%Y-%m-%d')} 至 {data['date'].max().strftime('%Y-%m-%d')}")
    print(f"📈 總天數：{len(data)} 天")
    print(f"{'='*60}\n")

    strategy = PanicReversalStrategy(initial_capital)

    # 開始回測（從 lookback 之後開始）
    start_idx = 60  # 留 60 天作為 lookback

    for idx in range(start_idx, len(data)):
        strategy.on_new_day(data, idx)

    # 計算績效
    results = calculate_performance(strategy, initial_capital)

    return results


def calculate_performance(strategy: PanicReversalStrategy, initial_capital: float) -> Dict:
    """計算績效指標"""
    daily_values = pd.DataFrame(strategy.daily_values)

    if len(daily_values) == 0:
        return {'error': 'No data'}

    # 計算日回報
    daily_values['daily_return'] = daily_values['account_value'].pct_change()

    # 移除 NaN
    daily_values = daily_values.dropna(subset=['daily_return'])

    # 計算統計
    total_days = len(daily_values)
    total_years = total_days / 252

    final_value = daily_values['account_value'].iloc[-1]
    total_return = (final_value - initial_capital) / initial_capital
    annual_return = (1 + total_return) ** (1 / total_years) - 1

    daily_std = daily_values['daily_return'].std()
    annual_std = daily_std * np.sqrt(252)
    sharpe_ratio = annual_return / annual_std if annual_std > 0 else 0

    # 最大回撤
    cum_returns = (1 + daily_values['daily_return']).cumprod()
    cum_max = cum_returns.expanding().max()
    drawdown = (cum_returns - cum_max) / cum_max
    max_drawdown = drawdown.min()

    # 交易統計
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

        avg_holding_days = np.mean([(t['exit_date'] - t['entry_date']).days for t in trades])

        # 按信號等級統計
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
        'strategy': strategy,
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
# 可視化
# ============================================================

def plot_results(results: Dict, output_path: str = None):
    """繪製回測結果"""
    daily_values = results['daily_values']
    performance = results['performance']
    trading_stats = results['trading_stats']

    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('恐慌逆勢策略回測結果（改進版 V2）\nPanic Reversal Strategy Backtest (Improved V2)',
                 fontsize=16, fontweight='bold')

    # 1. 賬戶價值曲線
    ax1 = axes[0, 0]
    ax1.plot(daily_values['date'], daily_values['account_value'],
             linewidth=1.5, color='#2E86AB', label='Account Value')
    ax1.axhline(y=performance['initial_capital'], color='red',
                linestyle='--', linewidth=1, label='Initial Capital')
    ax1.set_xlabel('Date', fontsize=12)
    ax1.set_ylabel('Account Value ($)', fontsize=12)
    ax1.set_title('Account Value Curve', fontsize=14, fontweight='bold')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}k'))

    # 2. 回撤曲線
    ax2 = axes[0, 1]
    cum_returns = (1 + daily_values['daily_return']).cumprod()
    cum_max = cum_returns.expanding().max()
    drawdown = (cum_returns - cum_max) / cum_max * 100

    ax2.plot(daily_values['date'], drawdown,
             linewidth=1.5, color='#E63946', label='Drawdown')
    ax2.fill_between(daily_values['date'], drawdown, 0,
                     where=drawdown < 0, color='#E63946', alpha=0.3)
    ax2.set_xlabel('Date', fontsize=12)
    ax2.set_ylabel('Drawdown (%)', fontsize=12)
    ax2.set_title('Drawdown Curve', fontsize=14, fontweight='bold')
    ax2.legend(loc='lower left')
    ax2.grid(True, alpha=0.3)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.0f}%'))

    # 3. 交易回報分佈
    ax3 = axes[1, 0]
    if len(results['trades']) > 0:
        returns = [t['return'] * 100 for t in results['trades']]
        colors = ['#2E86AB' if r > 0 else '#E63946' for r in returns]

        ax3.bar(range(len(returns)), returns, color=colors, alpha=0.7)
        ax3.axhline(y=0, color='black', linewidth=1)
        ax3.set_xlabel('Trade Number', fontsize=12)
        ax3.set_ylabel('Return (%)', fontsize=12)
        ax3.set_title('Trade Return Distribution', fontsize=14, fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='y')

    # 4. 按信號等級統計
    ax4 = axes[1, 1]
    trades_by_level = trading_stats['trades_by_level']

    if trades_by_level:
        levels = list(trades_by_level.keys())
        counts = [trades_by_level[l]['count'] for l in levels]
        win_rates = [trades_by_level[l]['win_rate'] * 100 for l in levels]

        x = np.arange(len(levels))
        width = 0.35

        ax4a = ax4
        bars1 = ax4a.bar(x - width/2, counts, width, label='Trade Count', color='#2E86AB', alpha=0.7)
        ax4a.set_xlabel('Signal Level', fontsize=12)
        ax4a.set_ylabel('Trade Count', fontsize=12, color='#2E86AB')
        ax4a.tick_params(axis='y', labelcolor='#2E86AB')

        ax4b = ax4a.twinx()
        bars2 = ax4b.bar(x + width/2, win_rates, width, label='Win Rate (%)', color='#E63946', alpha=0.7)
        ax4b.set_ylabel('Win Rate (%)', fontsize=12, color='#E63946')
        ax4b.tick_params(axis='y', labelcolor='#E63946')
        ax4b.set_ylim(0, 100)

        ax4a.set_xticks(x)
        ax4a.set_xticklabels(levels)
        ax4a.set_title('Trades by Signal Level', fontsize=14, fontweight='bold')

        # 添加數值標籤
        for bars, ax in [(bars1, ax4a), (bars2, ax4b)]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.0f}' if height >= 1 else '',
                       ha='center', va='bottom', fontsize=10)

        # 合併圖例
        lines, labels = ax4a.get_legend_handles_labels()
        lines2, labels2 = ax4b.get_legend_handles_labels()
        ax4a.legend(lines + lines2, labels + labels2, loc='upper right')

        ax4a.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"📊 圖表已保存到：{output_path}")

    # 不使用 plt.show()，避免在無顯示環境中卡住
    # plt.show()


def print_summary(results: Dict):
    """打印回測摘要"""
    performance = results['performance']
    trading_stats = results['trading_stats']

    print(f"\n{'='*60}")
    print(f"📊 回測結果摘要（改進版 V2）")
    print(f"{'='*60}\n")

    print("【績效指標】")
    print(f"  初始資金：${performance['initial_capital']:,.2f}")
    print(f"  最終價值：${performance['final_value']:,.2f}")
    print(f"  總回報：{performance['total_return']:.2%}")
    print(f"  年化回報：{performance['annual_return']:.2%}")
    print(f"  年化波動率：{performance['annual_volatility']:.2%}")
    print(f"  Sharpe 比率：{performance['sharpe_ratio']:.2f}")
    print(f"  最大回撤：{performance['max_drawdown']:.2%}")
    print(f"  回測期間：{performance['total_days']} 天 ({performance['total_years']:.1f} 年)")

    print(f"\n【交易統計】")
    print(f"  總交易次數：{trading_stats['num_trades']}")
    print(f"  年交易頻率：{trading_stats['num_trades'] / performance['total_years']:.1f} 次/年")
    print(f"  勝率：{trading_stats['win_rate']:.2%}")
    print(f"  平均獲利：{trading_stats['avg_win']:.2%}")
    print(f"  平均虧損：{trading_stats['avg_loss']:.2%}")
    print(f"  最大獲利：{trading_stats['max_win']:.2%}")
    print(f"  最大虧損：{trading_stats['max_loss']:.2%}")
    print(f"  平均持有天數：{trading_stats['avg_holding_days']:.1f} 天")

    print(f"\n【按信號等級統計】")
    for level, stats in trading_stats['trades_by_level'].items():
        if stats['count'] > 0:
            print(f"  {level}：")
            print(f"    交易次數：{stats['count']}")
            print(f"    年頻率：{stats['count'] / performance['total_years']:.1f} 次/年")
            print(f"    勝率：{stats['win_rate']:.2%}")
            print(f"    平均回報：{stats['avg_return']:.2%}")
        else:
            print(f"  {level}：無交易")

    print(f"\n{'='*60}\n")


# ============================================================
# 主程序
# ============================================================

def main():
    """主程序"""
    print(f"\n{'='*60}")
    print(f"恐慌逆勢策略完整回測（改進版 V2）")
    print(f"改進內容：")
    print(f"  1. 降低 Z-score 閾值 30%")
    print(f"  2. 增加 ULTRA_EXTREME 等級")
    print(f"  3. 改進信號條件邏輯（加權評分）")
    print(f"  4. 延長回測期間到 3650 天（約 10 年）")
    print(f"{'='*60}\n")

    # 獲取數據（3650 天 ≈ 10 年）
    symbols = ['QQQ', 'GLD', 'UUP']
    data = fetch_all_data(symbols, days=3650)

    if data is None or len(data) == 0:
        print("❌ 無法獲取數據，回測終止")
        return

    # 執行回測
    results = run_backtest(data, initial_capital=100000)

    # 打印摘要
    print_summary(results)

    # 繪製圖表
    plot_results(results, output_path='/Users/charlie/.openclaw/workspace/kanban/panic-reversal-backtest-v2.png')

    # 保存結果
    output_file = '/Users/charlie/.openclaw/workspace/kanban/panic-reversal-backtest-v2-results.json'
    with open(output_file, 'w') as f:
        # 移除不可序列化的對象
        serializable_results = {
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
                    'exit_signal': t['exit_signal'],
                    'return': t['return'],
                    'pnl': t['pnl'],
                }
                for t in results['trades']
            ],
        }
        json.dump(serializable_results, f, indent=2)

    print(f"💾 結果已保存到：{output_file}")


if __name__ == '__main__':
    main()
