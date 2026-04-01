# Project Roadmap

## Project Vision

Build a disciplined enterprise-style GenAI repository that evolves from a verified local application baseline into a grounded, governed, and operationally credible AI platform.

## Current Maturity Summary

### Verified Today

- FastAPI application shell
- Health endpoint
- Ollama-backed `/ask` endpoint
- Stable `/ask` error path for Ollama unavailability (HTTP 502)
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

- Retrieval modules
- Ingestion modules
- Prompt-building modules
- Vector-store integration modules
- Additional AI utility code that is not yet integrated and verified through the current live application path

## Current Phase

Milestone 1 review gate and Milestone 2 entry planning.

## Now

- Hold the Milestone 1 review gate
- Prepare Milestone 2 Task 66 from the current verified baseline
- Keep baseline claims conservative: staged modules remain non-live until integrated and verified

## Next

- Start Milestone 2 with ingestion-run coherence (Task 66) after the Milestone 1 review gate
- Integrate retrieval/prompt/vector path into the live route incrementally
- Expand capability only when route behavior and tests confirm integration

## Later

- Retrieval integration and grounded answer flow
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
