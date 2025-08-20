import os
import hashlib
import fitz
import pytest

os.environ["DATABASE_URL"] = "sqlite://"
os.environ.setdefault("FLASK_SECRET_KEY", "test")
os.environ.setdefault("JWT_SECRET", "test")

from apps.legal_discovery.interface_flask import app, db, Document, Agent, Case, DocumentVersion, DocumentSource


def _create_pdf(path: str):
    doc = fitz.open()
    doc.new_page()
    doc.save(path)


@pytest.fixture
def client(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    _create_pdf(str(pdf_path))
    sha = hashlib.sha256(pdf_path.read_bytes()).hexdigest()
    with app.app_context():
        db.drop_all()
        db.create_all()
        case = Case(name="c1", description="d1")
        db.session.add(case)
        agent = Agent(name="tester", role="user")
        db.session.add(agent)
        db.session.flush()
        doc = Document(
            case_id=case.id,
            name="sample",
            file_path=str(pdf_path),
            sha256=sha,
            source=DocumentSource.USER,
        )
        db.session.add(doc)
        db.session.commit()
    return app.test_client()


def test_sequential_versions(client, tmp_path):
    file_path = str(tmp_path / "sample.pdf")
    resp1 = client.post("/api/document/stamp", json={"file_path": file_path, "prefix": "CASE", "user_id": 1})
    assert resp1.status_code == 200
    resp2 = client.post("/api/document/stamp", json={"file_path": file_path, "prefix": "CASE", "user_id": 1})
    assert resp2.status_code == 200
    with app.app_context():
        versions = DocumentVersion.query.order_by(DocumentVersion.id).all()
        assert [v.bates_number for v in versions] == ["CASE_000001", "CASE_000002"]
