# Scout Reports 📊

A web application for displaying, searching, and managing Scout research reports with automated preference learning capabilities.

**Version:** 1.0.0
**Status:** Design Phase → Implementation

---

## 🎯 Overview

Scout Reports provides a centralized platform to:

- 📖 **Display** Research reports with rich Markdown rendering
- 🔍 **Search** Full-text search across all reports
- 🏷️ **Filter** By status, topic, date, and tags
- ⭐ **Feedback** Collect user ratings and comments
- 📈 **Analytics** View statistics and trends
- 🎓 **Learn** Automated preference learning (EMA)

---

## 🚀 Quick Start

### For Humans (Developers)

```bash
# Clone and setup
git clone <repo-url> ScoutReports
cd ScoutReports

# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# Initialize database
docker-compose -f docker-compose.dev.yml exec backend python scripts/init_db.py

# Access
# Frontend: http://localhost:5174
# Backend API: http://localhost:8001
# API Docs: http://localhost:8001/docs
```

### For AI Agents

```python
from app.api.agent_api import AgentAPI

# Initialize API client
api = AgentAPI(base_url="http://localhost:8001")

# List reports
reports = api.list_reports(status="completed", limit=10)

# Get specific report
report = api.get_report(reports[0]["path"])
print(f"Title: {report['metadata']['title']}")
print(f"Content: {report['content'][:200]}...")

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
print(f"Total reports: {stats['total_reports']}")

# Get preferences
prefs = api.get_preferences()
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│              Scout Reports System              │
├─────────────────────────────────────────────────┤
│  Frontend (React + Vite)     Port 5174        │
│  ├─ Report List                                │
│  ├─ Report Detail                              │
│  ├─ Search                                     │
│  ├─ Analytics                                  │
│  └─ Preferences                                │
├─────────────────────────────────────────────────┤
│  Backend (FastAPI)          Port 8001          │
│  ├─ Report Service                             │
│  ├─ Preference Service (EMA Learning)          │
│  ├─ Search Service                             │
│  ├─ Analytics Service                          │
│  └─ SQLite Database                            │
├─────────────────────────────────────────────────┤
│  Scout Data (Read-only Mount)                  │
│  └─ kanban/projects/*.md                       │
│  └─ workspace-scout/PREFERENCES*.json          │
└─────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
ScoutReports/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   ├── services/          # Business logic
│   │   ├── models/            # Database models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── repositories/      # Data access
│   │   └── utils/             # Utilities
│   ├── tests/                 # Tests
│   └── requirements.txt
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── pages/             # Page components
│   │   ├── components/        # Reusable components
│   │   ├── stores/            # Zustand state
│   │   ├── services/          # API services
│   │   └── types/             # TypeScript types
│   ├── tests/                 # Tests
│   └── package.json
│
├── DESIGN.md                   # Full technical design
├── DEVELOPER_GUIDE.md          # Developer guide
├── API.md                     # Simplified API docs
├── README.md                   # This file
├── docker-compose.dev.yml      # Development Docker
└── docker-compose.prod.yml     # Production Docker
```

---

## 🔧 Technology Stack

### Backend
- **Framework:** FastAPI
- **Database:** SQLite (with FTS)
- **Validation:** Pydantic
- **Markdown:** markdown2
- **Logging:** loguru
- **Testing:** pytest

### Frontend
- **Framework:** React 19 + Vite
- **UI:** React Bootstrap 5
- **State:** Zustand
- **Routing:** React Router v7
- **Data Fetching:** TanStack Query
- **Markdown:** react-markdown
- **Testing:** Vitest + Playwright

---

## 📡 API Endpoints

### Reports

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/reports` | List all reports |
| GET | `/api/reports/{path}` | Get report content |
| GET | `/api/reports/{path}/metadata` | Get report metadata |

### Feedback

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/feedback` | Submit feedback |
| GET | `/api/feedback/{report_id}` | Get report feedback |

### Search

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/search` | Full-text search |

### Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/overview` | Overall statistics |
| GET | `/api/analytics/trends` | Trend analysis |

### Preferences

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/preferences` | Get Scout preferences |
| GET | `/api/preferences/topics` | Get topic affinities |

**Full API Documentation:** http://localhost:8001/docs

---

## 🤖 Agent-Ready Features

This system is designed to be easily used by AI agents:

### 1. **Simplified API Wrapper**

```python
from app.api.agent_api import AgentAPI

api = AgentAPI()
reports = api.list_reports(status="completed")
```

### 2. **Comprehensive Documentation**

- Module-level docstrings
- Function-level docstrings with examples
- Type hints everywhere
- Clear error messages

### 3. **Standardized Responses**

All API responses follow a standard format:

```json
{
  "success": true,
  "data": {...},
  "message": null
}
```

### 4. **OpenAPI Specification**

Auto-generated API documentation at `/docs`

---

## 🛠️ Development

### Backend Development

```bash
cd backend

