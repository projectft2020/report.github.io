#!/usr/bin/env python3
"""
研究報告優化器 v1 - 標籤系統優化

功能：
1. 優化標籤提取邏輯
2. 創建更精細的主題分類
3. 添加連結類型（papers → strategies 應用）
4. 重構主題文件結構
5. 創建知識圖譜
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Set
from collections import defaultdict


class ResearchOptimizer:
    """研究報告優化器"""
    
    def __init__(self, obsidian_path="~/Documents/Obsidian Vault"):
        self.obsidian_path = Path(obsidian_path).expanduser()
        self.research_dir = self.obsidian_path / "Research"
        self.topics_dir = self.research_dir / "Topics"
        
        # 標籤分類系統
        self.tag_categories = {
            "methodology": ["machine-learning", "deep-learning", "ml", "ai", "neural-network"],
            "strategy": ["strategy", "trading", "momentum", "mean-reversion", "trend-following"],
            "risk": ["risk", "risk-management", "risk-control", "position-sizing"],
            "market": ["market-structure", "market-microstructure", "liquidity", "volatility"],
            "asset": ["equity", "futures", "options", "crypto", "forex", "bond"],
            "analysis": ["backtest", "backtesting", "technical-analysis", "fundamental-analysis"],
            "quant": ["quantitative", "quant", "factor-investing", "multi-factor"],
            "research": ["paper", "research-paper", "arxiv", "empirical"]
        }
        
        # 連結類型定義
        self.link_types = {
            "citation": "引用",
            "application": "應用",
            "definition": "定義",
            "example": "案例",
            "extension": "擴展"
        }
        
        # 統計數據
        self.stats = {
            "total_files": 0,
            "tags_added": 0,
            "links_created": 0,
            "topics_updated": 0
        }
    
    def optimize_all(self):
        """優化所有研究報告"""
        
        print("🚀 開始優化研究報告...")
        print("=" * 50)
        
        # 掃描所有研究報告
        research_files = []
        for dir_name in ["Papers", "Strategies", "Summaries", "Projects", "Reports"]:
            dir_path = self.research_dir / dir_name
            if dir_path.exists():
                files = list(dir_path.glob("*.md"))
                research_files.extend(files)
                print(f"📁 {dir_name}: {len(files)} 個文件")
        
        print(f"\n📝 總共 {len(research_files)} 個研究報告")
        print("=" * 50)
        
        # 分析現有標籤
        existing_tags = self.analyze_existing_tags(research_files)
        print(f"\n🏷️  現有標籤: {len(existing_tags)} 個")
        
        # 優化每個文件
        for i, file_path in enumerate(research_files, 1):
            print(f"\n[{i}/{len(research_files)}] 優化: {file_path.name}")
            
            try:
                self.optimize_file(file_path, existing_tags)
                self.stats["total_files"] += 1
            except Exception as e:
                print(f"  ❌ 優化失敗: {e}")
        
        # 重構主題文件
        print("\n" + "=" * 50)
        print("🔗 重構主題文件...")
        print("=" * 50)
        self.rebuild_topics()
        
        # 創建知識圖譜
        print("\n" + "=" * 50)
        print("📊 創建知識圖譜...")
        print("=" * 50)
        self.create_knowledge_graph()
        
        # 打印統計
        print("\n" + "=" * 50)
        print("📊 優化統計")
        print("=" * 50)
        print(f"總文件數: {self.stats['total_files']} 個")
        print(f"添加標籤: {self.stats['tags_added']} 個")
        print(f"創建連結: {self.stats['links_created']} 個")
        print(f"更新主題: {self.stats['topics_updated']} 個")
        print("=" * 50)
    
    def analyze_existing_tags(self, files: List[Path]) -> Set[str]:
        """分析現有標籤"""
        
        existing_tags = set()
        
        for file_path in files:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 提取 Frontmatter 中的標籤
            tag_match = re.search(r'tags: \[(.*?)\]', content, re.DOTALL)
            if tag_match:
                tags_str = tag_match.group(1)
                tags = re.findall(r'"([^"]+)"', tags_str)
                existing_tags.update(tags)
        
        return existing_tags
    
    def optimize_file(self, file_path: Path, existing_tags: Set[str]):
        """優化單個文件"""
        
        # 讀取文件
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 提取現有 Frontmatter
        frontmatter_start = content.find("---")
        if frontmatter_start == -1:
            print(f"  ⚠️  沒有 Frontmatter，跳過")
            return
        
        frontmatter_end = content.find("---", frontmatter_start + 3)
        if frontmatter_end == -1:
            print(f"  ⚠️  Frontmatter 格式錯誤，跳過")
            return
        
        # 解析現有標籤
        frontmatter = content[frontmatter_start:frontmatter_end + 3]
        tag_match = re.search(r'tags: \[(.*?)\]', frontmatter, re.DOTALL)
        
        existing_file_tags = set()
        if tag_match:
            tags_str = tag_match.group(1)
            tags = re.findall(r'"([^"]+)"', tags_str)
            existing_file_tags = set(tags)
        
        # 提取標題和內容
        title_match = re.search(r'title: "([^"]+)"', frontmatter)
        title = title_match.group(1) if title_match else file_path.stem
        
        body_content = content[frontmatter_end + 3:]
        
        # 優化標籤
        new_tags = self.optimize_tags(body_content, title, existing_file_tags)
        
        # 檢查是否有新標籤
        added_tags = new_tags - existing_file_tags
        if added_tags:
            print(f"  ➕ 新增標籤: {', '.join(added_tags)}")
            self.stats["tags_added"] += len(added_tags)
            
            # 更新 Frontmatter
            if tag_match:
                formatted_tags = ', '.join([f'"{tag}"' for tag in sorted(new_tags)])
                updated_frontmatter = frontmatter.replace(
                    tag_match.group(0),
                    f"tags: [{formatted_tags}]"
                )
                updated_content = updated_frontmatter + body_content
                
                # 寫回文件
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(updated_content)
        else:
            print(f"  ✅ 標籤已優化（無新增）")
    
    def optimize_tags(self, content: str, title: str, existing_tags: Set[str]) -> Set[str]:
        """優化標籤"""
        
        # 從現有標籤開始
        tags = set(existing_tags)
        
        # 優化的關鍵詞映射（更精確）
        keyword_map = {
            # 方法論
            "機器學習": ["machine-learning", "ml", "deep-learning"],
            "深度學習": ["deep-learning", "neural-network"],
            "神經網絡": ["neural-network"],
            "聯邦學習": ["federated-learning", "machine-learning"],
            "強化學習": ["reinforcement-learning", "machine-learning"],
            
            # 策略類型
            "動量": ["momentum", "trend-following"],
            "趨勢": ["trend-following"],
            "均值回歸": ["mean-reversion"],
            "配對交易": ["pairs-trading", "statistical-arb"],
            "統計套利": ["statistical-arb"],
            "協整": ["cointegration", "statistical-arb"],
            "套利": ["arbitrage", "arbitrage-trading"],
            
            # 風險管理
            "風險": ["risk", "risk-management"],
            "風控": ["risk-control", "risk-management"],
            "倉位": ["position-sizing", "risk-management"],
            "凱利": ["kelly-criterion", "position-sizing", "risk-management"],
            "止損": ["stop-loss", "risk-management"],
            "回撤": ["drawdown", "risk-management"],
            
            # 市場分析
            "微結構": ["market-microstructure", "market-structure"],
            "流動性": ["liquidity", "market-structure"],
            "波動率": ["volatility", "risk"],
            "相關性": ["correlation", "risk-management"],
            
            # 資產類別
            "股票": ["equity"],
            "期貨": ["futures", "derivative"],
            "期權": ["options", "derivative"],
            "加密": ["crypto", "blockchain"],
            "外匯": ["forex"],
            "債券": ["bond"],
            
            # 分析方法
            "回測": ["backtest", "backtesting"],
            "技術分析": ["technical-analysis", "technical"],
            "基本面": ["fundamental-analysis"],
            "技術指標": ["indicator", "technical"],
            "蒙特卡洛": ["monte-carlo", "backtesting"],
            
            # 量化
            "量化": ["quantitative", "quant"],
            "多因子": ["multi-factor", "factor-investing"],
            "因子": ["factor-investing"],
            
            # 研究類型
            "論文": ["paper", "research-paper"],
            "arxiv": ["paper", "arxiv"],
            "實證": ["empirical", "research-paper"],
            
            # 特定策略
            "supertrend": ["supertrend", "indicator", "technical"],
            "rsi": ["rsi", "indicator", "technical"],
            "macd": ["macd", "indicator", "technical"],
            
            # 系統
            "系統": ["system", "architecture"],
            "監控": ["monitoring", "system"],
            "自動化": ["automation", "system"],
            "scout": ["scout", "automation"],
            "kanban": ["kanban", "system"]
        }
        
        # 從內容提取
        lower_content = content.lower()
        lower_title = title.lower()
        
        for keyword, tags_list in keyword_map.items():
            if keyword in lower_content or keyword in lower_title:
                tags.update(tags_list)
        
        # 智能補充（根據標籤之間的關係）
        tags = self.smart_tag_completion(tags)
        
        return tags
    
    def smart_tag_completion(self, tags: Set[str]) -> Set[str]:
        """智能標籤補充"""
        
        # 標籤關係映射
        tag_relations = {
            "machine-learning": ["deep-learning", "ml", "ai"],
            "deep-learning": ["machine-learning", "neural-network"],
            "pairs-trading": ["statistical-arb", "cointegration", "mean-reversion"],
            "cointegration": ["statistical-arb", "pairs-trading"],
            "trend-following": ["momentum", "technical-analysis"],
            "backtest": ["backtesting", "empirical"],
            "risk-management": ["risk-control", "position-sizing"],
            "quantitative": ["quant", "multi-factor"],
            "technical": ["technical-analysis", "indicator"],
            "futures": ["derivative"],
            "options": ["derivative"]
        }
        
        # 根據現有標籤補充相關標籤
        for tag in list(tags):
            if tag in tag_relations:
                tags.update(tag_relations[tag])
        
        return tags
    
    def rebuild_topics(self):
        """重構主題文件"""
        
        # 掃描所有研究報告
        research_files = []
        for dir_name in ["Papers", "Strategies", "Summaries", "Projects", "Reports"]:
            dir_path = self.research_dir / dir_name
            if dir_path.exists():
                files = list(dir_path.glob("*.md"))
                research_files.extend(files)
        
        # 按標籤分類
        topic_map = defaultdict(list)
        for file_path in research_files:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 提取標題和類型
            title_match = re.search(r'title: "([^"]+)"', content)
            title = title_match.group(1) if title_match else file_path.stem
            
            type_match = re.search(r'type: "([^"]+)"', content)
            doc_type = type_match.group(1) if type_match else "summary"
            
            # 提取標籤
            tag_match = re.search(r'tags: \[(.*?)\]', content, re.DOTALL)
            if tag_match:
                tags_str = tag_match.group(1)
                tags = re.findall(r'"([^"]+)"', tags_str)
                
                for tag in tags:
                    topic_map[tag].append({
                        "path": f"Research/{doc_type.capitalize()}s/{file_path.name}",
                        "title": title,
                        "type": doc_type
                    })
        
        # 重構每個主題文件
        for tag, papers in topic_map.items():
            tag_safe = tag.replace(" ", "-")
            topic_path = self.topics_dir / f"{tag_safe}.md"
            
            # 按類型分組
            papers_by_type = defaultdict(list)
            for paper in papers:
                papers_by_type[paper["type"]].append(paper)
            
            # 創建主題內容
            topic_content = f"""# {tag.replace("-", " ").title()}

