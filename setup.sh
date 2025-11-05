#!/bin/bash

# Compass Project Setup Script
# This script creates the complete project structure for the Compass MVP

set -e

echo "🚀 Setting up Compass project structure..."

# Create backend directories
echo "📁 Creating backend structure..."
mkdir -p backend/app/{api,models,services,scrapers,core,db,utils}
mkdir -p backend/app/api/{endpoints,deps}
mkdir -p backend/tests/{unit,integration}
mkdir -p backend/alembic/versions

# Create frontend directories
echo "📁 Creating frontend structure..."
mkdir -p frontend/src/{components,pages,hooks,store,services,utils,types}
mkdir -p frontend/src/components/{intake,recommendations,solver,partner,common}
mkdir -p frontend/public

# Create other directories
mkdir -p scripts
mkdir -p logs

# Create backend __init__.py files
echo "📝 Creating Python package files..."
touch backend/app/__init__.py
touch backend/app/api/__init__.py
touch backend/app/api/endpoints/__init__.py
touch backend/app/models/__init__.py
touch backend/app/services/__init__.py
touch backend/app/scrapers/__init__.py
touch backend/app/core/__init__.py
touch backend/app/db/__init__.py
touch backend/app/utils/__init__.py
touch backend/tests/__init__.py

# Create .gitignore
echo "📝 Creating .gitignore..."
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST
venv/
ENV/
env/

# Node
node_modules/
dist/
.next/
out/
build/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
.pnpm-store/

# Environment
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Database
*.db
*.sqlite
*.sqlite3

# Logs
logs/
*.log

# Testing
.coverage
htmlcov/
.pytest_cache/
coverage/

# Misc
*.bak
*.tmp
.cache/
EOF

# Create .env.example
echo "📝 Creating .env.example..."
cat > .env.example << 'EOF'
# Database
DATABASE_URL=postgresql://compass:your_password@localhost:5432/compass

# Redis
REDIS_URL=redis://localhost:6379/0

# Vector DB
QDRANT_URL=http://localhost:6333

# JWT Authentication
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# OpenAI (for LLM Q&A)
OPENAI_API_KEY=sk-your-openai-key-here

# Anthropic (alternative LLM)
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Email
SENDGRID_API_KEY=SG.your-sendgrid-key-here
FROM_EMAIL=noreply@compassapp.com
FROM_NAME=Compass

# Frontend
VITE_API_URL=http://localhost:8000/api

# Features
BANDITS_ENABLED=true
LLM_QA_ENABLED=true

# Monitoring
SENTRY_DSN=
PLAUSIBLE_DOMAIN=

# Development
DEBUG=true
LOG_LEVEL=INFO
EOF

# Create docker-compose.yml
echo "📝 Creating docker-compose.yml..."
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgis/postgis:16-3.4
    container_name: compass_postgres
    environment:
      POSTGRES_DB: compass
      POSTGRES_USER: compass
      POSTGRES_PASSWORD: compass_dev_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U compass"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: compass_redis
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  qdrant:
    image: qdrant/qdrant:latest
    container_name: compass_qdrant
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

volumes:
  postgres_data:
  qdrant_data:
EOF

echo "✅ Project structure created successfully!"
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env and fill in your configuration"
echo "2. Run 'docker-compose up -d' to start PostgreSQL, Redis, and Qdrant"
echo "3. Set up backend: cd backend && ./setup_backend.sh"
echo "4. Set up frontend: cd frontend && ./setup_frontend.sh"
echo ""
echo "See README.md for detailed instructions."
