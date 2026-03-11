#!/usr/bin/env python3
"""
優化版相關性策略 V2：結合價格趨勢 + 固定閾值寬度 + 更高的過渡市場倉位

核心改進：
1. 雙重確認機制：相關性 + 價格趨勢
2. 固定閾值寬度：0.20（更寬，更容易達到正常市場）
3. 過渡市場倉位：75%（更高，避免過度保守）
4. 危機市場倉位：0%（當相關性高且下跌時）
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import rcParams

# 設定中文字體
rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

# 載入數據
print("載入數據...")
df = pd.read_csv('correlation_timing_backtest_data.csv')
df['date'] = pd.to_datetime(df['date'])

# 計算價格趨勢（20 日均線）
df['ma20'] = df['index_price'].rolling(window=20).mean()
df['price_trend'] = np.where(df['index_price'] > df['ma20'], 'upward', 'downward')

# 設定優化參數
print("設定優化參數...")
FIXED_THRESHOLD_WIDTH = 0.20  # 固定閾值寬度（更寬）
HIGH_THRESHOLD_PERCENTILE = 0.90  # 高閾值分位數
ROLLING_WINDOW = 60  # 回看窗口

# 計算固定閾值
df['high_threshold'] = df['correlation'].rolling(window=ROLLING_WINDOW).quantile(HIGH_THRESHOLD_PERCENTILE)
df['low_threshold'] = df['high_threshold'] - FIXED_THRESHOLD_WIDTH  # 固定寬度

# 定義優化策略 V2
def calculate_position_v2(row):
    correlation = row['correlation']
    high_threshold = row['high_threshold']
    low_threshold = row['low_threshold']
    price_trend = row['price_trend']
    
    # 雙重確認機制 + 更高的過渡市場倉位
    if correlation > high_threshold and price_trend == "downward":
        # 高相關性 + 下跌趨勢 → 危機市場
        return 0.0, "crisis"
    elif correlation > high_threshold and price_trend == "upward":
        # 高相關性 + 上漲趨勢 → 可能反彈
        return 0.50, "crisis_rebound"  # 提高到 50%
    elif correlation < low_threshold and price_trend == "upward":
        # 低相關性 + 上漲趨勢 → 正常市場
        return 1.0, "normal"
    else:
        # 過渡市場：提高到 75%
        return 0.75, "transition"

# 應用優化策略 V2
print("應用優化策略 V2...")
df[['v2_position', 'v2_state']] = df.apply(
    lambda row: pd.Series(calculate_position_v2(row)),
    axis=1
)

# 計算策略報酬
df['index_return'] = df['index_price'].pct_change()
df['v2_strategy_return'] = df['index_return'] * df['v2_position'].shift(1)
df['v2_cumulative'] = (1 + df['v2_strategy_return']).cumprod()

# 過濾過去 1 年的數據
start_date = '2025-03-06'
end_date = '2026-02-20'
df_last_year = df[(df['date'] >= start_date) & (df['date'] <= end_date)].copy()

print(f"分析期間：{start_date} 到 {end_date}")
print(f"交易日數：{len(df_last_year)} 天")
print()

# 計算原策略績效
print("=== 原策略績效 ===")
original_cumulative_start = df_last_year['strategy_cumulative'].iloc[0]
original_cumulative_end = df_last_year['strategy_cumulative'].iloc[-1]
original_return = (original_cumulative_end - original_cumulative_start) / original_cumulative_start * 100

# 計算最大回撤
df_last_year['original_cummax'] = df_last_year['strategy_cumulative'].cummax()
df_last_year['original_drawdown'] = (df_last_year['strategy_cumulative'] - df_last_year['original_cummax']) / df_last_year['original_cummax'] * 100
original_mdd = df_last_year['original_drawdown'].min()

# 計算波動率
original_volatility = df_last_year['strategy_return'].std() * np.sqrt(252) * 100

# 計算夏普比率
risk_free_rate = 2.0
original_sharpe = (original_return - risk_free_rate) / original_volatility if original_volatility > 0 else 0

# 計算卡爾馬比率
original_calmar = original_return / abs(original_mdd) if original_mdd < 0 else 0

# 計算平均倉位
original_avg_position = df_last_year['position_size'].mean()

print(f"累積報酬率：{original_return:.2f}%")
print(f"最大回撤：{original_mdd:.2f}%")
print(f"波動率：{original_volatility:.2f}%")
print(f"夏普比率：{original_sharpe:.2f}")
print(f"卡爾馬比率：{original_calmar:.2f}")
print(f"平均倉位：{original_avg_position:.1%}")
print()

# 計算優化策略 V2 績效
print("=== 優化策略 V2 績效 ===")
v2_cumulative_start = df_last_year['v2_cumulative'].iloc[0]
v2_cumulative_end = df_last_year['v2_cumulative'].iloc[-1]
v2_return = (v2_cumulative_end - v2_cumulative_start) / v2_cumulative_start * 100

# 計算最大回撤
df_last_year['v2_cummax'] = df_last_year['v2_cumulative'].cummax()
df_last_year['v2_drawdown'] = (df_last_year['v2_cumulative'] - df_last_year['v2_cummax']) / df_last_year['v2_cummax'] * 100
v2_mdd = df_last_year['v2_drawdown'].min()

# 計算波動率
v2_volatility = df_last_year['v2_strategy_return'].std() * np.sqrt(252) * 100

# 計算夏普比率
v2_sharpe = (v2_return - risk_free_rate) / v2_volatility if v2_volatility > 0 else 0

# 計算卡爾馬比率
v2_calmar = v2_return / abs(v2_mdd) if v2_mdd < 0 else 0

# 計算平均倉位
v2_avg_position = df_last_year['v2_position'].mean()

print(f"累積報酬率：{v2_return:.2f}%")
print(f"最大回撤：{v2_mdd:.2f}%")
print(f"波動率：{v2_volatility:.2f}%")
print(f"夏普比率：{v2_sharpe:.2f}")
print(f"卡爾馬比率：{v2_calmar:.2f}")
print(f"平均倉位：{v2_avg_position:.1%}")
print()

# 三方對比
print("=== 三方對比（原策略 vs 優化 V1 vs 優化 V2）===")
print(f"{'指標':<20} {'原策略':<12} {'優化 V1':<12} {'優化 V2':<12}")
print("-" * 56)
print(f"{'累積報酬率':<20} {original_return:>10.2f}% {'N/A':>10} {v2_return:>10.2f}%")
print(f"{'最大回撤':<20} {original_mdd:>10.2f}% {'N/A':>10} {v2_mdd:>10.2f}%")
print(f"{'夏普比率':<20} {original_sharpe:>10.2f} {'N/A':>10} {v2_sharpe:>10.2f}")
print(f"{'卡爾馬比率':<20} {original_calmar:>10.2f} {'N/A':>10} {v2_calmar:>10.2f}")
print(f"{'平均倉位':<20} {original_avg_position:>10.1%} {'N/A':>10} {v2_avg_position:>10.1%}")
print()

# 分析踏空大行情
print("=== 踏空大行情分析 ===")
missed_start = '2025-04-03'
missed_end = '2025-07-01'

df_missed = df_last_year[(df_last_year['date'] >= missed_start) & (df_last_year['date'] <= missed_end)]
index_cumulative_missed_start = df_missed['index_cumulative'].iloc[0]
index_cumulative_missed_end = df_missed['index_cumulative'].iloc[-1]
missed_return = (index_cumulative_missed_end - index_cumulative_missed_start) / index_cumulative_missed_start * 100

# V2 策略在這段期間的報酬
v2_cumulative_missed_start = df_missed['v2_cumulative'].iloc[0]
v2_cumulative_missed_end = df_missed['v2_cumulative'].iloc[-1]
v2_missed_return = (v2_cumulative_missed_end - v2_cumulative_missed_start) / v2_cumulative_missed_start * 100

print(f"買進持有：{missed_return:.2f}%")
print(f"原策略：0.00%（踏空損失：-15.42%）")
print(f"優化 V2：{v2_missed_return:.2f}%（踏空損失：{v2_missed_return - missed_return:.2f}%）")
print()

# 分析頻繁調倉時期
print("=== 頻繁調倉時期分析 ===")
freq_start = '2025-08-01'
freq_end = '2025-11-30'

df_freq = df_last_year[(df_last_year['date'] >= freq_start) & (df_last_year['date'] <= freq_end)]
index_cumulative_freq_start = df_freq['index_cumulative'].iloc[0]
index_cumulative_freq_end = df_freq['index_cumulative'].iloc[-1]
freq_return = (index_cumulative_freq_end - index_cumulative_freq_start) / index_cumulative_freq_start * 100

# V2 策略在這段期間的報酬
v2_cumulative_freq_start = df_freq['v2_cumulative'].iloc[0]
v2_cumulative_freq_end = df_freq['v2_cumulative'].iloc[-1]
v2_freq_return = (v2_cumulative_freq_end - v2_cumulative_freq_start) / v2_cumulative_freq_start * 100

print(f"買進持有：{freq_return:.2f}%")
print(f"原策略：7.11%（損耗：-3.11%）")
print(f"優化 V2：{v2_freq_return:.2f}%（損耗：{v2_freq_return - freq_return:.2f}%）")
print()

# 結論
print("=== 結論 ===")
if v2_return > original_return:
    print(f"✅ 優化 V2 優於原策略 {v2_return - original_return:.2f}%")
    print(f"踏空大行情改善：{(v2_missed_return - missed_return) - (-15.42):.2f}%")
    print(f"頻繁調倉時期改善：{(v2_freq_return - freq_return) - (-3.11):.2f}%")
    print()
    print("推薦：使用優化 V2 策略")
else:
    print(f"❌ 優化 V2 落後原策略 {original_return - v2_return:.2f}%")
    print("需要進一步優化參數")
