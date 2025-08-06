import os
import json
import zipfile

import pytest
from flask import Flask
from reportlab.pdfgen import canvas

from apps.legal_discovery.database import db
from apps.legal_discovery.models import Case, Document, DocumentMetadata
from apps.legal_discovery.exhibit_manager import (
    ExhibitExportError,
    assign_exhibit_number,
    export_zip,
    generate_binder,
)


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
        return app, case.id


def _create_doc(case_id, tmp_path, name, hash_, bates, privileged=False):
    pdf_path = tmp_path / f"{name}.pdf"
    _create_pdf(pdf_path)
    doc = Document(
        case_id=case_id,
        name=name,
        file_path=str(pdf_path),
        content_hash=hash_,
        bates_number=bates,
        is_privileged=privileged,
    )
    db.session.add(doc)
    db.session.commit()
    return doc.id


def test_assign_and_generate_binder(tmp_path):
    app, case_id = _setup_app(tmp_path)
    with app.app_context():
        doc_id = _create_doc(case_id, tmp_path, "Doc", "hash1", "BATES1")
        num = assign_exhibit_number(doc_id, "Title")
        assert num == "EX_0001"
        assert Document.query.get(doc_id).exhibit_order == 1
        binder_path = tmp_path / "binder.pdf"
        result = generate_binder(case_id, binder_path)
        assert result == str(binder_path)
        assert os.path.exists(result)


def test_export_metadata_and_crosslinks(tmp_path):
    app, case_id = _setup_app(tmp_path)
    with app.app_context():
        doc1 = _create_doc(case_id, tmp_path, "Doc1", "hash1", "B1")
        doc2 = _create_doc(case_id, tmp_path, "Doc2", "hash2", "B2")
        assign_exhibit_number(doc1, "Title1")
        assign_exhibit_number(doc2, "Title2")
        db.session.add_all(
            [
                DocumentMetadata(document_id=doc1, schema="deposition_excerpt", data={"text": "dep"}),
                DocumentMetadata(document_id=doc1, schema="theory_reference", data={"text": "ref"}),
                DocumentMetadata(document_id=doc1, schema="evidence_scorecard", data={"score": 5}),
                DocumentMetadata(document_id=doc1, schema="sanctions_risk", data={"note": "low"}),
            ]
        )
        db.session.commit()
        zip_path = tmp_path / "exhibits.zip"
        export_zip(case_id, zip_path)
        with zipfile.ZipFile(zip_path) as z:
            manifest = json.load(z.open("manifest.json"))
            assert manifest[0]["exhibit_number"] == "EX_0001"
            assert manifest[1]["exhibit_number"] == "EX_0002"
            assert manifest[0]["deposition_excerpt"] == "EX_0001_deposition.txt"
            assert manifest[0]["theory_reference"] == "EX_0001_theory.txt"
            assert "evidence_scorecard" in manifest[0]
            assert "sanctions_risk" in manifest[0]
            assert "EX_0001_deposition.txt" in z.namelist()
            assert "EX_0001_theory.txt" in z.namelist()


def test_export_skips_privileged(tmp_path):
    app, case_id = _setup_app(tmp_path)
    with app.app_context():
        doc1 = _create_doc(case_id, tmp_path, "Doc1", "hash1", "B1")
        doc2 = _create_doc(case_id, tmp_path, "Doc2", "hash2", "B2", privileged=True)
        assign_exhibit_number(doc1)
        assign_exhibit_number(doc2)
        zip_path = tmp_path / "exhibits.zip"
        with pytest.raises(ExhibitExportError):
            export_zip(case_id, zip_path)
