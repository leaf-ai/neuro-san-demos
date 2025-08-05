from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import fitz
import spacy
from spacy.cli import download as spacy_download


@dataclass
class Span:
    """Represents a redaction span."""

    start: int
    end: int
    label: str
    text: str
    score: float | None = None


class PrivilegeDetector:
    """Detect and redact attorney–client privileged content.

    A spaCy model with a legal domain pipeline (e.g. ``en_legal_ner_trf``) or a
    fine‑tuned text classifier can be supplied. If the loaded model exposes a
    ``textcat``/``textcat_multilabel`` component, its ``PRIVILEGED`` (or
    configured) category score is used in conjunction with keyword and entity
    matching.
    """

    def __init__(
        self,
        model: str = "en_core_web_sm",
        textcat_label: str = "PRIVILEGED",
        threshold: float = 0.5,
    ) -> None:
        try:
            self.nlp = spacy.load(model)
        except OSError:
            spacy_download(model)
            self.nlp = spacy.load(model)
        self.textcat_label = textcat_label
        self.threshold = threshold
        # Keywords signalling potential privilege as a final fallback
        self.keywords = {
            "attorney-client",
            "privileged",
            "confidential legal advice",
            "legal opinion",
        }

    def detect(self, text: str) -> Tuple[bool, List[Span]]:
        """Return whether text appears privileged and any spans to redact."""
        doc = self.nlp(text)
        spans: List[Span] = []
        privileged = False

        # Use text classification if available
        if any(p in self.nlp.pipe_names for p in ["textcat", "textcat_multilabel"]):
            score = doc.cats.get(self.textcat_label, 0.0)
            if score >= self.threshold:
                privileged = True
        else:
            score = None

        # Use entity labels from legal models
        for ent in getattr(doc, "ents", []):
            if ent.label_.lower() in {"privileged", "attorney_client"}:
                spans.append(Span(ent.start_char, ent.end_char, ent.label_, ent.text, score))
                privileged = True

        # Fallback keyword scan
        lowered = {k.lower() for k in self.keywords}
        for sent in doc.sents:
            sent_lower = sent.text.lower()
            if any(k in sent_lower for k in lowered):
                spans.append(Span(sent.start_char, sent.end_char, "PRIVILEGED", sent.text, score))
                privileged = True
        return privileged, spans

    @staticmethod
    def redact_text(text: str, spans: List[Span]) -> str:
        """Return ``text`` with ``spans`` replaced by redaction markers."""
        redacted = text
        for span in sorted(spans, key=lambda s: s.start, reverse=True):
            redacted = redacted[: span.start] + "[REDACTED]" + redacted[span.end :]
        return redacted

    @staticmethod
    def redact_pdf(input_path: str, output_path: str, keywords: List[str]) -> None:
        """Redact occurrences of ``keywords`` in ``input_path`` PDF."""
        doc = fitz.open(input_path)
        for page in doc:
            for kw in keywords:
                for rect in page.search_for(kw):
                    page.add_redact_annot(rect, text="[REDACTED]")
            page.apply_redactions()
        doc.save(output_path)


__all__ = ["PrivilegeDetector", "Span"]
