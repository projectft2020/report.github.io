#!/usr/bin/env python3
"""
Score Research Report

Evaluate a single research report across quality dimensions.
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime, timezone

DEFAULT_PARAMS = Path(__file__).parent.parent / "references" / "scoring_params.json"

# Keywords indicating technical depth
DEPTH_KEYWORDS = [
    "公式", "formula", "proof", "證明", "theorem", "定理",
    "algorithm", "算法", "complexity", "複雜度", "optimization", "優化",
    "math", "數學", "statistical", "統計", "analysis", "分析"
]

# Keywords indicating completeness
COMPLETENESS_KEYWORDS = [
    "要求", "requirement", "全部", "all", "完整", "comprehensive",
    "覆蓋", "coverage", "詳細", "detailed", "具體", "specific"
]

# Keywords indicating innovation
INNOVATION_KEYWORDS = [
    "新", "new", "novel", "首個", "first", "創新", "innovation",
    "貢獻", "contribution", "突破", "breakthrough", "改進", "improvement"
]

# Keywords indicating applicability
APPLICABILITY_KEYWORDS = [
    "應用", "application", "實際", "practical", "場景", "scenario",
    "部署", "deployment", "實現", "implementation", "可用", "usable"
]

def load_params(params_path=None):
    """Load scoring parameters."""
    if params_path is None:
        params_path = DEFAULT_PARAMS

    try:
        with open(params_path, "r") as f:
            return json.load(f)
    except:
        # Return default if file not found
        return {
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

def evaluate_depth(content):
    """Evaluate technical depth (0-10)."""
    if not content:
        return 0

    score = 3  # Base score for having content

    # Check for formulas/equations
    formula_matches = len(re.findall(r'\$\$.*?\$\$|\\\[.*?\\\]|\\\\\[[^\\\]]*?\\\\\]', content))
    if formula_matches > 0:
        score += 1
    if formula_matches > 3:
        score += 1
    if formula_matches > 7:
        score += 1

    # Check for depth keywords
    keyword_count = sum(1 for kw in DEPTH_KEYWORDS if kw in content.lower())
    if keyword_count > 3:
        score += 1
    if keyword_count > 7:
        score += 1
    if keyword_count > 12:
        score += 1

    # Check content length (longer = more detail)
    if len(content) > 5000:
        score += 1
    if len(content) > 10000:
        score += 1

    return min(score, 10)

def evaluate_completeness(content):
    """Evaluate completeness (0-10)."""
    if not content:
        return 0

    score = 3  # Base score

    # Check for completeness keywords
    keyword_count = sum(1 for kw in COMPLETENESS_KEYWORDS if kw in content)
    if keyword_count > 2:
        score += 1
    if keyword_count > 5:
        score += 1
    if keyword_count > 8:
        score += 1

    # Check for structured sections
    sections = len(re.findall(r'^#+\s*\w+', content, re.MULTILINE))
    if sections >= 5:
        score += 1
    if sections >= 8:
        score += 1
    if sections >= 12:
        score += 1

    # Check for lists (indicates comprehensive coverage)
    lists = len(re.findall(r'^\s*[-*]\s+', content, re.MULTILINE))
    if lists >= 3:
        score += 1
    if lists >= 6:
        score += 1

    return min(score, 10)

def evaluate_innovation(content):
    """Evaluate innovation/novelty (0-10)."""
    if not content:
        return 0

    score = 3  # Base score

    # Check for innovation keywords
    keyword_count = sum(1 for kw in INNOVATION_KEYWORDS if kw in content)
    if keyword_count > 1:
        score += 1
    if keyword_count > 3:
        score += 1
    if keyword_count > 5:
        score += 1

    # Check for first-time/unique claims
    if "首個" in content or "first" in content.lower():
        score += 2
    if "新" in content and ("方法" in content or "algorithm" in content.lower()):
        score += 1

    # Check for comparison with existing methods
    if "改進" in content or "improvement" in content.lower():
        score += 1
    if "優於" in content or "better" in content.lower() and "existing" in content.lower():
        score += 2

    return min(score, 10)

def evaluate_applicability(content):
    """Evaluate practical applicability (0-10)."""
    if not content:
        return 0

    score = 3  # Base score

    # Check for application keywords
    keyword_count = sum(1 for kw in APPLICABILITY_KEYWORDS if kw in content)
    if keyword_count > 2:
        score += 1
    if keyword_count > 4:
        score += 1
    if keyword_count > 6:
        score += 1

    # Check for specific applications mentioned
    applications = len(re.findall(r'應用|application|實際|practical', content, re.IGNORECASE))
    if applications >= 2:
        score += 1
    if applications >= 4:
        score += 1

    # Check for implementation discussion
    if "實現" in content or "implementation" in content.lower():
        score += 1
    if "部署" in content or "deployment" in content.lower():
        score += 1

    return min(score, 10)

def calculate_overall(scores, weights):
    """Calculate overall score with weights."""
    overall = (
        scores["depth"] * weights["depth"] +
        scores["completeness"] * weights["completeness"] +
        scores["innovation"] * weights["innovation"] +
        scores["applicability"] * weights["applicability"]
    )
    return round(overall, 2)

def get_quality_level(overall_score, thresholds):
    """Determine quality level from score."""
    if overall_score >= thresholds["high"]:
        return "High Quality"
    elif overall_score >= thresholds["good"]:
        return "Good Quality"
    elif overall_score >= thresholds["moderate"]:
        return "Moderate Quality"
    else:
        return "Low Quality"

def generate_notes(content, scores):
    """Generate evaluation notes."""
    notes = []

    if scores["depth"] >= 7:
        notes.append("Deep technical analysis with comprehensive detail")
    elif scores["depth"] >= 4:
        notes.append("Moderate technical detail")
    else:
        notes.append("Limited technical depth")

    if scores["completeness"] >= 7:
        notes.append("Comprehensive coverage of requirements")
    elif scores["completeness"] >= 4:
        notes.append("Good coverage with minor gaps")
    else:
        notes.append("Significant gaps in coverage")

    if scores["innovation"] >= 7:
        notes.append("Novel approach with significant contributions")
    elif scores["innovation"] >= 4:
        notes.append("Minor improvements to existing methods")
    else:
        notes.append("Limited novelty, mostly known methods")

    if scores["applicability"] >= 7:
        notes.append("Clear practical applications")
    elif scores["applicability"] >= 4:
        notes.append("Some applications mentioned")
    else:
        notes.append("Theoretical focus, limited practical use")

    return notes

def extract_task_id(research_file):
    """Extract task ID from research file path."""
    # Pattern: scout-XXXXX-research.md or task-XXXXX-research.md
    match = re.search(r'(scout|task)-(\d+)', research_file)
    if match:
        return match.group(0)
    return Path(research_file).stem

def score_research(research_file, params=None, verbose=False):
    """Score a single research report.

    Returns:
        Score object with all dimensions
    """
    research_path = Path(research_file)

    if not research_path.exists():
        print(f"❌ 研究文件不存在: {research_file}")
        return None

    # Load content
    try:
        with open(research_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"❌ 讀取研究文件失敗: {e}")
        return None

    # Load parameters
    if params is None:
        params = load_params()
    else:
        params = params

    # Evaluate dimensions
    scores = {
        "depth": evaluate_depth(content),
        "completeness": evaluate_completeness(content),
        "innovation": evaluate_innovation(content),
        "applicability": evaluate_applicability(content)
    }

    # Calculate overall
    weights = params.get("weights", {})
    thresholds = params.get("thresholds", {})
    overall = calculate_overall(scores, weights)
    quality_level = get_quality_level(overall, thresholds)

    # Generate notes
    notes = generate_notes(content, scores)

    if verbose:
        print("=" * 60)
        print(f"📊 評分研究報告: {research_path.name}")
        print("=" * 60)
        print()
        print(f"深度 (Depth):        {scores['depth']}/10")
        print(f"完整性 (Completeness): {scores['completeness']}/10")
        print(f"創新性 (Innovation):  {scores['innovation']}/10")
        print(f"可應用性 (Applicability): {scores['applicability']}/10")
        print()
        print(f"總分 (Overall):     {overall}/10")
        print(f"品質等級: {quality_level}")
        print()
        print("評分說明:")
        for note in notes:
            print(f"  - {note}")

    # Prepare score object
    task_id = extract_task_id(research_file)
    score_obj = {
        "research_file": str(research_path),
        "task_id": task_id,
        "scores": scores,
        "overall": overall,
        "quality_level": quality_level,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "notes": notes
    }

    # Save to .score file
    score_file = research_path.parent / f"{research_path.stem}.score"
    with open(score_file, "w", encoding="utf-8") as f:
        json.dump(score_obj, f, indent=2, ensure_ascii=False)

    print(f"✅ 分數已保存: {score_file}")

    return score_obj

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python3 score_research.py <research-file> [--verbose]")
        print()
        print("參數:")
        print("  research-file  研究報告文件路徑")
        print("  --verbose     顯示詳細評分")
        sys.exit(1)

    research_file = sys.argv[1]
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    score_research(research_file, verbose=verbose)
