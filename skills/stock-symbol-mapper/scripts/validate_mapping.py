#!/usr/bin/env python3
"""
驗證股票映射資料的完整性和正確性
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
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析錯誤: {e}")
        return None

def validate_structure(data, market):
    """驗證資料結構"""
    print(f"\n📊 驗證 {market} 股票資料...")
    print(f"=" * 50)

    if not isinstance(data, dict):
        print(f"❌ 錯誤: 資料必須是字典格式")
        return False

    print(f"✅ 資料格式正確 (dict)")

    if len(data) == 0:
        print(f"⚠️  警告: 資料為空")
        return True

    print(f"✅ 股票數量: {len(data)}")

    return True

def validate_fields(data, market):
    """驗證必填欄位"""
    print(f"\n🔍 檢查必填欄位...")
    print(f"=" * 50)

    required_fields = ['name', 'market', 'industry']
    errors = []
    samples_checked = 0

    for symbol, info in data.items():
        samples_checked += 1

        # 只檢查前 100 個作為樣本
        if samples_checked > 100:
            break

        missing_fields = [field for field in required_fields if field not in info]
        if missing_fields:
            errors.append((symbol, missing_fields))

    if errors:
        print(f"❌ 發現 {len(errors)} 個缺少欄位的股票:")
        for symbol, fields in errors[:10]:  # 最多顯示 10 個
            print(f"   {symbol}: 缺少 {', '.join(fields)}")
        return False

    print(f"✅ 必填欄位檢查通過（樣本: {min(100, len(data))}）")
    return True

def validate_duplicates(data, market):
    """檢查重複"""
    print(f"\n🔄 檢查重複...")
    print(f"=" * 50)

    # 檢查 symbol 重複
    symbols = list(data.keys())
    unique_symbols = set(symbols)

    if len(symbols) != len(unique_symbols):
        duplicates = [s for s in unique_symbols if symbols.count(s) > 1]
        print(f"❌ 發現重複的 symbol: {duplicates}")
        return False

    print(f"✅ 無 symbol 重複")

    # 檢查 name 重複（允許，但要提醒）
    names = [info.get('name', '') for info in data.values()]
    name_counts = {name: names.count(name) for name in set(names)}
    duplicates = {k: v for k, v in name_counts.items() if v > 1}

    if duplicates:
        print(f"⚠️  發現重複的公司名稱:")
        for name, count in sorted(duplicates.items(), key=lambda x: -x[1])[:5]:
            print(f"   {name}: {count} 次")

    return True

def validate_formats(data, market):
    """驗證格式"""
    print(f"\n📋 檢查資料格式...")
    print(f"=" * 50)

    issues = []
    samples_checked = 0

    for symbol, info in data.items():
        samples_checked += 1
        if samples_checked > 50:  # 檢查前 50 個
            break

        # 檢查 symbol 格式
        if not isinstance(symbol, str) or not symbol:
            issues.append((symbol, "symbol 必須是字串"))

        # 檢查 name 格式
        name = info.get('name', '')
        if not isinstance(name, str) or not name:
            issues.append((symbol, "name 必須是非空字串"))

        # 檢查 market 格式
        market_val = info.get('market', '')
        if market_val not in ['上市', '上櫃', 'OTC', 'NASDAQ', 'NYSE', 'AMEX']:
            issues.append((symbol, f"market 值異常: {market_val}"))

    if issues:
        print(f"❌ 發現 {len(issues)} 個格式問題:")
        for symbol, issue in issues[:10]:
            print(f"   {symbol}: {issue}")
        return False

    print(f"✅ 格式檢查通過（樣本: {min(50, len(data))}）")
    return True

def validate_dashboard_consistency(data, market):
    """檢查與 Dashboard 的一致性"""
    print(f"\n🔗 檢查 Dashboard 一致性...")
    print(f"=" * 50)

    if market != "TW":
        print(f"ℹ️  跳過（僅檢查台灣股票）")
        return True

    dashboard_file = os.path.expanduser("~/Dashboard/frontend/src/data/securities_list.json")

    try:
        with open(dashboard_file, 'r', encoding='utf-8') as f:
            dashboard_data = json.load(f)
    except FileNotFoundError:
        print(f"⚠️  Dashboard 資料檔案不存在: {dashboard_file}")
        return True
    except json.JSONDecodeError as e:
        print(f"❌ Dashboard 資料 JSON 解析錯誤: {e}")
        return False

    # 比較數量
    diff = len(data) - len(dashboard_data)
    if abs(diff) > 10:  # 允許 10 個以內的差異
        print(f"⚠️  資料數量差異較大: skill({len(data)}) vs dashboard({len(dashboard_data)})")

    # 樣本比對
    samples = list(data.keys())[:20]
    mismatches = []

    for symbol in samples:
        skill_name = data.get(symbol, {}).get('name', '')
        dashboard_name = dashboard_data.get(symbol, {}).get('name', '')

        if skill_name != dashboard_name:
            mismatches.append((symbol, skill_name, dashboard_name))

    if mismatches:
        print(f"❌ 發現名稱不匹配:")
        for symbol, skill_name, dashboard_name in mismatches[:5]:
            print(f"   {symbol}: skill='{skill_name}' vs dashboard='{dashboard_name}'")
        return False

    print(f"✅ Dashboard 一致性檢查通過（樣本: {min(20, len(data))}）")
    return True

def main():
    markets = ['TW']

    # 如果有 US 資料，也檢查
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    us_file = os.path.join(skill_dir, 'references', 'data', 'us_stocks.json')
    if os.path.exists(us_file):
        markets.append('US')

    all_passed = True

    for market in markets:
        print(f"\n{'=' * 60}")
        print(f"驗證 {market} 股票資料")
        print(f"{'=' * 60}")

        data = load_data(market)

        if data is None:
            print(f"❌ 無法加載 {market} 資料")
            all_passed = False
            continue

        # 執行所有檢查
        if not validate_structure(data, market):
            all_passed = False

        if not validate_fields(data, market):
            all_passed = False

        if not validate_duplicates(data, market):
            all_passed = False

        if not validate_formats(data, market):
            all_passed = False

        if not validate_dashboard_consistency(data, market):
            all_passed = False

    # 總結
    print(f"\n{'=' * 60}")
    if all_passed:
        print(f"✅ 所有檢查通過！")
    else:
        print(f"❌ 發現問題，請檢查並修正")
    print(f"{'=' * 60}\n")

    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
