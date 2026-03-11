#!/usr/bin/env python3
import json
from datetime import datetime, timezone

TASKS_JSON = '/Users/charlie/.openclaw/workspace/kanban/tasks.json'

with open(TASKS_JSON, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 檢查 q009
q009 = next((t for t in data if t['id'] == 'q009'), None)
if q009:
    updated_at = q009.get('updated_at', '')
    if updated_at:
        dt = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
        time_ago = datetime.now(timezone.utc) - dt
        hours = time_ago.total_seconds() / 3600
        print(f'q009 最後更新: {dt.strftime("%H:%M")} ({hours:.1f} 小時前)')
        print(f'狀態: {q009.get("status")}')
        print(f'標題: {q009.get("title")}')

        # 檢查輸出文件
        output_path = q009.get('output_path', '')
        if output_path:
            import os
            full_path = os.path.expanduser('~/kanban/' + output_path)
            exists = os.path.exists(full_path)
            print(f'輸出文件: {"✓ 已存在" if exists else "✗ 未生成"}')
