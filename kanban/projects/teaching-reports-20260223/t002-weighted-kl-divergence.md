# 加權 KL 散度教學報告 - 馬爾可夫鏈檢驗

**Task ID:** t002-weighted-kl-divergence
**Agent:** Charlie Creative
**Status:** completed
**Timestamp:** 2026-02-23T04:55:00+08:00

## Creation Summary

創建了關於加權 KL 散度（Weighted KL Divergence）的完整教學報告，針對馬爾可夫鏈檢驗的專業應用。內容包含第一性原理、數學推導、Python 實作代碼、實務應用工具，以及簡化的快查表和操作流程。

---

## 第一部分：教學報告（深入學習）

## 1. 第一性原理

### 1.1 為什麼需要加權 KL 散度？

**標準 KL 散度的假設：**
- KL 散度（Kullback-Leibler Divergence）用於衡量兩個機率分佈之間的距離
- 基本假設：**數據點是獨立同分佈（IID）**
- 公式：D_KL(P||Q) = Σ_x P(x) * log(P(x)/Q(x))

**馬爾可夫鏈的現實：**
- 在馬爾可夫鏈中，**當前狀態依賴於前一個狀態**
- 數據點之間存在**相關性**，不符合 IID 假設
- 系統有「記憶」，過去的狀態會影響未來

### 1.2 解決什麼根本問題？

**問題 1：狀態出現頻率不均等**
- 某些狀態是「常駐」狀態（steady state 中權重高）
- 某些狀態是「過渡」狀態（steady state 中權重低）

**問題 2：標準 KL 忽略狀態重要性**
- 所有轉移被同等對待
- 實際上，穩態中權重大的狀態應該被賦予更高權重

**問題 3：檢驗統計量的有效性**
- 標準檢驗在相關數據下會失去漸近最優性
- 需要一個能正確處理相關性的散度度量

### 1.3 核心洞察

**關鍵觀察：**
- 馬爾可夫鏈在長期運行後，會收斂到一個**穩態分佈** π
- 穩態分佈 π 告訴我們每個狀態在系統中出現的「重要性」
- 我們應該用穩態權重來加權每個條件分佈的 KL 散度

**加權 KL 散度公式：**
```
D_ℳ(Q || P) = Σ_i π_i * D_KL(Q(i,·) || P(i,·))
```

其中：
- π_i = 穩態分佈中狀態 i 的機率（權重）
- Q(i,·) = 模型 Q 從狀態 i 出發的轉移分佈
- P(i,·) = 真實分佈 P 從狀態 i 出發的轉移分佈

---

## 2. 數學推導

### 2.1 KL 散度基礎

**定義：**
D_KL(P || Q) = E_P[log(P(X)/Q(X))]

**性質：**
- D_KL(P || Q) ≥ 0，等號成立當且僅當 P = Q
- 不對稱：D_KL(P || Q) ≠ D_KL(Q || P)
- 可以理解為「用 Q 來編碼 P 時的額外訊息損失」

### 2.2 馬爾可夫鏈的設定

**馬爾可夫鏈定義：**
- 狀態空間：S = {1, 2, ..., N}
- 轉移矩陣：P(i→j) = P(X_{t+1}=j | X_t=i)
- 轉移矩陣滿足：Σ_j P(i→j) = 1 對所有 i

**穩態分佈：**
- π = (π_1, π_2, ..., π_N)
- 滿足：π = πP，即 π_j = Σ_i π_i * P(i→j)
- Σ_i π_i = 1

### 2.3 從條件 KL 到加權 KL

**條件 KL 散度（固定狀態 i）：**
```
D_KL(Q(i,·) || P(i,·)) = Σ_j Q(i→j) * log(Q(i→j) / P(i→j))
```

這衡量了在「當前狀態為 i」的情況下，模型 Q 和真實 P 的差異。

**平均條件 KL（錯誤做法）：**
```
(1/N) * Σ_i D_KL(Q(i,·) || P(i,·))
```
問題：平等對待所有狀態，忽略了狀態的重要性。

**加權 KL（正確做法）：**
```
D_ℳ(Q || P) = Σ_i π_i * D_KL(Q(i,·) || P(i,·))
```

**解釋：**
- 如果狀態 i 在穩態中經常出現（π_i 大），則其轉移差異更重要
- 如果狀態 i 很少出現（π_i 小），則其轉移差異重要性較低
- 這符合「長期運行」的視角

### 2.4 展開形式

將條件 KL 展開：
```
D_ℳ(Q || P)
= Σ_i π_i * [Σ_j Q(i→j) * log(Q(i→j) / P(i→j))]
= Σ_i Σ_j π_i * Q(i→j) * log(Q(i→j) / P(i→j))
```

