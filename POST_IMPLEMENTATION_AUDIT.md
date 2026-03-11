# 實施後審計 (Post Implementation Audit)

> **目的：** 實施後審計，檢查是否重複造輪子、充分利用現有系統
> **應用場景：** 實施新系統或功能後
> **執行頻率：** 每次實施後執行，每月技術棧健康檢查，每季度技術債務評估

---

## 📋 審計檢查清單

### 檢查 1：重複造輪子檢測

**問題：** 是否重複造輪子？

**檢查步驟：**
1. 檢查 TECH_INVENTORY.md
2. 對比新實現和現有系統
3. 評估重複度

**評分標準：**

| 重複度 | 說明 | 行動 |
|--------|------|------|
| 0% | 沒有重複 | ✅ 通過 |
| 1-30% | 輕微重複（次要功能） | ✅ 可接受 |
| 31-60% | 中度重複（核心功能） | ⚠️ 需要討論 |
| 61-100% | 嚴重重複（整體重複） | ❌ 需要重構 |

**輸出：**
```markdown
## 重複造輪子檢測

**重複度：** [X%]

**對比分析：**
- [系統 1]：重複度 [X%]
- [系統 2]：重複度 [X%]

**結論：**
- [X%] 沒有重複 / 輕微重複 / 中度重複 / 嚴重重複

**行動：**
- [通過 / 需要討論 / 需要重構]
```

---

### 檢查 2：利用現有系統檢測

**問題：** 是否充分利用現有系統？

**檢查步驟：**
1. 列出使用的現有系統
2. 評估使用程度
3. 評估整合程度

**評分標準：**

| 利用度 | 說明 | 行動 |
|--------|------|------|
| 81-100% | 完全利用 | ✅ 優秀 |
| 61-80% | 良好利用 | ✅ 良好 |
| 41-60% | 部分利用 | ⚠️ 需要改進 |
| 0-40% | 未充分利用 | ❌ 需要優化 |

**輸出：**
```markdown
## 利用現有系統檢測

**利用度：** [X%]

**使用的系統：**
- [系統 1]：利用度 [X%]
- [系統 2]：利用度 [X%]

**整合程度：**
- [X%] 完全整合 / 良好整合 / 部分整合 / 未整合

**結論：**
- [X%] 完全利用 / 良好利用 / 部分利用 / 未充分利用

**行動：**
- [優秀 / 良好 / 需要改進 / 需要優化]
```

---

### 檢查 3：更新庫存檢測

**問題：** 是否更新 TECH_INVENTORY.md？

**檢查步驟：**
1. 檢查 TECH_INVENTORY.md
2. 確認新系統已記錄
3. 確認信息完整

**評分標準：**

| 完整度 | 說明 | 行動 |
|--------|------|------|
| 100% | 完全記錄 | ✅ 通過 |
| 50-99% | 部分記錄 | ⚠️ 需要補充 |
| 0-49% | 未記錄 | ❌ 需要更新 |

**輸出：**
```markdown
## 更新庫存檢測

**完整度：** [X%]

**記錄狀態：**
- [系統名稱]：[已記錄 / 未記錄]
- [路徑]：[已記錄 / 未記錄]
- [功能]：[已記錄 / 未記錄]
- [狀態]：[已記錄 / 未記錄]

**結論：**
- [X%] 完全記錄 / 部分記錄 / 未記錄

**行動：**
- [通過 / 需要補充 / 需要更新]
```

---

## 🗓️ 週期性審查機制

### 每月技術棧健康檢查

**執行時間：** 每月第一個星期一

**檢查內容：**
1. 技術棧庫存完整性
2. 系統依賴關係
3. 技術債務
4. 系統健康度

**檢查腳本：**

