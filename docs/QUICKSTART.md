# Quick Start Guide

Get Compass running locally in a few minutes.

## Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+

## Steps

### 1. Start Services

```bash
docker-compose up -d postgres redis qdrant
```

Wait a few seconds for services to start.

### 2. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend runs on http://localhost:8000

### 3. Frontend

In a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on http://localhost:5173

## Verify

- Backend health: `curl http://localhost:8000/health`
- Frontend: Open http://localhost:5173 in browser
- API docs: http://localhost:8000/api/docs

## First User

1. Open http://localhost:5173
2. Click "Sign up"
3. Register with email/password
4. You'll be redirected to dashboard

## Troubleshooting

**Backend won't start:**
- Check PostgreSQL is running: `docker-compose ps`
- Verify DATABASE_URL in `.env`

**Frontend proxy errors:**
- Make sure backend is running on port 8000
- Check vite.config.ts proxy settings

**Database errors:**
- Run migrations: `alembic upgrade head`
- Check PostGIS extension is enabled

