#!/usr/bin/env python3
"""
自動任務啟動器 - 心跳版本

在每次心跳時自動啟動 pending 任務：
1. 檢查並發限制（最多 5 個）
2. 找出可啟動的 pending 任務
3. 生成 spawn_commands.jsonl
4. 供主會話讀取並執行 sessions_spawn

P0 行動：集成 API 追蹤
P1 行動：集成背壓機制

使用方式：
    python3 kanban-ops/auto_spawn_heartbeat.py

集成到心跳：
    心跳時執行此腳本，讀取生成的 spawn_commands.jsonl 並執行
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Optional

# 導入背壓機制（P1 行動）
try:
    from backpressure import get_spawn_interval, check_backpressure
    BACKPRESSURE_AVAILABLE = True
except ImportError:
    BACKPRESSURE_AVAILABLE = False
    log = lambda level, msg: None  # Placeholder

# P2 行動：優先級規則引擎（通過 subprocess 調用）
PRIORITY_RULES_SCRIPT = Path.home() / ".openclaw" / "workspace" / "skills" / "priority-rule-engine" / "scripts" / "apply_rules.py"

# 多模型支持
try:
    from model_allocator import ModelAllocator
    MODEL_ALLOCATOR_AVAILABLE = True
except ImportError:
    MODEL_ALLOCATOR_AVAILABLE = False

# 成本優化支持
try:
    from cost_optimizer import CostOptimizer
    COST_OPTIMIZER_AVAILABLE = True
except ImportError:
    COST_OPTIMIZER_AVAILABLE = False

# 路徑配置
WORKSPACE = Path.home() / ".openclaw" / "workspace"
TASKS_JSON = WORKSPACE / "kanban" / "tasks.json"
SPAWN_COMMANDS_FILE = WORKSPACE / "kanban" / "spawn_commands.jsonl"
HEARTBEAT_LOG = WORKSPACE / "kanban-ops" / "heartbeat.log"
MODELS_JSON = WORKSPACE / "kanban-ops" / "models.json"
MAX_CONCURRENT = 3
SPAWN_INTERVAL = 65  # 每個任務啟動間隔（秒），避免觸發 API rate limit


def log(level, message):
    """記錄日誌"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}
    default_icon = "📝"
    print(f"{icons.get(level, default_icon)} [{timestamp}] {message}", flush=True)


def log_heartbeat_execution(start_time, end_time, task_count):
    """記錄心跳執行時間到日誌文件"""
    try:
        execution_time = end_time - start_time
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 確保日誌目錄存在
        HEARTBEAT_LOG.parent.mkdir(parents=True, exist_ok=True)

        # 追加記錄到日誌文件
        with open(HEARTBEAT_LOG, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] 執行時間: {execution_time:.2f}秒, 啟動任務: {task_count}\n")
    except Exception as e:
        # 如果記錄失敗，不影響主流程
        log("WARNING", f"記錄心跳日誌失敗: {e}")


# P0 行動：API 追蹤輔助函數
SPAWN_START_TIMES: Dict[str, datetime] = {}


def record_spawn_start(task_id: str):
    """
    記錄任務啟動開始時間（P0 行動：API 追蹤）

    Args:
        task_id: 任務 ID
    """
    SPAWN_START_TIMES[task_id] = datetime.now(timezone.utc)


def get_spawn_start_time(task_id: str) -> Optional[datetime]:
    """
    獲取任務啟動開始時間

    Args:
        task_id: 任務 ID

    Returns:
        啟動開始時間（如果存在）
    """
    return SPAWN_START_TIMES.get(task_id)


def load_tasks():
    """載入 tasks.json"""
    try:
        with open(TASKS_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)

            # 處理不同的 JSON 格式
            if isinstance(data, dict) and 'tasks' in data:
                return data['tasks']
            elif isinstance(data, list):
                return data
            else:
                log("ERROR", f"未知的 tasks.json 格式: {type(data)}")
                return []
    except Exception as e:
        log("ERROR", f"載入 tasks.json 失敗：{e}")
        return []


