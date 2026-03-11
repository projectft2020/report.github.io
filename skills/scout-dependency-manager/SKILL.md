---
name: scout-dependency-manager
description: Manage Scout Agent dependencies and health. Use when Scout Agent is unavailable, has missing dependencies, or requires health checks. Automatically checks for pybloom_live, installs missing packages, and verifies Scout connectivity.
---

# Scout Dependency Manager

## Overview

Automates Scout Agent dependency management and health monitoring. Ensures Scout Agent is always ready for topic discovery by checking required packages, installing missing dependencies, and validating connectivity.

## Core Capabilities

### 1. Check Dependencies

Check if required Scout Agent dependencies are installed:

- `pybloom_live` - Required for Scout Agent bloom filter expansion
- Other Scout-specific packages

**Usage:**
```bash
python3 scripts/check_dependencies.py
```

**Output:** List of missing and installed dependencies

### 2. Install Dependencies

Automatically install missing Scout Agent dependencies:

```bash
python3 scripts/install_dependencies.py
```

**Behavior:**
- Detects missing packages
- Runs `pip install` for each missing package
- Verifies installation success
- Reports installation results

### 3. Scout Health Check

Verify Scout Agent connectivity and configuration:

```bash
python3 scripts/health_check.py
```

**Checks:**
- Scout Agent connectivity to workspace
- Required package availability
- Configuration file validity
- Scan capability status

**Output:** Health status report with recommendations

### 4. Manual Scan Trigger

Trigger Scout Agent scan manually:

```bash
python3 scripts/trigger_scan.py
```

**Parameters:**
- `--force`: Force scan regardless of pending task count
- `--quiet`: Suppress verbose output

**Output:** Scan initiation confirmation

### 5. Scout Statistics

Display Scout Agent statistics and recent activity:

```bash
python3 scripts/stats.py
```

**Displays:**
- Total tasks in Kanban
- Pending task count
- Last scan timestamp
- Feedback statistics
- Recommendation quality metrics

## Workflow

### Initial Setup (First Time)

1. Run dependency check: `python3 scripts/check_dependencies.py`
2. Install missing dependencies: `python3 scripts/install_dependencies.py`
3. Verify health: `python3 scripts/health_check.py`

### Ongoing Maintenance

- **Before Scout operations:** Run health check
- **When Scout is disabled:** Check dependencies and install
- **Manual scan needed:** Use trigger_scan.py
- **Monitoring:** Use stats.py to check Scout activity

## Integration with Core System

### Auto-Integration with Heartbeat

This skill can be integrated into `kanban-ops/monitor_and_refill.py`:

```python
from skills.scout_dependency_manager import check_scout_health, install_missing

# In monitor_and_refill.py
if not check_scout_health():
    install_missing()
    # Then proceed with Scout operations
```

### Auto-Dependency Check on Start

Add to system startup or heartbeat:

```python
from skills.scout_dependency_manager import check_and_install_dependencies

# Check and install missing dependencies
check_and_install_dependencies()
```

## Troubleshooting

### Scout Agent Disabled

**Symptom:** "Scout Agent not available, expansion disabled" in logs

**Solution:**
1. Run `python3 scripts/check_dependencies.py`
2. Run `python3 scripts/install_dependencies.py`
3. Run `python3 scripts/health_check.py`

### Installation Fails

**Symptom:** pip install errors

**Solution:**
- Check Python version compatibility
- Verify pip is updated: `pip install --upgrade pip`
- Try virtual environment installation

### Connectivity Issues

**Symptom:** Health check fails connectivity

**Solution:**
- Verify workspace-scout directory exists
- Check Scout Agent configuration files
- Ensure proper file permissions

## Scripts Reference

### scripts/check_dependencies.py

Checks for required Scout Agent packages.

**Returns:** Dictionary with `installed` and `missing` lists

### scripts/install_dependencies.py

Installs missing Scout Agent dependencies.

**Returns:** Installation results and status

### scripts/health_check.py

Comprehensive Scout Agent health verification.

**Returns:** Health status object with detailed checks

### scripts/trigger_scan.py

Manual Scout scan initiation.

**Parameters:** `--force`, `--quiet`

**Returns:** Scan initiation confirmation

### scripts/stats.py

Display Scout Agent statistics.

**Returns:** Formatted statistics output

## Configuration

No configuration required. Scripts auto-detect:

- Scout Agent workspace location
- Python environment
- Package installation path
