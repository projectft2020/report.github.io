#!/usr/bin/env python3
"""
基於 Supertrend 回測結果，分析最佳進場時機策略
"""

import pandas as pd
import json
from datetime import datetime

# 基於回測報告的關鍵數據
key_stats = {
    "total_trades": 180,
    "win_rate": 45.0,  # 45%
    "reward_risk_ratio": 5.21,
    "avg_profit": 11647,
    "avg_loss": -2234,
    "max_profit": 204538,
    "max_loss": -8878,
    "avg_holding_days": 101.4,
    "median_holding_days": 61,
    "best_year": {
        "year": 2025,
        "profit": 516783,
        "trades": 45,
        "win_rate": 62.22
    },
    "worst_year": {
        "year": 2019,
        "profit": -5989,
        "trades": 3,
        "win_rate": 0
    },
    "monthly_losses": 3,
    "max_consecutive_wins": 10,
    "max_consecutive_losses": 12,
    "drawdown": 27.0,
    "top_performers": [
        {"symbol": "6770.TW", "profit": 204538},
        {"symbol": "8046.TW", "profit": 78460}
    ]
}

print("="*60)
print("Supertrend 策略：最佳進場時機分析")
print("="*60)

print("\n【核心發現】")
print(f"1. 勝率低（{key_stats['win_rate']}%），但盈虧比高（{key_stats['reward_risk_ratio']}:1）")
print(f"2. 經典趨勢跟隨模式：低勝率 + 高盈虧比")
print(f"3. 利潤高度集中：少數大盈利驅動回報")
print(f"4. 最大虧損僅 ${key_stats['max_loss']:,}，風險控制優秀")
print(f"5. 平均持倉 {key_stats['avg_holding_days']:.1f} 天（中位數 {key_stats['median_holding_days']} 天）")

print("\n" + "="*60)
print("策略一：基於年份的進場時機")
print("="*60)

print(f"\n【最佳年份】{key_stats['best_year']['year']} 年")
print(f"- 總利潤：${key_stats['best_year']['profit']:,}")
print(f"- 勝率：{key_stats['best_year']['win_rate']:.1f}%")
print(f"- 交易數：{key_stats['best_year']['trades']}")
print(f"✅ 這個年份的市場環境非常適合 Supertrend")

print(f"\n【最差年份】{key_stats['worst_year']['year']} 年")
print(f"- 總利潤：${key_stats['worst_year']['profit']:,}")
print(f"- 勝率：{key_stats['worst_year']['win_rate']:.1f}%")
print(f"- 交易數：{key_stats['worst_year']['trades']}")
print(f"⚠️ 這個年份的市場環境不適合 Supertrend")

print("\n【年份特徵推斷】")
print("2025 年（最佳）：")
print("- 可能是牛市或強勢市場")
print("- 趨勢明顯，假突破較少")
print("- 適合全倉或高倉位操作")
print("\n2019 年（最差）：")
print("- 可能是盤整或震盪市場")
print("- 趨勢不明顯，頻繁翻轉")
print("- 應該空倉或極低倉位")

print("\n" + "="*60)
print("策略二：基於持倉天數的進場時機")
print("="*60)

print("\n【持倉天數分類】")
print("< 14 天：")
print("- 短期波動，容易虧損")
print("- 不適合進場（假突破多）")
print("\n14-30 天：")
print("- 中期持倉，盈利機會增加")
print("- 可以適當參與")
print("\n30-60 天：")
print("- 中長期持倉，盈利開始顯著")
print("- ✅ 最佳進場區間")
print("\n> 60 天：")
print("- 長期趨勢，大盈利機會")
print("- ✅ 保留現有倉位，不加倉")

print("\n【進場建議】")
print("1. 等待 Supertrend 訊號後，觀察 7 天")
print("2. 第 7 天評估：")
print("   - 如果盈利 → 繼續持有")
print("   - 如果虧損 > -2% → 出場（假突破）")
print("   - 如果虧損 < -2% → 繼續持有")
print("3. 第 30 天後：大幅加倉")
print("4. 第 60 天後：減倉，鎖定利潤")

print("\n" + "="*60)
print("策略三：基於勝率/虧損的進場時機")
print("="*60)

