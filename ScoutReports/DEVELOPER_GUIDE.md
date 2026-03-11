# Scout Reports - Developer Guide

**Version:** 1.0.0
**Last Updated:** 2026-03-04

---

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [Development Environment](#development-environment)
3. [Backend Development](#backend-development)
4. [Frontend Development](#frontend-development)
5. [Testing](#testing)
6. [Code Style](#code-style)
7. [Common Tasks](#common-tasks)
8. [Troubleshooting](#troubleshooting)
9. [AI Agent Usage](#ai-agent-usage)

---

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.9+
- Node.js 18+
- Git

### Initial Setup

```bash
# Clone repository
git clone <repo-url> ScoutReports
cd ScoutReports

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
vim .env

# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# Initialize database
docker-compose -f docker-compose.dev.yml exec backend python scripts/init_db.py

# Verify setup
curl http://localhost:8001/health
curl http://localhost:5174
```

---

## 🏗️ Development Environment

### Project Structure

```
ScoutReports/
├── backend/               # Python FastAPI
├── frontend/              # React + Vite
├── data/                  # SQLite database
├── logs/                  # Application logs
├── DESIGN.md              # Full technical design
├── README.md              # Project overview
├── API.md                 # API reference
├── DEVELOPER_GUIDE.md     # This file
├── docker-compose.dev.yml # Development Docker
└── docker-compose.prod.yml # Production Docker
```

### Environment Variables

```bash
# .env
APP_NAME=Scout Reports API
APP_VERSION=1.0.0
DEBUG=True
HOST=0.0.0.0
PORT=8001
DATABASE_URL=sqlite:///./scout_reports.db
SCOUT_REPORTS_DIR=/app/scout_projects
SCOUT_CONFIG_PATH=/app/scout_config/PREFERENCES_v2.json
CORS_ORIGINS=["http://localhost:5174"]
LOG_LEVEL=INFO
```

---

## 🐍 Backend Development

### Setting Up Local Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Run tests
pytest

# Run with coverage
pytest --cov=app tests/ --cov-report=html
```

### Code Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app
│   ├── config.py               # Settings
│   ├── database.py             # DB connection
│   │
│   ├── api/                    # API endpoints
│   │   ├── reports.py
│   │   ├── feedback.py
│   │   ├── search.py
│   │   ├── analytics.py
│   │   └── preferences.py
│   │
│   ├── services/               # Business logic
│   │   ├── report_service.py
│   │   ├── preference_service.py
│   │   ├── search_service.py
│   │   └── analytics_service.py
│   │
│   ├── models/                 # DB models
│   │   ├── report.py
│   │   ├── feedback.py
│   │   └── bookmark.py
│   │
│   ├── schemas/                # Pydantic schemas
│   │   ├── report.py
│   │   ├── feedback.py
│   │   └── common.py
│   │
│   ├── repositories/           # Data access
│   │   ├── report_repository.py
│   │   └── feedback_repository.py
│   │
│   ├── utils/                  # Utilities
│   │   ├── logger.py
│   │   ├── markdown_parser.py
│   │   └── file_watcher.py
│   │
│   └── tests/                  # Tests
│       ├── conftest.py
│       ├── test_api/
│       ├── test_services/
│       └── test_repositories/
```

### Creating a New API Endpoint

1. **Create Pydantic Schema** (`app/schemas/`):

```python
from pydantic import BaseModel, Field

class ExampleRequest(BaseModel):
    """Example request schema"""
    
    name: str = Field(..., min_length=1, max_length=100)
    value: int = Field(..., ge=0, le=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "test",
                "value": 42
            }
        }
```

2. **Create Service** (`app/services/`):

```python
from loguru import logger
from typing import List

class ExampleService:
    """Example service"""
    
    def process_data(self, name: str, value: int) -> dict:
        """
        Process example data
        
        Args:
            name: Name field
            value: Value field
            
        Returns:
            Processed data
        """
        result = {
            "processed_name": name.upper(),
            "doubled_value": value * 2
        }
        
        logger.info(f"Processed data: {result}")
        return result
```

3. **Create API Endpoint** (`app/api/`):

```python
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.example import ExampleRequest, ExampleResponse
from app.services.example_service import ExampleService

router = APIRouter(prefix="/api/examples", tags=["Examples"])

@router.post("", response_model=ExampleResponse)
async def create_example(
    request: ExampleRequest,
    service: ExampleService = Depends(get_example_service)
):
    """
    Create example resource
    
    - **name**: Example name (1-100 chars)
    - **value**: Example value (0-100)
    """
    try:
        result = service.process_data(request.name, request.value)
        
        return ExampleResponse(
            success=True,
            data=result,
            message="Data processed successfully"
        )
    except Exception as e:
        logger.error(f"Failed to process example: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

4. **Register Router** (`app/main.py`):

```python
from fastapi import FastAPI
from app.api import examples

app = FastAPI()
app.include_router(examples.router)
```

### Testing

```python
# tests/test_api/test_examples.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestExampleAPI:
    """Test example API endpoints"""
    
    def test_create_example(self):
        """Test POST /api/examples"""
        response = client.post(
            "/api/examples",
            json={"name": "test", "value": 42}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["processed_name"] == "TEST"
        assert data["data"]["doubled_value"] == 84
    
    def test_invalid_input(self):
        """Test POST /api/examples with invalid input"""
        response = client.post(
            "/api/examples",
            json={"name": "", "value": 42}
        )
        
        assert response.status_code == 422  # Validation error
```

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_api/test_examples.py

# With coverage
pytest --cov=app tests/ --cov-report=html

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

---

## 🎨 Frontend Development

### Setting Up Local Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Access at http://localhost:5174

# Run tests
npm run test

# Run E2E tests
npx playwright test
```

### Code Structure

```
frontend/
├── src/
│   ├── App.tsx                 # Root component
│   ├── main.tsx               # Entry point
│   │
│   ├── pages/                 # Page components
│   │   ├── ReportList.tsx
│   │   ├── ReportDetail.tsx
│   │   ├── Search.tsx
│   │   ├── Analytics.tsx
│   │   └── Preferences.tsx
│   │
│   ├── components/            # Reusable components
│   │   ├── ReportCard.tsx
│   │   ├── MarkdownViewer.tsx
│   │   ├── FeedbackCard.tsx
│   │   ├── SearchBar.tsx
│   │   └── Pagination.tsx
│   │
│   ├── stores/                # Zustand stores
│   │   ├── reportStore.ts
│   │   ├── uiStore.ts
│   │   └── searchStore.ts
│   │
│   ├── hooks/                 # Custom hooks
│   │   ├── useReports.ts
│   │   ├── useFeedback.ts
│   │   └── useSearch.ts
│   │
│   ├── services/              # API services
│   │   ├── api.ts            # Axios instance
│   │   ├── reportService.ts
│   │   └── feedbackService.ts
│   │
│   ├── types/                 # TypeScript types
│   │   ├── report.ts
│   │   ├── feedback.ts
│   │   └── common.ts
│   │
│   ├── utils/                 # Utilities
│   │   ├── formatDate.ts
│   │   └── logger.ts
│   │
│   └── styles/                # Global styles
│       └── index.css
│
├── public/                    # Static assets
└── tests/                     # Tests
```

### Creating a New Page

1. **Create TypeScript Types** (`src/types/`):

```typescript
// src/types/example.ts
export interface Example {
  id: number;
  name: string;
  value: number;
}

export interface ExampleRequest {
  name: string;
  value: number;
}
```

2. **Create API Service** (`src/services/`):

```typescript
// src/services/exampleService.ts
import api from './api';
import type { Example, ExampleRequest } from '../types/example';

export const exampleService = {
  async createExample(data: ExampleRequest): Promise<Example> {
    const response = await api.post('/api/examples', data);
    return response.data.data;
  },
  
  async getExamples(): Promise<Example[]> {
    const response = await api.get('/api/examples');
    return response.data.data;
  }
};
```

3. **Create Zustand Store** (`src/stores/`):

```typescript
// src/stores/exampleStore.ts
import { create } from 'zustand';
import type { Example } from '../types/example';
import { exampleService } from '../services/exampleService';

interface ExampleStore {
  examples: Example[];
  loading: boolean;
  error: string | null;
  
  fetchExamples: () => Promise<void>;
  createExample: (data: ExampleRequest) => Promise<void>;
}

export const useExampleStore = create<ExampleStore>((set) => ({
  examples: [],
  loading: false,
  error: null,
  
  fetchExamples: async () => {
    set({ loading: true, error: null });
    try {
      const examples = await exampleService.getExamples();
      set({ examples, loading: false });
    } catch (error) {
      set({ error: 'Failed to fetch examples', loading: false });
    }
  },
  
  createExample: async (data) => {
    set({ loading: true, error: null });
    try {
      const newExample = await exampleService.createExample(data);
      set((state) => ({
        examples: [...state.examples, newExample],
        loading: false
      }));
    } catch (error) {
      set({ error: 'Failed to create example', loading: false });
    }
  }
}));
```

4. **Create Page Component** (`src/pages/`):

```typescript
// src/pages/ExamplePage.tsx
import { useEffect } from 'react';
import { useExampleStore } from '../stores/exampleStore';
import { Button, Form, Alert } from 'react-bootstrap';

export default function ExamplePage() {
  const { examples, loading, error, fetchExamples } = useExampleStore();
  const { createExample } = useExampleStore();
  
  useEffect(() => {
    fetchExamples();
  }, [fetchExamples]);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const form = e.target as HTMLFormElement;
    const formData = new FormData(form);
    
    await createExample({
      name: formData.get('name') as string,
      value: parseInt(formData.get('value') as string)
    });
    
    form.reset();
  };
  
  if (loading) return <div>Loading...</div>;
  if (error) return <Alert variant="danger">{error}</Alert>;
  
  return (
    <div className="container">
      <h1>Example Page</h1>
      
      <Form onSubmit={handleSubmit}>
        <Form.Group>
          <Form.Label>Name</Form.Label>
          <Form.Control name="name" type="text" required />
        </Form.Group>
        
        <Form.Group>
          <Form.Label>Value</Form.Label>
          <Form.Control name="value" type="number" required />
        </Form.Group>
        
        <Button type="submit">Create</Button>
      </Form>
      
      <h2>Examples</h2>
      <ul>
        {examples.map((example) => (
          <li key={example.id}>{example.name}: {example.value}</li>
        ))}
      </ul>
    </div>
  );
}
```

5. **Add Route** (`src/App.tsx`):

```typescript
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ExamplePage from './pages/ExamplePage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/examples" element={<ExamplePage />} />
      </Routes>
    </BrowserRouter>
  );
}
```

### Testing

```typescript
// src/pages/__tests__/ExamplePage.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ExamplePage from '../ExamplePage';

// Mock the store
vi.mock('../stores/exampleStore');

describe('ExamplePage', () => {
  it('renders examples list', () => {
    render(<ExamplePage />);
    expect(screen.getByText('Example Page')).toBeInTheDocument();
  });
  
  it('creates new example', async () => {
    const user = userEvent.setup();
    render(<ExamplePage />);
    
    await user.type(screen.getByLabelText('Name'), 'Test');
    await user.type(screen.getByLabelText('Value'), '42');
    await user.click(screen.getByRole('button', { name: 'Create' }));
    
    // Assert example was created
  });
});
```

---

## 🧪 Testing

### Backend Testing

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# All tests
pytest -v

# Coverage
pytest --cov=app tests/ --cov-report=html
open htmlcov/index.html
```

### Frontend Testing

```bash
# Unit tests
npm run test

# Watch mode
npm run test:watch

# Coverage
npm run test:coverage

# E2E tests
npx playwright test

# E2E UI mode
npx playwright test --ui
```

### Test Coverage Goals

- Unit tests: > 80%
- Integration tests: Critical paths
- E2E tests: User flows

---

## 🎨 Code Style

### Backend (Python)

```bash
# Format code
black app/ tests/

# Check style
flake8 app/ tests/

# Type checking
mypy app/

# All checks
black --check app/ tests/ && flake8 app/ tests/ && mypy app/
```

**Style Guide:**
- PEP 8
- 100 character line limit
- Type hints on all public functions
- Docstrings on all modules, classes, and functions

### Frontend (TypeScript)

```bash
# Format code
npm run format

# Lint code
npm run lint

# Type check
npm run type-check

# All checks
npm run format && npm run lint && npm run type-check
```

**Style Guide:**
- ESLint + Prettier
- 2-space indentation
- Semiautomatic semicolons
- Single quotes for strings

---

## 🛠️ Common Tasks

### Adding a New Database Model

1. **Create Model** (`app/models/`):

```python
from sqlalchemy import Column, Integer, String
from app.database import Base

class NewModel(Base):
    """New model"""
    __tablename__ = "new_table"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
```

2. **Create Schema** (`app/schemas/`):

```python
from pydantic import BaseModel

class NewModelSchema(BaseModel):
    """New model schema"""
    id: int
    name: str
    
    class Config:
        from_attributes = True
```

3. **Create Repository** (`app/repositories/`):

```python
from sqlalchemy.orm import Session
from app.models.new_model import NewModel

class NewModelRepository:
    """New model repository"""
    
    def get_all(self, db: Session) -> list[NewModel]:
        return db.query(NewModel).all()
    
    def get_by_id(self, db: Session, id: int) -> NewModel | None:
        return db.query(NewModel).filter(NewModel.id == id).first()
```

4. **Create Migration** (SQLAlchemy Alembic):

```bash
# Generate migration
alembic revision --autogenerate -m "Add new_model table"

# Apply migration
alembic upgrade head
```

### Debugging

**Backend:**

```python
from loguru import logger
import sys

logger.remove()
logger.add(sys.stderr, level="DEBUG")

# In code
logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message", exc_info=True)
```

**Frontend:**

```typescript
// src/utils/logger.ts
export const logger = {
  debug: (message: string, data?: any) => {
    console.debug(`[DEBUG] ${message}`, data);
  },
  info: (message: string, data?: any) => {
    console.info(`[INFO] ${message}`, data);
  },
  error: (message: string, error?: any) => {
    console.error(`[ERROR] ${message}`, error);
  }
};
```

### Hot Reload

Backend hot reload is automatic with `uvicorn --reload`.

Frontend hot reload is automatic with Vite.

---

## 🔧 Troubleshooting

### Backend Issues

**Issue: Module not found**

```bash
# Reinstall dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

**Issue: Database locked**

```bash
# Check for other processes
lsof | grep scout_reports.db

# Restart database
docker-compose restart backend
```

**Issue: Import errors**

```bash
# Ensure PYTHONPATH is set
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or use relative imports
```

### Frontend Issues

**Issue: npm install fails**

```bash
# Clear cache
npm cache clean --force

# Delete node_modules
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

**Issue: Vite dev server issues**

```bash
# Clear cache
npm run clean

# Or manually
rm -rf node_modules/.vite
```

**Issue: TypeScript errors**

```bash
# Reinstall dependencies
npm install

# Clear tsconfig cache
rm -rf tsconfig.tsbuildinfo
```

### Docker Issues

**Issue: Container won't start**

```bash
# Check logs
docker-compose logs backend

# Rebuild
docker-compose up -d --build

# Check for port conflicts
lsof -i :8001
lsof -i :5174
```

**Issue: Volume mount issues**

```bash
# Check volume mounts
docker-compose config

# Rebuild with fresh volumes
docker-compose down -v
docker-compose up -d
```

---

## 🤖 AI Agent Usage

### Quick Start for Agents

```python
from app.api.agent_api import AgentAPI

# Initialize
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

### Reading Documentation

```python
# Backend
from app.services.report_service import ReportService
help(ReportService.parse_metadata)

# Frontend
# See docstrings in TypeScript files
```

### Understanding Code Structure

**Backend:**
- `app/api/` - API endpoints (start here)
- `app/services/` - Business logic
- `app/models/` - Database models
- `app/schemas/` - Pydantic schemas

**Frontend:**
- `src/pages/` - Page components (start here)
- `src/components/` - Reusable components
- `src/stores/` - State management
- `src/services/` - API services

---

## 📚 Additional Resources

- **Full Design:** [DESIGN.md](DESIGN.md)
- **API Reference:** [API.md](API.md)
- **Project README:** [README.md](README.md)
- **OpenAPI Docs:** http://localhost:8001/docs

---

**End of Developer Guide**