# Install dependencies
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest

# Run with hot reload
uvicorn app.main:app --reload

# Linting
black app/
flake8 app/
mypy app/
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Run tests
npm run test

# Linting
npm run lint
npm run type-check
```

### Docker Development

```bash
# Start all services
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop services
docker-compose -f docker-compose.dev.yml down

# Rebuild
docker-compose -f docker-compose.dev.yml up -d --build
```

---

## 🧪 Testing

### Backend Tests

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# Coverage report
pytest --cov=app tests/ --cov-report=html
```

### Frontend Tests

```bash
# Unit tests
npm run test

# E2E tests
npx playwright test

# Coverage
npm run test:coverage
```

---

## 📊 Monitoring

### Health Check

```bash
curl http://localhost:8001/health
```

### Logs

```bash
# Backend logs
docker-compose -f docker-compose.dev.yml logs backend -f

# Frontend logs
docker-compose -f docker-compose.dev.yml logs frontend -f
```

---

## 🔒 Security

- Input validation (Pydantic schemas)
- Rate limiting (slowapi)
- SQL injection prevention (ORM)
- XSS protection (React)
- CORS configuration

**Note:** Authentication is planned for Phase 2.

---

## 🚢 Deployment

### Production Setup

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start production services
docker-compose -f docker-compose.prod.yml up -d

# Check health
curl http://localhost/health
```

### Environment Variables

See `.env.example` for full configuration.

---

## 📈 Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| Page Load Time | < 500ms | TBD |
| API Response Time | < 100ms | TBD |
| Test Coverage | > 80% | 0% |
| Lighthouse Score | > 90 | TBD |

---

## 🗺️ Roadmap

### Phase 1: Core Features (Current)
- [x] Design documentation
- [ ] Backend API
- [ ] Frontend UI
- [ ] Report parsing
- [ ] Feedback system
- [ ] Basic search

### Phase 2: Enhanced Features
- [ ] Advanced search
- [ ] Analytics dashboard
- [ ] Bookmarking
- [ ] Tagging
- [ ] Filtering

### Phase 3: Advanced Features
- [ ] User authentication
- [ ] Report sharing
- [ ] Collaboration
- [ ] Export features
- [ ] Mobile app

---

## 🤝 Contributing

### Development Workflow

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and test
3. Submit pull request
4. Code review
5. Merge to main

### Code Style

- **Backend:** PEP 8, Black formatting
- **Frontend:** ESLint, Prettier
- **Commits:** Conventional Commits

---

## 📝 Documentation

- **Full Design:** [DESIGN.md](DESIGN.md)
- **Developer Guide:** [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)
- **API Reference:** [API.md](API.md)
- **OpenAPI:** http://localhost:8001/docs

---

## 🐛 Troubleshooting

### Common Issues

**Issue: Backend won't start**
```bash
# Check logs
docker-compose logs backend

# Rebuild
docker-compose up -d --build backend
```

**Issue: Frontend can't connect to backend**
```bash
# Check CORS settings
# Ensure VITE_API_URL is correct
# Check backend is running
curl http://localhost:8001/health
```

**Issue: Database errors**
```bash
# Reinitialize database
docker-compose exec backend python scripts/init_db.py

# Check database file
ls -la backend/data/scout_reports.db
```

---

## 📞 Support

- **Documentation:** See docs in `/docs/`
- **Issues:** GitHub Issues
- **Discussions:** GitHub Discussions

---

## 📄 License

MIT License

---

## 🙏 Acknowledgments

- Scout Agent Team
- OpenClaw Team
- FastAPI Community
- React Community

---

**Last Updated:** 2026-03-04
**Version:** 1.0.0
**Status:** Design Phase

---

## 🎯 Quick Reference

### Key Files

| File | Purpose |
|------|---------|
| `DESIGN.md` | Full technical design |
| `README.md` | This file |
| `backend/app/main.py` | FastAPI application |
| `frontend/src/App.tsx` | React app |
| `docker-compose.dev.yml` | Development Docker |
| `docker-compose.prod.yml` | Production Docker |

### Key Commands

| Command | Purpose |
|---------|---------|
| `docker-compose -f docker-compose.dev.yml up -d` | Start dev |
| `docker-compose -f docker-compose.dev.yml down` | Stop dev |
| `pytest` | Run backend tests |
| `npm run test` | Run frontend tests |
| `npm run dev` | Start frontend dev server |

### Key URLs

| URL | Purpose |
|-----|---------|
| http://localhost:5174 | Frontend |
| http://localhost:8001 | Backend API |
| http://localhost:8001/docs | API Docs |
| http://localhost:8001/health | Health Check |

---

**End of README**
