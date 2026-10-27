from __future__ import annotations

import json
import logging
import re
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

    The state is intentionally strict so the graph behaves like a deterministic
    workflow: it exposes the current route, the selected tool, the short-term
    memory, the compact long-term summary, and a trace identifier for auditing.
    """

    question: str
    route: str = "retrieve"
    context: list[str] = field(default_factory=list)
    external_context: list[str] = field(default_factory=list)
    answer: str = ""
    sources: list[str] = field(default_factory=list)
    history: list[dict[str, str]] = field(default_factory=list)
    session_id: str = "default"
    retrieval_mode: str = "local_search"
    tool_name: str = "document_search"
    memory_summary: str = ""
    trace_id: str = ""
    domain: str = "academic_documents"
    case_study: str = "asistente académico para documentos universitarios"
    metadata: dict[str, Any] = field(default_factory=dict)

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
            retrieval_mode=str(data.get("retrieval_mode", "local_search") or "local_search"),
            tool_name=str(data.get("tool_name", "document_search") or "document_search"),
            memory_summary=str(data.get("memory_summary", "") or ""),
            trace_id=str(data.get("trace_id", "") or ""),
            domain=str(data.get("domain", "academic_documents") or "academic_documents"),
            case_study=str(data.get("case_study", "asistente académico para documentos universitarios") or "asistente académico para documentos universitarios"),
            metadata=dict(data.get("metadata", {}) or {}),
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
            "retrieval_mode": self.retrieval_mode,
            "tool_name": self.tool_name,
            "memory_summary": self.memory_summary,
            "trace_id": self.trace_id,
            "domain": self.domain,
            "case_study": self.case_study,
            "metadata": dict(self.metadata),
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
        if not isinstance(self.retrieval_mode, str) or self.retrieval_mode not in {"local_search", "external_search"}:
            raise ValueError("retrieval_mode must be either 'local_search' or 'external_search'")
        if not isinstance(self.tool_name, str) or not self.tool_name.strip():
            raise ValueError("tool_name is not valid")
        if not isinstance(self.memory_summary, str):
            raise ValueError("memory_summary must be a string")
        if not isinstance(self.trace_id, str):
            raise ValueError("trace_id must be a string")
        if not isinstance(self.domain, str) or not self.domain.strip():
            raise ValueError("domain must be a non-empty string")
        if not isinstance(self.case_study, str) or not self.case_study.strip():
            raise ValueError("case_study must be a non-empty string")
        if not isinstance(self.metadata, dict):
            raise ValueError("metadata must be a dictionary")
        return self


class ShortTermMemory:
    def __init__(self, max_history: int = 20):
        self.max_history = max_history

    def normalize(self, history: Iterable[dict[str, str]] | None) -> list[dict[str, str]]:
        normalized = []
        for item in history or []:
            if not isinstance(item, dict):
                continue
            normalized.append({
                "role": str(item.get("role", "user")),
                "content": str(item.get("content", "")),
            })
        return normalized[: self.max_history]


class LongTermMemory:
    def __init__(self, max_chars: int = 220):
        self.max_chars = max_chars

    def summarize(self, history: Iterable[dict[str, str]] | None) -> str:
        parts = []
        for item in history or []:
            if not isinstance(item, dict):
                continue
            content = str(item.get("content", "")).strip()
            if content:
                parts.append(content)
        summary = " ".join(parts)
        summary = " ".join(summary.split())
        if not summary:
            return "Sin historial previo."
        if len(summary) > self.max_chars:
            summary = summary[: self.max_chars].rsplit(" ", 1)[0] + "..."
        return summary


class DaikokuAgent:
    MAX_HISTORY = 20
    MAX_EXTERNAL_CONTEXT_CHARS = 600
    EXTERNAL_CONTEXT_THRESHOLD = 0.15
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

    def __init__(self, domain: str = "documentos_academicos_universitarios", case_study: str = "asistente académico para documentos universitarios"):
        self.domain = domain or "documentos_academicos_universitarios"
        self.case_study = case_study or "asistente académico para documentos universitarios"
        self.store = VectorStore(index_name="daikoku_local_index")
        self.tool_registry = {
            "buscar_documentos": self.buscar_documentos,
            "buscar_en_wikipedia": self.buscar_contexto_externo,
            "resolver_ambigüedad": self.resolver_ambigüedad,
            "resumir_historial": self.resumir_historial,
        }
        self.session_memory: dict[str, list[dict]] = {}
        self.short_term_memory = ShortTermMemory(max_history=self.MAX_HISTORY)
        self.long_term_memory = LongTermMemory(max_chars=220)
        self.session_dir = Path(__file__).resolve().parent.parent / "data" / "sessions"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger("DaikokuAgent")
        self.observability: dict[str, Any] = {"events": [], "sessions": {}}
        self.graph = self.build_graph()

    def _make_trace_id(self, session_id: str = "default") -> str:
        return f"{session_id}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"

    def _audit(self, event: str, **details):
        payload = {"event": event, "domain": self.domain, "case_study": self.case_study}
        payload.update(details)
        self.observability.setdefault("events", []).append(payload)
        session_id = str(details.get("session_id") or "default").strip() or "default"
        self.observability.setdefault("sessions", {}).setdefault(session_id, []).append(payload)
        self.logger.info("agent_event=%s payload=%s", event, payload)

    def get_observability_summary(self, session_id: str = "default") -> dict:
        session_id = str(session_id or "default").strip() or "default"
        history = self.get_session_history(session_id)
        backend_info = self.store.backend_info()
        events = self.observability.get("events", [])
        session_events = self.observability.get("sessions", {}).get(session_id, [])

        if not events and not session_events:
            snapshot = {
                "event": "session_summary",
                "session_id": session_id,
                "domain": self.domain,
                "case_study": self.case_study,
                "backend": backend_info.get("backend"),
                "standard_backend": backend_info.get("standard_backend"),
            }
            self.observability.setdefault("events", []).append(snapshot)
            self.observability.setdefault("sessions", {}).setdefault(session_id, []).append(snapshot)
            events = self.observability.get("events", [])
            session_events = self.observability.get("sessions", {}).get(session_id, [])

        summary = {
            "session_id": session_id,
            "history_length": len(history),
            "backend": backend_info.get("backend"),
            "standard_backend": backend_info.get("standard_backend"),
            "event_count": len(session_events) if session_events else len(events),
            "domain": self.domain,
            "case_study": self.case_study,
        }
        if session_events:
            summary["last_event"] = session_events[-1]
        elif events:
            summary["last_event"] = events[-1]
        return summary

    def validate_workflow_state(self, state: AgentState | dict[str, Any]) -> AgentState:
        """Reject malformed workflow data before any transition or answer generation."""
        state_obj = self._coerce_state(state)
        route = str(state_obj.route or "retrieve").strip().lower()
        if route not in {"retrieve", "external"}:
            raise ValueError(f"Invalid graph route: {state_obj.route!r}")
        if not str(state_obj.session_id or "").strip():
            raise ValueError("session_id is required for every workflow step")
        if not str(state_obj.tool_name or "").strip():
            raise ValueError("tool_name is required for every workflow step")
        return state_obj

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

    def _prune_history(self, history: Iterable[dict[str, str]] | None) -> list[dict[str, str]]:
        cleaned: list[dict[str, str]] = []
        seen: set[tuple[str, str]] = set()
        for item in history or []:
            if not isinstance(item, dict):
                continue
            role = str(item.get("role", "user"))
            content = str(item.get("content", "")).strip()
            if not role or not content:
                continue
            key = (role.lower(), content.lower())
            if key in seen:
                continue
            seen.add(key)
            cleaned.append({"role": role, "content": content})
        return cleaned

    def _extract_session_keywords(self, history: Iterable[dict[str, str]] | None) -> list[str]:
        tokens: list[str] = []
        for item in history or []:
            if not isinstance(item, dict):
                continue
            content = str(item.get("content", "")).strip()
            if not content:
                continue
            tokens.extend(
                token.lower()
                for token in re.findall(r"[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]+", content)
                if len(token) > 3
            )
        ordered = list(dict.fromkeys(tokens))
        return ordered[:12]

    def _normalize_history(self, history: Iterable[dict[str, str]] | None) -> list[dict[str, str]]:
        normalized = self._prune_history(history)
        if len(normalized) > self.MAX_HISTORY:
            normalized = self._summarize_history(normalized, keep_last=4)
        return normalized[: self.MAX_HISTORY]

    def _build_memory_summary(self, history: Iterable[dict[str, str]] | None) -> str:
        parts: list[str] = []
        for item in history or []:
            if not isinstance(item, dict):
                continue
            content = str(item.get("content", "")).strip()
            if content:
                parts.append(content)
        summary = " ".join(parts)
        summary = " ".join(summary.split())
        if not summary:
            return "Sin historial previo."
        if len(summary) > 220:
            summary = summary[:220].rsplit(" ", 1)[0] + "..."
        return summary

    def evaluate_memory_quality(self, session_id: str, history: Iterable[dict[str, str]] | None = None) -> dict[str, Any]:
        session_history = list(history) if history is not None else self.get_session_history(session_id)
        cleaned = self._prune_history(session_history)
        summary = self._build_memory_summary(cleaned)
        metrics = {
            "session_id": str(session_id or "default").strip() or "default",
            "history_length": len(cleaned),
            "raw_history_length": len(list(session_history or [])),
            "deduplicated_entries": max(0, len(list(session_history or [])) - len(cleaned)),
            "short_term_limit": self.MAX_HISTORY,
            "memory_summary_length": len(summary),
            "summary_preview": summary[:120],
            "retention_policy": "bounded_summary_with_deduplication",
            "session_keywords": self._extract_session_keywords(cleaned),
        }
        return metrics

    def _persist_session(self, session_id: str, history: list[dict[str, str]]):
        short_history = self._normalize_history(history)
        session_summary = self._build_memory_summary(short_history)
        payload = {
            "session_id": str(session_id or "default").strip() or "default",
            "history": short_history,
            "short_term_history": short_history,
            "memory_summary": session_summary,
            "long_term_memory": {
                "summary": session_summary,
                "strategy": "bounded_summary_with_deduplication",
                "keywords": self._extract_session_keywords(short_history),
            },
            "session_metadata": {
                "retention_policy": "bounded_summary_with_deduplication",
                "short_term_limit": self.MAX_HISTORY,
                "session_keywords": self._extract_session_keywords(short_history),
            },
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

        if isinstance(payload, dict):
            history = payload.get("short_term_history") or payload.get("history", [])
        else:
            history = []
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

    def resolver_ambigüedad(self, question: str) -> str:
        """Explicit tool for clarifying vague questions before the answer node runs."""
        if not question or not str(question).strip():
            return "No recibí una pregunta válida. Escribe una consulta más específica."
        normalized = " ".join(str(question).split())
        if self._is_ambiguous_question(normalized):
            return "La consulta es ambigua. Indica el tema, el documento o el concepto exacto que quieres revisar."
        return "Consulta suficientemente específica para continuar con la recuperación."

    def resumir_historial(self, session_id: str = "default") -> str:
        """Summarizes the persisted session history into a compact memory snapshot."""
        history = self.get_session_history(session_id)
        return self._build_memory_summary(history)

    def evaluate_retrieval_quality(self, query: str, *args, **kwargs) -> dict:
        """Returns a lightweight retrieval-quality summary to make the semantic pipeline easier to audit."""
        return self.store.evaluate_query(query, *args, **kwargs)

    def benchmark_retrieval(self, queries: Sequence[str], top_k: int = 3, min_score: float = 0.0) -> list[dict]:
        """Runs a small benchmark over a set of test queries to make retrieval quality measurable."""
        started = datetime.now(timezone.utc)
        results = self.store.benchmark_queries(list(queries), top_k=top_k, min_score=min_score)
        duration_ms = (datetime.now(timezone.utc) - started).total_seconds() * 1000.0
        for item in results:
            item.setdefault("domain", self.domain)
            item.setdefault("backend", self.store.backend)
            item.setdefault("benchmark_duration_ms", round(duration_ms, 3))
        self._audit("benchmark_retrieval", query_count=len(list(queries)), duration_ms=round(duration_ms, 3), backend=self.store.backend, domain=self.domain)
        return results

    def _append_history(self, session_id: str, role: str, content: str):
        history = self.get_session_history(session_id)
        history.append({"role": role, "content": content})
        history = self._normalize_history(history)
        self.session_memory[session_id] = history
        self._persist_session(session_id, history)

    def _router_node(self, state: AgentState | dict[str, Any]):
        """Chooses the retrieval path: local memory or external evidence."""
        state_obj = self.validate_workflow_state(state)
        state_obj.trace_id = state_obj.trace_id or self._make_trace_id(state_obj.session_id)
        question = state_obj.question.lower()

        local_hits = list(state_obj.context or [])
        if not local_hits:
            local_hits = self.buscar_documentos(state_obj.question, top_k=1)

        should_use_external = self._should_use_external_context(question, local_hits)
        route = "external" if should_use_external else "retrieve"
        state_obj.route = route if route in {"retrieve", "external"} else "retrieve"
        state_obj.retrieval_mode = "external_search" if should_use_external else "local_search"
        state_obj.tool_name = "buscar_en_wikipedia" if should_use_external else "buscar_documentos"
        state_obj.memory_summary = self._build_memory_summary(state_obj.history)
        state_obj.metadata = {
            "trace_id": state_obj.trace_id,
            "local_hits": bool(local_hits),
            "should_use_external": should_use_external,
            "session_id": state_obj.session_id,
            "domain": self.domain,
            "case_study": self.case_study,
            "vector_backend": self.store.backend,
            "available_backends": self.store.available_backends,
        }
        self._audit("router_decision", route=state_obj.route, trace_id=state_obj.trace_id, local_hits=bool(local_hits), should_use_external=should_use_external, domain=self.domain)
        self.validate_workflow_state(state_obj)
        return state_obj.to_dict()

    def _tool_layer_node(self, state: AgentState | dict[str, Any]):
        """Explicit tool layer: each tool is selected and logged before retrieval."""
        state_obj = self.validate_workflow_state(state)
        question = state_obj.question
        if not question or not str(question).strip():
            state_obj.tool_name = "resolver_ambigüedad"
        elif self._is_ambiguous_question(question):
            state_obj.tool_name = "resolver_ambigüedad"
        elif self.buscar_documentos(question, top_k=1):
            state_obj.tool_name = "buscar_documentos"
        else:
            state_obj.tool_name = "buscar_en_wikipedia"
        if state_obj.tool_name not in self.tool_registry and state_obj.tool_name not in {"empty_fallback"}:
            raise ValueError(f"Unsupported tool name in workflow state: {state_obj.tool_name!r}")
        state_obj.metadata["tool_name"] = state_obj.tool_name
        state_obj.metadata["available_tools"] = list(self.tool_registry.keys())
        self._audit("tool_layer", tool_name=state_obj.tool_name, question=question, domain=self.domain)
        return state_obj.to_dict()

    def _memory_node(self, state: AgentState | dict[str, Any]):
        """Loads and summarizes session memory before answer generation."""
        state_obj = self.validate_workflow_state(state)
        history = self.get_session_history(state_obj.session_id)
        state_obj.history = history
        state_obj.memory_summary = self._build_memory_summary(history)
        state_obj.metadata["memory_summary"] = state_obj.memory_summary
        state_obj.metadata["history_length"] = len(history)
        self._audit("memory_snapshot", session_id=state_obj.session_id, history_length=len(history), domain=self.domain)
        self.validate_workflow_state(state_obj)
        return state_obj.to_dict()

    def _observability_node(self, state: AgentState | dict[str, Any]):
        """Captures a compact production-style observability record for this execution."""
        state_obj = self.validate_workflow_state(state)
        payload = {
            "trace_id": state_obj.trace_id,
            "session_id": state_obj.session_id,
            "route": state_obj.route,
            "tool_name": state_obj.tool_name,
            "context_count": len(state_obj.context),
            "external_context_count": len(state_obj.external_context),
            "domain": self.domain,
            "vector_backend": self.store.backend,
        }
        state_obj.metadata["observability"] = payload
        self._audit("observability", **payload)
        self.validate_workflow_state(state_obj)
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
        query_text = " ".join(
            str(item.get("title", "") or "").strip() + " " + str(item.get("snippet", "") or "").strip()
            for item in results[:2]
        ).strip()
        return self.store._filter_external_candidates(
            results,
            query_text or " ".join(str(item.get("snippet", "") or "") for item in results[:2]),
            top_k=top_k,
            max_chars=max_chars,
            min_overlap=self.EXTERNAL_CONTEXT_THRESHOLD,
        )

    def _score_external_candidate(self, text: str, query: str) -> float:
        if not text or not query:
            return 0.0

        query_tokens = {
            token.lower()
            for token in re.findall(r"[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]+", (query or "").lower())
            if len(token) > 2
        }
        if not query_tokens:
            return 0.0

        text_tokens = {
            token.lower()
            for token in re.findall(r"[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]+", (text or "").lower())
            if len(token) > 2
        }
        overlap = len(query_tokens & text_tokens) / max(len(query_tokens), 1)
        phrase_bonus = 0.1 if any(token in (text or "").lower() for token in query_tokens) else 0.0
        return round(min(1.0, overlap + phrase_bonus), 3)

    def evaluate_external_impact(
        self,
        query: str,
        local_context: Sequence[str] | None,
        external_context: Sequence[str] | None,
    ) -> dict[str, Any]:
        local_items = list(local_context or [])
        external_items = list(external_context or [])
        local_text = " ".join(local_items)
        external_text = " ".join(external_items)
        relevance_score = max((self._score_external_candidate(item, query) for item in external_items), default=0.0)
        uses_external = bool(external_items) and (not local_items or relevance_score >= self.EXTERNAL_CONTEXT_THRESHOLD)
        summary = {
            "query": str(query or "").strip(),
            "local_context_count": len(local_items),
            "external_context_count": len(external_items),
            "relevance_score": round(float(relevance_score), 3),
            "uses_external": bool(uses_external),
            "external_text_length": len(external_text),
            "local_text_length": len(local_text),
        }
        return summary

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
        filtered = self.store._filter_external_candidates(
            raw_results,
            query,
            top_k=top_k,
            max_chars=self.MAX_EXTERNAL_CONTEXT_CHARS,
            min_overlap=self.EXTERNAL_CONTEXT_THRESHOLD,
        )
        return filtered

    def _retrieve_context_node(self, state: AgentState | dict[str, Any]):
        """Collects local context from the indexed document store.

        This node isolates retrieval from generation so the final answer step only
        has to synthesize based on evidence already selected.
        """
        state_obj = self.validate_workflow_state(state)
        question = state_obj.question
        selected = self.buscar_documentos(question, top_k=3, min_score=0.05)
        if not selected:
            selected = self._search_context(question, top_k=3, min_score=0.05)
        state_obj.context = selected
        state_obj.sources = selected
        state_obj.metadata["local_context_count"] = len(selected)
        state_obj.metadata["domain"] = self.domain
        state_obj.metadata["case_study"] = self.case_study
        state_obj.metadata["backend"] = self.store.backend
        state_obj.metadata["backend_info"] = self.store.backend_info()
        self._audit("local_retrieval", trace_id=state_obj.trace_id, count=len(selected), question=question, domain=self.domain, backend=self.store.backend)
        state_obj.validate()
        return state_obj.to_dict()

    def _retrieve_external_node(self, state: AgentState | dict[str, Any]):
        """Adds external web evidence when local retrieval is insufficient.

        This node exists to preserve the RAG distinction between corpus evidence
        and supplementary knowledge retrieved from a public source.
        """
        state_obj = self.validate_workflow_state(state)
        question = state_obj.question
        local_context = list(state_obj.context)
        external = self.buscar_contexto_externo(question, top_k=2)

        impact = self.evaluate_external_impact(question, local_context, external)
        if not external or not impact["uses_external"]:
            state_obj.external_context = []
            state_obj.context = list(local_context)
            state_obj.sources = list(state_obj.sources)
            state_obj.metadata["external_context_count"] = 0
            state_obj.metadata["external_impact"] = impact
            self._audit("external_retrieval", trace_id=state_obj.trace_id, count=0, question=question, impact=impact)
            state_obj.validate()
            return state_obj.to_dict()

        merged_context = list(local_context) + external[:1]
        state_obj.external_context = external[:1]
        state_obj.context = merged_context[:4]
        state_obj.sources = merged_context[:4]
        state_obj.metadata["external_context_count"] = len(state_obj.external_context)
        state_obj.metadata["external_impact"] = impact
        state_obj.metadata["domain"] = self.domain
        state_obj.metadata["case_study"] = self.case_study
        state_obj.metadata["backend"] = self.store.backend
        self._audit("external_retrieval", trace_id=state_obj.trace_id, count=len(state_obj.external_context), question=question, domain=self.domain, backend=self.store.backend, impact=impact)
        state_obj.validate()
        return state_obj.to_dict()

    def _finalizer_node(self, state: AgentState | dict[str, Any]):
        """Generates the user-facing answer and persists session memory."""
        state_obj = self.validate_workflow_state(state)
        question = state_obj.question
        context = state_obj.context
        session_id = state_obj.session_id
        history = list(state_obj.history)
        if not session_id or not str(session_id).strip():
            raise ValueError("Finalizer requires a valid session_id")

        if context:
            answer = generate_answer(
                question,
                context,
                domain=self.domain,
                case_study=self.case_study,
            )
            state_obj.tool_name = state_obj.tool_name or "document_search"
        else:
            answer = (
                f"No tengo evidencia suficiente en el dominio de {self.domain} para responder de forma fiable "
                f"la pregunta: {question}"
            )
            state_obj.tool_name = "empty_fallback"

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
        state_obj.memory_summary = self._build_memory_summary(history)
        state_obj.metadata.update({
            "answer_length": len(answer),
            "context_length": len(context),
            "history_length": len(history),
            "session_id": session_id,
            "domain": self.domain,
            "case_study": self.case_study,
        })
        self._audit("finalizer_output", trace_id=state_obj.trace_id, session_id=session_id, answer_chars=len(answer), domain=self.domain)
        state_obj.validate()
        return state_obj.to_dict()

    def build_graph(self):
        if StateGraph is None or END is None:
            return None

        workflow = StateGraph(dict)
        workflow.add_node("router", self._router_node)
        workflow.add_node("tool_layer", self._tool_layer_node)
        workflow.add_node("retrieve_context", self._retrieve_context_node)
        workflow.add_node("retrieve_external", self._retrieve_external_node)
        workflow.add_node("memory", self._memory_node)
        workflow.add_node("observability", self._observability_node)
        workflow.add_node("finalizer", self._finalizer_node)
        workflow.set_entry_point("router")
        workflow.add_edge("router", "tool_layer")
        workflow.add_conditional_edges(
            "tool_layer",
            lambda state: state["route"],
            {
                "retrieve": "retrieve_context",
                "external": "retrieve_external",
            },
        )
        workflow.add_edge("retrieve_context", "memory")
        workflow.add_edge("retrieve_external", "memory")
        workflow.add_edge("memory", "observability")
        workflow.add_edge("observability", "finalizer")
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
