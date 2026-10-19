import json
import os
import tempfile
import unittest

from src.agente import AgentState, DaikokuAgent
from src.ingesta import extract_text, load_documents
from src.retrieval import VectorStore


class TestDaikoku(unittest.TestCase):
    def test_extract_text_from_txt(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as handle:
            handle.write("Neural networks learn patterns from data using layers and weights.")
            temp_path = handle.name

        try:
            text = extract_text(temp_path)
            self.assertIn("Neural networks", text)
            self.assertIn("weights", text)
        finally:
            os.unlink(temp_path)

    def test_vector_store_search(self):
        store = VectorStore()
        docs = [
            "Neural networks learn patterns from data.",
            "Cats are domestic animals.",
            "The weather is sunny today.",
        ]
        store.add_documents(docs)
        results = store.search("deep learning model", top_k=1)
        self.assertIn("Neural networks", results[0]["text"])

    def test_vector_store_relevance_filtering_and_metadata(self):
        store = VectorStore()
        store.add_document("Neural networks learn patterns from data.", metadata={"source": "paper_a", "chunk_id": 1})
        store.add_document("Cats are domestic animals.", metadata={"source": "paper_b", "chunk_id": 2})

        results = store.search("deep learning model", top_k=2, min_score=0.01)
        self.assertTrue(results)
        self.assertEqual(results[0]["metadata"]["source"], "paper_a")

        irrelevant = store.search("quantum gravity paradox", top_k=3, min_score=0.8)
        self.assertEqual(irrelevant, [])

    def test_agent_answer(self):
        agent = DaikokuAgent()
        answer = agent.answer(
            "What are neural networks?",
            [
                "Neural networks are computational models inspired by biological brains. "
                "They learn patterns from data by adjusting their weights."
            ],
        )
        self.assertIn("neural", answer.lower())

    def test_langgraph_answer(self):
        agent = DaikokuAgent()
        agent.add_documents([
            "Neural networks are computational models inspired by biological brains.",
            "Machine learning uses algorithms to detect patterns from examples.",
        ])
        answer = agent.graph_answer("What are neural networks?")
        self.assertIn("neural", answer.lower())

    def test_router_and_session_memory(self):
        agent = DaikokuAgent()
        agent.session_path("session_1").unlink(missing_ok=True)
        agent.add_documents([
            "Neural networks are computational models inspired by biological brains.",
            "Machine learning uses algorithms to detect patterns from examples.",
        ])
        first = agent.answer("What are neural networks?", session_id="session_1")
        second = agent.answer("Can you repeat that?", session_id="session_1")
        history = agent.get_session_history("session_1")

        self.assertIn("neural", first.lower())
        self.assertIn("repeat", second.lower())
        self.assertGreaterEqual(len(history), 4)
        self.assertEqual(history[0]["role"], "user")

    def test_router_routes_local_and_external_context(self):
        agent = DaikokuAgent()
        agent.add_documents([
            "Neural networks are computational models inspired by biological brains.",
            "Machine learning uses algorithms to detect patterns from examples.",
        ])

        local_state = agent._router_node({
            "question": "What are neural networks?",
            "route": "retrieve",
            "context": [],
            "external_context": [],
            "answer": "",
            "sources": [],
            "history": [],
            "session_id": "router_local_test",
        })
        self.assertEqual(local_state["route"], "retrieve")

        external_state = agent._router_node({
            "question": "What is machine learning?",
            "route": "retrieve",
            "context": [],
            "external_context": [],
            "answer": "",
            "sources": [],
            "history": [],
            "session_id": "router_external_test",
        })
        self.assertEqual(external_state["route"], "external")

    def test_without_local_context_and_with_local_context_behaviors(self):
        agent = DaikokuAgent()

        no_context = agent.answer("What is machine learning?", session_id="no_context_case")
        self.assertIsInstance(no_context, str)
        self.assertTrue(no_context)

        agent.add_documents([
            "Neural networks learn patterns from data using layers and weights."
        ])
        local_answer = agent.answer("What are neural networks?", session_id="with_context_case")
        self.assertIn("neural", local_answer.lower())

    def test_external_context_lookup(self):
        agent = DaikokuAgent()
        result = agent.buscar_contexto_externo("machine learning", top_k=1)
        self.assertIsInstance(result, list)

    def test_conversation_continuity_and_repeat_protection(self):
        agent = DaikokuAgent()
        session_id = "continuity_test"
        agent.session_path(session_id).unlink(missing_ok=True)
        agent.add_documents([
            "Neural networks are computational models inspired by biological brains.",
            "Machine learning uses algorithms to detect patterns from examples.",
        ])

        first = agent.answer("What are neural networks?", session_id=session_id)
        second = agent.answer("Can you repeat that?", session_id=session_id)
        history = agent.get_session_history(session_id)

        self.assertIn("neural", first.lower())
        self.assertIn("repeat", second.lower())
        self.assertGreaterEqual(len(history), 4)
        self.assertEqual(history[-1]["role"], "assistant")

    def test_agent_state_contract_and_validation(self):
        state = AgentState(
            question="What are neural networks?",
            route="retrieve",
            context=["A neural network learns from data."],
            external_context=[],
            answer="",
            sources=["A neural network learns from data."],
            history=[],
            session_id="session_validation",
        )
        self.assertEqual(state.question, "What are neural networks?")
        self.assertEqual(state.route, "retrieve")
        state.validate()

        with self.assertRaises(ValueError):
            AgentState(
                question="",
                route="retrieve",
                context=[],
                external_context=[],
                answer="",
                sources=[],
                history=[],
                session_id="session_validation",
            ).validate()

        with self.assertRaises(ValueError):
            AgentState(
                question="What are neural networks?",
                route="unknown",
                context=[],
                external_context=[],
                answer="",
                sources=[],
                history=[],
                session_id="session_validation",
            ).validate()

    def test_external_context_normalization_and_limits(self):
        agent = DaikokuAgent()
        payload = [
            {"title": "Machine learning", "snippet": "Machine learning is a field of artificial intelligence."},
            {"title": "", "snippet": ""},
            {"title": "Very long topic", "snippet": "x" * 5000},
        ]
        results = agent._normalize_external_results(payload, top_k=2, max_chars=300)
        self.assertTrue(results)
        self.assertLessEqual(sum(len(item) for item in results), 300)
        self.assertNotIn("", results)

    def test_session_memory_persists_and_trims_history(self):
        agent = DaikokuAgent()
        session_id = "disk_session_test"
        agent.session_path(session_id).unlink(missing_ok=True)

        for idx in range(40):
            agent._append_history(session_id, "user", f"message {idx}")

        storage_file = agent.session_path(session_id)
        self.assertTrue(storage_file.exists())

        with open(storage_file, "r", encoding="utf-8") as handle:
            payload = json.load(handle)

        self.assertLessEqual(len(payload["history"]), agent.MAX_HISTORY)
        self.assertEqual(payload["session_id"], session_id)

    def test_history_summary_before_trimming(self):
        agent = DaikokuAgent()
        history = [
            {"role": "user", "content": "I want to learn neural networks."},
            {"role": "assistant", "content": "Neural networks model patterns with layers."},
            {"role": "user", "content": "Explain backpropagation in simple terms."},
            {"role": "assistant", "content": "Backpropagation adjusts weights using gradients."},
        ]

        compact = agent._summarize_history(history, keep_last=2)
        self.assertTrue(any("neural" in entry["content"].lower() for entry in compact))
        self.assertLessEqual(len(compact), 2)

    def test_empty_and_ambiguous_queries_are_handled(self):
        agent = DaikokuAgent()
        empty = agent.answer("   ", session_id="empty_test")
        ambiguous = agent.answer("what", session_id="ambiguous_test")

        self.assertIn("pregunta", empty.lower())
        self.assertIn("ambigua", ambiguous.lower())

    def test_bad_documents_are_skipped_without_crashing(self):
        docs = load_documents(["missing_file_123456789.txt"])
        self.assertEqual(docs, [])


if __name__ == "__main__":
    unittest.main()
