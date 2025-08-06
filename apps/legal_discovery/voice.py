import base64
from io import BytesIO


def synthesize_voice(text: str, model: str) -> str:
    """Generate base64-encoded audio from text using gTTS."""
    try:  # pragma: no cover - best effort
        from gtts import gTTS

        audio_io = BytesIO()
        gTTS(text=text, lang=model).write_to_fp(audio_io)
        audio_io.seek(0)
        return base64.b64encode(audio_io.read()).decode("utf-8")
    except Exception:  # pragma: no cover
        return ""


__all__ = ["synthesize_voice"]
