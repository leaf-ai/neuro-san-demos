import os
import pytest
from flask import Flask, jsonify, request

from apps.legal_discovery.database import db
from apps.legal_discovery.models import Case, Document, DocumentSource, RedactionAudit


@pytest.fixture
def client_with_doc():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
    db.init_app(app)
    with app.app_context():
        db.drop_all()
        db.create_all()
        case = Case(name="Test")
        db.session.add(case)
        db.session.commit()
        doc = Document(
            case_id=case.id,
            name="doc",
            file_path="f",
            sha256="hash",
            source=DocumentSource.USER,
        )
        db.session.add(doc)
        db.session.commit()
        doc_id = doc.id

    @app.route("/api/privilege/<int:doc_id>", methods=["POST"])
    def override_privilege(doc_id: int):
        data = request.get_json() or {}
        privileged = data.get("privileged")
        reviewer = data.get("reviewer")
        reason = data.get("reason")
        if privileged is None:
            return jsonify({"error": "privileged required"}), 400
        doc = Document.query.get_or_404(doc_id)
        doc.is_privileged = bool(privileged)
        doc.is_redacted = bool(privileged)
        doc.needs_review = False
        db.session.add(
            RedactionAudit(
                document_id=doc.id,
                reviewer=reviewer,
                action="override_privilege",
                reason=reason,
            )
        )
        db.session.commit()
        return jsonify({"status": "ok"})

    return app.test_client(), app, doc_id


def test_override_privilege_flow(client_with_doc):
    client, app, doc_id = client_with_doc
    resp = client.post(f"/api/privilege/{doc_id}", json={"privileged": True, "reviewer": "rev"})
    assert resp.status_code == 200
    with app.app_context():
        doc = Document.query.get(doc_id)
        assert doc.is_privileged is True
        audit = RedactionAudit.query.filter_by(document_id=doc_id).first()
        assert audit is not None and audit.action == "override_privilege"
    resp = client.post(f"/api/privilege/{doc_id}", json={"privileged": False, "reviewer": "rev"})
    assert resp.status_code == 200
    with app.app_context():
        doc = Document.query.get(doc_id)
        assert doc.is_privileged is False
