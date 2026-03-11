#!/usr/bin/env python3
"""
Input Compressor - Automatic input file compression for sub-agent tasks

This module provides functions to automatically compress input files for
sub-agent tasks using semantic extraction. It's designed to be integrated
into the spawn protocol for 100% automation.

Usage:
    from input_compressor import compress_task_inputs

    # Compress inputs for a task
    compressed = compress_task_inputs(task_data)

    # Build task message with compressed inputs
    task_message = build_task_message(task_data, compressed)

Author: System Optimization Team
Date: 2026-02-23
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add kanban-ops to path
sys.path.insert(0, str(Path(__file__).parent))
from input_extractor import extract_key_info


def compress_task_inputs(task: Dict[str, Any], workspace: Path = None) -> Dict[str, str]:
    """
    Compress all input files for a task using semantic extraction

    Args:
        task: Task data dictionary with 'input_paths' field
        workspace: Workspace root path (defaults to ~/.openclaw/workspace)

    Returns:
        Dictionary mapping original file paths to compressed content
    """
    if workspace is None:
        workspace = Path.home() / ".openclaw" / "workspace"

    input_paths = task.get('input_paths', [])

    if not input_paths:
        return {}

    compressed_inputs = {}
    total_original = 0
    total_compressed = 0

    for input_path in input_paths:
        # Resolve full path
        if not Path(input_path).is_absolute():
            full_path = workspace / input_path
        else:
            full_path = Path(input_path)

        if not full_path.exists():
            print(f"⚠️  Input file not found: {input_path}")
            compressed_inputs[input_path] = f"[File not found: {input_path}]"
            continue

        # Read original size
        original_size = len(full_path.read_text(encoding='utf-8'))
        total_original += original_size

        # Extract key info
        extracted = extract_key_info(str(full_path), verbose=False)

        # Format as compressed text
        compressed_text = _format_compressed_content(extracted)
        compressed_inputs[input_path] = compressed_text

        total_compressed += len(compressed_text)

    # Print summary
    if total_original > 0:
        compression_ratio = (1 - total_compressed / total_original) * 100
        print(f"📦 Compressed {len(input_paths)} input files: "
              f"{total_original//1024}KB → {total_compressed//1024}KB "
              f"(節省 {compression_ratio:.1f}%)")

    return compressed_inputs


def _format_compressed_content(extracted: Dict[str, Any]) -> str:
    """
    Format extracted data into a readable compressed format

    Args:
        extracted: Extracted data dictionary

    Returns:
        Formatted text string
    """
    if 'error' in extracted:
        return extracted.get('error', 'Unknown error')

    lines = []

    # Title
    if extracted.get('title'):
        lines.append(f"# {extracted['title']}\n")

    # Metadata
    metadata = extracted.get('metadata', {})
    if metadata:
        lines.append("## Metadata")
        for key, value in metadata.items():
            lines.append(f"- {key}: {value}")
        lines.append("")

    # Key formulas
    if extracted.get('key_formulas'):
        lines.append("## Key Formulas")
        for formula in extracted['key_formulas']:
            lines.append(f"- ${formula}$")
        lines.append("")

    # Summary tables
    if extracted.get('summary_tables'):
        lines.append("## Summary Tables (truncated)")
        for table in extracted['summary_tables']:
            lines.append(table)
            lines.append("")

    # Code signatures
    if extracted.get('code_signatures'):
        lines.append("## Code Signatures")
        for sig in extracted['code_signatures'][:15]:  # Limit to 15
            lines.append(f"- {sig}")
        lines.append("")

    # Key points
    if extracted.get('key_points'):
        lines.append("## Key Points")
        for point in extracted['key_points'][:10]:  # Limit to 10
            lines.append(f"- {point}")
        lines.append("")

    # Conclusions
    if extracted.get('conclusions'):
        lines.append("## Conclusion")
        lines.append(extracted['conclusions'])
        lines.append("")

    # Source reference
    if extracted.get('source_file'):
        lines.append(f"*Source: {extracted['source_file']} (compressed)*")

    return '\n'.join(lines)


def build_task_message_with_compressed_inputs(
    task: Dict[str, Any],
    compressed_inputs: Dict[str, str]
) -> str:
    """
    Build task message with compressed inputs

    Args:
        task: Task data dictionary
        compressed_inputs: Compressed input content mapping

    Returns:
        Task message string with INPUT FILES section
    """
    task_type = task.get('agent', 'research')

    # Base template
    task_message = f"""TASK: {task.get('title', '')}

CONTEXT:
"""

    # Add context notes
    if task.get('notes'):
        task_message += f"- {task['notes']}\n"

    # Add compressed inputs
    if compressed_inputs:
        task_message += "\nINPUT FILES (compressed for efficiency):\n"
        for path, content in compressed_inputs.items():
            task_message += f"\n--- {path} ---\n"
            task_message += content
            task_message += "\n--- END ---\n"

    # Add requirements
    task_message += f"\nREQUIREMENTS:\n"
    task_message += f"- {task.get('notes', 'Complete the task as specified')}\n"

    # Add output path
    task_message += f"\nOUTPUT PATH: /Users/charlie/.openclaw/workspace/{task.get('output_path', '')}\n"

    return task_message


def compress_and_build_message(task: Dict[str, Any], workspace: Path = None) -> str:
    """
    One-step function: compress inputs and build task message

    Args:
        task: Task data dictionary
        workspace: Workspace root path

    Returns:
        Complete task message with compressed inputs
    """
    # Step 1: Compress inputs
    compressed_inputs = compress_task_inputs(task, workspace)

    # Step 2: Build message
    return build_task_message_with_compressed_inputs(task, compressed_inputs)


# Test function
if __name__ == '__main__':
    # Test with a sample task
    sample_task = {
        'id': 'test001',
        'title': 'Test analysis task',
        'agent': 'analyst',
        'input_paths': [
            'DHRI-daily-hedge-ratio.md',
            'workspace-research/outputs/20260221-105056-s095.md'
        ],
        'output_path': 'kanban/projects/test/test-output.md',
        'notes': 'Analyze the hedge ratio indicators'
    }

    print("="*60)
    print("🧪 Testing input compressor")
    print("="*60)

    # Test compression
    compressed_inputs = compress_task_inputs(sample_task)

    # Build message
    message = build_task_message_with_compressed_inputs(sample_task, compressed_inputs)

    print("\n" + "="*60)
    print("📝 Generated Task Message:")
    print("="*60)
    print(message[:1000] + "..." if len(message) > 1000 else message)
