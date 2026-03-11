#!/usr/bin/env python3
"""
Apprentice Checkpoint - 學徒檢查點主腳本
Main script for periodic apprentice checkpoints
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path


# 添加工作區到 Python 路徑
workspace = os.path.expanduser("~/.openclaw/workspace")
sys.path.insert(0, workspace)


class ApprenticeCheckpoint:
    """學徒檢查點管理器"""
    
    def __init__(self):
        self.workspace = workspace
        self.memory_dir = Path(workspace) / "memory"
        self.learning_dir = Path(workspace) / "memory" / "learning"
        self.checkpoint_file = self.learning_dir / f"{datetime.now().strftime('%Y-%m-%d')}.md"
        
        # 確保目錄存在
        self.learning_dir.mkdir(parents=True, exist_ok=True)
        
    def gather_checkpoint_context(self) -> dict:
        """
        收集檢查點上下文
        Gather checkpoint context
        """
        context = {
            "timestamp": datetime.now().isoformat(),
            "recent_activity": self._get_recent_activity(),
            "current_projects": self._get_current_projects(),
            "system_status": self._get_system_status(),
            "error_summary": self._get_error_summary(),
            "pain_points": self._get_pain_points()
        }
        return context
        
    def _get_recent_activity(self) -> list:
        """獲取最近活動"""
        # 讀取今天的 memory 文件
        today = datetime.now().strftime('%Y-%m-%d')
        today_file = self.memory_dir / f"{today}.md"
        
        if today_file.exists():
            content = today_file.read_text()
            # 簡化：提取關鍵活動（實際實現可以用更複雜的解析）
            return ["已完成 tasks", "已更新 memory"]
        return []
        
    def _get_current_projects(self) -> list:
        """獲取當前專案狀態"""
        kanban_file = Path(workspace) / "kanban" / "tasks.json"
        
        if kanban_file.exists():
            with open(kanban_file, 'r') as f:
                tasks = json.load(f)
                
            # 統計專案狀態
            projects = {}
            for task in tasks:
                project_id = task.get('project_id', 'unknown')
                if project_id not in projects:
                    projects[project_id] = {'total': 0, 'pending': 0, 'in_progress': 0, 'completed': 0}
                    
                projects[project_id]['total'] += 1
                status = task.get('status', 'unknown')
                if status in projects[project_id]:
                    projects[project_id][status] += 1
                    
            return [
                {
                    'id': pid,
                    'total': data['total'],
                    'pending': data['pending'],
                    'in_progress': data['in_progress'],
                    'completed': data['completed']
                }
                for pid, data in projects.items()
            ]
        return []
        
    def _get_system_status(self) -> dict:
        """獲取系統狀態"""
        # 載入 trigger 系統狀態
        try:
            from mentor_ops.trigger_system import MentorTriggerSystem
            trigger_system = MentorTriggerSystem()
            return trigger_system.get_status()
        except Exception as e:
            return {"error": str(e)}
            
    def _get_error_summary(self) -> list:
        """獲取錯誤摘要"""
        # 簡化實現
        return []
        
    def _get_pain_points(self) -> list:
        """獲取痛點"""
        # 簡化實現
        return []
        
    def generate_checkpoint_questions(self, context: dict) -> list:
        """
        生成檢查點問題
        Generate checkpoint questions
        """
        questions = [
            {
                "id": "direction_check",
                "question": "最近的工作方向是否符合您的期望？有沒有偏好的改進？",
                "category": "direction"
            },
            {
                "id": "improvement_check",
                "question": "有哪些需要改進的地方？系統運作是否順暢？",
                "category": "improvement"
            },
            {
                "id": "challenge_check",
                "question": "最近遇到的最大挑戰是什麼？是如何解決的？",
                "category": "challenge"
            },
            {
                "id": "learning_check",
                "question": "有哪些新學到的知識或技能？如何應用到未來的工作中？",
                "category": "learning"
            },
            {
                "id": "mentor_check",
                "question": "是否需要 Mentor 的深入指導？有哪些複雜問題需要討論？",
                "category": "mentor"
            }
        ]
        return questions
        
    def format_checkpoint_report(self, context: dict) -> str:
        """
        格式化檢查點報告
        Format checkpoint report
        """
        report = f"""# 學徒檢查點 - {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 系統概況

