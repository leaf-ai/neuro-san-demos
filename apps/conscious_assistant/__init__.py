"""Expose the Flask application for the Conscious Assistant demo."""

from .interface_flask import app as _app

__all__ = ["create_app", "_app"]


def create_app():
    """Return the configured Flask application."""
    return _app
