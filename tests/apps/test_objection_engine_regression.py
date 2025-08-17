from flask import Flask

from apps.legal_discovery.database import db
from apps.legal_discovery.models_trial import (
    TrialSession,
    TranscriptSegment,
    ObjectionEvent,
)
from apps.legal_discovery.trial_assistant.services.objection_engine import (
    ObjectionEngine,
)


def _create_app():
    app = Flask(__name__)
    app.config.update(
        SQLALCHEMY_DATABASE_URI="sqlite://",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    db.init_app(app)
    with app.app_context():
        db.create_all()
    return app


def test_objection_engine_detects_hearsay():
    app = _create_app()
    engine = ObjectionEngine()
    with app.app_context():
        sess = TrialSession(id="s", case_id="1")
        seg = TranscriptSegment(
            session_id="s",
            t0_ms=0,
            t1_ms=1,
            speaker="lawyer",
            text="objection hearsay",
            confidence=100,
        )
        db.session.add_all([sess, seg])
        db.session.commit()
        events = engine.analyze_segment("s", seg)
        assert any(e.ground == "hearsay" for e in events)
        assert ObjectionEvent.query.count() == 1
        clean_seg = TranscriptSegment(
            session_id="s",
            t0_ms=1,
            t1_ms=2,
            speaker="lawyer",
            text="no objection here",
            confidence=100,
        )
        db.session.add(clean_seg)
        db.session.commit()
        assert engine.analyze_segment("s", clean_seg) == []


