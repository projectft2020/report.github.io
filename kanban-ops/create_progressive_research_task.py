#!/usr/bin/env python3
"""
Helper script to create research tasks with Progressive Output Protocol

Usage:
    python3 create_progressive_research_task.py --task-id <id> --question "<research question>"

Example:
    python3 create_progressive_research_task.py \
        --task-id h003 \
        --question "Analyze the impact of high-frequency trading on market microstructure in 2026"
"""

import argparse
import json
from pathlib import Path
from datetime import datetime


PROGRESSIVE_RESEARCH_TEMPLATE = '''# Research Task: {question}

**Task ID**: {task_id}
**Created**: {timestamp}
**Protocol**: Progressive Output (Checkpoint every 3 searches)

---

## 🎯 Research Question

{question}

---

## 📋 MANDATORY: Progressive Output Protocol

⚠️ **CRITICAL**: This research MUST follow Progressive Output Protocol to avoid token explosion and ensure reliability.

### Step 1: Initialize Progressive Research Manager

```python
import sys
sys.path.insert(0, '/Users/charlie/.openclaw/workspace/kanban-ops')
from progressive_research import ProgressiveResearchManager

# Initialize manager for this task
mgr = ProgressiveResearchManager(
    output_dir='{task_output_dir}',
    checkpoint_interval=3
)

print("✅ Progressive Research Manager initialized")
print(f"Output directory: {task_output_dir}")
```

### Step 2: Conduct Research with Checkpoints

For EACH web search you perform:

```python
# Perform search
query = "your search query here"
results = web_search(query)  # or use your search method

# Record search
need_checkpoint = mgr.record_search(query, results)

# Create checkpoint if needed
if need_checkpoint:
    # Synthesize last 3 searches
    synthesis = """
    ## Key Findings from Last 3 Searches

    <Summarize the key insights from the last 3 searches>

    ## Patterns and Connections

    <Identify patterns across the searches>

    ## Next Research Direction

    <Based on findings, what should be explored next>
    """

    checkpoint_file = mgr.create_checkpoint(synthesis)
    print(f"✅ Checkpoint created: {{checkpoint_file.name}}")
```

### Step 3: Create Final Report

After all searches complete:

```python
# Load all checkpoints
all_checkpoints = mgr.load_checkpoints()

print(f"📊 Loaded {{len(all_checkpoints)}} checkpoints")

# Create comprehensive final report
final_report = """
# {question}

## Executive Summary

<High-level summary of all findings>

## Methodology

Total web searches: {{mgr.search_count}}
Checkpoints created: {{len(all_checkpoints)}}

## Key Findings

<Synthesize findings from ALL checkpoints - not raw search results>

### Finding 1: <Major Finding>

<Details>

### Finding 2: <Major Finding>

<Details>

### Finding 3: <Major Finding>

<Details>

## Analysis and Insights

<Deep analysis connecting all findings>

## Conclusions

<Main conclusions>

## Recommendations

<Actionable recommendations based on research>

---

## Research Statistics

- Total searches performed: {{mgr.search_count}}
- Checkpoints created: {{len(all_checkpoints)}}
- Average searches per checkpoint: {{mgr.search_count / len(all_checkpoints):.1f}}
"""

final_file = mgr.create_final_report(final_report)
print(f"✅ Final report created: {{final_file}}")

# Show progress summary
print(mgr.generate_progress_report())
```

---

## 📊 Expected Outcome

Your research will:
- ✅ Create checkpoints every 3 searches (preserving intermediate work)
- ✅ Reduce total token consumption by ~57% (from 467k to ~200k)
- ✅ Enable recovery if interrupted
- ✅ Produce high-quality synthesized report

---

## 🔍 Verification

After completion, verify:
- [ ] Checkpoint files exist: `ls -l {task_output_dir}/checkpoint_*.md`
- [ ] Final report exists: `cat {task_output_dir}/final_report.md`
- [ ] Total searches recorded: Check `{task_output_dir}/research_metadata.json`
- [ ] Token consumption < 250k: Check task logs

---

## 🚨 Important Notes

1. **DO NOT skip checkpoints** - they are mandatory every 3 searches
2. **DO synthesize at each checkpoint** - don't just copy raw results
3. **DO load previous checkpoints** - use them for context in synthesis
4. **DO create final report** - synthesize ALL checkpoints into comprehensive report

---

**Start your research below this line following the protocol above.**

---

'''


