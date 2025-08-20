from flask import Flask

from apps.legal_discovery.extensions import socketio, limiter
from apps.legal_discovery.database import db
from apps.legal_discovery.chat_routes import chat_bp
from apps.message_bus import TIMELINE_ALERT_TOPIC


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


def test_voice_command_routing_and_bus(monkeypatch):
    app = _create_app()

    monkeypatch.setattr(
        "apps.legal_discovery.chat_routes._ensure_listeners_started", lambda: None
    )
    monkeypatch.setattr(
        "apps.legal_discovery.auth._require_auth", lambda: True
    )

    publish_calls = []

    def fake_publish(topic, message):
        publish_calls.append((topic, message.payload))

    monkeypatch.setattr(
        "apps.legal_discovery.chat_routes.bus.publish", fake_publish
    )
    monkeypatch.setattr(
        "apps.legal_discovery.chat_routes.synthesize_voice",
        lambda text, model: "audio",
    )

    class DummyAgent:
        def query(self, **kwargs):
            return {"answer": "ok", "message_id": 1}

    monkeypatch.setattr(
        "apps.legal_discovery.chat_routes.RetrievalChatAgent", DummyAgent
    )

    class DummyTM:
        def summarize(self, case_id: int) -> str:  # pragma: no cover - trivial
            return "summary"

    monkeypatch.setattr(
        "apps.legal_discovery.voice_commands.TimelineManager", DummyTM
    )

    with app.test_client() as client:
        resp = client.post(
            "/api/chat/voice",
            json={"transcript": "timeline summary please", "case_id": 1},
        )

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["command"] == "timeline summary"
    assert data["result"] == "summary"
    assert any(t == TIMELINE_ALERT_TOPIC for t, _ in publish_calls)


def test_voice_query_auth_error(monkeypatch):
    app = _create_app()
    monkeypatch.setattr(
        "apps.legal_discovery.chat_routes._ensure_listeners_started", lambda: None
    )
    with app.test_client() as client:
        resp = client.post("/api/chat/voice", json={"transcript": "hi"})
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "unauthorized"