**特殊情況：獨立數據**
如果數據是獨立的（即轉移分佈等於邊際分佈），則：
- π_i * Q(i→j) = Q(i,j) = Q(i)Q(j)（假設獨立）
- 加權 KL 退化為標準 KL

### 2.5 漸近最優性（Sethi et al., 2026）

**理論結果：**
- 對於馬爾可夫數據的序列檢驗問題
- 使用加權 KL 散度 D_ℳ 作為檢驗統計量的基礎
- 可以達到漸近最優的錯誤概率衰減率

**直觀理解：**
- 檢驗統計量的「檢測力」與散度大小相關
- 正確的散度度量（加權 KL）能反映真實的分布差異
- 因此能設計出最優的檢驗閾值

---

## 3. 實作代碼

### 3.1 基礎實作：計算加權 KL 散度

```python
import numpy as np
from typing import Tuple, Optional

class WeightedKLDivergence:
    """
    加權 KL 散度計算器，適用於馬爾可夫鏈檢驗
    
    公式：D_ℳ(Q || P) = Σ_i π_i * D_KL(Q(i,·) || P(i,·))
    """
    
    def __init__(self, states: list):
        """
        初始化
        
        參數:
            states: 狀態列表
        """
        self.states = states
        self.n_states = len(states)
        self.state_to_idx = {s: i for i, s in enumerate(states)}
    
    def compute_steady_state(self, transition_matrix: np.ndarray, 
                            max_iter: int = 1000, 
                            tol: float = 1e-10) -> np.ndarray:
        """
        計算馬爾可夫鏈的穩態分佈
        
        參數:
            transition_matrix: 轉移矩陣 P[i,j] = P(state_i -> state_j)
            max_iter: 最大迭代次數
            tol: 收斂容忍度
            
        返回:
            穩態分佈 π
        """
        # 從均勻分佈開始
        pi = np.ones(self.n_states) / self.n_states
        
        # 迭代直到收斂
        for _ in range(max_iter):
            pi_new = pi @ transition_matrix
            if np.linalg.norm(pi_new - pi, 1) < tol:
                break
            pi = pi_new
        
        return pi
    
    def kl_divergence(self, p: np.ndarray, q: np.ndarray, 
                     epsilon: float = 1e-10) -> float:
        """
        計算標準 KL 散度 D_KL(P || Q)
        
        參數:
            p, q: 機率分佈向量
            epsilon: 避免除以零的小常數
            
        返回:
            KL 散度值
        """
        # 平滑處理以避免 log(0)
        p = p + epsilon
        q = q + epsilon
        
        # 重新正規化
        p = p / p.sum()
        q = q / q.sum()
        
        return np.sum(p * np.log(p / q))
    
    def weighted_kl_divergence(self, 
                              transition_matrix_P: np.ndarray,
                              transition_matrix_Q: np.ndarray,
                              steady_state_P: Optional[np.ndarray] = None) -> float:
        """
        計算加權 KL 散度 D_ℳ(Q || P)
        
        參數:
            transition_matrix_P: 真實分佈的轉移矩陣
            transition_matrix_Q: 模型分佈的轉移矩陣
            steady_state_P: 真實分佈的穩態（若為 None 則自動計算）
            
        返回:
            加權 KL 散度值
        """
        # 計算穩態分佈（使用 P）
        if steady_state_P is None:
            steady_state_P = self.compute_steady_state(transition_matrix_P)
        
        # 計算加權 KL 散度
        weighted_kl = 0.0
        for i in range(self.n_states):
            # 從狀態 i 出發的轉移分佈
            p_i = transition_matrix_P[i, :]
            q_i = transition_matrix_Q[i, :]
            
            # 條件 KL 散度
            kl_i = self.kl_divergence(q_i, p_i)
            
            # 用穩態權重加權
            weighted_kl += steady_state_P[i] * kl_i
        
        return weighted_kl
    
    def compare_standard_vs_weighted(self,
                                    transition_matrix_P: np.ndarray,
                                    transition_matrix_Q: np.ndarray) -> dict:
        """
        比較標準 KL 散度和加權 KL 散度
        
        返回:
            包含兩種散度的字典
        """
        # 計算穩態
        pi = self.compute_steady_state(transition_matrix_P)
        
        # 加權 KL 散度
        weighted_kl = self.weighted_kl_divergence(transition_matrix_P, 
                                                  transition_matrix_Q,
                                                  pi)
        
        # 平均條件 KL（錯誤做法）
        avg_conditional_kl = 0.0
        for i in range(self.n_states):
            p_i = transition_matrix_P[i, :]
            q_i = transition_matrix_Q[i, :]
            avg_conditional_kl += self.kl_divergence(q_i, p_i)
        avg_conditional_kl /= self.n_states
        
        return {
            'weighted_kl': weighted_kl,
            'avg_conditional_kl': avg_conditional_kl,
            'steady_state': pi,
            'ratio': weighted_kl / avg_conditional_kl if avg_conditional_kl > 0 else 0
        }
```

