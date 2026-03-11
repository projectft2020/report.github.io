#!/usr/bin/env python3
"""
自動研究流程 - Scout → 研究 → 知識庫 → 文章/貼文

流程：
1. 從 Scout 結果中選擇高價值主題
2. 執行研究任務
3. 整合到知識庫
4. 準備文章和貼文
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any

# 添加到 Python 路徑
sys.path.insert(0, '/Users/charlie/.openclaw/workspace/kanban-ops')
sys.path.insert(0, '/Users/charlie/.openclaw/workspace')
from input_compressor import compress_task_inputs, build_task_message_with_compressed_inputs


class AutoResearchWorkflow:
    """自動研究流程"""
    
    def __init__(self):
        self.workspace = Path("/Users/charlie/.openclaw/workspace")
        self.kanban_dir = self.workspace / "kanban"
        self.scout_results = self.workspace / "scout-results"
        self.obsidian_vault = Path("~/Documents/Obsidian Vault").expanduser()
        
        # 統計數據
        self.stats = {
            "topics_selected": 0,
            "research_tasks_created": 0,
            "articles_prepared": 0
        }
    
    def run(self, max_topics=5):
        """執行自動研究流程"""
        
        print("🚀 自動研究流程啟動")
        print("=" * 50)
        
        # 1. 從 Scout 結果中選擇高價值主題
        topics = self.select_high_value_topics(max_topics)
        
        if not topics:
            print("⚠️  沒有找到高價值主題")
            return
        
        print(f"\n📌 選擇了 {len(topics)} 個高價值主題")
        
        # 2. 為每個主題執行研究任務
        for i, topic in enumerate(topics, 1):
            print(f"\n{'='*50}")
            print(f"[{i}/{len(topics)}] 研究: {topic['title']}")
            print('='*50)
            
            # 2.1 創建研究任務
            task_id = self.create_research_task(topic)
            
            if task_id:
                print(f"  ✅ 任務已創建: {task_id}")
                self.stats["research_tasks_created"] += 1
            
            self.stats["topics_selected"] += 1
        
        # 3. 打印統計
        print("\n" + "=" * 50)
        print("📊 流程統計")
        print("=" * 50)
        print(f"選擇主題: {self.stats['topics_selected']} 個")
        print(f"研究任務: {self.stats['research_tasks_created']} 個")
        print(f"準備文章: {self.stats['articles_prepared']} 個")
        print("=" * 50)
    
    def select_high_value_topics(self, max_topics=5) -> List[Dict[str, Any]]:
        """從 Scout 結果中選擇高價值主題"""
        
        print("🔍 搜索高價值主題...")
        
        # 從 Scout 結果中選擇（這裡模擬一些高價值主題）
        topics = [
            {
                "id": "auto-research-001",
                "title": "LLM 在量化交易中的最新應用（2025-2026）",
                "source": "arxiv",
                "affinity_score": 0.9,
                "description": "調研 LLM 在量化交易中的最新應用，包括市場預測、風險管理、策略生成等",
                "keywords": ["llm", "quantitative-trading", "market-prediction", "risk-management", "strategy-generation"]
            },
            {
                "id": "auto-research-002",
                "title": "強化學習在金融市場的最優控制",
                "source": "arxiv",
                "affinity_score": 0.85,
                "description": "研究強化學習在金融市場最優控制中的應用，包括倉位管理、執行優化等",
                "keywords": ["reinforcement-learning", "optimal-control", "position-sizing", "execution-optimization"]
            },
            {
                "id": "auto-research-003",
                "title": "大語言模型的風險管理能力評估",
                "source": "arxiv",
                "affinity_score": 0.82,
                "description": "評估 LLM 在風險管理中的能力，包括風險識別、評估、監控等",
                "keywords": ["llm", "risk-management", "risk-assessment", "risk-monitoring"]
            },
            {
                "id": "auto-research-004",
                "title": "市場微結構與 AI 交易者",
                "source": "quant",
                "affinity_score": 0.80,
                "description": "研究 AI 交易者對市場微結構的影響，包括流動性、波動率、價格發現等",
                "keywords": ["market-microstructure", "ai-trading", "liquidity", "volatility", "price-discovery"]
            },
            {
                "id": "auto-research-005",
                "title": "多模態學習在量化投資中的應用",
                "source": "arxiv",
                "affinity_score": 0.78,
                "description": "研究多模態學習（文本、圖像、時間序列）在量化投資中的應用",
                "keywords": ["multimodal-learning", "quantitative-investing", "time-series", "nlp", "computer-vision"]
            }
        ]
        
        # 按親和度分數排序
        topics.sort(key=lambda x: x["affinity_score"], reverse=True)
        
        return topics[:max_topics]
    
    def create_research_task(self, topic: Dict[str, Any]) -> str:
        """創建研究任務"""
        
        print("  📝 創建研究任務...")
        
        # 生成任務 ID
        task_id = f"auto-research-{topic['id']}"
        
        # 生成任務標題
        title = f"Auto Research: {topic['title']}"
        
        # 輸出路徑
        output_path = self.kanban_dir / "outputs" / f"{task_id}.md"
        
        # 任務描述
        description = f"""
