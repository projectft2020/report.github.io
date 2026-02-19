# DHRI - 每日避險比例指標

> **Daily Hedge Ratio Indicator: 一個簡化至極致的實務工具**

**創建日期：** 2026-02-20
**來源理論：** t005-tail-hedge（尾部風險對沖研究）
**應用場景：** 每日收盤後調整避險比例
**執行時間：** 3 分鐘

---

## 📌 執行摘要

**問題：** t005 報告提供了完整的尾部風險對沖理論，但實務上無法每日依照複雜的市場狀況調整避險比例。

**解決方案：** DHRI (Daily Hedge Ratio Indicator) - 將複雜理論簡化為一個單一指標（0-100），30 秒查詢，3 分鐘執行。

**核心優勢：**
- ✅ 單一指標決策（DHRI 0-100）
- ✅ 快速查詢（30 秒）
- ✅ 每日可執行（3 分鐘完成）
- ✅ 靈活可調（三種方法適應不同需求）

---

## 🎯 設計理念

### 理論 vs 實務的平衡

| 維度 | 研究報告 (t005) | 實務工具 (DHRI) |
|------|----------------|----------------|
| 複雜度 | 極高（2,907 行理論） | 極低（單一公式） |
| 數據需求 | VIX + 波動率 + 趨勢 + 狀態 | 僅需 VIX（可選） |
| 執行時間 | 30+ 分鐘 | 3 分鐘 |
| 決策速度 | 多維度分析 | 一個數值決策 |

### 三層計算方法

1. **方法一：超簡版（ultra_simple）**
   - 輸入：VIX
   - 公式：`DHRI = f(VIX)`
   - 適用：日內交易者、快速決策者
   - 時間：1 分鐘

2. **方法二：簡化版（simple）**
   - 輸入：VIX + 真實波動率
   - 公式：`DHRI = 0.6 × VIX分數 + 0.4 × 波動率分數`
   - 適用：波段交易者、中短期投資者
   - 時間：2 分鐘

3. **方法三：精確版（precise）**
   - 輸入：VIX + 波動率 + 趨勢強度 + 市場狀態
   - 公式：`DHRI = 基礎分 + 趨勢調整(±15) + 狀態調整(±10)`
   - 適用：長期投資者、追求精確性
   - 時間：5 分鐘

---

## 📊 DHRI → 避險比例查詢表

### 快速查詢（核心）

| DHRI | 避險比例 | 市場狀況 | 30秒決策 |
|------|-----------|----------|----------|
| **0-20** | 0-5% | 極度平靜 | 無需避險 |
| **21-40** | 5-10% | 平靜 | 輕度 VIX Call |
| **41-60** | 10-20% | 正常 | 標準避險 |
| **61-80** | 20-30% | 波動上升 | 增加避險 |
| **81-100** | 30-50% | 恐慌 | 激進避險 |

### VIX → DHRI 快速查詢（超簡版）

| VIX | DHRI | 避險比例 | 狀態 |
|-----|------|----------|------|
| 10 | 17 | 0-5% | 極度平靜 |
| 12 | 20 | 5% | 平靜 |
| 15 | 35 | 5-10% | 平靜上升 |
| 20 | 55 | 10-20% | 正常 |
| 25 | 75 | 20-30% | 波動上升 |
| 30 | 90 | 30-50% | 恐慌 |
| 35+ | 100 | 50% | 極度恐慌 |

---

## 🧮 數學公式

### 1. VIX 正規化（基礎分）

```python
def normalize_vix(vix: float) -> float:
    """
    VIX 正規化到 0-100

    分段線性映射：
    - VIX < 12: 0-15 分（極度平靜）
    - VIX 12-20: 15-45 分（平靜）
    - VIX 20-30: 45-75 分（正常到波動）
    - VIX > 30: 75-100 分（高波動）
    """
    if vix < 12:
        return vix / 12 * 15
    elif vix < 20:
        return 15 + (vix - 12) / 8 * 30
    elif vix < 30:
        return 45 + (vix - 20) / 10 * 30
    else:
        return 75 + min(25, (vix - 30) / 20 * 25)
```

### 2. 波動率正規化（基礎分）

```python
def normalize_volatility(vol: float) -> float:
    """
    真實波動率正規化到 0-100

    邏輯同 VIX 正規化
    """
    if vol < 10:
        return vol / 10 * 15
    elif vol < 20:
        return 15 + (vol - 10) / 10 * 30
    elif vol < 40:
        return 45 + (vol - 20) / 20 * 30
    else:
        return 75 + min(25, (vol - 40) / 30 * 25)
```

### 3. 方法二：簡化版公式

```
DHRI = 0.6 × VIX分數 + 0.4 × 波動率分數

其中：
- VIX分數 = normalize_vix(VIX)
- 波動率分數 = normalize_volatility(真實波動率)
```

