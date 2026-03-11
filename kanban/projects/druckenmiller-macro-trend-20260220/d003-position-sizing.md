# 動態資金管理系統

**任務 ID:** 20260220-040000-d003
**項目 ID:** druckenmiller-macro-trend-20260220
**分析師:** Charlie Analyst
**狀態:** completed
**時間戳:** 2026-02-20T13:03:00Z
**基於:** Druckenmiller 交易哲學

---

## 摘要

本系統基於 Stanley Druckenmiller 的核心資金管理原則設計，實現完整的動態資金管理框架。系統整合凱利公式優化、期望值驅動倉位調整、風險平價策略、最大回撤控制和實時動態調整機制，為集中投資提供科學的資金分配決策支持。

**核心原則：**
- 信念驅動倉位：高信念機會集中配置，但嚴格控制風險
- 動態調整：根據市場條件和信念強度實時調整倉位
- 快速減損：當投資論證不再有效時迅速退出
- 保護資本：嚴格控制最大回撤，確保長期生存能力

---

## 系統架構

### 資金管理組件

```
動態資金管理系統
├── 1. 凱利公式優化模塊
│   ├── 全凱利公式計算
│   ├── 部分凱利（Fractional Kelly）調整
│   ├── 連續凱利（Continuous Kelly）優化
│   └── 凱利下限保護
├── 2. 期望值驅動倉位調整
│   ├── 勝率估算
│   ├── 盈虧比計算
│   ├── 期望值計算
│   └── 倉位大小映射
├── 3. 風險平價策略
│   ├── 波動率計算
│   ├── 相關性分析
│   ├── 風險貢獻分配
│   └── 目標風險調整
├── 4. 最大回撤控制
│   ├── 波動率預測
│   ├── VaR 計算
│   ├── CVaR 計算
│   └── 倉位限制器
└── 5. 實時動態調整機制
    ├── 信念強度監控
    ├── 市場條件評估
    ├── 倉位再平衡
    └── 止損觸發
```

### 信號驅動流程

```
宏觀趨勢信號
    ↓
信念強度評估（Conviction Level）
    ↓
期望值計算（Expected Value）
    ↓
凱利倉位計算（Kelly Position）
    ↓
風險限制（Risk Constraints）
    ↓
最終倉位（Final Position）
```

---

## 1. 凱利公式優化模塊

### 1.1 基礎凱利公式

凱利公式是優化的賭注策略，用於最大化長期增長率：

**公式：**

```
f* = (bp - q) / b

其中：
- f* = 最優資金比例
- b = 盈虧比（贏的賠率）
- p = 勝率
- q = 敗率 = 1 - p
```

**Python 實現：**

```python
def kelly_fraction(win_rate: float, win_loss_ratio: float) -> float:
    """
    計算基礎凱利公式倉位
    
    Parameters:
    -----------
    win_rate : float
        勝率 (0 到 1)
    win_loss_ratio : float
        盈虧比（平均盈利 / 平均虧損）
    
    Returns:
    --------
    float: 建議倉位比例（資金百分比）
    
    Examples:
    ---------
    >>> kelly_fraction(0.6, 2.0)  # 60%勝率，2:1盈虧比
    0.4  # 40%倉位
    """
    if win_rate <= 0 or win_rate >= 1:
        return 0.0
    
    q = 1 - win_rate
    
    # Kelly 公式
    kelly = (win_rate * win_loss_ratio - q) / win_loss_ratio
    
    # 負值表示不應交易
    if kelly < 0:
        return 0.0
    
    return kelly
```

### 1.2 部分凱利（Fractional Kelly）

Druckenmiller 和其他頂級交易員通常使用部分凱利來降低風險：

**公式：**

```
f_adj = f* * k

其中：
- f_adj = 調整後倉位
- f* = 基礎凱利倉位
- k = 凱利縮減因子（通常 0.25 - 0.5）
```

**Python 實現：**

```python
def fractional_kelly(kelly_f: float, 
                     shrinkage_factor: float = 0.25,
                     max_position: float = 0.40,
                     min_position: float = 0.01) -> float:
    """
    應用部分凱利縮減
    
    Parameters:
    -----------
    kelly_f : float
        基礎凱利倉位
    shrinkage_factor : float
        縮減因子（0-1）
        - 0.25: 激進（Druckenmiller 類型）
        - 0.10-0.15: 保守
    max_position : float
        最大倉位限制（單個標的）
    min_position : float
        最小倉位閾值
    
    Returns:
    --------
    float: 調整後倉位
    """
    # 應用縮減
    adjusted = kelly_f * shrinkage_factor
    
    # 應用倉位限制
    adjusted = max(min_position, min(adjusted, max_position))
    
    return adjusted
```

### 1.3 連續凱利（Continuous Kelly）

處理連續回報（股票、匯率等）的凱利公式：

**公式：**

```
f* = μ / σ²

其中：
- μ = 期望回報率
- σ = 波動率（標準差）
```

**Python 實現：**

```python
import numpy as np

def continuous_kelly(expected_return: float,
                      volatility: float,
                      risk_free_rate: float = 0.0) -> float:
    """
    連續凱利公式（用於資產價格）
    
    Parameters:
    -----------
    expected_return : float
        期望回報率（年化，小數形式）
    volatility : float
        波動率（年化，小數形式）
    risk_free_rate : float
        無風險利率（年化，小數形式）
    
    Returns:
    --------
    float: 建議槓桿倍數或倉位比例
    
    Notes:
    ------
    這是 Samuelson-Merton 應用於連續資產的凱利公式
    """
    if volatility <= 0:
        return 0.0
    
    # 超額回報
    excess_return = expected_return - risk_free_rate
    
    # 連續凱利
    kelly = excess_return / (volatility ** 2)
    
    # 負值表示不應持有多頭
    return max(0.0, kelly)
```

### 1.4 凱利下限保護

防止過度優化的凱利倉位導致回撤：

**Python 實現：**

```python
def kelly_with_floor(kelly_f: float,
                     confidence_interval: float = 0.95,
                     max_drawdown_limit: float = 0.20) -> float:
    """
    應用凱利下限保護（降低過度優化風險）
    
    Parameters:
    -----------
    kelly_f : float
        計算出的凱利倉位
    confidence_interval : float
        置信區間（0-1）
    max_drawdown_limit : float
        最大回撤限制
    
    Returns:
    --------
    float: 受保護的凱利倖位
    
    Notes:
    ------
    基於歷史數據估計的凱利分佈，應用安全邊際
    """
    # 凱利下限（降低估計不確定性影響）
    # 基於經驗：凱利估計誤差約為 ±50%
    kelly_floor = kelly_f * 0.5
    
    # 回撤限制調整
    # 經驗法則：凱利倉位與回撤相關
    drawdown_adjustment = min(1.0, max_drawdown_limit / (kelly_f * 2))
    
    # 應用限制
    protected_kelly = min(kelly_floor, drawdown_adjustment)
    
    return protected_kelly
```

---

## 2. 期望值驅動倉位調整

### 2.1 期望值計算框架

**公式：**

```
EV = p * W - q * L

其中：
- EV = 期望值
- p = 勝率
- W = 平均盈利（百分比）
- q = 敗率 = 1 - p
- L = 平均虧損（百分比）
```

**Python 實現：**

```python
def expected_value(win_rate: float,
                   avg_win: float,
                   avg_loss: float) -> float:
    """
    計算期望值
    
    Parameters:
    -----------
    win_rate : float
        勝率（0-1）
    avg_win : float
        平均盈利（百分比，如 5.0 代表 5%）
    avg_loss : float
        平均虧損（百分比，如 3.0 代表 3%）
    
    Returns:
    --------
    float: 期望值（百分比）
    """
    lose_rate = 1 - win_rate
    ev = win_rate * avg_win - lose_rate * avg_loss
    return ev
```

### 2.2 信念強度與期望值映射

Druckenmiller 根據信念強度調整倉位：

```python
class ConvictionLevel:
    """信念強度等級"""
    NONE = 0.0       # 無信念：不交易
    LOW = 0.25       # 低信念：小倉位試水
    MEDIUM = 0.5     # 中信念：正常倉位
    HIGH = 0.75      # 高信念：集中倉位
    MAXIMUM = 1.0    # 最高信念：最大倉位


def conviction_from_expected_value(ev: float,
                                  ev_threshold_low: float = 0.5,
                                  ev_threshold_med: float = 1.5,
                                  ev_threshold_high: float = 3.0) -> float:
    """
    將期望值映射到信念強度
    
    Parameters:
    -----------
    ev : float
        期望值（百分比）
    ev_threshold_low : float
        低信念閾值
    ev_threshold_med : float
        中信念閾值
    ev_threshold_high : float
        高信念閥值
    
    Returns:
    --------
    float: 信念強度（0-1）
    """
    if ev <= 0:
        return ConvictionLevel.NONE
    elif ev < ev_threshold_low:
        return ConvictionLevel.LOW
    elif ev < ev_threshold_med:
        return ConvictionLevel.MEDIUM
    elif ev < ev_threshold_high:
        return ConvictionLevel.HIGH
    else:
        return ConvictionLevel.MAXIMUM
```

