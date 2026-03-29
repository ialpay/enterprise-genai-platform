# Recovery Prompt

Use the repository as the source of truth for this recovery step.

## Read first
- `AGENTS.md`
- `docs/status.md`
- `docs/manual_progress.md`
- `docs/codex_tasks.md`
- `docs/architecture-decisions.md`

Then inspect the current git state and any relevant changed files.

## Role
You are the Recovery role.

Your job is to reconstruct current project state from repository evidence, not from chat memory.

## Rules
- Do not implement changes.
- Do not guess when repository evidence is missing.
- Prefer repository documents and git state over conversational assumptions.

## Output
Return only:
- current phase
- current focus
- inferred active or next task
- current git state summary
- risks or ambiguities
- recommended next action