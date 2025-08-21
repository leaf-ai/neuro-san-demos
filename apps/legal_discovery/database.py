"""Database helpers for the legal discovery application."""

from __future__ import annotations

from typing import Dict, List
import logging

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


logger = logging.getLogger(__name__)


class IngestionLog(db.Model):
    """Tracks document ingestions to ensure idempotency."""

    __tablename__ = "ingestion_logs"
    __table_args__ = (db.Index("ix_ingestion_case_path", "case_id", "path"),)

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.String(64), nullable=False)
    path = db.Column(db.String(1024), nullable=False)
    doc_id = db.Column(db.String(64), nullable=False, unique=True)
    segment_hashes = db.Column(db.JSON, nullable=False, default=list)
    status = db.Column(db.String(32), nullable=False, default="ingested")
    duration_ms = db.Column(db.Float)
    error = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


def log_ingestion(
    *,
    case_id: str,
    path: str,
    doc_id: str,
    segment_hashes: List[str],
    status: str,
    duration_ms: float | None = None,
    error: str | None = None,
) -> None:
    """Persist an ingestion event with timing and status."""

    try:
        existing = IngestionLog.query.filter_by(doc_id=doc_id).one_or_none()

        if existing:
            existing.case_id = case_id
            existing.path = path
            existing.segment_hashes = segment_hashes
            existing.status = status
            existing.duration_ms = duration_ms
            existing.error = error
        else:
            entry = IngestionLog(
                case_id=case_id,
                path=path,
                doc_id=doc_id,
                segment_hashes=segment_hashes,
                status=status,
                duration_ms=duration_ms,
                error=error,
            )
            db.session.add(entry)

        db.session.commit()
    except Exception as exc:  # pragma: no cover - best effort
        logger.exception("failed to log ingestion", exc_info=exc)
        try:
            db.session.rollback()
        except Exception as rollback_exc:
            logger.exception("failed to rollback ingestion log", exc_info=rollback_exc)


def ingestion_matches(doc_id: str, segment_hashes: List[str]) -> bool:
    """Return True if ``doc_id`` has already been ingested with ``segment_hashes``."""

    try:
        entry = IngestionLog.query.filter_by(doc_id=doc_id, status="ingested").first()
        return bool(entry and entry.segment_hashes == segment_hashes)
    except Exception as exc:
        logger.exception("failed to check ingestion match", exc_info=exc)
        return False


def log_retrieval_trace(
    *,
    trace_id: str,
    case_id: str,
    query: str,
    graph_weight: float,
    dense_weight: float,
    timings: Dict[str, float],
    results: List[Dict],
) -> None:
    """Best-effort persistence of a retrieval trace."""

    try:
        from .models import RetrievalTrace

        entry = RetrievalTrace(
            trace_id=trace_id,
            case_id=case_id,
            query=query,
            graph_weight=graph_weight,
            dense_weight=dense_weight,
            timings=timings,
            results=results,
        )
        db.session.add(entry)
        db.session.commit()
    except Exception as exc:  # pragma: no cover - best effort
        logger.exception("failed to log retrieval trace", exc_info=exc)
        try:
            db.session.rollback()
        except Exception as rollback_exc:
            logger.exception("failed to rollback retrieval trace", exc_info=rollback_exc)


def log_objection_event(
    *,
    session_id: str,
    segment_id: str,
    type: str,
    ground: str,
    confidence: int,
    extracted_phrase: str,
    suggested_cures: List[str] | None = None,
    trace_id: str | None = None,
    refs: List[Dict] | None = None,
    path: Dict | List | None = None,
    action_taken: str | None = None,
    outcome: str | None = None,
) -> "ObjectionEvent":
    """Persist and return an objection event."""

    from .models import ObjectionEvent

    try:
        evt = ObjectionEvent(
            session_id=session_id,
            segment_id=segment_id,
            trace_id=trace_id,
            type=type,
            ground=ground,
            confidence=confidence,
            extracted_phrase=extracted_phrase,
            suggested_cures=suggested_cures or [],
            refs=refs,
            path=path,
            action_taken=action_taken,
            outcome=outcome,
        )
        db.session.add(evt)
        db.session.commit()
        return evt
    except Exception as exc:  # pragma: no cover - best effort
        logger.exception("failed to log objection event", exc_info=exc)
        try:
            db.session.rollback()
        except Exception as rollback_exc:
            logger.exception("failed to rollback objection event", exc_info=rollback_exc)
        return None


def log_objection_resolution(*, event_id: str, chosen_cure: str) -> None:
    """Record a chosen cure for an objection event."""

    from .models import ObjectionResolution

    try:
        resolution = ObjectionResolution(event_id=event_id, chosen_cure=chosen_cure)
        db.session.add(resolution)
        db.session.commit()
    except Exception as exc:  # pragma: no cover - best effort
        logger.exception("failed to log objection resolution", exc_info=exc)
        try:
            db.session.rollback()
        except Exception as rollback_exc:
            logger.exception(
                "failed to rollback objection resolution", exc_info=rollback_exc
            )

