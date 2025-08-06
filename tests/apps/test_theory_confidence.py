from flask import Flask
from apps.legal_discovery.database import db
from apps.legal_discovery.models import (
    Case,
    Document,
    LegalTheory,
    Fact,
    TheoryConfidence,
)


def _setup_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    return app


def test_theory_confidence_model():
    app = _setup_app()
    with app.app_context():
        db.create_all()
        case = Case(name="Test Case")
        db.session.add(case)
        db.session.commit()
        doc = Document(
            case_id=case.id,
            name="Doc",
            file_path="/tmp/doc.txt",
            sha256="hash",
        )
        theory = LegalTheory(case_id=case.id, theory_name="Breach of Contract")
        fact = Fact(case_id=case.id, document=doc, legal_theory=theory, text="Alice signed", parties=[], dates=[], actions=[])
        db.session.add_all([doc, theory, fact])
        db.session.commit()
        tc = TheoryConfidence(legal_theory=theory, fact=fact, confidence=0.8, source_team="team1")
        db.session.add(tc)
        db.session.commit()
        assert tc.id is not None
        assert 0 <= tc.confidence <= 1
        assert tc.source_team == "team1"
