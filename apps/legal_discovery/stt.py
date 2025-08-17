import logging
import time
from typing import Generator, Iterable

from prometheus_client import Counter, Histogram

logger = logging.getLogger(__name__)

# Prometheus metrics
stt_latency = Histogram(
    "stt_latency_seconds", "Time spent processing speech-to-text audio"
)
stt_errors = Counter("stt_errors_total", "Count of STT transcription failures")


def stream_transcribe(audio_iter: Iterable[bytes]) -> Generator[dict, None, None]:
    """Yield transcription results from a stream of audio bytes.

    The generator attempts to use a local Whisper model for speech-to-text. If the
    model cannot be loaded, a single dictionary with an error key is yielded
    to signal the caller that transcription is unavailable. Each yielded mapping
    contains text and is_final keys; interim chunks have is_final set
    to False.
    """

    start = time.perf_counter()
    logger.info("STT transcription started")

    try:  # pragma: no cover - best effort to load optional dependency
        import whisper  # type: ignore

        model = whisper.load_model("base")
    except Exception as exc:  # pragma: no cover - model is optional
        stt_errors.inc()
        stt_latency.observe(time.perf_counter() - start)
        logger.exception("STT model unavailable: %s", exc)
        for _ in audio_iter:
            pass
        yield {"text": "", "is_final": True, "error": "stt_unavailable"}
        return

    buffer = bytearray()
    for chunk in audio_iter:
        buffer.extend(chunk)
        try:
            result = model.transcribe(bytes(buffer), fp16=False)
            text = result.get("text", "").strip()
            if text:
                yield {"text": text, "is_final": False}
        except Exception as exc:  # pragma: no cover - transcription failure
            stt_errors.inc()
            stt_latency.observe(time.perf_counter() - start)
            logger.exception("STT transcription failed: %s", exc)
            yield {"text": "", "is_final": True, "error": "transcription_error"}
            return

    try:
        result = model.transcribe(bytes(buffer), fp16=False)
        text = result.get("text", "").strip()
    except Exception as exc:  # pragma: no cover - final transcription failure
        stt_errors.inc()
        stt_latency.observe(time.perf_counter() - start)
        logger.exception("STT final transcription failed: %s", exc)
        yield {"text": "", "is_final": True, "error": "transcription_error"}
    else:
        stt_latency.observe(time.perf_counter() - start)
        logger.info("STT transcription completed in %.3fs", time.perf_counter() - start)
        yield {"text": text, "is_final": True}


__all__ = ["stream_transcribe", "stt_latency", "stt_errors"]
