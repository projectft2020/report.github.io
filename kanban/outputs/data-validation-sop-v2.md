# 數據驗證 SOP v2.0
## 紅隊測試機制（2026-03-01）

---

## 一、背景與動機

### 1.1 Supertrend 驗證失敗案例（2026-02-28）

**問題發現**：
- Supertrend 策略對比報告顯示「勝率 100%」
- 最大虧損 1.37% 與勝率 100% 矛盾
- 獲利因子 0.00 計算錯誤

**原因分析**：
1. ❌ 沒有事前假設（假設勝率應該是什麼範圍？）
2. ❌ 沒有邊界檢查（勝率>95%應該觸發警報）
3. ❌ 沒有雙重驗證（用另一種方法交叉檢查）

**教訓**：可疑數據立即停止，先驗證再分析

### 1.2 為什麼需要「紅隊測試」？

**紅隊測試定義**：
- 自己攻擊自己的結果
- 從對手角度挑戰假設和結論
- 尋找邊界情況和異常點

**目的**：
- 避免確認偏差（Confirmation Bias）
- 發現數據洩漏和計算錯誤
- 確保結論的穩健性

---

## 二、數據驗證 SOP（4步驟）

### 步驟 1：事前假設（Pre-Assumption）

**目標**：在分析前預先定義合理範圍

**檢查清單**：
- [ ] 勝率範圍：假設在什麼範圍內是合理的？
- [ ] 收益率範圍：年化收益率是否合理？
- [ ] 最大回撤：與策略類型是否匹配？
- [ ] 交易頻率：是否符合策略特性？

**策略類型參考**：

| 策略類型 | 勝率範圍 | 收益率範圍 | 最大回撤 |
|---------|---------|-----------|---------|
| 趨勢跟踪 | 30-50% | 中高 | 可能較大 |
| 均值回歸 | 70-90% | 中低 | 中等 |
| 動量策略 | 55-65% | 中高 | 中等 |
| 套利策略 | 85-95% | 低 | 低 |

**示例**：
> Supertrend 策略（趨勢跟踪）：事前假設勝率 30-50%
> 如果報告顯示勝率 100% → **立即觸發警報** ⚠️

### 步驟 2：邊界檢查（Boundary Check）

**目標**：檢查數據是否在合理邊界內

**檢查清單**：
- [ ] 勝率 > 95%？ → 立即停止，驗證數據
- [ ] 勝率 < 20%？ → 檢查計算邏輯
- [ ] Sharpe > 3？ → 檢查是否過擬合
- [ ] 最大回撤 < 1% 且 勝率高？ → 檢查數據洩漏
- [ ] 交易次數 < 10？ → 統計意義不足

**不可能數據清單**：

| 指標 | 不可能條件 | 檢查原因 |
|------|-----------|---------|
| 勝率 | > 95% 或 < 20% | 過擬合或計算錯誤 |
| Sharpe | > 3 | 過擬合或數據洩漏 |
| 最大回撤 | < 1% 且勝率高 | 數據洩漏或計算錯誤 |
| 獲利因子 | = 0 或 ∞ | 計算錯誤 |
| 總收益 | > 1000%/年 | 過擬合或數據錯誤 |
| 交易次數 | < 10 | 統計意義不足 |

### 步驟 3：雙重驗證（Cross-Validation）

**目標**：用另一種方法交叉檢查關鍵結論

**驗證方法**：

#### 方法 1：獨立計算
- 用不同的代碼庫重新計算關鍵指標
- 例如：用 pandas vs numpy vs 手動計算

#### 方法 2：滾動窗口檢查
- 檢查不同時間窗口的穩定性
- 例如：2020-2023 vs 2021-2023

#### 方法 3：參數敏感性分析
- 改變關鍵參數，觀察結果變化
- 如果小改動導致大變化 → 不穩定

#### 方法 4：樣本外測試
- 用訓練集之外的數據測試
- 如果樣本外表現遠低於樣本內 → 過擬合

**示例**：
> Supertrend 策略報告：勝率 100%
>
> 驗證步驟：
> 1. ✅ 獨立計算：用另一個腳本重新計算 → 結果一致
> 2. ⚠️ 滾動窗口：2020-2022 勝率 100%，2023 勝率 60% → **不穩定**
> 3. ❌ 樣本外：用 2024-2026 測試 → 勝率 40% → **過擬合**
> 4. ❌ **結論**：報告中的勝率 100% 不可靠

