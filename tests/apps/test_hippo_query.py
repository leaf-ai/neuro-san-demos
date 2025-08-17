from flask import Flask

from flask import Flask

from apps.legal_discovery.hippo import chunk_text, make_doc_id
from apps.legal_discovery.hippo_routes import bp as hippo_bp


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
    first = data["items"][0]
    assert "segment_id" in first
    assert first["path"]  # at least one element
