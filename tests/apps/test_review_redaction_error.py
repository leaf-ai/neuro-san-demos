import importlib
import logging
import os

import pytest


def test_review_redaction_copy_failure(monkeypatch, caplog, tmp_path):
    monkeypatch.setenv("FLASK_SECRET_KEY", "test")
    monkeypatch.setenv("JWT_SECRET", "test")
    monkeypatch.setenv("DATABASE_URL", "sqlite://")
    ifl = importlib.import_module("apps.legal_discovery.interface_flask")
    ifl.socketio.stop = lambda *a, **kw: None
    ifl.app.config["SECURE_FOLDER"] = str(tmp_path)
    with ifl.app.app_context():
        case = ifl.Case(name="case")
        ifl.db.session.add(case)
        ifl.db.session.commit()
        doc = ifl.Document(
            case_id=case.id,
            name="doc.txt",
            file_path=str(tmp_path / "doc.txt"),
            sha256="hash",
            source=ifl.DocumentSource.USER,
        )
        ifl.db.session.add(doc)
        ifl.db.session.commit()
        doc_id = doc.id
    def _raise(*args, **kwargs):
        raise OSError("boom")
    monkeypatch.setattr(ifl.shutil, "copy", _raise)
    with caplog.at_level(logging.ERROR):
        resp = ifl.app.test_client().post(
            f"/api/redaction/{doc_id}",
            json={"action": "override", "reviewer": "r", "reason": "r"},
        )
    assert resp.status_code == 500
    assert "failed to restore original file" in caplog.text
