"""
History Service - 回測歷史記錄服務
修改版本：添加 win_rate 和 profit_factor 查詢功能 (方案 A)
"""

from typing import List, Dict, Optional
from datetime import datetime
import json
from sqlalchemy import text
from sqlalchemy.orm import Session


class HistoryService:
    """回測歷史記錄服務類"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def list_backtest_history(self, user_id: int, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        獲取回測歷史記錄列表（包含 win_rate 和 profit_factor）
        
        Args:
            user_id: 用戶 ID
            limit: 限制數量
            offset: 偏移量
            
        Returns:
            List[Dict]: 回測歷史記錄列表
        """
        query = """
        SELECT
            bh.id,
            bh.user_id,
            bh.run_id,
            bh.strategy_id,
            bh.params,
            bh.start_date,
            bh.end_date,
            bh.created_at,
            bh.status,
            br.win_rate,
            br.profit_factor,
            br.total_trades
        FROM backtest_history bh
        LEFT JOIN backtest_runs br ON bh.run_id = br.id
        WHERE bh.user_id = :user_id
        ORDER BY bh.created_at DESC
        LIMIT :limit OFFSET :offset
        """
        
        try:
            result = self.db.execute(
                text(query),
                {
                    "user_id": user_id,
                    "limit": limit,
                    "offset": offset
                }
            ).fetchall()
            
            histories = []
            for row in result:
                history = {
                    "id": row.id,
                    "user_id": row.user_id,
                    "run_id": row.run_id,
                    "strategy_id": row.strategy_id,
                    "params": self._parse_params(row.params) if row.params else None,
                    "start_date": row.start_date.isoformat() if row.start_date else None,
                    "end_date": row.end_date.isoformat() if row.end_date else None,
                    "created_at": row.created_at.isoformat(),
                    "status": row.status,
                    "win_rate": float(row.win_rate) if row.win_rate is not None else None,
                    "profit_factor": float(row.profit_factor) if row.profit_factor is not None else None,
                    "total_trades": row.total_trades
                }
                histories.append(history)
            
            return histories
            
        except Exception as e:
            print(f"Error in list_backtest_history: {e}")
            return []
    
    def get_backtest_by_id(self, history_id: int, user_id: int) -> Optional[Dict]:
        """
        根據 ID 獲取回測歷史記錄詳情（包含 win_rate 和 profit_factor）
        
        Args:
            history_id: 歷史記錄 ID
            user_id: 用戶 ID
            
        Returns:
            Optional[Dict]: 回測歷史記錄詳情
        """
        query = """
        SELECT
            bh.*,
            br.win_rate,
            br.profit_factor,
            br.total_trades,
            br.total_profit,
            br.max_drawdown,
            br.sharpe_ratio
        FROM backtest_history bh
        LEFT JOIN backtest_runs br ON bh.run_id = br.id
        WHERE bh.id = :history_id AND bh.user_id = :user_id
        """
        
        try:
            result = self.db.execute(
                text(query),
                {
                    "history_id": history_id,
                    "user_id": user_id
                }
            ).fetchone()
            
            if result:
                return {
                    "id": result.id,
                    "user_id": result.user_id,
                    "run_id": result.run_id,
                    "strategy_id": result.strategy_id,
                    "params": self._parse_params(result.params) if result.params else None,
                    "start_date": result.start_date.isoformat() if result.start_date else None,
                    "end_date": result.end_date.isoformat() if result.end_date else None,
                    "created_at": result.created_at.isoformat(),
                    "status": result.status,
                    "win_rate": float(result.win_rate) if result.win_rate is not None else None,
                    "profit_factor": float(result.profit_factor) if result.profit_factor is not None else None,
                    "total_trades": result.total_trades,
                    "total_profit": float(result.total_profit) if result.total_profit else None,
                    "max_drawdown": float(result.max_drawdown) if result.max_drawdown else None,
                    "sharpe_ratio": float(result.sharpe_ratio) if result.sharpe_ratio else None
                }
            
            return None
            
        except Exception as e:
            print(f"Error in get_backtest_by_id: {e}")
            return None
    
    def compare_backtests(self, history_ids: List[int], user_id: int) -> List[Dict]:
        """
        比較多個回測歷史記錄（包含 win_rate 和 profit_factor）
        
        Args:
            history_ids: 歷史記錄 ID 列表
            user_id: 用戶 ID
            
        Returns:
            List[Dict]: 回測記錄比較列表
        """
        if not history_ids:
            return []
        
        placeholders = ','.join([f':id_{i}' for i in range(len(history_ids))])
        params = {"user_id": user_id}
        params.update({f"id_{i}": hist_id for i, hist_id in enumerate(history_ids)})
        
        query = f"""
        SELECT
            bh.*,
            br.win_rate,
            br.profit_factor,
            br.total_trades,
            br.total_profit,
            br.max_drawdown
        FROM backtest_history bh
        LEFT JOIN backtest_runs br ON bh.run_id = br.id
        WHERE bh.id IN ({placeholders}) AND bh.user_id = :user_id
        ORDER BY bh.created_at DESC
        """
        
        try:
            results = self.db.execute(text(query), params).fetchall()
            
            comparisons = []
            for row in results:
                comparison = {
                    "id": row.id,
                    "user_id": row.user_id,
                    "run_id": row.run_id,
                    "strategy_id": row.strategy_id,
                    "params": self._parse_params(row.params) if row.params else None,
                    "start_date": row.start_date.isoformat() if row.start_date else None,
                    "end_date": row.end_date.isoformat() if row.end_date else None,
                    "created_at": row.created_at.isoformat(),
                    "status": row.status,
                    "win_rate": float(row.win_rate) if row.win_rate is not None else None,
                    "profit_factor": float(row.profit_factor) if row.profit_factor is not None else None,
                    "total_trades": row.total_trades,
                    "total_profit": float(row.total_profit) if row.total_profit else None,
                    "max_drawdown": float(row.max_drawdown) if row.max_drawdown else None
                }
                comparisons.append(comparison)
            
            return comparisons
            
        except Exception as e:
            print(f"Error in compare_backtests: {e}")
            return []
    
    def get_history_statistics(self, user_id: int) -> Dict:
        """
        獲取用戶的回測歷史統計信息（包含 win_rate 和 profit_factor 統計）
        
        Args:
            user_id: 用戶 ID
            
        Returns:
            Dict: 統計信息
        """
        query = """
        SELECT
            COUNT(bh.id) as total_histories,
            COUNT(br.win_rate) as histories_with_win_rate,
            COUNT(br.profit_factor) as histories_with_profit_factor,
            AVG(br.win_rate) as avg_win_rate,
            AVG(br.profit_factor) as avg_profit_factor,
            MAX(br.win_rate) as max_win_rate,
            MIN(br.win_rate) as min_win_rate,
            MAX(br.profit_factor) as max_profit_factor,
            MIN(br.profit_factor) as min_profit_factor
        FROM backtest_history bh
        LEFT JOIN backtest_runs br ON bh.run_id = br.id
        WHERE bh.user_id = :user_id
        """
        
        try:
            result = self.db.execute(text(query), {"user_id": user_id}).fetchone()
            
            if result:
                return {
                    "total_histories": result.total_histories or 0,
                    "histories_with_win_rate": result.histories_with_win_rate or 0,
                    "histories_with_profit_factor": result.histories_with_profit_factor or 0,
                    "win_rate_coverage": round(
                        (result.histories_with_win_rate / result.total_histories * 100) 
                        if result.total_histories > 0 else 0, 2
                    ),
                    "profit_factor_coverage": round(
                        (result.histories_with_profit_factor / result.total_histories * 100) 
                        if result.total_histories > 0 else 0, 2
                    ),
                    "avg_win_rate": float(result.avg_win_rate) if result.avg_win_rate else None,
                    "avg_profit_factor": float(result.avg_profit_factor) if result.avg_profit_factor else None,
                    "max_win_rate": float(result.max_win_rate) if result.max_win_rate else None,
                    "min_win_rate": float(result.min_win_rate) if result.min_win_rate else None,
                    "max_profit_factor": float(result.max_profit_factor) if result.max_profit_factor else None,
                    "min_profit_factor": float(result.min_profit_factor) if result.min_profit_factor else None
                }
            
            return {
                "total_histories": 0,
                "win_rate_coverage": 0,
                "profit_factor_coverage": 0
            }
            
        except Exception as e:
            print(f"Error in get_history_statistics: {e}")
            return {"total_histories": 0, "win_rate_coverage": 0, "profit_factor_coverage": 0}
    
    def _parse_params(self, params_str: str) -> Dict:
        """
        解析 JSON 格式的參數字符串
        
        Args:
            params_str: JSON 格式的參數字符串
            
        Returns:
            Dict: 解析後的參數字典
        """
        try:
            return json.loads(params_str)
        except (json.JSONDecodeError, TypeError):
            return {"raw": params_str}


