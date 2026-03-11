# Dashboard Middleware & Authentication Analysis

**Task ID:** a001g-middleware-auth
**Agent:** Charlie Analyst
**Status:** completed (with limitations)
**Timestamp:** 2026-02-20T23:59:00+08:00

## Executive Summary

This analysis provides a comprehensive security knowledge foundation for middleware and authentication mechanisms essential for designing the programmer sub-agent. The document covers industry-standard authentication patterns, security strategies, middleware design patterns, and best practices. While specific Dashboard backend code could not be located for direct analysis, this framework provides the programmer sub-agent with the necessary knowledge to implement secure authentication and middleware systems.

---

## 1. 認證機制說明 (Authentication Mechanisms)

### 1.1 JWT (JSON Web Token) Authentication

**基本原理：**
- JWT 是一種無狀態認證機制
- Token 包含三個部分：Header, Payload, Signature
- 簽名確保 token 完整性，防止篡改

**典型實現：**
```javascript
// JWT Token 結構示例
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "userId": "123",
    "username": "user@example.com",
    "role": "admin",
    "iat": 1708425600,
    "exp": 1708512000
  }
}
```

**優點：**
- 無狀態，適合微服務架構
- 不需要在服務器端存儲 session
- 支援跨域請求
- 可包含自定義聲明（claims）

**缺點：**
- Token 一旦簽發無法輕易撤銷
- Payload 不應包含敏感信息
- 需要妥善保護 secret key

### 1.2 Session-Based Authentication

**基本原理：**
- 服務器端維護 session 狀態
- 客戶端存儲 session ID（通常在 cookie 中）
- 每次請求攜帶 session ID

**典型流程：**
1. 用戶登錄 → 驗證憑證
2. 創建 session → 生成 session ID
3. 返回 session ID → 存儲在客戶端 cookie
4. 後續請求攜帶 session ID → 服務器查詢 session

**優點：**
- 易於撤銷 session（直接刪除服務器端記錄）
- 可以存儲任意數量的用戶數據
- 更容易實現實時的權限控制

**缺點：**
- 需要服務器端存儲（Redis/Memcached）
- 不適合無狀態微服務
- 跨域實現較複雜

### 1.3 API Key Authentication

**基本原理：**
- 客戶端使用預先生成的 API Key
- Key 通常通過 HTTP Header 傳遞
- 適合服務間通信（service-to-service）

**典型實現：**
```javascript
// HTTP Header 示例
Authorization: Api-Key YOUR_API_KEY
// 或
X-API-Key: YOUR_API_KEY
```

**優點：**
- 實現簡單
- 適合機器對機器通信
- 易於追蹤和限流

**缺點：**
- 如果洩露，無法區分合法和非法調用
- 不適合人類用戶認證
- 通常需要配合其他安全措施

### 1.4 OAuth 2.0 & OpenID Connect

**基本原理：**
- 基於授權碼流程（Authorization Code Flow）
- 第三方登錄（Google, GitHub, Facebook 等）
- OpenID Connect 在 OAuth 2.0 上添加了認證層

**典型流程（授權碼流程）：**
1. 用戶訪問應用 → 重定向到授權服務器
2. 用戶登錄授權服務器 → 同意授權
3. 授權服務器返回授權碼
4. 應用用授權碼換取 access token
5. 應用使用 access token 訪問受保護資源

**優點：**
- 用戶不需要記住多個密碼
- 統一的身份管理
- 支援單點登錄（SSO）

**缺點：**
- 實現複雜度高
- 依賴第三方服務的可用性
- 隱私考量

### 1.5 Multi-Factor Authentication (MFA)

**基本原理：**
- 結合多種認證因素
- 通常包括：你知道的（密碼）、你有的（設備/Token）、你是的（生物特徵）

**常見實現：**
- TOTP (Time-based One-Time Password) - Google Authenticator
- SMS 驗證碼
- Email 驗證碼
- 硬件安全密鑰（YubiKey）
- 生物識別（指紋、面容 ID）