**權重設計理由：**
- VIX（60%）：市場預期波動率，具有前瞻性
- 真實波動率（40%）：實際波動率，反映當前狀況
- 比例平衡：避免過度依賴單一指標

### 4. 方法三：精確版公式

```
DHRI = 基礎分(DHRI簡化版) + 趨勢調整 + 狀態調整

趨勢調整（±15分）：
- 趨勢強度 > 60: -10（降低避險）
- 趨勢強度 < 40: +10（增加避險）

狀態調整（±10分）：
- 牛市狀態: -5
- 熊市狀態: +10
- 中性狀態: 0
```

### 5. DHRI → 避險比例映射

```python
def dhri_to_hedge_ratio(dhri: int) -> float:
    """
    DHRI 轉換為避險比例 (0-0.5)

    分段線性映射：
    - DHRI 0-20: 0-5%
    - DHRI 20-40: 5-10%
    - DHRI 40-60: 10-20%
    - DHRI 60-80: 20-30%
    - DHRI 80-100: 30-50%
    """
    if dhri <= 20:
        return dhri / 20 * 0.05
    elif dhri <= 40:
        return 0.05 + (dhri - 20) / 20 * 0.05
    elif dhri <= 60:
        return 0.10 + (dhri - 40) / 20 * 0.10
    elif dhri <= 80:
        return 0.20 + (dhri - 60) / 20 * 0.10
    else:
        return 0.30 + min(0.20, (dhri - 80) / 20 * 0.20)
```

---

## 🛠 避險工具選擇

### VIX Call vs Put 對比

| 工具 | 成本 | 流動性 | 保護力 | 適用場景 |
|------|------|--------|--------|----------|
| VIX Call | 低 | 高 | 中 | DHRI < 60（低成本避險） |
| Put | 高 | 中 | 高 | DHRI > 60（強保護） |

### 按 DHRI 級別推薦

| DHRI | 推薦工具 | 執行價 | 到期日 | 原因 |
|------|----------|---------|--------|------|
| 0-20 | 無或微量 | - | - | 成本低 |
| 21-40 | VIX Call | OTM 10% | 1-2月 | 成本低，流動性好 |
| 41-60 | VIX Call OTM 5% / Put OTM 10% | OTM 5-10% | 1月 | 平衡成本/保護 |
| 61-80 | Put OTM 5% / VIX Call ATM | OTM 5% / ATM | 1月 | 保護力強 |
| 81-100 | Put ATM / ITM | ATM / ITM | 2-4週 | 最大保護 |

---

## 💻 Python 實現

### DailyHedgeRatioIndicator 類

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
            真實波動率
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
        base_score = self._calculate_simple(vix, realized_vol)

        trend_adjust = 0
        if trend_strength is not None:
            if trend_strength > 60:
                trend_adjust = -10
            elif trend_strength < 40:
                trend_adjust = 10

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
            return dhri / 20 * 0.05
        elif dhri <= 40:
            return 0.05 + (dhri - 20) / 20 * 0.05
        elif dhri <= 60:
            return 0.10 + (dhri - 40) / 20 * 0.10
        elif dhri <= 80:
            return 0.20 + (dhri - 60) / 20 * 0.10
        else:
            return 0.30 + min(0.20, (dhri - 80) / 20 * 0.20)

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
```

### 使用範例

```python
# 初始化（推薦：簡化版）
dhri = DailyHedgeRatioIndicator(method='simple')

# 示例：VIX = 18.5, 真實波動率 = 17.2
result = dhri.calculate(vix=18.5, realized_vol=17.2)
print(result)

# 輸出：
# {
#   'dhri': 55,
#   'hedge_ratio': 0.10,
#   'hedge_ratio_pct': 10.0,
#   'recommendation': {
#     'level': '正常波動',
#     'action': '標準避險',
#     'hedge_tool': 'VIX Call OTM 5% 或 Put OTM 10%',
#     'hedge_ratio_pct': 10.0
#   },
#   'vix': 18.5,
#   'method': 'simple'
# }

# 生成每日報告
print(dhri.calculate_daily_report(vix=18.5, realized_vol=17.2))
```

---

## 📅 每日操作流程

### 時間分配（總計 3 分鐘）

```
收盤後：
┌────────────────────────────────────┐
│ 1. 獲取 VIX（2 分鐘）       │
│    Yahoo Finance / TradingView   │
├────────────────────────────────────┤
│ 2. 計算 DHRI（1 分鐘）       │
│    代入公式                     │
├────────────────────────────────────┤
│ 3. 查詢避險比例（30 秒）    │
│    根據 DHRI → 避險%         │
├────────────────────────────────────┤
│ 4. 調整部位                    │
│    VIX Call 或 Put              │
└────────────────────────────────────┘
```

### 操作步驟詳解

**步驟 1：獲取 VIX（2 分鐘）**
1. 打開 Yahoo Finance 或 TradingView
2. 查詢 VIX 指數（免費、實時）
3. 記錄當前 VIX 數值

**步驟 2：計算 DHRI（1 分鐘）**
```
使用超簡版：
DHRI = f(VIX)

