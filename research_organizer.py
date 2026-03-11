#!/usr/bin/env python3
"""
研究報告整理器 - 遷移到 Obsidian

功能：
1. 掃描研究報告（Kanban outputs）
2. 解析報告內容
3. 添加 Frontmatter
4. 創建雙向連結
5. 分類到 Topics
6. 一次性遷移所有論文
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from obsidian_wrapper import ObsidianCLI


class ResearchOrganizer:
    """研究報告整理器"""
    
    def __init__(self, obsidian_path="~/Documents/Obsidian"):
        # 使用當前工作目錄
        import os
        cwd = Path(os.getcwd())
        
        # 初始化 Obsidian CLI
        self.obsidian = ObsidianCLI(vault_path=obsidian_path)
        
        print(f"📁 當前工作目錄: {cwd}")
        
        # 檢查 kanban/outputs 是否存在
        kanban_outputs = cwd / "kanban" / "outputs"
        print(f"📁 Kanban outputs: {kanban_outputs}")
        print(f"   存在: {kanban_outputs.exists()}")
        if kanban_outputs.exists():
            md_files = list(kanban_outputs.glob("*.md"))
            print(f"   .md 文件數: {len(md_files)}")
        
        self.workspace = cwd
        
        # 研究報告目錄
        self.source_dirs = [
            cwd / "kanban" / "outputs",
            cwd / "report",  # 如果存在的話
        ]
        
        # 統計數據
        self.stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "skipped": 0
        }
        
        # 創建 Obsidian 目錄
        self.obsidian_dirs = {
            "papers": "Research/Papers",
            "strategies": "Research/Strategies",
            "summaries": "Research/Summaries",
            "topics": "Research/Topics"
        }
        
        for dir_name, path in self.obsidian_dirs.items():
            full_path = Path(obsidian_path).expanduser() / path
            full_path.mkdir(parents=True, exist_ok=True)
    
    def migrate_all(self, dry_run=False, limit=None):
        """遷移所有研究報告"""
        
        print("🚀 開始遷移所有研究報告...")
        print("=" * 50)
        
        # 掃描所有 Markdown 文件
        all_files = []
        for source_dir in self.source_dirs:
            if source_dir.exists():
                print(f"📁 掃描目錄: {source_dir}")
                dir_files = list(source_dir.glob("*.md"))
                print(f"   找到 {len(dir_files)} 個 .md 文件")
                all_files.extend(dir_files)
                
                py_files = list(source_dir.glob("*.py"))
                print(f"   找到 {len(py_files)} 個 .py 文件")
                all_files.extend(py_files)
            else:
                print(f"⚠️  目錄不存在: {source_dir}")
        
        print(f"\n📊 總共找到 {len(all_files)} 個文件")
        
        # 過濾測試腳本和配置文件
        research_files = []
        for file in all_files:
            # 跳過測試腳本
            if "test" in file.name.lower():
                self.stats["skipped"] += 1
                continue
            
            # 跳過配置文件
            if file.suffix == ".py" and "test" in file.name.lower():
                self.stats["skipped"] += 1
                continue
            
            # 只處理 Markdown 和 Python 文件
            if file.suffix in [".md", ".py"]:
                research_files.append(file)
        
        # 限制數量
        if limit:
            research_files = research_files[:limit]
            print(f"📝 將遷移 {len(research_files)} 個研究報告（限制前 {limit} 個）")
        else:
            print(f"📝 將遷移 {len(research_files)} 個研究報告")
        print("=" * 50)
        
        # 遷移每個文件
        for i, file_path in enumerate(research_files, 1):
            print(f"\n[{i}/{len(research_files)}] 處理: {file_path.name}")
            
            try:
                if dry_run:
                    print(f"  ⏭️  Dry run: 將遷移 {file_path.name}")
                else:
                    self.migrate_file(file_path)
                    self.stats["success"] += 1
                
                self.stats["total"] += 1
                
            except Exception as e:
                print(f"  ❌ 遷移失敗: {e}")
                self.stats["failed"] += 1
                self.stats["total"] += 1
        
        # 打印統計
        print("\n" + "=" * 50)
        print("📊 遷移統計")
        print("=" * 50)
        print(f"總計: {self.stats['total']} 個文件")
        print(f"成功: {self.stats['success']} 個")
        print(f"失敗: {self.stats['failed']} 個")
        print(f"跳過: {self.stats['skipped']} 個")
        print(f"成功率: {self.stats['success']/self.stats['total']*100 if self.stats['total'] > 0 else 0:.1f}%")
        print("=" * 50)
        
        # 保存統計
        self.save_stats()
    
    def migrate_file(self, file_path: Path):
        """遷移單個文件"""
        
        # 讀取文件
        with open(file_path, "r") as f:
            content = f.read()
        
        # 解析元數據
        metadata = self.parse_metadata(file_path, content)
        
        # 添加 Frontmatter
        frontmatter = self.create_frontmatter(metadata)
        
        # 提取連結
        links = self.extract_links(content)
        
        # 創建連結區塊
        link_section = self.create_link_section(links)
        
        # 組合內容
        if "---" in content:
            # 已經有 Frontmatter，只替換
            lines = content.split("\n")
            end_of_frontmatter = lines.index("---", 1)
            # 替換 Frontmatter
            full_content = "\n".join([frontmatter] + lines[end_of_frontmatter+1:])
        else:
            # 沒有 Frontmatter，添加
            full_content = f"{frontmatter}\n\n{content}\n\n{link_section}"
        
        # 確定保存位置
        if metadata["type"] == "paper":
            save_dir = self.obsidian_dirs["papers"]
            filename = f"paper-{metadata['id']}.md"
        elif metadata["type"] == "strategy":
            save_dir = self.obsidian_dirs["strategies"]
            filename = f"strategy-{metadata['id']}.md"
        else:
            save_dir = self.obsidian_dirs["summaries"]
            filename = f"summary-{metadata['id']}.md"
        
        # 保存到 Obsidian
        full_path = f"{save_dir}/{filename}"
        self.obsidian.create(
            name=full_path,
            content=full_content,
            overwrite=True
        )
        
        print(f"  ✅ 已遷移到: {full_path}")
        
        # 創建主題筆記
        self.create_topic_notes(metadata, full_path)
    
    def parse_metadata(self, file_path: Path, content: str) -> Dict[str, Any]:
        """解析元數據"""
        
        # 生成 ID
        file_id = file_path.stem.replace("-", "_")
        safe_id = re.sub(r"[^a-zA-Z0-9]", "-", file_id)[:20]
        
        # 提取標題
        title_match = re.search(r"^# (.+)$", content, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()
        else:
            title = file_path.stem
        
        # 確定類型
        if "research" in title.lower() or "paper" in title.lower():
            doc_type = "paper"
        elif "strategy" in title.lower():
            doc_type = "strategy"
        else:
            doc_type = "summary"
        
        # 提取標籤
        tags = self.extract_tags(content, title)
        
        # 元數據
        metadata = {
            "id": safe_id,
            "title": title,
            "type": doc_type,
            "category": "research",
            "tags": tags,
            "source": "kanban-outputs",
            "created": datetime.now().isoformat(),
            "original_file": str(file_path)
        }
        
        return metadata
    
    def extract_tags(self, content: str, title: str) -> List[str]:
        """提取標籤"""
        
        tags = []
        
        # 關鍵詞映射
        keyword_map = {
            "機器學習": ["machine-learning", "ml", "deep-learning"],
            "量化": ["quantitative", "quant"],
            "策略": ["strategy", "trading"],
            "風險": ["risk", "risk-management"],
            "回測": ["backtest", "backtesting"],
            "期货": ["futures", "derivative"],
            "時間框架": ["timeframe", "time-frame"],
            "技術指標": ["indicator", "technical"],
            "市場微結構": ["microstructure", "market-structure"]
        }
        
        # 從內容提取
        for keyword, tags_list in keyword_map.items():
            if keyword in content.lower() or keyword in title.lower():
                tags.extend(tags_list)
        
        # 去重
        tags = list(set(tags))
        
        return tags
    
    def create_frontmatter(self, metadata: Dict[str, Any]) -> str:
        """創建 Frontmatter"""
        
        frontmatter = "---\n"
        for key, value in metadata.items():
            if key == "original_file":
                continue
            
            if isinstance(value, list):
                formatted_tags = ', '.join([f'"{v}"' for v in value])
                frontmatter += f"{key}: [{formatted_tags}]\n"
            else:
                frontmatter += f"{key}: \"{value}\"\n"
        frontmatter += "---"
        
        return frontmatter
    
    def extract_links(self, content: str) -> Dict[str, List[str]]:
        """提取連結"""
        
        links = {
            "papers": [],
            "strategies": [],
            "concepts": []
        }
        
        # 論文關鍵詞
        paper_keywords = r"(?:paper|論文|Paper|research|研究)\s*[:：]\s*([^\n]+)"
        for match in re.finditer(paper_keywords, content, re.IGNORECASE):
            link_title = match.group(1).strip()
            if link_title and len(link_title) > 2:
                links["papers"].append(link_title)
        
        # 策略關鍵詞
        strategy_keywords = r"(?:strategy|策略|Strategy)\s*[:：]\s*([^\n]+)"
        for match in re.finditer(strategy_keywords, content, re.IGNORECASE):
            link_title = match.group(1).strip()
            if link_title and len(link_title) > 2:
                links["strategies"].append(link_title)
        
        # 概念關鍵詞
        concept_keywords = r"(?:concept|概念|Concept)\s*[:：]\s*([^\n]+)"
        for match in re.finditer(concept_keywords, content, re.IGNORECASE):
            link_title = match.group(1).strip()
            if link_title and len(link_title) > 2:
                links["concepts"].append(link_title)
        
        return links
    
    def create_link_section(self, links: Dict[str, List[str]]) -> str:
        """創建連結區塊"""
        
        if not any(links.values()):
            return ""
        
        section = "## 關聯\n\n"
        
        # 論文連結
        if links["papers"]:
            section += "### 相關研究\n\n"
            for paper in links["papers"][:5]:  # 最多 5 個
                section += f"- [[Research/Papers/{paper.lower().replace(' ', '-')}|{paper}]]\n"
            section += "\n"
        
        # 策略連結
        if links["strategies"]:
            section += "### 相關策略\n\n"
            for strategy in links["strategies"][:5]:  # 最多 5 個
                section += f"- [[Research/Strategies/{strategy.lower().replace(' ', '-')}|{strategy}]]\n"
            section += "\n"
        
        # 概念連結
        if links["concepts"]:
            section += "### 相關概念\n\n"
            for concept in links["concepts"][:5]:  # 最多 5 個
                section += f"- [[Research/Topics/{concept.lower().replace(' ', '-')}|{concept}]]\n"
            section += "\n"
        
        return section
    
    def create_topic_notes(self, metadata: Dict[str, Any], full_path: str):
        """創建主題筆記"""
        
        # 為每個標籤創建主題筆記
        for tag in metadata["tags"]:
            tag_safe = tag.replace(" ", "-")
            topic_path = f"Research/Topics/{tag_safe}"
            
            # 檢查是否存在
            exists = False
            try:
                exists = self.obsidian.note_exists(topic_path)
            except:
                exists = False
            
            if not exists:
                # 創建主題筆記
                topic_content = f"""# {tag.title()}