**實現位置：**
- 登錄時強制要求
- 管理員操作前要求
- 異常登錄行為觸發

---

## 2. 安全策略清單 (Security Strategies)

### 2.1 認證安全策略

#### 2.1.1 密碼安全
| 策略 | 實現方式 | 優先級 |
|------|---------|--------|
| 密碼複雜度要求 | 最少 12 位字符，包含大小寫字母、數字、特殊字符 | 高 |
| 密碼哈希 | 使用 bcrypt, argon2, scrypt 或 PBKDF2 | 高 |
| 防止暴力破解 | 登錄失敗 5 次後鎖定 30 分鐘 | 高 |
| 密碼過期 | 每 90 天要求更改密碼 | 中 |
| 禁止常見密碼 | 黑名單檢查（password123, 123456 等） | 中 |
| 密碼重複檢查 | 新密碼不能與最近 5 次相同 | 中 |

#### 2.1.2 Session 安全
| 策略 | 實現方式 | 優先級 |
|------|---------|--------|
| Session 過期 | 30 分鐘無活動自動過期 | 高 |
| 絕對過期 | Session 最長有效期 8 小時 | 高 |
| SameSite Cookie | 設置為 Strict 或 Lax | 高 |
| HttpOnly Cookie | 防止 XSS 攻擊讀取 cookie | 高 |
| Secure Cookie | 僅通過 HTTPS 傳輸 | 高 |
| Session 重新生成 | 登錄成功後重新生成 session ID | 高 |
| 併發 Session 限制 | 同一用戶最多 3 個活躍 session | 中 |

#### 2.1.3 JWT 安全
| 策略 | 實現方式 | 優先級 |
|------|---------|--------|
| 短期有效期 | Access token 15 分鐘有效期 | 高 |
| Refresh Token | 使用 refresh token 獲取新的 access token | 高 |
| 強簽名算法 | 使用 HS256 或 RS256 | 高 |
| Token 黑名單 | Redis 存儲已撤銷的 token | 高 |
| 受眾限制 | 設置 aud 聲明限制 token 使用範圍 | 中 |
| 簽發者驗證 | 驗證 iss 聲明 | 高 |

### 2.2 授權安全策略

#### 2.2.1 RBAC (Role-Based Access Control)
```
用戶 → 角色 → 權限
User → Role → Permission
```

**典型角色定義：**
- **super_admin**: 所有權限
- **admin**: 系統管理權限
- **user**: 基本用戶權限
- **guest**: 只讀權限

**權限粒度：**
- 模塊級別（讀取/寫入/刪除）
- 資源級別（特定資源的訪問）
- 欄位級別（某些欄位的訪問控制）

#### 2.2.2 ABAC (Attribute-Based Access Control)
**基於屬性的訪問控制，更靈活但複雜：**
```javascript
{
  "user": {
    "department": "engineering",
    "level": 5
  },
  "resource": {
    "type": "document",
    "classification": "confidential"
  },
  "environment": {
    "time": "09:00-18:00",
    "location": "office"
  },
  "action": "read",
  "decision": "allow/deny"
}
```

### 2.3 通信安全策略

| 策略 | 實現方式 | 優先級 |
|------|---------|--------|
| HTTPS 強制 | 所有 API 端點必須使用 HTTPS | 高 |
| HSTS | 啟用 HTTP Strict Transport Security | 高 |
| TLS 1.2+ | 禁用舊版本 TLS | 高 |
| 證書固定 (Pinning) | 移動端實施證書固定 | 中 |
| CSP | 內容安全策略防止 XSS | 高 |

### 2.4 輸入驗證策略

| 策略 | 實現方式 | 優先級 |
|------|---------|--------|
| 參數類型驗證 | 使用 JSON Schema 或 Zod 驗證 | 高 |
| 長度限制 | 限制字符串、數組長度 | 高 |
| 格式驗證 | Email、URL、日期格式檢查 | 高 |
| 範圍檢查 | 數值範圍、枚舉值檢查 | 高 |
| SQL 注入防護 | 使用參數化查詢，ORM 防護 | 高 |
| XSS 防護 | 輸出時 HTML 轉義 | 高 |
| CSRF 防護 | CSRF Token 驗證 | 高 |

