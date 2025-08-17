"""Flask blueprint exposing minimal HippoRAG endpoints."""
from __future__ import annotations

from flask import Blueprint, jsonify, request

from . import hippo

bp = Blueprint("hippo", __name__, url_prefix="/api/hippo")


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
    if not case_id:
        return jsonify({"error": "case_id required"}), 400
    return jsonify(hippo.hippo_query(case_id, query, k=k))
