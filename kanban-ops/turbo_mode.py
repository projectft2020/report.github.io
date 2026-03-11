#!/usr/bin/env python3
"""Turbo Mode 狀態管理"""

import json
import sys
from datetime import datetime
from pathlib import Path

TURBO_DIR = Path.home() / ".openclaw" / "workspace" / "kanban-ops"
STATUS_FILE = TURBO_DIR / "TURBO_STATUS.json"
LOG_FILE = TURBO_DIR / "TURBO_LOG.md"


def load_status():
    """載入 Turbo Mode 狀態"""
    if not STATUS_FILE.exists():
        return None
    with open(STATUS_FILE, 'r') as f:
        return json.load(f)


def save_status(status):
    """保存 Turbo Mode 狀態"""
    with open(STATUS_FILE, 'w') as f:
        json.dump(status, f, indent=2, ensure_ascii=False)


def status_command():
    """顯示當前狀態"""
    status = load_status()
    if not status:
        print("⚠️  Turbo Mode 未初始化")
        return

    active = status.get('active', False)

    if active:
        print("🚀 Turbo Mode: 運行中")
        print(f"   開始時間: {status.get('started_at', 'N/A')}")
        print(f"   預計結束: {status.get('estimated_end_at', 'N/A')}")
        print(f"   當前階段: {status.get('current_phase', 'N/A')}")

        # 計算剩餘時間
        try:
            end_time = datetime.fromisoformat(status.get('estimated_end_at', '').replace('Z', '+00:00'))
            remaining = end_time - datetime.now(end_time.tzinfo)
            hours, remainder = divmod(remaining.total_seconds(), 3600)
            minutes, _ = divmod(remainder, 60)
            print(f"   剩餘時間: {int(hours)} 小時 {int(minutes)} 分鐘")
        except:
            pass

        stats = status.get('stats', {})
        print(f"\n📊 統計:")
        print(f"   觸發任務: {stats.get('tasks_triggered', 0)}")
        print(f"   執行掃描: {stats.get('scans_performed', 0)}")
        print(f"   創建文檔: {stats.get('documents_created', 0)}")
        print(f"   遇到錯誤: {stats.get('errors_encountered', 0)}")
    else:
        print("💤 Turbo Mode: 未運行")
        if 'stopped_at' in status:
            print(f"   停止時間: {status['stopped_at']}")


def phases_command():
    """顯示所有階段"""
    status = load_status()
    if not status:
        return

    print("📋 Turbo Mode 階段:")
    for i, phase in enumerate(status.get('phases', []), 1):
        print(f"\n{i}. {phase['name']} ({phase['duration_minutes']} 分鐘)")
        print(f"   {phase['description']}")


def main():
    if len(sys.argv) < 2:
        status_command()
        return

    command = sys.argv[1].lower()

    if command == 'status':
        status_command()
    elif command == 'phases':
        phases_command()
    else:
        print(f"未知命令: {command}")
        print("用法: python3 turbo_mode.py [status|phases]")


if __name__ == '__main__':
    main()
