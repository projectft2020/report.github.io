# KANBAN.md - Task Management System v2

> Orchestrator's task queue and project management system.

---

## Directory Structure

```
kanban/
├── tasks.json                          # Master task list (all active projects)
├── projects/                           # Project workspaces
│   └── [project-id]/
│       ├── meta.json                   # Project overview & DAG
│       └── [task-id]-[agent].md        # Agent output files
└── archive/                            # Completed projects (30-day retention)
    └── YYYY-MM/
        └── [project-id]/
```

---

## Task Schema (tasks.json)

```json
[
  {
    "id": "20260218-143052-r001",
    "project_id": "ai-stock-report-20260218",
    "title": "Research AI stock market",
    "status": "pending | in_progress | completed | failed",
    "agent": "research | analyst | creative | automation",
    "priority": "high | normal | low",
    "input_paths": [],
    "output_path": "kanban/projects/ai-stock-report-20260218/r001-research.md",
    "depends_on": [],
    "next_tasks": ["20260218-143200-a001"],
    "created_at": "2026-02-18T14:30:52Z",
    "updated_at": "2026-02-18T14:30:52Z",
    "completed_at": null,
    "notes": ""
  }
]
```

### Field Reference

| Field | Purpose |
|-------|---------|
| `input_paths` | Files THIS agent must read as input (outputs from upstream tasks) |
| `output_path` | Where THIS agent writes its result |
| `depends_on` | Task IDs that must be `completed` before this can start |
| `next_tasks` | Task IDs to check/trigger when this task completes |

---

## Project Meta (projects/[id]/meta.json)

```json
{
  "id": "ai-stock-report-20260218",
  "title": "AI Stock Daily Report",
  "description": "Research → Analyze → Write report",
  "status": "in_progress",
  "created_at": "2026-02-18T14:30:00Z",
  "tasks": ["20260218-143052-r001", "20260218-143200-a001", "20260218-143300-c001"],
  "dag": {
    "r001": ["a001"],
    "a001": ["c001"],
    "c001": []
  }
}
```

---

## Task Handoff Protocol

### How agents pass work to each other

Data flows through **files** — each agent reads its `input_paths`, writes to its `output_path`.

```
[Research Task r001]
  input_paths: []                          ← no inputs needed
  output_path: projects/X/r001-research.md ← writes findings here

        ↓ completes → triggers a001

[Analyst Task a001]
  input_paths: ["projects/X/r001-research.md"]  ← reads research output
  output_path: projects/X/a001-analysis.md       ← writes analysis here

        ↓ completes → triggers c001

[Creative Task c001]
  input_paths: [
    "projects/X/r001-research.md",   ← reads research
    "projects/X/a001-analysis.md"    ← reads analysis
  ]
  output_path: projects/X/c001-report.md  ← writes final report
```

### Orchestrator dispatch logic

After any task completes:
```
1. Update task status → "completed", set completed_at
2. Read task.next_tasks
3. For each next task:
   a. Check ALL its depends_on are "completed"
   b. If yes → spawn that agent with its input_paths as context
   c. If no → leave as "pending" (waiting for other dependencies)
```

### How to build the spawn message for a downstream task

```
TASK: [task.title]

CONTEXT:
[Read each file in task.input_paths and include relevant content]

REQUIREMENTS:
[task-specific requirements]

INPUT FILES:
- [input_path_1]: [brief description of what's in it]
- [input_path_2]: [brief description]

OUTPUT PATH: [task.output_path]
```

---

## Kanban Query Responses

When user asks about task status, format response as:

### "待辦項目" / "todo"
```
📋 待辦項目 (N 個)

1. [task title] — [agent] | priority: [p]
2. ...
```

### "工作看板" / "kanban" / "任務狀態"
```
🗂 工作看板

🔵 進行中 (N)
  • [project] → [task title] — [agent] ⏱ 進行中...

⏳ 待辦 (N)
  • [task title] — [agent] (waiting for: [depends_on titles])
  • [task title] — [agent] (ready to start)

✅ 今日完成 (N)
  • [task title] — [agent] [completed_at]

❌ 失敗 (N)
  • [task title] — [agent] | [notes]
```

### "專案狀態" / "project status"
```
📁 專案總覽

[project title] — [status]
  任務: A✅ → B🔵 → C⏳
  進度: 2/4 完成
```

### "清理看板" / "archive"
Archive all fully-completed projects to `kanban/archive/`.

---

## Workflow Templates

Common pipelines. Reference when planning multi-step work:

### Research → Report
```json
[
  {"id": "r001", "agent": "research", "depends_on": [], "next_tasks": ["c001"]},
  {"id": "c001", "agent": "creative", "input_paths": ["r001 output"], "depends_on": ["r001"], "next_tasks": []}
]
```

### Research → Analysis → Report
```json
[
  {"id": "r001", "agent": "research",  "depends_on": [], "next_tasks": ["a001"]},
  {"id": "a001", "agent": "analyst",   "input_paths": ["r001 output"], "depends_on": ["r001"], "next_tasks": ["c001"]},
  {"id": "c001", "agent": "creative",  "input_paths": ["r001", "a001 outputs"], "depends_on": ["a001"], "next_tasks": []}
]
```

### Backtest → Chart + Report (parallel)
```json
[
  {"id": "bt001", "agent": "automation", "depends_on": [], "next_tasks": ["ch001", "rp001"]},
  {"id": "ch001", "agent": "creative",   "input_paths": ["bt001 output"], "depends_on": ["bt001"], "next_tasks": ["rp001"]},
  {"id": "rp001", "agent": "creative",   "input_paths": ["bt001", "ch001 outputs"], "depends_on": ["bt001", "ch001"], "next_tasks": []}
]
```

### Parallel Research → Merge Analysis
```json
[
  {"id": "rA",    "agent": "research", "depends_on": [], "next_tasks": ["a001"]},
  {"id": "rB",    "agent": "research", "depends_on": [], "next_tasks": ["a001"]},
  {"id": "a001",  "agent": "analyst",  "input_paths": ["rA", "rB outputs"], "depends_on": ["rA", "rB"], "next_tasks": []}
]
```

---

## Storage Policy

### Size targets
- Active kanban (`projects/`): **≤ 200MB** — warn if exceeded
- Individual task output: **≤ 2MB** recommended (summarize if larger)
- Archive: **30 days** retention, then auto-delete

### Archive trigger
When ALL tasks in a project are `completed` or `failed`:
```
move: kanban/projects/[id]/ → kanban/archive/YYYY-MM/[id]/
update: tasks.json → remove project's tasks
update: meta.json status → "archived"
```

### Manual cleanup
```
exec({"command": "du -sh /Users/charlie/.openclaw/workspace/kanban"})
exec({"command": "find /Users/charlie/.openclaw/workspace/kanban/archive -mtime +30 -name '*.md' -delete"})
```

### Large output handling
If a task output exceeds 1MB:
1. Write full content to the file as normal
2. Also create a `[task-id]-summary.md` with a ≤200-line summary
3. Downstream tasks use the summary version in `input_paths`

---

## Task ID Convention

Format: `YYYYMMDD-HHMMSS-[agent][seq]`

Examples:
- `20260218-143052-r001` (research, first)
- `20260218-143200-a001` (analyst, first)
- `20260218-150000-c001` (creative, first)
- `20260218-143052-r002` (research, second — parallel research)

---

**Version:** 2.0
**Updated:** 2026-02-18
