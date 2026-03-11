#!/usr/bin/env python3
"""
[廢棄] 任務啟動 Daemon - 不可行方案

原因：
- sessions_spawn 是 OpenClaw 內部工具
- 無法在子進程或腳本中使用
- 只有主會話可以調用
- 此方案已被證實不可行

替換方案：
- 使用選項 1：切換到 glm-4.5（避開嚴格限流）
- 或選項 3：等待配額重置（2-3 小時）
- 選項 2：每次心跳啟動 1 個（慢但可靠）

保留此文件僅作記錄，不應使用。
"""

raise NotImplementedError("此方案不可行：sessions_spawn 只能在主會話調用，無法在 daemon 中使用")
