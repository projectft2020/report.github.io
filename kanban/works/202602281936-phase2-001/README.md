# 美股前 30 股票相關性分析與組合優化

## 快速開始

### 1. 安裝依賴

```bash
pip install yfinance numpy pandas matplotlib seaborn networkx scikit-learn scipy
```

### 2. 運行完整分析

```bash
python correlation_analysis_notebook.py
```

這將執行以下步驟：

1. ✅ 數據獲取（美股前 30 股票，2020-2026）
2. ✅ 數據清理
3. ✅ 相關性分析（驗證 Preis 等人的發現）
4. ✅ 網絡分析（MST、社群檢測）
5. ✅ 投資組合構建（MST 基礎、特徵組合）
6. ✅ 回測驗證
7. ✅ 策略比較

### 3. 預期輸出

**數據文件：**
- `mst_weights.csv` - MST 投資組合權重
- `ensemble_weights.csv` - 特徵組合權重
- `equal_weights.csv` - 等權重基準權重
- `strategy_comparison.csv` - 策略績效對比
- `network_metrics.csv` - 網絡指標

**可視化圖表：**
- `correlation_trend_analysis.png` - 相關性趨勢分析
- `mst_network.png` - MST 網絡結構
- `strategy_comparison.png` - 策略累積收益曲線對比

---

## 研究目標

### 核心目標

1. **驗證 Preis 等人的相關性破壞現象**
   - 在 2020-2026 年的美股市場中，是否仍然存在「市場壓力時相關性增加」的現象？
   - 線性關係：C- = -0.085R + 0.267（負回報）
   - 線性關係：C+ = 0.064R + 0.188（正回報）

2. **構建網絡分析系統**
   - 最小生成樹（MST）揭示股票間的層級結構
   - 社群檢測識別股票群組
   - 中心性分析找出系統性重要股票

3. **開發組合優化策略**
   - MST 基礎投資組合（反度權重）
   - 特徵組合（Eigen Portfolios）
   - 動態相關性調整策略

4. **回測驗證**
   - 在 2020-2026 年期間回測
   - 比較不同策略的績效
   - 驗證策略優勢

---

## 研究方法

### 相關性分析

**Preis 等人的方法：**
1. 計算滾動相關性矩陣（窗口：252 個交易日）
2. 計算平均相關性（排除對角線）
3. 標準化市場指數回報
4. 分離正負市場回報
5. 線性回歸：C = a×R + b

**預期結果：**
- 負回報時相關性斜率更大（|a-| > a+）
- 相關性破壞現象：市場下跌時相關性顯著增加

### 網絡分析

**Mantegna 的方法：**
1. 將相關性轉為距離：d_ij = √[2(1 - ρ_ij)]
2. 構建完全圖
3. 計算最小生成樹（MST）
4. 分析網絡指標（度中心性、介數中心性等）

**網絡指標：**
- **度中心性**：連接數量，識別系統性重要股票
- **介數中心性**：位於最短路徑上的頻率
- **特徵向量中心性**：與重要節點連接的程度
- **社群檢測**：識別股票群組

### 投資組合優化

**MST 基礎投資組合：**
- 權重 = 1 / (度中心性 + 0.01)
- 懲罰中心性高的節點（系統性風險）
- 提供真正的分散投資

**特徵組合（Eigen Portfolios）：**
- PCA 分解相關性矩陣
- 選擇前 k 個特徵向量
- 構建不相關的投資組合
- 組合策略減少過擬合

---

## 代碼結構

### 主要函數

**數據處理：**
- `get_stock_data()` - 獲取股票歷史數據
- `clean_data()` - 清理數據（缺失值、異常值）

**相關性分析：**
- `calculate_rolling_correlation()` - 計算滾動相關性
- `analyze_average_correlation_trend()` - 分析平均相關性趨勢
- `plot_correlation_trend()` - 繪製相關性趨勢圖

**網絡分析：**
- `correlation_to_distance()` - 相關性轉距離
- `build_mst()` - 構建最小生成樹
- `calculate_network_metrics()` - 計算網絡指標
- `detect_communities()` - 社群檢測
- `plot_mst_network()` - 繪製 MST 網絡

**投資組合：**
- `mst_based_portfolio()` - MST 基礎投資組合
- `eigen_portfolios()` - 特徵組合
- `equal_weight_portfolio()` - 等權重基準

**回測：**
- `backtest_strategy()` - 回測單一策略
- `compare_strategies()` - 比較多個策略

---

## 預期結果

### 相關性分析

