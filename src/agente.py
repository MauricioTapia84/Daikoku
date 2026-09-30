from __future__ import annotations

from typing import Iterable, Sequence, TypedDict

import requests

try:
    from langgraph.graph import END, StateGraph
except Exception:  # pragma: no cover - optional dependency for graph orchestration
    END = None
    StateGraph = None

from .generacion import generate_answer
from .ingesta import extract_text, load_documents
from .retrieval import VectorStore


class AgentState(TypedDict):
    question: str
    route: str
    context: list[str]
    external_context: list[str]
    answer: str
    sources: list[str]
    history: list[dict]
    session_id: str


class DaikokuAgent:
    def __init__(self):
        self.store = VectorStore()
        self.session_memory: dict[str, list[dict]] = {}
        self.graph = self.build_graph()

    def get_session_history(self, session_id: str = "default") -> list[dict]:
        if session_id not in self.session_memory:
            self.session_memory[session_id] = []
        return self.session_memory[session_id]

    def _append_history(self, session_id: str, role: str, content: str):
        history = self.get_session_history(session_id)
        history.append({"role": role, "content": content})
        if len(history) > 20:
            history[:] = history[-20:]

    def _router_node(self, state: AgentState):
        question = state.get("question", "")
        q = question.lower()
        should_use_external = any(token in q for token in ["what is", "who is", "definition", "define", "qué es", "concepto", "resumen", "summary"])
        if should_use_external and not self.buscar_documentos(question, 1):
            route = "external"
        elif not self.buscar_documentos(question, 1):
            route = "external"
        else:
            route = "retrieve"
        return {**state, "route": route}

    def buscar_documentos(self, query: str, top_k: int = 3) -> list[str]:
        if not self.store.documents:
            return []
        results = self.store.search(query, top_k=top_k)
        return [item["text"] for item in results]

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
        results = []
        for item in data.get("query", {}).get("search", [])[:top_k]:
            title = item.get("title", "")
            snippet = item.get("snippet", "")
            if title:
                results.append(f"Wikipedia: {title}. {snippet}")
        return results

    def _retrieve_context_node(self, state: AgentState):
        question = state.get("question", "")
        selected = self.buscar_documentos(question, top_k=3)
        if not selected:
            selected = self._search_context(question, top_k=3)
        return {**state, "context": selected, "sources": selected}

    def _retrieve_external_node(self, state: AgentState):
        question = state.get("question", "")
        external = self.buscar_contexto_externo(question, top_k=2)
        context = list(state.get("context", [])) + external
        return {**state, "external_context": external, "context": context, "sources": context}

    def _finalizer_node(self, state: AgentState):
        question = state.get("question", "")
        context = state.get("context", [])
        session_id = state.get("session_id", "default")
        history = state.get("history", [])

        if context:
            answer = generate_answer(question, context)
        else:
            answer = f"No encontré información relevante para: {question}"

        if "repeat" in question.lower():
            answer = f"Repeat: {answer}"

        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": answer})
        history = history[-20:]

        self.session_memory[session_id] = history
        return {
            **state,
            "answer": answer,
            "sources": context,
            "history": history,
        }

    def build_graph(self):
        if StateGraph is None or END is None:
            return None

        workflow = StateGraph(AgentState)
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

    def _search_context(self, question: str, context: Sequence[str] | None = None, top_k: int = 3):
        if context:
            local_store = VectorStore(list(context))
            results = local_store.search(question, top_k=top_k)
            return [item["text"] for item in results]

        if not self.store.documents:
            return []

        results = self.store.search(question, top_k=top_k)
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
        selected = self._search_context(question, context=context, top_k=top_k)

        if self.graph is not None:
            state = {
                "question": question,
                "route": "retrieve",
                "context": selected,
                "external_context": [],
                "answer": "",
                "sources": selected,
                "history": self.get_session_history(session_id),
                "session_id": session_id,
            }
            result = self.graph.invoke(state)
            answer = result.get("answer") or f"No encontré información relevante para: {question}"
            if "repeat" in question.lower():
                answer = f"Repeat: {answer}"
            return answer

        if not selected:
            fallback = f"No encontré información relevante para: {question}"
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
