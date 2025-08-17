import pytest


@pytest.fixture(autouse=True)
def stub_retrieval(monkeypatch):
    class DummyAgent:
        def query(self, **kwargs):
            return {"facts": [], "message_id": 1}

    monkeypatch.setattr(
        "apps.legal_discovery.chat_routes.RetrievalChatAgent", DummyAgent
    )
