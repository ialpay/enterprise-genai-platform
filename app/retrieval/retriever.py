"""Retrieval helpers for query-to-Qdrant search."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from functools import cmp_to_key
import re

from app.retrieval.embeddings import EmbeddingGenerator, OllamaEmbeddingGenerator
from app.retrieval.vector_store import QdrantSearchResult, QdrantVectorStore

TOP_K_SEARCH = 10
SIMILARITY_THRESHOLD = 0.55
MAX_CHUNKS_FROM_BEST_DOCUMENT = 3
MAX_CHUNKS_FROM_OTHER_DOCUMENTS = 1
MAX_RETURNED_CHUNKS = 5
CLOSE_SCORE_DELTA = 0.02
SUPPRESSION_SCORE_DELTA = 0.015
POLICY_SOURCE_PRIORITY = {
    "DEFAULT": {
        "internal_docs": 3,
        "aws_docs": 2,
        "nist_docs": 1,
    },
    "INTERNAL_FIRST": {
        "internal_docs": 4,
        "aws_docs": 2,
        "nist_docs": 1,
    },
    "AWS_FIRST": {
        "aws_docs": 4,
        "internal_docs": 2,
        "nist_docs": 1,
    },
    "NIST_FIRST": {
        "nist_docs": 4,
        "aws_docs": 2,
        "internal_docs": 1,
    },
}
FILENAME_KEYWORDS = ("playbook", "profile", "framework", "pillar")
QUERY_EXPANSIONS = {
    "playbook": "playbook tactical actions companion resource",
    "profile": "profile companion resource generative ai",
    "framework": "framework risk management guidance",
    "pillar": "pillar well-architected guidance",
}
MIN_RERANK_TOKEN_LENGTH = 3


def detect_policy(query: str) -> str:
    lowered = query.lower()
    if any(term in lowered for term in ("aws", "well-architected", "security pillar")):
        return "AWS_FIRST"
    if any(term in lowered for term in ("nist", "rmf", "governance", "playbook")):
        return "NIST_FIRST"
    if any(term in lowered for term in ("policy", "runbook", "incident", "internal")):
        return "INTERNAL_FIRST"
    return "DEFAULT"


def detect_filename_keyword(query: str) -> str | None:
    lowered = query.lower()
    for keyword in FILENAME_KEYWORDS:
        if keyword in lowered:
            return keyword
    return None


def expand_query(query: str) -> str:
    lowered = query.lower()
    for keyword in FILENAME_KEYWORDS:
        if keyword in lowered:
            return f"{query} {QUERY_EXPANSIONS[keyword]}"
    return query


def normalize_text(text: str) -> str:
    cleaned = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    return re.sub(r"\s+", " ", cleaned).strip()


def tokenize(text: str) -> set[str]:
    normalized = normalize_text(text)
    return {token for token in normalized.split() if len(token) >= MIN_RERANK_TOKEN_LENGTH}


@dataclass(frozen=True)
class RetrievalResult:
    text: str
    source_file: str
    source_type: str
    chunk_index: int
    score: float | None = None


class Retriever:
    """Minimal retrieval layer for semantic search."""

    def __init__(
        self,
        embedding_generator: EmbeddingGenerator | None = None,
        vector_store: QdrantVectorStore | None = None,
    ) -> None:
        self._embedding_generator = embedding_generator or OllamaEmbeddingGenerator()
        self._vector_store = vector_store or QdrantVectorStore()

    def retrieve(self, query: str, limit: int = 5) -> list[RetrievalResult]:
        expanded_query = expand_query(query)
        query_embedding = self._embedding_generator.embed_query(expanded_query)
        matches = self._vector_store.search(
            query_vector=query_embedding,
            limit=TOP_K_SEARCH,
        )
        filtered_matches = self._filter_matches(
            matches=matches,
            limit=limit,
            query=query,
        )
        return [self._to_result(match) for match in filtered_matches]

    @staticmethod
    def _to_result(match: QdrantSearchResult) -> RetrievalResult:
        return RetrievalResult(
            text=match.text,
            source_file=match.source_file,
            source_type=match.source_type,
            chunk_index=match.chunk_index,
            score=match.score,
        )

    @staticmethod
    def _filter_matches(
        matches: list[QdrantSearchResult],
        limit: int,
        query: str,
    ) -> list[QdrantSearchResult]:
        filtered_results: list[QdrantSearchResult] = []
        document_counts: dict[str, int] = defaultdict(int)
        final_limit = min(limit, MAX_RETURNED_CHUNKS)
        policy = detect_policy(query)
        filename_keyword = detect_filename_keyword(query)
        source_priority = POLICY_SOURCE_PRIORITY.get(
            policy,
            POLICY_SOURCE_PRIORITY["DEFAULT"],
        )
        thresholded_matches = [
            match
            for match in matches
            if match.score is not None and match.score >= SIMILARITY_THRESHOLD
        ]

        if not thresholded_matches:
            return filtered_results

        preferred_source_type = None
        if policy == "AWS_FIRST":
            preferred_source_type = "aws_docs"
        elif policy == "NIST_FIRST":
            preferred_source_type = "nist_docs"

        if preferred_source_type:
            preferred_matches = [
                match
                for match in thresholded_matches
                if match.source_type == preferred_source_type
            ]
            if preferred_matches:
                best_preferred_score = max(
                    match.score if match.score is not None else float("-inf")
                    for match in preferred_matches
                )
                thresholded_matches = [
                    match
                    for match in thresholded_matches
                    if match.source_type == preferred_source_type
                    or abs((match.score or 0.0) - best_preferred_score)
                    < SUPPRESSION_SCORE_DELTA
                ]

        best_source_file = max(
            thresholded_matches,
            key=lambda match: match.score if match.score is not None else float("-inf"),
        ).source_file
        ranked_matches = sorted(
            thresholded_matches,
            key=cmp_to_key(
                lambda left, right: Retriever._compare_matches(
                    left,
                    right,
                    source_priority,
                    filename_keyword,
                )
            ),
        )

        for match in ranked_matches:
            max_chunks_for_document = (
                MAX_CHUNKS_FROM_BEST_DOCUMENT
                if match.source_file == best_source_file
                else MAX_CHUNKS_FROM_OTHER_DOCUMENTS
            )
            if document_counts[match.source_file] >= max_chunks_for_document:
                continue

            filtered_results.append(match)
            document_counts[match.source_file] += 1

            if len(filtered_results) >= final_limit:
                break

        reranked_results = Retriever._rerank_results(filtered_results, query, final_limit)
        return reranked_results

    @staticmethod
    def _rerank_results(
        matches: list[QdrantSearchResult],
        query: str,
        limit: int,
    ) -> list[QdrantSearchResult]:
        if not matches:
            return matches
        query_tokens = tokenize(query)

        def rerank_key(match: QdrantSearchResult) -> tuple[int, float]:
            chunk_tokens = tokenize(match.text)
            overlap = len(query_tokens & chunk_tokens)
            score = match.score if match.score is not None else float("-inf")
            return (overlap, score)

        reranked = sorted(matches, key=rerank_key, reverse=True)
        return reranked[:limit]

    @staticmethod
    def _compare_matches(
        left: QdrantSearchResult,
        right: QdrantSearchResult,
        source_priority: dict[str, int],
        filename_keyword: str | None,
    ) -> int:
        left_score = left.score if left.score is not None else float("-inf")
        right_score = right.score if right.score is not None else float("-inf")
        score_difference = abs(left_score - right_score)

        if score_difference >= CLOSE_SCORE_DELTA:
            if left_score > right_score:
                return -1
            if left_score < right_score:
                return 1
        else:
            left_priority = source_priority.get(left.source_type, 0)
            right_priority = source_priority.get(right.source_type, 0)
            if left_priority > right_priority:
                return -1
            if left_priority < right_priority:
                return 1

            if filename_keyword:
                left_match = filename_keyword in left.source_file.lower()
                right_match = filename_keyword in right.source_file.lower()
                if left_match and not right_match:
                    return -1
                if right_match and not left_match:
                    return 1

            if left_score > right_score:
                return -1
            if left_score < right_score:
                return 1

        if left.source_file < right.source_file:
            return -1
        if left.source_file > right.source_file:
            return 1
        if left.chunk_index < right.chunk_index:
            return -1
        if left.chunk_index > right.chunk_index:
            return 1
        return 0
