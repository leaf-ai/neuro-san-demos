from __future__ import annotations
"""Detect narrative discrepancies using Gemini 2.5 NLI."""

import json
from dataclasses import dataclass
from typing import List, Tuple

import google.generativeai as genai

from neuro_san.interfaces.coded_tool import CodedTool

from .vector_database_manager import VectorDatabaseManager
from apps.legal_discovery.models import (
    Document,
    DocumentSource,
    Fact,
    NarrativeDiscrepancy,
    db,
)


@dataclass
class DiscrepancyResult:
    """Structured result returned after analysis."""

    opposing_doc_id: int
    user_doc_id: int
    conflicting_claim: str
    evidence_excerpt: str
    confidence: float
    legal_theory_id: int | None
    calendar_event_id: int | None


class NarrativeDiscrepancyDetector(CodedTool):
    """Compare opposition documents to internal corpus and flag contradictions."""

    def __init__(self, model_name: str = "gemini-2.5-flash", **kwargs) -> None:
        super().__init__(**kwargs)
        self.model_name = model_name
        self.vectors = VectorDatabaseManager()

    def analyze(self, opposing_doc: Document) -> List[DiscrepancyResult]:
        """Run discrepancy detection for a single opposing document."""
        with open(opposing_doc.file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        chunks = [text[i : i + 500] for i in range(0, len(text), 500)]
        results: List[DiscrepancyResult] = []
        for chunk in chunks:
            query = self.vectors.query([chunk], n_results=3, where={"source": DocumentSource.USER.value})
            for doc_id in query.get("ids", [[]])[0]:
                try:
                    user_doc = Document.query.get(int(doc_id))
                    if not user_doc:
                        continue
                    with open(user_doc.file_path, "r", encoding="utf-8", errors="ignore") as uf:
                        user_text = uf.read()
                    label, conf = self._nli(chunk, user_text)
                    if label == "CONTRADICTION" and conf > 0:
                        theory_id = None
                        fact = Fact.query.filter_by(document_id=user_doc.id).first()
                        if fact:
                            theory_id = fact.legal_theory_id
                        discrepancy = NarrativeDiscrepancy(
                            opposing_doc_id=opposing_doc.id,
                            user_doc_id=user_doc.id,
                            conflicting_claim=chunk,
                            evidence_excerpt=user_text[:500],
                            confidence=conf,
                            legal_theory_id=theory_id,
                        )
                        db.session.add(discrepancy)
                        db.session.commit()
                        results.append(
                            DiscrepancyResult(
                                opposing_doc_id=opposing_doc.id,
                                user_doc_id=user_doc.id,
                                conflicting_claim=chunk,
                                evidence_excerpt=user_text[:200],
                                confidence=conf,
                                legal_theory_id=theory_id,
                                calendar_event_id=None,
                            )
                        )
                except Exception:  # pragma: no cover - best effort
                    continue
        return results

    def _nli(self, claim: str, evidence: str) -> Tuple[str, float]:
        """Use Gemini 2.5 to perform natural language inference."""
        prompt = (
            "Respond with JSON containing 'label' (CONTRADICTION, ENTAILMENT, NEUTRAL) "
            "and 'confidence' between 0 and 1 given the claim and evidence."\
            f"\nClaim: {claim}\nEvidence: {evidence}"
        )
        model = genai.GenerativeModel(self.model_name)
        response = model.generate_content(prompt)
        try:
            data = json.loads(response.text.strip())
            label = str(data.get("label", "NEUTRAL")).upper()
            confidence = float(data.get("confidence", 0))
        except Exception:  # pragma: no cover - best effort
            label = "NEUTRAL"
            confidence = 0.0
        return label, confidence
