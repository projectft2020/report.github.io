"""
任務數據服務

處理任務的 CRUD 操作、文件讀寫和業務邏輯。
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from app.config import settings
from app.models.task import (
    Task, TaskCreate, TaskUpdate, TaskStatus,
    TaskListResponse, BatchOperation
)
from app.utils.exceptions import (
    TaskNotFound, InvalidTaskStatus, FileAccessError
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TaskService:
    """任務服務類"""
    
    def __init__(self):
        self.tasks_file = Path(settings.tasks_file)
        self._ensure_tasks_file_exists()
    
    def _ensure_tasks_file_exists(self):
        """確保任務文件存在"""
        try:
            if not self.tasks_file.exists():
                self.tasks_file.parent.mkdir(parents=True, exist_ok=True)
                with open(self.tasks_file, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
                logger.info(f"Created tasks file: {self.tasks_file}")
        except Exception as e:
            raise FileAccessError(
                str(self.tasks_file),
                f"Cannot create tasks file: {e}"
            )
    
    def _load_tasks(self) -> List[Dict[str, Any]]:
        """加載任務數據"""
        try:
            with open(self.tasks_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in tasks file: {e}")
            return []
        except Exception as e:
            raise FileAccessError(
                str(self.tasks_file),
                f"Cannot read tasks file: {e}"
            )
    
    def _save_tasks(self, tasks: List[Dict[str, Any]]):
        """保存任務數據"""
        try:
            # 備份現有文件
            backup_file = self.tasks_file.with_suffix('.json.backup')
            if self.tasks_file.exists():
                self.tasks_file.replace(backup_file)
            
            # 保存新數據
            with open(self.tasks_file, 'w', encoding='utf-8') as f:
                json.dump(tasks, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Saved {len(tasks)} tasks to {self.tasks_file}")
            
        except Exception as e:
            raise FileAccessError(
                str(self.tasks_file),
                f"Cannot save tasks file: {e}"
            )
    
    def get_tasks(
        self,
        status: Optional[TaskStatus] = None,
        agent: Optional[str] = None,
        priority: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> TaskListResponse:
        """獲取任務列表"""
        
        tasks_data = self._load_tasks()
        tasks = [Task(**task_data) for task_data in tasks_data]
        
        # 過濾
        if status:
            tasks = [t for t in tasks if t.status == status]
        if agent:
            tasks = [t for t in tasks if t.agent == agent]
        if priority:
            tasks = [t for t in tasks if t.priority.value == priority]
        
        # 排序
        reverse = sort_order.lower() == "desc"
        if sort_by == "created_at":
            tasks.sort(key=lambda t: t.created_at, reverse=reverse)
        elif sort_by == "updated_at":
            tasks.sort(key=lambda t: t.updated_at, reverse=reverse)
        elif sort_by == "priority":
            priority_order = {"highest": 4, "high": 3, "normal": 2, "low": 1}
            tasks.sort(
                key=lambda t: priority_order.get(t.priority.value, 0),
                reverse=reverse
            )
        
        # 分頁
        start = (page - 1) * page_size
        end = start + page_size
        paginated_tasks = tasks[start:end]
        
        return TaskListResponse(
            tasks=paginated_tasks,
            total=len(tasks),
            page=page,
            page_size=page_size
        )
    
    def get_task(self, task_id: str) -> Task:
        """獲取單個任務"""
        tasks_data = self._load_tasks()
        
        for task_data in tasks_data:
            if task_data.get('id') == task_id:
                return Task(**task_data)
        
        raise TaskNotFound(task_id)
    
    def create_task(self, task_create: TaskCreate) -> Task:
        """創建新任務"""
        tasks_data = self._load_tasks()
        
        # 生成任務 ID
        now = datetime.now()
        task_id = now.strftime("%Y%m%d-%H%M%S-") + "001"
        
        # 檢查 ID 是否已存在
        existing_ids = {t.get('id') for t in tasks_data}
        suffix = 1
        while task_id in existing_ids:
            task_id = now.strftime(f"%Y%m%d-%H%M%S-{suffix:03d}")
            suffix += 1
        
        # 創建任務
        task_dict = task_create.dict()
        task_dict.update({
            'id': task_id,
            'created_at': now.isoformat(),
            'updated_at': now.isoformat(),
            'completed_at': None
        })
        
        tasks_data.append(task_dict)
        self._save_tasks(tasks_data)
        
        task = Task(**task_dict)
        logger.info(f"Created task: {task_id} - {task.title}")
        
        return task
    
    def update_task(self, task_id: str, task_update: TaskUpdate) -> Task:
        """更新任務"""
        tasks_data = self._load_tasks()
        
        for i, task_data in enumerate(tasks_data):
            if task_data.get('id') == task_id:
                # 更新字段
                update_dict = task_update.dict(exclude_unset=True)
                
                # 如果狀態改為完成，設置完成時間
                if (task_update.status == TaskStatus.COMPLETED and 
                    task_data.get('completed_at') is None):
                    update_dict['completed_at'] = datetime.now().isoformat()
                
                # 更新時間
                update_dict['updated_at'] = datetime.now().isoformat()
                
                # 應用更新
                task_data.update(update_dict)
                
                # 保存
                self._save_tasks(tasks_data)
                
                task = Task(**task_data)
                logger.info(f"Updated task: {task_id}")
                
                return task
        
        raise TaskNotFound(task_id)
    
    def delete_task(self, task_id: str) -> bool:
        """刪除任務"""
        tasks_data = self._load_tasks()
        
        original_length = len(tasks_data)
        tasks_data = [t for t in tasks_data if t.get('id') != task_id]
        
        if len(tasks_data) == original_length:
            raise TaskNotFound(task_id)
        
        self._save_tasks(tasks_data)
        logger.info(f"Deleted task: {task_id}")
        
        return True
    
    def update_task_status(self, task_id: str, status: TaskStatus) -> Task:
        """更新任務狀態"""
        try:
            return self.update_task(task_id, TaskUpdate(status=status))
        except ValueError:
            raise InvalidTaskStatus(status.value)
    
    def restart_task(self, task_id: str) -> Task:
        """重新啟動任務"""
        return self.update_task(task_id, TaskUpdate(
            status=TaskStatus.PENDING,
            completed_at=None
        ))
    
    def batch_operation(self, batch_op: BatchOperation) -> Dict[str, Any]:
        """批量操作任務"""
        succeeded = []
        failed = []
        
        for task_id in batch_op.task_ids:
            try:
                if batch_op.operation == "restart":
                    self.restart_task(task_id)
                elif batch_op.operation == "delete":
                    self.delete_task(task_id)
                elif batch_op.operation == "update_status" and batch_op.status:
                    self.update_task_status(task_id, batch_op.status)
                else:
                    raise ValueError(f"Invalid operation: {batch_op.operation}")
                
                succeeded.append(task_id)
                
            except Exception as e:
                failed.append({
                    "task_id": task_id,
                    "error": str(e)
                })
                logger.error(f"Batch operation failed for task {task_id}: {e}")
        
        return {
            "succeeded": succeeded,
            "failed": failed,
            "total": len(batch_op.task_ids)
        }
    
    def get_task_stats(self) -> Dict[str, Any]:
        """獲取任務統計信息"""
        tasks_data = self._load_tasks()
        
        stats = {
            "total": len(tasks_data),
            "pending": 0,
            "in_progress": 0,
            "completed": 0,
            "failed": 0
        }
        
        for task_data in tasks_data:
            status = task_data.get('status', 'pending')
            if status in stats:
                stats[status] += 1
        
        return stats


# 創建全局服務實例
task_service = TaskService()