### 3.2 範例：市場狀態檢測

```python
def market_state_example():
    """
    範例：使用加權 KL 散度檢測市場狀態變化
    """
    # 狀態定義：牛市、熊市、震盪
    states = ['Bull', 'Bear', 'Sideways']
    wkl = WeightedKLDivergence(states)
    
    # 正常市場的轉移矩陣（真實分佈 P）
    # 牛市傾向持續，熊市可能快速反轉，震盪狀態多變
    P = np.array([
        [0.7, 0.15, 0.15],  # Bull -> Bull/Bear/Sideways
        [0.2, 0.5, 0.3],   # Bear -> Bull/Bear/Sideways
        [0.25, 0.25, 0.5]  # Sideways -> Bull/Bear/Sideways
    ])
    
    # 觀察到的市場（模型 Q1）：接近正常
    Q1 = np.array([
        [0.68, 0.16, 0.16],
        [0.22, 0.48, 0.30],
        [0.26, 0.24, 0.50]
    ])
    
    # 異常市場（模型 Q2）：轉移模式完全不同
    Q2 = np.array([
        [0.3, 0.35, 0.35],  # Bull 很快轉換
        [0.4, 0.3, 0.3],    # Bear 很快反轉
        [0.33, 0.34, 0.33]  # Sideways 變化劇烈
    ])
    
    # 計算散度
    result1 = wkl.compare_standard_vs_weighted(P, Q1)
    result2 = wkl.compare_standard_vs_weighted(P, Q2)
    
    print("=" * 60)
    print("市場狀態檢測範例")
    print("=" * 60)
    print(f"\n穩態分佈（正常市場）:")
    for state, prob in zip(states, result1['steady_state']):
        print(f"  {state}: {prob:.4f}")
    
    print(f"\n案例 1：接近正常的市場")
    print(f"  加權 KL 散度: {result1['weighted_kl']:.6f}")
    print(f"  平均條件 KL: {result1['avg_conditional_kl']:.6f}")
    print(f"  比率: {result1['ratio']:.2f}")
    
    print(f"\n案例 2：異常市場")
    print(f"  加權 KL 散度: {result2['weighted_kl']:.6f}")
    print(f"  平均條件 KL: {result2['avg_conditional_kl']:.6f}")
    print(f"  比率: {result2['ratio']:.2f}")
    
    # 判斷
    threshold = 0.05
    print(f"\n檢驗閾值: {threshold}")
    print(f"案例 1: {'正常' if result1['weighted_kl'] < threshold else '異常'}")
    print(f"案例 2: {'正常' if result2['weighted_kl'] < threshold else '異常'}")
    
    return result1, result2

if __name__ == "__main__":
    market_state_example()
```

### 3.3 範例：時間序列變點檢測

