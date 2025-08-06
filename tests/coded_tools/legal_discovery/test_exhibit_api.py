import os
import zipfile
from flask import Flask
from reportlab.pdfgen import canvas

from apps.legal_discovery.database import db
from apps.legal_discovery.models import (
    Case,
    Document,
    ChainOfCustodyLog,
    ChainEventType,
    DocumentSource,
    LegalTheory,
    Fact,
)
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

        pdf1 = tmp_path / "doc1.pdf"
        pdf2 = tmp_path / "doc2.pdf"
        pdf3 = tmp_path / "doc3.pdf"
        _create_pdf(pdf1)
        _create_pdf(pdf2)
        _create_pdf(pdf3)

        doc1 = Document(
            case_id=case_id,
            name="Doc1",
            file_path=str(pdf1),
            content_hash="hash1",
            bates_number="B1",
            source=DocumentSource.USER,
        )
        doc2 = Document(
            case_id=case_id,
            name="Doc2",
            file_path=str(pdf2),
            content_hash="hash2",
            bates_number="B2",
            source=DocumentSource.OPP_COUNSEL,
        )
        doc3 = Document(
            case_id=case_id,
            name="Doc3",
            file_path=str(pdf3),
            content_hash="hash3",
            bates_number="B3",
            is_privileged=True,
            source=DocumentSource.COURT,
        )
        db.session.add_all([doc1, doc2, doc3])
        db.session.commit()

        db.session.add_all(
            [
                ChainOfCustodyLog(
                    document_id=doc1.id, event_type=ChainEventType.INGESTED, source_team="team1"
                ),
                ChainOfCustodyLog(
                    document_id=doc2.id, event_type=ChainEventType.INGESTED, source_team="team2"
                ),
                ChainOfCustodyLog(
                    document_id=doc3.id, event_type=ChainEventType.INGESTED, source_team="team1"
                ),
            ]
        )
        db.session.commit()
        return app, case_id, doc1.id, doc2.id, doc3.id


def test_assign_list_and_exports(tmp_path):
    app, case_id, doc1, doc2, doc3 = _setup(tmp_path)
    client = app.test_client()

    res = client.post("/api/exhibits/assign", json={"document_id": doc1, "title": "T1"})
    assert res.status_code == 200
    assert res.json["exhibit_number"] == "EX_0001"

    res = client.post("/api/exhibits/binder", json={"case_id": case_id})
    assert res.status_code == 200
    binder_path = tmp_path / f"case_{case_id}_binder.pdf"
    assert binder_path.exists()

    res = client.post("/api/exhibits/zip", json={"case_id": case_id})
    assert res.status_code == 200
    zip_path = tmp_path / f"case_{case_id}_exhibits.zip"
    assert zip_path.exists()
    with zipfile.ZipFile(zip_path) as z:
        assert "manifest.json" in z.namelist()

    client.post("/api/exhibits/assign", json={"document_id": doc2, "title": "T2"})
    client.post("/api/exhibits/assign", json={"document_id": doc3, "title": "T3"})
    res = client.post(
        "/api/exhibits/reorder", json={"case_id": case_id, "order": [doc2, doc1, doc3]}
    )
    assert res.status_code == 200

    res = client.get(f"/api/exhibits?case_id={case_id}")
    assert [e["id"] for e in res.json] == [doc2, doc1]

    res = client.get(
        f"/api/exhibits?case_id={case_id}&include_privileged=true"
    )
    assert [e["id"] for e in res.json] == [doc2, doc1, doc3]

    res = client.get(
        f"/api/exhibits?case_id={case_id}&include_privileged=true&source_team=team1"
    )
    assert [e["id"] for e in res.json] == [doc1, doc3]

    res = client.get(f"/api/exhibits?case_id={case_id}&source=opp_counsel")
    assert [e["id"] for e in res.json] == [doc2]

    # links endpoint
    with app.app_context():
        theory = LegalTheory(case_id=case_id, theory_name="Breach")
        db.session.add(theory)
        db.session.commit()
        db.session.add(
            Fact(
                case_id=case_id,
                document_id=doc1,
                legal_theory_id=theory.id,
                text="Event",
                dates=["2020-01-01"],
            )
        )
        db.session.commit()
    client.post("/api/exhibits/assign", json={"document_id": doc1, "title": "T1"})
    res = client.get(f"/api/exhibits/{doc1}/links")
    assert res.status_code == 200
    assert res.json["theories"] == ["Breach"]
    assert res.json["timeline"][0]["date"] == "2020-01-01"
