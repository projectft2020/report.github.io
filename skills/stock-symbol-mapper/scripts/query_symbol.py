#!/usr/bin/env python3
"""
查詢股票代碼或公司名稱
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
        print(f"❌ 錯誤: 找不到 {market} 股票資料檔案")
        print(f"   路徑: {data_file}")
        return None

def search_by_symbol(symbol, data):
    """根據代碼搜索"""
    # 移除可能存在的後綴，統一格式
    clean_symbol = symbol.replace('.TW', '').replace('.tw', '').upper()

    # 先精確匹配
    if clean_symbol in data:
        return data[clean_symbol]

    # 模糊匹配
    for key, value in data.items():
        if key.replace('.TW', '').upper() == clean_symbol:
            return value

    return None

def search_by_name(keyword, data):
    """根據關鍵詞搜索公司名稱"""
    results = []
    keyword_upper = keyword.upper()

    for symbol, info in data.items():
        if keyword_upper in info.get('name', '').upper():
            results.append((symbol, info))

    return results

def main():
    if len(sys.argv) < 2:
        print("用法: python3 query_symbol.py <symbol_or_name>")
        print("範例:")
        print("  python3 query_symbol.py 2330.TW")
        print("  python3 query_symbol.py 台積電")
        sys.exit(1)

    query = sys.argv[1]
    market = 'TW'

    # 檢測是否為台灣股票（.TW 後綴或純數字）
    if query.endswith('.TW') or query.endswith('.tw'):
        market = 'TW'
    elif query.endswith('.US') or query.endswith('.us'):
        market = 'US'
    elif query.replace('.', '').isdigit() and len(query.replace('.', '')) == 4:
        market = 'TW'  # 4位數字可能是台灣股票

    # 加載資料
    data = load_data(market)
    if not data:
        sys.exit(1)

    # 判斷是代碼還是名稱
    query_clean = query.replace('.TW', '').replace('.tw', '').replace('.US', '').replace('.us', '').upper()

    # 先嘗試作為代碼查詢
    result = search_by_symbol(query_clean, data)

    if result:
        print(f"✅ 找到股票資訊:")
        print(f"   代碼: {result.get('symbol', query_clean)}")
        print(f"   名稱: {result.get('name', 'N/A')}")
        print(f"   市場: {result.get('market', 'N/A')}")
        print(f"   行業: {result.get('industry', 'N/A')}")
        return

    # 嘗試作為名稱查詢
    results = search_by_name(query, data)

    if results:
        if len(results) == 1:
            symbol, info = results[0]
            print(f"✅ 找到股票資訊:")
            print(f"   代碼: {symbol}")
            print(f"   名稱: {info.get('name', 'N/A')}")
            print(f"   市場: {info.get('market', 'N/A')}")
            print(f"   行業: {info.get('industry', 'N/A')}")
        else:
            print(f"✅ 找到 {len(results)} 個匹配的股票:")
            for i, (symbol, info) in enumerate(results[:10], 1):  # 最多顯示 10 個
                print(f"   {i}. {symbol} - {info.get('name', 'N/A')}")
            if len(results) > 10:
                print(f"   ... 還有 {len(results) - 10} 個結果")
    else:
        print(f"❌ 未找到: '{query}'")
        print(f"💡 嘗試:")
        print(f"   - 檢查拼寫是否正確")
        print(f"   - 使用不同關鍵詞搜索")
        print(f"   - 確認股票代碼格式（例如：2330.TW 或 2330）")

if __name__ == "__main__":
    main()
