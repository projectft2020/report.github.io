#!/usr/bin/env python3
"""
分析 Supertrend 策略的最佳進場時機
- 分析大盤條件下的策略表現
- 找出風險最低、報酬最高的進場時機點
"""

import json
import pandas as pd
from datetime import datetime
from collections import defaultdict

# 載入 Supertrend 回測結果
with open('/Users/charlie/.openclaw/workspace/kanban/outputs/supertrend_deep_analysis_report.md', 'r') as f:
    report = f.read()

# 解析交易數據
def parse_trades_from_report(report):
    """從報告中解析交易數據"""
    trades = []

    # 尋找 "All Transactions" 部分
    lines = report.split('\n')
    in_transactions = False
    transactions_start = None

    for i, line in enumerate(lines):
        if '## 9. All Transactions' in line or 'All Transactions' in line and '##' in lines[i-1]:
            in_transactions = True
            continue

        if in_transactions:
            if line.startswith('##') and 'Transactions' not in line:
                break
            if 'Trade #' in line or line.startswith('1.') or '|' in line:
                continue

            # 解析交易行
            if line.strip() and '|' in line and 'Entry' not in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 6:
                    try:
                        # 嘗試解析各種格式
                        trade_num = parts[0] if parts[0].isdigit() else None
                        symbol = parts[1]
                        entry_date = parts[2]
                        exit_date = parts[3]
                        entry_price = float(parts[4].replace(',', '').replace('$', '')) if parts[4] else None
                        exit_price = float(parts[5].replace(',', '').replace('$', '')) if parts[5] else None
                        pnl = None
                        if len(parts) >= 7 and parts[6]:
                            pnl = float(parts[6].replace(',', '').replace('$', '').replace('+', '').replace('(', '').replace(')', ''))

                        if entry_price and exit_price:
                            trades.append({
                                'symbol': symbol,
                                'entry_date': entry_date,
                                'exit_date': exit_date,
                                'entry_price': entry_price,
                                'exit_price': exit_price,
                                'pnl': pnl
                            })
                    except (ValueError, IndexError):
                        pass

    return trades

# 載入並分析
trades = parse_trades_from_report(report)
print(f"解析到 {len(trades)} 筆交易")

