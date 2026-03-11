# Scout Reports API Reference

**Version:** 1.0.0
**Base URL:** `http://localhost:8001`

---

## 📡 Standard Response Format

All API responses follow this format:

```json
{
  "success": true,
  "data": { /* Response data */ },
  "message": null
}
```

Error responses:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description",
    "details": {}
  }
}
```

---

## 📊 Reports API

### List Reports

**GET** `/api/reports`

List all research reports with pagination and filtering.

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `status` | string | No | null | Filter by status (`completed`, `pending`, `failed`) |
| `topic` | string | No | null | Filter by topic keyword |
| `limit` | integer | No | 50 | Maximum number of reports (1-200) |
| `offset` | integer | No | 0 | Pagination offset |

**Example:**

```bash
curl "http://localhost:8001/api/reports?status=completed&limit=10"
```

**Response:**

```json
{
  "success": true,
  "data": {
    "reports": [
      {
        "id": 1,
        "task_id": "scout-1772244923253",
        "title": "ConformalHDC: Uncertainty-Aware Hyperdimensional Computing",
        "status": "completed",
        "timestamp": "2026-03-04T01:30:00Z",
        "summary": "This paper proposes ConformalHDC...",
        "topics": ["machine learning", "uncertainty quantification"],
        "path": "arxiv-1772244923/scout-1772244923253-research.md",
        "file_size": 23494
      }
    ],
    "total": 42,
    "offset": 0,
    "limit": 50
  }
}
```

---

### Get Report

**GET** `/api/reports/{report_path}`

Get full report content including metadata and markdown.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `report_path` | string | Yes | Relative path to report file |

**Example:**

```bash
curl "http://localhost:8001/api/reports/arxiv-1772244923/scout-1772244923253-research.md"
```

**Response:**

```json
{
  "success": true,
  "data": {
    "metadata": {
      "id": 1,
      "task_id": "scout-1772244923253",
      "title": "ConformalHDC: Uncertainty-Aware Hyperdimensional Computing",
      "status": "completed",
      "timestamp": "2026-03-04T01:30:00Z",
      "summary": "This paper proposes ConformalHDC...",
      "topics": ["machine learning", "uncertainty quantification"],
      "path": "arxiv-1772244923/scout-1772244923253-research.md",
      "file_size": 23494
    },
    "content": "# ConformalHDC Research Report\n\n## Research Summary\n\n..."
  }
}
```

---

### Get Report Metadata

**GET** `/api/reports/{report_path}/metadata`

Get only report metadata (without content).

**Example:**

```bash
curl "http://localhost:8001/api/reports/arxiv-1772244923/scout-1772244923253-research.md/metadata"
```

---

## ⭐ Feedback API

### Submit Feedback

**POST** `/api/feedback`

Submit user feedback for a report (triggers preference learning).

**Request Body:**

```json
{
  "task_id": "scout-1772244923253",
  "report_path": "arxiv-1772244923/scout-1772244923253-research.md",
  "rating": 5,
  "feedback_type": "positive",
  "comment": "Very helpful research!",
  "topics": ["machine learning", "uncertainty quantification"]
}
```

**Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `task_id` | string | Yes | Scout task ID |
| `report_path` | string | Yes | Relative path to report |
| `rating` | integer | Yes | Rating from 1 to 5 |
| `feedback_type` | string | Yes | `positive` or `negative` |
| `comment` | string | No | Optional comment text |
| `topics` | array | No | List of topics from report |

**Example:**

```bash
curl -X POST "http://localhost:8001/api/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "scout-1772244923253",
    "report_path": "arxiv-1772244923/scout-1772244923253-research.md",
    "rating": 5,
    "feedback_type": "positive",
    "comment": "Very helpful!"
  }'
