#!/usr/bin/env python3
"""
更新或添加股票映射（互動式）
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
        return {}

def save_data(data, market="TW"):
    """保存股票資料"""
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_file = os.path.join(skill_dir, 'references', 'data', f'{market.lower()}_stocks.json')

    # 備份
    backup_file = data_file + '.backup'
    if os.path.exists(data_file):
        os.replace(data_file, backup_file)
        print(f"✅ 已備份原始資料到: {backup_file}")

    # 保存新資料
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ 已保存更新後的資料到: {data_file}")

def add_stock(data):
    """添加新股票"""
    print("\n添加新股票")
    print("=" * 40)

    symbol = input("股票代碼 (例如: 2330): ").strip()
    if not symbol:
        print("❌ 取消")
        return data

    name = input("公司名稱 (例如: 台積電): ").strip()
    if not name:
        print("❌ 取消")
        return data

    market = input("市場 (上市/上櫃) [默認: 上市]: ").strip() or "上市"
    industry = input("行業 (例如: 半導體業): ").strip()

    # 創建記錄
    data[symbol] = {
        "name": name,
        "market": market,
        "type": "股票",
        "industry": industry
    }

    print(f"✅ 已添加: {symbol} - {name}")
    return data

def update_stock(data):
    """更新現有股票"""
    print("\n更新現有股票")
    print("=" * 40)

    symbol = input("股票代碼 (例如: 2330): ").strip()
    if symbol not in data:
        print(f"❌ 未找到股票: {symbol}")
        return data

    info = data[symbol]
    print(f"當前資訊:")
    print(f"  名稱: {info.get('name', 'N/A')}")
    print(f"  市場: {info.get('market', 'N/A')}")
    print(f"  行業: {info.get('industry', 'N/A')}")

    print("\n輸入新值（直接按 Enter 保持不變）:")

    name = input(f"公司名稱 [{info.get('name', '')}]: ").strip()
    if name:
        info['name'] = name

    market = input(f"市場 [{info.get('market', '')}]: ").strip()
    if market:
        info['market'] = market

    industry = input(f"行業 [{info.get('industry', '')}]: ").strip()
    if industry:
        info['industry'] = industry

    print(f"✅ 已更新: {symbol} - {info.get('name', 'N/A')}")
    return data

def delete_stock(data):
    """刪除股票"""
    print("\n刪除股票")
    print("=" * 40)

    symbol = input("股票代碼 (例如: 2330): ").strip()
    if symbol not in data:
        print(f"❌ 未找到股票: {symbol}")
        return data

    info = data[symbol]
    print(f"確認刪除: {symbol} - {info.get('name', 'N/A')}?")
    confirm = input("輸入 'yes' 確認刪除: ").strip().lower()

    if confirm == 'yes':
        del data[symbol]
        print(f"✅ 已刪除: {symbol}")
    else:
        print("❌ 已取消刪除")

    return data

def main():
    market = 'TW'

    # 加載資料
    data = load_data(market)
    if not data:
        data = {}

    print(f"\n{'=' * 50}")
    print(f"股票映射更新工具 - {market} 市場")
    print(f"當前股票數量: {len(data)}")
    print(f"{'=' * 50}\n")

    while True:
        print("\n請選擇操作:")
        print("  1. 添加新股票")
        print("  2. 更新現有股票")
        print("  3. 刪除股票")
        print("  4. 列出所有股票")
        print("  5. 保存並退出")
        print("  6. 退出（不保存）")

        choice = input("\n請輸入選項 (1-6): ").strip()

        if choice == '1':
            data = add_stock(data)
        elif choice == '2':
            data = update_stock(data)
        elif choice == '3':
            data = delete_stock(data)
        elif choice == '4':
            print(f"\n{'=' * 60}")
            print(f"所有股票 ({len(data)}):")
            print(f"{'=' * 60}")
            for symbol, info in sorted(data.items()):
                print(f"{symbol:8s} - {info.get('name', 'N/A')}")
            print(f"{'=' * 60}")
        elif choice == '5':
            save_data(data, market)
            print("✅ 已保存，退出")
            break
        elif choice == '6':
            print("❌ 未保存，退出")
            break
        else:
            print("❌ 無效選項，請重新選擇")

if __name__ == "__main__":
    main()
