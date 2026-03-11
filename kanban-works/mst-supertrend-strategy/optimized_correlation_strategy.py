#!/usr/bin/env python3
"""
優化版相關性策略：結合價格趨勢 + 固定閾值寬度

核心改進：
1. 雙重確認機制：相關性 + 價格趨勢
2. 固定閾值寬度：0.15（避免動態增大）
3. 危機市場退出條件：相關性低於閾值 或 價格突破均線
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
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
FIXED_THRESHOLD_WIDTH = 0.15  # 固定閾值寬度
HIGH_THRESHOLD_PERCENTILE = 0.90  # 高閾值分位數
ROLLING_WINDOW = 60  # 回看窗口

# 計算固定閾值
df['high_threshold'] = df['correlation'].rolling(window=ROLLING_WINDOW).quantile(HIGH_THRESHOLD_PERCENTILE)
df['low_threshold'] = df['high_threshold'] - FIXED_THRESHOLD_WIDTH  # 固定寬度

# 定義優化策略
def calculate_position_optimized(row):
    correlation = row['correlation']
    high_threshold = row['high_threshold']
    low_threshold = row['low_threshold']
    price_trend = row['price_trend']
    state = row['market_state']

    # 雙重確認機制
    if correlation > high_threshold and price_trend == "downward":
        # 高相關性 + 下跌趨勢 → 危機市場
        return 0.0, "crisis"
    elif correlation > high_threshold and price_trend == "upward":
        # 高相關性 + 上漲趨勢 → 可能反彈
        return 0.25, "crisis_rebound"
    elif correlation < low_threshold and price_trend == "upward":
        # 低相關性 + 上漲趨勢 → 正常市場
        return 1.0, "normal"
    else:
        # 過渡市場
        return 0.5, "transition"

# 應用優化策略
print("應用優化策略...")
df[['optimized_position', 'optimized_state']] = df.apply(
    lambda row: pd.Series(calculate_position_optimized(row)),
    axis=1
)

# 計算策略報酬
df['index_return'] = df['index_price'].pct_change()
df['optimized_strategy_return'] = df['index_return'] * df['optimized_position'].shift(1)
df['optimized_cumulative'] = (1 + df['optimized_strategy_return']).cumprod()

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

# 計算夏普比率（假設無風險利率 = 2%）
risk_free_rate = 2.0
original_sharpe = (original_return - risk_free_rate) / original_volatility if original_volatility > 0 else 0

# 計算卡爾馬比率
original_calmar = original_return / abs(original_mdd) if original_mdd < 0 else 0

# 計算平均倉位
original_avg_position = df_last_year['position_size'].mean()

print(f"起始淨值：{original_cumulative_start:.4f}")
print(f"結束淨值：{original_cumulative_end:.4f}")
print(f"累積報酬率：{original_return:.2f}%")
print(f"最大回撤：{original_mdd:.2f}%")
print(f"波動率：{original_volatility:.2f}%")
print(f"夏普比率：{original_sharpe:.2f}")
print(f"卡爾馬比率：{original_calmar:.2f}")
print(f"平均倉位：{original_avg_position:.1%}")
print()

# 計算優化策略績效
print("=== 優化策略績效 ===")
optimized_cumulative_start = df_last_year['optimized_cumulative'].iloc[0]
optimized_cumulative_end = df_last_year['optimized_cumulative'].iloc[-1]
optimized_return = (optimized_cumulative_end - optimized_cumulative_start) / optimized_cumulative_start * 100

# 計算最大回撤
df_last_year['optimized_cummax'] = df_last_year['optimized_cumulative'].cummax()
df_last_year['optimized_drawdown'] = (df_last_year['optimized_cumulative'] - df_last_year['optimized_cummax']) / df_last_year['optimized_cummax'] * 100
optimized_mdd = df_last_year['optimized_drawdown'].min()

# 計算波動率
optimized_volatility = df_last_year['optimized_strategy_return'].std() * np.sqrt(252) * 100

# 計算夏普比率
optimized_sharpe = (optimized_return - risk_free_rate) / optimized_volatility if optimized_volatility > 0 else 0

# 計算卡爾馬比率
optimized_calmar = optimized_return / abs(optimized_mdd) if optimized_mdd < 0 else 0

# 計算平均倉位
optimized_avg_position = df_last_year['optimized_position'].mean()

print(f"起始淨值：{optimized_cumulative_start:.4f}")
print(f"結束淨值：{optimized_cumulative_end:.4f}")
print(f"累積報酬率：{optimized_return:.2f}%")
print(f"最大回撤：{optimized_mdd:.2f}%")
print(f"波動率：{optimized_volatility:.2f}%")
print(f"夏普比率：{optimized_sharpe:.2f}")
print(f"卡爾馬比率：{optimized_calmar:.2f}")
print(f"平均倉位：{optimized_avg_position:.1%}")
print()

# 對比分析
print("=== 對比分析 ===")
print(f"{'指標':<20} {'原策略':<15} {'優化策略':<15} {'改善':<15}")
print("-" * 65)
print(f"{'累積報酬率':<20} {original_return:>14.2f}% {optimized_return:>14.2f}% {optimized_return - original_return:>14.2f}%")
print(f"{'最大回撤':<20} {original_mdd:>14.2f}% {optimized_mdd:>14.2f}% {optimized_mdd - original_mdd:>14.2f}%")
print(f"{'波動率':<20} {original_volatility:>14.2f}% {optimized_volatility:>14.2f}% {optimized_volatility - original_volatility:>14.2f}%")
print(f"{'夏普比率':<20} {original_sharpe:>14.2f} {optimized_sharpe:>14.2f} {optimized_sharpe - original_sharpe:>14.2f}")
print(f"{'卡爾馬比率':<20} {original_calmar:>14.2f} {optimized_calmar:>14.2f} {optimized_calmar - original_calmar:>14.2f}")
print(f"{'平均倉位':<20} {original_avg_position:>14.1%} {optimized_avg_position:>14.1%} {optimized_avg_position - original_avg_position:>14.1%}")
print()

# 分析踏空大行情（2025/04/03 - 2025/07/01）
print("=== 踏空大行情分析 ===")
missed_start = '2025-04-03'
missed_end = '2025-07-01'

df_missed = df_last_year[(df_last_year['date'] >= missed_start) & (df_last_year['date'] <= missed_end)]
index_cumulative_missed_start = df_missed['index_cumulative'].iloc[0]
index_cumulative_missed_end = df_missed['index_cumulative'].iloc[-1]
missed_return = (index_cumulative_missed_end - index_cumulative_missed_start) / index_cumulative_missed_start * 100

# 原策略在這段期間的報酬
original_cumulative_missed_start = df_missed['strategy_cumulative'].iloc[0]
original_cumulative_missed_end = df_missed['strategy_cumulative'].iloc[-1]
original_missed_return = (original_cumulative_missed_end - original_cumulative_missed_start) / original_cumulative_missed_start * 100

# 優化策略在這段期間的報酬
optimized_cumulative_missed_start = df_missed['optimized_cumulative'].iloc[0]
optimized_cumulative_missed_end = df_missed['optimized_cumulative'].iloc[-1]
optimized_missed_return = (optimized_cumulative_missed_end - optimized_cumulative_missed_start) / optimized_cumulative_missed_start * 100

print(f"期間：{missed_start} 到 {missed_end}（{len(df_missed)} 天）")
print(f"買進持有報酬：{missed_return:.2f}%")
print(f"原策略報酬：{original_missed_return:.2f}%")
print(f"優化策略報酬：{optimized_missed_return:.2f}%")
print(f"原策略踏空損失：{original_missed_return - missed_return:.2f}%")
print(f"優化策略踏空損失：{optimized_missed_return - missed_return:.2f}%")
print(f"改善：{(optimized_missed_return - missed_return) - (original_missed_return - missed_return):.2f}%")
print()

# 分析頻繁調倉時期（2025/08 - 2025/11）
print("=== 頻繁調倉時期分析 ===")
freq_start = '2025-08-01'
freq_end = '2025-11-30'

df_freq = df_last_year[(df_last_year['date'] >= freq_start) & (df_last_year['date'] <= freq_end)]
index_cumulative_freq_start = df_freq['index_cumulative'].iloc[0]
index_cumulative_freq_end = df_freq['index_cumulative'].iloc[-1]
freq_return = (index_cumulative_freq_end - index_cumulative_freq_start) / index_cumulative_freq_start * 100

# 原策略在這段期間的報酬
original_cumulative_freq_start = df_freq['strategy_cumulative'].iloc[0]
original_cumulative_freq_end = df_freq['strategy_cumulative'].iloc[-1]
original_freq_return = (original_cumulative_freq_end - original_cumulative_freq_start) / original_cumulative_freq_start * 100

# 優化策略在這段期間的報酬
optimized_cumulative_freq_start = df_freq['optimized_cumulative'].iloc[0]
optimized_cumulative_freq_end = df_freq['optimized_cumulative'].iloc[-1]
optimized_freq_return = (optimized_cumulative_freq_end - optimized_cumulative_freq_start) / optimized_cumulative_freq_start * 100

print(f"期間：{freq_start} 到 {freq_end}（{len(df_freq)} 天）")
print(f"買進持有報酬：{freq_return:.2f}%")
print(f"原策略報酬：{original_freq_return:.2f}%")
print(f"優化策略報酬：{optimized_freq_return:.2f}%")
print(f"原策略損耗：{original_freq_return - freq_return:.2f}%")
print(f"優化策略損耗：{optimized_freq_return - freq_return:.2f}%")
print(f"改善：{(optimized_freq_return - freq_return) - (original_freq_return - freq_return):.2f}%")
print()

# 計算轉換次數
print("=== 轉換次數對比 ===")

# 原策略轉換次數
original_position_changes = df_last_year['position_size'].diff().abs().sum()
print(f"原策略轉換次數：{int(original_position_changes * 2)} 次")  # 估算

# 優化策略轉換次數
optimized_position_changes = df_last_year['optimized_position'].diff().abs().sum()
print(f"優化策略轉換次數：{int(optimized_position_changes * 2)} 次")  # 估算

# 估算
print(f"減少：{int(original_position_changes * 2 - optimized_position_changes * 2)} 次")
print()

# 生成圖表
print("生成圖表...")

fig, axes = plt.subplots(3, 1, figsize=(14, 12))

# 圖表 1：累積報酬對比
ax1 = axes[0]
ax1.plot(df_last_year['date'], df_last_year['index_cumulative'], label='買進持有', linewidth=2, color='gray')
ax1.plot(df_last_year['date'], df_last_year['strategy_cumulative'], label='原策略', linewidth=2, color='red')
ax1.plot(df_last_year['date'], df_last_year['optimized_cumulative'], label='優化策略', linewidth=2, color='blue', linestyle='--')
ax1.set_title('累積報酬對比（過去 1 年）', fontsize=14, fontweight='bold')
ax1.set_ylabel('累積報酬', fontsize=12)
ax1.legend(loc='upper left', fontsize=10)
ax1.grid(True, alpha=0.3)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)

# 圖表 2：倉位變化對比
ax2 = axes[1]
ax2.plot(df_last_year['date'], df_last_year['position_size'], label='原策略倉位', linewidth=1.5, color='red')
ax2.plot(df_last_year['date'], df_last_year['optimized_position'], label='優化策略倉位', linewidth=1.5, color='blue', linestyle='--')
ax2.set_title('倉位變化對比', fontsize=14, fontweight='bold')
ax2.set_ylabel('倉位 (%)', fontsize=12)
ax2.set_ylim([0, 1.1])
ax2.legend(loc='upper left', fontsize=10)
ax2.grid(True, alpha=0.3)
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)

# 圖表 3：相關性與價格趨勢
ax3 = axes[2]
ax3_twin = ax3.twinx()

# 相關性
line1 = ax3.plot(df_last_year['date'], df_last_year['correlation'], label='相關性', linewidth=1.5, color='orange')[0]
ax3.set_ylabel('相關性', fontsize=12)
ax3.tick_params(axis='y', labelcolor='orange')
ax3.set_ylim([0, 1.0])

# 指數價格
line2 = ax3_twin.plot(df_last_year['date'], df_last_year['index_price'], label='指數價格', linewidth=1.5, color='green')[0]
ax3_twin.set_ylabel('指數價格', fontsize=12)
ax3_twin.tick_params(axis='y', labelcolor='green')

# 20 日均線
ax3_twin.plot(df_last_year['date'], df_last_year['ma20'], label='20 日均線', linewidth=1, color='blue', linestyle='--')

ax3.set_title('相關性與價格趨勢', fontsize=14, fontweight='bold')
ax3.set_xlabel('日期', fontsize=12)

# 組合圖例
lines = [line1, line2]
labels = [l.get_label() for l in lines]
ax3.legend(lines, labels, loc='upper left', fontsize=10)

ax3.grid(True, alpha=0.3)
ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax3.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)

plt.tight_layout()
plt.savefig('optimized_strategy_comparison.png', dpi=300, bbox_inches='tight')
print("✅ 圖表已保存：optimized_strategy_comparison.png")
print()

# 保存數據
output_columns = [
    'date', 'index_price', 'correlation', 'high_threshold', 'low_threshold',
    'market_state', 'position_size', 'strategy_cumulative',
    'optimized_position', 'optimized_state', 'optimized_cumulative',
    'ma20', 'price_trend'
]
df_output = df_last_year[output_columns].copy()
df_output.to_csv('optimized_strategy_data.csv', index=False)
print("✅ 數據已保存：optimized_strategy_data.csv")
print()

# 生成摘要報告
summary = f"""
# 優化策略執行報告

