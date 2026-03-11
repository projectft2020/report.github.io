#!/bin/bash
# Backup critical Charlie files
# Usage: bash ~/workspace/scripts/backup_critical.sh

set -e

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$HOME/.openclaw/backups/charlie-backup-$DATE"

echo "📦 Creating Charlie backup..."

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
)

echo "📁 Backing up core files..."
mkdir -p "$BACKUP_DIR/core"
for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "$BACKUP_DIR/core/" 2>/dev/null
        SIZE=$(wc -c < "$BACKUP_DIR/core/$file")
        echo "  ✅ $file ($SIZE bytes)"
    else
        echo "  ⚠️  $file (not found)"
    fi
done

# Special handling for files with slashes
echo "📋 Backing up kanban files..."
mkdir -p "$BACKUP_DIR/kanban"
if [ -f "kanban/tasks.json" ]; then
    cp "kanban/tasks.json" "$BACKUP_DIR/kanban/"
    SIZE=$(wc -c < "$BACKUP_DIR/kanban/tasks.json")
    echo "  ✅ kanban/tasks.json ($SIZE bytes)"
else
    echo "  ⚠️  kanban/tasks.json (not found)"
fi

# Memory files
echo "🧠 Backing up memory..."
mkdir -p "$BACKUP_DIR/memory"
if [ -d "memory" ]; then
    cp -r memory/* "$BACKUP_DIR/memory/" 2>/dev/null
    MEMORY_COUNT=$(ls -1 "$BACKUP_DIR/memory"/*.md 2>/dev/null | wc -l)
    echo "  ✅ Memory files: $MEMORY_COUNT"
fi

# Skills
echo "🛠️  Backing up skills..."
mkdir -p "$BACKUP_DIR/skills"
if [ -d "skills" ]; then
    cp -r skills/* "$BACKUP_DIR/skills/" 2>/dev/null
    SKILL_COUNT=$(ls -1 "$BACKUP_DIR/skills"/*/SKILL.md 2>/dev/null | wc -l)
    echo "  ✅ Skills: $SKILL_COUNT"
fi

# Create checksum
echo "🔍 Creating checksums..."
cd "$BACKUP_DIR"
find . -type f -exec md5 {} \; > checksums.md5
cd -

echo ""
echo "✅ Backup created: $BACKUP_DIR"
echo "📊 Size: $(du -sh "$BACKUP_DIR" | cut -f1)"

# Keep only last 7 backups
echo ""
echo "🧹 Cleaning old backups (keeping last 7)..."
find "$HOME/.openclaw/backups" -type d -name "charlie-backup-*" | sort | head -n -7 | xargs rm -rf 2>/dev/null || true

# List all backups
echo ""
echo "📦 Current backups:"
ls -1 "$HOME/.openclaw/backups" | tail -5