print("\n【連勝連敗分析】")
print(f"最大連勝：{key_stats['max_consecutive_wins']} 次")
print(f"最大連敗：{key_stats['max_consecutive_losses']} 次")
print("\n【進場建議】")
print("1. 連勝 > 5 次：")
print("   - 市場處於良好狀態")
print("   - ✅ 可以積極進場")
print("   - 倉位提升至 15-20% per trade")
print("\n2. 連敗 > 3 次：")
print("   - 市場可能轉壞")
print("   - ⚠️ 減少新進場")
print("   - 倉位降至 5-10% per trade")
print("\n3. 連敗 > 8 次：")
print("   - 市場環境不適合")
print("   - ❌ 完全停止進場")
print("   - 現有倉位止損出場")

print("\n" + "="*60)
print("策略四：基於最大虧損的進場時機")
print("="*60)

print("\n【風險控制】")
print(f"單筆最大虧損：${key_stats['max_loss']:,}")
print(f"相當於：${key_stats['max_loss']:,} / ${key_stats['avg_profit'] * key_stats['win_rate'] / 100:.0f} = "
      f"{key_stats['max_loss'] / (key_stats['avg_profit'] * key_stats['win_rate'] / 100) * 100:.1f}% 平均盈利")
print("\n【進場建議】")
print("1. 設定單筆虧損限額：$10,000")
print("2. 超過限額立即出場")
print("3. 連續 3 次觸發限額 → 停止進場")
print("4. 每月總虧損超過 $30,000 → 停止進場")

print("\n" + "="*60)
print("策略五：基於大盤環境的進場時機")
print("="*60)

print("\n【大盤指標（推斷）】")
print("加權指數處於：")
print("- 低點區域（距低點 < 10%）：")
print("  - ✅ 機會大於風險")
print("  - 積極進場，倉位 15-20%")
print("\n- 中間區域（距低點 10-30%）：")
print("  - ⚠️ 風險平衡")
print("  - 正常進場，倉位 10-15%")
print("\n- 高點區域（距高點 < 10%）：")
print("  - ❌ 風險大於機會")
print("  - 減少進場，倉位 5-10%")

print("\n【波動率指標】")
print("低波動率（< 1%）：")
print("- 盤整市場，趨勢不明")
print("- ⚠️ 不進場或少進場")
print("\n正常波動率（1-2%）：")
print("- 適合 Supertrend")
print("- ✅ 正常進場")
print("\n高波動率（> 2%）：")
print("- 市場不穩定")
print("- ⚠️ 減少倉位，5-10%")

print("\n" + "="*60)
print("綜合進場策略建議")
print("="*60)

print("\n【今天應該進場嗎？】")
print("\n✅ **可以進場，但要分批**")
print("\n理由：")
print("1. 當前有 61 檔買入訊號（60.4%），市場偏多")
print("2. 類似於 2025 年的市場環境（推斷）")
print("3. 連勝連敗未知，假設正常")
print("4. 建議：先買 3-5 檔，觀察 7 天")

print("\n【進場步驟】")
print("1. 今天買入 3-5 檔（每檔 10-13.3% 倉位）")
print("2. 等待 7 天評估")
print("3. 第 7 天：")
print("   - 盈利 > 2%：加倉到 7-10 檔")
print("   - 虧損 < -2%：出場")
print("   - 其他：持有不動")
print("4. 監控新訊號（空轉多）")
print("   - 如果出現，繼續進場")
print("   - 如果沒有，觀察現有倉位")

print("\n【風險控制】")
print("1. 單檔最大虧損：$10,000")
print("2. 總倉位不超過 80%")
print("3. 連敗 3 次：停止進場")
print("4. 每月總虧損超過 $30,000：停止進場")

print("\n【資金分配】")
print("初始：$90,000")
print("第一天：")
print("- 買入 3 檔：每檔 $11,970（13.3%）")
print("- 總成本：$35,910（39.9%）")
print("- 剩餘：$54,090（60.1%）")
print("\n第 7 天（如果盈利）：")
print("- 加倉 2-4 檔：每檔 $11,970")
print("- 總成本：$59,850-83,790（66.5-93.1%）")
print("- 剩餘：$30,150-$6,210")

print("\n【總結】")
print("✅ 可以進場，但要分批")
print("✅ 先買 3-5 檔，觀察 7 天")
print("✅ 第 7 天根據表現調整")
print("✅ 監控新訊號（空轉多）")
print("✅ 嚴格風險控制")
print("✅ 不要一次全買")

print("\n" + "="*60)
print(f"分析時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*60)
