#!/usr/bin/env python3
import duckdb
import json

# 連接數據庫
conn = duckdb.connect('/Users/charlie/Dashboard/backend/market_data_db/market_data.duckdb')

# 獲取最新的回測運行數據
print('=== supertrend_7b9f5ebf 最新回測詳情 ===')
result = conn.execute("""
    SELECT run_id, strategy_id, run_name, status, parameters,
           start_date, end_date, initial_capital, final_value,
           total_return, cagr, sharpe, max_drawdown, win_rate,
           trades_count, profit_factor, avg_trade,
           created_at, completed_at
    FROM backtest_runs
    WHERE strategy_id = 'supertrend_7b9f5ebf' AND status = 'completed'
    ORDER BY created_at DESC
    LIMIT 1
""").fetchone()

if result:
    run_id, strategy_id, run_name, status, parameters, start_date, end_date, initial_capital, final_value, total_return, cagr, sharpe, max_drawdown, win_rate, trades_count, profit_factor, avg_trade, created_at, completed_at = result

    print(f'運行ID: {run_id}')
    print(f'策略ID: {strategy_id}')
    print(f'名稱: {run_name}')
    print(f'狀態: {status}')
    print(f'\n參數:')
    if parameters:
        params = json.loads(parameters) if isinstance(parameters, str) else parameters
        for k, v in params.items():
            print(f'  {k}: {v}')

    print(f'\n回測範圍: {start_date} 至 {end_date}')
    print(f'初始資金: ${initial_capital:,.2f}')
    print(f'最終資金: ${final_value:,.2f}')
    print(f'\n總回報: {total_return:.2%}')
    print(f'年化回報: {cagr:.2%}')
    print(f'Sharpe比率: {sharpe:.2f}')
    print(f'最大回撤: {max_drawdown:.2%}')
    print(f'勝率: {win_rate:.2%}')
    print(f'交易次數: {trades_count}')
    if profit_factor:
        print(f'利潤因子: {profit_factor:.2f}')
    else:
        print('利潤因子: N/A')
    if avg_trade:
        print(f'平均交易: ${avg_trade:,.2f}')
    else:
        print('平均交易: N/A')
    print(f'\n創建時間: {created_at}')
    print(f'完成時間: {completed_at}')

    # 獲取交易記錄
    print(f'\n=== 交易記錄樣本（前20筆）===')
    trades_result = conn.execute(f"""
        SELECT trades
        FROM backtest_runs
        WHERE run_id = '{run_id}'
    """).fetchone()

    if trades_result and trades_result[0]:
        trades = json.loads(trades_result[0])
        for i, trade in enumerate(trades[:20]):
            print(f'\n交易 #{i+1}:')
            for k, v in trade.items():
                if k == 'date':
                    print(f'  {k}: {v}')
                elif isinstance(v, (int, float)):
                    if 'price' in k or 'value' in k or 'amount' in k or 'pct' in k:
                        if 'pct' in k:
                            print(f'  {k}: {v:.2%}')
                        else:
                            print(f'  {k}: {v:,.2f}')
                    else:
                        print(f'  {k}: {v}')
                else:
                    print(f'  {k}: {v}')

    # 獲取策略配置
    print(f'\n=== 策略配置 ===')
    config_result = conn.execute(f"""
        SELECT instance_id, display_name, template_name, market, params,
               is_active, tier, description
        FROM strategy_configs
        WHERE instance_id = 'supertrend_7b9f5ebf'
    """).fetchone()

    if config_result:
        instance_id, display_name, template_name, market, params, is_active, tier, description = config_result
        print(f'實例ID: {instance_id}')
        print(f'顯示名稱: {display_name}')
        print(f'模板名: {template_name}')
        print(f'市場: {market}')
        print(f'活躍: {is_active}')
        print(f'層級: {tier}')
        print(f'描述: {description}')
        print(f'\n配置參數:')
        if params:
            config_params = json.loads(params) if isinstance(params, str) else params
            for k, v in config_params.items():
                print(f'  {k}: {v}')

conn.close()
