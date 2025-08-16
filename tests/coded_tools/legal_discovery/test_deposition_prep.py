import os
import os
import sys
from types import SimpleNamespace
import pytest
pytestmark = pytest.mark.skip("requires genai client update")

from flask import Flask

sys.path.insert(0, os.path.abspath("."))

from apps.legal_discovery.database import db
from apps.legal_discovery.models import (
    Case,
    Document,
    Witness,
    DocumentWitnessLink,
    Fact,
    FactConflict,
    Agent,
    DepositionQuestion,
    DepositionReviewLog,
)
from coded_tools.legal_discovery.deposition_prep import DepositionPrep


class DummyGenAIResponse:
    def __init__(self, text: str):
        self.text = text
class DummyResponse:
    class Choice:
        def __init__(self, content):
            self.message = type("obj", (), {"content": content})

    def __init__(self, content):
        self.content = content
        self.choices = [DummyResponse.Choice(content)]


def setup_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()
    return app


def test_generate_questions(monkeypatch):
    app = setup_app()
    with app.app_context():
        case = Case(name="Test", description="")
        db.session.add(case)
        db.session.commit()
        doc = Document(
            case_id=case.id,
            name="Doc1",
            bates_number="B1",
            file_path="/tmp/doc1",
            sha256="h1",
        )
        witness = Witness(name="Alice", role="Witness", associated_case=case.id)
        db.session.add_all([doc, witness])
        db.session.commit()
        link = DocumentWitnessLink(document_id=doc.id, witness_id=witness.id)
        db.session.add(link)
        fact = Fact(
            case_id=case.id,
            document_id=doc.id,
            text="Alice met Bob",
            witness_id=witness.id,
        )
        db.session.add(fact)
        db.session.commit()

        def mock_genai():
            class MockModel:
                def __init__(self, _name):
                    pass

                def generate_content(self, prompt, generation_config=None):
                    return DummyGenAIResponse(
                        '[{"category": "Background", "question": "State your name", "source": "Doc1"}]'
                    )

            class MockTypes:
                @staticmethod
                def GenerationConfig(**kwargs):
                    return None

            return SimpleNamespace(GenerativeModel=MockModel, types=MockTypes)

        def mock_llm(model, temperature):
            class Client:
                def invoke(self, prompt):
                    return DummyResponse(
                        '[{"category": "Background", "question": "State your name", "source": "Doc1"}]'
                    )

            return Client()

        deposition_prep_module = sys.modules[DepositionPrep.__module__]
        monkeypatch.setattr(deposition_prep_module, "genai", mock_genai())
        monkeypatch.setattr(deposition_prep_module, "ChatGoogleGenerativeAI", mock_llm)

        questions = DepositionPrep.generate_questions(witness.id)
        assert len(questions) == 1
        assert questions[0]["category"] == "Background"
        assert questions[0]["source"] == "Doc1"


def test_detect_contradictions_and_export(monkeypatch, tmp_path):
    app = setup_app()
    with app.app_context():
        case = Case(name="C1", description="")
        db.session.add(case)
        db.session.commit()
        doc = Document(
            case_id=case.id,
            name="DocA",
            bates_number="B100",
            file_path="/tmp/docA",
            sha256="hA",
        )
        witness = Witness(name="Bob", role="Witness", associated_case=case.id)
        reviewer = Agent(name="Ann", role="attorney")
        db.session.add_all([doc, witness, reviewer])
        db.session.add_all([doc, witness])
        db.session.commit()
        link = DocumentWitnessLink(document_id=doc.id, witness_id=witness.id)
        db.session.add(link)
        fact1 = Fact(
            case_id=case.id,
            document_id=doc.id,
            text="Bob was present on Monday",
            witness_id=witness.id,
        )
        fact2 = Fact(
            case_id=case.id,
            document_id=doc.id,
            text="Bob was absent on Monday",
            witness_id=witness.id,
        )
        db.session.add_all([fact1, fact2])
        db.session.commit()

        def mock_genai():
            class MockModel:
                def __init__(self, _name):
                    pass

                def generate_content(self, prompt, generation_config=None):
                    if prompt.startswith("Do these statements contradict"):
                        return DummyGenAIResponse(
                            '{"contradiction": true, "score": 0.95}'
                        )
                    return DummyGenAIResponse(
                        '[{"category": "Events", "question": "Where were you on Monday?", "source": "DocA"}]'
                    )

            class MockTypes:
                @staticmethod
                def GenerationConfig(**kwargs):
                    return None

            return SimpleNamespace(GenerativeModel=MockModel, types=MockTypes)

        deposition_prep_module = sys.modules[DepositionPrep.__module__]
        monkeypatch.setattr(deposition_prep_module, "genai", mock_genai())
        def mock_llm(model, temperature):
            class Client:
                def invoke(self, prompt):
                    if prompt.startswith("Do these statements contradict"):
                        return DummyResponse('{"contradiction": true, "score": 0.95}')
                    return DummyResponse(
                        '[{"category": "Events", "question": "Where were you on Monday?", "source": "DocA"}]'
                    )

            return Client()

        deposition_prep_module = sys.modules[DepositionPrep.__module__]
        monkeypatch.setattr(deposition_prep_module, "ChatGoogleGenerativeAI", mock_llm)

        # detect contradictions and generate questions
        questions = DepositionPrep.generate_questions(witness.id)
        assert len(questions) == 1
        assert questions[0]["source"] == "DocA"
        assert FactConflict.query.count() == 1
        conflict = FactConflict.query.first()
        assert conflict.witness_id == witness.id
        assert {conflict.fact1_id, conflict.fact2_id} == {fact1.id, fact2.id}
        assert conflict.score == pytest.approx(0.95)
        assert "present on Monday" in conflict.description
        assert "absent on Monday" in conflict.description
        assert conflict.created_at is not None
        pdf_path = tmp_path / "out.pdf"
        docx_path = tmp_path / "out.docx"
        returned_pdf = DepositionPrep.export_questions(witness.id, str(pdf_path), reviewer.id)
        returned_docx = DepositionPrep.export_questions(witness.id, str(docx_path), reviewer.id)
        assert returned_pdf == str(pdf_path)
        assert returned_docx == str(docx_path)
        assert pdf_path.exists() and pdf_path.stat().st_size > 0
        assert docx_path.exists() and docx_path.stat().st_size > 0


