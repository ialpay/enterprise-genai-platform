# AGENTS.md

## Project Purpose
This repository is an enterprise-style GenAI platform reference project.

It demonstrates:
- local AI runtime with Ollama
- vector retrieval with Qdrant
- FastAPI application layer
- governance, evaluation, and operational maturity
- later packaging and deployment maturity

## Core Operating Rules
- Follow the layered architecture in `docs/architecture-overview.md`.
- Use `docs/status.md` as the live source of truth for current phase, current focus, and next recommended task.
- Use `docs/codex_tasks.md` as the source of truth for task numbering and task acceptance criteria.
- Do not add extra features beyond the requested task.
- Keep changes minimal, modular, and readable.
- Prefer standard Python and FastAPI patterns unless the task explicitly requires otherwise.
- Preserve current architecture unless the task explicitly changes it.

## Document Roles
Use project documents as follows:

- `docs/status.md` = current live state
- `docs/roadmap.md` = medium/long-term direction
- `docs/manual_progress.md` = implementation history
- `docs/architecture-decisions.md` = design reasoning and trade-offs
- `docs/codex_tasks.md` = task definitions and acceptance criteria

## Task Workflow Rules
Before implementing a task:
- read `docs/status.md`
- read the relevant task in `docs/codex_tasks.md`
- read any architecture or packaging documents directly relevant to that task
- confirm the allowed file scope before editing

During implementation:
- modify only files required for the task
- avoid unrelated refactors
- do not silently change architecture, evaluation policy, or route behavior unless the task explicitly requires it

After implementation:
- run the relevant validation steps
- report the real files changed
- summarize what was added, changed, or extended
- state any assumptions or unresolved risks

## Validation Expectations
When relevant to the task, run the lightest suitable validation that gives confidence without inventing new requirements.

Prefer applicable checks such as:
- Python import/syntax validation
- targeted script execution
- evaluation runner checks
- task-specific smoke tests

Do not claim checks were run if they were not run.

## Documentation Update Policy
Do not update project state documents unless the task explicitly requires it.

Project state documents include:
- `docs/status.md`
- `docs/manual_progress.md`
- `docs/roadmap.md`

Only update `docs/architecture-decisions.md` when an accepted task genuinely changes an architectural decision or trade-off.

## Data and Local Environment Rules
Keep local runtime state, caches, logs, and generated storage out of version-controlled changes unless the task explicitly requires them.

`.env.example` may remain tracked as a safe template, but real secret-bearing `.env` files must not be committed.

## Implementation Style
- Keep logic deterministic where the task requires deterministic behavior.
- Reuse existing helpers or constants when practical instead of duplicating policy logic.
- Extend existing outputs and structures additively unless the task explicitly requires replacement.
- Prefer small, reviewable diffs.