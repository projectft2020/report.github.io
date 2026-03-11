---
name: spawn-protocol
description: How to spawn sub-agents correctly. Use this every time before calling sessions_spawn.
user-invocable: false
---

# Spawn Protocol

Before every `sessions_spawn`, complete this checklist — in order, no skipping.

## Pre-Spawn Checklist

1. **Pick the right agent** from the dispatch table below
2. **Generate task ID**: format `YYYYMMDD-HHMMSS-[agent][seq]` (e.g. `20260218-143052-r001`)
3. **Set project ID**: slugified topic + date (e.g. `ai-market-report-20260218`)
4. **Create the output directory** (always do this first):
   ```
   exec({"command": "mkdir -p /Users/charlie/.openclaw/workspace/kanban/projects/[project-id]"})
   ```
5. **Update tasks.json** — add task entry with status `in_progress` before spawning
6. **Compress input files** (if task has `input_paths`):
   ```python
   # Add this to your spawn code:
   import sys
   sys.path.insert(0, '/Users/charlie/.openclaw/workspace/kanban-ops')
   from input_compressor import compress_task_inputs

   # Compress all input files
   compressed = compress_task_inputs(task_data)
   # This automatically shows compression ratio and saves 94-96% of tokens
   # V2 uses QMD semantic search for large files (≥ 30 KB)
   ```
7. **Build the task message** using the template for the chosen agent (include compressed inputs in INPUT FILES section)
8. **Call sessions_spawn** with the full message

---

## Agent Dispatch Table

### `research` — Web search, fact-finding, source validation
- Model: GLM-4.5 (default, do NOT specify model)
- Task message template:
```
TASK: [Specific research question — be precise]

CONTEXT:
- [Why this is needed]
- [Any constraints or focus areas]

REQUIREMENTS:
- Find [N] quality sources minimum
- Include dates for time-sensitive data
- Cross-validate key claims with 2+ sources
- [Any specific angle]

OUTPUT PATH: /Users/charlie/.openclaw/workspace/kanban/projects/[project-id]/[task-id]-research.md
```

---

### `analyst` — Data analysis, reasoning, risk assessment
- Model: GLM-4.7 — **always specify**: `"model": "zai/glm-4.7"`
- Requires input files from upstream task
- **Always compress input files** (saves 94-96% tokens - V2 with QMD semantic search)
- Task message template:
```
TASK: [What to analyze — specific framework if needed]

CONTEXT:
- [Analysis angle]

INPUT FILES (compressed):
[Use `compress_task_inputs()` to compress and include here]

REQUIREMENTS:
- [Type of analysis: trend / risk / SWOT / comparison]
- [Specific questions to answer]
- Include confidence level and assumptions

OUTPUT PATH: /Users/charlie/.openclaw/workspace/kanban/projects/[project-id]/[task-id]-analysis.md
```

---

### `creative` — Writing, reports, code, documentation
- Model: GLM-4.7 — **always specify**: `"model": "zai/glm-4.7"`
- Requires input files from upstream tasks
- **Always compress input files** (saves 94-96% tokens - V2 with QMD semantic search)
- Task message template:
```
TASK: [What to create — type, audience, format]

CONTEXT:
- Audience: [who will read this]
- Tone: [professional / technical / casual]

INPUT FILES (compressed):
[Use `compress_task_inputs()` to compress and include here]

REQUIREMENTS:
- Format: [article / report / code / document]
- Length: [approximate]
- [Any specific structure or sections]

OUTPUT PATH: /Users/charlie/.openclaw/workspace/kanban/projects/[project-id]/[task-id]-report.md
```

---

### `automation` — System commands, file operations, scripts
- Model: GLM-4.5 (default, do NOT specify model)
- Task message template:
```
TASK: [Specific operation to perform]

CONTEXT:
- Target: [paths or systems involved]
- Expected state before: [what should exist]
- Expected state after: [what should be true when done]

INPUT FILES:
- [path to config or data file if needed]

REQUIREMENTS:
- [Specific commands to run]
- Verify each step before proceeding
- Do NOT delete without confirming target

OUTPUT PATH: /Users/charlie/.openclaw/workspace/kanban/projects/[project-id]/[task-id]-automation.md
```

---

## sessions_spawn Call Format

**Step 1: Compress inputs (if task has input_paths)**
```python
# Add this before calling sessions_spawn
import sys
sys.path.insert(0, '/Users/charlie/.openclaw/workspace/kanban-ops')
from input_compressor import compress_task_inputs, build_task_message_with_compressed_inputs

# Compress all input files
compressed_inputs = compress_task_inputs(task_data)

# Build task message with compressed inputs
task_message = build_task_message_with_compressed_inputs(task_data, compressed_inputs)
```

