import os
import re
from typing import Iterable, List

try:
    from sentence_transformers import SentenceTransformer
except Exception:  # pragma: no cover - optional dependency for semantic embeddings
    SentenceTransformer = None

_MODEL = None
_CONCEPTS = {
    "neural": 0,
    "network": 0,
    "networks": 0,
    "brain": 0,
    "model": 1,
    "models": 1,
    "deep": 1,
    "learning": 1,
    "learn": 1,
    "layer": 1,
    "layers": 1,
    "pattern": 2,
    "patterns": 2,
    "data": 2,
    "animal": 3,
    "animals": 3,
    "cat": 3,
    "cats": 3,
    "weather": 4,
    "sunny": 4,
    "sun": 4,
    "today": 4,
}


def _concept_vector(text: str, dimensions: int = 8) -> List[float]:
    vector = [0.0 for _ in range(dimensions)]
    text = (text or "").lower()
    words = re.findall(r"[a-z]+", text)
    if not words:
        return vector

    for word in words:
        concept = _CONCEPTS.get(word, None)
        if concept is None:
            continue
        vector[concept] += 1.0

    norm = sum(value * value for value in vector) ** 0.5
    if norm:
        return [value / norm for value in vector]
    return vector


def get_model():
    global _MODEL
    if SentenceTransformer is None:
        return None

    enable_model = os.getenv("DAIKOKU_USE_SEMANTIC_MODEL", "false").lower() in {"1", "true", "yes", "on"}
    if not enable_model:
        return None

    if _MODEL is None:
        _MODEL = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    return _MODEL


def embed_text(text: str):
    if isinstance(text, (list, tuple)):
        return [embed_text(item) for item in text]

    model = get_model()
    if model is not None:
        try:
            vector = model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
            return vector.tolist()
        except Exception:
            pass

    return _concept_vector(text)


def cosine_similarity(vec_a: Iterable[float], vec_b: Iterable[float]) -> float:
    left = list(vec_a)
    right = list(vec_b)
    if len(left) != len(right):
        max_len = max(len(left), len(right))
        left += [0.0] * (max_len - len(left))
        right += [0.0] * (max_len - len(right))

    dot = sum(a * b for a, b in zip(left, right))
    norm_left = sum(a * a for a in left) ** 0.5
    norm_right = sum(b * b for b in right) ** 0.5
    if not norm_left or not norm_right:
        return 0.0
    return dot / (norm_left * norm_right)
