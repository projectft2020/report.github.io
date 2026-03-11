#!/usr/bin/env python3
"""
Supertrend 策略回測腳本
正確回測四個策略，避免未來函數
"""

import duckdb
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional
import warnings
warnings.filterwarnings('ignore')

# 資料庫路徑
DATABASE_FILE = "/Users/charlie/Dashboard/backend/market_data_db/market_data.duckdb"

# 連接資料庫
conn = duckdb.connect(database=DATABASE_FILE, read_only=False)

print("=" * 80)
print("🔄 Supertrend 策略回測腳本")
print("=" * 80)

@dataclass
class Trade:
    """單筆交易"""
    stock_code: str
    entry_date: str
    exit_date: str
    entry_price: float
    exit_price: float
    quantity: float
    return_pct: float
    holding_days: int
    strategy: str

@dataclass
class StrategyPerformance:
    """策略績效"""
    name: str
    trade_count: int
    total_return: float  # % (複利)
    avg_return: float  # %
    win_rate: float  # %
    profit_factor: float
    max_profit: float  # %
    max_loss: float  # %
    sharpe_ratio: float
    trades: List[Trade]

# 計算 Supertrend
def calculate_supertrend(df, period=10, multiplier=3.0):
    """計算 Supertrend 指標"""
    high = df['high'].values
    low = df['low'].values
    close = df['close'].values

    # 計算 ATR
    tr1 = high - low
    tr2 = np.abs(high - np.roll(close, 1))
    tr3 = np.abs(low - np.roll(close, 1))
    tr = np.maximum.reduce([tr1, tr2, tr3])
    atr = pd.Series(tr).rolling(window=period).mean().values

    # 計算基本 Supertrend
    hl2 = (high + low) / 2
    supertrend = hl2 + multiplier * atr

    # 動態調整
    direction = np.zeros(len(df))
    direction[0] = 1 if close[0] > supertrend[0] else -1

    for i in range(1, len(df)):
        if close[i-1] <= supertrend[i-1]:
            supertrend[i] = min(hl2[i] + multiplier * atr[i], supertrend[i-1])
            direction[i] = 1 if close[i] > supertrend[i] else -1
        else:
            supertrend[i] = max(hl2[i] - multiplier * atr[i], supertrend[i-1])
            direction[i] = 1 if close[i] > supertrend[i] else -1

    return supertrend, direction

# 計算 ADX
def calculate_adx(df, period=14):
    """計算 ADX 指標"""
    high = df['high'].values
    low = df['low'].values
    close = df['close'].values

    # 計算 +DM 和 -DM
    up_move = high - np.roll(high, 1)
    down_move = np.roll(low, 1) - low

    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)

    # 計算 TR
    tr1 = high - low
    tr2 = np.abs(high - np.roll(close, 1))
    tr3 = np.abs(low - np.roll(close, 1))
    tr = np.maximum.reduce([tr1, tr2, tr3])

    # 平滑
    atr = pd.Series(tr).rolling(window=period).mean().values
    plus_dm_smooth = pd.Series(plus_dm).rolling(window=period).mean().values
    minus_dm_smooth = pd.Series(minus_dm).rolling(window=period).mean().values

    # 避免除以 0
    atr_safe = np.where(atr == 0, 1e-6, atr)

    # 計算 +DI 和 -DI
    plus_di = 100 * (plus_dm_smooth / atr_safe)
    minus_di = 100 * (minus_dm_smooth / atr_safe)

    # 計算 DX
    di_sum = plus_di + minus_di
    di_sum_safe = np.where(di_sum == 0, 1e-6, di_sum)
    dx = 100 * np.abs(plus_di - minus_di) / di_sum_safe

    # 計算 ADX
    adx = pd.Series(dx).rolling(window=period).mean().values

    return adx

# 生成模擬交易信號
def generate_trading_signals(symbol, start_date, end_date):
    """從股價數據生成 Supertrend 交易信號"""
    # 查詢股價數據
    query = f"""
        SELECT
            trade_date,
            open,
            high,
            low,
            close,
            volume
        FROM daily_prices
        WHERE symbol = '{symbol}'
          AND trade_date >= '{start_date}'
          AND trade_date <= '{end_date}'
        ORDER BY trade_date
    """

    df = conn.execute(query).fetchdf()

    if len(df) < 30:
        return None, None, None

    # 計算指標
    supertrend, direction = calculate_supertrend(df)
    adx = calculate_adx(df)

    df['supertrend'] = supertrend
    df['direction'] = direction
    df['adx'] = adx

    # 生成交易信號
    signals = []
    current_direction = None

    for i in range(1, len(df)):
        if direction[i] != direction[i-1]:
            # 方向翻轉，生成信號
            current_direction = direction[i]
            signals.append({
                'date': df['trade_date'].iloc[i],
                'price': df['close'].iloc[i],
                'direction': current_direction,  # 1 = long, -1 = short
                'supertrend': supertrend[i],
                'adx': adx[i]
            })

    return df, signals, supertrend