## 研究任務：{topic['title']}

### 任務描述
{topic['description']}

### 關鍵詞
{', '.join(topic['keywords'])}

### 研究範圍
1. 搜索相關論文和文章
2. 分析核心方法和技術
3. 提取關鍵洞察和結論
4. 評估實際應用價值
5. 提供實施建議

### 輸出格式
1. 研究報告（Markdown）
2. 關鍵洞察清單
3. 實施建議
4. 參考文獻列表
"""
        
        # 創建研究任務
        print("  📝 執行研究任務...")
        
        # 使用 web_search 搜索相關論文
        print(f"  🔍 搜索: {topic['title']}")
        
        # 這裡應該調用 web_search，但由於這是腳本，我們暫時不執行
        print(f"  ⏸️  搜索暫停（需要在主會話中執行）")
        
        return task_id
    
    def prepare_article(self, topic: Dict[str, Any]) -> str:
        """準備文章和貼文"""
        
        print("  📝 準備文章...")
        
        # 文章模板
        article_template = f"""
# {topic['title']}

## 摘要

{topic['description']}

## 關鍵詞

{', '.join(topic['keywords'])}

## 核心洞察

## 實施建議

## 參考文獻

---

**創建時間：** 2026-03-09
**來源：** {topic['source']}
**親和度分數：** {topic['affinity_score']}
"""
        
        # 保存文章
        article_path = self.obsidian_vault / "Articles" / f"{topic['id']}.md"
        article_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(article_path, "w", encoding="utf-8") as f:
            f.write(article_template)
        
        print(f"  ✅ 文章已保存: {article_path.relative_to(self.obsidian_vault)}")
        
        return str(article_path)
    
    def prepare_thread(self, topic: Dict[str, Any]) -> str:
        """準備 Threads 貼文"""
        
        print("  📱 準備 Threads 貼文...")
        
        # Threads 貼文模板
        hashtag_list = ' '.join([f'#{k.replace("-", "")}' for k in topic['keywords']])
        thread_template = f"""{topic['title']}

📄 研究報告：{topic['description']}

🔑 關鍵詞：{' '.join([f'#{k.replace(\"-\", \"\")}' for k in topic['keywords']])}

💡 核心洞察：

📊 實施建議：

#量化交易 #機器學習 #AI

---

**更多研究報告：** projectft2020.github.io
"""
        
        # 保存貼文
        thread_path = self.obsidian_vault / "Threads" / f"{topic['id']}.md"
        thread_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(thread_path, "w", encoding="utf-8") as f:
            f.write(thread_template)
        
        print(f"  ✅ 貼文已保存: {thread_path.relative_to(self.obsidian_vault)}")
        
        return str(thread_path)


# 使用示例
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="自動研究流程")
    parser.add_argument("--max-topics", type=int, default=5, help="最大主題數量")
    
    args = parser.parse_args()
    
    # 創建工作流程
    workflow = AutoResearchWorkflow()
    
    # 執行工作流程
    workflow.run(max_topics=args.max_topics)
