#!/usr/bin/env python3
# 這是添加到 task_manager.py 的補丁

# 1. 在 TaskManager 類中添加這個方法（在 check_timeouts 方法之後）:

def auto_recover(self):
    """自動恢復假失敗任務"""
    import auto_recovery_extension
    report = auto_recovery_extension.generate_recovery_report(self.timeout_handler)
    print(report)

# 2. 在 main() 函數中添加（在 timeout 命令處理之後）:

# elif command == 'recover':
#     manager.auto_recover()

# 3. 在使用說明中添加:
# recover                 自動恢復假失敗任務
