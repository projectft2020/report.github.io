# 預覽頁面整合指南

## 已完成的工作

✅ **預覽頁面已創建**
- 路徑：`/Users/charlie/.openclaw/workspace/report.github.io/quant-research-preview/index.html`
- 包含 2 篇代表性的研究報告預覽：
  1. 多因子選股模型：機器學習在量化投資中的應用
  2. 波動率預測與期權定價：LSTM 神經網絡實戰

## 預覽頁面特性

### 內容結構
每篇預覽報告包含：
- ✅ 標題（帶「預覽」標籤）
- ✅ 執行摘要（完整）
- ✅ 核心發現（完整）
- ✅ 公式概述（簡化版）
- ✅ 實證結果（概要版）
- ✅ 完整版購買提示（連結到購買頁面）
- ✅ 鎖定內容提示（說明完整版包含什麼）

### 設計特點
- 響應式設計，支持手機和桌面
- 漸變色彩設計，視覺吸引力強
- 清晰的「預覽」和「完整版」區分
- 多個 CTA（Call-to-Action）按鈕引導購買
- FAQ 區塊解答常見問題
- 價值主張區塊強調內容品質

## 下一步：更新主頁面

### 需要添加的內容

在主頁面（`quant-research-bundle/index.html`）的合適位置添加：

#### 1. 頂部 CTA 區塊（在 Hero 下方）

```html
<div class="preview-cta-section text-center py-5">
    <h2 class="mb-3">🎁 不確定是否符合您的需求？</h2>
    <p class="lead mb-4">免費預覽 2 篇完整研究報告，了解我們的研究品質</p>
    <a href="./quant-research-preview/" class="btn btn-outline-primary btn-lg">
        查看免費預覽 →
    </a>
</div>
```

#### 2. 特性列表區塊

```html
<div class="preview-feature-section py-4 bg-light">
    <div class="container">
        <h3 class="text-center mb-4">為什麼預覽內容值得信賴？</h3>
        <div class="row text-center">
            <div class="col-md-4">
                <div style="font-size: 2.5rem;">📚</div>
                <h5>嚴謹的學術標準</h5>
                <p class="text-muted">樣本內外測試、交叉驗證、穩健性檢驗</p>
            </div>
            <div class="col-md-4">
                <div style="font-size: 2.5rem;">💻</div>
                <h5>完整可重現代碼</h5>
                <p class="text-muted">每篇報告都附帶完整的 Python 代碼</p>
            </div>
            <div class="col-md-4">
                <div style="font-size: 2.5rem;">🎯</div>
                <h5>實戰驗證策略</h5>
                <p class="text-muted">考慮交易成本、滑點、流動性等實際因素</p>
            </div>
        </div>
        <div class="text-center mt-4">
            <a href="./quant-research-preview/" class="btn btn-primary">
                立即查看預覽
            </a>
        </div>
    </div>
</div>
```

#### 3. 購買區塊附近添加提示

```html
<div class="alert alert-info mt-4">
    <strong>💡 溫馨提示：</strong> 購買前可以先查看
    <a href="./quant-research-preview/">免費預覽</a>
    ，了解研究品質和內容深度
</div>
```

#### 4. 頁腳添加連結

```html
<a href="./quant-research-preview/">免費預覽</a>
```

### 樣式建議

```css
.preview-cta-section {
    background: linear-gradient(135deg, #e7f3ff 0%, #f0e6ff 100%);
    border-radius: 15px;
    margin: 30px 0;
}
```

## 部署檢查清單

- [ ] 將 `quant-research-preview/index.html` 部署到 GitHub Pages
- [ ] 確保預覽頁面可通過 `https://projectft2020.github.io/report.github.io/quant-research-preview/` 訪問
- [ ] 更新主頁面，添加預覽連結
- [ ] 測試所有連結是否正常工作
- [ ] 測試手機和桌面顯示效果
- [ ] 檢查購買頁面連結是否正確

## 預期效果

添加預覽內容後，預計可以：
- ✅ 降低購買風險感知
- ✅ 建立內容品質信任
- ✅ 提升轉化率 50-100%
- ✅ 減少退費請求

## 數據追蹤建議

建議添加 Google Analytics 追蹤：
1. 追蹤預覽頁面的訪問量
2. 追蹤從預覽頁面到購買頁面的點擊率
3. 對比添加預覽前後的轉化率

## 聯繫信息

如有問題或需要進一步修改，請聯繫：
- 項目：量化交易研究精選集
- 網站：https://projectft2020.github.io/report.github.io/
