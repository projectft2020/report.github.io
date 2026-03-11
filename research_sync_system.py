#!/usr/bin/env python3
"""
Research Report Sync System - 自動同步研究報告到 Obsidian

這個系統會：
1. 掃描 kanban/works/ 目錄，找到新完成的研究報告
2. 從報告中提取元數據（標題、摘要、分類、日期）
3. 根據內容分類到適當的 Obsidian 目錄
4. 更新 INDEX.md，建立連結

使用方式：
    python3 research_sync_system.py scan          # 掃描新報告
    python3 research_sync_system.py sync <id>     # 同步指定報告
    python3 research_sync_system.py sync-all      # 同步所有未同步的報告
    python3 research_sync_system.py status        # 查看同步狀態
"""

import os
import sys
import json
import re
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import hashlib

# 添加工作目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ResearchSyncSystem:
    """研究報告同步系統"""

    def __init__(
        self,
        workspace_path: str = "/Users/charlie/.openclaw/workspace",
        obsidian_vault: str = "/Users/charlie/.openclaw/workspace/quant/research",
        tasks_file: str = "/Users/charlie/.openclaw/workspace/kanban/tasks.json",
        sync_db_path: str = "/Users/charlie/.openclaw/workspace/.research_sync_db.json"
    ):
        """
        初始化同步系統

        參數:
            workspace_path: 工作區路徑
            obsidian_vault: Obsidian vault 路徑
            tasks_file: tasks.json 路徑
            sync_db_path: 同步數據庫路徑（記錄已同步的任務）
        """
        self.workspace_path = Path(workspace_path)
        self.obsidian_vault = Path(obsidian_vault)
        self.tasks_file = Path(tasks_file)
        self.sync_db_path = Path(sync_db_path)
        self.kanban_works = self.workspace_path / "kanban/works"

        # 目錄結構定義
        self.research_categories = {
            "Market-Microstructure": ["market microstructure", "order flow", "liquidity", "bid-ask"],
            "Risk-Management": ["risk", "hedge", "var", "cvar", "tail risk", "crisis", "drawdown"],
            "Strategy-Development": ["strategy", "trading", "backtest", "momentum", "mean reversion"],
            "Empirical-Testing": ["empirical", "testing", "validation", "out-of-sample", "backtest"],
            "Factor-Investing": ["factor", "alpha", "beta", "exposure", "premium"],
            "Machine-Learning": ["machine learning", "neural network", "deep learning", "ai", "model"],
            "Economic-Analysis": ["economic", "macro", "fomc", "inflation", "gdp", "recession"],
            "Crypto-Research": ["crypto", "bitcoin", "ethereum", "blockchain", "defi"]
        }

        # 加載同步數據庫
        self.sync_db = self._load_sync_db()

        logger.info(f"ResearchSyncSystem initialized")
        logger.info(f"Workspace: {self.workspace_path}")
        logger.info(f"Obsidian Vault: {self.obsidian_vault}")

    def _load_sync_db(self) -> Dict[str, Any]:
        """加載同步數據庫"""
        if self.sync_db_path.exists():
            with open(self.sync_db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "last_scan": None,
            "synced_tasks": {},
            "pending_sync": []
        }

    def _save_sync_db(self):
        """保存同步數據庫"""
        with open(self.sync_db_path, 'w', encoding='utf-8') as f:
            json.dump(self.sync_db, f, indent=2, ensure_ascii=False)

    def _load_tasks(self) -> List[Dict[str, Any]]:
        """加載 tasks.json"""
        if not self.tasks_file.exists():
            logger.warning(f"Tasks file not found: {self.tasks_file}")
            return []

        with open(self.tasks_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _extract_metadata(self, report_path: Path) -> Dict[str, Any]:
        """
        從研究報告中提取元數據

        參數:
            report_path: 報告文件路徑

        返回:
            元數據字典
        """
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()

        metadata = {
            "title": "",
            "summary": "",
            "category": "Strategy-Development",  # 默認分類
            "tags": [],
            "date": datetime.now().isoformat(),
            "key_findings": [],
            "source": "kanban"
        }

        # 提取標題（第一個 # 標題）
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            metadata["title"] = title_match.group(1).strip()
        else:
            metadata["title"] = report_path.stem.replace('-', ' ').title()

        # 提取摘要（第一段文字）
        summary_match = re.search(r'(?:^|\n)([A-Z][^.!?]*[.!?])', content)
        if summary_match:
            metadata["summary"] = summary_match.group(1).strip()

        # 提取分類（根據關鍵詞）
        content_lower = content.lower()
        for category, keywords in self.research_categories.items():
            if any(keyword in content_lower for keyword in keywords):
                metadata["category"] = category
                break

        # 提取標籤
        tags = re.findall(r'#(\w+)', content)
        metadata["tags"] = list(set(tags))

        # 提取關鍵發現
        findings = re.findall(r'(?:##|###)\s+(?:關鍵發現|Key Findings|結論|Conclusion)\s*\n(.*?)(?:##|\Z)', content, re.DOTALL)
        if findings:
            metadata["key_findings"] = [
                line.strip()
                for line in findings[0].split('\n')
                if line.strip() and not line.startswith('#')
            ][:5]  # 最多 5 個關鍵發現

        # 計算文件 hash（用於檢測變更）
        metadata["file_hash"] = hashlib.md5(content.encode()).hexdigest()

        return metadata

    def _generate_obsidian_path(self, task_id: str, metadata: Dict[str, Any]) -> Path:
        """
        生成 Obsidian 文件路徑

        參數:
            task_id: 任務 ID
            metadata: 元數據

        返回:
            Obsidian 文件路徑
        """
        category = metadata["category"]
        filename = f"{task_id}.md"

        return self.obsidian_vault / "Research" / category / filename

    def _add_frontmatter(self, content: str, metadata: Dict[str, Any], task_id: str) -> str:
        """
        添加 Obsidian frontmatter

        參數:
            content: 原始內容
            metadata: 元數據
            task_id: 任務 ID

        返回:
            帶 frontmatter 的內容
        """
        frontmatter = {
            "task_id": task_id,
            "title": metadata["title"],
            "category": metadata["category"],
            "tags": metadata["tags"],
            "date": metadata["date"],
            "summary": metadata["summary"][:200] + "..." if len(metadata["summary"]) > 200 else metadata["summary"],
            "source": "kanban"
        }

        frontmatter_str = "---\n"
        for key, value in frontmatter.items():
            if isinstance(value, list):
                frontmatter_str += f"{key}: {json.dumps(value, ensure_ascii=False)}\n"
            else:
                frontmatter_str += f"{key}: {value}\n"
        frontmatter_str += "---\n\n"

        return frontmatter_str + content

    def _update_index(self, category: str, task_id: str, metadata: Dict[str, Any]):
        """
        更新 Research/INDEX.md

        參數:
            category: 分類
            task_id: 任務 ID
            metadata: 元數據
        """
        index_path = self.obsidian_vault / "Research" / "INDEX.md"

        # 創建目錄結構
        category_dir = self.obsidian_vault / "Research" / category
        category_dir.mkdir(parents=True, exist_ok=True)

        # 創建或更新 INDEX.md
        if not index_path.exists():
            index_content = "# Research Reports Index\n\n"
            for cat in self.research_categories.keys():
                index_content += f"## {cat}\n\n"
                index_content += f"See [{cat}/INDEX.md]({cat}/INDEX.md)\n\n"
            index_path.write_text(index_content, encoding='utf-8')

        # 創建或更新分類 INDEX
        category_index_path = category_dir / "INDEX.md"
        if not category_index_path.exists():
            category_index_content = f"# {category} Research Reports\n\n"
            category_index_content += "## Reports\n\n"
        else:
            category_index_content = category_index_path.read_text(encoding='utf-8')

        # 添加新報告到分類 INDEX
        date_str = metadata["date"][:10]
        new_entry = f"- [{date_str}] [{metadata['title']}]({task_id}.md) - {metadata['summary'][:100]}...\n"

        if new_entry not in category_index_content:
            category_index_content += new_entry
            category_index_path.write_text(category_index_content, encoding='utf-8')
            logger.info(f"Updated {category}/INDEX.md with {task_id}")

    def scan_new_reports(self) -> List[Dict[str, Any]]:
        """
        掃描新完成的研究報告

        返回:
            新報告列表
        """
        tasks = self._load_tasks()
        new_reports = []

        for task in tasks:
            # 只處理已完成且未同步的任務
            if task.get("status") != "completed":
                continue

            task_id = task["id"]

            # 檢查是否已同步
            if task_id in self.sync_db["synced_tasks"]:
                continue

            # 檢查報告文件是否存在
            work_dir = self.kanban_works / task_id
            if not work_dir.exists():
                continue

            # 查找報告文件
            report_files = list(work_dir.glob("*-research.md"))
            if not report_files:
                logger.warning(f"No research report found for task {task_id}")
                continue

            report_path = report_files[0]
            metadata = self._extract_metadata(report_path)

            new_reports.append({
                "task_id": task_id,
                "report_path": str(report_path),
                "metadata": metadata,
                "task_data": task
            })

        self.sync_db["last_scan"] = datetime.now().isoformat()
        self.sync_db["pending_sync"] = [r["task_id"] for r in new_reports]
        self._save_sync_db()

        logger.info(f"Scanned {len(new_reports)} new reports")
        return new_reports

    def sync_report(self, task_id: str) -> bool:
        """
        同步單個研究報告

        參數:
            task_id: 任務 ID

        返回:
            是否同步成功
        """
        # 獲取任務信息
        tasks = self._load_tasks()
        task = next((t for t in tasks if t["id"] == task_id), None)

        if not task:
            logger.error(f"Task not found: {task_id}")
            return False

        if task.get("status") != "completed":
            logger.error(f"Task not completed: {task_id}")
            return False

        # 查找報告文件
        work_dir = self.kanban_works / task_id
        report_files = list(work_dir.glob("*-research.md"))

        if not report_files:
            logger.error(f"Research report not found: {task_id}")
            return False

        report_path = report_files[0]

        # 提取元數據
        metadata = self._extract_metadata(report_path)

        # 生成 Obsidian 路徑
        obsidian_path = self._generate_obsidian_path(task_id, metadata)
        obsidian_path.parent.mkdir(parents=True, exist_ok=True)

        # 讀取報告內容
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 添加 frontmatter
        content_with_frontmatter = self._add_frontmatter(content, metadata, task_id)

        # 複製到 Obsidian vault
        obsidian_path.parent.mkdir(parents=True, exist_ok=True)
        obsidian_path.write_text(content_with_frontmatter, encoding='utf-8')
        relative_path = obsidian_path.relative_to(self.obsidian_vault)

        # 更新 INDEX.md
        self._update_index(metadata["category"], task_id, metadata)

        # 記錄到同步數據庫
        self.sync_db["synced_tasks"][task_id] = {
            "synced_at": datetime.now().isoformat(),
            "obsidian_path": str(relative_path),
            "file_hash": metadata["file_hash"],
            "metadata": metadata
        }

        if task_id in self.sync_db["pending_sync"]:
            self.sync_db["pending_sync"].remove(task_id)

        self._save_sync_db()

        logger.info(f"Synced report {task_id} to {relative_path}")
        return True

    def sync_all(self) -> Dict[str, Any]:
        """
        同步所有未同步的報告

        返回:
            同步結果統計
        """
        new_reports = self.scan_new_reports()

        results = {
            "total": len(new_reports),
            "success": 0,
            "failed": 0,
            "skipped": 0,
            "details": []
        }

        for report in new_reports:
            task_id = report["task_id"]
            try:
                success = self.sync_report(task_id)
                if success:
                    results["success"] += 1
                    results["details"].append({"task_id": task_id, "status": "success"})
                else:
                    results["failed"] += 1
                    results["details"].append({"task_id": task_id, "status": "failed"})
            except Exception as e:
                logger.error(f"Failed to sync {task_id}: {e}")
                results["failed"] += 1
                results["details"].append({"task_id": task_id, "status": "error", "error": str(e)})

        return results

    def status(self) -> Dict[str, Any]:
        """
        查看同步狀態

        返回:
            同步狀態信息
        """
        tasks = self._load_tasks()
        completed_tasks = [t for t in tasks if t.get("status") == "completed"]

        return {
            "last_scan": self.sync_db["last_scan"],
            "total_completed": len(completed_tasks),
            "total_synced": len(self.sync_db["synced_tasks"]),
            "pending_sync": len(self.sync_db["pending_sync"]),
            "pending_sync_tasks": self.sync_db["pending_sync"]
        }


def main():
    """主函數"""
    import argparse

    parser = argparse.ArgumentParser(description="Research Report Sync System")
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # scan 命令
    subparsers.add_parser("scan", help="Scan for new reports")

    # sync 命令
    sync_parser = subparsers.add_parser("sync", help="Sync a specific report")
    sync_parser.add_argument("task_id", help="Task ID to sync")

    # sync-all 命令
    subparsers.add_parser("sync-all", help="Sync all pending reports")

    # status 命令
    subparsers.add_parser("status", help="Show sync status")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # 初始化同步系統
    sync_system = ResearchSyncSystem()

    if args.command == "scan":
        new_reports = sync_system.scan_new_reports()
        print(f"\n📊 Found {len(new_reports)} new reports:")
        for report in new_reports:
            metadata = report["metadata"]
            print(f"  - {report['task_id']}: {metadata['title']}")
            print(f"    Category: {metadata['category']}")
            print(f"    Summary: {metadata['summary'][:100]}...")
            print()

    elif args.command == "sync":
        success = sync_system.sync_report(args.task_id)
        if success:
            print(f"✅ Successfully synced {args.task_id}")
        else:
            print(f"❌ Failed to sync {args.task_id}")

    elif args.command == "sync-all":
        print("🔄 Syncing all pending reports...")
        results = sync_system.sync_all()
        print(f"\n📊 Sync Results:")
        print(f"  Total: {results['total']}")
        print(f"  ✅ Success: {results['success']}")
        print(f"  ❌ Failed: {results['failed']}")
        print()

        for detail in results["details"]:
            if detail["status"] == "success":
                print(f"  ✅ {detail['task_id']}")
            else:
                print(f"  ❌ {detail['task_id']}: {detail.get('error', 'Unknown error')}")

    elif args.command == "status":
        status = sync_system.status()
        print(f"\n📊 Sync Status:")
        print(f"  Last Scan: {status['last_scan'] or 'Never'}")
        print(f"  Total Completed: {status['total_completed']}")
        print(f"  Total Synced: {status['total_synced']}")
        print(f"  Pending Sync: {status['pending_sync']}")
        print()

        if status["pending_sync_tasks"]:
            print(f"Pending Tasks:")
            for task_id in status["pending_sync_tasks"]:
                print(f"  - {task_id}")


if __name__ == "__main__":
    main()
