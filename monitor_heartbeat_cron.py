#!/usr/bin/env python3
"""
Monitor Heartbeat Cron Jobs - 監控 cron 心跳運作

查看 cron 心跳 jobs 的運行狀態和歷史記錄。
"""

import json
import subprocess
from datetime import datetime, timezone, timedelta


def run_command(cmd):
    """執行 shell 命令並返回輸出"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout


def get_cron_list():
    """獲取 cron jobs 列表"""
    cmd = "openclaw cron list --json"
    output = run_command(cmd)
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        return {"jobs": []}


def get_cron_runs(job_id):
    """獲取指定 job 的運行歷史"""
    cmd = f"openclaw cron runs --json {job_id}"
    output = run_command(cmd)
    try:
        data = json.loads(output)
        return data.get("entries", [])
    except json.JSONDecodeError:
        return []


def format_timestamp(ms):
    """格式化時間戳（台灣時區）"""
    if not ms:
        return "N/A"
    dt = datetime.fromtimestamp(ms / 1000, tz=timezone(timedelta(hours=8)))
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def main():
    """主函數"""
    print()
    print("=" * 80)
    print("📊 Cron Heartbeat 監控器")
    print("=" * 80)
    print()

    # 獲取 cron jobs 列表
    cron_data = get_cron_list()

    if "jobs" not in cron_data:
        print("❌ 無法獲取 cron jobs")
        return

    jobs = cron_data["jobs"]

    # 篩選出心跳相關的 jobs
    heartbeat_jobs = [j for j in jobs if "心跳" in j.get("name", "")]

    if not heartbeat_jobs:
        print("❌ 沒有心跳 cron jobs")
        return

    print(f"✅ 找到 {len(heartbeat_jobs)} 個心跳 cron jobs")
    print()

    # 顯示每個 job 的狀態
    for job in heartbeat_jobs:
        job_id = job.get("id")
        name = job.get("name")
        enabled = job.get("enabled")
        schedule = job.get("schedule", {})
        state = job.get("state", {})

        # 解析 schedule
        expr = schedule.get("expr", "N/A")
        tz = schedule.get("tz", "N/A")
        next_run = state.get("nextRunAt")
        last_run = state.get("lastRunAt")
        last_status = state.get("lastStatus")

        # 顯示 job 詳情
        print(f"{'─' * 80}")
        print(f"📌 Job: {name}")
        print(f"   ID: {job_id}")
        print(f"   狀態: {'✅ 啟用' if enabled else '❌ 禁用'}")
        print(f"   時間表: {expr} ({tz})")
        print(f"   下次運行: {format_timestamp(next_run)}")
        print(f"   上次運行: {format_timestamp(last_run)}")
        print(f"   上次狀態: {last_status or 'N/A'}")
        print()

        # 獲取運行歷史
        runs = get_cron_runs(job_id)
        if runs:
            print(f"   📜 最近 {len(runs)} 次運行記錄:")
            for i, run in enumerate(runs[-5:], 1):  # 顯示最近 5 次
                run_at = format_timestamp(run.get("runAt"))
                status = run.get("status", "unknown")
                duration = run.get("durationMs", 0)
                print(f"      {i}. [{run_at}] 狀態: {status} ({duration}ms)")
        else:
            print(f"   📜 還沒有運行記錄")

        print()

    # 總結
    print("=" * 80)
    print("💡 提示:")
    print("   - 等待下一次運行後，再次運行此腳本查看歷史記錄")
    print("   - 如果 job 狀態顯示錯誤，請檢查 Gateway 日誌")
    print("   - 使用 'openclaw cron list' 查看所有 jobs")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