```python
#!/usr/bin/env python3
"""
每月技術棧健康檢查
"""

import json
from pathlib import Path

def check_inventory_completeness():
    """檢查庫存完整性"""
    print("🔍 檢查技術棧庫存完整性...")

    # 讀取 TECH_INVENTORY.md
    with open("TECH_INVENTORY.md", "r") as f:
        content = f.read()

    # 檢查必要部分
    required_sections = [
        "向量資料庫",
        "筆記系統",
        "任務管理",
        "監控系統",
        "Dashboard",
        "研究系統",
        "記憶系統",
        "技能系統",
        "代理系統",
        "SOP 文檔",
        "整合系統",
    ]

    missing_sections = []
    for section in required_sections:
        if section not in content:
            missing_sections.append(section)

    if missing_sections:
        print(f"  ⚠️  缺失部分：{', '.join(missing_sections)}")
        return False
    else:
        print("  ✅ 庫存完整")
        return True

def check_dependencies():
    """檢查依賴關係"""
    print("🔗 檢查系統依賴關係...")

    # 讀取 TECH_INVENTORY.md
    with open("TECH_INVENTORY.md", "r") as f:
        content = f.read()

    # 檢查依賴
    if "依賴：" in content:
        print("  ✅ 依賴記錄完整")
        return True
    else:
        print("  ⚠️  依賴記錄不完整")
        return False

def check_tech_debt():
    """檢查技術債務"""
    print("💳 檢查技術債務...")

    # 讀取記憶系統
    try:
        with open("memory/topics/system-architecture.md", "r") as f:
            content = f.read()

        # 檢查技術債務部分
        if "技術債務" in content:
            print("  ✅ 技術債務記錄存在")
            return True
        else:
            print("  ⚠️  技術債務記錄缺失")
            return False
    except FileNotFoundError:
        print("  ⚠️  系統架構文檔不存在")
        return False

def check_system_health():
    """檢查系統健康度"""
    print("💚 檢查系統健康度...")

    # 檢查關鍵系統
    systems = [
        ("QMD", "~/.qmd/qmd"),
        ("Obsidian", "~/Documents/Obsidian"),
        ("Prometheus", "/Users/charlie/monitoring/prometheus"),
        ("Grafana", "/Users/charlie/monitoring/grafana"),
    ]

    all_healthy = True
    for name, path in systems:
        path_obj = Path(path).expanduser()
        if path_obj.exists():
            print(f"  ✅ {name}: 健康")
        else:
            print(f"  ❌ {name}: 異常")
            all_healthy = False

    return all_healthy

# 主執行
if __name__ == "__main__":
    print("🗓️  每月技術棧健康檢查")
    print("=" * 50)

    # 執行檢查
    results = {
        "inventory_completeness": check_inventory_completeness(),
        "dependencies": check_dependencies(),
        "tech_debt": check_tech_debt(),
        "system_health": check_system_health(),
    }

    # 總結
    print("\n" + "=" * 50)
    print("📊 檢查總結")
    print("=" * 50)

    for check, result in results.items():
        status = "✅ 通過" if result else "❌ 異常"
        print(f"{check}: {status}")

    # 整體評估
    all_passed = all(results.values())
    if all_passed:
        print("\n🎉 所有檢查通過！技術棧健康！")
    else:
        print("\n⚠️  部分檢查未通過，需要關注！")
```

---

### 每季度技術債務評估

**執行時間：** 每季度最後一個星期五

**評估內容：**
1. 技術債務清單
2. 優先級排序
3. 解決計劃
4. 預估成本

**評估腳本：**

