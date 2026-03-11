#!/usr/bin/env python3
"""
Trigger System - Charlie 自我判斷何時需要 Mentor
Charlie's self-assessment system for when to call Mentor
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json
import os


class MentorTriggerSystem:
    """Mentor 觸發判斷系統"""
    
    def __init__(self, state_file: str = None):
        self.state_file = state_file or os.path.expanduser("~/.openclaw/workspace/mentor-ops/trigger_state.json")
        self.last_mentor_session = self._load_state().get("last_mentor_session", None)
        self.heartbeat_counter = self._load_state().get("heartbeat_counter", 0)
        self.error_patterns = self._load_state().get("error_patterns", {})
        
        # 評估權重
        self.weights = {
            'time_based': 0.2,
            'complexity_based': 0.3,
            'error_based': 0.3,
            'innovation_based': 0.2
        }
        
        # 觸發閾值
        self.trigger_threshold = 0.6
        self.checkpoint_interval = 12  # 12 個 heartbeat = 6 小時
        
    def _load_state(self) -> Dict:
        """載入狀態"""
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {}
        
    def _save_state(self):
        """保存狀態"""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        state = {
            "last_mentor_session": self.last_mentor_session,
            "heartbeat_counter": self.heartbeat_counter,
            "error_patterns": self.error_patterns
        }
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
            
    def _check_time_trigger(self) -> float:
        """
        時間觸發檢查（每 6 小時）
        Time-based trigger check (every 6 hours)
        
        Returns:
            float: 觸發分數 (0.0 - 1.0)
        """
        if self.last_mentor_session is None:
            return 1.0  # 從未調用過，立即觸發
            
        try:
            last_time = datetime.fromisoformat(self.last_mentor_session)
        except (ValueError, TypeError):
            return 1.0  # 無效時間格式，觸發
            
        time_since_last = datetime.now() - last_time
        
        # 每 6 小時觸發一次
        if time_since_last >= timedelta(hours=6):
            return 1.0
        elif time_since_last >= timedelta(hours=5, minutes=30):
            return 0.8  # 提前 30 分鐘開始加權
            
        return 0.0
        
    def _check_complexity_trigger(self, context: Dict) -> float:
        """
        複雜度觸發檢查
        Complexity-based trigger check
        
        Args:
            context: 上下文信息，包含決策變量、不確定性等
            
        Returns:
            float: 觸發分數 (0.0 - 1.0)
        """
        decision_vars = len(context.get("decision_variables", []))
        uncertainty = context.get("uncertainty_level", 0.0)
        impact_scope = context.get("impact_scope", "low")
        
        score = 0.0
        
        # 決策變量數 > 5
        if decision_vars > 5:
            score += 0.3
        elif decision_vars > 3:
            score += 0.1
            
        # 不確定性 > 70%
        if uncertainty > 0.7:
            score += 0.4
        elif uncertainty > 0.5:
            score += 0.2
            
        # 影響範圍
        if impact_scope == "system":
            score += 0.3
        elif impact_scope == "project":
            score += 0.15
            
        return min(score, 1.0)
        
    def _check_error_trigger(self, context: Dict) -> float:
        """
        錯誤觸發檢查
        Error-based trigger check
        
        Args:
            context: 上下文信息，包含錯誤類型和頻率
            
        Returns:
            float: 觸發分數 (0.0 - 1.0)
        """
        current_error = context.get("current_error", None)
        error_severity = context.get("error_severity", "low")
        
        # 記錄錯誤模式
        if current_error:
            error_type = context.get("error_type", "unknown")
            if error_type not in self.error_patterns:
                self.error_patterns[error_type] = {
                    "count": 0,
                    "last_occurrence": None
                }
                
            self.error_patterns[error_type]["count"] += 1
            self.error_patterns[error_type]["last_occurrence"] = datetime.now().isoformat()
            self._save_state()
            
        # 檢查重複錯誤
        score = 0.0
        
        for error_type, data in self.error_patterns.items():
            if data["count"] >= 3:  # 同類型錯誤 3 次以上
                score += 0.4
                
        # 錯誤嚴重性
        if error_severity == "critical":
            score += 0.6
        elif error_severity == "high":
            score += 0.3
        elif error_severity == "medium":
            score += 0.15
            
        return min(score, 1.0)
        
    def _check_innovation_trigger(self, context: Dict) -> float:
        """
        創新觸發檢查
        Innovation-based trigger check
        
        Args:
            context: 上下文信息，包含新想法和潛在影響
            
        Returns:
            float: 觸發分數 (0.0 - 1.0)
        """
        new_ideas = context.get("new_ideas", [])
        potential_impact = context.get("potential_impact", "low")
        feasibility = context.get("feasibility", "low")
        
        score = 0.0
        
        # 新想法數量 > 3
        if len(new_ideas) > 3:
            score += 0.3
        elif len(new_ideas) > 1:
            score += 0.15
            
        # 潛在影響
        if potential_impact == "disruptive":
            score += 0.4
        elif potential_impact == "significant":
            score += 0.2
            
        # 可行性
        if feasibility == "high":
            score += 0.3
        elif feasibility == "medium":
            score += 0.15
            
        return min(score, 1.0)
        
    def increment_heartbeat(self):
        """增加 heartbeat 計數"""
        self.heartbeat_counter += 1
        self._save_state()
        
    def should_trigger_mentor(self, context: Dict = None) -> Tuple[bool, float, Dict]:
        """
        判斷是否需要呼叫 Mentor
        Judge whether to call Mentor
        
        Args:
            context: 上下文信息（可選）
            
        Returns:
            (should_trigger, trigger_score, details): 
                - should_trigger: 是否觸發
                - trigger_score: 觸發分數 (0.0 - 1.0)
                - details: 詳細信息
        """
        if context is None:
            context = {}
            
        # 評估各個觸發條件
        triggers = {
            'time_based': self._check_time_trigger(),
            'complexity_based': self._check_complexity_trigger(context),
            'error_based': self._check_error_trigger(context),
            'innovation_based': self._check_innovation_trigger(context)
        }
        
        # 計算加權分數
        trigger_score = (
            triggers['time_based'] * self.weights['time_based'] +
            triggers['complexity_based'] * self.weights['complexity_based'] +
            triggers['error_based'] * self.weights['error_based'] +
            triggers['innovation_based'] * self.weights['innovation_based']
        )
        
        should_trigger = trigger_score > self.trigger_threshold
        
        details = {
            'triggers': triggers,
            'weights': self.weights,
            'threshold': self.trigger_threshold,
            'heartbeat_counter': self.heartbeat_counter,
            'last_mentor_session': self.last_mentor_session
        }
        
        return should_trigger, trigger_score, details
        
    def record_mentor_session(self):
        """記錄 Mentor 會話"""
        self.last_mentor_session = datetime.now().isoformat()
        self._save_state()
        
    def get_status(self) -> Dict:
        """獲取系統狀態"""
        return {
            "heartbeat_counter": self.heartbeat_counter,
            "last_mentor_session": self.last_mentor_session,
            "error_patterns": self.error_patterns,
            "trigger_threshold": self.trigger_threshold,
            "checkpoint_interval": self.checkpoint_interval
        }


if __name__ == "__main__":
    # 測試
    trigger_system = MentorTriggerSystem()
    
    # 模擬 heartbeat
    for i in range(15):
        trigger_system.increment_heartbeat()
        should_trigger, score, details = trigger_system.should_trigger_mentor()
        print(f"Heartbeat {i}: should_trigger={should_trigger}, score={score:.2f}")
        
    print("\n狀態:", trigger_system.get_status())
