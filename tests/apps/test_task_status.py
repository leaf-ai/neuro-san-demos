import os
import pytest
from flask import Flask

from apps.legal_discovery import tasks

os.environ.setdefault("FLASK_SECRET_KEY", "test")
os.environ.setdefault("JWT_SECRET", "test")


@pytest.fixture
def client():
    app = Flask(__name__)
    app.secret_key = "test"
    app.config["JWT_SECRET"] = "test"
    app.register_blueprint(tasks.tasks_bp)
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["user"] = "tester"
    return client


def test_task_status_missing_id(client, monkeypatch):
    monkeypatch.setattr(tasks, "queue", object())
    monkeypatch.setattr(tasks, "redis_conn", object())

    class MissingJob:
        @classmethod
        def fetch(cls, job_id, connection=None):
            raise tasks.NoSuchJobError

    monkeypatch.setattr(tasks, "Job", MissingJob)
    resp = client.get("/api/tasks/does-not-exist")
    assert resp.status_code == 404
    assert resp.get_json() == {"status": "unknown", "error": "task not found"}


def test_task_status_malformed_id(client, monkeypatch):
    monkeypatch.setattr(tasks, "queue", object())
    monkeypatch.setattr(tasks, "redis_conn", object())

    class BadJob:
        @classmethod
        def fetch(cls, job_id, connection=None):
            raise ValueError("bad id")

    monkeypatch.setattr(tasks, "Job", BadJob)
    resp = client.get("/api/tasks/!!!")
    assert resp.status_code == 500
    data = resp.get_json()
    assert data["status"] == "unknown"
    assert data["error"] == "lookup failed"
