"""Blueprint exposing REST endpoints for exhibit operations."""
from __future__ import annotations

from pathlib import Path

from flask import Blueprint, jsonify, request, current_app, session
from werkzeug.utils import secure_filename
from .chat_routes import auth_required
from PyPDF2 import PdfReader
from pydantic import ValidationError

from .validators import ExhibitAssignPayload

from .database import db
from .models import Case, ChainOfCustodyLog, Document, DocumentSource
from .exhibit_manager import assign_exhibit_number, export_zip
from .tasks import enqueue, binder_task

exhibits_bp = Blueprint("exhibits", __name__, url_prefix="/api/exhibits")


@exhibits_bp.route("", methods=["GET"])
@exhibits_bp.route("/", methods=["GET"])
@auth_required
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
@auth_required
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
@auth_required
def assign():
    """Assign the next exhibit number to a document."""
    payload = request.get_json() or {}
    try:
        data = ExhibitAssignPayload.model_validate(payload)
    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 400
    num = assign_exhibit_number(data.document_id, data.title, data.user)
    return jsonify({"exhibit_number": num})


@exhibits_bp.post("/reorder")
@auth_required
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
@auth_required
def binder():
    """Generate a combined PDF binder for the case exhibits."""
    payload = request.get_json() or {}
    case_id = payload.get("case_id")
    try:
        case_id = int(case_id)
    except (TypeError, ValueError):
        return jsonify({"error": "case_id required"}), 400

    case = Case.query.get(case_id)
    if not case:
        return jsonify({"error": "case not found"}), 404
    user = session.get("user")
    if user and case_id not in user.get("cases", []):
        return jsonify({"error": "forbidden"}), 403

    export_dir = Path(current_app.config.get("UPLOAD_FOLDER", "uploads")).resolve()
    export_dir.mkdir(parents=True, exist_ok=True)
    filename = secure_filename(f"case_{case_id}_binder.pdf")
    target = (export_dir / filename).resolve()
    if export_dir not in target.parents:
        return jsonify({"error": "invalid path"}), 400

    task_id, result = enqueue(binder_task, case_id, str(target))
    if result is not None:
        path = Path(result).resolve()
        if export_dir not in path.parents or not path.exists():
            return jsonify({"error": "file generation failed"}), 500
        return jsonify({"task_id": task_id, "binder_path": f"/uploads/{path.name}", "path": str(path)})
    return jsonify({"task_id": task_id}), 202


@exhibits_bp.post("/zip")
@auth_required
def zip_export():
    """Export exhibits and manifest as a zip archive."""
    payload = request.get_json() or {}
    case_id = payload.get("case_id")
    try:
        case_id = int(case_id)
    except (TypeError, ValueError):
        return jsonify({"error": "case_id required"}), 400

    case = Case.query.get(case_id)
    if not case:
        return jsonify({"error": "case not found"}), 404
    user = session.get("user")
    if user and case_id not in user.get("cases", []):
        return jsonify({"error": "forbidden"}), 403

    export_dir = Path(current_app.config.get("UPLOAD_FOLDER", "uploads")).resolve()
    export_dir.mkdir(parents=True, exist_ok=True)
    filename = secure_filename(f"case_{case_id}_exhibits.zip")
    target = (export_dir / filename).resolve()
    if export_dir not in target.parents:
        return jsonify({"error": "invalid path"}), 400

    path = Path(export_zip(case_id, target)).resolve()
    if export_dir not in path.parents or not path.exists():
        return jsonify({"error": "file generation failed"}), 500

    return jsonify({"zip_path": f"/uploads/{path.name}", "path": str(path)})