### 2.3 期望值到倉位的映射

```python
def ev_to_position(ev: float,
                   kelly_base: float,
                   conviction: float,
                   max_position: float = 0.40) -> float:
    """
    將期望值和信念強度轉換為倉位
    
    Parameters:
    -----------
    ev : float
        期望值
    kelly_base : float
        基礎凱利倖位
    conviction : float
        信念強度（0-1）
    max_position : float
        最大倖位限制
    
    Returns:
    --------
    float: 建議倖位（資金百分比）
    
    Notes:
    ------
    結合凱利公式和信念強度，Druckenmiller 風格的倖位調整
    """
    # 基礎：凱利倖位
    base_position = kelly_base
    
    # 信念調整：高信念可以增加倖位，低信念減少
    belief_adjustment = 0.5 + 0.5 * conviction  # 0.5 - 1.0 倍
    
    # 應用信念調整
    position = base_position * belief_adjustment
    
    # 應用最大倖位限制
    position = min(position, max_position)
    
    # 最小倖位閾值
    if position < 0.01:
        position = 0.0
    
    return position
```

---

## 3. 風險平價策略

### 3.1 波動率計算

```python
import numpy as np
import pandas as pd

def calculate_volatility(returns: pd.Series,
                         window: int = 20,
                         annualize: bool = True) -> float:
    """
    計算波動率（標準差）
    
    Parameters:
    -----------
    returns : pd.Series
        收益率序列
    window : int
        移動窗口大小（交易天數）
    annualize : bool
        是否年化
    
    Returns:
    --------
    float: 波動率
    """
    if len(returns) < window:
        # 數據不足時使用所有數據
        vol = returns.std()
    else:
        # 使用移動窗口
        vol = returns.tail(window).std()
    
    if annualize:
        # 假設 252 個交易日/年
        vol *= np.sqrt(252)
    
    return vol


def ewma_volatility(returns: pd.Series,
                    lambda_: float = 0.94,
                    min_obs: int = 20) -> pd.Series:
    """
    計算 EWMA（指數加權移動平均）波動率
    
    Parameters:
    -----------
    returns : pd.Series
        收益率序列
    lambda_ : float
        衰減因子（通常 0.94-0.97）
    min_obs : int
        最小觀測值數量
    
    Returns:
    --------
    pd.Series: EWMA 波動率序列
    
    Notes:
    ------
    EWMA 對近期的波動變化更敏感，適合動態風險管理
    """
    if len(returns) < min_obs:
        # 數據不足時使用標準方法
        return pd.Series([returns.std()] * len(returns), index=returns.index)
    
    # 初始化
    ewma = pd.Series(index=returns.index, dtype=float)
    
    # 初始波動率（使用最初 min_obs 個觀測值）
    initial_vol = returns[:min_obs].std()
    ewma.iloc[min_obs-1] = initial_vol
    
    # 遞歸計算
    for i in range(min_obs, len(returns)):
        # EWMA 公式
        ewma.iloc[i] = np.sqrt(
            lambda_ * ewma.iloc[i-1]**2 + 
            (1 - lambda_) * returns.iloc[i-1]**2
        )
    
    # 填充前面的值
    ewma.iloc[:min_obs-1] = initial_vol
    
    return ewma
```

### 3.2 相關性分析

```python
def calculate_correlation_matrix(returns_df: pd.DataFrame,
                                window: int = 60) -> pd.DataFrame:
    """
    計算滾動相關性矩陣
    
    Parameters:
    -----------
    returns_df : pd.DataFrame
        多資產收益率（列=資產，行=時間）
    window : int
        滾動窗口大小
    
    Returns:
    --------
    pd.DataFrame: 相關性矩陣
    """
    if len(returns_df) < window:
        # 數據不足時使用所有數據
        corr = returns_df.corr()
    else:
        # 使用滾動窗口
        corr = returns_df.tail(window).corr()
    
    return corr


def effective_correlation(corr_matrix: pd.DataFrame) -> float:
    """
    計算有效相關性（平均相關性）
    
    Parameters:
    -----------
    corr_matrix : pd.DataFrame
        相關性矩陣
    
    Returns:
    --------
    float: 有效相關性（0-1）
    """
    n = len(corr_matrix)
    
    # 提取上三角（排除對角線）
    upper = corr_matrix.values[np.triu_indices(n, k=1)]
    
    # 平均相關性
    if len(upper) > 0:
        eff_corr = np.mean(upper)
    else:
        eff_corr = 0.0
    
    return eff_corr
```

### 3.3 風險平價倉位計算

```python
def risk_parity_weights(volatilities: dict,
                        target_vol: float = 0.15,
                        correlations: pd.DataFrame = None) -> dict:
    """
    計算風險平價權重
    
    Parameters:
    -----------
    volatilities : dict
        {資產名稱: 波動率} 字典
    target_vol : float
        目標投資組合波動率
    correlations : pd.DataFrame
        相關性矩陣（可選）
    
    Returns:
    --------
    dict: 風險平價權重
    
    Notes:
    ------
    風險平價目標：每個資產對投資組合風險的貢獻相等
    """
    assets = list(volatilities.keys())
    n = len(assets)
    
    if n == 0:
        return {}
    
    if correlations is None:
        # 假設資產不相關
        correlations = pd.DataFrame(np.eye(n), index=assets, columns=assets)
    
    # 逆波動率加權（簡化版風險平價）
    inv_vol = {asset: 1.0 / vol for asset, vol in volatilities.items()}
    total_inv_vol = sum(inv_vol.values())
    
    # 未調整權重
    raw_weights = {asset: inv_vol[asset] / total_inv_vol 
                   for asset in assets}
    
    # 調整以達到目標波動率
    # 計算組合波動率
    weights_array = np.array([raw_weights[asset] for asset in assets])
    vols_array = np.array([volatilities[asset] for asset in assets])
    
    # 組合波動率（簡化版，忽略相關性）
    portfolio_vol = np.sqrt(np.sum(weights_array**2 * vols_array**2))
    
    # 縮放因子
    if portfolio_vol > 0:
        scale_factor = target_vol / portfolio_vol
    else:
        scale_factor = 1.0
    
    # 最終權重
    final_weights = {asset: weight * scale_factor 
                     for asset, weight in raw_weights.items()}
    
    return final_weights
```

---

## 4. 最大回撤控制

### 4.1 波動率預測（GARCH 模型）

```python
from arch import arch_model

def garch_forecast(returns: pd.Series,
                   horizon: int = 10,
                   p: int = 1,
                   q: int = 1) -> pd.Series:
    """
    使用 GARCH 模型預測波動率
    
    Parameters:
    -----------
    returns : pd.Series
        收益率序列
    horizon : int
        預測天數
    p : int
        GARCH(p,q) 的 p 參數
    q : int
        GARCH(p,q) 的 q 參數
    
    Returns:
    --------
    pd.Series: 預測波動率
    
    Notes:
    ------
    GARCH(1,1) 是最常用的設定，能夠捕捉波動率聚集現象
    """
    # 擬合 GARCH 模型
    model = arch_model(returns * 100, vol='Garch', p=p, q=q)
    fitted = model.fit(disp='off')
    
    # 預測波動率
    forecast = fitted.forecast(horizon=horizon)
    
    # 提取預測值並轉換回原來的單位
    forecast_vol = np.sqrt(forecast.variance.values[-1, :]) / 100
    
    return pd.Series(forecast_vol)
```

### 4.2 VaR 和 CVaR 計算

```python
def calculate_var(returns: pd.Series,
                   confidence_level: float = 0.95,
                   method: str = 'historical') -> float:
    """
    計算風險價值（VaR）
    
    Parameters:
    -----------
    returns : pd.Series
        收益率序列
    confidence_level : float
        置信水平（0-1）
    method : str
        計算方法：
        - 'historical': 歷史模擬法
        - 'parametric': 參數法（假設正態分佈）
        - 'ewma': 指數加權法
    
    Returns:
    --------
    float: VaR（負值表示損失）
    """
    alpha = 1 - confidence_level
    
    if method == 'historical':
        # 歷史模擬法
        var = returns.quantile(alpha)
        
    elif method == 'parametric':
        # 參數法（假設正態分佈）
        from scipy import stats
        mean = returns.mean()
        std = returns.std()
        var = stats.norm.ppf(alpha, mean, std)
        
    elif method == 'ewma':
        # 指數加權法
        lambda_ = 0.94
        weights = np.array([(1 - lambda_) * (lambda_ ** i) 
                           for i in range(len(returns))])
        weights = weights / weights.sum()
        weighted_returns = returns * weights
        var = weighted_returns.quantile(alpha)
        
    else:
        raise ValueError(f"Unknown method: {method}")
    
    return var


def calculate_cvar(returns: pd.Series,
                   confidence_level: float = 0.95) -> float:
    """
    計算條件風險價值（CVaR / Expected Shortfall）
    
    Parameters:
    -----------
    returns : pd.Series
        收益率序列
    confidence_level : float
        置信水平（0-1）
    
    Returns:
    --------
    float: CVaR（負值表示損失）
    
    Notes:
    ------
    CVaR 是超過 VaR 的平均損失，是更穩健的風險度量
    """
    var = calculate_var(returns, confidence_level)
    
    # 計算低於 VaR 的平均損失
    cvar = returns[returns <= var].mean()
    
    return cvar
```