# 策略 1：原始策略
def backtest_original_strategy(df, signals, symbol):
    """原始策略：第 0 天進場，訊號驅動出場"""
    trades = []

    # 只做多頭交易
    long_signals = [s for s in signals if s['direction'] == 1]

    for entry_signal in long_signals:
        entry_date = entry_signal['date']
        entry_price = entry_signal['price']

        # 找到下一個反向信號（從所有信號中找）
        exit_signal = None
        for s in signals:
            if s['direction'] == -1 and s['date'] > entry_date:
                exit_signal = s
                break

        if not exit_signal:
            continue

        exit_date = exit_signal['date']
        exit_price = exit_signal['price']

        # 計算報酬
        return_pct = (exit_price - entry_price) / entry_price * 100

        # 計算持倉天數
        entry_dt = pd.to_datetime(entry_date)
        exit_dt = pd.to_datetime(exit_date)
        holding_days = (exit_dt - entry_dt).days

        trades.append(Trade(
            stock_code=symbol,
            entry_date=entry_date,
            exit_date=exit_date,
            entry_price=entry_price,
            exit_price=exit_price,
            quantity=1.0,
            return_pct=return_pct,
            holding_days=holding_days,
            strategy="原始策略"
        ))

    return trades

# 策略 2：延遲進場（第 8 天）
def backtest_delayed_strategy(df, signals, symbol, adx_threshold=None):
    """
    延遲進場：第 8 天進場，訊號驅動出場
    
    Args:
        adx_threshold: ADX 閾值，如果 None 則不過濾
    """
    trades = []

    # 只做多頭交易
    long_signals = [s for s in signals if s['direction'] == 1]

    for entry_signal in long_signals:
        entry_date = entry_signal['date']
        entry_price = entry_signal['price']
        entry_adx = entry_signal.get('adx', 0)

        # ADX 過濾
        if adx_threshold is not None and entry_adx < adx_threshold:
            continue  # ADX 低，無趨勢，跳過

        # 延遲 8 天進場
        entry_dt = pd.to_datetime(entry_date)
        delayed_date = entry_dt + timedelta(days=8)

        # 檢查延遲日期是否有數據
        delayed_date_str = delayed_date.strftime('%Y-%m-%d')

        # 查詢延遲日期的價格
        price_query = f"""
            SELECT close
            FROM daily_prices
            WHERE symbol = '{symbol}'
              AND trade_date = '{delayed_date_str}'
        """

        price_result = conn.execute(price_query).fetchone()

        if not price_result:
            continue  # 沒有數據，跳過

        actual_entry_price = price_result[0]

        # 找到下一個反向信號
        exit_signal = None
        for s in signals:
            if s['direction'] == -1 and s['date'] > entry_date:
                exit_signal = s
                break

        if not exit_signal:
            continue

        exit_date = exit_signal['date']
        exit_price = exit_signal['price']

        # 檢查延遲日期是否在出場日期之前
        if pd.to_datetime(delayed_date_str) >= pd.to_datetime(exit_date):
            continue  # 信號已經翻轉，不能進場

        # 計算報酬
        return_pct = (exit_price - actual_entry_price) / actual_entry_price * 100

        # 計算持倉天數
        exit_dt = pd.to_datetime(exit_date)
        holding_days = (exit_dt - pd.to_datetime(delayed_date_str)).days

        strategy_name = "延遲進場" if adx_threshold is None else f"延遲進場+ADX{adx_threshold}"
        
        trades.append(Trade(
            stock_code=symbol,
            entry_date=delayed_date_str,
            exit_date=exit_date,
            entry_price=actual_entry_price,
            exit_price=exit_price,
            quantity=1.0,
            return_pct=return_pct,
            holding_days=holding_days,
            strategy=strategy_name
        ))

    return trades

