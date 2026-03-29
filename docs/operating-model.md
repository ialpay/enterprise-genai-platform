# Operating Model

## Roles

### Owner / Approver
Who:
- repository owner

Responsibilities:
- choose priorities
- approve task scope
- approve merges
- decide whether architecture really changed

### Planner
Who:
- prompt-preparer chat

Responsibilities:
- define or refine tasks
- prepare role-specific prompts
- keep task scope tight
- propose allowed files and acceptance criteria

Must not:
- approve its own task as complete
- act as final implementation authority

### Builder
Who:
- Codex implementation run

Responsibilities:
- implement one scoped task on one branch
- change only allowed files
- report real checks run

Must not:
- decide roadmap
- silently change architecture
- update project-state docs during implementation
- approve itself

### Historian
Who:
- separate Codex run after merge

Responsibilities:
- inspect what was actually merged
- update only project-state docs

Allowed files:
- `docs/status.md`
- `docs/manual_progress.md`
- `docs/architecture-decisions.md` only if a real design decision changed

Must not:
- change app code
- change CI
- change roadmap unless explicitly requested

### Verifier
Who:
- GitHub Actions

Responsibilities:
- run required checks
- provide objective pass/fail

Current required checks:
- `verify`
- `secret-scan`

## Shared Memory

### Standing rules
- `AGENTS.md`

### Live state
- `docs/status.md`

### Task definitions
- `docs/codex_tasks.md`

### Implementation history
- `docs/manual_progress.md`

### Design reasoning
- `docs/architecture-decisions.md`

### Governance and workflow
- `docs/project-governance.md`
- `docs/task-workflow.md`
- `docs/operating-model.md`

### Role prompts
- `prompts/`

## Working Rules

1. Chats are workers, not project memory.
2. The repo is the shared source of truth.
3. No single run should define, implement, verify, and approve the same change.
4. Implementation and history updates must be separate steps.
5. Every important change should go through a branch and PR.

## Lifecycle

### Before implementation
Planner:
- prepares or refines the task
- defines scope
- prepares Builder prompt if needed

Owner:
- approves task scope

### During implementation
Builder:
- starts from clean `main`
- creates task branch
- implements only scoped change
- pushes branch
- opens PR

Verifier:
- runs `verify`
- runs `secret-scan`

Owner:
- reviews PR
- merges or rejects

### After merge
Historian:
- runs as a separate Codex task
- updates only state/history docs
- opens a docs-only PR if needed

Owner:
- reviews and merges historian update

## Branch Rules

### Task branch naming
- `task-<number>-<short-name>`

### Non-task maintenance branch naming
- `chore/<short-name>`

## Merge Rule

Do not merge unless:
- PR exists
- required checks pass
- owner is satisfied with scope and result

## Doc Update Rule

### During implementation
Do not update:
- `docs/status.md`
- `docs/manual_progress.md`
- `docs/roadmap.md`

### After accepted merge
Historian may update:
- `docs/status.md`
- `docs/manual_progress.md`
- `docs/architecture-decisions.md` if needed