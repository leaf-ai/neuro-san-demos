import os

FEATURE_FLAGS = {
    "theories": os.getenv("ENABLE_THEORIES", "1") == "1",
    "binder": os.getenv("ENABLE_BINDER", "1") == "1",
    "chat": os.getenv("ENABLE_CHAT", "1") == "1",
}

__all__ = ["FEATURE_FLAGS"]
