# GitHub Pages 設置指南

## 問題診斷

你看到的 404 錯誤是因為 GitHub Pages 還沒有啟用。雖然我們已經成功推送了代碼到 GitHub，但 GitHub Pages 功能需要在倉庫設置中手動啟用。

## 解決步驟

### Step 1：打開 GitHub 倉庫設置

1. 訪問你的 GitHub 倉庫：https://github.com/projectft2020/report.github.io
2. 點擊右上角的 **Settings** 選項卡
3. 在左側菜單中找到並點擊 **Pages**

### Step 2：配置 GitHub Pages

在 **Pages** 頁面中：

1. **Build and deployment** 部分：
   - Source: 選擇 **Deploy from a branch**
   - Branch: 選擇 **main**
   - Folder: 選擇 **/(root)**
   - 點擊 **Save** 按鈕

2. 等待 1-2 分鐘，GitHub Pages 會自動部署

### Step 3：確認部署成功

1. 在 **Pages** 頁面的頂部，你會看到：
   ```
   Your site is live at https://projectft2020.github.io/
   ```

2. 點擊這個鏈接，確認主頁可以訪問

### Step 4：訪問產品頁面

部署成功後，產品頁面的 URL 是：

```
https://projectft2020.github.io/quant-research-bundle/
```

---

## 設置截圖指南

### 確保正確的設置：

```
Settings → Pages
├── Build and deployment
│   ├── Source: Deploy from a branch
│   ├── Branch:
│   │   ├── main /
│   │   └── /(root)
│   └── [Save]
```

---

## 常見問題

### Q: 點擊 Save 後沒有反應？
A: 刷新頁面，確認設置已保存。

### Q: 部署需要多長時間？
A: 通常 1-2 分鐘，有時候可能需要 5 分鐘。

### Q: 還是看到 404？
A:
1. 檢查 URL 是否正確（`https://projectft2020.github.io/`）
2. 刷新瀏覽器（Ctrl+F5 或 Cmd+Shift+R）
3. 等待 5 分鐘後再試

### Q: 看到其他錯誤？
A: 查看 GitHub Pages 的部署日誌：
1. Settings → Pages
2. 找到 **Build and deployment** 部分
3. 點擊最近的部署記錄查看詳細日誌

---

## 完成後的下一步

1. ✅ 確認主頁可以訪問：`https://projectft2020.github.io/`
2. ✅ 確認產品頁面可以訪問：`https://projectft2020.github.io/quant-research-bundle/`
3. ⏭️ 添加銀行帳號到購買說明
4. ⏭️ 宣傳推廣（Threads、Telegram）

---

## 技術細節

### 倉庫類型：User Site
- 倉庫名稱：`projectft2020.github.io`
- 這是一個 User Site，會自動映射到 `https://projectft2020.github.io/`
- 不需要額外的路徑

### 部署分支：main
- 我們的代碼已經推送到 `main` 分支
- GitHub Pages 會自動從 `main` 分支部署

### 部署目錄：/(root)
- 我們的文件直接放在倉庫根目錄
- 不需要 `gh-pages` 分支或其他特殊目錄

---

**設置完成後，告訴我，我會幫你驗證部署！** 🚀
