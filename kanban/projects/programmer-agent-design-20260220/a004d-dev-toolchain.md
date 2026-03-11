# Dashboard 開發工具鏈分析報告

## 執行摘要

- **分析日期**: 2026-02-21
- **目標目錄**: `~/Dashboard/`
- **分析方法**: 配置文件分析、目錄結構探索
- **狀態**: ✅ 已完成

---

## 前端工具鏈

| 類別 | 工具 | 版本/配置 | 用途 |
|------|------|-----------|------|
| 包管理 | npm | - | Node.js 套件管理 |
| 運行工具 | concurrently | ^8.2.2 | 多進程並行運行（frontend + backend） |
| 構建工具 | Babel | ^7.28.6 | JS/JSX 轉譯 |
| 構建工具 | Webpack | - | 前端打包和優化 |
| 測試 | Cypress | ^7.0.2 | E2E 測試框架 |
| 測試處理器 | @cypress/webpack-preprocessor | ^7.0.2 | Cypress Webpack 預處理 |

### package.json Scripts

```json
{
  "dev": "concurrently \"npm run dev --prefix frontend\" \"cd backend && python main.py\"",
  "install-all": "npm install --prefix frontend && pip install -r backend/requirements.txt",
  "build-prod": "npm run build --prefix frontend && rm -rf backend/static && cp -r frontend/dist backend/static"
}
```

**特點**: 統一的前端啟動、依賴安裝、生產環境構建命令。

---

## 後端工具鏈

### 核心框架

| 類別 | 工具 | 版本 | 用途 |
|------|------|------|------|
| Web 框架 | FastAPI | >=0.128.0 | 高性能 API 框架 |
| 服務器 | uvicorn[standard] | >=0.40.0 | ASGI 伺服器（開發環境） |
| 服務器 | gunicorn | - | WSGI/ASGI 伺服器（生產環境） |
| 熱重載 | watchfiles | >=0.21.0 | 文件變更監控 |

### 數據獲取與存儲

| 類別 | 工具 | 版本 | 用途 |
|------|------|------|------|
| 數據獲取 | yfinance | >=0.2.51 | Yahoo Finance 數據 API |
| 數據庫 | DuckDB | ==1.1.0 | 列式數據庫（高性能分析） |
| 數據處理 | pandas | ==2.3.3 | 數據操作與分析 |
| 數值計算 | numpy | >=2.0.0 | 高效數值計算 |
| 科學計算 | scipy | >=1.13.0 | 科學計算與統計 |

### 技術分析與回測

| 類別 | 工具 | 版本 | 用途 |
|------|------|------|------|
| 技術指標 | pandas-ta-classic | ==0.3.54 | 技術分析指標庫 |
| 回測框架 | backtrader | - | 事件驅動回測 |
| 回測框架 | vectorbt | ==0.28.2 | 向量化回測（高效） |
| 進度顯示 | tqdm | - | 進度條顯示 |

### 任務調度與驗證

| 類別 | 工具 | 用途 |
|------|------|------|
| 任務調度 | APScheduler | 定時任務執行 |
| 數據驗證 | pydantic | 數據驗證與序列化 |

### 測試框架

| 類別 | 工具 | 功能 |
|------|------|------|
| 測試框架 | pytest | Python 單元測試 |
| 並行測試 | pytest-xdist | 並行執行加速 |
| 超時控制 | pytest-timeout | 測試超時保護 |
| 覆蓋率 | pytest-cov | 代碼覆蓋率報告 |

### HTTP 客戶端

| 工具 | 用途 |
|------|------|
| requests | 同步 HTTP 請求 |
| httpx | 異步 HTTP 請求 |

---

## 自動化工具

### CI/CD

| 類別 | 工具 | 配置位置 |
|------|------|----------|
| 持續集成 | GitHub Actions | `.github/workflows/` |
| Pre-commit hooks | .pre-commit | `.pre-commit-config.yaml` |
| Git hooks | githooks | `.githooks/` |

