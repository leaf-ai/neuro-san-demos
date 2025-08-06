import langchain_google_genai as genai


class DummyLLM:
    def __init__(self, *args, **kwargs):
        pass

    def invoke(self, *args, **kwargs):  # pragma: no cover - simple stub
        return type("R", (), {"content": ""})()


class DummyVector:
    def query(self, *args, **kwargs):
        return {"documents": [["doc"]], "metadatas": [[{}]]}

    def add_documents(self, *args, **kwargs):
        return None


class DummyGraph:
    def run_query(self, *args, **kwargs):
        return []

    def create_node(self, *args, **kwargs):
        return None


def test_cocounsel_surfaces_warning(monkeypatch):
    monkeypatch.setattr(genai, "ChatGoogleGenerativeAI", DummyLLM)
    monkeypatch.setattr(genai, "GoogleGenerativeAIEmbeddings", DummyLLM)
    from coded_tools.legal_discovery.cocounsel_agent import CocounselAgent
    agent = CocounselAgent(vector_db=DummyVector(), graph_db=DummyGraph())
    monkeypatch.setattr(agent.llm, "invoke", lambda *a, **k: type("R", (), {"content": "answer"})())
    monkeypatch.setattr(agent.internet_search, "search", lambda *a, **k: [])
    risk = {"risk": "high", "analysis": "", "warning": "spoliation", "triggers": {"discovery": ["spoliation"]}}
    monkeypatch.setattr(agent.sanctions_analyzer, "assess", lambda text: risk)
    result = agent.ask("question")
    assert result["sanctions_warning"]
    assert result["sanctions_risk"] == risk