```

**Response:**

```json
{
  "success": true,
  "data": {
    "feedback_id": 1,
    "updated_topics": {
      "machine_learning": {
        "old_affinity": 0.7,
        "new_affinity": 0.76,
        "signal": 0.3
      },
      "uncertainty_quantification": {
        "old_affinity": 0.5,
        "new_affinity": 0.6,
        "signal": 0.5
      }
    },
    "total_feedback": 42
  }
}
```

---

### Get Report Feedback

**GET** `/api/feedback/{report_id}`

Get all feedback for a specific report.

**Example:**

```bash
curl "http://localhost:8001/api/feedback/1"
```

---

## 🔍 Search API

### Search Reports

**GET** `/api/search`

Full-text search across all reports.

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `q` | string | Yes | - | Search query |
| `limit` | integer | No | 10 | Maximum number of results |
| `offset` | integer | No | 0 | Pagination offset |

**Example:**

```bash
curl "http://localhost:8001/api/search?q=hyperdimensional+computing&limit=10"
```

**Response:**

```json
{
  "success": true,
  "data": {
    "results": [
      {
        "report": { /* ReportMetadata */ },
        "score": 0.95,
        "highlights": [
          "This paper proposes <mark>ConformalHDC</mark>, which combines conformal prediction with <mark>hyperdimensional computing</mark>"
        ]
      }
    ],
    "total": 5,
    "query": "hyperdimensional computing",
    "offset": 0,
    "limit": 10
  }
}
```

---

## 📈 Analytics API

### Get Overview

**GET** `/api/analytics/overview`

Get overall statistics and summary data.

**Example:**

```bash
curl "http://localhost:8001/api/analytics/overview"
```

**Response:**

```json
{
  "success": true,
  "data": {
    "total_reports": 156,
    "completed_reports": 142,
    "pending_reports": 12,
    "failed_reports": 2,
    "total_feedback": 89,
    "average_rating": 4.2,
    "top_topics": [
      {"topic": "machine learning", "count": 45},
      {"topic": "neural networks", "count": 32}
    ],
    "recent_activity": [
      {"timestamp": "2026-03-04T02:00:00Z", "action": "report_created"},
      {"timestamp": "2026-03-04T01:55:00Z", "action": "feedback_submitted"}
    ]
  }
}
```

---

### Get Trends

**GET** `/api/analytics/trends`

Get trend analysis data over time.

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `period` | string | No | 7d | Time period (`1d`, `7d`, `30d`, `90d`) |

**Example:**

```bash
curl "http://localhost:8001/api/analytics/trends?period=7d"
```

---

## 🎓 Preferences API

### Get Preferences

**GET** `/api/preferences`

Get current Scout preference configuration.

**Example:**

```bash
curl "http://localhost:8001/api/preferences"
```

**Response:**

```json
{
  "success": true,
  "data": {
    "version": "2.0",
    "last_updated": "2026-03-04T02:30:00Z",
    "topics": {
      "machine_learning": {
        "affinity_score": 0.76,
        "feedback_count": 15,
        "average_rating": 4.5,
        "last_seen": "2026-03-04T02:25:00Z"
      }
    },
    "learning_config": {
      "ema_alpha": 0.2,
      "min_feedback_count": 3,
      "affinity_decay_rate": 0.05
    }
  }
}
```

---

### Get Topic Affinity

**GET** `/api/preferences/topics`

Get affinity scores for all topics.

**Example:**

```bash
curl "http://localhost:8001/api/preferences/topics"
```

**Response:**

```json
{
  "success": true,
  "data": {
    "topics": [
      {
        "topic": "machine_learning",
        "affinity_score": 0.76,
        "feedback_count": 15,
        "average_rating": 4.5
      }
    ]
  }
}
```

---

## 🏥 Health Check

**GET** `/health`

Check system health status.

**Example:**

```bash
curl "http://localhost:8001/health"
```

**Response:**

```json
{
  "status": "healthy",
  "checks": {
    "database": true,
    "scout_reports": true,
    "scout_config": true
  },
  "timestamp": "2026-03-04T03:00:00Z"
}
```

---

## 🤖 Agent-Friendly API Wrapper

For AI agents, use the simplified wrapper:

```python
from app.api.agent_api import AgentAPI

api = AgentAPI(base_url="http://localhost:8001")

# List reports
reports = api.list_reports(status="completed", limit=10)

# Get report
report = api.get_report(reports[0]["path"])

# Search
results = api.search_reports("machine learning")

# Submit feedback
api.submit_feedback(
    task_id=report["task_id"],
    rating=5,
    feedback_type="positive"
)

# Get analytics
stats = api.get_analytics()

# Get preferences
prefs = api.get_preferences()
```

---

## 📚 Data Models

### ReportMetadata

```typescript
interface ReportMetadata {
  id?: number;
  task_id?: string;
  title: string;
  status: 'completed' | 'pending' | 'failed';
  timestamp: string;  // ISO 8601
  summary: string;
  topics: string[];
  path: string;      // Relative file path
  file_size: number;  // Bytes
}
```

### FeedbackSubmission

```typescript
interface FeedbackSubmission {
  task_id: string;
  report_path: string;
  rating: number;  // 1-5
  feedback_type: 'positive' | 'negative';
  comment?: string;
  topics?: string[];
}
```

### SearchResult

```typescript
interface SearchResult {
  report: ReportMetadata;
  score: number;        // Relevance score (0-1)
  highlights: string[]; // Highlighted text snippets
}
```

---

## ❌ Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `REPORT_NOT_FOUND` | 404 | Report file does not exist |
| `INVALID_REPORT_FORMAT` | 400 | Report is not valid markdown |
| `INVALID_FEEDBACK` | 400 | Feedback submission is invalid |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Internal server error |

---

## 📝 Response Codes

| HTTP Code | Description |
|-----------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 429 | Too Many Requests |
| 500 | Internal Server Error |

---

## 🔐 Authentication

Currently, the API is open (no authentication required). Authentication is planned for Phase 2.

---

## 📊 Rate Limiting

| Endpoint | Limit | Window |
|----------|-------|--------|
| POST /api/feedback | 5/minute | 1 minute |
| All other endpoints | 100/minute | 1 minute |

---

## 📄 Interactive Documentation

- **Swagger UI:** http://localhost:8001/docs
- **ReDoc:** http://localhost:8001/redoc

---

**End of API Reference**
