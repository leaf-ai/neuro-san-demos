import os
import zipfile
from flask import Flask
from reportlab.pdfgen import canvas

from apps.legal_discovery.database import db
from apps.legal_discovery.models import Case, Document
from apps.legal_discovery.exhibit_routes import exhibits_bp

def _create_pdf(path):
    c = canvas.Canvas(str(path))
    c.drawString(100, 750, "Test")
    c.save()


def _setup(tmp_path):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = str(tmp_path)
    db.init_app(app)
    app.register_blueprint(exhibits_bp)
    with app.app_context():
        db.create_all()
        case = Case(name="Test Case")
        db.session.add(case)
        db.session.commit()
        case_id = case.id
        pdf_path = tmp_path / "doc.pdf"
        _create_pdf(pdf_path)
        doc = Document(
            case_id=case_id,
            name="Doc",
            file_path=str(pdf_path),
            content_hash="hash1",
            bates_number="B1",
        )
        db.session.add(doc)
        db.session.commit()
        doc_id = doc.id
    return app, case_id, doc_id


def test_assign_list_and_exports(tmp_path):
    app, case_id, doc_id = _setup(tmp_path)
    client = app.test_client()

    res = client.post("/api/exhibits/assign", json={"document_id": doc_id, "title": "Title"})
    assert res.status_code == 200
    assert res.json["exhibit_number"] == "EX_0001"

    res = client.get(f"/api/exhibits?case_id={case_id}")
    assert res.status_code == 200
    assert res.json[0]["exhibit_number"] == "EX_0001"

    res = client.post("/api/exhibits/binder", json={"case_id": case_id})
    assert res.status_code == 200
    binder_path = tmp_path / "case_{}_binder.pdf".format(case_id)
    assert binder_path.exists()

    res = client.post("/api/exhibits/zip", json={"case_id": case_id})
    assert res.status_code == 200
    zip_path = tmp_path / "case_{}_exhibits.zip".format(case_id)
    assert zip_path.exists()
    with zipfile.ZipFile(zip_path) as z:
        assert "manifest.json" in z.namelist()
