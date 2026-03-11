# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

---

## Dashboard - Market Data Backfill

### 快捷指令：「回補最新市場資料」

**意義：** 進入 System Ops 回補 US/TW 資料

### 快速執行

```bash
# 1. 啟動 Dashboard
cd ~/Dashboard && docker-compose -f docker-compose.dev.yml up -d

# 2. 回補 US 資料
curl -s -X POST "http://localhost:8000/api/system/operations/backfill/us" \
  -H "X-Admin-Token: admin995"

# 3. 回補 TW 資料
curl -s -X POST "http://localhost:8000/api/system/operations/backfill/tw" \
  -H "X-Admin-Token: admin995"

# 4. 查看進度
docker logs dashboard_backend_dev --tail 50 -f
```

### 服務端點

- 後端 API：`http://localhost:8000`
- 前端：`http://localhost:5173`
- API 文檔：`http://localhost:8000/docs`

### 認證信息

- Admin Token：`admin995`
- Header：`X-Admin-Token: admin995`

### API 端點

- `POST /api/system/operations/backfill/us` - US 市場回補
- `POST /api/system/operations/backfill/tw` - TW 市場回補
- `POST /api/system/operations/backfill/fred` - FRED 宏觀數據
- `GET /api/system/operations/status` - 系統狀態
- `GET /api/system/operations/logs` - 操作日誌
