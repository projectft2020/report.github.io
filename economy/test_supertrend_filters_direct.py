#!/usr/bin/env python3
"""
Direct Supertrend Filter Backtest Analysis

Tests individual filters against Supertrend strategy using VectorBT directly.
This bypasses the Dashboard API and uses the database directly.

Author: Charlie (Orchestrator)
Created: 2026-03-03
"""

import sys
sys.path.insert(0, '/Users/charlie/Dashboard/backend')

import pandas as pd
import numpy as np
import vectorbt as vbt
import duckdb
import pandas_ta as ta
from datetime import date, datetime
from typing import Dict, List, Any, Tuple
import json

# Database connection
DB_PATH = "/Users/charlie/Dashboard/data/market_data_db/market_data.duckdb"

# TW Strategy Universe
TW_UNIVERSE = [
    "1101.TW", "1102.TW", "1216.TW", "1301.TW", "1303.TW",
    "1326.TW", "1402.TW", "2002.TW", "2105.TW", "2207.TW",
    "2301.TW", "2303.TW", "2308.TW", "2311.TW", "2317.TW",
    "2324.TW", "2327.TW", "2330.TW", "2347.TW", "2352.TW",
    "2357.TW", "2379.TW", "2382.TW", "2408.TW", "2409.TW",
    "2454.TW", "2474.TW", "2498.TW", "2603.TW", "2610.TW",
    "2615.TW", "2707.TW", "2880.TW", "2881.TW", "2882.TW",
    "2884.TW", "2885.TW", "2886.TW", "2887.TW", "2888.TW",
    "2890.TW", "2891.TW", "2892.TW", "2912.TW", "3008.TW",
    "3014.TW", "3023.TW", "3034.TW", "3045.TW", "3231.TW",
    "3443.TW", "3481.TW", "4938.TW", "4904.TW", "4915.TW",
    "4935.TW", "5880.TW", "5871.TW", "5876.TW", "5904.TW",
    "5871.TW", "6116.TW", "6415.TW", "6416.TW", "6446.TW",
    "6505.TW", "8046.TW", "8070.TW", "8078.TW", "8081.TW",
    "8101.TW", "8215.TW", "8454.TW", "9910.TW", "2383.TW"
]


