"""Common authentication utilities for legal discovery routes."""

from __future__ import annotations

import jwt
from flask import current_app, jsonify, request, session
from functools import wraps

from .database import db
from .models import MessageAuditLog


def _log_auth_failure(reason: str) -> None:
    """Persist authentication failures for audit.

    Logging authentication errors should never cause request handling to
    fail.  The database may not be initialised in certain test scenarios, so
    we attempt to record the failure but silently ignore any issues.
    """

    try:  # pragma: no cover - best effort logging
        db.session.add(
            MessageAuditLog(message_id=None, sender="system", transcript=reason)
        )
        db.session.commit()
    except Exception:  # pragma: no cover - logging should not break auth
        try:
            db.session.rollback()
        except Exception:
            pass


def _require_auth() -> bool:
    """Validate JWT or session token presence.

    Authentication is skipped when ``JWT_SECRET`` is empty.
    """
    if not current_app.config.get("JWT_SECRET"):
        return True
    auth_header = request.headers.get("Authorization", "")
    token = None
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1]
    if token:
        try:
            jwt.decode(token, current_app.config["JWT_SECRET"], algorithms=["HS256"])
            return True
        except jwt.PyJWTError:
            _log_auth_failure("invalid_token")
            return False
    if session.get("user"):
        return True
    _log_auth_failure("missing_token")
    return False


def auth_required(func):
    """Decorator enforcing JWT or session authentication."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not _require_auth():
            return jsonify({"status": "error", "error": "unauthorized"}), 401
        return func(*args, **kwargs)

    return wrapper


__all__ = ["auth_required", "_require_auth"]

