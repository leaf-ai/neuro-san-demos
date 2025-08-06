from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import requests
from neuro_san.interfaces.coded_tool import CodedTool


class DocumentFetcher(CodedTool):
    """Download remote documents for analysis."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def fetch(self, url: str, dest: str | None = None) -> str:
        """Fetch a document from ``url`` and optionally save it to ``dest``."""
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        if dest:
            path = Path(dest)
            path.write_bytes(response.content)
            return str(path)
        # default to temporary file
        filename = os.path.basename(url.split("?")[0]) or "downloaded_file"
        path = Path("/tmp") / filename
        path.write_bytes(response.content)
        return str(path)


__all__ = ["DocumentFetcher"]
