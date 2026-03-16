#!/usr/bin/env python3
"""
Script Scanner - 自動掃描所有腳本並生成 TOOLS_INDEX.md

功能：
1. 掃描所有目錄中的 Python 腳本
2. 提取元數據（docstring、使用模式）
3. 自動分類（core/kanban/scout/tools）
4. 生成/更新 TOOLS_INDEX.md

使用：
    python3 scripts/scanner.py          # 掃描並生成 TOOLS_INDEX.md
    python3 scripts/scanner.py --dry-run  # 預覽模式，不寫入文件
    python3 scripts/scanner.py --stats   # 顯示統計信息

作者：Charlie
日期：2026-03-12
"""

import os
import re
import argparse
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class ScriptMetadata:
    """腳本元數據類別"""

    def __init__(self, path: Path):
        self.path = path
        self.relative_path = path.relative_to(Path.home() / ".openclaw" / "workspace")
        self.name = path.stem
        self.docstring: Optional[str] = None
        self.usage: Optional[str] = None
        self.trigger: Optional[str] = None
        self.functions: List[str] = []
        self.category: str = "tools"

    def parse(self):
        """解析腳本，提取元數據"""
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                content = f.read()
            self._extract_docstring(content)
            self._extract_usage_patterns(content)
            self._detect_category()
        except Exception as e:
            print(f"⚠️  無法解析 {self.path}: {e}")

    def _extract_docstring(self, content: str):
        """提取 docstring"""
        # 提取模組級別 docstring（支援 """ 和 '''）
        match = re.search(r'^("{3}|\'{3})(.*?)\1', content, re.DOTALL)
        if match:
            self.docstring = match.group(2).strip()

        # 如果沒有模組docstring，嘗試提取類docstring
        if not self.docstring:
            class_match = re.search(r'class\s+\w+.*?:\s*("{3}|\'{3})(.*?)\1', content, re.DOTALL)
            if class_match:
                self.docstring = class_match.group(2).strip()

    def _extract_usage_patterns(self, content: str):
        """提取使用模式"""
        # 提取觸發模式（heartbeat, daily, manual等）
        if re.search(r'觸發|trigger|每|按需', content, re.IGNORECASE):
            trigger_patterns = [
                r'(觸發|trigger)[:：\s]*([^\n.]+)',
                r'每次(\w+)',
                r'每(\w+)[：\s]*([^\n.]+)',
                r'(daily|heartbeat|manual|按需)'
            ]
            for pattern in trigger_patterns:
                trigger_match = re.search(pattern, content, re.IGNORECASE)
                if trigger_match:
                    self.trigger = trigger_match.group(0).strip()[:50]  # 限制長度
                    break

        # 提取用途描述
        if self.docstring:
            # 嘗試多種用途模式
            usage_patterns = [
                r'用途[:：\s]*([^\n.]+)',
                r'usage[:：\s]*([^\n.]+)',
                r'功能[:：\s]*([^\n.]+)',
                r'function[:：\s]*([^\n.]+)',
            ]
            for pattern in usage_patterns:
                usage_match = re.search(pattern, self.docstring, re.IGNORECASE)
                if usage_match:
                    self.usage = usage_match.group(1).strip()[:80]  # 限制長度
                    break

        # 如果沒有從docstring提取到用途，從第一行推斷
        if not self.usage and self.docstring:
            first_line = self.docstring.split('\n')[0].strip()
            if first_line and len(first_line) > 10:
                self.usage = first_line[:80]

        # 提取函數名稱
        function_matches = re.findall(r'^def\s+(\w+)\s*\(', content, re.MULTILINE)
        self.functions = function_matches[:5]  # 只顯示前 5 個

    def _detect_category(self):
        """自動分類"""
        path_str = str(self.path).lower()

        # 核心腳本（每次心跳執行）
        if any(x in path_str for x in [
            'auto_spawn_heartbeat',
            'task_sync',
            'task_state_rollback',
            'error_recovery'
        ]):
            self.category = "core"

        # Kanban 腳本
        elif any(x in path_str for x in [
            'kanban-ops',
            'monitor_and_refill',
            'task_cleanup',
            'spawn_tasks'
        ]):
            self.category = "kanban"

        # Scout 腳本
        elif any(x in path_str for x in [
            'scout_agent',
            'workspace-scout'
        ]):
            self.category = "scout"

        # 工具腳本
        else:
            self.category = "tools"

    def get_frequency(self) -> str:
        """推斷使用頻率"""
        if self.category == "core":
            return "高（心跳）"
        elif self.trigger:
            if "心跳" in self.trigger or "heartbeat" in self.trigger.lower():
                return "高（心跳）"
            elif "每天" in self.trigger or "daily" in self.trigger.lower():
                return "高（每天）"
            elif "每週" in self.trigger or "weekly" in self.trigger.lower():
                return "中（每週）"
            else:
                return "中（按需）"
        else:
            return "低（按需）"


