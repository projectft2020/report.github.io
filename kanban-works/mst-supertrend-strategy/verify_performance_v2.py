#!/usr/bin/env python3
"""
修正版：驗證動態倉位策略 vs 買進持有的績效
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

# 過濾過去 1 年的數據
start_date = '2025-03-06'
end_date = '2026-02-20'

df_daily = df_prices[(df_prices['date'] >= start_date) & (df_prices['date'] <= end_date)].copy()

print("=== 數據預覽 ===")
print(f"分析期間：{start_date} 到 {end_date}")
print(f"交易日數：{len(df_daily)} 天")
print(f"倉位變化記錄：{len(df_positions)} 次")
print()

# 計算買進持有績效
print("=== 買進持有策略 ===")

# 使用 index_cumulative 列計算總報酬
index_cumulative_start = df_daily['index_cumulative'].iloc[0]
index_cumulative_end = df_daily['index_cumulative'].iloc[-1]
bh_return = (index_cumulative_end - index_cumulative_start) / index_cumulative_start * 100

# 計算最大回撤
df_daily['bh_cummax'] = df_daily['index_cumulative'].cummax()
df_daily['bh_drawdown'] = (df_daily['index_cumulative'] - df_daily['bh_cummax']) / df_daily['bh_cummax'] * 100
bh_mdd = df_daily['bh_drawdown'].min()

print(f"起始淨值：{index_cumulative_start:.4f}")
print(f"結束淨值：{index_cumulative_end:.4f}")
print(f"買進持有報酬率：{bh_return:.2f}%")
print(f"買進持有最大回撤：{bh_mdd:.2f}%")
print()

# 計算動態倉位策略績效
print("=== 動態倉位策略 ===")

# 使用已經計算好的倉位和報酬
strategy_cumulative_start = df_daily['strategy_cumulative'].iloc[0]
strategy_cumulative_end = df_daily['strategy_cumulative'].iloc[-1]
strategy_return = (strategy_cumulative_end - strategy_cumulative_start) / strategy_cumulative_start * 100

# 計算策略最大回撤
df_daily['strategy_cummax'] = df_daily['strategy_cumulative'].cummax()
df_daily['strategy_drawdown'] = (df_daily['strategy_cumulative'] - df_daily['strategy_cummax']) / df_daily['strategy_cummax'] * 100
strategy_mdd = df_daily['strategy_drawdown'].min()

# 計算平均倉位
avg_position = df_daily['position_size'].mean()

print(f"起始淨值：{strategy_cumulative_start:.4f}")
print(f"結束淨值：{strategy_cumulative_end:.4f}")
print(f"動態倉位報酬率：{strategy_return:.2f}%")
print(f"動態倉位最大回撤：{strategy_mdd:.2f}%")
print(f"平均倉位：{avg_position:.1%}")
print(f"與買進持有差異：{strategy_return - bh_return:.2f}%")
print(f"風險降低：{strategy_mdd - bh_mdd:+.2f}%")
print()

# 報酬/回撤比
bh_reward_risk = bh_return / abs(bh_mdd)
strategy_reward_risk = strategy_return / abs(strategy_mdd)
print("=== 報酬/回撤比 ===")
print(f"買進持有：{bh_reward_risk:.2f}")
print(f"動態倉位：{strategy_reward_risk:.2f}")
print()

# 詳細分析踏空大行情（2025/04/03 - 2025/07/01）
print("=== 踏空大行情詳細分析 ===")
missed_start = '2025-04-03'
missed_end = '2025-07-01'

df_missed = df_daily[(df_daily['date'] >= missed_start) & (df_daily['date'] <= missed_end)]
index_cumulative_missed_start = df_missed['index_cumulative'].iloc[0]
index_cumulative_missed_end = df_missed['index_cumulative'].iloc[-1]
missed_return = (index_cumulative_missed_end - index_cumulative_missed_start) / index_cumulative_missed_start * 100

# 計算策略在這段期間的報酬
strategy_cumulative_missed_start = df_missed['strategy_cumulative'].iloc[0]
strategy_cumulative_missed_end = df_missed['strategy_cumulative'].iloc[-1]
strategy_missed_return = (strategy_cumulative_missed_end - strategy_cumulative_missed_start) / strategy_cumulative_missed_start * 100

# 計算平均倉位
avg_position_missed = df_missed['position_size'].mean()

print(f"期間：{missed_start} 到 {missed_end}（{len(df_missed)} 天）")
print(f"買進持有報酬：{missed_return:.2f}%")
print(f"動態倉位報酬：{strategy_missed_return:.2f}%")
print(f"策略平均倉位：{avg_position_missed:.1%}")
print(f"踏空損失：{strategy_missed_return - missed_return:.2f}%")
print()

# 詳細分析頻繁調倉時期（2025/08 - 2025/11）
print("=== 頻繁調倉時期詳細分析 ===")
freq_start = '2025-08-01'
freq_end = '2025-11-30'

df_freq = df_daily[(df_daily['date'] >= freq_start) & (df_daily['date'] <= freq_end)]
index_cumulative_freq_start = df_freq['index_cumulative'].iloc[0]
index_cumulative_freq_end = df_freq['index_cumulative'].iloc[-1]
freq_return = (index_cumulative_freq_end - index_cumulative_freq_start) / index_cumulative_freq_start * 100

# 計算策略在這段期間的報酬
strategy_cumulative_freq_start = df_freq['strategy_cumulative'].iloc[0]
strategy_cumulative_freq_end = df_freq['strategy_cumulative'].iloc[-1]
strategy_freq_return = (strategy_cumulative_freq_end - strategy_cumulative_freq_start) / strategy_cumulative_freq_start * 100

print(f"期間：{freq_start} 到 {freq_end}（{len(df_freq)} 天）")
print(f"買進持有報酬：{freq_return:.2f}%")
print(f"動態倉位報酬：{strategy_freq_return:.2f}%")
print(f"頻繁調倉損耗：{strategy_freq_return - freq_return:.2f}%")
print()

# 分析 11 月份具體情況
print("=== 11 月份詳細分析 ===")
nov_start = '2025-11-01'
nov_end = '2025-11-30'

df_nov = df_daily[(df_daily['date'] >= nov_start) & (df_daily['date'] <= nov_end)]
index_cumulative_nov_start = df_nov['index_cumulative'].iloc[0]
index_cumulative_nov_end = df_nov['index_cumulative'].iloc[-1]
nov_return = (index_cumulative_nov_end - index_cumulative_nov_start) / index_cumulative_nov_start * 100

# 計算策略在 11 月份的報酬
strategy_cumulative_nov_start = df_nov['strategy_cumulative'].iloc[0]
strategy_cumulative_nov_end = df_nov['strategy_cumulative'].iloc[-1]
strategy_nov_return = (strategy_cumulative_nov_end - strategy_cumulative_nov_start) / strategy_cumulative_nov_start * 100

print(f"期間：{nov_start} 到 {nov_end}（{len(df_nov)} 天）")
print(f"起始指數價格：{df_nov['index_price'].iloc[0]:.2f}")
print(f"結束指數價格：{df_nov['index_price'].iloc[-1]:.2f}")
print(f"買進持有報酬：{nov_return:.2f}%")
print(f"動態倉位報酬：{strategy_nov_return:.2f}%")
print(f"11 月份損耗：{strategy_nov_return - nov_return:.2f}%")
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
print(f"1. 踏空大行情損失：{strategy_missed_return - missed_return:.2f}%（4-7 月）")
print(f"2. 頻繁調倉損耗：{strategy_freq_return - freq_return:.2f}%（8-11 月）")
print(f"3. 11 月份損耗：{strategy_nov_return - nov_return:.2f}%")
print(f"4. 風險降低收益：{abs(strategy_mdd - bh_mdd):.2f}%")
print()

print("=== 根本原因分析 ===")
print("1. 相關性滯後性：市場已經開始反彈，但相關性仍然高於閾值")
print("2. 閾值寬度過大：0.12 → 0.38，導致反應變慢")
print("3. 頻繁切換：正常市場和過渡市場頻繁切換，交易成本高")
print()

print("=== 結論 ===")
if strategy_return < bh_return:
    diff = abs(strategy_return - bh_return)
    print(f"❌ 動態倉位策略落後買進持有 {diff:.2f}%")
    print(f"在多頭市場中，動態倉位策略明顯失效")
    print(f"主要原因：踏空大行情（{strategy_missed_return - missed_return:.2f}%）+ 頻繁調倉損耗（{strategy_freq_return - freq_return:.2f}%）")
else:
    print(f"✅ 動態倉位策略優於買進持有 {strategy_return - bh_return:.2f}%")
    print(f"在震盪市場中，動態倉位策略有效降低風險")
