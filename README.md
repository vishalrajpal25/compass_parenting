# Compass

AI-powered enrichment activity advisor for parents. Helps you find the best activities for your kids based on their interests, goals, and your family's constraints.

## What It Does

- Builds profiles for your kids and family
- Recommends activities that match interests and goals
- Handles scheduling constraints automatically
- Pulls in local activity catalogs

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 16+ with PostGIS

### Setup

1. **Start services:**
   ```bash
   docker-compose up -d postgres redis qdrant
   ```

2. **Backend:**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   alembic upgrade head
   uvicorn app.main:app --reload
   ```

3. **Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

Visit http://localhost:5173 to use the app.

## Project Structure

```
compass/
├── docs/              # Product and technical docs
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── api/      # Endpoints
│   │   ├── models/   # Database models
│   │   ├── services/ # Business logic
│   │   └── main.py
│   └── alembic/      # Migrations
├── frontend/          # React + TypeScript
│   └── src/
└── docker-compose.yml
```

## Development

### Backend
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm run dev
```

### Database Migrations
```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Environment Variables

Create a `.env` file:

```env
DATABASE_URL=postgresql+asyncpg://compass:password@localhost:5432/compass
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
DEBUG=true
```

## API Docs

When backend is running:
- Swagger: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Tech Stack

**Backend:** FastAPI, SQLAlchemy, PostgreSQL, Redis, Celery  
**Frontend:** React, TypeScript, Vite, Tailwind  
**Tools:** Docker, Alembic, OR-Tools

## Documentation

- [Quick Start Guide](./docs/QUICKSTART.md)
- [Product Requirements](./docs/Compass_PRD_v4_1.md)
- [Technical Spec](./docs/TECHNICAL_SPEC.md)

## Status

MVP in development. Core features:
- ✅ Authentication & profiles
- ✅ Recommendation engine
- ⏳ Catalog pipeline
- ⏳ Partner sharing

---

Built for parents and families
