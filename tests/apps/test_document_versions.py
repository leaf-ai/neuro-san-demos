import fitz
import pytest
from flask import Flask, jsonify, request

from apps.legal_discovery.database import db
from apps.legal_discovery.models import Case, Document, DocumentSource, DocumentVersion
from coded_tools.legal_discovery.bates_numbering import BatesNumberingService, stamp_pdf


def create_pdf(path: str) -> None:
    doc = fitz.open()
    doc.new_page()
    doc.save(path)


@pytest.fixture
def client(tmp_path):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
    db.init_app(app)

    bates_service = BatesNumberingService()

    @app.route("/api/document/stamp", methods=["POST"])
    def stamp():
        data = request.get_json() or {}
        file_path = data["file_path"]
        prefix = data.get("prefix", "BATES")
        document_id = data["document_id"]
        user_id = data["user_id"]
        start_bates = bates_service.get_next_bates_number(prefix)
        start_num = int(start_bates.split("_")[-1])
        output_path = f"{file_path}_stamped.pdf"
        stamp_pdf(file_path, output_path, start_num, prefix=prefix)
        last_version = (
            DocumentVersion.query.filter_by(document_id=document_id)
            .order_by(DocumentVersion.version_number.desc())
            .first()
        )
        version_number = 1 if last_version is None else last_version.version_number + 1
        db.session.add(
            DocumentVersion(
                document_id=document_id,
                version_number=version_number,
                file_path=output_path,
                bates_number=start_bates,
                user_id=user_id,
            )
        )
        db.session.commit()
        return jsonify({"output": output_path})
    with app.app_context():
        db.create_all()
        case = Case(name="T")
        db.session.add(case)
        db.session.commit()
        pdf_path = tmp_path / "doc.pdf"
        create_pdf(str(pdf_path))
        doc = Document(
            case_id=case.id,
            name="doc",
            file_path=str(pdf_path),
            sha256="hash",
            source=DocumentSource.USER,
        )
        db.session.add(doc)
        db.session.commit()
        doc_id = doc.id
    return app.test_client(), app, doc_id, str(pdf_path)


def test_document_versions_sequential(client):
    client, app, doc_id, path = client
    resp1 = client.post(
        "/api/document/stamp",
        json={"file_path": path, "prefix": "TEST", "document_id": doc_id, "user_id": 1},
    )
    assert resp1.status_code == 200
    out1 = resp1.get_json()["output"]
    resp2 = client.post(
        "/api/document/stamp",
        json={"file_path": out1, "prefix": "TEST", "document_id": doc_id, "user_id": 1},
    )
    assert resp2.status_code == 200
    with app.app_context():
        versions = (
            DocumentVersion.query.filter_by(document_id=doc_id)
            .order_by(DocumentVersion.version_number)
            .all()
        )
        assert [v.version_number for v in versions] == [1, 2]
        assert versions[0].bates_number == "TEST_000001"
        assert versions[1].bates_number == "TEST_000002"
