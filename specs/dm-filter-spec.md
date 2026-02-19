# Charlie DM 和群組回應規格書

## 目標

實作精確的訊息回應過濾邏輯：
1. 私聊只回應 David 的訊息
2. 群組只在特定頻道被 @ 時回應

---

## 需求描述

### 1. 私聊過濾

**行為：**
- David 的私聊 → 全部回應
- 其他人的私聊 → 不回應

**識別方式：**
- 使用 Discord 用戶 ID（David 的 ID）

### 2. 群組過濾

**行為：**
- 只有在記錄的群組頻道被 @ 時回應
- 未記錄的群組頻道不回應

**識別方式：**
- 群組頻道 ID 清單（預設為空，需手動設定）

---

## 技術實作方案

### 方案：自訂 Inbound Hook

利用 OpenClaw 的 hooks 機制，在訊息進來時先過濾：

```
Inbound Message → Hook Filter → Agent 决定回應
```

---

## 設定檔調整

### openclaw.json

```json
{
  "messages": {
    "ackReactionScope": "all-messages",
    "inbound": {
      "debounceMs": 3000,
      "hookEnabled": true,
      "hookFile": "./workspace/hooks/filter-messages.js"
    }
  }
}
```

**變更：**
- `ackReactionScope` 改為 `all-messages`（讓所有訊息都進到 hook）
- 新增 `hookEnabled: true`
- 新增 `hookFile` 指向自訂過濾器

---

## Agent 邏輯（filter-messages.js）

**位置：** `~/.openclaw/workspace/hooks/filter-messages.js`

**功能：**
1. 檢查訊息類型（私聊 / 群組）
2. 私聊 → 檢查用戶 ID
3. 群組 → 檢查頻道 ID
4. 回傳 true（允許進入）或 false（攔截）

**程式碼架構：**

```javascript
const { hooks } = require('@openclaw/core');

// David 的 Discord 用戶 ID（需要手動設定）
const DAVID_USER_ID = process.env.CHARLIE_DAVID_ID || 'YOUR_ID_HERE';

// 允許回應的群組頻道 ID 清單（空清單 = 沒有群組回應）
const ALLOWED_GROUP_CHANNELS = process.env.CHARLIE_ALLOWED_CHANNELS
  ? process.env.CHARLIE_ALLOWED_CHANNELS.split(',')
  : [];

module.exports = {
  name: 'message-filter',
  async inbound(ctx) {
    const { message, user, channel, guild } = ctx;

    // 群組訊息處理
    if (guild) {
      const isMentioned = message.content.includes('<@YOUR_BOT_ID>');

      // 如果該頻道不在允許清單中，攔截
      if (!ALLOWED_GROUP_CHANNELS.includes(channel.id)) {
        return false;
      }

      // 如果沒有被 @，攔截
      if (!isMentioned) {
        return false;
      }

      // 頻道被允許且有 @，放行
      return true;
    }

    // 私聊訊息處理
    if (user) {
      // 只放行 David
      if (user.id !== DAVID_USER_ID) {
        return false;
      }

      // David 的私聊，放行
      return true;
    }

    // 其他情況，預設攔截
    return false;
  }
};
```

---

## 環境變數設定

### .env 檔案

```bash
CHARLIE_DAVID_ID=123456789012345678
CHARLIE_ALLOWED_CHANNELS=channel-id-1,channel-id-2
```

**說明：**
- `CHARLIE_DAVID_ID`：David 的 Discord 用戶 ID
- `CHARLIE_ALLOWED_CHANNELS`：允許回應的群組頻道 ID，用逗號分隔
- 空值時：群組完全不回應

---

## 取得 Discord ID

### 方法 1：從機器人日誌
啟動 Discord 機器人時，查看日誌中顯示的用戶 ID

### 方法 2：使用者設定
1. Discord → 使用者設定（User Settings）
2. 語音與視訊（Voice & Video）
3. 在控制台輸入 `/debug` 並回車
4. 查看顯示的用戶 ID

### 方法 3：從消息連結
1. 對 David 的私聊訊息按「查看訊息」
2. URL 中有 `/messages/` 後面的數字就是 ID

---

## 測試流程

### 1. 私聊測試

**測試步驟：**
1. David 在私聊發訊息 → 應該收到回應
2. 其他人在私聊發訊息 → 不應該收到回應

**檢查：**
```bash
# 在 David 的私聊中測試
你：測試訊息
Charlie：收到，有什麼需要幫忙的嗎？

# 在其他人的私聊中測試
你：測試訊息
（無回應）
```

### 2. 群組測試

**測試步驟：**
1. 在允許的群組頻道 @ Charlie → 應該收到回應
2. 在未允許的群組頻道 @ Charlie → 不應該收到回應
3. 在允許的群組頻道發訊息（沒 @）→ 不應該收到回應

**檢查：**
```bash
# 在允許的頻道（channel-id-1）測試
你：@Charlie 測試
Charlie：收到，有什麼需要幫忙的嗎？

# 在未允許的頻道測試
你：@Charlie 測試
（無回應）

# 在允許的頻道發訊息（沒 @）
你：沒有 @ Charlie 的訊息
（無回應）
```

---

## 預期行為總結

| 場景 | 行為 |
|------|------|
| David 私聊 | 回應 |
| 其他人私聊 | 不回應 |
| 允許的群組 @ Charlie | 回應 |
| 未允許的群組 @ Charlie | 不回應 |
| 群組發訊息未 @ | 不回應 |

---

## 預設值

- **群組頻道**：空清單（完全封鎖群組回應，需手動設定）
- **私聊**：只有 David 回應（預設）

---

## 進階選項（未來）

1. **時間限制**：只在特定時間範圍回應
2. **權限角色**：只有特定角色的用戶能觸發回應
3. **訊息過濾**：只回應包含特定關鍵字的訊息
4. **冷卻時間**：同一用戶/頻道的回應冷卻時間

---

## 注意事項

1. **修改後需要重啟 Gateway**
2. **錯誤時會暫時回退到 `group-mentions` 模式**
3. **群組頻道 ID 一旦設定就生效，記得定期檢查**

---

## 完成後的設定檔總覽

**openclaw.json：**
```json
{
  "messages": {
    "ackReactionScope": "all-messages",
    "inbound": {
      "debounceMs": 3000,
      "hookEnabled": true,
      "hookFile": "./workspace/hooks/filter-messages.js"
    }
  }
}
```

**環境變數：**
```bash
CHARLIE_DAVID_ID=123456789012345678
CHARLIE_ALLOWED_CHANNELS=
```

---

**建立日期：** 2026-02-16
**版本：** 1.0
**狀態：** 待實作
