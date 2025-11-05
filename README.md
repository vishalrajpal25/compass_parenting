# Compass - AI-Powered Children's Enrichment Advisor

**Version:** 1.0.0 (MVP)  
**Status:** Development  
**Solo Builder Project**

## Overview

Compass is a hybrid AI advisor that helps parents find the best enrichment activities for their children by:
- Building concise child and family profiles
- Using a structured recommender and constraint solver for optimal scheduling
- Providing explainable recommendations with tradeoff visibility
- Automating local catalog ingestion with zero-touch operations

## Documentation

- **[Product Requirements Document](./docs/PRD_v4.2.md)** - Complete product vision and requirements
- **[Technical Specification](./docs/TECHNICAL_SPEC.md)** - Architecture, data models, and implementation details

## Quick Start

### Prerequisites

- **Backend:**
  - Python 3.11+
  - PostgreSQL 16+ with PostGIS extension
  - Redis 7+
  
- **Frontend:**
  - Node.js 18+ (with pnpm)
  
- **Tools:**
  - Docker & Docker Compose (recommended for local development)
  - Git

### Initial Setup

1. **Clone and navigate to project:**
   ```bash
   cd /Users/vishal.rajpal/Documents/projects/compass
   ```

2. **Create environment files:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Option A: Docker (Recommended)**
   ```bash
   docker-compose up -d
   ```

4. **Option B: Manual Setup**
   
   **Backend:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   
   # Run migrations
   alembic upgrade head
   
   # Start server
   uvicorn app.main:app --reload
   ```
   
   **Frontend:**
   ```bash
   cd frontend
   pnpm install
   pnpm dev
   ```

## Project Structure

```
compass/
├── docs/                    # Documentation
│   ├── PRD_v4.2.md         # Product Requirements Document
│   └── TECHNICAL_SPEC.md   # Technical Specification
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── models/         # SQLAlchemy models
│   │   ├── services/       # Business logic
│   │   ├── scrapers/       # Catalog ingestion
│   │   ├── core/           # Core utilities
│   │   ├── db/             # Database configuration
│   │   └── main.py         # Application entry point
│   ├── tests/              # Backend tests
│   ├── alembic/            # Database migrations
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile
├── frontend/                # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── hooks/          # Custom hooks
│   │   ├── store/          # State management (Zustand)
│   │   ├── services/       # API client
│   │   ├── utils/          # Utilities
│   │   └── types/          # TypeScript types
│   ├── public/             # Static assets
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
├── scripts/                 # Utility scripts
├── docker-compose.yml       # Docker orchestration
├── .env.example            # Environment template
└── README.md               # This file
```

## Development Workflow

### Backend Development

```bash
cd backend

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create new migration
alembic revision --autogenerate -m "description"

# Run migrations
alembic upgrade head

# Run development server
uvicorn app.main:app --reload --port 8000

# Run tests
pytest

# Run scrapers manually (for testing)
python -m app.scrapers.run --scraper city_rec
```

### Frontend Development

```bash
cd frontend

# Install dependencies
pnpm install

# Start development server
pnpm dev

# Build for production
pnpm build

# Run tests
pnpm test

# Lint and format
pnpm lint
pnpm format
```

### Database Management

```bash
# Access PostgreSQL
psql -U compass -d compass

# Backup database
pg_dump -U compass compass > backup.sql

# Restore database
psql -U compass compass < backup.sql

# Reset database (development only!)
psql -U compass -c "DROP DATABASE compass; CREATE DATABASE compass;"
alembic upgrade head
```

## Implementation Phases

### Phase 1: Foundation (Week 1-2) ✅
- [x] Project structure
- [x] Documentation
- [x] Database schema (User, Family, ChildProfile models)
- [x] Authentication system (JWT, password hashing)
- [x] Profile management APIs (families and children CRUD)
- [x] Basic frontend scaffold (React + TypeScript + Tailwind)
- [x] Auth pages (Login, Register, Dashboard)

### Phase 2: Catalog Pipeline (Week 3-4)
- [ ] Scraper framework
- [ ] ICS/RSS/HTML scrapers
- [ ] De-duplication engine
- [ ] Quality validation
- [ ] Celery background workers

### Phase 3: Recommendations (Week 5-6)
- [ ] Scoring algorithm
- [ ] Constraint solver (CP-SAT)
- [ ] Recommendation generation
- [ ] Explanation templates
- [ ] Recommendation UI

### Phase 4: Features & Polish (Week 7-8)
- [ ] Partner sharing
- [ ] Radar digest
- [ ] Email notifications
- [ ] ICS import
- [ ] Report functionality
- [ ] PWA setup
- [ ] Production deployment

## Key Technologies

**Backend:**
- FastAPI (REST API)
- SQLAlchemy + Alembic (ORM, migrations)
- PostgreSQL + PostGIS (database)
- Redis (cache, job queue)
- Celery (background tasks)
- OR-Tools (constraint solver)
- Qdrant (vector DB for LLM)

**Frontend:**
- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS (styling)
- Zustand (state management)
- React Router (routing)
- Axios (HTTP client)

**DevOps:**
- Docker & Docker Compose
- GitHub Actions (CI/CD)
- Railway/Fly.io (backend hosting)
- Vercel (frontend hosting)

## Environment Variables

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=postgresql://compass:password@localhost:5432/compass

# Redis
REDIS_URL=redis://localhost:6379/0

# Vector DB
QDRANT_URL=http://localhost:6333

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI (for LLM Q&A)
OPENAI_API_KEY=sk-...

# Email
SENDGRID_API_KEY=SG...
FROM_EMAIL=noreply@compassapp.com

# Frontend
VITE_API_URL=http://localhost:8000/api
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

### Backend Tests
```bash
cd backend
pytest -v
pytest --cov=app tests/  # With coverage
```

### Frontend Tests
```bash
cd frontend
pnpm test
pnpm test:coverage
```

### End-to-End Tests
```bash
# TODO: Implement E2E tests with Playwright
```

## Deployment

### Development
- Backend: Local (uvicorn) or Docker
- Frontend: Local (vite dev server)
- Database: Local PostgreSQL or Docker

### Production
- Backend: Railway.app or Fly.io
- Frontend: Vercel
- Database: Neon, Supabase, or Railway PostgreSQL
- Redis: Upstash Redis
- Object Storage: Cloudflare R2

See [Deployment Guide](./docs/DEPLOYMENT.md) for detailed instructions.

## Contributing

This is a solo project, but if you'd like to contribute:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[To be determined]

## Roadmap

### MVP (8 weeks)
- ✅ Project setup & documentation
- ⏳ Core features (profiles, catalog, recommendations)
- ⏳ Partner sharing & radar
- ⏳ Pilot launch (100 families)

### Post-MVP
- Multi-city expansion
- Bilingual support (EN/ES)
- Provider self-service portal
- Native mobile apps
- Contextual bandits optimization
- LLM Q&A enhancements

## Contact

Builder: Vishal Rajpal  
Email: [your-email]  
Project Start: November 04, 2025

---

**Built with ❤️ for parents and families**
