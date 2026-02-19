# 每日避險比例指標 (DHRI) - 簡化版實務指南

> 基於 t005 報告的理論框架，簡化為每日可用的單一指標

---

## 📊 DHRI (Daily Hedge Ratio Indicator)

**核心思想：** 每日只看一個數值（0-100），立即知道今日適合的避險比例。

---

## 快速查詢表

| DHRI | 避險比例 | 市場狀況 | 建議行動 |
|------|-----------|----------|----------|
| **0-20** | 0-5% | 極度平靜 | 無需避險或微量 VIX Call |
| **21-40** | 5-10% | 平靜 | 輕度 VIX Call 避險 |
| **41-60** | 10-20% | 正常波動 | 標準避險（VIX Call 或遠期 Put） |
| **61-80** | 20-30% | 波動上升 | 增加避險（近月 Put 或 VIX Call） |
| **81-100** | 30-50% | 恐慌 | 激進避險（ITM Put 或高比例 VIX Call） |

---

## DHRI 計算公式（三種簡化方法）

### 方法一：快速版（僅需 VIX + 真實波動率）

```python
def calculate_dhri_simple(vix: float, realized_vol: float = None) -> int:
    """
    簡化版 DHRI 計算（僅需 VIX 和真實波動率）

    Parameters:
    -----------
    vix : float
        當前 VIX 水平
    realized_vol : float
        真實波動率（可選，默認使用 VIX）

    Returns:
    --------
    int
        DHRI 值 (0-100)
    """
    if realized_vol is None:
        realized_vol = vix

    # VIX 分量 (60% 權重)
    vix_score = normalize_vix(vix) * 60

    # 真實波動率分量 (40% 權重)
    vol_score = normalize_volatility(realized_vol) * 40

    # 總分
    dhri = int(vix_score + vol_score)

    return min(100, max(0, dhri))

def normalize_vix(vix: float) -> float:
    """VIX 正規化到 0-100"""
    if vix < 12:
        return vix / 12 * 15  # 0-15
    elif vix < 20:
        return 15 + (vix - 12) / 8 * 30  # 15-45
    elif vix < 30:
        return 45 + (vix - 20) / 10 * 30  # 45-75
    else:
        return 75 + min(25, (vix - 30) / 20 * 25)  # 75-100

def normalize_volatility(vol: float) -> float:
    """波動率正規化到 0-100"""
    if vol < 10:
        return vol / 10 * 15
    elif vol < 20:
        return 15 + (vol - 10) / 10 * 30
    elif vol < 40:
        return 45 + (vol - 20) / 20 * 30
    else:
        return 75 + min(25, (vol - 40) / 30 * 25)
```

**每日操作步驟：**
1. 收盤後獲取 VIX（免費數據源：Yahoo Finance, TradingView）
2. （可選）計算過去 20 日真實波動率
3. 代入公式 → 得到 DHRI
4. 查詢表調整避險比例

---

### 方法二：精確版（加入趨勢信號）

```python
def calculate_dhri_precise(vix: float,
                       realized_vol: float,
                       trend_strength: float = 50,
                       regime: str = 'neutral') -> int:
    """
    精確版 DHRI 計算（加入趨勢和市場狀態）

    Parameters:
    -----------
    vix : float
        當前 VIX 水平
    realized_vol : float
        真實波動率
    trend_strength : float
        趨勢強度 (0-100, 50 = 中性)
    regime : str
        市場狀態 ('bull', 'bear', 'neutral')

    Returns:
    --------
    int
        DHRI 值 (0-100)
    """
    # 基礎分 (VIX + 波動率)
    base_score = calculate_dhri_simple(vix, realized_vol)

    # 趨勢調整 (最多 +/- 15 分)
    trend_adjust = 0
    if trend_strength > 60:  # 強趨勢
        trend_adjust = -10  # 降低避險
    elif trend_strength < 40:  # 趨勢不明
        trend_adjust = 10  # 增加避險

    # 市場狀態調整 (最多 +/- 10 分)
    regime_adjust = 0
    if regime == 'bull':
        regime_adjust = -5
    elif regime == 'bear':
        regime_adjust = 10

    # 最終得分
    dhri = int(base_score + trend_adjust + regime_adjust)

    return min(100, max(0, dhri))
```

