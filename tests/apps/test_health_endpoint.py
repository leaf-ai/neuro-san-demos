"""Unit tests for health endpoint."""

from flask import Flask

from apps.legal_discovery.hippo_routes import health_bp


def test_health_endpoint_returns_status_keys():
    app = Flask(__name__)
    app.register_blueprint(health_bp)
    client = app.test_client()
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert set(data.keys()) == {"neo4j", "chroma", "blocked_requests"}
