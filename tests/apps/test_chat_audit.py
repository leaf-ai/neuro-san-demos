import base64
import os
import pytest

os.environ["DATABASE_URL"] = "sqlite://"

from apps.legal_discovery.interface_flask import app, db, MessageAuditLog


@pytest.fixture
def client():
    with app.app_context():
        db.drop_all()
        db.create_all()
    return app.test_client()


def test_query_logs_message(client):
    resp = client.post("/api/query", json={"text": "hello"})
    assert resp.status_code == 200
    with app.app_context():
        logs = MessageAuditLog.query.all()
        assert any(l.sender == "user" and l.transcript == "hello" for l in logs)


def test_voice_query_logs_message(client, monkeypatch):
    monkeypatch.setattr(
        "apps.legal_discovery.interface_flask.synthesize_voice", lambda text, model: ""
    )
    audio = base64.b64encode(b"test").decode()
    resp = client.post(
        "/api/voice_query",
        json={"audio": audio, "transcript": "hi", "voice_model": "en-US"},
    )
    assert resp.status_code == 200
    with app.app_context():
        log = MessageAuditLog.query.filter_by(transcript="hi").first()
        assert log is not None
        assert log.voice_model == "en-US"
