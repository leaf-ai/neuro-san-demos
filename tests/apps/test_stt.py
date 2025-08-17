from apps.legal_discovery.stt import stream_transcribe


def test_stream_transcribe_offline():
    frames = [b"test"]
    result = list(stream_transcribe(frames))
    assert result[-1]["error"] == "stt_unavailable"
