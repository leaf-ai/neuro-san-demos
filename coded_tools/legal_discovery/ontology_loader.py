"""Utilities for loading the legal theory ontology."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional


class OntologyLoader:
    """Load and provide access to the legal theory ontology.

    The ontology is stored as a JSON file mapping causes of action to their
    elements, defenses and typical factual indicators.  This loader caches the
    parsed ontology so multiple tools and Flask routes can share the data
    without repeatedly hitting the filesystem.
    """

    def __init__(self, path: Optional[Path | str] = None) -> None:
        self.path = Path(path) if path else Path(__file__).with_name("legal_theory_ontology.json")
        self._ontology: Optional[Dict[str, Any]] = None

    def load(self) -> Dict[str, Any]:
        """Return the ontology as a dictionary, loading it if necessary."""
        if self._ontology is None:
            with self.path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if "causes_of_action" not in data:
                raise ValueError("Ontology must contain 'causes_of_action'")
            self._ontology = data
        return self._ontology

    def get_cause(self, name: str) -> Optional[Dict[str, Any]]:
        """Return a single cause of action by name."""
        ontology = self.load()
        return ontology.get("causes_of_action", {}).get(name)


__all__ = ["OntologyLoader"]
