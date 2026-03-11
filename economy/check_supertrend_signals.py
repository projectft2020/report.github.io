#!/usr/bin/env python3
"""
檢查台灣股市 Supertrend 當前訊號
"""

import requests
import json
from typing import List, Dict

# Dashboard API 配置
API_BASE = "http://localhost:8000"
ADMIN_TOKEN = "admin995"
HEADERS = {"X-Admin-Token": ADMIN_TOKEN}

# Supertrend 策略配置
ST_CONFIG = {
    "symbols": [
        "1101.TW","1102.TW","1216.TW","1301.TW","1303.TW","1326.TW","1503.TW","1504.TW",
        "1513.TW","1514.TW","1519.TW","1590.TW","1609.TW","1707.TW","1795.TW","2002.TW",
        "2049.TW","2059.TW","2105.TW","2303.TW","2308.TW","2317.TW","2324.TW","2327.TW",
        "2330.TW","2344.TW","2345.TW","2356.TW","2357.TW","2368.TW","2376.TW","2379.TW",
        "2382.TW","2383.TW","2408.TW","2409.TW","2412.TW","2449.TW","2454.TW","2603.TW",
        "2609.TW","2610.TW","2615.TW","2618.TW","2633.TW","2727.TW","2731.TW","2880.TW",
        "2881.TW","2882.TW","2883.TW","2884.TW","2885.TW","2886.TW","2890.TW","2891.TW",
        "2892.TW","2912.TW","3008.TW","3017.TW","3034.TW","3036.TW","3037.TW","3044.TW",
        "3045.TW","3081.TW","3231.TW","3324.TW","3443.TW","3481.TW","3533.TW","3661.TW",
        "3680.TW","3706.TW","3711.TW","4105.TW","4123.TW","4743.TW","4904.TW","4938.TW",
        "4958.TW","4979.TW","5269.TW","5371.TW","5871.TW","5876.TW","5880.TW","5904.TW",
        "6239.TW","6274.TW","6442.TW","6446.TW","6472.TW","6505.TW","6535.TW","6669.TW",
        "6770.TW","8046.TW","8069.TW","8358.TW","8454.TW"
    ],
    "period": 10,
    "multiplier": 3.0
}

def get_supertrend_signal(symbol: str) -> Dict:
    """獲取單一股票的 Supertrend 訊號"""
    try:
        # 提取股票代碼（去除 .TW 後綴）
        stock_code = symbol.replace('.TW', '')

        # 調用 API
        response = requests.get(
            f"{API_BASE}/api/stocks/{stock_code}/history",
            params={
                "market": "TW",
                "supertrend": "true",
                "days": 365
            },
            headers=HEADERS,
            timeout=10
        )

        if response.status_code != 200:
            return {
                "symbol": stock_code,
                "error": f"API Error: {response.status_code}"
            }

        data = response.json()

        if not data:
            return {
                "symbol": stock_code,
                "error": "No data"
            }

        # 獲取最後一條數據
        latest = data[-1]

        # 檢查 Supertrend 訊號
        supertrend_direction = latest.get(f"SUPERTd_{ST_CONFIG['period']}_{ST_CONFIG['multiplier']}")
        supertrend_value = latest.get(f"SUPERTl_{ST_CONFIG['period']}_{ST_CONFIG['multiplier']}")
        supertrend_short = latest.get(f"SUPERTs_{ST_CONFIG['period']}_{ST_CONFIG['multiplier']}")
        price = latest.get("close")

        if supertrend_direction is None:
            return {
                "symbol": stock_code,
                "error": "No Supertrend data"
            }

        # 解讀訊號
        # SUPERTd = 1 表示看漲，SUPERTd = -1 表示看跌
        signal = "BUY" if supertrend_direction == 1 else "SELL"

        # 使用合適的 Supertrend 值（根據方向）
        st_value = supertrend_short if supertrend_direction == -1 else supertrend_value

        return {
            "symbol": stock_code,
            "date": latest.get("trade_date"),
            "close": price,
            "supertrend": st_value,
            "signal": signal,
            "direction": supertrend_direction
        }

    except Exception as e:
        return {
            "symbol": symbol.replace('.TW', '') if symbol else "unknown",
            "error": str(e)
        }

def check_all_signals() -> Dict:
    """檢查所有股票的當前訊號"""
    results = {
        "buy_signals": [],
        "sell_signals": [],
        "errors": [],
        "summary": {
            "total": len(ST_CONFIG["symbols"]),
            "buy": 0,
            "sell": 0,
            "error": 0
        }
    }

    print(f"🔍 檢查 {len(ST_CONFIG['symbols'])} 檔台股的 Supertrend 訊號...\n")

    for i, symbol in enumerate(ST_CONFIG["symbols"], 1):
        result = get_supertrend_signal(symbol)

        if "error" in result:
            results["errors"].append(result)
            results["summary"]["error"] += 1
            print(f"❌ [{i}/{len(ST_CONFIG['symbols'])}] {result['symbol']}: {result['error']}")
        else:
            if result["signal"] == "BUY":
                results["buy_signals"].append(result)
                results["summary"]["buy"] += 1
                print(f"✅ [{i}/{len(ST_CONFIG['symbols'])}] {result['symbol']}: BUY (價格: {result['close']:.2f}, ST: {result['supertrend']:.2f})")
            else:
                results["sell_signals"].append(result)
                results["summary"]["sell"] += 1
                print(f"⏬ [{i}/{len(ST_CONFIG['symbols'])}] {result['symbol']}: SELL (價格: {result['close']:.2f}, ST: {result['supertrend']:.2f})")

    return results

if __name__ == "__main__":
    results = check_all_signals()

    print(f"\n{'='*60}")
    print("📊 訊號統計摘要")
    print(f"{'='*60}")
    print(f"總計: {results['summary']['total']} 檔")
    print(f"✅ 買入訊號: {results['summary']['buy']} 檔")
    print(f"⏬ 賣出訊號: {results['summary']['sell']} 檔")
    print(f"❌ 錯誤: {results['summary']['error']} 檔")

    if results["buy_signals"]:
        print(f"\n{'='*60}")
        print(f"📈 買入訊號列表 ({results['summary']['buy']} 檔)")
        print(f"{'='*60}")
        for signal in results["buy_signals"]:
            print(f"{signal['symbol']}: {signal['close']:.2f} (ST: {signal['supertrend']:.2f})")

    if results["sell_signals"]:
        print(f"\n{'='*60}")
        print(f"📉 賣出訊號列表 ({results['summary']['sell']} 檔)")
        print(f"{'='*60}")
        for signal in results["sell_signals"]:
            print(f"{signal['symbol']}: {signal['close']:.2f} (ST: {signal['supertrend']:.2f})")

    if results["errors"]:
        print(f"\n{'='*60}")
        print(f"❌ 錯誤列表 ({results['summary']['error']} 檔)")
        print(f"{'='*60}")
        for error in results["errors"]:
            print(f"{error['symbol']}: {error['error']}")
