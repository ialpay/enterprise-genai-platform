"""Embedding generation for ingestion."""

from __future__ import annotations

import json
from urllib import error, request

from app.core.config import get_settings


class EmbeddingError(Exception):
    """Raised when embedding generation fails."""


class EmbeddingGenerator:
    def embed_text(self, text: str) -> list[float]:
        raise NotImplementedError

    def embed_query(self, query: str) -> list[float]:
        return self.embed_text(query)


class OllamaEmbeddingGenerator(EmbeddingGenerator):
    """Minimal Ollama embedding client."""

    def __init__(self) -> None:
        self._settings = get_settings()
        self._endpoint = f"{self._settings.ollama_base_url.rstrip('/')}/api/embeddings"
        self._tags_endpoint = f"{self._settings.ollama_base_url.rstrip('/')}/api/tags"
        self._model = self._settings.embedding_model

    @property
    def model_name(self) -> str:
        return self._model

    def ensure_model_available(self) -> None:
        req = request.Request(self._tags_endpoint, method="GET")
        try:
            with request.urlopen(req, timeout=30) as response:
                body = response.read().decode("utf-8")
        except error.HTTPError as exc:
            response_body = exc.read().decode("utf-8", errors="replace").strip()
            raise EmbeddingError(
                f"Failed to check local Ollama models while validating embedding model "
                f"'{self._model}' (HTTP {exc.code}): {response_body or exc.reason}"
            ) from exc
        except error.URLError as exc:
            raise EmbeddingError(
                f"Failed to connect to local Ollama runtime while validating embedding model "
                f"'{self._model}': {exc.reason}"
            ) from exc

        try:
            parsed = json.loads(body)
        except json.JSONDecodeError as exc:
            raise EmbeddingError(
                f"Received invalid Ollama model listing while validating embedding model "
                f"'{self._model}'."
            ) from exc

        models = parsed.get("models")
        if not isinstance(models, list):
            raise EmbeddingError(
                f"Ollama model listing was not in the expected format while validating "
                f"embedding model '{self._model}'."
            )

        installed_models: list[str] = []
        for model in models:
            if not isinstance(model, dict):
                continue
            model_name = model.get("name") or model.get("model")
            if isinstance(model_name, str) and model_name.strip():
                installed_models.append(model_name.strip())

        configured_model = self._model.strip()
        configured_model_lower = configured_model.lower()
        configured_base = configured_model_lower.split(":", maxsplit=1)[0]

        for installed_model in installed_models:
            installed_lower = installed_model.lower()
            installed_base = installed_lower.split(":", maxsplit=1)[0]
            if installed_lower == configured_model_lower:
                return
            if ":" not in configured_model_lower and installed_base == configured_model_lower:
                return
            if configured_model_lower.endswith(":latest") and installed_base == configured_base:
                return

        raise EmbeddingError(
            f"Configured embedding model '{self._model}' is not installed or unavailable "
            f"in local Ollama runtime. Run `ollama pull {self._model}` or set "
            f"EMBEDDING_MODEL to an installed embedding model."
        )

    def embed_text(self, text: str) -> list[float]:
        payload = {
            "model": self._model,
            "prompt": text,
        }

        data = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        req = request.Request(self._endpoint, data=data, headers=headers, method="POST")

        try:
            with request.urlopen(req, timeout=60) as response:
                body = response.read().decode("utf-8")
        except error.HTTPError as exc:
            response_body = exc.read().decode("utf-8", errors="replace").strip()
            if exc.code == 500:
                raise EmbeddingError(
                    f"Ollama embeddings API returned HTTP 500 for model "
                    f"'{self._model}': {response_body or 'empty response body'}"
                ) from exc
            raise EmbeddingError(
                f"Ollama embeddings API returned HTTP {exc.code} for model "
                f"'{self._model}': {response_body or exc.reason}"
            ) from exc
        except error.URLError as exc:
            raise EmbeddingError(
                f"Failed to connect to Ollama embeddings API for model "
                f"'{self._model}': {exc.reason}"
            ) from exc

        try:
            parsed = json.loads(body)
        except json.JSONDecodeError as exc:
            raise EmbeddingError(
                f"Received invalid embedding response for model '{self._model}'."
            ) from exc

        embedding = parsed.get("embedding")
        if not isinstance(embedding, list) or not embedding:
            raise EmbeddingError(
                f"Embedding response for model '{self._model}' did not contain a valid vector."
            )

        return [float(value) for value in embedding]
