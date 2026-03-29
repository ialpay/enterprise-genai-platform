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
        self._model = self._settings.embedding_model

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
