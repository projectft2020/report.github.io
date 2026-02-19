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
6. **Build the task message** using the template for the chosen agent
7. **Call sessions_spawn** with the full message

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
- Task message template:
```
TASK: [What to analyze — specific framework if needed]

CONTEXT:
- [Analysis angle]

INPUT FILES:
- /Users/charlie/.openclaw/workspace/kanban/projects/[project-id]/[upstream-task-id]-research.md

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
- Task message template:
```
TASK: [What to create — type, audience, format]

CONTEXT:
- Audience: [who will read this]
- Tone: [professional / technical / casual]

INPUT FILES:
- /Users/charlie/.openclaw/workspace/kanban/projects/[project-id]/[task-id]-research.md
- /Users/charlie/.openclaw/workspace/kanban/projects/[project-id]/[task-id]-analysis.md

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

```
// research / automation — no model field
sessions_spawn({
  "task": "[full task message above]",
  "agentId": "research",
  "label": "[task-id]"
})

// analyst / creative — must include model
sessions_spawn({
  "task": "[full task message above]",
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

