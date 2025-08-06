import os
from flask import Blueprint, jsonify, request, current_app

from coded_tools.legal_discovery.document_drafter import DocumentDrafter
from coded_tools.legal_discovery.pretrial_generator import PretrialGenerator
from coded_tools.legal_discovery.timeline_manager import TimelineManager
from coded_tools.legal_discovery.legal_theory_engine import LegalTheoryEngine

from .database import db
from .models import LegalTheory


theories_bp = Blueprint("theories", __name__, url_prefix="/api/theories")


@theories_bp.get("/suggest")
def suggest_theories():
    """Return ranked legal theory candidates."""
    engine = LegalTheoryEngine()
    theories = engine.suggest_theories()
    engine.close()
    return jsonify({"status": "ok", "theories": theories})


@theories_bp.get("/graph")
def theory_graph():
    """Return graph data for a specific cause of action."""
    cause = request.args.get("cause")
    if not cause:
        return jsonify({"status": "error", "error": "cause required"}), 400
    engine = LegalTheoryEngine()
    nodes, edges = engine.get_theory_subgraph(cause)
    engine.close()
    return jsonify({"status": "ok", "nodes": nodes, "edges": edges})


@theories_bp.post("/accept")
def accept_theory():
    """Pipe an accepted theory to drafting, pretrial and timeline tools."""

    data = request.get_json() or {}
    cause = data.get("cause")
    if not cause:
        return jsonify({"status": "error", "error": "cause required"}), 400

    engine = LegalTheoryEngine()
    try:
        theories = engine.suggest_theories()
        theory = next((t for t in theories if t["cause"] == cause), None)
        if theory is None:
            return jsonify({"status": "error", "error": "unknown cause"}), 404

        drafter = DocumentDrafter()
        upload_dir = current_app.config.get("UPLOAD_FOLDER", "uploads")
        doc_path = os.path.join(upload_dir, f"{cause.replace(' ', '_')}_theory.docx")
        drafter.create_document(doc_path, f"Accepted theory: {cause}")

        pretrial = PretrialGenerator()
        statement = pretrial.generate_statement(cause, [e["name"] for e in theory["elements"]])

        timeline_items: list[dict] = []
        for element in theory["elements"]:
            for fact in element["facts"]:
                for date in fact.get("dates", []):
                    timeline_items.append({"date": date, "description": fact["text"]})

        timeline_manager = TimelineManager()
        if timeline_items:
            timeline_manager.create_timeline(cause, timeline_items)

        lt = LegalTheory.query.filter_by(theory_name=cause, case_id=1).first()
        if lt is None:
            lt = LegalTheory(case_id=1, theory_name=cause)
            db.session.add(lt)
        lt.status = "approved"
        if data.get("comment"):
            lt.review_comment = data.get("comment")
        db.session.commit()

        return jsonify(
            {
                "status": "ok",
                "document": doc_path,
                "pretrial": statement,
                "timeline_items": timeline_items,
            }
        )
    finally:
        engine.close()


@theories_bp.post("/reject")
def reject_theory():
    data = request.get_json() or {}
    cause = data.get("cause")
    if not cause:
        return jsonify({"status": "error", "error": "cause required"}), 400

    lt = LegalTheory.query.filter_by(theory_name=cause, case_id=1).first()
    if lt is None:
        lt = LegalTheory(case_id=1, theory_name=cause)
        db.session.add(lt)
    lt.status = "rejected"
    if data.get("comment"):
        lt.review_comment = data.get("comment")
    db.session.commit()
    return jsonify({"status": "ok"})


@theories_bp.post("/comment")
def comment_theory():
    data = request.get_json() or {}
    cause = data.get("cause")
    comment = data.get("comment")
    if not cause or comment is None:
        return jsonify({"status": "error", "error": "cause and comment required"}), 400

    lt = LegalTheory.query.filter_by(theory_name=cause, case_id=1).first()
    if lt is None:
        lt = LegalTheory(case_id=1, theory_name=cause)
        db.session.add(lt)
    lt.review_comment = comment
    db.session.commit()
    return jsonify({"status": "ok"})


__all__ = ["theories_bp"]
