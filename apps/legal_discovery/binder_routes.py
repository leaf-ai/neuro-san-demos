import os
from flask import Blueprint, jsonify, request

from coded_tools.legal_discovery.pretrial_generator import PretrialGenerator

binder_bp = Blueprint("binder", __name__, url_prefix="/api/binder")


@binder_bp.post("/pretrial/export")
def export_pretrial_statement():
    """Generate a pretrial statement document and update timeline/binder."""

    data = request.get_json() or {}
    case_id = data.get("case_id", type=int)
    if not case_id:
        return jsonify({"error": "Missing case_id"}), 400

    os.makedirs("exports", exist_ok=True)
    path = os.path.join("exports", f"pretrial_{case_id}.docx")
    generator = PretrialGenerator()
    generator.export(case_id, path)
    return jsonify({"status": "ok", "path": path})


__all__ = ["binder_bp"]