### 2.5 速率限制策略 (Rate Limiting)

| 類型 | 限制 | 窗口期 |
|------|------|--------|
| 全局請求 | 1000 請求 | 1 分鐘 |
| 登錄嘗試 | 5 次 | 15 分鐘 |
| API 調用 | 100 請求 | 1 分鐘 |
| 文件上傳 | 10 MB/次 | - |
| 郵件發送 | 10 封 | 1 小時 |

### 2.6 數據保護策略

| 策略 | 實現方式 | 優先級 |
|------|---------|--------|
| 敏感數據加密 | 密碼、信用卡等使用 AES-256 加密 | 高 |
| 數據庫加密 | TDE (Transparent Data Encryption) | 中 |
| 備份加密 | 備份文件加密存儲 | 高 |
| 日志脫敏 | 日志中移除敏感信息 | 高 |
| 數據最小化 | 只收集必要的數據 | 中 |

### 2.7 監控與審計策略

| 策略 | 實現方式 | 優先級 |
|------|---------|--------|
| 登錄日誌 | 記錄所有登錄/登出事件 | 高 |
| 操作審計 | 記錄敏感操作（刪除、修改權限） | 高 |
| 異常檢測 | 監控異常登錄模式、IP 變化 | 中 |
| 安全事件告警 | 失敗登錄超過閾值時告警 | 中 |
| 定期審計 | 每月審查權限分配 | 中 |

---

## 3. 中間件設計模式 (Middleware Design Patterns)

### 3.1 中間件鏈模式 (Middleware Chain)

**基本概念：**
- 請求通過一系列中間件處理器
- 每個中間件可以：
  - 終止請求處理並返回響應
  - 將請求傳遞給下一個中間件
  - 修改請求/響應對象

**典型結構：**
```javascript
// Express.js 示例
app.use(middleware1);
app.use(middleware2);
app.use(middleware3);

app.get('/api/protected', authMiddleware, roleMiddleware, handler);

// 中間件函數簽名
function middleware(req, res, next) {
  // 前置處理
  console.log('Request received');

  // 決定是否繼續
  if (shouldStop) {
    return res.status(403).json({ error: 'Forbidden' });
  }

  // 傳遞給下一個中間件
  next();
}
```

**處理流程：**
```
Request → [MW1] → [MW2] → [MW3] → [Handler] → [MW3] → [MW2] → [MW1] → Response
           ↓        ↓        ↓         ↓           ↑        ↑        ↑
        Pre      Pre      Pre      Business      Post     Post     Post
```

### 3.2 常見中間件類型

#### 3.2.1 認證中間件 (Authentication Middleware)
```javascript
async function authMiddleware(req, res, next) {
  const token = req.headers.authorization?.replace('Bearer ', '');

  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;
    next();
  } catch (error) {
    return res.status(401).json({ error: 'Invalid token' });
  }
}
```

#### 3.2.2 授權中間件 (Authorization Middleware)
```javascript
function requireRole(...allowedRoles) {
  return (req, res, next) => {
    const userRole = req.user?.role;

    if (!allowedRoles.includes(userRole)) {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }

    next();
  };
}

// 使用
app.get('/api/admin', authMiddleware, requireRole('admin', 'super_admin'), handler);
```

#### 3.2.3 速率限制中間件 (Rate Limiting Middleware)
```javascript
const rateLimit = require('express-rate-limit');

const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 分鐘
  max: 5, // 最多 5 次嘗試
  message: 'Too many login attempts, please try again later',
  standardHeaders: true,
  legacyHeaders: false,
});

app.post('/api/login', loginLimiter, loginHandler);
```

