#!/usr/bin/env python3
"""
Market Score + 雙市場 MA 組合策略 v2

修正版策略邏輯：

1. **主要進場條件（任一滿足即可）：**
   - Market Score > 50（多頭市場）
   - OR (0050 > 120MA AND QQQ > 20MA)（雙市場趨勢確認）

2. **出場條件（空頭市場保護）：**
   - Market Score < 40（空頭市場嚴重）
   - OR (0050 < 120MA AND QQQ < 20MA)（雙市場趨勢轉弱）

3. **減倉條件（中等風險）：**
   - Market Score 在 40-50 之間時，持倉減半
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


def analyze_market_score_strategy_v2(
    qqq_df: pd.DataFrame,
    tw0050_df: pd.DataFrame,
    market_score_df: pd.DataFrame,
    initial_capital: float = 100000,
    position_size_full: float = 0.5,
    position_size_half: float = 0.25
) -> Dict:
    """
    分析 Market Score + 雙市場 MA 組合策略 v2

    Returns:
        Dict: 包含績效指標和詳細數據
    """

    # 對齊所有數據的日期範圍
    start_date = max(qqq_df.index.min(), tw0050_df.index.min())
    end_date = min(qqq_df.index.max(), tw0050_df.index.max())

    # 限制在 2019-01-01 之後的數據
    start_date = max(start_date, pd.Timestamp("2019-01-01"))

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

    # Market Score 條件
    results['ms_bullish'] = results['market_score'] > 50
    results['ms_bearish'] = results['market_score'] < 40
    results['ms_neutral'] = (results['market_score'] >= 40) & (results['market_score'] <= 50)

    # v2 策略邏輯：
    # 1. 主要進場條件：Market Score > 50 OR (0050 > 120MA AND QQQ > 20MA)
    # 2. 出場條件：Market Score < 40 OR (0050 < 120MA AND QQQ < 20MA)
    # 3. 減倉條件：Market Score 在 40-50 之間

    # 進場訊號
    results['entry_signal'] = (
        results['ms_bullish'].fillna(False) |  # 如果沒有 MS 數據，不看 MS 條件
        (results['tw0050_above_120ma'] & results['qqq_above_20ma'])
    )

    # 出場訊號（空頭保護）
    results['exit_signal'] = (
        results['ms_bearish'].fillna(False) |
        (~results['tw0050_above_120ma'] & ~results['qqq_above_20ma'])
    )

    # 模擬交易
    cash = initial_capital
    holdings_qqq = 0
    holdings_tw0050 = 0

    results['position_size'] = 0.0  # 0 = 空倉, 0.5 = 半倉, 1.0 = 全倉
    results['portfolio_value'] = float(initial_capital)
    results['cash'] = float(cash)
    results['qqq_value'] = 0.0
    results['tw0050_value'] = 0.0

    for date, row in results.iterrows():
        if pd.isna(row['qqq_close']) or pd.isna(row['tw0050_close']):
            continue

        # 判斷當前應該持倉多少
        ms_bullish = row['ms_bullish'] if pd.notna(row['ms_bullish']) else False
        ms_neutral = row['ms_neutral'] if pd.notna(row['ms_neutral']) else False

        if ms_bullish:
            # 多頭市場：全倉
            target_position_size = position_size_full * 2  # 50% QQQ + 50% 0050
        elif ms_neutral:
            # 中性市場：半倉
            target_position_size = position_size_half * 2  # 25% QQQ + 25% 0050
        elif row['entry_signal']:
            # 趨勢確認：全倉
            target_position_size = position_size_full * 2
        else:
            # 空頭市場或趨勢轉弱：空倉
            target_position_size = 0

        # 計算當前持倉價值
        qqq_value = holdings_qqq * row['qqq_close']
        tw0050_value = holdings_tw0050 * row['tw0050_close']
        current_position_value = qqq_value + tw0050_value
        current_position_size = current_position_value / (cash + current_position_value) if (cash + current_position_value) > 0 else 0

        # 調整倉位
        target_value = (cash + current_position_value) * target_position_size
        current_value = current_position_value

        if abs(target_value - current_value) > 100:  # 避免微小調整
            # 需要調整
            if target_value > current_value:
                # 增加倉位
                additional_cash = target_value - current_value
                if cash >= additional_cash:
                    qqq_buy = additional_cash * 0.5 / row['qqq_close']
                    tw0050_buy = additional_cash * 0.5 / row['tw0050_close']
                    holdings_qqq += qqq_buy
                    holdings_tw0050 += tw0050_buy
                    cash -= additional_cash
            else:
                # 減少倉位
                reduce_amount = current_value - target_value
                qqq_sell = reduce_amount * (qqq_value / current_value) / row['qqq_close']
                tw0050_sell = reduce_amount * (tw0050_value / current_value) / row['tw0050_close']
                holdings_qqq -= qqq_sell
                holdings_tw0050 -= tw0050_sell
                cash += reduce_amount

        # 計算當天持倉價值
        qqq_value = holdings_qqq * row['qqq_close']
        tw0050_value = holdings_tw0050 * row['tw0050_close']
        portfolio_value = cash + qqq_value + tw0050_value

        results.loc[date, 'position_size'] = target_position_size
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

    # 勝率
    win_rate = (returns > 0).sum() / len(returns) if len(returns) > 0 else 0

    # 平均倉位
    avg_position_size = results['position_size'].mean()

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
            'avg_position_size': avg_position_size,
            'total_days': len(results),
            'days_full_position': int((results['position_size'] >= 0.9).sum()),
            'days_half_position': int(((results['position_size'] >= 0.4) & (results['position_size'] < 0.9)).sum()),
            'days_no_position': int((results['position_size'] < 0.4).sum()),
            'market_score_coverage': results['market_score'].notna().sum() / len(results)
        }
    }


def print_analysis_report(analysis: Dict, strategy_name: str = "Market Score + 雙市場 MA 策略 v2"):
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

    print("📊 倉位統計")
    print("-" * 80)
    print(f"平均倉位:        {metrics['avg_position_size']:.1%}")
    days_full = metrics['days_full_position']
    days_half = metrics['days_half_position']
    days_no = metrics['days_no_position']
    total_days = metrics['total_days']
    print(f"全倉天數:        {days_full} ({days_full/total_days:.1%})")
    print(f"半倉天數:        {days_half} ({days_half/total_days:.1%})")
    print(f"空倉天數:        {days_no} ({days_no/total_days:.1%})")
    print(f"Market Score 覆蓋率: {metrics['market_score_coverage']:.1%}")
    print()

    print("💡 關鍵洞察")
    print("-" * 80)
    if metrics['excess_return'] > 0:
        print(f"✅ 策略跑贏 Buy & Hold {metrics['excess_return']:.2%}")
    else:
        print(f"❌ 策略落後 Buy & Hold {abs(metrics['excess_return']):.2%}")

    if metrics['max_drawdown'] > -0.15:
        print(f"✅ 最大回撤控制在 {abs(metrics['max_drawdown']):.1%} 以內")
    else:
        print(f"⚠️  最大回撤較大: {abs(metrics['max_drawdown']):.1%}")

    if metrics['sharpe_ratio'] > 1:
        print(f"✅ 夏普比率優秀: {metrics['sharpe_ratio']:.2f}")
    elif metrics['sharpe_ratio'] > 0.5:
        print(f"⚠️  夏普比率中等: {metrics['sharpe_ratio']:.2f}")
    else:
        print(f"❌ 夏普比率偏低: {metrics['sharpe_ratio']:.2f}")

    # 回撤對比
    buy_hold_dd = (results['buy_hold_value'] - results['buy_hold_value'].cummax()) / results['buy_hold_value'].cummax()
    strategy_dd = results['drawdown']
    print(f"📉 回撤對比: 策略 {abs(strategy_dd.min()):.1%} vs Buy & Hold {abs(buy_hold_dd.min()):.1%}")

    if abs(strategy_dd.min()) < abs(buy_hold_dd.min()):
        print(f"✅ 策略回撤比 Buy & Hold 少 {abs(buy_hold_dd.min()) - abs(strategy_dd.min()):.1%}")

    print()
    print("=" * 80)


def main():
    """主函數"""
    print("🚀 開始分析 Market Score + 雙市場 MA 組合策略 v2")
    print()

    # 獲取價格數據
    print("📥 獲取價格數據...")
    qqq_df = get_stock_price("QQQ", "US", days=3000)
    tw0050_df = get_stock_price("0050", "TW", days=3000)
    market_score_df = get_market_score("TW", "2019-01-01", "2026-02-21")

    print(f"   QQQ 數據: {len(qqq_df)} 天 ({qqq_df.index[0].date()} 到 {qqq_df.index[-1].date()})")
    print(f"   0050.TW 數據: {len(tw0050_df)} 天 ({tw0050_df.index[0].date()} 到 {tw0050_df.index[-1].date()})")

    if market_score_df.empty:
        print("   ⚠️  Market Score 數據不可用")
    else:
        print(f"   Market Score 數據: {len(market_score_df)} 天 ({market_score_df.index[0].date()} 到 {market_score_df.index[-1].date()})")
    print()

    # 執行分析
    print("📊 執行策略分析...")
    analysis = analyze_market_score_strategy_v2(qqq_df, tw0050_df, market_score_df)
    print()

    # 打印報告
    print_analysis_report(analysis)

    # 保存結果到 CSV
    output_path = "/Users/charlie/.openclaw/workspace/market_score_strategy_v2_results.csv"
    analysis['results'].to_csv(output_path)
    print(f"📁 詳細結果已保存至: {output_path}")

    return analysis


if __name__ == "__main__":
    main()
