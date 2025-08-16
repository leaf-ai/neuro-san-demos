from __future__ import annotations

"""Pretrial statement generation and export utilities."""

from pathlib import Path
import logging

from google import genai
import os
from neuro_san.interfaces.coded_tool import CodedTool

from .document_drafter import DocumentDrafter
from .timeline_manager import TimelineManager

try:  # pragma: no cover - optional import in some environments
    from apps.legal_discovery.exhibit_manager import generate_binder
except Exception:  # pragma: no cover - binder not available
    generate_binder = None

try:  # pragma: no cover - optional import of ORM models
    from apps.legal_discovery.models import Fact, FactConflict, LegalTheory, Witness
except Exception:  # pragma: no cover - test environments may not load app modules
    Fact = FactConflict = LegalTheory = Witness = None


class PretrialGenerator(CodedTool):
    """Generate pretrial statements from approved theories and evidence."""

    def __init__(self, model_name: str = "gemini-2.5-flash", temperature: float = 0.2, **kwargs):
        super().__init__(**kwargs)
        self.model_name = model_name
        self.temperature = temperature

    def generate_statement(self, cause: str, elements: list[str]) -> str:
        prompt = (
            f"Prepare a pretrial statement for {cause} covering: "
            + ", ".join(elements)
        )
        api_key = os.getenv("GOOGLE_API_KEY", "")
        if api_key:
            try:
                client = genai.Client(api_key=api_key)
                resp = client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=genai.types.GenerateContentConfig(
                        temperature=self.temperature
                    ),
                )
                return resp.text
            except Exception as exc:  # pragma: no cover - best effort
                logging.warning("pretrial statement generation failed: %s", exc)
        return prompt

    # ------------------------------------------------------------------
    # Data aggregation
    # ------------------------------------------------------------------
    def aggregate(self, case_id: int) -> dict:
        """Collect stipulations, contested issues and witnesses for a case."""

        if LegalTheory is None:  # pragma: no cover - safety check
            return {"stipulations": [], "contested": [], "witnesses": [], "timeline": []}

        theories = LegalTheory.query.filter_by(case_id=case_id, status="approved").all()

        stipulations: list[str] = []
        contested: list[str] = []
        witness_ids: set[int] = set()
        timeline: list[dict] = []

        for theory in theories:
            facts = Fact.query.filter_by(legal_theory_id=theory.id).all()
            for fact in facts:
                if fact.witness_id:
                    witness_ids.add(fact.witness_id)
                if fact.dates:
                    for d in fact.dates:
                        timeline.append({"date": d, "description": fact.text})

                conflict = FactConflict.query.filter(
                    (FactConflict.fact1_id == fact.id)
                    | (FactConflict.fact2_id == fact.id)
                ).first()
                if conflict:
                    contested.append(conflict.description)
                else:
                    stipulations.append(fact.text)

        witnesses = []
        for wid in witness_ids:
            w = Witness.query.get(wid)
            if w:
                witnesses.append(w.name)

        return {
            "stipulations": stipulations,
            "contested": contested,
            "witnesses": witnesses,
            "timeline": timeline,
        }

    # ------------------------------------------------------------------
    # Drafting utilities
    # ------------------------------------------------------------------
    def draft(self, case_id: int) -> tuple[str, dict]:
        """Use Gemini 2.5 to draft a pretrial statement for the case."""

        data = self.aggregate(case_id)
        lines = ["Prepare a concise pretrial statement using the data below.", ""]
        lines.append("Stipulations:")
        lines.extend(f"- {s}" for s in data["stipulations"] or ["None"])
        lines.append("\nContested Issues:")
        lines.extend(f"- {c}" for c in data["contested"] or ["None"])
        lines.append("\nWitnesses:")
        lines.extend(f"- {w}" for w in data["witnesses"] or ["None"])

        prompt = "\n".join(lines)
        api_key = os.getenv("GOOGLE_API_KEY", "")
        if api_key:
            try:
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=genai.types.GenerateContentConfig(temperature=self.temperature),
                )
                text = response.text
            except Exception as exc:  # pragma: no cover - best effort
                logging.warning("pretrial draft failed: %s", exc)
                text = prompt
        else:
            text = prompt
        return text, data

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------
    def export(self, case_id: int, file_path: str) -> str:
        """Generate and export a DOCX pretrial statement."""

        text, data = self.draft(case_id)
        path = Path(file_path)
        drafter = DocumentDrafter()
        drafter.create_document(str(path), text)

        tm = TimelineManager()
        if data["timeline"]:
            tm.create_timeline(f"case_{case_id}_pretrial", data["timeline"])

        if generate_binder is not None:
            generate_binder(case_id)

        return str(path)


__all__ = ["PretrialGenerator"]

