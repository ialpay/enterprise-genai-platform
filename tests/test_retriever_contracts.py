"""Deterministic retrieval helper contract checks with local doubles."""

from app.retrieval.retriever import (
    TOP_K_SEARCH,
    Retriever,
    detect_filename_keyword,
    detect_policy,
    expand_query,
)
from app.retrieval.vector_store import QdrantSearchResult


class _EmbeddingDouble:
    def __init__(self) -> None:
        self.queries: list[str] = []

    def embed_query(self, query: str) -> list[float]:
        self.queries.append(query)
        return [0.11, 0.22, 0.33]


class _VectorStoreDouble:
    def __init__(self, matches: list[QdrantSearchResult]) -> None:
        self.matches = matches
        self.calls: list[tuple[list[float], int]] = []

    def search(self, query_vector: list[float], limit: int = 5) -> list[QdrantSearchResult]:
        self.calls.append((query_vector, limit))
        return list(self.matches)


def test_retriever_retrieve_uses_expanded_query_and_filters_low_scores() -> None:
    embedding_double = _EmbeddingDouble()
    vector_store_double = _VectorStoreDouble(
        matches=[
            QdrantSearchResult(
                text="The playbook requires deterministic checks in CI.",
                source_file="team_playbook.md",
                source_type="internal_docs",
                chunk_index=2,
                score=0.88,
            ),
            QdrantSearchResult(
                text="Low-confidence text.",
                source_file="noise.md",
                source_type="aws_docs",
                chunk_index=1,
                score=0.20,
            ),
        ]
    )
    retriever = Retriever(
        embedding_generator=embedding_double, vector_store=vector_store_double
    )

    results = retriever.retrieve("Summarize the playbook requirements", limit=5)

    assert embedding_double.queries == [
        expand_query("Summarize the playbook requirements")
    ]
    assert vector_store_double.calls == [([0.11, 0.22, 0.33], TOP_K_SEARCH)]
    assert len(results) == 1
    assert results[0].source_file == "team_playbook.md"
    assert results[0].score == 0.88


def test_detect_policy_returns_expected_priorities() -> None:
    assert detect_policy("Need AWS security pillar guidance") == "AWS_FIRST"
    assert detect_policy("What does the NIST playbook require?") == "NIST_FIRST"
    assert detect_policy("internal runbook incident process") == "INTERNAL_FIRST"
    assert detect_policy("general capability question") == "DEFAULT"


def test_filename_keyword_detection_and_query_expansion() -> None:
    query = "Compare PLAYBOOK and profile references"
    assert detect_filename_keyword(query) == "playbook"
    assert "tactical actions companion resource" in expand_query(query)

    plain_query = "No keyword here"
    assert detect_filename_keyword(plain_query) is None
    assert expand_query(plain_query) == plain_query
