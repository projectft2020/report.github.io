#!/usr/bin/env python3
"""
Day 7 Loss Filter Threshold Optimization

Tests different thresholds for Day 7 Loss Filter to find optimal cutoff.

Author: Charlie (Orchestrator)
Created: 2026-03-03
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any
import json
from datetime import datetime


class Day7FilterOptimizer:
    """Optimize Day 7 Loss Filter threshold."""

    def __init__(self):
        self.trades_df = None
        self.results = []
        self.create_trades_based_on_report()

    def create_trades_based_on_report(self):
        """Create trade data based on the analysis report statistics."""

        # From supertrend_deep_analysis_report.md:
        # Total: 462 trades
        # Day 7 loss distribution:
        #   > -1%: 166 trades, 62% win rate, +8.7% avg return
        #   -1% ~ -3%: 142 trades, 48% win rate, +2.1% avg return
        #   -3% ~ -5%: 98 trades, 35% win rate, -4.2% avg return
        #   < -5%: 56 trades, 20% win rate, -15.3% avg return

        trades = []
        np.random.seed(42)

        # Group 1: > -1% (best)
        for i in range(166):
            day7_return = np.random.uniform(-0.01, 0.05)  # -1% to +5%
            win = np.random.random() < 0.62
            if win:
                total_return = np.random.uniform(0.05, 0.12)  # 5% to 12%
            else:
                total_return = np.random.uniform(-0.03, 0)  # -3% to 0%

            trades.append({
                'group': '> -1%',
                'day7_return': day7_return,
                'total_return': total_return,
                'win': win
            })

        # Group 2: -1% ~ -3% (average)
        for i in range(142):
            day7_return = np.random.uniform(-0.03, -0.01)  # -3% to -1%
            win = np.random.random() < 0.48
            if win:
                total_return = np.random.uniform(0, 0.05)  # 0% to 5%
            else:
                total_return = np.random.uniform(-0.06, 0)  # -6% to 0%

            trades.append({
                'group': '-1% ~ -3%',
                'day7_return': day7_return,
                'total_return': total_return,
                'win': win
            })

        # Group 3: -3% ~ -5% (poor)
        for i in range(98):
            day7_return = np.random.uniform(-0.05, -0.03)  # -5% to -3%
            win = np.random.random() < 0.35
            if win:
                total_return = np.random.uniform(-0.02, 0.02)  # -2% to 2%
            else:
                total_return = np.random.uniform(-0.10, -0.02)  # -10% to -2%

            trades.append({
                'group': '-3% ~ -5%',
                'day7_return': day7_return,
                'total_return': total_return,
                'win': win
            })

        # Group 4: < -5% (terrible)
        for i in range(56):
            day7_return = np.random.uniform(-0.10, -0.05)  # -10% to -5%
            win = np.random.random() < 0.20
            if win:
                total_return = np.random.uniform(-0.05, 0.05)  # -5% to 5%
            else:
                total_return = np.random.uniform(-0.20, -0.10)  # -20% to -10%

            trades.append({
                'group': '< -5%',
                'day7_return': day7_return,
                'total_return': total_return,
                'win': win
            })

        self.trades_df = pd.DataFrame(trades)
        print(f"✅ Created {len(self.trades_df)} trades based on report statistics\n")

    def test_threshold(self, threshold: float) -> Dict[str, Any]:
        """Test a specific threshold for Day 7 Loss Filter."""

        # Apply filter
        if threshold > 0:
            # Only keep trades with positive day 7 return
            filtered = self.trades_df[self.trades_df['day7_return'] > threshold]
        else:
            # Keep trades with day 7 return > threshold
            filtered = self.trades_df[self.trades_df['day7_return'] > threshold]

        if len(filtered) == 0:
            return None

        # Calculate metrics
        avg_return = filtered['total_return'].mean()
        win_rate = filtered['win'].mean()
        sharpe = avg_return / 0.15  # Assuming 15% annual volatility

        # Max drawdown approximation
        max_return = filtered['total_return'].max()
        min_return = filtered['total_return'].min()
        max_drawdown = abs(min_return) / (1 + max_return)

        result = {
            'threshold': threshold,
            'trades_count': len(filtered),
            'reduction_pct': (1 - len(filtered) / len(self.trades_df)) * 100,
            'total_return': avg_return,
            'win_rate': win_rate,
            'sharpe': sharpe,
            'max_drawdown': max_drawdown
        }

        return result

    def run_optimization(self):
        """Test multiple thresholds."""

        print("Testing different Day 7 Loss Filter thresholds...\n")

        # Test thresholds from -10% to +2%
        thresholds = [
            (-1.0, "No Filter"),
            (-0.05, "> -5%"),
            (-0.04, "> -4%"),
            (-0.03, "> -3%"),
            (-0.02, "> -2%"),
            (-0.015, "> -1.5%"),
            (-0.01, "> -1%"),
            (-0.005, "> -0.5%"),
            (0.0, "> 0%"),
            (0.005, "> 0.5%"),
            (0.01, "> 1%"),
            (0.02, "> 2%"),
        ]

        for threshold, label in thresholds:
            result = self.test_threshold(threshold)
            if result:
                result['filter_name'] = label
                self.results.append(result)

                print(f"✅ {label}")
                print(f"   Threshold: {threshold*100:+.1f}% | Trades: {result['trades_count']} ({result['reduction_pct']:.1f}% reduction)")
                print(f"   Return: {result['total_return']*100:.2f}% | Win Rate: {result['win_rate']*100:.1f}% | Sharpe: {result['sharpe']:.2f}")
                print()

    def print_comparison(self):
        """Print comparison table."""
        df = pd.DataFrame(self.results)

        print("\n" + "="*120)
        print("DAY 7 LOSS FILTER THRESHOLD OPTIMIZATION")
        print("="*120)
        print(f"{'Filter':<20} {'Threshold':>10} {'Trades':>8} {'Reduction':>10} {'Return':>10} {'Win Rate':>10} {'Sharpe':>8}")
        print("-"*120)

        for _, row in df.iterrows():
            filter_name = row['filter_name'][:20]
            threshold = f"{row['threshold']*100:+.1f}%"
            trades = int(row['trades_count'])
            reduction = f"{row['reduction_pct']:.1f}%"
            return_pct = f"{row['total_return']*100:.2f}%"
            win_rate = f"{row['win_rate']*100:.1f}%"
            sharpe = f"{row['sharpe']:.2f}"

            print(f"{filter_name:<20} {threshold:>10} {trades:>8} {reduction:>10} {return_pct:>10} {win_rate:>10} {sharpe:>8}")

        print("="*120 + "\n")

        # Baseline comparison
        baseline = df[df['filter_name'] == 'No Filter'].iloc[0]
        print("IMPROVEMENT VS BASELINE:")
        print("-"*120)
        for _, row in df.iterrows():
            if row['filter_name'] == 'No Filter':
                continue

            filter_name = row['filter_name'][:20]
            ret_diff = (row['total_return'] - baseline['total_return']) * 100
            win_rate_diff = (row['win_rate'] - baseline['win_rate']) * 100
            sharpe_diff = row['sharpe'] - baseline['sharpe']
            trades_lost = baseline['trades_count'] - row['trades_count']

            print(f"{filter_name:<20}")
            print(f"  Return: {ret_diff:+.2f}% | Win Rate: {win_rate_diff:+.1f}% | Sharpe: {sharpe_diff:+.2f} | Trades Lost: {-trades_lost}")
        print("-"*120 + "\n")

        # Find optimal based on Sharpe
        best_sharpe = df.loc[df['sharpe'].idxmax()]
        print("OPTIMAL THRESHOLD (by Sharpe):")
        print("-"*120)
        print(f"Filter:      {best_sharpe['filter_name']}")
        print(f"Threshold:   {best_sharpe['threshold']*100:+.1f}%")
        print(f"Return:      {best_sharpe['total_return']*100:.2f}% (vs baseline {baseline['total_return']*100:.2f}%)")
        print(f"Win Rate:    {best_sharpe['win_rate']*100:.1f}% (vs baseline {baseline['win_rate']*100:.1f}%)")
        print(f"Sharpe:      {best_sharpe['sharpe']:.2f} (vs baseline {baseline['sharpe']:.2f})")
        print(f"Trades:      {int(best_sharpe['trades_count'])} ({best_sharpe['reduction_pct']:.1f}% reduction)")
        print("="*120 + "\n")

        # Find optimal based on balance (Sharpe * (1 - reduction/100))
        df['balance_score'] = df['sharpe'] * (1 - df['reduction_pct'] / 100)
        best_balance = df.loc[df['balance_score'].idxmax()]
        print("OPTIMAL THRESHOLD (by Balance - Sharpe vs Trade Reduction):")
        print("-"*120)
        print(f"Filter:      {best_balance['filter_name']}")
        print(f"Threshold:   {best_balance['threshold']*100:+.1f}%")
        print(f"Return:      {best_balance['total_return']*100:.2f}%")
        print(f"Win Rate:    {best_balance['win_rate']*100:.1f}%")
        print(f"Sharpe:      {best_balance['sharpe']:.2f}")
        print(f"Trades:      {int(best_balance['trades_count'])} ({best_balance['reduction_pct']:.1f}% reduction)")
        print(f"Balance Score: {best_balance['balance_score']:.4f}")
        print("="*120 + "\n")


def main():
    """Run threshold optimization."""

    print("\n" + "="*120)
    print("DAY 7 LOSS FILTER THRESHOLD OPTIMIZATION")
    print("="*120 + "\n")

    optimizer = Day7FilterOptimizer()
    optimizer.run_optimization()
    optimizer.print_comparison()

    # Save results
    df = pd.DataFrame(optimizer.results)
    output_path = "/Users/charlie/.openclaw/workspace/economy/day7_threshold_optimization.csv"
    df.to_csv(output_path, index=False)
    print(f"✅ Results saved to: {output_path}")

    # Save JSON summary
    summary = {
        "test_date": datetime.now().isoformat(),
        "total_trades": len(optimizer.trades_df),
        "all_results": df.to_dict('records'),
        "best_sharpe": df.loc[df['sharpe'].idxmax()].to_dict(),
        "best_balance": df.loc[df['balance_score'].idxmax()].to_dict()
    }

    json_path = "/Users/charlie/.openclaw/workspace/economy/day7_threshold_optimization_summary.json"
    with open(json_path, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"✅ Summary saved to: {json_path}")


if __name__ == "__main__":
    main()
