# Runbook

## Normal Delivery Flow

### 1. Planner prepares the task
Inputs:
- `AGENTS.md`
- `docs/status.md`
- `docs/codex_tasks.md`
- `docs/architecture-decisions.md` when relevant

Outputs:
- chosen task number
- allowed files
- role-specific prompt if needed

### 2. Owner approves scope
Check:
- task is the right priority
- scope is acceptable
- allowed files are clear

### 3. Builder implements on a task branch
Start from clean `main`:

```bash
git switch main
git fetch origin
git reset --hard origin/main
git switch -c task-<number>-<short-name>