**每日操作步驟：**
1. 收盤後獲取 VIX 和真實波動率
2. 計算趨勢強度（如使用趨勢強度評分系統 t001）
3. 判斷市場狀態（使用 Regime Detection r001）
4. 代入公式 → 得到 DHRI
5. 查詢表調整避險比例

---

### 方法三：超簡版（僅需 VIX）

```python
def calculate_dhri_ultra_simple(vix: float) -> int:
    """
    超簡版 DHRI 計算（僅需 VIX）

    Parameters:
    -----------
    vix : float
        當前 VIX 水平

    Returns:
    --------
    int
        DHRI 值 (0-100)
    """
    # 簡化映射表
    if vix < 12:
        return int(vix / 12 * 20)
    elif vix < 15:
        return int(20 + (vix - 12) / 3 * 15)
    elif vix < 20:
        return int(35 + (vix - 15) / 5 * 20)
    elif vix < 25:
        return int(55 + (vix - 20) / 5 * 20)
    elif vix < 30:
        return int(75 + (vix - 25) / 5 * 15)
    else:
        return int(90 + min(10, (vix - 30) / 10 * 10))
```

**VIX → DHRI 快速查詢：**

| VIX | DHRI | 避險比例 | 狀態 |
|------|-------|----------|------|
| 10 | 17 | 0-5% | 極度平靜 |
| 12 | 20 | 5% | 平靜 |
| 15 | 35 | 5-10% | 平靜上升 |
| 20 | 55 | 10-20% | 正常 |
| 25 | 75 | 20-30% | 波動上升 |
| 30 | 90 | 30-50% | 恐慌 |
| 35+ | 100 | 50% | 極度恐慌 |

---

## 實務操作指南

### 每日收盤後操作流程

**步驟 1：獲取數據（2 分鐘）**
```
1. 打開 Yahoo Finance 或 TradingView
2. 查詢 VIX 指數（免費，實時）
3. （可選）查看過去 20 日波動率
```

**步驟 2：計算 DHRI（1 分鐘）**
```
使用超簡版：
DHRI = f(VIX)

或使用快速版：
DHRI = 0.6 × VIX分數 + 0.4 × 波動率分數
```

**步驟 3：查詢避險比例（30 秒）**
```
根據 DHRI 查快速查詢表，得到避險比例
```

**步驟 4：調整部位（根據時間）**

**如果使用 VIX Call（推薦）：**
- 低避險比例（<10%）：購買 OTM 10% VIX Call
- 中避險比例（10-20%）：購買 OTM 5% VIX Call
- 高避險比例（>20%）：購買 ATM 或 ITM VIX Call

**如果使用 Put（成本較高）：**
- 低避險比例：每月購買一次 30 天 OTM Put
- 高避險比例：每月購買兩次（15 天 + 15 天）

---

## 避險工具推薦（按 DHRI 級別）

### DHRI 0-20（無需避險）
- **無需任何操作**
- 如有心理壓力，可購買微量 VIX Call（1-2% 組合價值）

### DHRI 21-40（輕度避險）
- **推薦：** VIX Call OTM 10%
- **原因：** 成本低，流動性好
- **到期日：** 1-2 個月
- **比例：** 5-10% 組合價值

### DHRI 41-60（標準避險）
- **推薦：** VIX Call OTM 5% 或 Put OTM 10%
- **原因：** 平衡成本和保護
- **到期日：** 1 個月
- **比例：** 10-20% 組合價值

### DHRI 61-80（增加避險）
- **推薦：** Put OTM 5% 或 VIX Call ATM
- **原因：** 保護力強
- **到期日：** 1 個月
- **比例：** 20-30% 組合價值

### DHRI 81-100（激進避險）
- **推薦：** Put ATM 或 ITM
- **原因：** 最大保護
- **到期日：** 2-4 週（短期）
- **比例：** 30-50% 組合價值

---

## Python 富現（可直接使用）

