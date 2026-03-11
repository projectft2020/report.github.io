#!/usr/bin/env python3
import json
from datetime import datetime, timezone

TASKS_JSON = '/Users/charlie/.openclaw/workspace/kanban/tasks.json'

with open(TASKS_JSON, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 更新 q006a 為 completed
for t in data:
    if t['id'] == 'q006a' and t['status'] == 'in_progress':
        t['status'] = 'completed'
        t['updated_at'] = datetime.now(timezone.utc).isoformat()
        print(f"✓ 任務 q006a 已標記為 completed")

with open(TASKS_JSON, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
