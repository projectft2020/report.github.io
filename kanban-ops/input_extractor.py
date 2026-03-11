#!/usr/bin/env python3
"""
Input File Extractor - Semantic compression for sub-agent tasks

Reduces input file size by 80-90% by extracting only key information:
- Title and metadata
- Key formulas
- Summary tables (first 5 rows)
- Function signatures (not full implementations)
- Conclusions and summaries

Usage:
    from input_extractor import extract_key_info
    result = extract_key_info("path/to/file.md")

Author: System Optimization Team
Date: 2026-02-23
"""

import re
from pathlib import Path
from typing import Dict, List, Any
import json


def extract_key_info(file_path: str, verbose: bool = True) -> Dict[str, Any]:
    """
    Extract key semantic information from Markdown file

    Args:
        file_path: Path to the input file
        verbose: Print compression statistics

    Returns:
        Dictionary with extracted key information
    """
    path = Path(file_path)
    if not path.exists():
        if verbose:
            print(f"❌ File not found: {file_path}")
        return {"error": "File not found", "path": file_path}

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_size = len(content)

    # Extract key information
    extracted = {
        "source_file": str(path.name),
        "title": _extract_title(content),
        "key_formulas": _extract_formulas(content),
        "summary_tables": _extract_tables(content, max_rows=5),
        "code_signatures": _extract_code_signatures(content),
        "conclusions": _extract_conclusions(content),
        "key_points": _extract_key_points(content),
        "metadata": _extract_metadata(content),
    }

    compressed_size = len(str(extracted))
    compression_ratio = (1 - compressed_size / original_size) * 100

    if verbose:
        print(f"✅ {path.name}: {original_size//1024}KB → {compressed_size//1024}KB "
              f"(節省 {compression_ratio:.1f}%)")

    # Add size metadata to extracted dict
    extracted['original_size'] = original_size
    extracted['compressed_size'] = compressed_size
    extracted['compression_ratio'] = compression_ratio

    return extracted


def _extract_title(content: str) -> str:
    """Extract the main title from markdown"""
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    return match.group(1).strip() if match else "Untitled"


def _extract_formulas(content: str, max_count: int = 10) -> List[str]:
    """Extract mathematical formulas ($$...$$ or $...$)"""
    # Block formulas
    block_formulas = re.findall(r'\$\$([^$]+)\$\$', content, re.DOTALL)
    # Inline formulas
    inline_formulas = re.findall(r'(?<!\$)\$([^$]+)\$(?!\$)', content)

    all_formulas = [f.strip() for f in block_formulas + inline_formulas if f.strip()]
    return all_formulas[:max_count]


def _extract_tables(content: str, max_rows: int = 5, max_tables: int = 3) -> List[str]:
    """Extract tables, keeping only first max_rows rows"""
    tables = []
    current_table = []

    for line in content.split('\n'):
        stripped = line.strip()
        if '|' in stripped and not stripped.startswith('```'):
            current_table.append(stripped)
        elif current_table and len(current_table) > 2:  # Need at least header + separator + 1 row
            tables.append('\n'.join(current_table[:max_rows + 2]))  # +2 for header and separator
            current_table = []
        elif current_table:
            current_table = []

    return tables[:max_tables]


def _extract_code_signatures(content: str, max_count: int = 20) -> List[str]:
    """Extract function/class signatures (not full implementations)"""

    # Extract from code blocks
    signatures = []

    # Python signatures
    python_patterns = [
        r'(?:^|\n)def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\):',
        r'(?:^|\n)class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:\([^)]*\))?:',
    ]

    for pattern in python_patterns:
        matches = re.findall(pattern, content)
        signatures.extend([f"def {m}()" for m in matches])

    # JavaScript/TypeScript signatures
    js_patterns = [
        r'(?:^|\n)(?:function\s+|const\s+[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*(?:async\s+)?)([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)',
        r'(?:^|\n)class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:extends\s+[a-zA-Z_][a-zA-Z0-9_]*)?',
    ]

    for pattern in js_patterns:
        matches = re.findall(pattern, content)
        signatures.extend([m for m in matches])

    # Remove duplicates and limit
    unique_sigs = list(dict.fromkeys(signatures))  # Preserve order
    return unique_sigs[:max_count]