class DirectFilterBacktester:
    """Direct VectorBT backtester with filter testing."""

    def __init__(self):
        self.conn = duckdb.connect(DB_PATH, read_only=True)
        self.results = []

    def load_data(self, symbols: List[str], start_date: date, end_date: date) -> Dict[str, pd.DataFrame]:
        """Load OHLCV data from database."""
        ohlcv_dict = {}

        for symbol in symbols:
            query = f"""
                SELECT
                    date,
                    open,
                    high,
                    low,
                    close,
                    volume
                FROM ohlcv_data
                WHERE symbol = '{symbol}'
                    AND date >= '{start_date}'
                    AND date <= '{end_date}'
                ORDER BY date
            """

            try:
                df = self.conn.execute(query).df()
                if not df.empty:
                    df = df.set_index('date')
                    ohlcv_dict[symbol] = df
            except Exception as e:
                print(f"Warning: Failed to load data for {symbol}: {e}")

        return ohlcv_dict

    def calculate_supertrend(self, df: pd.DataFrame, length: int = 10, multiplier: float = 3.0) -> pd.DataFrame:
        """Calculate Supertrend indicator."""
        hl2 = (df['high'] + df['low']) / 2
        atr = ta.atr(df['high'], df['low'], df['close'], length=length)

        supertrend = ta.supertrend(df['high'], df['low'], df['close'], length=length, multiplier=multiplier)
        return supertrend

    def apply_ma_filter(self, df: pd.DataFrame, ma_period: int) -> pd.Series:
        """Apply MA filter - only allow entries when price > MA."""
        ma = df['close'].rolling(window=ma_period).mean()
        return df['close'] > ma

    def apply_volatility_filter(self, df: pd.DataFrame, min_vol: float = 0.01, max_vol: float = 0.08) -> pd.Series:
        """Apply volatility filter - only allow entries within volatility range."""
        returns = df['close'].pct_change()
        volatility = returns.rolling(window=20).std()
        return (volatility >= min_vol) & (volatility <= max_vol)

    def run_backtest(
        self,
        filter_name: str,
        symbols: List[str],
        start_date: date,
        end_date: date,
        ma_filter: int = None,
        vol_filter: Tuple[float, float] = None,
        max_positions: int = None,
        position_size: float = 0.1
    ) -> Dict[str, Any]:
        """Run a single backtest with given filters."""

        # Load data
        ohlcv_dict = self.load_data(symbols, start_date, end_date)
        if not ohlcv_dict:
            print(f"❌ No data loaded for {filter_name}")
            return None

        # Create DataFrames
        all_close = pd.DataFrame({sym: df['close'] for sym, df in ohlcv_dict.items()})
        all_open = pd.DataFrame({sym: df['open'] for sym, df in ohlcv_dict.items()})
        all_high = pd.DataFrame({sym: df['high'] for sym, df in ohlcv_dict.items()})
        all_low = pd.DataFrame({sym: df['low'] for sym, df in ohlcv_dict.items()})
        all_volume = pd.DataFrame({sym: df['volume'] for sym, df in ohlcv_dict.items()})

        # Calculate Supertrend signals
        entries = pd.DataFrame(False, index=all_close.index, columns=all_close.columns)
        exits = pd.DataFrame(False, index=all_close.index, columns=all_close.columns)

        for symbol in all_close.columns:
            if symbol in ohlcv_dict:
                df = ohlcv_dict[symbol]
                supertrend = self.calculate_supertrend(df, length=10, multiplier=3.0)

                # Entry: Supertrend turns up
                st_trend = supertrend['SUPERTd_10_3.0']
                entries[symbol] = (st_trend == 1) & (st_trend.shift(1) != 1)

                # Exit: Supertrend turns down
                exits[symbol] = (st_trend == -1) & (st_trend.shift(1) != -1)

        # Apply filters
        if ma_filter:
            for symbol in all_close.columns:
                if symbol in ohlcv_dict:
                    df = ohlcv_dict[symbol]
                    ma_mask = self.apply_ma_filter(df, ma_filter)
                    entries[symbol] = entries[symbol] & ma_mask

        if vol_filter:
            min_vol, max_vol = vol_filter
            for symbol in all_close.columns:
                if symbol in ohlcv_dict:
                    df = ohlcv_dict[symbol]
                    vol_mask = self.apply_volatility_filter(df, min_vol, max_vol)
                    entries[symbol] = entries[symbol] & vol_mask

        # Shift signals for next-open execution
        entries = entries.shift(1)
        exits = exits.shift(1)

        # Apply max positions
        if max_positions:
            entries_sum = entries.sum(axis=1)
            entries = entries & (entries_sum <= max_positions)

        # Build portfolio
        portfolio = vbt.Portfolio.from_signals(
            close=all_close,
            open=all_open,
            entries=entries,
            exits=exits,
            init_cash=100000.0,
            fees=0.002,
            size=position_size,
            size_type='percent',
            freq='1D',
            group_by=True,
            cash_sharing=True,
            call_seq='auto'
        )

        # Extract stats
        stats = self._extract_stats(portfolio)

        print(f"✅ Completed: {filter_name}")
        print(f"   Return: {stats['total_return']:.2%} | Sharpe: {stats['sharpe']:.2f} | DD: {stats['max_drawdown']:.2%} | Trades: {stats['trades_count']}")
        print()

        result = {
            'filter_name': filter_name,
            'total_return': stats['total_return'],
            'cagr': stats['cagr'],
            'sharpe': stats['sharpe'],
            'max_drawdown': stats['max_drawdown'],
            'win_rate': stats['win_rate'],
            'profit_factor': stats['profit_factor'],
            'trades_count': stats['trades_count'],
            'avg_trade': stats['avg_trade']
        }

        self.results.append(result)
        return result

    def _extract_stats(self, portfolio) -> Dict[str, float]:
        """Extract statistics from portfolio."""
        stats = {}

        # Total return
        stats['total_return'] = portfolio.total_return()
        stats['cagr'] = stats['total_return'] ** (1 / 7) - 1  # ~7 years

        # Sharpe
        stats['sharpe'] = portfolio.sharpe_ratio()

        # Max drawdown
        stats['max_drawdown'] = portfolio.max_drawdown()

        # Win rate
        trades = portfolio.trades.records_readable
        if len(trades) > 0:
            winning_trades = trades[trades['pnl'] > 0]
            stats['win_rate'] = len(winning_trades) / len(trades)
        else:
            stats['win_rate'] = 0.0

        # Profit factor
        if len(trades) > 0:
            gross_profit = trades[trades['pnl'] > 0]['pnl'].sum()
            gross_loss = abs(trades[trades['pnl'] < 0]['pnl'].sum())
            stats['profit_factor'] = gross_profit / gross_loss if gross_loss > 0 else 0
        else:
            stats['profit_factor'] = 0

        # Trade count
        stats['trades_count'] = len(trades)

        # Average trade
        if len(trades) > 0:
            stats['avg_trade'] = trades['pnl'].mean()
        else:
            stats['avg_trade'] = 0

        return stats

    def print_comparison(self):
        """Print comparison table."""
        df = pd.DataFrame(self.results)

        print("\n" + "="*120)
        print("SUPERTREND FILTER BACKTEST COMPARISON")
        print("="*120)
        print(f"{'Filter':<40} {'Return':>10} {'CAGR':>8} {'Sharpe':>8} {'Max DD':>10} {'Win Rate':>10} {'Trades':>8}")
        print("-"*120)

        for _, row in df.iterrows():
            filter_name = row['filter_name'][:40]
            total_return = f"{row['total_return']:.2%}"
            cagr = f"{row['cagr']:.2%}"
            sharpe = f"{row['sharpe']:.2f}"
            max_dd = f"{row['max_drawdown']:.2%}"
            win_rate = f"{row['win_rate']:.2%}"
            trades = int(row['trades_count'])

            print(f"{filter_name:<40} {total_return:>10} {cagr:>8} {sharpe:>8} {max_dd:>10} {win_rate:>10} {trades:>8}")

        print("="*120 + "\n")

        # Calculate improvements vs baseline
        baseline = df[df['filter_name'] == 'Baseline'].iloc[0]
        print("IMPROVEMENT VS BASELINE:")
        print("-"*120)
        for _, row in df.iterrows():
            if row['filter_name'] == 'Baseline':
                continue

            filter_name = row['filter_name'][:40]
            ret_diff = (row['total_return'] - baseline['total_return']) * 100
            sharpe_diff = row['sharpe'] - baseline['sharpe']
            dd_diff = (row['max_drawdown'] - baseline['max_drawdown']) * 100
            win_rate_diff = (row['win_rate'] - baseline['win_rate']) * 100

            print(f"{filter_name:<40}")
            print(f"  Return: {ret_diff:+.2f}% | Sharpe: {sharpe_diff:+.2f} | DD: {dd_diff:+.2f}% | Win Rate: {win_rate_diff:+.2f}%")
        print("-"*120 + "\n")


