from flask import Flask

from apps.legal_discovery.extensions import socketio
from apps.legal_discovery.database import db, RetrievalTrace
from apps.legal_discovery.trial_assistant import bp as trial_bp
from apps.legal_discovery.hippo_routes import objections_bp
from apps.legal_discovery.models_trial import (
    TrialSession,
    ObjectionEvent,
    ObjectionResolution,
    TranscriptSegment,
)
from apps.legal_discovery.trial_assistant.services.objection_engine import engine
from apps.legal_discovery import hippo


def _create_app():
    app = Flask(__name__)
    app.config.update(
        SQLALCHEMY_DATABASE_URI="sqlite://",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    db.init_app(app)
    socketio.init_app(app, logger=False, engineio_logger=False)
    app.register_blueprint(trial_bp)
    app.register_blueprint(objections_bp)
    with app.app_context():
        db.create_all()
    return app


def test_analyze_segment_emits_refs_and_persists():
    app = _create_app()
    client = app.test_client()
    sock = socketio.test_client(app, namespace="/ws/trial")
    sock.emit("join", {"session_id": "trial_objections"}, namespace="/ws/trial")
    with app.app_context():
        hippo.INDEX.clear()
        sess = TrialSession(id="s1", case_id="c1")
        db.session.add(sess)
        db.session.commit()
        hippo.ingest_document("c1", "this is hearsay evidence", "doc.txt")
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
    received = sock.get_received("/ws/trial")
    assert any(
        r["name"] == "objection_event" and r["args"][0]["refs"] for r in received
    )
    with app.app_context():
        evt = ObjectionEvent.query.one()
        trace = db.session.query(RetrievalTrace).one()
        assert evt.refs and evt.path
        assert evt.trace_id == trace.trace_id


def test_cure_chosen_records_resolution_and_clears_highlight():
    app = _create_app()
    sock = socketio.test_client(app, namespace="/ws/trial")
    sock.emit("join", {"session_id": "trial_objections"}, namespace="/ws/trial")
    with app.app_context():
        sess = TrialSession(id="s1", case_id="c1")
        seg = TranscriptSegment(
            session_id="s1",
            t0_ms=0,
            t1_ms=1,
            speaker="lawyer",
            text="objection hearsay",
            confidence=100,
        )
        db.session.add_all([sess, seg])
        db.session.commit()
        events = engine.analyze_segment("s1", seg)
        evt_id = events[0].id
    sock.emit(
        "objection_cure_chosen",
        {"event_id": evt_id, "cure": "rephrase"},
        namespace="/ws/trial",
    )
    received = sock.get_received("/ws/trial")
    assert any(r["name"] == "clear_highlights" for r in received)
    with app.app_context():
        assert ObjectionResolution.query.count() == 1
