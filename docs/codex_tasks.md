# Codex Tasks

## Task 1 — Create FastAPI Skeleton

Create a FastAPI application inside the `app` directory.

Requirements:

- Health endpoint `/health`
- Question endpoint `/ask`
- Environment configuration loader
- Logging setup
- Basic request/response models

Use Python and FastAPI.

## Task 2 — Create application bootstrap

Create the initial FastAPI bootstrap in `app/main.py`.

Requirements:

- FastAPI app instance
- `/health` endpoint returning `{ "status": "ok" }`
- `/ask` endpoint placeholder returning a static response
- configuration loader in `app/core/config.py`
- logging setup in `app/core/logging.py`

Keep the implementation simple and modular.


# Codex Tasks

## Task 4 — Build initial FastAPI application shell

Implement the initial application bootstrap for this project.

### Requirements

1. Create `app/main.py`
   - initialize a FastAPI application
   - register routes from `app/api/routes.py`

2. Create `app/api/routes.py`
   - implement `GET /health`
   - return JSON: `{ "status": "ok" }`
   - implement `POST /ask`
   - for now return a static placeholder JSON response

3. Create `app/api/schemas.py`
   - define request model for `/ask`
   - define response model for `/ask`

4. Create `app/core/config.py`
   - create a small settings class using environment variables
   - include:
     - app name
     - app environment
     - host
     - port
     - Ollama base URL
     - Ollama model
     - Qdrant host
     - Qdrant port
     - Qdrant collection

5. Create `app/core/logging.py`
   - create a simple logger configuration helper

### Constraints
- keep the code simple and modular
- use FastAPI and standard Python
- do not implement RAG yet
- do not implement AWS integration yet
- do not add startup health checks for Ollama or Qdrant yet
- use standard Python logging only
- no Docker changes are needed for this task

### Acceptance Criteria
- app starts successfully
- `GET /health` returns status ok
- `POST /ask` returns a valid placeholder response
- configuration is loaded from environment variables
- logging is initialized cleanly