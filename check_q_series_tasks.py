#!/usr/bin/env python3
import json
import os

TASKS_JSON = '/Users/charlie/.openclaw/workspace/kanban/tasks.json'

with open(TASKS_JSON, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 檢查 q005-q011 任務
tasks_to_check = ['q005a', 'q005b', 'q006a', 'q006b', 'q007', 'q008', 'q009', 'q010', 'q011']

print('任務狀態檢查 (q005a - q011):')
print('=' * 80)

for task_id in tasks_to_check:
    task = next((t for t in data if t['id'] == task_id), None)
    if task:
        status = task.get('status', 'N/A')
        output_path = task.get('output_path', 'N/A')
        project = task.get('project', 'N/A')

        # 檢查輸出檔案
        if output_path:
            full_path = os.path.expanduser('~/.openclaw/workspace/kanban/' + output_path)
            exists = os.path.exists(full_path)
        else:
            full_path = 'N/A'
            exists = False

        print(f'[{task_id}] {status}')
        print(f'  Project: {project}')
        print(f'  Output: {output_path}')
        print(f'  File: {"✓" if exists else "✗"} {full_path}')
        print()
