from flask import Flask
import pytest

from apps.legal_discovery.extensions import socketio
from apps.legal_discovery.database import db
from apps.legal_discovery.trial_assistant import bp as trial_bp
from apps.legal_discovery.hippo_routes import bp as hippo_bp, objections_bp
from apps.legal_discovery import hippo
from apps.legal_discovery.models import ObjectionEvent
from apps.legal_discovery.models_trial import TrialSession
from apps.legal_discovery import auth as auth_module


@pytest.fixture(autouse=True)
def _no_auth(monkeypatch):
    monkeypatch.setattr(auth_module, "_require_auth", lambda: True)


def _create_app() -> Flask:
    app = Flask(__name__)
    app.config.update(
        SQLALCHEMY_DATABASE_URI="sqlite://",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    db.init_app(app)
    socketio.init_app(app, logger=False, engineio_logger=False)
    app.register_blueprint(hippo_bp)
    app.register_blueprint(objections_bp)
    app.register_blueprint(trial_bp)
    with app.app_context():
        db.create_all()
    return app


def _seed_fixture_graph() -> None:
    hippo.INDEX.clear()
    hippo.ingest_document("c1", "this is hearsay evidence", "doc.txt")


def test_query_returns_items_with_paths():
    app = _create_app()
    _seed_fixture_graph()
    client = app.test_client()
    res = client.post(
        "/api/hippo/query",
        json={"case_id": "c1", "query": "hearsay"},
    )
    assert res.status_code == 200
    items = res.get_json()["items"]
    assert items and items[0]["path"]


def test_objection_events_persist_with_refs():
    app = _create_app()
    _seed_fixture_graph()
    client = app.test_client()
    sock = socketio.test_client(app, namespace="/ws/trial")
    sock.emit("join", {"session_id": "s1"}, namespace="/ws/trial")
    with app.app_context():
        db.session.add(TrialSession(id="s1", case_id="c1"))
        db.session.commit()
    res = client.post(
        "/api/objections/analyze-segment",
        json={
            "session_id": "s1",
            "text": "that's hearsay",
            "t0_ms": 0,
            "t1_ms": 1,
            "speaker": "witness",
            "confidence": 100,
        },
    )
    assert res.status_code == 200
    with app.app_context():
        evt = ObjectionEvent.query.one()
        assert evt.refs and evt.path
