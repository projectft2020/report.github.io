#!/usr/bin/env python3
"""
驗證動態倉位策略 vs 買進持有的績效
"""

import pandas as pd
import numpy as np
from datetime import datetime

# 讀取倉位變化數據
df_positions = pd.read_csv('last_1_year_position_changes.csv')

# 讀取指數價格數據（從 correlation_timing_backtest_data.csv）
df_prices = pd.read_csv('correlation_timing_backtest_data.csv')

# 將日期轉換為 datetime
df_positions['date'] = pd.to_datetime(df_positions['date'])
df_prices['date'] = pd.to_datetime(df_prices['date'])

print("=== 數據預覽 ===")
print(f"倉位變化記錄：{len(df_positions)} 次")
print(f"價格數據範圍：{df_prices['date'].min()} 到 {df_prices['date'].max()}")
print()

# 計算買進持有績效
print("=== 買進持有策略 ===")
initial_price = df_prices[df_prices['date'] == '2025-03-06']['index_price'].values[0]
final_price = df_prices[df_prices['date'] == '2026-02-20']['index_price'].values[0]
bh_return = (df_prices[df_prices['date'] == '2026-02-20']['index_cumulative'].iloc[0] - 1) * 100
print(f"起始價格：{initial_price:.2f}")
print(f"結束價格：{final_price:.2f}")
print(f"買進持有報酬率：{bh_return:.2f}%")

# 計算最大回撤
df_prices_bh = df_prices[(df_prices['date'] >= '2025-03-06') & (df_prices['date'] <= '2026-02-20')].copy()
df_prices_bh['cummax'] = df_prices_bh['index_price'].cummax()
df_prices_bh['drawdown'] = (df_prices_bh['index_price'] - df_prices_bh['cummax']) / df_prices_bh['cummax'] * 100
bh_mdd = df_prices_bh['drawdown'].min()
print(f"買進持有最大回撤：{bh_mdd:.2f}%")
print()

# 計算動態倉位策略績效
print("=== 動態倉位策略 ===")

# 建立每日倉位數據
df_daily = df_prices[(df_prices['date'] >= '2025-03-06') & (df_prices['date'] <= '2026-02-20')].copy()

# 使用已經計算好的倉位
df_daily['position'] = df_daily['position_size']

# 前向填充倉位（以防有空值）
df_daily['position'] = df_daily['position'].ffill()

print(f"起始倉位：{df_daily['position'].iloc[0]:.0%}")
print(f"結束倉位：{df_daily['position'].iloc[-1]:.0%}")
print(f"平均倉位：{df_daily['position'].mean():.1%}")
print(f"倉位變化次數：{len(df_positions)} 次")
print()

# 計算每日報酬
df_daily['daily_return'] = df_daily['index_price'].pct_change() * 100

# 使用已經計算好的策略報酬
strategy_return = df_daily['strategy_cumulative'].iloc[-1] - 1

print(f"動態倉位報酬率：{strategy_return:.2f}%")
print(f"與買進持有差異：{strategy_return - bh_return:.2f}%")
print()

# 計算策略最大回撤
df_daily['strategy_cummax'] = df_daily['strategy_cumulative'].cummax()
df_daily['strategy_drawdown'] = (df_daily['strategy_cumulative'] - df_daily['strategy_cummax']) / df_daily['strategy_cummax'] * 100
strategy_mdd = df_daily['strategy_drawdown'].min()
print(f"動態倉位最大回撤：{strategy_mdd:.2f}%")
print(f"風險降低：{strategy_mdd - bh_mdd:+.2f}%")
print()

# 報酬/回撤比
bh_reward_risk = bh_return / abs(bh_mdd)
strategy_reward_risk = strategy_return / abs(strategy_mdd)
print("=== 報酬/回撤比 ===")
print(f"買進持有：{bh_reward_risk:.2f}")
print(f"動態倉位：{strategy_reward_risk:.2f}")
print()

# 分析踏空大行情（2025/04/03 - 2025/07/01）
print("=== 踏空大行情分析 ===")
missed_start = '2025-04-03'
missed_end = '2025-07-01'

df_missed = df_daily[(df_daily['date'] >= missed_start) & (df_daily['date'] <= missed_end)]
price_start = df_missed['index_price'].iloc[0]
price_end = df_missed['index_price'].iloc[-1]
missed_return = (price_end - price_start) / price_start * 100

print(f"期間：{missed_start} 到 {missed_end}")
print(f"起始價格：{price_start:.2f}")
print(f"結束價格：{price_end:.2f}")
print(f"期間漲幅：{missed_return:.2f}%")

# 計算策略在這段期間的倉位
avg_position_missed = df_missed['position'].mean()
print(f"策略平均倉位：{avg_position_missed:.1%}")
print(f"實際獲利：{missed_return * avg_position_missed / 100:.2f}%")
print(f"踏空損失：{missed_return * (1 - avg_position_missed) / 100:.2f}%")
print()

# 分析頻繁調倉時期（2025/08 - 2025/11）
print("=== 頻繁調倉時期分析 ===")
freq_start = '2025-08-01'
freq_end = '2025-11-30'

df_freq = df_daily[(df_daily['date'] >= freq_start) & (df_daily['date'] <= freq_end)]
price_freq_start = df_freq['index_price'].iloc[0]
price_freq_end = df_freq['index_price'].iloc[-1]
freq_return = (price_freq_end - price_freq_start) / price_freq_start * 100

print(f"期間：{freq_start} 到 {freq_end}")
print(f"起始價格：{price_freq_start:.2f}")
print(f"結束價格：{price_freq_end:.2f}")
print(f"期間漲幅：{freq_return:.2f}%")

# 計算策略在這段期間的報酬
strategy_freq_start = df_freq['strategy_cumulative'].iloc[0]
strategy_freq_end = df_freq['strategy_cumulative'].iloc[-1]
strategy_freq_return = (strategy_freq_end - strategy_freq_start) / strategy_freq_start * 100
print(f"策略報酬：{strategy_freq_return:.2f}%")
print(f"與買進持有差異：{strategy_freq_return - freq_return:.2f}%")
print()

# 總結
print("=== 績效對比總結 ===")
print(f"{'指標':<20} {'買進持有':<15} {'動態倉位':<15} {'差異':<15}")
print("-" * 65)
print(f"{'累積報酬率':<20} {bh_return:>14.2f}% {strategy_return:>14.2f}% {strategy_return - bh_return:>14.2f}%")
print(f"{'最大回撤':<20} {bh_mdd:>14.2f}% {strategy_mdd:>14.2f}% {strategy_mdd - bh_mdd:>14.2f}%")
print(f"{'報酬/回撤比':<20} {bh_reward_risk:>14.2f} {strategy_reward_risk:>14.2f} {strategy_reward_risk - bh_reward_risk:>14.2f}")
print()

# 關鍵洞察
print("=== 關鍵洞察 ===")
print(f"1. 踏空大行情損失：{missed_return * (1 - avg_position_missed) / 100:.2f}%")
print(f"2. 頻繁調倉損耗：{strategy_freq_return - freq_return:.2f}%")
print(f"3. 風險降低收益：{abs(strategy_mdd - bh_mdd):.2f}%")
print()
print("結論：動態倉位策略在多頭市場中明顯落後，主要原因是踏空大行情和頻繁調倉損耗。")
