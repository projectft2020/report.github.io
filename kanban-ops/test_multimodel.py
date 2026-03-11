#!/usr/bin/env python3
"""
測試多模型架構
演示如何使用 ModelAllocator 和 ModelMonitor
"""

import sys
from pathlib import Path

# 添加 kanban-ops 到路徑
sys.path.insert(0, str(Path(__file__).parent))

from model_allocator import ModelAllocator
from model_monitor import ModelMonitor


def test_model_allocator():
    """測試模型分配器"""
    print("\n" + "=" * 60)
    print("🧪 測試 1：模型分配器")
    print("=" * 60)

    allocator = ModelAllocator()

    # 測試 1：獲取系統狀態
    print("\n1. 系統狀態：")
    status = allocator.get_system_status()
    print(f"   總請求：{status['total_requests']}")
    print(f"   成功：{status['successful']}")
    print(f"   失敗：{status['failed']}")
    print(f"   成功率：{status['success_rate']:.2%}")
    print(f"   啟用模型：{status['enabled_models']}/{status['total_models']}")

    # 測試 2：為不同代理分配任務
    print("\n2. 為不同代理分配任務（默認策略）：")
    agents = ["research", "analyst", "creative", "automation", "developer", "architect", "mentors"]

    for agent in agents:
        result = allocator.allocate_task(agent)
        if result:
            print(f"   ✅ {agent:10} → {result['model_id']} (品質:{result['quality']}, 速度:{result['speed']})")
        else:
            print(f"   ❌ {agent:10} → 無可用模型")

    # 測試 3：高品質優先
    print("\n3. 高品質優先策略：")
    result = allocator.allocate_task("analyst", priority="high_quality")
    if result:
        print(f"   ✅ analyst → {result['model_id']} (高品質優先)")
    else:
        print(f"   ❌ analyst → 無可用模型（高品質優先）")

    # 測試 4：快速優先
    print("\n4. 快速優先策略：")
    result = allocator.allocate_task("research", priority="fast")
    if result:
        print(f"   ✅ research → {result['model_id']} (快速優先)")
    else:
        print(f"   ❌ research → 無可用模型（快速優先）")

    # 測試 5：標記任務完成
    print("\n5. 標記任務完成：")
    allocator.complete_task("zai/glm-4.7", success=True)
    print(f"   ✅ 已標記任務完成")


def test_model_monitor():
    """測試模型監控器"""
    print("\n" + "=" * 60)
    print("🧪 測試 2：模型監控器")
    print("=" * 60)

    monitor = ModelMonitor()

    # 測試 1：獲取所有模型健康度
    print("\n1. 模型健康度：")
    health_list = monitor.get_all_models_health()
    for health in health_list:
        status_icon = "✅" if health["healthy"] else "❌"
        print(f"   {status_icon} {health['model_id']}")
        print(f"      狀態：{health['status']}")
        print(f"      活躍：{health['active_tasks']}/{health['concurrent_limit']}")
        print(f"      成功率：{health['success_rate']:.2%}")
        if health['rate_limited']:
            print(f"      ⚠️  Rate limit 直到：{health['rate_limit_until']}")

    # 測試 2：獲取模型利用率
    print("\n2. 模型利用率：")
    utilization = monitor.get_model_utilization()
    for model_id, util in utilization.items():
        print(f"   {model_id}：{util['active']}/{util['limit']} ({util['percentage']:.1f}%)")

    # 測試 3：檢測 rate limit 模式
    print("\n3. 檢測 rate limit 模式：")
    models = monitor.allocator.get_model_stats()
    for model_id in models.keys():
        pattern = monitor.detect_rate_limit_pattern(model_id)
        if pattern["has_pattern"]:
            print(f"   ⚠️  {model_id}: {pattern['message']}")
        else:
            print(f"   ✅ {model_id}: 沒有明顯的 rate limit 模式")

    # 測試 4：獲取系統建議
    print("\n4. 系統建議：")
    recommendations = monitor.get_system_recommendations()
    if recommendations:
        for rec in recommendations:
            print(f"   {rec}")
    else:
        print(f"   ✅ 系統運行良好，沒有特別建議")

    # 測試 5：記錄狀態
    print("\n5. 記錄狀態：")
    monitor.log_status()


def test_rate_limit_simulation():
    """模擬 rate limit 場景"""
    print("\n" + "=" * 60)
    print("🧪 測試 3：模擬 rate limit 場景")
    print("=" * 60)

    allocator = ModelAllocator()

    print("\n1. 分配多個任務到 glm-4.7（觸發並發限制）：")
    for i in range(3):
        result = allocator.allocate_task("analyst")
        if result:
            print(f"   ✅ 任務 {i+1} → {result['model_id']}")
        else:
            print(f"   ❌ 任務 {i+1} → 無可用模型（並發限制）")

    print("\n2. 標記 glm-4.7 被 rate limit：")
    allocator.mark_rate_limit("zai/glm-4.7", cooldown_minutes=30)
    print("   ✅ glm-4.7 已標記為 rate limit")

    print("\n3. 嘗試分配任務（應該無法分配到 glm-4.7）：")
    result = allocator.allocate_task("analyst", priority="high_quality")
    if result:
        print(f"   ✅ 分配成功：{result['model_id']}")
    else:
        print(f"   ❌ 分配失敗：無可用高品質模型")

    # 測試 4：清除 rate limit
    print("\n4. 清除 rate limit（手動）：")
    model = allocator.models_config["models"]["zai/glm-4.7"]
    model["health"]["rate_limit_until"] = None
    model["health"]["status"] = "healthy"
    allocator._save_models()
    print("   ✅ rate limit 已清除")


def test_integration():
    """測試集成場景"""
    print("\n" + "=" * 60)
    print("🧪 測試 4：集成場景")
    print("=" * 60)

    print("\n場景：下午時段，glm-4.7 容易觸發 rate limit")
    print("策略：自動分配到 glm-4.5（如果已啟用）")

    allocator = ModelAllocator()

    # 模擬 glm-4.7 rate limit
    print("\n1. 標記 glm-4.7 被 rate limit：")
    allocator.mark_rate_limit("zai/glm-4.7", cooldown_minutes=30)
    print("   ✅ glm-4.7 已標記為 rate limit")

    # 嘗試分配不同類型的任務
    print("\n2. 分配不同類型的任務：")

    tasks = [
        ("research", "研究論文"),
        ("analyst", "數據分析"),
        ("creative", "撰寫報告"),
        ("automation", "系統操作")
    ]

    for agent, description in tasks:
        result = allocator.allocate_task(agent)
        if result:
            print(f"   ✅ {description:15} ({agent:10}) → {result['model_id']} (品質:{result['quality']})")
        else:
            print(f"   ❌ {description:15} ({agent:10}) → 無可用模型")

    print("\n結論：")
    print("   - 高品質任務（analyst, creative）無法分配（glm-4.7 被限流）")
    print("   - 如果啟用 glm-4.5，可以分配快速任務（research, automation）")


def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("🚀 多模型架構測試套件")
    print("=" * 60)

    try:
        # 測試 1：模型分配器
        test_model_allocator()

        # 測試 2：模型監控器
        test_model_monitor()

        # 測試 3：模擬 rate limit 場景
        test_rate_limit_simulation()

        # 測試 4：集成場景
        test_integration()

        print("\n" + "=" * 60)
        print("✅ 所有測試完成")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 測試失敗：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