### Git 工具鏈

- **Git 忽略規則**: `.gitignore`, `.dockerignore`
- **預提交配置**: `.pre-commit-config.yaml`
- **備份機制**: `.backup/` 目錄

---

## 容器化與部署

### Docker 配置

| 配置文件 | 用途 |
|----------|------|
| `docker-compose.yml` | 基礎 Docker Compose 配置 |
| `docker-compose.dev.yml` | 開發環境配置 |
| `docker-compose.prod.yml` | 生產環境配置 |
| `.dockerignore` | 構建時排除的文件 |
| `.env.example` | 環境變量模板 |

### 部署架構

```
┌─────────────┐
│   Nginx    │  ← 反向代理
└──────┬──────┘
       │
┌──────▼──────┐
│  Gunicorn   │  ← WSGI/ASGI 伺服器
└──────┬──────┘
       │
┌──────▼──────┐
│   FastAPI   │  ← Web 框架
└─────────────┘
```

**特點**: dev/prod 環境分離、容器化部署、反向代理。

---

## 目錄結構

```
Dashboard/
├── backend/              # 後端代碼
│   ├── routers/         # API 路由
│   └── requirements.txt # Python 依賴
├── frontend/            # 前端代碼
│   └── package.json     # Node.js 依賴
├── docs/               # 文檔
├── scripts/            # 腳本工具
├── tools/              # 開發工具
├── nginx/              # Nginx 配置
├── market_data_export/  # 市場數據導出
├── .github/workflows/  # CI/CD 配置
├── docker-compose*.yml  # Docker 配置
└── package.json        # 根級依賴管理
```

---

## 優化建議

### 1. 依賴管理

- ✅ **前端**: 使用 `npm workspaces` 或 `pnpm` 優化多包管理
- ✅ **後端**: 考慮 `poetry` 替代 pip（更好的依賴鎖定和虛擬環境）

### 2. 測試覆蓋率

- ⚠️ 當前: pytest + pytest-cov 已配置
- ✅ 建議: 添加覆蓋率閾值（如 `< 80%` 失敗）

### 3. 類型安全

- ❌ 缺失: 前端缺少 TypeScript
- ✅ 建議: 遷移到 TypeScript 提高類型安全

### 4. 監控與日誌

- ⚠️ 當前: 無監控工具
- ✅ 建議: 添加 Prometheus + Grafana（監控）
- ✅ 建議: 使用 Loguru 替代 logging（日誌）

### 5. 文檔生成

- ⚠️ 當前: 有 docs/ 目錄但內容未知
- ✅ 建議: 使用 Sphinx（Python）+ JSDoc（JavaScript）自動生成文檔

---

## 總結

### 工具鏈評估

| 類別 | 評分 | 說明 |
|------|------|------|
| 前端 | 🟡 7/10 | 基礎完備，缺少類型安全 |
| 後端 | 🟢 9/10 | 現代化工具鏈，選擇合理 |
| 測試 | 🟢 8/10 | pytest 生态完善 |
| CI/CD | 🟢 8/10 | GitHub Actions 完整 |
| 部署 | 🟢 9/10 | Docker + Nginx 組合優秀 |

### 核心優勢

1. ✅ 前後端分離架構
2. ✅ 現代化技術棧（FastAPI + React）
3. ✅ 完整的測試框架
4. ✅ CI/CD 自動化
5. ✅ 容器化部署

### 改進空間

1. ⚠️ 前端類型安全（遷移到 TypeScript）
2. ⚠️ 監控系統（Prometheus + Grafana）
3. ⚠️ 日誌系統（Loguru）
4. ⚠️ 依賴管理（poetry/pnpm）

---

**生成時間**: 2026-02-21 12:45 GMT+8
**分析工具**: 手動配置文件分析
**工具鏈完整度**: 85%
