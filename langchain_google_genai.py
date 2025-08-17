class ChatGoogleGenerativeAI:  # pragma: no cover - simple stub
    def __init__(self, *args, **kwargs) -> None:
        raise RuntimeError("langchain_google_genai is unavailable")

    def invoke(self, *args, **kwargs):  # pragma: no cover - simple stub
        return type("R", (), {"content": ""})()


class GoogleGenerativeAIEmbeddings:  # pragma: no cover - simple stub
    def __init__(self, *args, **kwargs) -> None:
        raise RuntimeError("langchain_google_genai is unavailable")

    def embed_query(self, text: str):  # pragma: no cover - simple stub
        return []
