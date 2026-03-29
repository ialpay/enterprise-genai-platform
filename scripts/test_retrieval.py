"""Simple local retrieval smoke test."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.retrieval.embeddings import EmbeddingError
from app.retrieval.retriever import Retriever

DEFAULT_QUERY = "What does the incident response runbook say about escalation?"
DEFAULT_LIMIT = 5


def main() -> None:
    query = " ".join(sys.argv[1:]).strip() or DEFAULT_QUERY
    retriever = Retriever()

    try:
        results = retriever.retrieve(query=query, limit=DEFAULT_LIMIT)
    except EmbeddingError as exc:
        print(f"Embedding failed: {exc}")
        raise SystemExit(1) from exc
    except Exception as exc:
        print(f"Retrieval failed: {exc}")
        raise SystemExit(1) from exc

    print(f"Query: {query}")
    print(f"Matches returned: {len(results)}")

    for index, result in enumerate(results, start=1):
        print(f"\nMatch {index}")
        print(f"Score: {result.score}")
        print(f"Source: {result.source_type}/{result.source_file}")
        print(f"Chunk: {result.chunk_index}")
        print(f"Text: {result.text[:300]}")


if __name__ == "__main__":
    main()
