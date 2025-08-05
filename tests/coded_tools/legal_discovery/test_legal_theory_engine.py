import unittest
from coded_tools.legal_discovery.legal_theory_engine import LegalTheoryEngine


class DummyKG:
    def run_query(self, query, params):
        element = params["element"]
        if element == "Existence of a contract":
            return [{"text": "Contract between A and B", "weight": 0.9}]
        return []

    def get_cause_subgraph(self, cause):
        return ["n"], ["e"]

    def close(self):
        pass


class ScoringKG:
    def run_query(self, query, params):
        element = params["element"]
        if element == "Existence of a contract":
            return [{"text": "Contract exists", "weight": 0.9}]
        if element == "Plaintiff's performance or excuse":
            return [{"text": "Performance", "weight": 0.8}]
        return []

    def get_cause_subgraph(self, cause):
        return [], []

    def close(self):
        pass


class TestLegalTheoryEngine(unittest.TestCase):
    def test_suggest_theories(self):
        engine = LegalTheoryEngine(kg=DummyKG())
        theories = engine.suggest_theories()
        breach = next(t for t in theories if t["cause"] == "Breach of Contract")
        elements = {e["name"]: e for e in breach["elements"]}
        self.assertAlmostEqual(elements["Existence of a contract"]["weight"], 0.9)
        self.assertEqual(
            elements["Existence of a contract"]["facts"][0]["weight"], 0.9
        )
        self.assertAlmostEqual(breach["score"], 0.25)
        elements = {e["name"]: e for e in breach["elements"]}
        self.assertTrue(elements["Existence of a contract"]["facts"])
        self.assertIn("defenses", breach)
        self.assertIn("indicators", breach)
        engine.close()

    def test_suggestion_scoring(self):
        engine = LegalTheoryEngine(kg=ScoringKG())
        theories = engine.suggest_theories()
        top = theories[0]
        self.assertEqual(top["cause"], "Breach of Contract")
        self.assertAlmostEqual(top["score"], 0.5)
        elements = {e["name"]: e for e in top["elements"]}
        self.assertAlmostEqual(
            elements["Plaintiff's performance or excuse"]["weight"], 0.8
        )
        engine.close()

    def test_get_theory_subgraph(self):
        engine = LegalTheoryEngine(kg=DummyKG())
        nodes, edges = engine.get_theory_subgraph("Fraud")
        self.assertEqual(nodes, ["n"])
        self.assertEqual(edges, ["e"])
        engine.close()


if __name__ == "__main__":
    unittest.main()

