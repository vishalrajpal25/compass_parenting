#!/bin/bash
# Quick start script for Compass - Manual Control

set -e

echo "🚀 Compass Manual Startup"
echo "========================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Docker Services
echo -e "${YELLOW}Step 1: Starting Docker Services...${NC}"
cd /Users/vishal.rajpal/Documents/projects/compass
docker-compose up -d postgres redis qdrant
sleep 3
echo -e "${GREEN}✅ Docker services started${NC}"
echo ""

# Step 2: Backend
echo -e "${YELLOW}Step 2: Starting Backend Server...${NC}"
cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
export DATABASE_URL="postgresql+asyncpg://compass:compass_dev_password@localhost:5433/compass"
export DEBUG=true
export ENVIRONMENT=development
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

echo "Environment:"
echo "  DATABASE_URL=$DATABASE_URL"
echo "  DEBUG=$DEBUG"
echo ""
echo "Starting backend server..."
echo "  👉 Backend will run at: http://localhost:8000"
echo "  👉 API Docs: http://localhost:8000/api/docs"
echo ""
echo "Press CTRL+C to stop backend"
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

