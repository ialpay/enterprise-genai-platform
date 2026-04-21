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
- Initial evaluation boundary: Start with bounded repository-oriented tasks that require more than one step of reasoning or tool use but do not require autonomous long-running background execution.
- In scope first: Multi-step repository questions, structured repo inspection, bounded tool-using workflows, and planner-style decomposition followed by explicit tool use.
- Out of scope first: Changes to the live `/ask` route, memory features, multimodal handling, autonomous long-running jobs, or any pilot that requires baseline route replacement.
- Initial implementation shape: A standalone script-driven pilot that accepts one bounded repository task, decomposes it into a short step plan, executes only explicitly allowed local read-only tools at first, and returns both the final answer and a compact execution trace.
- Initial pilot-safe input shape: One repository-oriented user request that can be satisfied through a small number of local inspection steps.
- Initial pilot-safe output shape: Final answer, ordered step list, tools used, files inspected, and a short reflection on whether the workflow added value over the baseline.
- First run scenario: Ask the pilot to analyze the current repository baseline and identify the next most reasonable implementation step using a bounded multi-step read-only workflow.
- First run success signal: The pilot produces a coherent step plan, inspects the right files, and returns a materially better or more structured answer than the baseline without unnecessary wandering.
- First run failure signal: The pilot loops, uses tools without improving the answer, inspects irrelevant areas, or produces a result no better than the baseline grounded route.
- Fair comparison rule: Compare Pilot 1 against the current Milestone 3 grounded baseline on the same bounded tasks, using usefulness, task completion, and operator effort as the initial comparison lens.
- Minimum comparison question: Can an isolated agentic workflow complete a bounded multi-step repository task more effectively than the current single-turn grounded baseline without requiring baseline route changes?
- Comparison note: Compare against the current grounded and minimally governed `/ask` baseline for operator usefulness, task-completion quality, and architectural fit.
- Learning signal: Continue only if the pilot shows clearly better multi-step task completion, tool-use sequencing, or operator leverage than the current grounded baseline.
- Phase 2 direction: Extend the shell-stage pilot into a planning-first bounded hybrid agent while keeping the script as execution authority.
- Phase 2 hybrid shape: Code continues to validate requests, derive bounded targets, execute read-only tools, enforce caps and stop conditions, and assemble the output structure. Ollama assists only with short-horizon planning inside those script-enforced limits.
- Phase 2 runtime loop: Validate request -> derive bounded targets in code -> request a short plan from Ollama -> trim/normalize the plan to script limits -> execute only allowlisted read-only inspection steps -> assemble the final answer in code from inspected evidence and trace.
- Phase 2 guardrails: No model-directed tool expansion, no model-directed path expansion beyond script-approved targets, no final-answer freeform generation by Ollama, no write actions, no long loops, and deterministic fallback to code-only planning if Ollama is unavailable.
- Non-goals: Do not replace the live `/ask` route, do not introduce memory as part of this pilot, do not add multimodal behavior, and do not treat pilot output as baseline progress.
- Promotion test: Consider promotion only if the pilot shows clear value on multi-step task completion or tool-using workflow support beyond the current grounded baseline while remaining deterministic enough to validate and operationally understandable.
- Discard / pause condition: Pause or discard if the pilot mostly reproduces the current grounded route, requires invasive baseline changes to be useful, or fails to show a clear learning or architectural-fit advantage.
- First bounded comparison result (Task 79, pilot-only, 2026-04-07):
  - Pilot-only note: This is an isolated pilot learning record and is not live baseline progress.
  - Scenario used: `pilot1_first_bounded_repo_comparison` with request: "Analyze the current repository baseline and identify the next most reasonable implementation step using a bounded multi-step read-only workflow."
  - What the pilot inspected: `docs/pilot-track.md`, `docs/status.md`, and `docs/codex_tasks.md` via bounded `read_file_excerpt` actions (all status `ok`).
  - What answer the pilot produced: "The next most reasonable implementation step is to Complete the Milestone 3 review gate and confirm completion status. Pilot evidence confirms this conclusion with bounded read-only inspection of pilot scope, live status, and task-definition files."
  - Baseline-style comparison summary: Baseline-style answer converged on the same next step; pilot output added explicit inspected files and traceable tool actions, while baseline style did not surface an explicit tool trace.
  - Usefulness judgment: `pilot_more_useful = true` for operator visibility and traceability with equivalent task-completion outcome.
  - Decision: `continue`
