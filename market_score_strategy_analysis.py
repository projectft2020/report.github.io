#!/usr/bin/env python3
"""
Market Score + 雙市場 MA 組合策略分析

策略邏輯：
1. Market Score < 50 → 空頭市場，避開淨值縮水（減倉/空倉）
2. Market Score > 50 → 多頭市場，佔領獲利（進場）
3. 0050.TW 120MA → 台股趨勢指標
4. QQQ 20MA → 美股趨勢指標

進場條件：
- Market Score > 50（如果可用）
- AND (0050 > 120MA OR QQQ > 20MA)

出場條件：
- Market Score < 50（如果可用）
- OR (0050 < 120MA AND QQQ < 20MA)
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Tuple, Dict, List

# API 配置
API_BASE = "http://localhost:8001"


def get_stock_price(symbol: str, market: str = "US", days: int = 1500) -> pd.DataFrame:
    """獲取股票價格歷史數據"""
    url = f"{API_BASE}/api/stock/{symbol}?market={market}&days={days}"
    response = requests.get(url)
    data = response.json()

    if 'history' not in data:
        return pd.DataFrame()

    df = pd.DataFrame(data['history'])
    df['date'] = pd.to_datetime(df['trade_date'])
    df.set_index('date', inplace=True)
    df.sort_index(inplace=True)

    return df


def get_market_score(market: str = "TW", start_date: str = "2023-01-01", end_date: str = "2026-02-21") -> pd.DataFrame:
    """獲取 Market Score 歷史數據"""
    url = f"{API_BASE}/api/market/thermometer/score-history?market={market}&start_date={start_date}&end_date={end_date}"
    response = requests.get(url)
    data = response.json()

    if 'data' not in data:
        return pd.DataFrame()

    df = pd.DataFrame(data['data'])
    df['date'] = pd.to_datetime(df['date']).dt.tz_localize(None)
    df.set_index('date', inplace=True)
    df.sort_index(inplace=True)

    return df


def calculate_ma(df: pd.DataFrame, period: int) -> pd.Series:
    """計算移動平均線"""
    return df['close'].rolling(window=period).mean()


def analyze_market_score_strategy(
    qqq_df: pd.DataFrame,
    tw0050_df: pd.DataFrame,
    market_score_df: pd.DataFrame,
    initial_capital: float = 100000,
    position_size: float = 0.5
) -> Dict:
    """
    分析 Market Score + 雙市場 MA 組合策略

    Returns:
        Dict: 包含績效指標和詳細數據
    """

    # 對齊所有數據的日期範圍
    start_date = max(qqq_df.index.min(), tw0050_df.index.min())
    end_date = min(qqq_df.index.max(), tw0050_df.index.max())

    # 限制在 2023-01-01 之後的數據（因為 Market Score 從那時開始才有意義）
    start_date = max(start_date, pd.Timestamp("2023-01-01"))

    # 創建完整的日期範圍（只有交易日）
    all_dates = pd.date_range(start=start_date, end=end_date, freq='D')
    trading_dates = sorted(set(qqq_df.index) & set(tw0050_df.index))

    # 初始化結果 DataFrame
    results = pd.DataFrame(index=trading_dates)

    # 添加價格數據
    results['qqq_close'] = qqq_df['close']
    results['tw0050_close'] = tw0050_df['close']

    # 計算移動平均線
    results['qqq_20ma'] = calculate_ma(qqq_df, 20)
    results['tw0050_120ma'] = calculate_ma(tw0050_df, 120)

    # 添加 Market Score（向前填充，因為不是每天都有數據）
    if not market_score_df.empty:
        ms_aligned = market_score_df.reindex(results.index, method='ffill')
        results['market_score'] = ms_aligned['total_score']
    else:
        results['market_score'] = np.nan

    # 計算指標條件
    results['qqq_above_20ma'] = results['qqq_close'] > results['qqq_20ma']
    results['tw0050_above_120ma'] = results['tw0050_close'] > results['tw0050_120ma']
    results['market_score_bullish'] = results['market_score'] > 50

    # 組合進場/出場條件
    # 進場：Market Score > 50 AND (0050 > 120MA OR QQQ > 20MA)
    results['entry_signal'] = (
        results['market_score_bullish'].fillna(True) &  # 如果沒有 Market Score，假設為多頭
        (results['tw0050_above_120ma'] | results['qqq_above_20ma'])
    )

    # 出場：Market Score < 50 OR (0050 < 120MA AND QQQ < 20MA)
    results['exit_signal'] = (
        results['market_score_bullish'].fillna(True).apply(lambda x: not x) |
        (~results['tw0050_above_120ma'] & ~results['qqq_above_20ma'])
    )

    # 模擬交易
    # 使用 50/50 分配在 QQQ 和 0050.TW
    cash = initial_capital
    holdings_qqq = 0
    holdings_tw0050 = 0

    results['position'] = 0.0  # 0 = 空倉, 1 = 全倉
    results['portfolio_value'] = initial_capital
    results['cash'] = cash
    results['qqq_value'] = 0.0
    results['tw0050_value'] = 0.0

    prev_position = 0

    for date, row in results.iterrows():
        if pd.isna(row['qqq_close']) or pd.isna(row['tw0050_close']):
            continue

        # 判斷當前應該持倉還是空倉
        should_long = row['entry_signal']

        # 倉位變化
        if should_long and prev_position == 0:
            # 進場：買入 QQQ 和 0050.TW
            holdings_qqq = (cash * position_size) / row['qqq_close']
            holdings_tw0050 = (cash * position_size) / row['tw0050_close']
            cash = cash * (1 - position_size * 2)  # 剩餘現金
            prev_position = 1
        elif not should_long and prev_position == 1:
            # 出場：賣出所有持倉
            cash += holdings_qqq * row['qqq_close']
            cash += holdings_tw0050 * row['tw0050_close']
            holdings_qqq = 0
            holdings_tw0050 = 0
            prev_position = 0

        # 計算當天持倉價值
        qqq_value = holdings_qqq * row['qqq_close']
        tw0050_value = holdings_tw0050 * row['tw0050_close']
        portfolio_value = cash + qqq_value + tw0050_value

        results.loc[date, 'position'] = prev_position
        results.loc[date, 'cash'] = cash
        results.loc[date, 'qqq_value'] = qqq_value
        results.loc[date, 'tw0050_value'] = tw0050_value
        results.loc[date, 'portfolio_value'] = portfolio_value

    # 計算績效指標
    returns = results['portfolio_value'].pct_change().dropna()

    # Buy & Hold 基準（50% QQQ + 50% 0050.TW）
    initial_qqq_shares = (initial_capital * 0.5) / results['qqq_close'].iloc[0]
    initial_tw0050_shares = (initial_capital * 0.5) / results['tw0050_close'].iloc[0]

    results['buy_hold_qqq_value'] = initial_qqq_shares * results['qqq_close']
    results['buy_hold_tw0050_value'] = initial_tw0050_shares * results['tw0050_close']
    results['buy_hold_value'] = results['buy_hold_qqq_value'] + results['buy_hold_tw0050_value']

    # 計算回撤
    results['cummax'] = results['portfolio_value'].cummax()
    results['drawdown'] = (results['portfolio_value'] - results['cummax']) / results['cummax']

    final_value = results['portfolio_value'].iloc[-1]
    buy_hold_value = results['buy_hold_value'].iloc[-1]
    total_return = (final_value / initial_capital) - 1
    buy_hold_return = (buy_hold_value / initial_capital) - 1

    # 計算夏普比率（年化）
    trading_days_per_year = 252
    annual_return = returns.mean() * trading_days_per_year
    annual_std = returns.std() * np.sqrt(trading_days_per_year)
    sharpe_ratio = annual_return / annual_std if annual_std > 0 else 0

    # 最大回撤
    max_drawdown = results['drawdown'].min()

    # 勝率（計算正收益交易日比例）
    win_rate = (returns > 0).sum() / len(returns) if len(returns) > 0 else 0

    # 計算交易次數
    position_changes = results['position'].diff().abs().sum() / 2
    trades_count = int(position_changes)

    return {
        'results': results,
        'metrics': {
            'total_return': total_return,
            'buy_hold_return': buy_hold_return,
            'excess_return': total_return - buy_hold_return,
            'final_value': final_value,
            'buy_hold_value': buy_hold_value,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'trades_count': trades_count,
            'total_days': len(results),
            'days_in_market': (results['position'] > 0).sum(),
            'market_score_coverage': results['market_score'].notna().sum() / len(results)
        }
    }


def print_analysis_report(analysis: Dict, strategy_name: str = "Market Score + 雙市場 MA 策略"):
    """打印分析報告"""
    metrics = analysis['metrics']
    results = analysis['results']

    print("=" * 80)
    print(f"📊 {strategy_name}")
    print("=" * 80)
    print()

    print("📈 績效指標")
    print("-" * 80)
    print(f"總報酬率:        {metrics['total_return']:.2%}")
    print(f"Buy & Hold 報酬率: {metrics['buy_hold_return']:.2%}")
    print(f"超額報酬:        {metrics['excess_return']:.2%}")
    print()
    print(f"最終價值:        \${metrics['final_value']:,.2f}")
    print(f"Buy & Hold 價值:  \${metrics['buy_hold_value']:,.2f}")
    print()
    print(f"夏普比率:        {metrics['sharpe_ratio']:.2f}")
    print(f"最大回撤:        {metrics['max_drawdown']:.2%}")
    print(f"勝率:            {metrics['win_rate']:.2%}")
    print()

    print("📊 交易統計")
    print("-" * 80)
    print(f"交易次數:        {metrics['trades_count']}")
    print(f"總交易日數:      {metrics['total_days']}")
    print(f"在市天數:        {metrics['days_in_market']} ({metrics['days_in_market']/metrics['total_days']:.1%})")
    print(f"Market Score 覆蓋率: {metrics['market_score_coverage']:.1%}")
    print()

    print("💡 關鍵洞察")
    print("-" * 80)
    if metrics['excess_return'] > 0:
        print(f"✅ 策略跑贏 Buy & Hold {metrics['excess_return']:.2%}")
    else:
        print(f"❌ 策略落後 Buy & Hold {abs(metrics['excess_return']):.2%}")

    if metrics['max_drawdown'] > -0.2:
        print(f"✅ 最大回撤控制在 {abs(metrics['max_drawdown']):.1%} 以內")
    else:
        print(f"⚠️  最大回撤較大: {abs(metrics['max_drawdown']):.1%}")

    if metrics['sharpe_ratio'] > 1:
        print(f"✅ 夏普比率優秀: {metrics['sharpe_ratio']:.2f}")
    elif metrics['sharpe_ratio'] > 0.5:
        print(f"⚠️  夏普比率中等: {metrics['sharpe_ratio']:.2f}")
    else:
        print(f"❌ 夏普比率偏低: {metrics['sharpe_ratio']:.2f}")

    print()
    print("=" * 80)


def main():
    """主函數"""
    print("🚀 開始分析 Market Score + 雙市場 MA 組合策略")
    print()

    # 獲取價格數據
    print("📥 獲取價格數據...")
    qqq_df = get_stock_price("QQQ", "US", days=1500)
    tw0050_df = get_stock_price("0050", "TW", days=1500)
    market_score_df = get_market_score("TW", "2023-01-01", "2026-02-21")

    print(f"   QQQ 數據: {len(qqq_df)} 天 ({qqq_df.index[0].date()} 到 {qqq_df.index[-1].date()})")
    print(f"   0050.TW 數據: {len(tw0050_df)} 天 ({tw0050_df.index[0].date()} 到 {tw0050_df.index[-1].date()})")

    if market_score_df.empty:
        print("   ⚠️  Market Score 數據不可用")
    else:
        print(f"   Market Score 數據: {len(market_score_df)} 天 ({market_score_df.index[0].date()} 到 {market_score_df.index[-1].date()})")
    print()

    # 執行分析
    print("📊 執行策略分析...")
    analysis = analyze_market_score_strategy(qqq_df, tw0050_df, market_score_df)
    print()

    # 打印報告
    print_analysis_report(analysis)

    # 保存結果到 CSV
    output_path = "/Users/charlie/.openclaw/workspace/market_score_strategy_results.csv"
    analysis['results'].to_csv(output_path)
    print(f"📁 詳細結果已保存至: {output_path}")

    return analysis


if __name__ == "__main__":
    main()
