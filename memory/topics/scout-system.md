# Scout System

> **Category:** Scout Agent 數據源、偏好學習、掃描器、反饋收集
> **Source:** MEMORY.md 2026-02-20 to 2026-02-23
> **Last Updated:** 2026-02-23

---

## 📡 數據源

### API 數據源
| 數據源 | 類型 | 狀態 | 可靠性 | 掃描頻率 |
|--------|------|------|---------|---------|
| **arXiv** | API | ✅ 活躍 | 0.95 | 每天 |
| **Reddit** | API（模擬）| ✅ 活躍 | 0.8 | 每天 |
| **News** | Web | ✅ 活躍 | 0.75 | 每天 |

### 爬文數據源（Phase 2.1-W - HIGH 優先級）
| 數據源 | 狀態 | 可靠性 | 掃描頻率 | 特點 |
|--------|------|---------|---------|------|
| **Threads** | ✅ 活躍 | 0.7 | 每 2 小時 | 監控 @top3pct |
| **Quantocracy** | ✅ 活躍 | 0.75 | 每天 | 量化博客聚合器 |
| **QuantConnect** | ✅ 活躍 | 0.75 | 每天 | 算法交易平台社群 |
| **Nuclear Phynance** | ✅ 活躍 | 0.8 | 每天 | 專業量化金融論壇 |
| **QuantNet** | ✅ 活躍 | 0.75 | 每天 | 量化教育和職業討論 |

### 爬文數據源（Phase 2.2-W - MEDIUM-HIGH 優先級）
| 數據源 | 狀態 | 可靠性 | 掃描頻率 | 特點 |
|--------|------|---------|---------|------|
| **SSRN** | ✅ 活躍 | 0.8 | 每天 | 社會科學研究網絡 |
| **NBER** | ✅ 活躍 | 0.8 | 每天 | 國家經濟研究局 |
| **Hedge Fund Reports** | ✅ 活躍 | 0.75 | 每天 | AQR、Two Sigma、Citadel、Man AHL |
| **TradingView** | ✅ 活躍 | 0.7 | 每天 | Pine Script 策略社群 |
| **Quant StackExchange** | ✅ 活躍 | 0.8 | 每天 | 量化金融問答 |

**總計數據源：** 12 個（2 個 API + 10 個爬文）
**預估掃描頻率：** 每 2-4 小時
**預估主題數：** 100+ 主題/天

---

## 🎯 用戶偏好（Scout）

### 高權重主題（affinity_score: 0.9）
- performance_metrics - 績效指標（Omega、CSR、Kappa、SKTASR）
- risk_adjusted_metrics - 風險調整指標
- fat_tail_analysis - 肥尾分佈分析
- skewness_kurtosis - 偏度/峰度調整策略
- quantitative_research - 量化研究

### 正面關鍵詞
- mathematical derivation - 數學推導
- empirical testing - 實證測試
- rolling window - 滾動窗口分析
- statistical significance - 統計顯著性檢驗
- diebold-mariano - Diebold-Mariano 檢驗
- hypothesis testing - 假設檢驗
- fat-tailed - 肥尾分佈
- power law - 功率法則
- tail index - 尾指數
- coherent risk measure - 魯棒風險度量
- utility function - 效用函數
- maximum likelihood - 最大似然
- monte carlo - Monte Carlo 模擬
- backtesting - 回測驗證

### 負面關鍵詞
- simple - 簡單過度簡化
- basic - 基礎內容
- tutorial - 教程類容

### 數據源可靠性評分
| 數據源 | Reliability Score | 評分標準 |
|--------|-----------------|-----------|
| arXiv | 0.95 | 學術來源，標準化 API |
| reddit_r_quant | 0.8 | 社群討論，質量參差不齊 |
| reddit_r_algotrading | 0.8 | 社群討論，質量參差不齊 |
| bloomberg | 0.75 | 新聞數據源，時效性 |
| reuters | 0.75 | 新聞數據源，時效性 |
| threads | 0.7 | 社交媒體，內容長度限制 |

---

## 🧠 學習機制

### 用戶反饋收集
**狀態：** 🆕 待實施（Phase 2 學習部分）
**目標：** 收集用戶對 Scout 推薦任務的反饋
**輸入：**
- 對任務的評分（1-5 分）
- 是否深入（是否想要更多細節）
- 是否有價值（是否繼續研究方向）

