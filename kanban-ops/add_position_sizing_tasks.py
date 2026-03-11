#!/usr/bin/env python3
"""Add position sizing papers to kanban tasks.json"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Paths
kanban_root = Path(__file__).parent.parent
tasks_path = kanban_root / "kanban" / "tasks.json"
add_path = kanban_root / "kanban" / "tasks" / "add_position_sizing_papers.json"

# Load existing tasks
with open(tasks_path, 'r') as f:
    existing_tasks = json.load(f)

# Load new tasks
with open(add_path, 'r') as f:
    new_tasks_data = json.load(f)
    new_tasks = new_tasks_data['tasks']

# Get existing task IDs
existing_ids = {task['id'] for task in existing_tasks}

# Add new tasks with full schema
added_count = 0
for task in new_tasks:
    if task['id'] in existing_ids:
        print(f"⏭️  Skipping existing task: {task['id']}")
        continue

    # Create full task object
    full_task = {
        "id": task['id'],
        "project_id": "position-sizing-2026",
        "title": task['title'],
        "status": task['status'],
        "agent": task['type'],  # research
        "model": task['metadata']['model'],
        "priority": task['priority'],
        "input_paths": [],
        "output_path": f"kanban/projects/position-sizing-2026/{task['id']}-research.md",
        "depends_on": task['dependencies'],
        "next_tasks": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
        "notes": task['description'],
        "time_tracking": {
            "estimated_time": {
                "min": int(task['metadata']['estimated_time'].split('-')[0].strip()),
                "max": int(task['metadata']['estimated_time'].split('-')[1].split(' ')[0].strip())
            },
            "complexity_level": int(task['metadata']['complexity'] * 5),
            "recommended_model": task['metadata']['model']
        },
        "created_by": "user",
        "metadata": task['metadata']
    }

    existing_tasks.append(full_task)
    added_count += 1
    print(f"✅ Added task: {task['id']} - {task['title']}")

# Save updated tasks
with open(tasks_path, 'w') as f:
    json.dump(existing_tasks, f, indent=2)

print(f"\n📊 Summary:")
print(f"   Existing tasks: {len(existing_tasks) - added_count}")
print(f"   New tasks added: {added_count}")
print(f"   Total tasks: {len(existing_tasks)}")
