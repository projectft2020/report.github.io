#!/bin/bash
# Check if Charlie is healthy
# Usage: bash ~/workspace/scripts/charlie_health_check.sh

set -e

WORKSPACE="$HOME/.openclaw/workspace"
ERRORS=0
WARNINGS=0

echo "🩺 Charlie Health Check"
echo "======================"

# Check if workspace exists
if [ ! -d "$WORKSPACE" ]; then
    echo "❌ Workspace not found: $WORKSPACE"
    exit 1
fi

cd "$WORKSPACE"

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
    if [ -f "$file" ]; then
        SIZE=$(wc -c < "$file")
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

# Check important files
IMPORTANT_FILES=(
    "MEMORY.md"
    "KANBAN.md"
    "HEARTBEAT.md"
)

echo ""
echo "📄 Checking important files..."
for file in "${IMPORTANT_FILES[@]}"; do
    if [ -f "$file" ]; then
        SIZE=$(wc -c < "$file")
        echo "  ✅ $file ($SIZE bytes)"
    else
        echo "  ⚠️  $file (not found, but recoverable)"
        WARNINGS=$((WARNINGS + 1))
    fi
done

# Check memory
echo ""
echo "🧠 Checking memory..."
if [ -d "memory" ]; then
    MEMORY_COUNT=$(ls -1 memory/*.md 2>/dev/null | wc -l)
    TOTAL_SIZE=$(du -sh memory 2>/dev/null | cut -f1)
    echo "  ✅ Memory directory exists"
    echo "  📊 Files: $MEMORY_COUNT"
    echo "  📏 Total size: $TOTAL_SIZE"

    # Check for daily logs
    TODAY=$(date +%Y-%m-%d)
    if [ -f "memory/$TODAY.md" ]; then
        echo "  ✅ Today's log exists: $TODAY.md"
    else
        echo "  ⚠️  Today's log not found: $TODAY.md"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo "  ❌ Memory directory missing!"
    ERRORS=$((ERRORS + 1))
fi

# Check skills
echo ""
echo "🛠️  Checking skills..."
if [ -d "skills" ]; then
    SKILL_COUNT=$(ls -1 skills/*/SKILL.md 2>/dev/null | wc -l)
    echo "  ✅ Skills directory exists"
    echo "  📊 Skills: $SKILL_COUNT"

    # List available skills
    if [ $SKILL_COUNT -gt 0 ]; then
        echo "  📋 Available skills:"
        ls -1 skills/*/SKILL.md 2>/dev/null | sed 's|skills/\(.*\)/SKILL.md|     - \1|'
    fi
else
    echo "  ❌ Skills directory missing!"
    ERRORS=$((ERRORS + 1))
fi

# Check Kanban
echo ""
echo "📋 Checking Kanban..."
if [ -f "kanban/tasks.json" ]; then
    TASK_SIZE=$(wc -c < kanban/tasks.json)
    echo "  ✅ tasks.json exists ($TASK_SIZE bytes)"

    # Try to parse JSON
    if command -v python3 &> /dev/null; then
        TASK_COUNT=$(python3 -c "import json; tasks=json.load(open('kanban/tasks.json')); print(len(tasks))" 2>/dev/null || echo "0")
        COMPLETED=$(python3 -c "import json; tasks=json.load(open('kanban/tasks.json')); print(sum(1 for t in tasks if t.get('status') == 'completed'))" 2>/dev/null || echo "0")
        echo "  📊 Total tasks: $TASK_COUNT"
        echo "  ✅ Completed: $COMPLETED"
    fi
else
    echo "  ❌ Kanban tasks.json missing!"
    ERRORS=$((ERRORS + 1))
fi

# Check Git
echo ""
echo "📦 Checking Git..."
if git rev-parse --git-dir > /dev/null 2>&1; then
    LATEST_COMMIT=$(git log -1 --format="%cd" --date=relative 2>/dev/null || echo "N/A")
    COMMIT_HASH=$(git log -1 --format="%h" 2>/dev/null || echo "N/A")
    echo "  ✅ Git initialized"
    echo "  📅 Latest commit: $LATEST_COMMIT ($COMMIT_HASH)"

    # Check for uncommitted changes
    CHANGES=$(git status --porcelain 2>/dev/null | wc -l)
    if [ $CHANGES -gt 0 ]; then
        echo "  ⚠️  Uncommitted changes: $CHANGES files"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo "  ⚠️  Git not initialized (no version control)"
    WARNINGS=$((WARNINGS + 1))
fi

# Check backups
echo ""
echo "💾 Checking backups..."
if [ -d "$HOME/.openclaw/backups" ]; then
    BACKUP_COUNT=$(ls -1 "$HOME/.openclaw/backups" | wc -l)
    echo "  ✅ Backups directory exists"
    echo "  📊 Backup count: $BACKUP_COUNT"

    if [ $BACKUP_COUNT -gt 0 ]; then
        LATEST_BACKUP=$(ls -t "$HOME/.openclaw/backups" | head -1)
        BACKUP_DATE=$(echo "$LATEST_BACKUP" | sed 's/charlie-backup-//' | sed 's/_/ /')
        echo "  📅 Latest backup: $BACKUP_DATE"
    else
        echo "  ⚠️  No backups found"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo "  ⚠️  No backups directory"
    WARNINGS=$((WARNINGS + 1))
fi

# Summary
echo ""
echo "======================"
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "✅ Charlie is perfectly healthy!"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo "⚠️  Charlie is healthy but has $WARNINGS warning(s)"
    exit 0
else
    echo "❌ Charlie has $ERRORS error(s) and $WARNINGS warning(s)!"
    exit 1
fi
