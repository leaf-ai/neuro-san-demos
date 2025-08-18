import logging
import time
from flask import Blueprint, jsonify, request

from . import hippo
from .database import db, log_retrieval_trace
from .extensions import socketio
from .models_trial import TranscriptSegment, TrialSession
from .trial_assistant.services.objection_engine import engine

bp = Blueprint("objections", __name__, url_prefix="/api/objections")
logger = logging.getLogger(__name__)


@bp.post("/analyze-segment")
def analyze_segment():
    data = request.get_json() or {}
    session_id = data.get("session_id")
    text = data.get("text", "")
    if not session_id or not text:
        return jsonify({"error": "session_id and text required"}), 400
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
    events = engine.analyze_segment(session_id, seg)
    refs: list = []
    trace_id = None
    try:
        sess = db.session.get(TrialSession, session_id)
        if sess:
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
    except Exception as exc:  # pragma: no cover - retrieval is best effort
        logger.exception("hippo_query failed: %s", exc)
    for e in events:
        e.refs = refs
        e.trace_id = trace_id
        e.path = refs[0]["path"] if refs else None
    db.session.commit()
    for e in events:
        socketio.emit(
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
            room="trial_objections",
            namespace="/ws/trial",
        )
    return jsonify({"events": [e.id for e in events], "segment_id": seg.id})
