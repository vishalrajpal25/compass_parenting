#!/bin/bash
# Quick start script for Compass backend

set -e

echo "🚀 Starting Compass Backend..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from defaults..."
    cat > .env << EOF
# Database
DATABASE_URL=postgresql+asyncpg://compass:compass_dev_password@localhost:5432/compass

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=dev_secret_key_change_in_production
DEBUG=true
ENVIRONMENT=development

# CORS
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
EOF
fi

# Check if database is running
echo "🔍 Checking database connection..."
if ! docker ps | grep -q compass_postgres; then
    echo "📦 Starting Docker services..."
    docker-compose up -d postgres redis qdrant
    echo "⏳ Waiting for database to be ready..."
    sleep 5
fi

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "📦 Installing dependencies..."
source venv/bin/activate
pip install -q -r requirements.txt

# Run migrations
echo "🗄️  Running database migrations..."
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
alembic upgrade head

echo "✅ Backend is ready!"
echo ""
echo "To start the server, run:"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "API docs will be available at: http://localhost:8000/api/docs"

