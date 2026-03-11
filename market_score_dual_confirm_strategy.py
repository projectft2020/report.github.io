"""
Market Score + 雙市場同時確認策略 v3
===============================

策略邏輯：
1. 進場條件（全倉）：
   - TW Market Score > 50 (多頭)
   - US Market Score > 50 (多頭)
   - 0050.TW > 120MA (趨勢向上)
   - QQQ > 20MA (趨勢向上)
   
2. 減倉條件（半倉）：
   - 市場處於中性狀態（40-50 之間）
   
3. 出場條件（空倉）：
   - TW Market Score < 40 (空頭) AND US Market Score < 40 (空頭)
   - OR (0050.TW < 120MA AND QQQ < 20MA)

這是一個更嚴格的策略，要求雙市場同時確認。
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class MarketScoreDualConfirmStrategy:
    def __init__(self, initial_cash=100000):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.position_size = 0.0  # 0.0-1.0，表示倉位大小
        
        # 策略參數
        self.long_threshold = 50  # Market Score > 50 為多頭
        self.short_threshold = 40  # Market Score < 40 為空頭
        self.neutral_min = 40
        self.neutral_max = 50
        
    def get_market_score(self, market, start_date, end_date):
        """獲取 Market Score 歷史數據"""
        try:
            response = requests.get(
                "http://localhost:8001/api/market/thermometer/score-history",
                params={
                    "market": market,
                    "start_date": start_date,
                    "end_date": end_date
                }
            )
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    df = pd.DataFrame(data['data'])
                    df['date'] = pd.to_datetime(df['date']).dt.tz_localize(None)
                    df = df.set_index('date')
                    return df
        except Exception as e:
            print(f"獲取 {market} Market Score 時發生錯誤: {e}")
        return pd.DataFrame()
    
    def get_stock_price(self, symbol, market, days=1500):
        """獲取股票價格歷史數據"""
        try:
            response = requests.get(
                f"http://localhost:8001/api/stocks/{symbol}/history",
                params={
                    "market": market,
                    "days": days
                }
            )
            if response.status_code == 200:
                df = pd.DataFrame(response.json())
                df['trade_date'] = pd.to_datetime(df['trade_date'])
                df = df.set_index('trade_date')
                return df
        except Exception as e:
            print(f"獲取 {symbol} 價格時發生錯誤: {e}")
        return pd.DataFrame()
    
    def calculate_position(self, row):
        """
        根據雙市場同時確認策略計算倉位
        
        Args:
            row: 包含以下欄位的 DataFrame row
                - tw_market_score: 台灣 Market Score
                - us_market_score: 美國 Market Score
                - tw0050_above_120ma: 台股是否在 120MA 之上
                - qqq_above_20ma: 美股是否在 20MA 之上
        """
        # 檢查 Market Score 是否為空
        tw_ms = row['tw_market_score']
        us_ms = row['us_market_score']
        
        # 檢查趨勢指標
        tw0050_above = row['tw0050_above_120ma']
        qqq_above = row['qqq_above_20ma']
        
        # 如果任何 Market Score 為空，使用趨勢指標
        if pd.isna(tw_ms) or pd.isna(us_ms):
            # 只有雙重趨勢確認才全倉
            if tw0050_above and qqq_above:
                return 1.0
            elif (tw0050_above == False) and (qqq_above == False):
                return 0.0
            else:
                return 0.5
        
        # Market Score 都為多頭且趨勢都向上 → 全倉
        if tw_ms > self.long_threshold and us_ms > self.long_threshold and tw0050_above and qqq_above:
            return 1.0
        
        # Market Score 都為空頭且趨勢都向下 → 空倉
        if tw_ms < self.short_threshold and us_ms < self.short_threshold and (tw0050_above == False) and (qqq_above == False):
            return 0.0
        
        # 其他情況 → 半倉
        return 0.5
    
    def backtest(self):
        """執行回測"""
        print("🚀 開始分析 Market Score + 雙市場同時確認策略 v3\n")
        
        # 獲取價格數據
        print("📥 獲取價格數據...")
        qqq_df = self.get_stock_price("QQQ", "US", days=3000)
        tw0050_df = self.get_stock_price("0050", "TW", days=3000)
        
        print(f"   QQQ 數據: {len(qqq_df)} 天 ({qqq_df.index.min().date()} 到 {qqq_df.index.max().date()})")
        print(f"   0050.TW 數據: {len(tw0050_df)} 天 ({tw0050_df.index.min().date()} 到 {tw0050_df.index.max().date()})")
        
        # 獲取 Market Score 數據
        print("📥 獲取 Market Score 數據...")
        tw_ms_df = self.get_market_score("TW", "2015-01-01", "2026-02-21")
        us_ms_df = self.get_market_score("US", "2015-01-01", "2026-02-21")
        
        print(f"   TW Market Score 數據: {len(tw_ms_df)} 天")
        print(f"   US Market Score 數據: {len(us_ms_df)} 天")
        
        # 計算技術指標
        print("\n📊 計算技術指標...")
        qqq_df['sma20'] = qqq_df['close'].rolling(window=20).mean()
        qqq_df['qqq_above_20ma'] = qqq_df['close'] > qqq_df['sma20']
        
        tw0050_df['sma120'] = tw0050_df['close'].rolling(window=120).mean()
        tw0050_df['tw0050_above_120ma'] = tw0050_df['close'] > tw0050_df['sma120']
        
        # 合併所有數據
        print("\n🔗 合併數據...")
        df = pd.DataFrame(index=pd.date_range(start=qqq_df.index.min(), end=qqq_df.index.max(), freq='D'))
        
        # 合併價格數據
        df = df.join(qqq_df[['close', 'qqq_above_20ma']], how='left', rsuffix='_qqq')
        df = df.join(tw0050_df[['close', 'tw0050_above_120ma']], how='left', rsuffix='_tw0050')
        
        # 重命名
        df = df.rename(columns={'close': 'qqq_close', 'close_tw0050': 'tw0050_close'})
        
        # 合併 Market Score
        df = df.join(tw_ms_df[['total_score']], how='left')
        df = df.rename(columns={'total_score': 'tw_market_score'})
        
        df = df.join(us_ms_df[['total_score']], how='left')
        df = df.rename(columns={'total_score': 'us_market_score'})
        
        # 計算 Buy & Hold 價值（50% QQQ + 50% 0050）
        df['buy_hold_value'] = (df['qqq_close'] / df['qqq_close'].iloc[0] * self.initial_cash * 0.5 +
                               df['tw0050_close'] / df['tw0050_close'].iloc[0] * self.initial_cash * 0.5)
        
        # 限制在 2019-01-01 之後的數據
        start_date = pd.Timestamp("2019-01-01")
        df = df[df.index >= start_date]
        
        # 移除沒有價格數據的行
        df = df.dropna(subset=['qqq_close', 'tw0050_close'])
        
        # 計算策略倉位
        print("📊 執行策略分析...")
        df['position_size'] = df.apply(self.calculate_position, axis=1)
        
        # 計算每日收益
        df['qqq_daily_return'] = df['qqq_close'].pct_change()
        df['tw0050_daily_return'] = df['tw0050_close'].pct_change()
        
        # 計算投資組合每日收益（50% QQQ + 50% 0050）
        df['portfolio_daily_return'] = (df['qqq_daily_return'] * 0.5 + df['tw0050_daily_return'] * 0.5)
        
        # 計算投資組合價值
        df['portfolio_value'] = self.initial_cash
        for i in range(1, len(df)):
            prev_value = df['portfolio_value'].iloc[i-1]
            daily_return = df['portfolio_daily_return'].iloc[i]
            position = df['position_size'].iloc[i]
            
            # 使用當日倉位的收益
            df.loc[df.index[i], 'portfolio_value'] = prev_value * (1 + daily_return * position)
        
        # 計算績效指標
        print("\n" + "="*80)
        print("📊 Market Score + 雙市場同時確認策略 v3")
        print("="*80)
        
        # 總報酬率
        total_return = (df['portfolio_value'].iloc[-1] / self.initial_cash - 1) * 100
        buy_hold_return = (df['buy_hold_value'].iloc[-1] / self.initial_cash - 1) * 100
        excess_return = total_return - buy_hold_return
        
        print(f"\n📈 績效指標")
        print("-" * 80)
        print(f"總報酬率:        {total_return:.2f}%")
        print(f"Buy & Hold 報酬率: {buy_hold_return:.2f}%")
        print(f"超額報酬:        {excess_return:.2f}%")
        
        print(f"\n最終價值:        ${df['portfolio_value'].iloc[-1]:,.2f}")
        print(f"Buy & Hold 價值:  ${df['buy_hold_value'].iloc[-1]:,.2f}")
        
        # 夏普比率
        excess_returns = df['portfolio_daily_return'] * df['position_size']
        sharpe_ratio = np.sqrt(252) * excess_returns.mean() / excess_returns.std() if excess_returns.std() != 0 else 0
        
        buy_hold_excess = df['portfolio_daily_return']
        buy_hold_sharpe = np.sqrt(252) * buy_hold_excess.mean() / buy_hold_excess.std() if buy_hold_excess.std() != 0 else 0
        
        print(f"\n夏普比率:        {sharpe_ratio:.2f}")
        print(f"Buy & Hold 夏普比率: {buy_hold_sharpe:.2f}")
        
        # 最大回撤
        df['drawdown'] = (df['portfolio_value'] - df['portfolio_value'].cummax()) / df['portfolio_value'].cummax()
        max_drawdown = df['drawdown'].min() * 100
        
        buy_hold_drawdown = (df['buy_hold_value'] - df['buy_hold_value'].cummax()) / df['buy_hold_value'].cummax()
        buy_hold_max_dd = buy_hold_drawdown.min() * 100
        
        print(f"最大回撤:        {max_drawdown:.2f}%")
        print(f"Buy & Hold 最大回撤: {buy_hold_max_dd:.2f}%")
        
        # 勝率
        trade_returns = df['portfolio_daily_return'] * df['position_size']
        win_rate = (trade_returns > 0).sum() / (trade_returns != 0).sum() * 100 if (trade_returns != 0).sum() > 0 else 0
        
        print(f"勝率:            {win_rate:.2f}%")
        
        # 倉位統計
        print(f"\n📊 倉位統計")
        print("-" * 80)
        print(f"平均倉位:        {df['position_size'].mean()*100:.1f}%")
        print(f"全倉天數:        {(df['position_size'] > 0.9).sum()} 天 ({(df['position_size'] > 0.9).sum()/len(df)*100:.1f}%)")
        print(f"半倉天數:        {((df['position_size'] >= 0.4) & (df['position_size'] <= 0.6)).sum()} 天 ({((df['position_size'] >= 0.4) & (df['position_size'] <= 0.6)).sum()/len(df)*100:.1f}%)")
        print(f"空倉天數:        {(df['position_size'] < 0.1).sum()} 天 ({(df['position_size'] < 0.1).sum()/len(df)*100:.1f}%)")
        
        # Market Score 覆蓋率
        ms_coverage = (df['tw_market_score'].notna() | df['us_market_score'].notna()).sum() / len(df) * 100
        print(f"Market Score 覆蓋率: {ms_coverage:.1f}%")
        
        # 關鍵洞察
        print(f"\n💡 關鍵洞察")
        print("-" * 80)
        if excess_return > 0:
            print(f"✅ 策略跑贏 Buy & Hold {excess_return:.2f}%")
        else:
            print(f"❌ 策略落後 Buy & Hold {abs(excess_return):.2f}%")
        
        if max_drawdown < buy_hold_max_dd:
            print(f"✅ 最大回撤控制在 {abs(max_drawdown):.1f}% 以內")
            print(f"📉 回撤對比: 策略 {abs(max_drawdown):.1f}% vs Buy & Hold {abs(buy_hold_max_dd):.1f}%")
            print(f"✅ 策略回撤比 Buy & Hold 少 {abs(buy_hold_max_dd - max_drawdown):.1f}%")
        
        if sharpe_ratio > buy_hold_sharpe:
            print(f"✅ 夏普比率優秀: {sharpe_ratio:.2f} vs Buy & Hold {buy_hold_sharpe:.2f}")
        
        print(f"\n" + "="*80)
        
        # 保存結果
        output_file = "/Users/charlie/.openclaw/workspace/market_score_dual_confirm_strategy_results.csv"
        df.to_csv(output_file)
        print(f"\n📁 詳細結果已保存至: {output_file}")
        
        return df

if __name__ == "__main__":
    strategy = MarketScoreDualConfirmStrategy(initial_cash=100000)
    results = strategy.backtest()
