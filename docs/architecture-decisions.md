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
