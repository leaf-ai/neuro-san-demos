from __future__ import annotations
from flask import Blueprint, request, jsonify
from flask_socketio import emit, join_room
import time
from ..extensions import socketio
from ..database import db, log_retrieval_trace
from ..models_trial import (
    TranscriptSegment,
    ObjectionEvent,
    ObjectionResolution,
    TrialSession,
)
from .. import hippo
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
    refs: list = []
    trace_id = None
    sess = db.session.get(TrialSession, session_id)
    if sess:
        try:
            start = time.perf_counter()
            result = hippo.hippo_query(sess.case_id, text, k=3)
            elapsed_ms = (time.perf_counter() - start) * 1000
            items = result.get("items", [])
            trace_id = result.get("trace_id")
            refs = [
                {"segment_id": item.get("segment_id"), "path": item.get("path")}
                for item in items
            ]
            timings = {"total_ms": round(elapsed_ms, 2)}
            log_retrieval_trace(
                trace_id=trace_id,
                case_id=sess.case_id,
                query=text,
                graph_weight=1.0,
                dense_weight=1.0,
                timings=timings,
                results=items,
            )
        except Exception:  # pragma: no cover - best effort
            pass
    for e in events:
        e.refs = refs
        e.trace_id = trace_id
        e.path = refs[0]["path"] if refs else None
    db.session.commit()
    for e in events:
        emit(
            "objection_event",
            {
                "event_id": e.id,
                "segment_id": e.segment_id,
                "ground": e.ground,
                "confidence": e.confidence,
                "suggested_cures": e.suggested_cures,
                "refs": e.refs,
                "trace_id": e.trace_id,
            },
            room=session_id,
        )


@socketio.on("objection_cure_chosen", namespace="/ws/trial")
def cure_chosen(data):
    evt_id = data.get("event_id")
    cure = data.get("cure")
    if not evt_id:
        return
    resolution = ObjectionResolution(event_id=evt_id, chosen_cure=cure)
    db.session.add(resolution)
    db.session.commit()
    evt = db.session.get(ObjectionEvent, evt_id)
    if evt:
        emit(
            "clear_highlights",
            {"segment_id": evt.segment_id},
            room="trial_objections",
        )