**預期效果：**
- 提高推薦準確度
- 學習用戶偏好
- 動態調整評分權重

---

### 反饋分析引擎
**狀態：** 🆕 待實施
**功能：**
- 分析反饋模式
- 識別高價值主題
- 更新評分權重

**指標：**
- 平均評分
- 評分標準差
- 高評分主題的共同特徵

---

### 動態權重調整機制
**狀態：** 🆕 待實施
**目標：** 根據反饋動態調整 Scout 的推薦系統
**調整內容：**
- 主題權重（topics affinity_scores）
- 來源權重（sources reliability_scores）
- 關鍵詞權重（keywords positive/negative weights）
- 子代理偏好（agent preferences）

**調整頻率：** 每週或每 10 個反饋後

---

## 📊 Scout 統計

### 掃描統計（截至 2026-02-23）
- **總掃描次數：** 3 次
- **總發現主題：** 60 個
- **推薦任務：** 0 個（創建但未推薦）
- **創建任務：** 0 個

### 反饋統計
- **總反饋數：** 0
- **平均評分：** 0
- **需要開始：** 用戶需要開始提供反饋幫助 Scout 改進

### QDM (Query Distribution Manager) 狀態
- **總主題數：** 504（緩存）
- **來源分佈：** arXiv、Reddit、News
- **去重效果：** 90%+ 去重率

---

## 🔧 使用方法

### 基本使用
```bash
cd ~/.openclaw/workspace-scout

# 執行完整掃描（包含所有 12 個數據源）
python3 scout_agent.py scan

# 只掃描爬文數據源
python3 scout_agent.py web-only

# 測試所有功能
python3 scout_agent.py test

# 查看統計信息
python3 scout_agent.py stats
```

### 個別掃描器使用
```bash
# Phase 2.1-W
python3 scout_agent.py threads
python3 scout_agent.py quantocracy
python3 scout_agent.py quantconnect
python3 scout_agent.py nuclearphynance
python3 scout_agent.py quantnet

# Phase 2.2-W
python3 scout_agent.py ssrn
python3 scout_agent.py nber
python3 scout_agent.py hedge_funds
python3 scout_agent.py tradingview
python3 scout_agent.py quant_se
```

### Monitor and Refill 集成
```bash
cd ~/workspace
python3 kanban-ops/monitor_and_refill.py
```
**功能：**
- Event-driven task monitoring（無需 cron）
- 自動觸發 Scout 掃描（任務 < 3 且上次掃描 > 2 小時）
- 防止過度掃描（2 小時保護窗）

---

## 📁 配置文件

### PREFERENCES.json
**位置：** `~/.openclaw/workspace-scout/PREFERENCES.json`
**內容：**
- 用戶偏好（topics, sources, keywords）
- 反饋統計（feedbacks）
- 數據源可靠性（sources_reliability）
- 子代理偏好（agent_preferences）

### SOURCES.md
**位置：** `~/.openclaw/workspace-scout/SOURCES.md`
**內容：**
- 數據源列表（URL、配置、過濾器）
- 更新歷史
- 監控狀態

---

## 🌐 Scout Reports Web 界面

### 項目概述
- **位置：** `~/.openclaw/workspace/ScoutReports/`
- **狀態：** ✅ 設計完成（2026-03-04）
- **實施時間：** 9-13 天（完整實施）

### 核心功能
- 📖 **報告展示** - Markdown 渲染、元數據顯示
- 🔍 **全文搜索** - SQLite FTS5、高亮顯示
- 🏷️ **過濾和標籤** - 按狀態、主題、日期過濾
- ⭐ **反饋收集** - 評分、評論、偏好學習
- 📈 **分析儀表板** - 統計、趨勢、可視化
- 🎓 **偏好學習** - EMA 更新、親和度調整

### 技術架構
- **後端：** FastAPI + SQLite + Pydantic
- **前端：** React 19 + Vite + React Bootstrap
- **部署：** Docker + Docker Compose（獨立容器）
- **端口：** Backend 8001, Frontend 5174

### Agent-Ready 設計
- ✅ 簡化 API 包裝器（`AgentAPI` 類）
- ✅ 全面文檔（模組、函數、類級 docstring）
- ✅ 類型提示（完整覆蓋）
- ✅ 標準化響應格式
- ✅ OpenAPI 規範（自動生成）
- ✅ 結構化日誌（Loguru）
- ✅ 配置管理（Pydantic + 環境變量）
- ✅ 依賴注入（FastAPI）

