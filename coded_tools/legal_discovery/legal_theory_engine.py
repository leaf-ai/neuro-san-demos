from __future__ import annotations

from typing import Any, Dict, List, Optional

from neuro_san.interfaces.coded_tool import CodedTool

from .knowledge_graph_manager import KnowledgeGraphManager
from .ontology_loader import OntologyLoader


class LegalTheoryEngine(CodedTool):
    """Suggest legal theories by linking facts to ontology elements."""

    def __init__(self, kg: Optional[KnowledgeGraphManager] = None, loader: Optional[OntologyLoader] = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.kg = kg or KnowledgeGraphManager()
        self.loader = loader or OntologyLoader()

    def suggest_theories(self) -> List[Dict[str, Any]]:
        """Return ranked candidate theories based on graph support."""
        ontology = self.loader.load()["causes_of_action"]
        suggestions: List[Dict[str, Any]] = []
        for cause, data in ontology.items():
            elements = data.get("elements", [])
            element_results: List[Dict[str, Any]] = []
            for element in elements:
                query = (
                    "MATCH (f:Fact)-[r:SUPPORTS]->(e:Element {name:$element})"
                    "-[:BELONGS_TO]->(c:CauseOfAction {name:$cause}) "
                    "RETURN f.text as text, r.weight as weight"
                )
                records = self.kg.run_query(query, {"element": element, "cause": cause})
                facts = [
                    {"text": r["text"], "weight": r.get("weight", 0)} for r in records
                ]
                element_weight = max((r.get("weight", 0) for r in records), default=0)
                element_results.append(
                    {"name": element, "facts": facts, "weight": element_weight}
                )
            score = (
                sum(e["weight"] for e in element_results) / len(elements)
                if elements
                else 0
            )
            suggestions.append({"cause": cause, "score": score, "elements": element_results})
        suggestions.sort(key=lambda s: s["score"], reverse=True)
        return suggestions

            defenses = data.get("defenses", [])
            indicators = data.get("indicators", [])
            element_results: List[Dict[str, Any]] = []
            supported = 0
            for element in elements:
                query = (
                    "MATCH (f:Fact)-[:SUPPORTS]->(e:Element {name:$element})"
                    "-[:BELONGS_TO]->(c:CauseOfAction {name:$cause}) "
                    "RETURN f.text as text"
                )
                records = self.kg.run_query(query, {"element": element, "cause": cause})
                facts = [r["text"] for r in records]
                if facts:
                    supported += 1
                element_results.append({"name": element, "facts": facts})
            score = supported / len(elements) if elements else 0
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
        self.kg.close()
