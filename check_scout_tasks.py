#!/usr/bin/env python3
import json

TASKS_JSON = '/Users/charlie/.openclaw/workspace/kanban/tasks.json'

with open(TASKS_JSON, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 檢查 Scout 創建的任務
scout_tasks = [t for t in data if t.get('created_by') == 'scout']

print(f'Scout 創建的任務: {len(scout_tasks)}')
if scout_tasks:
    print('\n最近的 Scout 任務:')
    for t in scout_tasks[-5:]:
        created = t.get('created_at', 'N/A')
        title = t.get('title', 'N/A')
        status = t.get('status', 'N/A')
        print(f'  [{t["id"]}] {title[:50]}...')
        print(f'      狀態: {status} | 創建: {created}')
else:
    print('\n  沒有找到 Scout 創建的任務')
