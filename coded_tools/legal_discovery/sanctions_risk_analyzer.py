from __future__ import annotations

import json
import os
from typing import Any, Dict

from langchain_google_genai import ChatGoogleGenerativeAI
from neuro_san.interfaces.coded_tool import CodedTool


class SanctionsRiskAnalyzer(CodedTool):
    """Assess text for potential court-sanctions risk using Gemini."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._llm = ChatGoogleGenerativeAI(
            model=os.getenv("GOOGLE_MODEL_NAME", "gemini-2.5-flash-lite-preview-06-17")
        )

    def assess(self, text: str) -> Dict[str, str]:
        """Return risk level and reasoning for the provided text."""
        prompt = (
            "You are a legal ethics expert. Assess the sanctions risk of the"
            " following text. Respond with JSON {\"risk\":\"low|medium|high\","
            " \"analysis\":\"...\"}.\n\n" + text
        )
        try:
            raw = self._llm.invoke(prompt, timeout=60).content
            data = json.loads(raw)
        except Exception:  # pragma: no cover - best effort
            data = {"risk": "unknown", "analysis": raw if 'raw' in locals() else ""}
        return data


__all__ = ["SanctionsRiskAnalyzer"]
