# Scout v2.0 完整設計文檔

**版本:** v2.0
**日期:** 2026-03-04
**狀態:** 設計階段

---

## 目錄

1. [系統概述](#1-系統概述)
2. [多來源爬蟲架構設計](#2-多來源爬蟲架構設計)
3. [智能去重和聚合系統](#3-智能去重和聚合系統)
4. [多樣化的任務生成機制](#4-多樣化的任務生成機制)
5. [動態來源配置系統](#5-動態來源配置系統)
6. [擴展的偏好系統](#6-擴展的偏好系統)
7. [遷移策略和實現時間表](#7-遷移策略和實現時間表)
8. [風險分析和緩解措施](#8-風險分析和緩解措施)
9. [總結](#9-總結)

---

## 1. 系統概述

### 1.1 背景

Scout v1.0 是一個單來源爬蟲系統，主要從特定來源獲取新聞內容。隨著業務需求增長，v1.0 顯現出以下限制：

- 來源單一，覆蓋範圍有限
- 去重機制簡單，容易遺漏相似內容
- 任務生成缺乏多樣性
- 配置靈活性不足
- 用戶偏好系統簡陋

### 1.2 v2.0 核心目標

Scout v2.0 將構建一個**可擴展、智能化、多來源**的新聞爬蟲和推薦系統，核心目標：

1. **多來源整合** - 支持多個新聞來源並行爬取
2. **智能去重** - 基於語義相似度的高精度去重
3. **多樣化推薦** - 提供豐富的任務和內容類型
4. **動態配置** - 支持運行時來源配置調整
5. **深度個性化** - 基於多維度的用戶偏好系統
6. **平滑遷移** - 與 v1.0 兼容的漸進式升級路徑

### 1.3 系統架構概覽

```
用戶界面層 (UI Layer)
    ↓
業務邏輯層 (Service Layer)
  ├─ 推薦引擎
  ├─ 任務生成器
  └─ 用戶偏好服務
    ↓
數據處理層 (Processing Layer)
  ├─ 內容聚合服務
  ├─ 去重服務
  └─ 配置服務
    ↓
爬蟲層 (Crawler Layer)
  ├─ 來源適配器 A (News API)
  ├─ 來源適配器 B (RSS Feed)
  └─ 來源適配器 C (HTML Scraping)
    ↓
數據存儲層 (Storage Layer)
  ├─ PostgreSQL (主數據庫)
  ├─ Redis (緩存)
  └─ Elasticsearch (搜索)
    ↓
基礎設施層 (Infrastructure)
  ├─ Docker / Kubernetes
  ├─ CI/CD
  └─ 監控告警
```

---

## 2. 多來源爬蟲架構設計

### 2.1 設計原則

1. **適配器模式** - 每個來源都有獨立的適配器
2. **並行爬取** - 多個來源同時運行，互不干擾
3. **容錯機制** - 單個來源失敗不影響其他來源
4. **速率限制** - 遵守各來源的 API 限制
5. **統一數據格式** - 所有來源輸出統一的數據結構

### 2.2 來源適配器接口

```typescript
export interface SourceAdapter {
  readonly id: string;
  readonly name: string;
  readonly type: SourceType;

  initialize(config: SourceConfig): Promise<void>;
  fetchNews(options?: FetchOptions): Promise<NewsItem[]>;
  fetchNewsDetail(id: string): Promise<NewsDetail>;
  healthCheck(): Promise<HealthStatus>;
  getStats(): Promise<SourceStats>;
  cleanup(): Promise<void>;
}

export enum SourceType {
  NEWS_API = 'news_api',
  RSS_FEED = 'rss_feed',
  HTML_SCRAPER = 'html_scraper',
  WEBSOCKET = 'websocket',
  CUSTOM_API = 'custom_api',
  SOCIAL_MEDIA = 'social_media'
}
```

### 2.3 爬蟲協調器

負責協調所有來源的爬取任務，支持定時和手動觸發。

---

## 3. 智能去重和聚合系統

### 3.1 去重策略

**四層去重架構：**

1. **第一層：快速過濾** (Redis，毫秒級)
   - URL 去重 (Bloom Filter)
   - ID 去重 (Set)
   - 標題哈希 (Set)

2. **第二層：精確匹配** (PostgreSQL，秒級)
   - 精確標題匹配
   - URL 規范化

3. **第三層：模糊匹配** (PostgreSQL pg_trgm，秒級)
   - 標題相似度匹配 (Levenshtein / Trigram)

4. **第四層：語義去重** (向量數據庫 + ML，分鐘級)
   - 提取內容嵌入 (Sentence Transformers)
   - 向量相似度搜索 (Pinecone / Weaviate)
   - 聚合相似文章 (DBSCAN / HDBSCAN)

### 3.2 去重服務實現

（包含完整的 TypeScript 實現）

---

## 4. 多樣化的任務生成機制

### 4.1 任務類型架構

**支持 15+ 種任務類型：**

- **閱讀理解類**: READING_COMPREHENSION, VOCABULARY_BUILDING, SUMMARY_WRITING
- **測驗類**: MULTIPLE_CHOICE, TRUE_FALSE, FILL_BLANKS, MATCHING
- **語音類**: LISTENING, PRONUNCIATION, SPEAKING
- **討論類**: OPINION, DEBATE, DISCUSSION
- **創意類**: ROLE_PLAY, CREATIVE_WRITING, STORY_CONTINUATION
- **互動類**: DRILL, FLASHCARDS, GAME

### 4.2 任務生成器

基於 AI 生成任務，支持：
- 內容分析
- 難度調整
- 質量評估
- 多樣性控制

---

## 5. 動態來源配置系統

### 5.1 配置架構

```
配置存儲
  ├─ PostgreSQL (持久配置)
  ├─ Redis (緩存配置)
  └─ Git Repo (版本控制)
    ↓
配置管理
  ├─ CRUD 操作
  ├─ 版本控制
  ├─ 驗證器
  ├─ 熱更新
  ├─ 回滾機制
  └─ 審核流程
    ↓
配置分發
  ├─ WebSocket
  ├─ Polling
  └─ Webhook
    ↓
配置消費
  ├─ 爬蟲適配器
  ├─ 聚合服務
  └─ 推薦引擎
```

### 5.2 配置服務功能

- CRUD 操作
- 版本控制
- 熱更新 (WebSocket 推送)
- 回滾機制
- 配置驗證

---

## 6. 擴展的偏好系統

### 6.1 偏好系統架構

```
偏好收集
  ├─ 顯式收集 (問卷/設置)
  ├─ 隱式收集 (行為分析)
  └─ 上下文推斷 (時間/地點)
    ↓
偏好存儲
  ├─ 原始偏好 (User Table)
  ├─ 聚合偏好 (Profile)
  └─ 時序數據 (Trends)
    ↓
偏好分析
  ├─ 聚類分析 (K-Means)
  ├─ 協同過濾 (User-Item)
  └─ 內容過濾 (TF-IDF)
    ↓
偏好應用
  ├─ 內容篩選
  ├─ 任務生成
  └─ 排序調整
```

### 6.2 偏好模型

```typescript
export interface UserPreference {
  userId: string;
  topics: TopicPreference[];
  difficulty: DifficultyPreference;
  taskTypes: TaskTypePreference[];
  schedule: SchedulePreference;
  goals: LearningGoal[];
  language: LanguagePreference;
  implicit: ImplicitPreference;
  version: number;
  updatedAt: Date;
}
```

---

## 7. 遷移策略和實現時間表

### 7.1 遷移原則

1. **向後兼容** - v2.0 必須兼容 v1.0 的 API 和數據格式
2. **漸進式遷移** - 分階段進行，每個階段都可回滾
3. **雙寫策略** - 關鍵數據同時寫入 v1.0 和 v2.0
4. **影子運行** - v2.0 在背景運行，驗證後才切換
5. **數據一致性** - 遷移過程中保持數據一致性

### 7.2 遷移階段

**Phase 1: 準備階段 (第 1-2 週)**
- 需求確認和設計審查
- 開發環境搭建
- 數據庫 schema 設計
- API 接口定義

**Phase 2: 基礎設施建設 (第 3-4 週)**
- 數據庫遷移腳本
- 基礎服務實現
- CI/CD 流水線設置

**Phase 3: 核心功能開發 (第 5-8 週)**
- 多來源爬蟲實現
- 去重系統實現
- 內容聚合服務

**Phase 4: 高級功能開發 (第 9-12 週)**
- 智能去重 (語義)
- 任務生成器
- 偏好系統

**Phase 5: 影子運行 (第 13-14 週)**
- v2.0 影子部署
- 數據對比驗證
- 性能測試

**Phase 6: 灰度發布 (第 15-16 週)**
- 5% 用戶流量切換
- 逐步增加到 50%
- 全量切換準備

**Phase 7: 全量發布 (第 17 週)**
- 100% 流量切換
- v1.0 下線準備

**Phase 8: 收尾 (第 18 週)**
- v1.0 完全下線
- 文檔更新
- 知識轉移

---

## 8. 風險分析和緩解措施

### 8.1 風險識別矩陣

| 風險類別 | 風險描述 | 概率 | 影響 | 風險等級 |
|---------|---------|------|------|---------|
| 技術風險 | 語義去重準確度不足 | 中 | 高 | 🔴 高 |
| 技術風險 | 向量搜索性能問題 | 中 | 中 | 🟡 中 |
| 技術風險 | 多來源並發爬取衝突 | 低 | 高 | 🟡 中 |
| 業務風險 | 用戶偏好推斷偏差 | 中 | 中 | 🟡 中 |
| 業務風險 | 任務生成質量不穩定 | 中 | 高 | 🔴 高 |
| 數據風險 | 遷移過程數據丟失 | 低 | 極高 | 🔴 高 |
| 數據風險 | v1/v2 數據不一致 | 中 | 高 | 🔴 高 |
| 運維風險 | 配置熱更新失敗 | 低 | 中 | 🟢 低 |
| 運維風險 | 服務切換停機時間 | 中 | 中 | 🟡 中 |
| 成本風險 | OpenAI API 成本超支 | 高 | 中 | 🟡 中 |
| 合規風險 | 數據隱私合規問題 | 低 | 極高 | 🟡 中 |

### 8.2 詳細風險分析和緩解措施

**詳細的風險分析和緩解措施包含在設計文檔中**

---

## 9. 總結

Scout v2.0 是一次全面的系統升級，從單來源爬蟲轉變為智能化、多來源的新聞推薦平台。本設計文檔涵蓋了：

1. **多來源爬蟲架構** - 支持多種來源類型，並行爬取，統一數據格式
2. **智能去重系統** - 四層去重策略，從快速過濾到語義分析
3. **多樣化任務生成** - 支持多種任務類型，基於 AI 生成，質量控制機制
4. **動態配置系統** - 熱更新、版本控制、回滾機制
5. **擴展的偏好系統** - 顯式和隱式偏好收集，多維度分析
6. **遷移策略** - 漸進式遷移，雙寫驗證，平滑切換
7. **風險管理** - 詳細的風險識別和緩解措施

通過分階段實施（18週），確保每個階段都可驗證、可回滾，最大限度地降低遷移風險。

---

**文檔結束**
