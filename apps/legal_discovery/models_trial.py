from __future__ import annotations
from datetime import datetime
import uuid
from .database import db


def uuid4() -> str:
    return str(uuid.uuid4())


class TrialSession(db.Model):
    __tablename__ = "trial_sessions"
    id = db.Column(db.String, primary_key=True, default=uuid4)
    case_id = db.Column(db.String, index=True, nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime)
    mode = db.Column(db.String, default="guidance")
    local_only = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.String, index=True)


class TranscriptSegment(db.Model):
    __tablename__ = "transcript_segments"
    id = db.Column(db.String, primary_key=True, default=uuid4)
    session_id = db.Column(db.String, db.ForeignKey("trial_sessions.id"), index=True)
    t0_ms = db.Column(db.Integer)
    t1_ms = db.Column(db.Integer)
    speaker = db.Column(db.String)
    text = db.Column(db.Text)
    confidence = db.Column(db.Integer)
    privilege = db.Column(db.Boolean, default=False)
    meta = db.Column(db.JSON)
    session = db.relationship("TrialSession", backref="segments")


class TrialNote(db.Model):
    __tablename__ = "trial_notes"
    id = db.Column(db.String, primary_key=True, default=uuid4)
    session_id = db.Column(db.String, db.ForeignKey("trial_sessions.id"), index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.String, index=True)
    text = db.Column(db.Text)
    tags = db.Column(db.JSON)
    link = db.Column(db.JSON)


class PresentationEvent(db.Model):
    __tablename__ = "presentation_events"
    id = db.Column(db.String, primary_key=True, default=uuid4)
    session_id = db.Column(db.String, index=True)
    ts = db.Column(db.DateTime, default=datetime.utcnow)
    command = db.Column(db.String)
    payload = db.Column(db.JSON)
    issued_by = db.Column(db.String, index=True)


class StrategySuggestion(db.Model):
    __tablename__ = "strategy_suggestions"
    id = db.Column(db.String, primary_key=True, default=uuid4)
    session_id = db.Column(db.String, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    kind = db.Column(db.String)
    text = db.Column(db.Text)
    rationale = db.Column(db.Text)
    refs = db.Column(db.JSON)
    confidence = db.Column(db.Integer)


class ObjectionEvent(db.Model):
    __tablename__ = "objection_events"
    id = db.Column(db.String, primary_key=True, default=uuid4)
    session_id = db.Column(db.String, index=True)
    segment_id = db.Column(db.String, index=True)
    ts = db.Column(db.DateTime, default=datetime.utcnow)
    type = db.Column(db.String)
    ground = db.Column(db.String)
    confidence = db.Column(db.Integer)
    extracted_phrase = db.Column(db.String)
    suggested_cures = db.Column(db.JSON)
    action_taken = db.Column(db.String)
    outcome = db.Column(db.String)
