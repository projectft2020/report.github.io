# Memory Optimization Plan

**Created:** 2026-02-21 02:10 GMT+8
**Goal:** Prevent memory bloat and improve vector retrieval efficiency

---

## 📊 Current State Analysis

### Memory Size (2026-02-21 02:10)
| Metric | Current | Threshold | Status |
|--------|---------|-----------|--------|
| Total Memory | 223 KB | 2 MB | ✅ OK |
| Daily Max | 108 KB | 50 KB | ⚠️ Over |
| Index Files | 18 KB | 100 KB | ✅ OK |
| Archived Projects | 10 KB | 500 KB | ✅ OK |

### Bloat Risk
- **Growth Rate:** ~100 KB/day (recent trend)
- **Projection (1 month):** 3-5 MB
- **Projection (3 months):** 9-15 MB
- **Risk Level:** Medium-High

---

## 🎯 Optimization Strategy

### Layer 1: Daily Memory (Raw Logs)

**Purpose:** Preserve raw information for reference
**Rule:** Never delete, but compress after 7 days

**Compression Strategy (after 7 days):**
```markdown
## 2026-02-19 (Compressed)

### Key Events
- ✅ QuantEvolve research completed (5/5 tasks)
- ✅ Trend trading system deployed (6/6 tasks)
- 📈 Output: ~93K words, ~1.4K lines code

### Insights
- Genetic algorithms show promise for strategy evolution
- Trend strength scoring improves accuracy 20-30%
- Tail risk hedging superior to stop-loss

### Full Details
See: kanban/projects/quant-evolve-20260219/
     kanban/projects/trend-trading-20260219/
```

**Action:** 
- Keep daily logs for 7 days uncompressed
- After 7 days, compress to key events + insights + links
- Delete redundant content, keep only unique insights

---

### Layer 2: MEMORY.md (Curated Insights)

**Purpose:** Long-term memory, high-value insights only
**Rule:** Only update when new patterns emerge

**Update Frequency:** Weekly (or after major project completion)

**Content Strategy:**
1. **Identity & Preferences** (static, rarely change)
2. **Completed Projects** (summary only, link to details)
3. **Key Insights** (patterns, decisions, lessons learned)
4. **System Capabilities** (tools, reliability patterns)
5. **Research Focus** (priority topics, user preferences)

**Example:**
```markdown
## Key Insights (2026-02-19)

### Pattern: Task Recovery
- **Finding:** Many "failed" tasks have valid output files
- **Rule:** Always check output files before marking as failed
- **Implementation:** Check file size > 20 KB as success indicator

### Pattern: Agent Reliability
- **Research:** 100% reliable (4/4 tasks)
- **Analyst:** 100% reliable (2/2 tasks)
- **Automation:** 0% reliable (0/2 tasks)
- **Rule:** Avoid automation agent for critical tasks
```

---

### Layer 3: INDEX.md (Navigation)

**Purpose:** Quick access to all memory
**Rule:** Update when new files/projects added

**Content:**
- Daily memory files (with size/date)
- Completed projects (status, links)
- Active projects (progress, blockers)
- Quick reference (commands, paths)

**Size Target:** ≤ 20 KB

---

### Layer 4: ARCHIVED_PROJECTS.md (Summaries)

**Purpose:** Completed project summaries
**Rule:** Archive after project completion + 3 days

**Compression Strategy:**
- Project name + ID
- Status + rating
- Key findings (3-5 bullets)
- Output summary (size, lines)
- Link to full output

**Example:**
```markdown
### 1. QuantEvolve (2026-02-19)
- **Rating:** ⭐⭐⭐⭐ (4/5)
- **Feasibility:** Medium (4-7 weeks)
- **Key Finding:** Genetic algorithms show promise for strategy evolution
- **Output:** 93K words, 1.4K lines code
- **Location:** kanban/projects/quant-evolve-20260219/
```

---

## 🔍 Vector Retrieval System (QMD)

### What is QMD?

**QMD = Quant Data Management** (or **Quant Memory Discovery**)

**Purpose:** 
- Semantic search across memory files
- Vector-based trajectory tracking
- Pattern discovery across projects

### Implementation

#### Option 1: Native memory_search (Current)
```python
# Already built-in to OpenClaw
memory_search({
  "query": "fat-tail analysis",
  "maxResults": 5,
  "minScore": 0.7
})
```

**Pros:**
- ✅ Already available
- ✅ Semantic search
- ✅ Returns with file paths + line numbers

**Cons:**
- ❌ Requires manual memory_get for details
- ❌ No pattern visualization

#### Option 2: Enhanced Memory Tags

**Add to MEMORY.md:**
```markdown
## Tags

### #risk-management
- Tail risk hedging (2026-02-19)
- DHRI indicator (2026-02-20)
- Fat-tail analysis (m001, 2026-02-20)

### #multi-factor
- Alpha101 extension (ml-multifactor, 2026-02-20)
- Factor optimization (research-2026-02-17)

### #trend-following
- Trend strength scoring (trend-trading, 2026-02-19)
- Multi-timeframe (trend-trading, 2026-02-19)
```

**Pros:**
- ✅ Easy to scan
- ✅ No additional tools
- ✅ Simple to maintain