## 執行時間
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 優化方案
1. **雙重確認機制**：相關性 + 價格趨勢
2. **固定閾值寬度**：0.15（避免動態增大）
3. **危機市場退出條件**：相關性低於閾值 或 價格突破均線

## 參數設置
- 固定閾值寬度：{FIXED_THRESHOLD_WIDTH}
- 高閾值分位數：{HIGH_THRESHOLD_PERCENTILE * 100}%
- 回看窗口：{ROLLING_WINDOW} 天
- 價格趨勢窗口：20 日均線

## 績效對比

| 指標 | 原策略 | 優化策略 | 改善 |
|------|--------|---------|------|
| 累積報酬率 | {original_return:.2f}% | {optimized_return:.2f}% | {optimized_return - original_return:+.2f}% |
| 最大回撤 | {original_mdd:.2f}% | {optimized_mdd:.2f}% | {optimized_mdd - original_mdd:+.2f}% |
| 波動率 | {original_volatility:.2f}% | {optimized_volatility:.2f}% | {optimized_volatility - original_volatility:+.2f}% |
| 夏普比率 | {original_sharpe:.2f} | {optimized_sharpe:.2f} | {optimized_sharpe - original_sharpe:+.2f} |
| 卡爾馬比率 | {original_calmar:.2f} | {optimized_calmar:.2f} | {optimized_calmar - original_calmar:+.2f} |
| 平均倉位 | {original_avg_position:.1%} | {optimized_avg_position:.1%} | {(optimized_avg_position - original_avg_position)*100:+.1f}% |

