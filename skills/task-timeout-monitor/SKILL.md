---
name: task-timeout-monitor
description: Monitor task timeouts and automatically rollback stuck tasks. Use when tasks remain in spawning or in_progress state for too long, or when task state monitoring is needed. Automatically detects timeout conditions, generates alerts, and can rollback stuck tasks.
---

# Task Timeout Monitor

## Overview

Automatically monitors task execution times and handles timeout conditions. Prevents tasks from getting permanently stuck in spawning or in_progress states.

## Core Capabilities

### 1. Check Task Timeouts

Scan tasks.json for tasks that have exceeded timeout thresholds:

```bash
python3 scripts/check_timeouts.py
```

**Parameters:**
- `--hours <N>`: Timeout threshold in hours (default: 24)
- `--status <status>`: Filter by status (spawning, in_progress, or all)

**Output:** List of tasks with timeout status and duration

### 2. Auto-Rollback Stuck Tasks

Automatically rollback tasks stuck in spawning state:

```bash
python3 scripts/rollback_stuck.py
```

**Parameters:**
- `--hours <N>`: Timeout threshold in hours (default: 2 for spawning)
- `--dry-run`: Preview changes without executing

**Behavior:**
- Detects tasks stuck in spawning state
- Rolls back to pending status
- Adds timeout notes
- Logs rollback actions

### 3. Timeout Alert Generator

Generate timeout alerts for monitoring:

```bash
python3 scripts/generate_alert.py
```

**Parameters:**
- `--threshold <N>`: Alert threshold in hours (default: 12)

**Output:** Formatted alert message with:
- Number of timeout tasks
- Task IDs and descriptions
- Time exceeded duration
- Recommended actions

## Workflow

### Regular Monitoring

Run timeout checks during heartbeat or periodic monitoring:

```bash
# Check for timeouts (24 hour threshold)
python3 scripts/check_timeouts.py --hours 24

# Auto-rollback spawning tasks (2 hour threshold)
python3 scripts/rollback_stuck.py --hours 2
```

### Integration with Heartbeat

Add to heartbeat workflow in `kanban-ops/auto_spawn_heartbeat.py`:

```python
from skills.task_timeout_monitor import check_timeouts, rollback_stuck

# Check for long-running tasks
timeout_tasks = check_timeouts(hours=24, status="in_progress")
if timeout_tasks:
    generate_alert(timeout_tasks)

# Auto-rollback stuck spawning tasks
stuck_count = rollback_stuck(hours=2, dry_run=False)
if stuck_count > 0:
    print(f"Auto-rolled back {stuck_count} stuck tasks")
```

## Timeout Thresholds

### Recommended Defaults

- **Spawning tasks:** 2 hours
  - Spawning should complete within minutes
  - 2 hours provides buffer for API delays

- **In-progress tasks:** 24 hours
  - Research tasks typically complete within 1-2 hours
  - 24 hours accommodates complex tasks

- **Customize based on task type:**
  - Research: 24 hours
  - Development: 48 hours
  - Testing: 12 hours

## Configuration

No configuration required. Scripts auto-detect:

- Tasks file location (`kanban/tasks.json`)
- Current time and timezone
- Task states and timestamps

## Troubleshooting

### Tasks Not Timing Out

**Symptom:** Tasks remain in spawning/in_progress but no timeout detected

**Solution:**
- Verify task timestamps are timezone-aware
- Check threshold values with `--hours` parameter
- Ensure tasks.json timestamps are updated correctly

### Rollback Too Aggressive

**Symptom:** Valid tasks being rolled back

**Solution:**
- Increase threshold with `--hours` parameter
- Use `--dry-run` to preview before execution
- Adjust default thresholds in scripts

### Alert Not Generated

**Symptom:** No alerts despite timeouts

**Solution:**
- Check alert threshold with `--threshold` parameter
- Verify task status matches filter
- Ensure alert generation script is called

## Scripts Reference

### scripts/check_timeouts.py

Check for task timeouts.

**Parameters:** `--hours`, `--status`

**Returns:** List of timeout tasks with details

### scripts/rollback_stuck.py

Auto-rollback stuck spawning tasks.

**Parameters:** `--hours`, `--dry-run`

**Returns:** Count of rolled back tasks

### scripts/generate_alert.py

Generate formatted timeout alerts.

**Parameters:** `--threshold`

**Returns:** Alert message string

## Integration Example

Complete heartbeat integration:

```python
from skills.task_timeout_monitor import (
    check_timeouts,
    rollback_stuck,
    generate_alert
)

def heartbeat_monitor():
    # 1. Check spawning timeouts (2 hours)
    stuck = rollback_stuck(hours=2, dry_run=False)

    # 2. Check in-progress timeouts (24 hours)
    timeouts = check_timeouts(hours=24, status="in_progress")

    # 3. Generate alerts if needed
    if timeouts:
        alert = generate_alert(timeout_tasks=timeouts, threshold=12)
        print(alert)
        # Optionally send alert to notification system

    return {
        "stuck_rolled_back": stuck,
        "timeouts_detected": len(timeouts)
    }
```

## Best Practices

1. **Use conservative thresholds:** Start with 24 hours, adjust based on task patterns
2. **Dry-run first:** Use `--dry-run` to preview rollback actions
3. **Log all actions:** Keep records of timeouts and rollbacks
4. **Monitor alert frequency:** If alerts are too frequent, adjust thresholds
5. **Review timeout causes:** Identify why tasks timeout and address root causes
