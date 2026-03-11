#!/usr/bin/env python3
import json
from datetime import datetime, timezone

TASKS_JSON = '/Users/charlie/.openclaw/workspace/kanban/tasks.json'

with open(TASKS_JSON, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 檢查 q009 詳細信息
q009 = next((t for t in data if t['id'] == 'q009'), None)
if q009:
    print('q009 任務信息:')
    print('=' * 60)
    print(f'標題: {q009.get("title")}')
    print(f'狀態: {q009.get("status")}')
    print(f'Agent: {q009.get("agent")}')
    print(f'Model: {q009.get("model")}')
    print(f'輸出路徑: {q009.get("output_path")}')
    print()

    # 時間信息
    created = q009.get('created_at', '')
    updated = q009.get('updated_at', '')

    if created:
        dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
        print(f'創建時間: {dt.strftime("%Y-%m-%d %H:%M:%S")}')

    if updated:
        dt = datetime.fromisoformat(updated.replace('Z', '+00:00'))
        time_ago = datetime.now(timezone.utc) - dt
        hours = time_ago.total_seconds() / 3600
        print(f'更新時間: {dt.strftime("%Y-%m-%d %H:%M:%S")} ({hours:.1f} 小時前)')

    # 依賴信息
    depends = q009.get('depends_on', [])
    if depends:
        print(f'依賴: {depends}')

    # 輸入文件
    inputs = q009.get('input_paths', [])
    if inputs:
        print(f'輸入文件 ({len(inputs)}):')
        for inp in inputs:
            print(f'  - {inp}')
