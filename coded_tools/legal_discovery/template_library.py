from __future__ import annotations

"""Template library for motion drafting."""

from neuro_san.interfaces.coded_tool import CodedTool

try:  # optional imports for runtime
    from apps.legal_discovery.models import Fact, LegalTheory, FactConflict
except Exception:  # pragma: no cover - used when app context missing
    Fact = LegalTheory = FactConflict = None  # type: ignore


class TemplateLibrary(CodedTool):
    """Load motion templates and populate them with case data."""

    MOTION_TEMPLATES = {
        "motion_to_dismiss": (
            "Draft a Motion to Dismiss using the following facts:\n{facts}\n"
            "Accepted theories:\n{theories}\nOpposition:\n{conflicts}"
        ),
        "motion_for_summary_judgment": (
            "Prepare a Motion for Summary Judgment grounded on these facts:\n{facts}\n"
            "Accepted theories:\n{theories}\nOpposition:\n{conflicts}"
        ),
        "motion_in_limine": (
            "Draft a Motion in Limine considering these facts:\n{facts}\n"
            "Accepted theories:\n{theories}\nOpposition:\n{conflicts}"
        ),
    }

    def available(self) -> list[str]:
        """Return available motion types."""
        return list(self.MOTION_TEMPLATES.keys())

    def build_prompt(self, motion_type: str) -> str:
        """Build an LLM prompt for the given motion type."""
        template = self.MOTION_TEMPLATES.get(motion_type)
        if not template:
            raise ValueError("Unknown motion type")

        facts_text = "No facts available."
        theories_text = "No accepted theories."
        conflicts_text = "No conflicts recorded."
        try:
            if Fact is not None:
                facts = Fact.query.order_by(Fact.id).all()
                if facts:
                    facts_text = "\n".join(f"- {f.text}" for f in facts)
            if LegalTheory is not None:
                theories = LegalTheory.query.filter_by(status="accepted").all()
                if theories:
                    theories_text = "\n".join(
                        f"- {t.theory_name}: {t.description or ''}" for t in theories
                    )
            if FactConflict is not None:
                conflicts = FactConflict.query.order_by(FactConflict.id).all()
                if conflicts:
                    conflicts_text = "\n".join(c.description for c in conflicts)
        except Exception:  # pragma: no cover - missing DB/app context
            pass

        return template.format(
            facts=facts_text, theories=theories_text, conflicts=conflicts_text
        )