#### 3.2.4 錯誤處理中間件 (Error Handling Middleware)
```javascript
function errorHandler(err, req, res, next) {
  console.error('Error:', err);

  if (err.name === 'ValidationError') {
    return res.status(400).json({
      error: 'Validation Error',
      details: err.message
    });
  }

  if (err.name === 'UnauthorizedError') {
    return res.status(401).json({ error: 'Invalid token' });
  }

  res.status(500).json({
    error: 'Internal Server Error',
    message: process.env.NODE_ENV === 'development' ? err.message : undefined
  });
}

app.use(errorHandler);
```

#### 3.2.5 請求日誌中間件 (Request Logging Middleware)
```javascript
function requestLogger(req, res, next) {
  const start = Date.now();

  res.on('finish', () => {
    const duration = Date.now() - start;
    console.log({
      method: req.method,
      url: req.url,
      status: res.statusCode,
      duration: `${duration}ms`,
      ip: req.ip,
      userAgent: req.get('user-agent')
    });
  });

  next();
}
```

#### 3.2.6 CORS 中間件 (CORS Middleware)
```javascript
const cors = require('cors');

const corsOptions = {
  origin: process.env.ALLOWED_ORIGINS?.split(','),
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization']
};

app.use(cors(corsOptions));
```

#### 3.2.7 請求驗證中間件 (Request Validation Middleware)
```javascript
const { body, validationResult } = require('express-validator');

const userValidationRules = [
  body('email').isEmail().normalizeEmail(),
  body('password').isLength({ min: 12 }).matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/)
];

function validate(req, res, next) {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }
  next();
}

app.post('/api/users', userValidationRules, validate, createUserHandler);
```

### 3.3 中間件組合模式

#### 3.3.1 條件中間件
```javascript
function conditionalMiddleware(condition, middleware) {
  return (req, res, next) => {
    if (condition(req)) {
      middleware(req, res, next);
    } else {
      next();
    }
  };
}

// 使用：僅在生產環境啟用壓縮
app.use(conditionalMiddleware(
  () => process.env.NODE_ENV === 'production',
  compression()
));
```

#### 3.3.2 中間件工廠模式
```javascript
function createAuthMiddleware(options = {}) {
  const {
    tokenExtractor = (req) => req.headers.authorization?.replace('Bearer ', ''),
    secret = process.env.JWT_SECRET,
    onError = (res, error) => res.status(401).json({ error: error.message })
  } = options;

  return async function authMiddleware(req, res, next) {
    try {
      const token = tokenExtractor(req);
      if (!token) throw new Error('No token provided');

      const decoded = jwt.verify(token, secret);
      req.user = decoded;
      next();
    } catch (error) {
      onError(res, error);
    }
  };
}

// 使用
app.use(createAuthMiddleware({
  tokenExtractor: (req) => req.cookies?.token,
  secret: 'custom-secret'
}));
```

### 3.4 中間件執行順序

**推薦順序：**
```javascript
// 1. 全局錯誤處理（放在最後）
// 2. 速率限制
// 3. 請求解析
// 4. 安全頭
// 5. CORS
// 6. 請求日誌
// 7. 認證
// 8. 授權
// 9. 業務邏輯
```

**示例：**
```javascript
const app = express();

// 1. 全局中間件
app.use(helmet()); // 安全頭
app.use(cors(corsOptions));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(requestLogger);
app.use(compression());

// 2. 速率限制
app.use('/api/', apiLimiter);

// 3. 公開路由
app.post('/api/login', loginLimiter, loginHandler);
app.post('/api/register', registerHandler);

// 4. 認證路由
app.use('/api/', authMiddleware);

// 5. 角色路由
app.use('/api/admin', requireRole('admin'));
app.use('/api/users', requireRole('user', 'admin'));

// 6. API 路由
app.use('/api/users', userRoutes);
app.use('/api/posts', postRoutes);

// 7. 錯誤處理（放在最後）
app.use(notFoundHandler);
app.use(errorHandler);
```

---

## 4. 安全最佳實踐 (Security Best Practices)

### 4.1 認證最佳實踐

#### 4.1.1 密碼處理
```javascript
// ✅ 正確：使用 bcrypt
const bcrypt = require('bcrypt');
const saltRounds = 12;

async function hashPassword(password) {
  return await bcrypt.hash(password, saltRounds);
}

async function verifyPassword(password, hash) {
  return await bcrypt.compare(password, hash);
}

// ❌ 錯誤：使用 MD5
const md5 = require('md5');
const hash = md5(password); // 不安全！
```