## 研究論文（Papers）

"""
            
            if "paper" in papers_by_type:
                for paper in papers_by_type["paper"]:
                    topic_content += f"- [[{paper['path']}|{paper['title']}]]\n"
            else:
                topic_content += "*暫無研究論文*\n"
            
            topic_content += "\n## 策略研究（Strategies）\n\n"
            
            if "strategy" in papers_by_type:
                for paper in papers_by_type["strategy"]:
                    topic_content += f"- [[{paper['path']}|{paper['title']}]]\n"
            else:
                topic_content += "*暫無策略研究*\n"
            
            topic_content += "\n## 項目報告（Projects）\n\n"
            
            if "project" in papers_by_type:
                for paper in papers_by_type["project"]:
                    topic_content += f"- [[{paper['path']}|{paper['title']}]]\n"
            else:
                topic_content += "*暫無項目報告*\n"
            
            topic_content += "\n## 分析報告（Reports）\n\n"
            
            if "report" in papers_by_type or "analysis" in papers_by_type:
                for paper_type in ["report", "analysis"]:
                    if paper_type in papers_by_type:
                        for paper in papers_by_type[paper_type]:
                            topic_content += f"- [[{paper['path']}|{paper['title']}]]\n"
            else:
                topic_content += "*暫無分析報告*\n"
            
            topic_content += "\n## 其他報告（Summaries）\n\n"
            
            if "summary" in papers_by_type:
                for paper in papers_by_type["summary"]:
                    topic_content += f"- [[{paper['path']}|{paper['title']}]]\n"
            else:
                topic_content += "*暫無其他報告*\n"
            
            topic_content += "\n## 相關主題\n\n"
            
            # 查找相關主題
            related_tags = self.find_related_tags(tag, topic_map.keys())
            for related_tag in related_tags:
                related_tag_safe = related_tag.replace(" ", "-")
                topic_content += f"- [[Research/Topics/{related_tag_safe}.md|{related_tag.replace('-', ' ').title()}]]\n"
            
            topic_content += "\n## 筆記\n\n*在此添加關於 " + tag.replace("-", " ") + " 的筆記*\n"
            
            # 寫入文件
            with open(topic_path, "w", encoding="utf-8") as f:
                f.write(topic_content)
            
            print(f"  ✅ 重構主題: {tag_safe}")
            self.stats["topics_updated"] += 1
    
    def find_related_tags(self, tag: str, all_tags: Set[str]) -> List[str]:
        """查找相關標籤"""
        
        # 標籤相似度映射
        tag_similarity = {
            "machine-learning": ["deep-learning", "ml", "ai", "neural-network"],
            "deep-learning": ["machine-learning", "ml", "neural-network"],
            "risk": ["risk-management", "risk-control", "position-sizing"],
            "trading": ["strategy", "momentum", "trend-following"],
            "quantitative": ["quant", "multi-factor", "factor-investing"],
            "backtest": ["backtesting", "empirical"],
            "technical": ["technical-analysis", "indicator"],
            "futures": ["derivative"],
            "options": ["derivative"],
            "pairs-trading": ["statistical-arb", "cointegration"]
        }
        
        if tag in tag_similarity:
            related = tag_similarity[tag]
            # 過濾出存在的標籤
            related = [t for t in related if t in all_tags]
            return related
        else:
            return []
    
    def create_knowledge_graph(self):
        """創建知識圖譜"""
        
        # 創建知識圖譜文件
        graph_path = self.research_dir / "KNOWLEDGE_GRAPH.md"
        
        graph_content = """# 知識圖譜