**Preis 現象驗證：**
```
正回報：C = 0.064R + 0.188 (R² ≈ 0.15)
負回報：C = -0.085R + 0.267 (R² ≈ 0.25)

結論：✅ 確認相關性破壞現象！
```

### 網絡分析

**MST 結構：**
- 節點：30 隻股票
- 邊：29 條邊
- 網絡密度：0.067
- 網絡直徑：~8-10

**中心性前 5 名（預期）：**
1. AAPL（科技中心）
2. MSFT（科技中心）
3. GOOGL（科技中心）
4. JPM（金融中心）
5. V（支付中心）

**社群檢測（預期）：**
- 社群 1：科技股（AAPL, MSFT, GOOGL, NVDA, META）
- 社群 2：金融股（JPM, BAC, GS, V, MA）
- 社群 3：消費股（HD, WMT, NKE, MCD, KO, PEP）
- 社群 4：能源股（XOM, CVX）
- 社群 5：醫療股（UNH, PFE, MRK, ABBV）

### 策略績效對比

**預期結果（基於文獻）：**

| 策略 | 年化收益 | 年化波動 | 夏普比率 | 最大回撤 | Calmar比率 |
|------|---------|---------|---------|---------|-----------|
| 等權重基準 | 12-15% | 18-22% | 0.60-0.75 | -30% ~ -40% | 0.35-0.45 |
| MST 投資組合 | 13-16% | 16-20% | 0.70-0.85 | -25% ~ -35% | 0.45-0.60 |
| 特徵組合 | 14-18% | 15-19% | 0.80-0.95 | -20% ~ -30% | 0.55-0.75 |

**關鍵發現：**
- MST 和特徵組合優於等權重基準
- 夏普比率提升：+15% ~ +30%
- 最大回撤降低：-20% ~ -35%
- Calmar 比率提升：+30% ~ +60%

---

## 進階功能

### 1. 動態相關性調整策略

如果你想實施動態相關性調整，可以添加以下代碼：

```python
def dynamic_correlation_adjustment(returns, window=252, target_volatility=0.10):
    """
    動態相關性調整策略
    """
    weights_history = []
    portfolio_returns = []
    
    for i in range(window, len(returns)):
        # 訓練數據
        train_returns = returns.iloc[i-window:i]
        
        # 計算相關性矩陣
        corr_matrix = train_returns.corr()
        
        # 構建 MST
        distance_matrix = correlation_to_distance(corr_matrix.values)
        G = nx.from_numpy_array(distance_matrix)
        mst = nx.minimum_spanning_tree(G)
        
        # 計算 MST 基礎權重
        degree_centrality = nx.degree_centrality(mst)
        base_weights = pd.Series({node: 1.0 / (dc + 0.01)
                                 for node, dc in degree_centrality.items()})
        base_weights = base_weights / base_weights.sum()
        
        # 根據波動率調整
        volatilities = train_returns.std() * np.sqrt(252)
        adjusted_weights = base_weights.copy()
        for stock in base_weights.index:
            if stock in volatilities.index:
                adjusted_weights[stock] = (base_weights[stock] *
                                         target_volatility / volatilities[stock])
        
        # 歸一化
        adjusted_weights = adjusted_weights / adjusted_weights.sum()
        
        # 計算當期回報
        current_returns = returns.iloc[i]
        portfolio_return = (adjusted_weights * current_returns).sum()
        
        weights_history.append(adjusted_weights)
        portfolio_returns.append(portfolio_return)
    
    return pd.DataFrame(weights_history), pd.Series(portfolio_returns)
```

### 2. 機器學習擴展

如果你想使用機器學習預測相關性變化：

```python
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit

def train_correlation_predictor(returns, window=252, forecast_horizon=5):
    """
    訓練相關性預測模型
    """
    # 準備特徵
    features = []
    targets = []
    
    for i in range(window, len(returns) - forecast_horizon):
        # 歷史相關性
        historical_corr = returns.iloc[i-window:i].corr()
        avg_corr = historical_corr.values[np.triu_indices_from(historical_corr.values, k=1)].mean()
        
        # 市場狀態
        market_return = returns.iloc[i-window:i].mean(axis=1).mean()
        market_volatility = returns.iloc[i-window:i].mean(axis=1).std()
        
        # 未來相關性
        future_corr = returns.iloc[i:i+forecast_horizon].corr()
        future_avg_corr = future_corr.values[np.triu_indices_from(future_corr.values, k=1)].mean()
        
        features.append([avg_corr, market_return, market_volatility])
        targets.append(future_avg_corr)
    
    # 訓練模型
    X = np.array(features)
    y = np.array(targets)
    
    # 時間序列交叉驗證
    tscv = TimeSeriesSplit(n_splits=5)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    
    scores = cross_val_score(model, X, y, cv=tscv, scoring='neg_mean_squared_error')
    print(f"交叉驗證 MSE: {-scores.mean():.6f}")
    
    # 訓練最終模型
    model.fit(X, y)
    
    return model
```

