"""Basic API tests for the FastAPI routes."""

import pytest
from fastapi import HTTPException

from app.api import routes
from app.api.schemas import AskRequest
from app.ai.llm_client import OllamaClientError


def test_health_returns_ok() -> None:
    assert routes.health() == {"status": "ok"}


def test_ask_returns_ollama_response(monkeypatch) -> None:
    monkeypatch.setattr(routes, "generate_answer", lambda prompt: "mock answer")
    response = routes.ask(AskRequest(question="hello"))
    assert response.question == "hello"
    assert response.answer == "mock answer"
    assert response.source == "ollama"

def test_ask_returns_502_when_ollama_unavailable(monkeypatch) -> None:
    def fail(prompt: str) -> str:
        raise OllamaClientError("boom")

    monkeypatch.setattr(routes, "generate_answer", fail)

    with pytest.raises(HTTPException) as exc:
        routes.ask(AskRequest(question="hello"))

    assert exc.value.status_code == 502
    assert exc.value.detail == "Ollama service unavailable."
