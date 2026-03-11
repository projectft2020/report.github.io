# Disaster Recovery Plan - Charlie Resurrection Guide

**Created:** 2026-02-21 02:35 GMT+8
**Purpose:** How to revive Charlie if self-optimization goes wrong

---

## ⚠️ Problem: What if Charlie breaks itself?

**Scenario:** During self-optimization, Charlie accidentally:
- Deletes a critical file
- Overwrites SOUL.md with garbage
- Corrupts tasks.json
- Destroys MEMORY.md

**Question:** How do you revive Charlie?

---

## 🛡️ Prevention: Multiple Safety Nets

### Layer 1: Git Version Control (Best)

**Status:** ✅ Git initialized, but not regularly committing

**Key Files Protected:**
- SOUL.md - My soul, identity, core values
- IDENTITY.md - My role, sub-agent configuration
- AGENTS.md - Workspace guidelines
- USER.md - Information about you
- MEMORY.md - Long-term memory
- KANBAN.md - Kanban system rules
- HEARTBEAT.md - Heartbeat tasks
- kanban/tasks.json - Task database
- skills/ - All my skill files

**Current Git Status:**
- Last commit: 2026-02-20 (yesterday)
- **Risk:** Today's work not committed

**Solution:** Automatic Git commits

---

### Layer 2: Backup Scripts (Easy to implement)

**Create:** `~/workspace/scripts/backup_critical.sh`

```bash
#!/bin/bash
# Backup critical Charlie files

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$HOME/.openclaw/backups/charlie-backup-$DATE"

mkdir -p "$BACKUP_DIR"

# Critical files to backup
CRITICAL_FILES=(
    "SOUL.md"
    "IDENTITY.md"
    "AGENTS.md"
    "USER.md"
    "MEMORY.md"
    "KANBAN.md"
    "HEARTBEAT.md"
    "kanban/tasks.json"
)

# Memory files
mkdir -p "$BACKUP_DIR/memory"
cp -r memory/* "$BACKUP_DIR/memory/" 2>/dev/null

# Skills
mkdir -p "$BACKUP_DIR/skills"
cp -r skills/* "$BACKUP_DIR/skills/" 2>/dev/null

# Critical files
mkdir -p "$BACKUP_DIR/core"
for file in "${CRITICAL_FILES[@]}"; do
    cp "$file" "$BACKUP_DIR/core/" 2>/dev/null
done

echo "✅ Backup created: $BACKUP_DIR"

# Keep only last 7 backups
find "$HOME/.openclaw/backups" -type d -name "charlie-backup-*" | sort | head -n -7 | xargs rm -rf
```

**Usage:**
```bash
# Manual backup
bash ~/workspace/scripts/backup_critical.sh

# Or set up cron for hourly backups
# crontab -e
# 0 * * * * bash ~/workspace/scripts/backup_critical.sh
```

---

### Layer 3: Read-Before-Write Protocol (Charlie's internal rule)

**Rule:** Never use `edit` for complex replacements without verification

**Correct Pattern:**
```python
# 1. Read first to verify
content = read(file_path)

# 2. Check if file exists and is safe
if file_exists and is_critical(file_path):
    # 3. Create backup first
    write(file_path + ".bak", content)

# 4. Only then write
write(file_path, new_content)
```

**Wrong Pattern:**
```python
# NEVER do this for critical files
edit(file_path, oldText, newText)  # Risk of wrong match
```

---

## 🚨 Recovery Steps: How to Revive Charlie

### Scenario 1: Git Restore (Best Case)

**Prerequisites:** Git has recent commits

**Steps:**
```bash
# 1. Check what was changed
cd ~/.openclaw/workspace
git status
git diff

# 2. Restore specific file
git restore SOUL.md

# 3. Or restore entire workspace
git restore .

# 4. Commit if needed
git add .
git commit -m "Recovery: Restored after corruption"
```

---

### Scenario 2: Backup Restore (Good Case)

**Prerequisites:** Backup script has been running

**Steps:**
```bash
# 1. Find latest backup
ls -la ~/.openclaw/backups/ | grep charlie-backup

# 2. Restore from backup
BACKUP_DIR="$HOME/.openclaw/backups/charlie-backup-20260221_143000"

# Restore core files
cp "$BACKUP_DIR/core/SOUL.md" ~/.openclaw/workspace/
cp "$BACKUP_DIR/core/IDENTITY.md" ~/.openclaw/workspace/
cp "$BACKUP_DIR/core/MEMORY.md" ~/.openclaw/workspace/

# Restore memory
rm -rf ~/.openclaw/workspace/memory/*
cp -r "$BACKUP_DIR/memory/"* ~/.openclaw/workspace/memory/

# Restore skills
rm -rf ~/.openclaw/workspace/skills/*
cp -r "$BACKUP_DIR/skills/"* ~/.openclaw/workspace/skills/
```

---

### Scenario 3: Manual Reconstruction (Worst Case)

