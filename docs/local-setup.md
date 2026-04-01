# Local Setup

This document describes the current local run path for the tracked baseline.

## Prerequisites

- Python 3.11+
- Docker (for Qdrant)
- Ollama installed locally (`ollama` CLI available on `PATH`)

## One-Time Setup

Run from repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Start the Platform

```bash
./scripts/start_platform.sh
```

What the start script does:

1. Prepares local runtime state under `.run/`.
2. Starts or reuses Qdrant in Docker:
   - container name: `qdrant`
   - port: `6333`
   - storage: `infra/docker/qdrant_storage`
3. Checks Ollama at `http://127.0.0.1:11434/api/tags`:
   - if unavailable, starts `ollama serve` in background.
4. Verifies `.venv` exists and activates it.
5. Starts FastAPI with:
   - `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
6. Writes FastAPI PID to `.run/uvicorn.pid` and logs to `app.log`.

## Verify Runtime

```bash
curl http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"hello"}'
```

## Stop the Platform

```bash
./scripts/stop_platform.sh
```

What the stop script does:

1. Stops FastAPI using `.run/uvicorn.pid` when present.
2. Stops Ollama only when it was started by `start_platform.sh`.
3. Stops the Docker container named `qdrant`.

## Notes

- Keep commands local to this repository.
- The scripts are developer utilities and are not deployment orchestration.
