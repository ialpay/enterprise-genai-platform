# Task Workflow

## Task Types

### 1. Implementation Task
Purpose:
- make the scoped code or doc change required by a task

Rules:
- work on a dedicated branch
- change only allowed files
- do not update live project-state docs unless the task explicitly requires it

### 2. Completion / Handover Task
Purpose:
- record accepted work into project-state documents

Rules:
- update only the relevant state/history documents
- do not introduce new implementation changes

## Branch Naming

Use:
- `task-<number>-<short-name>`

Examples:
- `task-47-expand-eval`
- `task-48-add-ci`

## Standard Flow

1. Confirm current phase and focus from `docs/status.md`
2. Read the task in `docs/codex_tasks.md`
3. Create a task branch
4. Implement only scoped changes
5. Run relevant validation
6. Review the diff
7. Accept or reject the task
8. If accepted, run a completion/handover update
9. Merge only after validation and review pass

## Required Task Summary

Each implementation must report:
- task number
- files changed
- checks run
- unresolved risks or assumptions

## Separation Rules

Implementation tasks must not:
- update `docs/status.md`
- update `docs/manual_progress.md`
- update `docs/roadmap.md`

Completion / handover tasks may update:
- `docs/status.md`
- `docs/manual_progress.md`
- `docs/architecture-decisions.md` if a real design decision changed

## Review Rule

The same task run should not be trusted as:
- planner
- implementer
- verifier
- final approver

At minimum, separate:
- builder
- verifier
- reviewer