# 策略 3：動態風險管理
def backtest_dynamic_strategy(df, signals, symbol):
    """動態風險管理：第 0 天進場，第 7/11 天評估，訊號驅動出場"""
    trades = []

    # 只做多頭交易
    long_signals = [s for s in signals if s['direction'] == 1]

    for i, entry_signal in enumerate(long_signals):
        entry_date = entry_signal['date']
        entry_price = entry_signal['price']

        # 查詢第 7 天的價格
        day7_dt = pd.to_datetime(entry_date) + timedelta(days=7)
        day7_str = day7_dt.strftime('%Y-%m-%d')

        day7_query = f"""
            SELECT close
            FROM daily_prices
            WHERE symbol = '{symbol}'
              AND trade_date = '{day7_str}'
        """

        day7_result = conn.execute(day7_query).fetchone()

        if not day7_result:
            continue

        day7_price = day7_result[0]
        day7_return = (day7_price - entry_price) / entry_price * 100

        # 第 7 天評估
        if day7_return < -3:
            # 虧損 > 3%，出場
            trades.append(Trade(
                stock_code=symbol,
                entry_date=entry_date,
                exit_date=day7_str,
                entry_price=entry_price,
                exit_price=day7_price,
                quantity=1.0,
                return_pct=day7_return,
                holding_days=7,
                strategy="動態風險管理"
            ))
            continue

        # 查詢第 11 天的價格
        day11_dt = pd.to_datetime(entry_date) + timedelta(days=11)
        day11_str = day11_dt.strftime('%Y-%m-%d')

        day11_query = f"""
            SELECT close
            FROM daily_prices
            WHERE symbol = '{symbol}'
              AND trade_date = '{day11_str}'
        """

        day11_result = conn.execute(day11_query).fetchone()

        if not day11_result:
            continue

        day11_price = day11_result[0]
        day11_return = (day11_price - entry_price) / entry_price * 100

        # 第 11 天評估
        if day11_return < -4:
            # 虧損 > 4%，出場
            trades.append(Trade(
                stock_code=symbol,
                entry_date=entry_date,
                exit_date=day11_str,
                entry_price=entry_price,
                exit_price=day11_price,
                quantity=1.0,
                return_pct=day11_return,
                holding_days=11,
                strategy="動態風險管理"
            ))
            continue

        # 找到下一個反向信號
        exit_signal = None
        for j in range(i+1, len(signals)):
            if signals[j]['direction'] == -1 and signals[j]['date'] > entry_date:
                exit_signal = signals[j]
                break

        if not exit_signal:
            continue

        exit_date = exit_signal['date']
        exit_price = exit_signal['price']

        # 計算報酬
        return_pct = (exit_price - entry_price) / entry_price * 100

        # 計算持倉天數
        entry_dt = pd.to_datetime(entry_date)
        exit_dt = pd.to_datetime(exit_date)
        holding_days = (exit_dt - entry_dt).days

        trades.append(Trade(
            stock_code=symbol,
            entry_date=entry_date,
            exit_date=exit_date,
            entry_price=entry_price,
            exit_price=exit_price,
            quantity=1.0,
            return_pct=return_pct,
            holding_days=holding_days,
            strategy="動態風險管理"
        ))

    return trades

# 策略 4：延遲+動態（第 8 天進場 + 第 7 天篩選）
def backtest_hybrid_strategy(df, signals, symbol):
    """延遲+動態：第 7 天篩選，第 8 天進場，訊號驅動出場"""
    trades = []

    # 只做多頭交易
    long_signals = [s for s in signals if s['direction'] == 1]

    for i, entry_signal in enumerate(long_signals):
        entry_date = entry_signal['date']
        entry_price = entry_signal['price']

        # 查詢第 7 天的價格（篩選）
        day7_dt = pd.to_datetime(entry_date) + timedelta(days=7)
        day7_str = day7_dt.strftime('%Y-%m-%d')

        day7_query = f"""
            SELECT close
            FROM daily_prices
            WHERE symbol = '{symbol}'
              AND trade_date = '{day7_str}'
        """

        day7_result = conn.execute(day7_query).fetchone()

        if not day7_result:
            continue

        day7_price = day7_result[0]
        day7_return = (day7_price - entry_price) / entry_price * 100

        # 第 7 天篩選：虧損 > 1% 不進場
        if day7_return > 1:
            continue  # 過濾掉

        # 延遲 8 天進場
        delayed_date = pd.to_datetime(entry_date) + timedelta(days=8)
        delayed_date_str = delayed_date.strftime('%Y-%m-%d')

        # 查詢延遲日期的價格
        price_query = f"""
            SELECT close
            FROM daily_prices
            WHERE symbol = '{symbol}'
              AND trade_date = '{delayed_date_str}'
        """

        price_result = conn.execute(price_query).fetchone()

        if not price_result:
            continue  # 沒有數據，跳過

        actual_entry_price = price_result[0]

        # 找到下一個反向信號
        exit_signal = None
        for j in range(i+1, len(signals)):
            if signals[j]['direction'] == -1 and signals[j]['date'] > entry_date:
                exit_signal = signals[j]
                break

        if not exit_signal:
            continue

        exit_date = exit_signal['date']
        exit_price = exit_signal['price']

        # 檢查延遲日期是否在出場日期之前
        if pd.to_datetime(delayed_date_str) >= pd.to_datetime(exit_date):
            continue  # 信號已經翻轉，不能進場

        # 計算報酬
        return_pct = (exit_price - actual_entry_price) / actual_entry_price * 100

        # 計算持倉天數
        exit_dt = pd.to_datetime(exit_date)
        holding_days = (exit_dt - pd.to_datetime(delayed_date_str)).days

        trades.append(Trade(
            stock_code=symbol,
            entry_date=delayed_date_str,
            exit_date=exit_date,
            entry_price=actual_entry_price,
            exit_price=exit_price,
            quantity=1.0,
            return_pct=return_pct,
            holding_days=holding_days,
            strategy="延遲+動態"
        ))

    return trades

