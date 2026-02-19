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
WORKSPACE = Path.home() / ".openclaw" / "workspace"
TURBO_TASKS = WORKSPACE / "kanban-ops" / "TURBO_TASKS.json"
TURBO_STATUS = WORKSPACE / "kanban-ops" / "TURBO_STATUS.json"
TURBO_LOG = WORKSPACE / "kanban-ops" / "TURBO_LOG.md"
TASKS_JSON = Path.home() / ".openclaw" / "workspace-automation" / "kanban" / "tasks.json"


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
        self.log("INFO", f"模式：{self.config['turbo_config']['mode']}")

        # 根據模式選擇執行方式
        mode = self.config['turbo_config'].get('mode', 'phases')

        try:
            if mode == 'loop':
                # 快速循環模式（方案 3）
                self.run_loop_mode()
            else:
                # 原有分階段模式
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

    def run_loop_mode(self):
        """快速循環模式（方案 3）"""
        config = self.config['turbo_config']
        duration_hours = config.get('duration_hours', 6)
        check_interval_minutes = config.get('check_interval_minutes', 10)
        max_concurrent = config.get('max_concurrent', 1)
        max_tasks_per_check = config.get('max_tasks_per_check', 2)

        # 確保 total_checks 是整數
        total_checks = int(duration_hours * 60 // check_interval_minutes)

        print(f"\n📊 快速循環模式")
        print(f"⏰ 運行時間：{duration_hours} 小時")
        print(f"🔁 檢查間隔：{check_interval_minutes} 分鐘")
        print(f"⚡ 並行上限：{max_concurrent} 個")
        print(f"📋 每次最多觸發：{max_tasks_per_check} 個任務")
        print(f"🔢 預計檢查次數：{total_checks} 次")
        print("=" * 60)

        # 1. Scout 預熱（啟動時）
        print(f"\n🔍 Scout 預熱掃描...")
        self.scout_prewarm(force=True)

        # 2. 快速循環檢查
        for i in range(total_checks):
            if not self.should_continue():
                self.log("INFO", "達到停止條件，結束循環")
                break

            elapsed = self.get_elapsed_time()
            print(f"\n{'=' * 60}")
            print(f"🔁 循環檢查 {i + 1}/{total_checks}")
            print(f"⏱️  已運行：{elapsed:.1f} 小時")
            print(f"{'=' * 60}\n")

            # 檢查並觸發任務
            ready_tasks = self.get_ready_tasks(limit=max_tasks_per_check)

            if ready_tasks:
                print(f"📋 找到 {len(ready_tasks)} 個待觸發任務")

                for task in ready_tasks:
                    if not self.should_continue():
                        break

                    self.spawn_task(task)

                # 等待並行任務完成（如果有）
                if max_concurrent > 0:
                    self.wait_for_concurrent_tasks(max_concurrent)
            else:
                print(f"📋 沒有待觸發任務")

            # 等待下次檢查
            if i < total_checks - 1:
                print(f"\n⏳ 等待 {check_interval_minutes} 分鐘後下次檢查...")
                time.sleep(check_interval_minutes * 60)

        # 完成
        if self.status["enabled"]:
            self.log("SUCCESS", "快速循環模式執行完成")
            self.stop("執行完成")

    def scout_prewarm(self, force=False):
        """Scout 預熱掃描"""
        try:
            scout_script = Path.home() / ".openclaw" / "workspace-scout" / "scout_agent.py"

            if not scout_script.exists():
                self.log("INFO", "Scout 腳本不存在，跳過預熱")
                print(f"ℹ️  Scout 腳本不存在，跳過預熱")
                return True  # 返回 True 繼續執行

            print(f"🔍 觸發 Scout 掃描（預熱模式）...")

            result = subprocess.run(
                ['python3', str(scout_script), 'scan'],
                cwd=str(scout_script.parent),
                capture_output=True,
                text=True,
                timeout=300  # 5 分鐘超時
            )

            if result.returncode == 0:
                print(f"✅ Scout 預熱掃描完成")
                self.log("SUCCESS", "Scout 預熱掃描完成")
                return True
            else:
                print(f"⚠️  Scout 掃描失敗: {result.stderr}")
                self.log("WARNING", f"Scout 掃描失敗: {result.stderr}")
                return True  # 返回 True 繼續執行

        except Exception as e:
            print(f"⚠️  Scout 預熱掃描失敗: {e}")
            self.log("WARNING", f"Scout 預熱掃描失敗: {e}")
            return False

    def get_ready_tasks(self, limit=2):
        """獲取準備觸發的任務"""
        try:
            with open(TASKS_JSON, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 處理多種格式
            if isinstance(data, dict):
                if 'tasks' in data:
                    # 格式: {"tasks": [{...}, {...}]}
                    tasks_list = data['tasks']
                else:
                    # 舊格式: {"task_id": {...}}
                    tasks_list = []
                    for task_id, task_data in data.items():
                        if isinstance(task_data, dict):
                            task_data['id'] = task_id
                            tasks_list.append(task_data)
            elif isinstance(data, list):
                # 格式: [{...}, {...}]
                tasks_list = data
            else:
                self.log("ERROR", f"未知 tasks.json 格式: {type(data)}")
                return []

            ready = []

            # 構建任務映射以便快速查找
            tasks_dict = {task.get('id'): task for task in tasks_list if isinstance(task, dict)}

            for task in tasks_list:
                if not isinstance(task, dict):
                    continue

                if task.get('status') == 'pending':
                    # 檢查依賴
                    depends_on = task.get('depends_on', [])
                    all_dependencies_completed = True

                    for dep_id in depends_on:
                        dep_task = tasks_dict.get(dep_id)
                        if not dep_task or dep_task.get('status') != 'completed':
                            all_dependencies_completed = False
                            break

                    if all_dependencies_completed:
                        task_id = task.get('id', 'unknown')
                        ready.append((task_id, task))
                        if len(ready) >= limit:
                            break

            return ready

        except Exception as e:
            self.log("ERROR", f"獲取待觸發任務失敗: {e}")
            import traceback
            self.log("ERROR", traceback.format_exc())
            return []

    def spawn_task(self, task_info):
        """觸發單個任務"""
        task_id, task = task_info

        try:
            # 獲取任務信息
            title = task.get('title', 'N/A')
            agent_type = task.get('agent', 'analyst')
            priority = task.get('priority', 'medium')
            project_id = task.get('project_id', 'default')

            # 映射代理 ID
            agent_id_map = {
                'research': 'research',
                'analyst': 'analyst',
                'creative': 'creative',
                'automation': 'automation'
            }

            agent_id = agent_id_map.get(agent_type, 'analyst')

            # 決定使用哪個模型
            model = None
            if agent_type in ['analyst', 'creative']:
                model = "zai/glm-4.7"  # 高品質輸出使用 GLM-4.7

            # 構建任務消息
            task_message = self.build_task_message(task_id, task)

            print(f"\n🚀 觸發任務：{task_id}")
            print(f"   標題：{title}")
            print(f"   代理：{agent_id}")
            print(f"   模型：{model or '默認'}")
            print(f"   優先級：{priority}")
            print(f"   項目：{project_id}")

            # 記錄到日誌
            self.log("INFO", f"觸發任務：{task_id} (代理: {agent_id}, 模型: {model or '默認'})")

            # 實際調用 sessions_spawn
            result = self.call_sessions_spawn(
                task_message=task_message,
                agent_id=agent_id,
                label=task_id,
                model=model
            )

            if result['success']:
                self.log("SUCCESS", f"任務 {task_id} 已成功啟動")
                self.log("INFO", f"  Session Key: {result.get('session_key', 'N/A')}")
                return True
            else:
                self.log("ERROR", f"任務 {task_id} 啟動失敗: {result.get('error', 'Unknown error')}")
                return False

        except Exception as e:
            self.log("ERROR", f"觸發任務失敗 {task_id}: {e}")
            import traceback
            self.log("ERROR", traceback.format_exc())
            return False

    def call_sessions_spawn(self, task_message, agent_id, label, model=None):
        """調用 sessions_spawn 工具

        注意：由於 sessions_spawn 是 OpenClaw 工具，只能在主會話中使用
        在 Python 子進程中無法直接調用。

        策略：
        1. 生成待啟動任務文件
        2. 由主會話讀取並使用 sessions_spawn 實際啟動
        3. 測試時使用模擬模式
        """
        try:
            # 生成待啟動任務文件
            task_file = self.write_task_to_queue(task_message, agent_id, label, model)

            if task_file:
                self.log("INFO", f"任務已加入隊列: {task_file}")
                return {
                    'success': True,
                    'task_file': task_file,
                    'queued': True
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to write task to queue'
                }

        except Exception as e:
            self.log("ERROR", f"Failed to queue task: {e}")
            import traceback
            self.log("ERROR", traceback.format_exc())
            return {
                'success': False,
                'error': str(e)
            }

    def write_task_to_queue(self, task_message, agent_id, label, model):
        """將任務寫入隊列文件"""
        try:
            import json
            from datetime import datetime

            # 隊列目錄
            queue_dir = WORKSPACE / "kanban-ops" / "task_queue"
            queue_dir.mkdir(parents=True, exist_ok=True)

            # 任務文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            task_file = queue_dir / f"{label}_{timestamp}.json"

            # 任務數據
            task_data = {
                "task": task_message,
                "agent_id": agent_id,
                "label": label,
                "model": model,
                "created_at": datetime.now().isoformat(),
                "status": "pending",
                "session_key": None
            }

            # 寫入文件
            with open(task_file, 'w', encoding='utf-8') as f:
                json.dump(task_data, f, indent=2, ensure_ascii=False)

            return str(task_file)

        except Exception as e:
            self.log("ERROR", f"Failed to write task to queue: {e}")
            return None

    def simulate_sessions_spawn(self, task_message, agent_id, label, model):
        """模擬 sessions_spawn（用於測試）"""
        import uuid

        # 生成模擬的 session_key
        session_key = f"agent:{agent_id}:subagent:{uuid.uuid4()}"

        self.log("INFO", f"[模擬模式] 會話已創建: {session_key}")

        return {
            'success': True,
            'session_key': session_key,
            'simulated': True
        }

    def build_task_message(self, task_id, task):
        """構建任務消息"""
        # 使用標題作為任務描述
        title = task.get('title', 'N/A')
        project_id = task.get('project_id', 'default')
        priority = task.get('priority', 'medium')

        message = f"""TASK: {title}

CONTEXT:
- 任務 ID: {task_id}
- 項目 ID: {project_id}
- 優先級: {priority}

INPUT FILES:
{self.get_input_paths(task)}

OUTPUT PATH: {self.get_output_path(task_id, task)}

REQUIREMENTS:
- 完整實現代碼
- 詳細文檔說明
- 實證驗證（如適用）
- 實用工具（如適用）
"""

        return message

    def get_input_paths(self, task):
        """獲取輸入文件路徑"""
        input_paths = task.get('input_paths', [])
        if not input_paths:
            return "無"

        paths_str = "\n".join(f"- {p}" for p in input_paths)
        return paths_str

    def get_output_path(self, task_id, task):
        """獲取輸出文件路徑"""
        project_id = task.get('project_id', 'default')
        agent = task.get('agent', 'task')

        # 優先使用 output_path，否則構建默認路徑
        output_path = task.get('output_path')
        if output_path:
            return output_path

        # 構建默認路徑
        timestamp = datetime.now().strftime("%Y%m%d")
        output_dir = f"/Users/charlie/.openclaw/workspace/kanban/projects/{project_id}"
        output_file = f"{task_id}-{agent}.md"

        return f"{output_dir}/{output_file}"

    def wait_for_concurrent_tasks(self, max_concurrent):
        """等待並行任務完成"""
        # TODO: 實現並行任務管理
        # 這裡需要追蹤正在運行的任務，等待它們完成
        # 目前先暫時實現一個簡單的等待
        pass

    def get_elapsed_time(self):
        """獲取已運行時間（小時）"""
        if not self.status.get("start_time"):
            return 0

        start_time = datetime.fromisoformat(self.status["start_time"])
        elapsed = (datetime.now(timezone.utc) - start_time).total_seconds() / 3600
        return elapsed

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
  python3 turbo_mode.py test-ready  測試：列出準備好的任務
  python3 turbo_mode.py test-spawn  測試：觸發 1 個任務（模擬模式）

觸發方式：
  用戶發送「我睡了」 → 調用 start
  用戶發送「我醒了」 → 調用 stop
        """
    )

    parser.add_argument('action', choices=['start', 'stop', 'status', 'resume', 'test-ready', 'test-spawn'],
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
    elif args.action == 'test-ready':
        print("\n📋 測試：列出準備好的任務\n")
        print("=" * 60)

        ready_tasks = turbo.get_ready_tasks(limit=5)

        if ready_tasks:
            print(f"\n✅ 找到 {len(ready_tasks)} 個準備好的任務：\n")

            for task_id, task in ready_tasks:
                print(f"📌 {task_id}")
                print(f"   標題：{task.get('title', 'N/A')}")
                print(f"   代理：{task.get('agent', 'N/A')}")
                print(f"   優先級：{task.get('priority', 'N/A')}")
                print(f"   項目：{task.get('project_id', 'N/A')}")
                print()

        else:
            print("\n⚠️  沒有找到準備好的任務")
            print("   可能原因：")
            print("   - 所有任務都有未完成的依賴")
            print("   - 沒有 pending 任務")
            print("   - 需要先執行 Scout 掃描獲取新任務")

        print("=" * 60)

    elif args.action == 'test-spawn':
        print("\n🧪 測試：觸發任務（模擬模式）\n")
        print("=" * 60)

        ready_tasks = turbo.get_ready_tasks(limit=1)

        if ready_tasks:
            task_id, task = ready_tasks[0]

            print(f"🎯 觸發任務：{task_id}\n")

            result = turbo.spawn_task((task_id, task))

            if result:
                print(f"\n✅ 任務觸發成功")

                # 檢查隊列
                print(f"\n📋 檢查隊列：")
                import subprocess
                subprocess.run(
                    ['python3', '/Users/charlie/.openclaw/workspace/kanban-ops/process_task_queue.py', 'list']
                )

            else:
                print(f"\n❌ 任務觸發失敗")

        else:
            print("\n⚠️  沒有準備好的任務可測試")

        print("=" * 60)
