# Project Status

## Date

2026-04-01

## Current Phase

Milestone 1 review gate and Milestone 2 entry planning.

## Current Focus

- Hold the Milestone 1 review gate
- Keep live baseline claims aligned to integrated and verified behavior
- Prepare Milestone 2 entry from the current Ollama-backed `/ask` baseline

## Verified Application Baseline

- FastAPI application shell is present
- `GET /health` is implemented and verified
- `POST /ask` is Ollama-backed and returns `source: "ollama"`
- Ollama failure on `/ask` returns HTTP 502 with stable error detail
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

Advanced application modules for retrieval, ingestion, prompting, and vector integration exist in the repository tree, but they are not treated as completed live baseline unless they are integrated into the current application flow and verified by the repository’s tests and workflow.

## Completed Recently

- Task 61: descriptive architecture docs reconciled to the live route baseline
- Task 62: config/dependency baseline stabilized for tracked modules
- Task 63: deterministic contract validation added for live and staged-module assumptions
- Task 64: local developer run path documentation and scripts aligned
- Task 65: repository memory docs updated to reflect the accepted Milestone 1 baseline

## In Progress

- Milestone 1 review gate (Planner + Owner)

## Next Recommended Work

1. Complete the Milestone 1 review gate and confirm completion status
2. If the review gate passes, begin Milestone 2 Task 66 to make ingestion locally runnable from tracked sources
3. Continue enforcing baseline truth: staged retrieval/prompt modules are not live until integrated and verified

## Risks / Blockers

- Milestone 1 should not be treated as closed until review-gate confirmation is recorded
- Advanced modules in the tree may be mistaken for completed live functionality
- Milestone 2 sequencing can drift if staged code is treated as live before route integration and verification

## Notes

- `docs/status.md` reflects the live current repository state
- `docs/roadmap.md` reflects direction, not assumed completion
- Current baseline truth must be grounded in the integrated application path, tests, and repository workflows
