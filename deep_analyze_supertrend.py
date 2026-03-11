#!/usr/bin/env python3
import duckdb
import json
from collections import defaultdict
from datetime import datetime
import statistics

# 連接數據庫
conn = duckdb.connect('/Users/charlie/Dashboard/backend/market_data_db/market_data.duckdb')

# 獲取完整的交易記錄
print('=== 提取完整交易數據 ===')
result = conn.execute("""
    SELECT run_id, strategy_id, run_name, status, parameters,
           start_date, end_date, initial_capital, final_value,
           total_return, cagr, sharpe, max_drawdown, win_rate,
           trades_count, profit_factor, avg_trade, equity_curve, drawdown_curve
    FROM backtest_runs
    WHERE strategy_id = 'supertrend_7b9f5ebf' AND status = 'completed'
    ORDER BY created_at DESC
    LIMIT 1
""").fetchone()

if not result:
    print('未找到回測數據')
    exit(1)

run_id, strategy_id, run_name, status, parameters, start_date, end_date, initial_capital, final_value, total_return, cagr, sharpe, max_drawdown, win_rate, trades_count, profit_factor, avg_trade, equity_curve, drawdown_curve = result

# 獲取所有交易記錄
trades_result = conn.execute(f"""
    SELECT trades
    FROM backtest_runs
    WHERE run_id = '{run_id}'
""").fetchone()

if not trades_result or not trades_result[0]:
    print('未找到交易記錄')
    exit(1)

trades = json.loads(trades_result[0])

print(f'總交易數: {len(trades)}')

# 分析函數
def analyze_trades(trades):
    """深度分析交易數據"""
    analysis = {
        'basic': {},
        'profit_loss': {},
        'holding_period': {},
        'monthly': defaultdict(list),
        'yearly': defaultdict(list),
        'symbol': defaultdict(list),
        'streak': {'win': 0, 'loss': 0, 'max_win_streak': 0, 'max_loss_streak': 0},
        'trade_size': [],
        'position_size': []
    }

    # 基本統計
    profitable_trades = [t for t in trades if t.get('pnl', 0) > 0]
    loss_trades = [t for t in trades if t.get('pnl', 0) < 0]

    analysis['basic'] = {
        'total_trades': len(trades),
        'profitable_trades': len(profitable_trades),
        'loss_trades': len(loss_trades),
        'win_rate': len(profitable_trades) / len(trades) if trades else 0,
        'avg_profit': statistics.mean([t['pnl'] for t in profitable_trades]) if profitable_trades else 0,
        'avg_loss': statistics.mean([t['pnl'] for t in loss_trades]) if loss_trades else 0,
        'max_profit': max([t['pnl'] for t in profitable_trades]) if profitable_trades else 0,
        'max_loss': min([t['pnl'] for t in loss_trades]) if loss_trades else 0
    }

    # 盈虧分佈
    profits = [t['pnl'] for t in profitable_trades]
    losses = [t['pnl'] for t in loss_trades]

    if profits:
        analysis['profit_loss'] = {
            'profit_std': statistics.stdev(profits) if len(profits) > 1 else 0,
            'profit_median': statistics.median(profits),
            'profit_range': max(profits) - min(profits),
            'profit_quartile_25': statistics.quantiles(profits, n=4)[0] if len(profits) >= 4 else min(profits),
            'profit_quartile_75': statistics.quantiles(profits, n=4)[2] if len(profits) >= 4 else max(profits)
        }

    if losses:
        analysis['profit_loss'].update({
            'loss_std': statistics.stdev(losses) if len(losses) > 1 else 0,
            'loss_median': statistics.median(losses),
            'loss_range': max(losses) - min(losses),
            'loss_quartile_25': statistics.quantiles(losses, n=4)[0] if len(losses) >= 4 else min(losses),
            'loss_quartile_75': statistics.quantiles(losses, n=4)[2] if len(losses) >= 4 else max(losses)
        })

    # 持倉時間分析
    holding_periods = []
    for t in trades:
        if t.get('holding_days'):
            holding_periods.append(t['holding_days'])

    if holding_periods:
        analysis['holding_period'] = {
            'avg_holding_days': statistics.mean(holding_periods),
            'median_holding_days': statistics.median(holding_periods),
            'min_holding_days': min(holding_periods),
            'max_holding_days': max(holding_periods),
            'holding_std': statistics.stdev(holding_periods) if len(holding_periods) > 1 else 0
        }

    # 按月/年統計
    for t in trades:
        if t.get('entry_date'):
            try:
                entry_date = datetime.strptime(t['entry_date'], '%Y-%m-%d')
                month_key = entry_date.strftime('%Y-%m')
                year_key = entry_date.strftime('%Y')
                analysis['monthly'][month_key].append(t)
                analysis['yearly'][year_key].append(t)
            except:
                pass

    # 按標的分析
    for t in trades:
        if t.get('symbol'):
            analysis['symbol'][t['symbol']].append(t)

    # 連續盈虧分析
    current_win_streak = 0
    current_loss_streak = 0
    for t in trades:
        if t.get('pnl', 0) > 0:
            current_win_streak += 1
            current_loss_streak = 0
            analysis['streak']['max_win_streak'] = max(analysis['streak']['max_win_streak'], current_win_streak)
        elif t.get('pnl', 0) < 0:
            current_loss_streak += 1
            current_win_streak = 0
            analysis['streak']['max_loss_streak'] = max(analysis['streak']['max_loss_streak'], current_loss_streak)

    # 交易規模分析
    for t in trades:
        if t.get('value'):
            analysis['trade_size'].append(t['value'])
        if t.get('shares'):
            analysis['position_size'].append(t['shares'])

    if analysis['trade_size']:
        analysis['trade_size_stats'] = {
            'avg_trade_size': statistics.mean(analysis['trade_size']),
            'median_trade_size': statistics.median(analysis['trade_size']),
            'min_trade_size': min(analysis['trade_size']),
            'max_trade_size': max(analysis['trade_size'])
        }

    if analysis['position_size']:
        analysis['position_size_stats'] = {
            'avg_position_size': statistics.mean(analysis['position_size']),
            'median_position_size': statistics.median(analysis['position_size']),
            'min_position_size': min(analysis['position_size']),
            'max_position_size': max(analysis['position_size'])
        }

    return analysis

