#!/usr/bin/env python3
"""Seed PostgreSQL schema and default data for legal_discovery."""
import os
from apps.legal_discovery.interface_flask import app
from apps.legal_discovery.models import Case
from apps.legal_discovery.database import db

# Default to local docker-compose settings if DATABASE_URL is unset
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/legal_discovery",
)

def main() -> None:
    """Create tables and insert initial records."""
    with app.app_context():
        db.create_all()
        if not Case.query.first():
            db.session.add(Case(name="Default Case"))
            db.session.commit()
        print("PostgreSQL schema seeded.")

if __name__ == "__main__":
    main()
