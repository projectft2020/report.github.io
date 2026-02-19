# 環境配置記憶 - 立即參考

## Matrix Dashboard 環境

**工作目錄：** `/Users/charlie/Dashboard`

### 容器架構

| 容器 | 服務 | 端口 | 用途 |
|------|------|------|------|
| `dashboard_app` | 生產 (Gunicorn) | 8000 | 靜態前端 + API |
| `dashboard_backend_dev` | 開發 (Uvicorn) | 8001 | 熱重載開發 |
| `dashboard_frontend_dev` | Vite | 5173 | 開發服務器 |

### API 端點

- **健康檢查：** `GET http://localhost:8000/health`
- **策略列表：** `GET http://localhost:8000/strategies`
- **回測 API：** 需要查看 Swagger UI 確認

### Docker 命令

```bash
# 檢查狀態
cd /Users/charlie/Dashboard && docker compose ps

# 查看日誌
docker compose -f docker-compose.dev.yml logs backend --tail 50

# 進入容器
docker compose -f docker-compose.dev.yml exec backend bash
```

### 關鍵提醒

⚠️ 開發環境 API 在 **8001** 端口
⚠️ 生產環境 API 在 **8000** 端口
⚠� 執行 docker 命令前先 `cd /Users/charlie/Dashboard`

---

**最後更新：** 2026-02-19
