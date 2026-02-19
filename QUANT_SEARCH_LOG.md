# Brave Search API 使用追蹤

**啟動日期：** 2026-02-17
**配額上限：** 2000 次/月
**追蹤工具：** `scripts/track_search_usage.sh`

---

## 使用量記錄

### 2026-02-17
- **日期**: 2026-02-17
- **剩餘配額**: 2000 次 / 2000 次
- **備註**: 首次設定

---

## 警告記錄

---

## 配額管理建議

---

## 自動化腳本

### track_search_usage.sh
- **位置**：`scripts/track_search_usage.sh`
- **功能**：
  - 每日自動記錄使用量
  - 配額不足時發送警報（< 100 次）
  - 記錄剩餘配額

### 使用方法

```bash
# 手動執行
/Users/charlie/.openclaw/workspace/scripts/track_search_usage.sh

# 設定 cron job（每日 0 點執行）
0 0 * * * /Users/charlie/.openclaw/workspace/scripts/track_search_usage.sh
```
---
## 2026-02-17

### 使用量統計
- **日期**: 2026-02-17
- **剩餘配額**: 2000 次 / 2000 次