### 步驟 4：紅隊測試（Red Team Testing）

**目標**：從對手角度攻擊自己的結論

**攻擊角度**：

#### 角度 1：尋找數據洩漏
**問題**：
- 是否使用了未來數據？
- 是否在回測中使用了訓練集的信息？

**檢查方法**：
- 檢查代碼是否有 look-ahead bias
- 檢查是否在計算指標時使用了未來數據

#### 角度 2：尋找過擬合
**問題**：
- 是否對特定數據集過度優化？
- 是否有太多參數？

**檢查方法**：
- 參數數量 > 5？ → 高風險
- 樣本內表現遠高於樣本外？ → 過擬合
- 改變參數，結果崩潰？ → 不穩定

#### 角度 3：尋找邏輯錯誤
**問題**：
- 數據是否邏輯一致？
- 計算方式是否正確？

**檢查方法**：
- 檢查指標定義（勝率、夏普、最大回撤）
- 檢查計算邏輯（是否除以零？是否缺少條件？）
- 檢查數據完整性（是否有缺失值？）

#### 角度 4：尋找幸存者偏差
**問題**：
- 是否只選擇了表現好的資產？
- 是否忽略了失敗的案例？

**檢查方法**：
- 是否有選擇性報告？
- 是否有隱藏的失敗案例？

**示例**：
> Supertrend 策略報告紅隊測試：
>
> 攻擊角度 1：尋找數據洩漏
> - ⚠️ 發現：計算 Supertrend 指標時，使用了當日收盤價
> - ❌ 問題：當日收盤價在交易時不可用，屬於數據洩漏
>
> 攻擊角度 2：尋找過擬合
> - ⚠️ 發現：參數 length=10, multiplier=3.0 是在全數據集上優化的
> - ❌ 問題：沒有樣本外測試，可能過擬合
>
> 攻擊角度 3：尋找邏輯錯誤
> - ❌ 發現：獲利因子計算錯誤，總利潤/總虧損 = 0.00
> - ❌ 問題：計算邏輯錯誤，分母為 0
>
> **結論**：報告不可靠，數據驗證失敗

---

## 三、不可能數據清單（Quick Check）

### 3.1 策略指標不可能清單

| 指標 | 不可能條件 | 可能原因 | 處理 |
|------|-----------|---------|------|
| 勝率 | > 95% | 過擬合、數據洩漏 | ❌ 立即停止 |
| 勝率 | < 20% | 計算錯誤 | ❌ 檢查邏輯 |
| Sharpe | > 3 | 過擬合、數據洩漏 | ❌ 檢查樣本外 |
| Sharpe | < 0 | 策略虧損 | ⚠️ 檢查策略 |
| 最大回撤 | < 1% 且勝率高 | 數據洩漏 | ❌ 檢查代碼 |
| 獲利因子 | = 0 | 計算錯誤 | ❌ 檢查邏輯 |
| 獲利因子 | = ∞ | 無虧損交易 | ⚠️ 檢查數據 |
| 年化收益 | > 1000% | 過擬合、數據錯誤 | ❌ 檢查樣本外 |
| 交易次數 | < 10 | 統計不足 | ⚠️ 增加數據 |
| 交易次數 | > 10000/年 | 過度交易 | ⚠️ 檢查成本 |

### 3.2 策略類型參考範圍

| 策略類型 | 勝率範圍 | Sharpe 範圍 | 最大回撤 | 交易頻率 |
|---------|---------|-----------|---------|---------|
| 趨勢跟踪 | 30-50% | 0.5-1.5 | 10-30% | 低-中 |
| 均值回歸 | 70-90% | 0.5-1.5 | 5-15% | 中-高 |
| 動量策略 | 55-65% | 0.8-2.0 | 10-25% | 低-中 |
| 套利策略 | 85-95% | 2.0-5.0 | < 5% | 高 |
| 高頻策略 | 50-60% | 1.0-3.0 | < 10% | 極高 |

**使用說明**：
- 如果報告中的數據超出參考範圍 → 檢查原因
- 如果數據在範圍內 → 可能合理，但仍需驗證

