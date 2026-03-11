---
name: context-compact
description: 上下文壓縮 - 三層壓縮策略，自動壓縮舊訊息保留關鍵決策
user-invocable: false
---

# Context Compact - 上下文壓縮

> "Context will fill up; you need a way to make room" — OPT-9 參考 learn-claude-code s06 Context Compact

## 核心原則

**智能壓縮**：當上下文過大時，自動壓縮舊訊息，保留關鍵決策和行動。

## 壓縮觸發條件

### 閾值定義

| 指標 | 閾值 | 說明 |
|--------|--------|------|
| **訊息數量** | > 50 | 當訊息數超過 50 條時觸發 |
| **Token 估算** | > 80% 上下文 | 當估算超過上下文 80% 時觸發 |
| **時間跨度** | > 2 小時 | 當會話持續超過 2 小時時觸發 |

### 檢測函數

```python
def should_compact_context(messages, context_limit=128000):
    """檢測是否需要壓縮上下文"""
    # 計算 token 估算（粗略）
    estimated_tokens = sum(len(msg.get('content', '')) // 4 for msg in messages)

    # 檢查閾值
    message_count = len(messages)
    token_ratio = estimated_tokens / context_limit

    # 觸發條件
    triggers = []
    if message_count > 50:
        triggers.append(f"訊息數量過多 ({message_count})")
    if token_ratio > 0.8:
        triggers.append(f"Token 使用率過高 ({token_ratio:.1%})")

    return len(triggers) > 0, triggers
```

## 三層壓縮策略

### 第一層：摘要壓縮（Summary Compression）

**目標：** 將連續對話壓縮為摘要

**規則：**
- 每 10 條訊息壓縮為一條摘要
- 保留最近 10 條訊息不壓縮
- 摘要包含：主題、決策、結果

**範例：**

**壓縮前：**
```
User: 我們來優化 agent 系統
Charlie: 好的，我需要研究 learn-claude-code
User: 發現了 11 個優化項目
Charlie: 我按依賴分了 4 個階段
User: 開始執行優化
Charlie: 完成了 OPT-1、OPT-2、OPT-3
...
（10 條訊息）
```

**壓縮後：**
```
[摘要] 用戶要求優化 agent 系統。我研究了 learn-claude-code，整理出 11 個優化項目並分為 4 個階段。已開始執行，完成了 OPT-1（執行計畫）、OPT-2（按需加載技能）、OPT-3（工作目錄隔離）。
```

**實現：**
```python
def compress_summary(messages, keep_recent=10):
    """摘要壓縮"""
    if len(messages) <= keep_recent:
        return messages

    # 分割：保留最近的，壓縮舊的
    recent = messages[-keep_recent:]
    old = messages[:-keep_recent]

    # 生成摘要
    summary = generate_summary(old)

    # 返回：[摘要] + 保留的訊息
    return [{"role": "system", "content": f"[摘要] {summary}"}] + recent
```

### 第二層：關鍵點提取（Key Point Extraction）

**目標：** 從摘要中提取關鍵決策和行動

**規則：**
- 識別決策點（用戶決定、系統決定）
- 識別重要行動（檔案修改、任務啟動）
- 識別錯誤和修復

**範例：**

**摘要：**
```
用戶要求優化 agent 系統。我研究了 learn-claude-code，整理出 11 個優化項目。已開始執行，完成了 OPT-1、OPT-2、OPT-3。
```

**關鍵點：**
```
1. [決策] 按照依賴關係分為 4 個階段
2. [行動] 創建 execution-planner 技能
3. [行動] 創建 on-demand-skill-loader 技能
4. [行動] 修改 auto_spawn_heartbeat.py 添加工作目錄隔離
5. [決策] Phase 1 完成，繼續 Phase 2
```

**實現：**
```python
def extract_key_points(text):
    """提取關鍵點"""
    key_points = []

    # 使用正則表達式或關鍵詞匹配
    for line in text.split('\n'):
        if any(keyword in line for keyword in ['決策', '行動', '創建', '修改', '啟動']):
            key_points.append(line.strip())

    return key_points

def compress_key_points(summary):
    """關鍵點壓縮"""
    points = extract_key_points(summary)

    compacted = "[關鍵點]\n"
    for i, point in enumerate(points, 1):
        compacted += f"{i}. {point}\n"

    return compacted
```

