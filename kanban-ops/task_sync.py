#!/usr/bin/env python3
"""
Task Sync - 狀態同步器

由心跳調用，負責：
1. 掃描子代理的 .status 文件
2. 更新 tasks.json 中的任務狀態
3. 檢查超時任務（超過 24 小時標記為 failed）
4. 複製輸出文件到主工作區
"""

import json
import logging
import shutil
import sys
import yaml
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# 配置
TASKS_FILE = Path.home() / '.openclaw/workspace/kanban/tasks.json'
SYNC_LOG = Path.home() / '.openclaw/workspace/kanban/sync.log'
TIMEOUT_HOURS = 24

# 子代理工作區目錄
WORKSPACE_AGENTS = ['analyst', 'research', 'creative', 'automation']

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(SYNC_LOG, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def load_tasks() -> List[Dict]:
    """載入 tasks.json"""
    with open(TASKS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_tasks(tasks: List[Dict]):
    """保存 tasks.json"""
    with open(TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)


def update_task_status(task_id: str, status: str, completed_at: Optional[str] = None) -> bool:
    """
    更新任務狀態

    Args:
        task_id: 任務 ID
        status: 新狀態
        completed_at: 完成時間（可選）

    Returns:
        是否成功更新
    """
    try:
        tasks = load_tasks()

        for i, task in enumerate(tasks):
            if task.get('id') == task_id:
                tasks[i]['status'] = status
                tasks[i]['updated_at'] = datetime.now(timezone.utc).isoformat()

                if status == 'completed':
                    tasks[i]['completed_at'] = completed_at or datetime.now(timezone.utc).isoformat()

                save_tasks(tasks)
                return True

        return False

    except Exception as e:
        logger.error(f"[Sync] Error updating task {task_id}: {e}")
        return False


def parse_status_file(status_file: Path) -> Tuple[Optional[Dict], Optional[str]]:
    """
    解析 status 文件（支持 JSON 和 YAML）

    Args:
        status_file: status 文件路徑

    Returns:
        (status_data, error_message) 元組
    """
    try:
        content = status_file.read_text()

        # 嘗試 JSON 解析
        try:
            return json.loads(content), None
        except json.JSONDecodeError:
            pass

        # 嘗試 YAML 解析
        try:
            return yaml.safe_load(content), None
        except yaml.YAMLError as e:
            return None, f"YAML parse error: {e}"

    except Exception as e:
        return None, f"Read error: {e}"


def get_task_id(status_data: Dict, default: str) -> str:
    """
    獲取 task_id，支持駝峰命名和下劃線命名

    Args:
        status_data: status 文件數據
        default: 默認值

    Returns:
        task_id 字符串
    """
    # 優先順序：task_id > taskId > default
    return status_data.get('task_id') or status_data.get('taskId') or default


def get_status(status_data: Dict) -> Optional[str]:
    """
    獲取 status，支持多種命名

    Args:
        status_data: status 文件數據

    Returns:
        status 字符串或 None
    """
    # 優先順序：status > result > None
    return status_data.get('status') or status_data.get('result')


def find_status_files() -> Dict[str, Tuple[Path, Dict]]:
    """
    掃描所有子代理工作區的 .status 文件

    Returns:
        字典 {task_id: (status_file_path, status_data)}
    """
    status_files = {}

    for agent_type in WORKSPACE_AGENTS:
        workspace = Path.home() / f'.openclaw/workspace-{agent_type}'
        status_dir = workspace / 'outputs/.status'

        if not status_dir.exists():
            continue

        for status_file in status_dir.glob('*.status'):
            # 解析 status 文件
            status_data, error = parse_status_file(status_file)

            if error:
                logger.warning(f"[Sync] Failed to parse {status_file}: {error}")
                continue

            # 獲取 task_id
            task_id = get_task_id(status_data, status_file.stem)

            if task_id:
                status_files[task_id] = (status_file, status_data)

    logger.info(f"[Sync] Found {len(status_files)} status files")
    return status_files


def process_status_file(status_file: Path, status_data: Dict) -> bool:
    """
    處理單個 status 文件

    Args:
        status_file: status 文件路徑
        status_data: 解析後的 status 數據

    Returns:
        是否處理成功
    """
    try:
        # 獲取字段（支持多種命名）
        task_id = get_task_id(status_data, status_file.stem)
        status = get_status(status_data)
        output_path = status_data.get('output_path') or status_data.get('output_file') or status_data.get('outputPath')
        completed_at = status_data.get('completed_at') or status_data.get('endTime') or status_data.get('completedAt')
        exit_code = status_data.get('exit_code')

        if not task_id:
            logger.warning(f"[Sync] Status file missing task_id: {status_file}")
            return False

        # 規範化 status
        if status and status.lower() in ('success', 'completed'):
            status = 'completed'
        elif status and status.lower() == 'failed':
            status = 'failed'
        elif not status:
            logger.warning(f"[Sync] Status file missing status field: {status_file}")
            return False

        # 讀取任務
        tasks = load_tasks()
        task = next((t for t in tasks if t.get('id') == task_id), None)

        if not task:
            logger.warning(f"[Sync] Task {task_id} not found in tasks.json")
            # 清理孤兒 status 文件
            try:
                status_file.unlink()
                logger.info(f"[Sync] ✓ Cleaned up orphan status file: {status_file.name}")
            except:
                pass
            return False

        # 檢查任務狀態，避免重複處理
        if task.get('status') == status:
            logger.info(f"[Sync] Task {task_id} already {status}, skipping")
            # 刪除 status 文件
            status_file.unlink()
            return True

        # 更新任務狀態
        success = update_task_status(task_id, status, completed_at)

        if not success:
            logger.error(f"[Sync] Failed to update task {task_id}")
            return False

        logger.info(f"[Sync] ✓ Task {task_id} marked as {status}")

        # 複製輸出文件到主工作區
        if output_path and status == 'completed':
            copy_output_file(output_path, task_id)

        # 刪除 status 文件
        status_file.unlink()
        logger.info(f"[Sync] ✓ Deleted status file: {status_file.name}")

        return True

    except Exception as e:
        logger.error(f"[Sync] Error processing status file {status_file}: {e}")
        import traceback
        traceback.print_exc()
        return False


def copy_output_file(output_path: str, task_id: str):
    """
    複製輸出文件到主工作區

    Args:
        output_path: 子代理輸出文件路徑
        task_id: 任務 ID
    """
    try:
        # 解析輸出路徑
        output_file = Path(output_path).expanduser()

        if not output_file.exists():
            logger.warning(f"[Sync] Output file not found: {output_file}")
            return

        # 讀取任務獲取 project_id
        tasks = load_tasks()
        task = next((t for t in tasks if t.get('id') == task_id), None)

        if not task:
            logger.warning(f"[Sync] Task {task_id} not found")
            return

        project_id = task.get('project_id', 'unknown')

        # 構建主工作區路徑
        main_workspace = Path.home() / '.openclaw/workspace/kanban/projects'
        target_dir = main_workspace / project_id
        target_dir.mkdir(parents=True, exist_ok=True)

        target_file = target_dir / f"{task_id}.md"

        # 複製文件
        shutil.copy2(output_file, target_file)

        logger.info(f"[Sync] ✓ Copied output to: {target_file}")

    except Exception as e:
        logger.error(f"[Sync] Error copying output file: {e}")


def check_timeout_tasks():
    """
    檢查超時任務

    超過 24 小時未完成的任務標記為 failed
    """
    tasks = load_tasks()
    now = datetime.now(timezone.utc)

    timeout_count = 0

    for i, task in enumerate(tasks):
        if task.get('status') != 'in_progress':
            continue

        # 檢查 started_at
        time_tracking = task.get('time_tracking', {})
        started_at_str = time_tracking.get('started_at')

        if not started_at_str:
            continue

        try:
            started_at = datetime.fromisoformat(started_at_str.replace('Z', '+00:00'))
            elapsed = now - started_at

            if elapsed > timedelta(hours=TIMEOUT_HOURS):
                task_id = task.get('id')
                logger.warning(f"[Sync] Task {task_id} timed out after {elapsed}")

                # 標記為 failed
                tasks[i]['status'] = 'failed'
                tasks[i]['updated_at'] = now.isoformat()
                tasks[i]['time_tracking'] = {
                    **time_tracking,
                    'failed_at': now.isoformat(),
                    'failure_reason': 'timeout',
                }

                timeout_count += 1

        except Exception as e:
            logger.error(f"[Sync] Error checking timeout for task {task.get('id')}: {e}")

    # 保存更新的任務
    if timeout_count > 0:
        save_tasks(tasks)
        logger.info(f"[Sync] Marked {timeout_count} tasks as failed due to timeout")


def main():
    """主函數"""
    logger.info(f"[Sync] Starting task sync at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # 1. 掃描 status 文件
        status_files = find_status_files()

        if not status_files:
            logger.info(f"[Sync] No status files found")

        # 2. 處理每個 status 文件
        processed_count = 0
        failed_count = 0

        for task_id, (status_file, status_data) in status_files.items():
            success = process_status_file(status_file, status_data)

            if success:
                processed_count += 1
            else:
                failed_count += 1

        logger.info(f"[Sync] Processed {processed_count} status files, {failed_count} failed")

        # 3. 檢查超時任務
        check_timeout_tasks()

        logger.info(f"[Sync] Task sync completed")

    except Exception as e:
        logger.error(f"[Sync] Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
