#!/usr/bin/env python3
"""分析 backlog 任務分佈"""

import json
from datetime import datetime, timedelta, timezone

with open('/Users/charlie/.openclaw/workspace/kanban/tasks.json', 'r') as f:
    tasks = json.load(f)

now = datetime.now(timezone.utc)
backlog_tasks = [t for t in tasks if t.get('status') == 'backlog']

# 分析創建時間
creation_times = [t.get('created_at', '') for t in backlog_tasks if t.get('created_at')]
if creation_times:
    creation_times.sort()
    oldest = creation_times[0]
    newest = creation_times[-1]
    print(f'📊 Backlog 任務創建時間分析')
    print(f'=' * 50)
    print(f'總數: {len(backlog_tasks)}')
    print(f'最舊: {oldest}')
    print(f'最新: {newest}')
    print()

# 計算不同時間段的任務數量
def count_tasks_in_range(delta):
    count = 0
    for t in backlog_tasks:
        created_at = t.get('created_at')
        if not created_at:
            continue
        try:
            created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            if created.replace(tzinfo=None) > (now - delta).replace(tzinfo=None):
                count += 1
        except:
            pass
    return count

print(f'📅 Backlog 任務分佈')
print(f'=' * 50)
count_1d = count_tasks_in_range(timedelta(days=1))
count_7d = count_tasks_in_range(timedelta(days=7))
count_30d = count_tasks_in_range(timedelta(days=30))
count_90d = count_tasks_in_range(timedelta(days=90))

print(f'1 天內: {count_1d} ({count_1d/len(backlog_tasks)*100:.1f}%)')
print(f'7 天內: {count_7d} ({count_7d/len(backlog_tasks)*100:.1f}%)')
print(f'30 天內: {count_30d} ({count_30d/len(backlog_tasks)*100:.1f}%)')
print(f'90 天內: {count_90d} ({count_90d/len(backlog_tasks)*100:.1f}%)')
print(f'90 天以上: {len(backlog_tasks)-count_90d} ({(len(backlog_tasks)-count_90d)/len(backlog_tasks)*100:.1f}%)')

# 分析優先級分佈
print()
print(f'🎯 Backlog 優先級分佈')
print(f'=' * 50)
priority_dist = {}
for task in backlog_tasks:
    priority = task.get('priority', 'unknown')
    priority_dist[priority] = priority_dist.get(priority, 0) + 1

# 排序：數字優先，然後字串
def priority_key(p):
    if isinstance(p, int):
        return (0, p)
    else:
        return (1, str(p))

for priority in sorted(priority_dist.keys(), key=priority_key):
    count = priority_dist[priority]
    print(f'{priority}: {count} ({count/len(backlog_tasks)*100:.1f}%)')

# 標記可刪除的任務（> 30 天的 low 優先級）
print()
print(f'🗑️  可清理任務分析')
print(f'=' * 50)
deletable_30d_low = []
for task in backlog_tasks:
    created_at = task.get('created_at')
    priority = task.get('priority')
    if not created_at or priority != 'low':
        continue
    try:
        created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        if created.replace(tzinfo=None) <= (now - timedelta(days=30)).replace(tzinfo=None):
            deletable_30d_low.append(task)
    except:
        pass

print(f'> 30 天的 low 優先級任務: {len(deletable_30d_low)}')
if deletable_30d_low:
    sample = [t['id'] for t in deletable_30d_low[:5]]
    print(f'範例: {sample}')
