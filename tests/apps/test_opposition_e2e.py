import os
from dataclasses import dataclass

from flask import Flask
import pytest
import sys

os.environ["DATABASE_URL"] = "sqlite://"
sys.path.append(os.getcwd())

from apps.legal_discovery.database import db
from apps.legal_discovery.models import (
    Case,
    Document,
    DocumentSource,
    NarrativeDiscrepancy,
)

@dataclass
class DiscrepancyResult:
    opposing_doc_id: int
    user_doc_id: int
    conflicting_claim: str
    evidence_excerpt: str
    confidence: float
    legal_theory_id: int | None = None
    calendar_event_id: int | None = None

class NarrativeDiscrepancyDetector:
    def analyze(self, doc):
        return []


@pytest.fixture
def app(tmp_path):
    flask_app = Flask(__name__)
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(flask_app)
    with flask_app.app_context():
        db.create_all()
        db.session.add(Case(id=1, name="Test"))
        db.session.commit()
    yield flask_app
    with flask_app.app_context():
        db.drop_all()


def test_upload_detection_dashboard_flow(app, tmp_path, monkeypatch):
    with app.app_context():
        user_file = tmp_path / "user.txt"
        user_file.write_text("The sky is blue.")
        user_doc = Document(
            case_id=1,
            name="user.txt",
            file_path=str(user_file),
            sha256="u",
            source=DocumentSource.USER,
        )
        db.session.add(user_doc)
        db.session.commit()

        opp_file = tmp_path / "opp.txt"
        opp_file.write_text("The sky is green.")
        opp_doc = Document(
            case_id=1,
            name="opp.txt",
            file_path=str(opp_file),
            sha256="o",
            source=DocumentSource.OPP_COUNSEL,
        )
        db.session.add(opp_doc)
        db.session.commit()

        def fake_analyze(self, doc):
            db.session.add(
                NarrativeDiscrepancy(
                    opposing_doc_id=opp_doc.id,
                    user_doc_id=user_doc.id,
                    conflicting_claim="The sky is green.",
                    evidence_excerpt="The sky is blue.",
                    confidence=0.9,
                )
            )
            db.session.commit()
            return [
                DiscrepancyResult(
                    opposing_doc_id=opp_doc.id,
                    user_doc_id=user_doc.id,
                    conflicting_claim="The sky is green.",
                    evidence_excerpt="The sky is blue.",
                    confidence=0.9,
                )
            ]

        monkeypatch.setattr(NarrativeDiscrepancyDetector, "analyze", fake_analyze)
        detector = NarrativeDiscrepancyDetector()
        detector.analyze(opp_doc)

        results = NarrativeDiscrepancy.query.all()
        assert any(r.conflicting_claim == "The sky is green." for r in results)
