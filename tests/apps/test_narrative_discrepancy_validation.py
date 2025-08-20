import os

os.environ.setdefault("FLASK_SECRET_KEY", "test")
os.environ.setdefault("JWT_SECRET", "test")

from apps.legal_discovery.interface_flask import app


def test_narrative_discrepancy_validation():
    client = app.test_client()
    res = client.post("/api/narrative_discrepancies/analyze", json={"foo": 1})
    assert res.status_code == 400
    assert res.json["errors"][0]["loc"] == ["opposing_doc_id"]
