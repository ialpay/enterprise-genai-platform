"""Basic API tests for the placeholder FastAPI routes."""

from app.api.routes import ask, health
from app.api.schemas import AskRequest


def test_health_returns_ok() -> None:
    assert health() == {"status": "ok"}


def test_ask_returns_placeholder_response() -> None:
    response = ask(AskRequest(question="hello"))
    assert response.answer == "This is a placeholder response."
