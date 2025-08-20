"""Flask routes for Trial Prep Academy APIs."""
from __future__ import annotations

from flask import Blueprint, abort, jsonify, request
from .auth import auth_required

from .models import LegalResource, Lesson
from .trial_prep import CurriculumManager, ResourceManager

trial_prep_bp = Blueprint("trial_prep", __name__)
resource_manager = ResourceManager()
curriculum_manager = CurriculumManager()


@trial_prep_bp.route("/api/resources/search")
@auth_required
def search_resources():
    query = request.args.get("query", "")
    resources = (
        resource_manager.search(query) if query else LegalResource.query.all()
    )
    return jsonify([r.to_dict() for r in resources])


@trial_prep_bp.route("/api/resources/<int:res_id>")
@auth_required
def get_resource(res_id: int):
    resource = LegalResource.query.get_or_404(res_id)
    return jsonify(resource.to_dict(include_content=True))


@trial_prep_bp.route("/api/lessons")
@auth_required
def list_lessons():
    topic = request.args.get("topic")
    lessons = curriculum_manager.list_lessons(topic)
    return jsonify([l.to_dict(with_progress=True) for l in lessons])


@trial_prep_bp.route("/api/lessons/<int:lesson_id>/progress", methods=["POST"])
@auth_required
def update_progress(lesson_id: int):
    data = request.get_json() or {}
    progress = curriculum_manager.record_progress(
        lesson_id,
        completed=bool(data.get("completed")),
        quiz_score=data.get("quiz_score"),
        thumbs_up=data.get("thumbs_up"),
    )
    return jsonify(progress.to_dict())
