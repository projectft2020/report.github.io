#!/usr/bin/env python3
"""
記憶維護主腳本

執行完整的記憶維護流程：
1. 知識提取（掃描 daily logs）
2. 記憶更新（更新 MEMORY.md、SOUL.md）
3. 記憶整理（清理過時記憶）
4. 優化記錄（記錄優化成果）

執行頻率：每週一次

Usage:
    python3 maintain.py                    # 執行完整流程
    python3 maintain.py --dry-run         # 只顯示計劃，不執行
    python3 maintain.py --skip-cleanup     # 跳過清理步驟
"""

import argparse
import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path

# 路徑配置
WORKSPACE = Path("/Users/charlie/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
MEMORY_MD = WORKSPACE / "MEMORY.md"
SOUL_MD = WORKSPACE / "SOUL.md"
TOPICS_DIR = MEMORY_DIR / "topics"

# 顏色輸出
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}\n")


def print_step(step_num, text):
    print(f"{Colors.OKCYAN}[Step {step_num}] {text}{Colors.ENDC}")


def print_success(text):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")


def print_warning(text):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")


def print_info(text):
    print(f"ℹ️  {text}")


def load_json_file(path):
    """載入 JSON 文件"""
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def save_json_file(data, path):
    """保存 JSON 文件"""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def scan_recent_logs(days=7):
    """掃描最近 N 天的 daily logs"""
    print_step(1, f"掃描最近 {days} 天的 daily logs")

    today = datetime.now()
    log_files = []

    for i in range(days):
        date = today - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        log_file = MEMORY_DIR / f"{date_str}.md"

        if log_file.exists():
            log_files.append(log_file)
            print_info(f"  找到: {date_str}.md")

    print_success(f"找到 {len(log_files)} 個 daily log 文件")
    return log_files


def extract_knowledge(log_files):
    """從 daily logs 提取知識"""
    print_step(2, "提取知識和洞察")

    knowledge = {
        "learnings": [],
        "patterns": [],
        "decisions": [],
        "achievements": [],
        "topics": {}
    }

    for log_file in log_files:
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()

            # 提取學習點（### What I've Learned）
            learnings = re.findall(r'### (?:我學到|What I\'ve Learned|學習總結)[\s\S]*?(?=\n### |\n---|$)', content)
            for learning in learnings:
                knowledge["learnings"].append({
                    "date": log_file.stem,
                    "content": learning.strip()
                })

            # 提取模式（### 核心模式）
            patterns = re.findall(r'### (?:核心模式|關鍵洞察|可複用)[\s\S]*?(?=\n### |\n---|$)', content)
            for pattern in patterns:
                knowledge["patterns"].append({
                    "date": log_file.stem,
                    "content": pattern.strip()
                })

            # 提取決策（### 關鍵決策）
            decisions = re.findall(r'### (?:關鍵決策|重要決策|Key Decisions)[\s\S]*?(?=\n### |\n---|$)', content)
            for decision in decisions:
                knowledge["decisions"].append({
                    "date": log_file.stem,
                    "content": decision.strip()
                })

            # 提取成就（### 完成項目）
            achievements = re.findall(r'### (?:完成項目|成就|成就|Achievements)[\s\S]*?(?=\n### |\n---|$)', content)
            for achievement in achievements:
                knowledge["achievements"].append({
                    "date": log_file.stem,
                    "content": achievement.strip()
                })

    print_success(f"提取完成：{len(knowledge['learnings'])} 個學習點")
    print_info(f"  - 模式: {len(knowledge['patterns'])} 個")
    print_info(f"  - 決策: {len(knowledge['decisions'])} 個")
    print_info(f"  - 成就: {len(knowledge['achievements'])} 個")

    return knowledge


def update_memory_md(knowledge):
    """更新 MEMORY.md"""
    print_step(3, "更新 MEMORY.md")

    if not MEMORY_MD.exists():
        print_warning("MEMORY.md 不存在，跳過")
        return

    # 讀取現有內容
    with open(MEMORY_MD, 'r', encoding='utf-8') as f:
        content = f.read()

    # 找到 Update Log 部分並更新
    update_log_pattern = r'(## 📅 Update Log\n)'
    today_str = datetime.now().strftime("%Y-%m-%d")

    # 構建今天的更新記錄
    update_entry = f"""### {today_str} (Today)
- ✅ 記憶維護執行
- ✅ 知識提取：{len(knowledge['learnings'])} 個學習點
- ✅ 模式識別：{len(knowledge['patterns'])} 個核心模式
- ✅ 決策記錄：{len(knowledge['decisions'])} 個關鍵決策

"""

    # 如果今天的記錄已存在，跳過
    if today_str in content:
        print_info(f"  今天的記錄已存在，跳過")
        return

    # 插入更新記錄
    content = re.sub(update_log_pattern, r'\1' + update_entry, content)

    # 寫回文件
    with open(MEMORY_MD, 'w', encoding='utf-8') as f:
        f.write(content)

    print_success("MEMORY.md 已更新")


