#!/usr/bin/env python3
"""
Supertrend 交易深度分析工具
從 Dashboard 資料庫查詢股價數據，計算技術指標，分析假突破、趨勢持久度
"""

import duckdb
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# 資料庫路徑
DATABASE_FILE = "/Users/charlie/Dashboard/backend/market_data_db/market_data.duckdb"

# 連接資料庫
conn = duckdb.connect(database=DATABASE_FILE, read_only=False)

print("=" * 80)
print("🔍 Supertrend 交易深度分析工具")
print("=" * 80)

# 測試查詢：檢查資料庫結構
print("\n📊 檢查資料庫結構...")
print("\n【daily_prices 表結構】")
schema = conn.execute("DESCRIBE daily_prices").fetchdf()
print(schema)

print("\n【數據統計】")
print(conn.execute("""
    SELECT
        COUNT(*) as total_records,
        COUNT(DISTINCT symbol) as unique_symbols,
        MIN(trade_date) as earliest_date,
        MAX(trade_date) as latest_date
    FROM daily_prices
""").fetchdf().to_string(index=False))

# 查詢可用的股票代碼
print("\n【可用股票代碼（前 20 筆）】")
symbols = conn.execute("""
    SELECT symbol, COUNT(*) as days
    FROM daily_prices
    WHERE symbol LIKE '%.TW'
    GROUP BY symbol
    ORDER BY days DESC
    LIMIT 20
""").fetchdf()
print(symbols.to_string(index=False))

# 根據之前的 Supertrend 交易數據，提取一些範例股票
# 從 supertrend_trade_analysis.py 中提取的股票代碼
sample_symbols = [
    '2356.TW', '1609.TW', '1795.TW', '2324.TW', '1504.TW',
    '1514.TW', '1513.TW', '2105.TW', '2727.TW', '1503.TW',
    '2330.TW', '1301.TW', '2317.TW', '2308.TW', '2303.TW'
]

print(f"\n📋 查詢範例股票數據（{len(sample_symbols)} 筆）")

# 查詢這些股票的數據
query = f"""
    SELECT
        symbol,
        trade_date,
        open,
        high,
        low,
        close,
        volume
    FROM daily_prices
    WHERE symbol IN ({','.join([f"'{s}'" for s in sample_symbols])})
    ORDER BY symbol, trade_date
"""

df = conn.execute(query).fetchdf()
print(f"\n✅ 成功查詢 {len(df)} 筆股價數據")

# 保存原始數據
output_dir = Path("/Users/charlie/.openclaw/workspace/kanban/outputs")
output_dir.mkdir(parents=True, exist_ok=True)

df.to_csv(output_dir / "sample_price_data.csv", index=False)
print(f"💾 原始數據已保存到: {output_dir / 'sample_price_data.csv'}")

# 計算技術指標
print("\n" + "=" * 80)
print("🧮 計算技術指標")
print("=" * 80)

def calculate_atr(df, period=14):
    """計算 ATR (Average True Range)"""
    high = df['high']
    low = df['low']
    close = df['close']

    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()

    return atr

def calculate_adx(df, period=14):
    """計算 ADX (Average Directional Index)"""
    high = df['high']
    low = df['low']
    close = df['close']

    # 計算 +DM 和 -DM
    up_move = high - high.shift()
    down_move = low.shift() - low

    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)

    # 計算 TR
    tr = pd.concat([
        high - low,
        abs(high - close.shift()),
        abs(low - close.shift())
    ], axis=1).max(axis=1)

    # 平滑
    atr = pd.Series(tr).rolling(window=period).mean()
    plus_dm_smooth = pd.Series(plus_dm).rolling(window=period).mean()
    minus_dm_smooth = pd.Series(minus_dm).rolling(window=period).mean()

    # 計算 +DI 和 -DI
    plus_di = 100 * (plus_dm_smooth / atr)
    minus_di = 100 * (minus_dm_smooth / atr)

    # 計算 DX
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)

    # 計算 ADX
    adx = dx.rolling(window=period).mean()

    return adx, plus_di, minus_di

