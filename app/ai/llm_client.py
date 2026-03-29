"""Minimal Ollama client using standard Python HTTP utilities."""

from __future__ import annotations

import json
from urllib import error, request

from app.core.config import get_settings


class OllamaClientError(Exception):
    """Raised when the Ollama request fails."""


def generate_answer(prompt: str) -> str:
    settings = get_settings()
    endpoint = f"{settings.ollama_base_url.rstrip('/')}/api/generate"
    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
    }
    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    req = request.Request(endpoint, data=data, headers=headers, method="POST")

    try:
        with request.urlopen(req, timeout=30) as response:
            body = response.read().decode("utf-8")
    except error.URLError as exc:
        raise OllamaClientError("Failed to connect to Ollama.") from exc

    try:
        parsed = json.loads(body)
    except json.JSONDecodeError as exc:
        raise OllamaClientError("Received invalid response from Ollama.") from exc

    answer = parsed.get("response")
    if not isinstance(answer, str) or not answer.strip():
        raise OllamaClientError("Ollama returned an empty response.")

    return answer.strip()