### 3. 壓力測試

如果你想進行壓力測試：

```python
def stress_test_portfolio(weights, returns, scenarios):
    """
    壓力測試
    """
    results = {}
    
    for scenario_name, scenario_params in scenarios.items():
        # 應用場景
        shocked_returns = returns.copy()
        
        if 'correlation_shock' in scenario_params:
            # 相關性衝擊
            new_corr = scenario_params['correlation_shock']
            shocked_returns = shocked_returns.apply(lambda x: x + new_corr * x.mean())
        
        if 'volatility_shock' in scenario_params:
            # 波動率衝擊
            vol_multiplier = scenario_params['volatility_shock']
            shocked_returns = shocked_returns * vol_multiplier
        
        # 計算組合回報
        portfolio_return = (shocked_returns * weights).sum(axis=1)
        
        # 計算風險指標
        annual_return = portfolio_return.mean() * 252
        annual_volatility = portfolio_return.std() * np.sqrt(252)
        max_drawdown = (1 + portfolio_return).cumprod().div((1 + portfolio_return).cumprod().cummax()).sub(1).min()
        
        results[scenario_name] = {
            'annual_return': annual_return,
            'annual_volatility': annual_volatility,
            'max_drawdown': max_drawdown
        }
    
    return pd.DataFrame(results).T

# 定義場景
scenarios = {
    '正常市場': {},
    '相關性破壞': {'correlation_shock': 0.7},  # 相關性增加到 0.7
    '波動率翻倍': {'volatility_shock': 2.0},  # 波動率翻倍
    '雙重衝擊': {'correlation_shock': 0.7, 'volatility_shock': 2.0}
}

# 執行壓力測試
stress_results = stress_test_portfolio(mst_weights, cleaned_returns, scenarios)
print(stress_results)
```

---

## 常見問題

### Q1: 數據下載失敗怎麼辦？

**A:** 檢查網絡連接，yfinance 依賴 Yahoo Finance API。如果持續失敗，可以：
1. 嘗試使用 VPN
2. 縮短時間範圍（如 `start_date='2022-01-01'`）
3. 使用其他數據源（如 Alpha Vantage、Quandl）

### Q2: 運行時間太長怎麼辦？

**A:** 可以優化：
1. 減少股票數量（從 30 隻減到 15-20 隻）
2. 縮短滾動窗口（從 252 天減到 126 天）
3. 使用更快的硬件（GPU 加速）

### Q3: 如何解釋網絡圖？

**A:**
- **節點大小**：度中心性，越大表示該股票越重要
- **節點顏色**：社群，相同顏色表示股票屬於同一個群組
- **邊**：距離，越短表示相關性越高
- **網絡結構**：層級結構，反映股票間的相互依賴

### Q4: 策略績效不如預期怎麼辦？

**A:** 可能原因：
1. 市場環境變化（2020-2026 有 COVID、量化寬鬆等事件）
2. 交易成本未考慮
3. 流動性限制
4. 模型過擬合

**解決方案：**
1. 添加交易成本到回測
2. 使用樣本外測試
3. 實施風險管理（止損、槓桿控制）
4. 定期重新訓練模型

---

## 參考文獻

1. Preis, T., Kenett, D. Y., Stanley, H. E., & Helbing, D. (2012). Quantifying Behavior of Stock Correlations Under Market Stress. *Scientific Reports*, 2, 752.

2. Mantegna, R. N. (1999). Hierarchical Structure in Financial Markets. *European Physical Journal B*, 11(1), 193-197.

3. Zhou, Z., & Luan, Y. (2025). Eigen Portfolios: From Single Component Models to Ensemble Approaches. arXiv preprint arXiv:2508.15586.

4. Onnela, J. P., Kaski, K., & Kertész, J. (2004). Clustering and Information in Correlation Based Financial Networks. *European Physical Journal B*, 38(2), 353-362.

---

## 聯繫方式

如有問題或建議，請通過以下方式聯繫：
- 項目路徑：`/Users/charlie/.openclaw/workspace/kanban/works/202602281936-phase2-001/`
- 分析師：Charlie

---

**最後更新：** 2026-03-06
**版本：** 1.0
**狀態：** 可執行 ✅
