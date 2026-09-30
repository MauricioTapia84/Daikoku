import os
import tempfile
import unittest

from src.agente import DaikokuAgent
from src.ingesta import extract_text
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

    def test_external_context_lookup(self):
        agent = DaikokuAgent()
        result = agent.buscar_contexto_externo("machine learning", top_k=1)
        self.assertIsInstance(result, list)


if __name__ == "__main__":
    unittest.main()
