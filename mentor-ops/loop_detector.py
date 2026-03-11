#!/usr/bin/env python3
"""
Loop Detector - 檢測並防止無限循環討論
Detects and prevents infinite conversation loops
"""

from datetime import datetime
from typing import Tuple, List, Dict
import json


class LoopDetector:
    """檢測對話中的循環模式"""
    
    def __init__(self):
        self.conversation_history: List[Dict] = []
        self.similarity_threshold = 0.85
        self.max_repeated_topics = 3
        self.max_history_size = 20
        
    def _calculate_similarity(self, msg1: str, msg2: str) -> float:
        """
        計算兩條消息的相似度（簡化版）
        Calculate similarity between two messages (simplified)
        """
        # 詞級相似度（簡化實現）
        words1 = set(msg1.lower().split())
        words2 = set(msg2.lower().split())
        
        if not words1 or not words2:
            return 0.0
            
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
        
    def _extract_topics(self, message: str) -> List[str]:
        """
        提取消息中的主題關鍵詞
        Extract topic keywords from message
        """
        # 簡化的主題提取（使用關鍵詞匹配）
        keywords = {
            "策略": ["策略", "計劃", "設計", "架構"],
            "執行": ["執行", "實施", "操作", "運行"],
            "錯誤": ["錯誤", "失敗", "問題", "異常"],
            "優化": ["優化", "改進", "提升", "增強"],
            "決策": ["決策", "選擇", "判斷", "決定"],
        }
        
        topics = []
        for topic, words in keywords.items():
            if any(word in message for word in words):
                topics.append(topic)
                
        return topics
        
    def detect_loop(self, current_message: str) -> Tuple[bool, str]:
        """
        檢測是否出現循環討論
        Detect if conversation is looping
        
        Args:
            current_message: 當前消息內容
            
        Returns:
            (is_looping, message): 是否循環和描述信息
        """
        # 檢查歷史記錄大小
        if len(self.conversation_history) > self.max_history_size:
            self.conversation_history = self.conversation_history[-self.max_history_size:]
            
        # 檢測話題重複
        similar_topics = 0
        current_topics = self._extract_topics(current_message)
        
        for past_msg in self.conversation_history[-10:]:  # 檢查最近 10 輪
            similarity = self._calculate_similarity(current_message, past_msg["message"])
            
            if similarity > self.similarity_threshold:
                similar_topics += 1
                
            # 檢查主題重複
            past_topics = self._extract_topics(past_msg["message"])
            common_topics = set(current_topics) & set(past_topics)
            
            if len(common_topics) >= 2:  # 至少有 2 個共同主題
                similar_topics += 1
                
        if similar_topics >= self.max_repeated_topics:
            return True, f"檢測到循環討論（相似度 > {self.similarity_threshold}，重複 {similar_topics} 次），建議轉換話題或結束會話"
            
        # 記錄當前消息
        self.conversation_history.append({
            "message": current_message,
            "topics": current_topics,
            "timestamp": datetime.now().isoformat()
        })
        
        return False, "對話進展正常"
        
    def reset(self):
        """重置檢測器狀態"""
        self.conversation_history = []
        
    def get_summary(self) -> Dict:
        """獲取對話摘要統計"""
        if not self.conversation_history:
            return {"turn_count": 0, "topic_distribution": {}}
            
        topic_counts = {}
        for msg in self.conversation_history:
            for topic in msg["topics"]:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
                
        return {
            "turn_count": len(self.conversation_history),
            "topic_distribution": topic_counts
        }


if __name__ == "__main__":
    # 測試
    detector = LoopDetector()
    
    test_messages = [
        "策略設計需要優化",
        "執行計劃",
        "策略設計需要優化",
        "執行計劃",
        "策略設計需要改進",
    ]
    
    for msg in test_messages:
        is_looping, message = detector.detect_loop(msg)
        print(f"消息: {msg}")
        print(f"循環: {is_looping} - {message}")
        print("---")
        
    print("\n摘要:", detector.get_summary())
