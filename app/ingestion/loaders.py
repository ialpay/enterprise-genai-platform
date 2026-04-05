"""Document loaders for local ingestion sources."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from pypdf import PdfReader


@dataclass(frozen=True)
class SourceDocument:
    text: str
    source_file: str
    source_type: str


def _require_directory(directory: Path) -> Path:
    if not directory.exists():
        raise FileNotFoundError(f"Source directory not found: {directory}")
    if not directory.is_dir():
        raise NotADirectoryError(f"Source path is not a directory: {directory}")
    return directory


def _iter_files(directory: Path, pattern: str) -> Iterable[Path]:
    return sorted(_require_directory(directory).rglob(pattern))


def load_markdown_documents(directory: Path, source_type: str) -> list[SourceDocument]:
    documents: list[SourceDocument] = []
    for path in _iter_files(directory, "*.md"):
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            continue
        documents.append(
            SourceDocument(
                text=text,
                source_file=path.relative_to(directory).as_posix(),
                source_type=source_type,
            )
        )
    return documents


def load_pdf_documents(directory: Path, source_type: str) -> list[SourceDocument]:
    documents: list[SourceDocument] = []
    for path in _iter_files(directory, "*.pdf"):
        try:
            reader = PdfReader(str(path))
        except Exception as exc:
            raise RuntimeError(f"Failed to read PDF file: {path}") from exc
        pages = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            pages.append(page_text)
        text = "\n".join(pages).strip()
        if not text:
            continue
        documents.append(
            SourceDocument(
                text=text,
                source_file=path.relative_to(directory).as_posix(),
                source_type=source_type,
            )
        )
    return documents
