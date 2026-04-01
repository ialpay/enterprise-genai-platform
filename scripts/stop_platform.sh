#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "$PROJECT_ROOT"

QDRANT_NAME="qdrant"
OLLAMA_PID_FILE="/tmp/enterprise-genai-platform-ollama.pid"
RUN_DIR=".run"
UVICORN_PID_FILE="${RUN_DIR}/uvicorn.pid"

echo "Stopping Enterprise GenAI Platform..."

echo "Stopping FastAPI (uvicorn)..."
if [ -f "$UVICORN_PID_FILE" ]; then
  UVICORN_PID="$(cat "$UVICORN_PID_FILE")"
  if ps -p "$UVICORN_PID" >/dev/null 2>&1; then
    kill "$UVICORN_PID" || true
    for _ in {1..5}; do
      if ! ps -p "$UVICORN_PID" >/dev/null 2>&1; then
        break
      fi
      sleep 1
    done
    if ps -p "$UVICORN_PID" >/dev/null 2>&1; then
      echo "Force-stopping uvicorn..."
      kill -9 "$UVICORN_PID" || true
    fi
    echo "FastAPI process stopped."
  else
    echo "FastAPI PID file was stale."
  fi
  rm -f "$UVICORN_PID_FILE"
else
  if pgrep -f "uvicorn app.main:app" >/dev/null; then
    echo "Stopping FastAPI process without PID file..."
    pkill -f "uvicorn app.main:app" || true
  else
    echo "FastAPI is not running."
  fi
fi

echo "Stopping Ollama (if started here)..."
if [ -f "$OLLAMA_PID_FILE" ]; then
  OLLAMA_PID="$(cat "$OLLAMA_PID_FILE")"
  if ps -p "$OLLAMA_PID" >/dev/null 2>&1; then
    kill "$OLLAMA_PID" || true
  fi
  rm -f "$OLLAMA_PID_FILE"
else
  echo "Ollama was not started by this workflow."
fi

echo "Stopping Qdrant container..."
if docker ps -q -f name=^${QDRANT_NAME}$ | grep -q .; then
  docker stop "${QDRANT_NAME}" >/dev/null
else
  echo "Qdrant container is not running."
fi

echo "Platform stopped."
