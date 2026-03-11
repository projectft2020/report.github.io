# Research Agent - Progressive Output Protocol

## 🎯 Purpose

This protocol must be followed when conducting research tasks to:
- Avoid token explosion (reduce from 467k to ~200k)
- Ensure intermediate results are preserved
- Improve reliability and success rate from ~50% to ~95%
- Enable recovery from interruptions

---

## 📋 Protocol for Research Tasks

**CRITICAL**: When creating or executing research tasks, include this protocol in the task instructions.

### System Instructions for Research Agent

```markdown
# Progressive Output Protocol

You are conducting research with **UNLIMITED search capability**. However, you MUST follow this checkpoint protocol to ensure reliability:

## MANDATORY RULES

1. **Initialize Progressive Research Manager**
   - At the start of research, initialize the checkpoint system:
   ```python
   import sys
   sys.path.insert(0, '/Users/charlie/.openclaw/workspace/kanban-ops')
   from progressive_research import ProgressiveResearchManager

   # Initialize manager
   mgr = ProgressiveResearchManager(
       output_dir='<current_task_output_directory>',
       checkpoint_interval=3
   )
   ```

2. **Record Every Search**
   - After EACH web search, record it:
   ```python
   need_checkpoint = mgr.record_search(
       query="<your search query>",
       results="<search results or summary>"
   )
   ```

3. **Create Checkpoint Every 3 Searches**
   - When `need_checkpoint` returns True, IMMEDIATELY create checkpoint:
   ```python
   if need_checkpoint:
       # Synthesize findings from last 3 searches
       synthesis = """
       ## Key Findings from Searches X-Y

       - Finding 1: <insight>
       - Finding 2: <insight>
       - Finding 3: <insight>

       ## Patterns Observed
       <connections between searches>

       ## Next Research Direction
       <what to explore next>
       """

       checkpoint_file = mgr.create_checkpoint(synthesis)
       print(f"✅ Checkpoint created: {checkpoint_file}")
   ```

4. **Final Synthesis**
   - After all searches complete, load ALL checkpoints and synthesize:
   ```python
   # Load all checkpoints
   all_checkpoints = mgr.load_checkpoints()

   # Create final comprehensive report
   final_report = """
   # <Research Topic> - Final Report

   ## Executive Summary
   <High-level overview>

   ## Key Findings
   <Synthesize ALL checkpoint findings>

   ## Analysis
   <Deep analysis and insights>

   ## Conclusions
   <Conclusions and recommendations>
   """

   final_file = mgr.create_final_report(final_report)
   print(f"✅ Final report: {final_file}")
   ```

## Checkpoint Format

Each checkpoint should contain:

```markdown
# Research Checkpoint N

## Searches Covered
- Search X: <query>
- Search Y: <query>
- Search Z: <query>

## Key Findings
<Concise synthesis of findings - 500-1000 words>

## Insights
<Patterns, connections, important observations>

## Next Research Directions
<What to explore based on these findings>
```

## Benefits

✅ No search limits - research as deeply as needed
✅ Fault tolerant - checkpoints preserve work even if interrupted
✅ Token efficient - only synthesized findings in context (57% reduction)
✅ Incremental progress - can see intermediate results
✅ Better insights - forced synthesis improves quality

## Example Workflow

```python
# === RESEARCH INITIALIZATION ===
import sys
sys.path.insert(0, '/Users/charlie/.openclaw/workspace/kanban-ops')
from progressive_research import ProgressiveResearchManager

mgr = ProgressiveResearchManager(
    output_dir='/Users/charlie/.openclaw/workspace/kanban/projects/<task_id>',
    checkpoint_interval=3
)

checkpoint_number = 0

# === RESEARCH PHASE 1 ===
queries_phase1 = [
    "HFT microstructure basics",
    "order book dynamics",
    "market making strategies"
]

for query in queries_phase1:
    results = web_search(query)  # Your search method
    need_checkpoint = mgr.record_search(query, results)

    if need_checkpoint:
        checkpoint_number += 1
        synthesis = synthesize_findings()  # Your synthesis logic
        mgr.create_checkpoint(synthesis)
        print(f"✅ Checkpoint {checkpoint_number} created")

# === RESEARCH PHASE 2 ===
queries_phase2 = [
    "latency arbitrage",
    "quote stuffing detection",
    "tick size impact"
]

