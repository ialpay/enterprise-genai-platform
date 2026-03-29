# Project Status

## Date
2026-03-29

## Current Phase
Governance expansion, operational polish, and packaging maturity.

## Current Focus
- Governance expansion
- Operational maturity refinement
- Packaging maturity and professional operating model
- Operate through task branches and pull requests
- Use GitHub required checks as the first verification gate
- Separate Planner, Builder, Historian, Verifier, and Owner roles
- Keep project memory in repository documents instead of chat history

## Current Operating Model
- Planner = prompt-preparer chat
- Builder = Codex implementation run
- Historian = separate Codex run after merge
- Verifier = GitHub Actions
- Owner / Approver = repository owner

## Current Required Checks
- `verify`
- `secret-scan`

## Completed Recently
- Local enterprise-style RAG baseline
- Retrieval quality baseline
- Evaluation baseline
- Governance/safety baseline
- Operational reliability baseline
- Packaging baseline
- Operating model baseline
- Repository governance baseline established:
  - `.gitignore` hardened
  - `AGENTS.md` rewritten as stable operating policy
  - governance and workflow docs added
  - PR template and `CODEOWNERS` added
  - CI workflow added
  - secret scan workflow added
  - protected PR flow validated on GitHub

## In Progress
- Expand governance coverage beyond baseline
- Refine operational workflows and reliability checks
- Keep packaging documents aligned with current behavior
- Formalise role-based operating model across Planner, Builder, Historian, and Verifier

## Next Recommended Work
1. Update `docs/manual_progress.md`
2. Add next tasks to `docs/codex_tasks.md`
3. Create role prompt library under `prompts/`
4. Begin the next real task using the protected PR workflow

## Risks / Blockers
- Limited evaluation dataset size
- Local-only runtime limits scale testing
- Single-owner workflow limits strict approval enforcement practicality

## Notes
- `manual_progress.md` is the implementation history
- `architecture-decisions.md` captures design reasoning
- `AGENTS.md` contains standing repo rules
- `project-governance.md`, `task-workflow.md`, and `operating-model.md` define the working method