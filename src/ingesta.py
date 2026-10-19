import csv
import logging
import re
from pathlib import Path
from typing import Iterable

logger = logging.getLogger(__name__)

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

    normalized = re.sub(r"\s+", " ", (text or "")).strip()
    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", normalized) if part.strip()]
    if not sentences:
        return []

    chunks: list[str] = []
    current = ""
    overlap_chars = max(0, min(overlap, chunk_size // 2))

    for sentence in sentences:
        candidate = (current + " " + sentence).strip() if current else sentence
        if len(candidate) <= chunk_size:
            current = candidate
            continue

        if current:
            chunks.append(current)
            if overlap_chars > 0:
                current = current[-overlap_chars:]
            else:
                current = ""

        if len(sentence) <= chunk_size:
            current = sentence
        else:
            words = sentence.split()
            long_chunk = ""
            for word in words:
                next_chunk = f"{long_chunk} {word}".strip()
                if len(next_chunk) <= chunk_size:
                    long_chunk = next_chunk
                else:
                    if long_chunk:
                        chunks.append(long_chunk)
                        if overlap_chars > 0:
                            long_chunk = long_chunk[-overlap_chars:]
                    long_chunk = word
            if long_chunk:
                current = long_chunk

    if current:
        chunks.append(current)

    return [chunk for chunk in chunks if chunk]


def load_documents(paths: Iterable[str], chunk_size: int = 500, overlap: int = 80) -> list[str]:
    documents: list[str] = []
    for file_path in paths:
        try:
            extracted = extract_text(file_path)
            documents.extend(chunk_text(extracted, chunk_size=chunk_size, overlap=overlap))
        except (FileNotFoundError, OSError, ValueError) as exc:
            logger.warning("No se pudo procesar el documento %s: %s", file_path, exc)
    return documents