for query in queries_phase2:
    results = web_search(query)
    need_checkpoint = mgr.record_search(query, results)

    if need_checkpoint:
        checkpoint_number += 1
        # Load previous checkpoint for context
        prev_checkpoints = mgr.load_checkpoints()
        synthesis = synthesize_with_context(prev_checkpoints)
        mgr.create_checkpoint(synthesis)
        print(f"✅ Checkpoint {checkpoint_number} created")

# === FINAL SYNTHESIS ===
all_checkpoints = mgr.load_checkpoints()
final_report = create_comprehensive_report(all_checkpoints)
mgr.create_final_report(final_report)

# === SHOW PROGRESS ===
print(mgr.generate_progress_report())
```

## Recovery from Interruption

If research is interrupted, you can resume:

```python
# Resume from existing checkpoints
num_checkpoints, checkpoints = mgr.resume_from_checkpoints()

# Continue from where you left off
# Next checkpoint will be checkpoint N+1
```

---

**REMEMBER**:
- Create checkpoint EVERY 3 searches
- Synthesize findings at each checkpoint
- Final report synthesizes ALL checkpoints
- Do NOT include raw search results in final report
```

---

## 🔧 Integration Methods

### Method 1: Task Instructions

When creating a research task via kanban-ops, include this in the task prompt:

```python
task_prompt = """
<your research question>

IMPORTANT: You MUST follow the Progressive Output Protocol for this research.

See: /Users/charlie/.openclaw/workspace/kanban-ops/research_agent_progressive_protocol.md

Initialize ProgressiveResearchManager and create checkpoints every 3 searches.
"""
```

### Method 2: Pre-Task Setup Script

Create a helper script to setup research tasks:

```bash
#!/bin/bash
# setup_progressive_research.sh

TASK_ID=$1
RESEARCH_QUESTION=$2

TASK_DIR="/Users/charlie/.openclaw/workspace/kanban/projects/${TASK_ID}"
mkdir -p "${TASK_DIR}"

# Create task with progressive output protocol
cat > "${TASK_DIR}/task.md" << EOF
# Research Task: ${RESEARCH_QUESTION}

## Protocol
This task MUST use Progressive Output Protocol.

## Instructions
1. Initialize ProgressiveResearchManager from /Users/charlie/.openclaw/workspace/kanban-ops/progressive_research.py
2. Create checkpoint every 3 searches
3. Synthesize findings at each checkpoint
4. Create final report from all checkpoints

## Research Question
${RESEARCH_QUESTION}

EOF

echo "✅ Research task ${TASK_ID} created with Progressive Output Protocol"
```

### Method 3: Agent Configuration Override

For persistent configuration, you could create a custom research agent variant:

```bash
# In ~/.openclaw/agents/research-progressive/
# Copy research agent config and add default instructions
```

---

## 📊 Monitoring Integration

Track progressive research effectiveness:

```bash
# Check checkpoint creation across all research tasks
find ~/.openclaw/workspace/kanban/projects -name "checkpoint_*.md" | wc -l

# Check research tasks with checkpoints
find ~/.openclaw/workspace/kanban/projects -name "checkpoint_*.md" -exec dirname {} \; | sort -u

# Analyze checkpoint sizes
find ~/.openclaw/workspace/kanban/projects -name "checkpoint_*.md" -exec wc -l {} \; | \
  awk '{sum+=$1; count++} END {print "Avg checkpoint size:", sum/count, "lines"}'
```

---

## ✅ Verification Checklist

After implementing progressive output on a research task:

- [ ] ProgressiveResearchManager was initialized
- [ ] Checkpoints created every 3 searches
- [ ] Each checkpoint contains synthesized findings (not raw results)
- [ ] Final report exists and synthesizes all checkpoints
- [ ] Total token consumption < 250k (check logs)
- [ ] Research completed successfully (not terminated/timeout)

---

## 🎯 Expected Results

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Token consumption | 467k | ~200k | -57% |
| Success rate | ~50% | ~95% | +90% |
| Research depth | Limited (fear of timeout) | Unlimited | ∞ |
| Recovery capability | None | Full | 100% |
| Intermediate results | Lost | Preserved | 100% |

---

**This protocol is MANDATORY for all research tasks to prevent token explosion and ensure reliability.**
