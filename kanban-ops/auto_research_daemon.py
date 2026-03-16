#!/usr/bin/env python3
"""
深夜自動研究守護進程

功能：
- 自動觸發 Scout 掃描找新研究主題
- 自動啟動研究任務（sub-agent）
- 深夜時段（23:00-08:00）運行
- 無限循環直到關閉或天亮

流程：
1. 檢查是否在深夜時段
2. 檢查待辦任務數量
3. 待辦 < threshold → 觸發 Scout 掃描
4. 檢查並發限制
5. 自動啟動 pending 任務
6. 更新統計
7. 等待並重複

使用方式：
    # 啟動守護進程（後台）
    python3 kanban-ops/auto_research_daemon.py start

    # 停止守護進程
    python3 kanban-ops/auto_research_daemon.py stop

    # 查看狀態
    python3 kanban-ops/auto_research_daemon.py status
"""

import json
import os
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# 配置
WORKSPACE = Path.home() / ".openclaw" / "workspace"
CONFIG_FILE = WORKSPACE / "kanban-ops" / "AUTO_RESEARCH.json"
PID_FILE = WORKSPACE / "kanban-ops" / ".auto_research_daemon.pid"
TASKS_JSON = Path.home() / ".openclaw" / "workspace" / "kanban" / "tasks.json"
SCOUT_SCAN_LOG = Path.home() / ".openclaw" / "workspace-scout" / "SCAN_LOG.md"
SPAWN_COMMANDS_FILE = WORKSPACE / "kanban" / "spawn_commands.jsonl"


# ============ 日誌系統 ============

LOG_FILE = WORKSPACE / "kanban-ops" / "auto_research.log"

def log(level, message, daemon=True):
    """記錄日誌"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    icons = {
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "WARNING": "⚠️",
        "ERROR": "❌",
        "DAEMON": "🔄",
        "SCOUT": "🔍",
        "SPAWN": "🚀"
    }
    default_icon = "📝"
    icon = icons.get(level, default_icon)
    prefix = "[Daemon] " if daemon else ""

    # 輸出到控制台
    log_message = f"{icon} [{timestamp}] {prefix}{message}"
    print(log_message, flush=True)

    # 寫入日誌文件
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
    except Exception as e:
        print(f"寫入日誌失敗: {e}", flush=True)


# ============ 配置管理 ============

def load_config():
    """載入配置"""
    try:
        if not CONFIG_FILE.exists():
            log("ERROR", f"配置文件不存在: {CONFIG_FILE}")
            return None

        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)

        return config
    except Exception as e:
        log("ERROR", f"載入配置失敗: {e}")
        return None


def save_config(config):
    """保存配置"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        log("ERROR", f"保存配置失敗: {e}")
        return False


def is_enabled():
    """檢查是否啟用"""
    config = load_config()
    return config and config.get('enabled', False)


def is_night_time(config):
    """判斷是否在深夜時段"""
    hour = datetime.now().hour
    start = config['schedule']['start_hour']
    end = config['schedule']['end_hour']

    # 跨午夜處理 (e.g., 23:00 - 08:00)
    if start > end:
        return hour >= start or hour < end
    else:
        return start <= hour < end


# ============ 統計管理 ============

def update_stats(config, **updates):
    """更新統計"""
    if 'stats' not in config:
        config['stats'] = {}

    stats = config['stats']

    # 更新字段
    for key, value in updates.items():
        if value is not None:
            stats[key] = value

    # 自動更新時間戳
    stats['last_cycle_at'] = datetime.now(timezone.utc).isoformat()

    save_config(config)
    return stats


# ============ 任務管理 ============

