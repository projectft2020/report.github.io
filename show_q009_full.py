#!/usr/bin/env python3
import json

TASKS_JSON = '/Users/charlie/.openclaw/workspace/kanban/tasks.json'

with open(TASKS_JSON, 'r', encoding='utf-8') as f:
    data = json.load(f)
    q009 = next((t for t in data if t['id'] == 'q009'), None)
    if q009:
        print(json.dumps(q009, indent=2, ensure_ascii=False))
