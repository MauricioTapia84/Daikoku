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

    def test_vector_store_query_quality_metrics(self):
        store = VectorStore()
        store.add_document("Neural networks learn patterns from data.")
        store.add_document("Cats are domestic animals.")

        quality = store.evaluate_query("neural networks learning", top_k=2, min_score=0.0)
        self.assertGreaterEqual(quality["result_count"], 1)
        self.assertGreater(quality["top_score"], 0.0)
        self.assertTrue(quality["relevant"])

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

    def test_domain_specialization_and_evidence_style(self):
        agent = DaikokuAgent(domain="documentos_academicos_universitarios")
        answer = agent.answer(
            "What are neural networks?",
            [
                "Neural networks are computational models inspired by biological brains. "
                "They learn patterns from data by adjusting their weights."
            ],
            session_id="domain_specialization_test",
        )
        lowered = answer.lower()
        self.assertIn("evidencia", lowered)
        self.assertIn("documentos", lowered)
        self.assertIn("acad", lowered)

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

    def test_benchmark_retrieval_reports_quality_metrics(self):
        agent = DaikokuAgent(domain="academic_documents")
        agent.add_documents([
            "Neural networks learn patterns from data using layers and weights.",
            "Machine learning uses examples to detect patterns and make predictions.",
            "Deep learning uses layered neural networks to model complex information.",
        ])

        results = agent.benchmark_retrieval([
            "what are neural networks",
            "what is machine learning",
        ], top_k=2, min_score=0.0)

        self.assertEqual(len(results), 2)
        self.assertIn("result_count", results[0])
        self.assertIn("top_score", results[0])
        self.assertIn("index_summary", results[0])

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

    def test_memory_summary_and_short_term_are_distinct(self):
        agent = DaikokuAgent()
        session_id = "memory_layers_test"
        agent.session_path(session_id).unlink(missing_ok=True)
        agent._append_history(session_id, "user", "I want to learn neural networks.")
        agent._append_history(session_id, "assistant", "Neural networks model patterns with layers.")

        storage_file = agent.session_path(session_id)
        with open(storage_file, "r", encoding="utf-8") as handle:
            payload = json.load(handle)

        self.assertIn("short_term_history", payload)
        self.assertIn("memory_summary", payload)
        self.assertTrue(payload["short_term_history"])
        self.assertTrue(payload["memory_summary"]) 

    def test_empty_and_ambiguous_queries_are_handled(self):
        agent = DaikokuAgent()
        empty = agent.answer("   ", session_id="empty_test")
        ambiguous = agent.answer("what", session_id="ambiguous_test")

        self.assertIn("pregunta", empty.lower())
        self.assertIn("ambigua", ambiguous.lower())

    def test_bad_documents_are_skipped_without_crashing(self):
        docs = load_documents(["missing_file_123456789.txt"])
        self.assertEqual(docs, [])

    def test_backend_and_observability_summary(self):
        agent = DaikokuAgent(domain="documentos_academicos_universitarios")
        agent.add_documents(["Neural networks learn patterns from data."])
        summary = agent.get_observability_summary("backend_obs_session")

        self.assertIn("backend", summary)
        self.assertIn("event_count", summary)
        self.assertIn("domain", summary)
        self.assertIn("standard_backend", summary)
        self.assertGreaterEqual(summary["event_count"], 1)

    def test_backend_comparison_and_external_relevance_filtering(self):
        store = VectorStore()
        store.add_documents([
            "Neural networks learn patterns from data using layers.",
            "Weather is sunny and the sky is clear.",
        ])

        comparison = store.compare_backends([
            "what are neural networks",
            "what is the weather today",
        ], top_k=2, min_score=0.0)
        self.assertTrue(comparison)
        self.assertIn("backend", comparison[0])
        self.assertIn("result_count", comparison[0])

        payload = [
            {"title": "Weather", "snippet": "The weather is sunny today."},
            {"title": "Neural network", "snippet": "A neural network learns patterns from data using layers."},
        ]
        filtered = store._filter_external_candidates(payload, "neural network", top_k=2, max_chars=500)
        self.assertTrue(filtered)
        self.assertIn("neural", " ".join(filtered).lower())

    def test_top_k_and_chunk_size_variants_are_benchmarked(self):
        store = VectorStore()
        store.add_documents([
            "Neural networks are computational models inspired by biological neurons. "
            "They learn patterns from data by adjusting weights through repeated optimization steps. "
            "Deep learning architectures stack many layers to capture complex relationships. ",
            "Retrieval systems search for relevant passages in a document collection before generating an answer.",
        ])

        by_top_k = store.compare_top_k(["what are neural networks", "how does retrieval work"], top_k_values=[1, 2], min_score=0.0)
        self.assertTrue(by_top_k)
        self.assertIn("top_k", by_top_k[0])
        self.assertEqual(sorted(item["top_k"] for item in by_top_k), [1, 2])

        by_chunk_size = store.compare_chunk_sizes(["what are neural networks", "how does retrieval work"], chunk_sizes=[80, 180], top_k=2, min_score=0.0)
        self.assertTrue(by_chunk_size)
        self.assertIn("chunk_size", by_chunk_size[0])
        self.assertEqual(sorted(item["chunk_size"] for item in by_chunk_size), [80, 180])

    def test_external_retrieval_threshold_and_impact_summary(self):
        agent = DaikokuAgent()
        local_context = [
            "Neural networks learn patterns from data by adjusting weights through optimization.",
        ]
        generic_results = [
            {"title": "Wikipedia", "snippet": "Wikipedia is a free encyclopedia with many articles."},
            {"title": "General concept", "snippet": "This is an overview of a topic without concrete evidence."},
        ]
        relevant_results = [
            {"title": "Neural network", "snippet": "A neural network learns patterns from data and updates weights during training."},
            {"title": "Deep learning", "snippet": "Deep learning relies on stacks of neural layers to model complex patterns."},
        ]

        filtered = agent.store._filter_external_candidates(generic_results, "neural network", top_k=2, max_chars=500)
        self.assertEqual(filtered, [])

        relevant_filtered = agent.store._filter_external_candidates(relevant_results, "neural network", top_k=2, max_chars=500)
        self.assertTrue(relevant_filtered)
        self.assertIn("neural", " ".join(relevant_filtered).lower())

        impact = agent.evaluate_external_impact("neural network", local_context, relevant_filtered)
        self.assertIn("uses_external", impact)
        self.assertIn("local_context_count", impact)
        self.assertIn("relevance_score", impact)

    def test_memory_policy_and_quality_metrics(self):
        agent = DaikokuAgent()
        history = [
            {"role": "user", "content": "Explain neural networks."},
            {"role": "assistant", "content": "Neural networks learn patterns from data using layers."},
            {"role": "user", "content": "Explain neural networks."},
            {"role": "assistant", "content": "Neural networks learn patterns from data using layers."},
        ]

        cleaned = agent._normalize_history(history)
        self.assertLessEqual(len(cleaned), agent.MAX_HISTORY)
        self.assertEqual(cleaned[0]["content"], "Explain neural networks.")

        metrics = agent.evaluate_memory_quality("memory_policy_test", history)
        self.assertIn("history_length", metrics)
        self.assertIn("deduplicated_entries", metrics)
        self.assertIn("short_term_limit", metrics)
        self.assertIn("memory_summary_length", metrics)

    def test_guardrails_reject_invalid_workflow_states(self):
        agent = DaikokuAgent()
        invalid_state = {
            "question": "What is a neural network?",
            "route": "invalid_route",
            "context": [],
            "external_context": [],
            "answer": "",
            "sources": [],
            "history": [],
            "session_id": "",
            "retrieval_mode": "local_search",
            "tool_name": "document_search",
            "memory_summary": "",
            "trace_id": "trace-1",
            "domain": "academic_documents",
            "case_study": "asistente académico",
            "metadata": {},
        }

        with self.assertRaises(ValueError):
            agent.validate_workflow_state(invalid_state)


if __name__ == "__main__":
    unittest.main()
