"""Flask blueprint exposing minimal HippoRAG endpoints."""
from __future__ import annotations

import logging
import time
import uuid

from flask import Blueprint, jsonify, request

from . import hippo, bootstrap_graph
from .database import log_retrieval_trace

bootstrap_graph()

bp = Blueprint("hippo", __name__, url_prefix="/api/hippo")

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
