import unittest
from coded_tools.legal_discovery.legal_theory_engine import LegalTheoryEngine


class DummyKG:
    def run_query(self, query, params):
        element = params["element"]
        if element == "Existence of a contract":
            return [{"text": "Contract between A and B", "weight": 0.9}]
        return []

    def close(self):
        pass


class TestLegalTheoryEngine(unittest.TestCase):
    def test_suggest_theories(self):
        engine = LegalTheoryEngine(kg=DummyKG())
        theories = engine.suggest_theories()
        breach = next(t for t in theories if t["cause"] == "Breach of Contract")
        self.assertAlmostEqual(breach["score"], 0.9 / 4, places=3)
        elements = {e["name"]: e for e in breach["elements"]}
        self.assertAlmostEqual(elements["Existence of a contract"]["weight"], 0.9)
        self.assertEqual(
            elements["Existence of a contract"]["facts"][0]["weight"], 0.9
        )
        engine.close()


if __name__ == "__main__":
    unittest.main()