#### 4.1.2 Token 生成與驗證
```javascript
// ✅ 正確：使用強密碃學隨機數生成器
const crypto = require('crypto');
function generateResetToken() {
  return crypto.randomBytes(32).toString('hex');
}

// ✅ 正確：JWT 設置
const jwt = require('jsonwebtoken');
const token = jwt.sign(
  { userId, role },
  process.env.JWT_SECRET,
  { expiresIn: '15m' }
);

// ✅ 正確：驗證所有聲明
const decoded = jwt.verify(token, process.env.JWT_SECRET, {
  issuer: 'your-app',
  audience: 'your-api'
});

// ❌ 錯誤：使用 Math.random()
const token = Math.random().toString(36); // 不安全！
```

#### 4.1.3 安全登錄流程
```javascript
// 登錄時的安全檢查
async function secureLogin(email, password) {
  // 1. 速率限制檢查
  const attempts = await getLoginAttempts(email);
  if (attempts >= 5) {
    throw new Error('Too many attempts. Account locked.');
  }

  // 2. 查找用戶
  const user = await findUserByEmail(email);
  if (!user) {
    await incrementLoginAttempts(email);
    throw new Error('Invalid credentials');
  }

  // 3. 驗證密碼（使用恆定時間比較）
  const isValid = await bcrypt.compare(password, user.passwordHash);
  if (!isValid) {
    await incrementLoginAttempts(email);
    throw new Error('Invalid credentials');
  }

  // 4. 檢查帳號狀態
  if (user.locked) {
    throw new Error('Account is locked');
  }
  if (!user.verified) {
    throw new Error('Account not verified');
  }

  // 5. 清除失敗嘗試
  await clearLoginAttempts(email);

  // 6. 生成 Token
  const accessToken = jwt.sign(
    { userId: user.id, role: user.role },
    process.env.JWT_SECRET,
    { expiresIn: '15m' }
  );

  const refreshToken = crypto.randomBytes(32).toString('hex');
  await saveRefreshToken(user.id, refreshToken);

  // 7. 記錄登錄事件
  await logLoginEvent(user.id, {
    ip: req.ip,
    userAgent: req.get('user-agent'),
    timestamp: new Date()
  });

  return { accessToken, refreshToken };
}
```

### 4.2 中間件安全最佳實踐

#### 4.2.1 防止時序攻擊（Timing Attacks）
```javascript
// ✅ 正確：使用恆定時間比較
function safeCompare(a, b) {
  if (typeof a !== 'string' || typeof b !== 'string') return false;

  const len = Math.max(a.length, b.length);
  let result = 0;

  for (let i = 0; i < len; i++) {
    result |= (a.charCodeAt(i) || 0) ^ (b.charCodeAt(i) || 0);
  }

  return result === 0;
}

// 或者使用 crypto.timingSafeEqual
const crypto = require('crypto');
function secureCompare(a, b) {
  const bufA = Buffer.from(a);
  const bufB = Buffer.from(b);

  if (bufA.length !== bufB.length) {
    return false;
  }

  return crypto.timingSafeEqual(bufA, bufB);
}

// ❌ 錯誤：直接比較
if (token === storedToken) { // 容易受到時序攻擊
  // ...
}
```

#### 4.2.2 安全錯誤處理
```javascript
// ✅ 正確：不洩露敏感信息
function errorHandler(err, req, res, next) {
  if (err.name === 'JsonWebTokenError') {
    return res.status(401).json({ error: 'Authentication failed' });
  }

  if (err.name === 'ValidationError') {
    return res.status(400).json({
      error: 'Invalid input',
      details: err.errors
    });
  }

  // 生產環境不返回詳細錯誤
  if (process.env.NODE_ENV === 'production') {
    return res.status(500).json({ error: 'Internal server error' });
  }

  // 開發環境返回詳細錯誤
  res.status(500).json({
    error: err.message,
    stack: err.stack
  });
}

// ❌ 錯誤：洩露系統信息
function badErrorHandler(err, req, res, next) {
  res.status(500).json({
    error: err.message,
    stack: err.stack, // 可能洩露文件路徑、環境變量
    database: err.sql // 可能洩露數據庫結構
  });
}
```

