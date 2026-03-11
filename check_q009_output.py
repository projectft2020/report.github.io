#!/usr/bin/env python3
import json
import os

TASKS_JSON = '/Users/charlie/.openclaw/workspace/kanban/tasks.json'

with open(TASKS_JSON, 'r', encoding='utf-8') as f:
    data = json.load(f)
    q009 = next((t for t in data if t['id'] == 'q009'), None)
    if q009:
        output_path = q009.get('output_path', 'N/A')
        project = q009.get('project', 'N/A')
        print(f'輸出路徑: {output_path}')
        print(f'專案: {project}')
        print(f'完整路徑: ~/kanban/{output_path}')
        print()

        # 檢查檔案是否存在
        full_path = os.path.expanduser('~/kanban/' + output_path)
        exists = os.path.exists(full_path)
        print(f'檔案存在: {exists}')

        # 檢查目錄
        dir_path = os.path.dirname(full_path)
        dir_exists = os.path.exists(dir_path)
        print(f'目錄存在: {dir_exists} ({dir_path})')