def _extract_conclusions(content: str, max_length: int = 500) -> str:
    """Extract conclusion/summary section"""
    # Common section headers
    section_patterns = [
        r'##+\s*(?:結論|總結|結尾|結論與展望|Conclusion|Summary|Conclusions)\s*\n+(.+?)(?=\n##|\Z)',
        r'###+\s*(?:結論|總結|結尾|Conclusion|Summary)\s*\n+(.+?)(?=\n###|\n##|\Z)',
    ]

    for pattern in section_patterns:
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            conclusion = match.group(1).strip()
            # Remove markdown formatting
            conclusion = re.sub(r'[#*`\[\]]', '', conclusion)
            return conclusion[:max_length] + '...' if len(conclusion) > max_length else conclusion

    return ""


def _extract_key_points(content: str, max_points: int = 10) -> List[str]:
    """Extract bullet points and numbered lists"""
    points = []

    # Bullet points
    bullets = re.findall(r'^[\s]*[-*+]\s+(.+)$', content, re.MULTILINE)
    points.extend(bullets)

    # Numbered lists
    numbered = re.findall(r'^[\s]*\d+[.)\s]+(.+)$', content, re.MULTILINE)
    points.extend(numbered)

    # Remove duplicates and limit
    unique_points = [p.strip() for p in points if p.strip()]
    unique_points = list(dict.fromkeys(unique_points))

    return unique_points[:max_points]


def _extract_metadata(content: str) -> Dict[str, str]:
    """Extract metadata like authors, dates, tags"""
    metadata = {}

    # Frontmatter YAML
    frontmatter = re.search(r'^---\n(.+?)\n---', content, re.DOTALL)
    if frontmatter:
        yaml_content = frontmatter.group(1)
        for match in re.finditer(r'([a-zA-Z_][a-zA-Z0-9_]*):\s*(.+)', yaml_content):
            key = match.group(1).strip()
            value = match.group(2).strip().strip('"\'')
            metadata[key] = value

    # Common metadata patterns
    date_match = re.search(r'(?:日期|Date|Updated):\s*([0-9-]+)', content, re.IGNORECASE)
    if date_match:
        metadata['date'] = date_match.group(1)

    author_match = re.search(r'(?:作者|Author|By):\s*(.+?)(?:\n|$)', content, re.IGNORECASE)
    if author_match:
        metadata['author'] = author_match.group(1).strip()

    return metadata


def extract_multiple_files(file_paths: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Extract key info from multiple files

    Args:
        file_paths: List of file paths

    Returns:
        Dictionary mapping file names to extracted info
    """
    results = {}

    print(f"\n📦 Processing {len(file_paths)} files...")

    for file_path in file_paths:
        path = Path(file_path)
        if path.exists():
            results[path.name] = extract_key_info(str(path))
        else:
            print(f"⚠️  File not found: {file_path}")

    total_original = sum(len(Path(f).read_text(encoding='utf-8')) if Path(f).exists() else 0 for f in file_paths)
    total_compressed = sum(len(str(r)) for r in results.values())

    if total_original > 0:
        print(f"\n📊 Total: {total_original//1024}KB → {total_compressed//1024}KB "
              f"(節省 {(1-total_compressed/total_original)*100:.1f}%)")

    return results


# Test function
if __name__ == '__main__':
    # Test with DHRI file
    dhri_file = "/Users/charlie/.openclaw/workspace/DHRI-daily-hedge-ratio.md"

    if Path(dhri_file).exists():
        print("="*60)
        print("🧪 Testing input extractor on DHRI file")
        print("="*60)

        result = extract_key_info(dhri_file)

        print("\n📋 Extracted Information:")
        print(f"Title: {result['title']}")
        print(f"Formulas: {len(result['key_formulas'])}")
        print(f"Tables: {len(result['summary_tables'])}")
        print(f"Code Signatures: {len(result['code_signatures'])}")
        print(f"Key Points: {len(result['key_points'])}")

        if result['conclusions']:
            print(f"\n📝 Conclusion Preview:")
            print(result['conclusions'])

        if result['key_formulas']:
            print(f"\n🔢 Sample Formulas:")
            for formula in result['key_formulas'][:3]:
                print(f"  - {formula}")

        print("\n" + "="*60)
    else:
        print(f"⚠️  Test file not found: {dhri_file}")
        print(f"   No test performed")
