"""Flask blueprint exposing minimal HippoRAG endpoints."""
from __future__ import annotations

import logging
import time
import uuid

from flask import Blueprint, jsonify, request

from . import hippo, bootstrap_graph
from .database import db, log_retrieval_trace
from .extensions import socketio
from .models_trial import (
    TranscriptSegment,
    TrialSession,
    ObjectionEvent,
    ObjectionResolution,
)
from .trial_assistant.services.objection_engine import engine

bootstrap_graph()

bp = Blueprint("hippo", __name__, url_prefix="/api/hippo")
objections_bp = Blueprint("objections", __name__, url_prefix="/api/objections")

logger = logging.getLogger(__name__)


@bp.post("/index")
def index_document():
    data = request.get_json() or {}
    case_id = data.get("case_id")
    text = data.get("text")
    path = data.get("doc_path", "")
    if not case_id or not text:
        return jsonify({"error": "case_id and text required"}), 400
    doc_id = hippo.ingest_document(case_id, text, path)
    segments = len(hippo.INDEX[case_id][doc_id])
    return jsonify({"doc_id": doc_id, "segments": segments})


@bp.post("/query")
def query_document():
    data = request.get_json() or {}
    case_id = data.get("case_id")
    query = data.get("query", "")
    k = int(data.get("k", 10))
    graph_weight = float(data.get("graph_weight", 1.0))
    dense_weight = float(data.get("dense_weight", 1.0))
    return_paths = data.get("return_paths", True)
    if not case_id:
        return jsonify({"error": "case_id required"}), 400

    overall_start = time.perf_counter()
    query_start = overall_start
    result = hippo.hippo_query(case_id, query, k=k)
    query_ms = (time.perf_counter() - query_start) * 1000

    items = result.get("items", [])
    format_start = time.perf_counter()
    for item in items:
        scores = item.get("scores", {})
        graph_score = scores.get("graph", 0) * graph_weight
        dense_score = scores.get("dense", 0) * dense_weight
        cross_score = scores.get("cross", 0)
        scores["graph"] = graph_score
        scores["dense"] = dense_score
        scores["hybrid"] = graph_score + dense_score + cross_score
        if not return_paths:
            item.pop("path", None)

    format_ms = (time.perf_counter() - format_start) * 1000
    total_ms = (time.perf_counter() - overall_start) * 1000

    items.sort(key=lambda r: r["scores"]["hybrid"], reverse=True)
    trace_id = uuid.uuid4().hex
    timings = {
        "query_ms": round(query_ms, 2),
        "format_ms": round(format_ms, 2),
        "total_ms": round(total_ms, 2),
    }

    log_retrieval_trace(
        trace_id=trace_id,
        case_id=case_id,
        query=query,
        graph_weight=graph_weight,
        dense_weight=dense_weight,
        timings=timings,
        results=items,
    )
    logger.info("hippo query trace %s %.2fms", trace_id, total_ms)

    return jsonify({"items": items, "trace_id": trace_id, "timings": timings})


@objections_bp.post("/analyze-segment")
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
    except Exception as exc:  # pragma: no cover - retrieval best effort
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


@socketio.on("objection_cure_chosen", namespace="/ws/trial")
def objection_cure_chosen(data):
    evt_id = data.get("event_id")
    cure = data.get("cure")
    if not evt_id:
        return
    resolution = ObjectionResolution(event_id=evt_id, chosen_cure=cure)
    db.session.add(resolution)
    db.session.commit()
    evt = db.session.get(ObjectionEvent, evt_id)
    if evt:
        socketio.emit(
            "clear_highlights",
            {"segment_id": evt.segment_id},
            room="trial_objections",
            namespace="/ws/trial",
        )
