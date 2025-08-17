from __future__ import annotations
from flask import Blueprint, request, jsonify
from flask_socketio import emit, join_room
from ..extensions import socketio
from ..database import db
from ..models_trial import TranscriptSegment, ObjectionEvent
from .services.objection_engine import engine

bp = Blueprint("trial_assistant", __name__, url_prefix="/api/trial")


@bp.post("/objection/action")
def objection_action():
    payload = request.json or {}
    evt_id = payload.get("event_id")
    action = payload.get("action")
    if not evt_id:
        return jsonify({"error": "event_id required"}), 400
    evt = db.session.get(ObjectionEvent, evt_id)
    if evt:
        evt.action_taken = action
        db.session.commit()
    return jsonify({"ok": True})


@socketio.on("join", namespace="/ws/trial")
def join(data):
    sess = data.get("session_id")
    if sess:
        join_room(sess)


@socketio.on("segment", namespace="/ws/trial")
def handle_segment(data):
    session_id = data.get("session_id")
    text = data.get("text", "")
    seg = TranscriptSegment(
        session_id=session_id,
        text=text,
        t0_ms=data.get("t0_ms"),
        t1_ms=data.get("t1_ms"),
        speaker=data.get("speaker"),
        confidence=data.get("confidence"),
    )
    db.session.add(seg)
    db.session.commit()
    emit(
        "transcript_update",
        {
            "segment_id": seg.id,
            "speaker": seg.speaker,
            "text": seg.text,
            "t0_ms": seg.t0_ms,
            "t1_ms": seg.t1_ms,
        },
        room=session_id,
    )
    events = engine.analyze_segment(session_id, seg)
    for e in events:
        emit(
            "objection_event",
            {
                "event_id": e.id,
                "segment_id": e.segment_id,
                "ground": e.ground,
                "confidence": e.confidence,
                "suggested_cures": e.suggested_cures,
            },
            room=session_id,
        )
