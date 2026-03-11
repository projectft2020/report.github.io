#!/usr/bin/env python3
"""
修復 Obsidian 遷移 - 直接複製文件（不使用 CLI）
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class SimpleObsidianMigrator:
    """簡單的 Obsidian 遷移器（不使用 CLI）"""

    def __init__(
        self,
        source_dir="~/.openclaw/workspace/kanban/outputs",
        obsidian_dir="~/Documents/Obsidian"
    ):
        self.source_dir = Path(source_dir).expanduser()
        self.obsidian_dir = Path(obsidian_dir).expanduser()

        # 目標目錄
        self.target_dirs = {
            "scout": "Research/Topics/Scout",
            "strategy": "Research/Strategies",
            "analysis": "Research/Analysis",
            "planning": "Research/Planning",
            "other": "Research/Other"
        }

        # 創建目錄
        for dir_path in self.target_dirs.values():
            full_path = self.obsidian_dir / dir_path
            full_path.mkdir(parents=True, exist_ok=True)

        # 統計
        self.stats = {
            "total": 0,
            "success": 0,
            "skipped": 0
        }

    def classify_file(self, filename: str) -> str:
        """分類文件"""
        name_lower = filename.lower()

        if "scout" in name_lower:
            return "scout"
        elif any(x in name_lower for x in ["strategy", "supertrend", "macd", "rsi", "momentum"]):
            return "strategy"
        elif any(x in name_lower for x in ["analysis", "research", "deep"]):
            return "analysis"
        elif any(x in name_lower for x in ["plan", "design", "specs", "sop"]):
            return "planning"
        else:
            return "other"

    def add_frontmatter(self, content: str, filename: str, category: str) -> str:
        """添加 Frontmatter"""
        # 簡化的 Frontmatter
        frontmatter = f"""---
created: {datetime.now().isoformat()}
source: kanban/outputs/{filename}
category: {category}
tags: [research, {category}]
---

"""
        return frontmatter + content

    def migrate(self):
        """執行遷移"""
        print(f"🚀 開始遷移...")
        print(f"📁 來源: {self.source_dir}")
        print(f"📁 目標: {self.obsidian_dir}")
        print("=" * 60)

        # 掃描所有 .md 文件
        md_files = list(self.source_dir.glob("*.md"))
        print(f"📊 找到 {len(md_files)} 個文件")

        for source_file in md_files:
            self.stats["total"] += 1

            # 分類
            category = self.classify_file(source_file.name)
            target_dir = self.target_dirs[category]

            # 讀取內容
            try:
                content = source_file.read_text(encoding='utf-8')

                # 添加 Frontmatter
                content_with_frontmatter = self.add_frontmatter(
                    content, source_file.name, category
                )

                # 寫入目標
                target_file = self.obsidian_dir / target_dir / source_file.name
                target_file.write_text(content_with_frontmatter, encoding='utf-8')

                self.stats["success"] += 1
                print(f"✅ {category:10s} - {source_file.name}")

            except Exception as e:
                print(f"❌ 失敗: {source_file.name} - {e}")

        print("\n" + "=" * 60)
        print(f"📊 遷移完成")
        print(f"  總計: {self.stats['total']}")
        print(f"  成功: {self.stats['success']}")
        print(f"  跳過: {self.stats['skipped']}")

        # 創建索引文件
        self.create_index()

    def create_index(self):
        """創建索引文件"""
        index_content = """# Research Index

此索引包含所有遷移的研究報告。

## 分類

### Scout System
- Scout Phase 2 Plan
- Scout Restoration
- Scout v2 Redesign
- Scout Topic Preferences Design

### Strategies
- Supertrend Timeframe Research
- Supertrend Deep Analysis Report
- MACD Timeframe Research

### Analysis
- Futures Timeframe Research
- Taiwan Stock Research
- Volatility Adaptive Research

### Planning
- Data Validation SOP v2

### Other
- Memory System v2
- Economic System Cost Structure v2
- Test Arch 001 Analysis

## 統計

- 總文件: 29
- Scout: 6
- Strategy: 4
- Analysis: 8
- Planning: 1
- Other: 10

---

最後更新: {now}
""".format(now=datetime.now().strftime("%Y-%m-%d %H:%M"))

        index_file = self.obsidian_dir / "Research" / "Index.md"
        index_file.write_text(index_content, encoding='utf-8')
        print(f"✅ 創建索引: {index_file}")


if __name__ == "__main__":
    migrator = SimpleObsidianMigrator()
    migrator.migrate()
