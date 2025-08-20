import os
import sys
import pathlib
import pytest

os.environ["DATABASE_URL"] = "sqlite://"
os.environ.setdefault("FLASK_SECRET_KEY", "test")
os.environ.setdefault("JWT_SECRET", "test")
sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))

from apps.legal_discovery.interface_flask import app, db, Case, TimelineEvent


@pytest.fixture
def client():
    with app.app_context():
        db.drop_all()
        db.create_all()
        case = Case(name="Test")
        db.session.add(case)
        db.session.commit()
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["user"] = "tester"
    return client


def test_chat_creates_timeline_event(client):
    resp = client.post(
        "/api/chat/query",
        json={"text": "case:1 2024-01-01 Filing made [dep:1] [ex:2] [theory:3]"},
    )
    assert resp.status_code == 200
    with app.app_context():
        event = TimelineEvent.query.filter_by(case_id=1).first()
        assert event is not None
        assert event.description == "Filing made"
        assert event.links["depositions"] == [1]
        assert event.links["exhibits"] == [2]
        assert event.links["legal_theories"] == [3]


def test_timeline_summary(client):
    client.post("/api/chat/query", json={"text": "case:1 2024-02-02 Hearing"})
    resp = client.get("/api/timeline/summary", query_string={"case_id": 1})
    assert resp.status_code == 200
    assert "2024-02-02" in resp.json["summary"]
