#!/usr/bin/env python3
"""
Task Input Preprocessor

Automatically compresses input files for OpenClaw sub-agents.
This integrates with the task execution pipeline.
"""

import sys
import json
from pathlib import Path

# Add kanban-ops to path
sys.path.insert(0, str(Path.home() / '.openclaw' / 'workspace' / 'kanban-ops'))

from input_extractor import extract_key_info, extract_multiple_files


def preprocess_task_inputs(task: dict) -> dict:
    """
    Preprocess task inputs by compressing all input_paths files.

    Args:
        task: Task dictionary with input_paths

    Returns:
        Modified task with compressed_inputs added
    """
    if not task.get('input_paths'):
        return task

    print(f"\n🔄 Preprocessing {len(task['input_paths'])} input files...")

    # Extract key info from all input files
    compressed_inputs = extract_multiple_files(task['input_paths'])

    # Add compressed inputs to task
    task['compressed_inputs'] = compressed_inputs
    task['preprocessing_stats'] = {
        'original_files': len(task['input_paths']),
        'compressed_files': len(compressed_inputs),
        'compression_applied': True
    }

    return task


def main():
    """CLI interface"""
    if len(sys.argv) < 2:
        print("Usage: python3 input_preprocessor.py <tasks.json>")
        sys.exit(1)

    tasks_file = Path(sys.argv[1])

    if not tasks_file.exists():
        print(f"❌ File not found: {tasks_file}")
        sys.exit(1)

    # Load tasks
    with open(tasks_file, 'r') as f:
        data = json.load(f)

    tasks = data.get('tasks', [])

    if not tasks:
        print("❌ No tasks found")
        sys.exit(1)

    print(f"📦 Processing {len(tasks)} tasks...")

    # Process each task
    for task in tasks:
        task = preprocess_task_inputs(task)

    # Save back with compressed inputs
    output_file = tasks_file.parent / f"{tasks_file.stem}_preprocessed.json"
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Saved preprocessed tasks to: {output_file}")

    # Show stats
    total_original = sum(
        sum(t.get('compressed_inputs', {}).get(f, {}).get('original_size', 0)
            for f in t.get('compressed_inputs', {}))
        for t in tasks
    )

    total_compressed = sum(
        sum(t.get('compressed_inputs', {}).get(f, {}).get('compressed_size', 0)
            for f in t.get('compressed_inputs', {}))
        for t in tasks
    )

    if total_original > 0:
        saved_percent = (1 - total_compressed / total_original) * 100
        print(f"\n📊 Overall compression:")
        print(f"   Original: {total_original // 1024}KB")
        print(f"   Compressed: {total_compressed // 1024}KB")
        print(f"   Saved: {saved_percent:.1f}%")


if __name__ == '__main__':
    main()
