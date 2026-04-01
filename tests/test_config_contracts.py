"""Deterministic contract checks for application settings."""

import pytest

from app.core import config


@pytest.fixture(autouse=True)
def _clear_settings_cache() -> None:
    config.get_settings.cache_clear()
    yield
    config.get_settings.cache_clear()


def test_get_settings_defaults_match_baseline(monkeypatch) -> None:
    for key in (
        "APP_NAME",
        "APP_ENV",
        "APP_HOST",
        "APP_PORT",
        "OLLAMA_BASE_URL",
        "OLLAMA_MODEL",
        "EMBEDDING_MODEL",
        "QDRANT_HOST",
        "QDRANT_PORT",
        "QDRANT_COLLECTION",
    ):
        monkeypatch.delenv(key, raising=False)

    settings = config.get_settings()

    assert settings.app_name == "enterprise-genai-platform"
    assert settings.app_env == "local"
    assert settings.app_host == "0.0.0.0"
    assert settings.app_port == 8000
    assert settings.ollama_base_url == "http://localhost:11434"
    assert settings.ollama_model == "llama3.2:3b"
    assert settings.embedding_model == "nomic-embed-text"
    assert settings.qdrant_host == "localhost"
    assert settings.qdrant_port == 6333
    assert settings.qdrant_collection == "enterprise_docs"


def test_get_settings_reads_env_once_and_keeps_cached_instance(monkeypatch) -> None:
    monkeypatch.setenv("APP_PORT", "9001")
    monkeypatch.setenv("OLLAMA_MODEL", "custom-model")

    first = config.get_settings()
    assert first.app_port == 9001
    assert first.ollama_model == "custom-model"

    monkeypatch.setenv("APP_PORT", "9999")
    second = config.get_settings()

    assert second is first
    assert second.app_port == 9001