## 相關研究

- [[{full_path}|{metadata['title']}]]

## 相關策略

## 相關概念

## 筆記

"""
                self.obsidian.create(
                    name=topic_path,
                    content=topic_content,
                    overwrite=False
                )
                print(f"    📁 創建主題: Research/Topics/{tag_safe}")
            else:
                # 添加連結
                try:
                    current_content = self.obsidian.read(topic_path)
                    new_link = f"\n- [[{full_path}|{metadata['title']}]]"
                    updated_content = current_content + new_link
                    self.obsidian.create(
                        name=topic_path,
                        content=updated_content,
                        overwrite=True
                    )
                    print(f"    🔗 更新主題: Research/Topics/{tag_safe}")
                except:
                    print(f"    ⚠️  更新主題失敗: Research/Topics/{tag_safe}")
    
    def save_stats(self):
        """保存統計"""
        
        stats_file = self.workspace / "research_migration_stats.json"
        
        with open(stats_file, "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "stats": self.stats
            }, f, indent=2)
        
        print(f"📊 統計已保存到: {stats_file}")


# 使用示例
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="研究報告整理器")
    parser.add_argument("--dry-run", action="store_true", help="Dry run（不實際遷移）")
    parser.add_argument("--obsidian-path", default="~/Documents/Obsidian", help="Obsidian vault 路徑")
    parser.add_argument("--limit", type=int, default=None, help="限制遷移文件數量（用於測試）")
    
    args = parser.parse_args()
    
    # 擴展路徑
    obsidian_path = Path(args.obsidian_path).expanduser()
    
    # 創建整理器
    organizer = ResearchOrganizer(obsidian_path=str(obsidian_path))
    
    # 遷移研究報告
    if args.limit:
        print(f"🔢 測試模式：只遷移前 {args.limit} 個文件\n")
    
    organizer.migrate_all(dry_run=args.dry_run, limit=args.limit)