## 關鍵改善

### 踏空大行情（2025/04/03 - 2025/07/01）
- 買進持有：{missed_return:.2f}%
- 原策略：{original_missed_return:.2f}%（踏空損失：{original_missed_return - missed_return:.2f}%）
- 優化策略：{optimized_missed_return:.2f}%（踏空損失：{optimized_missed_return - missed_return:.2f}%）
- **改善**：{(optimized_missed_return - missed_return) - (original_missed_return - missed_return):.2f}%

### 頻繁調倉時期（2025/08 - 2025/11）
- 買進持有：{freq_return:.2f}%
- 原策略：{original_freq_return:.2f}%（損耗：{original_freq_return - freq_return:.2f}%）
- 優化策略：{optimized_freq_return:.2f}%（損耗：{optimized_freq_return - freq_return:.2f}%）
- **改善**：{(optimized_freq_return - freq_return) - (original_freq_return - freq_return):.2f}%

## 結論
"""

if optimized_return > original_return:
    summary += f"""
✅ **優化策略優於原策略 {optimized_return - original_return:.2f}%**

**關鍵改善**：
1. 減少踏空大行情損失：{(optimized_missed_return - missed_return) - (original_missed_return - missed_return):.2f}%
2. 減少頻繁調倉損耗：{(optimized_freq_return - freq_return) - (original_freq_return - freq_return):.2f}%
3. 提升夏普比率：{optimized_sharpe - original_sharpe:.2f}
4. 提升卡爾馬比率：{optimized_calmar - original_calmar:.2f}

**推薦**：使用優化策略
"""
else:
    summary += f"""
❌ **優化策略落後原策略 {original_return - optimized_return:.2f}%**

**分析原因**：
1. 可能需要調整參數（閾值寬度、趨勢窗口等）
2. 可能需要更複雜的雙重確認機制
3. 可能需要增加冷卻期

**建議**：進一步優化參數
"""

with open('OPTIMIZED_STRATEGY_REPORT.md', 'w', encoding='utf-8') as f:
    f.write(summary)

print("✅ 報告已保存：OPTIMIZED_STRATEGY_REPORT.md")
print()
print("=== 優化完成 ===")
print("查看圖表：optimized_strategy_comparison.png")
print("查看數據：optimized_strategy_data.csv")
print("查看報告：OPTIMIZED_STRATEGY_REPORT.md")
