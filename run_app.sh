#!/bin/bash

# Function to kill background processes on exit
cleanup() {
    echo "Stopping services..."
    # Kill all child processes of the current shell script
    pkill -P $$
}
trap cleanup EXIT

# 1. Setup Python Environment
echo "=== Setting up Backend Context ==="
if [ ! -d ".venv" ]; then
    echo "Creating python virtual environment..."
    python3 -m venv .venv
fi

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Installing/Updating Python dependencies..."
pip install -r requirements.txt

# 2. Check for Node.js/NPM
echo "=== Setting up Frontend Context ==="

# Attempt to setup local Node.js if missing
source ./setup_node.sh

if ! command -v npm &> /dev/null
then
    echo "❌ ERROR: 'npm' could not be found."
    echo "The frontend (Vue.js) requires Node.js and npm to run."
    echo "Please install Node.js: https://nodejs.org/en/download/package-manager/"
    echo "Skipping frontend setup..."
    FRONTEND_READY=false
else
    echo "Installing Frontend dependencies..."
    cd frontend
    npm install
    cd ..
    FRONTEND_READY=true
fi

# 3. Start Services
echo "=== Starting Services ==="

# Start Backend
echo "Starting Backend Server (FastAPI)..."
# Using python -m uvicorn to ensure it uses the venv's python
python -m uvicorn backend.main:app --reload --port 8000 &
BACKEND_PID=$!

if [ "$FRONTEND_READY" = true ]; then
    echo "Starting Frontend (Vite)..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    
    echo "✅ Application running!"
    echo "   - Backend: http://localhost:8000/docs"
    echo "   - Frontend: http://localhost:5173"
else
    echo "⚠️  Application running (Backend ONLY)"
    echo "   - Backend: http://localhost:8000/docs"
    echo "   - Frontend: NOT RUNNING (Missing npm)"
fi

# Keep script running to maintain services
wait
