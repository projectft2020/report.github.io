"""
動態閾值系統 - 基於歷史分位數
實現相關性非對稱閾值，自動適應市場環境
"""

import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 設置中文字體
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

class DynamicThresholdSystem:
    """動態閾值系統"""
    
    def __init__(self):
        self.thresholds = {}
    
    def calculate_correlation(self, prices, window=60):
        """
        計算滾動相關性
        
        參數:
            prices: 價格數據
            window: 滾動窗口
        
        返回:
            correlation_series: 平均相關性時間序列
        """
        # 計算收益率
        returns = prices.pct_change().dropna()
        
        # 計算滾動相關性矩陣
        rolling_corr = returns.rolling(window=window).corr()
        
        # 計算平均相關性（去除對角線）
        def avg_correlation(corr_matrix):
            if corr_matrix.isna().all().all():
                return np.nan
            values = corr_matrix.values
            # 只取上三角（不包含對角線）
            mask = np.triu_indices_from(values, k=1)
            return values[mask].mean()
        
        avg_corr_series = rolling_corr.groupby(level=0).apply(avg_correlation)
        
        return avg_corr_series
    
    def get_dynamic_threshold(self, correlation_history, window=252):
        """
        基於歷史分位數計算動態閾值
        
        參數:
            correlation_history: 歷史相關性序列
            window: 回看窗口（252 天 = 1 年）
        
        返回:
            high_threshold: 進入危機模式的閾值（75 分位）
            low_threshold: 退出危機模式的閾值（25 分位）
            stats: 統計信息字典
        """
        if len(correlation_history) < window:
            window = len(correlation_history)
        
        recent_corr = correlation_history.tail(window)
        
        # 75 分位：75% 的時間相關性低於此值
        high_threshold = recent_corr.quantile(0.75)
        
        # 25 分位：25% 的時間相關性高於此值
        low_threshold = recent_corr.quantile(0.25)
        
        # 統計信息
        stats = {
            'window': window,
            'current_corr': float(correlation_history.iloc[-1]),
            'mean': float(recent_corr.mean()),
            'std': float(recent_corr.std()),
            'min': float(recent_corr.min()),
            'max': float(recent_corr.max()),
            'high_threshold': float(high_threshold),
            'low_threshold': float(low_threshold),
            'median': float(recent_corr.median())
        }
        
        return high_threshold, low_threshold, stats
    
    def check_emergency_exit(self, correlation, vix, market_drop, correlation_history):
        """
        檢查是否需要緊急退場
        
        參數:
            correlation: 當前相關性
            vix: 當前 VIX
            market_drop: 市場下跌幅度
            correlation_history: 歷史相關性序列
        
        返回:
            should_exit: 是否退出
            reason: 退出原因
        """
        reasons = []
        
        # 條件 1：相關性暴漲（忽然爆升）
        if len(correlation_history) >= 5:
            recent_change = correlation - correlation_history.iloc[-5]
            if recent_change > 0.2:
                reasons.append(f"相關性暴漲：+{recent_change:.1%}")
        
        # 條件 2：VIX 暴漲（>40）
        if vix > 40:
            reasons.append(f"VIX 暴漲：{vix:.1f}")
        
        # 條件 3：市場大跌（>10%）
        if market_drop > 0.10:
            reasons.append(f"市場大跌：{market_drop:.1%}")
        
        should_exit = len(reasons) > 0
        reason = "、".join(reasons) if reasons else "無緊急退場"
        
        return should_exit, reason
    
    def check_entry_condition(self, correlation, vix, correlation_history, trend_signal):
        """
        檢查是否可以進場
        
        參數:
            correlation: 當前相關性
            vix: 當前 VIX
            correlation_history: 歷史相關性序列
            trend_signal: 趨勢信號
        
        返回:
            can_entry: 是否可以進場
            reason: 進場/不進場原因
        """
        reasons = []
        
        # 條件 1：相關性已經穩定在低位（至少 30 天）
        if len(correlation_history) >= 30:
            recent_avg = correlation_history.tail(30).mean()
            if recent_avg > 0.3:
                reasons.append(f"相關性仍高（{recent_avg:.2f}）")
        else:
            reasons.append("觀察期不足")
        
        # 條件 2：VIX 已經回落到正常水平（<25）
        if vix > 25:
            reasons.append(f"VIX 仍高（{vix:.1f}）")
        
        # 條件 3：有趨勢信號
        if not trend_signal:
            reasons.append("無趨勢信號")
        
        can_entry = len(reasons) == 0
        reason = "可以進場" if can_entry else "、".join(reasons)
        
        return can_entry, reason
    
    def simulate_strategy(self, prices, vix_data, window=252):
        """
        模擬策略執行
        
        參數:
            prices: 價格數據
            vix_data: VIX 數據
            window: 回看窗口
        
        返回:
            signals_df: 信號 DataFrame
        """
        # 計算相關性時間序列
        correlation_series = self.calculate_correlation(prices)
        
        # 對齊數據
        aligned_data = pd.concat([
            correlation_series,
            vix_data
        ], axis=1).dropna()
        
        aligned_data.columns = ['correlation', 'vix']
        
        # 計算動態閾值
        signals = []
        for i in range(len(aligned_data)):
            # 只在有足夠歷史數據時計算閾值
            if i >= window:
                history = aligned_data['correlation'].iloc[:i]
                high_threshold, low_threshold, stats = self.get_dynamic_threshold(
                    history, 
                    window=window
                )
                
                current_corr = aligned_data['correlation'].iloc[i]
                current_vix = aligned_data['vix'].iloc[i]
                
                # 確定市場狀態
                if current_corr > high_threshold:
                    market_state = '危機市場'
                elif current_corr < low_threshold:
                    market_state = '正常市場'
                else:
                    market_state = '過渡市場'
                
                signals.append({
                    'date': aligned_data.index[i],
                    'correlation': current_corr,
                    'vix': current_vix,
                    'high_threshold': high_threshold,
                    'low_threshold': low_threshold,
                    'market_state': market_state
                })
        
        signals_df = pd.DataFrame(signals)
        signals_df.set_index('date', inplace=True)
        
        return signals_df
    
    def plot_signals(self, signals_df, title="動態閾值系統 - 市場狀態識別"):
        """
        繪製信號圖表
        
        參數:
            signals_df: 信號 DataFrame
            title: 圖表標題
        """
        fig, axes = plt.subplots(3, 1, figsize=(15, 12))
        
        # 子圖 1：相關性時間序列與動態閾值
        axes[0].plot(signals_df.index, signals_df['correlation'], 
                    label='相關性', linewidth=2, color='blue')
        axes[0].plot(signals_df.index, signals_df['high_threshold'], 
                    label='高閾值（進入危機）', linewidth=1.5, color='red', linestyle='--')
        axes[0].plot(signals_df.index, signals_df['low_threshold'], 
                    label='低閾值（進入正常）', linewidth=1.5, color='green', linestyle='--')
        
        axes[0].set_title('相關性時間序列與動態閾值', fontsize=14, fontweight='bold')
        axes[0].set_ylabel('相關係數', fontsize=12)
        axes[0].legend(loc='upper left')
        axes[0].grid(True, alpha=0.3)
        
        # 子圖 2：市場狀態
        state_colors = {
            '正常市場': 'green',
            '過渡市場': 'yellow',
            '危機市場': 'red'
        }
        
        for state, color in state_colors.items():
            state_data = signals_df[signals_df['market_state'] == state]
            if not state_data.empty:
                axes[1].scatter(state_data.index, 
                               [1] * len(state_data), 
                               label=state, color=color, s=30, alpha=0.6)
        
        axes[1].set_title('市場狀態識別', fontsize=14, fontweight='bold')
        axes[1].set_ylabel('市場狀態', fontsize=12)
        axes[1].set_yticks([1])
        axes[1].set_yticklabels(['市場狀態'])
        axes[1].legend(loc='upper left')
        axes[1].grid(True, alpha=0.3)
        
        # 子圖 3：VIX 時間序列
        axes[2].plot(signals_df.index, signals_df['vix'], 
                    label='VIX', linewidth=2, color='purple')
        axes[2].axhline(y=40, color='red', linestyle='--', 
                       linewidth=1.5, label='VIX 暴漲閾值（40）')
        axes[2].axhline(y=25, color='green', linestyle='--', 
                       linewidth=1.5, label='VIX 正常閾值（25）')
        
        axes[2].set_title('VIX 時間序列', fontsize=14, fontweight='bold')
        axes[2].set_ylabel('VIX', fontsize=12)
        axes[2].set_xlabel('日期', fontsize=12)
        axes[2].legend(loc='upper left')
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('dynamic_threshold_analysis.png', dpi=150, bbox_inches='tight')
        print(f"\n📊 圖表已保存: dynamic_threshold_analysis.png")
        plt.close()
    
    def analyze_states(self, signals_df):
        """
        分析市場狀態分佈
        
        參數:
            signals_df: 信號 DataFrame
        
        返回:
            state_stats: 狀態統計
        """
        state_counts = signals_df['market_state'].value_counts()
        total = len(signals_df)
        
        state_stats = {}
        for state, count in state_counts.items():
            percentage = (count / total) * 100
            state_stats[state] = {
                'count': count,
                'percentage': percentage
            }
        
        # 計算狀態轉換次數
        state_transitions = 0
        previous_state = None
        for state in signals_df['market_state']:
            if previous_state is not None and state != previous_state:
                state_transitions += 1
            previous_state = state
        
        return state_stats, state_transitions
    
    def print_analysis(self, signals_df):
        """
        打印分析結果
        
        參數:
            signals_df: 信號 DataFrame
        """
        print("="*80)
        print("📊 動態閾值系統分析結果")
        print("="*80)
        
        # 基本統計
        print(f"\n📈 基本統計:")
        print(f"  - 數據期間: {signals_df.index[0]} 至 {signals_df.index[-1]}")
        print(f"  - 總交易日: {len(signals_df)} 天")
        
        # 相關性統計
        print(f"\n🔗 相關性統計:")
        print(f"  - 當前相關性: {signals_df['correlation'].iloc[-1]:.4f}")
        print(f"  - 平均相關性: {signals_df['correlation'].mean():.4f}")
        print(f"  - 最小相關性: {signals_df['correlation'].min():.4f}")
        print(f"  - 最大相關性: {signals_df['correlation'].max():.4f}")
        print(f"  - 相關性標準差: {signals_df['correlation'].std():.4f}")
        
        # 動態閾值統計
        print(f"\n🎯 動態閾值統計:")
        print(f"  - 高閾值平均: {signals_df['high_threshold'].mean():.4f}")
        print(f"  - 低閾值平均: {signals_df['low_threshold'].mean():.4f}")
        print(f"  - 閾值寬度平均: {(signals_df['high_threshold'] - signals_df['low_threshold']).mean():.4f}")
        
        # 市場狀態分析
        state_stats, state_transitions = self.analyze_states(signals_df)
        
        print(f"\n📊 市場狀態分佈:")
        for state, stats in state_stats.items():
            color = "🟢" if state == "正常市場" else ("🟡" if state == "過渡市場" else "🔴")
            print(f"  - {color} {state}: {stats['count']} 天 ({stats['percentage']:.1f}%)")
        
        print(f"\n🔄 狀態轉換次數: {state_transitions} 次")
        
        # 當前狀態
        current_state = signals_df['market_state'].iloc[-1]
        current_corr = signals_df['correlation'].iloc[-1]
        current_vix = signals_df['vix'].iloc[-1]
        current_high = signals_df['high_threshold'].iloc[-1]
        current_low = signals_df['low_threshold'].iloc[-1]
        
        print(f"\n📍 當前市場狀態:")
        color = "🟢" if current_state == "正常市場" else ("🟡" if current_state == "過渡市場" else "🔴")
        print(f"  - {color} {current_state}")
        print(f"  - 當前相關性: {current_corr:.4f}")
        print(f"  - 高閾值: {current_high:.4f}")
        print(f"  - 低閾值: {current_low:.4f}")
        print(f"  - VIX: {current_vix:.1f}")
        
        # 策略建議
        if current_state == "危機市場":
            print(f"\n💡 策略建議:")
            print(f"  - 🔴 保持現金，避免虧損")
            print(f"  - 🔴 等待相關性下降到 {current_low:.4f} 以下")
            print(f"  - 🔴 等待 VIX 下降到 25 以下")
        elif current_state == "過渡市場":
            print(f"\n💡 策略建議:")
            print(f"  - 🟡 謹慎配置，增加現金比例")
            print(f"  - 🟡 密切監控相關性變化")
            print(f"  - 🟡 等待明確的進場信號")
        else:  # 正常市場
            print(f"\n💡 策略建議:")
            print(f"  - 🟢 MST + Supertrend 策略正常運作")
            print(f"  - 🟢 尋找低相關性資產")
            print(f"  - 🟢 等待 Supertrend 買入信號")


def main():
    """主函數"""
    print("="*80)
    print("🚀 動態閾值系統測試")
    print("="*80)
    
    # 創建系統實例
    system = DynamicThresholdSystem()
    
    # 測試資產（核心 + 板塊）
    tickers = ['SPY', 'QQQ', 'IWM', 'XLI', 'XLV', 'XLK', 'XLF', 'XLE']
    
    print(f"\n下載 {len(tickers)} 個資產的數據...")
    prices = yf.download(tickers, period='2y', progress=False, auto_adjust=True)['Close']
    
    # 下載 VIX 數據
    print("下載 VIX 數據...")
    vix = yf.download('^VIX', period='2y', progress=False, auto_adjust=True)['Close']
    
    # 模擬策略
    print("\n模擬策略執行...")
    signals_df = system.simulate_strategy(prices, vix, window=252)
    
    # 打印分析結果
    system.print_analysis(signals_df)
    
    # 繪製圖表
    print("\n繪製圖表...")
    system.plot_signals(signals_df)
    
    # 保存結果
    signals_df.to_csv('dynamic_threshold_signals.csv')
    print(f"\n💾 信號數據已保存: dynamic_threshold_signals.csv")
    
    print("\n✅ 測試完成！")


if __name__ == '__main__':
    main()
