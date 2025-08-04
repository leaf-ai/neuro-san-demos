"""Flask application factory for the Legal Discovery module."""

__all__ = ["create_app"]


def create_app():
    """Return the configured Flask application."""
    from .interface_flask import app
    return app
