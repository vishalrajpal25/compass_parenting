#!/bin/bash
# Frontend startup script

set -e

echo "🚀 Starting Frontend..."
echo "========================"
echo ""

cd /Users/vishal.rajpal/Documents/projects/compass/frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

echo ""
echo "Starting frontend dev server..."
echo "  👉 Frontend: http://localhost:5173"
echo "  👉 Proxy: /api → http://localhost:8000"
echo ""
echo "Press CTRL+C to stop frontend"
echo ""

npm run dev

