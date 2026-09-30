import csv
import re
from pathlib import Path
from typing import Iterable

try:
    from markitdown import MarkItDown
except Exception:  # pragma: no cover - optional dependency for document conversion
    MarkItDown = None


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()


def extract_text(file_path: str) -> str:
    """Return normalized text from a supported document format."""
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix in {".txt", ".md", ".rst"}:
        return _normalize_text(path.read_text(encoding="utf-8", errors="ignore"))

    if suffix == ".csv":
        rows = []
        with path.open("r", encoding="utf-8", errors="ignore", newline="") as handle:
            reader = csv.reader(handle)
            for row in reader:
                rows.append(" | ".join(row))
        return _normalize_text("\n".join(rows))

    if suffix == ".pdf":
        if MarkItDown is not None:
            try:
                result = MarkItDown().convert(str(path))
                text = getattr(result, "text_content", None) or ""
                if text:
                    return _normalize_text(text)
            except Exception:
                pass

        try:
            from pypdf import PdfReader
        except Exception as exc:  # pragma: no cover - optional dependency fallback
            raise ValueError("PDF extraction requires markitdown or pypdf to be installed.") from exc

        pages = []
        reader = PdfReader(str(path))
        for page in reader.pages:
            text = page.extract_text() or ""
            if text:
                pages.append(text)
        return _normalize_text("\n".join(pages))

    if suffix in {".docx", ".xlsx", ".xls", ".pptx"}:
        if MarkItDown is not None:
            try:
                result = MarkItDown().convert(str(path))
                text = getattr(result, "text_content", None) or ""
                if text:
                    return _normalize_text(text)
            except Exception:
                pass
        raise ValueError(f"Unsupported document type for {suffix!r}. Install markitdown to process this file.")

    if path.exists():
        return _normalize_text(path.read_text(encoding="utf-8", errors="ignore"))

    raise FileNotFoundError(f"File not found: {file_path}")


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 80) -> list[str]:
    if not text:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunk = text[start:end]
        chunks.append(chunk.strip())
        if end >= len(text):
            break
        start += max(1, chunk_size - overlap)
    return [chunk for chunk in chunks if chunk]


def load_documents(paths: Iterable[str], chunk_size: int = 500, overlap: int = 80) -> list[str]:
    documents: list[str] = []
    for file_path in paths:
        extracted = extract_text(file_path)
        documents.extend(chunk_text(extracted, chunk_size=chunk_size, overlap=overlap))
    return documents
