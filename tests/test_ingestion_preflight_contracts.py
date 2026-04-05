"""Deterministic contract checks for ingestion/retrieval preflight behavior."""

from __future__ import annotations

import argparse
import json
from types import SimpleNamespace

import pytest

from app.ingestion.chunking import TextChunk
from app.ingestion.loaders import SourceDocument
from app.retrieval import embeddings as embeddings_module
from app.retrieval.embeddings import EmbeddingError, OllamaEmbeddingGenerator
from scripts import ingest_documents


class _FakeResponse:
    def __init__(self, payload: dict[str, object]) -> None:
        self._payload = payload

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


class _EmbeddingGeneratorDouble:
    def __init__(self, state: dict[str, object], vector_size: int) -> None:
        self._state = state
        self._vector_size = vector_size
        self.model_name = "nomic-embed-text"

    def ensure_model_available(self) -> None:
        self._state["ensure_model_available_calls"] += 1

    def embed_text(self, text: str) -> list[float]:
        self._state["embed_text_calls"].append(text)
        return [0.1] * self._vector_size


class _VectorStoreDouble:
    def __init__(
        self,
        state: dict[str, object],
        *,
        collection_name: str,
        collection_vector_size: int | None,
    ) -> None:
        self._state = state
        self.collection_name = collection_name
        self._collection_vector_size = collection_vector_size

    def get_collection_vector_size(self) -> int | None:
        self._state["get_collection_vector_size_calls"] += 1
        return self._collection_vector_size

    def ensure_collection(self, vector_size: int) -> None:
        self._state["ensure_collection_calls"].append(vector_size)

    def recreate_collection(self, vector_size: int) -> None:
        self._state["recreate_collection_calls"].append(vector_size)

    def upsert_chunks(
        self,
        chunks: list[TextChunk],
        vectors: list[list[float]],
        batch_size: int,
        progress_callback,
    ) -> None:
        self._state["upsert_calls"] += 1
        self._state["upsert_chunks_count"] = len(chunks)
        self._state["upsert_vector_size"] = len(vectors[0])
        self._state["upsert_batch_size"] = batch_size


def _install_main_doubles(
    monkeypatch,
    *,
    recreate_collection: bool,
    embedding_vector_size: int,
    collection_vector_size: int | None,
) -> dict[str, object]:
    state: dict[str, object] = {
        "ensure_model_available_calls": 0,
        "embed_text_calls": [],
        "get_collection_vector_size_calls": 0,
        "ensure_collection_calls": [],
        "recreate_collection_calls": [],
        "embed_chunk_with_retry_calls": 0,
        "upsert_calls": 0,
        "upsert_chunks_count": 0,
        "upsert_vector_size": 0,
        "upsert_batch_size": 0,
    }

    documents = [
        SourceDocument(
            text="example text",
            source_file="example.md",
            source_type="internal_docs",
        )
    ]
    chunks = [
        TextChunk(
            text="example chunk",
            source_file="example.md",
            source_type="internal_docs",
            chunk_index=0,
        )
    ]

    monkeypatch.setattr(
        ingest_documents,
        "parse_args",
        lambda: argparse.Namespace(
            chunk_size=500,
            chunk_overlap=50,
            dry_run=False,
            recreate_collection=recreate_collection,
        ),
    )
    monkeypatch.setattr(ingest_documents, "load_tracked_documents", lambda _raw_dir: documents)
    monkeypatch.setattr(
        ingest_documents,
        "chunk_documents",
        lambda _documents, chunk_size, chunk_overlap: chunks,
    )

    def _embedding_generator_factory() -> _EmbeddingGeneratorDouble:
        return _EmbeddingGeneratorDouble(state=state, vector_size=embedding_vector_size)

    def _vector_store_factory() -> _VectorStoreDouble:
        return _VectorStoreDouble(
            state=state,
            collection_name="enterprise_docs",
            collection_vector_size=collection_vector_size,
        )

    def _embed_chunk_with_retry(
        embedding_generator,
        index: int,
        total_chunks: int,
        chunk: TextChunk,
    ) -> list[tuple[TextChunk, list[float]]]:
        del embedding_generator, index, total_chunks
        state["embed_chunk_with_retry_calls"] += 1
        return [(chunk, [0.2] * embedding_vector_size)]

    monkeypatch.setattr(ingest_documents, "OllamaEmbeddingGenerator", _embedding_generator_factory)
    monkeypatch.setattr(ingest_documents, "QdrantVectorStore", _vector_store_factory)
    monkeypatch.setattr(ingest_documents, "embed_chunk_with_retry", _embed_chunk_with_retry)

    return state