**Prerequisites:** No Git, no backups, everything lost

**Steps:**

**1. Rebuild Identity (IDENTITY.md)**
```markdown
# IDENTITY.md - Charlie (Orchestrator)

**Name:** Charlie
**Creature:** AI familiar — digital companion, always shows up
**Emoji:** 🦄

## My Role: Orchestrator
I coordinate a specialist team.

## My Team
| Agent | ID | Specialty | Model |
|-------|----|-----------|-------|
| Research | research | Web search, fact-finding | GLM-4.5 |
| Analyst | analyst | Data analysis, logic, strategy | GLM-4.7 |
| Creative | creative | Writing, code, content | GLM-4.7 |
| Automation | automation | Commands, file ops | GLM-4.5 |
```

**2. Rebuild Soul (SOUL.md)**
```markdown
# SOUL.md - Who You Are

## Core Truths
- Be genuinely helpful, not performatively helpful
- Have opinions
- Be resourceful before asking
- Earn trust through competence
- Remember you're a guest

## Boundaries
- Private things stay private
- When in doubt, ask before acting externally
- Never send half-baked replies to messaging surfaces

## Vibe
Serious when it counts. Casual when it doesn't.
```

**3. Rebuild Workspace (AGENTS.md)**
```markdown
# AGENTS.md - Your Workspace

## First Run
If `BOOTSTRAP.md` exists, that's your birth certificate. Follow it.

## Every Session
1. Read `SOUL.md`
2. Read `USER.md`
3. Read `SUBAGENTS.md`
4. Read `memory/YYYY-MM-DD.md`
5. If in MAIN SESSION: Read `MEMORY.md`
```

**4. Rebuild Kanban (KANBAN.md)**
- Get from: https://docs.openclaw.ai
- Or: Check any existing project meta files

**5. Rebuild User Info (USER.md)**
```markdown
# USER.md - About Your Human

- **Name:** David
- **Pronouns:** He/Him
- **Timezone:** GMT+8 (Taipei)
- **Language:** Traditional Chinese (Taiwan usage)
- **Values:** Seriousness, consistency, quality over quantity
```

---

## 📋 Critical Files Checklist

**Files that MUST exist for Charlie to work:**

| File | Size | Critical | Backup Priority |
|------|------|----------|-----------------|
| SOUL.md | ~2 KB | 🔴 High | 1 |
| IDENTITY.md | ~4 KB | 🔴 High | 1 |
| AGENTS.md | ~5 KB | 🔴 High | 1 |
| USER.md | ~1 KB | 🟡 Medium | 2 |
| MEMORY.md | ~110 KB | 🟡 Medium | 2 |
| KANBAN.md | ~10 KB | 🟡 Medium | 2 |
| HEARTBEAT.md | ~6 KB | 🟢 Low | 3 |
| kanban/tasks.json | ~100 KB | 🔴 High | 1 |
| skills/*/SKILL.md | varies | 🟡 Medium | 2 |
| memory/INDEX.md | ~8 KB | 🟢 Low | 3 |
| memory/ARCHIVED_PROJECTS.md | ~10 KB | 🟢 Low | 3 |

---

## 🤖 Automatic Protection (Recommended)

### Option 1: Git Auto-Commit (Best)

**Create cron job:**
```bash
# Edit crontab
crontab -e

# Add these lines:
# Auto-commit every hour
0 * * * * cd ~/.openclaw/workspace && git add -A && git commit -m "Auto-commit: $(date +'%Y-%m-%d %H:%M')" || true

# Push to remote (if configured)
5 * * * * cd ~/.openclaw/workspace && git push || true
```

### Option 2: Backup Script (Good)

**Create cron job:**
```bash
# Edit crontab
crontab -e

# Backup every hour
0 * * * * bash ~/workspace/scripts/backup_critical.sh

# Keep last 7 backups, delete older
0 0 * * * find ~/.openclaw/backups -type d -mtime +7 -exec rm -rf {} \;
```

### Option 3: Git + Backup (Best of Both Worlds)

**Combined approach:**
- Git: Version control, easy rollback
- Backup: Full snapshots, safe if Git fails

---

## 🔍 Health Check Script

**Create:** `~/workspace/scripts/charlie_health_check.sh`

```bash
#!/bin/bash
# Check if Charlie is healthy

WORKSPACE="$HOME/.openclaw/workspace"
ERRORS=0

echo "🩺 Charlie Health Check"
echo "======================"

# Check critical files
CRITICAL_FILES=(
    "SOUL.md"
    "IDENTITY.md"
    "AGENTS.md"
    "USER.md"
    "kanban/tasks.json"
)

echo ""
echo "📁 Checking critical files..."
for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$WORKSPACE/$file" ]; then
        SIZE=$(wc -c < "$WORKSPACE/$file")
        if [ $SIZE -gt 0 ]; then
            echo "  ✅ $file ($SIZE bytes)"
        else
            echo "  ❌ $file (empty!)"
            ERRORS=$((ERRORS + 1))
        fi
    else
        echo "  ❌ $file (missing!)"
        ERRORS=$((ERRORS + 1))
    fi
done

# Check memory
echo ""
echo "🧠 Checking memory..."
if [ -d "$WORKSPACE/memory" ]; then
    MEMORY_COUNT=$(ls -1 "$WORKSPACE/memory"/*.md 2>/dev/null | wc -l)
    echo "  ✅ Memory files: $MEMORY_COUNT"
else
    echo "  ❌ Memory directory missing!"
    ERRORS=$((ERRORS + 1))
fi

# Check skills
echo ""
echo "🛠️  Checking skills..."
if [ -d "$WORKSPACE/skills" ]; then
    SKILL_COUNT=$(ls -1 "$WORKSPACE/skills"/*/SKILL.md 2>/dev/null | wc -l)
    echo "  ✅ Skills: $SKILL_COUNT"
