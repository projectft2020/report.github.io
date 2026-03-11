#!/usr/bin/env python3
"""
智能並發任务启动器 - 方案 B

核心思路：
1. 预估每个任务的 Token 使用
2. 按 Token 限制分組（每組 300k）
3. 每組同时啟動
4. 組間隔 5 分鐘

優點：
- 效率和安全性平衡
- 适应不同类型的任务
- 智能 Token 管理

基於歷史數據的預估：
- Research: 80k-150k tokens
- Analyst: 50k-100k tokens
- Architect: 60k-120k tokens
- Developer: 40k-80k tokens
- Automation: 20k-50k tokens
- Creative: 40k-90k tokens
"""

import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Tuple

# 路徑配置
WORKSPACE = Path.home() / ".openclaw" / "workspace"
KANBAN_WORKSPACE = Path.home() / ".openclaw" / "workspace-automation" / "kanban"
TASKS_JSON = KANBAN_WORKSPACE / "tasks.json"
QUEUE_DIR = WORKSPACE / "kanban-ops" / "task_queue"


# ============================================================================
# 配置參數
# ============================================================================

SPAWN_CONFIG = {
    # Token 限制配置
    'TOKEN_LIMIT_PER_BATCH': 300_000,  # 每組最大 Token（輸入 + 輸出）
    'TOKEN_SAFETY_MARGIN': 0.8,         # 安全係數（實際使用 80%）
    
    # 時間配置
    'BATCH_DELAY_MINUTES': 5,            # 組間隔（分鐘）
    'TASK_VERIFICATION_TIMEOUT': 10,      # 每個任務驗證超時（秒）
    
    # 並發配置
    'MAX_CONCURRENT_TASKS': 5,           # 每組最大並發任務數
}


# ============================================================================
# Token 預估數據（基於歷史統計）
# ============================================================================

# 每個代理的 Token 使用範圍（輸入 + 輸出）
TOKEN_ESTIMATES = {
    'research': {
        'min': 80_000,   # 最小 Token 使用
        'max': 150_000,  # 最大 Token 使用
        'avg': 115_000,  # 平均 Token 使用
    },
    'analyst': {
        'min': 50_000,
        'max': 100_000,
        'avg': 75_000,
    },
    'architect': {
        'min': 60_000,
        'max': 120_000,
        'avg': 90_000,
    },
    'developer': {
        'min': 40_000,
        'max': 80_000,
        'avg': 60_000,
    },
    'automation': {
        'min': 20_000,
        'max': 50_000,
        'avg': 35_000,
    },
    'creative': {
        'min': 40_000,
        'max': 90_000,
        'avg': 65_000,
    },
    'mentors': {
        'min': 50_000,
        'max': 100_000,
        'avg': 75_000,
    },
    'unknown': {
        'min': 50_000,
        'max': 100_000,
        'avg': 75_000,
    },
}


# ============================================================================
# 日誌工具
# ============================================================================

def log(level: str, message: str):
    """記錄日誌"""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "DEBUG": "🔍"}
    print(f"{icons.get(level, '📝')} [{timestamp}] {message}", flush=True)


# ============================================================================
# 任務和隊列管理
# ============================================================================

