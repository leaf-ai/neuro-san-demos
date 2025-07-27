"""Utility helpers to load Flask apps from the subpackages."""

from importlib import import_module
from typing import Any

__all__ = ["load_app"]


def load_app(package: str) -> Any:
    """Return the Flask app object from the given subpackage."""
    module = import_module(f"apps.{package}.__init__")
    if hasattr(module, "create_app"):
        return module.create_app()
    raise ImportError(f"No create_app() in apps.{package}")