# 計算策略績效
def calculate_performance(trades: List[Trade]) -> StrategyPerformance:
    """計算策略績效指標"""
    if len(trades) == 0:
        return StrategyPerformance(
            name="",
            trade_count=0,
            total_return=0,
            avg_return=0,
            win_rate=0,
            profit_factor=0,
            max_profit=0,
            max_loss=0,
            sharpe_ratio=0,
            trades=[]
        )

    # 基礎統計
    returns = [t.return_pct for t in trades]

    # 總報酬（算術平均 × 交易筆數）
    # 假設每筆交易投入固定資金，按算術方式累計
    total_return = np.sum(returns)

    # 平均報酬
    avg_return = np.mean(returns)

    # 勝率
    win_count = sum(1 for r in returns if r > 0)
    win_rate = win_count / len(returns) * 100

    # 獲利因子
    profits = [r for r in returns if r > 0]
    losses = [abs(r) for r in returns if r < 0]

    if sum(losses) == 0:
        profit_factor = float('inf')
    else:
        profit_factor = sum(profits) / sum(losses)

    # 最大獲利和最大虧損
    max_profit = max(returns)
    max_loss = min(returns)

    # Sharpe Ratio
    # 假設無風險利率為 0
    if len(returns) > 1:
        sharpe_ratio = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
    else:
        sharpe_ratio = 0

    strategy_name = trades[0].strategy if trades else ""

    return StrategyPerformance(
        name=strategy_name,
        trade_count=len(trades),
        total_return=total_return,
        avg_return=avg_return,
        win_rate=win_rate,
        profit_factor=profit_factor,
        max_profit=max_profit,
        max_loss=max_loss,
        sharpe_ratio=sharpe_ratio,
        trades=trades
    )

