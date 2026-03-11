# 解決方案：不修改資料庫實現 Win Rate 和 Profit Factor 顯示

**日期:** 2026-02-22
**方案類型:** 臨時解決方案（不修改資料庫架構）
**狀態:** ✅ 已實現

---

## 📋 問題分析

### 現況
| 層級 | 狀態 | 說明 |
|-----|------|------|
| 後端代碼 | ✅ 已準備 | `history_service.py` 已經準備好接收和保存 win_rate 和 profit_factor |
| 前端代碼 | ✅ 已準備 | `BacktestHistoryPage.jsx` 已經準備好顯示這兩個欄位 |
| 數據庫結構 | ❌ 缺失 | `backtest_history` 表缺少 win_rate 和 profit_factor 欄位 |
| 保存邏輯 | ❌ 未實現 | `stats_cache_service.py` 沒有計算和傳遞這兩個值 |

### 核心問題
- 代碼已經準備好，但保存時沒有傳遞 win_rate 和 profit_factor
- 數據庫缺少這兩個欄位
- 用戶要求：**不修改資料庫**

---

## 💡 解決方案：使用 params JSON 作為臨時存儲

### 方案概述

**不修改資料庫架構**，通過以下方式實現：

1. **保存時**：將 `win_rate` 和 `profit_factor` 存入 `params` JSON 欄位
   - Key: `_win_rate`, `_profit_factor`
   - 同時嘗試保存到數據庫欄位（如果存在）

2. **讀取時**：優先從數據庫欄位讀取，如果不存在則從 `params` JSON 中提取
   - 向後兼容：支持未來應用遷移 005 後的數據庫欄位

3. **計算時**：在 `_run_simulation` 中計算 `profit_factor`

### 優點
- ✅ 完全不需要修改資料庫架構
- ✅ 立即可用，無需等待遷移
- ✅ 向後兼容，未來可以平滑切換到數據庫欄位
- ✅ 符合「數據庫修改的三重審查原則」

### 缺點
- ⚠️ 存儲在 JSON 中，查詢性能略低（但對於列表查詢影響很小）
- ⚠️ 需要額外的邏輯處理 JSON 解析

---

## 🔧 實現詳情

### 1. stats_cache_service.py 修改

#### 1.1 修改 `_run_simulation` 方法

**添加 `profit_factor` 計算：**

```python
# Calculate profit factor: sum of positive PnL / sum of negative PnL (absolute)
total_win_pnl = wins['pnl'].sum() if not wins.empty else 0
total_loss_pnl = abs(losses['pnl'].sum()) if not losses.empty else 0
profit_factor = total_win_pnl / total_loss_pnl if total_loss_pnl > 0 else None

stats = {
    'win_rate': len(wins) / len(df),
    'profit_factor': profit_factor,  # ✅ 新增
    'expected_return': df['return_pct'].mean(),
    'sample_count': len(df),
    'avg_win': wins['return_pct'].mean() if not wins.empty else 0,
    'avg_loss': losses['return_pct'].mean() if not losses.empty else 0,
    'forward_20d': holding_stats.get('20D', 0)
}
```

#### 1.2 修改 `cache_simulation_result` 方法

**傳遞 win_rate 和 profit_factor 給 `_save_to_history`：**

```python
def cache_simulation_result(
    self,
    instance_id: str,
    strategy_type: str,
    market: str,
    params: Dict[str, Any],
    result: Dict[str, Any],
    stats: Dict[str, Any],
    years: float
):
    try:
        # 1. Save to Stats Cache
        self._store_stats(instance_id, market, 'all', 30, stats, years)

        # 2. Save to History (Async)
        self._save_to_history(
            instance_id=instance_id,
            strategy_type=strategy_type,
            market=market,
            params=params,
            result=result,
            years=years,
            win_rate=stats.get('win_rate'),      # ✅ 新增
            profit_factor=stats.get('profit_factor')  # ✅ 新增
        )
    except Exception as e:
        logger.error(f"Error caching simulation result: {e}")
```

#### 1.3 修改 `_save_to_history` 方法

**接收 win_rate 和 profit_factor 參數，存入 params JSON：**