```python
class ChangePointDetector:
    """
    使用加權 KL 散度的變點檢測器
    """
    
    def __init__(self, states: list, window_size: int = 100, 
                 threshold: float = 0.05):
        """
        初始化檢測器
        
        參數:
            states: 狀態列表
            window_size: 計算轉移矩陣的窗口大小
            threshold: 檢測閾值
        """
        self.wkl = WeightedKLDivergence(states)
        self.window_size = window_size
        self.threshold = threshold
        self.baseline_matrix = None
        self.baseline_steady_state = None
    
    def fit(self, sequence: list):
        """
        訓練：從基準序列計算基準轉移矩陣
        
        參數:
            sequence: 狀態序列
        """
        self.baseline_matrix = self._estimate_transition_matrix(sequence)
        self.baseline_steady_state = self.wkl.compute_steady_state(
            self.baseline_matrix
        )
        print(f"基準模型已建立，穩態: {self.baseline_steady_state}")
    
    def _estimate_transition_matrix(self, sequence: list) -> np.ndarray:
        """
        從序列估計轉移矩陣
        """
        n = len(self.wkl.states)
        count_matrix = np.zeros((n, n))
        
        # 計算轉移次數
        for i in range(len(sequence) - 1):
            from_state = self.wkl.state_to_idx[sequence[i]]
            to_state = self.wkl.state_to_idx[sequence[i + 1]]
            count_matrix[from_state, to_state] += 1
        
        # 正規化
        transition_matrix = count_matrix / count_matrix.sum(axis=1, keepdims=True)
        
        # 處理全零行（平滑）
        transition_matrix = np.nan_to_num(transition_matrix, nan=1.0/n)
        transition_matrix = transition_matrix / transition_matrix.sum(axis=1, keepdims=True)
        
        return transition_matrix
    
    def detect(self, sequence: list, step_size: int = 10) -> list:
        """
        檢測變點
        
        參數:
            sequence: 監測序列
            step_size: 每次移動的步長
            
        返回:
            檢測結果列表，每個元素包含 (index, divergence, is_anomaly)
        """
        results = []
        
        for start in range(0, len(sequence) - self.window_size, step_size):
            end = start + self.window_size
            window = sequence[start:end]
            
            # 估計當前窗口的轉移矩陣
            current_matrix = self._estimate_transition_matrix(window)
            
            # 計算加權 KL 散度
            divergence = self.wkl.weighted_kl_divergence(
                self.baseline_matrix,
                current_matrix,
                self.baseline_steady_state
            )
            
            is_anomaly = divergence > self.threshold
            
            results.append({
                'index': end,
                'divergence': divergence,
                'is_anomaly': is_anomaly,
                'window': window
            })
        
        return results
    
    def plot_results(self, results: list):
        """
        視覺化檢測結果
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print("需要安裝 matplotlib: pip install matplotlib")
            return
        
        indices = [r['index'] for r in results]
        divergences = [r['divergence'] for r in results]
        anomalies = [r['is_anomaly'] for r in results]
        
        plt.figure(figsize=(12, 4))
        
        # 散度曲線
        plt.plot(indices, divergences, 'b-', label='加權 KL 散度')
        plt.axhline(y=self.threshold, color='r', linestyle='--', 
                   label=f'閾值 ({self.threshold})')
        
        # 標記異常點
        anomaly_indices = [indices[i] for i, a in enumerate(anomalies) if a]
        anomaly_divergences = [divergences[i] for i, a in enumerate(anomalies) if a]
        plt.scatter(anomaly_indices, anomaly_divergences, 
                   color='red', s=100, zorder=5, label='檢測到變點')
        
        plt.xlabel('時間點')
        plt.ylabel('加權 KL 散度')
        plt.title('變點檢測結果')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

# 使用範例
def change_point_detection_example():
    """
    變點檢測範例
    """
    import random
    
    states = ['A', 'B', 'C']
    detector = ChangePointDetector(states, window_size=50, threshold=0.03)
    
    # 生成基準序列（第一個馬爾可夫鏈）
    baseline_sequence = []
    current = 'A'
    P1 = {
        'A': {'A': 0.7, 'B': 0.2, 'C': 0.1},
        'B': {'A': 0.3, 'B': 0.5, 'C': 0.2},
        'C': {'A': 0.2, 'B': 0.3, 'C': 0.5}
    }
    for _ in range(200):
        baseline_sequence.append(current)
        probs = list(P1[current].values())
        next_states = list(P1[current].keys())
        current = random.choices(next_states, weights=probs)[0]
    
    # 訓練檢測器
    detector.fit(baseline_sequence[:150])
    
    # 生成監測序列（前半正常，後半異常）
    monitoring_sequence = []
    current = 'A'
    
    # 前 100 點：正常
    for _ in range(100):
        monitoring_sequence.append(current)
        probs = list(P1[current].values())
        next_states = list(P1[current].keys())
        current = random.choices(next_states, weights=probs)[0]
    
    # 後 100 點：變化（第二個馬爾可夫鏈）
    P2 = {
        'A': {'A': 0.3, 'B': 0.4, 'C': 0.3},
        'B': {'A': 0.4, 'B': 0.2, 'C': 0.4},
        'C': {'A': 0.3, 'B': 0.4, 'C': 0.3}
    }
    for _ in range(100):
        monitoring_sequence.append(current)
        probs = list(P2[current].values())
        next_states = list(P2[current].keys())
        current = random.choices(next_states, weights=probs)[0]
    
    # 檢測
    results = detector.detect(monitoring_sequence, step_size=5)
    
    # 總結結果
    anomaly_count = sum(1 for r in results if r['is_anomaly'])
    print(f"\n檢測到 {anomaly_count} 個異常窗口")
    
    # 找到第一個異常點
    first_anomaly = next((r for r in results if r['is_anomaly']), None)
    if first_anomaly:
        print(f"第一個異常檢測於位置 {first_anomaly['index']}")
        print(f"（變點實際約在位置 100 附近）")
    
    # 視覺化
    detector.plot_results(results)
    
    return results

if __name__ == "__main__":
    change_point_detection_example()
```

---

## 4. 應用案例

### 4.1 金融市場狀態監控

**場景描述：**
- 監控市場在牛市、熊市、震盪狀態之間的轉移模式
- 檢測市場結構性變化（如政策變更、重大事件）

**實作步驟：**
1. 從歷史數據估計基準轉移矩陣
2. 計算穩態分佈（了解市場的正常佔比）
3. 實時監控新數據，計算加權 KL 散度
4. 當散度超過閾值時發出警報

