"""Document loaders for local ingestion sources."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


@dataclass(frozen=True)
class SourceDocument:
    text: str
    source_file: str
    source_type: str


def load_markdown_documents(directory: Path, source_type: str) -> list[SourceDocument]:
    documents: list[SourceDocument] = []
    for path in sorted(directory.glob("*.md")):
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            continue
        documents.append(
            SourceDocument(
                text=text,
                source_file=path.name,
                source_type=source_type,
            )
        )
    return documents


def load_pdf_documents(directory: Path, source_type: str) -> list[SourceDocument]:
    documents: list[SourceDocument] = []
    for path in sorted(directory.glob("*.pdf")):
        reader = PdfReader(str(path))
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
                source_file=path.name,
                source_type=source_type,
            )
        )
    return documents
