from apps.legal_discovery.interface_flask import app
from apps.legal_discovery.stt import stt_errors, stream_transcribe


def test_metrics_endpoint_available():
    client = app.test_client()
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert b"stt_latency_seconds" in resp.data or b"python_info" in resp.data


def test_stt_error_counter_increments():
    start = stt_errors._value.get()
    list(stream_transcribe([b"test"]))
    end = stt_errors._value.get()
    assert end >= start + 1