**優勢：**
- 自動識別狀態（無需人工標註）
- 考慮狀態的重要性（牛市/熊市比震盪更重要）
- 對噪音有魯棒性（短期波動不會觸發）

### 4.2 網路流量異常檢測

**場景描述：**
- 網路狀態：正常、擁塞、攻擊
- 監控狀態轉移模式，檢測 DDoS 攻擊或異常流量

**應用方式：**
- 訓練：從正常時期的流量數據建立基準模型
- 檢測：實時計算加權 KL 散度
- 響應：超閾值時觸發防護機制

### 4.3 用戶行為分析

**場景描述：**
- 電商平台用戶狀態：瀏覽、加入購物車、結帳、流失
- 檢測用戶行為模式變化（如促銷活動效果）

**實用價值：**
- 評估活動效果（活動後行為模式是否改變）
- 識別流失風險（某些狀態轉移異常）
- 優化用戶體驗（找出低效的狀態轉換）

### 4.4 生物序列分析

**場景描述：**
- 基因或蛋白質序列的狀態轉移
- 檢測突變或疾病標記

**應用：**
- 比較健康和病患的狀態轉移模式
- 加權 KL 散度量化差異程度
- 輔助診斷和藥物開發

---

## 第二部分：簡化應用（實務工具）

## 5. 簡化公式

### 5.1 核心公式（記住這個）

```
加權 KL = Σ (權重 × 條件 KL)

權重 = 狀態重要性（穩態機率）
條件 KL = 在該狀態下，兩個模型的差異
```

### 5.2 計算步驟

```
步驟 1：計算穩態分佈 π
  → 系統長期運行後，各狀態的出現機率

步驟 2：對每個狀態 i
  → 計算條件 KL：D_KL(Q(i,·) || P(i,·))
  → 用穩態權重 π_i 加權

步驟 3：加總
  → 所有狀態的加權貢獻
```

### 5.3 直觀理解

**類比：評估兩個司機的駕駛習慣**

- 標準 KL：比較每個路口的轉向，平等對待
- 加權 KL：比較每個路口的轉向，但常走路口的權重更高

為什麼？因為常走路口的習慣更能反映真實風格。

---

## 6. 快查表（30 秒查詢）

### 6.1 何時使用加權 KL？

| 情況 | 使用 | 原因 |
|------|------|------|
| 數據獨立（IID） | 標準 KL | 無相關性 |
| 時間序列/馬爾可夫鏈 | 加權 KL | 數據相關 |
| 需考慮狀態重要性 | 加權 KL | 穩態權重 |
| 所有狀態等價 | 標準/平均 KL | 無需加權 |

### 6.2 計算步驟快查

```python
# 1. 初始化
wkl = WeightedKLDivergence(states)

# 2. 計算穩態
pi = wkl.compute_steady_state(transition_matrix)

# 3. 計算加權 KL
result = wkl.weighted_kl_divergence(P, Q, pi)
```

### 6.3 閾值設定指南

| 應用 | 建議閾值 | 說明 |
|------|----------|------|
| 高敏感檢測（安全） | 0.01 - 0.02 | 寧可誤報，不可漏報 |
| 一般檢測（金融） | 0.05 - 0.1 | 平衡靈敏度和誤報 |
| 低敏感（統計） | 0.1 - 0.2 | 減少誤報 |

### 6.4 常見問題速解

| 問題 | 解決方案 |
|------|----------|
| 散度為 NaN | 添加 epsilon 平滑 |
| 散度過大 | 檢查轉移矩陣是否正規化 |
| 穩態不收斂 | 增加迭代次數，檢查鏈是否不可約 |
| 檢測效果差 | 調整閾值或窗口大小 |

---

## 7. 3 分鐘操作流程

### 7.1 第一次使用（設定基準）

```
分鐘 0-1：準備數據
  ✓ 收集正常時期的狀態序列
  ✓ 定義狀態列表（如：['A', 'B', 'C']）

分鐘 1-2：建立基準
  ✓ 初始化：wkl = WeightedKLDivergence(states)
  ✓ 估計轉移矩陣：baseline_matrix = estimate(sequence)
  ✓ 計算穩態：pi = wkl.compute_steady_state(baseline_matrix)

分鐘 2-3：設定閾值
  ✓ 使用驗證數據測試
  ✓ 選擇能區分正常/異常的閾值
  ✓ 記錄：threshold = X
```

### 7.2 日常使用（監控）

```
步驟 1：收集新數據（10秒）
  → 獲取最新的狀態序列窗口

步驟 2：計算散度（20秒）
  → 估計當前轉移矩陣
  → 計算加權 KL：divergence = wkl.weighted_kl(P, Q, pi)

步驟 3：判斷（10秒）
  → divergence < threshold ✓ 正常
  → divergence ≥ threshold ⚠ 異常，需進一步檢查
```