---

## 四、數據驗證腳本模板

### 4.1 基本數據驗證腳本

```python
"""
數據驗證腳本 - 基本檢查
用途：快速檢查策略回測數據的合理性
"""

import pandas as pd
import numpy as np

class DataValidator:
    """數據驗證器"""

    def __init__(self, df):
        """
        初始化驗證器

        Parameters:
        -----------
        df : pd.DataFrame
            交易數據，必須包含以下列：
            - 'entry_date' : 進場日期
            - 'exit_date' : 出場日期
            - 'pnl' : 盈虧（絕對金額）
        """
        self.df = df.copy()
        self.errors = []
        self.warnings = []

    def validate_win_rate(self, expected_range=(0.3, 0.7)):
        """
        驗證勝率

        Parameters:
        -----------
        expected_range : tuple
            預期勝率範圍（默認 30-70%）
        """
        if 'pnl' not in self.df.columns:
            self.errors.append("缺少 'pnl' 列")
            return False

        win_rate = (self.df['pnl'] > 0).mean()

        if win_rate > 0.95:
            self.errors.append(f"勝率過高：{win_rate:.1%}（>95%）")
        elif win_rate < 0.2:
            self.errors.append(f"勝率過低：{win_rate:.1%}（<20%）")
        elif not (expected_range[0] <= win_rate <= expected_range[1]):
            self.warnings.append(f"勝率超出預期範圍：{win_rate:.1%}（預期 {expected_range[0]:.1%}-{expected_range[1]:.1%}）")

        return len(self.errors) == 0

    def validate_profit_factor(self):
        """驗證獲利因子"""
        if 'pnl' not in self.df.columns:
            self.errors.append("缺少 'pnl' 列")
            return False

        total_profit = self.df[self.df['pnl'] > 0]['pnl'].sum()
        total_loss = abs(self.df[self.df['pnl'] < 0]['pnl'].sum())

        if total_loss == 0:
            self.errors.append("無虧損交易，獲利因子無法計算")
            return False

        profit_factor = total_profit / total_loss

        if profit_factor == 0:
            self.errors.append("獲利因子 = 0，計算錯誤")
        elif profit_factor > 5:
            self.warnings.append(f"獲利因子過高：{profit_factor:.2f}（>5）")

        return len(self.errors) == 0

    def validate_annual_return(self, total_days=None):
        """
        驗證年化收益率

        Parameters:
        -----------
        total_days : int or None
            總天數，如果為 None 則從數據中計算
        """
        if total_days is None:
            if 'entry_date' not in self.df.columns or 'exit_date' not in self.df.columns:
                self.warnings.append("無法計算年化收益率（缺少日期列）")
                return True

            total_days = (self.df['exit_date'].max() - self.df['entry_date'].min()).days

        total_pnl = self.df['pnl'].sum()
        initial_capital = 100000  # 假設初始資金

        annual_return = (1 + total_pnl / initial_capital) ** (365 / total_days) - 1

        if annual_return > 10:  # 1000%
            self.errors.append(f"年化收益率過高：{annual_return:.1%}（>1000%）")

        return len(self.errors) == 0

    def validate_trade_count(self, min_trades=10, max_trades_per_year=10000):
        """
        驗證交易次數

        Parameters:
        -----------
        min_trades : int
            最小交易次數
        max_trades_per_year : int
            每年最大交易次數
        """
        trade_count = len(self.df)

        if trade_count < min_trades:
            self.warnings.append(f"交易次數過少：{trade_count}（< {min_trades}）")

        # 計算每年交易次數
        if 'entry_date' in self.df.columns and 'exit_date' in self.df.columns:
            total_days = (self.df['exit_date'].max() - self.df['entry_date'].min()).days
            years = total_days / 365
            trades_per_year = trade_count / years if years > 0 else 0

            if trades_per_year > max_trades_per_year:
                self.warnings.append(f"每年交易次數過多：{trades_per_year:.0f}（> {max_trades_per_year}）")

        return len(self.errors) == 0

    def validate_max_drawdown(self, equity_curve=None):
        """
        驗證最大回撤

        Parameters:
        -----------
        equity_curve : pd.Series or None
            權益曲線，如果為 None 則從交易數據計算
        """
        if equity_curve is None:
            self.warnings.append("無法驗證最大回撤（缺少權益曲線）")
            return True

        # 計算最大回撤
        rolling_max = equity_curve.expanding().max()
        drawdown = (equity_curve - rolling_max) / rolling_max
        max_drawdown = drawdown.min()

        # 檢查是否過小
        win_rate = (self.df['pnl'] > 0).mean()
        if abs(max_drawdown) < 0.01 and win_rate > 0.8:
            self.errors.append(f"最大回撤過小且勝率高：{max_drawdown:.2%}（可能數據洩漏）")

        return len(self.errors) == 0

    def run_all_checks(self):
        """執行所有檢查"""
        self.validate_win_rate()
        self.validate_profit_factor()
        self.validate_annual_return()
        self.validate_trade_count()

        # 輸出結果
        print("=" * 50)
        print("數據驗證報告")
        print("=" * 50)

        if self.errors:
            print("\n❌ 錯誤：")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print("\n⚠️  警告：")
            for warning in self.warnings:
                print(f"  - {warning}")

        if not self.errors and not self.warnings:
            print("\n✅ 所有檢查通過")

        print("=" * 50)

        return len(self.errors) == 0


# 使用示例
if __name__ == "__main__":
    import pandas as pd
    from datetime import datetime, timedelta

    # 創建測試數據
    np.random.seed(42)
    n_trades = 50

    df = pd.DataFrame({
        'entry_date': [datetime(2020, 1, 1) + timedelta(days=i*7) for i in range(n_trades)],
        'exit_date': [datetime(2020, 1, 1) + timedelta(days=i*7 + 5) for i in range(n_trades)],
        'pnl': np.random.randn(n_trades) * 1000
    })

    # 執行驗證
    validator = DataValidator(df)
    validator.run_all_checks()
```