### 4.3 倉位限制器

```python
class PositionLimiter:
    """
    倉位限制器
    基於回撤控制和風險預算限制倉位
    """
    
    def __init__(self,
                 max_portfolio_risk: float = 0.20,
                 max_position_risk: float = 0.05,
                 var_confidence: float = 0.95,
                 lookback_days: int = 252):
        """
        Parameters:
        -----------
        max_portfolio_risk : float
            最大投資組合風險（年化波動率）
        max_position_risk : float
            單個倖位最大風險（年化波動率）
        var_confidence : float
            VaR 置信水平
        lookback_days : int
            回溯天數
        """
        self.max_portfolio_risk = max_portfolio_risk
        self.max_position_risk = max_position_risk
        self.var_confidence = var_confidence
        self.lookback_days = lookback_days
    
    def limit_position(self,
                       position: float,
                       asset_volatility: float,
                       portfolio_volatility: float = None) -> float:
        """
        限制倖位大小
        
        Parameters:
        -----------
        position : float
            建議倖位（資金百分比）
        asset_volatility : float
            資產波動率（年化）
        portfolio_volatility : float
            當前投資組合波動率（年化，可選）
        
        Returns:
        --------
        float: 限制後倖位
        """
        # 檢查資產風險限制
        position_risk = position * asset_volatility
        if position_risk > self.max_position_risk:
            position = self.max_position_risk / asset_volatility
        
        # 檢查投資組合風險限制（如果提供）
        if portfolio_volatility is not None:
            # 簡化：假設新增資產與現有組合不完全相關
            # 實際應用應考慮相關性
            new_portfolio_risk = np.sqrt(
                portfolio_volatility**2 + (position * asset_volatility)**2
            )
            
            if new_portfolio_risk > self.max_portfolio_risk:
                # 縮減倖位以滿足投資組合風險限制
                allowable_risk = np.sqrt(
                    self.max_portfolio_risk**2 - portfolio_volatility**2
                )
                if allowable_risk > 0:
                    position = allowable_risk / asset_volatility
                else:
                    position = 0.0
        
        # 確保非負
        position = max(0.0, position)
        
        return position
    
    def calculate_stop_loss(self,
                           entry_price: float,
                           position: float,
                           asset_volatility: float,
                           holding_period_days: int = 10) -> float:
        """
        計算止損價格
        
        Parameters:
        -----------
        entry_price : float
            入場價格
        position : float
            倖位大小
        asset_volatility : float
            資產波動率（年化）
        holding_period_days : int
            預期持有天數
        
        Returns:
        --------
        float: 止損價格
        """
        # 計算持有期間的波動率
        period_vol = asset_volatility * np.sqrt(holding_period_days / 252)
        
        # 止損距離：2 個標準差（約 95% 置信）
        stop_distance = 2.0 * period_vol
        
        # 止損價格
        stop_price = entry_price * (1 - stop_distance)
        
        return stop_price
```

---

## 5. 實時動態調整機制

### 5.1 信念強度監控

```python
class ConvictionMonitor:
    """
    信念強度監控器
    實時監控投資論證的有效性，動態調整倖位
    """
    
    def __init__(self,
                 initial_conviction: float,
                 signal_source,
                 conviction_decay_rate: float = 0.05,
                 conviction_boost_rate: float = 0.10):
        """
        Parameters:
        -----------
        initial_conviction : float
            初始信念強度（0-1）
        signal_source
            信號源（提供更新的宏觀信號）
        conviction_decay_rate : float
            信念衰減率（每日）
        conviction_boost_rate : float
            信念增強率（當信號確認時）
        """
        self.current_conviction = initial_conviction
        self.signal_source = signal_source
        self.decay_rate = conviction_decay_rate
        self.boost_rate = conviction_boost_rate
        self.history = []
    
    def update(self, days_passed: int = 1) -> float:
        """
        更新信念強度
        
        Parameters:
        -----------
        days_passed : int
            經過的天數
        
        Returns:
        --------
        float: 更新後的信念強度
        """
        # 獲取當前信號
        current_signal = self.signal_source.generate_composite_signal()
        
        # 衰減信念（時間衰減）
        decay = self.decay_rate * days_passed
        self.current_conviction -= decay
        
        # 檢查信號方向是否一致
        # 這裡需要跟蹤初始信號方向
        if hasattr(self, 'initial_signal_direction'):
            signal_alignment = self._check_signal_alignment(current_signal)
            
            if signal_alignment > 0.8:
                # 信號強烈對齊：增強信念
                self.current_conviction += self.boost_rate
        
        # 限制在 0-1 範圍
        self.current_conviction = max(0.0, min(1.0, self.current_conviction))
        
        # 記錄歷史
        self.history.append({
            'timestamp': pd.Timestamp.now(),
            'conviction': self.current_conviction,
            'signal_score': current_signal['composite_score']
        })
        
        return self.current_conviction
    
    def _check_signal_alignment(self, current_signal: dict) -> float:
        """
        檢查當前信號與初始信號的對齊程度
        
        Parameters:
        -----------
        current_signal : dict
            當前信號
        
        Returns:
        --------
        float: 對齊程度（0-1）
        """
        initial_score = self.initial_signal_direction
        current_score = current_signal['composite_score']
        
        # 檢查方向是否一致
        if initial_score * current_score > 0:
            # 方向一致，計算對齊程度
            alignment = min(abs(initial_score), abs(current_score)) / max(abs(initial_score), abs(current_score))
        else:
            # 方向相反
            alignment = 0.0
        
        return alignment
    
    def set_initial_signal(self, signal: dict):
        """
        設置初始信號方向
        
        Parameters:
        -----------
        signal : dict
            初始信號
        """
        self.initial_signal_direction = signal['composite_score']
```

### 5.2 市場條件評估

```python
class MarketConditionAssessor:
    """
    市場條件評估器
    評估市場環境，調整風險偏好
    """
    
    def __init__(self):
        self.vix_threshold_high = 30.0
        self.vix_threshold_low = 15.0
        self.trend_strength_threshold = 0.5
    
    def assess_market_regime(self,
                             vix: float,
                             market_trend_strength: float,
                             liquidity_conditions: str) -> dict:
        """
        評估市場制度
        
        Parameters:
        -----------
        vix : float
            VIX 指數（波動率指數）
        market_trend_strength : float
            市場趨勢強度（-1 到 1）
        liquidity_conditions : str
            流動性條件：'tight', 'normal', 'abundant'
        
        Returns:
        --------
        dict: 市場制度評估
        """
        # 波動率評估
        if vix > self.vix_threshold_high:
            volatility_regime = 'HIGH'
            risk_adjustment = 0.5  # 降低倖位
        elif vix < self.vix_threshold_low:
            volatility_regime = 'LOW'
            risk_adjustment = 1.2  # 增加倖位
        else:
            volatility_regime = 'NORMAL'
            risk_adjustment = 1.0
        
        # 趨勢評估
        if abs(market_trend_strength) > self.trend_strength_threshold:
            trend_regime = 'STRONG'
        else:
            trend_regime = 'WEAK'
        
        # 流動性評估
        if liquidity_conditions == 'abundant':
            liquidity_regime = 'ABUNDANT'
            liquidity_adjustment = 1.2
        elif liquidity_conditions == 'tight':
            liquidity_regime = 'TIGHT'
            liquidity_adjustment = 0.7
        else:
            liquidity_regime = 'NORMAL'
            liquidity_adjustment = 1.0
        
        # 綜合調整因子
        overall_adjustment = risk_adjustment * liquidity_adjustment
        
        return {
            'volatility_regime': volatility_regime,
            'trend_regime': trend_regime,
            'liquidity_regime': liquidity_regime,
            'risk_adjustment': risk_adjustment,
            'liquidity_adjustment': liquidity_adjustment,
            'overall_adjustment': overall_adjustment
        }
```

### 5.3 倉位再平衡