def test_review_logging_and_permissions(tmp_path):
    app = setup_app()
    with app.app_context():
        case = Case(name="C2", description="")
        db.session.add(case)
        db.session.commit()
        doc = Document(
            case_id=case.id,
            name="DocB",
            bates_number="B200",
            file_path="/tmp/docB",
            sha256="hB",
        )
        witness = Witness(name="Eve", role="Witness", associated_case=case.id)
        attorney = Agent(name="Terry", role="attorney")
        paralegal = Agent(name="Paula", role="paralegal")
        db.session.add_all([doc, witness, attorney, paralegal])
        db.session.commit()
        question = DepositionQuestion(
            witness_id=witness.id,
            category="Background",
            question="State your address",
            source="DocB",
        )
        db.session.add(question)
        db.session.commit()

        result = DepositionPrep.log_review(witness.id, attorney.id, True, "looks good")
        assert result["approved"] is True
        assert result["notes"] == "looks good"
        assert DepositionReviewLog.query.count() == 1
        log = DepositionReviewLog.query.first()
        assert result["id"] == log.id
        assert log.reviewer_id == attorney.id
        assert log.witness_id == witness.id
        assert log.approved is True
        assert log.notes == "looks good"
        assert log.timestamp is not None
        with pytest.raises(PermissionError):
            DepositionPrep.log_review(witness.id, paralegal.id, True)
        assert DepositionReviewLog.query.count() == 1

        with pytest.raises(PermissionError):
            DepositionPrep.export_questions(witness.id, str(tmp_path / "x.docx"), paralegal.id)

        docx_path = tmp_path / "y.docx"
        pdf_path = tmp_path / "y.pdf"
        returned_docx = DepositionPrep.export_questions(
            witness.id, str(docx_path), attorney.id
        )
        returned_pdf = DepositionPrep.export_questions(
            witness.id, str(pdf_path), attorney.id
        )
        assert returned_docx == str(docx_path)
        assert returned_pdf == str(pdf_path)
        assert docx_path.exists() and docx_path.stat().st_size > 0
        assert pdf_path.exists() and pdf_path.stat().st_size > 0


def test_export_questions_authorized_formats(tmp_path):
    app = setup_app()
    with app.app_context():
        case = Case(name="C3", description="")
        db.session.add(case)
        db.session.commit()
        doc = Document(
            case_id=case.id,
            name="DocC",
            bates_number="B300",
            file_path="/tmp/docC",
            sha256="hC",
        )
        witness = Witness(name="Rick", role="Witness", associated_case=case.id)
        attorney = Agent(name="Rita", role="attorney")
        db.session.add_all([doc, witness, attorney])
        db.session.commit()
        question = DepositionQuestion(
            witness_id=witness.id,
            category="General",
            question="What is your role?",
            source="DocC",
        )
        db.session.add(question)
        db.session.commit()

        pdf_path = tmp_path / "auth.pdf"
        docx_path = tmp_path / "auth.docx"
        pdf_ret = DepositionPrep.export_questions(witness.id, str(pdf_path), attorney.id)
        docx_ret = DepositionPrep.export_questions(witness.id, str(docx_path), attorney.id)

        assert pdf_ret == str(pdf_path)
        assert docx_ret == str(docx_path)
        assert pdf_path.exists() and pdf_path.stat().st_size > 0
        assert docx_path.exists() and docx_path.stat().st_size > 0


def test_export_questions_permission_denied(tmp_path):
    app = setup_app()
    with app.app_context():
        case = Case(name="C4", description="")
        db.session.add(case)
        db.session.commit()
        doc = Document(
            case_id=case.id,
            name="DocD",
            bates_number="B400",
            file_path="/tmp/docD",
            sha256="hD",
        )
        witness = Witness(name="Sam", role="Witness", associated_case=case.id)
        paralegal = Agent(name="Pat", role="paralegal")
        db.session.add_all([doc, witness, paralegal])
        db.session.commit()
        question = DepositionQuestion(
            witness_id=witness.id,
            category="General",
            question="Q?",
            source="DocD",
        )
        db.session.add(question)
        db.session.commit()

        with pytest.raises(PermissionError):
            DepositionPrep.export_questions(witness.id, str(tmp_path / "denied.pdf"), paralegal.id)
        with pytest.raises(PermissionError):
            DepositionPrep.export_questions(witness.id, str(tmp_path / "denied.docx"), paralegal.id)
