---
name: priority-rule-engine
description: Dynamic task priority adjustment based on configurable rules. Use when task priorities need automatic updates, when pending tasks need prioritization, or when implementing priority rules. Automatically reads rule configuration, evaluates pending tasks against rules, and updates priorities accordingly.
---

# Priority Rule Engine

## Overview

Automatically adjusts task priorities based on configurable rules. Enables dynamic prioritization of pending tasks based on age, user preferences, research quality, and custom criteria.

## Core Capabilities

### 1. Apply Priority Rules

Apply priority rules to all pending tasks:

```bash
python3 scripts/apply_rules.py
```

**Parameters:**
- `--rules <path>`: Path to rules configuration file (default: references/priority_rules.json)
- `--dry-run`: Preview changes without executing
- `--verbose`: Show detailed rule evaluation

**Output:** Count of updated tasks and priority changes

### 2. Validate Rules Configuration

Check rules configuration for errors:

```bash
python3 scripts/validate_rules.py
```

**Output:** Validation report with rule syntax errors and warnings

### 3. Generate Priority Report

Display current priority distribution:

```bash
python3 scripts/priority_report.py
```

**Output:** Summary of task priorities and recommendations

## Priority Rules

Rule configuration is stored in `references/priority_rules.json`.

### Rule Format

Each rule has:
- `name`: Rule identifier
- `description`: What the rule does
- `condition`: When rule applies (task properties)
- `action`: What to do when rule matches
- `priority`: Target priority value

### Built-in Rules

#### Rule 1: Age-based Promotion

Promote old tasks that have been pending too long:

```json
{
  "name": "age_based_promotion",
  "description": "Promote tasks pending > 7 days to medium",
  "condition": {
    "status": "pending",
    "days_pending": "> 7",
    "current_priority": ["normal", "low"]
  },
  "action": "set_priority",
  "priority": "medium"
}
```

#### Rule 2: User Request Promotion

Promote tasks explicitly marked as needed by user:

```json
{
  "name": "user_request_promotion",
  "description": "Promote tasks with 'user_needed' tag to high",
  "condition": {
    "status": "pending",
    "tags": ["user_needed"]
  },
  "action": "set_priority",
  "priority": "high"
}
```

#### Rule 3: Quality-based Promotion

Promote tasks related to high-quality completed research:

```json
{
  "name": "quality_based_promotion",
  "description": "Promote tasks related to research with score >= 8.0",
  "condition": {
    "status": "pending",
    "related_score": ">= 8.0"
  },
  "action": "set_priority",
  "priority": "high"
}
```

#### Rule 4: Keyword-based Promotion

Promote tasks containing specific keywords:

```json
{
  "name": "keyword_based_promotion",
  "description": "Promote tasks with 'ML', 'AI', or 'trading' keywords to medium",
  "condition": {
    "status": "pending",
    "keywords": ["ML", "AI", "trading"],
    "current_priority": ["normal", "low"]
  },
  "action": "set_priority",
  "priority": "medium"
}
```

## Rule Evaluation Order

Rules are evaluated in the order they appear in the configuration file. The first matching rule is applied. Stop rule evaluation after first match.

## Configuration

### Priority Values

- `high`: Highest priority, execute first
- `medium`: Medium priority
- `normal`: Normal priority (default)
- `low`: Lowest priority

### Condition Operators

- `days_pending`: `> 7`, `< 3`, `>= 14`
- `current_priority`: `["normal", "low"]`
- `tags`: `["user_needed"]`
- `keywords`: `["ML", "AI"]`
- `related_score`: `>= 8.0`, `< 6.0`

## Workflow

### Setup and Apply Rules

1. **Create/Edit rules:** Edit `references/priority_rules.json`
2. **Validate rules:** Run `python3 scripts/validate_rules.py`
3. **Apply rules:** Run `python3 scripts/apply_rules.py`
4. **Review changes:** Check logs and priority report

### Integration with Auto-Spawn

Add to `kanban-ops/auto_spawn_heartbeat.py`:

```python
from skills.priority_rule_engine import apply_priority_rules

# Apply priority rules before spawning
updated_count = apply_priority_rules(
    rules_file="references/priority_rules.json"
)

if updated_count > 0:
    print(f"Updated {updated_count} task priorities")
```

### Periodic Application

Run priority rule engine periodically:

```bash
# Every heartbeat or hourly
python3 scripts/apply_rules.py --verbose

# Generate priority report
python3 scripts/priority_report.py
```

## Scripts Reference

### scripts/apply_rules.py

Apply priority rules to pending tasks.

**Parameters:** `--rules`, `--dry-run`, `--verbose`

**Returns:** Count of updated tasks

### scripts/validate_rules.py

Validate rules configuration syntax and logic.

**Returns:** Validation report

### scripts/priority_report.py

Generate priority distribution report.

**Returns:** Formatted report with statistics

## References

### references/priority_rules.json

Default rule configuration file.

**Contains:** Array of rule objects with condition, action, and priority

### references/rule_examples.md

Additional rule examples and patterns.

**Contains:** Complex rule scenarios and best practices

## Best Practices

1. **Rule ordering matters:** Put more specific rules first
2. **Test with dry-run:** Preview changes before applying
3. **Monitor impact:** Track how rules affect task execution order
4. **Keep rules simple:** Avoid complex nested conditions
5. **Log changes:** Review priority updates regularly
6. **Adjust based on results:** Refine rules based on execution patterns

## Troubleshooting

### Rules Not Applying

**Symptom:** No tasks updated despite matching conditions

**Solution:**
- Verify rule syntax with validate_rules.py
- Check condition operators and values
- Ensure task properties match conditions
- Use --verbose to see rule evaluation

### Conflicting Rules

**Symptom:** Multiple rules match same task

**Solution:**
- Reorder rules (first match wins)
- Add exclusion conditions
- Combine rules into single rule

### Too Many Updates

**Symptom:** Most tasks change priority every run

**Solution:**
- Add conditions to prevent re-evaluation
- Use stable priority values
- Review rule necessity

## Integration Example

Complete heartbeat integration:

```python
from skills.priority_rule_engine import (
    apply_priority_rules,
    validate_rules,
    generate_priority_report
)

def heartbeat_priority_update():
    # 1. Validate rules
    if not validate_rules():
        print("Rules validation failed, skipping update")
        return 0

    # 2. Apply rules with preview
    updated = apply_priority_rules(dry_run=True)
    if updated > 0:
        print(f"Preview: {updated} tasks would be updated")
        # Option: require confirmation

    # 3. Apply rules
    updated = apply_priority_rules(dry_run=False)

    # 4. Generate report
    if updated > 0:
        report = generate_priority_report()
        print(report)

    return updated
```
