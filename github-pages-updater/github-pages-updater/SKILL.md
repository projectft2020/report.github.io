---
name: github-pages-updater
description: Automated GitHub Pages publishing workflow for research reports. Use when batch converting Markdown reports to HTML, updating index.html, and pushing to GitHub Pages. Ideal for recurring deployments of research output to projectft2020.github.io/report.github.io.
---

# GitHub Pages Updater

## Quick Start

Complete workflow to publish research reports to GitHub Pages:

```bash
# 1. Batch convert Markdown to HTML
cd /Users/charlie/.openclaw/workspace
python3 batch_convert_reports.py

# 2. Update index.html with all reports
cd /Users/charlie/report
python3 /Users/charlie/.openclaw/workspace/update_index.py

# 3. Commit and push
git add .
git commit -m "📚 更新研究報告"
git push origin main
```

## Workflow

### Step 1: Batch Convert Reports

Convert all Markdown research reports to HTML format.

**Script:** `scripts/batch_convert_reports.py`

**What it does:**
- Recursively scans `/Users/charlie/.openclaw/workspace/kanban/projects/` for `.md` files
- Extracts title from first H1 heading in each Markdown file
- Checks if HTML already exists (incremental update)
- Converts Markdown → HTML with template
- Reports progress every 10 files

**Usage:**
```bash
cd /Users/charlie/.openclaw/workspace
python3 batch_convert_reports.py
```

**Output:**
- Converted HTML files in `/Users/charlie/report/`
- Summary: converted, skipped, failed counts

### Step 2: Update Index HTML

Update `index.html` to include all reports with links.

**Script:** `scripts/update_index.py`

**What it does:**
- Scans all HTML files (except `index.html`)
- Extracts metadata (title, description, date, category)
- Generates JavaScript `reports` array
- Updates report count in stats section
- Writes complete index.html

**Usage:**
```bash
cd /Users/charlie/report
python3 /Users/charlie/.openclaw/workspace/update_index.py
```

**Auto-categorization (by file prefix):**
- `q*` → quant-evolve
- `t*` → trend-trading
- `m*` → momentum
- `s*/st*` → statistical-arb
- `b*` (barra) → barra
- `b*` (other) → blockchain
- `k*` → skewness
- `r*` (regime) → regime
- `r*` (other) → risk-management
- `d*` (dhri) → tools
- `d*` (other) → derivatives
- `f*` → factor-analysis
- `h*` → hft
- `e*/g*/v*` → ml
- `x*` → ai
- `a*/w*/p*/pj*` → system/crisis

### Step 3: Git Push

Deploy updates to GitHub Pages.

```bash
cd /Users/charlie/report
git add .
git commit -m "📚 更新研究報告"
git push origin main
```

**Deployment time:** 1-2 minutes for GitHub Pages to rebuild.

### Step 4: Verify

Visit https://projectft2020.github.io/report.github.io/ to verify:

- Report count is correct
- All reports have clickable links
- New reports appear in timeline

## When to Use This Skill

**Trigger scenarios:**
- After batch of research tasks complete (5+ new reports)
- Daily/weekly scheduled deployment
- Manual request: "Update GitHub Pages" or "Publish my reports"
- Index.html shows outdated report count or missing links

**Do NOT use for:**
- Individual report editing (use HTML template directly)
- Repository setup or configuration issues
- Customizing CSS or layout (edit index.html directly)

## Troubleshooting

**Issue:** `update_index.py` fails with "No such file or directory"
**Fix:** Ensure you're running from `/Users/charlie/report` directory

**Issue:** Reports not appearing on website
**Fix:** Wait 2-3 minutes for GitHub Pages to rebuild; verify push succeeded

**Issue:** Wrong categorization
**Fix:** Edit `update_index.py` auto-categorization logic; re-run script

**Issue:** Missing CNAME causes wrong URL
**Fix:** Remove `CNAME` file from `/Users/charlie/report/` to use default GitHub Pages URL

## Project Paths

| Item | Path |
|-------|------|
| **Workspace** | `/Users/charlie/.openclaw/workspace` |
| **Report repo** | `/Users/charlie/report` |
| **Remote** | `git@github.com:projectft2020/report.github.io.git` |
| **Website URL** | `https://projectft2020.github.io/report.github.io/` |

## Resources

### scripts/

**batch_convert_reports.py** - Batch Markdown→HTML converter
- Supports incremental updates (skips existing HTML)
- Progress reporting every 10 files
- Extracts titles from H1 headings

**update_index.py** - Index.html updater
- Extracts metadata from HTML files
- Generates JavaScript reports array
- Updates statistics
- Auto-categorization by file prefix

## Best Practices

1. **Run both scripts** in order (convert → update)
2. **Commit immediately** after updating to avoid merge conflicts
3. **Verify deployment** by checking website after 2 minutes
4. **Monitor report count** - should match total HTML files (index.html excluded)
5. **Backup before** major updates: `git commit` creates revision history