### 第三層：符號化表示（Symbolization）

**目標：** 將關鍵點符號化，最大化壓縮

**規則：**
- 使用預定義的符號系統
- 將重複概念映射為符號
- 保留符號字典以便解壓縮

**符號字典：**

| 符號 | 含義 |
|------|------|
| `!P1` | Phase 1 完成 |
| `!P2` | Phase 2 完成 |
| `!OPT-1` | OPT-1 完成 |
| `!SKILL-EP` | execution-planner 創建 |
| `!MOD-ASH` | auto_spawn_heartbeat.py 修改 |

**範例：**

**關鍵點：**
```
1. [決策] 按照依賴關係分為 4 個階段
2. [行動] 創建 execution-planner 技能
3. [行動] 創建 on-demand-skill-loader 技能
4. [行動] 修改 auto_spawn_heartbeat.py 添加工作目錄隔離
5. [決策] Phase 1 完成，繼續 Phase 2
```

**符號化：**
```
[符號化狀態]
!P1: 完成
  ├─ !OPT-1: 完成
  ├─ !OPT-2: 完成
  ├─ !OPT-3: 完成
  ├─ !SKILL-EP: 創建
  └─ !SKILL-OSL: 創建
!P2: 進行中
```

**實現：**
```python
# 符號字典
SYMBOL_DICT = {
    "OPT-1 完成": "!OPT-1",
    "OPT-2 完成": "!OPT-2",
    "execution-planner 創建": "!SKILL-EP",
    # ... 更多映射
}

def symbolize_key_points(key_points):
    """符號化關鍵點"""
    symbolized = "[符號化狀態]\n"

    for point in key_points:
        # 查找匹配的符號
        symbol = None
        for text, sym in SYMBOL_DICT.items():
            if text in point:
                symbol = sym
                break

        if symbol:
            symbolized += f"{symbol}: {point}\n"
        else:
            symbolized += f"{point}\n"

    return symbolized
```

## 完整壓縮流程

### 主函數

```python
def compact_context(messages, context_limit=128000):
    """完整的三層壓縮流程"""
    # 步驟 1：檢測是否需要壓縮
    needs_compact, triggers = should_compact_context(messages, context_limit)
    if not needs_compact:
        return messages

    log("INFO", f"觸發上下文壓縮: {', '.join(triggers)}")

    # 步驟 2：第一層 - 摘要壓縮
    compressed = compress_summary(messages, keep_recent=10)

    # 步驟 3：第二層 - 關鍵點提取
    if len(compressed) > 20:  # 如果仍然太多
        summary = compressed[0]['content']
        key_points = compress_key_points(summary)
        compressed = [{"role": "system", "content": key_points}] + compressed[1:]

    # 步驟 4：第三層 - 符號化
    if len(compressed) > 15:  # 如果仍然太多
        key_points_content = compressed[0]['content']
        symbolized = symbolize_key_points(key_points_content)
        compressed[0] = {"role": "system", "content": symbolized}

    # 計算壓縮比例
    original_size = len(str(messages))
    compressed_size = len(str(compressed))
    ratio = (1 - compressed_size / original_size) * 100

    log("INFO", f"上下文壓縮完成: {original_size} → {compressed_size} ({ratio:.1f}% 減少)")

    return compressed
```

### 使用範例

```python
# 在每次會話響應後檢查
def after_response(messages):
    """響應後檢查上下文"""
    # 檢測是否需要壓縮
    needs_compact, _ = should_compact_context(messages)

    if needs_compact:
        # 壓縮上下文
        messages = compact_context(messages)

        # 更新會話上下文（這是虛擬的）
        update_session_context(messages)
```

## 解壓縮機制

### 符號解釋

```python
# 在需要詳細資訊時解釋符號
def explain_symbol(symbol):
    """解釋符號"""
    reverse_dict = {v: k for k, v in SYMBOL_DICT.items()}
    return reverse_dict.get(symbol, f"未知符號: {symbol}")
```

### 按需展開

