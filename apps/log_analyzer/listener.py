from __future__ import annotations

from apps.message_bus import (
    FORENSIC_HASH_TOPIC,
    RESEARCH_INSIGHT_TOPIC,
    MessageBus,
    TeamMessage,
)


bus = MessageBus()


def _handle_forensic(message: TeamMessage) -> None:
    print(f"[log_analyzer] Forensic hash from {message.source_team}: {message.payload}")


def _handle_research(message: TeamMessage) -> None:
    print(f"[log_analyzer] Research insight from {message.source_team}: {message.payload}")


def start_listening() -> None:
    bus.subscribe(FORENSIC_HASH_TOPIC, _handle_forensic)
    bus.subscribe(RESEARCH_INSIGHT_TOPIC, _handle_research)