# 主回測流程
def run_backtest():
    """執行完整回測"""
    # 查詢可用的股票代碼
    query = """
        SELECT symbol, COUNT(*) as days, MIN(trade_date) as start_date, MAX(trade_date) as end_date
        FROM daily_prices
        WHERE symbol LIKE '%.TW'
        GROUP BY symbol
        HAVING days > 200
        ORDER BY days DESC
        LIMIT 20
    """

    stocks = conn.execute(query).fetchdf()

    print(f"\n📊 找到 {len(stocks)} 支股票")

    all_trades = {
        '原始策略': [],
        '延遲進場': [],
        '延遲進場+ADX20': [],
        '延遲進場+ADX25': [],
        '延遲進場+ADX30': [],
        '動態風險管理': [],
        '延遲+動態': []
    }

    for _, stock in stocks.iterrows():
        symbol = stock['symbol']
        start_date = stock['start_date']
        end_date = stock['end_date']

        print(f"\n📈 處理 {symbol}...")

        # 生成交易信號
        df, signals, supertrend = generate_trading_signals(symbol, start_date, end_date)

        if df is None or len(signals) == 0:
            print(f"  ⚠️ 沒有足夠的信號，跳過")
            continue

        print(f"  ✅ 生成 {len(signals)} 個信號")

        # 回測各個策略
        original_trades = backtest_original_strategy(df, signals, symbol)
        delayed_trades = backtest_delayed_strategy(df, signals, symbol)
        delayed_adx20_trades = backtest_delayed_strategy(df, signals, symbol, adx_threshold=20)
        delayed_adx25_trades = backtest_delayed_strategy(df, signals, symbol, adx_threshold=25)
        delayed_adx30_trades = backtest_delayed_strategy(df, signals, symbol, adx_threshold=30)
        dynamic_trades = backtest_dynamic_strategy(df, signals, symbol)
        hybrid_trades = backtest_hybrid_strategy(df, signals, symbol)

        print(f"  原始策略: {len(original_trades)} 筆")
        print(f"  延遲進場: {len(delayed_trades)} 筆")
        print(f"  延遲進場+ADX20: {len(delayed_adx20_trades)} 筆")
        print(f"  延遲進場+ADX25: {len(delayed_adx25_trades)} 筆")
        print(f"  延遲進場+ADX30: {len(delayed_adx30_trades)} 筆")
        print(f"  動態風險管理: {len(dynamic_trades)} 筆")
        print(f"  延遲+動態: {len(hybrid_trades)} 筆")

        all_trades['原始策略'].extend(original_trades)
        all_trades['延遲進場'].extend(delayed_trades)
        all_trades['延遲進場+ADX20'].extend(delayed_adx20_trades)
        all_trades['延遲進場+ADX25'].extend(delayed_adx25_trades)
        all_trades['延遲進場+ADX30'].extend(delayed_adx30_trades)
        all_trades['動態風險管理'].extend(dynamic_trades)
        all_trades['延遲+動態'].extend(hybrid_trades)

    # 計算各策略績效
    print("\n" + "=" * 80)
    print("📊 策略績效對比")
    print("=" * 80)

    results = {}
    for strategy_name, trades in all_trades.items():
        print(f"\n【{strategy_name}】")
        performance = calculate_performance(trades)
        results[strategy_name] = performance

        print(f"  交易筆數: {performance.trade_count}")
        print(f"  總報酬: {performance.total_return:.2f}%")
        print(f"  平均報酬: {performance.avg_return:.2f}%")
        print(f"  勝率: {performance.win_rate:.1f}%")
        print(f"  獲利因子: {performance.profit_factor:.2f}" if performance.profit_factor != float('inf') else "  獲利因子: ∞")
        print(f"  最大獲利: {performance.max_profit:.2f}%")
        print(f"  最大虧損: {performance.max_loss:.2f}%")
        print(f"  Sharpe Ratio: {performance.sharpe_ratio:.2f}")

    # 生成對比表
    print("\n" + "=" * 80)
    print("📊 策略對比表")
    print("=" * 80)

    print(f"{'策略':<15} {'筆數':>6} {'總報酬':>10} {'平均報酬':>10} {'勝率':>6} {'獲利因子':>10} {'最大虧損':>10} {'Sharpe':>8}")
    print("-" * 80)

    for strategy_name, performance in results.items():
        pf = f"{performance.profit_factor:.2f}" if performance.profit_factor != float('inf') else "∞"
        print(f"{strategy_name:<15} {performance.trade_count:>6} {performance.total_return:>9.2f}% {performance.avg_return:>9.2f}% {performance.win_rate:>5.1f}% {pf:>10} {performance.max_loss:>9.2f}% {performance.sharpe_ratio:>7.2f}")

    # 保存結果
    output_dir = Path("/Users/charlie/.openclaw/workspace/kanban/outputs")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 保存所有交易
    all_trades_df = pd.DataFrame([
        {
            'stock_code': t.stock_code,
            'entry_date': t.entry_date,
            'exit_date': t.exit_date,
            'entry_price': t.entry_price,
            'exit_price': t.exit_price,
            'return_pct': t.return_pct,
            'holding_days': t.holding_days,
            'strategy': t.strategy
        }
        for trades in all_trades.values()
        for t in trades
    ])

    all_trades_df.to_csv(output_dir / "backtest_all_trades.csv", index=False)
    print(f"\n💾 所有交易已保存到: {output_dir / 'backtest_all_trades.csv'}")

    # 保存績效摘要
    performance_df = pd.DataFrame([
        {
            'strategy': name,
            'trade_count': perf.trade_count,
            'total_return': perf.total_return,
            'avg_return': perf.avg_return,
            'win_rate': perf.win_rate,
            'profit_factor': perf.profit_factor,
            'max_profit': perf.max_profit,
            'max_loss': perf.max_loss,
            'sharpe_ratio': perf.sharpe_ratio
        }
        for name, perf in results.items()
    ])

    performance_df.to_csv(output_dir / "backtest_performance.csv", index=False)
    print(f"💾 績效摘要已保存到: {output_dir / 'backtest_performance.csv'}")

    return results

if __name__ == "__main__":
    # 執行回測
    results = run_backtest()

    # 關閉資料庫連接
    conn.close()

    print("\n" + "=" * 80)
    print("✅ 回測完成！")
    print("=" * 80)
