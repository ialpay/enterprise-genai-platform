# Architecture Overview

## Project Name
Enterprise GenAI Platform

## Goal
Build a reference enterprise-style GenAI platform that demonstrates:

- local AI runtime using Ollama
- vector retrieval using Qdrant
- FastAPI application layer
- deterministic orchestration
- governance and safety controls
- later AWS deployment using Bedrock and OpenSearch

## Initial Scope
The first implementation is local-only and runs on a MacBook.

Current local stack:

- Ollama running natively on macOS
- Qdrant running in Docker
- FastAPI application running locally
- Python application code in the `app` folder

## Architecture Layers

### 1. Infrastructure Layer
- local MacBook runtime
- Docker container for Qdrant
- local Ollama service

### 2. Application Layer
- FastAPI app entry point
- API routes
- request/response schemas
- config and logging

### 3. AI Layer
- document ingestion
- embeddings
- retrieval
- RAG answer generation

### 4. Orchestration Layer
- deterministic request routing
- later optional agent workflow

### 5. Governance Layer
- input validation
- access control
- audit logging
- output controls

## Current Phase
Current phase is application bootstrap only.

We are NOT implementing RAG yet.
We are NOT implementing AWS deployment yet.
We are only building the initial FastAPI application shell.
