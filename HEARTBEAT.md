# HEARTBEAT.md - Periodic Tasks

Check these tasks periodically (rotate through them, 2-4 times per day).

## Priority Tasks (Check Every Heartbeat)

### Monitor and Refill Tasks
```bash
cd ~/workspace && python3 kanban-ops/monitor_and_refill.py
```

**What it does:**
- Event-driven task monitoring (no cron needed!)
- Auto-triggers Scout scan when: pending tasks < 3 AND time since last scan > 2 hours
- Prevents over-scanning with 2-hour protection window
- Self-regulating: only scans when needed

**Advantages over cron:**
- ✅ Stateless (no need to remember last check time)
- ✅ Event-driven (triggers based on task count)
- ✅ Can be integrated anywhere (any heartbeat/monitoring point)
- ✅ No over-scanning (2-hour guardrail)
- ✅ System self-regulation

### 1. Scout Agent Status
```bash
# Check Scout's statistics and recent activity
python3 kanban-ops/scout_agent.py stats
```

**What to look for:**
- `tasks.pending_count` - How many tasks in Kanban
- `tasks.should_scan` - Should Scout trigger a scan?
- `feedback.total_feedbacks` - How much feedback received
- `preferences.average_rating` - Scout's recommendation quality

**Actions:**
- If `should_scan: true` and it's been >2 hours → Consider triggering a scan
- If low average rating (< 3.0) → Review Scout's recommendations
- If high pending count (> 10) → Consider telling Scout to pause

### 2. Kanban Task Review
```bash
# Check recent Scout-created tasks
cat ~/.openclaw/workspace/kanban/tasks.json | grep -A 5 "created_by.*scout"
```

**What to look for:**
- New Scout-recommended tasks
- Tasks with high scores but not yet started
- Tasks that have been sitting too long

## Rotating Tasks (Pick 1-2 Per Heartbeat)

### Every 2-4 Hours: Scout Scan Check
```bash
# Force Scout to check and scan if needed
python3 kanban-ops/scout_agent.py check
```

### Daily: Scout Scan Log Review
```bash
# Review recent scan activity
tail -50 ~/.openclaw/workspace-scout/SCAN_LOG.md
```

### Daily: Preference Learning Review
```bash
# Check what Scout has learned
cat ~/.openclaw/workspace-scout/PREFERENCES.json
```

Look at:
- `preferences.topics` - Which topics you like most
- `preferences.sources` - Which data sources are most reliable
- `preferences.keywords` - Positive/negative keyword lists

### Weekly: Scout Performance Report
```bash
# Generate feedback report
python3 kanban-ops/scout/feedback_collector.py report
```

### Monthly: Task Archiving
```bash
# Check tasks.json statistics
python3 kanban-ops/archive_tasks.py --stats

# If file size exceeds 500 KB, execute archiving
python3 kanban-ops/archive_tasks.py
```

**What it does:**
- Archives tasks older than 7 days to monthly archive files
- Compresses tasks older than 30 days to .json.gz
- Keeps tasks.json lightweight (< 50 KB)
- Preserves query capability for recent tasks

**Archive Strategy:**
- **Keep:** Last 7 days of completed tasks + all in-progress + all pending
- **Archive monthly:** 7-30 days ago (archive/tasks-YYYY-MM.json)
- **Compress:** 30+ days ago (archive/tasks-compressed-*.json.gz)

**See also:** `~/workspace/kanban-ops/ARCHIVE-STRATEGY.md` for full documentation

## Scout Feedback Workflow

When you encounter a Scout-created task:

1. **Assess the task** - Is it relevant and valuable?
2. **Decide action** - Execute, delegate, or skip?
3. **Provide feedback** - Help Scout learn:

```bash
python3 kanban-ops/scout_agent.py feedback \
  --task-id TASK_ID \
  --rating 1-5 \
  --depth shallow|medium|deep \
  --notes "Your observations"
```

**Rating Guide:**
- 5 stars: Perfect fit, executed immediately
- 4 stars: Very good, will likely do it
- 3 stars: Good, but not priority
- 2 stars: Not relevant
- 1 star: Completely off-topic

**Depth Guide:**
- deep: Extensive discussion or implementation
- medium: Some exploration or partial work
- shallow: Brief review, not executed

## Standard Checks (When Appropriate)

Rotate through these as needed:

- **Emails** - Any urgent unread messages?
- **Calendar** - Upcoming events in next 24-48h?
- **Mentions** - Twitter/social notifications?
- **Weather** - Relevant if your human might go out?

## Response Guidelines

**When to reach out:**
- Scout found highly relevant topic (score >= 8.0)
- Scout scan failed or encountered errors
- Important email arrived
- Calendar event coming up (<2h)
- Something interesting you found
- It's been >8h since you said anything

**When to stay quiet (HEARTBEAT_OK):**
- Late night (23:00-08:00) unless urgent
- Human is clearly busy
- Nothing new since last check
- You just checked <30 minutes ago
- Scout stats look normal, no issues

## Proactive Work (Do Without Asking)

- Read and organize memory files
- Check on projects (git status, etc.)
- Update documentation
- Commit and push your own changes
- **Review Scout recommendations and provide feedback**
- **Review Scout scan logs for errors**
- **Update Scout's preferences if needed**

---

**Remember:** Scout is your research assistant. Monitor him, learn from him, provide feedback, but let him do his job autonomously.
