#!/usr/bin/env python3
"""
Obsidian 記憶系統整合

這個腳本將現有的記憶系統整合到 Obsidian CLI。

整合內容：
1. 更新記憶存儲函數
2. 更新記憶搜索函數
3. 添加連結分析到記憶系統
4. 創建遷移腳本
"""

import shutil
from pathlib import Path
from obsidian_memory import ObsidianMemory
import logging

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ObsidianIntegration:
    """Obsidian 整合器"""

    def __init__(self):
        """初始化整合器"""
        self.memory = ObsidianMemory()
        self.workspace_path = Path("/Users/charlie/.openclaw/workspace")
        self.memory_path = self.workspace_path / "memory"
        self.obsidian_path = Path("/Users/charlie/.openclaw/workspace/quant/research")

        # 創建 Obsidian 資料夾結構
        self.obsidian_memory_path = self.obsidian_path / "Memory"
        self.obsidian_daily_path = self.obsidian_path / "Daily Notes"
        self.obsidian_topics_path = self.obsidian_path / "Topics"

        # 確保資料夾存在
        self.obsidian_memory_path.mkdir(parents=True, exist_ok=True)
        self.obsidian_daily_path.mkdir(parents=True, exist_ok=True)
        self.obsidian_topics_path.mkdir(parents=True, exist_ok=True)

    def migrate_memory_file(self, source_path: str, dest_name: str) -> str:
        """
        遷移記憶檔案

        參數:
            source_path: 來源檔案路徑
            dest_name: 目標檔案名稱

        返回:
            遷移結果
        """
        source = Path(source_path)
        dest = self.obsidian_memory_path / dest_name

        if not source.exists():
            logger.warning(f"Source file not found: {source}")
            return f"Skipped: {source} (not found)"

        # 複製檔案
        shutil.copy(source, dest)
        logger.info(f"Migrated: {source} -> {dest}")

        # 更新 Obsidian
        self.obsidian_content = self.memory.read(str(dest.name))
        self.memory.store(
            self.obsidian_content,
            path=str(dest.name),
            category="遷移",
            tags=["migration", "from-workspace"]
        )

        return f"Migrated: {source} -> {dest}"

    def migrate_daily_notes(self) -> dict:
        """
        遷移每日記錄

        返回:
            遷移結果
        """
        if not self.memory_path.exists():
            logger.warning(f"Memory path not found: {self.memory_path}")
            return {"status": "skipped", "reason": "memory path not found"}

        # 找出所有每日記錄
        daily_files = list(self.memory_path.glob("2026-*.md"))
        logger.info(f"Found {len(daily_files)} daily notes")

        results = {
            "total": len(daily_files),
            "migrated": 0,
            "skipped": 0,
            "failed": 0
        }

        for daily_file in daily_files:
            try:
                dest = self.obsidian_daily_path / daily_file.name
                shutil.copy(daily_file, dest)
                logger.info(f"Migrated daily note: {daily_file.name}")
                results["migrated"] += 1
            except Exception as e:
                logger.error(f"Failed to migrate {daily_file.name}: {e}")
                results["failed"] += 1

        return results

    def migrate_topics(self) -> dict:
        """
        遷移主題分類

        返回:
            遷移結果
        """
        topics_path = self.memory_path / "topics"

        if not topics_path.exists():
            logger.warning(f"Topics path not found: {topics_path}")
            return {"status": "skipped", "reason": "topics path not found"}

        # 找出所有主題檔案
        topic_files = list(topics_path.glob("*.md"))
        logger.info(f"Found {len(topic_files)} topic files")

        results = {
            "total": len(topic_files),
            "migrated": 0,
            "skipped": 0,
            "failed": 0
        }

        for topic_file in topic_files:
            try:
                dest = self.obsidian_topics_path / topic_file.name
                shutil.copy(topic_file, dest)
                logger.info(f"Migrated topic: {topic_file.name}")
                results["migrated"] += 1
            except Exception as e:
                logger.error(f"Failed to migrate {topic_file.name}: {e}")
                results["failed"] += 1

        return results

    def create_workspace_backup(self) -> str:
        """
        創建工作區備份

        返回:
            備份路徑
        """
        from datetime import datetime

        # 創建備份目錄
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.workspace_path / f"backup_{timestamp}"

        # 複製 memory 目錄
        if self.memory_path.exists():
            shutil.copytree(self.memory_path, backup_path / "memory")
            logger.info(f"Backup created: {backup_path}")

            return str(backup_path)
        else:
            logger.warning("Memory path not found, skipping backup")
            return "skipped"

    def run_full_migration(self) -> dict:
        """
        執行完整遷移

        返回:
            遷移結果
        """
        logger.info("Starting full migration...")

        # 創建備份
        backup_path = self.create_workspace_backup()

        # 遷移每日記錄
        daily_results = self.migrate_daily_notes()

        # 遷移主題分類
        topics_results = self.migrate_topics()

        # 遷移 MEMORY.md
        memory_md_result = self.migrate_memory_file(
            str(self.workspace_path / "MEMORY.md"),
            "MEMORY.md"
        )

        # 總結
        results = {
            "status": "completed",
            "backup": backup_path,
            "daily": daily_results,
            "topics": topics_results,
            "memory_md": memory_md_result
        }

        logger.info("Migration completed!")
        return results

    def print_migration_summary(self, results: dict):
        """
        打印遷移摘要

        參數:
            results: 遷移結果
        """
        print("\n" + "=" * 60)
        print("Obsidian 整合 - 遷移摘要")
        print("=" * 60)

        print(f"\n狀態: {results['status']}")
        print(f"備份路徑: {results['backup']}")

        if "daily" in results:
            print(f"\n每日記錄:")
            print(f"  總數: {results['daily']['total']}")
            print(f"  已遷移: {results['daily']['migrated']}")
            print(f"  失敗: {results['daily']['failed']}")

        if "topics" in results:
            print(f"\n主題分類:")
            print(f"  總數: {results['topics']['total']}")
            print(f"  已遷移: {results['topics']['migrated']}")
            print(f"  失敗: {results['topics']['failed']}")

        if "memory_md" in results:
            print(f"\nMEMORY.md:")
            print(f"  {results['memory_md']}")

        print("\n" + "=" * 60)
        print("遷移完成！✅")
        print("=" * 60 + "\n")


def main():
    """主函數"""
    print("開始 Obsidian 整合...\n")

    # 創建整合器
    integrator = ObsidianIntegration()

    # 執行完整遷移
    results = integrator.run_full_migration()

    # 打印摘要
    integrator.print_migration_summary(results)

    # Vault 統計
    print("\nVault 統計:")
    stats = integrator.memory.get_vault_stats()
    print(f"  總檔案數: {stats['total_files']}")
    print(f"  孤立檔案: {stats['orphans']}")
    print(f"  總標籤數: {stats['total_tags']}")


if __name__ == "__main__":
    main()
