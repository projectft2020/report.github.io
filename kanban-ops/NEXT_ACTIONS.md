# 接下來的行動計劃

**日期**: 2026-02-20
**狀態**: Phase 1 完成，進入驗證與監控階段

---

## 🎯 核心目標

1. **驗證 Progressive Research 效果** - 確認 token 消耗真的降低 57%
2. **監控 Auto-Recovery 運行狀況** - 確保無假陽性
3. **決定是否需要 Phase 2** - 評估 gateway timeout 影響

---

## ✅ 立即行動（本週內完成）

### 行動 1: 創建第一個 Progressive Research 任務 ⭐ **最高優先級**

**目的**: 驗證 token 消耗確實降低 57%

**步驟**:

```bash
# 1. 連接到生產環境
ssh charlie@192.168.1.117

# 2. 創建帶有 progressive protocol 的研究任務
cd ~/.openclaw/workspace/kanban-ops
python3 create_progressive_research_task.py create \
    --task-id h004 \
    --question "分析 2026 年量化交易中機器學習模型的應用趨勢和最佳實踐"

# 3. 將任務分配給 research agent（使用你的正常流程）

# 4. 監控 checkpoint 創建
watch -n 30 'ls -lh ~/.openclaw/workspace/kanban/projects/h004/research_checkpoints/'
```

**預期結果**:
- ✅ 每 3 次搜索創建 1 個 checkpoint
- ✅ 總 token 消耗 < 250k（vs h001 的 467k）
- ✅ 任務成功完成（不會 timeout）
- ✅ Final report 質量高

**驗證方法**:
```bash
# 檢查 checkpoints
ls -l ~/.openclaw/workspace/kanban/projects/h004/research_checkpoints/

# 檢查 token 消耗（在任務完成後從 logs 中查找）
grep -r "h004.*token" ~/.openclaw/logs/*.log
```

**時間**: 等待研究任務完成（預計 15-20 分鐘）

---

### 行動 2: 監控 Auto-Recovery 運行狀況

**目的**: 確保自動恢復正常工作，無假陽性

**每日檢查**:

```bash
ssh charlie@192.168.1.117

# 查看最近的恢復活動
tail -50 ~/.openclaw/logs/auto_recovery.log

# 檢查是否有誤恢復（false positives）
cd ~/.openclaw/workspace/kanban
python3 -c "
import json
with open('tasks.json', 'r') as f:
    tasks = json.load(f)

# 找出被自動恢復的任務
recovered = [t for t in tasks if t.get('time_tracking', {}).get('auto_recovered')]

if recovered:
    print(f'發現 {len(recovered)} 個自動恢復的任務:')
    for t in recovered:
        print(f\"  {t['id']}: {t['title']}\")
        print(f\"    原狀態: {t['time_tracking']['original_status']}\")
        print(f\"    置信度: {t['time_tracking']['recovery_confidence']}\")
        print()
else:
    print('目前無自動恢復的任務')
"
```

**檢查頻率**: 每天 1 次（約 2 分鐘）
**持續時間**: 本週每天

**預期結果**:
- ✅ 有輸出文件的 failed/terminated 任務被自動恢復
- ✅ 無輸出文件的任務保持 failed 狀態
- ✅ 所有恢復都有詳細記錄

---

### 行動 3: 收集 Baseline 數據

**目的**: 建立改進前後對比基準

**收集的數據**:

```bash
# 1. 當前任務統計
cd ~/.openclaw/workspace/kanban
python3 -c "
import json
from collections import Counter

with open('tasks.json', 'r') as f:
    tasks = json.load(f)

print('=== 整體任務統計 ===')
statuses = Counter(t['status'] for t in tasks)
total = len(tasks)
for status, count in sorted(statuses.items()):
    pct = count * 100 / total
    print(f'{status:15s}: {count:3d} ({pct:5.1f}%)')

print()
print('=== Research 任務統計 ===')
research = [t for t in tasks if 'research' in str(t).lower()]
r_statuses = Counter(t['status'] for t in research)
r_total = len(research)
for status, count in sorted(r_statuses.items()):
    pct = count * 100 / r_total if r_total > 0 else 0
    print(f'{status:15s}: {count:3d} ({pct:5.1f}%)')

print()
completed = r_statuses.get('completed', 0)
if r_total > 0:
    print(f'Research 成功率: {completed}/{r_total} = {completed*100/r_total:.1f}%')
"

# 2. Gateway timeout 統計
echo "=== 今日 Gateway Timeout ==="
grep "gateway timeout" ~/.openclaw/logs/gateway.err.log | \
  grep "$(date +%Y-%m-%d)" | wc -l

# 3. 保存 baseline
date > ~/openclaw_baseline_$(date +%Y%m%d).txt
echo "記錄當前系統狀態作為 baseline" >> ~/openclaw_baseline_$(date +%Y%m%d).txt
```