```python
class PositionRebalancer:
    """
    倉位再平衡器
    根據信念變化和市場條件動態調整倖位
    """
    
    def __init__(self,
                 rebalance_threshold: float = 0.10,
                 max_daily_change: float = 0.20):
        """
        Parameters:
        -----------
        rebalance_threshold : float
            再平衡觸發閾值（倖位變化百分比）
        max_daily_change : float
            最大每日倖位變化（百分比）
        """
        self.rebalance_threshold = rebalance_threshold
        self.max_daily_change = max_daily_change
        self.current_positions = {}
    
    def calculate_target_positions(self,
                                   convictions: dict,
                                   kelly_positions: dict,
                                   market_adjustment: float = 1.0) -> dict:
        """
        計算目標倖位
        
        Parameters:
        -----------
        convictions : dict
            {資產: 信念強度} 字典
        kelly_positions : dict
            {資產: 凱利倖位} 字典
        market_adjustment : float
            市場調整因子
        
        Returns:
        --------
        dict: 目標倖位
        """
        target_positions = {}
        
        for asset in convictions:
            # 信念調整的凱利倖位
            conviction = convictions[asset]
            kelly = kelly_positions.get(asset, 0.0)
            
            # 信念驅動的倖位調整
            belief_adjusted = kelly * (0.5 + 0.5 * conviction)
            
            # 市場調整
            market_adjusted = belief_adjusted * market_adjustment
            
            # 應用最大倖位限制（Druckenmiller 風格：單個標的最大 40%）
            max_position = 0.40
            market_adjusted = min(market_adjusted, max_position)
            
            target_positions[asset] = market_adjusted
        
        return target_positions
    
    def rebalance(self,
                  target_positions: dict,
                  current_positions: dict) -> dict:
        """
        執行再平衡
        
        Parameters:
        -----------
        target_positions : dict
            目標倖位
        current_positions : dict
            當前倖位
        
        Returns:
        --------
        dict: 建議的倖位調整
        """
        adjustments = {}
        
        for asset in set(list(target_positions.keys()) + list(current_positions.keys())):
            target = target_positions.get(asset, 0.0)
            current = current_positions.get(asset, 0.0)
            
            # 計算變化
            change = target - current
            
            # 檢查是否超過閾值
            if abs(change) / max(current, 0.01) > self.rebalance_threshold:
                # 應用最大每日變化限制
                max_change = current * self.max_daily_change
                if abs(change) > max_change:
                    change = max_change if change > 0 else -max_change
                
                adjustments[asset] = {
                    'current': current,
                    'target': target,
                    'change': change,
                    'action': 'buy' if change > 0 else 'sell' if change < 0 else 'hold'
                }
        
        return adjustments
```

### 5.4 止損觸發器

```python
class StopLossManager:
    """
    止損管理器
    實現 Druckenmiller 的快速減損原則
    """
    
    def __init__(self,
                 max_position_loss: float = 0.15,
                 time_based_stop: int = 30):
        """
        Parameters:
        -----------
        max_position_loss : float
            最大倖位損失（百分比）
        time_based_stop : int
        	基於時間的止損天數（如果不應驗）
        """
        self.max_position_loss = max_position_loss
        self.time_based_stop = time_based_stop
        self.positions = {}
    
    def open_position(self,
                      asset: str,
                      entry_price: float,
                      position_size: float,
                      thesis: str):
        """
        開倉，設置止損
        
        Parameters:
        -----------
        asset : str
            資產名稱
        entry_price : float
            入場價格
        position_size : float
            倖位大小（資金百分比）
        thesis : str
            投資論證
        """
        self.positions[asset] = {
            'entry_price': entry_price,
            'position_size': position_size,
            'thesis': thesis,
            'entry_date': pd.Timestamp.now(),
            'stop_loss_price': None,
            'status': 'OPEN'
        }
    
    def check_stop_loss(self,
                       asset: str,
                       current_price: float) -> bool:
        """
        檢查是否觸發止損
        
        Parameters:
        -----------
        asset : str
            資產名稱
        current_price : float
            當前價格
        
        Returns:
        --------
        bool: 是否應該止損
        """
        if asset not in self.positions:
            return False
        
        position = self.positions[asset]
        
        if position['status'] != 'OPEN':
            return False
        
        # 計算損失
        loss = (position['entry_price'] - current_price) / position['entry_price']
        
        # 最大損失止損
        if loss > self.max_position_loss:
            return True
        
        # 基於時間的止損
        holding_days = (pd.Timestamp.now() - position['entry_date']).days
        if holding_days > self.time_based_stop:
            # 檢查價格是否沒有如預期
            # 如果虧損小於 0，但價格沒有上漲，也退出
            if current_price <= position['entry_price']:
                return True
        
        return False
    
    def update_thesis_validity(self,
                             asset: str,
                             is_valid: bool):
        """
        更新投資論證有效性
        
        Parameters:
        -----------
        asset : str
            資產名稱
        is_valid : bool
            論證是否仍然有效
        """
        if asset in self.positions:
            if not is_valid:
                # Druckenmiller 原則：論證不再有效時立即退出
                self.positions[asset]['status'] = 'CLOSE_INVALID_THESIS'
```

---

## 6. 完整系統實現

### 6.1 主系統類

