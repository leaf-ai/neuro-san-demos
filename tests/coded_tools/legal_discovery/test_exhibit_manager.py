import os
import zipfile
from flask import Flask
from reportlab.pdfgen import canvas

from apps.legal_discovery.database import db
from apps.legal_discovery.models import Case, Document
from apps.legal_discovery.exhibit_manager import assign_exhibit_number, generate_binder, export_zip


def _create_pdf(path):
    c = canvas.Canvas(str(path))
    c.drawString(100, 750, "Test")
    c.save()


def _setup_app(tmp_path):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()
        case = Case(name="Test Case")
        db.session.add(case)
        db.session.commit()
        pdf_path = tmp_path / "doc.pdf"
        _create_pdf(pdf_path)
        doc = Document(
            case_id=case.id,
            name="Doc",
            file_path=str(pdf_path),
            content_hash="hash1",
            bates_number="BATES1",
        )
        db.session.add(doc)
        db.session.commit()
        return app, case.id, doc.id


def test_assign_and_generate_binder(tmp_path):
    app, case_id, doc_id = _setup_app(tmp_path)
    with app.app_context():
        num = assign_exhibit_number(doc_id, "Title")
        assert num == "EX_0001"
        binder_path = tmp_path / "binder.pdf"
        result = generate_binder(case_id, binder_path)
        assert result == str(binder_path)
        assert os.path.exists(result)


def test_export_zip(tmp_path):
    app, case_id, doc_id = _setup_app(tmp_path)
    with app.app_context():
        assign_exhibit_number(doc_id, "Title")
        zip_path = tmp_path / "exhibits.zip"
        result = export_zip(case_id, zip_path)
        assert result == str(zip_path)
        assert os.path.exists(result)
        with zipfile.ZipFile(zip_path) as z:
            assert "manifest.json" in z.namelist()