```python
#!/usr/bin/env python3
"""
每季度技術債務評估
"""

import json
from datetime import datetime

def collect_tech_debt():
    """收集技術債務"""
    print("💳 收集技術債務...")

    # 從多個源收集技術債務
    sources = [
        "memory/topics/system-architecture.md",
        "TECH_INVENTORY.md",
        "memory/2026-03-09.md",  # 最新日誌
    ]

    tech_debt = []

    for source in sources:
        try:
            with open(source, "r") as f:
                content = f.read()

            # 搜索技術債務關鍵詞
            if "重複造輪子" in content or "技術債務" in content:
                tech_debt.append({
                    "source": source,
                    "type": "重複造輪子" if "重複造輪子" in content else "技術債務",
                    "content": content
                })
        except FileNotFoundError:
            continue

    return tech_debt

def prioritize_debt(debt_items):
    """優先級排序技術債務"""
    print("🎯 優先級排序技術債務...")

    # 優先級評分
    priority_score = {
        "high": 3,
        "medium": 2,
        "low": 1
    }

    # 排序
    prioritized = sorted(
        debt_items,
        key=lambda x: priority_score.get(x.get("priority", "medium"), 2),
        reverse=True
    )

    for i, item in enumerate(prioritized):
        print(f"  {i+1}. {item.get('type')} - {item.get('source')}")

    return prioritized

def create_resolution_plan(debt_items):
    """創建解決計劃"""
    print("📋 創建解決計劃...")

    plan = {
        "date": datetime.now().isoformat(),
        "items": []
    }

    for item in debt_items:
        plan["items"].append({
            "type": item.get("type"),
            "source": item.get("source"),
            "action": item.get("action", "需要評估"),
            "priority": item.get("priority", "medium"),
            "estimated_cost": item.get("cost", "TBD")
        })

    return plan

# 主執行
if __name__ == "__main__":
    print("🗓️  每季度技術債務評估")
    print("=" * 50)

    # 收集技術債務
    tech_debt = collect_tech_debt()
    print(f"  收集到 {len(tech_debt)} 項技術債務\n")

    # 優先級排序
    prioritized = prioritize_debt(tech_debt)
    print()

    # 創建解決計劃
    plan = create_resolution_plan(prioritized)

    # 輸出計劃
    with open("TECH_DEBT_PLAN.json", "w") as f:
        json.dump(plan, f, indent=2)

    print("✅ 解決計劃已保存到 TECH_DEBT_PLAN.json")

    # 總結
    print("\n" + "=" * 50)
    print("📊 評估總結")
    print("=" * 50)
    print(f"技術債務總數：{len(tech_debt)}")
    print(f"高優先級：{len([x for x in prioritized if x.get('priority') == 'high'])}")
    print(f"中優先級：{len([x for x in prioritized if x.get('priority') == 'medium'])}")
    print(f"低優先級：{len([x for x in prioritized if x.get('priority') == 'low'])}")
```

---

## 📝 審計報告模板

```markdown
# 實施後審計報告

**審計時間：** [日期時間]
**審計者：** [姓名]
**實施項目：** [項目名稱]

---

## 檢查 1：重複造輪子檢測

**重複度：** [X%]

**對比分析：**
- [系統 1]：重複度 [X%]
- [系統 2]：重複度 [X%]

**結論：**
- [X%] 沒有重複 / 輕微重複 / 中度重複 / 嚴重重複

**行動：**
- [通過 / 需要討論 / 需要重構]

---

## 檢查 2：利用現有系統檢測

**利用度：** [X%]

**使用的系統：**
- [系統 1]：利用度 [X%]
- [系統 2]：利用度 [X%]

**整合程度：**
- [X%] 完全整合 / 良好整合 / 部分整合 / 未整合

**結論：**
- [X%] 完全利用 / 良好利用 / 部分利用 / 未充分利用

**行動：**
- [優秀 / 良好 / 需要改進 / 需要優化]

---

## 檢查 3：更新庫存檢測

**完整度：** [X%]

**記錄狀態：**
- [系統名稱]：[已記錄 / 未記錄]
- [路徑]：[已記錄 / 未記錄]
- [功能]：[已記錄 / 未記錄]
- [狀態]：[已記錄 / 未記錄]

**結論：**
- [X%] 完全記錄 / 部分記錄 / 未記錄

**行動：**
- [通過 / 需要補充 / 需要更新]

---

## 總結

**整體評分：** [X/100]

**主要問題：**
- [問題 1]
- [問題 2]

**改進建議：**
- [建議 1]
- [建議 2]

**下次行動：**
- [行動 1]
- [行動 2]

---

**簽名：** [姓名]
**日期：** [日期]
```

---

## 🎯 審計頻率

| 類型 | 頻率 | 執行時間 | 責任人 |
|------|------|---------|--------|
| **實施後審計** | 每次實施後 | 立即 | 項目負責人 |
| **每月健康檢查** | 每月 | 第一個星期一 | 系統管理員 |
| **季度技術債務評估** | 每季度 | 最後一個星期五 | 技術主管 |

---

**完成時間：** 2026-03-09 01:27 AM
**版本：** v1.0
**作者：** Charlie
