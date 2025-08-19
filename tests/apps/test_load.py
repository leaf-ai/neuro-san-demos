import time
from concurrent.futures import ThreadPoolExecutor
from typing import List

from flask import Flask

from apps.legal_discovery.hippo_routes import bp as hippo_bp


def _create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(hippo_bp)
    return app


def _do_query(app: Flask) -> float:
    with app.test_client() as client:
        t0 = time.perf_counter()
        res = client.post(
            "/api/hippo/query", json={"case_id": "c1", "query": "Bob"}
        )
        assert res.status_code == 200
        return time.perf_counter() - t0


def test_p95_latency_under_900ms():
    app = _create_app()
    with app.test_client() as client:
        client.post(
            "/api/hippo/index", json={"case_id": "c1", "text": "Alice met Bob."}
        )
    with ThreadPoolExecutor(max_workers=200) as ex:
        latencies: List[float] = list(ex.map(lambda _: _do_query(app), range(200)))
    latencies.sort()
    p95 = latencies[int(len(latencies) * 0.95) - 1]
    assert p95 < 0.9
