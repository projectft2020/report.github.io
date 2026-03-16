# TOOLS_INDEX.md - 腳本中央索引（自動生成）

> **生成時間：** 2026-03-12 02:37:51
> **腳本數量：** 10
> **目標：** 統一索引所有腳本，提升可見性，避免重複造輪子

## 🚀 快速查找

| 工具類型 | 名稱 | 用途 | 路徑 | 使用頻率 |
|----------|------|------|------|----------|
| core | auto_spawn_heartbeat | 待定 | scripts/core/auto_spawn_heartbeat.py | 高（心跳） |
| core | task_state_rollback | 待定 | scripts/core/task_state_rollback.py | 高（心跳） |
| core | error_recovery | 待定 | scripts/core/error_recovery.py | 高（心跳） |
| core | task_sync | 待定 | scripts/core/task_sync.py | 高（心跳） |
| kanban | spawn_daemon | 待定 | kanban-ops/spawn_daemon.py | 高（心跳） |
| kanban | auto_spawn_pending | 待定 | kanban-ops/auto_spawn_pending.py | 高（心跳） |
| tools | market_score_dual_confirm_strategy | Market Score + 雙市場同時確認策略 v3 | market_score_dual_confirm_strategy.py | 高（每天） |
| tools | market_score_strategy_analysis | 待定 | market_score_strategy_analysis.py | 高（每天） |
| tools | market_score_strategy_v2 | 待定 | market_score_strategy_v2.py | 高（每天） |
| tools | verify_performance | 待定 | kanban-works/mst-supertrend-strategy/verify_performance.py | 高（每天） |

## 📋 CORE 腳本

### auto_spawn_heartbeat

- **路徑：** `scripts/core/auto_spawn_heartbeat.py`
- **用途：** 待定
- **使用頻率：** 高（心跳）
- **觸發：** 觸發 API rate limit
- **主要函數：** log, log_heartbeat_execution, record_spawn_start, get_spawn_start_time, load_tasks

### task_state_rollback

- **路徑：** `scripts/core/task_state_rollback.py`
- **用途：** 待定
- **使用頻率：** 高（心跳）
- **主要函數：** log, load_tasks, save_tasks, get_active_subagent_labels, find_stuck_spawnings

### error_recovery

- **路徑：** `scripts/core/error_recovery.py`
- **用途：** 待定
- **使用頻率：** 高（心跳）
- **主要函數：** main
- **功能：** 錯誤類型

### task_sync

- **路徑：** `scripts/core/task_sync.py`
- **用途：** 待定
- **使用頻率：** 高（心跳）
- **觸發：** 觸發 Scout 擴展
- **主要函數：** load_tasks, save_tasks, update_task_status, parse_status_file, get_task_id

## 📋 KANBAN 腳本

### spawn_daemon

- **路徑：** `kanban-ops/spawn_daemon.py`
- **用途：** 待定
- **使用頻率：** 高（心跳）
- **觸發：** 每次心跳啟動

### auto_spawn_pending

- **路徑：** `kanban-ops/auto_spawn_pending.py`
- **用途：** 待定
- **使用頻率：** 高（心跳）
- **觸發：** 每次心跳時執行此腳本
- **主要函數：** log, load_tasks, count_in_progress, find_spawnable_tasks, print_spawn_commands

## 📋 SCOUT 腳本

（無腳本）

## 📋 TOOLS 腳本

### market_score_dual_confirm_strategy

- **路徑：** `market_score_dual_confirm_strategy.py`
- **用途：** Market Score + 雙市場同時確認策略 v3
- **使用頻率：** 高（每天）
- **觸發：** 每日收益
        df['qqq_daily_return'] = df['qqq_clos
- **功能：** Market Score + 雙市場同時確認策略 v3

### market_score_strategy_analysis

- **路徑：** `market_score_strategy_analysis.py`
- **用途：** 待定
- **使用頻率：** 高（每天）
- **觸發：** 每天都有數據）
- **主要函數：** get_stock_price, get_market_score, calculate_ma, analyze_market_score_strategy, print_analysis_report

### market_score_strategy_v2

- **路徑：** `market_score_strategy_v2.py`
- **用途：** 待定
- **使用頻率：** 高（每天）
- **觸發：** 每天都有數據）
- **主要函數：** get_stock_price, get_market_score, calculate_ma, analyze_market_score_strategy_v2, print_analysis_report

### verify_performance

- **路徑：** `kanban-works/mst-supertrend-strategy/verify_performance.py`
- **用途：** 待定
- **使用頻率：** 高（每天）
- **觸發：** 每日倉位數據
df_daily = df_prices[(df_prices['date'] >= 

## 📊 統計信息

| 類別 | 腳本數量 |
|------|----------|
| core | 4 |
| kanban | 2 |
| scout | 0 |
| tools | 4 |

| **總計** | **10** |

## 📈 使用頻率統計

- 高（心跳）：6 個
- 高（每天）：4 個

## 📝 維護說明

### 如何重新生成
```bash
cd ~/.openclaw/workspace && python3 scripts/scanner.py
```

### 預覽模式（不寫入文件）
```bash
python3 scripts/scanner.py --dry-run
```

### 查看統計
```bash
python3 scripts/scanner.py --stats
```
