import os
from neuro_san.interfaces.coded_tool import CodedTool

try:
    from .courtlistener_client import CourtListenerClient
except Exception:  # pragma: no cover - optional
    CourtListenerClient = None


class ResearchTools(CodedTool):
    """Simple research wrapper around CourtListenerClient."""

    def search(self, query: str):
        if not CourtListenerClient:
            return []
        client = CourtListenerClient()
        try:
            results = client.search_opinions(query)
        except Exception:
            results = {}
        return results
