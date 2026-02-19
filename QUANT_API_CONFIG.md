# Brave Search API Key 配置說明

## API Key 狀態

**Key:** BSAQCyaZlB7rq8AWh8N60ka1srdj7uf
**狀態：** 已記錄在檔案中，但需要配置才能使用
**配額：** 2000 次/月
**已使用：** 1 次（2026-02-17 嘗試搜尋）

---

## 配置方式

### 方法 1：OpenClaw 命令行

```bash
openclaw configure --section web
```

系統會提示輸入：
- Brave Search API key

### 方法 2：環境變數

```bash
export BRAVE_API_KEY="BSAQCyaZlB7rq8AWh8N60ka1srdj7uf"
```

或寫入 `~/.zshrc` / `~/.bashrc`：
```bash
echo 'export BRAVE_API_KEY="BSAQCyaZlB7rq8AWh8N60ka1srdj7uf"' >> ~/.zshrc
source ~/.zshrc
```

---

## 配置後功能

### 可用的搜尋功能

1. **量化交易帳號搜尋**
   - 搜尋 Threads 上的量化交易帳號
   - 搜尋 Twitter/X 上的 quant 帳號
   - 搜尋 GitHub 上的 quant 倉庫

2. **論文研究**
   - 搜尋 arXiv、SSRN 的量化交易論文
   - 搜尋相關研究報告
   - 追蹤最新研究動態

3. **工具資源**
   - 搜尋回測工具
   - 搜尋數據供應商
   - 搜尋分析工具

4. **市場資訊**
   - 搜尋最新市場動態
   - 搜尋交易策略分享
   - 搜尋風險管理建議

---

## 使用量追蹤

每次搜尋會自動記錄：
- 使用次數
- 剩餘配額
- 搜尋時間
- 搜尋結果數量
- 相關度評估

---

## 下一步

1. [ ] 設定 Brave Search API key
2. [ ] 測試搜尋功能
3. [ ] 開始搜尋量化交易帳號
4. [ ] 記錄搜尋結果
5. [ ] 追蹤使用量

---

**配置需求：** 需要手動設定 API key
**記錄位置：** QUANT_SEARCH_LOG.md
**記錄人：** Charlie
