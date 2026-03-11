# 自動化系統配置

**配置日期:** 2026-03-04 11:45 AM (Asia/Taipei)
**狀態:** ✅ 已配置並啟用

---

## Cron 任務配置

### 已配置的定時任務

| 任務 | 頻率 | 命令 | 日誌 |
|------|------|------|------|
| Skills 維護檢查 | 每小時 | `python3 kanban-ops/maintenance_check.py` | `logs/maintenance.log` |
| 研究品質檢查 | 每天 9:00 AM | `python3 kanban-ops/research_quality_check.py` | `logs/quality.log` |
| 自動恢復 | 每 30 分鐘 | `kanban-ops/auto_recovery.sh` | |

### Cron 詳細配置

```cron
# OpenClaw 自動恢復 - 每 30 分鐘運行一次
*/30 * * * * ~/.openclaw/workspace/kanban-ops/auto_recovery.sh

# Skills 維護檢查 - 每小時運行一次
0 * * * * cd ~/.openclaw/workspace && python3 kanban-ops/maintenance_check.py >> ~/.openclaw/workspace/logs/maintenance.log 2>&1

# 研究品質檢查 - 每天早上 9 點運行
0 9 * * * cd ~/.openclaw/workspace && python3 kanban-ops/research_quality_check.py >> ~/.openclaw/workspace/logs/quality.log 2>&1
```

---

## 自動化任務說明

### 1. Skills 維護檢查

**運行頻率:** 每小時（0 分鐘）

**執行的檢查:**
- ✅ Scout 依賴檢查（pybloom_live）
- ✅ 任務超時檢查（spawning: 2h, in_progress: 24h）
- ✅ 任務異常檢測（卡住任務、無效優先級、孤兒任務）
- ✅ 優先級規則驗證
- ✅ 任務狀態報告

**輸出位置:**
- 標準輸出：`logs/maintenance.log`
- 異常任務：控制台輸出

**用途:**
- 檢測系統異常
- 及時發現卡住的任務
- 驗證配置正確性

---

### 2. 研究品質檢查

**運行頻率:** 每天 9:00 AM

**執行的檢查:**
- ✅ 自動評分最近的研究（24 小時內）
- ✅ 自動提取高分研究洞察（>= 7.0）
- ✅ 生成評分統計報告
- ✅ 生成質量趨勢圖

**輸出位置:**
- 標準輸出：`logs/quality.log`
- 評分文件：`kanban/projects/*/research.score`
- 洞察文件：`kanban/projects/*/research.insights`
- 趨勢圖：`kanban/projects/quality_trend.png`

**用途:**
- 自動評估研究品質
- 提取高價值洞察
- 追踪品質趨勢

---

### 3. 自動恢復

**運行頻率:** 每 30 分鐘

**執行的操作:**
- 檢查系統狀態
- 自動恢復失敗任務
- 清理臨時文件

**用途:**
- 系統容錯
- 自動清理

---

## 日誌管理

### 日誌位置

```bash
~/.openclaw/workspace/logs/
├── maintenance.log    # Skills 維護檢查日誌
└── quality.log        # 研究品質檢查日誌
```

### 查看日誌

**查看維護檢查日誌（最近 50 行）:**
```bash
tail -50 ~/.openclaw/workspace/logs/maintenance.log
```

**查看品質檢查日誌（最近 50 行）:**
```bash
tail -50 ~/.openclaw/workspace/logs/quality.log
```

**實時監控日誌:**
```bash
tail -f ~/.openclaw/workspace/logs/maintenance.log
tail -f ~/.openclaw/workspace/logs/quality.log
```

### 日誌輪轉

考慮設置 logrotate 來管理日誌大小：

```bash
# 安裝 logrotate（如果尚未安裝）
brew install logrotate

# 創建配置文件
sudo vim /usr/local/etc/logrotate.d/openclaw
```

配置內容：
```
~/.openclaw/workspace/logs/*.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
```

---

## 手動執行

### 運行維護檢查

**運行所有檢查:**
```bash
cd ~/.openclaw/workspace && python3 kanban-ops/maintenance_check.py
```