### 4.2 使用說明

**步驟 1：準備交易數據**
```python
df = pd.DataFrame({
    'entry_date': [...],  # 進場日期
    'exit_date': [...],   # 出場日期
    'pnl': [...]          # 盈虧
})
```

**步驟 2：創建驗證器**
```python
validator = DataValidator(df)
```

**步驟 3：執行檢查**
```python
validator.run_all_checks()
```

**步驟 4：處理結果**
- 如果有錯誤（❌）：立即停止，檢查數據
- 如果有警告（⚠️）：檢查是否合理
- 如果全部通過（✅）：可以繼續分析

---

## 五、實施步驟

### 5.1 文件更新
- [ ] 保存本文檔到 `workspace/kanban/outputs/data-validation-sop-v2.md`
- [ ] 保存腳本到 `workspace/tools/data_validator.py`
- [ ] 更新 `memory/topics/research-standards.md`

### 5.2 整合到研究流程
- [ ] 所有策略研究必須執行數據驗證
- [ ] 研究報告必須包含數據驗證章節
- [ ] 研究審查時檢查驗證步驟

### 5.3 自動化檢查
- [ ] 將腳本整合到回測流程
- [ ] 自動觸發數據驗證
- [ ] 自動生成驗證報告

---

## 六、總結

### 6.1 核心原則
1. **可疑數據立即停止** - 先驗證再分析
2. **事前假設** - 在分析前預先定義合理範圍
3. **邊界檢查** - 檢查是否超出合理範圍
4. **雙重驗證** - 用另一種方法交叉檢查
5. **紅隊測試** - 從對手角度攻擊自己的結論

### 6.2 快速檢查清單

**在查看任何策略報告前，快速檢查以下指標**：
- [ ] 勝率是否在 20-95% 之間？
- [ ] Sharpe 是否 < 3？
- [ ] 最大回撤是否 > 1%（如果勝率高）？
- [ ] 獲利因子是否 ≠ 0 且 ≠ ∞？
- [ ] 年化收益是否 < 1000%？
- [ ] 交易次數是否 > 10？

**如果任何一項不符合 → 立即停止，要求數據驗證**

### 6.3 下一步行動
- ✅ 立即應用到所有策略研究
- ✅ 將腳本整合到回測流程
- ✅ 建立數據驗證檢查點

---

**文檔版本**：v2.0
**創建日期**：2026-03-01
**創建者**：Charlie + Mentor
**狀態**：⏳ 等待實施
