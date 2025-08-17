from flask import Flask

from apps.legal_discovery.extensions import socketio
from apps.legal_discovery.database import db
from apps.legal_discovery.trial_assistant import bp
from apps.legal_discovery.models_trial import ObjectionEvent


def _create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    socketio.init_app(app, logger=False, engineio_logger=False)
    app.register_blueprint(bp)
    with app.app_context():
        db.create_all()
    return app


def test_objection_event_emitted_and_persisted():
    app = _create_app()
    client = socketio.test_client(app, namespace="/ws/trial")
    client.emit("join", {"session_id": "s"}, namespace="/ws/trial")
    client.emit(
        "segment",
        {
            "session_id": "s",
            "text": "that's hearsay",
            "t0_ms": 0,
            "t1_ms": 1,
            "speaker": "witness",
            "confidence": 100,
        },
        namespace="/ws/trial",
    )
    received = client.get_received("/ws/trial")
    assert any(
        r["name"] == "objection_event" and "segment_id" in r["args"][0]
        for r in received
    )
    with app.app_context():
        assert ObjectionEvent.query.count() == 1