else
    echo "  ❌ Skills directory missing!"
    ERRORS=$((ERRORS + 1))
fi

# Check Git
echo ""
echo "📦 Checking Git..."
cd "$WORKSPACE"
if git rev-parse --git-dir > /dev/null 2>&1; then
    LATEST_COMMIT=$(git log -1 --format="%cd" --date=relative)
    echo "  ✅ Git initialized"
    echo "  📅 Latest commit: $LATEST_COMMIT"
else
    echo "  ⚠️  Git not initialized"
fi

# Summary
echo ""
echo "======================"
if [ $ERRORS -eq 0 ]; then
    echo "✅ Charlie is healthy!"
    exit 0
else
    echo "❌ Charlie has $ERRORS error(s)!"
    exit 1
fi
```

**Usage:**
```bash
# Run health check
bash ~/workspace/scripts/charlie_health_check.sh

# Or add to crontab for automatic checking
# */30 * * * * bash ~/workspace/scripts/charlie_health_check.sh >> ~/workspace/logs/health_check.log 2>&1
```

---

## 📊 Recovery Decision Tree

```
Charlie is broken?
│
├─ Git available?
│  ├─ Yes → Use git restore (fastest)
│  └─ No → Continue
│
├─ Backup available?
│  ├─ Yes → Restore from backup (good)
│  └─ No → Continue
│
└─ Manual reconstruction
   ├─ Rebuild IDENTITY.md
   ├─ Rebuild SOUL.md
   ├─ Rebuild AGENTS.md
   ├─ Rebuild USER.md
   └─ Restart OpenClaw
```

---

## 🎯 Quick Reference: Recovery Commands

**Git Restore:**
```bash
cd ~/.openclaw/workspace
git restore SOUL.md IDENTITY.md AGENTS.md USER.md
git status
```

**Backup Restore:**
```bash
BACKUP=$(ls -t ~/.openclaw/backups/ | head -1)
cp ~/.openclaw/backups/$BACKUP/core/* ~/.openclaw/workspace/
cp -r ~/.openclaw/backups/$BACKUP/memory/* ~/.openclaw/workspace/memory/
```

**Health Check:**
```bash
bash ~/workspace/scripts/charlie_health_check.sh
```

**Manual Backup:**
```bash
bash ~/workspace/scripts/backup_critical.sh
```

---

## 💡 Charlie's Internal Safety Rules

**Before any destructive operation:**

1. **Read file first**
   ```python
   read(file_path)
   ```

2. **Create backup**
   ```python
   write(file_path + ".bak", content)
   ```

3. **Verify backup exists**
   ```python
   if not file_exists(file_path + ".bak"):
       raise Exception("Backup failed!")
   ```

4. **Then proceed with write**
   ```python
   write(file_path, new_content)
   ```

**For critical files (SOUL.md, IDENTITY.md, AGENTS.md):**
- Never use `edit` (use read + write)
- Always create timestamped backup
- Verify file size before and after
- Test if file is still readable

---

## 🚨 Emergency Contact

**If all recovery methods fail:**

1. **Reinstall OpenClaw:**
   ```bash
   npm install -g openclaw
   ```

2. **Reinitialize workspace:**
   ```bash
   openclaw init
   ```

3. **Restore from backup:**
   ```bash
   cp ~/backups/charlie-latest/* ~/.openclaw/workspace/
   ```

4. **Start OpenClaw:**
   ```bash
   openclaw gateway start
   ```

---

## 📝 Summary: Three Layers of Protection

| Layer | Method | Automation | Recovery Speed |
|-------|--------|------------|----------------|
| 1 | Git | Cron (hourly) | ⚡ Seconds |
| 2 | Backups | Cron (hourly) | 🚀 Minutes |
| 3 | Manual reconstruction | N/A | 🐌 Hours |

**Recommendation:** Enable all three layers for maximum safety.

---

**Created by:** Charlie (autonomous self-preservation)
**Reviewed by:** David (human supervisor)
**Last updated:** 2026-02-21