### 7.3 異常處理

```
如果檢測到異常：

1. 驗證（1分鐘）
   ✓ 檢查數據品質（是否有錯誤）
   ✓ 確認不是短暫波動

2. 分析（1分鐘）
   ✓ 找出貢獻最大的狀態
   ✓ 檢查該狀態的轉移模式

3. 行動（1分鐘）
   ✓ 通知相關人員
   ✓ 記錄異常事件
   ✓ 必要時更新基準
```

---

## 8. 實務工具類

### 8.1 快速開始工具類

```python
import numpy as np
from typing import List, Dict, Tuple, Optional

class QuickWeightedKL:
    """
    快速加權 KL 工具類
    設計目標：3 行代碼完成檢測
    """
    
    def __init__(self, states: List[str]):
        self.states = states
        self.n = len(states)
        self.idx = {s: i for i, s in enumerate(states)}
        self.baseline_P = None
        self.baseline_pi = None
    
    def train(self, sequence: List[str]) -> Dict:
        """
        從序列訓練基準模型
        
        使用方式:
            wkl = QuickWeightedKL(['A', 'B', 'C'])
            info = wkl.train(my_sequence)  # 建立基準
        
        返回:
            訓練資訊字典
        """
        self.baseline_P = self._estimate_matrix(sequence)
        self.baseline_pi = self._steady_state(self.baseline_P)
        
        return {
            'states': self.states,
            'steady_state': dict(zip(self.states, self.baseline_pi)),
            'transition_matrix': self.baseline_P
        }
    
    def detect(self, sequence: List[str], threshold: float = 0.05) -> Dict:
        """
        檢測序列是否偏離基準
        
        使用方式:
            result = wkl.detect(new_sequence, threshold=0.05)
            if result['is_anomaly']:
                print("檢測到異常！")
        
        返回:
            檢測結果字典
        """
        if self.baseline_P is None:
            raise ValueError("請先使用 train() 建立基準")
        
        Q = self._estimate_matrix(sequence)
        divergence = self._weighted_kl(self.baseline_P, Q, self.baseline_pi)
        
        # 找出貢獻最大的狀態
        contributions = self._analyze_contributions(self.baseline_P, Q)
        
        return {
            'divergence': divergence,
            'threshold': threshold,
            'is_anomaly': divergence >= threshold,
            'top_contributors': contributions[:3],
            'transition_matrix': Q
        }
    
    def _estimate_matrix(self, seq: List[str]) -> np.ndarray:
        """估計轉移矩陣"""
        count = np.zeros((self.n, self.n))
        for i in range(len(seq) - 1):
            from_i = self.idx[seq[i]]
            to_i = self.idx[seq[i + 1]]
            count[from_i, to_i] += 1
        
        # 平滑並正規化
        P = count + 1e-6
        return P / P.sum(axis=1, keepdims=True)
    
    def _steady_state(self, P: np.ndarray, max_iter: int = 1000) -> np.ndarray:
        """計算穩態"""
        pi = np.ones(self.n) / self.n
        for _ in range(max_iter):
            pi_new = pi @ P
            if np.linalg.norm(pi_new - pi, 1) < 1e-10:
                break
            pi = pi_new
        return pi
    
    def _kl(self, p: np.ndarray, q: np.ndarray) -> float:
        """標準 KL 散度"""
        epsilon = 1e-10
        p_safe = p + epsilon
        q_safe = q + epsilon
        return np.sum(p_safe * np.log(p_safe / q_safe))
    
    def _weighted_kl(self, P: np.ndarray, Q: np.ndarray, pi: np.ndarray) -> float:
        """加權 KL 散度"""
        total = 0.0
        for i in range(self.n):
            total += pi[i] * self._kl(Q[i, :], P[i, :])
        return total
    
    def _analyze_contributions(self, P: np.ndarray, Q: np.ndarray) -> List[Dict]:
        """分析各狀態的貢獻"""
        pi = self.baseline_pi
        contributions = []
        
        for i in range(self.n):
            kl_i = self._kl(Q[i, :], P[i, :])
            contributions.append({
                'state': self.states[i],
                'contribution': pi[i] * kl_i,
                'weight': pi[i],
                'kl': kl_i
            })
        
        # 按貢獻排序
        contributions.sort(key=lambda x: x['contribution'], reverse=True)
        return contributions


# ============ 使用範例 ============

def demo_quick_usage():
    """示範 3 分鐘快速使用"""
    
    # === 第一步：訓練（1 分鐘）===
    states = ['Up', 'Down', 'Flat']
    wkl = QuickWeightedKL(states)
    
    # 模擬正常市場數據
    import random
    normal_sequence = []
    current = 'Up'
    transitions = {
        'Up': {'Up': 0.7, 'Down': 0.15, 'Flat': 0.15},
        'Down': {'Up': 0.3, 'Down': 0.5, 'Flat': 0.2},
        'Flat': {'Up': 0.25, 'Down': 0.25, 'Flat': 0.5}
    }
    for _ in range(200):
        normal_sequence.append(current)
        next_options = list(transitions[current].keys())
        weights = list(transitions[current].values())
        current = random.choices(next_options, weights=weights)[0]
    
    # 訓練
    info = wkl.train(normal_sequence)
    print("✓ 基準模型已建立")
    print(f"  穩態分佈: {info['steady_state']}")
    
    # === 第二步：檢測（1 分鐘）===
    # 模擬正常市場
    test_normal = normal_sequence[-50:]
    result_normal = wkl.detect(test_normal, threshold=0.05)
    print(f"\n正常市場檢測:")
    print(f"  散度: {result_normal['divergence']:.4f}")
    print(f"  結果: {'正常 ✓' if not result_normal['is_anomaly'] else '異常 ⚠'}")
    
    # 模擬異常市場
    test_abnormal = []
    current = 'Up'
    abnormal_transitions = {
        'Up': {'Up': 0.3, 'Down': 0.35, 'Flat': 0.35},
        'Down': {'Up': 0.4, 'Down': 0.3, 'Flat': 0.3},
        'Flat': {'Up': 0.33, 'Down': 0.34, 'Flat': 0.33}
    }
    for _ in range(50):
        test_abnormal.append(current)
        next_options = list(abnormal_transitions[current].keys())
        weights = list(abnormal_transitions[current].values())
        current = random.choices(next_options, weights=weights)[0]
    
    result_abnormal = wkl.detect(test_abnormal, threshold=0.05)
    print(f"\n異常市場檢測:")
    print(f"  散度: {result_abnormal['divergence']:.4f}")
    print(f"  結果: {'正常 ✓' if not result_abnormal['is_anomaly'] else '異常 ⚠'}")
    
    # === 第三步：分析（1 分鐘）===
    if result_abnormal['is_anomaly']:
        print(f"\n異常分析:")
        print(f"  主要貢獻狀態:")
        for contrib in result_abnormal['top_contributors']:
            print(f"    - {contrib['state']}: 貢獻 {contrib['contribution']:.4f}")
            print(f"      (權重: {contrib['weight']:.3f}, KL: {contrib['kl']:.4f})")
    
    return wkl, result_normal, result_abnormal


if __name__ == "__main__":
    demo_quick_usage()
```

