---
name: kanban-ops
description: Kanban operations. ALWAYS end every kanban board response with a stale-check summary line showing how many in_progress tasks were checked, auto-recovered, timed out, and normal.
user-invocable: false
---

# Kanban Operations

## CRITICAL: Stale Check on Every Board Response

**Every time you show the kanban board, you MUST:**
1. For each `in_progress` task: check if `now - updated_at > 10 minutes`
2. If stale: `exec({"command": "test -f [output_path] && echo EXISTS || echo MISSING"})`
   - EXISTS -> mark `completed`, note `"auto-recovered: announce lost"`
   - MISSING -> mark `failed`, note `"timeout: no output after [age]m"`
3. Write the updated tasks.json
4. End your response with this line (always, even when all zeros):

```
Stale check: [N] checked | recovered: [N] | failed: [N] | ok: [N]
```

This line is mandatory. If it is absent, the check did not run.

---

## Writing a Task Entry (before spawning)

Read tasks.json -> run stale check -> append new task -> write back.

```json
{
  "id": "YYYYMMDD-HHMMSS-r001",
  "project_id": "topic-slug-YYYYMMDD",
  "title": "What this task does",
  "status": "in_progress",
  "agent": "research | analyst | creative | automation",
  "priority": "high | normal | low",
  "input_paths": [],
  "output_path": "/Users/charlie/.openclaw/workspace/kanban/projects/[project-id]/[task-id]-[type].md",
  "depends_on": [],
  "next_tasks": [],
  "created_at": "ISO8601",
  "updated_at": "ISO8601",
  "completed_at": null,
  "notes": ""
}
```

---

## Updating Task Status (after announce)

```
1. read tasks.json + run stale check
2. find task by id
3. update status -> "completed" | "failed", set completed_at
4. write tasks.json
5. if next_tasks exist and all depends_on are completed -> spawn immediately
```

---

## Board Format (kanban / task status)

```
Work Board

[IN PROGRESS] (N)
  * [project] -> [title] - [agent] [age]m

[PENDING] (N)
  * [title] - [agent] waiting: [deps]
  * [title] - [agent] ready

[COMPLETED TODAY] (N)
  * [title] - [agent] [time]

[FAILED] (N)
  * [title] - [agent] | [notes]

---
Stale check: [N] checked | recovered: [N] | failed: [N] | ok: [N]
```

---

## Other Keywords

**todo / pending** -> list pending tasks only

**project status** -> per-project task DAG progress

**archive / cleanup** -> move completed projects to `kanban/archive/YYYY-MM/`; remove from tasks.json

**recover / fix kanban** -> run stale check on ALL in_progress tasks regardless of age

---

## Conventions

Task ID: `YYYYMMDD-HHMMSS-[r/a/c/t][seq]` (r=research, a=analyst, c=creative, t=automation)

Project ID: `topic-slug-YYYYMMDD`