# 便捷函數
def get_history_service(db: Session) -> HistoryService:
    """
    獲取 HistoryService 實例
    
    Args:
        db: 資料庫會話
        
    Returns:
        HistoryService: 歷史記錄服務實例
    """
    return HistoryService(db)


# 向後兼容的函數（保持原有 API）
def list_backtest_history(user_id: int, db: Session, limit: int = 100, offset: int = 0) -> List[Dict]:
    """
    向後兼容的函數：獲取回測歷史記錄列表
    """
    service = get_history_service(db)
    return service.list_backtest_history(user_id, limit, offset)


def get_backtest_by_id(history_id: int, user_id: int, db: Session) -> Optional[Dict]:
    """
    向後兼容的函數：根據 ID 獲取回測歷史記錄詳情
    """
    service = get_history_service(db)
    return service.get_backtest_by_id(history_id, user_id)


def compare_backtests(history_ids: List[int], user_id: int, db: Session) -> List[Dict]:
    """
    向後兼容的函數：比較多個回測歷史記錄
    """
    service = get_history_service(db)
    return service.compare_backtests(history_ids, user_id)


def get_history_statistics(user_id: int, db: Session) -> Dict:
    """
    向後兼容的函數：獲取歷史統計信息
    """
    service = get_history_service(db)
    return service.get_history_statistics(user_id)