def save_tasks(tasks):
    """保存任務到 tasks.json"""
    try:
        with open(TASKS_JSON, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        log("ERROR", f"保存 tasks.json 失敗：{e}")
        return False


def get_running_sessions():
    """獲取當前運行的子代理會話數量（估算）"""
    # 這裡無法直接調用 sessions_list，因為腳本在子進程中運行
    # 所以我們通過檢查 tasks.json 中的 in_progress 狀態來估算
    tasks = load_tasks()
    return sum(1 for t in tasks if t.get('status') == 'in_progress')


def find_spawnable_tasks(tasks, max_spawn=5):
    """
    找出可啟動的任務

    規則：
    1. 狀態為 pending
    2. 沒有依賴或依賴已完成
    3. 按優先級排序（high > medium > low）
    4. 同優先級按創建時間排序

    Returns:
        可啟動的任務列表
    """
    spawnable = []

    for task in tasks:
        if task['status'] != 'pending':
            continue

        # 檢查依賴
        deps = task.get('dependencies', task.get('depends_on', []))
        if deps:
            # 檢查所有依賴是否完成
            all_deps_completed = True
            for dep_id in deps:
                dep_task = next((t for t in tasks if t['id'] == dep_id), None)
                if dep_task and dep_task['status'] != 'completed':
                    all_deps_completed = False
                    break

            if not all_deps_completed:
                continue  # 依賴未完成，跳過

        spawnable.append(task)

    # 按優先級排序
    priority_order = {'high': 0, 'medium': 1, 'low': 2, 'normal': 1}
    spawnable.sort(key=lambda t: (
        priority_order.get(t.get('priority', 'normal'), 1),
        t['created_at']
    ))

    return spawnable[:max_spawn]


def generate_spawn_commands(spawnable_tasks, output_path):
    """
    生成啟動命令並寫入文件

    每個命令格式：
    {
        "task": "TASK: ...",
        "agentId": "research",
        "label": "task-id",
        "model": "zai/glm-4.7"  // 可選
    }

    OPT-3 改進：每個任務使用獨立工作目錄 kanban/works/[task-id]/
    多模型支持：使用 ModelAllocator 自動分配模型
    成本優化：使用 CostOptimizer 選擇成本最優模型

    Args:
        spawnable_tasks: 可啟動的任務列表
        output_path: 輸出文件路徑

    Returns:
        生成的命令數量
    """
    count = 0

    # 初始化模型分配器
    allocator = None
    if MODEL_ALLOCATOR_AVAILABLE:
        try:
            allocator = ModelAllocator(str(MODELS_JSON))
            log("INFO", "✅ 多模型分配器已啟用")
        except Exception as e:
            log("WARNING", f"多模型分配器初始化失敗，使用默認模型：{e}")

    # 初始化成本優化器
    cost_optimizer = None
    budget_mode = "normal"
    if COST_OPTIMIZER_AVAILABLE:
        try:
            cost_optimizer = CostOptimizer(str(MODELS_JSON))
            budget_status = cost_optimizer.check_budget_status()
            budget_mode = budget_status.get("budget_mode", "normal")
            log("INFO", f"✅ 成本優化器已啟用，預算模式：{budget_mode}")
            if budget_mode != "normal":
                log("INFO", f"   今日花費：¥{budget_status['spend_today']:.2f} / ¥{budget_status['daily_limit']} ({budget_status['daily_usage']:.1%})")
        except Exception as e:
            log("WARNING", f"成本優化器初始化失敗，使用正常模式：{e}")
            budget_mode = "normal"

    # 清空或創建文件
    if output_path.exists():
        output_path.unlink()

    with open(output_path, 'w', encoding='utf-8') as f:
        for i, task in enumerate(spawnable_tasks):
            # 構建任務消息
            task_id = task['id']
            agent = task.get('agent', 'research')
            title = task.get('title', task_id)

            # P0 行動：記錄啟動開始時間（API 追蹤）
            record_spawn_start(task_id)

            # OPT-3: 創建獨立工作目錄
            work_dir = WORKSPACE / "kanban" / "works" / task_id
            work_dir.mkdir(parents=True, exist_ok=True)

            # 更新任務的 work_dir
            task['work_dir'] = str(work_dir)

            # 模型選擇邏輯（優先級：metadata.model > task.model > CostOptimizer > ModelAllocator > 默認 glm-4.7）
            model = None

            # 1. 優先從 metadata 讀取模型
            if 'metadata' in task and isinstance(task['metadata'], dict):
                model = task['metadata'].get('model')

            # 2. 其次從 task.model 讀取
            if not model:
                model = task.get('model')

            # 3. 使用 CostOptimizer 成本優化選擇
            if not model and cost_optimizer:
                try:
                    model = cost_optimizer.select_cost_optimal_model(task, budget_mode)
                    if model:
                        log("DEBUG", f"💰 成本優化器選擇：{agent} → {model} (預算模式: {budget_mode})")
                except Exception as e:
                    log("WARNING", f"成本優化器失敗，使用模型分配器：{e}")

            # 4. 使用 ModelAllocator 自動分配
            if not model and allocator:
                try:
                    allocation = allocator.allocate_task(agent)
                    if allocation:
                        model = allocation.get('model_id')
                        log("DEBUG", f"🎯 模型分配器分配：{agent} → {model}")
                except Exception as e:
                    log("WARNING", f"模型分配器失敗，使用默認模型：{e}")

            # 5. 默認使用 glm-4.7（保持高質量）
            if not model:
                model = 'zai/glm-4.7'

            # OPT-3: 構建輸出路徑（指向工作目錄）
            original_output_path = task.get('output_path', '')
            if original_output_path:
                # 將輸出重定向到工作目錄
                output_filename = Path(original_output_path).name
                isolated_output_path = work_dir / output_filename
            else:
                isolated_output_path = work_dir / f"{task_id}-output.md"

            # 這裡使用標準任務消息格式
            task_message = f"TASK: {title}\n\n"
            task_message += f"CONTEXT:\n"
            task_message += f"- 論文 ID: {task_id}\n"
            task_message += f"- 創建時間: {task.get('created_at', 'N/A')}\n"
            task_message += f"- 優先級: {task.get('priority', 'normal')}\n"
            task_message += f"- 預估時間: {task.get('time_tracking', {}).get('estimated_time', {}).get('min', 'N/A')}-{task.get('time_tracking', {}).get('estimated_time', {}).get('max', 'N/A')} 分鐘\n"
            task_message += f"- 工作目錄: {isolated_output_path.parent}\n"
            task_message += f"\nREQUIREMENTS:\n"
            task_message += f"- 找到並獲取論文全文\n"
            task_message += f"- 深度分析核心思想和技術細節\n"
            task_message += f"- 評估應用價值和局限性\n"
            task_message += f"- 用繁體中文撰寫結構化報告\n"
            task_message += f"- 所有輸出檔案寫入工作目錄: {isolated_output_path.parent}\n"
            task_message += f"\nOUTPUT PATH: {isolated_output_path}"

            # 構建 spawn 命令
            spawn_dict = {
                "task": task_message,
                "agentId": agent,
                "label": task_id
            }

            # 如果指定了 model
            if model:
                spawn_dict['model'] = model

            # 寫入文件
            f.write(json.dumps(spawn_dict, ensure_ascii=False) + '\n')
            count += 1

            # 注意：延遲應該在主會話執行 sessions_spawn 時加入
            # 這裡只是生成命令，不延遲

    return count


def update_task_status(tasks, task_ids, new_status):
    """更新任務狀態"""
    updated = 0
    for task in tasks:
        if task['id'] in task_ids:
            task['status'] = new_status
            task['updated_at'] = datetime.now(timezone.utc).isoformat()
            if new_status == 'in_progress':
                task['spawned_at'] = datetime.now(timezone.utc).isoformat()
            updated += 1
    return updated


def main():
    """主函數"""
    log("INFO", "自動任務啟動器（心跳版本）啟動")

    # 多模型分配器狀態檢查
    if MODEL_ALLOCATOR_AVAILABLE:
        try:
            from model_allocator import ModelAllocator
            allocator = ModelAllocator(str(MODELS_JSON))
            status = allocator.get_system_status()
            log("INFO", f"🤖 多模型系統：{status['enabled_models']}/{status['total_models']} 個模型已啟用")
            log("INFO", f"   總請求：{status['total_requests']}，成功率：{status['success_rate']:.2%}")
            log("INFO", f"   活躍任務：{status['active_tasks']} 個")
        except Exception as e:
            log("WARNING", f"多模型系統檢查失敗：{e}")
    else:
        log("INFO", "🤖 多模型系統：未啟用（使用默認 glm-4.7）")

    # 成本優化器狀態檢查
    if COST_OPTIMIZER_AVAILABLE:
        try:
            from cost_optimizer import CostOptimizer
            optimizer = CostOptimizer(str(MODELS_JSON))
            budget_status = optimizer.check_budget_status()
            budget_mode = budget_status.get("budget_mode", "normal")
            log("INFO", f"💰 成本優化器：預算模式 {budget_mode}")
            log("INFO", f"   今日花費：¥{budget_status['spend_today']:.2f} / ¥{budget_status['daily_limit']} ({budget_status['daily_usage']:.1%})")
            log("INFO", f"   本週花費：¥{budget_status['spend_this_week']:.2f} / ¥{budget_status['weekly_limit']} ({budget_status['weekly_usage']:.1%})")
            if budget_mode == "exceeded":
                log("WARNING", "⛔ 預算已超支，不啟動新任務")
                return 0
            elif budget_mode == "critical":
                log("WARNING", "⚠️ 預算緊張，啟動優化模式")
        except Exception as e:
            log("WARNING", f"成本優化器檢查失敗：{e}")
    else:
        log("INFO", "💰 成本優化器：未啟用（使用正常模式）")

    # P1 行動：檢查背壓機制
    if BACKPRESSURE_AVAILABLE:
        try:
            # 檢查並調整背壓
            bp_result = check_backpressure()
            spawn_interval = get_spawn_interval()

            # 顯示背壓狀態
            health = bp_result.get('health', 1.0)
            max_concurrent = bp_result.get('max_concurrent', MAX_CONCURRENT)

            log("INFO", f"🔄 背壓檢查：健康度 {health:.2f}")
            log("INFO", f"   並發上限：{max_concurrent} 個")
            log("INFO", f"   啟動頻率：{spawn_interval} 秒")

            # 更新全局配置
            if spawn_interval != SPAWN_INTERVAL:
                log("INFO", f"   ⚠️ 啟動頻率已調整：{SPAWN_INTERVAL}秒 → {spawn_interval}秒")

        except Exception as e:
            log("WARNING", f"背壓檢查失敗，使用默認配置：{e}")

    # 載入任務
    tasks = load_tasks()
    if not tasks:
        log("ERROR", "無法載入任務")
        return 0

    # P2 行動：應用優先級規則（在選擇任務之前調整優先級）
    if PRIORITY_RULES_SCRIPT.exists():
        try:
            rules_file = WORKSPACE / "skills" / "priority-rule-engine" / "references" / "priority_rules.json"
            if rules_file.exists():
                # 通過 subprocess 調用優先級規則引擎
                result = subprocess.run(
                    [sys.executable, str(PRIORITY_RULES_SCRIPT), "--rules", str(rules_file)],
                    capture_output=True,
                    text=True,
                    cwd=WORKSPACE
                )

                if result.returncode == 0:
                    # 重新載入任務以獲取更新後的優先級
                    tasks = load_tasks()
                    log("INFO", f"🎯 優先級規則引擎：已應用優先級規則")
                else:
                    log("WARNING", f"優先級規則引擎執行失敗（退出碼 {result.returncode}）")
                    if result.stderr:
                        log("WARNING", f"錯誤輸出：{result.stderr[:200]}")
                    if result.stdout:
                        log("WARNING", f"標準輸出：{result.stdout[:200]}")
            else:
                log("DEBUG", f"優先級規則文件不存在：{rules_file}")
        except Exception as e:
            log("WARNING", f"優先級規則引擎執行失敗：{e}")
    else:
        log("DEBUG", "優先級規則引擎腳本不存在，跳過優先級調整")

    # P1 行動：使用背壓機制建議的並發上限
    if BACKPRESSURE_AVAILABLE:
        try:
            from backpressure import get_max_concurrent
            MAX_CONCURRENT_CURRENT = get_max_concurrent()
        except:
            MAX_CONCURRENT_CURRENT = MAX_CONCURRENT
    else:
        MAX_CONCURRENT_CURRENT = MAX_CONCURRENT

    # 統計當前狀態
    in_progress_count = sum(1 for t in tasks if t.get('status') == 'in_progress')
    available_slots = MAX_CONCURRENT_CURRENT - in_progress_count

    log("INFO", f"執行中：{in_progress_count} 個")
    log("INFO", f"可用位置：{available_slots} 個")

    if available_slots <= 0:
        log("INFO", "並發限制已滿，無需啟動新任務")
        # 清空 spawn_commands.jsonl
        if SPAWN_COMMANDS_FILE.exists():
            SPAWN_COMMANDS_FILE.unlink()
        return 0

    # 找出可啟動的任務
    spawnable = find_spawnable_tasks(tasks, available_slots)

    if not spawnable:
        log("INFO", "沒有可啟動的任務")
        # 清空 spawn_commands.jsonl
        if SPAWN_COMMANDS_FILE.exists():
            SPAWN_COMMANDS_FILE.unlink()
        return 0

    log("INFO", f"找到 {len(spawnable)} 個可啟動的任務")

    # 生成啟動命令
    count = generate_spawn_commands(spawnable, SPAWN_COMMANDS_FILE)

    if count > 0:
        log("SUCCESS", f"已生成 {count} 個啟動命令 → {SPAWN_COMMANDS_FILE}")

        # P1 行動：使用背壓機制建議的啟動頻率
        if BACKPRESSURE_AVAILABLE:
            try:
                current_interval = get_spawn_interval()
            except:
                current_interval = SPAWN_INTERVAL
        else:
            current_interval = SPAWN_INTERVAL

        # 計算總等待時間
        total_wait_time = (count - 1) * current_interval if count > 1 else 0
        if total_wait_time > 0:
            log("INFO", f"⏱️ 預計總等待時間：{total_wait_time} 秒（{total_wait_time // 60} 分 {total_wait_time % 60} 秒）")

        # 更新任務狀態為 spawning
        task_ids = [t['id'] for t in spawnable]
        updated = update_task_status(tasks, task_ids, 'spawning')

        if updated > 0:
            save_tasks(tasks)
            log("INFO", f"已更新 {updated} 個任務狀態為 'spawning'")

        # 顯示任務摘要
        log("INFO", "=" * 60)
        for i, task in enumerate(spawnable, 1):
            log("INFO", f"{i}. [{str(task.get('priority', 'normal')).upper()}] {task['title'][:50]}")
            log("INFO", f"   代理：{task.get('agent', 'research')}")
            log("INFO", f"   模型：{task.get('model', '默認')}")
        log("INFO", "=" * 60)

    return count


if __name__ == '__main__':
    start_time = time.time()
    count = main()
    end_time = time.time()

    # 記錄心跳執行時間
    log_heartbeat_execution(start_time, end_time, count if count > 0 else 0)

    exit(0 if count >= 0 else 1)
