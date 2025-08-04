from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import fitz
import spacy
from spacy.cli import download as spacy_download


@dataclass
class Span:
    start: int
    end: int
    label: str


class PrivilegeDetector:
    """Detect and redact attorney–client privileged content."""

    def __init__(self, model: str = "en_core_web_sm") -> None:
        try:
            self.nlp = spacy.load(model)
        except OSError:
            spacy_download(model)
            self.nlp = spacy.load(model)
        # Keywords signalling potential privilege
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
        lowered = {k.lower() for k in self.keywords}
        for sent in doc.sents:
            sent_lower = sent.text.lower()
            if any(k in sent_lower for k in lowered):
                spans.append(Span(sent.start_char, sent.end_char, "PRIVILEGED"))
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
