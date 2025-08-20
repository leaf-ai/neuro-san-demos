"""Shared Flask extensions for the legal discovery app."""

from collections import Counter
import os

import jwt
import redis
from flask import current_app, request, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO


def user_limit_key() -> str:
    """Return a rate limit key based on the authenticated user.

    Falls back to the remote IP when no user identifier is available.
    """

    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1]
        try:
            data = jwt.decode(token, current_app.config["JWT_SECRET"], algorithms=["HS256"])
            user_id = data.get("sub")
            if user_id is not None:
                return f"user:{user_id}"
        except jwt.PyJWTError:
            pass
    if session.get("user"):
        return f"user:{session['user']}"
    return get_remote_address()


socketio = SocketIO()
limiter = Limiter(key_func=get_remote_address)

# Track how many requests were blocked by rate limiting.
blocked_requests: Counter[str] = Counter()

# Redis connection used for request caching.  Falls back to ``None`` when
# the service is unavailable so callers can degrade gracefully.
try:  # pragma: no cover - best effort
    redis_client = redis.Redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379/0"))
    redis_client.ping()
except Exception:  # pragma: no cover - redis may be absent
    redis_client = None

# Global counters for cache metrics exposed via ``/api/health``.
cache_stats: Counter[str] = Counter()

__all__ = [
    "socketio",
    "limiter",
    "user_limit_key",
    "blocked_requests",
    "redis_client",
    "cache_stats",
]