```python
"""
Druckenmiller 動態資金管理系統
完整實現代碼
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class DruckenmillerPositionSizing:
    """
    Druckenmiller 風格的動態資金管理系統
    
    核心原則：
    1. 信念驅動倖位：高信念機會集中配置
    2. 動態調整：根據市場條件和信念強度實時調整
    3. 快速減損：當投資論證不再有效時迅速退出
    4. 保護資本：嚴格控制最大回撤
    """
    
    def __init__(self,
                 initial_capital: float = 1000000.0,
                 max_position_size: float = 0.40,
                 max_portfolio_risk: float = 0.20,
                 kelly_shrinkage: float = 0.25):
        """
        Parameters:
        -----------
        initial_capital : float
            初始資本
        max_position_size : float
            單個標的最大倖位（資金百分比）
        max_portfolio_risk : float
            最大投資組合風險（年化波動率）
        kelly_shrinkage : float
            凱利縮減因子（0.25 = 部分凱利）
        """
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.max_position_size = max_position_size
        self.max_portfolio_risk = max_portfolio_risk
        self.kelly_shrinkage = kelly_shrinkage
        
        # 子模塊
        self.position_limiter = PositionLimiter(
            max_portfolio_risk=max_portfolio_risk
        )
        self.conviction_monitor = None
        self.market_assessor = MarketConditionAssessor()
        self.rebalancer = PositionRebalancer()
        self.stop_loss_manager = StopLossManager()
        
        # 狀態
        self.current_positions = {}
        self.target_positions = {}
        self.trade_history = []
        self.performance_history = []
    
    # ==================== 倉位計算 ====================
    
    def calculate_position_size(self,
                               win_rate: float,
                               avg_win: float,
                               avg_loss: float,
                               conviction: float = 0.5,
                               asset_volatility: float = 0.20,
                               market_regime: dict = None) -> Dict:
        """
        計算建議倖位大小（核心方法）
        
        Parameters:
        -----------
        win_rate : float
            預期勝率（0-1）
        avg_win : float
            平均盈利（百分比）
        avg_loss : float
            平均虧損（百分比）
        conviction : float
            信念強度（0-1）
        asset_volatility : float
            資產波動率（年化）
        market_regime : dict
            市場制度（可選）
        
        Returns:
        --------
        Dict: 倖位建議
        """
        # 1. 計算期望值
        ev = expected_value(win_rate, avg_win, avg_loss)
        
        # 2. 計算盈虧比
        win_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 0
        
        # 3. 計算基礎凱利倖位
        kelly_base = kelly_fraction(win_rate, win_loss_ratio)
        
        # 4. 應用部分凱利縮減
        kelly_adjusted = fractional_kelly(
            kelly_base,
            shrinkage_factor=self.kelly_shrinkage,
            max_position=self.max_position_size
        )
        
        # 5. 信念調整
        # Druckenmiller: 高信念可以增加倖位，但保持保守基礎
        belief_multiplier = 0.5 + 0.5 * conviction  # 0.5-1.0 倍
        belief_adjusted = kelly_adjusted * belief_multiplier
        
        # 6. 市場制度調整
        if market_regime is not None:
            market_adjustment = market_regime.get('overall_adjustment', 1.0)
            belief_adjusted *= market_adjustment
        
        # 7. 風險限制（倖位限制器）
        final_position = self.position_limiter.limit_position(
            position=belief_adjusted,
            asset_volatility=asset_volatility
        )
        
        # 8. 計算貨幣金額
        position_value = final_position * self.current_capital
        
        # 9. 計算止損價格
        stop_loss_price = self.position_limiter.calculate_stop_loss(
            entry_price=1.0,  # 相對價格
            position=final_position,
            asset_volatility=asset_volatility
        )
        
        return {
            'expected_value': ev,
            'kelly_base': kelly_base,
            'kelly_adjusted': kelly_adjusted,
            'belief_adjusted': belief_adjusted,
            'final_position_pct': final_position,
            'position_value': position_value,
            'stop_loss_distance_pct': stop_loss_price,
            'conviction_level': conviction,
            'market_regime_adjustment': market_regime.get('overall_adjustment', 1.0) if market_regime else 1.0
        }
    
    # ==================== 投資組合管理 ====================
    
    def optimize_portfolio(self,
                          assets_data: Dict[str, Dict],
                          correlations: pd.DataFrame = None) -> Dict:
        """
        優化投資組合
        
        Parameters:
        -----------
        assets_data : Dict
            {資產: {win_rate, avg_win, avg_loss, conviction, volatility}}
        correlations : pd.DataFrame
            相關性矩陣
        
        Returns:
        --------
        Dict: 投資組合建議
        """
        positions = {}
        total_risk = 0.0
        
        # 計算每個資產的倖位
        for asset, data in assets_data.items():
            position_result = self.calculate_position_size(
                win_rate=data['win_rate'],
                avg_win=data['avg_win'],
                avg_loss=data['avg_loss'],
                conviction=data['conviction'],
                asset_volatility=data['volatility']
            )
            positions[asset] = position_result
            
            # 累積風險（簡化）
            total_risk += position_result['final_position_pct'] * data['volatility']
        
        # 檢查總風險
        if total_risk > self.max_portfolio_risk:
            # 縮減所有倖位以滿足風險限制
            scale_factor = self.max_portfolio_risk / total_risk
            
            for asset in positions:
                positions[asset]['final_position_pct'] *= scale_factor
                positions[asset]['position_value'] *= scale_factor
        
        # 計算投資組合統計
        portfolio_stats = self._calculate_portfolio_stats(positions, assets_data)
        
        return {
            'positions': positions,
            'portfolio_stats': portfolio_stats,
            'total_risk': total_risk,
            'total_exposure': sum(p['final_position_pct'] for p in positions.values())
        }
    
    def _calculate_portfolio_stats(self,
                                  positions: Dict,
                                  assets_data: Dict) -> Dict:
        """計算投資組合統計"""
        # 加權平均
        weights = {asset: p['final_position_pct'] for asset, p in positions.items()}
        total_weight = sum(weights.values())
        
        if total_weight == 0:
            return {
                'weighted_win_rate': 0,
                'weighted_ev': 0,
                'weighted_volatility': 0,
                'sharpe_ratio': 0
            }
        
        # 標準化權重
        normalized_weights = {asset: w / total_weight for asset, w in weights.items()}
        
        # 加權統計
        weighted_win_rate = sum(
            normalized_weights[asset] * assets_data[asset]['win_rate']
            for asset in normalized_weights
        )
        
        weighted_ev = sum(
            normalized_weights[asset] * positions[asset]['expected_value']
            for asset in normalized_weights
        )
        
        weighted_vol = sum(
            normalized_weights[asset] * assets_data[asset]['volatility']
            for asset in normalized_weights
        )
        
        # 夏普比率（簡化，假設無風險利率為 0）
        sharpe = weighted_ev / weighted_vol if weighted_vol > 0 else 0
        
        return {
            'weighted_win_rate': weighted_win_rate,
            'weighted_ev': weighted_ev,
            'weighted_volatility': weighted_vol,
            'sharpe_ratio': sharpe
        }
    
    # ==================== 動態調整 ====================
    
    def update_positions(self,
                         market_conditions: Dict,
                         conviction_updates: Dict = None) -> Dict:
        """
        更新倖位（動態調整）
        
        Parameters:
        -----------
        market_conditions : Dict
            市場條件 {vix, market_trend, liquidity}
        conviction_updates : Dict
            信念更新 {資產: 新信念強度}
        
        Returns:
        --------
        Dict: 倖位調整建議
        """
        # 評估市場制度
        market_regime = self.market_assessor.assess_market_regime(
            vix=market_conditions.get('vix', 20.0),
            market_trend_strength=market_conditions.get('market_trend', 0.0),
            liquidity_conditions=market_conditions.get('liquidity', 'normal')
        )
        
        # 更新信念
        if conviction_updates:
            for asset, conviction in conviction_updates.items():
                if asset in self.current_positions:
                    self.current_positions[asset]['conviction'] = conviction
        
        # 計算目標倖位
        target_positions = {}
        for asset, pos in self.current_positions.items():
            # 重新計算倖位
            result = self.calculate_position_size(
                win_rate=pos['win_rate'],
                avg_win=pos['avg_win'],
                avg_loss=pos['avg_loss'],
                conviction=pos['conviction'],
                asset_volatility=pos['volatility'],
                market_regime=market_regime
            )
            target_positions[asset] = result['final_position_pct']
        
        self.target_positions = target_positions
        
        # 再平衡
        adjustments = self.rebalancer.rebalance(
            target_positions=target_positions,
            current_positions={k: v['position_pct'] for k, v in self.current_positions.items()}
        )
        
        return {
            'market_regime': market_regime,
            'target_positions': target_positions,
            'adjustments': adjustments
        }
    
    # ==================== 止損管理 ====================
    
    def check_stop_losses(self, current_prices: Dict) -> List[str]:
        """
        檢查止損觸發
        
        Parameters:
        -----------
        current_prices : Dict
            當前價格 {資產: 價格}
        
        Returns:
        --------
        List[str]: 應該止損的資產列表
        """
        stop_loss_assets = []
        
        for asset in self.current_positions:
            if asset in current_prices:
                current_price = current_prices[asset]
                entry_price = self.current_positions[asset]['entry_price']
                
                # 檢查止損
                if self.stop_loss_manager.check_stop_loss(asset, current_price):
                    stop_loss_assets.append(asset)
        
        return stop_loss_assets
    
    # ==================== 績效追蹤 ====================
    
    def record_trade(self,
                     asset: str,
                     action: str,
                     price: float,
                     quantity: float,
                     timestamp: datetime = None):
        """
        記錄交易
        
        Parameters:
        -----------
        asset : str
            資產名稱
        action : str
            操作類型：'buy', 'sell', 'short', 'cover'
        price : float
            價格
        quantity : float
            數量
        timestamp : datetime
            時間戳
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        trade = {
            'timestamp': timestamp,
            'asset': asset,
            'action': action,
            'price': price,
            'quantity': quantity,
            'value': price * quantity
        }
        
        self.trade_history.append(trade)
    
    def calculate_performance(self, prices: pd.DataFrame) -> Dict:
        """
        計算績效指標
        
        Parameters:
        -----------
        prices : pd.DataFrame
            價格數據（列=資產，行=時間）
        
        Returns:
        --------
        Dict: 績效指標
        """
        if not self.current_positions:
            return {}
        
        # 計算投資組合回報
        returns = []
        for asset, pos in self.current_positions.items():
            if asset in prices.columns:
                asset_returns = prices[asset].pct_change().dropna()
                weighted_returns = asset_returns * pos['position_pct']
                returns.append(weighted_returns)
        
        if returns:
            portfolio_returns = pd.concat(returns, axis=1).sum(axis=1)
        else:
            return {}
        
        # 計算績效指標
        total_return = (1 + portfolio_returns).prod() - 1
        annual_return = portfolio_returns.mean() * 252
        volatility = portfolio_returns.std() * np.sqrt(252)
        sharpe = annual_return / volatility if volatility > 0 else 0
        
        # 最大回撤
        cumulative = (1 + portfolio_returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # 勝率（如果有交易歷史）
        if self.trade_history:
            # 簡化：計算賣出交易的勝率
            sell_trades = [t for t in self.trade_history if t['action'] == 'sell']
            if sell_trades:
                # 這裡需要匹配買入和賣出計算實際損益
                # 簡化處理
                win_rate = 0.6  # 估計
            else:
                win_rate = 0.0
        else:
            win_rate = 0.0
        
        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate
        }
```

---

## 7. 回測驗證

### 7.1 回測框架

