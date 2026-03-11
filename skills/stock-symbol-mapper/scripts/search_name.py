#!/usr/bin/env python3
"""
根據關鍵詞搜索公司名稱
"""

import json
import sys
import os

def load_data(market="TW"):
    """加載股票資料"""
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_file = os.path.join(skill_dir, 'references', 'data', f'{market.lower()}_stocks.json')

    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def search(keyword, data, exact_match=False):
    """搜索公司名稱"""
    keyword_upper = keyword.upper()
    results = []

    for symbol, info in data.items():
        name = info.get('name', '')

        if exact_match:
            # 精確匹配
            if keyword_upper == name.upper():
                results.append((symbol, info))
        else:
            # 模糊匹配
            if keyword_upper in name.upper():
                results.append((symbol, info))

    return results

def main():
    if len(sys.argv) < 2:
        print("用法: python3 search_name.py \"<keyword>\" [--exact]")
        print("範例:")
        print("  python3 search_name.py \"台積電\"")
        print("  python3 search_name.py \"台積\"")
        print("  python3 search_name.py \"台積電\" --exact  # 精確匹配")
        sys.exit(1)

    keyword = sys.argv[1]
    exact_match = '--exact' in sys.argv
    market = 'TW'

    # 加載資料
    data = load_data(market)
    if not data:
        print(f"❌ 錯誤: 無法加載 {market} 股票資料")
        sys.exit(1)

    # 搜索
    results = search(keyword, data, exact_match)

    if results:
        if len(results) == 1:
            symbol, info = results[0]
            print(f"✅ 找到 1 個結果:")
            print(f"   代碼: {symbol}")
            print(f"   名稱: {info.get('name', 'N/A')}")
            print(f"   市場: {info.get('market', 'N/A')}")
            print(f"   行業: {info.get('industry', 'N/A')}")
        else:
            print(f"✅ 找到 {len(results)} 個結果:")
            print(f"{'=' * 60}")
            for i, (symbol, info) in enumerate(results, 1):
                name = info.get('name', 'N/A')
                market_val = info.get('market', 'N/A')
                industry = info.get('industry', 'N/A')
                print(f"{i:3d}. {symbol:8s} - {name:20s} ({market_val}) {industry}")
            print(f"{'=' * 60}")
    else:
        print(f"❌ 未找到: '{keyword}'")
        print(f"💡 嘗試:")
        print(f"   - 使用更短的關鍵詞")
        print(f"   - 移除 --exact 標誌進行模糊搜索")
        print(f"   - 檢查拼寫是否正確")

if __name__ == "__main__":
    main()
