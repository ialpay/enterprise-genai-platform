# AGENTS.md

## Project Purpose
This repository is an enterprise-style GenAI platform reference project.

The project demonstrates:
- local AI runtime with Ollama
- vector retrieval with Qdrant
- FastAPI application layer
- later RAG, orchestration, governance, and AWS deployment

## Development Rules
- Follow the layered architecture in `docs/architecture-overview.md`
- Implement only the current task from `docs/codex_tasks.md`
- Do not add extra features beyond the requested task
- Keep code simple, modular, and readable
- Prefer standard Python and FastAPI patterns
- Do not implement RAG unless explicitly requested
- Do not implement AWS integration unless explicitly requested

## Current Phase
Current phase is:
- initial FastAPI application bootstrap

## Current Infrastructure
- Ollama runs locally on macOS
- Qdrant runs in Docker on localhost:6333

## Important Constraint
For the current task, only implement:
- FastAPI bootstrap
- basic routes
- schemas
- config
- logging