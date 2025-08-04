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

    def close(self) -> None:
        self.kg.close()
