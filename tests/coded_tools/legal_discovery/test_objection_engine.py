from types import SimpleNamespace

from apps.legal_discovery.trial_assistant.services.objection_engine import ObjectionEngine
from apps.legal_discovery.models import ObjectionEvent


def test_counter_objection_detection(monkeypatch):
    engine = ObjectionEngine()

    def fake_log(**kwargs):
        return ObjectionEvent(**kwargs)

    monkeypatch.setattr(
        "apps.legal_discovery.trial_assistant.services.objection_engine.log_objection_event",
        fake_log,
    )
    seg = SimpleNamespace(id="s1", text="That was an excited utterance")
    events = engine.analyze_segment("sess", seg)
    assert any(e.type == "counter" and e.ground == "hearsay" for e in events)