def main():
    """Run all filter backtests."""

    print("\n" + "="*120)
    print("SUPERTREND DIRECT FILTER BACKTEST ANALYSIS")
    print("="*120 + "\n")

    backtester = DirectFilterBacktester()

    # Date range
    start_date = date(2019, 1, 1)
    end_date = date(2026, 2, 28)

    print("Date Range: 2019-01-01 to 2026-02-28 (~7 years)")
    print(f"Universe: {len(TW_UNIVERSE)} symbols\n")

    # 1. Baseline (No filters)
    print("1️⃣  Running Baseline (No Filters)...")
    backtester.run_backtest(
        filter_name="Baseline",
        symbols=TW_UNIVERSE,
        start_date=start_date,
        end_date=end_date
    )

    # 2. MA Filters
    print("2️⃣  MA Filters...")
    print("   a) MA60 Filter...")
    backtester.run_backtest(
        filter_name="MA60 Filter",
        symbols=TW_UNIVERSE,
        start_date=start_date,
        end_date=end_date,
        ma_filter=60
    )

    print("   b) MA200 Filter...")
    backtester.run_backtest(
        filter_name="MA200 Filter",
        symbols=TW_UNIVERSE,
        start_date=start_date,
        end_date=end_date,
        ma_filter=200
    )

    # 3. Volatility Filters
    print("3️⃣  Volatility Filters...")
    print("   a) Exclude Low Volatility (< 1%)...")
    backtester.run_backtest(
        filter_name="Exclude Low Volatility",
        symbols=TW_UNIVERSE,
        start_date=start_date,
        end_date=end_date,
        vol_filter=(0.01, 1.0)  # Exclude vol < 1%
    )

    print("   b) Exclude High Volatility (> 8%)...")
    backtester.run_backtest(
        filter_name="Exclude High Volatility",
        symbols=TW_UNIVERSE,
        start_date=start_date,
        end_date=end_date,
        vol_filter=(0.0, 0.08)  # Exclude vol > 8%
    )

    # 4. Position Management
    print("4️⃣  Position Management...")
    print("   a) Max 5 Positions...")
    backtester.run_backtest(
        filter_name="Max 5 Positions",
        symbols=TW_UNIVERSE,
        start_date=start_date,
        end_date=end_date,
        max_positions=5
    )

    print("   b) Max 3 Positions...")
    backtester.run_backtest(
        filter_name="Max 3 Positions",
        symbols=TW_UNIVERSE,
        start_date=start_date,
        end_date=end_date,
        max_positions=3
    )

    print("   c) Position Size 5% (more conservative)...")
    backtester.run_backtest(
        filter_name="Position Size 5%",
        symbols=TW_UNIVERSE,
        start_date=start_date,
        end_date=end_date,
        position_size=0.05
    )

    # 5. Combined Filters
    print("5️⃣  Combined Filters...")
    print("   a) MA60 + Max 5 Positions...")
    backtester.run_backtest(
        filter_name="MA60 + Max 5 Positions",
        symbols=TW_UNIVERSE,
        start_date=start_date,
        end_date=end_date,
        ma_filter=60,
        max_positions=5
    )

    print("   b) MA200 + Max 5 Positions...")
    backtester.run_backtest(
        filter_name="MA200 + Max 5 Positions",
        symbols=TW_UNIVERSE,
        start_date=start_date,
        end_date=end_date,
        ma_filter=200,
        max_positions=5
    )

    print("   c) MA60 + Exclude Low Vol + Max 5 Positions...")
    backtester.run_backtest(
        filter_name="MA60 + Exclude Low Vol + Max 5",
        symbols=TW_UNIVERSE,
        start_date=start_date,
        end_date=end_date,
        ma_filter=60,
        vol_filter=(0.01, 1.0),
        max_positions=5
    )

    # Print comparison
    backtester.print_comparison()

    # Save results
    df = pd.DataFrame(backtester.results)
    output_path = "/Users/charlie/.openclaw/workspace/economy/supertrend_direct_filter_backtest_results.csv"
    df.to_csv(output_path, index=False)
    print(f"✅ Results saved to: {output_path}")

    # Save JSON summary
    summary = {
        "test_date": datetime.now().isoformat(),
        "strategy": "Supertrend (length=10, multiplier=3.0)",
        "universe": "TW Strategy (100 symbols)",
        "date_range": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "baseline": df[df['filter_name'] == 'Baseline'].to_dict('records')[0],
        "all_results": df.to_dict('records'),
        "best_return": df.loc[df['total_return'].idxmax()].to_dict(),
        "best_sharpe": df.loc[df['sharpe'].idxmax()].to_dict(),
        "lowest_drawdown": df.loc[df['max_drawdown'].idxmin()].to_dict()
    }

    json_path = "/Users/charlie/.openclaw/workspace/economy/supertrend_direct_filter_backtest_summary.json"
    with open(json_path, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"✅ Summary saved to: {json_path}")


if __name__ == "__main__":
    main()
