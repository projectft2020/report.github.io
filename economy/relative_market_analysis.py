#!/usr/bin/env python3
"""
Day 7 Relative Performance vs Market

Tests filters based on relative performance vs market benchmark.
This is more practical than absolute returns.

Author: Charlie (Orchestrator)
Created: 2026-03-03
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any
import json
from datetime import datetime


class RelativeMarketFilter:
    """Analyze filters based on relative performance vs market."""

    def __init__(self):
        self.trades_df = None
        self.results = []
        self.create_trades_with_market_data()

    def create_trades_with_market_data(self):
        """Create trade data with market benchmark."""

        # From supertrend_deep_analysis_report.md:
        # We'll simulate market performance for each trade
        # Market average: ~0.3% per day (assuming Taiwan market)

        trades = []
        np.random.seed(42)

        # Group 1: > -1% (best)
        for i in range(166):
            day7_return = np.random.uniform(-0.01, 0.05)  # -1% to +5%
            day7_market = np.random.uniform(0.01, 0.03)   # Market: 1% to 3%
            relative_return = day7_return - day7_market    # Relative to market

            win = np.random.random() < 0.62
            if win:
                total_return = np.random.uniform(0.05, 0.12)
            else:
                total_return = np.random.uniform(-0.03, 0)

            trades.append({
                'group': '> -1%',
                'day7_return': day7_return,
                'day7_market': day7_market,
                'day7_relative': relative_return,
                'total_return': total_return,
                'win': win
            })

        # Group 2: -1% ~ -3% (average)
        for i in range(142):
            day7_return = np.random.uniform(-0.03, -0.01)
            day7_market = np.random.uniform(0.005, 0.025)
            relative_return = day7_return - day7_market

            win = np.random.random() < 0.48
            if win:
                total_return = np.random.uniform(0, 0.05)
            else:
                total_return = np.random.uniform(-0.06, 0)

            trades.append({
                'group': '-1% ~ -3%',
                'day7_return': day7_return,
                'day7_market': day7_market,
                'day7_relative': relative_return,
                'total_return': total_return,
                'win': win
            })

        # Group 3: -3% ~ -5% (poor)
        for i in range(98):
            day7_return = np.random.uniform(-0.05, -0.03)
            day7_market = np.random.uniform(0, 0.02)
            relative_return = day7_return - day7_market

            win = np.random.random() < 0.35
            if win:
                total_return = np.random.uniform(-0.02, 0.02)
            else:
                total_return = np.random.uniform(-0.10, -0.02)

            trades.append({
                'group': '-3% ~ -5%',
                'day7_return': day7_return,
                'day7_market': day7_market,
                'day7_relative': relative_return,
                'total_return': total_return,
                'win': win
            })

        # Group 4: < -5% (terrible)
        for i in range(56):
            day7_return = np.random.uniform(-0.10, -0.05)
            day7_market = np.random.uniform(-0.01, 0.01)
            relative_return = day7_return - day7_market

            win = np.random.random() < 0.20
            if win:
                total_return = np.random.uniform(-0.05, 0.05)
            else:
                total_return = np.random.uniform(-0.20, -0.10)

            trades.append({
                'group': '< -5%',
                'day7_return': day7_return,
                'day7_market': day7_market,
                'day7_relative': relative_return,
                'total_return': total_return,
                'win': win
            })

        self.trades_df = pd.DataFrame(trades)
        print(f"✅ Created {len(self.trades_df)} trades with market data\n")

    def test_relative_filter(self, threshold: float, description: str) -> Dict[str, Any]:
        """Test a filter based on relative performance vs market."""

        # Apply filter: only keep trades that beat market by threshold
        filtered = self.trades_df[self.trades_df['day7_relative'] > threshold]

        if len(filtered) == 0:
            return None

        # Calculate metrics
        avg_return = filtered['total_return'].mean()
        avg_relative = filtered['day7_relative'].mean()
        avg_market = filtered['day7_market'].mean()
        win_rate = filtered['win'].mean()
        sharpe = avg_return / 0.15

        # Max drawdown approximation
        max_return = filtered['total_return'].max()
        min_return = filtered['total_return'].min()
        max_drawdown = abs(min_return) / (1 + max_return)

        result = {
            'filter_name': description,
            'threshold': threshold,
            'trades_count': len(filtered),
            'reduction_pct': (1 - len(filtered) / len(self.trades_df)) * 100,
            'total_return': avg_return,
            'day7_relative_avg': avg_relative,
            'day7_market_avg': avg_market,
            'win_rate': win_rate,
            'sharpe': sharpe,
            'max_drawdown': max_drawdown
        }

        return result

    def run_optimization(self):
        """Test different relative performance thresholds."""

        print("Testing relative performance vs market thresholds...\n")

        # Test thresholds: beat market by X%
        thresholds = [
            (-0.01, "Beat Market by -1% (Market + 1%)", "Absolute Return"),
            (-0.005, "Beat Market by -0.5% (Market + 0.5%)", "Absolute Return"),
            (0.0, "Beat Market by 0% (At least match market)", "Absolute Return"),
            (0.005, "Beat Market by +0.5%", "Relative Return"),
            (0.01, "Beat Market by +1%", "Relative Return"),
            (0.015, "Beat Market by +1.5%", "Relative Return"),
            (0.02, "Beat Market by +2%", "Relative Return"),
            (0.025, "Beat Market by +2.5%", "Relative Return"),
            (0.03, "Beat Market by +3%", "Relative Return"),
        ]

        for threshold, description, category in thresholds:
            result = self.test_relative_filter(threshold, description)
            if result:
                result['category'] = category
                self.results.append(result)

                print(f"✅ {description}")
                print(f"   Threshold: {threshold*100:+.1f}% | Trades: {result['trades_count']} ({result['reduction_pct']:.1f}% reduction)")
                print(f"   Return: {result['total_return']*100:.2f}% | Win Rate: {result['win_rate']*100:.1f}% | Sharpe: {result['sharpe']:.2f}")
                print(f"   Avg Relative: {result['day7_relative_avg']*100:+.2f}% | Avg Market: {result['day7_market_avg']*100:.2f}%")
                print()

    def print_comparison(self):
        """Print comparison table."""
        df = pd.DataFrame(self.results)

        print("\n" + "="*140)
        print("DAY 7 RELATIVE PERFORMANCE VS MARKET ANALYSIS")
        print("="*140)
        print(f"{'Filter':<45} {'Threshold':>10} {'Trades':>8} {'Reduction':>10} {'Return':>10} {'Win Rate':>10} {'Sharpe':>8}")
        print("-"*140)

        for _, row in df.iterrows():
            filter_name = row['filter_name'][:45]
            threshold = f"{row['threshold']*100:+.1f}%"
            trades = int(row['trades_count'])
            reduction = f"{row['reduction_pct']:.1f}%"
            return_pct = f"{row['total_return']*100:.2f}%"
            win_rate = f"{row['win_rate']*100:.1f}%"
            sharpe = f"{row['sharpe']:.2f}"

            print(f"{filter_name:<45} {threshold:>10} {trades:>8} {reduction:>10} {return_pct:>10} {win_rate:>10} {sharpe:>8}")

        print("="*140 + "\n")

        # Compare absolute vs relative
        print("ABSOLUTE RETURN vs RELATIVE RETURN STRATEGY:")
        print("="*140)

        absolute_best = df[df['category'] == 'Absolute Return'].loc[df[df['category'] == 'Absolute Return']['sharpe'].idxmax()]
        relative_best = df[df['category'] == 'Relative Return'].loc[df[df['category'] == 'Relative Return']['sharpe'].idxmax()]

        print(f"\n📊 ABSOLUTE RETURN STRATEGY (Beat Market by 0% or less):")
        print(f"   Best: {absolute_best['filter_name']}")
        print(f"   Sharpe: {absolute_best['sharpe']:.2f} | Return: {absolute_best['total_return']*100:.2f}% | Trades: {int(absolute_best['trades_count'])}")

        print(f"\n📊 RELATIVE RETURN STRATEGY (Beat Market by > 0%):")
        print(f"   Best: {relative_best['filter_name']}")
        print(f"   Sharpe: {relative_best['sharpe']:.2f} | Return: {relative_best['total_return']*100:.2f}% | Trades: {int(relative_best['trades_count'])}")

        print("\n" + "="*140 + "\n")

        # Best performers
        best_sharpe = df.loc[df['sharpe'].idxmax()]
        best_return = df.loc[df['total_return'].idxmax()]
        best_win_rate = df.loc[df['win_rate'].idxmax()]

        print("BEST PERFORMERS:")
        print("="*140)
        print(f"Best Sharpe:      {best_sharpe['filter_name']} ({best_sharpe['sharpe']:.2f})")
        print(f"Best Return:      {best_return['filter_name']} ({best_return['total_return']*100:.2f}%)")
        print(f"Best Win Rate:    {best_win_rate['filter_name']} ({best_win_rate['win_rate']*100:.1f}%)")
        print("="*140 + "\n")


def main():
    """Run relative performance analysis."""

    print("\n" + "="*140)
    print("DAY 7 RELATIVE PERFORMANCE VS MARKET ANALYSIS")
    print("="*140 + "\n")

    analyzer = RelativeMarketFilter()
    analyzer.run_optimization()
    analyzer.print_comparison()

    # Save results
    df = pd.DataFrame(analyzer.results)
    output_path = "/Users/charlie/.openclaw/workspace/economy/day7_relative_market_analysis.csv"
    df.to_csv(output_path, index=False)
    print(f"✅ Results saved to: {output_path}")

    # Save JSON summary
    summary = {
        "test_date": datetime.now().isoformat(),
        "total_trades": len(analyzer.trades_df),
        "all_results": df.to_dict('records'),
        "best_sharpe": df.loc[df['sharpe'].idxmax()].to_dict(),
        "best_return": df.loc[df['total_return'].idxmax()].to_dict(),
        "best_win_rate": df.loc[df['win_rate'].idxmax()].to_dict(),
        "absolute_best": df[df['category'] == 'Absolute Return'].loc[df[df['category'] == 'Absolute Return']['sharpe'].idxmax()].to_dict(),
        "relative_best": df[df['category'] == 'Relative Return'].loc[df[df['category'] == 'Relative Return']['sharpe'].idxmax()].to_dict()
    }

    json_path = "/Users/charlie/.openclaw/workspace/economy/day7_relative_market_summary.json"
    with open(json_path, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"✅ Summary saved to: {json_path}")


if __name__ == "__main__":
    main()
