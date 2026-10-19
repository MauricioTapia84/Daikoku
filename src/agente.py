from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence

import requests

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

try:
    from langgraph.graph import END, StateGraph
except Exception:  # pragma: no cover - optional dependency for graph orchestration
    END = None
    StateGraph = None

from .generacion import generate_answer
from .ingesta import extract_text, load_documents
from .retrieval import VectorStore


@dataclass(slots=True)
class AgentState:
    """Formal state contract for the agent workflow.

    The graph passes this object between nodes; each node validates it before
    using it so the route and context remain consistent across executions.
    """

    question: str
    route: str = "retrieve"
    context: list[str] = field(default_factory=list)
    external_context: list[str] = field(default_factory=list)
    answer: str = ""
    sources: list[str] = field(default_factory=list)
    history: list[dict[str, str]] = field(default_factory=list)
    session_id: str = "default"

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "AgentState":
        if data is None:
            raise ValueError("Agent state cannot be empty.")
        return cls(
            question=str(data.get("question", "")).strip(),
            route=str(data.get("route", "retrieve")).strip() or "retrieve",
            context=list(data.get("context", []) or []),
            external_context=list(data.get("external_context", []) or []),
            answer=str(data.get("answer", "") or ""),
            sources=list(data.get("sources", []) or []),
            history=list(data.get("history", []) or []),
            session_id=str(data.get("session_id", "default") or "default"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "question": self.question,
            "route": self.route,
            "context": list(self.context),
            "external_context": list(self.external_context),
            "answer": self.answer,
            "sources": list(self.sources),
            "history": list(self.history),
            "session_id": self.session_id,
        }

    def validate(self) -> "AgentState":
        if not isinstance(self.question, str) or not self.question.strip():
            raise ValueError("question must be a non-empty string")
        if not isinstance(self.route, str) or self.route not in {"retrieve", "external"}:
            raise ValueError("route must be either 'retrieve' or 'external'")
        if not isinstance(self.context, list) or not all(isinstance(item, str) for item in self.context):
            raise ValueError("context must contain strings")
        if not isinstance(self.external_context, list) or not all(isinstance(item, str) for item in self.external_context):
            raise ValueError("external_context must contain strings")
        if not isinstance(self.answer, str):
            raise ValueError("answer must be a string")
        if not isinstance(self.sources, list) or not all(isinstance(item, str) for item in self.sources):
            raise ValueError("sources must contain strings")
        if not isinstance(self.history, list):
            raise ValueError("history must be a list")
        for entry in self.history:
            if not isinstance(entry, dict) or "role" not in entry or "content" not in entry:
                raise ValueError("history entries must be dictionaries with role and content")
        if not isinstance(self.session_id, str) or not self.session_id.strip():
            raise ValueError("session_id must be a non-empty string")
        return self


class DaikokuAgent:
    MAX_HISTORY = 20
    MAX_EXTERNAL_CONTEXT_CHARS = 600
    EXTERNAL_TRIGGER_PATTERNS = (
        "what is",
        "who is",
        "definition",
        "define",
        "qué es",
        "concepto",
        "resumen",
        "summary",
        "explain",
        "explica",
    )

    def __init__(self):
        self.store = VectorStore()
        self.session_memory: dict[str, list[dict]] = {}
        self.session_dir = Path(__file__).resolve().parent.parent / "data" / "sessions"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.graph = self.build_graph()

    def session_path(self, session_id: str) -> Path:
        safe_session_id = str(session_id or "default").strip() or "default"
        return self.session_dir / f"{safe_session_id}.json"

    def _summarize_history(self, history: Iterable[dict[str, str]] | None, keep_last: int = 4) -> list[dict[str, str]]:
        normalized: list[dict[str, str]] = []
        for item in history or []:
            if not isinstance(item, dict):
                continue
            role = str(item.get("role", "user"))
            content = str(item.get("content", ""))
            normalized.append({"role": role, "content": content})

        if len(normalized) <= max(1, int(keep_last)):
            return normalized

        keep_last = max(1, min(int(keep_last), self.MAX_HISTORY))
        recent = normalized[-keep_last:]
        prior = normalized[:-keep_last]
        if not prior:
            return recent

        summary_parts = []
        for item in prior:
            content = str(item.get("content", "")).strip()
            if content:
                summary_parts.append(content)

        summary = " ".join(summary_parts)
        summary = " ".join(summary.split())
        if len(summary) > 220:
            summary = summary[:220].rsplit(" ", 1)[0] + "..."

        if not summary:
            return recent[-1:]

        return [
            {"role": "system", "content": f"Resumen previo: {summary}"},
            *recent[-1:],
        ]

    def _normalize_history(self, history: Iterable[dict[str, str]] | None) -> list[dict[str, str]]:
        normalized: list[dict[str, str]] = []
        for item in history or []:
            if not isinstance(item, dict):
                continue
            role = str(item.get("role", "user"))
            content = str(item.get("content", ""))
            normalized.append({"role": role, "content": content})
        if len(normalized) > self.MAX_HISTORY:
            normalized = self._summarize_history(normalized, keep_last=4)
        return normalized[: self.MAX_HISTORY]

    def _persist_session(self, session_id: str, history: list[dict[str, str]]):
        payload = {
            "session_id": str(session_id or "default").strip() or "default",
            "history": self._normalize_history(history),
            "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        with self.session_path(payload["session_id"]).open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)

    def _load_session_from_disk(self, session_id: str) -> list[dict[str, str]]:
        file_path = self.session_path(session_id)
        if not file_path.exists():
            return []
        try:
            with file_path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except (json.JSONDecodeError, OSError):
            return []

        history = payload.get("history", []) if isinstance(payload, dict) else []
        normalized = self._normalize_history(history)
        self.session_memory[session_id] = normalized
        return normalized

    def _coerce_state(self, state: AgentState | dict[str, Any]) -> AgentState:
        if isinstance(state, AgentState):
            state_obj = state
        else:
            state_obj = AgentState.from_dict(state)
        return state_obj.validate()

    def _format_user_message(self, question: str, *, empty: bool = False, ambiguous: bool = False) -> str:
        if empty:
            return "No recibí una pregunta válida. Escribe lo que quieres consultar para poder ayudarte."
        if ambiguous:
            return "La consulta es ambigua. Sé más específico sobre el tema, el concepto o el documento que quieres revisar."
        return f"No encontré información relevante para: {question}"

    def _is_ambiguous_question(self, question: str) -> bool:
        normalized = " ".join(question.split())
        if not normalized:
            return False
        tokens = [token.lower() for token in normalized.split() if token.strip()]
        if len(tokens) <= 2:
            return True
        if normalized.lower() in {"what", "why", "how", "who", "cuando", "donde", "que"}:
            return True
        return False

    def get_session_history(self, session_id: str = "default") -> list[dict]:
        session_id = str(session_id or "default").strip() or "default"
        if session_id not in self.session_memory:
            self.session_memory[session_id] = self._load_session_from_disk(session_id)
        self.session_memory[session_id] = self._normalize_history(self.session_memory[session_id])
        self._persist_session(session_id, self.session_memory[session_id])
        return self.session_memory[session_id]

    def _append_history(self, session_id: str, role: str, content: str):
        history = self.get_session_history(session_id)
        history.append({"role": role, "content": content})
        history = self._normalize_history(history)
        self.session_memory[session_id] = history
        self._persist_session(session_id, history)

    def _router_node(self, state: AgentState | dict[str, Any]):
        """Chooses the retrieval path: local memory or external evidence.

        This node exists to keep the graph deterministic and to avoid asking
        the finalizer to decide how the question should be answered.
        """
        state_obj = self._coerce_state(state)
        question = state_obj.question.lower()
        local_hits = self.buscar_documentos(state_obj.question, top_k=1)
        should_use_external = self._should_use_external_context(question, local_hits)
        route = "external" if should_use_external else "retrieve"
        state_obj.route = route
        state_obj.validate()
        return state_obj.to_dict()

    def _should_use_external_context(self, question: str, local_hits: list[str]) -> bool:
        if not question or not question.strip():
            return False
        if not local_hits:
            return True
        if any(token in question for token in self.EXTERNAL_TRIGGER_PATTERNS):
            return True
        return False

    def buscar_documentos(self, query: str, top_k: int = 3, min_score: float = 0.05) -> list[str]:
        if not self.store.documents:
            return []
        results = self.store.search(query, top_k=top_k, min_score=min_score)
        return [item["text"] for item in results]

    def _normalize_external_results(self, results: Sequence[dict[str, str]], top_k: int = 2, max_chars: int = 600) -> list[str]:
        normalized: list[str] = []
        seen: set[str] = set()

        for item in results[:top_k]:
            title = str(item.get("title", "") or "").strip()
            snippet = str(item.get("snippet", "") or "").strip()
            if not title and not snippet:
                continue
            text = f"Wikipedia: {title}. {snippet}" if title else snippet
            text = " ".join(text.split())
            if not text or text in seen:
                continue
            seen.add(text)
            normalized.append(text)

        compact: list[str] = []
        current_chars = 0
        for entry in normalized:
            if current_chars + len(entry) > max_chars:
                remaining = max_chars - current_chars
                if remaining <= 0:
                    break
                compact.append(entry[:remaining].rstrip())
                break
            compact.append(entry)
            current_chars += len(entry)
        return compact

    def buscar_contexto_externo(self, query: str, top_k: int = 2) -> list[str]:
        if not query or not query.strip():
            return []

        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "utf8": "1",
            "srprop": "snippet",
        }
        try:
            response = requests.get(
                "https://es.wikipedia.org/w/api.php",
                params=params,
                timeout=8,
            )
            response.raise_for_status()
        except requests.RequestException:
            try:
                response = requests.get(
                    "https://en.wikipedia.org/w/api.php",
                    params=params,
                    timeout=8,
                )
                response.raise_for_status()
            except requests.RequestException:
                return []

        data = response.json()
        raw_results = data.get("query", {}).get("search", [])
        if not raw_results:
            return []
        return self._normalize_external_results(raw_results, top_k=top_k, max_chars=self.MAX_EXTERNAL_CONTEXT_CHARS)

    def _retrieve_context_node(self, state: AgentState | dict[str, Any]):
        """Collects local context from the indexed document store.

        This node isolates retrieval from generation so the final answer step only
        has to synthesize based on evidence already selected.
        """
        state_obj = self._coerce_state(state)
        question = state_obj.question
        selected = self.buscar_documentos(question, top_k=3, min_score=0.05)
        if not selected:
            selected = self._search_context(question, top_k=3, min_score=0.05)
        state_obj.context = selected
        state_obj.sources = selected
        state_obj.validate()
        return state_obj.to_dict()

    def _retrieve_external_node(self, state: AgentState | dict[str, Any]):
        """Adds external web evidence when local retrieval is insufficient.

        This node exists to preserve the RAG distinction between corpus evidence
        and supplementary knowledge retrieved from a public source.
        """
        state_obj = self._coerce_state(state)
        question = state_obj.question
        external = self.buscar_contexto_externo(question, top_k=2)
        if not external:
            state_obj.external_context = []
            state_obj.context = list(state_obj.context)
            state_obj.sources = list(state_obj.sources)
            state_obj.validate()
            return state_obj.to_dict()

        merged_context = list(state_obj.context) + external
        state_obj.external_context = external
        state_obj.context = merged_context[:4]
        state_obj.sources = merged_context[:4]
        state_obj.validate()
        return state_obj.to_dict()

    def _finalizer_node(self, state: AgentState | dict[str, Any]):
        """Generates the user-facing answer and persists session memory.

        Finalization is kept separate from routing and retrieval so the model only
        acts on a validated, complete state.
        """
        state_obj = self._coerce_state(state)
        question = state_obj.question
        context = state_obj.context
        session_id = state_obj.session_id
        history = list(state_obj.history)

        if context:
            answer = generate_answer(question, context)
        else:
            answer = f"No encontré información relevante para: {question}"

        if "repeat" in question.lower():
            answer = f"Repeat: {answer}"

        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": answer})
        history = self._normalize_history(history)

        self.session_memory[session_id] = history
        self._persist_session(session_id, history)
        state_obj.answer = answer
        state_obj.sources = context
        state_obj.history = history
        state_obj.validate()
        return state_obj.to_dict()

    def build_graph(self):
        if StateGraph is None or END is None:
            return None

        workflow = StateGraph(dict)
        workflow.add_node("router", self._router_node)
        workflow.add_node("retrieve_context", self._retrieve_context_node)
        workflow.add_node("retrieve_external", self._retrieve_external_node)
        workflow.add_node("finalizer", self._finalizer_node)
        workflow.set_entry_point("router")
        workflow.add_conditional_edges(
            "router",
            lambda state: state["route"],
            {
                "retrieve": "retrieve_context",
                "external": "retrieve_external",
            },
        )
        workflow.add_edge("retrieve_context", "finalizer")
        workflow.add_edge("retrieve_external", "finalizer")
        workflow.add_edge("finalizer", END)
        return workflow.compile()

    def _search_context(self, question: str, context: Sequence[str] | None = None, top_k: int = 3, min_score: float = 0.05):
        if context:
            local_store = VectorStore(list(context))
            results = local_store.search(question, top_k=top_k, min_score=min_score)
            return [item["text"] for item in results]

        if not self.store.documents:
            return []

        results = self.store.search(question, top_k=top_k, min_score=min_score)
        return [item["text"] for item in results]

    def add_documents(self, documents: Iterable[str]):
        self.store.add_documents(documents)

    def ingest_file(self, file_path: str):
        text = extract_text(file_path)
        self.store.add_document(text, metadata={"source": file_path})

    def ingest_files(self, file_paths: Iterable[str], chunk_size: int = 500, overlap: int = 80):
        documents = load_documents(file_paths, chunk_size=chunk_size, overlap=overlap)
        self.add_documents(documents)

    def graph_answer(self, question: str, context: Sequence[str] | None = None, top_k: int = 3, session_id: str = "default") -> str:
        if not isinstance(question, str) or not question.strip():
            logger.warning("Pregunta vacía recibida para session_id=%s", session_id)
            return self._format_user_message(question, empty=True)

        question = " ".join(question.strip().split())
        if self._is_ambiguous_question(question):
            logger.warning("Pregunta ambigua recibida para session_id=%s: %s", session_id, question)
            return self._format_user_message(question, ambiguous=True)

        selected = self._search_context(question, context=context, top_k=top_k)

        if self.graph is not None:
            state = AgentState(
                question=question,
                route="retrieve",
                context=selected,
                external_context=[],
                answer="",
                sources=selected,
                history=self.get_session_history(session_id),
                session_id=session_id,
            )
            result = self.graph.invoke(state.to_dict())
            answer = result.get("answer") or self._format_user_message(question)
            if "repeat" in question.lower():
                answer = f"Repeat: {answer}"
            return answer

        if not selected:
            fallback = self._format_user_message(question)
            if "repeat" in question.lower():
                fallback = f"Repeat: {fallback}"
            self._append_history(session_id, "user", question)
            self._append_history(session_id, "assistant", fallback)
            return fallback

        answer = generate_answer(question, selected)
        if "repeat" in question.lower():
            answer = f"Repeat: {answer}"
        self._append_history(session_id, "user", question)
        self._append_history(session_id, "assistant", answer)
        return answer

    def answer(self, question: str, context: Sequence[str] | None = None, top_k: int = 3, session_id: str = "default") -> str:
        return self.graph_answer(question, context=context, top_k=top_k, session_id=session_id)
