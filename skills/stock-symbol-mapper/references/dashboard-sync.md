# Dashboard 股號映射同步指南

## 問題描述

Dashboard 中可能存在股號與公司名稱映射不正確的問題。例如：
- 2301.TW（光寶科）被錯誤映射為「台積電」
- 正確映射：2330.TW（台積電）

## 解決方案

使用 `stock-symbol-mapper` skill 來驗證和修正映射。

## 快速驗證

### 1. 查詢特定股號
```bash
cd ~/.openclaw/workspace/skills/stock-symbol-mapper
python3 scripts/query_symbol.py 2330
# 應該輸出: 台積電

python3 scripts/query_symbol.py 2301
# 應該輸出: 光寶科
```

### 2. 搜索公司名稱
```bash
python3 scripts/search_name.py 台積電
# 應該只返回 2330.TW

python3 scripts/search_name.py 光寶科
# 應該返回 2301.TW
```

### 3. 驗證整體資料
```bash
python3 scripts/validate_mapping.py
# 檢查所有欄位、重複和格式
```

## Dashboard 前端檢查

### 檢查前端映射

前端股票映射位於：
```
~/.openclaw/workspace/Dashboard/frontend/src/data/securities_list.json
```

**檢查方法：**
```bash
cd ~/.openclaw/workspace/Dashboard/frontend
grep -A 2 "2301" src/data/securities_list.json
grep -A 2 "2330" src/data/securities_list.json
```

**正確輸出應該是：**
```json
"2301": {
  "name": "光寶科",
  "market": "上市",
  "industry": "電腦及週邊設備業"
}
```

```json
"2330": {
  "name": "台積電",
  "market": "上市",
  "industry": "半導體業"
}
```

### 檢查前端組件中的硬編碼

某些組件可能硬編碼了特定的股號映射：

1. **MarketScoreMonitorPage.jsx**
   ```bash
   grep -n "台積電\|2330\|2301" frontend/src/pages/MarketScoreMonitorPage.jsx
   ```

2. **TwHeatmap.jsx**
   ```bash
   grep -n "台積電\|2330\|2301" frontend/src/components/TwHeatmap.jsx
   ```

3. **所有前端檔案**
   ```bash
   grep -r "2301.*台積電\|台積電.*2301" frontend/src/
   ```

## 常見錯誤

### 錯誤 1: 前端硬編碼錯誤映射

**症狀：** 代碼中寫了錯誤的股號-公司名稱對應

**範例：**
```jsx
// ❌ 錯誤
{ symbol: '2301.TW', name: '台積電', color: '#ef4444' }

// ✅ 正確
{ symbol: '2330.TW', name: '台積電', color: '#ef4444' }
```

**修正方法：**
1. 找到硬編碼的映射
2. 使用 `query_symbol.py` 驗證正確映射
3. 更新代碼

### 錯誤 2: 數據源不一致

**症狀：** `securities_list.json` 與 skill 資料不一致

**解決方法：**
1. 以 skill 資料為準（經過驗證）
2. 更新 Dashboard 資料：
   ```bash
   cp ~/.openclaw/workspace/skills/stock-symbol-mapper/references/data/tw_stocks.json \
      ~/.openclaw/workspace/Dashboard/frontend/src/data/securities_list.json
   ```

### 錯誤 3: 後端服務返回錯誤數據

**症狀：** API 返回的數據包含錯誤映射

**檢查後端服務：**
```bash
# tw_market_service.py
grep -n "2301\|2330\|台積電\|光寶科" \
  ~/.openclaw/workspace/Dashboard/backend/services/tw_market_service.py

# yfinance_tw_service.py
grep -n "2301\|2330\|台積電\|光寶科" \
  ~/.openclaw/workspace/Dashboard/backend/services/yfinance_tw_service.py
```

## 同步工作流

### 定期同步（建議）

當更新 `stock-symbol-mapper` 資料時，自動同步到 Dashboard：

```bash
# 1. 更新 skill 資料（使用 update_mapping.py）
cd ~/.openclaw/workspace/skills/stock-symbol-mapper
python3 scripts/update_mapping.py

# 2. 驗證更新
python3 scripts/validate_mapping.py

# 3. 同步到 Dashboard
cp references/data/tw_stocks.json \
   ~/.openclaw/workspace/Dashboard/frontend/src/data/securities_list.json

# 4. 重啟 Dashboard（如果需要）
cd ~/.openclaw/workspace/Dashboard
docker-compose -f docker-compose.dev.yml restart frontend
```

### 緊急修復

如果發現 Dashboard 顯示錯誤映射：

```bash
# 1. 立即同步正確資料
cd ~/.openclaw/workspace/skills/stock-symbol-mapper
cp references/data/tw_stocks.json \
   ~/.openclaw/workspace/Dashboard/frontend/src/data/securities_list.json

# 2. 清除瀏覽器緩存並重新加載
# (用戶端操作)

# 3. 如果問題持續，檢查前端硬編碼
cd ~/.openclaw/workspace/Dashboard/frontend
grep -rn "2301.*台積電\|台積電.*2301" src/
```

## 參考資源

- Skill 位置: `~/.openclaw/workspace/skills/stock-symbol-mapper/`
- Dashboard 前端: `~/.openclaw/workspace/Dashboard/frontend/`
- Dashboard 後端: `~/.openclaw/workspace/Dashboard/backend/`
- 股票資料: `~/.openclaw/workspace/skills/stock-symbol-mapper/references/data/tw_stocks.json`

## 故障排除

### 問題：查詢返回 "未找到"

**可能原因：**
1. 股號格式錯誤（應該是純數字，例如 2330）
2. 公司名稱拼寫錯誤
3. 資料庫中沒有該股票

**解決方法：**
```bash
# 使用模糊搜索
python3 scripts/search_name.py 台積  # 只輸入部分關鍵詞

# 列出所有股票
python3 scripts/validate_mapping.py
```

### 問題：驗證失敗

**可能原因：**
1. JSON 格式錯誤
2. 缺少必填欄位
3. 資料類型錯誤

**解決方法：**
1. 使用 JSON 驗證工具檢查格式
2. 檢查 `validate_mapping.py` 的具體錯誤信息
3. 對照正確的資料格式進行修正

### 問題：Dashboard 仍然顯示錯誤映射

**可能原因：**
1. 前端緩存
2. 硬編碼映射未更新
3. 後端服務未重啟

**解決方法：**
1. 清除瀏覽器緩存（Ctrl+Shift+R）
2. 檢查前端代碼中的硬編碼
3. 重啟 Dashboard 後端服務