def calculate_supertrend(df, period=10, multiplier=3.0):
    """計算 Supertrend"""
    high = df['high']
    low = df['low']
    close = df['close']

    # 計算 ATR
    atr = calculate_atr(df, period)

    # 計算基本 Supertrend
    hl2 = (high + low) / 2
    supertrend = hl2 + (multiplier * atr)
    # 初始 Supertrend 是 hl2 + multiplier * atr

    # 動態調整
    for i in range(1, len(df)):
        if close.iloc[i-1] <= supertrend.iloc[i-1]:
            supertrend.iloc[i] = min(hl2.iloc[i] + multiplier * atr.iloc[i], supertrend.iloc[i-1])
        else:
            supertrend.iloc[i] = max(hl2.iloc[i] - multiplier * atr.iloc[i], supertrend.iloc[i-1])

    # 計算方向
    direction = np.where(close > supertrend, 1, -1)

    return supertrend, direction

# 對每個股票計算指標
results = []

for symbol in df['symbol'].unique():
    symbol_df = df[df['symbol'] == symbol].copy().sort_values('trade_date').reset_index(drop=True)

    if len(symbol_df) < 30:  # 需要至少 30 天的數據
        continue

    # 計算指標
    symbol_df['atr'] = calculate_atr(symbol_df)
    symbol_df['adx'], symbol_df['plus_di'], symbol_df['minus_di'] = calculate_adx(symbol_df)
    symbol_df['supertrend'], symbol_df['st_direction'] = calculate_supertrend(symbol_df)

    # 計算市場狀態
    symbol_df['trend_strength'] = np.where(
        symbol_df['adx'] < 20, '無趨勢',
        np.where(symbol_df['adx'] < 50, '中等', '強')
    )

    # 計算波動率水平
    atr_ratio = symbol_df['atr'] / symbol_df['close']
    symbol_df['volatility_level'] = np.where(
        atr_ratio < 0.015, '低',
        np.where(atr_ratio < 0.03, '中', '高')
    )

    # 計算 Supertrend 翻轉次數
    symbol_df['st_flip'] = symbol_df['st_direction'].diff().abs()
    st_flips = symbol_df['st_flip'].sum()

    results.append({
        'symbol': symbol,
        'total_days': len(symbol_df),
        'avg_adx': symbol_df['adx'].mean(),
        'avg_atr': symbol_df['atr'].mean(),
        'avg_atr_ratio': atr_ratio.mean(),
        'st_flips': st_flips,
        'avg_volatility': symbol_df['volatility_level'].value_counts(normalize=True).to_dict()
    })

# 生成報告
print("\n【技術指標統計】")
results_df = pd.DataFrame(results)
print(results_df.to_string(index=False))

# 保存技術指標數據
# 合併所有股票的技術指標
all_indicators = []
for symbol in df['symbol'].unique():
    symbol_df = df[df['symbol'] == symbol].copy().sort_values('trade_date').reset_index(drop=True)

    if len(symbol_df) < 30:
        continue

    symbol_df['atr'] = calculate_atr(symbol_df)
    symbol_df['adx'], symbol_df['plus_di'], symbol_df['minus_di'] = calculate_adx(symbol_df)
    symbol_df['supertrend'], symbol_df['st_direction'] = calculate_supertrend(symbol_df)
    symbol_df['trend_strength'] = np.where(
        symbol_df['adx'] < 20, '無趨勢',
        np.where(symbol_df['adx'] < 50, '中等', '強')
    )

    all_indicators.append(symbol_df)

if all_indicators:
    indicators_df = pd.concat(all_indicators, ignore_index=True)
    indicators_df.to_csv(output_dir / "sample_indicators.csv", index=False)
    print(f"\n💾 技術指標數據已保存到: {output_dir / 'sample_indicators.csv'}")

# 生成分析報告
print("\n" + "=" * 80)
print("📊 分析報告")
print("=" * 80)

print("\n【市場狀態分布】")
trend_counts = results_df['avg_adx'].apply(
    lambda x: '無趨勢' if x < 20 else ('中等' if x < 50 else '強')
).value_counts()
print(trend_counts)

print("\n【Supertrend 翻轉頻率分析】")
print(f"平均翻轉次數: {results_df['st_flips'].mean():.1f}")
print(f"最多翻轉次數: {results_df['st_flips'].max()}")
print(f"最少翻轉次數: {results_df['st_flips'].min()}")

