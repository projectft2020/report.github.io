#!/usr/bin/env python3
import json

TASKS_JSON = '/Users/charlie/.openclaw/workspace/kanban/tasks.json'

with open(TASKS_JSON, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 有描述的已完成任務
completed_with_desc = [t for t in data if t.get('status') == 'completed' and t.get('description')]
# 有描述的失敗任務
failed_with_desc = [t for t in data if t.get('status') == 'failed' and t.get('description')]

print('✅ 有描述的成功任務範例:')
for t in completed_with_desc[:5]:
    print(f'  [{t["id"]}] {t["title"][:50]}')
    print(f'      描述: {t["description"][:80]}')
    print(f'      Agent: {t.get("agent", "N/A")} | Model: {t.get("model", "N/A")}')
    print()

print('❌ 有描述的失敗任務範例:')
for t in failed_with_desc[:5]:
    print(f'  [{t["id"]}] {t["title"][:50]}')
    print(f'      描述: {t["description"][:80]}')
    print(f'      Agent: {t.get("agent", "N/A")} | Model: {t.get("model", "N/A")}')
    print()