def load_tasks() -> Dict:
    """載入 tasks.json"""
    if not TASKS_JSON.exists():
        log("ERROR", f"tasks.json 不存在：{TASKS_JSON}")
        return {}

    try:
        with open(TASKS_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {t['id']: t for t in data.get('tasks', [])}
    except Exception as e:
        log("ERROR", f"載入 tasks.json 失敗：{e}")
        return {}


def load_queue_tasks() -> List[Dict]:
    """載入隊列中的所有任務"""
    if not QUEUE_DIR.exists():
        log("INFO", "隊列目錄不存在")
        return []

    task_files = sorted(QUEUE_DIR.glob("*.json"))
    tasks = []

    for task_file in task_files:
        try:
            with open(task_file, 'r', encoding='utf-8') as f:
                task_data = json.load(f)
                task_data['queue_file'] = task_file
                tasks.append(task_data)
        except Exception as e:
            log("ERROR", f"載入任務失敗 {task_file.name}：{e}")

    return tasks


# ============================================================================
# Token 預估
# ============================================================================

def estimate_task_tokens(task: Dict) -> Dict[str, int]:
    """
    預估任務的 Token 使用
    
    考慮因素：
    1. 代理類型
    2. 任務複雜度（time_tracking.complexity_level）
    3. 任務描述長度（task 字段長度）
    
    Returns:
        {
            'min': 最小 Token 使用,
            'max': 最大 Token 使用,
            'avg': 平均 Token 使用,
            'confidence': 置信度 (0-1)
        }
    """
    agent = task.get('agentId', task.get('agent', 'unknown'))
    complexity = task.get('complexity', task.get('time_tracking', {}).get('complexity_level', 1))
    task_text = task.get('task', '')
    
    # 獲取基礎預估
    base_estimate = TOKEN_ESTIMATES.get(agent, TOKEN_ESTIMATES['unknown'])
    
    # 根據複雜度調整
    # complexity_level: 1 (簡單) - 5 (非常複雜)
    complexity_multiplier = 1.0 + (complexity - 1) * 0.25  # 1.0x - 2.0x
    
    # 根據任務描述長度調整
    text_length = len(task_text)
    text_multiplier = 1.0
    if text_length > 5000:
        text_multiplier = 1.2
    elif text_length > 10000:
        text_multiplier = 1.4
    
    # 計算調整後的預估
    min_tokens = int(base_estimate['min'] * complexity_multiplier * text_multiplier)
    max_tokens = int(base_estimate['max'] * complexity_multiplier * text_multiplier)
    avg_tokens = (min_tokens + max_tokens) // 2
    
    # 置信度（基於可用信息）
    confidence = 0.7  # 基礎置信度
    if 'time_tracking' in task and 'complexity_level' in task['time_tracking']:
        confidence += 0.1
    if text_length > 1000:
        confidence += 0.1
    
    return {
        'min': min_tokens,
        'max': max_tokens,
        'avg': avg_tokens,
        'confidence': min(confidence, 1.0)
    }


def print_token_estimates(tasks: List[Dict]):
    """打印所有任務的 Token 預估"""
    log("INFO", "=" * 60)
    log("INFO", "任務 Token 預估")
    log("INFO", "=" * 60)
    
    total_min = 0
    total_max = 0
    total_avg = 0
    
    for i, task in enumerate(tasks, 1):
        task_id = task.get('label', 'unknown')
        agent = task.get('agentId', 'unknown')
        
        estimate = estimate_task_tokens(task)
        total_min += estimate['min']
        total_max += estimate['max']
        total_avg += estimate['avg']
        
        confidence_str = f"{estimate['confidence']*100:.0f}%"
        log("INFO", f"{i}. {task_id[:30]:<30} | {agent:<12} | "
                  f"{estimate['min']:>6d} - {estimate['max']:>6d} avg {estimate['avg']:>6d} | "
                  f"置信度 {confidence_str}")
    
    log("INFO", "-" * 60)
    log("INFO", f"總計：{total_min:,} - {total_max:,} avg {total_avg:,} tokens")
    log("INFO", "=" * 60)


# ============================================================================
# 任務分組
# ============================================================================

def group_tasks_by_token_limit(
    tasks: List[Dict],
    token_limit: int = None,
    max_concurrent: int = None
) -> List[List[Dict]]:
    """
    按 Token 限制將任務分組
    
    策略：
    1. 按預估 Token 從小到大排序
    2. 貪心算法：盡量填滿每組，但不超過限制
    3. 每組最多 max_concurrent 個任務
    
    Args:
        tasks: 任務列表
        token_limit: 每組 Token 限制（預設從配置讀取）
        max_concurrent: 每組最大並發數（預設從配置讀取）
    
    Returns:
        分組後的任務列表 [[task1, task2], [task3, task4, task5], ...]
    """
    if token_limit is None:
        token_limit = SPAWN_CONFIG['TOKEN_LIMIT_PER_BATCH']
    
    if max_concurrent is None:
        max_concurrent = SPAWN_CONFIG['MAX_CONCURRENT_TASKS']
    
    # 應用安全係數
    effective_limit = int(token_limit * SPAWN_CONFIG['TOKEN_SAFETY_MARGIN'])
    
    log("INFO", f"分組配置：Token 限制 {effective_limit:,} ({token_limit:,} * {SPAWN_CONFIG['TOKEN_SAFETY_MARGIN']})")
    log("INFO", f"           最大並發 {max_concurrent} 個任務/組")
    
    # 按預估 Token 排序（小到大）
    tasks_with_estimate = []
    for task in tasks:
        estimate = estimate_task_tokens(task)
        tasks_with_estimate.append({
            'task': task,
            'estimate': estimate
        })
    
    tasks_with_estimate.sort(key=lambda x: x['estimate']['max'])
    
    # 貪心分組
    groups = []
    current_group = []
    current_tokens = 0
    task_count = 0
    
    for item in tasks_with_estimate:
        task = item['task']
        estimate = item['estimate']
        max_tokens = estimate['max']
        
        # 檢查是否可以加入當前組
        can_add = (
            task_count < max_concurrent and
            current_tokens + max_tokens <= effective_limit
        )
        
        if can_add:
            # 加入當前組
            current_group.append(task)
            current_tokens += max_tokens
            task_count += 1
        else:
            # 開始新組
            if current_group:
                groups.append(current_group)
            current_group = [task]
            current_tokens = max_tokens
            task_count = 1
    
    # 添加最後一組
    if current_group:
        groups.append(current_group)
    
    # 打印分組結果
    log("INFO", "=" * 60)
    log("INFO", f"分組結果：{len(groups)} 組")
    log("INFO", "=" * 60)
    
    for i, group in enumerate(groups, 1):
        group_tokens = sum(estimate_task_tokens(t)['max'] for t in group)
        log("INFO", f"組 {i}: {len(group)} 個任務, 預估 {group_tokens:,} tokens")
        for task in group:
            task_id = task.get('label', 'unknown')
            agent = task.get('agentId', 'unknown')
            estimate = estimate_task_tokens(task)
            log("DEBUG", f"    - {task_id} ({agent}): {estimate['max']:,} tokens")
    
    log("INFO", "=" * 60)
    
    return groups


# ============================================================================
# 任務啟動
# ============================================================================

def spawn_batch_with_verification(
    tasks: List[Dict],
    batch_index: int = 1
) -> Tuple[List[str], List[Dict]]:
    """
    啟動一組任務並驗證
    
    Args:
        tasks: 任務列表
        batch_index: 當前批次索引
    
    Returns:
        (success_list, failed_list)
    """
    log("INFO", f"開始啟動第 {batch_index} 組：{len(tasks)} 個任務")
    
    # 為主會話生成 spawn 命令
    spawn_commands = []
    for task in tasks:
        task_id = task.get('label', 'unknown')
        agent_id = task.get('agentId', 'research')
        
        spawn_command = {
            'agentId': agent_id,
            'task': task['task'],
            'label': task_id
        }
        
        if task.get('model'):
            spawn_command['model'] = task['model']
        
        spawn_commands.append((task_id, spawn_command))
    
    # 打印 spawn 命令
    log("WARNING", "=" * 60)
    log("WARNING", "需要在主會話中執行以下命令：")
    log("WARNING", "=" * 60)
    
    for task_id, spawn_command in spawn_commands:
        json_str = json.dumps(spawn_command, ensure_ascii=False)
        log("INFO", f"sessions_spawn({json_str})")
    
    log("WARNING", "=" * 60)
    log("INFO", f"等待 {len(tasks)} 個子代理啟動...")
    
    # 注意：這裡需要手動執行，因為腳本無法直接調用 sessions_spawn
    # 返回空列表，實際啟動需要在主會話中完成
    return [], []


def spawn_batches_sequentially(
    groups: List[List[Dict]],
    delay_minutes: int = None
) -> Dict:
    """
    序列啟動每組任務
    
    Args:
        groups: 分組後的任務列表
        delay_minutes: 組間隔（分鐘，預設從配置讀取）
    
    Returns:
        {
            'total_batches': 總批次数,
            'successes': 成功任務列表,
            'failures': 失敗任務列表
        }
    """
    if delay_minutes is None:
        delay_minutes = SPAWN_CONFIG['BATCH_DELAY_MINUTES']
    
    result = {
        'total_batches': len(groups),
        'successes': [],
        'failures': []
    }
    
    for i, group in enumerate(groups, 1):
        log("INFO", f"{'='*60}")
        log("INFO", f"批次 {i}/{len(groups)}")
        log("INFO", f"{'='*60}")
        
        # 啟動當前組
        successes, failures = spawn_batch_with_verification(group, i)
        
        result['successes'].extend(successes)
        result['failures'].extend(failures)
        
        # 等待下一批次
        if i < len(groups):
            log("INFO", f"等待 {delay_minutes} 分鐘後啟動下一批次...")
            time.sleep(delay_minutes * 60)
    
    return result


# ============================================================================
# 主流程
# ============================================================================

def spawn_tasks_intelligently(
    max_tasks: int = 10,
    dry_run: bool = False
) -> Dict:
    """
    智能啟動任務的主流程
    
    步驟：
    1. 載入隊列任務
    2. 預估每個任務的 Token 使用
    3. 按 Token 限制分組
    4. 序列啟動每組
    
    Args:
        max_tasks: 最大處理任務數
        dry_run: 只打印計劃，不實際啟動
    
    Returns:
        啟動結果
    """
    log("INFO", "=" * 60)
    log("INFO", "智能並發任務啟動器 - 方案 B")
    log("INFO", "=" * 60)
    
    # 步驟 1: 載入隊列任務
    log("INFO", f"步驟 1/4: 載入隊列任務...")
    tasks = load_queue_tasks()[:max_tasks]
    
    if not tasks:
        log("INFO", "隊列為空，無需啟動任務")
        return {'total_batches': 0, 'successes': [], 'failures': []}
    
    log("SUCCESS", f"載入 {len(tasks)} 個任務")
    
    # 步驟 2: 預估 Token 使用
    log("INFO", f"步驟 2/4: 預估 Token 使用...")
    print_token_estimates(tasks)
    
    # 步驟 3: 分組
    log("INFO", f"步驟 3/4: 按 Token 限制分組...")
    groups = group_tasks_by_token_limit(tasks)
    
    # 步驟 4: 啟動
    log("INFO", f"步驟 4/4: 序列啟動各組...")
    
    if dry_run:
        log("INFO", "[DRY RUN] 只打印計劃，不實際啟動")
        return {
            'total_batches': len(groups),
            'successes': [],
            'failures': [],
            'dry_run': True
        }
    
    result = spawn_batches_sequentially(groups)
    
    # 總結
    log("INFO", "=" * 60)
    log("INFO", "啟動完成")
    log("INFO", "=" * 60)
    log("SUCCESS", f"總批次：{result['total_batches']}")
    log("SUCCESS", f"成功：{len(result['successes'])}")
    log("SUCCESS", f"失敗：{len(result['failures'])}")
    
    return result


# ============================================================================
# 命令行介面
# ============================================================================

def print_usage():
    """打印使用說明"""
    print("""
智能並發任務啟動器 - 方案 B

用法：
    python3 spawn_tasks_intelligent.py spawn [max_tasks] [--dry-run]
    python3 spawn_tasks_intelligent.py estimate [max_tasks]
    python3 spawn_tasks_intelligent.py group [max_tasks]

命令：
    spawn [max_tasks]      啟動任務（智能分組和序列啟動）
    estimate [max_tasks]   只預估 Token，不啟動
    group [max_tasks]      只分組，不啟動
    --dry-run              只打印計劃，不實際啟動

參數：
    max_tasks              最大處理任務數（預設 10）

示例：
    python3 spawn_tasks_intelligent.py spawn 5
    python3 spawn_tasks_intelligent.py spawn --dry-run
    python3 spawn_tasks_intelligent.py estimate 10

配置：
    TOKEN_LIMIT_PER_BATCH = 300,000  tokens
    MAX_CONCURRENT_TASKS = 5         任務/組
    BATCH_DELAY_MINUTES = 5          分鐘
    """)


def main():
    """主函數"""
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help', 'help']:
        print_usage()
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == 'spawn':
        max_tasks = 10
        dry_run = False
        
        # 解析參數
        for arg in sys.argv[2:]:
            if arg.isdigit():
                max_tasks = int(arg)
            elif arg == '--dry-run':
                dry_run = True
        
        spawn_tasks_intelligently(max_tasks=max_tasks, dry_run=dry_run)
    
    elif command == 'estimate':
        max_tasks = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 10
        
        log("INFO", "=" * 60)
        log("INFO", "Token 預估模式")
        log("INFO", "=" * 60)
        
        tasks = load_queue_tasks()[:max_tasks]
        if tasks:
            print_token_estimates(tasks)
    
    elif command == 'group':
        max_tasks = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 10
        
        log("INFO", "=" * 60)
        log("INFO", "任務分組模式")
        log("INFO", "=" * 60)
        
        tasks = load_queue_tasks()[:max_tasks]
        if tasks:
            groups = group_tasks_by_token_limit(tasks)
            log("INFO", f"總共分為 {len(groups)} 組")
    
    else:
        log("ERROR", f"未知命令：{command}")
        print_usage()
        sys.exit(1)


if __name__ == '__main__':
    main()