```python
import pandas as pd
import numpy as np
from typing import Dict, Optional

class DailyHedgeRatioIndicator:
    """
    每日避險比例指標 (DHRI)

    簡化的實務工具，根據市場狀況快速計算避險比例
    """

    def __init__(self, method: str = 'simple'):
        """
        初始化 DHRI 計算器

        Parameters:
        -----------
        method : str
            計算方法 ('ultra_simple', 'simple', 'precise')
        """
        self.method = method

    def calculate(self,
                 vix: float,
                 realized_vol: Optional[float] = None,
                 trend_strength: Optional[float] = None,
                 regime: Optional[str] = None) -> Dict:
        """
        計算 DHRI

        Parameters:
        -----------
        vix : float
            當前 VIX 水平
        realized_vol : float, optional
            真實波動率（可選）
        trend_strength : float, optional
            趨勢強度 (0-100)
        regime : str, optional
            市場狀態 ('bull', 'bear', 'neutral')

        Returns:
        --------
        dict
            DHRI 和建議
        """
        # 根據方法計算 DHRI
        if self.method == 'ultra_simple':
            dhri = self._calculate_ultra_simple(vix)
        elif self.method == 'simple':
            dhri = self._calculate_simple(vix, realized_vol)
        elif self.method == 'precise':
            dhri = self._calculate_precise(vix, realized_vol, trend_strength, regime)
        else:
            raise ValueError(f"未知方法: {self.method}")

        # 計算避險比例
        hedge_ratio = self._dhri_to_hedge_ratio(dhri)

        # 獲取建議
        recommendation = self._get_recommendation(dhri, hedge_ratio)

        return {
            'dhri': dhri,
            'hedge_ratio': hedge_ratio,
            'hedge_ratio_pct': hedge_ratio * 100,
            'recommendation': recommendation,
            'vix': vix,
            'method': self.method
        }

    def _calculate_ultra_simple(self, vix: float) -> int:
        """超簡版計算（僅需 VIX）"""
        if vix < 12:
            return int(vix / 12 * 20)
        elif vix < 15:
            return int(20 + (vix - 12) / 3 * 15)
        elif vix < 20:
            return int(35 + (vix - 15) / 5 * 20)
        elif vix < 25:
            return int(55 + (vix - 20) / 5 * 20)
        elif vix < 30:
            return int(75 + (vix - 25) / 5 * 15)
        else:
            return int(90 + min(10, (vix - 30) / 10 * 10))

    def _calculate_simple(self, vix: float, realized_vol: Optional[float]) -> int:
        """簡化版計算（VIX + 波動率）"""
        if realized_vol is None:
            realized_vol = vix

        vix_score = self._normalize_vix(vix) * 60
        vol_score = self._normalize_volatility(realized_vol) * 40

        dhri = int(vix_score + vol_score)
        return min(100, max(0, dhri))

    def _calculate_precise(self,
                        vix: float,
                        realized_vol: Optional[float],
                        trend_strength: Optional[float],
                        regime: Optional[str]) -> int:
        """精確版計算（加入趨勢和市場狀態）"""
        # 基礎分
        base_score = self._calculate_simple(vix, realized_vol)

        # 趨勢調整
        trend_adjust = 0
        if trend_strength is not None:
            if trend_strength > 60:
                trend_adjust = -10
            elif trend_strength < 40:
                trend_adjust = 10

        # 市場狀態調整
        regime_adjust = 0
        if regime is not None:
            if regime == 'bull':
                regime_adjust = -5
            elif regime == 'bear':
                regime_adjust = 10

        dhri = int(base_score + trend_adjust + regime_adjust)
        return min(100, max(0, dhri))

    def _normalize_vix(self, vix: float) -> float:
        """VIX 正規化到 0-100"""
        if vix < 12:
            return vix / 12 * 15
        elif vix < 20:
            return 15 + (vix - 12) / 8 * 30
        elif vix < 30:
            return 45 + (vix - 20) / 10 * 30
        else:
            return 75 + min(25, (vix - 30) / 20 * 25)

    def _normalize_volatility(self, vol: float) -> float:
        """波動率正規化到 0-100"""
        if vol < 10:
            return vol / 10 * 15
        elif vol < 20:
            return 15 + (vol - 10) / 10 * 30
        elif vol < 40:
            return 45 + (vol - 20) / 20 * 30
        else:
            return 75 + min(25, (vol - 40) / 30 * 25)

    def _dhri_to_hedge_ratio(self, dhri: int) -> float:
        """DHRI 轉換為避險比例"""
        if dhri <= 20:
            return dhri / 20 * 0.05  # 0-5%
        elif dhri <= 40:
            return 0.05 + (dhri - 20) / 20 * 0.05  # 5-10%
        elif dhri <= 60:
            return 0.10 + (dhri - 40) / 20 * 0.10  # 10-20%
        elif dhri <= 80:
            return 0.20 + (dhri - 60) / 20 * 0.10  # 20-30%
        else:
            return 0.30 + min(0.20, (dhri - 80) / 20 * 0.20)  # 30-50%

    def _get_recommendation(self, dhri: int, hedge_ratio: float) -> Dict:
        """獲取建議"""
        if dhri <= 20:
            level = '極度平靜'
            action = '無需避險或微量避險'
            hedge_tool = '無或微量 VIX Call'
        elif dhri <= 40:
            level = '平靜'
            action = '輕度避險'
            hedge_tool = 'VIX Call OTM 10%'
        elif dhri <= 60:
            level = '正常波動'
            action = '標準避險'
            hedge_tool = 'VIX Call OTM 5% 或 Put OTM 10%'
        elif dhri <= 80:
            level = '波動上升'
            action = '增加避險'
            hedge_tool = 'Put OTM 5% 或 VIX Call ATM'
        else:
            level = '恐慌'
            action = '激進避險'
            hedge_tool = 'Put ATM 或 ITM'

        return {
            'level': level,
            'action': action,
            'hedge_tool': hedge_tool,
            'hedge_ratio_pct': hedge_ratio * 100
        }

    def calculate_daily_report(self, vix: float, **kwargs) -> str:
        """
        生成每日報告

        Parameters:
        -----------
        vix : float
            當前 VIX 水平
        **kwargs : dict
            其他參數

        Returns:
        --------
        str
            每日報告
        """
        result = self.calculate(vix, **kwargs)

        report = f"""
========================================
每日避險指標報告
========================================
DHRI: {result['dhri']}/100
避險比例: {result['hedge_ratio_pct']:.1f}%
市場狀態: {result['recommendation']['level']}
建議行動: {result['recommendation']['action']}
避險工具: {result['recommendation']['hedge_tool']}

VIX: {result['vix']:.2f}
計算方法: {result['method']}
========================================
"""
        return report


# 使用範例
if __name__ == "__main__":
    # 初始化
    dhri = DailyHedgeRatioIndicator(method='simple')

    # 示例：VIX = 18.5
    result = dhri.calculate(vix=18.5, realized_vol=17.2)
    print(result)

    # 生成每日報告
    print(dhri.calculate_daily_report(vix=18.5, realized_vol=17.2))
```