def create_research_task(task_id: str, question: str, workspace_path: str = None):
    """
    Create a progressive research task

    Args:
        task_id: Task identifier
        question: Research question
        workspace_path: Workspace base path (default: ~/.openclaw/workspace)
    """
    if workspace_path is None:
        workspace_path = Path.home() / '.openclaw' / 'workspace'
    else:
        workspace_path = Path(workspace_path)

    # Create task directory
    task_dir = workspace_path / 'kanban' / 'projects' / task_id
    task_dir.mkdir(parents=True, exist_ok=True)

    # Create checkpoint directory
    checkpoint_dir = task_dir / 'research_checkpoints'
    checkpoint_dir.mkdir(exist_ok=True)

    # Generate task file
    task_file = task_dir / f'{task_id}.md'

    task_content = PROGRESSIVE_RESEARCH_TEMPLATE.format(
        task_id=task_id,
        question=question,
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        task_output_dir=str(checkpoint_dir)
    )

    task_file.write_text(task_content, encoding='utf-8')

    print(f"✅ Progressive research task created:")
    print(f"   Task ID:      {task_id}")
    print(f"   Task file:    {task_file}")
    print(f"   Checkpoint dir: {checkpoint_dir}")
    print(f"   Question:     {question}")
    print()
    print("📋 Next steps:")
    print(f"   1. Review task file: cat {task_file}")
    print(f"   2. Assign to research agent")
    print(f"   3. Monitor checkpoints: ls -l {checkpoint_dir}")
    print()

    return task_file, checkpoint_dir


def add_progressive_protocol_to_existing_task(task_file_path: str):
    """
    Add progressive protocol to an existing research task

    Args:
        task_file_path: Path to existing task file
    """
    task_file = Path(task_file_path)

    if not task_file.exists():
        raise FileNotFoundError(f"Task file not found: {task_file_path}")

    # Read existing content
    original_content = task_file.read_text(encoding='utf-8')

    # Extract task info
    task_dir = task_file.parent
    task_id = task_dir.name
    checkpoint_dir = task_dir / 'research_checkpoints'
    checkpoint_dir.mkdir(exist_ok=True)

    # Create protocol section
    protocol_section = f'''
---

## 🔄 PROGRESSIVE OUTPUT PROTOCOL ADDED

⚠️ **This task has been updated to use Progressive Output Protocol**

### Setup Progressive Research Manager

```python
import sys
sys.path.insert(0, '/Users/charlie/.openclaw/workspace/kanban-ops')
from progressive_research import ProgressiveResearchManager

mgr = ProgressiveResearchManager(
    output_dir='{checkpoint_dir}',
    checkpoint_interval=3
)
```

### Follow Protocol

1. **Record each search**: `need_checkpoint = mgr.record_search(query, results)`
2. **Create checkpoint when needed**: Every 3 searches, synthesize and create checkpoint
3. **Final report**: Load all checkpoints and create comprehensive final report

See: /Users/charlie/.openclaw/workspace/kanban-ops/research_agent_progressive_protocol.md

---

'''

    # Prepend protocol to existing content
    updated_content = protocol_section + original_content

    # Backup original
    backup_file = task_file.with_suffix('.md.backup')
    task_file.rename(backup_file)

    # Write updated content
    task_file.write_text(updated_content, encoding='utf-8')

    print(f"✅ Progressive protocol added to existing task:")
    print(f"   Task file:     {task_file}")
    print(f"   Backup:        {backup_file}")
    print(f"   Checkpoint dir: {checkpoint_dir}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Create progressive research tasks with checkpoint protocol"
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Create new task
    create_parser = subparsers.add_parser('create', help='Create new progressive research task')
    create_parser.add_argument('--task-id', required=True, help='Task ID (e.g., h003)')
    create_parser.add_argument('--question', required=True, help='Research question')
    create_parser.add_argument('--workspace', help='Workspace path (default: ~/.openclaw/workspace)')

    # Update existing task
    update_parser = subparsers.add_parser('update', help='Add protocol to existing task')
    update_parser.add_argument('--task-file', required=True, help='Path to existing task file')

    args = parser.parse_args()

    if args.command == 'create':
        create_research_task(
            task_id=args.task_id,
            question=args.question,
            workspace_path=args.workspace
        )
    elif args.command == 'update':
        add_progressive_protocol_to_existing_task(args.task_file)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