if trades:
    # 轉換為 DataFrame
    df = pd.DataFrame(trades)

    # 轉換日期
    df['entry_date'] = pd.to_datetime(df['entry_date'])
    df['exit_date'] = pd.to_datetime(df['exit_date'])
    df['year'] = df['entry_date'].dt.year
    df['month'] = df['entry_date'].dt.month

    # 計算持倉天數
    df['holding_days'] = (df['exit_date'] - df['entry_date']).dt.days

    # 判斷交易結果
    df['is_profit'] = df['pnl'] > 0
    df['pnl_pct'] = (df['pnl'] / df['entry_price']) * 100

    print(f"\n交易統計：")
    print(f"總交易數：{len(df)}")
    print(f"盈利交易：{df['is_profit'].sum()} ({df['is_profit'].mean()*100:.1f}%)")
    print(f"平均 PnL：${df['pnl'].mean():,.0f}")
    print(f"平均持倉：{df['holding_days'].mean():.1f} 天")

    # 按年份分析
    print(f"\n{'='*60}")
    print("按年份分析")
    print(f"{'='*60}")

    yearly_stats = []
    for year in sorted(df['year'].unique()):
        year_df = df[df['year'] == year]
        stats = {
            'year': year,
            'trades': len(year_df),
            'win_rate': year_df['is_profit'].mean() * 100,
            'avg_pnl': year_df['pnl'].mean(),
            'total_pnl': year_df['pnl'].sum(),
            'max_profit': year_df['pnl'].max(),
            'max_loss': year_df['pnl'].min(),
            'avg_holding': year_df['holding_days'].mean()
        }
        yearly_stats.append(stats)

        print(f"\n{year} 年:")
        print(f"  交易數：{stats['trades']}")
        print(f"  勝率：{stats['win_rate']:.1f}%")
        print(f"  平均 PnL：${stats['avg_pnl']:,.0f}")
        print(f"  總 PnL：${stats['total_pnl']:,.0f}")
        print(f"  最大盈利：${stats['max_profit']:,.0f}")
        print(f"  最大虧損：${stats['max_loss']:,.0f}")
        print(f"  平均持倉：{stats['avg_holding']:.1f} 天")

    # 按月份分析
    print(f"\n{'='*60}")
    print("按月份分析（所有年份合計）")
    print(f"{'='*60}")

    monthly_stats = []
    for month in range(1, 13):
        month_df = df[df['month'] == month]
        if len(month_df) > 0:
            stats = {
                'month': month,
                'trades': len(month_df),
                'win_rate': month_df['is_profit'].mean() * 100,
                'avg_pnl': month_df['pnl'].mean(),
                'total_pnl': month_df['pnl'].sum(),
                'max_profit': month_df['pnl'].max(),
                'max_loss': month_df['pnl'].min()
            }
            monthly_stats.append(stats)

            print(f"\n{month} 月:")
            print(f"  交易數：{stats['trades']}")
            print(f"  勝率：{stats['win_rate']:.1f}%")
            print(f"  平均 PnL：${stats['avg_pnl']:,.0f}")
            print(f"  總 PnL：${stats['total_pnl']:,.0f}")

    # 找出最佳和最差的年份/月份
    print(f"\n{'='*60}")
    print("最佳/最差時機分析")
    print(f"{'='*60}")

    best_year = max(yearly_stats, key=lambda x: x['total_pnl'])
    worst_year = min(yearly_stats, key=lambda x: x['total_pnl'])

    print(f"\n最佳年份：{best_year['year']} 年")
    print(f"  總 PnL：${best_year['total_pnl']:,.0f}")
    print(f"  勝率：{best_year['win_rate']:.1f}%")
    print(f"  交易數：{best_year['trades']}")

    print(f"\n最差年份：{worst_year['year']} 年")
    print(f"  總 PnL：${worst_year['total_pnl']:,.0f}")
    print(f"  勝率：{worst_year['win_rate']:.1f}%")
    print(f"  交易數：{worst_year['trades']}")

    if monthly_stats:
        best_month = max(monthly_stats, key=lambda x: x['total_pnl'])
        worst_month = min(monthly_stats, key=lambda x: x['total_pnl'])

        print(f"\n最佳月份：{best_month['month']} 月")
        print(f"  總 PnL：${best_month['total_pnl']:,.0f}")
        print(f"  勝率：{best_month['win_rate']:.1f}%")
        print(f"  交易數：{best_month['trades']}")

        print(f"\n最差月份：{worst_month['month']} 月")
        print(f"  總 PnL：${worst_month['total_pnl']:,.0f}")
        print(f"  勝率：{worst_month['win_rate']:.1f}%")
        print(f"  交易數：{worst_month['trades']}")

    # 持倉天數分析
    print(f"\n{'='*60}")
    print("持倉天數分析")
    print(f"{'='*60}")

    holding_bins = [0, 14, 30, 60, 90, 180, 365]
    holding_labels = ['<14天', '14-30天', '30-60天', '60-90天', '90-180天', '180-365天']

    df['holding_range'] = pd.cut(df['holding_days'], bins=holding_bins, labels=holding_labels)

    for label in holding_labels:
        range_df = df[df['holding_range'] == label]
        if len(range_df) > 0:
            print(f"\n{label}:")
            print(f"  交易數：{len(range_df)}")
            print(f"  勝率：{range_df['is_profit'].mean()*100:.1f}%")
            print(f"  平均 PnL：${range_df['pnl'].mean():,.0f}")
            print(f"  總 PnL：${range_df['pnl'].sum():,.0f}")

    # 保存分析結果
    results = {
        'yearly_stats': yearly_stats,
        'monthly_stats': monthly_stats,
        'best_year': best_year,
        'worst_year': worst_year,
        'best_month': best_month if monthly_stats else None,
        'worst_month': worst_month if monthly_stats else None,
        'analysis_date': datetime.now().isoformat()
    }

    with open('/Users/charlie/.openclaw/workspace/economy/supertrend_timing_analysis.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n{'='*60}")
    print("分析結果已保存到 economy/supertrend_timing_analysis.json")
    print(f"{'='*60}")

else:
    print("無法解析交易數據，請檢查報告格式")