**運行單個檢查:**
```bash
cd ~/.openclaw/workspace && python3 kanban-ops/maintenance_check.py dependencies
cd ~/.openclaw/workspace && python3 kanban-ops/maintenance_check.py timeouts
cd ~/.openclaw/workspace && python3 kanban-ops/maintenance_check.py anomalies
cd ~/.openclaw/workspace && python3 kanban-ops/maintenance_check.py rules
cd ~/.openclaw/workspace && python3 kanban-ops/maintenance_check.py state
```

---

### 運行研究品質檢查

**檢查最近 24 小時的研究:**
```bash
cd ~/.openclaw/workspace && python3 kanban-ops/research_quality_check.py
```

**檢查指定時間範圍:**
```bash
cd ~/.openclaw/workspace && python3 kanban-ops/research_quality_check.py --hours 48
```

**顯示評分統計:**
```bash
cd ~/.openclaw/workspace && python3 kanban-ops/research_quality_check.py --stats
```

---

## 監控和告警

### 當前系統狀態

**檢查 cron 服務:**
```bash
ps aux | grep cron | grep -v grep
```

**檢查當前 cron 任務:**
```bash
crontab -l
```

**查看最近運行記錄:**
```bash
tail -50 ~/.openclaw/workspace/logs/maintenance.log
tail -50 ~/.openclaw/workspace/logs/quality.log
```

---

### 告警建議

雖然當前沒有自動告警系統，但可以考慮：

1. **郵件告警:** 在腳本中添加郵件發送功能
2. **Telegram 通知:** 使用 OpenClaw 的 message 工具發送通知
3. **Slack 通知:** 集成到工作空間

**示例：添加 Telegram 通知**

在 `maintenance_check.py` 中添加：
```python
# 發送告警（如果發現嚴重問題）
if failed_count > 3:
    from openclaw import message
    message.send(
        channel="telegram",
        message=f"⚠️ 維護檢查發現 {failed_count} 個問題"
    )
```

---

## 故障排除

### Cron 任務未執行

**檢查 cron 服務:**
```bash
ps aux | grep cron
```

**檢查 cron 日誌:**
```bash
grep CRON /var/log/system.log | tail -20
```

**驗證 cron 配置:**
```bash
crontab -l
```

### 腳本執行失敗

**檢查 Python 路徑:**
```bash
which python3
```

**檢查腳本權限:**
```bash
ls -l kanban-ops/maintenance_check.py
ls -l kanban-ops/research_quality_check.py
```

**手動執行腳本查看錯誤:**
```bash
cd ~/.openclaw/workspace && python3 kanban-ops/maintenance_check.py
cd ~/.openclaw/workspace && python3 kanban-ops/research_quality_check.py
```

---

## 配置修改

### 修改運行頻率

**編輯 cron 任務:**
```bash
crontab -e
```

**常用頻率設置:**
```cron
# 每 30 分鐘
*/30 * * * * command

# 每小時
0 * * * * command

# 每 6 小時
0 */6 * * * command

# 每天
0 9 * * * command

# 每週
0 9 * * 0 command

# 每月
0 9 1 * * command
```

---

## 未來改進

### 短期（1-2 週）

1. **添加告警機制**
   - 集成 Telegram 通知
   - 設置告警閾值（超時任務數量、異常數量）

2. **日誌優化**
   - 設置 logrotate
   - 添加日誌分析腳本

3. **性能監控**
   - 追踪執行時間
   - 識別性能瓶頸

### 中期（1-3 個月）

1. **自動化擴展**
   - 自動修復簡單問題（如無效優先級）
   - 自動重新啟動失敗任務

2. **儀表板**
   - 可視化系統狀態
   - 實時監控任務執行

3. **報告生成**
   - 每週/每月自動報告
   - 系統健康評分

---

## 總結

### 已配置的服務

- ✅ Cron 服務運行中
- ✅ 3 個定時任務已配置
- ✅ 日誌系統已設置
- ✅ 所有腳本測試通過

### 自動化覆蓋

- **系統維護:** 每小時
- **品質檢查:** 每天
- **自動恢復:** 每 30 分鐘

### 監控建議

- 每週檢查日誌
- 每月檢查系統健康
- 根據需要調整頻率

---

**配置完成時間:** 2026-03-04 11:45 AM (Asia/Taipei)
**系統狀態:** ✅ 自動化已啟用並正常運行