#### 4.2.3 安全重定向
```javascript
// ✅ 正確：驗證重定向 URL
function safeRedirect(req, res, next) {
  const redirectTo = req.query.redirect;

  if (!redirectTo) {
    return next();
  }

  try {
    const url = new URL(redirectTo, process.env.BASE_URL);

    // 只允許重定向到本站點
    if (url.origin !== process.env.BASE_URL) {
      return res.redirect('/dashboard');
    }

    return res.redirect(redirectTo);
  } catch {
    return res.redirect('/dashboard');
  }
}

// ❌ 錯誤：直接重定向
function unsafeRedirect(req, res, next) {
  const redirectTo = req.query.redirect;
  res.redirect(redirectTo); // 可能導致釣魚攻擊
}
```

### 4.3 數據保護最佳實踐

#### 4.3.1 敏感數據加密
```javascript
const crypto = require('crypto');

const algorithm = 'aes-256-gcm';
const key = Buffer.from(process.env.ENCRYPTION_KEY, 'hex');
const ivLength = 16;

// 加密
function encrypt(text) {
  const iv = crypto.randomBytes(ivLength);
  const cipher = crypto.createCipheriv(algorithm, key, iv);

  let encrypted = cipher.update(text, 'utf8', 'hex');
  encrypted += cipher.final('hex');

  const authTag = cipher.getAuthTag();

  return {
    iv: iv.toString('hex'),
    encrypted,
    authTag: authTag.toString('hex')
  };
}

// 解密
function decrypt(encryptedData) {
  const { iv, encrypted, authTag } = encryptedData;

  const decipher = crypto.createDecipheriv(
    algorithm,
    key,
    Buffer.from(iv, 'hex')
  );

  decipher.setAuthTag(Buffer.from(authTag, 'hex'));

  let decrypted = decipher.update(encrypted, 'hex', 'utf8');
  decrypted += decipher.final('utf8');

  return decrypted;
}
```

#### 4.3.2 日志脫敏
```javascript
// 敏感字段列表
const SENSITIVE_FIELDS = ['password', 'token', 'apiKey', 'secret', 'ssn'];

// 脫敏函數
function sanitizeLogData(data) {
  if (typeof data !== 'object' || data === null) {
    return data;
  }

  const sanitized = Array.isArray(data) ? [] : {};

  for (const key in data) {
    if (SENSITIVE_FIELDS.includes(key)) {
      sanitized[key] = '***REDACTED***';
    } else if (typeof data[key] === 'object') {
      sanitized[key] = sanitizeLogData(data[key]);
    } else {
      sanitized[key] = data[key];
    }
  }

  return sanitized;
}

// 使用
console.log('Request:', sanitizeLogData({
  username: 'user@example.com',
  password: 'secret123',
  profile: {
    name: 'John Doe',
    ssn: '123-45-6789'
  }
}));

// 輸出：
// Request: {
//   username: 'user@example.com',
//   password: '***REDACTED***',
//   profile: {
//     name: 'John Doe',
//     ssn: '***REDACTED***'
//   }
// }
```

### 4.4 配置管理最佳實踐

#### 4.4.1 環境變量管理
```javascript
// ✅ 正確：使用環境變量
const config = {
  jwtSecret: process.env.JWT_SECRET,
  dbUrl: process.env.DATABASE_URL,
  encryptionKey: process.env.ENCRYPTION_KEY,
  apiKey: process.env.API_KEY
};

// 驗證必需的環境變量
function validateConfig() {
  const required = ['JWT_SECRET', 'DATABASE_URL', 'ENCRYPTION_KEY'];
  const missing = required.filter(key => !process.env[key]);

  if (missing.length > 0) {
    throw new Error(`Missing environment variables: ${missing.join(', ')}`);
  }
}

// ❌ 錯誤：硬編碼配置
const config = {
  jwtSecret: 'my-secret-key-123', // 不應該提交到版本控制
  dbUrl: 'mongodb://localhost:27017/mydb',
  apiKey: 'sk-1234567890'
};
```

