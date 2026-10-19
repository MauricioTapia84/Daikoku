import re
from typing import Iterable, List, Sequence

from .embeddings import cosine_similarity, embed_text


def _normalize_tokens(text: str) -> set[str]:
    return {
        token for token in re.findall(r"[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]+", (text or "").lower())
        if len(token) > 2
    }


class VectorStore:
    def __init__(self, documents: Sequence[str] | None = None):
        self.documents: list[dict] = []
        if documents:
            self.add_documents(documents)

    def add_document(self, text: str, metadata: dict | None = None):
        cleaned_text = str(text or "").strip()
        if not cleaned_text:
            return
        self.documents.append({
            "text": cleaned_text,
            "metadata": dict(metadata or {}),
            "embedding": embed_text(cleaned_text),
        })

    def add_documents(self, documents: Iterable[str]):
        for document in documents:
            if isinstance(document, dict):
                text = str(document.get("text", ""))
                metadata = document.get("metadata", {})
            else:
                text = str(document)
                metadata = {}
            self.add_document(text, metadata)

    def search(self, query: str, top_k: int = 3, min_score: float = 0.0) -> list[dict]:
        if not query or not str(query).strip() or not self.documents:
            return []

        query_text = str(query).strip()
        query_tokens = _normalize_tokens(query_text)
        query_embedding = embed_text(query_text)
        scored: list[dict] = []

        for index, document in enumerate(self.documents):
            text = str(document.get("text", "") or "")
            metadata = dict(document.get("metadata", {}) or {})
            score = cosine_similarity(query_embedding, document["embedding"])
            overlap = 0.0
            if query_tokens:
                text_tokens = _normalize_tokens(text)
                if text_tokens:
                    overlap = len(query_tokens & text_tokens) / max(len(query_tokens), 1)
            relevance = max(score, overlap)
            scored.append({
                "index": index,
                "text": text,
                "metadata": metadata,
                "score": relevance,
            })

        scored.sort(key=lambda item: item["score"], reverse=True)
        filtered = [item for item in scored if item["score"] >= min_score]
        if not filtered and min_score > 0:
            return []
        if not filtered:
            filtered = scored
        return filtered[:top_k]
