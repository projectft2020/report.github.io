---
name: task-state-enhancer
description: Enhanced task state analysis and reporting. Use when detailed task status reports are needed, when analyzing task distribution, or when identifying abnormal tasks. Scans tasks.json, generates detailed statistics, and highlights anomalies.
---

# Task State Enhancer

## Overview

Provides enhanced task state analysis and reporting. Generates detailed task distribution reports, identifies anomalies, and provides actionable insights.

## Core Capabilities

### 1. Generate State Report

Comprehensive task state analysis:

```bash
python3 scripts/state_report.py
```

**Output:**
- Task status distribution (pending, in_progress, completed, failed)
- Priority distribution for pending tasks
- Task age distribution
- Recent activity summary
- Anomaly detection

### 2. Identify Abnormal Tasks

Detect tasks with unusual characteristics:

```bash
python3 scripts/identify_anomalies.py
```

**Detects:**
- Tasks stuck in spawning state
- Tasks with missing timestamps
- Tasks with invalid priorities
- Tasks with abnormal metadata
- Orphaned tasks (no output files)

### 3. Task Distribution Analysis

Analyze task distribution across categories:

```bash
python3 scripts/distribution_analysis.py
```

**Parameters:**
- `--by priority`: Group by priority
- `--by status`: Group by status
- `--by agent`: Group by agent type
- `--by age`: Group by age buckets

**Output:** Detailed distribution statistics

## Report Features

### Status Distribution

Breakdown of tasks by status:
- Pending: Ready to execute
- In Progress: Currently executing
- Completed: Successfully finished
- Failed: Failed execution

### Priority Analysis

For pending tasks:
- High priority count and percentage
- Medium priority count and percentage
- Normal priority count and percentage
- Low priority count and percentage

### Age Distribution

How long tasks have been pending:
- Less than 1 day
- 1-3 days
- 3-7 days
- 7-14 days
- More than 14 days

### Anomaly Detection

Identifies tasks requiring attention:
- Stuck spawning tasks (> 2 hours)
- Missing timestamps
- Invalid priorities
- Incomplete metadata
- Orphaned tasks

### Recent Activity

- Tasks completed in last 24 hours
- Tasks started in last 24 hours
- Tasks failed in last 24 hours

## Configuration

No configuration required. Scripts auto-detect:

- Tasks file location (`kanban/tasks.json`)
- Research output directory (`kanban/projects/`)
- Current time and timezone

## Integration

### Enhance Task Sync

Add to `kanban-ops/task_sync.py`:

```python
from skills.task_state_enhancer import generate_state_report

# After normal sync, generate enhanced report
report = generate_state_report()
print(report)
```

### Heartbeat Integration

Add to heartbeat workflow:

```python
from skills.task_state_enhancer import (
    generate_state_report,
    identify_anomalies
)

def enhanced_heartbeat():
    # 1. Generate state report
    report = generate_state_report()

    # 2. Identify anomalies
    anomalies = identify_anomalies()

    if anomalies:
        print("⚠️  發現異常任務:")
        for anomaly in anomalies:
            print(f"  - {anomaly}")

    return report, anomalies
```

## Scripts Reference

### scripts/state_report.py

Generate comprehensive task state report.

**Output:** Formatted report with all metrics

### scripts/identify_anomalies.py

Detect abnormal tasks requiring attention.

**Returns:** List of anomaly objects with details

### scripts/distribution_analysis.py

Analyze task distribution by various dimensions.

**Parameters:** `--by priority`, `--by status`, `--by agent`, `--by age`

**Returns:** Distribution statistics

## Anomaly Types

### Spuck Tasks

Tasks stuck in spawning or in_progress state beyond timeout thresholds.

**Action Required:** Manual review or auto-rollback

### Missing Metadata

Tasks with incomplete or missing required fields.

**Action Required:** Complete task metadata

### Invalid Priorities

Tasks with priority values not in [high, medium, normal, low].

**Action Required:** Correct priority values

### Orphaned Tasks

Tasks marked completed but missing output files.

**Action Required:** Investigate and regenerate output

## Best Practices

1. **Run regularly:** Generate reports during each heartbeat
2. **Review anomalies:** Address detected anomalies promptly
3. **Monitor trends:** Watch for patterns in state changes
4. **Archive old data:** Periodically archive completed tasks
5. **Clean up metadata:** Remove tasks with missing critical information

## Troubleshooting

### Report Incomplete

**Symptom:** Some sections show "N/A" or missing data

**Solution:**
- Verify tasks.json is complete
- Check task metadata fields
- Ensure timestamps are valid

### Anomaly False Positives

**Symptom:** Normal tasks flagged as anomalies

**Solution:**
- Adjust anomaly thresholds
- Review anomaly detection logic
- Consider task context before action

### Distribution Imbalance

**Symptom:** Heavily skewed distribution (e.g., 90% high priority)

**Solution:**
- Review priority rules
- Check if rules are over-elevating
- Evaluate task priorities manually