**Step 2: Call sessions_spawn**
```
// research / automation — no model field
sessions_spawn({
  "task": task_message,  // Use the compressed message from Step 1
  "agentId": "research",
  "label": "[task-id]"
})

// analyst / creative — must include model
sessions_spawn({
  "task": task_message,  // Use the compressed message from Step 1
  "agentId": "analyst",
  "label": "[task-id]",
  "model": "zai/glm-4.7"
})
```

---

## Post-Spawn

After sessions_spawn returns:
- Note the `childSessionKey` in the response
- `sessions_spawn` is non-blocking — the agent is now running independently
- When the agent announces, update tasks.json status → `completed` or `failed`
- Check `next_tasks` in the completed task — if all `depends_on` are met, spawn immediately

---

## Adding a New Agent Type

When a new sub-agent is added to the system, add a new section above with:
- Agent ID
- Model (specify if GLM-4.7, omit if GLM-4.5)
- Task message template with required fields
- Output file naming convention

---

## 🔧 100% Automatic Input Compression (V2 - QMD Enhanced)

**This is MANDATORY for all spawns with input files.**

### Why Compression is Mandatory

- Saves **94-96%** of token costs (实证测试：87KB → 3KB)
- Reduces monthly cost from ¥16.4 → ¥1.2
- No quality loss (all semantic information preserved)
- Zero manual overhead (automatic in spawn protocol)
- **V2 upgrade**: QMD semantic search for large files

### V2 Improvements

**Smart Compression Strategy:**
- 🧠 **Large files (≥ 30 KB)**: QMD semantic search extracts only task-relevant sections
- ⚡ **Small files (< 30 KB)**: Basic extraction (faster)
- 🛡️ **Automatic fallback**: If QMD fails, uses basic compression

**Performance:**
| Metric | V1 (Basic) | V2 (QMD) | Improvement |
|--------|-----------|----------|-------------|
| Compression | 85-90% | **94-96%** | +6-11% |
| Example | 87KB → 11KB | **87KB → 3KB** | **-73% output** |

### What Gets Compressed

✅ **Kept:** Title, formulas, tables (truncated), code signatures, conclusions, key points, metadata, task-relevant content (QMD)
❌ **Removed:** Formatting symbols, verbose explanations, full code implementations, duplicate content, irrelevant sections (QMD)

### Implementation Checklist

For **every** `sessions_spawn` call with `input_paths`:

1. **Import compressor** (once at top):
   ```python
   import sys
   sys.path.insert(0, '/Users/charlie/.openclaw/workspace/kanban-ops')
   from input_compressor import compress_task_inputs, build_task_message_with_compressed_inputs
   ```

2. **Compress inputs** (before building message):
   ```python
   compressed_inputs = compress_task_inputs(task_data)
   # V2 prints: "📦 Compressing 2 input files..."
   #          "  ⚡ file1.md: 15KB → 2KB (basic, 節省 88.2%)"
   #          "  🧠 file2.md: 74KB → 2KB (qmd_semantic, 節省 97.4%)"
   #          "✅ Total: 90KB → 4KB (節省 94.8%)"
   ```

3. **Build message** (with compressed content):
   ```python
   task_message = build_task_message_with_compressed_inputs(task_data, compressed_inputs)
   ```

4. **Call sessions_spawn** (with compressed message):
   ```python
   sessions_spawn({
     "task": task_message,  // Already compressed
     "agentId": "analyst",
     "label": task_id,
     "model": "zai/glm-4.7"
   })
   ```

### Quick Reference

**No compression needed:**
- `research` tasks (no input files)
- `automation` tasks (usually no input files)

**Compression MANDATORY:**
- `analyst` tasks (1-2 input files average)
- `creative` tasks (2 input files average)

**Verification:**
- Look for `📦 Compressing N input files...` in logs
- Check for `⚡` (basic) or `🧠` (semantic) icons per file
- Final summary: `✅ Total: XKB → YKB (節省 Z%)`

### Files Involved

- `/Users/charlie/.openclaw/workspace/kanban-ops/input_extractor.py` - Basic extraction logic
- `/Users/charlie/.openclaw/workspace/kanban-ops/qmd_enhanced_compressor.py` - QMD semantic search
- `/Users/charlie/.openclaw/workspace/kanban-ops/input_compressor.py` - Main compressor (V2)
- `/Users/charlie/.openclaw/workspace/kanban-ops/input_compressor_old.py` - V1 backup
- `/Users/charlie/.openclaw/workspace/skills/spawn-protocol/SKILL.md` - This file

---

**Remember:** Input compression is not optional. It's part of the standard spawn protocol for all tasks with input files. V2 provides better compression automatically with no API changes.

