---
name: research-scorer
description: Score research reports across multiple quality dimensions. Use when evaluating research quality, filtering by quality levels, or establishing quality standards. Automatically assesses depth, completeness, innovation, and applicability, generating structured scores.
---

# Research Scorer

## Overview

Automatically scores research reports across four quality dimensions. Provides objective assessment of research quality to help identify high-value work and filter out low-quality outputs.

## Core Capabilities

### 1. Score Single Research Report

Evaluate a single research report:

```bash
python3 scripts/score_research.py <research-file>
```

**Parameters:**
- `research-file`: Path to research markdown file
- `--output <path>`: Save score to file (default: same directory)
- `--verbose`: Show detailed evaluation

**Dimensions Evaluated:**
- **Depth** (0-10): Technical detail, formulas, proofs
- **Completeness** (0-10): Coverage of requirements
- **Innovation** (0-10): Novelty vs known methods
- **Applicability** (0-10): Practical use cases
- **Overall** (0-10): Weighted average

### 2. Batch Score Multiple Reports

Score all research reports in a directory:

```bash
python3 scripts/batch_score.py <directory>
```

**Parameters:**
- `directory`: Directory containing research files
- `--recursive`: Score in subdirectories
- `--min-score <N>`: Only show scores >= N
- `--output <path>`: Save summary to file

**Output:** Summary report with all scores

### 3. Generate Score Statistics

Analyze score distribution across all research:

```bash
python3 scripts/score_statistics.py
```

**Output:**
- Average scores by dimension
- Score distribution
- Low-score research list (< 6.0)
- High-score research list (>= 8.0)
- Quality trends over time

### 4. Filter by Quality

Filter research reports by score threshold:

```bash
python3 scripts/filter_by_score.py --threshold <N> --operator [gt|lt|ge|le]
```

**Parameters:**
- `--threshold <N>`: Score threshold (default: 7.0)
- `--operator [gt|lt|ge|le]`: Comparison operator (default: ge)
- `--output <path>`: Save filtered list to file

**Output:** List of research IDs matching criteria

## Scoring Criteria

### Depth (0-10 points)

**What it measures:**
- Technical detail level
- Presence of formulas, equations, proofs
- Understanding of underlying theory

**Evaluation:**
- 0-3 points: Surface-level, no technical detail
- 4-6 points: Moderate detail, some technical content
- 7-10 points: Deep technical analysis, comprehensive coverage

### Completeness (0-10 points)

**What it measures:**
- Coverage of all requirements
- Answer completeness
- Missing information

**Evaluation:**
- 0-3 points: Significant gaps, missing key aspects
- 4-6 points: Good coverage, some gaps
- 7-10 points: Comprehensive, all requirements addressed

### Innovation (0-10 points)

**What it measures:**
- Novelty vs known methods
- New contributions
- Originality

**Evaluation:**
- 0-3 points: Reproduction, no new insights
- 4-6 points: Minor improvements, known methods applied
- 7-10 points: Novel approach, significant contributions

### Applicability (0-10 points)

**What it measures:**
- Practical use cases
- Real-world application potential
- Implementation feasibility

**Evaluation:**
- 0-3 points: Theoretical only, no practical use
- 4-6 points: Some applications, limited feasibility
- 7-10 points: Clear applications, practical value

## Weighting System

### Default Weights

- **Depth:** 30%
- **Completeness:** 25%
- **Innovation:** 25%
- **Applicability:** 20%

### Overall Score Calculation

```
Overall = (Depth × 0.30) + (Completeness × 0.25)
        + (Innovation × 0.25) + (Applicability × 0.20)
```

### Quality Levels

- **High Quality:** Overall >= 8.0
- **Good Quality:** Overall >= 6.5 and < 8.0
- **Moderate Quality:** Overall >= 5.0 and < 6.5
- **Low Quality:** Overall < 5.0

## Output Format

### .score File

Each scored research generates a `.score` file:

```json
{
  "research_file": "path/to/research.md",
  "task_id": "task-id",
  "scores": {
    "depth": 8,
    "completeness": 7,
    "innovation": 7,
    "applicability": 6
  },
  "overall": 7.25,
  "quality_level": "High Quality",
  "timestamp": "2026-03-04T10:55:00Z",
  "notes": [
    "Deep technical analysis with formulas",
    "Comprehensive coverage of requirements",
    "Novel approach to problem"
  ]
}
```

## Configuration

### Scoring Parameters

Edit `references/scoring_params.json` to customize:

- Weights for each dimension
- Thresholds for quality levels
- Custom evaluation criteria

### Example Configuration

```json
{
  "weights": {
    "depth": 0.30,
    "completeness": 0.25,
    "innovation": 0.25,
    "applicability": 0.20
  },
  "thresholds": {
    "high": 8.0,
    "good": 6.5,
    "moderate": 5.0
  }
}
```

## Scripts Reference

### scripts/score_research.py

Score a single research report.

**Parameters:** `<research-file>`, `--output`, `--verbose`

**Returns:** Score object with all dimensions

### scripts/batch_score.py

Score multiple research reports.

**Parameters:** `<directory>`, `--recursive`, `--min-score`, `--output`

**Returns:** Summary report

### scripts/score_statistics.py

Analyze score distribution.

**Output:** Statistical report

### scripts/filter_by_score.py

Filter research by score threshold.

**Parameters:** `--threshold`, `--operator`, `--output`

**Returns:** Filtered list

## Best Practices

1. **Score after completion:** Generate scores immediately after research finishes
2. **Track quality trends:** Monitor score changes over time
3. **Filter low-quality work:** Exclude low-score research from summaries
4. **Highlight high-quality work:** Feature top-scoring research
5. **Use scores for prioritization:** Prioritize related tasks to high-quality research
6. **Customize for domain:** Adjust weights based on research type

## Troubleshooting

### Low Scores Consistently

**Symptom:** All research scoring low (< 5.0)

**Solution:**
- Review scoring criteria
- Check if research format matches expectations
- Adjust weights for research type
- Provide better guidelines to research agents

### Inconsistent Scores

**Symptom:** Similar research gets very different scores

**Solution:**
- Check evaluation consistency
- Review scoring notes for criteria
- Adjust evaluation thresholds
- Normalize scoring approach

### Scores Not Generated

**Symptom:** .score files not created

**Solution:**
- Verify research file exists and is readable
- Check file permissions
- Review scoring script errors
