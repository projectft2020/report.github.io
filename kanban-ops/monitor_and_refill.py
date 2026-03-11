#!/usr/bin/env python3
"""
Monitor and Refill - 事件驅動任務監控
自動檢查看板任務數量並觸發 Scout 補充
"""

import json
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path

# 配置
WORKSPACE_ROOT = Path.home() / ".openclaw" / "workspace"
TURBO_STATUS_FILE = WORKSPACE_ROOT / "kanban-ops" / "TURBO_STATUS.json"
TASKS_FILE = WORKSPACE_ROOT / "kanban" / "tasks.json"
SCOUT_SCAN_LOG = Path.home() / ".openclaw" / "workspace-scout" / "SCAN_LOG.md"

# 24 小時硬保護（防止 Scout 死鎖）
HARD_TIMEOUT = 24 * 60 * 60  # 24 小時

# 日誌配置
logging.basicConfig(
    level=logging.WARN,  # 默認只輸出 WARN 及以上級別
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def is_turbo_mode_active():
    """檢查是否在加速模式中"""
    try:
        if not TURBO_STATUS_FILE.exists():
            return False

        with open(TURBO_STATUS_FILE, 'r', encoding='utf-8') as f:
            status = json.load(f)

        return status.get('active', False)
    except Exception as e:
        print(f"[ERROR] 檢查加速模式狀態失敗: {e}")
        return False


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
                # 提取時間戳
                try:
                    timestamp_str = line.split('[')[1].split(']')[0]
                    # 嘗試 ISO 8601 格式（例如：2026-03-07T01:59:46.360706+00:00）
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    # 移除時區信息，使其變為 offset-naive
                    return timestamp.replace(tzinfo=None)
                except:
                    continue

        return None
    except Exception as e:
        print(f"[ERROR] 獲取掃描時間失敗: {e}")
        return None


def get_pending_task_count():
    """獲取待辦任務數量"""
    try:
        if not TASKS_FILE.exists():
            return 0

        with open(TASKS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 處理多種格式
        if isinstance(data, dict):
            # 格式 1: {"task_id": {...}} - 舊格式
            if 'tasks' in data:
                # 格式 2: {"tasks": [{...}, {...}]}
                tasks = data['tasks']
                pending_count = sum(1 for task in tasks if task.get('status') == 'pending')
            else:
                # 舊格式
                pending_count = sum(1 for task in data.values() if task.get('status') == 'pending')
        elif isinstance(data, list):
            # 格式 3: [{...}, {...}] - 直接列表
            pending_count = sum(1 for task in data if task.get('status') == 'pending')
        else:
            print(f"[WARNING] 未知 tasks.json 格式: {type(data)}")
            return 0

        return pending_count
    except Exception as e:
        print(f"[ERROR] 獲取待辦任務數量失敗: {e}")
        return 0


def should_scan(pending_count, last_scan_time):
    """判斷是否應該觸發 Scout 掃描"""
    turbo_mode = is_turbo_mode_active()

    if turbo_mode:
        # 加速模式：更快補充
        threshold = 5  # 待辦 < 5 個就掃描
        min_interval = 30 * 60  # 最少 30 分鐘
        mode = "加速模式"
    else:
        # 正常模式：保守掃描
        threshold = 3  # 待辦 < 3 個才掃描
        min_interval = 2 * 60 * 60  # 最少 2 小時
        mode = "正常模式"

    # 檢查時間間隔
    if last_scan_time:
        time_since_scan = (datetime.now() - last_scan_time).total_seconds()
        interval_ok = time_since_scan > min_interval
    else:
        time_since_scan = 0  # 從未掃描過
        interval_ok = True  # 允許掃描

    # 檢查待辦數量
    count_ok = pending_count < threshold

    should = count_ok and interval_ok

    # 24 小時硬保護（防止 Scout 死鎖）
    if last_scan_time and time_since_scan > HARD_TIMEOUT:
        logger.warning(f"⚠️ 超過 24 小時未掃描，強制觸發 Scout 掃描")
        return True

    print(f"[Monitor] {mode}")
    print(f"[Monitor] 待辦任務: {pending_count} (閾值: {threshold})")
    print(f"[Monitor] 距離上次掃描: {time_since_scan:.0f} 秒 (最小: {min_interval} 秒)")

    if should:
        print(f"[Monitor] ✓ 應該觸發 Scout 掃描")
    else:
        print(f"[Monitor] ✓ 不需要觸發 Scout 掃描")

    return should


def trigger_scout_scan():
    """觸發 Scout 掃描"""
    try:
        scout_script = Path.home() / ".openclaw" / "workspace-scout" / "scout_agent.py"

        if not scout_script.exists():
            logger.error(f"Scout 腳本不存在: {scout_script}")
            return False

        logger.info(f"觸發 Scout 掃描...")

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
            logger.info(f"Scout 掃描完成")
            return True
        else:
            logger.error(f"Scout 掃描失敗: {result.stderr}")
            return False

    except Exception as e:
        logger.error(f"觸發 Scout 掃描失敗: {e}")
        return False


def trigger_intelligent_spawn():
    """
    觸發智能並發任務啟動器

    在 Scout 掃描後，自動啟動隊列中的任務
    使用智能分組和序列啟動避免 rate limit
    """
    try:
        spawn_script = WORKSPACE_ROOT / "kanban-ops" / "spawn_tasks_intelligent.py"

        if not spawn_script.exists():
            logger.error(f"智能啟動器不存在: {spawn_script}")
            return False

        # 檢查隊列中是否有任務
        task_queue = WORKSPACE_ROOT / "kanban-ops" / "task_queue"
        if task_queue.exists():
            task_files = list(task_queue.glob("*.json"))
            task_count = len(task_files)

            if task_count == 0:
                logger.info(f"隊列中沒有任務，跳過啟動")
                return True

            logger.info(f"發現 {task_count} 個任務在隊列中")
        else:
            logger.warning(f"隊列目錄不存在，跳過啟動")
            return True

        logger.info(f"使用智能並發啟動器啟動任務...")

        # 執行智能啟動（dry-run 模式，只打印計劃）
        import subprocess
        result = subprocess.run(
            ['python3', str(spawn_script), 'spawn', '--dry-run'],
            cwd=str(WORKSPACE_ROOT),
            capture_output=True,
            text=True,
            timeout=60  # 1 分鐘超時
        )

        if result.returncode == 0:
            logger.info(f"智能啟動計劃已生成")
            logger.info(f"提示：在主會話中執行 'python3 kanban-ops/spawn_tasks_intelligent.py spawn' 來實際啟動")
            return True
        else:
            logger.error(f"智能啟動計劃生成失敗: {result.stderr}")
            return False

    except Exception as e:
        logger.error(f"觸發智能啟動失敗: {e}")
        return False


def main():
    """主函數"""
    print("=" * 60)
    print("🔍 Monitor and Refill - 事件驅動任務監控")
    print("=" * 60)

    # 檢查待辦任務數量
    pending_count = get_pending_task_count()
    print(f"\n📊 當前待辦任務: {pending_count}")

    # 獲取上次掃描時間
    last_scan_time = get_last_scan_time()
    if last_scan_time:
        time_since_scan = (datetime.now() - last_scan_time).total_seconds()
        print(f"📅 上次掃描: {last_scan_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️  距離上次: {time_since_scan / 60:.0f} 分鐘")
    else:
        print(f"📅 上次掃描: 從未掃描過")

    # 判斷是否應該掃描
    should = should_scan(pending_count, last_scan_time)

    # 觸發掃描
    if should:
        print(f"\n🚀 準備觸發 Scout 掃描...")
        scan_success = trigger_scout_scan()

        # 如果掃描成功，觸發智能啟動器
        if scan_success:
            print(f"\n🤖 準備使用智能並發啟動器...")
            trigger_intelligent_spawn()

    print(f"\n✓ 監控檢查完成")
    print("=" * 60)


if __name__ == '__main__':
    main()
