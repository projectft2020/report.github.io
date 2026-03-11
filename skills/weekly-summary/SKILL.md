---
name: weekly-summary
description: Generate weekly research summary reports. Use when compiling weekly research digests, identifying high-value work, or tracking research trends. Automatically selects top research, compiles themes, and formats output.
---

# Weekly Summary

## Overview

Automatically generates weekly research summary reports. Compiles high-quality research, identifies emerging themes, and highlights key achievements.

## Core Capabilities

### 1. Generate Weekly Summary

Generate a summary for the past week:

```bash
python3 scripts/generate_summary.py --days 7
```

**Parameters:**
- `--days <N>`: Number of days to summarize (default: 7)
- `--min-score <N>`: Minimum score to include (default: 7.0)
- `--output <path>`: Save summary to file

**Output:** Formatted weekly summary with Top 10 research

### 2. Customize Summary Template

Edit summary template:

```bash
python3 scripts/edit_template.py
```

**Opens:** Default template in text editor for customization

### 3. Preview Summary

Preview summary before finalizing:

```bash
python3 scripts/preview_summary.py
```

**Shows:** Summary content without saving

## Summary Sections

### Executive Summary

- Research completed in the period
- Key highlights
- Emerging trends

### Top 10 Research

High-scoring research from the period:
- Task ID and title
- Overall score and quality level
- Core method and key results
- Applications and limitations

### New Methods/Techniques

Novel approaches discovered:
- Method names and descriptions
- Research references
- Innovation indicators

### Application Themes

Common application domains:
- Frequency of applications
- Cross-research patterns
- Emerging domains

### Quality Trends

Research quality over time:
- Average score trends
- Quality distribution
- High-quality research count

### Recommendations

Based on the week's findings:
- Areas to focus on
- Research gaps identified
- Next week priorities

## Template Customization

### Default Template

The default template includes:

```markdown
# Weekly Research Summary - [Date Range]

## Executive Summary

This week completed [X] research tasks with average score of [Y].

## Top 10 Research

1. [Task ID] - [Score] - [Quality]
   **Core Method:** [Method]
   **Key Results:** [Results]
   **Applications:** [Apps]
   **Limitations:** [Limits]

[... continue for 10 items ...]

## New Methods

- [Method 1] ([Research ID])
- [Method 2] ([Research ID])

## Application Themes

- [Application 1]: [X] studies
- [Application 2]: [Y] studies

## Quality Trends

- Average score: [X]
- High-quality research: [Y] studies
- Trend: [Direction]

## Recommendations

- [Recommendation 1]
- [Recommendation 2]
```

### Customizing Template

Edit `references/summary_template.md` to customize:

- Add/remove sections
- Change formatting
- Adjust emphasis
- Add branding

## Scripts Reference

### scripts/generate_summary.py

Generate weekly summary.

**Parameters:** `--days`, `--min-score`, `--output`

**Returns:** Summary object and saved file

### scripts/edit_template.py

Edit summary template.

**Returns:** Opens template in editor

### scripts/preview_summary.py

Preview summary content.

**Returns:** Displays summary without saving

## Best Practices

1. **Generate regularly:** Run every week (Monday or Sunday)
2. **Include quality filter:** Only include research >= 7.0 score
3. **Highlight trends:** Show quality changes over time
4. **Provide context:** Explain why research matters
5. **Be concise:** Focus on actionable insights
6. **Track themes:** Identify emerging patterns

## Troubleshooting

### No Recent Research

**Symptom:** Summary shows no research for the period

**Solution:**
- Verify date range is correct
- Check if research outputs exist
- Review score thresholds
- Confirm time zone settings

### Low-Quality Research

**Symptom:** All Top 10 research has low scores (< 6.0)

**Solution:**
- Check scoring criteria
- Review research quality guidelines
- Adjust min-score threshold
- Provide feedback to research agents

### Summary Too Long

**Symptom:** Summary exceeds expected length

**Solution:**
- Customize template to be more concise
- Reduce detail in Top 10 descriptions
- Group related research
- Use bullet points instead of paragraphs

## Integration with Research Scorer

Generate summary only for high-quality research:

```python
from skills.weekly_summary import generate_summary

# Generate summary with quality filter
summary = generate_summary.generate_summary(
    days=7,
    min_score=7.0,  # Only include good or better
    output="weekly-summary.md"
)
```

## Scheduled Execution

### Cron Schedule

Add to crontab for weekly generation:

```cron
# Every Monday at 9:00 AM
0 9 * * 1 python3 /path/to/skills/weekly-summary/scripts/generate_summary.py --days 7
```

### Heartbeat Integration

Run weekly during heartbeat:

```python
from datetime import datetime, timedelta

def check_weekly_summary():
    # Check if summary was generated this week
    # If not, generate it
    pass
```

## Output Locations

- **Default:** `kanban/weekly-summary-YYYY-MM-DD.md`
- **Custom:** Path specified with `--output`

Files are automatically timestamped to prevent overwrites.