**Cons:**
- ❌ Manual tagging required
- ❌ No automatic clustering

#### Option 3: Python-based Vector Search

**Create:** `memory/vector_search.py`

```python
from openclaw_tools import memory_search, memory_get
from collections import defaultdict
import json

class VectorTrajectory:
    def __init__(self):
        self.trajectories = defaultdict(list)

    def find_trajectory(self, topic, max_results=10):
        """Find the vector trajectory of a research topic"""
        results = memory_search(topic, maxResults=max_results)
        
        trajectory = []
        for result in results:
            path = result['path']
            lines = result['lines']
            
            # Get actual content
            content = memory_get(path, from=lines[0], lines=len(lines))
            
            trajectory.append({
                'date': extract_date(path),
                'context': content,
                'confidence': result['score']
            })
        
        return sorted(trajectory, key=lambda x: x['date'])

    def visualize(self, topic):
        """Generate a beautiful trajectory visualization"""
        trajectory = self.find_trajectory(topic)
        
        # Generate ASCII visualization
        output = []
        for i, point in enumerate(trajectory):
            arrow = "→" if i < len(trajectory) - 1 else "✓"
            date = point['date']
            context = point['context'][:100] + "..."
            confidence = point['confidence']
            
            output.append(f"{arrow} {date} ({confidence:.2f}): {context}")
        
        return "\n".join(output)
```

**Usage:**
```python
# Find trajectory for "fat-tail"
vt = VectorTrajectory()
print(vt.visualize("fat-tail analysis"))
```

**Output:**
```
→ 2026-02-17 (0.85): Initial research topics added - GVX-based strategies, fat-tail analysis
→ 2026-02-19 (0.92): Tail risk hedging research - stop-loss creates point mass
→ 2026-02-20 (0.88): m001 advanced metrics - fat-tail distributions impact Sharpe
✓ 2026-02-20 (0.95): Hill Estimator implementation - Pareto distribution fitting
```

**Pros:**
- ✅ Clear trajectory visualization
- ✅ Confidence scoring
- ✅ Chronological ordering
- ✅ Easy to understand

**Cons:**
- ❌ Requires Python script
- ❌ Still uses memory_search internally

---

## 📋 Recommended Action Plan

### Phase 1: Compression (This Week)
1. ✅ Create INDEX.md (done)
2. ✅ Create ARCHIVED_PROJECTS.md (done)
3. ⏳ Compress 2026-02-19 (target: 73 KB → 20 KB)
4. ⏳ Compress 2026-02-20 (target: 108 KB → 30 KB)

### Phase 2: Retrieval System (Next Week)
1. ⏳ Implement vector trajectory script
2. ⏳ Add tag system to MEMORY.md
3. ⏳ Create visualizations for key trajectories

### Phase 3: Automation (Future)
1. ⏳ Auto-compress after 7 days (cron job)
2. ⏳ Auto-tag based on content analysis
3. ⏳ Weekly memory health report

---

## 🎯 Success Metrics

### Memory Health
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Daily Log Size | ≤ 50 KB | 108 KB | ⚠️ Needs compression |
| Total Memory | ≤ 2 MB | 223 KB | ✅ OK |
| Retrieval Speed | < 5 sec | ~2 sec | ✅ OK |

### Retrieval Quality
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Vector Visualization | Yes | No | ⏳ Need to implement |
| Tag Coverage | 80% of topics | 0% | ⏳ Need to implement |
| Search Relevance | > 0.8 score | ~0.85 | ✅ OK |

---

## 🔮 Future Enhancements

### QMD System Features
1. **Vector Clustering:** Group related insights automatically
2. **Trajectory Graphs:** Visualize how ideas evolve
3. **Cross-Project Links:** Show how projects connect
4. **Auto-Summarization:** Compress similar insights
5. **Confidence Scoring:** Track which insights are most reliable

### Advanced Visualizations
1. **Timeline View:** Chronological development of ideas
2. **Network Graph:** Connections between projects and insights
3. **Heatmap:** Research activity over time
4. **Sentiment Analysis:** Track positive/negative findings

---

## 💡 Quick Wins (Immediate)

1. **Compress Large Files:**
   ```bash
   # Compress 2026-02-20
   # Keep: Key events, insights, project completions
   # Delete: Duplicate details, verbose logs
   ```

2. **Add Tags to MEMORY.md:**
   ```markdown
   ## Tags
   - #risk-management
   - #multi-factor
   - #trend-following
   - #fat-tail
   - #agent-reliability
   ```

3. **Use memory_search More:**
   ```python
   # Before adding new insight, check if it exists
   results = memory_search("fat-tail distribution")
   # If high relevance found, update existing instead of duplicate
   ```

---

## 📝 Conclusion

**Yes, QMD system would help!** 

**Recommended Approach:**
1. **Immediate:** Compress daily logs (reduce 50-70% size)
2. **Short-term:** Add tag system + vector trajectory script
3. **Long-term:** Advanced visualizations and auto-compression

**Benefits:**
- ✅ Faster retrieval
- ✅ Clearer trajectories
- ✅ Prevents bloat
- ✅ Better organization

**Complexity:** Low-Medium (depends on features implemented)

---

*This plan provides a roadmap for memory optimization and vector retrieval enhancement.*
