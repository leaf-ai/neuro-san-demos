from coded_tools.legal_discovery.document_scorer import DocumentScorer
from coded_tools.legal_discovery.sanctions_risk_analyzer import SanctionsRiskAnalyzer


def test_document_scorer_values():
    scorer = DocumentScorer()
    text = "This is a confidential timeline event with privileged notes."
    scores = scorer.score(text)
    for key in ("probative_value", "admissibility_risk", "narrative_alignment", "score_confidence"):
        assert 0 <= scores[key] <= 1


def test_sanctions_uses_scorecard(monkeypatch):
    captured = {}

    class DummyLLM:
        def invoke(self, prompt, timeout=60):
            captured["prompt"] = prompt
            class R:
                content = '{"risk":"low","analysis":"ok"}'
            return R()

    import coded_tools.legal_discovery.sanctions_risk_analyzer as sra

    monkeypatch.setattr(sra, "ChatGoogleGenerativeAI", lambda **kw: DummyLLM())
    analyzer = sra.SanctionsRiskAnalyzer()
    analyzer.assess("text", scorecard={"probative_value": 0.5})
    assert "probative_value" in captured["prompt"]