### 8.2 批量檢測工具

```python
class BatchDetector:
    """
    批量檢測工具
    適用於：監控多個時間序列或多個實體
    """
    
    def __init__(self, states: List[str]):
        self.wkl = QuickWeightedKL(states)
        self.entities = {}  # {entity_id: baseline}
    
    def add_entity(self, entity_id: str, sequence: List[str]):
        """為某個實體添加基準模型"""
        info = self.wkl.train(sequence)
        self.entities[entity_id] = {
            'P': info['transition_matrix'],
            'pi': self.wkl.baseline_pi
        }
        return info
    
    def detect_batch(self, data: Dict[str, List[str]], 
                     threshold: float = 0.05) -> Dict:
        """
        批量檢測多個實體
        
        參數:
            data: {entity_id: sequence}
            threshold: 檢測閾值
            
        返回:
            {entity_id: result}
        """
        results = {}
        for entity_id, sequence in data.items():
            if entity_id not in self.entities:
                # 如果沒有基準，跳過或建立基準
                continue
            
            baseline = self.entities[entity_id]
            Q = self.wkl._estimate_matrix(sequence)
            divergence = self.wkl._weighted_kl(
                baseline['P'], Q, baseline['pi']
            )
            
            results[entity_id] = {
                'divergence': divergence,
                'is_anomaly': divergence >= threshold,
                'threshold': threshold
            }
        
        return results
    
    def get_anomaly_report(self, results: Dict) -> str:
        """生成異常報告"""
        anomalies = [eid for eid, r in results.items() if r['is_anomaly']]
        
        report = f"檢測完成\n"
        report += f"  總數: {len(results)}\n"
        report += f"  正常: {len(results) - len(anomalies)}\n"
        report += f"  異常: {len(anomalies)}\n"
        
        if anomalies:
            report += f"\n異常實體:\n"
            for eid in anomalies:
                report += f"  - {eid}: 散度 {results[eid]['divergence']:.4f}\n"
        
        return report


# 使用範例
def batch_demo():
    """批量檢測範例"""
    import random
    
    states = ['A', 'B', 'C']
    detector = BatchDetector(states)
    
    # 為 3 個實體建立基準
    for entity_id in ['User1', 'User2', 'User3']:
        # 生成正常序列
        seq = []
        current = random.choice(states)
        for _ in range(100):
            seq.append(current)
            current = random.choice(states)  # 隨機漫步
        detector.add_entity(entity_id, seq)
    
    # 生成測試數據
    test_data = {}
    for entity_id in ['User1', 'User2', 'User3']:
        seq = []
        current = random.choice(states)
        for _ in range(50):
            seq.append(current)
            current = random.choice(states)
        test_data[entity_id] = seq
    
    # User3 行為變化（異常）
    test_data['User3'] = [random.choice(['A', 'A', 'A']) for _ in range(50)]
    
    # 批量檢測
    results = detector.detect_batch(test_data, threshold=0.1)
    
    # 生成報告
    report = detector.get_anomaly_report(results)
    print(report)
    
    return results
```