def load_tasks():
    """載入 tasks.json"""
    try:
        with open(TASKS_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        log("ERROR", f"載入 tasks.json 失敗: {e}")
        return []


def save_tasks(tasks):
    """保存任務到 tasks.json"""
    try:
        with open(TASKS_JSON, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        log("ERROR", f"保存 tasks.json 失敗: {e}")
        return False


def get_pending_task_count():
    """獲取待辦任務數量"""
    tasks = load_tasks()
    return sum(1 for t in tasks if t.get('status') == 'pending')


def get_in_progress_task_count():
    """獲取進行中任務數量"""
    tasks = load_tasks()
    return sum(1 for t in tasks if t.get('status') in ['in_progress', 'spawning'])


def get_running_count():
    """獲取實際運行數量（從 subagents 估算）"""
    # 這裡無法直接調用 sessions_list
    # 所以使用 in_progress 數量作為估算
    return get_in_progress_task_count()


# ============ Scout 掃描 ============

def get_last_scan_time():
    """獲取上次 Scout 掃描時間"""
    try:
        if not SCOUT_SCAN_LOG.exists():
            return None

        with open(SCOUT_SCAN_LOG, 'r', encoding='utf-8') as f:
            content = f.read()

        # 查找最後一次掃描記錄
        lines = content.split('\n')
        for line in reversed(lines):
            if '[INFO]' in line and '開始掃描' in line:
                try:
                    timestamp_str = line.split('[')[1].split(']')[0]
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S %Z')
                    return timestamp
                except:
                    continue

        return None
    except Exception as e:
        log("ERROR", f"獲取掃描時間失敗: {e}")
        return None


def should_trigger_scout(config):
    """判斷是否應該觸發 Scout 掃描"""
    pending_count = get_pending_task_count()
    last_scan_time = get_last_scan_time()

    threshold = config['behavior']['scout_threshold']
    interval_minutes = config['behavior']['scout_interval_minutes']

    # 檢查數量
    count_ok = pending_count < threshold

    # 檢查時間間隔
    if last_scan_time:
        time_since_scan = (datetime.now() - last_scan_time).total_seconds() / 60
        interval_ok = time_since_scan >= interval_minutes
    else:
        interval_ok = True  # 從未掃描過

    should = count_ok and interval_ok

    log("INFO", f"Scout 檢查: 待辦={pending_count} (閾值={threshold}), 間隔={time_since_scan if last_scan_time else 'N/A'}分鐘 (最小={interval_minutes}分鐘)")

    return should


def trigger_scout_scan():
    """觸發 Scout 掃描"""
    try:
        scout_script = Path.home() / ".openclaw" / "workspace-scout" / "scout_agent.py"

        if not scout_script.exists():
            log("ERROR", f"Scout 腳本不存在: {scout_script}")
            return False

        log("SCOUT", "觸發 Scout 掃描...")

        # 執行 Scout 掃描
        import subprocess
        result = subprocess.run(
            ['python3', str(scout_script), 'scan'],
            cwd=str(scout_script.parent),
            capture_output=True,
            text=True,
            timeout=300  # 5 分鐘超時
        )

        if result.returncode == 0:
            log("SUCCESS", "Scout 掃描完成")
            return True
        else:
            log("ERROR", f"Scout 掃描失敗: {result.stderr}")
            return False

    except Exception as e:
        log("ERROR", f"觸發 Scout 掃描失敗: {e}")
        return False


# ============ 任務啟動 ============

def find_spawnable_tasks(tasks, max_spawn, only_research=True):
    """找出可啟動的任務"""
    spawnable = []

    for task in tasks:
        if task['status'] != 'pending':
            continue

        # 檢查是否只啟動研究任務
        if only_research:
            agent = task.get('agent', '')
            if agent != 'research':
                log("INFO", f"跳過非研究任務: {task['id']} (agent={agent})")
                continue

        # 檢查依賴
        deps = task.get('dependencies', task.get('depends_on', []))
        if deps:
            all_deps_completed = True
            for dep_id in deps:
                dep_task = next((t for t in tasks if t['id'] == dep_id), None)
                if dep_task and dep_task['status'] != 'completed':
                    all_deps_completed = False
                    break

            if not all_deps_completed:
                continue

        spawnable.append(task)

    # 按優先級排序
    priority_order = {'high': 0, 'medium': 1, 'low': 2, 'normal': 1}
    spawnable.sort(key=lambda t: (
        priority_order.get(t.get('priority', 'normal'), 1),
        t['created_at']
    ))

    return spawnable[:max_spawn]


def generate_spawn_commands(spawnable_tasks, output_path):
    """生成啟動命令"""
    count = 0

    # 清空或創建文件
    if output_path.exists():
        output_path.unlink()

    with open(output_path, 'w', encoding='utf-8') as f:
        for task in spawnable_tasks:
            task_id = task['id']
            agent = task.get('agent', 'research')
            title = task.get('title', task_id)
            model = task.get('model')

            # 構建任務消息
            task_message = f"TASK: {title}\n\n"
            task_message += f"CONTEXT:\n"
            task_message += f"- 論文 ID: {task_id}\n"
            task_message += f"- 創建時間: {task.get('created_at', 'N/A')}\n"
            task_message += f"- 優先級: {task.get('priority', 'normal')}\n"
            task_message += f"- 預估時間: {task.get('time_tracking', {}).get('estimated_time', {}).get('min', 'N/A')}-{task.get('time_tracking', {}).get('estimated_time', {}).get('max', 'N/A')} 分鐘\n"
            task_message += f"\nREQUIREMENTS:\n"
            task_message += f"- 找到並獲取論文全文\n"
            task_message += f"- 深度分析核心思想和技術細節\n"
            task_message += f"- 評估應用價值和局限性\n"
            task_message += f"- 用繁體中文撰寫結構化報告\n"
            task_message += f"\nOUTPUT PATH: {task.get('output_path', 'N/A')}"

            # 構建 spawn 命令
            spawn_dict = {
                "task": task_message,
                "agentId": agent,
                "label": task_id
            }

            if model:
                spawn_dict['model'] = model

            f.write(json.dumps(spawn_dict, ensure_ascii=False) + '\n')
            count += 1

    return count


def auto_spawn_tasks(config):
    """自動啟動任務"""
    max_concurrent = config['behavior']['max_concurrent']
    only_research = config['behavior'].get('only_research', True)

    # 獲取當前運行數量
    running_count = get_running_count()
    available_slots = max_concurrent - running_count

    log("INFO", f"並發檢查: 運行中={running_count}, 可用={available_slots}, 最大={max_concurrent}")

    if available_slots <= 0:
        log("INFO", "並發限制已滿，無需啟動新任務")
        return 0

    # 載入任務
    tasks = load_tasks()
    if not tasks:
        log("WARNING", "無法載入任務")
        return 0

    # 找出可啟動的任務
    spawnable = find_spawnable_tasks(tasks, available_slots, only_research)

    if not spawnable:
        log("INFO", "沒有可啟動的任務")
        return 0

    # 生成啟動命令
    count = generate_spawn_commands(spawnable, SPAWN_COMMANDS_FILE)

    if count > 0:
        log("SUCCESS", f"已生成 {count} 個啟動命令")

        # 更新任務狀態
        task_ids = [t['id'] for t in spawnable]
        updated = 0
        for task in tasks:
            if task['id'] in task_ids:
                task['status'] = 'spawning'
                task['updated_at'] = datetime.now(timezone.utc).isoformat()
                updated += 1

        if updated > 0:
            save_tasks(tasks)
            log("INFO", f"已更新 {updated} 個任務狀態為 'spawning'")

        return count

    return 0


# ============ 守護進程邏輯 ============

def daemon_main():
    """守護進程主循環"""
    log("DAEMON", "守護進程啟動")
    log("INFO", f"配置文件: {CONFIG_FILE}")
    log("INFO", f"PID 文件: {PID_FILE}")

    # 寫入 PID
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))

    # 載入配置
    config = load_config()
    if not config:
        log("ERROR", "無法載入配置，退出")
        return 1

    # 初始化統計
    if config['stats'].get('started_at') is None:
        update_stats(config, started_at=datetime.now(timezone.utc).isoformat())

    log("SUCCESS", f"模式已啟用: {config['name']}")
    log("INFO", f"時段: {config['schedule']['start_hour']}:00 - {config['schedule']['end_hour']}:00")
    log("INFO", f"Scout 閾值: {config['behavior']['scout_threshold']}, 間隔: {config['behavior']['scout_interval_minutes']}分鐘")
    log("INFO", f"最大並發: {config['behavior']['max_concurrent']}, 循環間隔: {config['behavior']['loop_interval_minutes']}分鐘")

    cycle_count = 0
    empty_scan_count = 0
    max_empty_scans = 3  # 連續 3 次空掃描就暫停

    try:
        while True:
            cycle_count += 1

            log("DAEMON", f"循環 #{cycle_count}")
            print("=" * 60)

            # 1. 檢查時段
            if not is_night_time(config):
                log("INFO", "⏰ 非深夜時段，暫停監控（等待 30 分鐘）")
                time.sleep(30 * 60)
                continue

            # 2. 檢查配置
            if not is_enabled():
                log("INFO", "🛑 模式已停用，退出守護進程")
                break

            # 3. 觸發 Scout 掃描
            if should_trigger_scout(config):
                log("DAEMON", "觸發 Scout 掃描...")

                # 記錄掃描前的待辦數量
                pending_before = get_pending_task_count()
                scout_success = trigger_scout_scan()

                if scout_success:
                    # 等待任務創建
                    time.sleep(5)

                    # 檢查是否創建了新任務
                    pending_after = get_pending_task_count()

                    if pending_after <= pending_before:
                        # 空掃描：沒有創建新任務
                        empty_scan_count += 1
                        log("WARNING", f"⚠️ 連續 {empty_scan_count} 次空掃描（掃描前={pending_before}, 掃描後={pending_after}）")

                        if empty_scan_count >= max_empty_scans:
                            log("INFO", f"⏸️  達到最大空掃描次數 ({max_empty_scans})，暫停 30 分鐘")
                            time.sleep(30 * 60)
                            empty_scan_count = 0  # 重置計數
                            continue  # 跳過本次循環，重新開始
                    else:
                        # 有新任務創建
                        new_tasks = pending_after - pending_before
                        log("SUCCESS", f"✅ Scout 掃描成功，創建了 {new_tasks} 個新任務")
                        empty_scan_count = 0  # 重置空掃描計數

                    # 更新統計
                    stats = update_stats(config, scout_scans=config['stats']['scout_scans'] + 1)
                    log("INFO", f"統計: Scout 掃描 {stats['scout_scans']} 次")

            # 4. 自動啟動任務
            log("DAEMON", "檢查並啟動任務...")
            spawned_count = auto_spawn_tasks(config)

            if spawned_count > 0:
                # 更新統計
                stats = update_stats(
                    config,
                    tasks_spawned=config['stats']['tasks_spawned'] + spawned_count,
                    total_cycles=config['stats']['total_cycles'] + 1
                )
                log("INFO", f"統計: 啟動 {spawned_count} 個任務，總共 {stats['tasks_spawned']} 個")

            # 5. 等待循環
            loop_interval = config['behavior']['loop_interval_minutes'] * 60
            log("DAEMON", f"等待 {loop_interval // 60} 分鐘後繼續...")
            print("=" * 60)

            time.sleep(loop_interval)

    except KeyboardInterrupt:
        log("INFO", "收到中斷信號，優雅退出")
    except Exception as e:
        log("ERROR", f"守護進程錯誤: {e}")
    finally:
        # 清理 PID 文件
        if PID_FILE.exists():
            PID_FILE.unlink()
        log("DAEMON", "守護進程已退出")

    return 0


