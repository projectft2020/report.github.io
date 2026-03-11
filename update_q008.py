#!/usr/bin/env python3
import json
from datetime import datetime, timezone

TASKS_JSON = '/Users/charlie/.openclaw/workspace/kanban/tasks.json'

with open(TASKS_JSON, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 更新 q008 為 completed
for t in data:
    if t['id'] == 'q008' and t['status'] in ['pending', 'in_progress']:
        t['status'] = 'completed'
        t['updated_at'] = datetime.now(timezone.utc).isoformat()
        print(f"✓ 任務 q008 已更新為 completed")

# 保存
with open(TASKS_JSON, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("\n當前運行中的任務:")
for t in data:
    if t.get('status') == 'in_progress':
        print(f"  - {t['id']}: {t.get('title', 'N/A')[:40]}")
