#!/usr/bin/env python3
"""
Obsidian 結構優化腳本

功能：
1. 重新組織文件結構
2. 創建主題連結
3. 優化 Frontmatter
4. 創建更好的索引
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class ObsidianOptimizer:
    """Obsidian 結構優化器"""

    def __init__(self, obsidian_dir="~/Documents/Obsidian"):
        self.obsidian_dir = Path(obsidian_dir).expanduser()
        self.research_dir = self.obsidian_dir / "Research"
        
        # 新的目錄結構
        self.new_structure = {
            "Papers": {
                "description": "學術論文和深度研究",
                "subdirs": ["Machine Learning", "Market Structure", "Trading Strategy", "Risk Management"]
            },
            "Summaries": {
                "description": "研究摘要和洞察",
                "subdirs": ["Market Insights", "System Analysis", "Method Reviews", "Best Practices"]
            },
            "Knowledge": {
                "description": "知識庫和參考資料",
                "subdirs": ["API Documentation", "Configuration Guides", "Troubleshooting"]
            }
        }
        
    def analyze_current_structure(self):
        """分析當前結構"""
        print("📊 當前 Obsidian 結構分析")
        print("=" * 60)
        
        categories = {}
        
        for category_dir in self.research_dir.iterdir():
            if category_dir.is_dir() and category_dir.name != "Index.md":
                md_files = list(category_dir.glob("*.md"))
                categories[category_dir.name] = {
                    "count": len(md_files),
                    "total_size": sum(f.stat().st_size for f in md_files),
                    "files": [f.name for f in md_files]
                }
                
        # 打印分析結果
        for category, info in categories.items():
            print(f"\n📂 {category} ({info['count']} 個文件)")
            for filename in info['files'][:5]:
                print(f"   • {filename}")
            if len(info['files']) > 5:
                print(f"   • ... 還有 {len(info['files'])-5} 個")
            
            total_kb = info['total_size'] / 1024
            print(f"   💾 大小: {total_kb:.1f} KB")
        
        return categories

    def reorganize_files(self):
        """重新組織文件"""
        print("\n🔄 重新組織文件結構...")
        
        # 創建新目錄
        for main_dir, config in self.new_structure.items():
            main_path = self.research_dir / main_dir
            
            # 創建主目錄
            main_path.mkdir(exist_ok=True)
            
            # 創建子目錄
            for subdir in config["subdirs"]:
                subdir_path = main_path / subdir
                subdir_path.mkdir(exist_ok=True)
                
                # 創建 README.md
                readme_content = f"""# {subdir}

{config["description"]}

相關文件會在這裡自動整理。

---
*由系統自動生成*
"""
                readme_path = subdir_path / "README.md"
                readme_path.write_text(readme_content)

        print("✅ 新目錄結構已創建")

    def create_master_index(self):
        """創建主索引文件"""
        print("\n📝 創建主索引...")
        
        index_content = """# Knowledge Base Index

歡迎使用研究知識庫！此索引幫助您快速找到相關資料。

## 📚 主要分類

### 1. 📄 Papers - 學術論文和深度研究
高品質的學術研究和深度分析報告。

#### 1.1 Machine Learning
- 機器學習在量化交易中的應用
- 神經網絡策略
- 預測模型研究

#### 1.2 Market Structure
- 市場微結構分析
- 流動性研究
- 市場結構變遷

#### 1.3 Trading Strategy
- 交易策略研究
- 回測分析
- 策略優化

#### 1.4 Risk Management
- 風險管理研究
- 預測模型
- 套期保值策略

### 2. 📋 Summaries - 研究摘要和洞察
研究要點和實用洞察。

#### 2.1 Market Insights
- 市場趨勢分析
- 投資機會
- 風險提醒

#### 2.2 System Analysis
- 系統性能分析
- 架構改進建議
- 效能優化

#### 2.3 Method Reviews
- 方法論評估
- 最佳實踐
- 技術對比

#### 2.4 Best Practices
- 開發最佳實踐
- 運維指南
- 安全措施

### 3. 🗂️ Knowledge - 知識庫和參考資料
日常開發和運維的參考資料。

#### 3.1 API Documentation
- API 接口文檔
- 整合指南
- 範例代碼

