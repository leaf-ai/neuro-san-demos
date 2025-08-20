import os
import pytest
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite://"
os.environ.setdefault("FLASK_SECRET_KEY", "test")
os.environ.setdefault("JWT_SECRET", "test")

from apps.legal_discovery.interface_flask import app, db


@pytest.fixture
def client(monkeypatch):
    with app.app_context():
        db.drop_all()
        db.create_all()
    def fake_export(self, case_id, path):
        Path(path).write_text("test")
        return path
    monkeypatch.setattr("apps.legal_discovery.binder_routes.PretrialGenerator.export", fake_export)
    return app.test_client()


def test_pretrial_export(client):
    resp = client.post("/api/binder/pretrial/export", json={"case_id": 1})
    assert resp.status_code == 200
    assert "path" in resp.json
