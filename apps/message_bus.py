from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable, Dict

import redis

# Topic names shared across features
FORENSIC_HASH_TOPIC = "team.forensic.hashes"
RESEARCH_INSIGHT_TOPIC = "team.research.insights"
AUTO_DRAFTER_ALERT_TOPIC = "alerts.auto_drafter"
TIMELINE_ALERT_TOPIC = "alerts.timeline"


@dataclass
class TeamMessage:
    """Message payload with provenance metadata."""

    source_team: str
    payload: Dict[str, Any]


class MessageBus:
    """Simple Redis pub/sub wrapper for team communication."""

    def __init__(self, url: str = "redis://localhost:6379/0") -> None:
        self._client = redis.Redis.from_url(url)

    def publish(self, topic: str, message: TeamMessage) -> None:
        data = json.dumps({"source_team": message.source_team, "payload": message.payload})
        self._client.publish(topic, data)

    def subscribe(self, topic: str, handler: Callable[[TeamMessage], None]) -> None:
        pubsub = self._client.pubsub()

        def _callback(msg: Dict[str, Any]) -> None:
            data = json.loads(msg["data"]) if isinstance(msg["data"], bytes) else {}
            handler(
                TeamMessage(source_team=data.get("source_team", "unknown"), payload=data.get("payload", {}))
            )

        pubsub.subscribe(**{topic: _callback})
        pubsub.run_in_thread(sleep_time=0.001, daemon=True)
