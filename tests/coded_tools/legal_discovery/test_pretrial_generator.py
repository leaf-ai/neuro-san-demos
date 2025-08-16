import os
import sys
from types import SimpleNamespace

import pytest
from flask import Flask

sys.path.insert(0, os.path.abspath("."))

from apps.legal_discovery.database import db
from apps.legal_discovery.models import (
    Case,
    Document,
    DocumentWitnessLink,
    Fact,
    FactConflict,
    LegalTheory,
    Witness,
)
from coded_tools.legal_discovery.pretrial_generator import PretrialGenerator


def setup_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    db.init_app(app)
    with app.app_context():
        db.create_all()
    return app


def mock_genai():
    class MockClient:
        def __init__(self, api_key=""):
            self.models = self

        def generate_content(self, model, contents, config=None):
            return SimpleNamespace(text="mock statement")

    class MockTypes:
        @staticmethod
        def GenerateContentConfig(**kwargs):
            return None

    return SimpleNamespace(Client=MockClient, types=MockTypes)


def test_export_generates_doc_and_integrates(monkeypatch, tmp_path):
    app = setup_app()
    with app.app_context():
        case = Case(name="C1", description="")
        db.session.add(case)
        db.session.commit()

        doc = Document(
            case_id=case.id,
            name="Doc1",
            bates_number="B1",
            file_path="/tmp/doc1",
            sha256="h1",
        )
        witness = Witness(name="Jane", role="Witness", associated_case=case.id)
        theory = LegalTheory(case_id=case.id, theory_name="Theory", status="approved")
        db.session.add_all([doc, witness, theory])
        db.session.commit()

        link = DocumentWitnessLink(document_id=doc.id, witness_id=witness.id)
        db.session.add(link)

        fact1 = Fact(
            case_id=case.id,
            document_id=doc.id,
            legal_theory_id=theory.id,
            text="A fact",
            dates=["2024-01-01"],
            witness_id=witness.id,
        )
        fact2 = Fact(
            case_id=case.id,
            document_id=doc.id,
            legal_theory_id=theory.id,
            text="Another fact",
            witness_id=witness.id,
        )
        db.session.add_all([fact1, fact2])
        db.session.commit()

        conflict = FactConflict(
            witness_id=witness.id,
            fact1_id=fact1.id,
            fact2_id=fact1.id,
            score=0.9,
            description="Conflict on A fact",
        )
        db.session.add(conflict)
        db.session.commit()

        pretrial_module = sys.modules[PretrialGenerator.__module__]
        monkeypatch.setattr(pretrial_module, "genai", mock_genai())

        calls = {}

        def fake_create_timeline(self, timeline_id, items):
            calls["timeline"] = (timeline_id, items)

        monkeypatch.setattr(pretrial_module.TimelineManager, "create_timeline", fake_create_timeline)

        def fake_binder(cid):
            calls["binder"] = cid

        monkeypatch.setattr(pretrial_module, "generate_binder", fake_binder)

        generator = PretrialGenerator()
        out_path = tmp_path / "pretrial.docx"
        generator.export(case.id, str(out_path))
        assert out_path.exists()
        assert "timeline" in calls
        assert "binder" in calls