```python
def _save_to_history(
    self,
    instance_id: str,
    strategy_type: str,
    market: str,
    params: Dict[str, Any],
    result: Dict[str, Any],
    years: float,
    win_rate: float = None,          # ✅ 新增參數
    profit_factor: float = None       # ✅ 新增參數
):
    try:
        stats = result.get('stats', {})
        return_series = result.get('return_series', [])

        start_date = return_series[0]['date'] if return_series else None
        end_date = return_series[-1]['date'] if return_series else None

        # 🔧 TEMPORARY: Store win_rate and profit_factor in params JSON
        # This avoids database schema changes while maintaining functionality
        enhanced_params = params.copy()
        if win_rate is not None:
            enhanced_params['_win_rate'] = win_rate
        if profit_factor is not None:
            enhanced_params['_profit_factor'] = profit_factor

        # Save with enhanced params and stats
        await history_service.save_backtest_result(
            conn=fresh_conn,
            strategy_type=strategy_type,
            strategy_name=f"{instance_id} (auto-cached)",
            market=market,
            params=enhanced_params,  # ✅ 使用增強的 params
            stats={
                'total_return': stats.get('total_return'),
                'cagr': stats.get('cagr'),
                'mdd': stats.get('mdd'),
                'sharpe': stats.get('sharpe'),
                'volatility': stats.get('volatility'),
                'win_rate': win_rate,            # ✅ 傳遞給保存
                'profit_factor': profit_factor   # ✅ 傳遞給保存
            },
            backtest_years=int(years),
            start_date=start_date or '',
            end_date=end_date or '',
            notes=f"Auto-saved by StatsCacheService for {market} ({years}Y)"
        )
```

### 2. history_service.py 修改

#### 2.1 新增輔助函數

**從 params JSON 中提取指標：**

```python
def _extract_metric_from_params(params: Dict[str, Any], metric_key: str, fallback: Any = None) -> Any:
    """
    Extract a metric from params JSON if database column doesn't exist.

    Temporary solution for win_rate and profit_factor storage
    without modifying database schema.

    Args:
        params: Parameters dictionary (JSON)
        metric_key: Key to extract (e.g., '_win_rate', '_profit_factor')
        fallback: Default value if key not found

    Returns:
        Extracted value or fallback
    """
    if params and isinstance(params, dict):
        return params.get(metric_key, fallback)
    return fallback
```

#### 2.2 修改 `list_backtest_history` 方法

**從 params JSON 中提取 win_rate 和 profit_factor（如果數據庫欄位不存在）：**

```python
async def list_backtest_history(
    conn: duckdb.DuckDBPyConnection,
    strategy_type: Optional[str] = None,
    market: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    # ... 查詢邏輯 ...

    records = []
    for _, row in result.iterrows():
        params_dict = json.loads(row['params']) if row['params'] else {}

        # Extract win_rate: try database column first, fallback to params
        win_rate = _clean_float(row.get('win_rate'))
        if win_rate is None:
            win_rate = _extract_metric_from_params(params_dict, '_win_rate')

        # Extract profit_factor: try database column first, fallback to params
        profit_factor = _clean_float(row.get('profit_factor'))
        if profit_factor is None:
            profit_factor = _extract_metric_from_params(params_dict, '_profit_factor')

        record = {
            # ... 其他欄位 ...
            "win_rate": win_rate,
            "profit_factor": profit_factor
        }
        records.append(record)

    return {"records": records, "count": len(records), "total": total, "offset": offset, "limit": limit}
```

#### 2.3 修改 `get_backtest_by_id` 方法

**使用相同的邏輯提取 win_rate 和 profit_factor：**

```python
async def get_backtest_by_id(
    conn: duckdb.DuckDBPyConnection,
    record_id: int
) -> Optional[Dict[str, Any]]:
    result = conn.execute("""...""", [record_id]).fetchone()

    if not result:
        return None

    params_dict = json.loads(result[4]) if result[4] else {}

    # Extract win_rate: try database column first, fallback to params
    win_rate = _clean_float(result[15])
    if win_rate is None:
        win_rate = _extract_metric_from_params(params_dict, '_win_rate')

    # Extract profit_factor: try database column first, fallback to params
    profit_factor = _clean_float(result[16])
    if profit_factor is None:
        profit_factor = _extract_metric_from_params(params_dict, '_profit_factor')

    return {
        # ... 其他欄位 ...
        "win_rate": win_rate,
        "profit_factor": profit_factor
    }
```

#### 2.4 修改 `compare_backtests` 方法

**使用相同的邏輯提取 win_rate 和 profit_factor：**

