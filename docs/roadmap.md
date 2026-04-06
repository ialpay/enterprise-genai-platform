# Project Roadmap

## Project Vision

Build a disciplined enterprise-style GenAI repository that evolves from a verified local application baseline into a grounded, governed, and operationally credible AI platform.

## Current Maturity Summary

### Verified Today

- FastAPI application shell
- Health endpoint
- Retrieval-grounded `/ask` endpoint that uses retrieved context plus grounded prompting
- Explicit insufficient-context handling in `/ask`
- Stable `/ask` error path for Ollama unavailability (HTTP 502)
- Local ingestion pipeline for tracked source folders into Qdrant
- Deterministic retrieval-layer validation with doubles/fakes
- Evaluation runner and question set aligned to grounded `/ask` behavior
- Config/dependency baseline aligned for tracked modules
- Deterministic contract tests for API/config/prompt/retrieval helper assumptions
- Coherent local run path docs/scripts for `.venv`, local Ollama, Docker Qdrant, and Uvicorn
- Repository governance documents
- Operating-model documents
- Task workflow documents
- Prompt-role documents
- GitHub verification workflow baseline
- Protected PR workflow on `main`
- Required checks: `verify`, `secret-scan`

### Present In Repository But Not Yet Counted As Completed Live Baseline

- Future governance and observability work
- Additional packaging and operational hardening
- Any future AI utility code that is not yet integrated and verified through the current live application path

## Current Phase

Milestone 2 review gate and Milestone 3 entry planning.

## Now

- Hold the Milestone 2 review gate
- Prepare the next milestone from the grounded retrieval baseline
- Keep baseline claims conservative: future modules remain non-live until integrated and verified

## Next

- Start the next milestone only after the Milestone 2 review gate closes
- Expand capability only when route behavior and tests confirm integration
- Keep governance and observability sequencing tied to verified live behavior

## Later

- Further retrieval refinement and answer-quality tuning
- Governance expansion tied to live application behavior
- Evaluation maturity tied to integrated functionality
- Operational maturity for the real application path
- Packaging and architecture maturity tied to verified baseline

## Parking Lot

- Advanced retrieval maturity
- Metadata-aware retrieval
- Stronger reranking
- Broader safety/policy expansion
- Agent/orchestration exploration
- Cloud mapping

## Sequencing Rule

Before planning or implementing advanced engineering work, repository docs and task sequencing must reflect the actual verified application baseline rather than staged or partially imported code present in the tree.