## 核心主題

### 方法論
- [[Research/Topics/machine-learning.md]]
- [[Research/Topics/deep-learning.md]]
- [[Research/Topics/neural-network.md]]
- [[Research/Topics/reinforcement-learning.md]]

### 策略類型
- [[Research/Topics/strategy.md]]
- [[Research/Topics/momentum.md]]
- [[Research/Topics/trend-following.md]]
- [[Research/Topics/mean-reversion.md]]
- [[Research/Topics/pairs-trading.md]]
- [[Research/Topics/statistical-arb.md]]

### 風險管理
- [[Research/Topics/risk.md]]
- [[Research/Topics/risk-management.md]]
- [[Research/Topics/position-sizing.md]]
- [[Research/Topics/kelly-criterion.md]]

### 市場分析
- [[Research/Topics/market-structure.md]]
- [[Research/Topics/market-microstructure.md]]
- [[Research/Topics/liquidity.md]]
- [[Research/Topics/volatility.md]]

### 資產類別
- [[Research/Topics/equity.md]]
- [[Research/Topics/futures.md]]
- [[Research/Topics/options.md]]
- [[Research/Topics/crypto.md]]
- [[Research/Topics/forex.md]]

### 分析方法
- [[Research/Topics/backtest.md]]
- [[Research/Topics/backtesting.md]]
- [[Research/Topics/technical-analysis.md]]
- [[Research/Topics/fundamental-analysis.md]]
- [[Research/Topics/indicator.md]]

