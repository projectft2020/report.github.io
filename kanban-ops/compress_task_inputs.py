#!/usr/bin/env python3
"""
Simple task input compressor

Usage:
    python3 compress_task_inputs.py <task_id>
"""

import sys
import json
from pathlib import Path

# Add kanban-ops to path
sys.path.insert(0, str(Path.home() / '.openclaw' / 'workspace' / 'kanban-ops'))

from input_extractor import extract_key_info

# Paths
TASKS_JSON = Path.home() / '.openclaw' / 'workspace-automation' / 'kanban' / 'tasks.json'


def compress_task(task_id: str):
    """Compress inputs for a task"""

    # Load tasks
    with open(TASKS_JSON, 'r') as f:
        data = json.load(f)

    # Find task
    task = None
    for t in data.get('tasks', []):
        if t.get('id') == task_id or t['id'].endswith(task_id):
            task = t
            break

    if not task:
        print(f"❌ Task not found: {task_id}")
        return 1

    # Get input paths
    input_paths = task.get('input_paths', [])

    if not input_paths:
        print(f"ℹ️  No input paths for task: {task_id}")
        return 0

    print(f"📦 Compressing {len(input_paths)} input files...")

    total_original = 0
    total_compressed = 0

    for input_path in input_paths:
        path = Path(input_path)
        if path.exists():
            result = extract_key_info(str(path), verbose=False)

            orig = result.get('original_size', 0)
            comp = result.get('compressed_size', 0)
            ratio = result.get('compression_ratio', 0)

            total_original += orig
            total_compressed += comp

            print(f"  → {path.name}: {orig//1024}KB → {comp//1024}KB (節省 {ratio:.1f}%)")
        else:
            print(f"  ⚠️  File not found: {input_path}")

    if total_original > 0:
        saved = (1 - total_compressed / total_original) * 100
        print(f"\n✅ Total: {total_original//1024}KB → {total_compressed//1024}KB (節省 {saved:.1f}%)")

    return 0


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 compress_task_inputs.py <task_id>")
        sys.exit(1)

    task_id = sys.argv[1]
    sys.exit(compress_task(task_id))
