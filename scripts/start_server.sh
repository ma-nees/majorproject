#!/bin/bash
# scripts/start_server.sh
# Starts the fraud detection API server and (optionally) the dashboard.

set -e  # exit on error

# --- Configuration ---
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Load environment variables from config/environment_variables.env if it exists
if [ -f "config/environment_variables.env" ]; then
    export $(grep -v '^#' config/environment_variables.env | xargs)
    echo "Loaded environment variables from config/environment_variables.env"
fi

# Python environment
VENV_PATH="${VENV_PATH:-./venv}"  # override via env if needed
if [ -d "$VENV_PATH" ]; then
    source "$VENV_PATH/bin/activate"
    echo "Activated virtual environment at $VENV_PATH"
else
    echo "Warning: Virtual environment not found at $VENV_PATH. Using system Python."
fi

# --- Start API ---
API_HOST="${API_HOST:-0.0.0.0}"
API_PORT="${API_PORT:-8000}"
WORKERS="${WORKERS:-1}"  # for production, increase to 4+ depending on CPU

echo "Starting fraud detection API on $API_HOST:$API_PORT with $WORKERS worker(s)..."
uvicorn api.main:app --host "$API_HOST" --port "$API_PORT" --workers "$WORKERS" --reload  # remove --reload in production

# --- Optional: Start Dashboard (React) ---
# Uncomment if you want to also start the frontend dev server
# DASHBOARD_DIR="$PROJECT_ROOT/dashboard/frontend"
# if [ -d "$DASHBOARD_DIR" ]; then
#     echo "Starting dashboard frontend..."
#     cd "$DASHBOARD_DIR"
#     npm start &
#     cd "$PROJECT_ROOT"
# fi

# Wait for all background processes (if any)
wait