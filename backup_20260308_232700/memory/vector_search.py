#!/usr/bin/env python3
"""
向量軌跡可視化腳本
使用 OpenClaw 的 memory_search 和 memory_get 功能追蹤研究主題的演變過程

Example Usage:
    from memory.vector_search import VectorTrajectory
    
    vt = VectorTrajectory()
    
    # 查找軌跡
    trajectory = vt.find_trajectory("fat-tail analysis")
    
    # 可視化
    print(vt.visualize("fat-tail analysis"))
    
    # 導出
    vt.export("fat-tail", format="md")
"""

import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
import os


class VectorTrajectory:
    """
    向量軌跡可視化類
    
    用於追蹤研究主題在時間序列上的演變過程，
    通過語義搜索找到相關記憶，並生成可視化軌跡。
    """
    
    def __init__(self, memory_path: str = "/Users/charlie/.openclaw/workspace/memory"):
        """
        初始化 VectorTrajectory
        
        Args:
            memory_path: 記憶文件目錄路徑
        """
        self.memory_path = memory_path
        self.min_confidence = 0.7  # 最小置信度閾值
        
    def memory_search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        模擬 OpenClaw 的 memory_search 功能
        
        Args:
            query: 搜索查詢
            max_results: 最大結果數
            
        Returns:
            搜索結果列表
        """
        # 這是一個模擬實現，實際使用時應替換為真正的 memory_search
        results = []
        
        if os.path.exists(self.memory_path):
            for filename in os.listdir(self.memory_path):
                if filename.endswith('.md') and filename.startswith('2026-'):
                    # 從文件名提取日期
                    date_match = re.match(r'(\d{4}-\d{2}-\d{2})', filename)
                    if date_match:
                        date_str = date_match.group(1)
                        file_path = os.path.join(self.memory_path, filename)
                        
                        # 讀取文件內容
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                
                            # 簡單的相關性計算（基於關鍵詞匹配）
                            relevance = self._calculate_relevance(query, content)
                            
                            if relevance >= self.min_confidence:
                                results.append({
                                    'id': filename,
                                    'path': file_path,
                                    'date': date_str,
                                    'title': filename.replace('.md', ''),
                                    'confidence': relevance,
                                    'summary': self._generate_summary(content)
                                })
                        except Exception as e:
                            continue
        
        # 按日期排序
        results.sort(key=lambda x: x['date'])
        return results[:max_results]
    
    def memory_get(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        模擬 OpenClaw 的 memory_get 功能
        
        Args:
            memory_id: 記憶ID（文件名）
            
        Returns:
            記憶詳細信息
        """
        file_path = os.path.join(self.memory_path, memory_id)
        
        if not os.path.exists(file_path):
            return None
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 從文件名提取日期
            date_match = re.match(r'(\d{4}-\d{2}-\d{2})', memory_id)
            date_str = date_match.group(1) if date_match else "unknown"
            
            return {
                'id': memory_id,
                'path': file_path,
                'date': date_str,
                'title': memory_id.replace('.md', ''),
                'content': content,
                'summary': self._generate_summary(content),
                'size': len(content)
            }
        except Exception as e:
            return None
    
    def find_trajectory(self, topic: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        找到主題的完整軌跡
        
        Args:
            topic: 研究主題
            max_results: 最大結果數
            
        Returns:
            按時間排序的軌跡點列表
        """
        # 使用 memory_search 找到相關記憶
        search_results = self.memory_search(topic, max_results)
        
        # 為每個結果獲取詳細信息
        trajectory = []
        for result in search_results:
            detailed = self.memory_get(result['id'])
            if detailed:
                trajectory.append(detailed)
        
        return trajectory
    
    def visualize(self, topic: str, max_results: int = 10) -> str:
        """
        生成 ASCII 可視化
        
        Args:
            topic: 研究主題
            max_results: 最大結果數
            
        Returns:
            ASCII 格式的可視化字符串
        """
        trajectory = self.find_trajectory(topic, max_results)
        
        if not trajectory:
            return f"❌ 找不到主題 '{topic}' 的相關軌跡"
        
        lines = []
        lines.append(f"🔍 主題軌跡: {topic}")
        lines.append("=" * 50)
        
        for i, point in enumerate(trajectory):
            # 確定箭頭符號
            if i == len(trajectory) - 1:
                arrow = "✓"  # 最後一個點用勾號
            else:
                arrow = "→"  # 中間點用箭頭
            
            # 格式化置信度
            confidence = point.get('confidence', 0.0)
            confidence_str = f"{confidence:.2f}"
            
            # 生成行
            line = f"{arrow} {point['date']} ({confidence_str}): {point['summary']}"
            lines.append(line)
        
        # 添加統計信息
        lines.append("=" * 50)
        lines.append(f"📊 總計: {len(trajectory)} 個軌跡點")
        if trajectory:
            avg_confidence = sum(p.get('confidence', 0) for p in trajectory) / len(trajectory)
            lines.append(f"📈 平均置信度: {avg_confidence:.2f}")
        
        return "\n".join(lines)
    
    def export(self, topic: str, format: str = "md", max_results: int = 10) -> str:
        """
        導出軌跡為指定格式
        
        Args:
            topic: 研究主題
            format: 輸出格式 ("md" 或 "json")
            max_results: 最大結果數
            
        Returns:
            導出的文件路徑
        """
        trajectory = self.find_trajectory(topic, max_results)
        
        if not trajectory:
            raise ValueError(f"找不到主題 '{topic}' 的相關軌跡")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format.lower() == "md":
            # Markdown 格式
            filename = f"trajectory_{topic.replace(' ', '_')}_{timestamp}.md"
            content = self._generate_markdown(topic, trajectory)
        elif format.lower() == "json":
            # JSON 格式
            filename = f"trajectory_{topic.replace(' ', '_')}_{timestamp}.json"
            content = json.dumps(trajectory, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"不支持的格式: {format}")
        
        # 寫入文件
        output_path = os.path.join(self.memory_path, filename)
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return output_path
        except Exception as e:
            raise RuntimeError(f"寫入文件失敗: {e}")
    
    def _calculate_relevance(self, query: str, content: str) -> float:
        """
        計算查詢與內容的相關性（簡化版）
        
        Args:
            query: 查詢字符串
            content: 內容字符串
            
        Returns:
            相關性分數 (0-1)
        """
        # 簡單的關鍵詞匹配相關性計算
        query_lower = query.lower()
        content_lower = content.lower()
        
        # 分詞
        query_words = query_lower.split()
        content_words = content_lower.split()
        
        # 計算匹配度
        matches = 0
        for word in query_words:
            if len(word) > 2:  # 忽略過短的詞
                if word in content_lower:
                    matches += 1
        
        # 計算相關性分數
        if len(query_words) == 0:
            return 0.0
        
        relevance = matches / len(query_words)
        return min(relevance, 1.0)  # 限制在 0-1 之間
    
    def _generate_summary(self, content: str, max_length: int = 100) -> str:
        """
        從內容生成摘要
        
        Args:
            content: 內容字符串
            max_length: 最大長度
            
        Returns:
            摘要字符串
        """
        # 移除 Markdown 格式
        content = re.sub(r'[#*`\[\]()]', '', content)
        
        # 分割成行
        lines = content.split('\n')
        
        # 找到第一個非空行
        for line in lines:
            line = line.strip()
            if line and len(line) > 10:
                # 截斷到指定長度
                if len(line) > max_length:
                    return line[:max_length-3] + "..."
                return line
        
        # 如果沒有找到合適的行，返回前幾個字符
        content = content.strip()
        if len(content) > max_length:
            return content[:max_length-3] + "..."
        return content if content else "無內容"
    
    def _generate_markdown(self, topic: str, trajectory: List[Dict[str, Any]]) -> str:
        """
        生成 Markdown 格式的報告
        
        Args:
            topic: 主題
            trajectory: 軌跡數據
            
        Returns:
            Markdown 格式字符串
        """
        lines = []
        lines.append(f"# 主題軌跡報告: {topic}")
        lines.append("")
        lines.append(f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # 統計信息
        avg_confidence = sum(p.get('confidence', 0) for p in trajectory) / len(trajectory)
        lines.append("## 統計信息")
        lines.append(f"- **軌跡點數量**: {len(trajectory)}")
        lines.append(f"- **平均置信度**: {avg_confidence:.2f}")
        lines.append(f"- **時間範圍**: {trajectory[0]['date']} 至 {trajectory[-1]['date']}")
        lines.append("")
        
        # 詳細軌跡
        lines.append("## 詳細軌跡")
        lines.append("")
        
        for i, point in enumerate(trajectory):
            lines.append(f"### {i+1}. {point['date']}")
            lines.append(f"**置信度**: {point.get('confidence', 0):.2f}")
            lines.append(f"**摘要**: {point.get('summary', '無摘要')}")
            lines.append("")
            
            # 添加部分內容
            content = point.get('content', '')
            if content:
                # 提取前幾行
                content_lines = content.split('\n')[:5]
                lines.append("```")
                lines.extend(content_lines)
                lines.append("```")
            lines.append("")
        
        return "\n".join(lines)


# 示例用法
if __name__ == "__main__":
    # 創建 VectorTrajectory 實例
    vt = VectorTrajectory()
    
    # 示例主題
    topics = ["fat-tail analysis", "GVX strategy", "risk management"]
    
    for topic in topics:
        print(f"\n{'='*60}")
        print(f"主題: {topic}")
        print('='*60)
        
        # 查找軌跡
        try:
            trajectory = vt.find_trajectory(topic)
            if trajectory:
                # 可視化
                print(vt.visualize(topic))
                
                # 導出
                try:
                    output_path = vt.export(topic, format="md")
                    print(f"\n📁 導出文件: {output_path}")
                except Exception as e:
                    print(f"❌ 導出失敗: {e}")
            else:
                print(f"❌ 找不到主題 '{topic}' 的相關軌跡")
        except Exception as e:
            print(f"❌ 處理主題 '{topic}' 時發生錯誤: {e}")