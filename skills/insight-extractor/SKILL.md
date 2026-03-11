---
name: insight-extractor
description: Extract structured insights from research reports. Use when building knowledge bases, analyzing research themes, or preparing weekly summaries. Automatically identifies core methods, key results, applications, and limitations, storing in queryable format.
---

# Insight Extractor

## Overview

Automatically extracts structured insights from research reports. Enables knowledge management by making research findings queryable and reusable.

## Core Capabilities

### 1. Extract Insights from Single Report

Extract insights from one research report:

```bash
python3 scripts/extract_insights.py <research-file>
```

**Parameters:**
- `research-file`: Path to research markdown file
- `--output <path>`: Save insights to file (default: same directory)
- `--verbose`: Show extraction details

**Extracted Insights:**
- **Core Method** (1-2 sentences): Main approach or technique
- **Key Results** (1-2 sentences): Primary findings or outcomes
- **Applications** (3-5 items): Practical use cases
- **Limitations** (2-3 items): Drawbacks or constraints
- **Related Papers** (arXiv IDs): Cited or related research

### 2. Batch Extract from Directory

Extract insights from all research reports in a directory:

```bash
python3 scripts/batch_extract.py <directory>
```

**Parameters:**
- `directory`: Directory containing research files
- `--recursive`: Extract from subdirectories
- `--output <path>`: Save summary to file

**Output:** Summary of extracted insights

### 3. Search Insights

Query extracted insights:

```bash
python3 scripts/search_insights.py <query>
```

**Parameters:**
- `query`: Search query (e.g., "fair clustering", "ML optimization")
- `--limit <N>`: Maximum results (default: 10)
- `--output <path>`: Save results to file

**Output:** List of relevant research with matching insights

## Insight Format

### .insights File

Each extracted research generates an `.insights` file:

```json
{
  "research_file": "path/to/research.md",
  "task_id": "task-id",
  "insights": {
    "core_method": "Novel approach using X and Y",
    "key_results": [
      "Achieved 95% accuracy on dataset Z",
      "Outperformed previous methods by 20%"
    ],
    "applications": [
      "Image classification",
      "Natural language processing",
      "Recommendation systems"
    ],
    "limitations": [
      "Computationally expensive",
      "Requires large datasets",
      "Limited to specific domains"
    ],
    "related_papers": [
      "2101.00001",
      "2205.12345"
    ]
  },
  "timestamp": "2026-03-04T10:55:00Z",
  "extraction_method": "automatic",
  "confidence": "high"
}
```

## Extraction Strategy

### Core Method Extraction

Identify the main approach or technique:

**Look for sections:**
- "方法", "Method", "核心方法", "Core Method"
- "算法", "Algorithm", "Approach"
- "技術", "Technique", "Solution"

**Extract from:**
- First paragraph after main heading
- Summary or abstract section
- Conclusions with key method described

**Target:** 1-2 sentences, concise and clear

### Key Results Extraction

Identify primary findings or outcomes:

**Look for sections:**
- "結果", "Results", "實驗結果", "Experimental Results"
- "結論", "Conclusion", "主要發現"
- "主要貢獻", "Main Contributions"

**Extract from:**
- Summary of main findings
- Numerical results (accuracy, improvement, metrics)
- Key quantitative outcomes

**Target:** 1-2 sentences, highlight key metrics

### Applications Extraction

Identify practical use cases:

**Look for sections:**
- "應用", "Application", "應用價值", "Applications"
- "實際應用", "Practical Applications"
- "使用場景", "Use Cases"

**Extract from:**
- Mentioned application domains
- Real-world scenarios
- Implementation contexts

**Target:** 3-5 items, specific and actionable

### Limitations Extraction

Identify drawbacks or constraints:

**Look for sections:**
- "局限性", "Limitations", "限制"
- "挑戰", "Challenges", "未來工作"
- "注意事項", "Considerations"

**Extract from:**
- Mentioned constraints
- Performance trade-offs
- Known limitations

**Target:** 2-3 items, honest about weaknesses

### Related Papers Extraction

Identify cited or related research:

**Look for sections:**
- "相關研究", "Related Work", "References"
- "引用", "Citations", "Bibliography"
- arXiv IDs in text (e.g., "arXiv:2101.00001")

**Extract from:**
- Explicitly cited papers
- Mentions of similar work
- arXiv ID patterns

**Target:** List of arXiv IDs for cross-referencing

## Scripts Reference

### scripts/extract_insights.py

Extract insights from single research.

**Parameters:** `<research-file>`, `--output`, `--verbose`

**Returns:** Insights object

### scripts/batch_extract.py

Extract insights from directory.

**Parameters:** `<directory>`, `--recursive`, `--output`

**Returns:** Summary of extracted insights

### scripts/search_insights.py

Query extracted insights.

**Parameters:** `<query>`, `--limit`, `--output`

**Returns:** List of relevant insights

## Best Practices

1. **Extract immediately:** Generate insights after research completion
2. **Review quality:** Check extracted insights for accuracy
3. **Consistent format:** Follow structure across all extractions
4. **Cross-reference:** Use related papers to link research
5. **Query regularly:** Use search to find relevant insights
6. **Maintain insights:** Keep .insights files updated with new research

## Troubleshooting

### Empty Insights

**Symptom:** All fields are empty or null

**Solution:**
- Check research report structure
- Verify extraction keywords match report sections
- Adjust section headers for consistency
- Manual review for research with non-standard format

### Low Confidence

**Symptom:** Confidence set to "low" for all extractions

**Solution:**
- Review extraction criteria
- Check if research language differs
- Adjust confidence thresholds
- Manual verification of extracted insights

### Search No Results

**Symptom:** Query returns no matching insights

**Solution:**
- Try broader search terms
- Check query spelling and language
- Verify insights exist in directory
- Use simpler queries

## Integration with Research Scorer

Extract insights after scoring:

```python
from skills.research_scorer import score_research
from skills.insight_extractor import extract_insights

# Score research
score = score_research.score_research(research_file)

# Extract insights (only if high quality)
if score and score["overall"] >= 7.0:
    insights = extract_insights.extract_insights(research_file)
```

## Knowledge Base Structure

All extracted insights can be queried and searched:

```
kanban/projects/
├── arxiv-xxxxx/
│   ├── scout-xxxxx-research.md
│   ├── scout-xxxxx-research.score
│   └── scout-xxxxx-research.insights
└── insights-index.json (search index)
```

The `insights-index.json` contains all insights for fast querying.
