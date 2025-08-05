import unittest
from flask import Flask, jsonify, request
from coded_tools.legal_discovery.legal_theory_engine import LegalTheoryEngine


class DummyKG:
    def run_query(self, query, params):
        if params["element"] == "Existence of a contract":
            return [{"text": "Contract between A and B", "weight": 1.0}]
        return []

    def get_cause_subgraph(self, cause):
        return [], []

    def close(self):
        pass


class TestAPIEndpoints(unittest.TestCase):
    def setUp(self):
        self.engine = LegalTheoryEngine(kg=DummyKG())
        app = Flask(__name__)

        @app.route("/api/theories/suggest")
        def suggest():
            return jsonify(self.engine.suggest_theories())

        @app.route("/api/theories/graph")
        def graph():
            nodes, edges = self.engine.get_theory_subgraph(request.args.get("cause", ""))
            return jsonify({"nodes": nodes, "edges": edges})

        self.client = app.test_client()

    def tearDown(self):
        self.engine.close()

    def test_theories_suggest_endpoint(self):
        resp = self.client.get("/api/theories/suggest")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIsInstance(data, list)
        self.assertTrue(any(t["cause"] == "Breach of Contract" for t in data))

    def test_theories_graph_endpoint(self):
        resp = self.client.get("/api/theories/graph?cause=Fraud")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("nodes", data)
        self.assertIn("edges", data)


if __name__ == "__main__":
    unittest.main()
