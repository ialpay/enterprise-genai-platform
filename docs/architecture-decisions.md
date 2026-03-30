# Architecture Decisions

## Introduction

This document records the main architecture decisions made for the current local, enterprise-style RAG platform.

## Decision 1: Start as a local-only platform

- Decision: Build the initial system to run locally on a developer workstation.
- Context: The goal was fast iteration and a self-contained reference implementation.
- Why this choice was made: Local execution reduces setup friction and speeds feedback loops.
- Trade-offs: Flexible for development, but not enterprise-grade and lacks managed reliability.
- Future evolution: Map to managed runtime and infrastructure services in cloud environments.

## Decision 2: Use Ollama as the local model runtime

- Decision: Use Ollama for local generation and embeddings.
- Context: The system needed a local model runtime without external dependencies.
- Why this choice was made: Ollama is lightweight, easy to run locally, and integrates with simple HTTP calls.
- Trade-offs: Model selection and performance are limited compared to managed services.
- Future evolution: Replace with managed model runtimes in enterprise cloud.

## Decision 3: Use Qdrant for vector storage

- Decision: Use Qdrant for local vector storage and similarity search.
- Context: The platform needed an open-source vector database that runs locally.
- Why this choice was made: Qdrant is well-supported, easy to run in Docker, and has a simple API.
- Trade-offs: Local storage is not highly available and does not match enterprise scale.
- Future evolution: Map to managed vector/search services in cloud.

## Decision 4: Use FastAPI for the application layer

- Decision: Use FastAPI for routing, schemas, and request handling.
- Context: The API needed to be lightweight and Python-native.
- Why this choice was made: FastAPI is concise, type-friendly, and easy to operate locally.
- Trade-offs: Minimal built-in enterprise features such as auth or policy enforcement.
- Future evolution: Add enterprise middleware, auth, and observability integrations.

## Decision 5: Improve retrieval quality using heuristic stages first

- Decision: Apply query expansion, thresholding, biasing, and reranking before adding heavier models.
- Context: Retrieval needed to improve without adding high compute or dependencies.
- Why this choice was made: Heuristics are fast, transparent, and easy to tune locally.
- Trade-offs: Less powerful than model-based rerankers and may miss semantic nuance.
- Future evolution: Add model-based reranking when infrastructure permits.

## Decision 6: Introduce evaluation-driven tuning

- Decision: Add a lightweight evaluation script and question set to validate retrieval and answers.
- Context: Changes to retrieval and prompting needed objective checks.
- Why this choice was made: Evaluation provides a repeatable signal without heavy tooling.
- Trade-offs: The dataset is limited and may not cover all use cases.
- Future evolution: Expand evaluation coverage and automate in CI.

## Decision 7: Enforce governance and safety controls in code and prompt

- Decision: Use both code-level controls and prompt guidance for safety.
- Context: Prompt-only defenses are unreliable for strict refusal behavior.
- Why this choice was made: Code-level handling ensures deterministic refusal and sanitization.
- Trade-offs: Adds application logic complexity beyond simple prompt design.
- Future evolution: Centralize policy enforcement and add richer guardrails.

## Decision 8: Add operational scripts and managed logging

- Decision: Provide start/stop scripts and enforce log capture to `app.log`.
- Context: Local services need predictable startup and debugging.
- Why this choice was made: Scripts reduce setup errors and make operations repeatable.
- Trade-offs: Shell-based management is basic and not a full process supervisor.
- Future evolution: Use managed process control and centralized logging/monitoring.

## Future Evolution Summary

Local runtime and heuristic control choices are designed to evolve toward managed cloud services, stronger guardrails, model-based reranking, and centralized observability as the platform matures.
## Decision: Use protected pull requests and required checks as the default delivery path

### Decision

Treat pull requests with required repository checks as the standard path for repository changes.

### Context

The repository now includes workflow and governance structure that expects changes to be reviewed and validated through the repository process rather than through ad hoc direct edits alone.

### Why this choice was made

Using protected pull requests and required checks creates a durable control point for quality, consistency, and recovery. It also supports a clearer separation between planning, implementation, review, and repository history.

### Trade-offs

This adds process overhead compared with direct local editing, but it reduces drift, improves auditability, and makes the repository easier to operate as a long-lived engineering asset.

### Future evolution

Required checks, review gates, and branch protection rules may become stricter over time, but the baseline decision remains: repository changes should flow through a validated PR path by default.


## Decision: Separate repository work across Planner, Builder, Reviewer, Historian, Verifier, and Owner roles

### Decision

Use an explicit role split for repository work:

- Planner
- Builder
- Reviewer
- Historian
- Verifier
- Owner

### Context

The project has grown beyond a simple single-threaded build flow. Planning, implementation, review, documentation maintenance, automated verification, and final acceptance now need clearer separation to avoid confusion and accidental scope drift.

### Why this choice was made

A role split improves task quality and repository discipline.

- Planner defines or refines the next task from repository truth
- Builder implements the approved task
- Reviewer checks task scope, correctness, and missing validation
- Historian updates repository state/history documents after accepted merge
- Verifier provides objective automated pass/fail through repository checks
- Owner decides direction, acceptance, and priority

This makes the operating model more explicit and reduces reliance on informal chat memory.

### Trade-offs

This introduces more process structure than a single-agent workflow, but it improves clarity, recovery, and consistency across sessions.

### Future evolution

The exact role boundaries may be refined, but the repository should continue to treat planning, implementation, review, verification, history maintenance, and ownership as distinct responsibilities.


## Decision: Use the repository as the project’s working memory

### Decision

Treat repository documents as the authoritative working memory for project direction, current state, implementation history, workflow rules, and recovery.

### Context

Chat history alone is not stable enough to carry project truth across long-running work. The repository now contains roadmap, status, task workflow, operating model, governance, and prompt-role documents intended to preserve that truth explicitly.

### Why this choice was made

Using the repository as working memory makes the project recoverable, reviewable, and less dependent on any single conversation. It also allows future planning and implementation to begin from repository state rather than from reconstructed memory.

### Trade-offs

This requires deliberate document maintenance. If the documents are not kept aligned with repository reality, the operating model becomes misleading instead of helpful.

### Future evolution

The repository may gain stronger reconciliation and review practices over time, but the core decision remains: project memory should live in repository documents rather than in chat memory alone.


## Decision: Treat only integrated and verified behavior as the authoritative baseline

### Decision

The authoritative current baseline is defined by integrated application behavior that is visible in the active code path and supported by repository tests and workflow validation.

### Context

The repository contains advanced modules and partially staged functionality that may exist in the tree without being fully integrated into the live route flow or validated by the current test/workflow path.

### Why this choice was made

Code present in the tree does not by itself prove completed baseline functionality. Treating only integrated and verified behavior as authoritative prevents roadmap/status drift, avoids planning from aspirational code, and keeps task sequencing grounded in actual repository reality.

### Trade-offs

This can make the repository appear less mature than the amount of code present might suggest, but it produces a more honest and operationally useful baseline.

### Future evolution

As more functionality becomes integrated and verified, the authoritative baseline can advance. The rule remains the same: presence in the tree is not enough; integration and verification are required.