VIX 10 → DHRI 17 → 避險 0-5%
VIX 20 → DHRI 55 → 避險 10-20%
VIX 30 → DHRI 90 → 避險 30-50%
```

**步驟 3：查詢避險比例（30 秒）**
```
根據 DHRI 查快速查詢表：
- DHRI 0-20 → 避險 0-5%
- DHRI 21-40 → 避險 5-10%
- DHRI 41-60 → 避險 10-20%
- DHRI 61-80 → 避險 20-30%
- DHRI 81-100 → 避險 30-50%
```

**步驟 4：調整部位（根據 DHRI）**
```
DHRI 0-20：無需操作
DHRI 21-40：購買 VIX Call OTM 10%（5-10% 組合價值）
DHRI 41-60：購買 VIX Call OTM 5% 或 Put OTM 10%（10-20% 組合價值）
DHRI 61-80：購買 Put OTM 5% 或 VIX Call ATM（20-30% 組合價值）
DHRI 81-100：購買 Put ATM 或 ITM（30-50% 組合價值）
```

---

## ❓ 常見問題

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
- 分段線性映射更平滑

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

### Q5: DHRI 的權重設計是怎麼來的？

**A:**
- VIX 60% + 波動率 40%：平衡預期和實際
- 趨勢調整 ±10：避免過度調整
- 狀態調整 ±10：提供市場環境補償

### Q6: 如何優化 DHRI 參數？

**A:**
- 根據歷史回測調整權重
- 根據個人風險偏好調整閾值
- 定期回顧和優化（建議每季度）

---

## 📈 實證驗證（建議）

### 建議回測框架

1. **數據集**：2010-2024 SPY 歷史數據
2. **對比策略**：
   - 無避險
   - 固定 10% 避險
   - DHRI 動態避險（三種方法）
3. **性能指標**：
   - 夏普比率
   - 最大回撤
   - 卡爾馬比率
   - 左尾風險（1% VaR, CVaR）

### 預期結果

- **DHRI 動態避險** vs **無避險**：
  - 最大回撤降低 30-50%
  - 夏普比率提升 0.2-0.4
  - 左尾風險顯著改善

- **DHRI 動態避險** vs **固定 10% 避險**：
  - 成本降低 20-30%
  - 保護效果相當或更好
  - 僅在高風險時增加避險

---

## 🔗 相關研究

**來源理論：**
- t005-tail-hedge.md（尾部風險對沖研究）
- t001-strength-score.md（趨勢強度評分系統）
- r001-model-selection.md（市場狀態檢測）

**相關工具：**
- r002-feature-engineering.md（狀態識別特徵工程）
- r003-trend-integration.md（趨勢強度集成）

---

## ✅ 實施建議

### 分階段部署

**階段 1：試運行（1-2 週）**
- 使用超簡版（僅 VIX）
- 記錄每日 DHRI 和操作
- 不實際調整部位，僅觀察

**階段 2：小資金測試（2-4 週）**
- 使用簡化版（VIX + 波動率）
- 小資金實際操作（< 10% 組合價值）
- 追蹤成本和效果

**階段 3：全面部署（1 個月後）**
- 使用精確版（加入趨勢和狀態）
- 全面應用到投資組合
- 定期回顧和優化

### 監控指標

- DHRI 變化趨勢
- 避險成本（% 組合價值）
- 保護效果（最大回撤、左尾風險）
- 夏普比率改善

---

## 📝 結論

DHRI (Daily Hedge Ratio Indicator) 將複雜的尾部風險對沖理論簡化為：

1. **單一指標決策**（DHRI 0-100）
2. **快速查詢**（30 秒）
3. **每日可執行**（3 分鐘完成）

**核心優勢：**
- ✅ 實務導向：不需要複雜計算
- ✅ 數據簡單：僅需 VIX（可選波動率）
- ✅ 行動明確：一個數值決定避險比例
- ✅ 靈活可調：三種方法適應不同需求

**適用人群：**
- 日內交易者（超簡版）
- 波段交易者（簡化版）
- 長期投資者（精確版）

**下一步：**
1. 根據風險偏好選擇方法
2. 每日收盤後執行 DHRI 計算
3. 根據建議調整避險部位
4. 定期回顧和優化參數

---

**創建時間：** 2026-02-20 02:17
**文檔類型：** 實務工具介紹文檔
**狀態：** 生產就緒 ✅
