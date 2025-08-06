from __future__ import annotations

import logging
from typing import Any, Dict, List

from neuro_san.interfaces.coded_tool import CodedTool

from coded_tools.google_search import GoogleSearch


class InternetSearch(CodedTool):
    """Wrapper around :class:`GoogleSearch` for legal discovery agents."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._search = GoogleSearch()

    def search(self, query: str, **params: Any) -> List[Dict[str, Any]]:
        """Perform an internet search using Google Custom Search."""
        args: Dict[str, Any] = {"search_terms": query, **params}
        try:
            return self._search.invoke(args, {})
        except Exception as exc:  # pragma: no cover - network may fail
            logging.warning("google search failed: %s", exc)
            return []


__all__ = ["InternetSearch"]
