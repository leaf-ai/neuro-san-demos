from __future__ import annotations
import re
import yaml
from typing import List
from ...models_trial import ObjectionEvent, TranscriptSegment
from ...database import db


class ObjectionEngine:
    def __init__(self, rules_path: str = "apps/legal_discovery/rules/objections.yaml"):
        with open(rules_path, "r", encoding="utf-8") as f:
            self.rules = yaml.safe_load(f)
        self.compiled = []
        for name, spec in self.rules.get("objections", {}).items():
            patterns = [re.compile(r, re.I) for r in spec.get("patterns", {}).get("transcript_regex", [])]
            cures = spec.get("cures", [])
            self.compiled.append((name, patterns, cures))

    def analyze_segment(self, session_id: str, seg: TranscriptSegment) -> List[ObjectionEvent]:
        text = seg.text or ""
        found: List[ObjectionEvent] = []
        for ground, patterns, cures in self.compiled:
            if any(p.search(text) for p in patterns):
                evt = ObjectionEvent(
                    session_id=session_id,
                    segment_id=seg.id,
                    type="incoming" if "objection" in text.lower() else "risk",
                    ground=ground,
                    confidence=85,
                    extracted_phrase=text[:160],
                    suggested_cures=cures,
                )
                db.session.add(evt)
                found.append(evt)
        if found:
            db.session.commit()
        return found


def create_engine() -> ObjectionEngine:
    return ObjectionEngine()


engine = create_engine()