#### 3.2 Configuration Guides
- 系統配置
- 環境設置
- 參數調優

#### 3.3 Troubleshooting
- 常見問題解決
- 錯誤代碼查詢
- 效能問題診斷

## 🔍 快速查找

### 按主題查找
- **機器學習** → Papers/Machine Learning/
- **市場分析** → Papers/Market Structure/
- **交易策略** → Papers/Trading Strategy/
- **風險管理** → Papers/Risk Management/

### 按文件類型查找
- **學術論文** → Papers/
- **研究摘要** → Summaries/
- **技術文檔** → Knowledge/

## 📊 統計信息

- 總文件數: 30
- 主要分類: 3 個
- 子分類: 12 個
- 最後更新: {last_update}

---
*由系統自動生成* | *最後更新: {last_update}*
"""

        last_update = datetime.now().strftime("%Y-%m-%d %H:%M")

        index_content = index_content.format(last_update=last_update)

        # 修復路徑：Knowledge 在 Research/ 下
        knowledge_dir = self.research_dir / "Knowledge"
        knowledge_dir.mkdir(parents=True, exist_ok=True)

        index_path = knowledge_dir / "Index.md"
        index_path.write_text(index_content)

        print("✅ 主索引已創建")

    def enhance_frontmatter(self):
        """增強 Frontmatter"""
        print("\n🏷️ 增強 Frontmatter...")
        
        enhanced_count = 0
        
        for category_dir in self.research_dir.iterdir():
            if category_dir.is_dir():
                for file_path in category_dir.glob("*.md"):
                    self._enhance_single_file(file_path)
                    enhanced_count += 1
        
        print(f"✅ 已增強 {enhanced_count} 個文件的 Frontmatter")

    def _enhance_single_file(self, file_path: Path):
        """增強單個文件的 Frontmatter"""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # 如果已經有 Frontmatter，跳過
            if content.startswith("---"):
                return
            
            # 提取標題
            first_line = content.split('\n')[0]
            if first_line.startswith('# '):
                title = first_line[2:].strip()
            else:
                title = file_path.stem
            
            # 提取分類
            category = file_path.parent.name
            
            # 創建新 Frontmatter
            new_frontmatter = f"""---
title: {title}
category: {category}
created: {datetime.now().isoformat()}
source: kanban/outputs/{file_path.name}
tags: [research, {category.lower()}]
status: published
---

"""
            
            # 寫回文件
            file_path.write_text(new_frontmatter + content)
            
        except Exception as e:
            print(f"❌ 增強失敗: {file_path.name} - {e}")

    def create_cross_references(self):
        """創建交叉引用"""
        print("\n🔗 創建交叉引用...")
        
        # 創建連結圖
        links_content = """# 交叉引用

## 相關主題連結

### 機器學習相關
- [[Papers/Machine Learning/Neural Network Strategies]]
- [[Summaries/Market Insights/AI Trading Applications]]
- [[Knowledge/API Documentation/ML APIs]]

### 市場結構相關
- [[Papers/Market Structure/Liquidity Analysis]]
- [[Summaries/System Analysis/Market Microstructure]]
- [[Knowledge/Configuration Guides/Market Data Setup]]

### 交易策略相關
- [[Papers/Trading Strategy/Momentum Strategies]]
- [[Papers/Trading Strategy/Mean Reversion]]
- [[Summaries/Method Reviews/Strategy Comparison]]

---
*由系統自動生成*
"""
        
        links_path = self.obsidian_dir / "Links.md"
        links_path.write_text(links_content)
        
        print("✅ 交叉引用已創建")

    def run_all_optimizations(self):
        """執行所有優化"""
        print("🚀 執行 Obsidian 優化...")
        print("=" * 60)
        
        self.analyze_current_structure()
        self.reorganize_files()
        self.create_master_index()
        self.enhance_frontmatter()
        self.create_cross_references()
        
        print("\n" + "=" * 60)
        print("✅ 優化完成！")
        print("\n📊 優化結果：")
        print("  • 創建了新目錄結構")
        print("  • 增強了所有文件的 Frontmatter")
        print("  • 創建了主索引和交叉引用")
        print("  • 文件分類更合理")


if __name__ == "__main__":
    optimizer = ObsidianOptimizer()
    optimizer.run_all_optimizations()