---

## 9. 進階主題

### 9.1 對稱加權 KL 散度

標準加權 KL 不對稱（D_ℳ(Q||P) ≠ D_ℳ(P||Q)），有時需要對稱版本：

```
對稱加權 KL = D_ℳ(Q||P) + D_ℳ(P||Q)
```

應用：當兩個模型地位平等時（如比較兩個時期的市場）。

### 9.2 自適應閾值

固定閾值可能不適應動態環境，可使用：

1. **歷史百分位數**：閾值 = 歷史散度的 95th 百分位
2. **移動平均**：閾值 = 過去 N 次散度的平均值 + k × 標準差
3. **動態調整**：根據虛警率自動調整閥值

### 9.3 多維狀態空間

當狀態是多維（如 [價格趨勢, 交易量]）：

1. 離散化：將連續值映射到離散狀態
2. 使用高階馬爾可夫鏈（考慮多步歷史）
3. 結合特徵工程

---

## 10. 總結

### 10.1 核心要點

| 要點 | 說明 |
|------|------|
| **為什麼需要** | 馬爾可夫鏈數據相關，標準 KL 假設獨立 |
| **核心思想** | 用穩態權重加權條件 KL 散度 |
| **公式** | D_ℳ(Q||P) = Σ π_i × D_KL(Q(i,·)\|\|P(i,·)) |
| **優勢** | 正確處理相關性，考慮狀態重要性 |
| **應用** | 時間序列檢驗、市場監控、異常檢測 |

### 10.2 實作檢查清單

- [ ] 確認數據是馬爾可夫鏈（存在狀態轉移）
- [ ] 正確估計轉移矩陣（注意平滑）
- [ ] 計算穩態分佈（確保收斂）
- [ ] 選擇合適的閾值（使用驗證數據）
- [ ] 處理邊界情況（NaN、零機率）
- [ ] 監控檢測性能（虛警率、漏報率）

### 10.3 參考資料

1. **Sethi et al. (2026)**. *Asymptotically Optimal Sequential Testing with Markovian Data*
2. Kullback, S., & Leibler, R. A. (1951). *On information and sufficiency*
3. Bishop, C. M. (2006). *Pattern Recognition and Machine Learning*

---

## 附錄 A：完整代碼清單

所有代碼已整合在教學報告中，可直接複製使用：

1. `WeightedKLDivergence` - 完整的加權 KL 計算器
2. `ChangePointDetector` - 變點檢測器
3. `QuickWeightedKL` - 快速實務工具
4. `BatchDetector` - 批量檢測工具

## 附錄 B：安裝依賴

```bash
pip install numpy matplotlib
```

核心實作只需 numpy；matplotlib 僅用於可視化（可選）。

## 附錄 C：故障排除

| 問題 | 可能原因 | 解決方案 |
|------|----------|----------|
| `ValueError: sum(p) != 1` | 轉移矩陣未正規化 | 檢查 `_estimate_matrix` 的正規化 |
| `RuntimeWarning: divide by zero` | 機率為零 | 添加 epsilon 平滑 |
| 穩態不收斂 | 馬爾可夫鏈不可約或非週期性 | 檢查鏈的性質，增加迭代次數 |
| 檢測效果差 | 閾值不當 | 使用驗證數據調整閥值 |

---

**END OF REPORT**

---

## Creation Notes

- **Type:** technical tutorial / report
- **Audience:** data scientists, quantitative researchers, engineers working with time series
- **Tone:** professional, educational, practical
- **Word count:** ~6,000 words
- **Language:** 繁體中文

## Metadata

- **Based on:** Sethi et al. (2026) - Asymptotically Optimal Sequential Testing with Markovian Data
- **Suggestions:** 
  - 可擴展至非齊次馬爾可夫鏈（時變轉移矩陣）
  - 可結合深度學習自動學習狀態表示
  - 可添加更多實際領域的案例研究
- **Limitations:**
  - 假設已知狀態空間；實際應用可能需要狀態發現
  - 轉移矩陣估計需要足夠數據
  - 閾值選擇需要領域知識或驗證數據
