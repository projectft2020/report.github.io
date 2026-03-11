#!/usr/bin/env python3
"""
自動恢復擴展模組
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple
from datetime import datetime
from pathlib import Path


@dataclass
class RecoveryAnalysis:
    """自動恢復分析結果"""
    task_id: str
    title: str
    original_status: str
    output_path: str
    output_exists: bool
    output_complete: bool
    output_size_bytes: int
    output_line_count: int
    should_recover: bool
    recovery_confidence: str
    recovery_reason: str


def _check_output_file(task, workspace_path) -> Tuple[bool, bool, str]:
    """
    檢查任務的輸出文件是否存在
    
    Returns:
        (output_exists, is_complete, output_path)
    """
    task_id = task['id']
    
    # 構建可能的輸出路徑
    kanban_dir = Path(workspace_path) / 'kanban'
    
    # 嘗試多種可能的路徑
    possible_paths = [
        kanban_dir / 'projects' / task_id / f"{task_id}.md",
        kanban_dir / 'projects' / task_id / 'output.md',
        kanban_dir / 'output' / f"{task_id}.md",
        Path(workspace_path) / f"{task_id}.md",
    ]
    
    for path in possible_paths:
        if path.exists():
            # 檢查文件是否完整（至少有一些內容）
            size = path.stat().st_size
            is_complete = size > 100  # 至少 100 字節
            return True, is_complete, str(path)
    
    return False, False, ''


def recover_failed_tasks_with_output(handler, min_output_size_bytes=1000, min_line_count=10):
    """檢測並恢復假失敗任務"""
    recoveries = []
    now = datetime.now()
    
    for task in handler.tasks:
        # 只檢查 failed 和 terminated 狀態
        if task.get('status') not in ['failed', 'terminated']:
            continue
        
        # 分析是否應該恢復
        analysis = _analyze_recovery(
            task,
            handler.workspace_path,
            min_output_size_bytes,
            min_line_count
        )
        
        if analysis.should_recover:
            # 自動恢復狀態
            _apply_recovery(task, analysis, now)
            recoveries.append(analysis)
    
    # 保存修改
    if recoveries:
        handler._save_tasks()
    
    return recoveries


def _analyze_recovery(task, workspace_path, min_output_size_bytes, min_line_count):
    """分析任務是否應該恢復"""
    task_id = task['id']
    title = task.get('title', 'Untitled')
    original_status = task['status']
    
    # 檢查輸出文件
    output_exists, is_complete, output_path = _check_output_file(task, workspace_path)
    
    # 獲取輸出文件詳情
    output_size = 0
    line_count = 0
    
    if output_exists and output_path and Path(output_path).exists():
        try:
            output_size = Path(output_path).stat().st_size
            with open(output_path, 'r', encoding='utf-8') as f:
                line_count = sum(1 for _ in f)
        except Exception:
            pass
    
    # 判斷是否應該恢復
    should_recover = False
    confidence = 'low'
    reason = ''
    
    if output_exists and is_complete:
        if output_size >= min_output_size_bytes and line_count >= min_line_count:
            should_recover = True
            confidence = 'high'
            reason = (
                f"Output file exists and is complete "
                f"({output_size} bytes, {line_count} lines). "
                f"Task likely completed but announce failed."
            )
        elif output_size >= min_output_size_bytes * 0.5:
            should_recover = True
            confidence = 'medium'
            reason = (
                f"Output file exists with substantial content "
                f"({output_size} bytes, {line_count} lines). "
                f"Task may have partially completed."
            )
        else:
            reason = (
                f"Output file exists but is small "
                f"({output_size} bytes, {line_count} lines). "
                f"Not recovering automatically."
            )
    else:
        reason = "No output file found or output is incomplete."
    
    return RecoveryAnalysis(
        task_id=task_id,
        title=title,
        original_status=original_status,
        output_path=output_path or 'N/A',
        output_exists=output_exists,
        output_complete=is_complete,
        output_size_bytes=output_size,
        output_line_count=line_count,
        should_recover=should_recover,
        recovery_confidence=confidence,
        recovery_reason=reason
    )


def _apply_recovery(task, analysis, timestamp):
    """應用恢復操作"""
    # 更新狀態為 completed
    task['status'] = 'completed'
    
    # 添加/更新 time_tracking
    if 'time_tracking' not in task:
        task['time_tracking'] = {}
    
    time_tracking = task['time_tracking']
    
    # 記錄自動恢復信息
    time_tracking['auto_recovered'] = True
    time_tracking['recovery_timestamp'] = timestamp.isoformat()
    time_tracking['original_status'] = analysis.original_status
    time_tracking['recovery_confidence'] = analysis.recovery_confidence
    time_tracking['recovery_note'] = (
        f"Auto-recovered from '{analysis.original_status}' status. "
        f"{analysis.recovery_reason} "
        f"Output: {analysis.output_path}"
    )
    
    # 如果還沒有完成時間，設置為恢復時間
    if 'completed_at' not in time_tracking:
        time_tracking['completed_at'] = timestamp.isoformat()


def generate_recovery_report(handler):
    """生成恢復報告"""
    recoveries = recover_failed_tasks_with_output(handler)
    
    if not recoveries:
        return (
            "=" * 70 + "\n"
            "✅ 無需恢復的任務\n"
            "=" * 70 + "\n"
            "所有失敗/終止的任務都確實沒有輸出文件。\n"
        )
    
    lines = [
        "=" * 70,
        f"🔄 自動恢復報告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 70,
        "",
        f"✅ 成功恢復 {len(recoveries)} 個任務",
        "",
    ]
    
    # 按置信度分組
    high_confidence = [r for r in recoveries if r.recovery_confidence == 'high']
    medium_confidence = [r for r in recoveries if r.recovery_confidence == 'medium']
    
    if high_confidence:
        lines.extend([
            "─" * 70,
            "🟢 高置信度恢復",
            "─" * 70,
            ""
        ])
        for r in high_confidence:
            lines.extend(_format_recovery(r))
    
    if medium_confidence:
        lines.extend([
            "─" * 70,
            "🟡 中等置信度恢復",
            "─" * 70,
            ""
        ])
        for r in medium_confidence:
            lines.extend(_format_recovery(r))
    
    lines.extend([
        "─" * 70,
        "📊 統計摘要",
        "─" * 70,
        f"總恢復數：{len(recoveries)}",
        f"高置信度：{len(high_confidence)}",
        f"中等置信度：{len(medium_confidence)}",
        "",
        "💡 建議：",
        "   • 高置信度恢復的任務可以直接使用",
        "   • 中等置信度恢復的任務建議人工審查輸出質量",
        "   • 所有恢復記錄都已保存在任務的 time_tracking.recovery_note 中",
        ""
    ])
    
    return "\n".join(lines)


def _format_recovery(recovery):
    """格式化單個恢復結果"""
    confidence_emoji = {
        'high': '🟢',
        'medium': '🟡',
        'low': '🔴'
    }
    
    lines = [
        f"{confidence_emoji[recovery.recovery_confidence]} {recovery.task_id}: {recovery.title}",
        f"   原始狀態：{recovery.original_status} → 已恢復為 completed",
        f"   輸出文件：{recovery.output_path}",
        f"   文件大小：{_format_bytes(recovery.output_size_bytes)}",
        f"   行數：{recovery.output_line_count:,}",
        f"   理由：{recovery.recovery_reason}",
        ""
    ]
    
    return lines


def _format_bytes(size_bytes):
    """格式化字節大小"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
