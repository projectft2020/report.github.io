#!/usr/bin/env python3
import json
import os

TASKS_JSON = '/Users/charlie/.openclaw/workspace/kanban/tasks.json'

with open(TASKS_JSON, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 檢查 q005a 的正確路徑
q005a = next((t for t in data if t['id'] == 'q005a'), None)
if q005a:
    output_path = q005a.get('output_path', 'N/A')
    print(f'Output path: {output_path}')
    print()

    # 檢查所有可能的完整路徑
    paths_to_try = [
        f'~/.openclaw/workspace/{output_path}',
        f'~/.openclaw/workspace/kanban/{output_path}',
        f'~/kanban/{output_path}',
    ]

    for path in paths_to_try:
        full_path = os.path.expanduser(path)
        exists = os.path.exists(full_path)
        print(f'{path}')
        print(f'  Full: {full_path}')
        print(f'  Exists: {"✓" if exists else "✗"}')
        print()
