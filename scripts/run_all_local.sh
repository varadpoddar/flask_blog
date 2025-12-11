#!/usr/bin/env bash
set -euo pipefail

# Minimal runner to start all three services locally on non-5000 ports.
# Prereq: install deps once (from repo root):
#   python3 -m venv .venv && source .venv/bin/activate
#   pip install -r services/blog-api/requirements.txt -r services/auth/requirements.txt -r services/frontend/requirements.txt

FRONTEND_PORT=${FRONTEND_PORT:-5100}
BLOG_PORT=${BLOG_PORT:-5101}
AUTH_PORT=${AUTH_PORT:-5102}

echo "Starting blog API on :$BLOG_PORT"
(cd "$(dirname "$0")/../services/blog-api" && PORT=$BLOG_PORT BLOG_DB_PATH=./database.db flask --app app run --port "$BLOG_PORT") &
BLOG_PID=$!

echo "Starting auth service on :$AUTH_PORT"
(cd "$(dirname "$0")/../services/auth" && PORT=$AUTH_PORT AUTH_DB_PATH=./auth.db JWT_SECRET=dev-secret flask --app app run --port "$AUTH_PORT") &
AUTH_PID=$!

echo "Starting frontend on :$FRONTEND_PORT (calls blog API on :$BLOG_PORT)"
(cd "$(dirname "$0")/../services/frontend" && PORT=$FRONTEND_PORT BLOG_API_BASE=http://localhost:$BLOG_PORT AUTH_API_BASE=http://localhost:$AUTH_PORT SECRET_KEY=dev flask --app app run --port "$FRONTEND_PORT") &
FRONT_PID=$!

echo "All services started. Frontend: http://localhost:${FRONTEND_PORT}"
echo "Press Ctrl+C to stop."

trap 'echo "Stopping..."; kill $BLOG_PID $AUTH_PID $FRONT_PID 2>/dev/null || true; wait' INT TERM
wait
