# Project Governance

## Document Ownership Model

### docs/status.md
Purpose:
- current live project state

Must contain:
- current phase
- current focus
- current active task or most recently completed task
- next recommended task
- current blockers or notable risks

Must not contain:
- long-term roadmap detail
- detailed implementation history
- full task specifications
- architectural decision rationale unless summarised briefly

Update when:
- a task is accepted and materially changes current state
- phase or focus genuinely changes
- next recommended task changes

---

### docs/roadmap.md
Purpose:
- medium-term and long-term direction

Must contain:
- planned stages
- future capabilities
- sequencing of larger initiatives

Must not contain:
- day-to-day implementation status
- detailed task execution notes
- temporary working state

Update when:
- project direction changes
- major sequencing changes
- new strategic workstreams are introduced

---

### docs/manual_progress.md
Purpose:
- implementation history

Must contain:
- completed tasks or milestones
- concise factual record of what was finished
- notable implementation outcomes

Must not contain:
- current live status
- future roadmap planning
- speculative next steps presented as completed work

Update when:
- a task or milestone is completed and accepted

---

### docs/architecture-decisions.md
Purpose:
- design decisions and trade-offs

Must contain:
- architectural decisions
- rationale
- trade-offs
- consequences where relevant

Must not contain:
- routine task progress
- temporary working notes
- implementation history without design significance

Update when:
- an accepted change alters architecture
- a new design decision is made
- an old decision is superseded

---

### docs/codex_tasks.md
Purpose:
- task definitions and acceptance criteria

Must contain:
- task identifiers
- task descriptions
- allowed scope where relevant
- acceptance criteria

Must not contain:
- live implementation status
- architecture rationale better suited to architecture-decisions
- implementation history better suited to manual_progress

Update when:
- adding new tasks
- refining future task definitions
- correcting task numbering or acceptance wording

---

## Operating Rules

1. A fact should have one primary home.
2. `docs/status.md` is the live operational snapshot.
3. `docs/codex_tasks.md` defines the work, but does not prove it is finished.
4. `docs/manual_progress.md` records completion, but does not define future work.
5. `docs/architecture-decisions.md` records why a design choice exists.
6. `docs/roadmap.md` describes direction, not day-to-day execution.

## Quick Placement Guide

- "What are we doing now?" → `docs/status.md`
- "What are we planning later?" → `docs/roadmap.md`
- "What did we complete?" → `docs/manual_progress.md`
- "Why was this design chosen?" → `docs/architecture-decisions.md`
- "What exactly must this task do?" → `docs/codex_tasks.md`