from __future__ import annotations

import json
import hashlib
from datetime import datetime
from typing import Any, Optional

from .database import db
from .models import ChainOfCustodyLog, ChainEventType, Document


def log_event(
    document_id: int,
    event_type: ChainEventType | str,
    user_id: Optional[int] = None,
    metadata: Optional[dict[str, Any]] = None,
    source_team: str = "unknown",
) -> str:
    """Persist a chain-of-custody event."""
    etype = ChainEventType(event_type) if isinstance(event_type, str) else event_type
    timestamp = datetime.utcnow()
    doc = Document.query.get(document_id)
    doc_hash = doc.sha256 if doc else ""
    payload = {
        "document_id": document_id,
        "event_type": etype.value,
        "timestamp": timestamp.isoformat(),
        "user_id": user_id,
        "metadata": metadata or {},
        "doc_hash": doc_hash,
        "source_team": source_team,
    }
    signature_hash = hashlib.sha256(
        json.dumps(payload, sort_keys=True).encode("utf-8")
    ).hexdigest()
    entry = ChainOfCustodyLog(
        document_id=document_id,
        event_type=etype,
        user_id=user_id,
        source_team=source_team,
        event_metadata=metadata or {},
        timestamp=timestamp,
        signature_hash=signature_hash,
    )
    db.session.add(entry)
    db.session.commit()
    return entry.id
