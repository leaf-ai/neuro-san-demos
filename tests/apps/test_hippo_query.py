from flask import Flask
import pytest

from apps.legal_discovery.hippo import chunk_text, make_doc_id
from apps.legal_discovery.hippo_routes import bp as hippo_bp
from apps.legal_discovery.database import db
from apps.legal_discovery.models import RetrievalTrace
from apps.legal_discovery import auth as auth_module
from apps.legal_discovery import hippo
from apps.legal_discovery.extensions import cache_stats


class FakeRedis:
    def __init__(self):
        self.store: dict[str, str] = {}

    def get(self, key: str):
        return self.store.get(key)

    def setex(self, key: str, ttl: int, value: str):
        self.store[key] = value

    def scan_iter(self, pattern: str):
        import re

        regex = re.compile(pattern.replace("*", ".*"))
        for k in list(self.store.keys()):
            if regex.fullmatch(k):
                yield k

    def delete(self, key: str):
        self.store.pop(key, None)

    def ping(self):
        return True


@pytest.fixture(autouse=True)
def _no_auth(monkeypatch):
    monkeypatch.setattr(auth_module, "_require_auth", lambda: True)


def _create_app():
    app = Flask(__name__)
    app.register_blueprint(hippo_bp)
    return app


def test_chunker_deterministic():
    doc_id = make_doc_id("case", "path.txt")
    text = "Hello world " * 50
    segs1 = chunk_text(text, doc_id)
    segs2 = chunk_text(text, doc_id)
    assert [s.segment_id for s in segs1] == [s.segment_id for s in segs2]


def test_query_endpoint_returns_paths():
    app = _create_app()
    client = app.test_client()
    client.post(
        "/api/hippo/index",
        json={"case_id": "c1", "text": "Alice met Bob at Acme."},
    )
    res = client.post(
        "/api/hippo/query",
        json={"case_id": "c1", "query": "Bob"},
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["items"]
    assert "trace_id" in data and data["timings"]["total_ms"] >= 0
    first = data["items"][0]
    assert "segment_id" in first
    assert first["path"]  # at least one element


def test_query_scores_and_document_path():
    app = _create_app()
    client = app.test_client()
    client.post(
        "/api/hippo/index",
        json={"case_id": "c1", "text": "Alice met Bob at Acme."},
    )
    res = client.post(
        "/api/hippo/query",
        json={"case_id": "c1", "query": "Bob"},
    )
    data = res.get_json()
    first = data["items"][0]
    assert {"graph", "dense", "hybrid"}.issubset(first["scores"])  # scoring fields
    assert first["path"][0]["type"] == "Document"


def test_query_fallback_to_token_seeding():
    app = _create_app()
    client = app.test_client()
    client.post(
        "/api/hippo/index",
        json={"case_id": "c1", "text": "Alice met Bob at Acme."},
    )
    res = client.post(
        "/api/hippo/query",
        json={"case_id": "c1", "query": "Zoe met"},
    )
    assert res.status_code == 200
    assert res.get_json()["items"]  # tokens still return results


def test_query_return_paths_toggle():
    app = _create_app()
    client = app.test_client()
    client.post(
        "/api/hippo/index",
        json={"case_id": "c1", "text": "Alice met Bob at Acme."},
    )
    res = client.post(
        "/api/hippo/query",
        json={"case_id": "c1", "query": "Bob", "return_paths": False},
    )
    first = res.get_json()["items"][0]
    assert "path" not in first


def test_query_score_weights():
    app = _create_app()
    client = app.test_client()
    client.post(
        "/api/hippo/index",
        json={"case_id": "c1", "text": "Alice met Bob at Acme."},
    )
    base = client.post(
        "/api/hippo/query", json={"case_id": "c1", "query": "Bob"}
    ).get_json()
    weighted = client.post(
        "/api/hippo/query",
        json={"case_id": "c1", "query": "Bob", "graph_weight": 2.0},
    ).get_json()
    default_graph = base["items"][0]["scores"]["graph"]
    boosted_graph = weighted["items"][0]["scores"]["graph"]
    assert pytest.approx(boosted_graph, rel=1e-6) == default_graph * 2


def test_query_logs_retrieval_trace():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    app.register_blueprint(hippo_bp)
    with app.app_context():
        db.create_all()
        client = app.test_client()
        client.post(
            "/api/hippo/index",
            json={"case_id": "c1", "text": "Alice met Bob at Acme."},
        )
        res = client.post(
            "/api/hippo/query", json={"case_id": "c1", "query": "Bob"}
        )
        trace_id = res.get_json()["trace_id"]
        trace = db.session.query(RetrievalTrace).filter_by(trace_id=trace_id).first()
        assert trace is not None
        assert trace.results


def test_query_caching_and_invalidation(monkeypatch):
    app = _create_app()
    client = app.test_client()
    fake = FakeRedis()
    monkeypatch.setattr("apps.legal_discovery.extensions.redis_client", fake)
    cache_stats.clear()

    call_count = {"n": 0}

    def fake_query(case_id: str, query: str, k: int = 10):
        call_count["n"] += 1
        return {"items": []}

    monkeypatch.setattr(hippo, "hippo_query", fake_query)

    payload = {"case_id": "c1", "query": "Bob"}
    client.post("/api/hippo/query", json=payload)
    client.post("/api/hippo/query", json=payload)
    assert call_count["n"] == 1
    assert cache_stats["hits"] == 1
    assert cache_stats["misses"] == 1

    hippo.ingest_document("c1", "New text")
    client.post("/api/hippo/query", json=payload)
    assert call_count["n"] == 2
