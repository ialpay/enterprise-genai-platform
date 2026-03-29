"""Qdrant vector storage helpers."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, QueryResponse, VectorParams

from app.core.config import get_settings
from app.ingestion.chunking import TextChunk


@dataclass(frozen=True)
class QdrantSearchResult:
    text: str
    source_file: str
    source_type: str
    chunk_index: int
    score: float | None = None


class QdrantVectorStore:
    def __init__(self) -> None:
        settings = get_settings()
        self._collection_name = settings.qdrant_collection
        self._client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)

    def ensure_collection(self, vector_size: int) -> None:
        try:
            self._client.get_collection(self._collection_name)
            return
        except Exception:
            pass

        self._client.create_collection(
            collection_name=self._collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )

    def upsert_chunks(
        self,
        chunks: list[TextChunk],
        vectors: list[list[float]],
        batch_size: int = 50,
        progress_callback: Callable[[int, int, int], None] | None = None,
    ) -> None:
        if len(chunks) != len(vectors):
            raise ValueError("chunks and vectors must have the same length")
        if batch_size <= 0:
            raise ValueError("batch_size must be > 0")

        total = len(chunks)
        for start in range(0, total, batch_size):
            end = min(start + batch_size, total)
            points: list[PointStruct] = []
            for chunk, vector in zip(chunks[start:end], vectors[start:end]):
                points.append(
                    PointStruct(
                        id=str(uuid4()),
                        vector=vector,
                        payload={
                            "text": chunk.text,
                            "source_file": chunk.source_file,
                            "source_type": chunk.source_type,
                            "chunk_index": chunk.chunk_index,
                        },
                    )
                )
            if points:
                self._client.upsert(collection_name=self._collection_name, points=points)
                if progress_callback is not None:
                    batch_number = (start // batch_size) + 1
                    total_batches = (total + batch_size - 1) // batch_size
                    progress_callback(batch_number, total_batches, len(points))

    def search(self, query_vector: list[float], limit: int = 5) -> list[QdrantSearchResult]:
        if not query_vector:
            raise ValueError("query_vector must not be empty")
        if limit <= 0:
            raise ValueError("limit must be > 0")

        response = self._client.query_points(
            collection_name=self._collection_name,
            query=query_vector,
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )
        return self._parse_search_response(response)

    @staticmethod
    def _parse_search_response(response: QueryResponse) -> list[QdrantSearchResult]:
        results: list[QdrantSearchResult] = []
        for point in response.points:
            payload = point.payload or {}
            chunk_index = payload.get("chunk_index")
            if not isinstance(chunk_index, int):
                try:
                    chunk_index = int(chunk_index)
                except (TypeError, ValueError):
                    chunk_index = -1

            results.append(
                QdrantSearchResult(
                    text=str(payload.get("text", "")),
                    source_file=str(payload.get("source_file", "")),
                    source_type=str(payload.get("source_type", "")),
                    chunk_index=chunk_index,
                    score=float(point.score) if point.score is not None else None,
                )
            )
        return results
