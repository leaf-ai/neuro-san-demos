"""Shared Flask extensions for the legal discovery app."""

import logging
import os
from collections import Counter

import jwt
import structlog
from flask import current_app, request, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from prometheus_flask_exporter import PrometheusMetrics


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
metrics = PrometheusMetrics.for_app_factory()


def configure_logging() -> None:
    """Configure structlog for JSON-formatted logs."""

    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(format="%(message)s", level=log_level)
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def init_tracing(app) -> None:
    """Initialize OpenTelemetry tracing for the Flask app."""

    provider = TracerProvider()
    provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)
    FlaskInstrumentor().instrument_app(app)


tracer = trace.get_tracer(__name__)

# Track how many requests were blocked by rate limiting.
blocked_requests: Counter[str] = Counter()

__all__ = [
    "socketio",
    "limiter",
    "metrics",
    "user_limit_key",
    "blocked_requests",
    "configure_logging",
    "init_tracing",
    "tracer",
]