---

## 常見問題

### Q1: 每天調整避險成本太高，怎麼辦？
**A:** 使用 VIX Call 而非 Put，因為：
- VIX Call 成本較低
- 流動性更好
- 可以選擇價外合約降低成本

### Q2: DHRI 和直接使用 VIX 有什麼區別？
**A:** DHRI 的優勢：
- 考慮真實波動率（不僅是預期波動率）
- 可選擇加入趨勢和市場狀態
- 提供明確的避險比例建議

### Q3: 什麼時候使用 Put，什麼時候使用 VIX Call？
**A:**
- **DHRI < 40**: 使用 VIX Call（成本低）
- **DHRI 40-60**: 兩者皆可（根據流動性和成本選擇）
- **DHRI > 60**: 優先使用 Put（保護力強）

### Q4: 這個系統適合什麼樣的投資者？
**A:**
- **日內交易者**: 使用超簡版，僅需 VIX
- **波段交易者**: 使用簡化版，加入真實波動率
- **長期投資者**: 使用精確版，加入趨勢和市場狀態

---

## 總結

**DHRI (Daily Hedge Ratio Indicator)** 將 t005 報告的複雜理論簡化為：

1. **單一指標** (0-100)
2. **快速查詢** (30 秒)
3. **每日可執行** (3 分鐘完成)

**核心優勢：**
- ✅ 實務導向：不需要複雜計算
- ✅ 數據簡單：僅需 VIX（可選波動率）
- ✅ 行動明確：一個數值決定避險比例
- ✅ 靈活可調：三種方法適應不同需求

**下一步：**
1. 根據你的風險偏好選擇方法（ultra_simple / simple / precise）
2. 每日收盤後執行 DHRI 計算
3. 根據建議調整避險部位
4. 定期回顧和優化參數

---

**參考：**
- t005-tail-hedge.html（完整理論框架）
- t001-trend-strength.md（趨勢強度評分）
- r001-model-selection.md（市場狀態檢測）
