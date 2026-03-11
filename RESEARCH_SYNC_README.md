# Research Sync System - 使用說明

## 概述

研究報告同步系統會自動將 Kanban 中完成的研究報告同步到 Obsidian vault，並根據內容分類到適當的目錄。

## 目錄結構

```
quant/research/
├── Research/
│   ├── INDEX.md                          # 主索引
│   ├── Market-Microstructure/
│   │   └── INDEX.md                      # 分類索引
│   ├── Risk-Management/
│   │   └── INDEX.md
│   ├── Strategy-Development/
│   │   └── INDEX.md
│   ├── Machine-Learning/
│   │   └── INDEX.md
│   └── [其他分類...]
```

## 使用方式

### 1. 掃描新報告
```bash
cd ~/.openclaw/workspace && python3 research_sync_system.py scan
```

### 2. 同步所有未同步的報告
```bash
cd ~/.openclaw/workspace && python3 research_sync_system.py sync-all
```

### 3. 查看同步狀態
```bash
cd ~/.openclaw/workspace && python3 research_sync_system.py status
```

### 4. 同步單個報告
```bash
cd ~/.openclaw/workspace && python3 research_sync_system.py sync <task_id>
```

## 自動同步

整合到 HEARTBEAT.md，每次心跳自動執行：

```bash
cd ~/.openclaw/workspace && python3 research_sync_system.py sync-all
```

## 分類規則

系統會根據報告內容中的關鍵詞自動分類：

| 分類 | 關鍵詞 |
|------|--------|
| Market-Microstructure | market microstructure, order flow, liquidity, bid-ask |
| Risk-Management | risk, hedge, var, cvar, tail risk, crisis, drawdown |
| Strategy-Development | strategy, trading, backtest, momentum, mean reversion |
| Empirical-Testing | empirical, testing, validation, out-of-sample, backtest |
| Factor-Investing | factor, alpha, beta, exposure, premium |
| Machine-Learning | machine learning, neural network, deep learning, ai, model |
| Economic-Analysis | economic, macro, fomc, inflation, gdp, recession |
| Crypto-Research | crypto, bitcoin, ethereum, blockchain, defi |

## Frontmatter 格式

每個同步的報告都會添加 YAML frontmatter：

```yaml
---
task_id: crisis-hedge-20260310-223500
title: 危機對沖策略整合實證研究報告
category: Risk-Management
tags: []
date: 2026-03-11T02:04:52.664996
summary: ...
source: kanban
---
```

## 索引系統

- **主索引** (`Research/INDEX.md`) - 列出所有分類
- **分類索引** (`Research/<Category>/INDEX.md`) - 列出該分類下的所有報告

## 技術細節

- **同步數據庫**：`.research_sync_db.json` - 記錄已同步的任務
- **去重機制**：通過 file hash 檢測變更
- **增量同步**：只同步新完成的任務
- **自動分類**：基於關鍵詞的智能分類

## 故障排除

### 報告未同步
檢查任務狀態是否為 `completed`：
```bash
cd ~/.openclaw/workspace && python3 research_sync_system.py status
```

### 分類錯誤
手動移動文件到正確的分類目錄，或關鍵詞優化（修改 `research_sync_system.py` 中的 `research_categories`）

### Obsidian 顯示異常
確保 Obsidian vault 路徑正確（默認：`/Users/charlie/.openclaw/workspace/quant/research`）

---

**創建日期**：2026-03-11
**版本**：1.0
**作者**：Charlie
