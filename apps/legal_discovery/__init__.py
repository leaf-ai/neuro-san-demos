"""Flask application factory for the Legal Discovery module."""

from __future__ import annotations

import os

try:  # pragma: no cover - allow tests without Neo4j installed
    from neo4j import GraphDatabase
except Exception:  # pragma: no cover - fallback when driver unavailable
    GraphDatabase = None

from .hippo import SCHEMA_QUERIES

__all__ = ["create_app", "bootstrap_graph"]


def bootstrap_graph() -> None:
    """Apply Neo4j constraints and indexes if possible."""

    if not GraphDatabase:  # pragma: no cover - driver not installed
        return

    uri = os.environ.get("NEO4J_URI", "bolt://neo4j:7687")
    user = os.environ.get("NEO4J_USER", "neo4j")
    pwd = os.environ.get("NEO4J_PASSWORD")
    auth = (user, pwd) if pwd else None
    db = os.environ.get("NEO4J_DATABASE", "neo4j")

    driver = None
    try:  # pragma: no cover - external dependency
        driver = GraphDatabase.driver(uri, auth=auth)
        with driver.session(database=db) as session:
            for query in SCHEMA_QUERIES:
                session.run(query)
    except Exception:
        pass
    finally:  # pragma: no cover - ensure closure
        if driver:
            try:
                driver.close()
            except Exception:
                pass


def create_app():
    """Return the configured Flask application."""

    from .interface_flask import app

    try:  # pragma: no cover - best effort
        bootstrap_graph()
    except Exception:  # pragma: no cover - external dependency may fail
        pass
    return app
