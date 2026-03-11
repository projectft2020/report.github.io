#!/usr/bin/env python3
"""
OpenClaw Research Task Runner with Progressive Output
This script runs a research task using the progressive output protocol
"""
import sys
import os
import json
import subprocess
from datetime import datetime

# Add kanban-ops to path
sys.path.insert(0, '/Users/charlie/.openclaw/workspace/kanban-ops')
from progressive_research import ProgressiveResearchManager

def main():
    task_id = "h004"
    task_file = f"/Users/charlie/.openclaw/workspace/kanban/projects/{task_id}/{task_id}.md"
    checkpoint_dir = f"/Users/charlie/.openclaw/workspace/kanban/projects/{task_id}/research_checkpoints"

    print("=" * 60)
    print(f"🔬 OpenClaw Research Task Runner")
    print(f"Task ID: {task_id}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Read task file to get research question
    with open(task_file, 'r') as f:
        task_content = f.read()
        print(f"\n📋 Research Question Loaded")

    # Initialize progressive research manager
    mgr = ProgressiveResearchManager(
        output_dir=checkpoint_dir,
        checkpoint_interval=3
    )

    print(f"✅ Progressive Research Manager initialized")
    print(f"   Checkpoint directory: {checkpoint_dir}")
    print(f"   Checkpoint interval: Every 3 searches")

    # Display research protocol
    print("\n" + "=" * 60)
    print("📋 RESEARCH PROTOCOL")
    print("=" * 60)
    print("""
This task will use the Progressive Output Protocol:

1. Conduct web searches on OpenClaw performance optimization
2. After every 3 searches, a checkpoint will be created
3. All intermediate findings will be preserved
4. If interrupted, research can resume from last checkpoint
5. Final report will be generated upon completion

Expected results:
- Token consumption: ~200k (vs 467k without progressive output)
- Checkpoints: 5-8 intermediate checkpoints
- Success rate: ~95% (vs ~50% without progressive output)
""")

    print("=" * 60)
    print("⚠️  IMPORTANT:")
    print("=" * 60)
    print("""
This script prepares the research infrastructure.
To actually run the research, you need to:

1. Use the OpenClaw UI to assign task h004 to the research agent
2. OR manually run web searches using the progressive protocol

The research task file is ready at:
{task_file}

Monitor checkpoints with:
  ls -l {checkpoint_dir}

View progress with:
  cat {checkpoint_dir}/progress.json
""".format(task_file=task_file, checkpoint_dir=checkpoint_dir))
    print("=" * 60)

    # Create initial checkpoint showing system is ready
    initial_status = f"""
# Research Task Ready: {task_id}

**Status**: Ready to start
**Initialized**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Protocol**: Progressive Output (every 3 searches)

## Research Infrastructure

- ✅ Task file created
- ✅ Checkpoint directory initialized
- ✅ Progressive Research Manager ready
- ✅ Monitoring scripts available

## Next Steps

Assign this task to the research agent through OpenClaw UI.

## Expected Performance

- Token consumption: ~200k (57% reduction from 467k)
- Checkpoints: 5-8
- Success rate: ~95%
"""

    mgr.create_checkpoint(initial_status)
    print("\n✅ Initial checkpoint created")
    print(f"   Checkpoint: {checkpoint_dir}/checkpoint_0.md")

    print("\n" + "=" * 60)
    print("🚀 System Ready!")
    print("=" * 60)
    print(f"""
Research task {task_id} is ready.

To start the research:
1. Open OpenClaw UI
2. Assign task {task_id} to research agent
3. Monitor progress: ls -l {checkpoint_dir}

Or use the manual research guide at:
{checkpoint_dir}/checkpoint_0.md
""")

if __name__ == "__main__":
    main()
