#!/usr/bin/env python3
"""
自動改進守護進程 - Auto Improvement Daemon

類似 Felix 的 cron job，每天凌晨自動執行：
1. 收集最近 24 小時的 session files
2. 分析 session files，找出改進點
3. 生成改進建議
4. 應用改進（修改 .md 文件）
5. 記錄改進日誌

核心概念：每天改進 1%，持續複利效果
(1.01)^60 ≈ 1.82x (60天)
(1.01)^365 ≈ 37.8x (一年)
"""

import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import glob
from typing import Dict, List, Optional, Tuple

class AutoImproveDaemon:
    """自動改進守護進程"""

    def __init__(self):
        self.workspace = Path("/Users/charlie/.openclaw/workspace")
        self.kanban_ops = self.workspace / "kanban-ops"
        self.memory_dir = self.workspace / "memory"

        # 改進日誌
        self.improvements_log = self.memory_dir / "improvements.log"
        self.last_improvement_file = self.workspace / ".last_improvement.json"

        # 系統狀態文件
        self.system_files = [
            self.workspace / "SOUL.md",
            self.workspace / "MEMORY.md",
            self.workspace / "USER.md",
            self.workspace / "TOOLS.md",
        ]

        # 加載上次改進時間
        self.last_improvement = self.load_last_improvement()

    def load_last_improvement(self) -> Optional[datetime]:
        """載入上一次改進的時間"""
        try:
            with open(self.last_improvement_file, "r") as f:
                data = json.load(f)
                return datetime.fromisoformat(data.get("timestamp", ""))
        except (FileNotFoundError, json.JSONDecodeError, ValueError):
            return None

    def save_last_improvement(self):
        """保存改進時間"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "daemon": "auto_improve",
        }
        with open(self.last_improvement_file, "w") as f:
            json.dump(data, f, indent=2)

    def should_run(self) -> Tuple[bool, str]:
        """
        檢查是否應該執行

        Returns:
            (should_run, reason)
        """
        if self.last_improvement is None:
            return True, "首次執行"

        time_since_last = datetime.now() - self.last_improvement
        hours_since = time_since_last.total_seconds() / 3600

        if hours_since < 24:
            remaining_hours = 24 - hours_since
            return False, f"距離上次改進還有 {remaining_hours:.1f} 小時"

        return True, f"距離上次改進已過 {hours_since:.1f} 小時"

    def collect_session_files(self) -> List[Path]:
        """
        收集最近 24 小時的 session files

        Returns:
            List of file paths
        """
        session_files = []

        # 掃描 workspace 下的所有 .status 文件
        for status_file in self.workspace.glob("**/.status"):
            # 檢查修改時間
            mtime = datetime.fromtimestamp(status_file.stat().st_mtime)
            if datetime.now() - mtime < timedelta(hours=24):
                session_files.append(status_file)

        # 掃描 kanban/outputs/ 下的 .md 文件
        for output_file in (self.workspace / "kanban" / "outputs").glob("*.md"):
            mtime = datetime.fromtimestamp(output_file.stat().st_mtime)
            if datetime.now() - mtime < timedelta(hours=24):
                session_files.append(output_file)

        # 掃描 memory/ 下的每日記錄
        for memory_file in self.memory_dir.glob("2026-*.md"):
            mtime = datetime.fromtimestamp(memory_file.stat().st_mtime)
            if datetime.now() - mtime < timedelta(hours=24):
                session_files.append(memory_file)

        return sorted(session_files, key=lambda x: x.stat().st_mtime, reverse=True)

    def read_file_content(self, file_path: Path) -> Optional[str]:
        """讀取文件內容"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"❌ 讀取文件失敗 {file_path}: {e}")
            return None

    def analyze_sessions(self, session_files: List[Path]) -> Dict:
        """
        分析 session files，找出改進點

        分析重點：
        1. 錯誤模式（重複出現的錯誤）
        2. 重複任務（可以自動化的）
        3. 效率低點（可以優化的）
        4. 新知識點（需要記錄的）

        Returns:
            分析結果字典
        """
        analysis = {
            "total_files": len(session_files),
            "error_patterns": [],
            "repetitive_tasks": [],
            "inefficiencies": [],
            "new_insights": [],
            "summary": "",
        }

        if not session_files:
            analysis["summary"] = "沒有找到最近的 session files"
            return analysis

        # 讀取所有文件內容
        contents = []
        for file_path in session_files:
            content = self.read_file_content(file_path)
            if content:
                contents.append({
                    "path": str(file_path),
                    "content": content,
                })

        # 分析錯誤模式
        error_keywords = [
            "錯誤", "失敗", "failed", "error", "exception",
            "timeout", "卡住", "stuck", "terminated",
        ]

        for item in contents:
            for keyword in error_keywords:
                if keyword.lower() in item["content"].lower():
                    # 提取上下文
                    context = self.extract_context(item["content"], keyword)
                    analysis["error_patterns"].append({
                        "file": item["path"],
                        "keyword": keyword,
                        "context": context,
                    })

        # 分析重複任務
        task_keywords = [
            "研究", "分析", "回測", "測試", "檢查",
        ]

        for item in contents:
            for keyword in task_keywords:
                if keyword in item["content"]:
                    context = self.extract_context(item["content"], keyword)
                    analysis["repetitive_tasks"].append({
                        "file": item["path"],
                        "keyword": keyword,
                        "context": context,
                    })

        # 分析新知識點
        insight_keywords = [
            "學到", "發現", "洞察", "insight", "learned",
            "關鍵", "重要", "核心",
        ]

        for item in contents:
            for keyword in insight_keywords:
                if keyword in item["content"]:
                    context = self.extract_context(item["content"], keyword)
                    analysis["new_insights"].append({
                        "file": item["path"],
                        "keyword": keyword,
                        "context": context,
                    })

        # 生成總結
        analysis["summary"] = (
            f"分析完成：{len(session_files)} 個文件，"
            f"發現 {len(analysis['error_patterns'])} 個錯誤模式，"
            f"{len(analysis['repetitive_tasks'])} 個重複任務，"
            f"{len(analysis['new_insights'])} 個新知識點"
        )

        return analysis

    def extract_context(self, content: str, keyword: str, max_chars: int = 200) -> str:
        """
        提取關鍵詞周圍的上下文

        Args:
            content: 文件內容
            keyword: 關鍵詞
            max_chars: 最大字符數

        Returns:
            上下文字符串
        """
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if keyword.lower() in line.lower():
                # 取前後幾行
                start = max(0, i - 2)
                end = min(len(lines), i + 3)
                context_lines = lines[start:end]
                context = '\n'.join(context_lines)
                if len(context) > max_chars:
                    context = context[:max_chars] + "..."
                return context
        return ""

    def generate_improvement(self, analysis: Dict) -> Optional[Dict]:
        """
        生成改進建議

        基於分析結果，生成 1 個具體的改進建議

        Returns:
            改進建議字典，如果沒有改進點則返回 None
        """
        if not analysis.get("error_patterns") and not analysis.get("new_insights"):
            print("ℹ️  沒有發現明顯的改進點")
            return None

        improvement = {
            "type": "",
            "target_file": "",
            "change": "",
            "reason": "",
            "priority": "",
        }

        # 優先處理錯誤模式
        if analysis.get("error_patterns"):
            error = analysis["error_patterns"][0]
            improvement["type"] = "fix_error"
            improvement["target_file"] = error["file"]
            improvement["change"] = "添加錯誤處理邏輯"
            improvement["reason"] = f"發現錯誤模式：{error['keyword']}"
            improvement["priority"] = "high"
            return improvement

        # 其次處理新知識點
        if analysis.get("new_insights"):
            insight = analysis["new_insights"][0]
            improvement["type"] = "record_insight"
            improvement["target_file"] = "MEMORY.md"
            improvement["change"] = "添加新知識點到長期記憶"
            improvement["reason"] = f"發現新知識點：{insight['keyword']}"
            improvement["priority"] = "medium"
            return improvement

        return None

    def apply_improvement(self, improvement: Dict) -> bool:
        """
        應用改進

        修改系統文件（.md, .py）或啟動 Agent 處理

        Args:
            improvement: 改進建議

        Returns:
            是否成功
        """
        print(f"\n🔧 應用改進...")
        print(f"   類型: {improvement['type']}")
        print(f"   目標: {improvement['target_file']}")
        print(f"   變更: {improvement['change']}")
        print(f"   原因: {improvement['reason']}")
        print(f"   優先級: {improvement['priority']}")

        # 備份目標文件
        backup_success = self.backup_target_file(improvement["target_file"])
        if not backup_success:
            print(f"⚠️  備份失敗，跳過改進")
            self.log_improvement(improvement, status="backup_failed")
            return False

        # 根據改進類型執行不同的操作
        success = False
        if improvement["type"] == "record_insight":
            success = self.apply_insight_improvement(improvement)
        elif improvement["type"] == "fix_error":
            success = self.apply_error_improvement(improvement)
        else:
            print(f"⚠️  未知的改進類型: {improvement['type']}")
            self.log_improvement(improvement, status="unknown_type")
            return False

        # 驗證改進
        if success and improvement["type"] == "fix_error":
            validation_success = self.validate_improvement(improvement)
            if not validation_success:
                print(f"⚠️  驗證失敗，回滾改進")
                self.rollback_improvement(improvement)
                self.log_improvement(improvement, status="validation_failed")
                return False

        return success

    def backup_target_file(self, target_file: str) -> bool:
        """
        備份目標文件

        Args:
            target_file: 目標文件路徑

        Returns:
            是否成功
        """
        try:
            # 解析相對路徑
            if not target_file.startswith("/"):
                target_path = self.workspace / target_file
            else:
                target_path = Path(target_file)

            if not target_path.exists():
                print(f"   ℹ️  目標文件不存在，跳過備份: {target_file}")
                return True

            # 創建備份目錄
            backup_dir = self.workspace / ".backups" / "improvements"
            backup_dir.mkdir(parents=True, exist_ok=True)

            # 生成備份文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{target_path.name}.{timestamp}.backup"
            backup_path = backup_dir / backup_name

            # 複製文件
            import shutil
            shutil.copy2(target_path, backup_path)
            print(f"   ✅ 備份成功: {backup_path}")

            return True
        except Exception as e:
            print(f"   ❌ 備份失敗: {e}")
            return False

    def rollback_improvement(self, improvement: Dict) -> bool:
        """
        回滾改進

        Args:
            improvement: 改進建議

        Returns:
            是否成功
        """
        try:
            # 解析相對路徑
            target_file = improvement["target_file"]
            if not target_file.startswith("/"):
                target_path = self.workspace / target_file
            else:
                target_path = Path(target_file)

            # 找到最新的備份
            backup_dir = self.workspace / ".backups" / "improvements"
            backups = sorted(backup_dir.glob(f"{target_path.name}.*.backup"), reverse=True)

            if not backups:
                print(f"   ⚠️  沒有找到備份文件")
                return False

            # 恢復最新的備份
            latest_backup = backups[0]
            import shutil
            shutil.copy2(latest_backup, target_path)
            print(f"   ✅ 回滾成功: {latest_backup}")

            return True
        except Exception as e:
            print(f"   ❌ 回滾失敗: {e}")
            return False

    def validate_improvement(self, improvement: Dict) -> bool:
        """
        驗證改進

        檢查改進後的文件是否有效

        Args:
            improvement: 改進建議

        Returns:
            是否驗證通過
        """
        try:
            # 解析相對路徑
            target_file = improvement["target_file"]
            if not target_file.startswith("/"):
                target_path = self.workspace / target_file
            else:
                target_path = Path(target_file)

            # 檢查文件是否存在
            if not target_path.exists():
                print(f"   ❌ 驗證失敗: 文件不存在")
                return False

            # 檢查文件大小
            file_size = target_path.stat().st_size
            if file_size == 0:
                print(f"   ❌ 驗證失敗: 文件為空")
                return False

            # 檢查文件是否為有效的 Markdown（如果是 .md 文件）
            if target_path.suffix == ".md":
                content = target_path.read_text(encoding="utf-8")
                if len(content) < 10:
                    print(f"   ❌ 驗證失敗: 文件內容太少")
                    return False

            print(f"   ✅ 驗證通過: 文件大小 {file_size} bytes")
            return True
        except Exception as e:
            print(f"   ❌ 驗證失敗: {e}")
            return False

    def apply_insight_improvement(self, improvement: Dict) -> bool:
        """應用知識點記錄改進"""
        print(f"📝 將知識點添加到 MEMORY.md")
        print(f"   ℹ️  當前模式：生成改進建議（等待人工確認）")
        print(f"   💡 未來改進：自動啟動 Research Agent 處理")

        # TODO: 自動啟動 Research Agent
        # task_message = f"""
        # TASK: 將以下知識點添加到 MEMORY.md
        #
        # 改進原因：{improvement['reason']}
        # 改進變更：{improvement['change']}
        #
        # OUTPUT PATH: /Users/charlie/.openclaw/workspace/MEMORY.md
        # """
        #
        # # 啟動 Research Agent
        # subprocess.run([
        #     "python3", "-m", "openclaw", "sessions_spawn",
        #     "--agentId", "research",
        #     "--task", task_message,
        #     "--label", f"improve-{improvement['type']}"
        # ])

        # 寫入日誌
        self.log_improvement(improvement, status="pending_agent")

        return True

    def apply_error_improvement(self, improvement: Dict) -> bool:
        """應用錯誤修復改進"""
        print(f"🐛 修復錯誤模式")
        print(f"   ℹ️  當前模式：生成改進建議（等待人工確認）")
        print(f"   💡 未來改進：自動啟動 Developer Agent 處理")

        # TODO: 自動啟動 Developer Agent
        # task_message = f"""
        # TASK: 修復以下錯誤模式
        #
        # 錯誤描述：{improvement['reason']}
        # 目標文件：{improvement['target_file']}
        # 建議變更：{improvement['change']}
        #
        # 請分析錯誤原因，實施修復，並驗證修復效果。
        #
        # OUTPUT PATH: {improvement['target_file']}
        # """
        #
        # # 啟動 Developer Agent
        # subprocess.run([
        #     "python3", "-m", "openclaw", "sessions_spawn",
        #     "--agentId", "developer",
        #     "--task", task_message,
        #     "--label", f"improve-{improvement['type']}"
        # ])

        # 寫入日誌
        self.log_improvement(improvement, status="pending_agent")

        return True

    def log_improvement(self, improvement: Dict, status: str = "applied"):
        """
        記錄改進到日誌文件

        Args:
            improvement: 改進建議
            status: 狀態
        """
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "type": improvement["type"],
            "target_file": improvement["target_file"],
            "change": improvement["change"],
            "reason": improvement["reason"],
            "priority": improvement["priority"],
            "status": status,
        }

        with open(self.improvements_log, "a") as f:
            f.write(f"\n---\n")
            f.write(f"## 改進記錄 [{timestamp}]\n")
            f.write(f"- 類型: {improvement['type']}\n")
            f.write(f"- 目標: {improvement['target_file']}\n")
            f.write(f"- 變更: {improvement['change']}\n")
            f.write(f"- 原因: {improvement['reason']}\n")
            f.write(f"- 優先級: {improvement['priority']}\n")
            f.write(f"- 狀態: {status}\n")

    def run(self, force: bool = False):
        """
        主流程

        Args:
            force: 強制執行（忽略時間檢查）
        """
        print("=" * 60)
        print("🚀 自動改進守護進程啟動")
        print("=" * 60)
        print(f"時間: {datetime.now().isoformat()}")

        # 檢查是否應該執行
        if not force:
            should_run, reason = self.should_run()
            if not should_run:
                print(f"⏭️  跳過: {reason}")
                return

            print(f"✅ 應該執行: {reason}")
        else:
            print(f"⚠️  強制執行模式")

        print()

        # 1. 收集 session files
        print("📂 收集 session files...")
        session_files = self.collect_session_files()
        print(f"   找到 {len(session_files)} 個文件")
        if session_files:
            for f in session_files[:5]:  # 只顯示前 5 個
                print(f"   - {f}")
            if len(session_files) > 5:
                print(f"   ... 還有 {len(session_files) - 5} 個")

        if not session_files:
            print("⚠️  沒有找到 session files，結束")
            return

        print()

        # 2. 分析 session files
        print("🔍 分析 session files...")
        analysis = self.analyze_sessions(session_files)
        print(f"   {analysis['summary']}")

        if analysis.get("error_patterns"):
            print(f"   錯誤模式: {len(analysis['error_patterns'])} 個")
        if analysis.get("repetitive_tasks"):
            print(f"   重複任務: {len(analysis['repetitive_tasks'])} 個")
        if analysis.get("new_insights"):
            print(f"   新知識點: {len(analysis['new_insights'])} 個")

        print()

        # 3. 生成改進建議
        print("💡 生成改進建議...")
        improvement = self.generate_improvement(analysis)

        if not improvement:
            print("ℹ️  沒有發現改進點")
            return

        print()

        # 4. 應用改進
        success = self.apply_improvement(improvement)

        if success:
            print("\n✅ 改進已應用")
            # 5. 記錄改進時間
            self.save_last_improvement()
            print(f"   下次改進: {(datetime.now() + timedelta(hours=24)).isoformat()}")
        else:
            print("\n❌ 改進應用失敗")

        print()
        print("=" * 60)
        print("🎉 自動改進守護進程完成")
        print("=" * 60)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="自動改進守護進程")
    parser.add_argument(
        "action",
        choices=["run", "force", "check", "status"],
        help="操作：run（正常運行）, force（強制執行）, check（檢查是否該執行）, status（顯示狀態）",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="詳細輸出",
    )

    args = parser.parse_args()

    daemon = AutoImproveDaemon()

    if args.action == "run":
        daemon.run(force=False)
    elif args.action == "force":
        daemon.run(force=True)
    elif args.action == "check":
        should_run, reason = daemon.should_run()
        if should_run:
            print(f"✅ 應該執行: {reason}")
        else:
            print(f"⏭️  跳過: {reason}")
    elif args.action == "status":
        print(f"上次改進: {daemon.last_improvement or '從未'}")
        print(f"改進日誌: {daemon.improvements_log}")
        print(f"狀態文件: {daemon.last_improvement_file}")


if __name__ == "__main__":
    main()
