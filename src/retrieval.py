import re
import time
from datetime import datetime, timezone
from typing import Iterable, Sequence

try:
    import faiss  # type: ignore
except Exception:  # pragma: no cover - optional backend dependency
    faiss = None

try:
    import numpy as np  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    np = None

try:
    import chromadb  # type: ignore
except Exception:  # pragma: no cover - optional backend dependency
    chromadb = None

from .embeddings import cosine_similarity, embed_text
from .ingesta import chunk_text


def _normalize_tokens(text: str) -> set[str]:
    return {
        token for token in re.findall(r"[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]+", (text or "").lower())
        if len(token) > 2
    }


class VectorStore:
    def __init__(self, documents: Sequence[str] | None = None, index_name: str = "daikoku_index"):
        self.index_name = index_name
        self.documents: list[dict] = []
        self.available_backends: list[str] = []
        if chromadb is not None:
            self.available_backends.append("chroma")
        if faiss is not None and np is not None:
            self.available_backends.append("faiss")
        self.available_backends.append("in_memory")
        if faiss is not None and np is not None:
            self.backend = "faiss"
        elif chromadb is not None:
            self.backend = "chroma"
        else:
            self.backend = "in_memory"
        self._faiss_index = None
        self._chroma_client = None
        if documents:
            self.add_documents(documents)

    def backend_info(self) -> dict:
        return {
            "backend": self.backend,
            "index_name": self.index_name,
            "document_count": self.document_count,
            "available_backends": list(dict.fromkeys(self.available_backends)),
            "standard_backend": "faiss" if self.backend == "faiss" else "chroma" if self.backend == "chroma" else "custom_similarity_index",
            "status": "ok" if self.documents else "ready",
        }

    @property
    def document_count(self) -> int:
        return len(self.documents)

    def index_summary(self) -> dict:
        sources = {}
        for document in self.documents:
            metadata = dict(document.get("metadata", {}) or {})
            source = metadata.get("source") or metadata.get("title") or "unknown"
            sources[source] = sources.get(source, 0) + 1
        return {
            "index_name": self.index_name,
            "document_count": self.document_count,
            "sources": sources,
        }

    def add_document(self, text: str, metadata: dict | None = None):
        cleaned_text = str(text or "").strip()
        if not cleaned_text:
            return

        normalized_metadata = {
            "source": "unknown",
            "title": "",
            "chunk_id": 0,
            "document_type": "text",
            "ingested_at": datetime.now(timezone.utc).isoformat(),
        }
        if metadata:
            normalized_metadata.update(dict(metadata))
        if not normalized_metadata.get("source") and normalized_metadata.get("title"):
            normalized_metadata["source"] = normalized_metadata["title"]

        embedding = embed_text(cleaned_text)
        self.documents.append({
            "text": cleaned_text,
            "metadata": normalized_metadata,
            "embedding": embedding,
        })

        if self.backend == "faiss" and np is not None and faiss is not None:
            if self._faiss_index is None:
                dimension = len(embedding)
                self._faiss_index = faiss.IndexFlatIP(dimension)
            vector = np.asarray([embedding], dtype="float32")
            self._faiss_index.add(vector)

    def add_documents(self, documents: Iterable[str]):
        for idx, document in enumerate(documents):
            if isinstance(document, dict):
                text = str(document.get("text", ""))
                metadata = dict(document.get("metadata", {}) or {})
                metadata.setdefault("chunk_id", idx)
            else:
                text = str(document)
                metadata = {"chunk_id": idx, "source": "inline_document"}
            self.add_document(text, metadata)

    def search(self, query: str, top_k: int = 3, min_score: float = 0.0) -> list[dict]:
        if not query or not str(query).strip() or not self.documents:
            return []

        query_text = str(query).strip()
        query_tokens = _normalize_tokens(query_text)
        query_embedding = embed_text(query_text)

        if self.backend == "faiss" and self._faiss_index is not None and np is not None:
            vector = np.asarray([query_embedding], dtype="float32")
            scores, indexes = self._faiss_index.search(vector, min(top_k, self.document_count))
            results = []
            for score, index in zip(scores[0], indexes[0]):
                if index < 0:
                    continue
                document = self.documents[int(index)]
                results.append({
                    "index": int(index),
                    "text": str(document.get("text", "") or ""),
                    "metadata": dict(document.get("metadata", {}) or {}),
                    "score": float(score),
                })
            if results:
                return [item for item in results if item["score"] >= min_score][:top_k]

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

    def evaluate_query(self, query: str, top_k: int = 3, min_score: float = 0.0) -> dict:
        started = time.perf_counter()
        results = self.search(query, top_k=top_k, min_score=min_score)
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        scores = [float(item.get("score", 0.0)) for item in results]
        return {
            "query": str(query or "").strip(),
            "result_count": len(results),
            "top_score": max(scores) if scores else 0.0,
            "avg_score": sum(scores) / len(scores) if scores else 0.0,
            "relevant": bool(results and results[0].get("score", 0.0) >= min_score),
            "index_summary": self.index_summary(),
            "backend": self.backend,
            "latency_ms": round(elapsed_ms, 3),
        }

    def _filter_external_candidates(
        self,
        results: Sequence[dict[str, str]],
        query: str,
        top_k: int = 2,
        max_chars: int = 600,
        min_overlap: float = 0.15,
    ) -> list[str]:
        if not results:
            return []

        query_tokens = _normalize_tokens(str(query or ""))
        generic_markers = (
            "wikipedia",
            "encyclopedia",
            "general information",
            "overview",
            "may refer to",
            "see also",
            "other uses",
        )
        normalized: list[str] = []
        seen: set[str] = set()

        for item in results[: max(2, top_k * 4)]:
            title = str(item.get("title", "") or "").strip()
            snippet = str(item.get("snippet", "") or "").strip()
            if not title and not snippet:
                continue
            text = f"{title}. {snippet}" if title else snippet
            text = " ".join(text.split())
            if not text or text in seen:
                continue

            lowered = text.lower()
            if any(marker in lowered for marker in generic_markers):
                if not query_tokens or not any(token in lowered for token in query_tokens):
                    continue

            if query_tokens:
                text_tokens = _normalize_tokens(text)
                overlap = len(query_tokens & text_tokens) / max(len(query_tokens), 1)
                if overlap < min_overlap and not any(token in lowered for token in query_tokens):
                    continue

            seen.add(text)
            normalized.append(text)

        compact: list[str] = []
        current_chars = 0
        for entry in normalized[:top_k]:
            if current_chars + len(entry) > max_chars:
                remaining = max_chars - current_chars
                if remaining <= 0:
                    break
                compact.append(entry[:remaining].rstrip())
                break
            compact.append(entry)
            current_chars += len(entry)
        return compact

    def compare_backends(self, queries: Sequence[str], top_k: int = 3, min_score: float = 0.0) -> list[dict]:
        if not queries or not self.documents:
            return []

        original_backend = self.backend
        comparisons: list[dict] = []
        for backend_name in list(dict.fromkeys(self.available_backends + ["in_memory"])):
            if backend_name not in self.available_backends and backend_name != "in_memory":
                continue
            self.backend = backend_name
            evaluations = [self.evaluate_query(query, top_k=top_k, min_score=min_score) for query in queries]
            comparisons.append({
                "backend": backend_name,
                "query_count": len(queries),
                "result_count": sum(item["result_count"] for item in evaluations),
                "avg_top_score": round(sum(item["top_score"] for item in evaluations) / len(evaluations), 4) if evaluations else 0.0,
                "avg_latency_ms": round(sum(item.get("latency_ms", 0.0) for item in evaluations) / len(evaluations), 3) if evaluations else 0.0,
                "evaluations": evaluations,
            })
        self.backend = original_backend
        return comparisons

    def compare_top_k(self, queries: Sequence[str], top_k_values: Sequence[int], min_score: float = 0.0) -> list[dict]:
        if not queries:
            return []

        comparisons: list[dict] = []
        for top_k in sorted({int(value) for value in top_k_values if int(value) > 0}):
            evaluations = [self.evaluate_query(query, top_k=top_k, min_score=min_score) for query in queries]
            comparisons.append({
                "top_k": top_k,
                "query_count": len(queries),
                "result_count": sum(item["result_count"] for item in evaluations),
                "avg_top_score": round(sum(item["top_score"] for item in evaluations) / len(evaluations), 4) if evaluations else 0.0,
                "avg_latency_ms": round(sum(item.get("latency_ms", 0.0) for item in evaluations) / len(evaluations), 3) if evaluations else 0.0,
                "evaluations": evaluations,
            })
        return comparisons

    def compare_chunk_sizes(
        self,
        queries: Sequence[str],
        chunk_sizes: Sequence[int],
        top_k: int = 3,
        min_score: float = 0.0,
    ) -> list[dict]:
        if not queries or not self.documents:
            return []

        comparisons: list[dict] = []
        for chunk_size in sorted({int(value) for value in chunk_sizes if int(value) > 0}):
            fragments: list[str] = []
            for document in self.documents:
                text = str(document.get("text", "") or "")
                if not text:
                    continue
                fragments.extend(chunk_text(text, chunk_size=chunk_size, overlap=max(0, chunk_size // 5)))

            temporary_store = VectorStore(fragments)
            evaluations = [temporary_store.evaluate_query(query, top_k=top_k, min_score=min_score) for query in queries]
            comparisons.append({
                "chunk_size": chunk_size,
                "query_count": len(queries),
                "result_count": sum(item["result_count"] for item in evaluations),
                "avg_top_score": round(sum(item["top_score"] for item in evaluations) / len(evaluations), 4) if evaluations else 0.0,
                "avg_latency_ms": round(sum(item.get("latency_ms", 0.0) for item in evaluations) / len(evaluations), 3) if evaluations else 0.0,
                "evaluations": evaluations,
            })
        return comparisons

    def benchmark_queries(self, queries: Sequence[str], top_k: int = 3, min_score: float = 0.0) -> list[dict]:
        evaluations = []
        for query in queries:
            evaluations.append(self.evaluate_query(query, top_k=top_k, min_score=min_score))
        return evaluations