class ScriptScanner:
    """腳本掃描器"""

    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.scripts: List[ScriptMetadata] = []
        self.seen_scripts: set = set()  # 避免重複
        self.categories = {
            "core": [],
            "kanban": [],
            "scout": [],
            "tools": []
        }
        # 重要腳本列表（優先索引）
        self.important_scripts = [
            # P0 核心腳本
            "auto_spawn_heartbeat.py",
            "task_sync.py",
            "task_state_rollback.py",
            "error_recovery.py",
            # P1 工具腳本
            "monitor_and_refill.py",
            "task_cleanup.py",
            "spawn_tasks_intelligent.py",
            "scout_agent.py",
            "research_sync_system.py",
            "scanner.py",
        ]

    def scan(self):
        """掃描所有腳本"""
        print("🔍 開始掃描腳本...\n")

        # 掃描的目錄列表（按優先級排序）
        scan_dirs = [
            self.workspace_path / "scripts",  # 符號鏈接目錄（優先）
            self.workspace_path / "kanban-ops",
            self.workspace_path / "workspace-scout",
            self.workspace_path,  # 根目錄腳本
            self.workspace_path / "skills",  # 技能腳本
        ]

        for scan_dir in scan_dirs:
            if not scan_dir.exists():
                continue

            print(f"📂 掃描目錄: {scan_dir.name}")
            self._scan_directory(scan_dir)

        # 過濾：只保留重要腳本
        self._filter_important_scripts()

        # 分類
        for script in self.scripts:
            self.categories[script.category].append(script)

        print(f"\n✅ 找到 {len(self.scripts)} 個腳本（已過濾重複和非重要腳本）\n")

    def _scan_directory(self, directory: Path):
        """掃描單個目錄"""
        for py_file in directory.rglob("*.py"):
            # 跳過 __init__.py 和測試文件
            if py_file.name.startswith("__") or "test" in py_file.name.lower():
                continue

            # 去重：如果腳本名稱已存在，跳過
            if py_file.name in self.seen_scripts:
                continue

            script = ScriptMetadata(py_file)
            script.parse()
            self.scripts.append(script)
            self.seen_scripts.add(py_file.name)

    def _filter_important_scripts(self):
        """過濾：只保留重要腳本"""
        # 如果腳本在重要列表中，保留
        # 如果腳本是P0核心腳本，保留
        # 如果腳本使用頻率高，保留
        important = []
        for script in self.scripts:
            if script.name in self.important_scripts:
                important.append(script)
            elif script.category == "core":
                important.append(script)
            elif script.get_frequency().startswith("高"):
                important.append(script)

        self.scripts = important

    def generate_tools_index(self) -> str:
        """生成 TOOLS_INDEX.md 內容"""
        lines = []

        # 標題
        lines.append("# TOOLS_INDEX.md - 腳本中央索引（自動生成）")
        lines.append("")
        lines.append("> **生成時間：** " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        lines.append("> **腳本數量：** " + str(len(self.scripts)))
        lines.append("> **目標：** 統一索引所有腳本，提升可見性，避免重複造輪子")
        lines.append("")

        # 快速查找表格
        lines.append("## 🚀 快速查找")
        lines.append("")
        lines.append("| 工具類型 | 名稱 | 用途 | 路徑 | 使用頻率 |")
        lines.append("|----------|------|------|------|----------|")

        for category in ["core", "kanban", "scout", "tools"]:
            for script in self.categories[category]:
                lines.append(f"| {category} | {script.name} | {script.usage or '待定'} | {script.relative_path} | {script.get_frequency()} |")

        lines.append("")

        # 分類詳情
        for category in ["core", "kanban", "scout", "tools"]:
            lines.append(f"## 📋 {category.upper()} 腳本")
            lines.append("")

            if not self.categories[category]:
                lines.append("（無腳本）")
                lines.append("")
                continue

            for script in self.categories[category]:
                lines.append(f"### {script.name}")
                lines.append("")
                lines.append(f"- **路徑：** `{script.relative_path}`")
                lines.append(f"- **用途：** {script.usage or '待定'}")
                lines.append(f"- **使用頻率：** {script.get_frequency()}")

                if script.trigger:
                    lines.append(f"- **觸發：** {script.trigger}")

                if script.functions:
                    lines.append(f"- **主要函數：** {', '.join(script.functions[:5])}")

                if script.docstring:
                    # 提取關鍵功能（前兩行）
                    doc_lines = script.docstring.split('\n')[:3]
                    lines.append(f"- **功能：** {doc_lines[0] if doc_lines else '待定'}")

                lines.append("")

        # 統計信息
        lines.append("## 📊 統計信息")
        lines.append("")
        lines.append("| 類別 | 腳本數量 |")
        lines.append("|------|----------|")
        for category in ["core", "kanban", "scout", "tools"]:
            count = len(self.categories[category])
            lines.append(f"| {category} | {count} |")

        lines.append("")
        lines.append(f"| **總計** | **{len(self.scripts)}** |")
        lines.append("")

        # 使用頻率統計
        lines.append("## 📈 使用頻率統計")
        lines.append("")
        freq_stats = {}
        for script in self.scripts:
            freq = script.get_frequency()
            freq_stats[freq] = freq_stats.get(freq, 0) + 1

        for freq, count in sorted(freq_stats.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"- {freq}：{count} 個")

        lines.append("")

        # 維護說明
        lines.append("## 📝 維護說明")
        lines.append("")
        lines.append("### 如何重新生成")
        lines.append("```bash")
        lines.append("cd ~/.openclaw/workspace && python3 scripts/scanner.py")
        lines.append("```")
        lines.append("")
        lines.append("### 預覽模式（不寫入文件）")
        lines.append("```bash")
        lines.append("python3 scripts/scanner.py --dry-run")
        lines.append("```")
        lines.append("")
        lines.append("### 查看統計")
        lines.append("```bash")
        lines.append("python3 scripts/scanner.py --stats")
        lines.append("```")
        lines.append("")

        return "\n".join(lines)

    def print_stats(self):
        """打印統計信息"""
        print("📊 統計信息\n")
        print(f"總計：{len(self.scripts)} 個腳本\n")

        print("按類別：")
        for category in ["core", "kanban", "scout", "tools"]:
            count = len(self.categories[category])
            print(f"  - {category}: {count} 個")

        print("\n按使用頻率：")
        freq_stats = {}
        for script in self.scripts:
            freq = script.get_frequency()
            freq_stats[freq] = freq_stats.get(freq, 0) + 1

        for freq, count in sorted(freq_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {freq}: {count} 個")

        print("\n按目錄：")
        dir_stats = {}
        for script in self.scripts:
            dir_name = script.path.parent.name
            dir_stats[dir_name] = dir_stats.get(dir_name, 0) + 1

        for dir_name, count in sorted(dir_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {dir_name}: {count} 個")


def main():
    parser = argparse.ArgumentParser(description="腳本掃描器 - 自動生成 TOOLS_INDEX.md")
    parser.add_argument("--dry-run", action="store_true", help="預覽模式，不寫入文件")
    parser.add_argument("--stats", action="store_true", help="顯示統計信息")
    args = parser.parse_args()

    # 工作空間路徑
    workspace_path = Path.home() / ".openclaw" / "workspace"

    # 創建掃描器
    scanner = ScriptScanner(workspace_path)

    # 掃描腳本
    scanner.scan()

    # 顯示統計
    if args.stats:
        scanner.print_stats()
        return

    # 生成 TOOLS_INDEX.md
    tools_index = scanner.generate_tools_index()

    # 預覽模式
    if args.dry_run:
        print("📄 預覽 TOOLS_INDEX.md\n")
        print(tools_index)
        return

    # 寫入文件
    output_path = workspace_path / "TOOLS_INDEX.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(tools_index)

    print(f"✅ TOOLS_INDEX.md 已生成：{output_path}")
    print(f"📊 共 {len(scanner.scripts)} 個腳本")


if __name__ == "__main__":
    main()
