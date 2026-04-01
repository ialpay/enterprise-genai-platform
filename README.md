# Enterprise GenAI Platform

Local-first reference platform with:
- FastAPI application layer
- Ollama for model inference
- Qdrant for vector storage

## Local Developer Quickstart

Run these commands from the repository root.

1. Create and activate a Python virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the local platform:
```bash
./scripts/start_platform.sh
```

4. Verify the API:
```bash
curl http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"What is this service?"}'
```

5. Stop the platform:
```bash
./scripts/stop_platform.sh
```

## Runtime Assumptions

- Python is managed through the local `.venv` virtual environment.
- Qdrant is run as a local Docker container named `qdrant`.
- Ollama must be installed locally; the start script checks `http://127.0.0.1:11434` and starts `ollama serve` when needed.
- FastAPI is started with:
  - `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`

For a fuller setup and behavior reference, see `docs/local-setup.md`.
