# Scout Reports - Technical Design Document

**Version:** 1.0.0
**Status:** Design Phase
**Last Updated:** 2026-03-04
**Author:** Charlie (Orchestrator)

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Design Principles](#design-principles)
3. [System Architecture](#system-architecture)
4. [Technology Stack](#technology-stack)
5. [Backend Design](#backend-design)
6. [Frontend Design](#frontend-design)
7. [Database Design](#database-design)
8. [API Specification](#api-specification)
9. [Agent-Ready Design](#agent-ready-design)
10. [Development Workflow](#development-workflow)
11. [Deployment Strategy](#deployment-strategy)
12. [Security Considerations](#security-considerations)
13. [Performance Optimization](#performance-optimization)
14. [Monitoring & Logging](#monitoring--logging)
15. [Testing Strategy](#testing-strategy)
16. [Future Enhancements](#future-enhancements)

---

## 🎯 Project Overview

### Mission Statement

Build a web application to display, search, and manage Scout research reports with automated preference learning capabilities.

### Core Objectives

1. **Display**: Render Markdown research reports with rich formatting
2. **Search**: Full-text search across all reports
3. **Filter**: Filter by status, topic, date, tags
4. **Feedback**: Collect user feedback for preference learning
5. **Analytics**: Display statistics and trends
6. **Manage**: Bookmarks, tags, sharing

### Target Users

- Primary: Charlie (researcher)
- Secondary: Team members (future feature)

### Success Metrics

- < 500ms page load time
- < 100ms API response time
- > 90% user satisfaction with search results
- > 80% feedback collection rate

---

## 🧭 Design Principles

### 1. Agent-Ready First

The system must be designed for AI agents to:
- **Understand**: Clear code structure and documentation
- **Operate**: Standardized interfaces and API contracts
- **Extend**: Well-documented extension points
- **Debug**: Comprehensive logging and error handling

### 2. Separation of Concerns

- Frontend: UI/UX, routing, state management
- Backend: API, business logic, data access
- Scout Service: Preference learning, report parsing

### 3. API-First Design

All functionality exposed via RESTful API with:
- OpenAPI specification
- Request/response validation
- Error handling contracts
- Versioning strategy

### 4. Progressive Enhancement

- Core features first (list, view, feedback)
- Advanced features later (analytics, collaboration)
- Always maintain backward compatibility

### 5. Developer Experience

- Hot reload for rapid development
- Clear error messages
- Comprehensive logging
- Easy debugging

---

## 🏗️ System Architecture

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Scout Reports                           │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐         ┌─────────────┐                   │
│  │   Browser   │         │   Browser   │                   │
│  │  (Frontend) │         │  (Mobile)  │                   │
│  └──────┬──────┘         └──────┬──────┘                   │
│         │                      │                             │
│         │ HTTP/HTTPS          │                             │
│         ▼                      ▼                             │
│  ┌─────────────────────────────────────┐                   │
│  │         Nginx (Reverse Proxy)        │                   │
│  │             (Optional)               │                   │
│  └───────────────┬─────────────────────┘                   │
│                  │                                             │
│                  ▼                                             │
│  ┌──────────────────────────────────────────────────┐        │
│  │           Scout Reports Backend                   │        │
│  │           (FastAPI + Python)                       │        │
│  ├──────────────────────────────────────────────────┤        │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────┐  │        │
│  │  │   API Layer │  │   Services  │  │  Models  │  │        │
│  │  │  (Routers)  │  │  (Business) │  │(Schemas) │  │        │
│  │  └─────────────┘  └─────────────┘  └──────────┘  │        │
│  │  ┌──────────────────────────────────────────────┐  │        │
│  │  │         Scout Preference Learning          │  │        │
│  │  │    (EMA, Time Decay, Trend Analysis)         │  │        │
│  │  └──────────────────────────────────────────────┘  │        │
│  └──────────────────────────────────────────────────┘        │
│                  │                                             │
│         ┌────────┴────────┐                                  │
│         ▼                 ▼                                  │
│  ┌──────────┐      ┌──────────┐                             │
│  │  SQLite  │      │   File   │                             │
│  │  (Cache) │      │  System  │                             │
│  └──────────┘      └──────────┘                             │
│         │                 │                                  │
│         ▼                 ▼                                  │
│  ┌──────────────────────────────────────┐                   │
│  │  Scout Data (Read-only Mount)        │                   │
│  │  - /kanban/projects/*.md             │                   │
│  │  - /workspace-scout/PREFERENCES*.json│                   │
│  └──────────────────────────────────────┘                   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Technology |
|-----------|---------------|------------|
| **Frontend** | UI rendering, user interactions | React + Vite |
| **Backend API** | Request handling, response formatting | FastAPI |
| **Report Service** | Report parsing, metadata extraction | Python |
| **Preference Service** | Feedback processing, EMA updates | Python |
| **Search Service** | Full-text search, ranking | SQLite FTS |
| **Analytics Service** | Statistics, trend analysis | Python |
| **Database** | Persistent storage, caching | SQLite |

---

## 🔧 Technology Stack

### Backend

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Web Framework** | FastAPI | ^0.109.0 | API server |
| **Database** | SQLite | 3.x | Persistent storage |
| **ORM** | SQLAlchemy | ^2.0.0 | Database operations |
| **Validation** | Pydantic | ^2.5.0 | Data validation |
| **Markdown** | markdown2 | ^2.5.2 | Markdown parsing |
| **Search** | Whoosh | ^2.7.4 | Full-text search |
| **Testing** | pytest | ^7.4.0 | Unit tests |
| **Logging** | loguru | ^0.7.0 | Structured logging |
| **Async** | httpx | ^0.26.0 | Async HTTP client |

### Frontend

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | React | ^19.2.0 | UI framework |
| **Build Tool** | Vite | ^5.0.0 | Build system |
| **Router** | React Router | ^7.11.0 | Routing |
| **State** | Zustand | ^5.0.9 | State management |
| **HTTP** | Axios | ^1.13.2 | HTTP client |
| **Query** | TanStack Query | ^5.90.16 | Data fetching |
| **UI** | React Bootstrap | ^2.10.10 | UI components |
| **Markdown** | react-markdown | ^9.0.0 | Markdown rendering |
| **Syntax** | highlight.js | ^11.9.0 | Code highlighting |
| **Icons** | lucide-react | ^0.562.0 | Icons |
| **Testing** | Vitest | ^1.0.0 | Unit tests |
| **E2E** | Playwright | ^1.40.0 | E2E tests |

### DevOps

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Container** | Docker | Containerization |
| **Orchestration** | Docker Compose | Multi-container management |
| **Reverse Proxy** | Nginx | Production routing |
| **Process Manager** | Gunicorn | Production server |
| **SSL** | Certbot | HTTPS certificates |

---

## 🐍 Backend Design

### Directory Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry
│   ├── config.py               # Configuration management
│   ├── database.py             # Database connection
│   ├── dependencies.py          # Dependency injection
│   │
│   ├── api/                    # API layer (routers)
│   │   ├── __init__.py
│   │   ├── reports.py          # Report endpoints
│   │   ├── feedback.py         # Feedback endpoints
│   │   ├── search.py           # Search endpoints
│   │   ├── analytics.py        # Analytics endpoints
│   │   └── preferences.py      # Preferences endpoints
│   │
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── report_service.py   # Report parsing
│   │   ├── preference_service.py # Preference learning
│   │   ├── search_service.py   # Full-text search
│   │   └── analytics_service.py # Statistics
│   │
│   ├── models/                 # Database models
│   │   ├── __init__.py
│   │   ├── report.py
│   │   ├── feedback.py
│   │   └── bookmark.py
│   │
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── report.py
│   │   ├── feedback.py
│   │   └── common.py
│   │
│   ├── repositories/           # Data access layer
│   │   ├── __init__.py
│   │   ├── report_repository.py
│   │   └── feedback_repository.py
│   │
│   ├── utils/                  # Utilities
│   │   ├── __init__.py
│   │   ├── logger.py
│   │   ├── markdown_parser.py
│   │   └── file_watcher.py
│   │
│   └── tests/                  # Tests
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_api/
│       ├── test_services/
│       └── test_repositories/
│
├── scripts/                    # Utility scripts
│   ├── init_db.py
│   ├── import_reports.py
│   └── migrate_preferences.py
│
├── requirements.txt            # Python dependencies
├── requirements-dev.txt        # Development dependencies
├── pyproject.toml             # Project metadata
├── Dockerfile.dev            # Development Dockerfile
├── Dockerfile.prod           # Production Dockerfile
└── README.md
```

### Core Components

#### 1. Report Service

```python
# backend/app/services/report_service.py

from typing import List, Optional, Dict
from pathlib import Path
import re
from datetime import datetime

from app.models.report import Report
from app.schemas.report import ReportMetadata, ReportContent
from app.utils.logger import get_logger

logger = get_logger(__name__)

class ReportService:
    """Service for parsing and managing research reports"""
    
    def __init__(self, reports_dir: Path):
        """
        Initialize report service
        
        Args:
            reports_dir: Path to Scout reports directory
        """
        self.reports_dir = reports_dir
        self._metadata_cache: Dict[str, ReportMetadata] = {}
    
    def parse_metadata(self, report_path: Path) -> ReportMetadata:
        """
        Parse report metadata from markdown file
        
        Args:
            report_path: Path to report markdown file
            
        Returns:
            ReportMetadata object
        """
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract title (first H1)
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else report_path.stem
        
        # Extract task ID
        task_id_match = re.search(r'任務編號[：:]\s*(.+)', content)
        task_id = task_id_match.group(1).strip() if task_id_match else None
        
        # Extract status
        status_match = re.search(r'狀態[：:]\s*(.+)', content)
        status = status_match.group(1).strip() if status_match else "unknown"
        
        # Extract timestamp
        timestamp_match = re.search(r'時間戳記[：:]\s*(.+)', content)
        if timestamp_match:
            try:
                timestamp = timestamp_match.group(1).strip()
            except:
                timestamp = datetime.fromtimestamp(
                    report_path.stat().st_mtime
                ).isoformat()
        else:
            timestamp = datetime.fromtimestamp(
                report_path.stat().st_mtime
            ).isoformat()
        
        # Extract summary
        summary_match = re.search(
            r'##\s*研究摘要\s*\n(.*?)(?=##|\Z)', 
            content, 
            re.DOTALL
        )
        summary = summary_match.group(1).strip()[:500] if summary_match else ""
        
        # Extract topics
        topics = self._extract_topics(content)
        
        return ReportMetadata(
            title=title,
            task_id=task_id,
            status=status,
            timestamp=timestamp,
            summary=summary,
            topics=topics,
            path=str(report_path.relative_to(self.reports_dir)),
            file_size=report_path.stat().st_size
        )
    
    def _extract_topics(self, content: str) -> List[str]:
        """
        Extract topics from report content
        
        Args:
            content: Report markdown content
            
        Returns:
            List of topic strings
        """
        # TODO: Use NLP model for topic extraction
        # For now, use keyword matching
        keywords = [
            "machine learning", "neural networks", "deep learning",
            "reinforcement learning", "clustering", "classification",
            "regression", "time series", "optimization"
        ]
        
        found_topics = []
        content_lower = content.lower()
        
        for keyword in keywords:
            if keyword in content_lower:
                found_topics.append(keyword)
        
        return found_topics
    
    def get_report_content(self, report_path: Path) -> ReportContent:
        """
        Get full report content
        
        Args:
            report_path: Path to report markdown file
            
        Returns:
            ReportContent object
        """
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        metadata = self.parse_metadata(report_path)
        
        return ReportContent(
            metadata=metadata,
            content=content
        )
    
    def list_reports(
        self, 
        status: Optional[str] = None,
        topic: Optional[str] = None,
        limit: int = 50
    ) -> List[ReportMetadata]:
        """
        List all reports with optional filtering
        
        Args:
            status: Filter by status
            topic: Filter by topic
            limit: Maximum number of reports to return
            
        Returns:
            List of ReportMetadata objects
        """
        reports = []
        
        for project_dir in self.reports_dir.iterdir():
            if not project_dir.is_dir():
                continue
                
            for report_file in project_dir.glob("*-research.md"):
                try:
                    metadata = self.parse_metadata(report_file)
                    
                    # Filter by status
                    if status and metadata.status != status:
                        continue
                    
                    # Filter by topic
                    if topic and topic.lower() not in " ".join(metadata.topics).lower():
                        continue
                    
                    reports.append(metadata)
                except Exception as e:
                    logger.error(f"Failed to parse report {report_file}: {e}")
        
        # Sort by timestamp (newest first)
        reports.sort(key=lambda x: x.timestamp, reverse=True)
        
        return reports[:limit]
```

#### 2. Preference Service

```python
# backend/app/services/preference_service.py

from typing import Dict, Optional
from pathlib import Path
import json
from datetime import datetime

from app.utils.logger import get_logger

logger = get_logger(__name__)

class PreferenceService:
    """Service for managing Scout preferences and learning"""
    
    def __init__(self, config_path: Path):
        """
        Initialize preference service
        
        Args:
            config_path: Path to Scout PREFERENCES_v2.json file
        """
        self.config_path = config_path
        self._config_cache: Optional[Dict] = None
        self._load_config()
    
    def _load_config(self):
        """Load Scout configuration from file"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self._config_cache = json.load(f)
    
    def _save_config(self):
        """Save Scout configuration to file"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self._config_cache, f, indent=2, ensure_ascii=False)
    
    def update_from_feedback(
        self,
        task_id: str,
        rating: int,
        feedback_type: str,
        topics: list
    ) -> Dict:
        """
        Update preferences based on user feedback
        
        Args:
            task_id: Task ID of the report
            rating: User rating (1-5)
            feedback_type: 'positive' or 'negative'
            topics: List of topics from the report
            
        Returns:
            Updated preference data
        """
        # Reload config to get latest state
        self._load_config()
        
        preferences = self._config_cache.get("preferences", {})
        topics_data = preferences.get("topics", {})
        learning_config = preferences.get("learning_config", {})
        
        # EMA alpha
        ema_alpha = learning_config.get("ema_alpha", 0.2)
        
        # Convert rating to signal (-1 to 1)
        # 1 -> -1, 2 -> -0.5, 3 -> 0, 4 -> 0.5, 5 -> 1
        signal = (rating - 3) / 2
        
        # Update affinity for each topic
        updated_topics = {}
        
        for topic in topics:
            # Normalize topic name
            topic_key = topic.lower().replace(" ", "_").replace("-", "_")
            
            if topic_key not in topics_data:
                # Create new topic entry
                topics_data[topic_key] = {
                    "feedback_count": 0,
                    "average_rating": 0,
                    "affinity_score": 0.5,  # Start neutral
                    "last_seen": None
                }
            
            topic_pref = topics_data[topic_key]
            current_affinity = topic_pref.get("affinity_score", 0.5)
            feedback_count = topic_pref.get("feedback_count", 0)
            avg_rating = topic_pref.get("average_rating", 0)
            
            # EMA update
            new_affinity = ema_alpha * signal + (1 - ema_alpha) * current_affinity
            
            # Clamp to [0, 1]
            new_affinity = max(0.0, min(1.0, new_affinity))
            
            # Update feedback count and average rating
            new_feedback_count = feedback_count + 1
            new_avg_rating = (avg_rating * feedback_count + rating) / new_feedback_count
            
            # Update topic preference
            topics_data[topic_key] = {
                "feedback_count": new_feedback_count,
                "average_rating": new_avg_rating,
                "affinity_score": new_affinity,
                "last_seen": datetime.now().isoformat()
            }
            
            updated_topics[topic_key] = {
                "old_affinity": current_affinity,
                "new_affinity": new_affinity,
                "signal": signal
            }
        
        # Save updated config
        self._save_config()
        
        logger.info(
            f"Updated preferences for task {task_id}: "
            f"rating={rating}, type={feedback_type}, "
            f"topics_updated={len(updated_topics)}"
        )
        
        return {
            "success": True,
            "updated_topics": updated_topics,
            "total_feedback": sum(
                t.get("feedback_count", 0) 
                for t in topics_data.values()
            )
        }
    
    def get_preferences(self) -> Dict:
        """
        Get current Scout preferences
        
        Returns:
            Preferences dictionary
        """
        self._load_config()
        return self._config_cache
    
    def get_topic_affinity(self, topic: str) -> float:
        """
        Get affinity score for a specific topic
        
        Args:
            topic: Topic name
            
        Returns:
            Affinity score (0-1)
        """
        self._load_config()
        
        preferences = self._config_cache.get("preferences", {})
        topics_data = preferences.get("topics", {})
        
        topic_key = topic.lower().replace(" ", "_").replace("-", "_")
        
        if topic_key not in topics_data:
            return 0.5  # Default neutral
        
        return topics_data[topic_key].get("affinity_score", 0.5)
```

### API Layer Structure

```python
# backend/app/api/reports.py

from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Optional
from app.services.report_service import ReportService
from app.schemas.report import ReportMetadata, ReportContent, ReportListResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/reports", tags=["Reports"])

# Dependency injection
def get_report_service() -> ReportService:
    """Get report service instance"""
    from app.dependencies import get_report_service as _get_report_service
    return _get_report_service()

@router.get("", response_model=ReportListResponse)
async def list_reports(
    status: Optional[str] = Query(None, description="Filter by status"),
    topic: Optional[str] = Query(None, description="Filter by topic"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of reports"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    service: ReportService = Depends(get_report_service)
):
    """
    List all research reports with optional filtering
    
    - **status**: Filter by report status (completed, pending, failed)
    - **topic**: Filter by topic keyword
    - **limit**: Maximum number of reports to return (1-200)
    - **offset**: Pagination offset
    """
    try:
        reports = service.list_reports(
            status=status,
            topic=topic,
            limit=limit
        )
        
        total = len(reports)
        paginated_reports = reports[offset:offset + limit]
        
        return ReportListResponse(
            reports=paginated_reports,
            total=total,
            offset=offset,
            limit=limit
        )
    except Exception as e:
        logger.error(f"Failed to list reports: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{report_path:path}", response_model=ReportContent)
async def get_report(
    report_path: str = Path(..., description="Path to report file"),
    service: ReportService = Depends(get_report_service)
):
    """
    Get full report content
    
    - **report_path**: Relative path to report markdown file
    """
    try:
        full_path = service.reports_dir / report_path
        
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="Report not found")
        
        return service.get_report_content(full_path)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get report {report_path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{report_path:path}/metadata", response_model=ReportMetadata)
async def get_report_metadata(
    report_path: str = Path(..., description="Path to report file"),
    service: ReportService = Depends(get_report_service)
):
    """
    Get report metadata only
    
    - **report_path**: Relative path to report markdown file
    """
    try:
        full_path = service.reports_dir / report_path
        
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="Report not found")
        
        return service.parse_metadata(full_path)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get report metadata {report_path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 🎨 Frontend Design

### Directory Structure

```
frontend/
├── src/
│   ├── App.tsx                 # Root component
│   ├── main.tsx               # Entry point
│   ├── vite-env.d.ts          # Vite type declarations
│   │
│   ├── pages/                 # Page components
│   │   ├── ReportList.tsx
│   │   ├── ReportDetail.tsx
│   │   ├── Search.tsx
│   │   ├── Analytics.tsx
│   │   ├── Preferences.tsx
│   │   └── NotFound.tsx
│   │
│   ├── components/            # Reusable components
│   │   ├── ReportCard.tsx
│   │   ├── MarkdownViewer.tsx
│   │   ├── FeedbackCard.tsx
│   │   ├── SearchBar.tsx
│   │   ├── TagFilter.tsx
│   │   ├── Pagination.tsx
│   │   └── Layout/
│   │       ├── Header.tsx
│   │       ├── Footer.tsx
│   │       └── Sidebar.tsx
│   │
│   ├── stores/                # Zustand stores
│   │   ├── reportStore.ts
│   │   ├── uiStore.ts
│   │   └── searchStore.ts
│   │
│   ├── hooks/                 # Custom hooks
│   │   ├── useReports.ts
│   │   ├── useFeedback.ts
│   │   ├── useSearch.ts
│   │   └── useDebounce.ts
│   │
│   ├── services/              # API services
│   │   ├── api.ts            # Axios instance
│   │   ├── reportService.ts
│   │   ├── feedbackService.ts
│   │   └── analyticsService.ts
│   │
│   ├── types/                 # TypeScript types
│   │   ├── report.ts
│   │   ├── feedback.ts
│   │   └── common.ts
│   │
│   ├── utils/                 # Utilities
│   │   ├── formatDate.ts
│   │   ├── truncateText.ts
│   │   └── logger.ts
│   │
│   ├── styles/                # Global styles
│   │   ├── index.css
│   │   └── markdown.css      # Markdown styling
│   │
│   └── assets/               # Static assets
│       ├── images/
│       └── fonts/
│
├── public/                    # Public files
│   └── favicon.ico
│
├── tests/                     # Tests
│   ├── unit/
│   └── e2e/
│
├── package.json
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.js
├── .eslintrc.cjs
└── Dockerfile.dev
```

### Component Hierarchy

```
App
├── Layout
│   ├── Header
│   ├── Main Content
│   │   ├── ReportList
│   │   │   ├── SearchBar
│   │   │   ├── FilterBar
│   │   │   └── ReportGrid
│   │   │       └── ReportCard (xN)
│   │   │
│   │   ├── ReportDetail
│   │   │   ├── ReportHeader
│   │   │   ├── MarkdownViewer
│   │   │   └── FeedbackCard
│   │   │
│   │   ├── Search
│   │   │   ├── SearchBar
│   │   │   └── ResultsList
│   │   │
│   │   ├── Analytics
│   │   │   ├── StatsCards
│   │   │   ├── Charts
│   │   │   └── TrendLines
│   │   │
│   │   └── Preferences
│   │       ├── TopicAffinity
│   │       ├── LearningSettings
│   │       └── FeedbackHistory
│   │
│   └── Footer
└── ToastContainer
```

---

## 🗄️ Database Design

### SQLite Schema

```sql
-- Reports table (cache for performance)
CREATE TABLE reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    status TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    summary TEXT,
    topics TEXT,  -- JSON array
    path TEXT UNIQUE NOT NULL,
    file_size INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_reports_task_id ON reports(task_id);
CREATE INDEX idx_reports_status ON reports(status);
CREATE INDEX idx_reports_timestamp ON reports(timestamp);
CREATE INDEX idx_reports_topics ON reports(topics);

-- Feedback table
CREATE TABLE feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER NOT NULL,
    task_id TEXT NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    feedback_type TEXT CHECK (feedback_type IN ('positive', 'negative')),
    comment TEXT,
    topics TEXT,  -- JSON array of topics
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE
);

CREATE INDEX idx_feedback_report_id ON feedback(report_id);
CREATE INDEX idx_feedback_created_at ON feedback(created_at);

-- Bookmarks table
CREATE TABLE bookmarks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER NOT NULL,
    user_id TEXT DEFAULT 'default',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE
);

CREATE INDEX idx_bookmarks_report_id ON bookmarks(report_id);
CREATE INDEX idx_bookmarks_user_id ON bookmarks(user_id);

-- Tags table
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    color TEXT DEFAULT '#6366f1'
);

-- Report Tags junction table
CREATE TABLE report_tags (
    report_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (report_id, tag_id),
    FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- Full-text search virtual table
CREATE VIRTUAL TABLE fts_reports USING fts5(
    title,
    summary,
    content,
    tokenize='unicode61'
);

-- Triggers for auto-indexing
CREATE TRIGGER fts_reports_insert AFTER INSERT ON reports BEGIN
    INSERT INTO fts_reports(rowid, title, summary, content)
    VALUES (NEW.id, NEW.title, NEW.summary, NULL);
END;

CREATE TRIGGER fts_reports_delete AFTER DELETE ON reports BEGIN
    DELETE FROM fts_reports WHERE rowid = OLD.id;
END;

-- Preferences cache table (optional)
CREATE TABLE preferences_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT UNIQUE NOT NULL,
    affinity_score REAL NOT NULL,
    feedback_count INTEGER DEFAULT 0,
    average_rating REAL DEFAULT 0,
    last_seen TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 📡 API Specification

### Standard Response Format

All API responses follow this standard format:

```typescript
// Success Response
{
  "success": true,
  "data": T,
  "message": string | null
}

// Error Response
{
  "success": false,
  "error": {
    "code": string,
    "message": string,
    "details": any
  }
}
```

### Report Endpoints

#### GET /api/reports

List all reports with pagination and filtering.

**Request:**
```typescript
GET /api/reports?status=completed&topic=machine+learning&limit=50&offset=0
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

#### GET /api/reports/{report_path}

Get full report content.

**Request:**
```typescript
GET /api/reports/arxiv-1772244923/scout-1772244923253-research.md
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

### Feedback Endpoints

#### POST /api/feedback

Submit user feedback for a report.

**Request:**
```typescript
POST /api/feedback
Content-Type: application/json

{
  "task_id": "scout-1772244923253",
  "report_path": "arxiv-1772244923/scout-1772244923253-research.md",
  "rating": 5,
  "feedback_type": "positive",
  "comment": "Very helpful research!",
  "topics": ["machine learning", "uncertainty quantification"]
}
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

### Search Endpoints

#### GET /api/search

Full-text search across all reports.

**Request:**
```typescript
GET /api/search?q=hyperdimensional+computing&limit=10&offset=0
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

### Analytics Endpoints

#### GET /api/analytics/overview

Get overall statistics.

**Request:**
```typescript
GET /api/analytics/overview
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

### Preferences Endpoints

#### GET /api/preferences

Get current Scout preferences.

**Request:**
```typescript
GET /api/preferences
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

## 🤖 Agent-Ready Design

### 1. Clear Code Structure

#### Standard File Naming Convention

```
backend/
├── app/
│   ├── api/              # API endpoints (routers)
│   ├── services/         # Business logic
│   ├── models/           # Database models
│   ├── schemas/          # Pydantic schemas
│   ├── repositories/     # Data access
│   ├── utils/            # Utilities
│   └── tests/            # Tests
```

#### Standard Naming Patterns

| Type | Pattern | Example |
|------|---------|---------|
| **Router** | `<resource>.py` | `reports.py`, `feedback.py` |
| **Service** | `<resource>_service.py` | `report_service.py` |
| **Model** | `<resource>.py` | `report.py`, `feedback.py` |
| **Schema** | `<resource>.py` | `report.py`, `feedback.py` |
| **Repository** | `<resource>_repository.py` | `report_repository.py` |
| **Test** | `test_<module>.py` | `test_report_service.py` |

### 2. Comprehensive Documentation

#### Module Documentation Template

```python
"""
Report Service - Research report parsing and management

This module provides functionality for parsing Scout research reports,
extracting metadata, and managing report operations.

Classes:
    ReportService: Main service for report operations

Functions:
    parse_metadata: Extract metadata from markdown file
    extract_topics: Identify topics in report content

Dependencies:
    - pathlib: File path handling
    - re: Regular expressions
    - datetime: Timestamp parsing
    - loguru: Structured logging

Author: Scout Reports Team
Version: 1.0.0
"""
```

#### Function Documentation Template

```python
def parse_metadata(self, report_path: Path) -> ReportMetadata:
    """
    Parse report metadata from markdown file
    
    Extracts title, task ID, status, timestamp, summary, and topics
    from a Scout research report markdown file.
    
    Args:
        report_path: Path to report markdown file (must exist)
        
    Returns:
        ReportMetadata: Parsed metadata object with all fields populated
        
    Raises:
        FileNotFoundError: If report file doesn't exist
        ValueError: If file is not valid markdown
        UnicodeDecodeError: If file encoding is invalid
        
    Example:
        >>> service = ReportService(reports_dir)
        >>> metadata = service.parse_metadata(report_path)
        >>> print(metadata.title)
        "ConformalHDC Research Report"
        
    Note:
        - Title is extracted from first H1 heading
        - Timestamp falls back to file mtime if not found
        - Summary is truncated to 500 characters
    """
```

### 3. Type Hints Everywhere

```python
from typing import List, Optional, Dict, Tuple
from pathlib import Path
from datetime import datetime
from pydantic import BaseModel, Field

class ReportMetadata(BaseModel):
    """Report metadata model"""
    
    id: Optional[int] = None
    task_id: Optional[str] = None
    title: str = Field(..., description="Report title")
    status: str = Field(..., description="Report status")
    timestamp: str = Field(..., description="ISO format timestamp")
    summary: str = Field(default="", description="Report summary")
    topics: List[str] = Field(default_factory=list, description="Report topics")
    path: str = Field(..., description="Relative file path")
    file_size: int = Field(..., description="File size in bytes")
    
    class Config:
        """Pydantic config"""
        json_schema_extra = {
            "example": {
                "title": "ConformalHDC Research",
                "status": "completed",
                "timestamp": "2026-03-04T01:30:00Z",
                "summary": "This paper proposes...",
                "topics": ["machine learning"],
                "path": "arxiv-1772244923/report.md",
                "file_size": 23494
            }
        }

def parse_metadata(
    self, 
    report_path: Path
) -> ReportMetadata:
    """
    Parse report metadata
    
    Returns:
        ReportMetadata: Parsed metadata object
    """
    pass
```

### 4. Standard Error Handling

```python
from fastapi import HTTPException, status
from app.utils.logger import get_logger

logger = get_logger(__name__)

class ReportNotFoundError(Exception):
    """Report file not found"""
    pass

class InvalidReportFormatError(Exception):
    """Invalid report markdown format"""
    pass

def parse_metadata(self, report_path: Path) -> ReportMetadata:
    """
    Parse report metadata with comprehensive error handling
    """
    try:
        # Check if file exists
        if not report_path.exists():
            logger.error(f"Report not found: {report_path}")
            raise ReportNotFoundError(f"Report not found: {report_path}")
        
        # Read file
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Validate markdown
        if not content.strip():
            logger.error(f"Empty report file: {report_path}")
            raise InvalidReportFormatError(f"Empty report file: {report_path}")
        
        # Parse metadata
        metadata = self._do_parse(content, report_path)
        
        logger.info(f"Parsed report: {report_path}")
        return metadata
        
    except UnicodeDecodeError as e:
        logger.error(f"Encoding error in {report_path}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file encoding: {str(e)}"
        )
        
    except ReportNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
        
    except InvalidReportFormatError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
        
    except Exception as e:
        logger.error(f"Unexpected error parsing {report_path}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
```

### 5. Structured Logging

```python
from loguru import logger
import sys

# Configure logger
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add(
    "logs/backend.log",
    rotation="10 MB",
    retention="7 days",
    level="DEBUG"
)

# Usage
logger.info("Service started", extra={"service": "ReportService"})
logger.debug("Parsing report", extra={"path": str(report_path)})
logger.warning("Cache miss", extra={"key": "metadata:123"})
logger.error("Failed to parse", extra={"path": str(report_path), "error": str(e)})
```

### 6. Configuration Management

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Scout Reports API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    
    # Database
    DATABASE_URL: str = "sqlite:///./scout_reports.db"
    
    # Scout Data
    SCOUT_REPORTS_DIR: str = "/app/scout_projects"
    SCOUT_CONFIG_PATH: str = "/app/scout_config/PREFERENCES_v2.json"
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5174"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

settings = Settings()
```

### 7. Dependency Injection

```python
from fastapi import Depends
from functools import lru_cache

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

@lru_cache()
def get_report_service() -> ReportService:
    """Get cached report service instance"""
    settings = get_settings()
    return ReportService(
        reports_dir=Path(settings.SCOUT_REPORTS_DIR)
    )

@lru_cache()
def get_preference_service() -> PreferenceService:
    """Get cached preference service instance"""
    settings = get_settings()
    return PreferenceService(
        config_path=Path(settings.SCOUT_CONFIG_PATH)
    )
```

### 8. OpenAPI Specification

```python
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="Scout Reports API",
    description="API for managing Scout research reports",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

def custom_openapi():
    """Custom OpenAPI schema with additional metadata"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Scout Reports API",
        version="1.0.0",
        description="""
        Scout Reports API provides endpoints for:
        
        - Managing research reports
        - Collecting user feedback
        - Searching reports
        - Analytics and statistics
        - Preference learning
        
        All endpoints return JSON responses with standard format.
        """,
        routes=app.routes,
    )
    
    # Add tags metadata
    openapi_schema["tags"] = [
        {
            "name": "Reports",
            "description": "Operations for research reports",
        },
        {
            "name": "Feedback",
            "description": "Operations for user feedback",
        },
        {
            "name": "Search",
            "description": "Full-text search operations",
        },
        {
            "name": "Analytics",
            "description": "Statistics and analytics",
        },
        {
            "name": "Preferences",
            "description": "Scout preference management",
        },
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

### 9. Testing Strategy

#### Unit Test Template

```python
import pytest
from pathlib import Path
from app.services.report_service import ReportService
from app.schemas.report import ReportMetadata

class TestReportService:
    """Test ReportService functionality"""
    
    @pytest.fixture
    def sample_report_path(self, tmp_path):
        """Create sample report file for testing"""
        report_file = tmp_path / "test-report.md"
        content = """
# Test Report

**任務編號：** scout-test-001
**狀態：** completed
**時間戳記：** 2026-03-04T01:30:00Z

## Research Summary

This is a test report summary.
        """
        report_file.write_text(content)
        return report_file
    
    @pytest.fixture
    def report_service(self, tmp_path):
        """Create report service instance"""
        return ReportService(reports_dir=tmp_path)
    
    def test_parse_metadata_success(self, report_service, sample_report_path):
        """Test successful metadata parsing"""
        metadata = report_service.parse_metadata(sample_report_path)
        
        assert isinstance(metadata, ReportMetadata)
        assert metadata.title == "Test Report"
        assert metadata.task_id == "scout-test-001"
        assert metadata.status == "completed"
        assert "test report summary" in metadata.summary.lower()
    
    def test_parse_metadata_file_not_found(self, report_service, tmp_path):
        """Test parsing non-existent file"""
        non_existent = tmp_path / "non-existent.md"
        
        with pytest.raises(ReportNotFoundError):
            report_service.parse_metadata(non_existent)
    
    def test_list_reports_with_filtering(self, report_service, tmp_path):
        """Test listing reports with status filter"""
        # Create test reports
        for i, status in enumerate(["completed", "pending", "completed"]):
            report_file = tmp_path / f"report-{i}.md"
            report_file.write_text(f"# Report {i}\n\n**狀態：** {status}")
        
        completed_reports = report_service.list_reports(status="completed")
        
        assert len(completed_reports) == 2
        assert all(r.status == "completed" for r in completed_reports)
```

#### Integration Test Template

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestReportAPI:
    """Test Report API endpoints"""
    
    def test_list_reports(self, mock_report_service):
        """Test GET /api/reports"""
        response = client.get("/api/reports")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "reports" in data["data"]
        assert "total" in data["data"]
    
    def test_list_reports_with_filter(self, mock_report_service):
        """Test GET /api/reports?status=completed"""
        response = client.get("/api/reports?status=completed")
        
        assert response.status_code == 200
        data = response.json()
        assert all(
            r["status"] == "completed" 
            for r in data["data"]["reports"]
        )
    
    def test_get_report(self, mock_report_service):
        """Test GET /api/reports/{path}"""
        response = client.get("/api/reports/test/report.md")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "content" in data["data"]
        assert "metadata" in data["data"]
    
    def test_get_report_not_found(self, mock_report_service):
        """Test GET /api/reports/non-existent.md"""
        response = client.get("/api/reports/non-existent.md")
        
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert "error" in data
```

### 10. OpenAI / Agent Integration

#### Agent-Friendly API Wrapper

```python
"""
Agent API Module - Simplified interface for AI agents

This module provides a simplified, agent-friendly interface to the
Scout Reports API. All methods are designed for easy agent usage
with clear inputs/outputs and comprehensive error handling.

Example:
    >>> from app.api.agent_api import AgentAPI
    >>> api = AgentAPI()
    >>> reports = api.list_reports(status="completed")
    >>> report = api.get_report(reports[0]["path"])
    >>> feedback = api.submit_feedback(
    ...     task_id=report["task_id"],
    ...     rating=5,
    ...     feedback_type="positive"
    ... )
"""

from typing import List, Dict, Optional
from pathlib import Path
import requests

class AgentAPI:
    """Agent-friendly API wrapper for Scout Reports"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        """
        Initialize Agent API
        
        Args:
            base_url: Base URL of Scout Reports API
        """
        self.base_url = base_url
        self.session = requests.Session()
    
    def list_reports(
        self,
        status: Optional[str] = None,
        topic: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        List research reports
        
        Args:
            status: Filter by status (completed, pending, failed)
            topic: Filter by topic keyword
            limit: Maximum number of reports to return
            
        Returns:
            List of report dictionaries
            
        Example:
            >>> api = AgentAPI()
            >>> reports = api.list_reports(status="completed", limit=10)
            >>> print(f"Found {len(reports)} reports")
        """
        params = {"limit": limit}
        if status:
            params["status"] = status
        if topic:
            params["topic"] = topic
        
        response = self.session.get(
            f"{self.base_url}/api/reports",
            params=params
        )
        response.raise_for_status()
        
        data = response.json()
        return data["data"]["reports"]
    
    def get_report(self, path: str) -> Dict:
        """
        Get full report content
        
        Args:
            path: Relative path to report file
            
        Returns:
            Dictionary with metadata and content
            
        Example:
            >>> report = api.get_report("arxiv-1772244923/report.md")
            >>> print(report["metadata"]["title"])
            >>> print(report["content"])
        """
        response = self.session.get(
            f"{self.base_url}/api/reports/{path}"
        )
        response.raise_for_status()
        
        return response.json()["data"]
    
    def search_reports(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Search reports by keyword
        
        Args:
            query: Search query string
            limit: Maximum number of results
            
        Returns:
            List of search results with scores
            
        Example:
            >>> results = api.search_reports("hyperdimensional computing")
            >>> for result in results:
            ...     print(f"{result['score']:.2f}: {result['report']['title']}")
        """
        params = {"q": query, "limit": limit}
        response = self.session.get(
            f"{self.base_url}/api/search",
            params=params
        )
        response.raise_for_status()
        
        return response.json()["data"]["results"]
    
    def submit_feedback(
        self,
        task_id: str,
        rating: int,
        feedback_type: str,
        comment: Optional[str] = None,
        topics: Optional[List[str]] = None
    ) -> Dict:
        """
        Submit feedback for a report
        
        Args:
            task_id: Task ID of the report
            rating: Rating from 1 to 5
            feedback_type: 'positive' or 'negative'
            comment: Optional comment text
            topics: Optional list of topics
            
        Returns:
            Feedback submission result
            
        Example:
            >>> result = api.submit_feedback(
            ...     task_id="scout-123",
            ...     rating=5,
            ...     feedback_type="positive",
            ...     comment="Very helpful!"
            ... )
            >>> print(f"Updated topics: {len(result['updated_topics'])}")
        """
        payload = {
            "task_id": task_id,
            "rating": rating,
            "feedback_type": feedback_type
        }
        if comment:
            payload["comment"] = comment
        if topics:
            payload["topics"] = topics
        
        response = self.session.post(
            f"{self.base_url}/api/feedback",
            json=payload
        )
        response.raise_for_status()
        
        return response.json()["data"]
    
    def get_analytics(self) -> Dict:
        """
        Get overall analytics statistics
        
        Returns:
            Dictionary with statistics
            
        Example:
            >>> stats = api.get_analytics()
            >>> print(f"Total reports: {stats['total_reports']}")
            >>> print(f"Average rating: {stats['average_rating']}")
        """
        response = self.session.get(f"{self.base_url}/api/analytics/overview")
        response.raise_for_status()
        
        return response.json()["data"]
    
    def get_preferences(self) -> Dict:
        """
        Get current Scout preferences
        
        Returns:
            Preferences dictionary
            
        Example:
            >>> prefs = api.get_preferences()
            >>> for topic, data in prefs['topics'].items():
            ...     if data['affinity_score'] > 0.7:
            ...         print(f"{topic}: {data['affinity_score']:.2f}")
        """
        response = self.session.get(f"{self.base_url}/api/preferences")
        response.raise_for_status()
        
        return response.json()["data"]
```

---

## 🛠️ Development Workflow

### Local Development Setup

```bash
# 1. Clone repository
git clone <repo-url> ScoutReports
cd ScoutReports

# 2. Backend setup
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 3. Frontend setup
cd ../frontend
npm install

# 4. Environment setup
cd ..
cp .env.example .env
# Edit .env with your configuration

# 5. Start development services
docker-compose -f docker-compose.dev.yml up -d

# 6. Run migrations
cd backend
python scripts/init_db.py

# 7. Access application
# Frontend: http://localhost:5174
# Backend: http://localhost:8001
# API Docs: http://localhost:8001/docs
```

### Hot Reload Configuration

```yaml
# docker-compose.dev.yml
services:
  backend:
    command: uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
    volumes:
      - ./backend:/app
      - /app/__pycache__
      - /app/.venv
    environment:
      - WATCHFILES_FORCE_POLLING=true
  
  frontend:
    command: npm run dev -- --host 0.0.0.0
    volumes:
      - ./frontend/src:/app/src
      - /app/node_modules
      - /app/dist
```

### Code Quality Tools

```bash
# Backend linting
cd backend
black app/ tests/
flake8 app/ tests/
mypy app/

# Frontend linting
cd frontend
npm run lint
npm run type-check

# Run all tests
docker-compose -f docker-compose.dev.yml exec backend pytest
docker-compose -f docker-compose.dev.yml exec frontend npm run test
```

---

## 🚀 Deployment Strategy

### Production Docker Compose

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
      target: production
    container_name: scout_reports_backend
    ports:
      - "8081:8000"
    volumes:
      - ../../kanban/projects:/app/scout_projects:ro
      - ../workspace-scout:/app/scout_config:ro
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - ENV=production
      - DATABASE_URL=sqlite:///data/scout_reports.db
      - LOG_LEVEL=INFO
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
      target: production
    container_name: scout_reports_frontend
    ports:
      - "5175:80"
    environment:
      - VITE_API_URL=http://backend:8000
      - NODE_ENV=production
    depends_on:
      - backend
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: scout_reports_nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - frontend
      - backend
    restart: unless-stopped
```

### Deployment Checklist

- [ ] Environment variables configured
- [ ] SSL certificates obtained
- [ ] Database migrations run
- [ ] Nginx configuration updated
- [ ] Health checks passing
- [ ] Monitoring configured
- [ ] Backup strategy in place
- [ ] Rollback procedure tested

---

## 🔒 Security Considerations

### Authentication (Future)

```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException

security = HTTPBearer()

async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Verify JWT token
    
    Args:
        credentials: HTTP Bearer credentials
        
    Returns:
        User ID
        
    Raises:
        HTTPException: If token is invalid
    """
    token = credentials.credentials
    
    # TODO: Implement JWT verification
    # For now, skip auth (open access)
    return "default_user"
```

### Input Validation

```python
from pydantic import BaseModel, Field, validator

class FeedbackSubmission(BaseModel):
    """Feedback submission model"""
    
    task_id: str = Field(..., min_length=1, max_length=100)
    rating: int = Field(..., ge=1, le=5)
    feedback_type: str = Field(..., pattern="^(positive|negative)$")
    comment: Optional[str] = Field(None, max_length=1000)
    
    @validator('task_id')
    def validate_task_id(cls, v):
        """Validate task ID format"""
        if not v.startswith('scout-'):
            raise ValueError('Task ID must start with "scout-"')
        return v
```

### Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/api/feedback")
@limiter.limit("5/minute")
async def submit_feedback(
    request: Request,
    feedback: FeedbackSubmission
):
    """Submit feedback with rate limiting"""
    pass
```

---

## ⚡ Performance Optimization

### Caching Strategy

```python
from fastapi_cache import FastAPICache, Coder
from fastapi_cache.backends.redis import RedisBackend
from datetime import timedelta

# Cache report metadata for 5 minutes
@router.get("/api/reports")
@cache(expire=300)
async def list_reports():
    """List reports with caching"""
    pass

# Cache report content for 10 minutes
@router.get("/api/reports/{path}")
@cache(expire=600)
async def get_report(path: str):
    """Get report with caching"""
    pass
```

### Database Indexing

```sql
-- Already defined in schema section
CREATE INDEX idx_reports_status ON reports(status);
CREATE INDEX idx_reports_timestamp ON reports(timestamp);
CREATE INDEX idx_feedback_created_at ON feedback(created_at);
```

### Lazy Loading

```typescript
// Frontend lazy loading
import { lazy, Suspense } from 'react';

const ReportDetail = lazy(() => import('./pages/ReportDetail'));

function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <ReportDetail />
    </Suspense>
  );
}
```

---

## 📊 Monitoring & Logging

### Structured Logging

```python
from loguru import logger
import sys

logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add(
    "logs/backend_{time:YYYY-MM-DD}.log",
    rotation="10 MB",
    retention="30 days",
    compression="zip",
    level="DEBUG"
)
```

### Health Check Endpoints

```python
@router.get("/health")
async def health_check():
    """
    Health check endpoint
    
    Returns:
        Health status
    """
    checks = {
        "database": check_database_connection(),
        "scout_reports": check_scout_reports_access(),
        "scout_config": check_scout_config_access(),
    }
    
    all_healthy = all(checks.values())
    
    return {
        "status": "healthy" if all_healthy else "unhealthy",
        "checks": checks,
        "timestamp": datetime.now().isoformat()
    }
```

---

## 🧪 Testing Strategy

### Test Coverage Goals

- Unit tests: > 80% coverage
- Integration tests: Critical paths
- E2E tests: User flows

### Test Categories

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# E2E tests
npx playwright test

# Coverage report
pytest --cov=app tests/ --cov-report=html
```

---

## 🔮 Future Enhancements

### Phase 2 Features

- [ ] User authentication and authorization
- [ ] Report sharing with team members
- [ ] Collaboration features (comments, discussions)
- [ ] Report comparison tool
- [ ] Export to PDF/Word
- [ ] Mobile app (React Native)

### Phase 3 Features

- [ ] AI-powered report summarization
- [ ] Automatic topic extraction using NLP
- [ ] Similarity-based recommendations
- [ ] Knowledge graph visualization
- [ ] Custom report templates
- [ ] Multi-language support

---

## 📝 Appendix

### A. Environment Variables

```bash
# .env.example
APP_NAME=Scout Reports API
APP_VERSION=1.0.0
DEBUG=False
HOST=0.0.0.0
PORT=8001
DATABASE_URL=sqlite:///./scout_reports.db
SCOUT_REPORTS_DIR=/app/scout_projects
SCOUT_CONFIG_PATH=/app/scout_config/PREFERENCES_v2.json
CORS_ORIGINS=["http://localhost:5174"]
LOG_LEVEL=INFO
```

### B. API Response Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 429 | Too Many Requests |
| 500 | Internal Server Error |

### C. Data Types

```typescript
// Report Metadata
interface ReportMetadata {
  id?: number;
  task_id?: string;
  title: string;
  status: 'completed' | 'pending' | 'failed';
  timestamp: string;
  summary: string;
  topics: string[];
  path: string;
  file_size: number;
}

// Feedback Submission
interface FeedbackSubmission {
  task_id: string;
  report_path: string;
  rating: number;  // 1-5
  feedback_type: 'positive' | 'negative';
  comment?: string;
  topics?: string[];
}

// Search Result
interface SearchResult {
  report: ReportMetadata;
  score: number;
  highlights: string[];
}
```

---

**Document Status:** ✅ Design Complete
**Next Steps:** Implementation Phase
**Estimated Timeline:** 9-13 days

---

## 🎯 Quick Start for Agents

For AI agents wanting to use this system:

```python
# Quick agent example
from app.api.agent_api import AgentAPI

api = AgentAPI()

# List reports
reports = api.list_reports(status="completed", limit=10)

# Get specific report
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

**End of Document**
