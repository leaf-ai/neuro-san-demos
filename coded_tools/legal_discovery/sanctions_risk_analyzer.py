from __future__ import annotations

import json
import os
from typing import Any, Dict, List

from langchain_google_genai import ChatGoogleGenerativeAI
from neuro_san.interfaces.coded_tool import CodedTool


class SanctionsRiskAnalyzer(CodedTool):
    """Assess text for potential court-sanctions risk using Gemini 2.5."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._llm = ChatGoogleGenerativeAI(
            model=os.getenv("GOOGLE_MODEL_NAME", "gemini-2.5-flash")
        )
        self._rules: Dict[str, List[str]] = {
            "filing": ["rule 11", "frivolous", "improper purpose"],
            "discovery": ["spoliation", "withheld", "failed to preserve", "discovery abuse"],
        }

    def _check_triggers(self, text: str) -> Dict[str, List[str]]:
        """Return matched keywords grouped by category."""
        lower = text.lower()
        hits: Dict[str, List[str]] = {}
        for category, keywords in self._rules.items():
            matched = [k for k in keywords if k in lower]
            if matched:
                hits[category] = matched
        return hits

    def assess(self, text: str, scorecard: Dict[str, float] | None = None) -> Dict[str, str]:
        """Return risk level and reasoning for the provided text."""
        score_info = ""
        if scorecard:
            score_info = "Evidence scores:" + json.dumps(scorecard) + "\n"
        prompt = (
            "You are a legal ethics expert. Assess the sanctions risk of the"
            " following text. Respond with JSON {\"risk\":\"low|medium|high\"," 
            " \"analysis\":\"...\"}.\n\n" + score_info + text
        )
        triggers = self._check_triggers(text)
        try:
            raw = self._llm.invoke(prompt, timeout=60).content
            data = json.loads(raw)
        except Exception:  # pragma: no cover - best effort
            data = {"risk": "unknown", "analysis": raw if 'raw' in locals() else ""}
        data["triggers"] = triggers
        if triggers:
            data["warning"] = ", ".join(
                f"{cat}: {', '.join(words)}" for cat, words in triggers.items()
            )
            if data.get("risk", "unknown") in {"low", "unknown"}:
                data["risk"] = "medium"
        else:
            data["warning"] = ""
        return data


__all__ = ["SanctionsRiskAnalyzer"]
