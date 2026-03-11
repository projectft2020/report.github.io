#!/usr/bin/env python3
"""
驗證策略數據的真實性
檢查各種指標的邏輯一致性
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class StrategyPerformance:
    """策略績效數據"""
    name: str
    trade_count: int
    total_return: float  # %
    avg_return: float  # %
    win_rate: float  # %
    profit_factor: float
    max_profit: float  # %
    max_loss: float  # %
    sharpe_ratio: float

    def validate(self) -> List[str]:
        """驗證數據合理性"""
        issues = []

        # 檢查 1：平均報酬 = 總報酬 / 交易筆數
        expected_avg = self.total_return / self.trade_count
        if abs(self.avg_return - expected_avg) > 0.1:
            issues.append(f"⚠️ 平均報酬不匹配：計算值 {expected_avg:.2f}% vs 聲稱值 {self.avg_return:.2f}%")

        # 檢查 2：勝率範圍
        if self.win_rate < 0 or self.win_rate > 100:
            issues.append(f"⚠️ 勝率超出範圍：{self.win_rate}%")

        # 檢查 3：勝率 100% 但有最大虧損？
        if self.win_rate == 100 and self.max_loss < 0:
            issues.append(f"❌ 勝率 100% 但最大虧損為 {self.max_loss}%（邏輯矛盾）")

        # 檢查 4：獲利因子
        if self.profit_factor <= 0 and self.win_rate < 100:
            issues.append(f"⚠️ 獲利因子異常：{self.profit_factor}（通常應 > 0）")

        # 檢查 5：Sharpe Ratio
        if self.sharpe_ratio < 0:
            issues.append(f"⚠️ Sharpe Ratio 為負：{self.sharpe_ratio}（策略不賺錢）")

        # 檢查 6：最大虧損 < 最大獲利？
        if abs(self.max_loss) > self.max_profit and self.win_rate > 50:
            issues.append(f"⚠️ 最大虧損 {self.max_loss}% > 最大獲利 {self.max_profit}%，但勝率高（{self.win_rate}%）")

        # 檢查 7：勝率 100% 的合理性
        if self.win_rate == 100 and self.trade_count > 10:
            issues.append(f"❌ 勝率 100% 在 {self.trade_count} 筆交易中幾乎不可能（過擬合或計算錯誤）")

        # 檢查 8：報酬率過高？
        if self.avg_return > 50:
            issues.append(f"⚠️ 平均報酬過高：{self.avg_return}%（需驗證數據）")

        # 檢查 9：最大虧損過小？
        if self.max_loss > -2 and self.trade_count > 50:
            issues.append(f"⚠️ 最大虧損過小：{self.max_loss}%（在 {self.trade_count} 筆交易中不常見）")

        # 檢查 10：Sharpe Ratio 過高？
        if self.sharpe_ratio > 2 and self.trade_count < 100:
            issues.append(f"⚠️ Sharpe Ratio 過高：{self.sharpe_ratio}（需驗證數據）")

        return issues

def analyze_strategy_consistency(strategies: List[StrategyPerformance]) -> dict:
    """分析多個策略之間的一致性"""
    issues = {}

    # 檢查 1：原始策略 vs 延遲進場
    original = next((s for s in strategies if "原始" in s.name), None)
    delayed = next((s for s in strategies if "延遲" in s.name and "動態" not in s.name), None)
    dynamic = next((s for s in strategies if "動態" in s.name and "延遲" not in s.name), None)
    hybrid = next((s for s in strategies if "延遲" in s.name and "動態" in s.name), None)

    if original and delayed:
        # 延遲進場應該過濾掉一些短持倉交易
        if delayed.trade_count == original.trade_count:
            issues['delayed_trade_count'] = f"⚠️ 延遲進場交易筆數與原始相同（{delayed.trade_count}），但應該有部分過濾"

        # 延遲進場的報酬率應該更高
        if delayed.avg_return < original.avg_return:
            issues['delayed_return'] = f"⚠️ 延遲進場平均報酬 ({delayed.avg_return}%) < 原始 ({original.avg_return}%)"

    if original and hybrid:
        # 延遲+動態應該過濾掉很多交易
        filtered_count = original.trade_count - hybrid.trade_count
        filtered_pct = (filtered_count / original.trade_count * 100) if original.trade_count > 0 else 0

        if hybrid.trade_count >= original.trade_count:
            issues['hybrid_filtering'] = f"❌ 延遲+動態交易筆數 ({hybrid.trade_count}) ≥ 原始 ({original.trade_count})，但應該過濾掉部分"

        if hybrid.win_rate == 100 and hybrid.trade_count > 20:
            issues['hybrid_win_rate'] = f"❌ 延遲+動態勝率 100% 在 {hybrid.trade_count} 筆交易中不可能"

        # 獲利因子 0.00
        if hybrid.profit_factor == 0:
            issues['hybrid_profit_factor'] = f"⚠️ 延遲+動態獲利因子為 0（計算錯誤）"

    return issues

def check_calculation_logic():
    """檢查計算邏輯的合理性"""

    print("=" * 80)
    print("🔍 策略數據驗證")
    print("=" * 80)

    # 定義策略數據（從用戶提供的表格中提取）
    strategies = [
        StrategyPerformance(
            name="原始策略",
            trade_count=466,
            total_return=234.07,
            avg_return=11.17,
            win_rate=44.2,
            profit_factor=3.14,
            max_profit=363.24,
            max_loss=-34.56,
            sharpe_ratio=0.27
        ),
        StrategyPerformance(
            name="延遲進場 (第 8 天)",
            trade_count=466,
            total_return=6397.99,
            avg_return=13.73,
            win_rate=51.1,
            profit_factor=4.35,
            max_profit=372.47,
            max_loss=-32.95,
            sharpe_ratio=0.32
        ),
        StrategyPerformance(
            name="動態風險管理",
            trade_count=466,
            total_return=2601.94,
            avg_return=5.58,
            win_rate=44.2,
            profit_factor=3.14,
            max_profit=181.62,
            max_loss=-17.28,
            sharpe_ratio=0.27
        ),
        StrategyPerformance(
            name="延遲+動態 (第 7 天篩選)",
            trade_count=214,
            total_return=8291.20,
            avg_return=38.74,
            win_rate=100.0,
            profit_factor=0.00,
            max_profit=372.47,
            max_loss=1.37,
            sharpe_ratio=0.74
        ),
    ]

    # 檢查 1：各策略的內部一致性
    print("\n【檢查 1：各策略內部一致性】")
    all_issues = {}
    for strategy in strategies:
        issues = strategy.validate()
        if issues:
            print(f"\n🚨 {strategy.name} 發現問題：")
            for issue in issues:
                print(f"  {issue}")
            all_issues[strategy.name] = issues
        else:
            print(f"✅ {strategy.name} 內部檢查通過")

    # 檢查 2：策略之間的一致性
    print("\n" + "=" * 80)
    print("【檢查 2：策略之間的一致性】")
    consistency_issues = analyze_strategy_consistency(strategies)
    for key, issue in consistency_issues.items():
        print(f"{issue}")

    # 檢查 3：計算邏輯驗證
    print("\n" + "=" * 80)
    print("【檢查 3：計算邏輯驗證】")

    # 3.1 驗證平均報酬
    print("\n3.1 驗證平均報酬 = 總報酬 / 交易筆數")
    for strategy in strategies:
        expected_avg = strategy.total_return / strategy.trade_count
        diff = abs(strategy.avg_return - expected_avg)
        print(f"{strategy.name}:")
        print(f"  預期: {expected_avg:.2f}%")
        print(f"  聲稱: {strategy.avg_return:.2f}%")
        print(f"  差異: {diff:.2f}% {'✅' if diff < 1 else '❌'}")

    # 3.2 驗證獲利因子計算
    print("\n3.2 獲利因子邏輯")
    print("獲利因子 = 總盈利 / 總虧損")
    print("如果勝率 100%，獲利因子應該是無窮大或無法計算（分母為 0）")
    print("但延遲+動態策略聲稱獲利因子 = 0.00，這表示：")
    print("  ❌ 要么分母為 0（無虧損），應為無窮大")
    print("  ❌ 要么計算錯誤（除以 0 異常處理）")

    # 3.3 驗證勝率 100% 的可能性
    print("\n3.3 勝率 100% 的概率分析")
    if strategies[-1].win_rate == 100:
        n = strategies[-1].trade_count
        p = 0.5  # 假設每筆交易獲利概率 50%
        probability = p ** n
        print(f"如果每筆交易獲利概率 50%，{n} 筆交易全部獲利的概率：{probability:.10f}")
        print(f"  ≈ 1 / {1/probability:.0f}")
        print(f"  ❌ 幾乎不可能！")

    # 檢查 4：延遲+動態策略的篩選邏輯
    print("\n" + "=" * 80)
    print("【檢查 4：延遲+動態策略的篩選邏輯】")

    original = strategies[0]
    hybrid = strategies[3]

    filtered_count = original.trade_count - hybrid.trade_count
    filtered_pct = filtered_count / original.trade_count * 100

    print(f"原始策略交易筆數: {original.trade_count}")
    print(f"延遲+動態交易筆數: {hybrid.trade_count}")
    print(f"過濾掉交易: {filtered_count} ({filtered_pct:.1f}%)")
    print(f"\n第 7 天篩選邏輯：虧損 > 1% 不進場")
    print(f"  → 過濾掉的 {filtered_count} 筆交易在第 7 天都虧損 > 1%")
    print(f"  → 保留的 {hybrid.trade_count} 筆交易在第 7 天虧損 < 1%")
    print(f"  → 但這 {hybrid.trade_count} 筆交易後續都盈利？（勝率 100%）")
    print(f"  ⚠️ 這不合理！第 7 天虧損 < 1% 不代表第 8 天後一定盈利")

    # 總結
    print("\n" + "=" * 80)
    print("【總結】")
    print("=" * 80)

    total_issues = sum(len(issues) for issues in all_issues.values()) + len(consistency_issues)

    if total_issues > 0:
        print(f"❌ 發現 {total_issues} 個問題，數據可能不可信")
        print("\n最可疑的問題：")
        print("  1. 延遲+動態策略勝率 100%（214 筆交易全部盈利）")
        print("  2. 延遲+動態策略最大虧損 1.37%（但勝率 100%？）")
        print("  3. 延遲+動態策略獲利因子 0.00（計算錯誤）")
        print("  4. 平均報酬 = 總報酬 / 交易筆數 的檢查可能不通過")
    else:
        print("✅ 沒有發現明顯問題")

    # 結論
    print("\n" + "=" * 80)
    print("【結論】")
    print("=" * 80)

    print("延遲+動態策略的數據有明顯異常：")
    print("  ❌ 勝率 100% 在 214 筆交易中不可能")
    print("  ❌ 最大虧損 1.37% 與勝率 100% 矛盾")
    print("  ❌ 獲利因子 0.00 表示計算錯誤")
    print("\n建議：")
    print("  1. 驗證原始數據的來源和計算邏輯")
    print("  2. 重新回測各個策略")
    print("  3. 檢查是否有過擬合或數據洩漏")

if __name__ == "__main__":
    check_calculation_logic()
