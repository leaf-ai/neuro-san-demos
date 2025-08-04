import unittest
from coded_tools.legal_discovery.legal_theory_engine import LegalTheoryEngine


class DummyKG:
    def run_query(self, query, params):
        element = params["element"]
        if element == "Existence of a contract":
            return [{"text": "Contract between A and B"}]
        return []

    def get_cause_subgraph(self, cause):
        return ["n"], ["e"]

    def close(self):
        pass


class TestLegalTheoryEngine(unittest.TestCase):
    def test_suggest_theories(self):
        engine = LegalTheoryEngine(kg=DummyKG())
        theories = engine.suggest_theories()
        breach = next(t for t in theories if t["cause"] == "Breach of Contract")
        self.assertAlmostEqual(breach["score"], 0.25)
        elements = {e["name"]: e for e in breach["elements"]}
        self.assertTrue(elements["Existence of a contract"]["facts"])
        self.assertIn("defenses", breach)
        self.assertIn("indicators", breach)
        engine.close()

    def test_get_theory_subgraph(self):
        engine = LegalTheoryEngine(kg=DummyKG())
        nodes, edges = engine.get_theory_subgraph("Fraud")
        self.assertEqual(nodes, ["n"])
        self.assertEqual(edges, ["e"])
        engine.close()


if __name__ == "__main__":
    unittest.main()