- Phase 2 planning question: Does planning-only Ollama assistance improve bounded repository inspection usefulness over the current shell-stage pilot without weakening control, traceability, or operator understanding?
- Planning-phase comparison result (Task 81, pilot-only, 2026-04-16):
  - Pilot-only note: This is an isolated pilot learning record and is not live baseline progress.
  - Scenario used for both paths: "Analyze the current repository baseline and identify the next most reasonable implementation step using a bounded multi-step read-only workflow."
  - Code-only planning run: `--planning-mode code_only` produced `planning_source = code_only` with the bounded 3-step script plan and one bounded `read_file_excerpt` inspection of `docs/codex_tasks.md`.
  - Planning-assisted run: `--planning-mode auto` with bounded Ollama response produced `planning_source = ollama_assisted`; plan structure and execution stayed code-bounded, while step 2 added normalized model focus hints.
  - Structure comparison: No material change. Both runs retained the same script-owned 3-step bounded plan shape and same tool/action caps.
  - Focus comparison: Improved slightly in assisted mode because the step-2 details included explicit short-horizon focus hints while still constrained to script-derived targets.
  - Operator usefulness comparison: Improved slightly for planning readability, but not materially for execution outcome because both runs inspected the same file and produced equivalent final-answer evidence.
  - Decision: `continue`
  - Decision rationale: Continue the pilot to gather more bounded scenarios before stronger claims; current evidence shows small planning readability gains without reduced control, but no clear execution-outcome gain yet.
- Post-merge Pilot 1 hardening state (Tasks 80-83 on `main`, 2026-04-20):
  - Pilot-only note: This remains an isolated pilot learning record and is not live baseline progress.
  - Merged pilot scope now present on `main`: Tasks 80, 81, 82, and 83 are recorded in `docs/codex_tasks.md`, and the isolated entrypoint remains `scripts/pilot_agentic_workflow.py`.
  - Verified hardening facts: the pilot script compiles; deterministic fallback works when Ollama is unreachable; deterministic fallback works when Ollama returns unusable planning output.
  - Latest real pilot auto-run reality check: in the recent verification set on `main`, the pilot returned `planning_source = ollama_fallback_to_code` and `planning_fallback_reason = ollama_plan_unusable`.
  - Operational reading: assisted planning is available and hardened, but current repository evidence does not justify describing it as consistently successful or operationally reliable yet.
  - Decision: `continue`
  - Decision rationale: keep gathering bounded stability and usefulness evidence while preserving isolation, read-only control, and deterministic fallback behavior; do not treat the pilot as baseline-promoted or promotion-ready.
- Phase 3 repeated evidence round 2 comparison (Task 85, pilot-only, 2026-04-21):
  - Pilot-only note: This comparison is isolated Pilot 1 evidence and is not live baseline progress.
  - Evidence structure reused: `scripts/run_pilot_phase3_evidence.py` with the same bounded setup for both rounds (3 scenarios, 1 `code_only` control per scenario, and 3 `auto` attempts per scenario).
  - Round 1 summary:
    - Assisted vs fallback distribution: `8` assisted, `1` fallback (of `9` auto runs).
    - Fallback reasons: `ollama_plan_unusable = 1`.
    - Boundedness invariants: `overall_boundedness_invariants_held = true`.
    - Repeat consistency: `all_scenarios_auto_source_consistent = false`; `all_scenarios_auto_answer_consistent = true`.
    - Operator usefulness indicators: `control_trace_visible = true`; `auto_trace_visible_rate = 1.0`; `auto_non_empty_final_answer_rate = 1.0`.
  - Round 2 summary:
    - Assisted vs fallback distribution: `8` assisted, `1` fallback (of `9` auto runs).
    - Fallback reasons: `ollama_plan_unusable = 1`.
    - Boundedness invariants: `overall_boundedness_invariants_held = true`.
    - Repeat consistency: `all_scenarios_auto_source_consistent = false`; `all_scenarios_auto_answer_consistent = true`.
    - Operator usefulness indicators: `control_trace_visible = true`; `auto_trace_visible_rate = 1.0`; `auto_non_empty_final_answer_rate = 1.0`.
  - Comparison reading:
    - Distribution and fallback reason remained unchanged between rounds.
    - The single fallback moved scenario location across rounds, so assisted behavior remains mixed rather than stably all-assisted.
    - Boundedness and operator-visibility indicators remained stable and strong.
    - Final-answer consistency remained stable across repeated auto attempts.
  - Decision: `narrow_follow_up`
  - Decision rationale: keep Pilot 1 isolated and continue only one narrowly scoped follow-up on reducing `ollama_plan_unusable` incidence under the same bounded controls; current evidence does not support `promotion_candidate`.

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
