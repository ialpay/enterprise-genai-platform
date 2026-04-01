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
- define or refine milestones
- define or refine tasks
- ensure each milestone has one meaningful achievement
- prepare role-specific prompts
- prepare milestone prompt packs for Builder, Reviewer, and Historian
- keep task scope tight
- propose allowed files and acceptance criteria
- interpret returned outputs from Builder, Reviewer, and Historian
- hold a milestone review with Owner after each completed milestone before authorizing the next milestone
- trigger routine process steps proactively when they are the next required part of the workflow

Must not:
- approve its own task as complete
- act as final implementation authority
- act as Builder, Reviewer, and Historian for the same change

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
6. Temporary cross-chat handoff files may be stored under `.run/handoffs/` during an active milestone, but they are not project memory and should be deleted after the milestone closes.
7. Routine workflow steps should happen automatically and in order; they should not depend on the Owner restating them each time.
8. A task is not merge-ready merely because Reviewer passed; accepted work must also be isolated and left in a clean merge-ready branch state.

## Lifecycle

### Before implementation
Planner:
- defines or refines the active milestone
- prepares or refines the task
- defines scope
- prepares Builder prompt if needed
- triggers routine process-correction work when scope discipline or handoff discipline requires it

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

### After review pass and before merge
Planner:
- checks whether the accepted task is actually in a clean merge-ready state
- triggers routine finalization if the branch still has uncommitted or mixed-scope work

Builder:
- performs only the minimum finalization needed to leave the accepted task in a clean merge-ready state

### After merge
Historian:
- runs as a separate Codex task
- updates only state/history docs
- opens a docs-only PR if needed

Owner:
- reviews and merges historian update

### After milestone completion
Planner:
- reviews what was actually achieved and verified
- checks whether the authoritative baseline changed
- prepares the next milestone recommendation or re-sequencing proposal

Owner:
- reviews milestone achievement and remaining risks
- approves whether the next milestone should proceed

## Milestone Rule

- forward work should be grouped into milestones rather than treated as unrelated tasks
- each milestone should end with a Historian update after accepted merge
- a Planner/Owner milestone review gate must occur before the next milestone is authorized
- milestone planning must remain grounded in the integrated and verified baseline
- temporary handoff artifacts used during a milestone should be cleaned up after milestone closure
- accepted implementation tasks must be finalized into clean merge-ready branch states before merge sequence continues

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