**執行時間**: 今天完成（5 分鐘）

---

## 📊 本週監控（Day 2-7）

### 每日監控清單（每天 5 分鐘）

**早上檢查** (☕ 喝咖啡時順便看):

```bash
# 快速健康檢查腳本
ssh charlie@192.168.1.117 "cat > ~/daily_check.sh << 'EOF'
#!/bin/bash
echo \"========================================\"
echo \"OpenClaw 每日健康檢查\"
echo \"日期: \$(date '+%Y-%m-%d %H:%M')\"
echo \"========================================\"
echo \"\"

# 1. Auto-recovery 狀態
echo \"[1] Auto-Recovery 最近活動:\"
tail -5 ~/.openclaw/logs/auto_recovery.log 2>/dev/null || echo \"  無最近活動\"
echo \"\"

# 2. 今日 gateway timeout
echo \"[2] 今日 Gateway Timeout:\"
timeout_count=\$(grep \"gateway timeout\" ~/.openclaw/logs/gateway.err.log | grep \"\$(date +%Y-%m-%d)\" | wc -l | tr -d ' ')
echo \"  \${timeout_count} 次\"
echo \"\"

# 3. Progressive research 任務
echo \"[3] Progressive Research 任務:\"
find ~/.openclaw/workspace/kanban/projects -type d -name \"research_checkpoints\" | \
  while read dir; do
    task=\$(dirname \$dir | xargs basename)
    count=\$(ls \"\$dir\"/checkpoint_*.md 2>/dev/null | wc -l | tr -d ' ')
    if [ \$count -gt 0 ]; then
      echo \"  \$task: \$count checkpoints\"
    fi
  done
echo \"\"

# 4. 任務成功率快速統計
echo \"[4] 任務狀態快速統計:\"
cd ~/.openclaw/workspace/kanban
python3 << PYEOF
import json
from collections import Counter
with open('tasks.json', 'r') as f:
    tasks = json.load(f)
statuses = Counter(t['status'] for t in tasks)
total = len(tasks)
completed = statuses.get('completed', 0)
print(f\"  總任務: {total}\")
print(f\"  完成: {completed} ({completed*100/total:.1f}%)\")
print(f\"  失敗: {statuses.get('failed', 0)}\")
PYEOF

echo \"\"
echo \"========================================\"
EOF
chmod +x ~/daily_check.sh
"

# 每天執行
ssh charlie@192.168.1.117 "~/daily_check.sh"
```

**記錄觀察結果**（建議用簡單的筆記）:
- Progressive research 任務是否成功？
- Token 消耗是多少？
- Auto-recovery 是否正常工作？
- Gateway timeout 趨勢如何？

---

## 🔍 第一週結束時的評估（2026-02-27）

### 評估清單

**Progressive Research 效果**:
- [ ] 至少完成 1 個 progressive research 任務
- [ ] Token 消耗 < 250k（vs h001 的 467k）
- [ ] 成功率 > 90%
- [ ] Checkpoints 正常創建
- [ ] Final report 質量良好

**Auto-Recovery 效果**:
- [ ] 無假陽性（沒有錯誤恢復）
- [ ] 有輸出的任務被正確恢復
- [ ] 無輸出的任務保持 failed
- [ ] 30 分鐘內完成恢復

**系統整體健康**:
- [ ] 整體成功率維持或提升
- [ ] 無新的系統問題
- [ ] Gateway timeout 維持在可接受範圍

### 評估後決策樹

```
評估結果如何？
│
├─ ✅ Progressive Research 效果顯著（token -50%+, 成功率 >90%）
│   └─> 繼續使用，推廣到所有 research 任務
│       選項：
│       A. 維持現狀，繼續監控
│       B. 開始規劃 Prometheus 監控（可選）
│
├─ ⚠️ Progressive Research 效果一般（token -30-50%）
│   └─> 需要調優
│       • 調整 checkpoint interval (2 或 5 次搜索)
│       • 改進 synthesis 質量
│       • 再測試 1 週
│
├─ ✅ Gateway Timeout 不影響工作（< 10 次/天）
│   └─> Phase 2 (TypeScript 優化) 可以延後
│
└─ ❌ Gateway Timeout 嚴重影響（> 50 次/天）
    └─> 需要啟動 Phase 2
        • 設置開發環境
        • 實施 TypeScript 層優化
        • 動態 timeout + 重試機制
```

---

## 🚀 Phase 2 選項（視 Week 1 評估結果決定）

### 選項 A: TypeScript 層優化（解決 Gateway Timeout）

**適用情況**: Gateway timeout 嚴重影響工作

**準備工作**:
1. 設置 OpenClaw 開發環境
2. 理解 bundled code 結構
3. 制定測試計劃

**實施內容**:
- 動態 announce timeout (15s → 15-60s)
- 5 次重試機制
- 更好的錯誤處理

