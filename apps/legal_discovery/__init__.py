"""Flask application factory for the Legal Discovery module."""

__all__ = ["create_app"]


def create_app():
    """Return the configured Flask application."""

    from .interface_flask import app
    try:  # pragma: no cover - best effort
        from .hippo import ensure_graph_constraints

        ensure_graph_constraints()
    except Exception:  # pragma: no cover - external dependency may fail
        pass
    return app
