# Pilot Track

This document tracks isolated AI pilots only.
It is not the live source of truth for the application baseline.
Live baseline truth remains in:

- `docs/status.md`
- `docs/manual_progress.md`
- `docs/roadmap.md`

## Purpose

Track pilot experiments for learning, comparison, and architectural fit assessment without treating them as official baseline progress.

## Pilot Status Legend

- `active`
- `paused`
- `discarded`
- `promotion_candidate`

## Usage Rules

- Use this document for pilot work only.
- Keep one entry per pilot.
- Tie each pilot to a specific baseline reference.
- Use separate branches and isolated entrypoints by default.
- Use separate Qdrant collections when pilot retrieval or indexing behavior changes.
- Do not copy pilot progress into live state documents unless a pilot is explicitly promoted through the normal milestone process.

## Pilot Index

| Pilot | Status | Branch | Entrypoint | Collection | Baseline Ref |
|---|---|---|---|---|---|
| Agentic workflows | active | `pilot/agentic-workflows` | `scripts/pilot_agentic_workflow.py` | `not applicable` | `Milestone 3 baseline / 2026-04-06` |
| Conversational memory and context management | paused | `TBD` | `TBD` | `pilot_memory_context` | `Milestone 3 baseline / 2026-04-06` |
| Multimodal / document-intelligence | paused | `TBD` | `TBD` | `pilot_multimodal_docs` | `TBD` |

## Pilot Entries

### Agentic workflows
- Purpose: Explore agent-style orchestration and tool-using workflows in isolation from the live `/ask` route.
- Status: `active`
- Baseline reference: `Milestone 3 baseline / 2026-04-06`
- Branch/location: `pilot/agentic-workflows`
- Isolated entrypoint: `scripts/pilot_agentic_workflow.py`
- Isolated collection: `not applicable`
- Isolation rules: Must run outside the live `/ask` route, must not use feature flags as the default isolation method, must not update live baseline status/history docs, and must use a separate collection only if retrieval/indexing is later introduced inside the pilot.
- Comparison note: Compare against the current grounded and minimally governed `/ask` baseline for operator usefulness, task-completion quality, and architectural fit.
- Non-goals: Do not replace the live `/ask` route, do not introduce memory as part of this pilot, do not add multimodal behavior, and do not treat pilot output as baseline progress.
- Promotion test: Consider promotion only if the pilot shows clear value on multi-step task completion or tool-using workflow support beyond the current grounded baseline while remaining deterministic enough to validate and operationally understandable.
- Discard / pause condition: Pause or discard if the pilot mostly reproduces the current grounded route, requires invasive baseline changes to be useful, or fails to show a clear learning or architectural-fit advantage.

### Conversational memory and context management
- Purpose: Explore memory/context handling outside the live baseline to assess whether it improves assistant continuity without degrading control.
- Status: `paused`
- Baseline reference: `Milestone 3 baseline / 2026-04-06`
- Branch/location: `TBD`
- Isolated entrypoint: `TBD`
- Isolated collection: `pilot_memory_context`
- Isolation rules: Must use isolated storage/indexing and must not change the current live grounded route by default.
- Comparison note: Compare against the current single-turn grounded route.
- Promotion test: Consider promotion only if memory improves usefulness measurably without weakening deterministic control, safety handling, or observability.

### Multimodal / document-intelligence
- Purpose: Explore richer document understanding beyond the current text-centric grounded path.
- Status: `paused`
- Baseline reference: `TBD`
- Branch/location: `TBD`
- Isolated entrypoint: `TBD`
- Isolated collection: `pilot_multimodal_docs`
- Isolation rules: Must stay isolated from the live `/ask` route and use separate indexing/storage behavior where needed.
- Comparison note: Compare against the current text-grounded document workflow.
- Promotion test: Consider promotion only if multimodal handling improves grounded utility in a way that remains explainable, testable, and operationally manageable.
