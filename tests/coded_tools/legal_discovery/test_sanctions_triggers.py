import json
import langchain_google_genai as genai


class DummyLLM:
    def __init__(self, *args, **kwargs):
        pass

    def invoke(self, *args, **kwargs):  # pragma: no cover - simple stub
        return type("R", (), {"content": ""})()


def test_rule_triggers_upgrade_risk(monkeypatch):
    monkeypatch.setattr(genai, "ChatGoogleGenerativeAI", DummyLLM)
    from coded_tools.legal_discovery.sanctions_risk_analyzer import SanctionsRiskAnalyzer
    analyzer = SanctionsRiskAnalyzer()

    class Dummy:
        content = json.dumps({"risk": "low", "analysis": "ok"})

    monkeypatch.setattr(analyzer._llm, "invoke", lambda *a, **k: Dummy())
    text = "This frivolous filing was made for an improper purpose and evidence was withheld causing spoliation."
    data = analyzer.assess(text)
    assert data["risk"] == "medium"
    assert "filing" in data["triggers"]
    assert "discovery" in data["triggers"]
    assert data["warning"]
