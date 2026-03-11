#!/usr/bin/env python3
"""
API 錯誤追蹤模塊

功能：
1. 追蹤 sessions_spawn 調用的請求/回應時間
2. 記錄 HTTP 狀態碼和錯誤訊息
3. 統計錯誤類型、頻率、趨勢
4. 生成診斷報告

P0 行動：診斷卡住任務的根本原因

Author: System Optimization v2
Date: 2026-03-05
"""

import json
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict, field
from collections import defaultdict, Counter
import traceback

# 路徑配置
WORKSPACE = Path.home() / ".openclaw" / "workspace"
API_TRACK_LOG = WORKSPACE / "kanban-ops" / "api_tracker.log"
API_TRACK_DB = WORKSPACE / "kanban-ops" / "api_tracker_db.json"
API_STATS_FILE = WORKSPACE / "kanban-ops" / "api_tracker_stats.json"

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(API_TRACK_LOG, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class APICallRecord:
    """API 調用記錄"""
    timestamp: str
    task_id: str
    action: str  # 'spawn', 'poll', 'check'
    request_time: str  # ISO 格式
    response_time: Optional[str] = None
    duration_ms: Optional[int] = None
    http_status: Optional[int] = None
    error_message: Optional[str] = None
    success: bool = True
    rate_limit_headers: Dict[str, str] = field(default_factory=dict)
    status_code: Optional[str] = None  # OpenClaw status (e.g., "accepted", "rejected")


@dataclass
class APIStats:
    """API 統計"""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    rate_limit_errors: int = 0
    timeout_errors: int = 0
    avg_duration_ms: float = 0
    p95_duration_ms: float = 0
    p99_duration_ms: float = 0
    error_types: Dict[str, int] = field(default_factory=dict)
    hourly_calls: Dict[str, int] = field(default_factory=dict)
    last_update: str = ""


class APITracker:
    """API 追蹤器"""

    def __init__(self):
        self.records: List[APICallRecord] = []
        self.stats = self._load_stats()
        self._load_records()

    def _load_stats(self) -> APIStats:
        """載入統計數據"""
        try:
            if API_STATS_FILE.exists():
                with open(API_STATS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return APIStats(**data)
        except Exception as e:
            logger.warning(f"載入統計數據失敗: {e}")

        return APIStats()

    def _save_stats(self):
        """保存統計數據"""
        try:
            with open(API_STATS_FILE, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.stats), f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存統計數據失敗: {e}")

    def _load_records(self):
        """載入歷史記錄（最多保留 1000 條）"""
        try:
            if API_TRACK_DB.exists():
                with open(API_TRACK_DB, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.records = [APICallRecord(**r) for r in data[-1000:]]
        except Exception as e:
            logger.warning(f"載入歷史記錄失敗: {e}")

    def _save_records(self):
        """保存記錄（最多保留 1000 條）"""
        try:
            # 只保留最近 1000 條記錄
            records_to_save = self.records[-1000:]
            with open(API_TRACK_DB, 'w', encoding='utf-8') as f:
                json.dump([asdict(r) for r in records_to_save], f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存記錄失敗: {e}")

    def _calculate_percentiles(self, durations: List[float]) -> tuple:
        """計算百分位數"""
        if not durations:
            return 0, 0, 0

        sorted_durations = sorted(durations)
        n = len(sorted_durations)

        def percentile(p: float) -> float:
            idx = int(n * p / 100)
            return sorted_durations[min(idx, n - 1)]

        return (
            sum(durations) / n,
            percentile(95),
            percentile(99)
        )

    def record_call(self, task_id: str, action: str, start_time: datetime,
                     status_code: Optional[str] = None,
                     error_message: Optional[str] = None,
                     rate_limit_headers: Optional[Dict[str, str]] = None) -> APICallRecord:
        """
        記錄 API 調用

        Args:
            task_id: 任務 ID
            action: 動作類型 ('spawn', 'poll', 'check')
            start_time: 開始時間
            status_code: OpenClaw status code (e.g., "accepted", "rejected")
            error_message: 錯誤訊息（如果有）
            rate_limit_headers: Rate limit headers (e.g., X-RateLimit-Remaining)

        Returns:
            API 調用記錄
        """
        end_time = datetime.now(timezone.utc)
        duration_ms = int((end_time - start_time).total_seconds() * 1000)

        success = error_message is None and status_code in ['accepted', 'running', 'completed']

        record = APICallRecord(
            timestamp=end_time.isoformat(),
            task_id=task_id,
            action=action,
            request_time=start_time.isoformat(),
            response_time=end_time.isoformat(),
            duration_ms=duration_ms,
            status_code=status_code,
            error_message=error_message,
            success=success,
            rate_limit_headers=rate_limit_headers or {}
        )

        self.records.append(record)
        self._save_records()

        # 更新統計
        self._update_stats(record)

        # 記錄日誌
        if success:
            logger.info(f"[API] {action.upper()} {task_id} - {duration_ms}ms - {status_code}")
        else:
            logger.warning(f"[API] {action.upper()} {task_id} - {duration_ms}ms - {status_code} - {error_message}")

        return record

    def _update_stats(self, record: APICallRecord):
        """更新統計"""
        self.stats.total_calls += 1

        if record.success:
            self.stats.successful_calls += 1
        else:
            self.stats.failed_calls += 1

            # 錯誤分類
            if record.error_message:
                error_msg_lower = record.error_message.lower()

                if any(kw in error_msg_lower for kw in ['rate limit', '429', 'too many requests']):
                    self.stats.rate_limit_errors += 1
                elif any(kw in error_msg_lower for kw in ['timeout', 'timed out']):
                    self.stats.timeout_errors += 1

                # 統計錯誤類型
                error_type = self._classify_error(record.error_message)
                self.stats.error_types[error_type] = self.stats.error_types.get(error_type, 0) + 1

        # 計算平均和百分位數
        durations = [r.duration_ms for r in self.records if r.duration_ms is not None]
        if durations:
            avg, p95, p99 = self._calculate_percentiles(durations)
            self.stats.avg_duration_ms = round(avg, 2)
            self.stats.p95_duration_ms = round(p95, 2)
            self.stats.p99_duration_ms = round(p99, 2)

        # 每小時調用統計
        hour_key = record.timestamp[:13]  # YYYY-MM-DDTHH
        self.stats.hourly_calls[hour_key] = self.stats.hourly_calls.get(hour_key, 0) + 1

        # 清理舊的每小時統計（保留 24 小時）
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()[:13]
        self.stats.hourly_calls = {
            k: v for k, v in self.stats.hourly_calls.items() if k >= cutoff
        }

        self.stats.last_update = datetime.now(timezone.utc).isoformat()
        self._save_stats()

    def _classify_error(self, error_message: str) -> str:
        """分類錯誤類型"""
        error_msg_lower = error_message.lower()

        if any(kw in error_msg_lower for kw in ['rate limit', '429', 'too many requests']):
            return 'rate_limit'
        elif any(kw in error_msg_lower for kw in ['timeout', 'timed out']):
            return 'timeout'
        elif any(kw in error_msg_lower for kw in ['connection', 'network']):
            return 'network'
        elif any(kw in error_msg_lower for kw in ['parse', 'json']):
            return 'parsing'
        else:
            return 'unknown'

    def get_recent_records(self, hours: int = 1) -> List[APICallRecord]:
        """獲取最近 N 小時的記錄"""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        return [r for r in self.records
                if datetime.fromisoformat(r.timestamp) >= cutoff]

    def get_error_summary(self, hours: int = 24) -> Dict:
        """獲取錯誤摘要"""
        recent_records = self.get_recent_records(hours)
        failed_records = [r for r in recent_records if not r.success]

        if not failed_records:
            return {
                'total_errors': 0,
                'by_type': {},
                'by_hour': {},
                'recent_errors': []
            }

        # 按類型統計
        by_type = Counter()
        for record in failed_records:
            error_type = self._classify_error(record.error_message or 'unknown')
            by_type[error_type] += 1

        # 按小時統計
        by_hour = defaultdict(int)
        for record in failed_records:
            hour_key = record.timestamp[:13]
            by_hour[hour_key] += 1

        return {
            'total_errors': len(failed_records),
            'by_type': dict(by_type),
            'by_hour': dict(by_hour),
            'recent_errors': [
                {
                    'task_id': r.task_id,
                    'timestamp': r.timestamp,
                    'action': r.action,
                    'duration_ms': r.duration_ms,
                    'error': r.error_message
                }
                for r in failed_records[-10:]  # 最近 10 個錯誤
            ]
        }

    def print_stats(self):
        """打印統計信息"""
        print(f"\n{'='*70}")
        print(f"📊 API 追蹤統計")
        print(f"{'='*70}")
        print(f"總調用數: {self.stats.total_calls}")
        print(f"成功: {self.stats.successful_calls} ({self.stats.successful_calls/self.stats.total_calls*100:.1f}%)" if self.stats.total_calls > 0 else "成功: 0")
        print(f"失敗: {self.stats.failed_calls} ({self.stats.failed_calls/self.stats.total_calls*100:.1f}%)" if self.stats.total_calls > 0 else "失敗: 0")
        print(f"\n錯誤類型:")
        print(f"  Rate Limit: {self.stats.rate_limit_errors}")
        print(f"  Timeout: {self.stats.timeout_errors}")
        if self.stats.error_types:
            print(f"  其他: {self.stats.error_types}")
        print(f"\n回應時間:")
        print(f"  平均: {self.stats.avg_duration_ms:.2f}ms")
        print(f"  P95: {self.stats.p95_duration_ms:.2f}ms")
        print(f"  P99: {self.stats.p99_duration_ms:.2f}ms")
        print(f"\n最近調用（每小時）:")
        for hour, count in sorted(self.stats.hourly_calls.items())[-10:]:
            print(f"  {hour}: {count} 次調用")
        print(f"最後更新: {self.stats.last_update}")
        print(f"{'='*70}\n")

    def generate_diagnostic_report(self, hours: int = 24) -> str:
        """生成診斷報告"""
        error_summary = self.get_error_summary(hours)

        report = f"\n{'='*70}\n"
        report += f"🔍 API 診斷報告（最近 {hours} 小時）\n"
        report += f"{'='*70}\n\n"

        report += f"總錯誤數: {error_summary['total_errors']}\n"

        if error_summary['by_type']:
            report += f"\n錯誤類型統計:\n"
            for error_type, count in sorted(error_summary['by_type'].items(), key=lambda x: x[1], reverse=True):
                report += f"  - {error_type}: {count} 次\n"

        if error_summary['by_hour']:
            report += f"\n每小時錯誤分佈:\n"
            for hour, count in sorted(error_summary['by_hour'].items()):
                report += f"  {hour}: {count} 次\n"

        if error_summary['recent_errors']:
            report += f"\n最近 10 個錯誤:\n"
            for err in error_summary['recent_errors']:
                report += f"  [{err['timestamp']}] {err['task_id']} - {err['action']} - {err['error']}\n"
                report += f"    持續時間: {err['duration_ms']}ms\n"

        # 分析建議
        report += f"\n{'='*70}\n"
        report += f"🎯 診斷建議:\n"
        report += f"{'='*70}\n"

        if error_summary['total_errors'] == 0:
            report += f"✅ 沒有發現 API 錯誤，系統運作正常\n"
        elif self.stats.rate_limit_errors / max(self.stats.total_calls, 1) > 0.1:
            report += f"⚠️ Rate Limit 錯誤率 > 10%，建議:\n"
            report += f"  - 降低啟動頻率（當前 65 秒 → 建議 120-180 秒）\n"
            report += f"  - 降低並發上限（當前 3 → 建議 2）\n"
            report += f"  - 實施背壓機制（P1 行動）\n"
        elif self.stats.p99_duration_ms > 5000:
            report += f"⚠️ P99 回應時間 > 5 秒，API 可能存在延遲問題\n"
            report += f"  - 建議檢查網絡連接\n"
            report += f"  - 建議檢查 API 服務狀態\n"

        report += f"{'='*70}\n"

        return report


# 全局實例
_api_tracker = None


def get_tracker() -> APITracker:
    """獲取全局 API 追蹤器實例"""
    global _api_tracker
    if _api_tracker is None:
        _api_tracker = APITracker()
    return _api_tracker


def track_api_call(task_id: str, action: str, start_time: datetime,
                   status_code: Optional[str] = None,
                   error_message: Optional[str] = None,
                   rate_limit_headers: Optional[Dict[str, str]] = None):
    """追蹤 API 調用（便捷函數）"""
    tracker = get_tracker()
    return tracker.record_call(
        task_id=task_id,
        action=action,
        start_time=start_time,
        status_code=status_code,
        error_message=error_message,
        rate_limit_headers=rate_limit_headers
    )


def main():
    """主函數"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 api_tracker.py <command>")
        print("Commands:")
        print("  stats       - 顯示統計信息")
        print("  report      - 生成診斷報告")
        print("  errors      - 顯示錯誤摘要")
        return

    command = sys.argv[1]
    tracker = get_tracker()

    if command == 'stats':
        tracker.print_stats()
    elif command == 'report':
        hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
        print(tracker.generate_diagnostic_report(hours))
    elif command == 'errors':
        hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
        summary = tracker.get_error_summary(hours)
        print(f"\n錯誤摘要（最近 {hours} 小時）：")
        print(f"總錯誤數: {summary['total_errors']}")
        print(f"\n錯誤類型:")
        for error_type, count in summary['by_type'].items():
            print(f"  - {error_type}: {count}")
        if summary['recent_errors']:
            print(f"\n最近錯誤:")
            for err in summary['recent_errors'][-5:]:
                print(f"  [{err['timestamp']}] {err['task_id']} - {err['error']}")
    else:
        print(f"Unknown command: {command}")


if __name__ == '__main__':
    main()