### 時間戳
{context['timestamp']}

### Heartbeat 狀態
- 計數: {context['system_status'].get('heartbeat_counter', 'N/A')}
- 上次 Mentor 會話: {context['system_status'].get('last_mentor_session', 'Never')}
- 錯誤模式: {len(context['system_status'].get('error_patterns', {}))} 種

### 專案狀態
"""
        
        for project in context['current_projects']:
            report += f"""
- **{project['id']}**:
  - 總任務: {project['total']}
  - 待處理: {project['pending']}
  - 執行中: {project['in_progress']}
  - 已完成: {project['completed']}
"""
        
        report += """

## 最近活動
"""
        
        for activity in context['recent_activity']:
            report += f"- {activity}\n"
            
        if context['error_summary']:
            report += "\n## 錯誤摘要\n\n"
            for error in context['error_summary']:
                report += f"- {error}\n"
                
        if context['pain_points']:
            report += "\n## 痛點\n\n"
            for point in context['pain_points']:
                report += f"- {point}\n"
                
        return report
        
    def save_checkpoint_report(self, report: str):
        """
        保存檢查點報告
        Save checkpoint report
        """
        # 如果文件已存在，追加內容
        if self.checkpoint_file.exists():
            existing = self.checkpoint_file.read_text()
            report = existing + "\n\n---\n\n" + report
            
        self.checkpoint_file.write_text(report)
        print(f"✅ 檢查點報告已保存: {self.checkpoint_file}")
        
    def generate_mentor_request(self, context: dict) -> dict:
        """
        生成 Mentor 請求
        Generate Mentor request
        """
        request = {
            "message_type": "mentor_request",
            "session_id": "charlie_main",
            "request_type": "checkpoint_review",
            "context": {
                "current_task": f"學徒檢查點 - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "recent_actions": context['recent_activity'],
                "decision_history": f"最近處理了 {len(context['current_projects'])} 個專案",
                "pain_points": context['pain_points'],
                "priority": "medium"
            },
            "specific_questions": [
                q['question'] for q in self.generate_checkpoint_questions(context)
            ]
        }
        return request
        
    def run(self) -> dict:
        """
        執行學徒檢查點
        Run apprentice checkpoint
        
        Returns:
            dict: 檢查點結果
        """
        print("🔄 學徒檢查點開始...")
        
        # 1. 收集上下文
        print("📊 收集上下文...")
        context = self.gather_checkpoint_context()
        
        # 2. 生成報告
        print("📝 生成報告...")
        report = self.format_checkpoint_report(context)
        
        # 3. 保存報告
        self.save_checkpoint_report(report)
        
        # 4. 生成 Mentor 請求
        print("🤖 準備 Mentor 請求...")
        mentor_request = self.generate_mentor_request(context)
        
        result = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "report_saved": str(self.checkpoint_file),
            "mentor_request": mentor_request
        }
        
        print("✅ 學徒檢查點完成")
        return result


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="執行學徒檢查點")
    parser.add_argument("--dry-run", action="store_true", help="只生成報告，不調用 Mentor")
    args = parser.parse_args()
    
    checkpoint = ApprenticeCheckpoint()
    result = checkpoint.run()
    
    # 打印結果
    print("\n" + "="*60)
    print("檢查點結果")
    print("="*60)
    print(f"狀態: {result['status']}")
    print(f"時間: {result['timestamp']}")
    print(f"報告: {result['report_saved']}")
    
    if not args.dry_run:
        print("\n🤖 Mentor 請求:")
        print(json.dumps(result['mentor_request'], indent=2, ensure_ascii=False))
    else:
        print("\n⏭️  Dry run 模式：未生成 Mentor 請求")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
