#!/usr/bin/env python3
"""
研究報告整理器 v2 - 直接文件寫入

功能：
1. 掃描研究報告（Kanban outputs）
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


class SimpleResearchOrganizer:
    """簡單研究報告整理器（直接文件寫入）"""
    
    def __init__(self, obsidian_path="~/Documents/Obsidian Vault"):
        self.obsidian_path = Path(obsidian_path).expanduser()
        self.workspace = Path("~/.openclaw/workspace").expanduser()
        
        # 研究報告目錄
        self.source_dirs = [
            self.workspace / "kanban" / "outputs",           # 已遷移
            self.workspace / "kanban" / "projects",          # 272 個文件
            self.workspace / "analysis-reports",             # 1 個文件
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
            "papers": self.obsidian_path / "Research" / "Papers",
            "strategies": self.obsidian_path / "Research" / "Strategies",
            "summaries": self.obsidian_path / "Research" / "Summaries",
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
                md_files = list(source_dir.glob("*.md"))
                print(f"   找到 {len(md_files)} 個 .md 文件")
                all_files.extend(md_files)
            else:
                print(f"⚠️  目錄不存在: {source_dir}")
        
        # 過濾測試文件
        research_files = []
        for file in all_files:
            if "test" not in file.name.lower():
                research_files.append(file)
            else:
                self.stats["skipped"] += 1
        
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
        print(f"成功率: {self.stats['success']/self.stats['total']*100 if self.stats['total'] > 0 else 0:.1f}%")
        print("=" * 50)
    
    def migrate_file(self, file_path: Path):
        """遷移單個文件"""
        
        # 讀取文件
        with open(file_path, "r") as f:
            content = f.read()
        
        # 解析元數據
        metadata = self.parse_metadata(file_path, content)
        
        # 添加 Frontmatter
        frontmatter = self.create_frontmatter(metadata)
        
        # 組合內容
        if "---" in content:
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
        if metadata["type"] == "paper":
            save_dir = self.obsidian_dirs["papers"]
            filename = f"paper-{metadata['id']}.md"
        elif metadata["type"] == "strategy":
            save_dir = self.obsidian_dirs["strategies"]
            filename = f"strategy-{metadata['id']}.md"
        else:
            save_dir = self.obsidian_dirs["summaries"]
            filename = f"summary-{metadata['id']}.md"
        
        # 保存文件
        full_path = save_dir / filename
        with open(full_path, "w") as f:
            f.write(full_content)
        
        print(f"  ✅ 已遷移到: {full_path.relative_to(self.obsidian_path)}")
        
        # 創建主題連結
        self.create_topic_links(metadata, filename)
    
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
    
    def create_topic_links(self, metadata: Dict[str, Any], filename: str):
        """創建主題連結"""
        
        # 為每個標籤創建主題筆記
        for tag in metadata["tags"]:
            tag_safe = tag.replace(" ", "-")
            topic_path = self.obsidian_dirs["topics"] / f"{tag_safe}.md"
            
            # 創建主題筆記
            if not topic_path.exists():
                topic_content = f"""# {tag.title()}

## 相關研究

- [[Research/Summaries/{filename}|{metadata['title']}]]

## 相關策略

## 相關概念

## 筆記

"""
                with open(topic_path, "w") as f:
                    f.write(topic_content)
                print(f"    📁 創建主題: Research/Topics/{tag_safe}")
            else:
                # 添加連結
                with open(topic_path, "a") as f:
                    f.write(f"\n- [[Research/Summaries/{filename}|{metadata['title']}]]")
                print(f"    🔗 更新主題: Research/Topics/{tag_safe}")


# 使用示例
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="研究報告整理器 v2")
    parser.add_argument("--obsidian-path", default="~/Documents/Obsidian Vault", help="Obsidian vault 路徑")
    parser.add_argument("--limit", type=int, default=None, help="限制遷移文件數量（用於測試）")
    
    args = parser.parse_args()
    
    # 擴展路徑
    obsidian_path = Path(args.obsidian_path).expanduser()
    
    # 創建整理器
    organizer = SimpleResearchOrganizer(obsidian_path=str(obsidian_path))
    
    # 遷移研究報告
    if args.limit:
        print(f"🔢 測試模式：只遷移前 {args.limit} 個文件\n")
    
    organizer.migrate_all(limit=args.limit)