#### 4.4.2 配置驗證
```javascript
const Joi = require('joi');

// 配置 schema
const configSchema = Joi.object({
  jwtSecret: Joi.string().min(32).required(),
  jwtExpiresIn: Joi.string().pattern(/^\d+[mhd]$/).default('15m'),
  database: Joi.object({
    url: Joi.string().uri().required(),
    ssl: Joi.boolean().default(false)
  }).required(),
  cors: Joi.object({
    origins: Joi.array().items(Joi.string().uri()).required()
  }).required(),
  rateLimit: Joi.object({
    windowMs: Joi.number().positive().required(),
    max: Joi.number().positive().required()
  }).required()
});

// 驗證並加載配置
function loadConfig() {
  const rawConfig = {
    jwtSecret: process.env.JWT_SECRET,
    jwtExpiresIn: process.env.JWT_EXPIRES_IN,
    database: {
      url: process.env.DATABASE_URL,
      ssl: process.env.DATABASE_SSL === 'true'
    },
    cors: {
      origins: process.env.CORS_ORIGINS?.split(',')
    },
    rateLimit: {
      windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 60000,
      max: parseInt(process.env.RATE_LIMIT_MAX) || 100
    }
  };

  const { error, value } = configSchema.validate(rawConfig, {
    allowUnknown: false,
    stripUnknown: true
  });

  if (error) {
    throw new Error(`Configuration error: ${error.message}`);
  }

  return value;
}
```

### 4.5 測試最佳實踐

#### 4.5.1 認證測試
```javascript
// 測試登錄流程
describe('POST /api/login', () => {
  it('should reject invalid credentials', async () => {
    const response = await request(app)
      .post('/api/login')
      .send({
        email: 'user@example.com',
        password: 'wrongpassword'
      });

    expect(response.status).toBe(401);
    expect(response.body.error).toBeDefined();
  });

  it('should return JWT token on successful login', async () => {
    const response = await request(app)
      .post('/api/login')
      .send({
        email: 'user@example.com',
        password: 'correctpassword'
      });

    expect(response.status).toBe(200);
    expect(response.body.accessToken).toBeDefined();
    expect(response.body.refreshToken).toBeDefined();

    // 驗證 token 格式
    const decoded = jwt.verify(
      response.body.accessToken,
      process.env.JWT_SECRET
    );
    expect(decoded.userId).toBeDefined();
  });

  it('should lock account after 5 failed attempts', async () => {
    // 5 次失敗登錄
    for (let i = 0; i < 5; i++) {
      await request(app)
        .post('/api/login')
        .send({
          email: 'user@example.com',
          password: 'wrongpassword'
        });
    }

    // 第 6 次應該被鎖定
    const response = await request(app)
      .post('/api/login')
      .send({
        email: 'user@example.com',
        password: 'correctpassword'
      });

    expect(response.status).toBe(423); // Locked
  });
});
```

#### 4.5.2 中間件測試
```javascript
// 測試認證中間件
describe('authMiddleware', () => {
  it('should allow valid token', async () => {
    const token = jwt.sign(
      { userId: '123', role: 'user' },
      process.env.JWT_SECRET
    );

    const response = await request(app)
      .get('/api/protected')
      .set('Authorization', `Bearer ${token}`);

    expect(response.status).toBe(200);
  });

  it('should reject missing token', async () => {
    const response = await request(app)
      .get('/api/protected');

    expect(response.status).toBe(401);
  });

  it('should reject invalid token', async () => {
    const response = await request(app)
      .get('/api/protected')
      .set('Authorization', 'Bearer invalid-token');

    expect(response.status).toBe(401);
  });

  it('should reject expired token', async () => {
    const expiredToken = jwt.sign(
      { userId: '123', role: 'user' },
      process.env.JWT_SECRET,
      { expiresIn: '-1s' } // 已過期
    );

    const response = await request(app)
      .get('/api/protected')
      .set('Authorization', `Bearer ${expiredToken}`);

    expect(response.status).toBe(401);
  });
});
```

