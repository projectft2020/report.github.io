#!/usr/bin/env python3
import json
from pathlib import Path

TASKS_JSON = Path.home() / ".openclaw" / "workspace" / "kanban" / "tasks.json"

with open(TASKS_JSON, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 按狀態分類
completed = [t for t in data if t.get('status') == 'completed']
in_progress = [t for t in data if t.get('status') == 'in_progress']
failed = [t for t in data if t.get('status') == 'failed']

print('📊 任務描述質量分析')
print('=' * 70)

# 統計描述長度
def avg_len(tasks):
    if not tasks:
        return 0
    return sum(len(t.get('description', '')) for t in tasks) / len(tasks)

print(f'✅ 已完成 ({len(completed)}): 平均 {avg_len(completed):.0f} 字')
print(f'🔄 進行中 ({len(in_progress)}): 平均 {avg_len(in_progress):.0f} 字')
print(f'❌ 失敗 ({len(failed)}): 平均 {avg_len(failed):.0f} 字')
print()

# 描述空的比例
def empty_ratio(tasks):
    if not tasks:
        return 0
    empty = sum(1 for t in tasks if not t.get('description'))
    return empty / len(tasks) * 100

print('📌 描述空的比例:')
print(f'  已完成: {empty_ratio(completed):.1f}%')
print(f'  進行中: {empty_ratio(in_progress):.1f}%')
print(f'  失敗: {empty_ratio(failed):.1f}%')
print()

# 有 output_path 的比例
def output_ratio(tasks):
    if not tasks:
        return 0
    has_output = sum(1 for t in tasks if t.get('output_path'))
    return has_output / len(tasks) * 100

print('📁 有 output_path 的比例:')
print(f'  已完成: {output_ratio(completed):.1f}%')
print(f'  進行中: {output_ratio(in_progress):.1f}%')
print(f'  失敗: {output_ratio(failed):.1f}%')
print()

# 樣本任務
print('📋 任務樣本:')
print('-' * 70)
for t in data[:15]:
    desc = t.get('description', 'N/A')[:60]
    has_output = '✓' if t.get('output_path') else '✗'
    has_agent = '✓' if t.get('agent') else '✗'
    print(f'[{t["id"]:10}] desc:{desc:60} output:{has_output} agent:{has_agent}')
