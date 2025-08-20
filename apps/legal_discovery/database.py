"""Database helpers for the legal discovery application."""

from __future__ import annotations

from typing import Dict, List

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


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
        entry = IngestionLog(
            case_id=case_id,
            path=path,
            doc_id=doc_id,
            segment_hashes=segment_hashes,
            status=status,
            duration_ms=duration_ms,
            error=error,
        )
        db.session.merge(entry)
        db.session.commit()
    except Exception:  # pragma: no cover - best effort
        try:
            db.session.rollback()
        except Exception:
            pass


def ingestion_matches(doc_id: str, segment_hashes: List[str]) -> bool:
    """Return True if ``doc_id`` has already been ingested with ``segment_hashes``."""

    try:
        entry = IngestionLog.query.filter_by(doc_id=doc_id, status="ingested").first()
        return bool(entry and entry.segment_hashes == segment_hashes)
    except Exception:
        return False


class RetrievalTrace(db.Model):
    """Persists retrieval query results for analysis."""

    __tablename__ = "retrieval_traces"

    id = db.Column(db.Integer, primary_key=True)
    trace_id = db.Column(db.String(40), nullable=False, index=True)
    case_id = db.Column(db.String(64), nullable=False)
    query = db.Column(db.Text, nullable=False)
    graph_weight = db.Column(db.Float, nullable=False, default=1.0)
    dense_weight = db.Column(db.Float, nullable=False, default=1.0)
    timings = db.Column(db.JSON, nullable=False)
    results = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


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
    except Exception:  # pragma: no cover - best effort
        try:
            db.session.rollback()
        except Exception:
            pass

