#!/bin/bash
# kanban/cleanup.sh — Kanban storage management
# Run manually or via cron: 0 3 * * * /Users/charlie/.openclaw/workspace/kanban/cleanup.sh

KANBAN_DIR="/Users/charlie/.openclaw/workspace/kanban"
ARCHIVE_DIR="$KANBAN_DIR/archive"

echo "=== Kanban Cleanup: $(date) ==="
echo ""

# 1. Show current size
echo "📊 Current size:"
du -sh "$KANBAN_DIR"
echo ""

# 2. Delete archive files older than 30 days
echo "🗑 Deleting archive entries older than 30 days..."
find "$ARCHIVE_DIR" -name "*.md" -mtime +30 -delete 2>/dev/null
find "$ARCHIVE_DIR" -name "*.json" -mtime +30 -delete 2>/dev/null
# Remove empty project directories
find "$ARCHIVE_DIR" -type d -empty -delete 2>/dev/null
echo "Done."
echo ""

# 3. Check if projects/ is too large (warn at 200MB)
PROJECTS_SIZE=$(du -sm "$KANBAN_DIR/projects" 2>/dev/null | cut -f1)
if [ "$PROJECTS_SIZE" -gt 200 ] 2>/dev/null; then
    echo "⚠️  WARNING: projects/ is ${PROJECTS_SIZE}MB (limit: 200MB)"
    echo "   Consider archiving completed projects."
fi

# 4. Show archive size breakdown
echo "📁 Archive contents:"
ls -la "$ARCHIVE_DIR" 2>/dev/null || echo "  (empty)"
echo ""

echo "✅ Cleanup complete."