```python
async def compare_backtests(
    conn: duckdb.DuckDBPyConnection,
    record_ids: List[int]
) -> List[Dict[str, Any]]:
    # ... 查詢邏輯 ...

    for _, row in result.iterrows():
        params_dict = json.loads(row['params']) if row['params'] else {}

        # Extract win_rate: try database column first, fallback to params
        win_rate = _clean_float(row.get('win_rate'))
        if win_rate is None:
            win_rate = _extract_metric_from_params(params_dict, '_win_rate')

        # Extract profit_factor: try database column first, fallback to params
        profit_factor = _clean_float(row.get('profit_factor'))
        if profit_factor is None:
            profit_factor = _extract_metric_from_params(params_dict, '_profit_factor')

        record = {
            # ... 其他欄位 ...
            "win_rate": win_rate,
            "profit_factor": profit_factor
        }
        records.append(record)

    return records
```

---

## 📊 修改文件清單

| 文件 | 修改內容 | 行數變更 |
|-----|---------|---------|
| `services/stats_cache_service.py` | 添加 profit_factor 計算、傳遞參數、存入 params JSON | ~30 行 |
| `services/history_service.py` | 添加輔助函數、修改三個讀取方法 | ~40 行 |

**總計：** ~70 行代碼變更

---

## 🚀 使用說明

### 新數據（修改後）
1. 執行回測
2. win_rate 和 profit_factor 會自動計算並保存到 params JSON
3. 前端立即顯示這兩個指標

### 舊數據（修改前）
1. params JSON 中沒有 `_win_rate` 和 `_profit_factor`
2. 讀取時返回 `None`
3. 前端顯示 "-"（已經有這個邏輯）

### 未來升級
1. 如果需要應用遷移 005（添加數據庫欄位）
2. 無需修改讀取邏輯（已經優先使用數據庫欄位）
3. 平滑過渡，無數據遷移問題

---

## ✅ 測試驗證

### 語法檢查
```bash
cd /Users/charlie/.openclaw/workspace/Dashboard/backend
python3 -m py_compile services/stats_cache_service.py services/history_service.py
```

結果：✅ 通過

### 功能測試（建議）
1. 運行一個新的回測
2. 檢查 backtest_history 表中的 params JSON
3. 確認包含 `_win_rate` 和 `_profit_factor`
4. 檢查前端 Backtest History 頁面是否正確顯示

---

## 📝 備註

### 為什麼不修改資料庫？

根據 SOUL.md 中的「數據庫修改的三重審查原則」：

1. **優先級：非資料庫方案 > 資料庫修改**
   - ✅ 找到了使用 params JSON 的替代方案
   - ✅ 可以在不修改數據庫的情況下實現功能

2. **必須滿足條件才考慮數據庫修改**
   - ❌ 不是非動不可的核心功能需求
   - ❌ 沒有用戶明確同意修改數據庫

3. **記錄到記憶**
   - ✅ 已記錄這次案例（2026-02-22）
   - ✅ 教訓：永遠先問「能否不改動資料庫」

### 性能影響評估

- **JSON 解析開銷：** 對於列表查詢（~400 條記錄），JSON 解析開銷可以忽略
- **查詢性能：** 不影響，因為這些欄位不在 WHERE 或 ORDER BY 子句中
- **存儲空間：** params JSON 中增加 2 個鍵值對，影響極小

### 向後兼容性

讀取邏輯設計為：
1. 優先從數據庫欄位讀取
2. 如果數據庫欄位不存在或為 NULL，則從 params JSON 中提取
3. 如果都沒有，返回 NULL（前端顯示 "-"）

這意味著：
- 未來應用遷移 005 後，無需修改讀取邏輯
- 舊數據和新數據可以共存
- 平滑過渡，無數據遷移問題

---

## 🎯 總結

### ✅ 方案優點
- 完全不需要修改資料庫架構
- 立即可用，無需等待遷移
- 代碼變更量小（~70 行）
- 向後兼容，未來可以平滑切換
- 符合最佳實踐原則

### ⚠️ 方案限制
- 存儲在 JSON 中，無法直接用於 SQL 查詢條件
- 需要額外的邏輯處理 JSON 解析
- 不適合需要按 win_rate/profit_factor 排序或篩選的場景

### 📌 建議
1. 短期：使用此方案立即啟用功能
2. 長期：如果需要按 win_rate/profit_factor 排序或篩選，再考慮應用遷移 005
3. 監控：關注性能和用戶反饋，決定是否需要升級

---

**最後更新：** 2026-02-22 12:35 PM
**實施者：** Charlie (Orchestrator)
**狀態：** ✅ 完成，等待測試驗證
