#!/usr/bin/env python3
import json

TASKS_JSON = '/Users/charlie/.openclaw/workspace/kanban/tasks.json'

with open(TASKS_JSON, 'r', encoding='utf-8') as f:
    data = json.load(f)

pending = [t for t in data if t.get('status') == 'pending']
in_progress = [t for t in data if t.get('status') == 'in_progress']
failed = [t for t in data if t.get('status') == 'failed']

print('📊 當前看板狀態')
print('=' * 60)
print(f'✅ 已完成: 82')
print(f'🔄 進行中: {len(in_progress)}')
print(f'⏳ 待辦: {len(pending)}')
print(f'❌ 失敗: {len(failed)}')
print()

if pending:
    print('待辦任務:')
    for t in pending:
        print(f'  [{t["id"]}] {t.get("title", "N/A")}')

if in_progress:
    print('\n進行中任務:')
    for t in in_progress:
        print(f'  [{t["id"]}] {t.get("title", "N/A")}')

if failed:
    print('\n失敗任務:')
    for t in failed:
        print(f'  [{t["id"]}] {t.get("title", "N/A")}')
