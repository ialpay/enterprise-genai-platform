"""Basic API tests for the FastAPI routes."""

import pytest
from fastapi import HTTPException

from app.api import routes
from app.api.schemas import AskRequest
from app.ai.llm_client import OllamaClientError
from app.retrieval.retriever import RetrievalResult


def test_health_returns_ok() -> None:
    assert routes.health() == {"status": "ok"}


class DummyRetriever:
    def __init__(self, results: list[RetrievalResult]) -> None:
        self._results = results

    def retrieve(self, query: str, limit: int = 5) -> list[RetrievalResult]:
        return self._results


def test_ask_returns_rag_response(monkeypatch) -> None:
    results = [
        RetrievalResult(
            text="sample context",
            source_file="doc.md",
            source_type="internal_docs",
            chunk_index=0,
            score=0.9,
        )
    ]
    monkeypatch.setattr(routes, "Retriever", lambda: DummyRetriever(results))
    monkeypatch.setattr(routes, "generate_answer", lambda prompt: "mock answer")
    response = routes.ask(AskRequest(question="hello"))
    assert response.question == "hello"
    assert response.answer == "mock answer"
    assert response.source == "rag"


def test_ask_returns_insufficient_when_no_context(monkeypatch) -> None:
    monkeypatch.setattr(routes, "Retriever", lambda: DummyRetriever([]))
    monkeypatch.setattr(
        routes,
        "generate_answer",
        lambda prompt: (_ for _ in ()).throw(AssertionError("should not call Ollama")),
    )
    response = routes.ask(AskRequest(question="hello"))
    assert response.answer == "insufficient information"
    assert response.source == "rag"


def test_ask_returns_502_when_ollama_unavailable(monkeypatch) -> None:
    results = [
        RetrievalResult(
            text="sample context",
            source_file="doc.md",
            source_type="internal_docs",
            chunk_index=0,
            score=0.9,
        )
    ]
    monkeypatch.setattr(routes, "Retriever", lambda: DummyRetriever(results))

    def fail(prompt: str) -> str:
        raise OllamaClientError("boom")

    monkeypatch.setattr(routes, "generate_answer", fail)

    with pytest.raises(HTTPException) as exc:
        routes.ask(AskRequest(question="hello"))

    assert exc.value.status_code == 502
    assert exc.value.detail == "Ollama service unavailable."


def test_ask_returns_502_when_retrieval_fails(monkeypatch) -> None:
    class FailingRetriever:
        def retrieve(self, query: str, limit: int = 5) -> list[RetrievalResult]:
            raise RuntimeError("boom")

    monkeypatch.setattr(routes, "Retriever", lambda: FailingRetriever())

    with pytest.raises(HTTPException) as exc:
        routes.ask(AskRequest(question="hello"))

    assert exc.value.status_code == 502
    assert exc.value.detail == "Retrieval failed."
