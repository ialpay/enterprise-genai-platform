"""Simple text chunking utilities for ingestion."""

from __future__ import annotations

from dataclasses import dataclass
import re

from app.ingestion.loaders import SourceDocument


@dataclass(frozen=True)
class TextChunk:
    text: str
    source_file: str
    source_type: str
    chunk_index: int
    chunk_sub_index: str | None = None


def normalize_text(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").replace("\t", " ")
    paragraphs = re.split(r"\n\s*\n", normalized)
    cleaned_paragraphs: list[str] = []

    for paragraph in paragraphs:
        cleaned = re.sub(r"[ \t]+", " ", paragraph)
        cleaned = re.sub(r"\s*\n\s*", " ", cleaned).strip()
        if cleaned:
            cleaned_paragraphs.append(cleaned)

    return "\n\n".join(cleaned_paragraphs)


def chunk_document(
    document: SourceDocument,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> list[TextChunk]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be >= 0 and < chunk_size")

    chunks: list[TextChunk] = []
    step = chunk_size - chunk_overlap
    text = normalize_text(document.text)

    index = 0
    for start in range(0, len(text), step):
        chunk_text = text[start : start + chunk_size].strip()
        if not chunk_text:
            continue
        chunks.append(
            TextChunk(
                text=chunk_text,
                source_file=document.source_file,
                source_type=document.source_type,
                chunk_index=index,
            )
        )
        index += 1
    return chunks


def chunk_documents(
    documents: list[SourceDocument],
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> list[TextChunk]:
    all_chunks: list[TextChunk] = []
    for document in documents:
        all_chunks.extend(
            chunk_document(
                document=document,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )
        )
    return all_chunks
