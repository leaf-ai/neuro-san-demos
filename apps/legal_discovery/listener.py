from __future__ import annotations

from apps.message_bus import (
    FORENSIC_HASH_TOPIC,
    RESEARCH_INSIGHT_TOPIC,
    AUTO_DRAFTER_ALERT_TOPIC,
    TIMELINE_ALERT_TOPIC,
    MessageBus,
    TeamMessage,
)


bus = MessageBus()

_forensic_hashes: dict[str, str] = {}
_research_hashes: dict[str, str] = {}


def _cross_check(doc_id: str) -> None:
    f_hash = _forensic_hashes.get(doc_id)
    r_hash = _research_hashes.get(doc_id)
    if f_hash and r_hash and f_hash != r_hash:
        alert = {"doc_id": doc_id, "forensic_hash": f_hash, "research_hash": r_hash}
        bus.publish(AUTO_DRAFTER_ALERT_TOPIC, TeamMessage("tracker", alert))
        bus.publish(TIMELINE_ALERT_TOPIC, TeamMessage("tracker", alert))
        print(f"[legal_discovery] Contradiction detected for {doc_id}: {alert}")


def _handle_forensic(message: TeamMessage) -> None:
    doc_id = str(message.payload.get("doc_id"))
    _forensic_hashes[doc_id] = message.payload.get("hash", "")
    _cross_check(doc_id)
    print(
        f"[legal_discovery] Forensic hash from {message.source_team}: {message.payload}"
    )


def _handle_research(message: TeamMessage) -> None:
    doc_id = str(message.payload.get("doc_id"))
    _research_hashes[doc_id] = message.payload.get("hash", "")
    _cross_check(doc_id)
    print(
        f"[legal_discovery] Research insight from {message.source_team}: {message.payload}"
    )


def start_listening() -> None:
    bus.subscribe(FORENSIC_HASH_TOPIC, _handle_forensic)
    bus.subscribe(RESEARCH_INSIGHT_TOPIC, _handle_research)
