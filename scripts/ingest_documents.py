"""Local document ingestion script for Qdrant."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys
import time
import traceback

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.ingestion.chunking import TextChunk, chunk_documents
from app.ingestion.loaders import load_markdown_documents, load_pdf_documents
from app.retrieval.embeddings import EmbeddingError, OllamaEmbeddingGenerator
from app.retrieval.vector_store import QdrantVectorStore

EMBEDDING_PROGRESS_EVERY = 25
UPSERT_BATCH_SIZE = 50
RETRY_DELAY_SECONDS = 2
MIN_SPLIT_CHUNK_LENGTH = 120
CONTEXT_LENGTH_ERROR_TEXT = "input length exceeds the context length"


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
    raw_dir = PROJECT_ROOT / "data" / "raw"
    aws_docs_dir = raw_dir / "aws_docs"
    internal_docs_dir = raw_dir / "internal_docs"
    nist_docs_dir = raw_dir / "nist_docs"

    documents = []
    documents.extend(load_markdown_documents(aws_docs_dir, source_type="aws_docs"))
    documents.extend(
        load_markdown_documents(internal_docs_dir, source_type="internal_docs")
    )
    documents.extend(load_pdf_documents(nist_docs_dir, source_type="nist_docs"))

    print(f"Loaded documents: {len(documents)}")
    if not documents:
        print("No documents found to ingest.")
        return

    chunks = chunk_documents(documents)
    print(f"Created chunks: {len(chunks)}")
    if not chunks:
        print("Documents loaded but no chunks were created.")
        return

    embedding_generator = OllamaEmbeddingGenerator()
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

    vector_size = len(vectors[0])

    store = QdrantVectorStore()
    store.ensure_collection(vector_size=vector_size)
    store.upsert_chunks(
        chunks=embedded_chunks,
        vectors=vectors,
        batch_size=UPSERT_BATCH_SIZE,
        progress_callback=lambda batch, total, size: print(
            f"Upsert batch: {batch}/{total} ({size} points)"
        ),
    )

    print("Ingestion complete.")


if __name__ == "__main__":
    main()
