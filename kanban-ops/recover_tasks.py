#!/usr/bin/env python3
"""
獨立的任務恢復腳本
檢測並恢復假失敗任務
"""

import sys
from pathlib import Path

# 添加當前目錄到 path
sys.path.insert(0, str(Path(__file__).parent))

from timeout_handler import TimeoutHandler
import auto_recovery_extension

def main():
    tasks_json_path = '/Users/charlie/.openclaw/workspace/kanban/tasks.json'
    workspace_path = '/Users/charlie/.openclaw/workspace'
    
    # 創建 timeout handler
    handler = TimeoutHandler(tasks_json_path, workspace_path)
    
    # 生成並打印恢復報告
    report = auto_recovery_extension.generate_recovery_report(handler)
    print(report)

if __name__ == '__main__':
    main()