# ============ 命令行接口 ============

def start_daemon():
    """啟動守護進程"""
    # 檢查是否已經在運行
    if PID_FILE.exists():
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())

        # 檢查進程是否存在
        try:
            os.kill(pid, 0)
            log("ERROR", f"守護進程已在運行 (PID: {pid})")
            return 1
        except OSError:
            # 進程不存在，清理 PID 文件
            PID_FILE.unlink()

    # 啟用配置
    config = load_config()
    if not config:
        log("ERROR", "無法載入配置")
        return 1

    config['enabled'] = True
    save_config(config)

    # 啟動守護進程（後台）
    import subprocess
    with open(LOG_FILE, 'a') as log_file:
        subprocess.Popen(
            [sys.executable, __file__, 'run'],
            start_new_session=True,
            stdout=log_file,
            stderr=log_file
        )

    log("SUCCESS", "守護進程已啟動（後台運行）")
    log("INFO", "使用 'python3 kanban-ops/auto_research_daemon.py status' 查看狀態")
    log("INFO", "使用 'python3 kanban-ops/auto_research_daemon.py stop' 停止守護進程")
    return 0


def stop_daemon():
    """停止守護進程"""
    if not PID_FILE.exists():
        log("WARNING", "守護進程未運行")
        return 0

    with open(PID_FILE, 'r') as f:
        pid = int(f.read().strip())

    try:
        os.kill(pid, signal.SIGTERM)
        log("SUCCESS", f"已發送停止信號到守護進程 (PID: {pid})")

        # 等待進程退出
        for _ in range(10):
            try:
                os.kill(pid, 0)
                time.sleep(1)
            except OSError:
                break
        else:
            # 強制終止
            log("WARNING", "守護進程未響應，強制終止")
            os.kill(pid, signal.SIGKILL)

    except OSError as e:
        log("ERROR", f"停止守護進程失敗: {e}")
        return 1

    # 清理 PID 文件
    if PID_FILE.exists():
        PID_FILE.unlink()

    # 禁用配置
    config = load_config()
    if config:
        config['enabled'] = False
        save_config(config)

    log("SUCCESS", "守護進程已停止")
    return 0


