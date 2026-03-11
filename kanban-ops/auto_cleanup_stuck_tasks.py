#!/usr/bin/env python3
"""
自动清理卡住的任务

定期扫描并清理：
1. 卡在 'in_progress' 状态超过 2 小时的任务
2. 卡在 'spawning' 状态超过 5 分钟的任务

将它们回滚到 'pending' 状态，增加重试计数
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

TASKS_JSON = Path.home() / ".openclaw" / "workspace-automation" / "kanban" / "tasks.json"
LOG_FILE = Path.home() / ".openclaw" / "logs" / "stuck_tasks_cleanup.log"


def log(message):
    """记录日志"""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    log_line = f"[{timestamp}] {message}"
    print(log_line)
    
    # 写入日志文件
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_line + "\n")


def load_tasks():
    """载入任务"""
    if not TASKS_JSON.exists():
        return {}
    
    with open(TASKS_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return {t['id']: t for t in data.get('tasks', [])}


def save_tasks(tasks):
    """保存任务"""
    data = {"tasks": list(tasks.values())}
    with open(TASKS_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def cleanup_stuck_tasks():
    """清理卡住的任务"""
    log("开始扫描卡住的任务...")
    
    tasks = load_tasks()
    now = datetime.now(timezone.utc)
    
    # 阈值
    in_progress_threshold = now - timedelta(hours=2)   # 2 小时
    spawning_threshold = now - timedelta(minutes=5)     # 5 分钟
    
    cleaned = []
    
    for task_id, task in tasks.items():
        status = task.get('status')
        
        # 跳过非卡住状态
        if status not in ['in_progress', 'spawning']:
            continue
        
        # 获取最后更新时间
        updated_at = task.get('updated_at') or task.get('created_at')
        if not updated_at:
            continue
        
        try:
            # 解析时间
            update_time = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            
            # 检查是否超时
            is_stuck = False
            reason = ""
            
            if status == 'in_progress' and update_time < in_progress_threshold:
                is_stuck = True
                hours = (now - update_time).total_seconds() / 3600
                reason = f"卡在 in_progress 状态 {hours:.1f} 小时"
                
            elif status == 'spawning' and update_time < spawning_threshold:
                is_stuck = True
                minutes = (now - update_time).total_seconds() / 60
                reason = f"卡在 spawning 状态 {minutes:.1f} 分钟"
            
            if is_stuck:
                # 回滚状态
                old_status = status
                task['status'] = 'pending'
                task['updated_at'] = now.isoformat()
                task['retry_count'] = task.get('retry_count', 0) + 1
                task['last_cleanup'] = {
                    'at': now.isoformat(),
                    'reason': reason,
                    'old_status': old_status
                }
                
                cleaned.append({
                    'id': task_id,
                    'title': task.get('title', 'N/A')[:50],
                    'reason': reason
                })
                
                log(f"✅ 清理任务 {task_id}: {reason} → 回滚到 pending")
        
        except Exception as e:
            log(f"❌ 处理任务 {task_id} 时出错：{e}")
    
    # 保存更新
    if cleaned:
        save_tasks(tasks)
        log(f"✅ 共清理了 {len(cleaned)} 个卡住的任务")
        
        # 打印总结
        print("\n清理总结：")
        for item in cleaned:
            print(f"  - {item['id']}: {item['title']}")
            print(f"    原因：{item['reason']}")
    else:
        log("ℹ️  没有发现卡住的任务")
    
    return cleaned


if __name__ == '__main__':
    cleanup_stuck_tasks()
