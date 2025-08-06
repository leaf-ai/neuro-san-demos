"""Extract factual statements and metadata from documents."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import spacy
from spacy.cli import download as spacy_download

from .ontology_loader import OntologyLoader


class FactExtractor:
    """Identify facts, parties, actions and dates using spaCy."""

    def __init__(self, model: str = "en_core_web_sm", loader: Optional[OntologyLoader] = None) -> None:
        """Load a spaCy pipeline and ontology data.

        Parameters
        ----------
        model: str
            spaCy model name to load. The model will be downloaded if missing.
        loader: OntologyLoader, optional
            Loader instance providing ontology elements for similarity scoring.
        """
        try:
            self.nlp = spacy.load(model)
        except OSError:
            spacy_download(model)
            self.nlp = spacy.load(model)
        self.loader = loader or OntologyLoader()

    def _match_element(self, sent: spacy.tokens.Span) -> Tuple[Optional[str], float]:
        """Return the most similar ontology element for the sentence."""
        ontology = self.loader.load()["causes_of_action"]
        best_element: Optional[str] = None
        best_score = 0.0
        sent_doc = sent.as_doc()
        for data in ontology.values():
            for element in data.get("elements", []):
                elem_doc = self.nlp(element)
                score = sent_doc.similarity(elem_doc)
                if score > best_score:
                    best_score = score
                    best_element = element
        return best_element, best_score

    def _extract_relationships(self, sent: spacy.tokens.Span) -> List[Dict[str, Optional[str]]]:
        """Extract simple subject-verb-object relationships from a sentence."""
        relationships: List[Dict[str, Optional[str]]] = []
        for token in sent:
            if token.dep_ == "ROOT" and token.pos_ == "VERB":
                subj = [w.text for w in token.lefts if w.dep_ in {"nsubj", "nsubjpass"}]
                obj = [w.text for w in token.rights if w.dep_ in {"dobj", "pobj", "attr", "dative"}]
                if subj or obj:
                    relationships.append(
                        {
                            "subject": " ".join(subj) if subj else None,
                            "verb": token.lemma_,
                            "object": " ".join(obj) if obj else None,
                        }
                    )
        return relationships

    def extract(self, text: str, source_reliability: float = 1.0) -> List[Dict[str, Any]]:
        """Return a list of facts with entity tags and confidence scores.

        Confidence is computed as ``similarity * source_reliability`` where
        similarity is the cosine similarity between the sentence and the
        closest matching ontology element.

        Parameters
        ----------
        text: str
            Raw document text.
        source_reliability: float, optional
            Multiplier in [0,1] representing the trustworthiness of the source.
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
                relationships = self._extract_relationships(sent)
                element, similarity = self._match_element(sent)
                confidence = max(min(similarity * source_reliability, 1.0), 0.0)
                facts.append(
                    {
                        "text": sent.text.strip(),
                        "parties": parties,
                        "dates": dates,
                        "actions": actions,
                        "relationships": relationships,
                        "element": element,
                        "confidence": confidence,
                    }
                )
        return facts
