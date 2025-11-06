# Backend

FastAPI backend for Compass.

## Setup

1. **Install dependencies:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

3. **Start server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Environment

Create `.env`:
```env
DATABASE_URL=postgresql+asyncpg://compass:password@localhost:5432/compass
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
DEBUG=true
```

## Structure

```
app/
├── api/        # Endpoints
├── core/       # Config, security
├── db/         # Database setup
├── models/     # SQLAlchemy models
├── schemas/    # Pydantic schemas
├── services/   # Business logic
└── scrapers/   # Catalog scrapers
```

## API Endpoints

- `POST /api/v1/auth/register` - Register
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/families/me` - Get family
- `POST /api/v1/children` - Create child
- `GET /api/v1/activities` - List activities
- `POST /api/v1/recommendations` - Get recommendations

## Tests

```bash
pytest
```

## Migrations

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```
