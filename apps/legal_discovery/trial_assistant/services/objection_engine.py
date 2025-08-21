"""Objection analysis engine for trial assistant."""

from __future__ import annotations

import re
from typing import Any, Dict, List

import yaml

from ...database import log_objection_event
from ...models import ObjectionEvent
from ...models_trial import TranscriptSegment


class ObjectionEngine:
    def __init__(self, rules_path: str = "apps/legal_discovery/rules/objections.yaml"):
        with open(rules_path, "r", encoding="utf-8") as f:
            self.rules = yaml.safe_load(f)
        self.compiled = []
        self.counter_compiled = []
        for name, spec in self.rules.get("objections", {}).items():
            patterns = [re.compile(r, re.I) for r in spec.get("patterns", {}).get("transcript_regex", [])]
            cures = spec.get("cures", [])
            self.compiled.append((name, patterns, cures))
            for counter in spec.get("counter_objections", []):
                cpats = [
                    re.compile(r, re.I)
                    for r in counter.get("patterns", {}).get("transcript_regex", [])
                ]
                responses = counter.get("cures", [])
                self.counter_compiled.append((name, cpats, responses))

    def analyze_segment(
        self,
        session_id: str,
        seg: TranscriptSegment,
        *,
        trace_id: str | None = None,
        refs: List[Dict] | None = None,
        path: Any | None = None,
    ) -> List[ObjectionEvent]:
        text = seg.text or ""
        found: List[ObjectionEvent] = []
        for ground, patterns, cures in self.compiled:
            if any(p.search(text) for p in patterns):
                evt = log_objection_event(
                    session_id=session_id,
                    segment_id=seg.id,
                    type="incoming" if "objection" in text.lower() else "risk",
                    ground=ground,
                    confidence=85,
                    extracted_phrase=text[:160],
                    suggested_cures=cures,
                    trace_id=trace_id,
                    refs=refs,
                    path=path,
                )
                if evt:
                    found.append(evt)
        for ground, patterns, cures in self.counter_compiled:
            if any(p.search(text) for p in patterns):
                evt = log_objection_event(
                    session_id=session_id,
                    segment_id=seg.id,
                    type="counter",
                    ground=ground,
                    confidence=80,
                    extracted_phrase=text[:160],
                    suggested_cures=cures,
                    trace_id=trace_id,
                    refs=refs,
                    path=path,
                )
                if evt:
                    found.append(evt)
        return found


def create_engine() -> ObjectionEngine:
    return ObjectionEngine()


engine = create_engine()
