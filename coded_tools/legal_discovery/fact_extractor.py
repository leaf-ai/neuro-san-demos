"""Extract factual statements and metadata from documents."""

from __future__ import annotations

from typing import Any, Dict, List

import spacy
from spacy.cli import download as spacy_download


class FactExtractor:
    """Identify facts, parties, actions and dates using spaCy."""

    def __init__(self, model: str = "en_core_web_sm") -> None:
        """Load a spaCy pipeline, downloading the model if necessary."""
        try:
            self.nlp = spacy.load(model)
        except OSError:
            spacy_download(model)
            self.nlp = spacy.load(model)

    def extract(self, text: str) -> List[Dict[str, Any]]:
        """Return a list of facts with parties, actions and dates.

        Parameters
        ----------
        text: str
            Raw document text.
        """
        doc = self.nlp(text)
        facts: List[Dict[str, Any]] = []
        for sent in doc.sents:
            parties: List[str] = []
            dates: List[str] = []
            for ent in sent.ents:
                if ent.label_ in {"PERSON", "ORG"}:
                    parties.append(ent.text)
                elif ent.label_ == "DATE":
                    dates.append(ent.text)
            actions = [token.lemma_ for token in sent if token.pos_ == "VERB"]
            if parties or dates or actions:
                facts.append(
                    {
                        "text": sent.text.strip(),
                        "parties": parties,
                        "dates": dates,
                        "actions": actions,
                    }
                )
        return facts
