import os

FEATURE_FLAGS = {
    "theories": os.getenv("ENABLE_THEORIES", "1") == "1",
    "binder": os.getenv("ENABLE_BINDER", "1") == "1",
    "chat": os.getenv("ENABLE_CHAT", "1") == "1",
    # Voice subfeatures
    "voice_stt": os.getenv("ENABLE_VOICE_STT", "1") == "1",
    "voice_tts": os.getenv("ENABLE_VOICE_TTS", "1") == "1",
    "voice_commands": os.getenv("ENABLE_VOICE_COMMANDS", "1") == "1",
}

__all__ = ["FEATURE_FLAGS"]
