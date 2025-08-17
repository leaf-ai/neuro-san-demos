"""Database helpers for the legal discovery application."""

from __future__ import annotations

from typing import List

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class IngestionLog(db.Model):
    """Tracks document ingestions to ensure idempotency."""

    __tablename__ = "ingestion_logs"

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.String(64), nullable=False)
    path = db.Column(db.String(1024), nullable=False)
    doc_id = db.Column(db.String(64), nullable=False, unique=True)
    segment_hashes = db.Column(db.JSON, nullable=False, default=list)
    status = db.Column(db.String(32), nullable=False, default="ingested")
    created_at = db.Column(db.DateTime, server_default=db.func.now())


def log_ingestion(
    *, case_id: str, path: str, doc_id: str, segment_hashes: List[str]
) -> None:
    """Persist an ingestion event if it has not already been recorded."""

    try:
        if IngestionLog.query.filter_by(doc_id=doc_id).first():
            return
        entry = IngestionLog(
            case_id=case_id, path=path, doc_id=doc_id, segment_hashes=segment_hashes
        )
        db.session.add(entry)
        db.session.commit()
    except Exception:  # pragma: no cover - best effort
        try:
            db.session.rollback()
        except Exception:
            pass

