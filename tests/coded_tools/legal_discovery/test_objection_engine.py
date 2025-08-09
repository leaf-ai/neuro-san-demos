from types import SimpleNamespace

from apps.legal_discovery.trial_assistant.services.objection_engine import ObjectionEngine, db


def noop(*args, **kwargs):
    return None


def test_counter_objection_detection(monkeypatch):
    engine = ObjectionEngine()
    monkeypatch.setattr(db.session, "add", noop)
    monkeypatch.setattr(db.session, "commit", noop)
    seg = SimpleNamespace(id="s1", text="That was an excited utterance")
    events = engine.analyze_segment("sess", seg)
    assert any(e.type == "counter" and e.ground == "hearsay" for e in events)

