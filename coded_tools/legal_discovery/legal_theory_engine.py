"""Evaluate legal theories by matching facts to ontology elements.

The ``LegalTheoryEngine`` loads a cause-of-action ontology and then queries
both a Neo4j knowledge graph and an optional SQL database to determine which
theories have sufficient evidentiary support.  For each cause of action the
engine gathers supporting facts for every element, computes a score based on
how many elements are supported, and returns a structured summary.

The Neo4j queries expect ``Fact`` nodes linked to ``Element`` nodes via the
``SUPPORTS`` relationship and ``Element`` nodes linked to ``CauseOfAction``
via ``BELONGS_TO``.  When a SQLAlchemy session is supplied the engine will
also look for ``Fact`` records joined to ``Element`` and ``CauseOfAction``
tables to collect additional supporting facts.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from neuro_san.interfaces.coded_tool import CodedTool

from .knowledge_graph_manager import KnowledgeGraphManager
from .ontology_loader import OntologyLoader

try:  # pragma: no cover - optional dependency for SQL lookups
    from sqlalchemy.orm import Session
    from apps.legal_discovery.models import CauseOfAction, Element, Fact
except Exception:  # pragma: no cover - imports are optional for graph-only use
    Session = Any  # type: ignore[assignment]
    CauseOfAction = Element = Fact = None  # type: ignore[assignment]


class LegalTheoryEngine(CodedTool):
    """Suggest legal theories by linking facts to ontology elements."""

    def __init__(
        self,
        kg: Optional[KnowledgeGraphManager] = None,
        db_session: Optional[Session] = None,
        loader: Optional[OntologyLoader] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.kg = kg or KnowledgeGraphManager()
        self.db_session = db_session
        self.loader = loader or OntologyLoader()

    # ------------------------------------------------------------------
    # Internal helpers
    def _facts_for_element(self, cause: str, element: str) -> List[Dict[str, Any]]:
        """Return supporting facts for a cause/element pair.

        Facts are collected from the Neo4j knowledge graph and, when available,
        the SQL database.  Each fact is returned as a dictionary containing the
        fact text and an optional weight.
        """

        facts: List[Dict[str, Any]] = []

        # Neo4j query ---------------------------------------------------
        query = (
            "MATCH (f:Fact)-[r:SUPPORTS]->(e:Element {name:$element})"
            "-[:BELONGS_TO]->(c:CauseOfAction {name:$cause}) "
            "RETURN f.text AS text, r.weight AS weight"
        )

        try:
            records = self.kg.run_query(query, {"element": element, "cause": cause})
            for r in records:
                facts.append(
                    {
                        "text": r.get("text", ""),
                        "weight": r.get("weight", 0),
                        "source": "graph",
                    }
                )
        except Exception:  # pragma: no cover - graph may be unavailable
            pass

        # SQL query -----------------------------------------------------
        if self.db_session and Fact is not None:
            sql_records = (
                self.db_session.query(Fact)
                .join(Element)
                .join(CauseOfAction)
                .filter(Element.name == element, CauseOfAction.name == cause)
                .all()
            )
            for f in sql_records:
                facts.append(
                    {
                        "text": getattr(f, "text", ""),
                        "weight": getattr(f, "weight", 0),
                        "source": "sql",
                    }
                )

        return facts

    # ------------------------------------------------------------------
    # Public API
    def suggest_theories(self) -> List[Dict[str, Any]]:
        """Return ranked candidate theories based on factual support."""

        ontology = self.loader.load()["causes_of_action"]
        suggestions: List[Dict[str, Any]] = []

        for cause, data in ontology.items():
            elements: Sequence[str] = data.get("elements", [])
            defenses = data.get("defenses", [])
            indicators = data.get("indicators", [])

            element_results: List[Dict[str, Any]] = []
            total_weight = 0.0
            supported = 0

            for element in elements:
                facts = self._facts_for_element(cause, element)
                if facts:
                    supported += 1
                weight = max((f.get("weight", 0) for f in facts), default=0.0)
                total_weight += weight
                element_results.append({"name": element, "facts": facts, "weight": weight})

            weight_avg = total_weight / len(elements) if elements else 0
            coverage = supported / len(elements) if elements else 0
            score = (weight_avg + coverage) / 2

            suggestions.append(
                {
                    "cause": cause,
                    "score": score,
                    "elements": element_results,
                    "defenses": defenses,
                    "indicators": indicators,
                }
            )

        suggestions.sort(key=lambda s: s["score"], reverse=True)
        return suggestions

    def get_theory_subgraph(self, cause: str):
        """Expose subgraph retrieval for a specific cause of action."""

        return self.kg.get_cause_subgraph(cause)

    def close(self) -> None:
        """Clean up any external connections."""

        self.kg.close()


__all__ = ["LegalTheoryEngine"]