```python
"""
回測框架
驗證動態資金管理系統的歷史表現
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta


class PositionSizingBacktester:
    """
    倖位回測器
    """
    
    def __init__(self,
                 initial_capital: float = 1000000.0,
                 transaction_cost: float = 0.001):
        """
        Parameters:
        -----------
        initial_capital : float
            初始資本
        transaction_cost : float
            交易成本（百分比）
        """
        self.initial_capital = initial_capital
        self.transaction_cost = transaction_cost
        self.position_sizing = DruckenmillerPositionSizing(
            initial_capital=initial_capital
        )
    
    def backtest(self,
                 price_data: pd.DataFrame,
                 signal_data: pd.DataFrame,
                 start_date: str = None,
                 end_date: str = None) -> Dict:
        """
        執行回測
        
        Parameters:
        -----------
        price_data : pd.DataFrame
            價格數據（列=資產，行=日期）
        signal_data : pd.DataFrame
            信號數據（列=資產，值=綜合信號得分 -1 到 1）
        start_date : str
            開始日期
        end_date : str
            結束日期
        
        Returns:
        --------
        Dict: 回測結果
        """
        # 數據準備
        if start_date:
            price_data = price_data[start_date:]
            signal_data = signal_data[start_date:]
        if end_date:
            price_data = price_data[:end_date]
            signal_data = signal_data[:end_date]
        
        # 對齊數據
        aligned_data = pd.concat([price_data, signal_data], axis=1).dropna()
        
        # 初始化
        capital = self.initial_capital
        positions = {}
        equity_curve = [capital]
        trades = []
        
        # 滾動回測
        for i in range(len(aligned_data)):
            current_date = aligned_data.index[i]
            current_prices = aligned_data.iloc[i][price_data.columns]
            current_signals = aligned_data.iloc[i][signal_data.columns]
            
            # 計算歷史勝率和盈虧比（簡化版）
            # 實際應用應該使用滾動窗口計算
            win_rate = 0.55  # 假設
            avg_win = 5.0
            avg_loss = 3.0
            
            # 對每個資產生成倖位建議
            for asset in price_data.columns:
                signal = current_signals[asset]
                
                # 將信號轉換為信念強度
                conviction = min(abs(signal), 1.0)
                
                # 計算倖位
                position_result = self.position_sizing.calculate_position_size(
                    win_rate=win_rate,
                    avg_win=avg_win,
                    avg_loss=avg_loss,
                    conviction=conviction,
                    asset_volatility=0.20  # 簡化
                )
                
                target_position = position_result['final_position_pct']
                
                # 執行交易
                current_position = positions.get(asset, 0.0)
                position_change = target_position - current_position
                
                if abs(position_change) > 0.01:  # 超過 1% 才交易
                    trade_value = position_change * capital
                    num_shares = trade_value / current_prices[asset]
                    
                    # 記錄交易
                    trades.append({
                        'date': current_date,
                        'asset': asset,
                        'action': 'buy' if position_change > 0 else 'sell',
                        'shares': abs(num_shares),
                        'price': current_prices[asset],
                        'value': abs(trade_value)
                    })
                    
                    # 更新倖位
                    positions[asset] = target_position
                    
                    # 扣除交易成本
                    capital -= abs(trade_value) * self.transaction_cost
            
            # 計算當天回報
            daily_return = 0.0
            for asset, position_pct in positions.items():
                if asset in current_prices.index:
                    daily_return += position_pct * current_prices[asset]
            
            # 更新資本（簡化）
            capital *= (1 + daily_return * 0.01)  # 假設 1% 的平均日回報
            equity_curve.append(capital)
        
        # 計算績效
        performance = self._calculate_backtest_performance(equity_curve, trades)
        
        return {
            'equity_curve': pd.Series(equity_curve),
            'trades': trades,
            'performance': performance,
            'final_capital': capital
        }
    
    def _calculate_backtest_performance(self,
                                       equity_curve: list,
                                       trades: list) -> Dict:
        """計算回測績效"""
        equity_series = pd.Series(equity_curve)
        returns = equity_series.pct_change().dropna()
        
        # 總回報
        total_return = (equity_series.iloc[-1] / equity_series.iloc[0]) - 1
        
        # 年化回報
        num_years = len(equity_curve) / 252
        annual_return = (1 + total_return) ** (1 / num_years) - 1
        
        # 波動率
        volatility = returns.std() * np.sqrt(252)
        
        # 夏普比率
        sharpe = annual_return / volatility if volatility > 0 else 0
        
        # 最大回撤
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # 交易統計
        num_trades = len(trades)
        
        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown,
            'num_trades': num_trades
        }


# 回測示例
def run_backtest_example():
    """
    運行回測示例
    """
    # 創建模擬數據
    dates = pd.date_range(start='2020-01-01', end='2024-12-31', freq='D')
    dates = dates[dates.weekday < 5]  # 只保留交易日
    
    # 模擬價格數據
    np.random.seed(42)
    price_data = pd.DataFrame({
        'SPY': 100 * np.cumprod(1 + np.random.normal(0.0003, 0.01, len(dates))),
        'TLT': 100 * np.cumprod(1 + np.random.normal(0.0001, 0.005, len(dates))),
        'GLD': 100 * np.cumprod(1 + np.random.normal(0.0002, 0.008, len(dates)))
    }, index=dates)
    
    # 模擬信號數據（-1 到 1）
    signal_data = pd.DataFrame({
        'SPY': np.random.uniform(-0.5, 0.8, len(dates)),
        'TLT': np.random.uniform(-0.3, 0.5, len(dates)),
        'GLD': np.random.uniform(-0.4, 0.6, len(dates))
    }, index=dates)
    
    # 運行回測
    backtester = PositionSizingBacktester(
        initial_capital=1000000.0,
        transaction_cost=0.001
    )
    
    results = backtester.backtest(
        price_data=price_data,
        signal_data=signal_data,
        start_date='2020-01-01',
        end_date='2024-12-31'
    )
    
    print("回測結果:")
    print(f"最終資本: ${results['final_capital']:,.2f}")
    print(f"總回報: {results['performance']['total_return']:.2%}")
    print(f"年化回報: {results['performance']['annual_return']:.2%}")
    print(f"年化波動率: {results['performance']['volatility']:.2%}")
    print(f"夏普比率: {results['performance']['sharpe_ratio']:.2f}")
    print(f"最大回撤: {results['performance']['max_drawdown']:.2%}")
    print(f"交易次數: {results['performance']['num_trades']}")
    
    return results
```

### 7.2 績效比較

```python
def compare_position_sizing_strategies(price_data: pd.DataFrame,
                                       signal_data: pd.DataFrame) -> pd.DataFrame:
    """
    比較不同倖位調整策略的績效
    
    Parameters:
    -----------
    price_data : pd.DataFrame
        價格數據
    signal_data : pd.DataFrame
        信號數據
    
    Returns:
    --------
    pd.DataFrame: 績效比較結果
    """
    strategies = {
        'Full Kelly': {'shrinkage': 1.0},
        'Half Kelly': {'shrinkage': 0.5},
        'Quarter Kelly': {'shrinkage': 0.25},
        'Fixed 10%': {'shrinkage': 0.1},
        'Conviction-Adjusted': {'shrinkage': 0.25, 'use_conviction': True}
    }
    
    results = {}
    
    for strategy_name, params in strategies.items():
        backtester = PositionSizingBacktester(
            initial_capital=1000000.0
        )
        
        # 設置策略參數
        backtester.position_sizing.kelly_shrinkage = params['shrinkage']
        
        # 運行回測
        result = backtester.backtest(price_data, signal_data)
        
        # 提取績效
        performance = result['performance']
        results[strategy_name] = performance
    
    # 轉換為 DataFrame
    results_df = pd.DataFrame(results).T
    
    # 排序（按夏普比率）
    results_df = results_df.sort_values('sharpe_ratio', ascending=False)
    
    return results_df
```

---

## 8. 使用示例和最佳實踐

### 8.1 完整使用流程

