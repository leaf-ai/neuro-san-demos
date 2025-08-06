import re
from neuro_san.interfaces.coded_tool import CodedTool


class DocumentScorer(CodedTool):
    """Heuristically score documents for evidentiary value."""

    RISK_WORDS = {"privileged", "confidential", "inadmissible", "hearsay"}
    NARRATIVE_WORDS = {"story", "timeline", "event", "narrative", "account"}

    def score(self, text: str) -> dict[str, float]:
        tokens = re.findall(r"\b\w+\b", text.lower())
        total = len(tokens) or 1
        unique = len(set(tokens))
        probative = min(1.0, unique / 500)
        risk = sum(1 for t in tokens if t in self.RISK_WORDS) / total
        narrative = sum(1 for t in tokens if t in self.NARRATIVE_WORDS) / total
        confidence = max(0.0, min(1.0, 1.0 - risk))
        return {
            "probative_value": round(probative, 3),
            "admissibility_risk": round(risk, 3),
            "narrative_alignment": round(narrative, 3),
            "score_confidence": round(confidence, 3),
        }


__all__ = ["DocumentScorer"]
