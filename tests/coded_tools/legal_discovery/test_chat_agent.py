import sys
import types

# Stub minimal neuro_san.interfaces.coded_tool for tests
neuro_san = types.ModuleType("neuro_san")
interfaces = types.ModuleType("neuro_san.interfaces")
coded_tool = types.ModuleType("neuro_san.interfaces.coded_tool")

class CodedTool:  # type: ignore
    pass

coded_tool.CodedTool = CodedTool
interfaces.coded_tool = coded_tool
neuro_san.interfaces = interfaces
sys.modules.setdefault("neuro_san", neuro_san)
sys.modules.setdefault("neuro_san.interfaces", interfaces)
sys.modules.setdefault("neuro_san.interfaces.coded_tool", coded_tool)

# Stub embeddings package
lg = types.ModuleType("langchain_google_genai")

class GoogleGenerativeAIEmbeddings:  # type: ignore
    def embed_query(self, text: str):
        return [0.1, 0.2]

lg.GoogleGenerativeAIEmbeddings = GoogleGenerativeAIEmbeddings
sys.modules.setdefault("langchain_google_genai", lg)

# Stub neo4j driver
neo4j = types.ModuleType("neo4j")

class GraphDatabase:  # type: ignore
    def driver(self, *_, **__):
        raise RuntimeError("no neo4j")

neo4j.GraphDatabase = GraphDatabase
sys.modules.setdefault("neo4j", neo4j)

# Stub pyvis Network
pyvis = types.ModuleType("pyvis")
pyvis_network = types.ModuleType("pyvis.network")

class Network:  # type: ignore
    def __init__(self, *_, **__):
        pass

    def add_node(self, *args, **kwargs):
        pass

    def add_edge(self, *args, **kwargs):
        pass

    def save_graph(self, *args, **kwargs):
        return "graph.html"

pyvis_network.Network = Network
pyvis.network = pyvis_network
sys.modules.setdefault("pyvis", pyvis)
sys.modules.setdefault("pyvis.network", pyvis_network)

# Stub privilege detector module to avoid heavy deps
priv_mod = types.ModuleType("coded_tools.legal_discovery.privilege_detector")

class PrivilegeDetector:  # type: ignore
    def detect(self, text):
        return ("privileged" in text.lower(), [])

    def redact_text(self, text, spans):
        return text.replace("privileged", "[REDACTED]")

priv_mod.PrivilegeDetector = PrivilegeDetector
sys.modules.setdefault("coded_tools.legal_discovery.privilege_detector", priv_mod)

# Stub chromadb client
chromadb = types.ModuleType("chromadb")
chromadb_config = types.ModuleType("chromadb.config")

class Settings:  # type: ignore
    pass

chromadb_config.Settings = Settings
chromadb.config = chromadb_config

class HttpClient:  # type: ignore
    def __init__(self, *_, **__):
        pass

    def get_or_create_collection(self, *_args, **_kwargs):
        class Coll:
            def add(self, *a, **k):
                pass

            def query(self, *a, **k):
                return {"ids": [[]], "metadatas": [[]], "documents": [[]]}

            def get(self, *a, **k):
                return {}

            def delete(self, *a, **k):
                pass

            def count(self):
                return 0

        return Coll()

chromadb.HttpClient = HttpClient
sys.modules.setdefault("chromadb", chromadb)
sys.modules.setdefault("chromadb.config", chromadb_config)

import coded_tools.legal_discovery.chat_agent as ca

from coded_tools.legal_discovery.chat_agent import RetrievalChatAgent
from apps.legal_discovery.database import db
from flask import Flask


class DummyVectorDB:
    def __init__(self):
        self.store = {}

    def add_messages(self, messages, metadatas, ids, embeddings):
        for text, md, mid in zip(messages, metadatas, ids):
            self.store[mid] = {"document": text, "metadata": md}

    def add_conversations(self, texts, metadatas, ids, embeddings):
        pass

    def query_messages(self, query_texts=None, n_results=10, where=None, query_embeddings=None):
        docs = []
        metas = []
        for mid, data in self.store.items():
            vis = data["metadata"].get("visibility")
            if where and vis != where.get("visibility"):
                continue
            docs.append(data["document"])
            metas.append({"message_id": data["metadata"].get("message_id")})
        return {"documents": [docs], "metadatas": [metas]}

    def add_documents(self, *args, **kwargs):
        pass

    def query(self, *args, **kwargs):
        return {"ids": [[]], "metadatas": [[]]}


class DummyGraph:
    def create_node(self, *args, **kwargs):
        return 1

    def create_relationship(self, *args, **kwargs):
        pass


class DummyEmbeddings:
    def embed_query(self, text):
        return [0.1, 0.2]


def test_privileged_messages_excluded(monkeypatch):
    monkeypatch.setattr(ca, "GoogleGenerativeAIEmbeddings", lambda: DummyEmbeddings())
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    db.init_app(app)
    with app.app_context():
        db.create_all()
        agent = RetrievalChatAgent(vector_db=DummyVectorDB(), graph_db=DummyGraph())
        pub = agent.store_message(None, sender_id=1, content="public memo")
        priv = agent.store_message(pub.conversation_id, 1, "privileged advice")
        result = agent.query("memo", sender_id=1, conversation_id=pub.conversation_id)
        texts = [m["content"] for m in result["messages"]]
        assert any("public" in t for t in texts)
        assert all("privileged" not in t for t in texts)
        assert pub.vector_id
        assert priv.vector_id