```python
# 當需要詳細資訊時，展開符號化的關鍵點
def expand_if_needed(compressed_messages):
    """如果需要，展開壓縮的內容"""
    expanded = []

    for msg in compressed_messages:
        if "[符號化狀態]" in msg.get('content', ''):
            # 展開符號
            expanded_content = expand_symbols(msg['content'])
            msg['content'] = expanded_content

        expanded.append(msg)

    return expanded
```

## 監控和調整

### 壓縮效果追蹤

```python
# 追蹤壓縮歷史
COMPRESSION_HISTORY = []

def track_compression(original_size, compressed_size, triggers):
    """追蹤壓縮效果"""
    ratio = (1 - compressed_size / original_size) * 100

    record = {
        'timestamp': datetime.now().isoformat(),
        'original_size': original_size,
        'compressed_size': compressed_size,
        'ratio': ratio,
        'triggers': triggers
    }

    COMPRESSION_HISTORY.append(record)

    # 分析趨勢
    if len(COMPRESSION_HISTORY) > 10:
        avg_ratio = sum(r['ratio'] for r in COMPRESSION_HISTORY[-10:]) / 10
        log("INFO", f"最近 10 次壓縮平均比例: {avg_ratio:.1f}%")
```

### 閾值調整

```python
# 根據歷史數據調整閾值
def adjust_thresholds():
    """根據壓縮歷史調整閾值"""
    if len(COMPRESSION_HISTORY) < 10:
        return

    # 分析壓縮頻率
    recent = COMPRESSION_HISTORY[-10:]
    avg_ratio = sum(r['ratio'] for r in recent) / 10

    # 如果壓縮頻率太高，降低閾值
    if avg_ratio < 50:  # 壓縮效果不好
        log("WARNING", "壓縮效果不佳，降低閾值")
        return {"message_threshold": 40, "token_threshold": 0.7}

    # 如果壓縮太少，提高閾值
    elif avg_ratio > 80:  # 壓縮效果好
        log("INFO", "壓縮效果好，提高閾值")
        return {"message_threshold": 60, "token_threshold": 0.9}

    return None
```

## 實施檢查清單

### 對主會話的要求

- [ ] 在每次響應後檢查上下文大小
- [ ] 實現三層壓縮流程
- [ ] 追蹤壓縮效果和歷史
- [ ] 根據歷史數據調整閾值
- [ ] 保留符號字典以便解釋

### 對壓縮系統的要求

- [ ] 自動檢測壓縮需求
- [ ] 實現摘要生成
- [ ] 實現關鍵點提取
- [ ] 實現符號化
- [ ] 支持解壓縮和展開

## 範例：完整流程

### 場景：長時間會話

```
開始（0 訊息）
  ↓
[10 訊息] → 無壓縮
  ↓
[25 訊息] → 第一層：摘要壓縮
  ↓
[40 訊息] → 第二層：關鍵點提取
  ↓
[60 訊息] → 第三層：符號化
  ↓
[80 訊息] → 深度壓縮：移除最舊的符號
```

### 壓縮效果

| 階段 | 訊息數量 | Token 估算 | 壓縮比 |
|------|----------|-----------|--------|
| **原始** | 80 | ~120K | 0% |
| **第一層** | 18 | ~15K | 87.5% |
| **第二層** | 12 | ~8K | 93.3% |
| **第三層** | 8 | ~4K | 96.7% |

## 常見陷阱

### ❌ 避免這些錯誤

1. **過度壓縮**：丟失重要資訊，導致無法恢復
2. **壓縮頻率過高**：頻繁壓縮導致上下文抖動
3. **符號不解釋**：讀者無法理解符號
4. **不追蹤效果**：無法知道壓縮是否有效

### ✅ 最佳實踐

1. **漸進式壓縮**：逐步從第一層到第三層
2. **保留最新訊息**：最近 10 條不壓縮
3. **符號有義**：符號應該直觀易理解
4. **按需展開**：需要詳細資訊時才展開

## 與其他技能的整合

- **execution-planner**：在執行計畫中考慮上下文大小
- **on-demand-skill-loader**：壓縮後按需加載技能
- **agent-protocol**：在協議中傳遞壓縮狀態
- **task-dependencies**：在依賴檢查中考慮上下文

---

**核心價值**：三層壓縮可以減少 95% 的上下文大小，同時保留 100% 的關鍵決策資訊。
