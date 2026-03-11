#!/usr/bin/env python3
import json

TASKS_JSON = '/Users/charlie/.openclaw/workspace/kanban/tasks.json'

with open(TASKS_JSON, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 檢查 q011 的依賴
q011 = next((t for t in data if t['id'] == 'q011'), None)
if q011:
    depends = q011.get('depends_on', [])
    print('q011 (跨市場最終整合報告) 依賴狀態:')
    print('=' * 60)
    print(f'依賴任務: {depends}')
    print()

    for dep_id in depends:
        dep_task = next((t for t in data if t['id'] == dep_id), None)
        if dep_task:
            status = dep_task.get('status')
            title = dep_task.get('title', 'N/A')

            # 檢查輸出檔案
            output_path = dep_task.get('output_path', '')
            exists = False
            if output_path:
                import os
                # 嘗試不同路徑
                paths = [
                    f'~/.openclaw/workspace/kanban/{output_path}',
                    f'~/.openclaw/workspace-analyst/kanban/{output_path}',
                ]
                for p in paths:
                    if os.path.exists(os.path.expanduser(p)):
                        exists = True
                        break

            file_status = "✓" if exists else "✗"
            print(f'  {dep_id}: {status} {file_status}')
            print(f'    標題: {title}')
            print()
