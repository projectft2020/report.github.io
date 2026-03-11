#!/usr/bin/env python3
import json
from datetime import datetime, timezone

TASKS_JSON = '/Users/charlie/.openclaw/workspace/kanban/tasks.json'

with open(TASKS_JSON, 'r', encoding='utf-8') as f:
    data = json.load(f)

executable_ids = ['a004d', 'q005a', 'q005b', 'q006a', 'q006b', 'q007', 'q009', 'q010']
updated = []

for t in data:
    if t['id'] in executable_ids and t['status'] == 'pending':
        t['status'] = 'in_progress'
        t['updated_at'] = datetime.now(timezone.utc).isoformat()
        updated.append(t['id'])

with open(TASKS_JSON, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"✓ 已更新 {len(updated)} 個任務為 in_progress: {updated}")
