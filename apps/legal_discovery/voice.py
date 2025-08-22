"""Text to speech utilities with caching support."""

import base64
import importlib.util
import logging
import os
import time
from io import BytesIO
from typing import Dict, List

from prometheus_client import Counter, Histogram

from .database import db
from .models import VoiceCache
from .feature_flags import FEATURE_FLAGS

try:  # pragma: no cover - optional
    import redis
except Exception:  # pragma: no cover - allow missing dependency
    redis = None

_redis_client = None
if redis is not None:
    url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    try:  # pragma: no cover - best effort connection
        _redis_client = redis.Redis.from_url(url)
    except Exception:
        _redis_client = None


logger = logging.getLogger(__name__)

# Prometheus metrics
tts_latency = Histogram("tts_latency_seconds", "Time spent generating speech audio")
tts_errors = Counter("tts_errors_total", "Count of TTS synthesis failures")


def _cache_get(key: str, text: str, model: str) -> str:
    if _redis_client:
        val = _redis_client.get(key)
        if isinstance(val, bytes):
            return val.decode("utf-8")
    record = VoiceCache.query.filter_by(text=text, model=model).first()
    return record.audio if record else ""


def _cache_set(key: str, audio: str, text: str, model: str) -> None:
    if _redis_client:
        _redis_client.set(key, audio)
    db.session.add(VoiceCache(text=text, model=model, audio=audio))
    db.session.commit()


def _synthesize_gtts(text: str, model: str) -> str:
    from gtts import gTTS  # pragma: no cover - network dependent

    audio_io = BytesIO()
    gTTS(text=text, lang=model).write_to_fp(audio_io)
    audio_io.seek(0)
    return base64.b64encode(audio_io.read()).decode("utf-8")


def _synthesize_coqui(text: str, model: str) -> str:
    from TTS.api import TTS  # pragma: no cover - heavy dependency
    import soundfile as sf  # pragma: no cover

    tts = TTS(model)
    wav = tts.tts(text)
    buf = BytesIO()
    sf.write(buf, wav, samplerate=tts.synthesizer.output_sample_rate, format="WAV")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def _synthesize_system(text: str, model: str) -> str:
    import pyttsx3  # pragma: no cover - optional
    import tempfile

    engine = pyttsx3.init()
    engine.setProperty("voice", model)
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        engine.save_to_file(text, tmp.name)
        engine.runAndWait()
        tmp.seek(0)
        data = tmp.read()
    os.unlink(tmp.name)
    return base64.b64encode(data).decode("utf-8")


# Only register Coqui engine if the optional dependency is present
_ENGINE_MAP = {
    "gtts": _synthesize_gtts,
    "system": _synthesize_system,
}
if importlib.util.find_spec("TTS") is not None:
    _ENGINE_MAP["coqui"] = _synthesize_coqui


def synthesize_voice(text: str, model: str) -> str:
    """Generate base64-encoded audio, cached by text and model."""
    if not FEATURE_FLAGS["voice_tts"]:
        return ""
    key = f"{model}:{text}"
    cached = _cache_get(key, text, model)
    if cached:
        return cached

    engine = os.getenv("VOICE_ENGINE", "gtts").lower()
    synth = _ENGINE_MAP.get(engine, _synthesize_gtts)
    start = time.perf_counter()
    try:
        audio = synth(text, model)
    except Exception as exc:  # pragma: no cover
        tts_errors.inc()
        logger.exception("TTS synthesis failed: %s", exc)
        audio = ""
    tts_latency.observe(time.perf_counter() - start)
    logger.info("TTS synthesis via %s completed in %.3fs", engine, time.perf_counter() - start)
    if audio:
        _cache_set(key, audio, text, model)
    return audio


def get_available_voices() -> List[Dict[str, str]]:
    """Return list of available voices for the configured engine."""
    if not FEATURE_FLAGS["voice_tts"]:
        return []
    engine = os.getenv("VOICE_ENGINE", "gtts").lower()
    if engine == "system":
        try:  # pragma: no cover - optional
            import pyttsx3

            eng = pyttsx3.init()
            return [{"id": v.id, "name": v.name} for v in eng.getProperty("voices")]
        except Exception:
            return []
    if engine == "coqui":
        try:  # pragma: no cover - optional
            from TTS.utils.manage import ModelManager

            manager = ModelManager()
            models = manager.list_models()
            return [{"id": m, "name": m} for m in models]
        except Exception:
            return []
    try:
        from gtts.lang import tts_langs

        langs = tts_langs()
        return [{"id": code, "name": name} for code, name in langs.items()]
    except Exception:  # pragma: no cover
        return []


__all__ = ["synthesize_voice", "get_available_voices"]