### 量化
- [[Research/Topics/quantitative.md]]
- [[Research/Topics/quant.md]]
- [[Research/Topics/multi-factor.md]]
- [[Research/Topics/factor-investing.md]]

## 連結類型

### 引用（Citation）
- Papers → Papers（論文之間的引用關係）
- Papers → Strategies（論文應用到策略）

### 應用（Application）
- Papers → Projects（理論應用到實踐）
- Strategies → Projects（策略實施）

### 定義（Definition）
- Topics → Papers（主題定義在論文中）
- Topics → Strategies（主題定義在策略中）

### 案例（Example）
- Projects → Papers（項目驗證論文）
- Projects → Strategies（項目實施策略）

### 擴展（Extension）
- Papers → Papers（擴展研究）
- Strategies → Strategies（策略改進）

## 使用說明

### 查看知識圖譜
1. 打開 Obsidian
2. 點擊左側邊欄的「Graph View」
3. 設置過濾器，只顯示 `Research/` 目錄
4. 查看知識網絡結構

### 搜索相關研究
1. 使用 Ctrl+Shift+F（全局搜索）
2. 輸入標籤或關鍵詞
3. 點擊搜索結果查看連結

### 瀏覽相關知識
1. 打開任何研究報告
2. 點擊 Frontmatter 中的標籤
3. 系統會自動跳轉到相關主題
4. 從主題瀏覽所有相關研究

---

**最後更新：** 2026-03-09
**文檔版本：** v1.0
"""

        with open(graph_path, "w", encoding="utf-8") as f:
            f.write(graph_content)
        
        print(f"  ✅ 創建知識圖譜: KNOWLEDGE_GRAPH.md")


# 使用示例
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="研究報告優化器 v1")
    parser.add_argument("--obsidian-path", default="~/Documents/Obsidian Vault", help="Obsidian vault 路徑")
    
    args = parser.parse_args()
    
    # 擴展路徑
    obsidian_path = Path(args.obsidian_path).expanduser()
    
    # 創建優化器
    optimizer = ResearchOptimizer(obsidian_path=str(obsidian_path))
    
    # 執行優化
    optimizer.optimize_all()