# 識別假突破潛力
print("\n【假突破風險分析】")
high_flip_risk = results_df[results_df['st_flips'] > results_df['st_flips'].quantile(0.75)]
if len(high_flip_risk) > 0:
    print(f"⚠️ 高翻轉風險股票 ({len(high_flip_risk)} 筆):")
    print(high_flip_risk[['symbol', 'st_flips', 'avg_adx']].to_string(index=False))
else:
    print("✅ 所有股票 Supertrend 翻轉頻率正常")

# 弱趨勢股票
print("\n【弱趨勢股票分析】")
weak_trend = results_df[results_df['avg_adx'] < 25]
if len(weak_trend) > 0:
    print(f"⚠️ 弱趨勢股票 ({len(weak_trend)} 筆, 平均 ADX < 25):")
    print(weak_trend[['symbol', 'avg_adx', 'st_flips']].to_string(index=False))
else:
    print("✅ 所有股票趨勢強度正常")

# 關鍵洞察
print("\n" + "=" * 80)
print("💡 關鍵洞察")
print("=" * 80)

insights = []

# 1. 趨勢強度
avg_adx = results_df['avg_adx'].mean()
if avg_adx < 25:
    insights.append("⚠️ 整體市場趨勢較弱（平均 ADX < 25），假突破風險高")
elif avg_adx < 35:
    insights.append("✅ 市場趨勢中等（平均 ADX 25-35），需要過濾器")
else:
    insights.append("✅ 市場趨勢強勁（平均 ADX > 35），適合趨勢跟隨")

# 2. Supertrend 翻轉
avg_flips = results_df['st_flips'].mean()
if avg_flips > 10:
    insights.append(f"⚠️ Supertrend 翻轉頻繁（平均 {avg_flips:.1f} 次），建議增加過濾器")
elif avg_flips > 5:
    insights.append(f"⚠️ Supertrend 翻轉較多（平均 {avg_flips:.1f} 次），需要多時間框架確認")
else:
    insights.append(f"✅ Supertrend 翻轉正常（平均 {avg_flips:.1f} 次），訊號可靠")

# 3. 波動率
avg_volatility = results_df['avg_atr_ratio'].mean()
if avg_volatility < 0.02:
    insights.append(f"⚠️ 波動率較低（平均 ATR/Price {avg_volatility:.2%}），可能存在盤整")
else:
    insights.append(f"✅ 波動率適中（平均 ATR/Price {avg_volatility:.2%}），有利於趨勢交易")

for insight in insights:
    print(f"\n{insight}")

# 建議
print("\n" + "=" * 80)
print("📌 優化建議")
print("=" * 80)

recommendations = []

# 基於 ADX 過濾
if avg_adx < 30:
    recommendations.append("1. ✅ 加入 ADX 過濾器：ADX > 25 才進場")

# 基於 Supertrend 翻轉頻率
if avg_flips > 5:
    recommendations.append("2. ✅ 加入多時間框架確認：週線和月線趨勢一致")

# 基於波動率
if avg_volatility < 0.02:
    recommendations.append("3. ✅ 加入波動率過濾器：ATR/Price > 2% 才進場")

# 基於持倉時間
recommendations.append("4. ✅ 最小持倉時間：持倉至少 7-10 天，避免短線震盪")

# 假突破檢測
if len(high_flip_risk) > 0 or len(weak_trend) > 0:
    recommendations.append("5. ⚠️ 密切監控高翻轉頻率和弱趨勢股票")

for rec in recommendations:
    print(rec)

# 關閉資料庫連接
conn.close()

print("\n" + "=" * 80)
print("✅ 分析完成！")
print("=" * 80)
print(f"\n📁 輸出文件:")
print(f"  1. {output_dir / 'sample_price_data.csv'} - 原始股價數據")
print(f"  2. {output_dir / 'sample_indicators.csv'} - 技術指標數據")
print(f"\n下一步:")
print(f"  1. 載入完整的 462 筆 Supertrend 交易數據")
print(f"  2. 與技術指標數據結合，進行假突破檢測")
print(f"  3. 建立期望收益模型")
