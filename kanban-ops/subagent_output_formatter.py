#!/usr/bin/env python3
"""
子代理輸出格式化腳本

為子代理提供標準化的輸出路徑和日誌路徑

使用方式：
    在任務任務消息中添加輸出路徑配置：

    TASK: 任務描述

    OUTPUT PATH: /Users/charlie/.openclaw/subagents/outputs/{task_id}.md
    LOG PATH: /Users/charlie/.openclaw/subagents/logs/{task_id}.log
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

# 路徑配置
SUBAGENTS_DIR = Path.home() / ".openclaw" / "subagents"
OUTPUTS_DIR = SUBAGENTS_DIR / "outputs"
LOGS_DIR = SUBAGENTS_DIR / "logs"


def ensure_dirs():
    """確保目錄存在"""
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


def get_output_path(task_id: str) -> Path:
    """獲取輸出路徑"""
    ensure_dirs()
    return OUTPUTS_DIR / f"{task_id}.md"


def get_log_path(task_id: str) -> Path:
    """獲取日誌路徑"""
    ensure_dirs()
    return LOGS_DIR / f"{task_id}.log"


def format_task_message(task_message: str, task_id: str, output_path: Optional[str] = None, log_path: Optional[str] = None) -> str:
    """
    格式化任務消息，添加輸出和日誌路徑

    Args:
        task_message: 原始任務消息
        task_id: 任務 ID
        output_path: 自定義輸出路徑（可選）
        log_path: 自定義日誌路徑（可選）

    Returns:
        格式化後的任務消息
    """
    # 如果沒有提供路徑，使用默認路徑
    if output_path is None:
        output_path = str(get_output_path(task_id))

    if log_path is None:
        log_path = str(get_log_path(task_id))

    # 檢查是否已經有 OUTPUT PATH
    if "OUTPUT PATH:" not in task_message:
        task_message += f"\n\nOUTPUT PATH: {output_path}"
    else:
        # 替換現有的 OUTPUT PATH
        import re
        task_message = re.sub(
            r'OUTPUT PATH: [^\n]+',
            f'OUTPUT PATH: {output_path}',
            task_message
        )

    # 添加日誌路徑
    if "LOG PATH:" not in task_message:
        task_message += f"\nLOG PATH: {log_path}"

    return task_message


def list_outputs(limit: int = 20) -> list:
    """
    列出最近的輸出文件

    Args:
        limit: 最多顯示多少個文件

    Returns:
        輸出文件列表
    """
    if not OUTPUTS_DIR.exists():
        return []

    output_files = sorted(
        OUTPUTS_DIR.glob("*.md"),
        key=lambda f: f.stat().st_mtime,
        reverse=True
    )

    return output_files[:limit]


def list_logs(limit: int = 20) -> list:
    """
    列出最近的日誌文件

    Args:
        limit: 最多顯示多少個文件

    Returns:
        日誌文件列表
    """
    if not LOGS_DIR.exists():
        return []

    log_files = sorted(
        LOGS_DIR.glob("*.log"),
        key=lambda f: f.stat().st_mtime,
        reverse=True
    )

    return log_files[:limit]


def get_task_info(task_id: str) -> Dict:
    """
    獲取任務信息（輸出文件和日誌文件）

    Args:
        task_id: 任務 ID

    Returns:
        任務信息字典
    """
    output_file = get_output_path(task_id)
    log_file = get_log_path(task_id)

    return {
        "task_id": task_id,
        "output_path": str(output_file) if output_file.exists() else None,
        "log_path": str(log_file) if log_file.exists() else None,
        "output_exists": output_file.exists(),
        "log_exists": log_file.exists(),
        "output_size": output_file.stat().st_size if output_file.exists() else 0,
        "log_size": log_file.stat().st_size if log_file.exists() else 0,
        "output_mtime": datetime.fromtimestamp(output_file.stat().st_mtime, timezone.utc).isoformat() if output_file.exists() else None,
        "log_mtime": datetime.fromtimestamp(log_file.stat().st_mtime, timezone.utc).isoformat() if log_file.exists() else None,
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='子代理輸出格式化腳本',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('command', nargs='?', choices=['format', 'list-outputs', 'list-logs', 'info'],
                        help='命令')

    parser.add_argument('--task-id', help='任務 ID')
    parser.add_argument('--task-message', help='任務消息')
    parser.add_argument('--limit', type=int, default=20,
                        help='最多顯示多少個文件')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == 'format':
        if not args.task_id or not args.task_message:
            print("❌ 請提供 --task-id 和 --task-message")
            return

        formatted = format_task_message(args.task_message, args.task_id)
        print("\n格式化後的任務消息：")
        print("=" * 60)
        print(formatted)
        print("=" * 60)

    elif args.command == 'list-outputs':
        output_files = list_outputs(args.limit)

        print(f"\n📄 最近的輸出文件（最多 {args.limit} 個）：\n")
        print("=" * 80)

        if not output_files:
            print("⚠️ 沒有輸出文件\n")
        else:
            for i, file in enumerate(output_files, 1):
                size = file.stat().st_size
                mtime = datetime.fromtimestamp(file.stat().st_mtime, timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                print(f"{i}. {file.name}")
                print(f"   大小：{size:,} bytes")
                print(f"   修改時間：{mtime}")
                print(f"   路徑：{file}")

        print("\n" + "=" * 80)

    elif args.command == 'list-logs':
        log_files = list_logs(args.limit)

        print(f"\n📋 最近的日誌文件（最多 {args.limit} 個）：\n")
        print("=" * 80)

        if not log_files:
            print("⚠️ 沒有日誌文件\n")
        else:
            for i, file in enumerate(log_files, 1):
                size = file.stat().st_size
                mtime = datetime.fromtimestamp(file.stat().st_mtime, timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                print(f"{i}. {file.name}")
                print(f"   大小：{size:,} bytes")
                print(f"   修改時間：{mtime}")
                print(f"   路徑：{file}")

        print("\n" + "=" * 80)

    elif args.command == 'info':
        if not args.task_id:
            print("❌ 請提供 --task-id")
            return

        info = get_task_info(args.task_id)

        print(f"\n📊 任務信息：{args.task_id}\n")
        print("=" * 60)
        print(f"輸出文件：{info['output_path'] or 'N/A'}")
        print(f"日誌文件：{info['log_path'] or 'N/A'}")
        print(f"輸出存在：{'是' if info['output_exists'] else '否'}")
        print(f"日誌存在：{'是' if info['log_exists'] else '否'}")

        if info['output_exists']:
            print(f"輸出大小：{info['output_size']:,} bytes")
            print(f"輸出修改時間：{info['output_mtime']}")

        if info['log_exists']:
            print(f"日誌大小：{info['log_size']:,} bytes")
            print(f"日誌修改時間：{info['log_mtime']}")

        print("\n" + "=" * 60)


if __name__ == '__main__':
    main()
