#!/usr/bin/env python3
"""
Topic Visualizer - 主題知識地圖視覺化工具

創建超酷的 ASCII 藝術風格主題地圖視覺化。

使用方式：
    python3 kanban-ops/topic_visualizer.py
"""

import json
from collections import Counter, defaultdict


def print_header(title, width=67):
    """打印標題框"""
    print()
    print(' ' * ((100 - width) // 2) + '╔' + '═' * (width - 2) + '╗')
    print(' ' * ((100 - width) // 2) + '║' + ' ' * ((width - len(title) - 2) // 2) + title + ' ' * ((width - len(title) - 2) // 2) + '║')
    print(' ' * ((100 - width) // 2) + '╚' + '═' * (width - 2) + '╝')


def print_section(title, width=67):
    """打印分區標題"""
    print(' ' * ((100 - width) // 2) + '╔' + '═' * (width - 2) + '╗')
    print(' ' * ((100 - width) // 2) + '║' + ' ' + title + ' ' * (width - len(title) - 4) + '║')
    print(' ' * ((100 - width) // 2) + '╚' + '═' * (width - 2) + '╝')


def analyze_tasks(tasks):
    """分析任務並按主題分類"""
    pending_tasks = [t for t in tasks if t.get('status') == 'pending']

    theme_counts = Counter()
    task_by_theme = defaultdict(list)

    for task in pending_tasks:
        title = task.get('title', '').lower()
        source = task.get('source', '')

        if 'quant' in title or 'strategy' in title or 'trading' in title:
            theme = '量化策略'
            emoji = '📈'
        elif 'machine learning' in title or 'deep learning' in title or 'neural' in title:
            theme = '機器學習'
            emoji = '🧠'
        elif 'risk' in title or 'volatility' in title:
            theme = '風險管理'
            emoji = '🛡️'
        elif 'arxiv' in source:
            theme = '學術研究'
            emoji = '📚'
        elif 'reddit' in source or 'quantocracy' in source or 'threads' in source:
            theme = '社群討論'
            emoji = '💬'
        else:
            theme = '其他'
            emoji = '📦'

        theme_counts[theme] += 1
        task_by_theme[theme].append((task, emoji))

    return theme_counts, task_by_theme, pending_tasks


def draw_knowledge_map():
    """繪製知識地圖"""
    print()
    print(' ' * 32 + '        📊')
    print(' ' * 30 + '      ┌─────────┐')
    print(' ' * 30 + '      │Quantitative│')
    print(' ' * 30 + '      │  Research   │')
    print(' ' * 30 + '      └─────┬───────┘')
    print(' ' * 34 + '           │')
    print(' ' * 34 + '           ├─── Quant ──┐')
    print(' ' * 34 + '           ├─── ML ─────┤')
    print(' ' * 34 + '           └─── Risk ───┘')
    print(' ' * 34 + '              │')
    print(' ' * 34 + '              ▼')
    print(' ' * 32 + '        ┌─────────┐')
    print(' ' * 32 + '        │ Insights│')
    print(' ' * 32 + '        └─────────┘')
    print()


def draw_theme_cards(theme_counts, task_by_theme, total_tasks):
    """繪製主題卡片"""
    print_section('📦 主題卡片')

    for theme, count in theme_counts.most_common():
        percentage = (count / total_tasks) * 100

        # 根據百分比選擇卡片風格
        if percentage > 10:
            border = '█'
            intensity = '🔥'
        elif percentage > 5:
            border = '▓'
            intensity = '⭐'
        else:
            border = '░'
            intensity = '✨'

        # 卡片
        print(' ' * 28 + f'┌─{border * 45}─┐')
        print(' ' * 28 + f'│ {intensity} {theme:<20} {count:>3} 個 ({percentage:5.1f}%) {" " * 6}│')

        # 進度條
        bar_length = int(percentage * 0.4)
        bar = '█' * bar_length + '·' * (40 - bar_length)
        print(' ' * 28 + f'│ {bar} │')

        # 示例任務
        tasks_in_theme = [t for t, _ in task_by_theme[theme]][:2]
        for task in tasks_in_theme:
            title = task.get('title', '')[:40]
            print(' ' * 28 + f'│ • {title}{" " * (48 - len(title))}│')

        if len(task_by_theme[theme]) > 2:
            print(' ' * 28 + f'│ ... 還有 {len(task_by_theme[theme]) - 2} 個任務{" " * (32 - len(str(len(task_by_theme[theme]) - 2)))}│')

        print(' ' * 28 + f'└─{border * 45}─┘')
        print()


def draw_dashboard(tasks, pending_tasks, theme_counts):
    """繪製統計儀表板"""
    print_section('📊 統計儀表板')

    total = len(tasks)
    completed = sum(1 for t in tasks if t.get('status') == 'completed')
    completion_rate = (completed / total) * 100 if total > 0 else 0

    # 統計指標
    metrics = [
        ('📦 總任務數', f'{total} 個'),
        ('✅ 已完成', f'{completed} 個'),
        ('📋 待辦', f'{len(pending_tasks)} 個'),
        ('🎯 主題數', f'{len(theme_counts)} 個'),
        ('📈 完成率', f'{completion_rate:.1f}%'),
        ('⚡ 活躍度', '🟢 正常'),
    ]

    for i, (label, value) in enumerate(metrics):
        if i % 2 == 0:
            print(' ' * 28, end='')
        print(f'  {label:<10} {value:>10}', end='')
        if i % 2 == 1:
            print()
        elif i == len(metrics) - 1:
            print()

    print()
    print(' ' * 25 + '═════════════════════════════════════════════════════════')
    print(' ' * 38 + '✨ 數據更新時間: 2026-02-28')
    print()


def generate_visualization(tasks_json='kanban/tasks.json'):
    """生成完整的視覺化"""
    # 載入任務
    with open(tasks_json, 'r') as f:
        tasks = json.load(f)

    # 分析任務
    theme_counts, task_by_theme, pending_tasks = analyze_tasks(tasks)

    # 繪製視覺化
    print_header('🌟 主題知識地圖')
    draw_knowledge_map()
    draw_theme_cards(theme_counts, task_by_theme, len(pending_tasks))
    draw_dashboard(tasks, pending_tasks, theme_counts)


def main():
    """主函數"""
    import sys
    tasks_json = sys.argv[1] if len(sys.argv) > 1 else 'kanban/tasks.json'
    generate_visualization(tasks_json)


if __name__ == '__main__':
    main()
