from flask import Flask
import base64

from apps.legal_discovery.extensions import socketio, limiter
from apps.legal_discovery.database import db
from apps.legal_discovery.chat_routes import chat_bp


def _create_app():
    app = Flask(__name__)
    app.config.update(
        JWT_SECRET="secret",
        SQLALCHEMY_DATABASE_URI="sqlite://",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        RATELIMIT_ENABLED=False,
    )
    db.init_app(app)
    socketio.init_app(app, logger=False, engineio_logger=False)
    limiter.init_app(app)
    app.register_blueprint(chat_bp)
    with app.app_context():
        db.create_all()
    return app


def test_voice_ws_transcript_updates(monkeypatch):
    app = _create_app()
    monkeypatch.setattr(
        "apps.legal_discovery.chat_routes._require_auth", lambda: True
    )
    monkeypatch.setattr(
        "apps.legal_discovery.chat_routes._ensure_listeners_started", lambda: None
    )

    def fake_stream(_):
        yield {"text": "hi", "is_final": False}
        yield {"text": "bye", "is_final": True}

    monkeypatch.setattr(
        "apps.legal_discovery.chat_routes.stream_transcribe", fake_stream
    )
    monkeypatch.setattr(
        "apps.legal_discovery.chat_routes._handle_transcript", lambda t, d: {}
    )

    client = socketio.test_client(app, namespace="/chat")
    client.emit(
        "voice_query",
        {"frames": [base64.b64encode(b"a").decode("utf-8")]},
        namespace="/chat",
    )
    received = client.get_received("/chat")
    assert any(
        r["name"] == "voice_transcript" and r["args"][0]["text"] == "hi" and not r["args"][0]["final"]
        for r in received
    )
    assert any(
        r["name"] == "voice_transcript" and r["args"][0]["text"] == "bye" and r["args"][0]["final"]
        for r in received
    )



def test_voice_ws_auth_error(monkeypatch):
    app = _create_app()
    monkeypatch.setattr(
        "apps.legal_discovery.chat_routes._ensure_listeners_started", lambda: None
    )
    client = socketio.test_client(app, namespace="/chat")
    client.emit("voice_query", {"frames": [""]}, namespace="/chat")
    received = client.get_received("/chat")
    assert any(
        r["name"] == "voice_error" and r["args"][0]["error"] == "unauthorized"
        for r in received
    )
