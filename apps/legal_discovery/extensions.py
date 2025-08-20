"""Shared Flask extensions for the legal discovery app."""

from collections import Counter

import jwt
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

__all__ = [
    "socketio",
    "limiter",
    "user_limit_key",
    "blocked_requests",
]
