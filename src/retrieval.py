from typing import Iterable, List, Sequence

from .embeddings import cosine_similarity, embed_text


class VectorStore:
    def __init__(self, documents: Sequence[str] | None = None):
        self.documents: list[dict] = []
        if documents:
            self.add_documents(documents)

    def add_document(self, text: str, metadata: dict | None = None):
        self.documents.append({
            "text": text,
            "metadata": metadata or {},
            "embedding": embed_text(text),
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

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        if not self.documents:
            return []

        query_embedding = embed_text(query)
        scored = []
        for index, document in enumerate(self.documents):
            score = cosine_similarity(query_embedding, document["embedding"])
            scored.append({
                "index": index,
                "text": document["text"],
                "metadata": document["metadata"],
                "score": score,
            })

        scored.sort(key=lambda item: item["score"], reverse=True)
        return scored[:top_k]
