"""Local document ingestion script for Qdrant."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import replace
from pathlib import Path
import sys
import time
import traceback

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.ingestion.chunking import TextChunk, chunk_documents
from app.ingestion.loaders import (
    SourceDocument,
    load_markdown_documents,
    load_pdf_documents,
)
from app.retrieval.embeddings import EmbeddingError, OllamaEmbeddingGenerator
from app.retrieval.vector_store import QdrantVectorStore

EMBEDDING_PROGRESS_EVERY = 25
UPSERT_BATCH_SIZE = 50
RETRY_DELAY_SECONDS = 2
MIN_SPLIT_CHUNK_LENGTH = 120
CONTEXT_LENGTH_ERROR_TEXT = "input length exceeds the context length"
VECTOR_SIZE_PREFLIGHT_PROBE_TEXT = "qdrant vector size preflight probe"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ingest tracked source documents into Qdrant."
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=500,
        help="Chunk size for document splitting (default: 500).",
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=50,
        help="Chunk overlap for document splitting (default: 50).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Load and chunk tracked sources without embedding or Qdrant upsert.",
    )
    parser.add_argument(
        "--recreate-collection",
        action="store_true",
        help=(
            "Explicitly recreate the configured Qdrant collection when an existing "
            "collection vector size does not match the current embedding vector size."
        ),
    )
    return parser.parse_args()


def load_tracked_documents(raw_dir: Path) -> list[SourceDocument]:
    tracked_sources = (
        ("aws_docs", raw_dir / "aws_docs", load_markdown_documents),
        ("internal_docs", raw_dir / "internal_docs", load_markdown_documents),
        ("nist_docs", raw_dir / "nist_docs", load_pdf_documents),
    )

    documents = []
    for source_type, source_dir, loader in tracked_sources:
        loaded = loader(source_dir, source_type=source_type)
        print(
            f"Loaded {len(loaded)} documents from {source_type} "
            f"({source_dir.as_posix()})"
        )
        documents.extend(loaded)
    return documents


def chunk_label(chunk: TextChunk) -> str:
    if chunk.chunk_sub_index:
        return f"{chunk.chunk_index}.{chunk.chunk_sub_index}"
    return str(chunk.chunk_index)


def split_text_for_embedding(text: str) -> tuple[str, str]:
    midpoint = len(text) // 2
    split_at = text.rfind(" ", 0, midpoint)
    if split_at == -1 or split_at < len(text) // 4:
        split_at = text.find(" ", midpoint)
    if split_at == -1:
        split_at = midpoint

    left = text[:split_at].strip()
    right = text[split_at:].strip()
    return left, right


def is_context_length_error(exc: EmbeddingError) -> bool:
    return CONTEXT_LENGTH_ERROR_TEXT in str(exc).lower()


def embed_chunk_with_retry(
    embedding_generator: OllamaEmbeddingGenerator,
    index: int,
    total_chunks: int,
    chunk: TextChunk,
) -> list[tuple[TextChunk, list[float]]]:
    for attempt in range(1, 3):
        print(
            f"Embedding chunk {index}/{total_chunks} "
            f"(attempt {attempt}/2, source_type={chunk.source_type}, "
            f"source_file={chunk.source_file}, chunk_index={chunk_label(chunk)}, "
            f"chunk_length={len(chunk.text)})"
        )
        try:
            return [(chunk, embedding_generator.embed_text(chunk.text))]
        except EmbeddingError as exc:
            if is_context_length_error(exc):
                return split_and_embed_chunk(
                    embedding_generator=embedding_generator,
                    chunk=chunk,
                    index=index,
                    total_chunks=total_chunks,
                    error=exc,
                )
            if attempt == 1:
                print(
                    f"Embedding failed for chunk {index}/{total_chunks}: {exc}. "
                    f"Retrying in {RETRY_DELAY_SECONDS} seconds."
                )
                time.sleep(RETRY_DELAY_SECONDS)
                continue

            print(f"Embedding failed again for chunk {index}/{total_chunks}.")
            print(
                f"Failure details: source_type={chunk.source_type}, "
                f"source_file={chunk.source_file}, chunk_index={chunk_label(chunk)}, "
                f"chunk_length={len(chunk.text)}"
            )
            traceback.print_exception(type(exc), exc, exc.__traceback__)
            raise

    raise RuntimeError("Unreachable retry state while embedding chunk.")


def split_and_embed_chunk(
    embedding_generator: OllamaEmbeddingGenerator,
    chunk: TextChunk,
    index: int,
    total_chunks: int,
    error: EmbeddingError,
) -> list[tuple[TextChunk, list[float]]]:
    if len(chunk.text) <= MIN_SPLIT_CHUNK_LENGTH:
        print(f"Adaptive split stopped at minimum size for chunk {index}/{total_chunks}.")
        print(
            f"Failure details: source_type={chunk.source_type}, "
            f"source_file={chunk.source_file}, chunk_index={chunk_label(chunk)}, "
            f"chunk_length={len(chunk.text)}"
        )
        traceback.print_exception(type(error), error, error.__traceback__)
        raise error

    left_text, right_text = split_text_for_embedding(chunk.text)
    if not left_text or not right_text:
        print(f"Adaptive split produced an empty child chunk for chunk {index}/{total_chunks}.")
        print(
            f"Failure details: source_type={chunk.source_type}, "
            f"source_file={chunk.source_file}, chunk_index={chunk_label(chunk)}, "
            f"chunk_length={len(chunk.text)}"
        )
        traceback.print_exception(type(error), error, error.__traceback__)
        raise error

    print(
        f"Context length exceeded for chunk {index}/{total_chunks}; "
        f"splitting chunk_index={chunk_label(chunk)} into two smaller parts."
    )

    left_chunk = replace(
        chunk,
        text=left_text,
        chunk_sub_index=(chunk.chunk_sub_index or "") + "0",
    )
    right_chunk = replace(
        chunk,
        text=right_text,
        chunk_sub_index=(chunk.chunk_sub_index or "") + "1",
    )

    embedded_parts: list[tuple[TextChunk, list[float]]] = []
    embedded_parts.extend(
        embed_chunk_with_retry(
            embedding_generator=embedding_generator,
            index=index,
            total_chunks=total_chunks,
            chunk=left_chunk,
        )
    )
    embedded_parts.extend(
        embed_chunk_with_retry(
            embedding_generator=embedding_generator,
            index=index,
            total_chunks=total_chunks,
            chunk=right_chunk,
        )
    )
    return embedded_parts


def main() -> None:
    args = parse_args()
    raw_dir = PROJECT_ROOT / "data" / "raw"
    try:
        documents = load_tracked_documents(raw_dir)
    except (FileNotFoundError, NotADirectoryError, RuntimeError) as exc:
        print(f"Ingestion source loading failed: {exc}")
        raise SystemExit(1) from exc

    print(f"Loaded documents: {len(documents)}")
    if not documents:
        print("No documents found to ingest from tracked sources.")
        raise SystemExit(1)

    chunks = chunk_documents(
        documents,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )
    print(f"Created chunks: {len(chunks)}")
    if not chunks:
        print("Documents loaded but no chunks were created.")
        raise SystemExit(1)

    source_counts = Counter(document.source_type for document in documents)
    chunk_counts = Counter(chunk.source_type for chunk in chunks)
    print(f"Document counts by source: {dict(source_counts)}")
    print(f"Chunk counts by source: {dict(chunk_counts)}")

    if args.dry_run:
        print("Dry run complete. Skipping embedding generation and Qdrant upsert.")
        return

    try:
        embedding_generator = OllamaEmbeddingGenerator()
        embedding_generator.ensure_model_available()
        print(
            f"Embedding model preflight passed for configured model: "
            f"{embedding_generator.model_name}"
        )
        embedding_vector_size = len(
            embedding_generator.embed_text(VECTOR_SIZE_PREFLIGHT_PROBE_TEXT)
        )
        if embedding_vector_size <= 0:
            raise EmbeddingError(
                "Embedding preflight returned an empty vector while checking Qdrant "
                "collection compatibility."
            )
        print(f"Embedding vector size preflight: {embedding_vector_size}")

        store = QdrantVectorStore()
        collection_vector_size = store.get_collection_vector_size()
        if collection_vector_size is None:
            print(
                f"Qdrant collection '{store.collection_name}' not found. "
                f"Creating it with vector size {embedding_vector_size}."
            )
            store.ensure_collection(vector_size=embedding_vector_size)
        elif collection_vector_size != embedding_vector_size:
            if args.recreate_collection:
                print(
                    f"Qdrant collection '{store.collection_name}' vector size "
                    f"mismatch detected (existing={collection_vector_size}, "
                    f"embedding={embedding_vector_size}). Recreating collection "
                    f"because --recreate-collection was provided."
                )
                store.recreate_collection(vector_size=embedding_vector_size)
            else:
                raise RuntimeError(
                    f"Configured Qdrant collection '{store.collection_name}' vector "
                    f"size mismatch: existing collection size is "
                    f"{collection_vector_size}, current embedding vector size is "
                    f"{embedding_vector_size}. Re-run with --recreate-collection "
                    f"to recreate the local collection, or set QDRANT_COLLECTION "
                    f"to a collection that matches the embedding vector size."
                )
        else:
            print(
                f"Qdrant collection preflight passed for '{store.collection_name}' "
                f"(vector size {collection_vector_size})."
            )

        embedded_chunks: list[TextChunk] = []
        vectors: list[list[float]] = []
        total_chunks = len(chunks)
        for index, chunk in enumerate(chunks, start=1):
            embedded_results = embed_chunk_with_retry(
                embedding_generator=embedding_generator,
                index=index,
                total_chunks=total_chunks,
                chunk=chunk,
            )
            for embedded_chunk, vector in embedded_results:
                embedded_chunks.append(embedded_chunk)
                vectors.append(vector)
            if index % EMBEDDING_PROGRESS_EVERY == 0 or index == total_chunks:
                print(f"Embedding progress: {index}/{total_chunks}")

        store.upsert_chunks(
            chunks=embedded_chunks,
            vectors=vectors,
            batch_size=UPSERT_BATCH_SIZE,
            progress_callback=lambda batch, total, size: print(
                f"Upsert batch: {batch}/{total} ({size} points)"
            ),
        )
    except EmbeddingError as exc:
        print(f"Embedding pipeline failed: {exc}")
        raise SystemExit(1) from exc
    except Exception as exc:
        print(f"Ingestion pipeline failed during vector storage: {exc}")
        raise SystemExit(1) from exc

    print("Ingestion complete.")


if __name__ == "__main__":
    main()