### API 端點
**報告：**
- `GET /api/reports` - 列出所有報告（支持分頁和過濾）
- `GET /api/reports/{path}` - 獲取完整報告內容
- `GET /api/reports/{path}/metadata` - 獲取報告元數據

**反饋：**
- `POST /api/feedback` - 提交反饋（觸發偏好學習）
- `GET /api/feedback/{report_id}` - 獲取報告反饋

**搜索：**
- `GET /api/search` - 全文搜索

**分析：**
- `GET /api/analytics/overview` - 總體統計
- `GET /api/analytics/trends` - 趨勢分析

**偏好：**
- `GET /api/preferences` - 獲取 Scout 偏好
- `GET /api/preferences/topics` - 獲取主題親和度

### 文檔資源
- **DESIGN.md** (63 KB) - 完整技術設計
- **README.md** (11 KB) - 項目概覽和快速入門
- **API.md** (10 KB) - API 參考
- **DEVELOPER_GUIDE.md** (19 KB) - 開發者指南
- **PROJECT_SUMMARY.md** (11 KB) - 項目總結

### Agent 使用示例
```python
from app.api.agent_api import AgentAPI

api = AgentAPI(base_url="http://localhost:8001")

# 列出報告
reports = api.list_reports(status="completed", limit=10)

# 獲取報告
report = api.get_report(reports[0]["path"])

# 搜索
results = api.search_reports("machine learning")

# 提交反饋
api.submit_feedback(
    task_id=report["task_id"],
    rating=5,
    feedback_type="positive"
)

# 獲取分析
stats = api.get_analytics()

# 獲取偏好
prefs = api.get_preferences()
```

### 下一步
1. 選擇實施路徑（完整/MVP/分階段）
2. 設置開發環境
3. 實施後端 API（Day 3-4）
4. 實施前端核心（Day 5-6）
5. 集成 Scout 數據（Day 9）

---

## 🚀 Phase 2.3-W 待實施

### 券商量化報告（MEDIUM 優先級）
- **時間估算：** 2 小時
- **來源：** 投行、券商研究部門
- **預期內容：** 市場洞察、投資建議、研究報告

### Fintech Media（MEDIUM 優先級）
- **時間估算：** 1.5 小時
- **來源：** 金融科技媒體、新聞平台
- **預期內容：** 市場趨勢、新興技術、行業動態

**總計：** 3.5 小時

---

## 📈 下一步重點

1. **實施 Phase 2 學習部分**（用戶反饋收集 + 反饋分析 + 動態權重調整）
2. **實施 Phase 2.3-W**（券商報告 + Fintech Media）
3. **提高反饋收集率**
4. **優化掃描器性能**
5. **探索新的數據源**

---

## 📝 學習記錄

### 2026-03-04
- ✅ Scout Reports 項目設計完成（106 KB 文檔）
- ✅ Agent-ready 設計（API 包裝器、類型提示、全面文檔）
- ✅ 獨立項目架構（不與 Dashboard 合併）
- ✅ 完整 API 規範（報告、反饋、搜索、分析、偏好）
- ✅ 前後端技術棧規範（FastAPI + React 19）
- ✅ 開發者指南和項目總結
- **關鍵決策：** Scout Reports 為獨立項目，與 Dashboard 分離
- **實施時間：** 9-13 天（完整實施）

### 2026-02-23
- ✅ Scout Phase 2.1-W 完成（10 個爬文掃描器）
- ✅ 通用網頁掃描器框架
- ✅ 所有掃描器測試通過
- ✅ 集成到完整掃描流程
- **系統狀態：** 12 個數據源（2 API + 10 爬文）

### 2026-02-20
- ✅ Threads 數據源新增（@top3pct）
- ✅ Scout 偏好更新（用戶偏好）
- ✅ 研究報告標準模板建立

---

**下一步行動：**
- Scout Reports 項目實施（選擇完整/MVP/分階段路徑）
- 用戶需要開始提供反饋幫助 Scout 改進推薦質量
- 實施 Phase 2.3-W（券商報告 + Fintech Media）
- 實施 Phase 2 學習部分（反饋收集、分析、動態調整）
