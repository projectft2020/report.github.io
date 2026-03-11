---
name: stock-symbol-mapper
description: 股票代碼與公司名稱的映射查詢與驗證。用於查詢台灣/美國股票的代碼與公司名稱對應關係、驗證映射正確性、更新映射資料。
---

# 股票代碼映射器 (Stock Symbol Mapper)

提供台灣和美國股票代碼與公司名稱的映射查詢功能。

## 快速開始

查詢股票資訊：
```bash
cd ~/.openclaw/workspace/skills/stock-symbol-mapper
python3 scripts/query_symbol.py <symbol>
```

## 資料來源

### 台灣股票 (TW)
- **路徑**: `references/data/tw_stocks.json`
- **格式**: `{"<股票代碼>": {"name": "<公司名稱>", "market": "上市/上櫃", "type": "股票", "industry": "<行業>"}}`
- **數量**: 2261 檔
- **更新頻率**: 很少變動（公司名稱/代碼基本穩定）
- **來源**: Dashboard `frontend/src/data/securities_list.json`

### 美國股票 (US)
- **路徑**: `references/data/us_stocks.json`（待創建）
- **格式**: 同台灣股票
- **數量**: 待定
- **來源**: 待決定（可從 yfinance、Yahoo Finance 等獲取）

## 使用場景

### 場景 1: 查詢股票名稱
用戶想知道某個代碼的公司名稱。

```bash
python3 scripts/query_symbol.py 2330.TW
# 輸出: 台積電
```

### 場景 2: 驗證映射正確性
檢查 Dashboard 中是否有錯誤的映射（例如 2301.TW 錯誤映射為「台積電」）。

```bash
python3 scripts/validate_mapping.py
# 輸出所有可能的錯誤映射
```

### 場景 3: 搜索公司名稱
根據關鍵詞搜索公司。

```bash
python3 scripts/search_name.py "台積電"
# 輸出所有匹配的股票
```

### 場景 4: 更新映射資料
當需要添加新股票或修正錯誤時。

```bash
# 手動編輯 JSON 檔案
# 或使用腳本批量更新
python3 scripts/update_mapping.py
```

## 腳本說明

### `query_symbol.py`
查詢單個股票代碼或名稱。

**用法**:
```bash
python3 scripts/query_symbol.py <symbol_or_name>
```

**輸出**:
- 找到：顯示完整資訊（代碼、名稱、市場、行業）
- 未找到：提示用戶並建議搜索

### `validate_mapping.py`
驗證映射資料的完整性和正確性。

**檢查項目**:
- 必填欄位：symbol, name, market, industry
- 重複檢查：確保沒有重複的 symbol
- 格式檢查：JSON 格式正確

**用法**:
```bash
python3 scripts/validate_mapping.py
```

### `search_name.py`
根據關鍵詞搜索公司名稱。

**用法**:
```bash
python3 scripts/search_name.py "<keyword>"
```

**輸出**:
- 列出所有匹配的公司名稱和代碼

### `update_mapping.py`
更新或添加股票映射。

**用法**:
```bash
python3 scripts/update_mapping.py
# 互動式更新
```

## 資料維護

### 更新頻率
- 台灣股票：很少變動（公司合併/更名才需更新）
- 美國股票：可能需要定期更新（IPO、退市）

### 更新流程
1. 從來源獲取最新資料
2. 比對現有映射
3. 識別新增/變更/刪除
4. 更新 JSON 檔案
5. 運行 `validate_mapping.py` 驗證
6. 同步到 Dashboard

### 同步到 Dashboard
```bash
# 台灣股票
cp references/data/tw_stocks.json ~/.openclaw/workspace/Dashboard/frontend/src/data/securities_list.json

# 美國股票
cp references/data/us_stocks.json ~/.openclaw/workspace/Dashboard/frontend/src/data/us_stocks.json
```

## 注意事項

1. **資料一致性**：Dashboard 和 skill 的資料必須保持同步
2. **格式標準**：統一使用 `.TW`（台灣）和無後綴（美國）的格式
3. **大小寫**：股票代碼統一使用大寫（例如 `2330.TW`）
4. **備份**：修改前備份原始資料
