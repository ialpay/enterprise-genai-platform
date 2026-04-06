# Project Status

## Date

2026-04-06

## Current Phase

Milestone 3 review gate and next milestone planning.

## Current Focus

- Hold the Milestone 3 review gate
- Keep live baseline claims aligned to merged grounded retrieval, classification, audit, and safety behavior
- Prepare the next phase from the grounded, minimally governed `/ask` baseline

## Verified Application Baseline

- FastAPI application shell is present
- `GET /health` is implemented and verified
- `POST /ask` is grounded through retrieval plus grounded prompting
- `POST /ask` includes deterministic request classification on the original user question
- `POST /ask` emits lightweight audit/decision logs for request handling
- `POST /ask` applies minimal safety handling for suspicious override and hidden-instruction requests
- `/ask` handles insufficient retrieved context explicitly
- Ingestion works locally from tracked source folders into Qdrant
- Retrieval-layer behavior has deterministic validation coverage
- Evaluation runner and question set are aligned to grounded `/ask` behavior
- Config contract baseline covers app, Ollama, embedding, and Qdrant fields
- Lightweight contract tests cover API, config, prompt construction, and retrieval helpers without requiring live Ollama or Qdrant

## Repository / Process Baseline

- Repository governance documents are present
- Operating-model documents are present
- Prompt roles are present under `prompts/`
- GitHub workflows are present for verification and secret scanning
- PR-based, repo-driven workflow is established
- Protected PR workflow on `main`
- Local run path docs/scripts are coherent for `.venv`, local Ollama, Docker Qdrant, and Uvicorn startup
- Required checks:
  - `verify`
  - `secret-scan`

## Important Reality Check

Advanced application modules for retrieval, ingestion, prompting, and vector integration are only treated as live baseline when they are integrated into the active application flow and verified by the repository’s tests and workflow.

## Completed Recently

- Task 71: live request-classification helpers added for the grounded `/ask` route
- Task 72: basic audit logging added for the live `/ask` path
- Task 73: minimal safe handling added for suspicious and hidden-instruction requests
- Task 74: validation expanded for classification-aware live behavior
- Task 66: ingestion pipeline made locally runnable from tracked source folders into Qdrant
- Task 67: deterministic retrieval-layer validation added before route integration
- Task 68: `/ask` moved to a grounded retrieval flow with grounded prompting and explicit insufficient-context handling
- Task 69: evaluation runner and question set aligned to grounded retrieval behavior
- Task 65: repository memory docs updated to reflect the merged Milestone 1 baseline pending review-gate closure

## In Progress

- Milestone 3 review gate (Planner + Owner)

## Next Recommended Work

1. Complete the Milestone 3 review gate and confirm completion status
2. Only after that gate closes, begin the next milestone from the grounded `/ask` baseline
3. Continue enforcing baseline truth: future changes are only live once integrated and verified

## Risks / Blockers

- Milestone 3 should not be treated as closed until review-gate confirmation is recorded
- Advanced modules in the tree may be mistaken for completed live functionality if integration and verification are skipped
- Future milestone sequencing can drift if staged code is treated as live before route integration and verification

## Notes

- `docs/status.md` reflects the live current repository state
- `docs/roadmap.md` reflects direction, not assumed completion
- Current baseline truth must be grounded in the integrated application path, tests, and repository workflows
