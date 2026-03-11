#!/usr/bin/env python3
import json
import os

TASKS_JSON = '/Users/charlie/.openclaw/workspace/kanban/tasks.json'

with open(TASKS_JSON, 'r', encoding='utf-8') as f:
    data = json.load(f)
    q009 = next((t for t in data if t['id'] == 'q009'), None)
    if q009:
        output_path = q009.get('output_path', 'N/A')
        print(f'輸出路徑: {output_path}')
        print()

        # 嘗試不同的路徑
        paths_to_try = [
            os.path.expanduser('~/kanban/' + output_path),
            os.path.expanduser('~/.openclaw/workspace/' + output_path),
            os.path.expanduser('~/.openclaw/workspace/kanban/' + output_path),
        ]

        for path in paths_to_try:
            exists = os.path.exists(path)
            print(f'  {path}')
            print(f'  存在: {"✓" if exists else "✗"}')
            print()
