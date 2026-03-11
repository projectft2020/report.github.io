#!/usr/bin/env python3
"""
股號查詢腳本
查詢股號對應的公司名稱，或公司名稱對應的股號
"""

import json
import sys
import os
from pathlib import Path

# Skill 路徑
SKILL_DIR = Path(__file__).parent.parent
REFERENCES_DIR = SKILL_DIR / "references" / "data"

# 載入台灣股票
TW_STOCKS_FILE = REFERENCES_DIR / "tw_stocks.json"
tw_stocks = {}

if TW_STOCKS_FILE.exists():
    with open(TW_STOCKS_FILE, 'r', encoding='utf-8') as f:
        tw_stocks = json.load(f)

# 載入美國股票
US_STOCKS_FILE = REFERENCES_DIR / "us_stocks.json"
us_stocks = {}

if US_STOCKS_FILE.exists():
    with open(US_STOCKS_FILE, 'r', encoding='utf-8') as f:
        us_stocks = json.load(f)

# 合併所有股票
all_stocks = {**tw_stocks, **us_stocks}

def query_by_symbol(symbol):
    """根據股號查詢公司名稱"""
    # 標準化股號（去除 .TW 或 .US 後綴）
    symbol_clean = symbol.upper().replace('.TW', '').replace('.US', '')

    for key, info in all_stocks.items():
        if key == symbol_clean:
            return info

    return None

def query_by_name(name):
    """根據公司名稱查詢股號（模糊匹配）"""
    name_lower = name.lower()
    results = []

    for symbol, info in all_stocks.items():
        if name_lower in info['name'].lower():
            results.append({
                'symbol': symbol,
                'name': info['name'],
                'market': info.get('market', ''),
                'industry': info.get('industry', '')
            })

    return results

def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  查詢股號: python3 query.py symbol 2330")
        print("  查詢名稱: python3 query.py name 台積電")
        print("  模糊搜尋: python3 query.py search 台積")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == 'symbol' and len(sys.argv) >= 3:
        symbol = sys.argv[2]
        result = query_by_symbol(symbol)

        if result:
            print(f"✅ 找到: {symbol} → {result['name']}")
            print(f"   市場: {result.get('market', 'N/A')}")
            print(f"   產業: {result.get('industry', 'N/A')}")
        else:
            print(f"❌ 未找到: {symbol}")
            # 建議相似股號
            similar = [s for s in all_stocks.keys() if s.startswith(symbol)]
            if similar:
                print(f"   建議: {', '.join(similar[:5])}")

    elif mode == 'name' and len(sys.argv) >= 3:
        name = sys.argv[2]
        results = query_by_name(name)

        if results:
            print(f"✅ 找到 {len(results)} 筆:")
            for r in results[:10]:
                print(f"   {r['symbol']}: {r['name']} ({r['market']}, {r['industry']})")
            if len(results) > 10:
                print(f"   ... 還有 {len(results) - 10} 筆")
        else:
            print(f"❌ 未找到: {name}")

    elif mode == 'search' and len(sys.argv) >= 3:
        keyword = sys.argv[2]
        results = query_by_name(keyword)

        if results:
            print(f"✅ 搜尋結果 ({len(results)} 筆):")
            for r in results[:20]:
                print(f"   {r['symbol']}: {r['name']} ({r['market']}, {r['industry']})")
            if len(results) > 20:
                print(f"   ... 還有 {len(results) - 20} 筆")
        else:
            print(f"❌ 未找到: {keyword}")

    elif mode == 'stats':
        print("📊 股票資料統計:")
        print(f"   台灣股票: {len(tw_stocks)} 筆")
        print(f"   美國股票: {len(us_stocks)} 筆")
        print(f"   總計: {len(all_stocks)} 筆")

    else:
        print("❌ 未知的模式:", mode)
        sys.exit(1)

if __name__ == '__main__':
    main()