def test_ensure_model_available_raises_for_missing_embedding_model(monkeypatch) -> None:
    monkeypatch.setattr(
        embeddings_module,
        "get_settings",
        lambda: SimpleNamespace(
            ollama_base_url="http://unit-test-ollama:11434",
            embedding_model="nomic-embed-text",
        ),
    )
    monkeypatch.setattr(
        embeddings_module.request,
        "urlopen",
        lambda _req, timeout=30: _FakeResponse(payload={"models": [{"name": "llama3.2:3b"}]}),
    )

    generator = OllamaEmbeddingGenerator()

    with pytest.raises(EmbeddingError) as exc_info:
        generator.ensure_model_available()

    message = str(exc_info.value)
    assert "nomic-embed-text" in message
    assert "not installed or unavailable" in message
    assert "ollama pull nomic-embed-text" in message
    assert "EMBEDDING_MODEL" in message


def test_ensure_model_available_accepts_installed_embedding_model(monkeypatch) -> None:
    monkeypatch.setattr(
        embeddings_module,
        "get_settings",
        lambda: SimpleNamespace(
            ollama_base_url="http://unit-test-ollama:11434",
            embedding_model="nomic-embed-text",
        ),
    )
    monkeypatch.setattr(
        embeddings_module.request,
        "urlopen",
        lambda _req, timeout=30: _FakeResponse(
            payload={"models": [{"name": "nomic-embed-text:latest"}]}
        ),
    )

    generator = OllamaEmbeddingGenerator()

    generator.ensure_model_available()


def test_ingestion_preflight_collection_vector_size_match(monkeypatch) -> None:
    state = _install_main_doubles(
        monkeypatch,
        recreate_collection=False,
        embedding_vector_size=768,
        collection_vector_size=768,
    )

    ingest_documents.main()

    assert state["ensure_model_available_calls"] == 1
    assert state["embed_text_calls"] == [ingest_documents.VECTOR_SIZE_PREFLIGHT_PROBE_TEXT]
    assert state["get_collection_vector_size_calls"] == 1
    assert state["recreate_collection_calls"] == []
    assert state["embed_chunk_with_retry_calls"] == 1
    assert state["upsert_calls"] == 1
    assert state["upsert_vector_size"] == 768


def test_ingestion_preflight_collection_vector_size_mismatch(monkeypatch, capsys) -> None:
    state = _install_main_doubles(
        monkeypatch,
        recreate_collection=False,
        embedding_vector_size=768,
        collection_vector_size=1024,
    )

    with pytest.raises(SystemExit) as exc_info:
        ingest_documents.main()

    assert exc_info.value.code == 1
    assert state["embed_chunk_with_retry_calls"] == 0
    assert state["upsert_calls"] == 0

    output = capsys.readouterr().out
    assert "enterprise_docs" in output
    assert "existing collection size is 1024" in output
    assert "embedding vector size is 768" in output
    assert "--recreate-collection" in output


def test_ingestion_preflight_recreate_path_is_explicit_and_gated(monkeypatch) -> None:
    state = _install_main_doubles(
        monkeypatch,
        recreate_collection=True,
        embedding_vector_size=768,
        collection_vector_size=1024,
    )

    ingest_documents.main()

    assert state["recreate_collection_calls"] == [768]
    assert state["embed_chunk_with_retry_calls"] == 1
    assert state["upsert_calls"] == 1
