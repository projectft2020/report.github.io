#!/usr/bin/env python3
"""
Supertrend Filter Backtest Analysis

Tests individual filters against Supertrend strategy to understand their impact.

Author: Charlie (Orchestrator)
Created: 2026-03-03
"""

import requests
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any

# Dashboard API Configuration
API_BASE = "http://100.79.80.117:8000"
ADMIN_TOKEN = "admin995"

# Backtest endpoint
BACKTEST_ENDPOINT = "/api/strategies/backtest/run-saved"

# Headers for API requests
headers = {
    "X-Admin-Token": ADMIN_TOKEN,
    "Content-Type": "application/json"
}


class FilterBacktester:
    """Backtest Supertrend with different filters."""

    def __init__(self):
        self.results = []

    def run_backtest(self, filter_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single backtest with given parameters."""

        # Base strategy configuration
        strategy_id = "supertrend_7b9f5ebf"  # Original Supertrend strategy

        # Prepare request
        request_data = {
            "strategy_id": strategy_id,
            "start_date": "2019-01-01",
            "end_date": "2026-03-01",
            "initial_cash": 100000,
            "commission": 0.002
        }

        # Add parameters for run-saved endpoint
        request_data.update(params)

        try:
            # Run backtest
            response = requests.post(
                f"{API_BASE}{BACKTEST_ENDPOINT}",
                json=request_data,
                headers=headers,
                timeout=60
            )

            if response.status_code != 200:
                print(f"❌ Error running backtest for {filter_name}: {response.text}")
                return None

            result = response.json()

            # Extract key metrics
            metrics = result.get('metrics', {})
            stats = result.get('stats', {})

            summary = {
                'filter_name': filter_name,
                'run_id': result.get('run_id'),
                'total_return': metrics.get('total_return', 0),
                'cagr': metrics.get('cagr', 0),
                'sharpe': metrics.get('sharpe', 0),
                'max_drawdown': metrics.get('max_drawdown', 0),
                'win_rate': metrics.get('win_rate', 0),
                'profit_factor': metrics.get('profit_factor', 0),
                'trades_count': metrics.get('trades_count', 0),
                'avg_trade': metrics.get('avg_trade', 0),
                'final_value': result.get('final_value', 0)
            }

            print(f"✅ Completed: {filter_name}")
            print(f"   Return: {summary['total_return']:.2%} | Sharpe: {summary['sharpe']:.2f} | DD: {summary['max_drawdown']:.2%} | Trades: {summary['trades_count']}")
            print()

            self.results.append(summary)
            return summary

        except Exception as e:
            print(f"❌ Exception running backtest for {filter_name}: {e}")
            return None

    def compare_results(self) -> pd.DataFrame:
        """Compare all backtest results."""
        df = pd.DataFrame(self.results)
        return df

    def print_comparison(self):
        """Print comparison table."""
        df = self.compare_results()

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
    print("SUPERTREND FILTER BACKTEST ANALYSIS")
    print("="*120 + "\n")

    backtester = FilterBacktester()

    # 1. Baseline (No filters)
    print("1️⃣  Running Baseline (No Filters)...")
    backtester.run_backtest("Baseline", {})

    # 2. Market Filters
    print("\n2️⃣  Market Filters...")

    # MA Filter - Price above 200MA
    print("   a) MA200 Filter (Price > 200MA)...")
    backtester.run_backtest("MA200 Filter (Price > 200MA)", {
        "ma_filter": "200gt"
    })

    # MA Filter - Price above 60MA
    print("   b) MA60 Filter (Price > 60MA)...")
    backtester.run_backtest("MA60 Filter (Price > 60MA)", {
        "ma_filter": "60gt"
    })

    # 3. Volatility Filters
    print("\n3️⃣  Volatility Filters...")

    # Low Volatility Filter (exclude)
    print("   a) Low Volatility Filter (exclude low vol)...")
    backtester.run_backtest("Low Volatility Filter (exclude)", {
        "volatility_filter_enabled": True,
        "volatility_period": 20,
        "min_volatility": 0.01,
        "max_volatility": 0.08,
        "volatility_mode": "exclude"
    })

    # High Volatility Filter (exclude)
    print("   b) High Volatility Filter (exclude high vol)...")
    backtester.run_backtest("High Volatility Filter (exclude)", {
        "volatility_filter_enabled": True,
        "volatility_period": 20,
        "min_volatility": 0.02,
        "max_volatility": 0.04,
        "volatility_mode": "exclude"
    })

    # 4. Position Size Filters
    print("\n4️⃣  Position Size Filters...")

    # Max Positions = 5
    print("   a) Max 5 Positions...")
    backtester.run_backtest("Max 5 Positions", {
        "max_positions": 5
    })

    # Max Positions = 3
    print("   b) Max 3 Positions...")
    backtester.run_backtest("Max 3 Positions", {
        "max_positions": 3
    })

    # Position Size = 5% (more conservative)
    print("   c) Position Size 5% (more conservative)...")
    backtester.run_backtest("Position Size 5%", {
        "position_size_pct": 0.05
    })

    # 5. Combined Filters
    print("\n5️⃣  Combined Filters...")

    # MA200 + Max 5 Positions
    print("   a) MA200 Filter + Max 5 Positions...")
    backtester.run_backtest("MA200 + Max 5 Positions", {
        "ma_filter": "200gt",
        "max_positions": 5
    })

    # MA60 + Max 5 Positions
    print("   b) MA60 Filter + Max 5 Positions...")
    backtester.run_backtest("MA60 + Max 5 Positions", {
        "ma_filter": "60gt",
        "max_positions": 5
    })

    # MA60 + Low Vol Filter + Max 5 Positions
    print("   c) MA60 + Low Vol Filter + Max 5 Positions...")
    backtester.run_backtest("MA60 + Low Vol + Max 5", {
        "ma_filter": "60gt",
        "volatility_filter_enabled": True,
        "volatility_period": 20,
        "min_volatility": 0.01,
        "max_volatility": 0.08,
        "volatility_mode": "exclude",
        "max_positions": 5
    })

    # Print comparison
    backtester.print_comparison()

    # Save results
    df = backtester.compare_results()
    output_path = "/Users/charlie/.openclaw/workspace/economy/supertrend_filter_backtest_results.csv"
    df.to_csv(output_path, index=False)
    print(f"✅ Results saved to: {output_path}")

    # Save JSON summary
    summary = {
        "test_date": datetime.now().isoformat(),
        "strategy_id": "supertrend_7b9f5ebf",
        "baseline": df[df['filter_name'] == 'Baseline'].to_dict('records')[0],
        "all_results": df.to_dict('records'),
        "best_return": df.loc[df['total_return'].idxmax()].to_dict(),
        "best_sharpe": df.loc[df['sharpe'].idxmax()].to_dict(),
        "lowest_drawdown": df.loc[df['max_drawdown'].idxmin()].to_dict()
    }

    json_path = "/Users/charlie/.openclaw/workspace/economy/supertrend_filter_backtest_summary.json"
    with open(json_path, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"✅ Summary saved to: {json_path}")


if __name__ == "__main__":
    main()
