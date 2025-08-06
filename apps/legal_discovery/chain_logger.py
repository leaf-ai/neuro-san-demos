from __future__ import annotations

from typing import Any, Optional

from .database import db
from .models import ChainOfCustodyLog, ChainEventType


def log_event(
    document_id: int,
    event_type: ChainEventType | str,
    user_id: Optional[int] = None,
    metadata: Optional[dict[str, Any]] = None,
    source_team: str = "unknown",
) -> str:
    """Persist a chain-of-custody event."""
    etype = ChainEventType(event_type) if isinstance(event_type, str) else event_type
    entry = ChainOfCustodyLog(
        document_id=document_id,
        event_type=etype,
        user_id=user_id,
        source_team=source_team,
        event_metadata=metadata or {},
    )
    db.session.add(entry)
    db.session.commit()
    return entry.id
