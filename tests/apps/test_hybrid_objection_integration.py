from flask import Flask

from apps.legal_discovery.database import db
from apps.legal_discovery.extensions import socketio
from apps.legal_discovery.hippo_routes import bp as hippo_bp, objections_bp
from apps.legal_discovery.trial_assistant import bp as trial_bp
from apps.legal_discovery.models import RetrievalTrace
from apps.legal_discovery.models_trial import TrialSession
from apps.legal_discovery import hippo


def _create_app():
    app = Flask(__name__)
    app.config.update(
        SQLALCHEMY_DATABASE_URI="sqlite://",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    db.init_app(app)
    socketio.init_app(app, logger=False, engineio_logger=False)
    app.register_blueprint(hippo_bp)
    app.register_blueprint(trial_bp)
    app.register_blueprint(objections_bp)
    with app.app_context():
        db.create_all()
    return app


def test_hybrid_retrieval_path_and_objection_refs():
    app = _create_app()
    client = app.test_client()
    # Seed small graph via hippo indexing
    hippo.INDEX.clear()
    client.post(
        "/api/hippo/index",
        json={"case_id": "c1", "text": "Alice met Bob at Acme."},
    )
    res = client.post(
        "/api/hippo/query",
        json={"case_id": "c1", "query": "Bob"},
    )
    assert res.status_code == 200
    first = res.get_json()["items"][0]
    assert first["path"][0]["type"] == "Document"
    assert any(n["type"] == "Entity" for n in first["path"])
    assert first["path"][-1]["type"] == "Segment"

    # Prepare trial session and analyze segment for objections
    sock = socketio.test_client(app, namespace="/ws/trial")
    sock.emit("join", {"session_id": "trial_objections"}, namespace="/ws/trial")
    with app.app_context():
        hippo.INDEX.clear()
        hippo.ingest_document("c1", "this is hearsay evidence", "doc.txt")
        sess = TrialSession(id="s1", case_id="c1")
        db.session.add(sess)
        db.session.commit()
    res2 = client.post(
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
    assert res2.status_code == 200
    received = sock.get_received("/ws/trial")
    assert any(r["name"] == "objection_event" and r["args"][0]["refs"] for r in received)
    with app.app_context():
        traces = db.session.query(RetrievalTrace).all()
        assert any(t.results for t in traces)
