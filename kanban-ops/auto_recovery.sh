#!/bin/bash
# 自動恢復假失敗任務
# 每 30 分鐘運行一次

cd ~/.openclaw/workspace/kanban-ops

# 運行恢復
python3 recover_tasks.py >> ~/.openclaw/logs/auto_recovery.log 2>&1

# 記錄執行時間
echo "[2026-02-20 20:43:24] Auto recovery check completed" >> ~/.openclaw/logs/auto_recovery.log
echo "" >> ~/.openclaw/logs/auto_recovery.log
