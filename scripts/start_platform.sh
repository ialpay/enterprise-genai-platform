#!/bin/bash

set -euo pipefail

QDRANT_NAME="qdrant"
QDRANT_URL="http://127.0.0.1:6333/collections"
OLLAMA_URL="http://127.0.0.1:11434/api/tags"
FASTAPI_URL="http://127.0.0.1:8000/health"
OLLAMA_PID_FILE="/tmp/enterprise-genai-platform-ollama.pid"
RUN_DIR=".run"
UVICORN_PID_FILE="${RUN_DIR}/uvicorn.pid"
FASTAPI_LOG_FILE="app.log"

wait_for_http() {
  local url="$1"
  local name="$2"
  for _ in {1..10}; do
    if curl -sf "$url" >/dev/null; then
      echo "$name is healthy."
      return 0
    fi
    sleep 1
  done
  echo "ERROR: $name is not reachable at $url"
  return 1
}

echo "Starting Enterprise GenAI Platform..."

echo "Preparing FastAPI runtime state..."
mkdir -p "$RUN_DIR"
if [ -f "$UVICORN_PID_FILE" ]; then
  UVICORN_PID="$(cat "$UVICORN_PID_FILE")"
  if ps -p "$UVICORN_PID" >/dev/null 2>&1; then
    echo "Stopping existing FastAPI process (pid $UVICORN_PID)..."
    kill "$UVICORN_PID" || true
    for _ in {1..5}; do
      if ! ps -p "$UVICORN_PID" >/dev/null 2>&1; then
        break
      fi
      sleep 1
    done
  else
    echo "Removing stale FastAPI PID file."
  fi
  rm -f "$UVICORN_PID_FILE"
elif pgrep -f "uvicorn app.main:app" >/dev/null; then
  echo "Stopping stale FastAPI process..."
  pkill -f "uvicorn app.main:app" || true
fi

echo "Starting Qdrant (if needed)..."
if docker ps -q -f name=^${QDRANT_NAME}$ | grep -q .; then
  echo "Qdrant container is already running."
else
  if docker ps -aq -f name=^${QDRANT_NAME}$ | grep -q .; then
    docker start "${QDRANT_NAME}" >/dev/null
  else
    docker run -d \
      --name "${QDRANT_NAME}" \
      -p 6333:6333 \
      -v "$(pwd)/infra/docker/qdrant_storage:/qdrant/storage" \
      qdrant/qdrant >/dev/null
  fi
fi

wait_for_http "$QDRANT_URL" "Qdrant"

echo "Ensuring Ollama is reachable..."
if ! curl -sf "$OLLAMA_URL" >/dev/null; then
  echo "Starting Ollama..."
  nohup ollama serve >/tmp/ollama.log 2>&1 &
  echo $! > "$OLLAMA_PID_FILE"
fi

wait_for_http "$OLLAMA_URL" "Ollama"

if [ ! -f ".venv/bin/activate" ]; then
  echo "ERROR: Python virtual environment not found. Run: python -m venv .venv"
  exit 1
fi

echo "Activating Python environment..."
source .venv/bin/activate

echo "Starting FastAPI..."
echo "FastAPI logs will be written to $FASTAPI_LOG_FILE"
: > "$FASTAPI_LOG_FILE"
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload >"$FASTAPI_LOG_FILE" 2>&1 &
echo $! > "$UVICORN_PID_FILE"

wait_for_http "$FASTAPI_URL" "FastAPI"

echo "Platform started successfully."
echo "FastAPI: http://localhost:8000"
echo "Qdrant:  http://localhost:6333"
echo "Ollama:  http://localhost:11434"