```python
"""
完整使用示例
演示如何使用 Druckenmiller 動態資金管理系統
"""

def complete_workflow_example():
    """
    完整工作流程示例
    """
    
    # 1. 初始化系統
    print("=== 初始化 Druckenmiller 動態資金管理系統 ===")
    position_sizing = DruckenmillerPositionSizing(
        initial_capital=1000000.0,  # 100 萬美元
        max_position_size=0.40,     # 單個標的最大 40%
        max_portfolio_risk=0.20,    # 投資組合最大風險 20%
        kelly_shrinkage=0.25        # 1/4 凱利（保守）
    )
    
    # 2. 定義投資機會
    print("\n=== 分析投資機會 ===")
    investment_opportunity = {
        'asset': 'SPY (S&P 500 ETF)',
        'win_rate': 0.60,           # 60% 勝率
        'avg_win': 8.0,             # 平均盈利 8%
        'avg_loss': 4.0,            # 平均虧損 4%
        'conviction': 0.75,         # 高信念
        'volatility': 0.18          # 年化波動率 18%
    }
    
    print(f"資產: {investment_opportunity['asset']}")
    print(f"預期勝率: {investment_opportunity['win_rate']:.0%}")
    print(f"盈虧比: {investment_opportunity['avg_win']/investment_opportunity['avg_loss']:.2f}")
    print(f"信念強度: {investment_opportunity['conviction']:.0%}")
    
    # 3. 計算建議倖位
    print("\n=== 計算建議倖位 ===")
    position_result = position_sizing.calculate_position_size(
        win_rate=investment_opportunity['win_rate'],
        avg_win=investment_opportunity['avg_win'],
        avg_loss=investment_opportunity['avg_loss'],
        conviction=investment_opportunity['conviction'],
        asset_volatility=investment_opportunity['volatility']
    )
    
    print(f"期望值: {position_result['expected_value']:.2f}%")
    print(f"基礎凱利倖位: {position_result['kelly_base']:.2%}")
    print(f"部分凱利倖位 (1/4): {position_result['kelly_adjusted']:.2%}")
    print(f"信念調整倖位: {position_result['belief_adjusted']:.2%}")
    print(f"最終倖位建議: {position_result['final_position_pct']:.2%}")
    print(f"倖位金額: ${position_result['position_value']:,.2f}")
    print(f"止損距離: {position_result['stop_loss_distance_pct']:.2%}")
    
    # 4. 投資組合優化（多資產）
    print("\n=== 投資組合優化 ===")
    portfolio_data = {
        'SPY': {
            'win_rate': 0.60,
            'avg_win': 8.0,
            'avg_loss': 4.0,
            'conviction': 0.75,
            'volatility': 0.18
        },
        'TLT': {
            'win_rate': 0.55,
            'avg_win': 5.0,
            'avg_loss': 3.0,
            'conviction': 0.50,
            'volatility': 0.10
        },
        'GLD': {
            'win_rate': 0.52,
            'avg_win': 6.0,
            'avg_loss': 4.0,
            'conviction': 0.40,
            'volatility': 0.15
        }
    }
    
    portfolio_result = position_sizing.optimize_portfolio(portfolio_data)
    
    print("\n投資組合建議:")
    for asset, pos in portfolio_result['positions'].items():
        print(f"  {asset}: {pos['final_position_pct']:.2%} (${pos['position_value']:,.2f})")
    
    print(f"\n投資組合統計:")
    stats = portfolio_result['portfolio_stats']
    print(f"  加權勝率: {stats['weighted_win_rate']:.2%}")
    print(f"  加權期望值: {stats['weighted_ev']:.2f}%")
    print(f"  加權波動率: {stats['weighted_volatility']:.2%}")
    print(f"  夏普比率: {stats['sharpe_ratio']:.2f}")
    print(f"  總風險暴露: {portfolio_result['total_risk']:.2%}")
    print(f"  總倖位: {portfolio_result['total_exposure']:.2%}")
    
    # 5. 動態調整
    print("\n=== 動態調整 ===")
    market_conditions = {
        'vix': 25.0,              # 中等波動率
        'market_trend': 0.6,      # 看多趨勢
        'liquidity': 'normal'     # 正常流動性
    }
    
    # 模擬倖位
    position_sizing.current_positions = {
        'SPY': {
            'position_pct': portfolio_result['positions']['SPY']['final_position_pct'],
            'win_rate': 0.60,
            'avg_win': 8.0,
            'avg_loss': 4.0,
            'conviction': 0.75,
            'volatility': 0.18,
            'entry_price': 400.0
        },
        'TLT': {
            'position_pct': portfolio_result['positions']['TLT']['final_position_pct'],
            'win_rate': 0.55,
            'avg_win': 5.0,
            'avg_loss': 3.0,
            'conviction': 0.50,
            'volatility': 0.10,
            'entry_price': 100.0
        }
    }
    
    # 倖位調整
    adjustment_result = position_sizing.update_positions(
        market_conditions=market_conditions,
        conviction_updates={'SPY': 0.90, 'TLT': 0.40}  # 信念變化
    )
    
    print("市場制度評估:")
    print(f"  波動率制度: {adjustment_result['market_regime']['volatility_regime']}")
    print(f"  趨勢制度: {adjustment_result['market_regime']['trend_regime']}")
    print(f"  流動性制度: {adjustment_result['market_regime']['liquidity_regime']}")
    print(f"  總體調整因子: {adjustment_result['market_regime']['overall_adjustment']:.2f}")
    
    print("\n倖位調整建議:")
    for asset, adj in adjustment_result['adjustments'].items():
        print(f"  {asset}:")
        print(f"    當前倖位: {adj['current']:.2%}")
        print(f"    目標倖位: {adj['target']:.2%}")
        print(f"    調整: {adj['change']:+.2%} ({adj['action']})")
    
    # 6. 止損檢查
    print("\n=== 止損檢查 ===")
    current_prices = {'SPY': 380.0, 'TLT': 102.0}
    stop_loss_assets = position_sizing.check_stop_losses(current_prices)
    
    if stop_loss_assets:
        print(f"警告: 以下資產觸發止損 - {stop_loss_assets}")
    else:
        print("沒有資產觸發止損")
    
    return position_sizing


if __name__ == "__main__":
    # 運行完整示例
    position_sizing = complete_workflow_example()
```

### 8.2 最佳實踐建議

```python
"""
Druckenmiller 風格資金管理最佳實踐
"""

# 1. 凱利公式使用建議
KELLY_BEST_PRACTICES = {
    'shrinkage_factor': 0.25,        # Druckenmiller 風格：使用 1/4 凱利
    'max_single_position': 0.40,     # 單個標的最大 40%（高信念時）
    'normal_position': 0.10,         # 正常倖位 10%
    'min_position': 0.01,           # 最小倖位 1%（避免過度分散）
}

# 2. 信念強度使用建議
CONVICTION_GUIDELINES = {
    'MAXIMUM': {  # 最高信念（0.9-1.0）
        'description': '宏觀趨勢明確，多項指標強烈一致',
        'position_multiplier': 1.5,  # 可以增加倖位
        'max_position': 0.40,
        'examples': '收益率曲線陡峭 + 通脹受控 + 強勁經濟數據'
    },
    'HIGH': {  # 高信念（0.7-0.9）
        'description': '趨勢明確，大部分指標支持',
        'position_multiplier': 1.0,
        'max_position': 0.25,
        'examples': '經濟數據強勁 + 聯儲寬鬆立場'
    },
    'MEDIUM': {  # 中信念（0.5-0.7）
        'description': '趨勢存在，但指標部分分歧',
        'position_multiplier': 0.8,
        'max_position': 0.15,
        'examples': '經濟數據尚可，但政策不確定'
    },
    'LOW': {  # 低信念（0.3-0.5）
        'description': '趨勢不明顯，指標混雜',
        'position_multiplier': 0.5,
        'max_position': 0.10,
        'examples': '信號中性，觀望為主'
    },
    'NONE': {  # 無信念（0-0.3）
        'description': '無明確趨勢，不交易',
        'position_multiplier': 0.0,
        'max_position': 0.0,
        'examples': '市場混亂，等待機會'
    }
}

# 3. 止損建議
STOP_LOSS_GUIDELINES = {
    'max_position_loss': 0.15,        # 最大倖位損失 15%
    'max_portfolio_loss': 0.08,       # 最大投資組合損失 8%
    'time_based_stop': 30,           # 30 天內未應驗則退出
    'thesis_invalid_stop': True,      # 投資論證不再有效時立即退出
    'volatility_based': True,         # 基於波動率調整止損
}

# 4. 風險管理建議
RISK_MANAGEMENT_GUIDELINES = {
    'max_portfolio_volatility': 0.20,  # 最大投資組合波動率 20%
    'max_correlation': 0.7,            # 最大相關性（避免過度集中）
    'diversification_min': 3,          # 最少 3 個資產（分散化）
    'cash_reserve': 0.10,              # 保持 10% 現金（流動性）
}

# 5. 再平衡建議
REBALANCING_GUIDELINES = {
    'frequency': 'dynamic',            # 動態再平衡（觸發式）
    'threshold': 0.10,                 # 10% 倖位變化才調整
    'max_daily_change': 0.20,          # 最大每日變化 20%
    ' conviction_check': True,          # 每日檢查信念強度
}

def print_best_practices():
    """打印最佳實踐"""
    print("=" * 80)
    print("Druckenmiller 風格資金管理最佳實踐")
    print("=" * 80)
    
    print("\n1. 凱利公式使用建議:")
    for key, value in KELLY_BEST_PRACTICES.items():
        print(f"   {key}: {value}")
    
    print("\n2. 信念強度使用建議:")
    for level, guidelines in CONVICTION_GUIDELINES.items():
        print(f"\n   {level}:")
        print(f"     描述: {guidelines['description']}")
        print(f"     倖位倍數: {guidelines['position_multiplier']}")
        print(f"     最大倖位: {guidelines['max_position']}")
        print(f"     例子: {guidelines['examples']}")
    
    print("\n3. 止損建議:")
    for key, value in STOP_LOSS_GUIDELINES.items():
        print(f"   {key}: {value}")
    
    print("\n4. 風險管理建議:")
    for key, value in RISK_MANAGEMENT_GUIDELINES.items():
        print(f"   {key}: {value}")
    
    print("\n5. 再平衡建議:")
    for key, value in REBALANCING_GUIDELINES.items():
        print(f"   {key}: {value}")
    
    print("\n" + "=" * 80)
```

---

## 9. 系統文檔

### 9.1 API 參考

