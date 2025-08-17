from typing import Generator, Iterable

def stream_transcribe(audio_iter: Iterable[bytes]) -> Generator[dict, None, None]:
    """Yield transcription results from a stream of audio bytes.

    The generator attempts to use a local Whisper model for speech-to-text. If the
    model cannot be loaded, a single dictionary with an error key is yielded
    to signal the caller that transcription is unavailable. Each yielded mapping
    contains text and is_final keys; interim chunks have is_final set
    to False.
    """

    try:  # pragma: no cover - best effort to load optional dependency
        import whisper  # type: ignore

        model = whisper.load_model('base')
    except Exception:  # pragma: no cover - model is optional
        for _ in audio_iter:
            pass
        yield {'text': '', 'is_final': True, 'error': 'stt_unavailable'}
        return

    buffer = bytearray()
    for chunk in audio_iter:
        buffer.extend(chunk)
        try:
            result = model.transcribe(bytes(buffer), fp16=False)
            text = result.get('text', '').strip()
            if text:
                yield {'text': text, 'is_final': False}
        except Exception:  # pragma: no cover - transcription failure
            yield {'text': '', 'is_final': True, 'error': 'transcription_error'}
            return

    try:
        result = model.transcribe(bytes(buffer), fp16=False)
        text = result.get('text', '').strip()
    except Exception:  # pragma: no cover - final transcription failure
        yield {'text': '', 'is_final': True, 'error': 'transcription_error'}
    else:
        yield {'text': text, 'is_final': True}


__all__ = ['stream_transcribe']