# 執行分析
analysis = analyze_trades(trades)

# 輸出結果
print('\n' + '='*60)
print('Supertrend_TW100 深度分析報告')
print('='*60)

print('\n=== 1. 基本統計 ===')
basic = analysis['basic']
print(f'總交易數: {basic["total_trades"]}')
print(f'盈利交易: {basic["profitable_trades"]} ({basic["win_rate"]:.2%})')
print(f'虧損交易: {basic["loss_trades"]} ({(1-basic["win_rate"]):.2%})')
print(f'平均盈利: ${basic["avg_profit"]:,.2f}')
print(f'平均虧損: ${basic["avg_loss"]:,.2f}')
print(f'最大盈利: ${basic["max_profit"]:,.2f}')
print(f'最大虧損: ${basic["max_loss"]:,.2f}')
print(f'盈虧比: {abs(basic["avg_profit"] / basic["avg_loss"]):.2f}' if basic["avg_loss"] != 0 else '盈虧比: N/A')

print('\n=== 2. 盈虧分佈 ===')
pl = analysis['profit_loss']
if pl:
    print(f'盈利標準差: ${pl["profit_std"]:,.2f}')
    print(f'盈利中位數: ${pl["profit_median"]:,.2f}')
    print(f'盈利範圍: ${pl["profit_range"]:,.2f}')
    print(f'盈利 25分位: ${pl["profit_quartile_25"]:,.2f}')
    print(f'盈利 75分位: ${pl["profit_quartile_75"]:,.2f}')
    print(f'\n虧損標準差: ${pl["loss_std"]:,.2f}')
    print(f'虧損中位數: ${pl["loss_median"]:,.2f}')
    print(f'虧損範圍: ${pl["loss_range"]:,.2f}')
    print(f'虧損 25分位: ${pl["loss_quartile_25"]:,.2f}')
    print(f'虧損 75分位: ${pl["loss_quartile_75"]:,.2f}')

print('\n=== 3. 持倉時間分析 ===')
hp = analysis['holding_period']
if hp:
    print(f'平均持倉天數: {hp["avg_holding_days"]:.1f} 天')
    print(f'中位數持倉天數: {hp["median_holding_days"]:.1f} 天')
    print(f'最短持倉: {hp["min_holding_days"]} 天')
    print(f'最長持倉: {hp["max_holding_days"]} 天')
    print(f'持倉時間標準差: {hp["holding_std"]:.1f} 天')

print('\n=== 4. 按月統計 (前12個月) ===')
sorted_months = sorted(analysis['monthly'].items(), key=lambda x: x[0], reverse=True)[:12]
for month, month_trades in sorted_months:
    month_profit = sum([t.get('pnl', 0) for t in month_trades])
    month_win_rate = len([t for t in month_trades if t.get('pnl', 0) > 0]) / len(month_trades) if month_trades else 0
    print(f'{month}: {len(month_trades)} 筆, 盈虧: ${month_profit:,.2f}, 勝率: {month_win_rate:.2%}')