**預期效果**: Timeout 33/天 → <5/天 (-85%)

**時間投入**: 3-5 天
**風險**: 中（需要修改 bundled code）

---

### 選項 B: Prometheus + Grafana 監控

**適用情況**: 想要更好的可觀測性

**準備工作**:
1. 規劃監控指標
2. 設計 dashboard
3. 配置告警規則

**實施內容**:
- Prometheus 部署
- Grafana dashboard
- 自定義 metrics
- 智能告警

**預期效果**: 完整的實時監控和可視化

**時間投入**: 3-5 天
**風險**: 低（獨立系統）

---

### 選項 C: 優化現有系統（持續改進）

**適用情況**: 當前效果已經很好

**可能的改進**:
- 動態 checkpoint interval
- 更好的 synthesis prompts
- 自動化測試
- 更多統計和報告

**時間投入**: 靈活
**風險**: 極低

---

## 📅 時間規劃總覽

### 本週（2026-02-21 到 2026-02-27）

| 日期 | 任務 | 時間 |
|------|------|------|
| **Day 1 (今天)** | 創建第一個 progressive research 任務 | 30 分鐘 |
| **Day 1** | 收集 baseline 數據 | 5 分鐘 |
| **Day 2-7** | 每日健康檢查 | 5 分鐘/天 |
| **Day 3** | 檢查第一個 research 任務結果 | 10 分鐘 |
| **Day 7** | 週末評估和決策 | 30 分鐘 |

**總時間投入**: 約 2 小時/週

---

### 下週（視評估結果而定）

**情況 1: 一切順利** ✅
- 繼續使用 progressive research
- 保持日常監控（減少頻率到每週 2-3 次）
- 考慮是否需要 Phase 2

**情況 2: 需要調優** ⚙️
- 調整參數
- 再測試一週
- 持續每日監控

**情況 3: 需要 Phase 2** 🚀
- 啟動 TypeScript 優化或監控系統部署
- 制定詳細實施計劃

---

## 🎯 成功指標

### 本週末應該達成

- [ ] 至少 1 個 progressive research 任務完成
- [ ] Token 消耗數據收集完成
- [ ] Auto-recovery 運行 7 天無問題
- [ ] 決定是否需要 Phase 2

### 本月末應該達成

- [ ] 5+ progressive research 任務完成
- [ ] 平均 token 消耗 < 200k
- [ ] Research 成功率 > 95%
- [ ] 系統穩定運行無重大問題

---

## 📞 快速參考命令

### 創建 Progressive Research 任務

```bash
ssh charlie@192.168.1.117
cd ~/.openclaw/workspace/kanban-ops
python3 create_progressive_research_task.py create \
    --task-id <task-id> \
    --question "<研究問題>"
```

### 每日健康檢查

```bash
ssh charlie@192.168.1.117
~/daily_check.sh
```

### 查看特定任務的 checkpoints

```bash
ls -lh ~/.openclaw/workspace/kanban/projects/<task-id>/research_checkpoints/
cat ~/.openclaw/workspace/kanban/projects/<task-id>/research_checkpoints/checkpoint_1.md
```

### 手動觸發 auto-recovery

```bash
cd ~/.openclaw/workspace/kanban-ops
python3 recover_tasks.py
```

---

## 📚 相關文檔

| 文檔 | 位置 | 用途 |
|------|------|------|
| 快速開始指南 | `~/.openclaw/workspace/kanban-ops/QUICK_START_PROGRESSIVE_RESEARCH.md` | 日常參考 |
| Progressive 協議 | `~/.openclaw/workspace/kanban-ops/research_agent_progressive_protocol.md` | 完整協議 |
| Phase 1 完成報告 | `/Users/david/Documents/openclaw_matrix/PROGRESSIVE_RESEARCH_IMPLEMENTATION.md` | 實施細節 |
| 總體摘要 | `/Users/david/Documents/openclaw_matrix/OPTIMIZATION_COMPLETE_SUMMARY.md` | 全局視角 |

---

## ⚡ TL;DR（最簡版）

### 今天必做（30 分鐘）

1. **創建第一個 progressive research 任務** - 驗證 token 降低
   ```bash
   ssh charlie@192.168.1.117
   cd ~/.openclaw/workspace/kanban-ops
   python3 create_progressive_research_task.py create --task-id h004 --question "你的研究問題"
   ```

2. **設置每日健康檢查** - 運行上面提供的腳本創建 `daily_check.sh`

### 本週每天（5 分鐘）

```bash
ssh charlie@192.168.1.117
~/daily_check.sh
```

### 週末評估（30 分鐘）

- 檢查 progressive research 效果
- 決定是否需要 Phase 2
- 規劃下週行動

---

**最重要的事**: 創建第一個 progressive research 任務，驗證 token 消耗確實降低 ✅

**現在就開始**: `ssh charlie@192.168.1.117` 然後創建任務！🚀