def show_status():
    """顯示狀態"""
    config = load_config()

    if not config:
        log("ERROR", "無法載入配置")
        return 1

    print("\n" + "=" * 60)
    print(f"📊 {config['name']} 狀態")
    print("=" * 60)

    # 運行狀態
    if PID_FILE.exists():
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        try:
            os.kill(pid, 0)
            running = True
        except OSError:
            running = False
            PID_FILE.unlink()
    else:
        running = False

    print(f"狀態: {'🟢 運行中' if running else '🔴 未運行'}")
    if running:
        print(f"PID: {pid}")

    print(f"啟用: {'✅ 是' if config['enabled'] else '❌ 否'}")
    print(f"時段: {config['schedule']['start_hour']}:00 - {config['schedule']['end_hour']}:00")

    # 統計
    stats = config['stats']
    print(f"\n統計:")
    print(f"  總循環次數: {stats.get('total_cycles', 0)}")
    print(f"  Scout 掃描: {stats.get('scout_scans', 0)} 次")
    print(f"  任務啟動: {stats.get('tasks_spawned', 0)} 個")
    print(f"  任務完成: {stats.get('tasks_completed', 0)} 個")

    if stats.get('started_at'):
        started = datetime.fromisoformat(stats['started_at']).replace(tzinfo=None)
        print(f"  啟動時間: {started.strftime('%Y-%m-%d %H:%M:%S')}")

    if stats.get('last_cycle_at'):
        last = datetime.fromisoformat(stats['last_cycle_at']).replace(tzinfo=None)
        print(f"  最後循環: {last.strftime('%Y-%m-%d %H:%M:%S')}")

    # 當前狀態
    print(f"\n當前狀態:")
    print(f"  待辦任務: {get_pending_task_count()} 個")
    print(f"  進行中: {get_running_count()} 個")

    # 時段檢查
    if is_night_time(config):
        print(f"  時段: 🌙 深夜時段（活躍）")
    else:
        print(f"  時段: ☀️ 非深夜時段（暫停）")

    print("=" * 60)
    return 0


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("使用方式:")
        print("  python3 kanban-ops/auto_research_daemon.py start  # 啟動守護進程")
        print("  python3 kanban-ops/auto_research_daemon.py stop   # 停止守護進程")
        print("  python3 kanban-ops/auto_research_daemon.py status # 查看狀態")
        print("  python3 kanban-ops/auto_research_daemon.py run    # 守護進程主循環（內部使用）")
        return 1

    command = sys.argv[1]

    if command == 'start':
        return start_daemon()
    elif command == 'stop':
        return stop_daemon()
    elif command == 'status':
        return show_status()
    elif command == 'run':
        return daemon_main()
    else:
        log("ERROR", f"未知命令: {command}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
