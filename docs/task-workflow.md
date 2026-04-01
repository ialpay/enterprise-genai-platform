# Task Workflow

## Task Types

### 0. Planning / Milestone Task
Purpose:
- define or refine milestone sequencing
- add or tighten future task definitions
- prepare role-specific prompt packs

Rules:
- keep planning grounded in `docs/status.md` and the verified baseline
- use milestones with meaningful achievements rather than unrelated task piles
- do not mark future work as complete
- trigger routine next-step workflow actions proactively rather than waiting for them to be requested again

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

## Milestone Rule

- forward work should be grouped into milestones
- each milestone should produce one meaningful, reviewable achievement
- each milestone should end with a completion/handover update after accepted merge
- after a milestone closes, Planner and Owner hold a milestone review before the next milestone starts
- accepted tasks must be finalized into clean merge-ready branch states before they are treated as ready for merge

## Branch Naming

Use:
- `task-<number>-<short-name>`

Examples:
- `task-47-expand-eval`
- `task-48-add-ci`

## Standard Flow

1. Confirm current phase and focus from `docs/status.md`
2. Read the milestone and task in `docs/codex_tasks.md`
3. If needed, Planner refines the active milestone and prepares role-specific prompts
4. If routine process correction is needed, such as branch-scope cleanup or handoff preparation, do it before advancing
5. Create a task branch
6. Implement only scoped changes
7. Run relevant validation
8. Review the diff
9. Accept or reject the task
10. If accepted, ensure the task branch is in a clean merge-ready state
11. Merge only after validation, review pass, and branch finalization
12. If accepted merged work requires state/history updates, run a separate completion/handover task
13. If that completion/handover task closes a milestone, hold the Planner/Owner milestone review before starting the next milestone

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

## Planner Handoff Rule

- Builder, Reviewer, and Historian outputs should be concise and structured enough for Planner to turn them into the next prompt handoff
- Planner should interpret role outputs together with repository state, not rely on chat memory alone
- temporary handoff files may be stored under `.run/handoffs/` during an active milestone
- handoff files should be retained until the milestone closes, then deleted as part of milestone cleanup
