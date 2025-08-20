"""Application startup module for Legal Discovery.

This module centralizes Neo4j schema initialization so that the graph is
bootstrapped exactly once at process start. Downstream modules import the
pre-configured Flask ``app`` from here.
"""

from . import bootstrap_graph

# Apply graph constraints and indexes before the rest of the app imports.
bootstrap_graph()

# Import the Flask application after bootstrapping the graph.
from .interface_flask import app

__all__ = ["app"]
