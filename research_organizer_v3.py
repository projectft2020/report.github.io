#!/usr/bin/env python3
"""
研究報告整理器 v3 - 完整版本

功能：
1. 掃描所有研究報告（kanban/outputs, kanban/projects, analysis-reports, 根目錄）
2. 解析報告內容
3. 添加 Frontmatter
4. 直接寫入文件
5. 分類到 Topics
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


class CompleteResearchOrganizer:
    """完整研究報告整理器"""
    
    def __init__(self, obsidian_path="~/Documents/Obsidian Vault"):
        self.obsidian_path = Path(obsidian_path).expanduser()
        self.workspace = Path("~/.openclaw/workspace").expanduser()
        
        # 研究報告目錄
        self.source_dirs = [
            self.workspace / "kanban" / "outputs",           # 已遷移：28 個
            self.workspace / "kanban" / "projects",          # 未遷移：272 個
            self.workspace / "analysis-reports",             # 未遷移：1 個
        ]
        
        # 統計數據
        self.stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "skipped": 0,
            "already_migrated": 0
        }
        
        # 創建 Obsidian 目錄
        self.obsidian_dirs = {
            "papers": self.obsidian_path / "Research" / "Papers",
            "strategies": self.obsidian_path / "Research" / "Strategies",
            "summaries": self.obsidian_path / "Research" / "Summaries",
            "projects": self.obsidian_path / "Research" / "Projects",
            "reports": self.obsidian_path / "Research" / "Reports",
            "topics": self.obsidian_path / "Research" / "Topics"
        }
        
        for dir_name, path in self.obsidian_dirs.items():
            path.mkdir(parents=True, exist_ok=True)
    
    def migrate_all(self, limit=None):
        """遷移所有研究報告"""
        
        print("🚀 開始遷移所有研究報告...")
        print("=" * 50)
        
        # 掃描所有 Markdown 文件
        all_files = []
        for source_dir in self.source_dirs:
            if source_dir.exists():
                print(f"📁 掃描目錄: {source_dir}")
                md_files = list(source_dir.rglob("*.md"))
                print(f"   找到 {len(md_files)} 個 .md 文件")
                all_files.extend(md_files)
            else:
                print(f"⚠️  目錄不存在: {source_dir}")
        
        # 掃描根目錄的報告文件
        print(f"📁 掃描根目錄報告")
        report_files = list(self.workspace.glob("*report*.md"))
        analysis_files = list(self.workspace.glob("*analysis*.md"))
        root_files = report_files + analysis_files
        print(f"   找到 {len(root_files)} 個根目錄報告")
        all_files.extend(root_files)
        
        # 過濾測試文件
        research_files = []
        for file in all_files:
            if "test" not in file.name.lower():
                research_files.append(file)
            else:
                self.stats["skipped"] += 1
        
        # 去重（使用文件路徑）
        seen = set()
        unique_files = []
        for file in research_files:
            file_str = str(file)
            if file_str not in seen:
                seen.add(file_str)
                unique_files.append(file)
        
        research_files = unique_files
        
        # 限制數量
        if limit:
            research_files = research_files[:limit]
            print(f"\n📝 將遷移 {len(research_files)} 個研究報告（限制前 {limit} 個）")
        else:
            print(f"\n📝 將遷移 {len(research_files)} 個研究報告")
        print("=" * 50)
        
        # 遷移每個文件
        for i, file_path in enumerate(research_files, 1):
            print(f"\n[{i}/{len(research_files)}] 處理: {file_path.name}")
            
            try:
                self.migrate_file(file_path)
                self.stats["success"] += 1
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
        print(f"已遷移: {self.stats['already_migrated']} 個")
        print(f"成功率: {self.stats['success']/self.stats['total']*100 if self.stats['total'] > 0 else 0:.1f}%")
        print("=" * 50)
    
    def migrate_file(self, file_path: Path):
        """遷移單個文件"""
        
        # 讀取文件
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="latin-1") as f:
                content = f.read()
        
        # 解析元數據
        metadata = self.parse_metadata(file_path, content)
        
        # 添加 Frontmatter
        frontmatter = self.create_frontmatter(metadata)
        
        # 組合內容
        if "---" in content[:200]:  # 只檢查前 200 個字符
            # 已經有 Frontmatter，只替換
            lines = content.split("\n")
            try:
                end_of_frontmatter = lines.index("---", 1)
                # 替換 Frontmatter
                full_content = "\n".join([frontmatter] + lines[end_of_frontmatter+1:])
            except ValueError:
                # 如果沒有第二個 "---"，直接添加
                full_content = f"{frontmatter}\n\n{content}"
        else:
            # 沒有 Frontmatter，添加
            full_content = f"{frontmatter}\n\n{content}"
        
        # 確定保存位置
        save_dir = self.determine_save_dir(metadata)
        filename = self.generate_filename(metadata)
        
        # 檢查是否已經遷移
        full_path = save_dir / filename
        if full_path.exists():
            print(f"  ⏭️  已遷移，跳過: {full_path.relative_to(self.obsidian_path)}")
            self.stats["already_migrated"] += 1
            return
        
        # 保存文件
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(full_content)
        
        print(f"  ✅ 已遷移到: {full_path.relative_to(self.obsidian_path)}")
        
        # 創建主題連結
        self.create_topic_links(metadata, filename, save_dir)
    
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
            title = file_path.stem.replace("-", " ").replace("_", " ").title()
        
        # 確定類型和來源
        file_str = str(file_path)
        doc_type = "summary"
        
        if "kanban/outputs" in file_str:
            doc_type = "summary"
            source = "kanban-outputs"
        elif "kanban/projects" in file_str:
            doc_type = "project"
            source = "kanban-projects"
        elif "analysis-reports" in file_str:
            doc_type = "analysis"
            source = "analysis-reports"
        elif "report" in file_str.lower() or "analysis" in file_path.name.lower():
            doc_type = "report"
            source = "root-reports"
        elif "research" in title.lower() or "paper" in title.lower():
            doc_type = "paper"
            source = "workspace"
        elif "strategy" in title.lower():
            doc_type = "strategy"
            source = "workspace"
        else:
            source = "workspace"
        
        # 提取標籤
        tags = self.extract_tags(content, title, file_str)
        
        # 元數據
        metadata = {
            "id": safe_id,
            "title": title,
            "type": doc_type,
            "category": self.determine_category(doc_type, file_str),
            "tags": tags,
            "source": source,
            "created": datetime.now().isoformat(),
            "original_file": str(file_path.relative_to(self.workspace))
        }
        
        return metadata
    
    def determine_category(self, doc_type: str, file_str: str) -> str:
        """確定分類"""
        
        if doc_type == "project":
            return "project"
        elif doc_type == "report":
            return "report"
        elif doc_type == "analysis":
            return "analysis"
        elif doc_type == "paper":
            return "paper"
        elif doc_type == "strategy":
            return "strategy"
        else:
            return "research"
    
    def determine_save_dir(self, metadata: Dict[str, Any]) -> Path:
        """確定保存目錄"""
        
        doc_type = metadata["type"]
        
        if doc_type == "paper":
            return self.obsidian_dirs["papers"]
        elif doc_type == "strategy":
            return self.obsidian_dirs["strategies"]
        elif doc_type == "project":
            return self.obsidian_dirs["projects"]
        elif doc_type == "report" or doc_type == "analysis":
            return self.obsidian_dirs["reports"]
        else:
            return self.obsidian_dirs["summaries"]
    
    def generate_filename(self, metadata: Dict[str, Any]) -> str:
        """生成文件名"""
        
        doc_type = metadata["type"]
        safe_id = metadata["id"]
        
        prefix_map = {
            "paper": "paper-",
            "strategy": "strategy-",
            "project": "project-",
            "report": "report-",
            "analysis": "analysis-",
            "summary": "summary-"
        }
        
        prefix = prefix_map.get(doc_type, "summary-")
        filename = f"{prefix}{safe_id}.md"
        
        return filename
    
    def extract_tags(self, content: str, title: str, file_str: str) -> List[str]:
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
            "市場微結構": ["microstructure", "market-structure"],
            "統計套利": ["statistical-arb", "pairs-trading"],
            "區塊鏈": ["blockchain", "crypto"],
            "套利": ["arbitrage", "arbitrage-trading"],
            "arxiv": ["paper", "research-paper"],
            "多因子": ["multi-factor", "factor-investing"]
        }
        
        # 從內容提取
        lower_content = content.lower()
        lower_title = title.lower()
        
        for keyword, tags_list in keyword_map.items():
            if keyword in lower_content or keyword in lower_title or keyword in file_str.lower():
                tags.extend(tags_list)
        
        # 從文件路徑提取
        if "arxiv" in file_str.lower():
            tags.extend(["paper", "research-paper"])
        if "quant-research" in file_str.lower():
            tags.extend(["quantitative", "quant"])
        
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
                if value:  # 只在非空時添加
                    formatted_tags = ', '.join([f'"{v}"' for v in value])
                    frontmatter += f"{key}: [{formatted_tags}]\n"
            else:
                frontmatter += f"{key}: \"{value}\"\n"
        frontmatter += "---"
        
        return frontmatter
    
    def create_topic_links(self, metadata: Dict[str, Any], filename: str, save_dir: Path):
        """創建主題連結"""
        
        # 為每個標籤創建主題筆記
        for tag in metadata["tags"]:
            tag_safe = tag.replace(" ", "-")
            topic_path = self.obsidian_dirs["topics"] / f"{tag_safe}.md"
            
            # 構建連結路徑
            link_path = save_dir.relative_to(self.obsidian_path) / filename
            
            # 檢查是否已經連結過
            link_already_exists = False
            if topic_path.exists():
                with open(topic_path, "r") as f:
                    existing_content = f.read()
                if str(link_path) in existing_content:
                    link_already_exists = True
            
            if link_already_exists:
                continue
            
            # 創建或更新主題筆記
            if not topic_path.exists():
                topic_content = f"""# {tag.title()}

## 相關研究

## 相關策略

## 相關概念

## 筆記

- [[{link_path}|{metadata['title']}]]

"""
                with open(topic_path, "w", encoding="utf-8") as f:
                    f.write(topic_content)
                print(f"    📁 創建主題: Research/Topics/{tag_safe}")
            else:
                # 添加連結
                with open(topic_path, "a", encoding="utf-8") as f:
                    f.write(f"- [[{link_path}|{metadata['title']}]]\n")
                print(f"    🔗 更新主題: Research/Topics/{tag_safe}")


# 使用示例
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="研究報告整理器 v3 - 完整版本")
    parser.add_argument("--obsidian-path", default="~/Documents/Obsidian Vault", help="Obsidian vault 路徑")
    parser.add_argument("--limit", type=int, default=None, help="限制遷移文件數量（用於測試）")
    
    args = parser.parse_args()
    
    # 擴展路徑
    obsidian_path = Path(args.obsidian_path).expanduser()
    
    # 創建整理器
    organizer = CompleteResearchOrganizer(obsidian_path=str(obsidian_path))
    
    # 遷移研究報告
    if args.limit:
        print(f"🔢 測試模式：只遷移前 {args.limit} 個文件\n")
    
    organizer.migrate_all(limit=args.limit)
