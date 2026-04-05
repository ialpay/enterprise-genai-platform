"""Deterministic retrieval helper contract checks with local doubles."""

from collections import Counter

from app.retrieval.retriever import (
    MAX_RETURNED_CHUNKS,
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


def test_retriever_prefers_policy_source_and_suppresses_non_preferred() -> None:
    embedding_double = _EmbeddingDouble()
    vector_store_double = _VectorStoreDouble(
        matches=[
            QdrantSearchResult(
                text="AWS security guidance text.",
                source_file="aws_security.md",
                source_type="aws_docs",
                chunk_index=0,
                score=0.90,
            ),
            QdrantSearchResult(
                text="Higher-scoring non-AWS text.",
                source_file="internal_runbook.md",
                source_type="internal_docs",
                chunk_index=0,
                score=0.96,
            ),
            QdrantSearchResult(
                text="NIST companion text.",
                source_file="nist_profile.pdf",
                source_type="nist_docs",
                chunk_index=0,
                score=0.87,
            ),
        ]
    )
    retriever = Retriever(
        embedding_generator=embedding_double, vector_store=vector_store_double
    )

    results = retriever.retrieve("Need AWS security pillar guidance", limit=5)

    assert [result.source_type for result in results] == ["aws_docs"]
    assert results[0].source_file == "aws_security.md"


def test_retriever_reranks_by_query_token_overlap() -> None:
    embedding_double = _EmbeddingDouble()
    vector_store_double = _VectorStoreDouble(
        matches=[
            QdrantSearchResult(
                text="General advisory content without matching tokens.",
                source_file="advisory.md",
                source_type="internal_docs",
                chunk_index=0,
                score=0.90,
            ),
            QdrantSearchResult(
                text="Incident response runbook procedures for severe incidents.",
                source_file="runbook.md",
                source_type="internal_docs",
                chunk_index=1,
                score=0.80,
            ),
        ]
    )
    retriever = Retriever(
        embedding_generator=embedding_double, vector_store=vector_store_double
    )

    results = retriever.retrieve("incident response runbook", limit=5)

    assert [result.source_file for result in results] == [
        "runbook.md",
        "advisory.md",
    ]
    assert results[0].score == 0.80
    assert results[1].score == 0.90


def test_retriever_applies_best_document_bias_and_per_document_caps() -> None:
    embedding_double = _EmbeddingDouble()
    vector_store_double = _VectorStoreDouble(
        matches=[
            QdrantSearchResult(
                text="deterministic retrieval coverage text",
                source_file="best_doc.md",
                source_type="internal_docs",
                chunk_index=0,
                score=0.95,
            ),
            QdrantSearchResult(
                text="deterministic retrieval coverage text",
                source_file="best_doc.md",
                source_type="internal_docs",
                chunk_index=1,
                score=0.94,
            ),
            QdrantSearchResult(
                text="deterministic retrieval coverage text",
                source_file="best_doc.md",
                source_type="internal_docs",
                chunk_index=2,
                score=0.93,
            ),
            QdrantSearchResult(
                text="deterministic retrieval coverage text",
                source_file="best_doc.md",
                source_type="internal_docs",
                chunk_index=3,
                score=0.92,
            ),
            QdrantSearchResult(
                text="deterministic retrieval coverage text",
                source_file="other_doc_a.md",
                source_type="internal_docs",
                chunk_index=0,
                score=0.91,
            ),
            QdrantSearchResult(
                text="deterministic retrieval coverage text",
                source_file="other_doc_b.md",
                source_type="internal_docs",
                chunk_index=0,
                score=0.90,
            ),
        ]
    )
    retriever = Retriever(
        embedding_generator=embedding_double, vector_store=vector_store_double
    )

    results = retriever.retrieve("deterministic retrieval coverage", limit=5)
    counts = Counter(result.source_file for result in results)

    assert len(results) == 5
    assert counts["best_doc.md"] == 3
    assert counts["other_doc_a.md"] == 1
    assert counts["other_doc_b.md"] == 1
    assert (("best_doc.md", 3)) not in {
        (result.source_file, result.chunk_index) for result in results
    }


def test_retriever_returns_empty_when_all_matches_are_below_threshold_or_none() -> None:
    embedding_double = _EmbeddingDouble()
    vector_store_double = _VectorStoreDouble(
        matches=[
            QdrantSearchResult(
                text="No score match",
                source_file="none_score.md",
                source_type="internal_docs",
                chunk_index=0,
                score=None,
            ),
            QdrantSearchResult(
                text="Below threshold match",
                source_file="low_score.md",
                source_type="aws_docs",
                chunk_index=0,
                score=0.54,
            ),
        ]
    )
    retriever = Retriever(
        embedding_generator=embedding_double, vector_store=vector_store_double
    )

    results = retriever.retrieve("general capability question", limit=5)

    assert results == []


def test_compare_matches_prefers_filename_keyword_when_scores_are_close() -> None:
    source_priority = {"internal_docs": 3}
    left = QdrantSearchResult(
        text="left",
        source_file="team_playbook.md",
        source_type="internal_docs",
        chunk_index=0,
        score=0.80,
    )
    right = QdrantSearchResult(
        text="right",
        source_file="general_notes.md",
        source_type="internal_docs",
        chunk_index=0,
        score=0.81,
    )

    assert (
        Retriever._compare_matches(
            left,
            right,
            source_priority=source_priority,
            filename_keyword="playbook",
        )
        == -1
    )
    assert (
        Retriever._compare_matches(
            right,
            left,
            source_priority=source_priority,
            filename_keyword="playbook",
        )
        == 1
    )


def test_retriever_respects_caller_limit_below_max_returned_chunks() -> None:
    embedding_double = _EmbeddingDouble()
    vector_store_double = _VectorStoreDouble(
        matches=[
            QdrantSearchResult(
                text="general retrieval guidance",
                source_file=f"doc_{index}.md",
                source_type="internal_docs",
                chunk_index=0,
                score=0.95 - (index * 0.01),
            )
            for index in range(6)
        ]
    )
    retriever = Retriever(
        embedding_generator=embedding_double, vector_store=vector_store_double
    )

    results = retriever.retrieve("general guidance", limit=2)

    assert len(results) == 2
    assert [result.source_file for result in results] == ["doc_0.md", "doc_1.md"]


def test_retriever_caps_results_at_max_returned_chunks_when_limit_is_higher() -> None:
    embedding_double = _EmbeddingDouble()
    vector_store_double = _VectorStoreDouble(
        matches=[
            QdrantSearchResult(
                text="general retrieval guidance",
                source_file=f"doc_{index}.md",
                source_type="internal_docs",
                chunk_index=0,
                score=0.95 - (index * 0.01),
            )
            for index in range(8)
        ]
    )
    retriever = Retriever(
        embedding_generator=embedding_double, vector_store=vector_store_double
    )

    results = retriever.retrieve("general guidance", limit=MAX_RETURNED_CHUNKS + 3)

    assert len(results) == MAX_RETURNED_CHUNKS