print('\n=== 5. 按年統計 ===')
sorted_years = sorted(analysis['yearly'].items(), key=lambda x: x[0], reverse=True)
for year, year_trades in sorted_years:
    year_profit = sum([t.get('pnl', 0) for t in year_trades])
    year_win_rate = len([t for t in year_trades if t.get('pnl', 0) > 0]) / len(year_trades) if year_trades else 0
    print(f'{year}: {len(year_trades)} 筆, 盈虧: ${year_profit:,.2f}, 勝率: {year_win_rate:.2%}')

print('\n=== 6. 標的分佈 (交易次數前10) ===')
sorted_symbols = sorted(analysis['symbol'].items(), key=lambda x: len(x[1]), reverse=True)[:10]
for symbol, symbol_trades in sorted_symbols:
    symbol_profit = sum([t.get('pnl', 0) for t in symbol_trades])
    symbol_win_rate = len([t for t in symbol_trades if t.get('pnl', 0) > 0]) / len(symbol_trades) if symbol_trades else 0
    avg_return = statistics.mean([t.get('return_pct', 0) for t in symbol_trades]) if symbol_trades else 0
    print(f'{symbol}: {len(symbol_trades)} 筆, 盈虧: ${symbol_profit:,.2f}, 勝率: {symbol_win_rate:.2%}, 平均回報: {avg_return:.2%}')

print('\n=== 7. 連續盈虧分析 ===')
streak = analysis['streak']
print(f'最大連續盈利: {streak["max_win_streak"]} 筆')
print(f'最大連續虧損: {streak["max_loss_streak"]} 筆')

print('\n=== 8. 交易規模分析 ===')
if analysis['trade_size_stats']:
    ts = analysis['trade_size_stats']
    print(f'平均交易規模: ${ts["avg_trade_size"]:,.2f}')
    print(f'中位數交易規模: ${ts["median_trade_size"]:,.2f}')
    print(f'最小交易規模: ${ts["min_trade_size"]:,.2f}')
    print(f'最大交易規模: ${ts["max_trade_size"]:,.2f}')

if analysis['position_size_stats']:
    ps = analysis['position_size_stats']
    print(f'\n平均持倉股數: {ps["avg_position_size"]:,.0f} 股')
    print(f'中位數持倉股數: {ps["median_position_size"]:,.0f} 股')
    print(f'最小持倉股數: {ps["min_position_size"]:,.0f} 股')
    print(f'最大持倉股數: {ps["max_position_size"]:,.0f} 股')

# 詳細交易記錄（按盈虧排序）
print('\n=== 9. 盈利交易 TOP 20 ===')
profitable_trades = sorted([t for t in trades if t.get('pnl', 0) > 0], key=lambda x: x['pnl'], reverse=True)[:20]
for i, t in enumerate(profitable_trades, 1):
    print(f'{i}. {t.get("symbol", "N/A")}: ${t.get("pnl", 0):,.2f} ({t.get("return_pct", 0):.2%}), {t.get("entry_date", "N/A")} → {t.get("exit_date", "Open")}, {t.get("holding_days", "N/A")} 天')

print('\n=== 10. 虧損交易 TOP 20 ===')
loss_trades = sorted([t for t in trades if t.get('pnl', 0) < 0], key=lambda x: x['pnl'])[:20]
for i, t in enumerate(loss_trades, 1):
    print(f'{i}. {t.get("symbol", "N/A")}: ${t.get("pnl", 0):,.2f} ({t.get("return_pct", 0):.2%}), {t.get("entry_date", "N/A")} → {t.get("exit_date", "Open")}, {t.get("holding_days", "N/A")} 天')

# 所有交易明細
print('\n=== 11. 所有交易明細（按時間順序）===')
for i, t in enumerate(trades, 1):
    status_icon = '✅' if t.get('pnl', 0) > 0 else '❌' if t.get('pnl', 0) < 0 else '⏸️'
    print(f'{i:3d}. {status_icon} {t.get("symbol", "N/A"):8s} | PnL: ${t.get("pnl", 0):10,.2f} ({t.get("return_pct", 0):6.2%}) | {t.get("entry_date", "N/A")} → {t.get("exit_date", "Open"):12s} | {t.get("holding_days", "N/A"):3s} 天 | ${t.get("value", 0):,.2f}")

conn.close()
