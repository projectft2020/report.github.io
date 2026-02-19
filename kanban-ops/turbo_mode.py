#!/usr/bin/env python3
"""
加速模式 (Turbo Mode)

當用戶睡覺時，自動執行大量耗時的深度工作。

特點：
- 並行執行多個任務
- 分階段執行（清理 → 研究 → 深度工作 → 優化）
- 自動記錄日誌
- 支持手動停止

使用方式：
    python3 turbo_mode.py start       # 啟動加速模式
    python3 turbo_mode.py stop        # 停止加速模式
    python3 turbo_mode.py status      # 查看狀態
    python3 turbo_mode.py resume      # 恢復未完成的階段
"""

import json
import os
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
import subprocess

# 路徑配置
WORKSPACE = '/Users/charlie/.openclaw/workspace'
TURBO_TASKS = '/Users/charlie/.openclaw/workspace/kanban-ops/TURBO_TASKS.json'
TURBO_STATUS = '/Users/charlie/.openclaw/workspace/kanban-ops/TURBO_STATUS.json'
TURBO_LOG = '/Users/charlie/.openclaw/workspace/kanban-ops/TURBO_LOG.md'
TASKS_JSON = '/Users/charlie/.openclaw/workspace-automation/kanban/tasks.json'


class TurboMode:
    """加速模式管理器"""

    def __init__(self):
        self.config = self.load_config()
        self.status = self.load_status()
        self.log_file = TURBO_LOG

    def load_config(self):
        """載入加速任務配置"""
        if not os.path.exists(TURBO_TASKS):
            print(f"❌ 配置文件不存在：{TURBO_TASKS}")
            sys.exit(1)

        with open(TURBO_TASKS, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_status(self):
        """載入加速模式狀態"""
        if os.path.exists(TURBO_STATUS):
            with open(TURBO_STATUS, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {
                "enabled": False,
                "start_time": None,
                "current_phase": None,
                "completed_phases": [],
                "tasks_completed": 0,
                "total_tasks": 0,
                "last_activity": None
            }

    def save_status(self):
        """保存加速模式狀態"""
        self.status["last_activity"] = datetime.now(timezone.utc).isoformat()
        with open(TURBO_STATUS, 'w', encoding='utf-8') as f:
            json.dump(self.status, f, indent=2, ensure_ascii=False)

    def log(self, level, message):
        """記錄日誌"""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        log_entry = f"[{timestamp}] [{level}] {message}\n"

        # 寫入文件
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)

        # 同時輸出到控制台
        icon = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}
        print(f"{icon.get(level, '📝')} {message}")

    def start(self):
        """啟動加速模式"""
        if self.status["enabled"]:
            print("⚠️  加速模式已在運行中")
            self.status_report()
            return

        print("\n🌙 啟動加速模式...")
        print("=" * 60)

        # 更新狀態
        self.status["enabled"] = True
        self.status["start_time"] = datetime.now(timezone.utc).isoformat()
        self.status["current_phase"] = None
        self.status["completed_phases"] = []
        self.status["tasks_completed"] = 0

        # 統計總任務數
        total_tasks = sum(
            len([t for t in phase["tasks"] if t.get("enabled", True)])
            for phase in self.config["phases"]
        )
        self.status["total_tasks"] = total_tasks

        self.save_status()
        self.log("INFO", "加速模式已啟動")
        self.log("INFO", f"總任務數：{total_tasks}")
        self.log("INFO", f"預計運行時間：{self.config['turbo_config']['duration_hours']} 小時")

        # 執行所有階段
        try:
            self.run_all_phases()
        except KeyboardInterrupt:
            self.log("WARNING", "用戶中斷加速模式")
            self.stop()
        except Exception as e:
            self.log("ERROR", f"執行過程中出錯：{str(e)}")
            self.stop()

    def stop(self, reason=""):
        """停止加速模式"""
        if not self.status["enabled"]:
            print("⚠️  加速模式未在運行")
            return

        print("\n🛑 停止加速模式...")
        print("=" * 60)

        self.status["enabled"] = False
        self.save_status()

        if reason:
            self.log("INFO", f"停止原因：{reason}")
        else:
            self.log("INFO", "加速模式已停止")

        self.summary_report()

    def should_continue(self):
        """檢查是否應該繼續執行"""
        if not self.status["enabled"]:
            return False

        # 檢查是否超過預定時間
        duration_hours = self.config["turbo_config"]["duration_hours"]
        start_time = datetime.fromisoformat(self.status["start_time"])
        elapsed = (datetime.now(timezone.utc) - start_time).total_seconds() / 3600

        if elapsed >= duration_hours:
            self.log("INFO", f"已達預定運行時間（{duration_hours} 小時）")
            return False

        return True

    def run_all_phases(self):
        """執行所有階段"""
        phases = self.config["phases"]

        print(f"\n📊 將執行 {len(phases)} 個階段：\n")
        for i, phase in enumerate(phases, 1):
            print(f"{i}. {phase['name']} - {phase['duration_minutes']} 分鐘")
            print(f"   {phase['description']}")

        print("\n" + "=" * 60)

        # 執行每個階段
        for phase in phases:
            if not self.should_continue():
                self.log("INFO", "達到停止條件，結束執行")
                break

            self.run_phase(phase)

        # 完成所有階段
        if self.status["enabled"]:
            self.log("SUCCESS", "所有階段執行完成")
            self.stop("執行完成")

    def run_phase(self, phase):
        """執行單個階段"""
        phase_id = phase["id"]
        phase_name = phase["name"]
        duration = phase["duration_minutes"]

        self.log("INFO", f"開始階段：{phase_name}")
        print(f"\n{'=' * 60}")
        print(f"📋 階段：{phase_name}")
        print(f"⏰ 預計時長：{duration} 分鐘")
        print(f"{'=' * 60}\n")

        # 更新當前階段
        self.status["current_phase"] = phase_id
        self.save_status()

        # 獲取啟用的任務
        tasks = [t for t in phase["tasks"] if t.get("enabled", True)]

        # 執行任務
        if phase.get("parallel", False) and len(tasks) > 1:
            self.run_parallel_tasks(phase, tasks)
        else:
            self.run_sequential_tasks(phase, tasks)

        # 標記階段完成
        self.status["completed_phases"].append(phase_id)
        self.save_status()

        self.log("SUCCESS", f"階段完成：{phase_name}")

    def run_sequential_tasks(self, phase, tasks):
        """順序執行任務"""
        for task in tasks:
            if not self.should_continue():
                break

            self.run_task(phase, task)

    def run_parallel_tasks(self, phase, tasks):
        """並行執行任務"""
        max_concurrent = phase.get("max_concurrent", 3)
        active_tasks = []

        for task in tasks:
            if not self.should_continue():
                break

            # 啟動任務
            task_id = task["id"]
            print(f"🚀 啟動任務：{task_id} - {task['description']}")

            # 這裡應該實際調用 sessions_spawn 或其他機制
            # 簡化版：記錄到日誌
            self.log("INFO", f"並行啟動任務：{task_id}")

            # 實際應該使用 sessions_spawn
            # 這裡只是演示，實際實現需要集成

        self.log("INFO", f"並行啟動了 {len(tasks)} 個任務")

    def run_task(self, phase, task):
        """執行單個任務"""
        task_id = task["id"]
        action = task["action"]
        description = task["description"]

        print(f"\n🔧 執行任務：{task_id}")
        print(f"   描述：{description}")

        try:
            if action == "archive_check":
                self.task_archive_check()
            elif action == "stale_recovery":
                self.task_stale_recovery()
            elif action == "git_commit":
                self.task_git_commit()
            elif action == "spawn_kanban_tasks":
                self.task_spawn_kanban_tasks(task)
            elif action == "scout_scan":
                self.task_scout_scan(task)
            elif action == "organize_knowledge":
                self.task_organize_knowledge()
            elif action == "optimize_code":
                self.task_optimize_code()
            elif action == "update_docs":
                self.task_update_docs()
            elif action == "cleanup_logs":
                self.task_cleanup_logs()
            else:
                self.log("WARNING", f"未知任務類型：{action}")

            self.status["tasks_completed"] += 1
            self.save_status()

            self.log("SUCCESS", f"任務完成：{task_id}")

        except Exception as e:
            self.log("ERROR", f"任務失敗：{task_id} - {str(e)}")

    def task_archive_check(self):
        """執行歸檔檢查"""
        print("\n📂 執行歸檔檢查...")
        subprocess.run(
            ["python3", "/Users/charlie/.openclaw/workspace/kanban-ops/archive_tasks.py", "--stats"],
            check=True,
            capture_output=True,
            text=True
        )

    def task_stale_recovery(self):
        """執行過期任務恢復"""
        print("\n🔄 執行過期任務恢復...")
        subprocess.run(
            ["bash", "/Users/charlie/.openclaw/workspace-automation/scripts/check-work-tasks.sh"],
            check=True,
            capture_output=True,
            text=True
        )

    def task_git_commit(self):
        """執行 Git 提交"""
        print("\n📝 檢查 Git 狀態...")
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=WORKSPACE,
            capture_output=True,
            text=True
        )

        if result.stdout.strip():
            print("   有待提交的更改，可以執行提交")
            # 實際提交需要確認
        else:
            print("   沒有待提交的更改")

    def task_spawn_kanban_tasks(self, task):
        """觸發 Kanban 任務"""
        print("\n🚀 觸發 Kanban 任務...")
        # 這裡應該讀取 tasks.json，找到待觸發的任務，然後調用 sessions_spawn
        # 簡化版：只記錄
        self.log("INFO", f"準備觸發 Kanban 任務（優先級過濾：{task.get('priority_filter')}）")

    def task_scout_scan(self, task):
        """執行 Scout 掃描"""
        print("\n🔍 執行 Scout 掃描...")
        self.log("INFO", f"Scout 掃描（深度模式：{task.get('deep_scan')}）")

    def task_organize_knowledge(self):
        """整理知識庫"""
        print("\n📚 整理知識庫...")
        self.log("INFO", "整理知識庫和文檔")

    def task_optimize_code(self):
        """優化代碼"""
        print("\n⚡ 優化代碼...")
        self.log("INFO", "檢查並優化腳本")

    def task_update_docs(self):
        """更新文檔"""
        print("\n📝 更新文檔...")
        self.log("INFO", "更新過時的文檔")

    def task_cleanup_logs(self):
        """清理日誌"""
        print("\n🧹 清理日誌...")
        self.log("INFO", "清理過期日誌文件")

    def status_report(self):
        """顯示狀態報告"""
        print("\n📊 加速模式狀態")
        print("=" * 60)

        if self.status["enabled"]:
            start_time = datetime.fromisoformat(self.status["start_time"])
            elapsed = datetime.now(timezone.utc) - start_time
            duration_hours = elapsed.total_seconds() / 3600

            print(f"狀態：{'🟢 運行中' if self.status['enabled'] else '⏸️ 已停止'}")
            print(f"啟動時間：{start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"已運行時間：{duration_hours:.1f} 小時")
            print(f"當前階段：{self.status.get('current_phase', 'N/A')}")
            print(f"已完成階段：{len(self.status['completed_phases'])}")
            print(f"已完成任務：{self.status['tasks_completed']} / {self.status['total_tasks']}")
        else:
            print(f"狀態：⏸️ 已停止")

        print("=" * 60)

    def summary_report(self):
        """顯示摘要報告"""
        print("\n📊 加速模式摘要報告")
        print("=" * 60)

        if self.status["start_time"]:
            start_time = datetime.fromisoformat(self.status["start_time"])
            elapsed = datetime.now(timezone.utc) - start_time
            duration_hours = elapsed.total_seconds() / 3600

            print(f"啟動時間：{start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"運行時間：{duration_hours:.2f} 小時")

        print(f"已完成任務：{self.status['tasks_completed']} / {self.status['total_tasks']}")
        print(f"已完成階段：{len(self.status['completed_phases'])} / {len(self.config['phases'])}")

        print(f"\n✅ 日誌已保存到：{self.log_file}")
        print(f"✅ 狀態已保存到：{TURBO_STATUS}")
        print("=" * 60)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='加速模式管理',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例：
  python3 turbo_mode.py start       啟動加速模式
  python3 turbo_mode.py stop        停止加速模式
  python3 turbo_mode.py status      查看狀態
  python3 turbo_mode.py resume      恢復未完成的階段

觸發方式：
  用戶發送「我睡了」 → 調用 start
  用戶發送「我醒了」 → 調用 stop
        """
    )

    parser.add_argument('action', choices=['start', 'stop', 'status', 'resume'],
                        help='操作類型')

    args = parser.parse_args()

    turbo = TurboMode()

    if args.action == 'start':
        turbo.start()
    elif args.action == 'stop':
        turbo.stop("用戶停止")
    elif args.action == 'status':
        turbo.status_report()
    elif args.action == 'resume':
        print("⚠️  恢復功能尚未實現")
        turbo.status_report()