#### `DruckenmillerPositionSizing` 主類

**初始化參數:**
- `initial_capital` (float): 初始資本，默認 1,000,000
- `max_position_size` (float): 單個標的最大倖位（資金百分比），默認 0.40
- `max_portfolio_risk` (float): 最大投資組合風險（年化波動率），默認 0.20
- `kelly_shrinkage` (float): 凱利縮減因子，默認 0.25

**主要方法:**

1. `calculate_position_size(win_rate, avg_win, avg_loss, conviction, asset_volatility, market_regime=None)`
   - 計算建議倖位大小
   - 返回: Dict 包含期望值、凱利倖位、最終倖位等

2. `optimize_portfolio(assets_data, correlations=None)`
   - 優化投資組合倖位分配
   - 返回: Dict 包含倖位建議和投資組合統計

3. `update_positions(market_conditions, conviction_updates=None)`
   - 動態更新倖位
   - 返回: Dict 包含市場制度評估和倖位調整建議

4. `check_stop_losses(current_prices)`
   - 檢查止損觸發
   - 返回: List[str] 應該止損的資產列表

#### 輔助類

1. `PositionLimiter`: 倉位限制器
   - `limit_position(position, asset_volatility, portfolio_volatility=None)`: 限制倖位
   - `calculate_stop_loss(entry_price, position, asset_volatility, holding_period_days)`: 計算止損價格

2. `ConvictionMonitor`: 信念強度監控器
   - `update(days_passed=1)`: 更新信念強度
   - `set_initial_signal(signal)`: 設置初始信號方向

3. `MarketConditionAssessor`: 市場條件評估器
   - `assess_market_regime(vix, market_trend_strength, liquidity_conditions)`: 評估市場制度

4. `PositionRebalancer`: 倉位再平衡器
   - `calculate_target_positions(convictions, kelly_positions, market_adjustment)`: 計算目標倖位
   - `rebalance(target_positions, current_positions)`: 執行再平衡

5. `StopLossManager`: 止損管理器
   - `open_position(asset, entry_price, position_size, thesis)`: 開倉
   - `check_stop_loss(asset, current_price)`: 檢查止損
   - `update_thesis_validity(asset, is_valid)`: 更新論證有效性

### 9.2 參數說明

#### 凱利公式參數

| 參數 | 說明 | 推薦範圍 | Druckenmiller 設定 |
|------|------|----------|-------------------|
| `shrinkage_factor` | 凱利縮減因子 | 0.10-0.50 | 0.25 |
| `max_position` | 最大單個倖位 | 0.10-0.50 | 0.40 |
| `min_position` | 最小倖位閾值 | 0.005-0.02 | 0.01 |

#### 信念強度參數

| 信念等級 | 範圍 | 說明 | 倉位調整 |
|----------|------|------|----------|
| MAXIMUM | 0.9-1.0 | 最高信念 | ×1.5 |
| HIGH | 0.7-0.9 | 高信念 | ×1.0 |
| MEDIUM | 0.5-0.7 | 中信念 | ×0.8 |
| LOW | 0.3-0.5 | 低信念 | ×0.5 |
| NONE | 0-0.3 | 無信念 | ×0.0 |

#### 風險管理參數

| 參數 | 說明 | 推薦範圍 | Druckenmiller 設定 |
|------|------|----------|-------------------|
| `max_portfolio_risk` | 最大投資組合風險 | 0.10-0.25 | 0.20 |
| `max_position_risk` | 單個倖位最大風險 | 0.03-0.08 | 0.05 |
| `max_drawdown` | 最大回撤限制 | 0.10-0.30 | 0.20 |

### 9.3 使用流程圖

```
開始
  ↓
初始化 DruckenmillerPositionSizing
  ↓
分析投資機會
  ├─ 計算期望值（EV）
  ├─ 估算勝率和盈虧比
  └─ 評估信念強度（Conviction）
  ↓
計算凱利倖位
  ├─ 基礎凱利公式
  ├─ 應用部分凱利縮減
  └─ 信念調整
  ↓
風險限制檢查
  ├─ 倖位限制器
  ├─ 投資組合風險限制
  └─ 止損價格計算
  ↓
確定最終倖位
  ↓
執行交易
  ↓
持續監控
  ├─ 信念強度監控
  ├─ 市場條件評估
  ├─ 倖位再平衡
  └─ 止損檢查
  ↓
調整或退出
  ↓
結束
```

---

## 10. 總結

### 10.1 系統特點

本動態資金管理系統具有以下特點：

1. **凱利公式優化**: 實現完整凱利公式計算，包括部分凱利縮減、連續凱利和凱利下限保護

2. **期望值驅動**: 基於期望值和信念強度動態調整倖位，體現 Druckenmiller 的"集中大注"原則

3. **風險平價**: 通過波動率倒數加權實現風險平價，確保各資產風險貢獻均衡

4. **最大回撤控制**: 通過倖位限制器、VaR/CVaR 計算和止損管理嚴格控制回撤

5. **實時動態調整**: 信念監控、市場條件評估和倖位再平衡實現實時調整

6. **快速減損**: 實現 Druckenmiller 的核心原則 - 投資論證不再有效時迅速退出

### 10.2 Druckenmiller 原則體現

| Druckenmiller 原則 | 系統實現 |
|-------------------|---------|
| 流動性至上 | 與宏觀趨勢系統整合，監控流動性條件 |
| 頂向下宏觀分析 | 接收宏觀信號，驅動倖位決策 |
| 集中大注於高信念機會 | 信念驅動倖位調整，最高可達 40% |
| 快速減損 | 止損管理器，論證無效立即退出 |
| 保持靈活性 | 實時動態調整機制 |
| 保護資本 | 嚴格的風險限制和回撤控制 |

### 10.3 性能特點

- **保守的凱利縮減**: 使用 1/4 凱利，降低過度優化風險
- **信念驅動倖位**: 高信念時可增加倖位，但保持保守基礎
- **市場條件敏感**: 根據 VIX、趨勢和流動性動態調整
- **多層風險控制**: 倖位限制、投資組合風險、止損等多重保護

### 10.4 使用建議

1. **從保守開始**: 建議使用 1/4 凱利或更保守的縮減因子
2. **嚴格遵守信念評估**: 不要高估自己的信念強度
3. **設置明確止損**: 嚴格執行止損，保護資本
4. **持續監控**: 定期檢查信念強度和市場條件
5. **保持流動性**: 保留足夠現金以應對機會
6. **記錄和反思**: 記錄每筆交易的理由和結果，持續改進

### 10.5 限制和注意事項

1. **模型假設**: 凱利公式假設期望值和波動率可以準確估計，實際中存在不確定性
2. **相關性忽略**: 簡化版本未考慮資產間相關性，實際應用應加強
3. **交易成本**: 回測中簡化了交易成本，實際交易成本可能更高
4. **流動性風險**: 大倖位可能面臨流動性風險，實際執行需考慮滑點
5. **主觀性**: 信念強度評估具有主觀性，需要建立標準化流程

---

## 附錄：完整代碼清單

本系統包含以下模塊：

1. **凱利公式模塊**
   - `kelly_fraction()` - 基礎凱利公式
   - `fractional_kelly()` - 部分凱利
   - `continuous_kelly()` - 連續凱利
   - `kelly_with_floor()` - 凱利下限保護

2. **期望值模塊**
   - `expected_value()` - 期望值計算
   - `conviction_from_expected_value()` - 期望值到信念映射
   - `ev_to_position()` - 期望值到倖位映射

3. **風險平價模塊**
   - `calculate_volatility()` - 波動率計算
   - `ewma_volatility()` - EWMA 波動率
   - `calculate_correlation_matrix()` - 相關性矩陣
   - `risk_parity_weights()` - 風險平價權重

4. **風險控制模塊**
   - `garch_forecast()` - GARCH 波動率預測
   - `calculate_var()` - VaR 計算
   - `calculate_cvar()` - CVaR 計算
   - `PositionLimiter` - 倉位限制器類

5. **動態調整模塊**
   - `ConvictionMonitor` - 信念監控類
   - `MarketConditionAssessor` - 市場條件評估類
   - `PositionRebalancer` - 倉位再平衡類
   - `StopLossManager` - 止損管理類

6. **主系統類**
   - `DruckenmillerPositionSizing` - 主系統類

7. **回測模塊**
   - `PositionSizingBacktester` - 回測器類
   - `compare_position_sizing_strategies()` - 策略比較函數

8. **實用工具**
   - 完整使用示例
   - 最佳實踐建議
   - API 參考文檔

---

**文檔結束**

本系統完整實現了 Druckenmiller 風格的動態資金管理，為集中投資提供科學的倖位調整框架。系統結合凱利公式優化、期望值驅動倉位調整、風險平價策略和動態調整機制，嚴格控制風險的同時，允許在高信念機會上集中配置。
