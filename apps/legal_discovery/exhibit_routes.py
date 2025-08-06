"""Blueprint exposing REST endpoints for exhibit operations."""
from __future__ import annotations

import os
from pathlib import Path

from flask import Blueprint, jsonify, request, current_app
from PyPDF2 import PdfReader

from .database import db
from .models import Document, ChainOfCustodyLog, DocumentSource
from .exhibit_manager import assign_exhibit_number, generate_binder, export_zip

exhibits_bp = Blueprint("exhibits", __name__, url_prefix="/api/exhibits")


@exhibits_bp.route("", methods=["GET"])
@exhibits_bp.route("/", methods=["GET"])
def list_exhibits():
    """Return all exhibits for a given case."""
    case_id = request.args.get("case_id", type=int)
    if case_id is None:
        return jsonify({"error": "case_id required"}), 400
    include_priv = request.args.get("include_privileged", "false").lower() == "true"
    source = request.args.get("source")
    source_team = request.args.get("source_team")
    query = Document.query.filter_by(case_id=case_id, is_exhibit=True)
    if not include_priv:
        query = query.filter_by(is_privileged=False)
    if source:
        try:
            query = query.filter_by(source=DocumentSource(source))
        except ValueError:
            pass
    if source_team:
        query = (
            query.join(Document.chain_logs)
            .filter(ChainOfCustodyLog.source_team == source_team)
            .distinct()
        )
    exhibits = query.order_by(Document.exhibit_order, Document.exhibit_number).all()
    data = []
    for ex in exhibits:
        try:
            pages = len(PdfReader(ex.file_path).pages)
        except Exception:  # pylint: disable=broad-except
            pages = 0
        data.append(
            {
                "id": ex.id,
                "exhibit_number": ex.exhibit_number,
                "order": ex.exhibit_order,
                "title": ex.exhibit_title,
                "bates_number": ex.bates_number,
                "page_count": pages,
                "privileged": ex.is_privileged,
                "source": ex.source.value if ex.source else None,
            }
        )
    return jsonify(data)


@exhibits_bp.route("/<int:doc_id>/links", methods=["GET"])
def exhibit_links(doc_id: int):
    """Return legal theories and timeline nodes linked to an exhibit."""
    doc = Document.query.get_or_404(doc_id)
    theories = sorted({f.legal_theory.theory_name for f in doc.facts if f.legal_theory})
    timeline = []
    for fact in doc.facts:
        for date in fact.dates or []:
            timeline.append({"date": date, "text": fact.text})
    return jsonify({"theories": theories, "timeline": timeline})


@exhibits_bp.post("/assign")
def assign():
    """Assign the next exhibit number to a document."""
    payload = request.get_json() or {}
    doc_id = payload.get("document_id")
    title = payload.get("title")
    user = payload.get("user")
    if not doc_id:
        return jsonify({"error": "document_id required"}), 400
    num = assign_exhibit_number(doc_id, title, user)
    return jsonify({"exhibit_number": num})


@exhibits_bp.post("/reorder")
def reorder():
    """Update exhibit order based on provided list of IDs."""
    payload = request.get_json() or {}
    case_id = payload.get("case_id")
    order_list = payload.get("order")
    if case_id is None or not isinstance(order_list, list):
        return jsonify({"error": "case_id and order list required"}), 400
    exhibits = {
        ex.id: ex
        for ex in Document.query.filter_by(case_id=case_id, is_exhibit=True).all()
    }
    for idx, ex_id in enumerate(order_list, start=1):
        ex = exhibits.get(ex_id)
        if ex:
            ex.exhibit_order = idx
    db.session.commit()
    return jsonify({"status": "ok"})


@exhibits_bp.post("/binder")
def binder():
    """Generate a combined PDF binder for the case exhibits."""
    payload = request.get_json() or {}
    case_id = payload.get("case_id")
    if not case_id:
        return jsonify({"error": "case_id required"}), 400
    export_dir = Path(current_app.config.get("UPLOAD_FOLDER", "uploads"))
    export_dir.mkdir(parents=True, exist_ok=True)
    target = export_dir / f"case_{case_id}_binder.pdf"
    path = generate_binder(case_id, target)
    return jsonify({"binder_path": f"/uploads/{target.name}", "path": path})


@exhibits_bp.post("/zip")
def zip_export():
    """Export exhibits and manifest as a zip archive."""
    payload = request.get_json() or {}
    case_id = payload.get("case_id")
    if not case_id:
        return jsonify({"error": "case_id required"}), 400
    export_dir = Path(current_app.config.get("UPLOAD_FOLDER", "uploads"))
    export_dir.mkdir(parents=True, exist_ok=True)
    target = export_dir / f"case_{case_id}_exhibits.zip"
    path = export_zip(case_id, target)
    return jsonify({"zip_path": f"/uploads/{target.name}", "path": path})