def update_soul_md(knowledge):
    """更新 SOUL.md"""
    print_step(4, "更新 SOUL.md")

    if not SOUL_MD.exists():
        print_warning("SOUL.md 不存在，跳過")
        return

    # 讀取現有內容
    with open(SOUL_MD, 'r', encoding='utf-8') as f:
        content = f.read()

    # 找到 What I've Learned 部分並更新
    learned_pattern = r'(### What I\'ve Learned \(.*?\)\n)'
    today_str = datetime.now().strftime("%Y-%m-%d")

    # 構建今天的學習記錄
    if knowledge['learnings']:
        learned_entry = f"### What I've Learned ({today_str})\n\n"

        for item in knowledge['learnings'][:5]:  # 只保留最近 5 個
            learned_entry += f"{item['content']}\n\n"

        learned_entry += "---\n\n"

        # 檢查今天的記錄是否已存在
        if today_str not in content:
            # 插入學習記錄
            content = re.sub(learned_pattern, r'\1' + learned_entry, content)

            # 寫回文件
            with open(SOUL_MD, 'w', encoding='utf-8') as f:
                f.write(content)

            print_success("SOUL.md 已更新")
        else:
            print_info("  今天的記錄已存在，跳過")


def organize_topics(knowledge):
    """整理 topics/ 目錄"""
    print_step(5, "整理 topics/ 目錄")

    if not TOPICS_DIR.exists():
        print_warning("topics/ 目錄不存在，跳過")
        return

    # 統計每個主題文件
    topic_files = list(TOPICS_DIR.glob("*.md"))
    print_info(f"  找到 {len(topic_files)} 個主題文件")

    for topic_file in topic_files:
        print_info(f"  - {topic_file.name}")

    print_success("topics/ 整理完成")


def cleanup_old_memory(days=30):
    """清理舊記憶"""
    print_step(6, f"清理超過 {days} 天的舊記憶")

    today = datetime.now()
    cutoff_date = today - timedelta(days=days)

    # 清理舊的 daily logs
    old_logs = []
    for log_file in MEMORY_DIR.glob("*.md"):
        if log_file.name == "MEMORY.md" or log_file.name == "INDEX.md":
            continue

        try:
            date_str = log_file.stem
            log_date = datetime.strptime(date_str, "%Y-%m-%d")
            if log_date < cutoff_date:
                old_logs.append(log_file)
        except ValueError:
            continue

    if old_logs:
        print_warning(f"  找到 {len(old_logs)} 個舊日誌")
        for log_file in old_logs:
            print_info(f"  - {log_file.name}")
    else:
        print_success("  沒有舊日誌需要清理")

    return old_logs


def generate_report(knowledge):
    """生成維護報告"""
    print_step(7, "生成維護報告")

    report = f"""# 記憶維護報告

**執行時間:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 📊 統計摘要

- 📚 學習點: {len(knowledge['learnings'])} 個
- 🔄 核心模式: {len(knowledge['patterns'])} 個
- 🎯 關鍵決策: {len(knowledge['decisions'])} 個
- 🏆 成就: {len(knowledge['achievements'])} 個

## 🔍 最近學習點

"""
    for i, item in enumerate(knowledge['learnings'][:10], 1):
        report += f"{i}. {item['date']}\n"
        report += f"   {item['content'][:100]}...\n\n"

    report += "## 📋 最近模式\n\n"
    for i, item in enumerate(knowledge['patterns'][:5], 1):
        report += f"{i}. {item['date']}\n"
        report += f"   {item['content'][:100]}...\n\n"

    report += "---\n\n"
    report += "**報告生成時間:** " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"

    # 保存報告
    report_file = MEMORY_DIR / f"maintenance-report-{datetime.now().strftime('%Y%m%d')}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print_success(f"維護報告已生成: {report_file.name}")


def main():
    parser = argparse.ArgumentParser(description="記憶維護主腳本")
    parser.add_argument("--dry-run", action="store_true", help="只顯示計劃，不執行")
    parser.add_argument("--skip-cleanup", action="store_true", help="跳過清理步驟")
    parser.add_argument("--days", type=int, default=7, help="掃描最近 N 天的日誌（默認 7 天）")
    args = parser.parse_args()

    print_header("記憶維護系統")

    if args.dry_run:
        print_warning("🔍 Dry run 模式 - 只顯示計劃，不執行")

    # 1. 掃描 recent logs
    log_files = scan_recent_logs(args.days)

    if not log_files:
        print_warning("沒有找到任何 daily log 文件")
        return

    # 2. 提取知識
    knowledge = extract_knowledge(log_files)

    if args.dry_run:
        print_warning("Dry run 完成，跳過實際執行")
        return

    # 3. 更新 MEMORY.md
    update_memory_md(knowledge)

    # 4. 更新 SOUL.md
    update_soul_md(knowledge)

    # 5. 整理 topics/
    organize_topics(knowledge)

    # 6. 清理舊記憶
    if not args.skip_cleanup:
        cleanup_old_memory()

    # 7. 生成報告
    generate_report(knowledge)

    print_header("維護完成 ✅")
    print_info("所有記憶維護任務已完成")


if __name__ == "__main__":
    main()