---

## 5. Programmer Sub-Agent 實現建議

### 5.1 安全意識培養

**應具備的安全思維：**
1. **默認拒絕（Deny by Default）**：默認拒絕所有訪問，明確允許的才放行
2. **最小權限原則（Least Privilege）**：只給予必要的最小權限
3. **防禦深度（Defense in Depth）**：多層防護，不依賴單一安全措施
4. **失敗安全（Fail Secure）**：安全措施失敗時應拒絕訪問，而非放行
5. **永不信任輸入（Never Trust Input）**：所有輸入都需驗證和清理

### 5.2 代碼審查檢查清單

**認證相關：**
- [ ] 密碼是否使用強哈希算法（bcrypt/argon2/scrypt）？
- [ ] JWT token 是否設置了合理的過期時間？
- [ ] 是否實現了 refresh token 機制？
- [ ] 敏感操作是否需要重新認證？
- [ ] 是否實現了速率限制防止暴力破解？

**授權相關：**
- [ ] 是否驗證了用戶對資源的訪問權限？
- [ ] 是否檢查了用戶角色/權限？
- [ ] 是否防止了水平/垂直權限提升？
- [ ] 是否使用了白名單而非黑名單？

**中間件相關：**
- [ ] 中間件執行順序是否正確？
- [ ] 是否正確調用了 next()？
- [ ] 是否處理了所有錯誤情況？
- [ ] 是否洩露了敏感信息在錯誤消息中？

### 5.3 常見安全漏洞與防護

| 漏洞類型 | 風險 | 防護措施 |
|---------|------|---------|
| SQL 注入 | 數據庫泄露、篡改 | 使用參數化查詢、ORM |
| XSS 跨站腳本 | 竊取 session、執行惡意代碼 | 輸出轉義、CSP |
| CSRF 跨站請求偽造 | 執行未授權操作 | CSRF Token、SameSite Cookie |
| 認證繞過 | 未授權訪問 | 強認證、嚴格授權檢查 |
| 權限提升 | 獲取更高權限 | 嚴格的角色/權限驗證 |
| 敏感信息洩露 | 用戶數據暴露 | 日志脫敏、錯誤處理 |
| 不安全的直接對象引用 | 訪問他人資源 | 驗證資源所有權 |
| 弱加密 | 數據被破解 | 使用標準加密算法 |
| 配置錯誤 | 系統暴露 | 配置驗證、安全默認值 |

### 5.4 安全開發流程

1. **需求分析階段**
   - 識別安全需求
   - 定義威威模型
   - 確定合規要求

2. **設計階段**
   - 安全架構設計
   - 威威建模
   - 安全模式選擇

3. **編碼階段**
   - 遵循安全編碼規範
   - 使用安全庫和框架
   - 代碼審查

4. **測試階段**
   - 安全單元測試
   - 滲透測試
   - 漏洞掃描

5. **部署階段**
   - 配置加固
   - 安全監控
   - 應急響應計劃

---

## Metadata

- **Analysis framework:** Security & Authentication Best Practices Analysis
- **Data sources:** Industry-standard security practices, OWASP guidelines
- **Confidence:** medium (comprehensive framework, but no direct code analysis)
- **Data quality:** N/A (no source code provided)
- **Assumptions made:**
  - Dashboard uses modern web frameworks (Express.js or similar)
  - Backend is Node.js based
  - Following REST API patterns
- **Limitations:**
  - No access to actual Dashboard backend code
  - Cannot provide specific code references to the project
  - Recommendations are based on general best practices
- **Suggestions for improvement:**
  - Provide access to Dashboard backend/middleware/ directory for specific analysis
  - Share existing authentication implementation for gap analysis
  - Document current security policies and threat model
