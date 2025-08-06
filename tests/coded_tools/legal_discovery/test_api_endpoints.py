import unittest
import os
import tempfile
from flask import Flask, jsonify, request
from coded_tools.legal_discovery.legal_theory_engine import LegalTheoryEngine
from coded_tools.legal_discovery.document_drafter import DocumentDrafter
from coded_tools.legal_discovery.pretrial_generator import PretrialGenerator
from coded_tools.legal_discovery.timeline_manager import TimelineManager


class DummyKG:
    def run_query(self, query, params):
        if params["element"] == "Existence of a contract":
            return [
                {
                    "text": "Contract between A and B",
                    "weight": 1.0,
                    "dates": ["2024-01-01"],
                }
            ]
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

        @app.route("/api/theories/accept", methods=["POST"])
        def accept():
            data = request.get_json() or {}
            cause = data.get("cause")
            theories = self.engine.suggest_theories()
            theory = next((t for t in theories if t["cause"] == cause), None)
            drafter = DocumentDrafter()
            path = os.path.join(tempfile.gettempdir(), "test_theory.docx")
            drafter.create_document(path, cause)
            pretrial = PretrialGenerator()
            statement = pretrial.generate_statement(cause, [e["name"] for e in theory["elements"]])
            timeline = TimelineManager()
            timeline.create_timeline(cause, [])
            return jsonify({"document": path, "pretrial": statement, "timeline_items": []})

        @app.route("/api/theories/reject", methods=["POST"])
        def reject():
            return jsonify({"status": "ok"})

        @app.route("/api/theories/comment", methods=["POST"])
        def comment():
            data = request.get_json() or {}
            return jsonify({"status": "ok", "comment": data.get("comment")})

        self.client = app.test_client()

    def tearDown(self):
        self.engine.close()

    def test_theories_suggest_endpoint(self):
        resp = self.client.get("/api/theories/suggest")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIsInstance(data, list)
        breach = next(t for t in data if t["cause"] == "Breach of Contract")
        self.assertIn("missing_elements", breach)

    def test_theories_graph_endpoint(self):
        resp = self.client.get("/api/theories/graph?cause=Fraud")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("nodes", data)
        self.assertIn("edges", data)

    def test_theories_accept_endpoint(self):
        resp = self.client.post("/api/theories/accept", json={"cause": "Breach of Contract"})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("document", data)
        self.assertIn("pretrial", data)
        self.assertIn("timeline_items", data)

    def test_theories_reject_endpoint(self):
        resp = self.client.post("/api/theories/reject", json={"cause": "Breach of Contract"})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "ok")

    def test_theories_comment_endpoint(self):
        resp = self.client.post(
            "/api/theories/comment", json={"cause": "Breach of Contract", "comment": "test"}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["comment"], "test")


if __name__ == "__main__":
    unittest.main()
